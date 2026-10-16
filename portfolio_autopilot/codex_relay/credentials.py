"""Windows Credential Manager; tokens never written to configuration or logs."""
import ctypes
from ctypes import wintypes
import os

TARGET = "CodexRelay:Hi62384/Proj:Issues"


class Credential(ctypes.Structure):
    _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
                ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD),
                ("Attributes", ctypes.c_void_p), ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR)]


def library():
    if os.name != "nt":
        raise RuntimeError("Credential Manager requires Windows")
    lib = ctypes.WinDLL("advapi32", use_last_error=True)
    lib.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(Credential))]
    lib.CredReadW.restype = wintypes.BOOL
    lib.CredWriteW.argtypes = [ctypes.POINTER(Credential), wintypes.DWORD]
    lib.CredWriteW.restype = wintypes.BOOL
    lib.CredFree.argtypes = [ctypes.c_void_p]
    return lib


def get_token():
    lib = library()
    ptr = ctypes.POINTER(Credential)()
    if not lib.CredReadW(TARGET, 1, 0, ctypes.byref(ptr)):
        raise RuntimeError("Save an Issues-only GitHub token in Setup first")
    try:
        return ctypes.string_at(ptr.contents.CredentialBlob, ptr.contents.CredentialBlobSize).decode("utf-8")
    finally:
        lib.CredFree(ptr)


def save_token(token):
    if not token or len(token) > 2000 or any(c.isspace() for c in token):
        raise ValueError("Invalid token")
    lib = library()
    blob = (ctypes.c_ubyte * len(token.encode())).from_buffer_copy(token.encode())
    item = Credential(Type=1, TargetName=TARGET, CredentialBlobSize=len(blob),
                      CredentialBlob=blob, Persist=2, UserName="Codex Relay")
    if not lib.CredWriteW(ctypes.byref(item), 0):
        raise RuntimeError("Credential Manager could not save the token")
