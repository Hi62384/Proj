"""Windows handle-identity experiment. NEVER use this module for authorization.

The path returned here is a display/compatibility probe, not a durable capability.
Opening anything by that path can race with rename or reparse-point changes.
"""
import ctypes
from ctypes import wintypes
import os


class _FileInfo(ctypes.Structure):
    _fields_ = [('attributes', wintypes.DWORD), ('created', wintypes.FILETIME),
                ('accessed', wintypes.FILETIME), ('written', wintypes.FILETIME),
                ('volume', wintypes.DWORD), ('size_high', wintypes.DWORD),
                ('size_low', wintypes.DWORD), ('links', wintypes.DWORD),
                ('index_high', wintypes.DWORD), ('index_low', wintypes.DWORD)]


class _UnicodeString(ctypes.Structure):
    _fields_ = [('length', wintypes.USHORT), ('maximum', wintypes.USHORT), ('buffer', wintypes.LPWSTR)]


class _ObjectAttributes(ctypes.Structure):
    _fields_ = [('length', wintypes.ULONG), ('root', wintypes.HANDLE), ('name', ctypes.POINTER(_UnicodeString)),
                ('attributes', wintypes.ULONG), ('security', ctypes.c_void_p), ('quality', ctypes.c_void_p)]


class _IoStatus(ctypes.Structure):
    _fields_ = [('status', ctypes.c_void_p), ('information', ctypes.c_size_t)]


