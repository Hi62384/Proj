import hashlib
from pathlib import Path
import tempfile
import unittest
from multifile_stage import stage

class MultiFileStageTests(unittest.TestCase):
 def test_copies_pinned_files_and_preserves_source(self):
  with tempfile.TemporaryDirectory() as parent:
   root=Path(parent); source=root/'source'; scratch=root/'scratch';source.mkdir();scratch.mkdir()
   fixtures={'PlayerLevel':b'{"xp":7}', 'GameStatus':b'{"gold":4}'}
   for name,data in fixtures.items(): (source/name).write_bytes(data)
   expected={name:hashlib.sha256(data).hexdigest() for name,data in fixtures.items()}
   with stage(source,scratch,expected) as copied:
    copied=Path(copied)
    self.assertEqual({p.name:p.read_bytes() for p in copied.iterdir()},fixtures)
    (copied/'PlayerLevel').write_bytes(b'changed')
    self.assertEqual((source/'PlayerLevel').read_bytes(),fixtures['PlayerLevel'])
   self.assertFalse(copied.exists())
 def test_rejects_invalid_maps_and_bad_hash_without_creating_scratch(self):
  with tempfile.TemporaryDirectory() as parent:
   root=Path(parent);source=root/'source';scratch=root/'scratch';source.mkdir();scratch.mkdir();(source/'data').write_bytes(b'x')
   for expected in ({}, {'../data':'0'*64}, {'data':'0'*64}, {'DATA':'0'*64,'data':'0'*64}, {'data':'bad'}):
    with self.subTest(expected=expected), self.assertRaises(ValueError): stage(source,scratch,expected)
   self.assertEqual(list(scratch.iterdir()),[])

if __name__=='__main__':unittest.main(verbosity=2)
