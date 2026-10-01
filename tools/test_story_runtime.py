"""Execute the relocated story converter, with real MIPS branch delay slots."""
import struct
import unittest
from sp_disc import ROOT, Disc, EXE
from story_runtime import apply, convert, SETTEXT, NEW_CAVE, NEW_FILE, CODE_BYTES, TABLE_BYTES
from inspect_english_runtime import B_BASE


def execute(exe, raw, expanded=None):
    regs = [0] + [0x500000+i*256 for i in range(1, 32)]
    obj, src, stack, done = 0x900000, 0x910000, 0x1ff0000, 0x123400
    regs[4], regs[5], regs[29], regs[31] = obj, src if raw is not None else 0, stack, done
    initial = regs[:]; mem = {}
    def put(at, data): mem.update({at+i: b for i,b in enumerate(data)})
    put(NEW_CAVE, exe[NEW_FILE:NEW_FILE+CODE_BYTES+TABLE_BYTES])
    put(SETTEXT, exe[SETTEXT-B_BASE:SETTEXT-B_BASE+8])
    put(obj, b'\xcc'*1040); put(stack-0x420, b'\xcc'*0x420)
    put(src, (raw or b'')+b'\0')
    def cstr(at):
        buf = bytearray()
        for i in range(1024):
            b = mem[at+i]
            if b == 0: return bytes(buf)
            buf.append(b)
        raise AssertionError('Unbounded converter output')
    pc, pending = SETTEXT, None
    for _ in range(30000):
        if pc == done:
            for r in (16, 17, 29, 31): assert regs[r] == initial[r]
            assert bytes(mem[obj+i] for i in range(12)) == b'\xcc'*12
            return cstr(obj+12)
        if pc == 0x205490:
            regs[2] = 0x950000 if expanded is not None else 0; pc = regs[31]; continue
        if pc in (0x2056e0, 0x1a5238):
            if pc == 0x2056e0:
                assert regs[4] == 0x950000 and regs[6] == src
                at, data = regs[5], expanded
            else: at, data = regs[4], cstr(regs[5])
            put(at, data+b'\0'); pc = regs[31]; continue
        w = sum(mem[pc+i] << (8*i) for i in range(4)); op = w >> 26
        rs, rt, rd, sa, fn = w>>21&31, w>>16&31, w>>11&31, w>>6&31, w&63
        imm = w&65535; signed = imm-65536 if imm&32768 else imm
        next_pc = pc+4 if pending is None else pending; pending = None
        if op == 0:
            if fn == 0: regs[rd] = regs[rt] << sa
            elif fn == 0x21: regs[rd] = regs[rs]+regs[rt]
            elif fn == 8: pending = regs[rs]
            else: raise AssertionError(hex(w))
        elif op in (2, 3):
            if op == 3: regs[31] = pc+8
            pending = w&0x3ffffff; pending <<= 2
        elif op in (4, 5):
            equal = regs[rs] == regs[rt]
            pending = pc+4+signed*4 if equal == (op == 4) else pc+8
        elif op == 9: regs[rt] = regs[rs]+signed
        elif op == 11: regs[rt] = int(regs[rs] < (signed&0xffffffff))
        elif op == 13: regs[rt] = regs[rs]|imm
        elif op == 15: regs[rt] = imm<<16
        elif op == 36: regs[rt] = mem[regs[rs]+signed]
        elif op == 40:
            at = regs[rs]+signed
            assert obj+12 <= at < obj+1036 or stack-0x420 <= at < stack
            mem[at] = regs[rt]&255
        elif op == 35: regs[rt] = sum(mem[regs[rs]+signed+i] << (8*i) for i in range(4))
        elif op == 43:
            at = regs[rs]+signed; assert stack-0x420 <= at <= stack-4
            put(at, struct.pack('<I', regs[rt]))
        else: raise AssertionError(hex(w))
        regs = [r&0xffffffff for r in regs]; regs[0] = 0; pc = next_pc
    raise AssertionError('Converter did not return')


class StoryRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.0.iso').read(EXE)
        cls.patched, cls.report = apply(cls.base)
        cls.table = cls.patched[NEW_FILE+CODE_BYTES:NEW_FILE+CODE_BYTES+TABLE_BYTES]

    def test_screenshot_line_and_all_printable_ascii(self):
        pictured = "Eiji\n「Yeah, well. The world was turned upside\ndown, but we've been through about the\nsame.」".encode('cp932')
        for raw in (pictured, bytes(range(32,127)), b'', 'Pilot\n（A B...）\n「123!?」'.encode('cp932')):
            self.assertEqual(execute(self.patched,raw), convert(raw,self.table))
        self.assertEqual(execute(self.patched,pictured).count(b'\n'),3)

    def test_null_input_and_macro_expansion(self):
        self.assertEqual(execute(self.patched,None),b'')
        expanded = 'Pilot\n「セツコ, move!」'.encode('cp932')
        self.assertEqual(execute(self.patched,b'$n, move!',expanded),convert(expanded,self.table))

    def test_mixed_sjis_controls_and_halfwidth_passthrough(self):
        raw = bytes([0x81,0x40,0xe0,0x41,0xa1,0xdf,0xfd,1,10,31,127])+b'ABC'
        self.assertEqual(execute(self.patched,raw),convert(raw,self.table))

    def test_two_silent_dialogue_occurrences(self):
        from compile_story import targets
        rows=[r for r in targets().values() if r['id']=='x_aba71b54e5']
        self.assertEqual(len(rows),2)
        for row in rows:
            raw=row['text'].encode('cp932')
            self.assertEqual(execute(self.patched,raw),convert(raw,self.table))

    def test_idempotence_and_only_guarded_words_change(self):
        again, report = apply(self.patched)
        self.assertEqual(again,self.patched); self.assertEqual(report['patches'],[])
        restored=bytearray(self.patched)
        for p in self.report['patches']: struct.pack_into('<I',restored,p['offset'],p['before'])
        self.assertEqual(restored,self.base)
        self.assertEqual(len(self.report['patches']),13)
        bad=bytearray(self.base); bad[SETTEXT-B_BASE] ^= 1
        with self.assertRaises(ValueError): apply(bytes(bad))

    def test_entire_dialogue_corpus_conversion_budget(self):
        from story_layout import load, layout_row
        source,speakers,final=load(); longest=(0,None)
        for row in source:
            raw=layout_row(row,speakers,final[row['id']])[0].encode('cp932')
            result=convert(raw,self.table)
            self.assertEqual(raw.count(b'\n'),result.count(b'\n'))
            self.assertLess(len(raw),1024); self.assertLess(len(result),1024)
            if len(result)>longest[0]: longest=(len(result),raw)
        self.assertEqual(len(source),7509)
        self.assertEqual(execute(self.patched,longest[1]),convert(longest[1],self.table))
        print('All 7,509 ordinary dialogue rows fit conversion buffer; maximum bytes:',longest[0])

if __name__=='__main__': unittest.main()
