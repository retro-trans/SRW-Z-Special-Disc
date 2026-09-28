"""Check the shared selector, actual English width and bounded prompt edits."""
import unittest
from sp_disc import Disc,EXE,decode,banlz
from mission_prompt import PREVIOUS,MEMBER,inventory,compile_component,POSITION
from audit_mission_prompt import check


class PromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prior=Disc(PREVIOUS);cls.exe=prior.read(EXE);cls.comp=prior.read(MEMBER)
        cls.inv=inventory();cls.newexe,cls.newcomp,cls.report=compile_component(cls.exe,cls.comp,cls.inv)

    def test_shared_question_and_measured_center(self):
        report,restored=check(self.newexe,self.newcomp,self.exe,self.comp)
        self.assertEqual(report['width'],210)
        self.assertEqual(report['absolute_x']+report['width']/2,236)
        self.assertEqual(restored,self.exe)

    def test_unrelated_executable_change_rejected(self):
        raw=bytearray(self.newexe);raw[POSITION+4]^=1
        with self.assertRaisesRegex(ValueError,'Other executable'):
            check(bytes(raw),self.newcomp,self.exe,self.comp)

    def test_original_japanese_prompt_rejected(self):
        with self.assertRaisesRegex(ValueError,'text readback'):
            check(self.newexe,self.comp,self.exe,self.comp)

    def test_unrelated_overlay_change_rejected(self):
        raw=bytearray(decode(self.newcomp)[0]);raw[0x98290]^=1
        packed=banlz.compress_record(bytes(raw),flags=banlz.parse_header(self.newcomp)[1])
        with self.assertRaisesRegex(ValueError,'Other menu data'):
            check(self.newexe,packed,self.exe,self.comp)


if __name__=='__main__':unittest.main()
