"""Owner-clicked foreground handoff to installed Chrome, never a model input tool."""
import ctypes
from ctypes import wintypes
from pathlib import Path


def process_path(pid):
    kernel=ctypes.windll.kernel32
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x1000,False,pid)
    if not handle:return None
    try:
        text=ctypes.create_unicode_buffer(32768);size=wintypes.DWORD(len(text))
        return Path(text.value) if kernel.QueryFullProcessImageNameW(handle,0,text,ctypes.byref(size)) else None
    finally:kernel.CloseHandle(handle)


def allow_chrome_foreground():
    import win32gui,win32process,os
    roots=[Path(os.environ.get(name,''))/'Google/Chrome/Application/chrome.exe' for name in ('ProgramFiles','ProgramFiles(x86)','LOCALAPPDATA') if os.environ.get(name)]
    targets=set()
    def inspect(hwnd,_):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetClassName(hwnd).startswith('Chrome_WidgetWin'):
            pid=win32process.GetWindowThreadProcessId(hwnd)[1];path=process_path(pid)
            if path and any(path==root for root in roots):targets.add(pid)
    win32gui.EnumWindows(inspect,None)
    for pid in targets:ctypes.windll.user32.AllowSetForegroundWindow(pid)
