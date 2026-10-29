"""Authenticated, user-scoped Native Messaging rendezvous. No HTTP listener."""
import json
import os
import queue
import secrets
import threading
import time
import uuid
from pathlib import Path
from .chrome_protocol import VERSION,MAX_MESSAGE
from .permissions import Denied


def private_json(path,value):
    """Apply the current-user ACL before writing the rendezvous secret."""
    import win32api,win32con,win32file,win32security
    token=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_QUERY)
    try:sid=win32security.GetTokenInformation(token,win32security.TokenUser)[0]
    finally:token.Close()
    acl=win32security.ACL();acl.AddAccessAllowedAce(win32security.ACL_REVISION,win32con.GENERIC_ALL,sid)
    system=win32security.CreateWellKnownSid(win32security.WinLocalSystemSid,None)
    acl.AddAccessAllowedAce(win32security.ACL_REVISION,win32con.GENERIC_ALL,system)
    sd=win32security.SECURITY_DESCRIPTOR();sd.SetSecurityDescriptorDacl(True,acl,False)
    attributes=win32security.SECURITY_ATTRIBUTES();attributes.SECURITY_DESCRIPTOR=sd
    handle=win32file.CreateFile(str(path),win32con.GENERIC_WRITE|0x00040000,0,attributes,win32con.CREATE_ALWAYS,win32con.FILE_ATTRIBUTE_NORMAL,None)
    try:
        win32security.SetSecurityInfo(handle,win32security.SE_FILE_OBJECT,win32security.DACL_SECURITY_INFORMATION|win32security.PROTECTED_DACL_SECURITY_INFORMATION,None,None,acl,None)
        win32file.WriteFile(handle,json.dumps(value).encode('utf-8'))
    finally:handle.Close()


class UserPipeListener:
    """Current-user ACL plus PIPE_REJECT_REMOTE_CLIENTS (no SMB clients)."""
    def __init__(self,address,key):
        import win32api,win32con,win32pipe,win32security
        self.address,self.key=address,key;self.handle=None;self.closed=False
        token=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_QUERY)
        try:sid=win32security.GetTokenInformation(token,win32security.TokenUser)[0]
        finally:token.Close()
        acl=win32security.ACL();acl.AddAccessAllowedAce(win32security.ACL_REVISION,win32con.GENERIC_ALL,sid)
        sd=win32security.SECURITY_DESCRIPTOR();sd.SetSecurityDescriptorDacl(True,acl,False)
        self.attributes=win32security.SECURITY_ATTRIBUTES();self.attributes.SECURITY_DESCRIPTOR=sd
        self.create()

    def create(self):
        import win32pipe
        self.handle=win32pipe.CreateNamedPipe(self.address,win32pipe.PIPE_ACCESS_DUPLEX|0x40000000|0x00080000,
            win32pipe.PIPE_TYPE_MESSAGE|win32pipe.PIPE_READMODE_MESSAGE|win32pipe.PIPE_WAIT|0x8,
            1,65536,65536,1000,self.attributes)

    def accept(self):
        import win32pipe
        from multiprocessing.connection import PipeConnection,deliver_challenge,answer_challenge
        if self.closed:raise OSError('Pipe listener is closed')
        if self.handle is None:self.create()
        try:
            import _winapi
            overlapped=_winapi.ConnectNamedPipe(int(self.handle),overlapped=True)
            overlapped.GetOverlappedResult(True)
        except OSError as error:
            if getattr(error,'winerror',error.args[0])!=535:raise
        connection=PipeConnection(int(self.handle.Detach()));self.handle=None
        try:deliver_challenge(connection,self.key);answer_challenge(connection,self.key)
        except Exception:connection.close();raise
        return connection

    def close(self):
        self.closed=True
        if self.handle:
            try:self.handle.Close()
            except OSError:pass
            self.handle=None


