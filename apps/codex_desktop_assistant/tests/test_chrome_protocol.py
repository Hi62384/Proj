import io
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.chrome_protocol import read_message,write_message,ProtocolError,MAX_MESSAGE


class NativeFramingTests(unittest.TestCase):
    def test_unicode_roundtrip_and_clean_eof(self):
        stream=io.BytesIO();write_message(stream,{'id':'1','text':'First\nSecond — ✓'})
        stream.seek(0);self.assertEqual(read_message(stream),{'id':'1','text':'First\nSecond — ✓'});self.assertIsNone(read_message(stream))

    def test_truncated_and_oversized_frames(self):
        for raw in (b'\x01',struct.pack('<I',12)+b'{}',struct.pack('<I',MAX_MESSAGE+1),struct.pack('<I',0)):
            with self.subTest(raw=raw),self.assertRaises(ProtocolError):read_message(io.BytesIO(raw))

    def test_malformed_ambiguous_and_nonobject_json(self):
        for raw in (b'[]',b'null',b'{"id":1,"id":2}',b'{"v":NaN}',b'\xff'):
            with self.subTest(raw=raw),self.assertRaises(ProtocolError):read_message(io.BytesIO(struct.pack('<I',len(raw))+raw))

    def test_nonfinite_output_rejected(self):
        with self.assertRaises(ProtocolError):write_message(io.BytesIO(),{'value':float('nan')})


if __name__=='__main__':unittest.main()
