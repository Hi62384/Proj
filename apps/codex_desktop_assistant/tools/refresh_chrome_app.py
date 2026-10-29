"""Refresh this project's idle running app; never close an active task."""
import ctypes
import json
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from assistant.storage import private_directory


def main():
    directory=private_directory();dbpath=directory/'assistant.sqlite3'
    if dbpath.is_file():
        db=sqlite3.connect(dbpath.as_uri()+'?mode=ro',uri=True)
        try:
            if db.execute("SELECT COUNT(*) FROM conversations WHERE status IN ('Working','Waiting for User','Thinking','Acting')").fetchone()[0]:raise RuntimeError('Finish the active task before updating the app')
        finally:db.close()
    from pywinauto import Desktop
    candidates=Desktop(backend='uia').windows(title='Codex Desktop Assistant')
    if candidates:
        if len(candidates)!=1:raise RuntimeError('Multiple app windows found; select the intended instance manually')
        window=candidates[0];metadata=json.loads((directory/'chrome-bridge.json').read_text())
        if window.process_id()!=metadata['pid']:raise RuntimeError('Window identity does not match the registered private bridge')
        handle=window.handle;window.close();deadline=time.monotonic()+30
        while ctypes.windll.user32.IsWindow(handle) and time.monotonic()<deadline:time.sleep(.1)
        if ctypes.windll.user32.IsWindow(handle):raise RuntimeError('The app is still closing; no duplicate instance was started')
    subprocess.Popen([str(APP/'.venv/Scripts/pythonw.exe'),str(APP/'run.py')],cwd=APP,creationflags=subprocess.CREATE_NO_WINDOW)
    print('The idle app was refreshed. Existing conversations and browser sign-ins were preserved.')


if __name__=='__main__':main()
