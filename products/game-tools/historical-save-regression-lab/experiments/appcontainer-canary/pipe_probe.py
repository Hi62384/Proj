"""Synthetic named-pipe access checks. No Unity IPC endpoints are modified."""
import ctypes as c
from ctypes import wintypes as w
import uuid
import canary as ac

CreatePipe=ac.api(ac.k,'CreateNamedPipeW',w.HANDLE,w.LPCWSTR,w.DWORD,w.DWORD,w.DWORD,w.DWORD,w.DWORD,w.DWORD,c.c_void_p)
Connect=ac.api(ac.k,'ConnectNamedPipe',w.BOOL,w.HANDLE,c.c_void_p)
Read=ac.api(ac.k,'ReadFile',w.BOOL,w.HANDLE,c.c_void_p,w.DWORD,c.POINTER(w.DWORD),c.c_void_p)
ConvertSD=ac.api(ac.a,'ConvertStringSecurityDescriptorToSecurityDescriptorW',w.BOOL,w.LPCWSTR,w.DWORD,c.POINTER(c.c_void_p),c.POINTER(w.DWORD))
class SECURITY_ATTRIBUTES(c.Structure): _fields_=[('length',w.DWORD),('descriptor',c.c_void_p),('inherit',w.BOOL)]
INVALID=c.c_void_p(-1).value
for mode in ('control','denied','grant'):
 name=r'\\.\pipe\GDM001-canary-'+uuid.uuid4().hex
 handles=[]
 def make_pipe(sid=None):
  descriptor=c.c_void_p(); sidtext=w.LPWSTR(); sec=None
  try:
   if sid:
    ac.check(ac.SidString(sid,c.byref(sidtext)))
    # Only the unique temporary AppContainer SID is added to this disposable pipe.
    sddl='D:(A;;GA;;;SY)(A;;GA;;;OW)(A;;GA;;;'+sidtext.value+')S:(ML;;NW;;;LW)'
    ac.check(ConvertSD(sddl,1,c.byref(descriptor),None))
    attrs=SECURITY_ATTRIBUTES(c.sizeof(SECURITY_ATTRIBUTES),descriptor,False); sec=c.byref(attrs)
   handle=CreatePipe(name,1,1,1,4096,4096,0,sec)
   if handle == INVALID: raise c.WinError(c.get_last_error())
   handles.append(handle);connected=Connect(handle,None);err=c.get_last_error()
   if not connected and err not in (535,536): raise c.WinError(err)
  finally:
   if descriptor: ac.LocalFree(descriptor)
   if sidtext: ac.LocalFree(c.cast(sidtext,c.c_void_p))
 try:
  if mode!='grant': make_pipe()
  token,code,output=ac.run([r'C:\Windows\System32\cmd.exe','/d','/c','echo synthetic > "'+name+'"'],mode!='control',make_pipe if mode=='grant' else None)
  data=c.create_string_buffer(4096);n=w.DWORD();ok=Read(handles[0],data,len(data),c.byref(n),None)
  payload=data.raw[:n.value].decode(errors='replace') if ok else ''
  print(mode,'appcontainer=',token,'exit=',code,'output=',repr(output),'server_received=',repr(payload),flush=True)
  if token != (mode!='control'): raise AssertionError('unexpected token')
  if mode=='denied':
   if code==0 or payload: raise AssertionError('restricted process reached default pipe')
  elif code!=0 or 'synthetic' not in payload: raise AssertionError('allowed pipe did not receive data')
 finally:
  for handle in handles: ac.Close(handle)
