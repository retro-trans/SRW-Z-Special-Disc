"""Regression checks for fixed-cell terrain labels and grade spacing."""
import copy,unittest
from sp_disc import Disc,EXE
from terrain_rows import PREVIOUS,inventory,compile_component,REPLACEMENT
from audit_terrain_rows import check,glyph

class TerrainRowsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before=Disc(PREVIOUS).read(EXE);cls.inv=inventory()
        cls.after,cls.report=compile_component(cls.before,cls.inv)

    def test_all_eleven_rows_use_same_full_width_structure(self):
        result=check(self.after,self.before,self.inv)
        self.assertEqual(result['rows_read_back'],11)
        for row in self.inv['rows']:
            self.assertEqual(self.after[row['offset']:row['offset']+16],REPLACEMENT)
        self.assertFalse(any(glyph(self.after,0x85db)))

    def test_old_ascii_rows_fail_readback(self):
        with self.assertRaisesRegex(ValueError,'row byte readback'):check(self.before,self.before,self.inv)

    def test_word_space_in_place_of_blank_cell_is_rejected(self):
        bad=copy.deepcopy(self.inv)
        bad['rows'][0]['after_hex']=REPLACEMENT.replace(bytes.fromhex('85db'),bytes.fromhex('8140')).hex()
        with self.assertRaisesRegex(ValueError,'cell/blank encoding'):compile_component(self.before,bad)

    def test_missing_row_is_rejected(self):
        bad=copy.deepcopy(self.inv);bad['rows'].pop()
        with self.assertRaisesRegex(ValueError,'field ownership'):compile_component(self.before,bad)

    def test_changes_outside_rows_are_rejected(self):
        bad=bytearray(self.after);bad[0x10000]^=1
        with self.assertRaisesRegex(ValueError,'outside terrain rows'):check(bytes(bad),self.before,self.inv)

    def test_changed_donor_art_is_rejected(self):
        bad=bytearray(self.before);bad[self.inv['runtime_guards'][0]['offset']]^=1
        with self.assertRaisesRegex(ValueError,'renderer/art drift'):compile_component(bytes(bad),self.inv)

if __name__=='__main__':unittest.main()
