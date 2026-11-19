"""Windows AppContainer exploratory canary; not a Unity sandbox or production code.

Creates a uniquely named temporary AppContainer profile and deletes it on exit.
Does not change ACLs; abnormal termination could leave the temporary profile behind.
Only disposable files under this script's workspace directory are touched.
"""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import subprocess, sys, tempfile, uuid, os, msvcrt, socket, threading

k=c.WinDLL('kernel32',use_last_error=True); a=c.WinDLL('advapi32',use_last_error=True); u=c.WinDLL('userenv',use_last_error=True)
def api(lib,name,ret,*args):
 f=getattr(lib,name);f.restype=ret;f.argtypes=args;return f
def check(v):
 if not v: raise c.WinError(c.get_last_error())
 return v
class STARTUPINFO(c.Structure):
 _fields_=[('cb',w.DWORD),('reserved',w.LPWSTR),('desktop',w.LPWSTR),('title',w.LPWSTR),('x',w.DWORD),('y',w.DWORD),('xs',w.DWORD),('ys',w.DWORD),('xc',w.DWORD),('yc',w.DWORD),('fill',w.DWORD),('flags',w.DWORD),('show',w.WORD),('cb2',w.WORD),('r2',c.c_void_p),('stdin',w.HANDLE),('stdout',w.HANDLE),('stderr',w.HANDLE)]
class STARTUPINFOEX(c.Structure): _fields_=[('startup',STARTUPINFO),('attributes',c.c_void_p)]
class PROCESS_INFORMATION(c.Structure): _fields_=[('process',w.HANDLE),('thread',w.HANDLE),('pid',w.DWORD),('tid',w.DWORD)]
class SECURITY_CAPABILITIES(c.Structure): _fields_=[('sid',c.c_void_p),('capabilities',c.c_void_p),('count',w.DWORD),('reserved',w.DWORD)]
Init=api(k,'InitializeProcThreadAttributeList',w.BOOL,c.c_void_p,w.DWORD,w.DWORD,c.POINTER(c.c_size_t))
Update=api(k,'UpdateProcThreadAttribute',w.BOOL,c.c_void_p,w.DWORD,c.c_size_t,c.c_void_p,c.c_size_t,c.c_void_p,c.c_void_p)
Delete=api(k,'DeleteProcThreadAttributeList',None,c.c_void_p)
Create=api(k,'CreateProcessW',w.BOOL,w.LPCWSTR,w.LPWSTR,c.c_void_p,c.c_void_p,w.BOOL,w.DWORD,c.c_void_p,w.LPCWSTR,c.POINTER(STARTUPINFO),c.POINTER(PROCESS_INFORMATION))
Wait=api(k,'WaitForSingleObject',w.DWORD,w.HANDLE,w.DWORD); Code=api(k,'GetExitCodeProcess',w.BOOL,w.HANDLE,c.POINTER(w.DWORD)); Close=api(k,'CloseHandle',w.BOOL,w.HANDLE)
Terminate=api(k,'TerminateProcess',w.BOOL,w.HANDLE,w.UINT)
Profile=api(u,'CreateAppContainerProfile',c.c_long,w.LPCWSTR,w.LPCWSTR,w.LPCWSTR,c.c_void_p,w.DWORD,c.POINTER(c.c_void_p)); DeleteProfile=api(u,'DeleteAppContainerProfile',c.c_long,w.LPCWSTR); Free=api(a,'FreeSid',c.c_void_p,c.c_void_p)
SidString=api(a,'ConvertSidToStringSidW',w.BOOL,c.c_void_p,c.POINTER(w.LPWSTR)); Folder=api(u,'GetAppContainerFolderPath',c.c_long,w.LPCWSTR,c.POINTER(w.LPWSTR)); LocalFree=api(k,'LocalFree',c.c_void_p,c.c_void_p)
OpenToken=api(a,'OpenProcessToken',w.BOOL,w.HANDLE,w.DWORD,c.POINTER(w.HANDLE)); TokenInfo=api(a,'GetTokenInformation',w.BOOL,w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.POINTER(w.DWORD))
def run(command, restricted, setup_callback=None):
 sid=c.c_void_p(); attr=None; pi=PROCESS_INFORMATION(); tok=w.HANDLE(); profile=None
 readfd,writefd=os.pipe(); os.set_handle_inheritable(msvcrt.get_osfhandle(writefd),True)
 try:
  si=STARTUPINFOEX(); si.startup.cb=c.sizeof(si)
  si.startup.flags=0x100; si.startup.stdin=msvcrt.get_osfhandle(writefd); si.startup.stdout=msvcrt.get_osfhandle(writefd); si.startup.stderr=msvcrt.get_osfhandle(writefd)
  flags=0x08000000
  if restricted:
   name='GDM001.Canary.'+uuid.uuid4().hex
   hr=Profile(name,'GDM001 synthetic canary','Temporary local isolation experiment',None,0,c.byref(sid))
   if hr < 0: raise OSError('CreateAppContainerProfile HRESULT 0x%08x' % (hr & 0xffffffff))
   profile=name
   if setup_callback is not None: setup_callback(sid)
   if '__PROFILE__' in command[3]:
    sidtext=w.LPWSTR(); folder=w.LPWSTR(); check(SidString(sid,c.byref(sidtext)))
    try:
     hr=Folder(sidtext,c.byref(folder))
     if hr < 0: raise OSError('GetAppContainerFolderPath HRESULT 0x%08x' % (hr & 0xffffffff))
     command=command[:3]+[command[3].replace('__PROFILE__',folder.value)]
    finally:
     if folder: LocalFree(c.cast(folder,c.c_void_p))
     LocalFree(c.cast(sidtext,c.c_void_p))
   size=c.c_size_t(); Init(None,1,0,c.byref(size)); attr=c.create_string_buffer(size.value)
   check(Init(attr,1,0,c.byref(size))); si.attributes=c.cast(attr,c.c_void_p)
   caps=SECURITY_CAPABILITIES(sid,None,0,0)
   check(Update(si.attributes,0,0x00020009,c.byref(caps),c.sizeof(caps),None,None)); flags|=0x00080000
  else: si.startup.cb=c.sizeof(STARTUPINFO)
  cmd=c.create_unicode_buffer(subprocess.list2cmdline(command[:3]) + ' "' + command[3] + '"')
  check(Create(command[0],cmd,None,None,True,flags,None,r"C:\Windows\System32",c.byref(si.startup),c.byref(pi)))
  try:
   check(OpenToken(pi.process,0x0008,c.byref(tok)))
   is_container=w.DWORD(); size=w.DWORD(); check(TokenInfo(tok,29,c.byref(is_container),c.sizeof(is_container),c.byref(size)))
   if Wait(pi.process,10000)!=0:
    Terminate(pi.process,125); Wait(pi.process,5000); raise TimeoutError('canary process did not exit')
   code=w.DWORD(); check(Code(pi.process,c.byref(code))); os.close(writefd); writefd=None
   output=os.read(readfd,4096).decode("utf-8",errors="replace").strip()
   return bool(is_container.value),code.value,output
  finally:
   if tok: Close(tok)
   Close(pi.thread);Close(pi.process)
 finally:
  if writefd is not None: os.close(writefd)
  os.close(readfd)
  if attr is not None and si.attributes: Delete(si.attributes)
  if sid: Free(sid)
  if profile:
   hr=DeleteProfile(profile)
   if hr < 0: raise OSError('DeleteAppContainerProfile failed for experiment profile %s: 0x%08x' % (profile,hr & 0xffffffff))

