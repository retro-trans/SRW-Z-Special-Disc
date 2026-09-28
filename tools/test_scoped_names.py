"""Protect weapon names and paragraph boundaries during cross-corpus fixes."""
import unittest
from battle_terms import canonicalize


class ScopedNames(unittest.TestCase):
    def test_asakim_requires_full_native_identity(self):
        self.assertEqual(canonicalize('Asakim Dowin', 'アサキム・ドーウィン'), 'Asakim Dowen')
        self.assertEqual(canonicalize('Dowin', 'アサキム\nドーウィン',literal_breaks=False), 'Dowen')
        for source in ('アサキム','ドーウィン','別の人'):
            self.assertEqual(canonicalize('Dowin',source), 'Dowin')

    def test_raster_requires_native_weapon(self):
        self.assertEqual(canonicalize('Luster Edge (Rapid Fire)','ラスター・エッジ(連射)'), 'Raster Edge (Rapid Fire)')
        self.assertEqual(canonicalize('Luster Edge','別の武器'), 'Luster Edge')

    def test_weapon_and_unit_in_same_field(self):
        self.assertEqual(canonicalize('Saber uses a Beam\nSaber; Fire Saber is different.',
            'セイバーガンダムとビームサーベル、ファイヤーセイバー',literal_breaks=False),
            'Saviour uses a Beam\nSaber; Fire Saber is different.')
        self.assertEqual(canonicalize('Fire Saber!', 'ファイヤーセイバー'), 'Fire Saber!')
        self.assertEqual(canonicalize('Tornado Saber', 'トルネード・セイバー'), 'Tornado Saber')
        self.assertEqual(canonicalize('Saber Claw', 'セイバー・クロー'), 'Saber Claw')

    def test_names_require_native_identity(self):
        self.assertEqual(canonicalize('Kids will help Alicia.', '子供達'), 'Kids will help Alicia.')
        self.assertEqual(canonicalize('Kouji and Elche.', '甲児とエルチ'), 'Koji and Elchi.')

    def test_both_break_encodings(self):
        self.assertEqual(canonicalize('Ready!\\nHora!', 'ホーラ'), 'Ready!\\nHola!')
        self.assertEqual(canonicalize(' Over\nSkill.\n New paragraph.', 'オーバー\nスキル',literal_breaks=False),
            ' Overskill.\n New paragraph.')


if __name__=='__main__':unittest.main()
