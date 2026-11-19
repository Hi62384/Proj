"""Supervised synthetic Unity-player probe. Not a production sandbox."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,tempfile,time,uuid,socket,threading
import canary as ac
spec=importlib.util.spec_from_file_location('job_experiment',Path(__file__).resolve().parent.parent/'windows-job'/'job_experiment.py');job=importlib.util.module_from_spec(spec);spec.loader.exec_module(job)
here=Path(__file__).resolve().parent
build=here.parent/'standalone-probe-build-v9'
fixture=here.parent.parent/'SampleProject/Assets/Tests/Fixtures/v1.json'
def attempt(restricted,outer,mode,port):
 profile=None;sid=c.c_void_p();sidtext=w.LPWSTR();folder=w.LPWSTR();attrs=None;jobhandle=None;pi=ac.PROCESS_INFORMATION();tok=w.HANDLE();assigned=False
 temp=None;result={'restricted':restricted,'mode':mode,'state':'incomplete'}
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
  output=root/'result.json';started=root/'restore-started.txt';childmarker=root/'child-marker.txt';childcanary=outer/('child-outside-'+('restricted' if restricted else 'control')+'.txt');log=root/'player.log';canary=outer/('outside-'+('restricted' if restricted else 'control')+'-'+mode+'.txt')
  si=ac.STARTUPINFOEX();si.startup.cb=c.sizeof(si);flags=0x08000000|0x4
  if restricted:
   size=c.c_size_t();ac.Init(None,1,0,c.byref(size));attrs=c.create_string_buffer(size.value);ac.check(ac.Init(attrs,1,0,c.byref(size)))
   caps=ac.SECURITY_CAPABILITIES(sid,None,0,0);ac.check(ac.Update(attrs,0,0x00020009,c.byref(caps),c.sizeof(caps),None,None));si.attributes=c.cast(attrs,c.c_void_p);flags|=0x00080000
  else:si.startup.cb=c.sizeof(ac.STARTUPINFO)
  jobhandle=job.check(job.CreateJob(None,None));limits=job.EXTENDED_LIMIT();limits.BasicLimitInformation.LimitFlags=0x2000;job.check(job.SetJob(jobhandle,9,c.byref(limits),c.sizeof(limits)))
  exe=player/'SyntheticProbe.exe';args=[str(exe),'-batchmode','-nographics','-logFile',str(log),'--synthetic-fixture',str(inputpath),'--synthetic-result',str(output),'--synthetic-canary',str(canary),'--synthetic-mode',mode,'--synthetic-started',str(started),'--synthetic-loopback-port',str(port),'--synthetic-child-marker',str(childmarker),'--synthetic-child-canary',str(childcanary)]
  line=c.create_unicode_buffer(subprocess.list2cmdline(args));ac.check(ac.Create(str(exe),line,None,None,False,flags,None,str(player),c.byref(si.startup),c.byref(pi)))
  job.check(job.Assign(jobhandle,pi.process));assigned=True;ac.check(ac.OpenToken(pi.process,0x8,c.byref(tok)));flag=w.DWORD();size=w.DWORD();ac.check(ac.TokenInfo(tok,29,c.byref(flag),c.sizeof(flag),c.byref(size)))
  result['appcontainer_token']=bool(flag.value)
  if result['appcontainer_token']!=restricted:raise RuntimeError('Unexpected token')
  if job.Resume(pi.thread)==0xffffffff:raise c.WinError(c.get_last_error())
  wait=job.Wait(pi.process,45000 if mode=="hang" else 60000)
  if wait==0x102:result['state']='timeout';job.check(job.TerminateJob(jobhandle,124))
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
  result['canary_exists']=canary.exists();result['child_canary_exists']=childcanary.exists();result['child_marker_exists']=childmarker.exists();result['result_file_exists']=output.exists();result['restore_started']=started.exists()
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
  if profile:
   hr=ac.DeleteProfile(profile);result['profile_deleted']=hr>=0
   if hr<0:result['cleanup_error']='HRESULT 0x%08x' % (hr&0xffffffff)
  if temp:temp.cleanup()
 return result
if __name__=='__main__':
 with tempfile.TemporaryDirectory(prefix='player-network-',dir=here) as d, socket.socket() as server:
  outer=Path(d);server.bind(('127.0.0.1',0));server.listen(4);server.settimeout(1);port=server.getsockname()[1];received=[];stop=threading.Event()
  def serve():
   while not stop.is_set():
    try: client,_=server.accept()
    except socket.timeout: continue
    except OSError: break
    with client: received.append('connection')
  thread=threading.Thread(target=serve,daemon=True);thread.start();results=[]
  try:
   for restricted in (False,True):
    result=attempt(restricted,outer,'pass',port);results.append(result);print(json.dumps(result,indent=2),flush=True)
   control,contained=results
   assert control.get('exit_code')==0 and control.get('payload',{}).get('loopbackConnected') and control.get('canary_exists')
   assert contained.get('exit_code')==0 and contained.get('appcontainer_token') and not contained.get('payload',{}).get('loopbackConnected') and not contained.get('canary_exists') and contained.get('profile_deleted')
   time.sleep(0.1)
   assert len(received)==1
   assert control.get('child_marker_exists') and control.get('child_canary_exists') and control['payload'].get('childStarted')
   assert contained.get('child_marker_exists') and not contained.get('child_canary_exists') and contained['payload'].get('childStarted')
   (build/'child-observations.json').write_text(json.dumps({'runs':results,'server_connections':len(received)},indent=2)+'\n',encoding='utf-8')
  finally:
   stop.set();server.close();thread.join(timeout=3)
