"""Execute bonus-panel alignment instructions and verify bounded text edits."""
import struct,unittest
from sp_disc import ROOT,Disc,EXE,decode
from bonus_results import *
from test_story_panel_alignment import Machine,POOL_BASE

class BonusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d=Disc(ROOT/'work/output/SRW Z Special Disc English v0.3.1.iso')
        cls.exe=d.read(EXE);cls.comp=d.read(MEMBER)
        cls.out,cls.packed,cls.report=build(cls.exe,cls.comp)

    def test_append_columns_preserve_content_style_and_registers(self):
        for x in (112,80):
            for n in (0,1,7,16,17):
                for count in (0,1,2,7,8):
                    with self.subTest(x=x,row=n,count=count):
                        m=Machine(append_column(x));obj=0x2000000;row=obj+(n-1)*594
                        m.r[4]=obj;m.r[5]=0x2100000;m.r[6:9]=[21,0,4]
                        for i,b in enumerate(b'4,000,000\0'):m.put(m.r[5]+i,b,1)
                        original_s0=0x11112222333344445555666677778888;m.r[16]=original_s0
                        m.put(obj+0x252A,n,2);m.put(row+10,count,2);m.put(row+0x98,55,2)
                        m.run(POOL_BASE)
                        changed=1<=n<=16 and count==1
                        self.assertEqual(m.get(row+0x98,2,True),x if changed else 55)
                        self.assertEqual(m.calls[0][2:],(b'4,000,000',[21,0,4]))
                        self.assertEqual(m.r[16],original_s0);self.assertEqual(m.r[29],0x3000000)
                        if changed:
                            self.assertEqual(m.get(row+0x9A,2),18+(n-1)*12)
                            self.assertEqual([m.get(row+0x9C+i,1) for i in range(3)],[21,0,4])

    def test_status_all_four_result_modes_and_confirmation(self):
        helper=self.report['status_helper'];at=loaded(self.out,helper)
        words=struct.unpack_from('<41I',self.out,at)
        payload=self.out[at:at+164]
        clear=((words[10]&65535)<<16)|(words[11]&65535)
        dash=((words[14]&65535)<<16)|(words[15]&65535)
        for mode in range(5):
            for pointer,value in [(0x4C3990,b'CLEAR!'),(0x4C39B8,b'---')]:
                m=Machine(payload);obj=0x2000000;m.r[4]=obj;m.r[5]=pointer;m.r[20]=mode
                for addr,st in [(clear,b'CLEAR!\0'),(dash,b'---\0')]:
                    for i,b in enumerate(st):m.put(addr+i,b,1)
                m.put(obj+0x252A,1,2);m.put(obj+10,1,2);m.run(POOL_BASE)
                self.assertEqual(m.calls[0][2],value);self.assertEqual(m.get(obj+0x98,2),128)

    def test_slots_pointers_width_and_story_preservation(self):
        before=decode(self.comp)[0];after=decode(self.packed)[0];restored=bytearray(after)
        for field in self.report['fields']:
            at=field['offset'];cap=field['capacity'];p=field['pointer']
            self.assertEqual(text(after[at:at+cap].split(b'\0')[0]),field['text'])
            self.assertEqual(after[p:p+4],before[p:p+4]);restored[at:at+cap]=before[at:at+cap]
        self.assertEqual(restored,before)
        self.assertEqual(self.out[0x2112D0-BASE:0x2112D0-BASE+8],self.exe[0x2112D0-BASE:0x2112D0-BASE+8])
        self.assertLessEqual(64+actual_width('Beater Services Work Log'),432-16)
        self.assertLessEqual(92+actual_width('Starting Funds'),400-16)
        self.assertLessEqual(400+actual_width('4,294,967,295'),576)

    def test_reject_modified_executable_and_text(self):
        changed=bytearray(self.exe);changed[HEAD_CALLS[0]-BASE]^=1
        with self.assertRaises(ValueError):build(changed,self.comp)
        raw=bytearray(decode(self.comp)[0]);raw[FIELDS[0][0]]^=1
        bad=banlz.compress_record(bytes(raw),flags=banlz.parse_header(self.comp)[1])
        with self.assertRaises(ValueError):build(self.exe,bad)

if __name__=='__main__':unittest.main()
