"""Execute the installed Back Log converting copy; check guards and idempotence."""
import unittest
from sp_disc import ROOT, Disc, EXE
from backlog_runtime import apply, run_conv, planned, TABLE
from story_runtime import convert
from port_menu_runtime import NEW_FILE

BASE = ROOT/'work/output/SRW Z Special Disc English v0.3.16.iso'


class BacklogRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Disc(BASE, True).read(EXE)
        cls.exe, cls.report = apply(cls.base)
        cls.table = cls.exe[NEW_FILE+0x14c:NEW_FILE+0x14c+190]

    def check(self, text):
        raw = text.encode('cp932')
        out = run_conv(self.exe, raw)
        self.assertEqual(out, convert(raw, self.table))
        i = 0
        while i < len(out):                       # no Back Log control bytes survive
            b = out[i]
            if 0x81 <= b <= 0x9f or 0xe0 <= b <= 0xfc:
                i += 2
                continue
            self.assertFalse(0x2e <= b <= 0x3d, 'control byte %02x survives in %r' % (b, text))
            i += 1

    def test_screenshot_rows(self):
        self.check("Ziene\n「They're the unit that man had\norganized. Shall we be honored?」")
        self.check("Asakim\n「The time isn't ripe. Guests are arriving;\nI'll leave them to you.」")

    def test_every_printable_ascii(self):
        self.check(''.join(chr(c) for c in range(0x20, 0x7f)))

    def test_mixed_and_empty(self):
        self.check('「あい」 Funds 350,000 / Turn 5: ok.')
        self.check('')

    def test_already_converted_passes_through(self):
        once = run_conv(self.exe, b'A.B 1:2')
        self.assertEqual(run_conv(self.exe, once), once)

    def test_six_words_and_idempotent(self):
        self.assertEqual(len(self.report['patches']), 6)
        again, rep = apply(self.exe)
        self.assertEqual(again, self.exe)
        self.assertEqual(rep['patches'], [])
        self.assertEqual(TABLE, 0x81CABC)

    def test_guard_rejects_changed_preimage(self):
        bad = bytearray(self.base)
        at = min(planned(self.base))
        bad[at] ^= 0xFF
        with self.assertRaises(ValueError):
            apply(bytes(bad))


if __name__ == '__main__':
    unittest.main()
