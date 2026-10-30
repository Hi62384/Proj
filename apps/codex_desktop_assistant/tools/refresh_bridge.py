"""Development refresh of this idle controller, with identity and active-work checks."""
import ctypes
import json
import subprocess
import sys
import time
from pathlib import Path
from multiprocessing.connection import Client
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from assistant.storage import private_directory


def main():
    root=private_directory();info=json.loads((root/'computer-bridge.json').read_text())
    # Read-only compatibility health check for the first development protocol.
    with Client(info['address'],family='AF_PIPE',authkey=bytes.fromhex(info['key'])) as connection:
        connection.send_bytes(json.dumps({'client':'0'*32,'operation':'bridge_status','arguments':{},'request':'0'*32}).encode())
        if not connection.poll(5):raise RuntimeError('Controller health check timed out')
        response=json.loads(connection.recv_bytes(2000000))
    if not response.get('ok'):
        with Client(info['address'],family='AF_PIPE',authkey=bytes.fromhex(info['key'])) as connection:
            connection.send_bytes(json.dumps({'client':'0'*32,'operation':'bridge_status','arguments':{}}).encode())
            if not connection.poll(5):raise RuntimeError('Legacy health check timed out')
            response=json.loads(connection.recv_bytes(2000000))
    if not response.get('ok'):raise RuntimeError('Controller identity/health could not be verified')
    state=response['result']
    if state.get('active_tool') or state.get('pending_requests') or any(p.get('state')=='running' for p in state.get('projects',[])):raise RuntimeError('Finish or pause existing work before refreshing the controller')
    from pywinauto import Desktop
    window=Desktop(backend='uia').window(title='Codex Computer Bridge').wrapper_object()
    if window.process_id()!=info['pid']:raise RuntimeError('Controller window identity mismatch')
    handle=window.handle;next(c for c in window.descendants(control_type='Button') if c.window_text()=='Quit Bridge').invoke();deadline=time.monotonic()+30
    while ctypes.windll.user32.IsWindow(handle) and time.monotonic()<deadline:time.sleep(.1)
    if ctypes.windll.user32.IsWindow(handle):raise RuntimeError('Controller is still shutting down; no duplicate was started')
    subprocess.Popen([str(APP/'.venv/Scripts/pythonw.exe'),str(APP/'run.py'),'--bridge'],cwd=APP,creationflags=subprocess.CREATE_NO_WINDOW)
    print('Idle bridge refreshed. History, files and Chrome sign-ins preserved. If Stop was latched, it remains stopped until the owner resumes locally.')


if __name__=='__main__':main()
