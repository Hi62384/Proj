"""Bounded, synthetic Unity startup probe; not a security certification."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import importlib.util, json, shutil, subprocess, time, uuid
import canary as ac

jobfile=Path(__file__).resolve().parent.parent/'windows-job'/'job_experiment.py'
spec=importlib.util.spec_from_file_location('job_experiment',jobfile); job=importlib.util.module_from_spec(spec); spec.loader.exec_module(job)
editor=Path(r'C:\Program Files\Unity\Hub\Editor\6000.6.9f1\Editor\Unity.exe')
source=Path(__file__).resolve().parent.parent/'CleanComparisonProject'
profile=None; sid=c.c_void_p(); sidtext=w.LPWSTR(); folder=w.LPWSTR(); attrs=None; jobhandle=None; pi=ac.PROCESS_INFORMATION(); tok=w.HANDLE(); assigned=False
result={'experiment':'synthetic Unity AppContainer startup', 'result':'incomplete'}
try:
 name='GDM001.UnityProbe.'+uuid.uuid4().hex
 hr=ac.Profile(name,'GDM001 Unity probe','Temporary synthetic Unity startup experiment',None,0,c.byref(sid))
 if hr<0: raise OSError('Create profile HRESULT 0x%08x' % (hr & 0xffffffff))
 profile=name
 ac.check(ac.SidString(sid,c.byref(sidtext)))
 hr=ac.Folder(sidtext,c.byref(folder))
 if hr<0: raise OSError('Get folder HRESULT 0x%08x' % (hr & 0xffffffff))
 root=Path(folder.value); project=root/'SyntheticUnityProject'; project.mkdir()
 for sub in ('Assets','Packages','ProjectSettings'):
  shutil.copytree(source/sub, project/sub)
 log=root/'unity-probe.log'
 attrs_size=c.c_size_t(); ac.Init(None,1,0,c.byref(attrs_size)); attrs=c.create_string_buffer(attrs_size.value)
 ac.check(ac.Init(attrs,1,0,c.byref(attrs_size))); caps=ac.SECURITY_CAPABILITIES(sid,None,0,0)
 ac.check(ac.Update(attrs,0,0x00020009,c.byref(caps),c.sizeof(caps),None,None))
 si=ac.STARTUPINFOEX(); si.startup.cb=c.sizeof(si); si.attributes=c.cast(attrs,c.c_void_p)
 jobhandle=job.check(job.CreateJob(None,None)); limits=job.EXTENDED_LIMIT();limits.BasicLimitInformation.LimitFlags=0x2000
 job.check(job.SetJob(jobhandle,9,c.byref(limits),c.sizeof(limits)))
 command=[str(editor),'-batchmode','-nographics','-projectPath',str(project),'-quit','-logFile',str(log)]
 line=c.create_unicode_buffer(subprocess.list2cmdline(command))
 ac.check(ac.Create(str(editor),line,None,None,False,0x08000000|0x00080000|0x4,None,r'C:\Windows\System32',c.byref(si.startup),c.byref(pi)))
 job.check(job.Assign(jobhandle,pi.process));assigned=True
 ac.check(ac.OpenToken(pi.process,0x0008,c.byref(tok))); flag=w.DWORD();size=w.DWORD()
 ac.check(ac.TokenInfo(tok,29,c.byref(flag),c.sizeof(flag),c.byref(size)));result['appcontainer_token']=bool(flag.value)
 if not flag.value: raise RuntimeError('Unity token was not AppContainer')
 if job.Resume(pi.thread)==0xffffffff: raise c.WinError(c.get_last_error())
 wait=job.Wait(pi.process,90000)
 if wait==0x102: result['result']='timeout';job.check(job.TerminateJob(jobhandle,124))
 elif wait==0: result['result']='exited';job.check(job.TerminateJob(jobhandle,125))
 else: raise c.WinError(c.get_last_error())
 if job.Wait(pi.process,5000)!=0: raise RuntimeError('Unity exit not confirmed')
 code=w.DWORD();ac.check(ac.Code(pi.process,c.byref(code))); result['exit_code']=code.value
 deadline=time.monotonic()+5
 while True:
  info=job.ACCOUNTING();job.check(job.QueryJob(jobhandle,1,c.byref(info),c.sizeof(info),None))
  if info.ActiveProcesses==0: break
  if time.monotonic()>deadline: raise RuntimeError('job still has active processes')
  time.sleep(.01)
 result['job_total_processes']=info.TotalProcesses;result['job_active_processes']=info.ActiveProcesses
 result['log_exists']=log.exists()
 if log.exists():
  raw=log.read_text(encoding='utf-8',errors='replace')[:131072]
  result['log_lines']=[line.replace(str(root),'<temporary-profile>') for line in raw.splitlines() if any(word in line.lower() for word in ('error','fail','license','package manager','exit','exception'))][:30]
except Exception as exc:
 result['error']=type(exc).__name__+': '+str(exc)
finally:
 if pi.process:
  if assigned and jobhandle: job.TerminateJob(jobhandle,126)
  else: ac.Terminate(pi.process,126)
  ac.Wait(pi.process,5000)
 if tok: ac.Close(tok)
 if pi.thread: ac.Close(pi.thread)
 if pi.process: ac.Close(pi.process)
 if jobhandle: job.Close(jobhandle)
 if attrs: ac.Delete(attrs)
 if folder: ac.LocalFree(c.cast(folder,c.c_void_p))
 if sidtext: ac.LocalFree(c.cast(sidtext,c.c_void_p))
 if sid: ac.Free(sid)
 if profile:
  hr=ac.DeleteProfile(profile);result['profile_deleted']=(hr>=0)
  if hr<0: result['cleanup_error']='Delete profile HRESULT 0x%08x' % (hr & 0xffffffff)
print(json.dumps(result,indent=2))
