"""Check actual-disc pointer relocation and preservation of opaque/native data."""
import struct
import unittest
from battle_format import native,indexed,blocks
from battle_relocation import relocate


class RelocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,_,_,cls.chunks,cls.parsed=native()

    def test_every_indexed_block_accepts_longer_text(self):
        # Deliberately much longer than every source field; no Japanese byte
        # budget or fixed whole-pool capacity is used by this component.
        value=b'Full meaning beyond the original field. '*24
        for raw,parsed in zip(self.chunks,self.parsed):
            if not parsed['rows']:continue
            count=len(parsed['rows']);changes={0:value,count-1:value}
            out=relocate(raw,changes);rows=indexed(out,parsed['index'],count)
            self.assertEqual(rows[0]['raw'],value)
            self.assertEqual(rows[-1]['raw'],value)
            self.assertEqual(rows[0]['start'],rows[-1]['start'])
            self.assertGreaterEqual(rows[0]['start'],len(raw))
            self.assertEqual(out[parsed['pool']:len(raw)],raw[parsed['pool']:])
            restored=bytearray(out[:len(raw)])
            for i in changes:
                at=parsed['index']+8*i+4;restored[at:at+4]=raw[at:at+4]
            self.assertEqual(restored,raw)

    def test_empty_changes_and_empty_blocks_are_identical(self):
        for raw in self.chunks:self.assertEqual(relocate(raw,{}),raw)

    def test_rejects_invalid_targets_and_embedded_terminator(self):
        raw=self.chunks[0];count=len(self.parsed[0]['rows'])
        for changes in ({-1:b'no'},{count:b'no'},{0:b''},{0:b'a\0b'},{True:b'no'}):
            with self.assertRaises(ValueError):relocate(raw,changes)

    def test_repacked_segment_table_preserves_block_identity(self):
        chunks=[];offsets=[0]
        for raw,p in zip(self.chunks,self.parsed):
            out=relocate(raw,{0:b'English text relocated after the complete native block.'}if p['rows']else {})
            chunks.append(out);offsets.append(offsets[-1]+len(out))
        data=b''.join(chunks);seg=struct.pack('<%dI'%len(offsets),*offsets)
        got,readback=blocks(data,seg)
        self.assertEqual(tuple(offsets),got);self.assertEqual(chunks,readback)


if __name__=='__main__':unittest.main()
