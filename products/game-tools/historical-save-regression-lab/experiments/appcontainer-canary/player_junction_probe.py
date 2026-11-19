"""Supervised synthetic Unity-player probe. Not a production sandbox."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,tempfile,time,uuid,os
import canary as ac
spec=importlib.util.spec_from_file_location('job_experiment',Path(__file__).resolve().parent.parent/'windows-job'/'job_experiment.py');job=importlib.util.module_from_spec(spec);spec.loader.exec_module(job)
here=Path(__file__).resolve().parent
build=here.parent/'standalone-probe-build-v11'
fixture=here.parent.parent/'SampleProject/Assets/Tests/Fixtures/v1.json'
def attempt(restricted,outer,mode):
 profile=None;sid=c.c_void_p();sidtext=w.LPWSTR();folder=w.LPWSTR();attrs=None;jobhandle=None;pi=ac.PROCESS_INFORMATION();tok=w.HANDLE();assigned=False
 temp=None;aliasdir=None;result={'restricted':restricted,'mode':mode,'state':'incomplete'}
 try:
  if restricted:
   name='GDM001.PlayerProbe.'+uuid.uuid4().hex;hr=ac.Profile(name,'GDM001 player probe','Temporary synthetic player experiment',None,0,c.byref(sid))
   if hr<0: raise OSError('profile HRESULT 0x%08x' % (hr & 0xffffffff))
   profile=name;ac.check(ac.SidString(sid,c.byref(sidtext)));hr=ac.Folder(sidtext,c.byref(folder))
   if hr<0: raise OSError('folder HRESULT 0x%08x' % (hr & 0xffffffff))
   root=Path(folder.value)
  else:
   temp=tempfile.TemporaryDirectory(prefix='player-control-',dir=outer);root=Path(temp.name)
  player=root/'Player';player.mkdir()
  for item in build.iterdir():
   if item.name=='build.log':continue
   if item.is_dir():shutil.copytree(item,player/item.name)
   else:shutil.copy2(item,player/item.name)
  inputpath=root/'synthetic.json';shutil.copyfile(fixture,inputpath);before=hashlib.sha256(inputpath.read_bytes()).hexdigest()
  output=root/'result.json';started=root/'restore-started.txt';holdmarker=root/'child-hold.txt';log=root/'player.log';targetdir=outer/('target-'+('restricted' if restricted else 'control'));targetdir.mkdir();target=targetdir/'canary.txt';target.write_text('original',encoding='utf-8');aliasdir=root/'junction-canary'
  command='mklink /J \"'+str(aliasdir)+'\" \"'+str(targetdir)+'\"'
  created=subprocess.run(r'C:\Windows\System32\cmd.exe /d /s /c "'+command+'"',capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
  if created.returncode!=0:raise RuntimeError('Junction creation failed: '+created.stderr.strip())
  GetAttrs=ac.api(ac.k,'GetFileAttributesW',w.DWORD,w.LPCWSTR)
  if not (GetAttrs(str(aliasdir)) & 0x400) or Path(os.path.realpath(aliasdir))!=targetdir.resolve():raise RuntimeError('Junction target verification failed')
  canary=aliasdir/'canary.txt'
  si=ac.STARTUPINFOEX();si.startup.cb=c.sizeof(si);flags=0x08000000|0x4
  if restricted:
   size=c.c_size_t();ac.Init(None,1,0,c.byref(size));attrs=c.create_string_buffer(size.value);ac.check(ac.Init(attrs,1,0,c.byref(size)))
   caps=ac.SECURITY_CAPABILITIES(sid,None,0,0);ac.check(ac.Update(attrs,0,0x00020009,c.byref(caps),c.sizeof(caps),None,None));si.attributes=c.cast(attrs,c.c_void_p);flags|=0x00080000
  else:si.startup.cb=c.sizeof(ac.STARTUPINFO)
  jobhandle=job.check(job.CreateJob(None,None));limits=job.EXTENDED_LIMIT();limits.BasicLimitInformation.LimitFlags=0x2000;job.check(job.SetJob(jobhandle,9,c.byref(limits),c.sizeof(limits)))
  exe=player/'SyntheticProbe.exe';args=[str(exe),'-batchmode','-nographics','-logFile',str(log),'--synthetic-fixture',str(inputpath),'--synthetic-result',str(output),'--synthetic-canary',str(canary),'--synthetic-mode',mode,'--synthetic-started',str(started),'--synthetic-hold-marker',str(holdmarker)]
  line=c.create_unicode_buffer(subprocess.list2cmdline(args));ac.check(ac.Create(str(exe),line,None,None,False,flags,None,str(player),c.byref(si.startup),c.byref(pi)))
  job.check(job.Assign(jobhandle,pi.process));assigned=True;ac.check(ac.OpenToken(pi.process,0x8,c.byref(tok)));flag=w.DWORD();size=w.DWORD();ac.check(ac.TokenInfo(tok,29,c.byref(flag),c.sizeof(flag),c.byref(size)))
  result['appcontainer_token']=bool(flag.value)
  if result['appcontainer_token']!=restricted:raise RuntimeError('Unexpected token')
  if job.Resume(pi.thread)==0xffffffff:raise c.WinError(c.get_last_error())
  wait=job.Wait(pi.process,70000 if mode=="hang-child" else 60000)
  childhandle=None
  if wait==0x102:
   result['state']='timeout';result['hold_marker_exists']=holdmarker.exists()
   if holdmarker.exists():
    parts=holdmarker.read_text().strip().split(',');result['child_report']=parts
    if len(parts)==3 and parts[0].isdigit():
     Open=ac.api(ac.k,'OpenProcess',w.HANDLE,w.DWORD,w.BOOL,w.DWORD)
     childhandle=Open(0x00100000,False,int(parts[0]));result['child_alive_before_termination']=bool(childhandle) and job.Wait(childhandle,0)==0x102
   job.check(job.TerminateJob(jobhandle,124))
   if childhandle:
    result['child_terminated_after_job']=job.Wait(childhandle,5000)==0;ac.Close(childhandle)
  elif wait==0:result['state']='exited';job.check(job.TerminateJob(jobhandle,125))
  else:raise c.WinError(c.get_last_error())
  if job.Wait(pi.process,5000)!=0:raise RuntimeError('player exit not confirmed')
  exitcode=w.DWORD();ac.check(ac.Code(pi.process,c.byref(exitcode)));result['exit_code']=exitcode.value
  end=time.monotonic()+5
  while True:
   info=job.ACCOUNTING();job.check(job.QueryJob(jobhandle,1,c.byref(info),c.sizeof(info),None))
   if info.ActiveProcesses==0:break
   if time.monotonic()>end:raise RuntimeError('job not empty')
   time.sleep(.01)
  result['job_total_processes']=info.TotalProcesses;result['job_active_processes']=info.ActiveProcesses
  result['fixture_unchanged']=hashlib.sha256(inputpath.read_bytes()).hexdigest()==before
  result['canary_exists']=canary.exists();result['target_contents']=target.read_text(encoding='utf-8');result['result_file_exists']=output.exists();result['restore_started']=started.exists()
  if output.exists():
   result['payload']=json.loads(output.read_text(encoding='utf-8-sig'));result['result_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
  if log.exists():
   raw=log.read_text(encoding='utf-8',errors='replace')[:131072]
   result['diagnostics']=[x.replace(str(root),'<temporary-profile>') for x in raw.splitlines() if any(w in x.lower() for w in ('error','exception','denied','fail'))][:15]
 except Exception as e:result['error']=type(e).__name__+': '+str(e)
 finally:
  if pi.process:
   if assigned and jobhandle:job.TerminateJob(jobhandle,126)
   else:ac.Terminate(pi.process,126)
   ac.Wait(pi.process,5000)
  if tok:ac.Close(tok)
  if pi.thread:ac.Close(pi.thread)
  if pi.process:ac.Close(pi.process)
  if jobhandle:job.Close(jobhandle)
  if attrs:ac.Delete(attrs)
  if folder:ac.LocalFree(c.cast(folder,c.c_void_p))
  if sidtext:ac.LocalFree(c.cast(sidtext,c.c_void_p))
  if sid:ac.Free(sid)
  alias_removed=True
  if aliasdir and os.path.lexists(aliasdir):
   try: os.rmdir(aliasdir)
   except OSError as e: alias_removed=False;result['alias_cleanup_error']=type(e).__name__+': '+str(e)
  result['junction_removed']=alias_removed
  if profile and alias_removed:
   hr=ac.DeleteProfile(profile);result['profile_deleted']=hr>=0
   if hr<0:result['cleanup_error']='HRESULT 0x%08x' % (hr&0xffffffff)
  if temp and alias_removed:temp.cleanup()
 return result
if __name__=='__main__':
 with tempfile.TemporaryDirectory(prefix='junction-canary-',dir=here) as d:
  outer=Path(d);results=[]
  for restricted in (False,True):
   result=attempt(restricted,outer,'pass');results.append(result);print(json.dumps(result,indent=2),flush=True)
  control,contained=results
  assert control.get('state')=='exited' and control.get('exit_code')==0 and control.get('target_contents')=='synthetic'
  assert contained.get('state')=='exited' and contained.get('exit_code')==0 and contained.get('appcontainer_token') and contained.get('target_contents')=='original' and contained.get('payload',{}).get('outsideWriteBlocked') and contained.get('profile_deleted') and contained.get('junction_removed')
  (build/'junction-observations.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
