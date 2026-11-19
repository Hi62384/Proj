"""Supervised synthetic Unity-player probe. Not a production sandbox."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,tempfile,time,uuid
import canary as ac
spec=importlib.util.spec_from_file_location('job_experiment',Path(__file__).resolve().parent.parent/'windows-job'/'job_experiment.py');job=importlib.util.module_from_spec(spec);spec.loader.exec_module(job)
here=Path(__file__).resolve().parent
build=here.parent/'nightrealm-savecode-build-v1'
fixture=here.parent.parent/'SampleProject/Assets/Tests/Fixtures/v1.json'
def attempt(restricted,outer,mode,fixture_name,potions,quest):
 profile=None;sid=c.c_void_p();sidtext=w.LPWSTR();folder=w.LPWSTR();attrs=None;jobhandle=None;pi=ac.PROCESS_INFORMATION();tok=w.HANDLE();assigned=False
 temp=None;result={'restricted':restricted,'mode':mode,'fixture':fixture_name,'state':'incomplete'}
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
  inputpath=root/'synthetic.json';shutil.copyfile(fixture.parent/fixture_name,inputpath);before=hashlib.sha256(inputpath.read_bytes()).hexdigest()
  output=root/'result.json';started=root/'restore-started.txt';holdmarker=root/'child-hold.txt';log=root/'player.log';canary=outer/('outside-'+('restricted' if restricted else 'control')+'-'+mode+'-'+fixture_name+'.txt')
  si=ac.STARTUPINFOEX();si.startup.cb=c.sizeof(si);flags=0x08000000|0x4
  if restricted:
   size=c.c_size_t();ac.Init(None,1,0,c.byref(size));attrs=c.create_string_buffer(size.value);ac.check(ac.Init(attrs,1,0,c.byref(size)))
   caps=ac.SECURITY_CAPABILITIES(sid,None,0,0);ac.check(ac.Update(attrs,0,0x00020009,c.byref(caps),c.sizeof(caps),None,None));si.attributes=c.cast(attrs,c.c_void_p);flags|=0x00080000
  else:si.startup.cb=c.sizeof(ac.STARTUPINFO)
  jobhandle=job.check(job.CreateJob(None,None));limits=job.EXTENDED_LIMIT();limits.BasicLimitInformation.LimitFlags=0x2000;job.check(job.SetJob(jobhandle,9,c.byref(limits),c.sizeof(limits)))
  exe=player/'SyntheticProbe.exe';args=[str(exe),'-batchmode','-nographics','-logFile',str(log),'--synthetic-fixture',str(inputpath),'--synthetic-result',str(output),'--synthetic-canary',str(canary),'--synthetic-mode',mode,'--synthetic-started',str(started),'--synthetic-hold-marker',str(holdmarker),'--expected-potions',str(potions),'--expected-quest',str(quest).lower()]
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
  result['canary_exists']=canary.exists();result['result_file_exists']=output.exists();result['restore_started']=started.exists()
  if output.exists():
   result['payload']=json.loads(output.read_text(encoding='utf-8-sig'));result['result_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
  save_dir=root/'saves'/'Synthetic'
  result['save_files']=sorted(x.name for x in save_dir.iterdir()) if save_dir.exists() else []
  if result['save_files']==['GameStatus','GameStatusOut','PlayerLevel','PlayerLevelOut']:
   values={x.name:json.loads(x.read_text(encoding='utf-8-sig')) for x in save_dir.iterdir()}
   result['roundtrip_verified']=values['GameStatus']==values['GameStatusOut'] and values['PlayerLevel']==values['PlayerLevelOut'] and values['GameStatus'].get('gold')==123 and values['PlayerLevel'].get('currentXp')==7
   result['save_hashes']={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in save_dir.iterdir()}
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
  if profile:
   hr=ac.DeleteProfile(profile);result['profile_deleted']=hr>=0
   if hr<0:result['cleanup_error']='HRESULT 0x%08x' % (hr&0xffffffff)
  if temp:temp.cleanup()
 return result
if __name__=='__main__':
 with tempfile.TemporaryDirectory(prefix='nightrealm-savecode-',dir=here) as d:
  outer=Path(d);results=[]
  for restricted in (False,True):
   result=attempt(restricted,outer,'pass','v1.json',3,False);results.append(result);print(json.dumps(result,indent=2),flush=True)
  assert all(x.get('exit_code')==0 and x.get('state')=='exited' and x.get('restore_started') and x.get('roundtrip_verified') and x.get('fixture_unchanged') and x.get('job_active_processes')==0 for x in results)
  assert results[0].get('canary_exists') and not results[0].get('appcontainer_token')
  assert results[1].get('appcontainer_token') and not results[1].get('canary_exists') and results[1].get('profile_deleted')
  (build/'nightrealm-savecode-observations.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
