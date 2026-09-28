"""Regression checks for the corrupt movement format and native selectors."""
import copy,json,struct,unittest
from sp_disc import ROOT,Disc,EXE
from prepare_tactical_ui import PREVIOUS,inventory
from tactical_ui import compile_component
from audit_tactical_ui import layout_checks,selector_checks,movement,string
from library_text import text

class TacticalUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.disc=Disc(PREVIOUS);cls.before=cls.disc.read(EXE);cls.inv,cls.rows=inventory()
        cls.after,cls.report=compile_component(cls.before,cls.inv,cls.rows)

    def test_all_dynamic_movement_fields_fit_and_keep_meaning(self):
        report=layout_checks(self.after)
        self.assertEqual(report['movement_cases'],1101)
        self.assertEqual(report['max_movement_width'],198)
        self.assertEqual(text(movement(self.after,6,1)),'[ 6/AirOnly]')
        self.assertEqual(text(movement(self.after,99,0,5)),'[99/A-S]')

    def test_previous_shortened_templates_fail_regression(self):
        self.assertNotEqual(text(movement(self.before,6,1)),'[ 6/AirOnly]')
        with self.assertRaises(ValueError):layout_checks(self.before)

    def test_no_unscoped_bytes_are_modified(self):
        restored=bytearray(self.after)
        for row in self.report['spans']:
            at=row['offset'];restored[at:at+row['size']]=bytes.fromhex(row['before_hex'])
        self.assertEqual(restored,self.before)
        self.assertEqual(len(self.report['spans']),20)

    def test_changed_native_opcode_is_rejected(self):
        bad=bytearray(self.before);bad[0x392b6c-0xff680]^=1
        with self.assertRaisesRegex(ValueError,'instruction drift'):compile_component(bytes(bad),self.inv,self.rows)

    def test_one_byte_terrain_cell_is_rejected(self):
        bad=copy.deepcopy(self.rows);bad[-1]['encoded_hex']='53'
        with self.assertRaisesRegex(ValueError,'two-byte private glyph'):compile_component(self.before,self.inv,bad)

    def test_shortened_prefix_is_rejected(self):
        bad=copy.deepcopy(self.rows)
        for row in bad:
            if row['id']=='exe/3bfdf0':row['encoded_hex']='5b202f2d2d2d5d';row['text']='[ /---]'
        with self.assertRaisesRegex(ValueError,'prefix geometry'):compile_component(self.before,self.inv,bad)

    def test_all_requested_screen_selectors_resolve_to_english(self):
        b=self.after;po=struct.unpack_from('<I',b,28)[0];size,count=struct.unpack_from('<HH',b,42)
        segments=[struct.unpack_from('<8I',b,po+i*size) for i in range(count)]
        def loaded(address):
            s=next(s for s in segments if s[0]==1 and s[2]<=address<s[2]+s[4])
            return s[1]+address-s[2]
        selections=selector_checks(self.disc,b,loaded)
        self.assertEqual(sum(len(r['selections']) for r in selections),44)

if __name__=='__main__':unittest.main()
