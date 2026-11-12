import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from portfolio_manager.tests.windows_profile_journal import ProfileJournal


class ProfileJournalTests(unittest.TestCase):
    def test_records_pending_creation_and_confirmed_ownership(self):
        with tempfile.TemporaryDirectory() as folder:
            journal = ProfileJournal(folder, 'a' * 32)
            name = 'PortfolioManager.A.' + 'a' * 32 + '.model'
            journal.update(pending=name, created=[])
            self.assertEqual(json.loads(journal.path.read_text())['pending'], name)
            with self.assertRaises(RuntimeError):
                journal.finish()
            journal.update(pending=None, created=[name])
            self.assertEqual(json.loads(journal.path.read_text())['created'], [name])
            journal.update(pending=None, created=[])
            journal.finish()
            self.assertFalse(journal.path.exists())

    def test_rejects_unowned_names_and_duplicate_records(self):
        with tempfile.TemporaryDirectory() as folder:
            journal = ProfileJournal(folder, 'b' * 32)
            with self.assertRaises(ValueError):
                journal.update(pending='another-profile', created=[])
            with self.assertRaises(FileExistsError):
                ProfileJournal(folder, 'b' * 32)
            journal.finish()

    def test_live_owner_lock_blocks_another_process(self):
        with tempfile.TemporaryDirectory() as folder:
            journal = ProfileJournal(folder, 'c' * 32)
            code = ('import msvcrt,sys\nf=open(sys.argv[1],"r+b")\n'
                    'try: msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)\n'
                    'except OSError: sys.exit(0)\nsys.exit(1)\n')
            try:
                child = subprocess.run([sys.executable, '-I', '-c', code, str(journal.lock_path)],
                                       capture_output=True, timeout=10)
                self.assertEqual(child.returncode, 0, 'Another process acquired the live owner lock')
            finally:
                journal.finish()


if __name__ == '__main__':
    unittest.main()
