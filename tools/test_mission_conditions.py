"""Read-only regression checks for condition scope, encoding and row limits."""
import json,struct,unittest
from sp_disc import ROOT,Disc,SOURCE,decode
from inspect_mission_conditions import TARGET
from stage_ui_guard import assert_decoded,ROSTER_SITES
from audit_mission_conditions import layout_check
from menu_encoding import menu_encode,TOKENS
from library_text import text


class MissionConditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inv=json.loads(TARGET.read_text(encoding='utf8'))
        cls.ch=next(c for c in cls.inv['chunks'] if c['chunk']==13)
        cls.raw=decode(Disc(SOURCE).read('DATA/STAGE.BIN')[cls.ch['start']:cls.ch['end']])[0]
        cls.sites=set(ROSTER_SITES)|{e['pointer_site'] for g in cls.ch['tables'] for e in g['entries'] if e['source']!='？？？'}

    def test_typed_display_words_allowed(self):
        changed=bytearray(self.raw)
        for p in self.sites:struct.pack_into('<I',changed,p,0x83c4e4)
        assert_decoded(self.raw,changed,self.sites)

    def test_code_dialogue_and_roster_fields_rejected(self):
        # Initializer opcode, native condition text, roster unit ID, hidden placeholder pointer.
        hidden=next(e['pointer_site'] for g in self.ch['tables'] for e in g['entries'] if e['source']=='？？？')
        body=self.ch['tables'][0]['entries'][0]['offset']
        for p in (0x80,body,0x3fa0,hidden):
            with self.subTest(offset=p):
                changed=bytearray(self.raw);changed[p]^=1
                with self.assertRaises(Exception):assert_decoded(self.raw,changed,self.sites)

    def test_funds_less_than_is_a_visible_glyph(self):
        value='Funds earned <350,000 at turn 6 start.'
        self.assertIsNone(TOKENS.search(value));self.assertEqual(text(menu_encode(value)),value)
        self.assertIn('＜'.encode('cp932'),menu_encode(value))

    def test_damage_plus_and_hp_values_roundtrip(self):
        value='Deal 10,000+ damage. HP at 10% or less.'
        self.assertEqual(text(menu_encode(value)),value)

    def test_actual_reviewed_layouts(self):
        cfg=json.loads((ROOT/'work/translation/en/mission_conditions.json').read_text(encoding='utf8'))
        for row in cfg['entries']:layout_check(row['text'],row['lines'])
        self.assertTrue(all(r['rows']<=4 for r in cfg['groups']))

    def test_overflow_and_truncation_rejected(self):
        for value,lines in [('a b c d e',['a','b','c','d','e']),('W'*60,['W'*60]),('Earn funds',['Earn'])]:
            with self.assertRaises(Exception):layout_check(value,lines)


if __name__=='__main__':unittest.main(verbosity=2)
