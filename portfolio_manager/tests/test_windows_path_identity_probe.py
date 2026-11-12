"""Small host-side research probe; not an isolation or authorization implementation."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from portfolio_manager.tests.windows_path_research import DirectoryHandle


@unittest.skipUnless(os.name == 'nt', 'Windows path APIs are required')
class WindowsPathIdentityProbe(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='portfolio-path-research-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inside = self.root / 'allowed'
        self.outside = self.root / 'allowed-other'
        self.inside.mkdir()
        self.outside.mkdir()
        self.link = self.inside / 'junction'
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                            ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.kernel.CreateFileW.restype = wintypes.HANDLE
        self.kernel.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR,
                                                          wintypes.DWORD, wintypes.DWORD]
        self.kernel.GetFinalPathNameByHandleW.restype = wintypes.DWORD
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]

    def open_path(self, path):
        # Access 0 and share all: inspect only; follow junctions like a normal open.
        handle = self.kernel.CreateFileW(str(path), 0, 7, None, 3, 0x02000000, None)
        if handle == wintypes.HANDLE(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        return handle

    def nt_path_for_handle(self, handle):
        buffer = ctypes.create_unicode_buffer(32768)
        length = self.kernel.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 2)
        if not length or length >= len(buffer):
            raise ctypes.WinError(ctypes.get_last_error())
        return buffer.value.casefold()

    def nt_path(self, path):
        handle = self.open_path(path)
        try:
            return self.nt_path_for_handle(handle)
        finally:
            self.kernel.CloseHandle(handle)

    def junction(self, target):
        result = subprocess.run([os.environ.get('COMSPEC', r'C:\Windows\System32\cmd.exe'),
                                 '/d', '/c', 'mklink', '/J', str(self.link), str(target)],
                                capture_output=True, text=True, timeout=10)
        if result.returncode:
            self.skipTest('Disposable junction creation unavailable')
        self.addCleanup(lambda: self.link.rmdir() if self.link.exists() else None)

    def test_nt_handle_resolution_exposes_junction_escape(self):
        self.junction(self.outside)
        self.assertTrue(str(self.link).startswith(str(self.inside)))  # Lexical check alone misleads.
        resolved = self.nt_path(self.link)
        self.assertEqual(resolved, self.nt_path(self.outside))
        self.assertNotEqual(resolved, self.nt_path(self.inside))

    def test_retargeting_changes_the_next_open(self):
        self.junction(self.outside)
        before = self.nt_path(self.link)
        self.link.rmdir()
        self.junction(self.inside)
        self.assertNotEqual(before, self.nt_path(self.link))

    def test_open_handle_keeps_original_identity_when_junction_is_retargeted(self):
        self.junction(self.outside)
        handle = self.open_path(self.link)
        try:
            before = self.nt_path_for_handle(handle)
            self.link.rmdir()
            self.junction(self.inside)
            self.assertEqual(before, self.nt_path_for_handle(handle))
            self.assertNotEqual(before, self.nt_path(self.link))
        finally:
            self.kernel.CloseHandle(handle)

    def test_missing_directory_fails_to_open(self):
        with self.assertRaises(OSError):
            self.nt_path(self.inside / 'missing')

    def test_raw_device_path_is_not_a_win32_working_directory(self):
        # Run in a child so an unexpected success cannot alter the test runner cwd.
        code = ('import os,sys\ntry: os.chdir(sys.argv[1])\n'
                'except OSError: sys.exit(0)\nsys.exit(1)')
        result = subprocess.run([os.sys.executable, '-I', '-c', code, self.nt_path(self.inside)],
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, 'Raw NT device path unexpectedly accepted as Win32 cwd')

    def test_candidate_rejects_missing_and_non_directory(self):
        with self.assertRaises(OSError):
            DirectoryHandle(self.inside / 'missing')
        file = self.inside / 'file.txt'
        file.write_text('synthetic', encoding='utf-8')
        with self.assertRaises(NotADirectoryError):
            DirectoryHandle(file)

    def test_candidate_identity_tracks_open_object_across_junction_retarget(self):
        self.junction(self.outside)
        with DirectoryHandle(self.link) as old:
            old_identity = old.identity
            self.link.rmdir()
            self.junction(self.inside)
            with DirectoryHandle(self.link) as new:
                self.assertNotEqual(old_identity, new.identity)
                self.assertEqual(old_identity, old.identity)
        with self.assertRaises(ValueError):
            old.nt_name()

    def test_candidate_cwd_string_does_not_bind_later_open_to_handle(self):
        # Demonstrates why the prototype must not be used for authorization.
        with DirectoryHandle(self.outside) as old:
            name = old.experimental_cwd_name()
            moved = self.root / 'moved'
            self.outside.rename(moved)
            self.outside.mkdir()
            with DirectoryHandle(name) as reopened:
                self.assertNotEqual(old.identity, reopened.identity)

    def test_relative_open_stays_with_retained_root_after_replacement(self):
        child = self.outside / 'child'
        child.mkdir()
        with DirectoryHandle(child) as expected:
            identity = expected.identity
        with DirectoryHandle(self.outside) as root:
            self.outside.rename(self.root / 'moved')
            self.outside.mkdir()
            (self.outside / 'child').mkdir()
            self.assertEqual(identity, root.probe_open_child('child'))
            with DirectoryHandle(self.outside / 'child') as replacement:
                self.assertNotEqual(identity, replacement.identity)

    def test_relative_open_rejects_junction_and_bad_components(self):
        self.junction(self.outside)
        with DirectoryHandle(self.inside) as root:
            with self.assertRaises(OSError):
                root.probe_open_child('junction')
            for name in ('..', '.', 'a/b', 'a\\b', 'a:stream', '', 'name.', 'name '):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    root.probe_open_child(name)
            with self.assertRaises(OSError):
                root.probe_open_child('missing')

    def test_walk_retains_each_opened_parent_across_path_replacement(self):
        first = self.inside / 'first'
        first.mkdir()
        (first / 'second').mkdir()
        with DirectoryHandle(first / 'second') as expected:
            expected_id = expected.identity
        original = DirectoryHandle.probe_open_child_handle
        switched = []
        def replace_after_open(parent, name):
            child = original(parent, name)
            if name == 'first':
                first.rename(self.inside / 'moved')
                first.mkdir()
                (first / 'second').mkdir()
                switched.append(True)
            return child
        with DirectoryHandle(self.inside) as root, patch.object(DirectoryHandle, 'probe_open_child_handle', replace_after_open):
            with root.probe_walk(['first', 'second']) as found:
                self.assertEqual(found.identity, expected_id)
                self.assertTrue(switched)
                with DirectoryHandle(first / 'second') as replacement:
                    self.assertNotEqual(found.identity, replacement.identity)

    def test_walk_rejects_intermediate_junction_and_keeps_root_usable(self):
        first = self.inside / 'first'
        first.mkdir()
        link = first / 'escape'
        result = subprocess.run([os.environ.get('COMSPEC', r'C:\Windows\System32\cmd.exe'),
                                 '/d', '/c', 'mklink', '/J', str(link), str(self.outside)],
                                capture_output=True, timeout=10)
        if result.returncode:
            self.skipTest('Disposable junction creation unavailable')
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)
        with DirectoryHandle(self.inside) as root:
            with self.assertRaises(OSError):
                root.probe_walk(['first', 'escape'])
            with root.probe_walk(['first']) as allowed:
                self.assertIsNotNone(allowed.identity)
            with self.assertRaises(ValueError):
                root.probe_walk([])
            with self.assertRaises(ValueError):
                root.probe_walk('first')
            with self.assertRaises(ValueError):
                root.probe_walk(['first'] * 65)

    def test_child_handle_survives_parent_close_and_then_closes(self):
        (self.inside / 'child').mkdir()
        root = DirectoryHandle(self.inside)
        child = root.probe_open_child_handle('child')
        root.close()
        try:
            self.assertTrue(child.nt_name())
        finally:
            child.close()
        with self.assertRaises(ValueError):
            child.nt_name()

    def test_verified_anchor_rejects_replacement_and_junction(self):
        anchor = self.inside / 'anchor'
        anchor.mkdir()
        with DirectoryHandle(anchor) as expected:
            identity = expected.identity
        with DirectoryHandle(self.inside) as parent:
            with parent.probe_open_verified_child('anchor', identity) as verified:
                self.assertEqual(verified.identity, identity)
            anchor.rename(self.inside / 'old-anchor')
            anchor.mkdir()
            with self.assertRaises(OSError):
                parent.probe_open_verified_child('anchor', identity)
            self.junction(self.outside)
            with self.assertRaises(OSError):
                parent.probe_open_verified_child('junction', identity)

    def test_verified_file_read_rejects_replacement_hardlink_and_oversize(self):
        path = self.inside / 'example.txt'
        path.write_bytes(b'original')
        with DirectoryHandle(self.inside) as root:
            handle, info = root._probe_open_relative('example.txt', directory=False)
            root.kernel.CloseHandle(handle)
            identity = (info.volume, info.index_high, info.index_low)
            self.assertEqual(root.probe_read_verified_file('example.txt', identity, 8), b'original')
            with self.assertRaises(ValueError):
                root.probe_read_verified_file('example.txt', identity, 7)
            os.link(path, self.inside / 'hardlink.txt')
            with self.assertRaises(OSError):
                root.probe_read_verified_file('example.txt', identity, 8)
            (self.inside / 'hardlink.txt').unlink()
            path.rename(self.inside / 'old.txt')
            path.write_bytes(b'new')
            with self.assertRaises(OSError):
                root.probe_read_verified_file('example.txt', identity, 8)

    def test_identity_alone_does_not_prevent_in_place_content_changes(self):
        path = self.inside / 'example.txt'
        path.write_bytes(b'old')
        with DirectoryHandle(self.inside) as root:
            handle, info = root._probe_open_relative('example.txt', directory=False)
            root.kernel.CloseHandle(handle)
            identity = (info.volume, info.index_high, info.index_low)
            path.write_bytes(b'new')
            self.assertEqual(root.probe_read_verified_file('example.txt', identity, 3), b'new')


if __name__ == '__main__':
    unittest.main()
