"""Chrome-launched stdio relay. No webpage, filesystem or shell command API."""
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
from multiprocessing.connection import Client
sys.path.insert(0,str(Path(__file__).resolve().parent))
from assistant.chrome_protocol import read_message,write_message,VERSION,MAX_MESSAGE
from assistant.storage import private_directory


def main():
    if os.name!='nt':return 1
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(),os.O_BINARY);msvcrt.setmode(sys.stdout.fileno(),os.O_BINARY)
    settings=json.loads((private_directory()/'chrome-host'/'settings.json').read_text())
    allowed='chrome-extension://'+settings['extension_id']+'/'
    if not re.fullmatch(r'chrome-extension://[a-p]{32}/',allowed) or len(sys.argv)<2 or sys.argv[1]!=allowed:return 1
    write_lock=threading.Lock();connection=None;stopped=threading.Event()
    def output(value):
        with write_lock:write_message(sys.stdout.buffer,value)
    try:
        # Chrome starts us, not an arbitrary website. Opening the assistant is
        # a fixed owner-popup action, never an executable supplied by a message.
        first=read_message(sys.stdin.buffer)
        if first=={'type':'open_assistant','version':VERSION}:
            app=Path(__file__).resolve().parent
            subprocess.Popen([str(app/'.venv/Scripts/pythonw.exe'),str(app/'run.py')],cwd=app,creationflags=subprocess.CREATE_NO_WINDOW)
            output({'type':'opened','version':VERSION});return 0
        if first!={'type':'hello','version':VERSION}:return 1
        rendezvous=json.loads((private_directory()/'chrome-bridge.json').read_text())
        if rendezvous['version']!=VERSION:return 1
        connection=Client(rendezvous['address'],family='AF_PIPE',authkey=bytes.fromhex(rendezvous['key']))
        connection.send_bytes(json.dumps(first).encode());reply=json.loads(connection.recv_bytes(MAX_MESSAGE));output(reply)
        session=reply['session']
        def receive():
            try:
                while not stopped.is_set():output(json.loads(connection.recv_bytes(MAX_MESSAGE)))
            except Exception:
                stopped.set()
                # End the native host promptly, so Chrome marks its port closed.
                os._exit(0)
        threading.Thread(target=receive,daemon=True).start()
        while not stopped.is_set():
            message=read_message(sys.stdin.buffer)
            if message is None:break
            if message.get('session')!=session or message.get('type') not in ('event','response'):return 1
            connection.send_bytes(json.dumps(message,ensure_ascii=False).encode('utf-8'))
    except Exception:
        # Never disclose paths, keys, profile details or protocol payloads.
        try:output({'type':'error','error':'Assistant bridge unavailable. Open the assistant and reconnect.','version':VERSION})
        except Exception:pass
        return 1
    finally:
        stopped.set()
        if connection:connection.close()
    return 0


if __name__=='__main__':raise SystemExit(main())