def main():
 root=Path(__file__).resolve().parent
 with tempfile.TemporaryDirectory(prefix='canary-',dir=root) as d:
  read=Path(d)/'read.txt'; read.write_text('synthetic',encoding='utf-8')
  write=Path(d)/'write.txt'; cmd=r'C:\Windows\System32\cmd.exe'
  for restricted in (False,True):
   for op in ('read','write'):
    if write.exists(): write.unlink()
    expr=('type "'+str(read)+'" >nul') if op=='read' else ('echo synthetic > "'+str(write)+'"')
    container,code,output=run([cmd,'/d','/c',expr],restricted)
    print(('container' if restricted else 'control'),op,'token_appcontainer=',container,'exit=',code,'write_exists=',write.exists(),'output=',repr(output),flush=True)
    if container != restricted: raise AssertionError('unexpected process token')
    if not restricted and (code!=0 or (op=='write' and not write.exists())): raise AssertionError('control failed')
    if restricted and (code==0 or (op=='write' and write.exists())): raise AssertionError('canary access was not denied')
  expression='echo synthetic > "__PROFILE__\\canary.txt" && type "__PROFILE__\\canary.txt"'
  container,code,output=run([cmd,'/d','/c',expression],True)
  print('container profile scratch token_appcontainer=',container,'exit=',code,'output=',repr(output),flush=True)
  if not container or code != 0 or 'synthetic' not in output: raise AssertionError('profile scratch unavailable')
  # Loopback only: a local server is the entire network destination. No internet.
  with socket.socket() as server:
   server.bind(('127.0.0.1',0)); server.listen(4); server.settimeout(8); port=server.getsockname()[1]
   stop=threading.Event(); requests=[]
   def serve():
    while not stop.is_set():
     try: client,_=server.accept()
     except socket.timeout: return
     except OSError: return
     with client:
      client.settimeout(3)
      try:
       requests.append(client.recv(4096)); client.sendall(b'HTTP/1.0 200 OK\r\nContent-Length: 9\r\n\r\nsynthetic')
      except OSError: pass
   thread=threading.Thread(target=serve,daemon=True);thread.start()
   try:
    for restricted in (False,True):
     expr='curl.exe --silent --show-error --connect-timeout 2 --max-time 3 http://127.0.0.1:%d/' % port
     container,code,output=run([cmd,'/d','/c',expr],restricted)
     print(('container' if restricted else 'control'),'loopback token_appcontainer=',container,'exit=',code,'output=',repr(output),flush=True)
     if container != restricted: raise AssertionError('unexpected network process token')
     if not restricted and (code!=0 or 'synthetic' not in output): raise AssertionError('loopback control failed')
     if restricted and code==0: raise AssertionError('restricted loopback unexpectedly connected')
   finally:
    stop.set(); server.close(); thread.join(timeout=9)

if __name__=='__main__': main()