class DirectoryHandle:
    """Retain an open directory handle and inspect its identity for experiments."""
    def __init__(self, path, *, reject_final_reparse=False, read_security=False):
        if os.name != 'nt':
            raise OSError('This research helper requires Windows')
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                           ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.kernel.CreateFileW.restype = wintypes.HANDLE
        self.kernel.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(_FileInfo)]
        self.kernel.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR,
                                                         wintypes.DWORD, wintypes.DWORD]
        self.kernel.GetFinalPathNameByHandleW.restype = wintypes.DWORD
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        flags = 0x02000000 | (0x00200000 if reject_final_reparse else 0)
        access = 0x80 | 0x20 | (0x20000 if read_security else 0)
        self.handle = self.kernel.CreateFileW(os.fspath(path), access, 7, None, 3, flags, None)
        if self.handle == wintypes.HANDLE(-1).value:
            self.handle = None
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            info = _FileInfo()
            if not self.kernel.GetFileInformationByHandle(self.handle, ctypes.byref(info)):
                raise ctypes.WinError(ctypes.get_last_error())
            if not info.attributes & 0x10:
                raise NotADirectoryError(os.fspath(path))
            if reject_final_reparse and info.attributes & 0x400:
                raise OSError('Initial directory is a reparse point')
            self.identity = (info.volume, info.index_high, info.index_low)
            self.final_reparse_checked = reject_final_reparse
        except BaseException:
            self.close()
            raise

    def nt_name(self):
        if self.handle is None:
            raise ValueError('Directory handle is closed')
        buffer = ctypes.create_unicode_buffer(32768)
        length = self.kernel.GetFinalPathNameByHandleW(self.handle, buffer, len(buffer), 2)
        if not length or length >= len(buffer):
            raise ctypes.WinError(ctypes.get_last_error())
        if not buffer.value.startswith('\\Device\\'):
            raise ValueError('Unsupported NT path representation')
        return buffer.value

    def experimental_cwd_name(self):
        # This string does not bind later opens to this handle. Never authorize with it.
        return '\\\\?\\GLOBALROOT' + self.nt_name()

    def _probe_open_relative(self, name, *, directory, read_security=False):
        """Open one component without following reparse points for research only."""
        if self.handle is None:
            raise ValueError('Directory handle is closed')
        if (not isinstance(name, str) or not name or name in ('.', '..') or
                any(c in name for c in '/\\:\x00') or name.endswith(('.', ' '))):
            raise ValueError('Expected one ordinary child name')
        raw = ctypes.create_unicode_buffer(name)
        length = len(name.encode('utf-16-le'))
        if length > 65532:
            raise ValueError('Child name is too long')
        string = _UnicodeString(length, length + 2, ctypes.cast(raw, wintypes.LPWSTR))
        attrs = _ObjectAttributes(ctypes.sizeof(_ObjectAttributes), self.handle, ctypes.pointer(string),
                                  0x40 | 0x1000, None, None)  # case insensitive; do not follow reparse
        nt = ctypes.WinDLL('ntdll', use_last_error=True)
        nt.NtCreateFile.argtypes = [ctypes.POINTER(wintypes.HANDLE), wintypes.ULONG,
            ctypes.POINTER(_ObjectAttributes), ctypes.POINTER(_IoStatus), ctypes.c_void_p,
            wintypes.ULONG, wintypes.ULONG, wintypes.ULONG, wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG]
        nt.NtCreateFile.restype = ctypes.c_long
        handle = wintypes.HANDLE(); status_block = _IoStatus()
        desired = 0x80 | 0x100000 | (0x20 if directory else 0x1) | (0x20000 if read_security else 0)
        options = (0x1 if directory else 0x40) | 0x20 | 0x200000
        status = nt.NtCreateFile(ctypes.byref(handle), desired, ctypes.byref(attrs),
                                 ctypes.byref(status_block), None, 0, 7, 1,
                                 options, None, 0)
        if status < 0:
            raise OSError('Relative no-reparse open failed (NTSTATUS 0x%08x)' % (status & 0xffffffff))
        try:
            info = _FileInfo()
            if not self.kernel.GetFileInformationByHandle(handle, ctypes.byref(info)):
                raise ctypes.WinError(ctypes.get_last_error())
            if bool(info.attributes & 0x10) != directory or info.attributes & 0x400:
                raise OSError('Reparse point or wrong file type rejected')
            return handle.value, info
        except BaseException:
            self.kernel.CloseHandle(handle)
            raise

    def probe_open_child_handle(self, name, *, read_security=False):
        """Return a retained child handle for research; no authorization claim."""
        handle, info = self._probe_open_relative(name, directory=True, read_security=read_security)
        try:
            child = object.__new__(DirectoryHandle)
            child.kernel = self.kernel
            child.handle = handle
            child.identity = (info.volume, info.index_high, info.index_low)
            child.final_reparse_checked = True
            return child
        except BaseException:
            self.kernel.CloseHandle(handle)
            raise

    def probe_open_verified_child(self, name, expected_identity):
        """Compare with an identity supplied by a trusted provisioner, for research."""
        child = self.probe_open_child_handle(name)
        if child.identity != expected_identity:
            child.close()
            raise OSError('Directory identity changed')
        return child

    def probe_read_verified_file(self, name, expected_identity, limit):
        """Bounded handle read; identity must come from a separately trusted source."""
        if not isinstance(limit, int) or isinstance(limit, bool) or not 0 <= limit <= 1048576:
            raise ValueError('Invalid read limit')
        handle, info = self._probe_open_relative(name, directory=False)
        try:
            identity = (info.volume, info.index_high, info.index_low)
            if identity != expected_identity or info.links != 1:
                raise OSError('Unexpected file identity or hard link')
            self.kernel.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
                                             ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
            chunks = []
            total = 0
            while total <= limit:
                size = min(65536, limit + 1 - total)
                data = ctypes.create_string_buffer(size)
                count = wintypes.DWORD()
                if not self.kernel.ReadFile(handle, data, size, ctypes.byref(count), None):
                    raise ctypes.WinError(ctypes.get_last_error())
                if count.value == 0:
                    return b''.join(chunks)
                total += count.value
                if total > limit:
                    raise ValueError('File exceeds read limit')
                chunks.append(data.raw[:count.value])
            raise ValueError('File exceeds read limit')
        finally:
            self.kernel.CloseHandle(handle)

    def probe_open_child(self, name):
        with self.probe_open_child_handle(name) as child:
            return child.identity

    def probe_walk(self, components):
        """Walk from this pre-opened root; caller must close the returned handle."""
        if not isinstance(components, (tuple, list)) or not components or len(components) > 64:
            raise ValueError('Expected 1 to 64 separate path components')
        current = None
        try:
            parent = self
            for component in components:
                child = parent.probe_open_child_handle(component)
                if current is not None:
                    current.close()
                current = child
                parent = child
            return current
        except BaseException:
            if current is not None:
                current.close()
            raise

    def close(self):
        if self.handle is not None:
            self.kernel.CloseHandle(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()
