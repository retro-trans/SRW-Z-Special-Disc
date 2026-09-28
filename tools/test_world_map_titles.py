"""Exercise pixel orientation, lossless packing, and caption clipping guards."""
import unittest
import numpy as np
from world_map_titles import unpack,pack,render,WIDTH,HEIGHT


class LocationPixels(unittest.TestCase):
    def test_corners_and_nibble_order(self):
        p=np.zeros((HEIGHT,WIDTH),np.uint8);p[0,0]=3;p[0,1]=12;p[-1,-2]=7;p[-1,-1]=14
        raw=pack(p)
        self.assertEqual(raw[-256],0xc3)
        self.assertEqual(raw[255],0xe7)
        np.testing.assert_array_equal(unpack(raw),p)

    def test_roundtrip_all_indexes(self):
        raw=bytes(range(256))*32
        self.assertEqual(pack(unpack(raw)),raw)

    def test_reject_invalid_pixels_and_overflow(self):
        with self.assertRaises(ValueError):unpack(b'')
        with self.assertRaises(ValueError):pack(np.full((HEIGHT,WIDTH),16,np.uint8))
        with self.assertRaises(ValueError):render('A'*200)
        with self.assertRaises(ValueError):render('one\ntwo')


if __name__=='__main__':unittest.main()
