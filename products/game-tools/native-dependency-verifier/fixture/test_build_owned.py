"""Run with: python test_build_owned.py <experiment-root>."""
from pathlib import Path
import sys
import tempfile
import unittest

import build_owned

ROOT = Path(sys.argv.pop(1)).resolve()


class BuilderSafetyTests(unittest.TestCase):
    def test_cycle_copy_omits_runnable_game(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'cycle'
            build_owned.copy_package(ROOT / 'export', target, build_owned.CYCLE_OMIT)
            self.assertTrue((target / 'extension.dll').is_file())
            self.assertFalse(any(item.suffix.lower() in ('.exe', '.pck') for item in target.iterdir()))
            with self.assertRaises(FileExistsError):
                build_owned.copy_package(ROOT / 'export', target, build_owned.CYCLE_OMIT)

    def test_cmd_metacharacters_are_rejected(self):
        for value in ('bad&path', 'bad|path', 'bad%path', 'bad!path', 'bad"path'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_owned.checked_cmd_path(value)


if __name__ == '__main__':
    unittest.main(verbosity=2)
