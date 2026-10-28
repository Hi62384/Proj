"""Launch the actual Windows CMD in an isolated private profile, verify and close only its window."""
import ctypes
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from ctypes import wintypes
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from assistant.storage import private_directory


def main():
    directory=private_directory()/'verification'/('launcher-'+time.strftime('%Y%m%d-%H%M%S'));directory.mkdir(parents=True)
    existing=private_directory()/'application.lock'
    if existing.exists():
        # QLockFile validates liveness itself; this test refuses to close another app.
        lines=existing.read_text().splitlines()
        if lines:
            try:
                import psutil
                if psutil.pid_exists(int(lines[0])):raise RuntimeError('An owner assistant instance is already open')
            except ImportError:raise RuntimeError('Existing assistant lock; close it before running isolated launcher acceptance')
    command=[os.environ.get('COMSPEC','cmd.exe'),'/d','/c',str(APP/'Start_Desktop_Assistant.cmd'),'--data-dir',str(directory/'state')]
    subprocess.run(command,check=True,cwd=APP)
    import win32gui,win32process,win32api
    hwnd=None;result={'cmd_exit_success':True}
    try:
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            matches=[]
            def enum(handle,extra):
                if win32gui.GetWindowText(handle)=='Codex Desktop Assistant' and win32gui.IsWindowVisible(handle):matches.append(handle)
            win32gui.EnumWindows(enum,None)
            if len(matches)==1:hwnd=matches[0];break
            time.sleep(.2)
        assert hwnd,'The CMD launcher did not expose a native window'
        _,pid=win32process.GetWindowThreadProcessId(hwnd)
        process=win32api.OpenProcess(0x1000,False,pid)
        try:
            query=ctypes.windll.kernel32.QueryFullProcessImageNameW
            query.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
            query.restype=wintypes.BOOL
            buffer=ctypes.create_unicode_buffer(32768);length=wintypes.DWORD(len(buffer))
            if not query(int(process),0,buffer,ctypes.byref(length)):raise ctypes.WinError()
            exe=buffer.value
        finally:process.Close()
        assert Path(exe).name.lower()=='pythonw.exe'
        result['native_pythonw_window']=True
        # It is a real UI, not merely a hidden server; only inspect its metadata.
        result['window_rect']=list(win32gui.GetWindowRect(hwnd))
        time.sleep(3)
        win32gui.PostMessage(hwnd,0x0010,0,0)
        deadline=time.monotonic()+45
        while time.monotonic()<deadline and win32gui.IsWindow(hwnd):time.sleep(.2)
        assert not win32gui.IsWindow(hwnd),'Owned test window did not close cleanly'
        result['normal_window_close']=True
        import sqlite3
        db=sqlite3.connect((directory/'state/assistant.sqlite3').as_uri()+'?mode=ro',uri=True)
        assert db.execute('select count(*) from conversations').fetchone()[0]>=1;db.close()
        result['persistent_state']=True;result['complete']=True
    finally:
        if hwnd and win32gui.IsWindow(hwnd):win32gui.PostMessage(hwnd,0x0010,0,0)
        (directory/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True);print('Private evidence: '+str(directory/'results.json'),flush=True)


if __name__=='__main__':main()
