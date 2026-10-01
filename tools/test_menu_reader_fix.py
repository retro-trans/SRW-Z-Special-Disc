"""Execute the installed token-reader instructions, including poisoned tails."""
import struct
import unittest
from sp_disc import ROOT, Disc, EXE
from squad_followup import loaded
from menu_reader_fix import build, HOOK, TOTAL
from menu_encoding import menu_encode
from align_story_panels import actual_width
from test_story_panel_alignment import Machine, POOL_BASE

MASK = (1 << 64)-1

def signed(v, bits):
    v &= (1 << bits)-1
    return v-(1 << bits) if v & (1 << (bits-1)) else v


class Reader:
    """Run the native scanner/flush loop; intercept only the font submission.

    Entry is the first byte fetch after setup. End is the cleanup block. Source
    reads are recorded, so a skipped NUL is detected even if a later font draw
    happens to stop at an embedded NUL. Stale bytes model reused menu segments.
    """
    def __init__(self, exe, raw, tail=b'\x0aSTALE TEXT\0\0'):
        self.exe=exe; self.mem={}; self.r=[0]*32; self.draws=[]; self.reads=[]; self.icons=[]
        self.source=0x2000000; self.r[29]=0x3000000
        self.r[18]=0; self.r[19]=112; self.r[20]=0
        for i,b in enumerate(raw+b'\0'+tail): self.mem[self.source+i]=b
        # Native object leaves bytes past the copied terminator untouched.
        self.put(self.r[29]+0x1CC,self.source,4)
        self.put(self.r[29]+0xBE,112,2)
        self.put(0x4ED5EE,12,2)  # original native line-height field

    def get(self,at,n,sign=False):
        if self.source <= at < self.source+1024: self.reads.append(at-self.source)
        data=[]
        for i in range(n):
            if at+i in self.mem: data.append(self.mem[at+i])
            else:
                try: data.append(self.exe[loaded(self.exe,at+i)])
                except ValueError: data.append(0)
        return int.from_bytes(bytes(data), 'little', signed=sign)

    def put(self,at,value,n):
        for i,b in enumerate((value % (1 << (8*n))).to_bytes(n,'little')): self.mem[at+i]=b

    def string(self,at):
        out=bytearray()
        for i in range(512):
            b=self.get(at+i,1)
            if not b:return bytes(out)
            out.append(b)
        raise AssertionError('Unterminated submission')

    def run(self):
        pc=0x3638F0;pending=None
        for _ in range(20000):
            if pc==0x363948:return self.draws
            if pc==0x13D050:
                self.draws.append((self.string(self.r[4]), signed(self.r[5],16), signed(self.r[6],16)))
                self.r[2]=0x1234;pc=self.r[31];pending=None;continue
            if pc in (0x19EA38,0x1A4F60,0x13A5A0,0x390BE0):
                if pc==0x19EA38:
                    import re
                    self.r[2]=int(re.match(rb'-?[0-9]+',self.string(self.r[4]))[0])
                elif pc==0x1A4F60:
                    self.r[2]=self.r[4]+self.string(self.r[4]).index(self.r[5])
                elif pc==0x13A5A0:
                    from library_text import text
                    self.r[2]=actual_width(text(self.string(self.r[4])))
                else:
                    self.icons.append((self.r[5],signed(self.r[6],16),signed(self.r[7],16)))
                    self.r[2]=0x1234
                pc=self.r[31];pending=None;continue
            w=struct.unpack_from('<I',self.exe,loaded(self.exe,pc))[0]
            op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31
            imm=w&65535;si=signed(imm,16);jump=None;nxt=pc+4
            if op==0:
                fn=w&63;sa=w>>6&31
                if fn==0:self.r[rd]=signed(self.r[rt]<<sa,32)
                elif fn==0x21:self.r[rd]=signed(self.r[rs]+self.r[rt],32)
                elif fn==0x23:self.r[rd]=signed(self.r[rs]-self.r[rt],32)
                elif fn==0x2D:self.r[rd]=(self.r[rs]+self.r[rt])&MASK
                elif fn==0x2A:self.r[rd]=int(signed(self.r[rs],64)<signed(self.r[rt],64))
                elif fn==0x3C:self.r[rd]=(self.r[rt]<<(sa+32))&MASK
                elif fn==0x3F:self.r[rd]=signed(self.r[rt],64)>>(sa+32)
                elif fn==8:jump=self.r[rs]
                else:raise AssertionError((hex(pc),hex(w)))
            elif op in (2,3):
                if op==3:self.r[31]=pc+8
                jump=(w&0x3FFFFFF)<<2
            elif op in (4,5):
                if ((self.r[rs]&MASK)==(self.r[rt]&MASK))==(op==4):jump=pc+4+si*4
            elif op==1 and rt==1:
                if signed(self.r[rs],64)>=0:jump=pc+4+si*4
            elif op==10:self.r[rt]=int(signed(self.r[rs],64)<si)
            elif op==9:self.r[rt]=signed(self.r[rs]+si,32)
            elif op==11:self.r[rt]=int((self.r[rs]&MASK)<(si&MASK))
            elif op==13:self.r[rt]=self.r[rs]|imm
            elif op==15:self.r[rt]=signed(imm<<16,32)
            elif op in (30,32,33,35,36,55):
                n={30:16,32:1,33:2,35:4,36:1,55:8}[op]
                self.r[rt]=self.get(self.r[rs]+si,n,op in (32,33,35))
            elif op in (31,40,41,43,63):self.put(self.r[rs]+si,self.r[rt],{31:16,40:1,41:2,43:4,63:8}[op])
            else:raise AssertionError((hex(pc),hex(w)))
            self.r[0]=0
            if pending is not None:nxt=pending
            pending=jump;pc=nxt
        raise AssertionError('Reader exceeded instruction bound')


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.6.iso').read(EXE)
        cls.new,cls.report=build(cls.old)

    def test_reproduces_stale_gold_text_and_fixes_it(self):
        old=Reader(self.old,b'Funds');bad=old.run()
        self.assertGreater(max(old.reads),5)
        self.assertGreater(len(bad),1)  # extra line drawn after skipped terminator
        new=Reader(self.new,b'Funds')
        self.assertEqual(new.run(),[(b'Funds',112,0)])
        self.assertEqual(max(new.reads),5)

    def test_all_bonus_labels_and_arbitrary_ascii_lengths(self):
        values=['Funds','BS','PP','Parts','Starting Funds','Total Funds','Starting BS',
                'Total BS','Starting PP','Total PP','CLEAR!','---',
                'Added the above parts to your starting parts.','Beater Services Work Log']
        values += ['A'*n for n in range(1,66)]
        for value in values:
            raw=menu_encode(value);m=Reader(self.new,raw)
            with self.subTest(value=value):
                self.assertEqual(m.run(),[(raw,112,0)])
                self.assertEqual(max(m.reads),len(raw))

    def test_native_pairs_private_glyphs_and_even_ascii_preserved(self):
        # Includes a native pair with '[' as its trail byte; it must not be a token.
        for raw in [b'',b'BS',b'PP',bytes.fromhex('8381835b834a815b'),
                    bytes.fromhex('8e918be0'),bytes.fromhex('854785488149')]:
            with self.subTest(raw=raw):
                self.assertEqual(Reader(self.new,raw).run(),Reader(self.old,raw).run())

    def test_newlines_at_any_byte_boundary(self):
        for first in (b'Funds',b'BS',bytes.fromhex('8e918be0')):
            raw=first+b'\nTotal';m=Reader(self.new,raw)
            self.assertEqual(m.run(),[(first,112,0),(b'Total',112,12)])
            self.assertEqual(max(m.reads),len(raw))

    def test_native_button_and_spacing_tokens(self):
        for raw in (b'BS<0>OK',b'PP[10]OK'):
            a=Reader(self.old,raw);b=Reader(self.new,raw)
            self.assertEqual(a.run(),b.run())
            self.assertEqual(a.icons,b.icons)
        # Odd ASCII prefix no longer swallows the token's opening byte.
        m=Reader(self.new,b'A<0>B')
        self.assertEqual([row[0] for row in m.run()],[b'A',b'B'])
        self.assertEqual(len(m.icons),1)
        self.assertEqual(max(m.reads),len(b'A<0>B'))
        m=Reader(self.new,b'A[10]B')
        rows=m.run()
        self.assertEqual([r[0] for r in rows],[b'A',b'B'])
        self.assertEqual(rows[1][1],112+actual_width('A')+20)

    def test_total_column_and_preservation(self):
        at=loaded(self.new,TOTAL)
        m=Machine(self.new[at:at+108]);obj=0x2000000
        m.r[4]=obj;m.r[5]=0x2100000;m.r[6:9]=[15,0,4]
        m.put(obj+0x252A,1,2);m.put(obj+10,1,2)
        for i,b in enumerate(menu_encode('   4,000,000')+b'\0'):m.put(m.r[5]+i,b,1)
        m.run(POOL_BASE)
        self.assertEqual(m.get(obj+0x98,2,True),32)
        self.assertLessEqual(92+actual_width('Starting Funds')+16,352)
        # Font preset 0x33 uses 16-unit native cells, including padding.
        self.assertEqual(struct.unpack_from('<h',self.new,loaded(self.new,0x49E190+0x33*22))[0],16)
        # Twelve native cells at 16 units each, including leading padding.
        self.assertLessEqual(352+12*16,576)
        restored=bytearray(self.new[:len(self.old)])
        for p in self.report['patches']:struct.pack_into('<I',restored,p['offset'],p['before'])
        self.assertEqual(restored,self.old)
        self.assertLessEqual(self.report['segment_end'],self.report['heap_base'])

    def test_preimage_rejection(self):
        wrong=bytearray(self.old);wrong[loaded(wrong,HOOK)]^=1
        with self.assertRaises(ValueError):build(wrong)

if __name__=='__main__':unittest.main()
