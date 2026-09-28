"""Guard the episode texture format, full wording, and shared atlas edit scope."""
import unittest
import numpy as np
import episode_titles as e
from sp_disc import decode

class EpisodeTitlesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,_=e.native()

    def test_nibble_order_and_orientation(self):
        p=np.arange(32,dtype=np.uint8).reshape(2,16)%16
        self.assertEqual(e.pack(p)[:4],bytes.fromhex('10325476'))
        self.assertTrue(np.array_equal(e.unpack(e.pack(p),16,2),p))
        for i in range(6,27):
            raw=self.rows[i]['raw'][96:16480]
            self.assertEqual(e.pack(e.unpack(raw,512,64)),raw)

    def test_header_preserves_digits_and_unrelated_art(self):
        raw=self.rows[4]['raw'];new=e.header(raw)
        self.assertEqual(raw[:197376],new[:197376]);self.assertEqual(raw[202368:],new[202368:])
        a=e.unpack(raw[197376:202368],416,24);b=e.unpack(new[197376:202368],416,24)
        self.assertTrue(np.array_equal(a[:,:320],b[:,:320]));self.assertFalse(b[:,368:].any())
        encoded=e.compress_tail(self.rows[4]['stored'],raw,new)
        self.assertLessEqual(len(encoded),len(self.rows[4]['stored']));self.assertEqual(decode(encoded)[0],new)

    def test_oversized_or_invalid_text_rejected(self):
        for bad in ('','bad\nline','X'*1000,'日本語'):
            with self.subTest(text=bad[:20]),self.assertRaises(ValueError):e.render(bad)
        with self.assertRaises(ValueError):e.pack(np.full((2,16),16,np.uint8))

    def test_frozen_category_and_compression(self):
        changes,report,_=e.build()
        self.assertEqual(len(changes),21);self.assertEqual(report['count'],21)
        self.assertNotIn('9/20',[c['chunk'] for c in changes])
        for row in changes:
            self.assertEqual(len(row['payload']),row['end']-row['start'])
            self.assertEqual(e.sha(decode(row['payload'])[0]),row['decoded_sha256'])

if __name__=='__main__':unittest.main()
