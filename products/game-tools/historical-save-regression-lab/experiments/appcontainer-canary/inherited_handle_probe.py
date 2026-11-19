"""Demonstrate a deliberately inherited writable handle across AppContainer.
Only one disposable workspace file is inherited using an explicit handle list.
"""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import tempfile,uuid
import canary as ac
class SECURITY_ATTRIBUTES(c.Structure): _fields_=[('length',w.DWORD),('descriptor',c.c_void_p),('inherit',w.BOOL)]
CreateFile=ac.api(ac.k,'CreateFileW',w.HANDLE,w.LPCWSTR,w.DWORD,w.DWORD,c.POINTER(SECURITY_ATTRIBUTES),w.DWORD,w.DWORD,w.HANDLE)
invalid=c.c_void_p(-1).value
with tempfile.TemporaryDirectory(prefix='handle-canary-',dir=Path(__file__).resolve().parent) as directory:
 target=Path(directory)/'external.txt';sid=c.c_void_p();profile=None;attrs=None;handle=None;pi=ac.PROCESS_INFORMATION();tok=w.HANDLE()
 try:
  name='GDM001.HandleProbe.'+uuid.uuid4().hex;hr=ac.Profile(name,'GDM001 handle probe','Temporary synthetic inherited handle experiment',None,0,c.byref(sid))
  if hr<0:raise OSError('Profile HRESULT 0x%08x' % (hr&0xffffffff))
  profile=name;security=SECURITY_ATTRIBUTES(c.sizeof(SECURITY_ATTRIBUTES),None,True)
  handle=CreateFile(str(target),0x40000000,0,c.byref(security),1,0x80,None)
  if handle==invalid:handle=None;raise c.WinError(c.get_last_error())
  size=c.c_size_t();ac.Init(None,2,0,c.byref(size));attrs=c.create_string_buffer(size.value);ac.check(ac.Init(attrs,2,0,c.byref(size)))
  caps=ac.SECURITY_CAPABILITIES(sid,None,0,0);ac.check(ac.Update(attrs,0,0x00020009,c.byref(caps),c.sizeof(caps),None,None))
  handles=(w.HANDLE*1)(handle);ac.check(ac.Update(attrs,0,0x00020002,c.byref(handles),c.sizeof(handles),None,None))
  si=ac.STARTUPINFOEX();si.startup.cb=c.sizeof(si);si.attributes=c.cast(attrs,c.c_void_p);si.startup.flags=0x100
  si.startup.stdin=handle;si.startup.stdout=handle;si.startup.stderr=handle
  command=c.create_unicode_buffer(r'C:\Windows\System32\cmd.exe /d /c echo inherited-synthetic')
  ac.check(ac.Create(r'C:\Windows\System32\cmd.exe',command,None,None,True,0x08000000|0x00080000,None,r'C:\Windows\System32',c.byref(si.startup),c.byref(pi)))
  ac.check(ac.OpenToken(pi.process,0x8,c.byref(tok)));flag=w.DWORD();size2=w.DWORD();ac.check(ac.TokenInfo(tok,29,c.byref(flag),c.sizeof(flag),c.byref(size2)))
  if ac.Wait(pi.process,10000)!=0:ac.Terminate(pi.process,125);ac.Wait(pi.process,5000);raise TimeoutError('child timeout')
  code=w.DWORD();ac.check(ac.Code(pi.process,c.byref(code)));ac.Close(handle);handle=None
  contents=target.read_text(encoding='utf-8',errors='replace').strip()
  print('appcontainer=',bool(flag.value),'exit=',code.value,'inherited_handle_contents=',repr(contents),flush=True)
  assert flag.value and code.value==0 and contents=='inherited-synthetic'
 finally:
  if tok:ac.Close(tok)
  if pi.thread:ac.Close(pi.thread)
  if pi.process:ac.Close(pi.process)
  if handle:ac.Close(handle)
  if attrs:ac.Delete(attrs)
  if sid:ac.Free(sid)
  if profile:
   hr=ac.DeleteProfile(profile)
   if hr<0:raise OSError('Profile cleanup HRESULT 0x%08x' % (hr&0xffffffff))