class ChromeBridge:
    def __init__(self,directory,emit=lambda *args:None):
        self.directory=directory;self.emit=emit;self.lock=threading.RLock();self.connection=None
        self.pending={};self.offers={};self.session=None;self.closed=threading.Event();self.listener=None;self.write_lock=threading.Lock()
        self.started=False;self.error='Not connected';self.thread=None;self.verified_roundtrip_at=None

    def health(self,roundtrip=False):
        if not self.started:return
        state=self.status()
        value={'version':VERSION,'pid':os.getpid(),'updated':time.time(),'connected':state['connected'],'authorized_tab_count':len(state['tabs']),'error':state['error']}
        if roundtrip:self.verified_roundtrip_at=time.time()
        if self.verified_roundtrip_at:value['verified_roundtrip_at']=self.verified_roundtrip_at
        try:private_json(self.directory/'chrome-health.json',value)
        except Exception:pass  # Diagnostic persistence cannot break automation.

    def start(self):
        with self.lock:
            if self.started:return
            self.directory=Path(self.directory)
            self.directory.mkdir(parents=True,exist_ok=True)
            key=secrets.token_bytes(32);address=r'\\.\pipe\codex-assistant-'+uuid.uuid4().hex
            self.listener=UserPipeListener(address,key)
            private_json(self.directory/'chrome-bridge.json',{'version':VERSION,'address':address,'key':key.hex(),'pid':os.getpid()})
            self.started=True;self.thread=threading.Thread(target=self.serve,daemon=True,name='chrome-bridge');self.thread.start()

    def serve(self):
        while not self.closed.is_set():
            connection=None
            try:
                connection=self.listener.accept()
                if not connection.poll(5):raise Denied('Chrome handshake timed out')
                hello=json.loads(connection.recv_bytes(MAX_MESSAGE))
                if set(hello)!={'type','version'} or hello!={'type':'hello','version':VERSION}:raise Denied('Incompatible Chrome bridge version')
                with self.lock:
                    self.connection=connection;self.session=uuid.uuid4().hex;self.offers={};self.error=''
                    self.verified_roundtrip_at=None
                    connection.send_bytes(json.dumps({'type':'hello','version':VERSION,'session':self.session,'features':['grant_ack']}).encode())
                self.health()
                self.emit('chrome_status',None,self.status())
                while not self.closed.is_set():
                    if not connection.poll(.2):continue
                    message=json.loads(connection.recv_bytes(MAX_MESSAGE))
                    if not isinstance(message,dict) or message.get('session')!=self.session:raise Denied('Invalid Chrome session')
                    if message.get('type')=='response':
                        with self.lock:pending=self.pending.pop(message.get('id'),None)
                        if pending:pending.put(message)
                    elif message.get('type')=='event':self.event(message)
                    else:raise Denied('Unsupported Chrome message')
            except Exception as error:
                self.error=('Chrome disconnected: '+str(error))[:400] if isinstance(error,Denied) else 'Chrome disconnected ('+type(error).__name__+'). Pending actions were not replayed.'
            finally:
                with self.lock:
                    self.connection=None;self.session=None;self.offers={}
                    for pending in self.pending.values():pending.put({'ok':False,'error':'Chrome disconnected; completion may be uncertain. Inspect before continuing.'})
                    self.pending.clear()
                if connection:
                    try:connection.close()
                    except OSError:pass
                self.emit('chrome_status',None,self.status())
                self.health()

    def event(self,message):
        kind=message.get('event');tab=message.get('tab')
        if kind=='grant':
            if not isinstance(tab,dict) or type(tab.get('tab')) is not int or not isinstance(tab.get('origin'),str):raise Denied('Invalid Chrome tab grant')
            from .permissions import origin
            if origin(tab['origin'])!=tab['origin']:raise Denied('Invalid tab origin')
            frames=tab.get('frames',{'0':tab['origin']})
            if not isinstance(frames,dict) or len(frames)>32 or any(not str(k).isdigit() or not isinstance(v,str) or origin(v)!=v for k,v in frames.items()):raise Denied('Invalid Chrome frame authority')
            with self.lock:self.offers[tab['tab']]={**{k:tab[k] for k in ('tab','window','origin','manual') if k in tab},'frames':frames}
            self.send({'type':'grant_ack','session':self.session,'tab':tab['tab'],'origin':tab['origin']})
        elif kind in ('revoke','manual'):
            if type(tab) is not int:raise Denied('Invalid tab identity')
            with self.lock:
                if kind=='revoke':self.offers.pop(tab,None)
                elif tab in self.offers:self.offers[tab]['manual']=bool(message.get('enabled'))
        elif kind!='heartbeat':raise Denied('Unsupported extension event')
        if kind!='heartbeat':self.emit('chrome_status',None,self.status())
        self.health()

    def status(self):
        with self.lock:return {'connected':self.connection is not None,'session':self.session,'tabs':list(self.offers.values()),'error':self.error,'version':VERSION}

    def send(self,value):
        raw=json.dumps(value,ensure_ascii=False,allow_nan=False).encode('utf-8')
        if len(raw)>MAX_MESSAGE:raise Denied('Chrome message is too large')
        with self.lock:
            if not self.connection:raise Denied('Chrome extension is disconnected')
            connection=self.connection
        with self.write_lock:connection.send_bytes(raw)

    def request(self,operation,args=None,timeout=15,cancel=None,guard=None):
        ident=uuid.uuid4().hex;pending=queue.Queue(maxsize=1)
        with self.lock:
            if not self.session:raise Denied('Connect the Chrome extension first')
            session=self.session;self.pending[ident]=pending
        try:
            if guard:guard()
            self.send({'type':'request','version':VERSION,'session':session,'id':ident,'operation':operation,'arguments':args or {},'deadline':time.time()+timeout})
            deadline=time.monotonic()+timeout
            while time.monotonic()<deadline:
                if self.closed.is_set() or (cancel and cancel()) or (guard and guard() is False):raise Denied('Chrome action cancelled; inspect partial state before continuing')
                try:response=pending.get(timeout=.1)
                except queue.Empty:continue
                if not response.get('ok'):raise Denied(str(response.get('error','Chrome operation failed'))[:500])
                self.health(roundtrip=True)
                return response.get('result')
            raise Denied('Chrome operation timed out. It was not replayed; inspect the actual page before continuing.')
        finally:
            with self.lock:self.pending.pop(ident,None)
            try:self.send({'type':'cancel','session':session,'id':ident})
            except Exception:pass

    def stop_tabs(self):
        with self.lock:self.offers={}
        def dispatch():
            try:self.send({'type':'revoke_all','session':self.session})
            except Exception:pass
        threading.Thread(target=dispatch,daemon=True).start()

    def close(self):
        self.stop_tabs();self.closed.set()
        with self.lock:
            if self.connection:
                try:self.connection.close()
                except OSError:pass
        if self.listener:
            try:self.listener.close()
            except OSError:pass
        path=self.directory/'chrome-bridge.json'
        try:
            if json.loads(path.read_text())['pid']==os.getpid():path.unlink()
        except (OSError,ValueError,KeyError):pass
