"""Disposable Windows tests: python test_safe_open.py <SafeOpenProbe.dll> <fixture-root>."""
import hashlib
import json
import os
from pathlib import Path
import queue
import stat
import subprocess
import sys
import tempfile
import threading
import unittest

PROBE = Path(sys.argv.pop(1)).resolve()
FIXTURES = Path(sys.argv.pop(1)).resolve()


def call(root, relative):
    return subprocess.run(['dotnet', str(PROBE), str(root), relative],
                          capture_output=True, text=True, timeout=15)


@unittest.skipUnless(os.name == 'nt', 'Windows-specific experimental probe')
class SafeOpenTests(unittest.TestCase):
    def test_owned_pe_is_hashed_and_parsed_through_open_handle(self):
        path = FIXTURES / 'export/extension.dll'
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        result = subprocess.run(['dotnet', str(PROBE), str(FIXTURES), r'export\extension.dll', '--pe'],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['sha256'], digest)
        self.assertEqual(report['pe']['machine'], '0x8664')
        self.assertIn('root.dll', report['pe']['imports'])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest().upper(), digest)

    def test_regular_file_and_rejected_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'inner').mkdir()
            file = root / 'inner/data.dll'
            file.write_bytes(b'owned fixture bytes')
            before = hashlib.sha256(file.read_bytes()).hexdigest().upper()
            result = call(root, r'inner\data.dll')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'OPENED ' + before)
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest().upper(), before)
            for invalid in (r'..\outside.dll', r'inner\..\data.dll', r'inner/data.dll', r'inner\data.dll:stream'):
                rejected = call(root, invalid)
                self.assertEqual(rejected.returncode, 2)
                self.assertFalse(rejected.stdout.strip())

    def test_hardlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'original.dll'
            source.write_bytes(b'owned')
            try:
                os.link(source, root / 'linked.dll')
            except OSError as error:
                self.skipTest('hard links unavailable: ' + str(error))
            result = call(root, 'linked.dll')
            self.assertEqual(result.returncode, 2)
            self.assertIn('Hardlinked', result.stderr)
            self.assertFalse(result.stdout.strip())

    def test_junction_in_root_or_child_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'outside'
            target.mkdir()
            sentinel = target / 'sentinel.dll'
            sentinel.write_bytes(b'outside sentinel')
            link = root / 'junction'
            result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(link), str(target)],
                                    capture_output=True, text=True)
            if result.returncode:
                self.skipTest('junction unavailable: ' + result.stderr)
            try:
                for scan_root, relative in ((root, r'junction\sentinel.dll'), (link, 'sentinel.dll')):
                    rejected = call(scan_root, relative)
                    self.assertEqual(rejected.returncode, 2, rejected.stderr)
                    self.assertFalse(rejected.stdout.strip())
                self.assertEqual(sentinel.read_bytes(), b'outside sentinel')
            finally:
                os.rmdir(link)

    def test_held_handles_block_replacement_in_disposable_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / 'inner'
            child.mkdir()
            file = child / 'data.dll'
            file.write_bytes(b'held bytes')
            process = subprocess.Popen(['dotnet', str(PROBE), str(root), r'inner\data.dll', '--hold'],
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, bufsize=1)
            received = queue.Queue()
            thread = threading.Thread(target=lambda: received.put(process.stdout.readline()), daemon=True)
            thread.start()
            try:
                try:
                    first = received.get(timeout=15).strip()
                except queue.Empty:
                    self.fail('probe did not report an opened handle')
                self.assertTrue(first.startswith('OPENED '), first)
                with self.assertRaises(OSError):
                    os.replace(file, child / 'moved.dll')
                with self.assertRaises(OSError):
                    os.replace(child, root / 'moved-inner')
                with self.assertRaises(OSError):
                    with file.open('wb') as stream:
                        stream.write(b'should not replace held contents')
                stdout, stderr = process.communicate('\n', timeout=15)
                self.assertEqual(process.returncode, 0, stderr)
                self.assertEqual(stdout.strip(), 'AFTER ' + first.split(' ', 1)[1])
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=15)

    def test_concurrent_junction_swaps_never_return_outside_fixture_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inner, parked, outside = root / 'inner', root / 'parked', root / 'outside'
            inner.mkdir()
            outside.mkdir()
            (inner / 'data.dll').write_bytes(b'inside fixture')
            (outside / 'data.dll').write_bytes(b'outside fixture')
            inside_hash = hashlib.sha256(b'inside fixture').hexdigest().upper()
            outside_hash = hashlib.sha256(b'outside fixture').hexdigest().upper()
            stop = threading.Event()
            failures = []
            swaps = []

            def swap():
                while not stop.is_set():
                    moved = False
                    try:
                        inner.rename(parked)
                        moved = True
                        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(inner), str(outside)],
                                                capture_output=True, timeout=10)
                        if result.returncode == 0:
                            swaps.append(1)
                            info = inner.lstat()
                            if not getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                                failures.append('expected junction')
                                return
                            os.rmdir(inner)  # remove only the verified junction, not its target
                    except OSError:
                        pass  # A held scan handle may legitimately block the swap.
                    finally:
                        if moved and parked.exists() and not inner.exists():
                            for _ in range(200):
                                try:
                                    parked.rename(inner)
                                    break
                                except OSError:
                                    threading.Event().wait(0.01)
                            else:
                                failures.append('could not restore owned test directory')
                                return

            thread = threading.Thread(target=swap, daemon=True)
            thread.start()
            try:
                for _ in range(24):
                    result = call(root, r'inner\data.dll')
                    self.assertIn(result.returncode, (0, 2), result.stderr)
                    if result.returncode == 0:
                        self.assertEqual(result.stdout.strip(), 'OPENED ' + inside_hash)
                        self.assertNotIn(outside_hash, result.stdout)
                    else:
                        self.assertFalse(result.stdout.strip())
            finally:
                stop.set()
                thread.join(timeout=20)
                if not thread.is_alive() and inner.exists():
                    info = inner.lstat()
                    if getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                        os.rmdir(inner)
                if not thread.is_alive() and parked.exists() and not inner.exists():
                    parked.rename(inner)
            self.assertFalse(thread.is_alive(), 'swap thread did not stop')
            self.assertFalse(failures, failures)
            self.assertTrue(swaps, 'no junction swaps occurred')
            self.assertEqual((outside / 'data.dll').read_bytes(), b'outside fixture')


if __name__ == '__main__':
    unittest.main(verbosity=2)
