"""Authenticated local JSON IPC. Only the fixed bundled controller can be started."""
import json
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
from multiprocessing.connection import Client
from assistant.storage import private_directory

APP=Path(__file__).resolve().parents[1]


class ControllerClient:
    def __init__(self,directory=None):
        self.directory=Path(directory or private_directory());self.identity=uuid.uuid4().hex;self.closed=threading.Event();self.heartbeat=None

    def request(self,operation,arguments=None,request_id=None):
        info=json.loads((self.directory/'computer-bridge.json').read_text())
        if info.get('version')!=1 or not info.get('address','').startswith(r'\\.\pipe\codex-computer-'):raise RuntimeError('Invalid local controller registration')
        # Windows can briefly have no listening instance between accepts. Retry
        # only opening the pipe; once a request is sent it is never replayed.
        deadline=time.monotonic()+2
        while True:
            try:
                connection=Client(info['address'],family='AF_PIPE',authkey=bytes.fromhex(info['key']));break
            except OSError as error:
                if getattr(error,'winerror',None) not in (2,231,233) or time.monotonic()>=deadline:raise
                time.sleep(.025)
        with connection:
            connection.send_bytes(json.dumps({'client':self.identity,'operation':operation,'arguments':arguments or {},'request':request_id or uuid.uuid4().hex},allow_nan=False).encode())
            if not connection.poll(330):raise TimeoutError('Bridge action timed out; inspect actual state before retrying')
            response=json.loads(connection.recv_bytes(2000000))
        if not response.get('ok'):raise RuntimeError(response.get('error','Controller failed'))
        return response['result']

    def ensure(self):
        try:return self.request('bridge_health')
        except (OSError,ValueError,RuntimeError):pass
        # Nonsecret diagnostics distinguish transport startup from Windows job
        # lifetime constraints. Never remove a job/sandbox or elevate a token.
        try:
            import ctypes,os,win32job
            from assistant.chrome_bridge import private_json
            inside=ctypes.c_int();ctypes.windll.kernel32.IsProcessInJob(ctypes.windll.kernel32.GetCurrentProcess(),None,ctypes.byref(inside))
            limits=win32job.QueryInformationJobObject(None,win32job.JobObjectExtendedLimitInformation) if inside.value else {}
            private_json(self.directory/'mcp-startup-diagnostics.json',{'mcp_pid':os.getpid(),'in_windows_job':bool(inside.value),'job_limit_flags':limits.get('BasicLimitInformation',{}).get('LimitFlags',0),'at':time.time()})
        except (OSError,ValueError):pass
        # Fixed app entrypoint only. No model-selected executable, elevation, shell
        # command, browser profile or alternate Codex inference process.
        subprocess.Popen([str(APP/'.venv/Scripts/pythonw.exe'),str(APP/'run.py'),'--bridge','--background'],cwd=APP,creationflags=subprocess.CREATE_NO_WINDOW)
        deadline=time.monotonic()+25
        while time.monotonic()<deadline:
            try:return self.request('bridge_health')
            except (OSError,ValueError,RuntimeError):time.sleep(.25)
        raise RuntimeError('Windows controller could not start. Open Start_Computer_Bridge.cmd and inspect its dashboard. No task action was replayed.')

    def start_heartbeat(self):
        def beat():
            while not self.closed.wait(15):
                try:self.request('bridge_mcp_heartbeat')
                except (OSError,ValueError,RuntimeError):pass  # never replay a mutating operation
        self.heartbeat=threading.Thread(target=beat,daemon=True);self.heartbeat.start()

    def close(self):
        self.closed.set()
        try:self.request('bridge_detach')
        except (OSError,ValueError,RuntimeError):pass
