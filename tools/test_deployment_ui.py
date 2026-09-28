"""Negative guards: detect non-UI chapter mutations and oversized artwork."""
import unittest,struct
from sp_disc import Disc,SOURCE,decode,banlz
from audit_deployment_ui import protect_stage
from deployment_ui import render

class Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.native=Disc(SOURCE).read('DATA/STAGE.BIN')
    def mutated(self,offset):
        raw=bytearray(decode(self.native[173296:189648])[0]);raw[offset]^=1
        encoded=banlz.compress_record_optimal(bytes(raw),flags=banlz.parse_header(self.native[173296:])[1])
        self.assertLessEqual(len(encoded),16352)
        return self.native[:173296]+encoded+bytes(16352-len(encoded))+self.native[189648:]
    def test_roster_pointer_change_allowed(self):protect_stage(self.mutated(0x3fbc),self.native)
    def test_squad_membership_change_rejected(self):
        with self.assertRaisesRegex(ValueError,'dialogue or gameplay'):protect_stage(self.mutated(0x3fa8),self.native)
    def test_dialogue_byte_change_rejected(self):
        with self.assertRaisesRegex(ValueError,'dialogue or gameplay'):protect_stage(self.mutated(0x8000),self.native)
    def test_other_chunk_rejected(self):
        raw=bytearray(self.native);raw[44017]^=1
        with self.assertRaisesRegex(ValueError,'archive change'):protect_stage(bytes(raw),self.native)
    def test_artwork_overflow_rejected(self):
        with self.assertRaisesRegex(ValueError,'overflow'):render('An unreasonably long untranslated button label',[0,0,20,20])

if __name__=='__main__':unittest.main()
