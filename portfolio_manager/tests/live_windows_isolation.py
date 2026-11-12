"""Disposable Windows AppContainer availability probe; does not change product settings."""
import ctypes
from ctypes import wintypes
import argparse
import json
import msvcrt
import os
from pathlib import Path
import queue
import re
import socket
import subprocess
import shutil
import sys
import tempfile
import threading
import time
import uuid

sys.path.insert(0,str(Path.cwd()))
from portfolio_autopilot.codex_relay.config import Config
from portfolio_autopilot.codex_relay.codex import binary
from portfolio_autopilot.codex_relay.permissions import render
from portfolio_manager.development import _PYTHON_TEST_LOADER

k = ctypes.WinDLL('kernel32', use_last_error=True)
u = ctypes.WinDLL('userenv', use_last_error=True)
a = ctypes.WinDLL('advapi32', use_last_error=True)

class STARTUPINFO(ctypes.Structure):
    _fields_ = [('cb',wintypes.DWORD),('lpReserved',wintypes.LPWSTR),('lpDesktop',wintypes.LPWSTR),
        ('lpTitle',wintypes.LPWSTR),('dwX',wintypes.DWORD),('dwY',wintypes.DWORD),('dwXSize',wintypes.DWORD),
        ('dwYSize',wintypes.DWORD),('dwXCountChars',wintypes.DWORD),('dwYCountChars',wintypes.DWORD),
        ('dwFillAttribute',wintypes.DWORD),('dwFlags',wintypes.DWORD),('wShowWindow',wintypes.WORD),
        ('cbReserved2',wintypes.WORD),('lpReserved2',ctypes.c_void_p),('hStdInput',wintypes.HANDLE),
        ('hStdOutput',wintypes.HANDLE),('hStdError',wintypes.HANDLE)]
class STARTUPINFOEX(ctypes.Structure):
    _fields_ = [('StartupInfo',STARTUPINFO),('lpAttributeList',ctypes.c_void_p)]
class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [('hProcess',wintypes.HANDLE),('hThread',wintypes.HANDLE),('dwProcessId',wintypes.DWORD),('dwThreadId',wintypes.DWORD)]
class SECURITY_CAPABILITIES(ctypes.Structure):
    _fields_ = [('AppContainerSid',ctypes.c_void_p),('Capabilities',ctypes.c_void_p),('CapabilityCount',wintypes.DWORD),('Reserved',wintypes.DWORD)]
class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('Sid',ctypes.c_void_p),('Attributes',wintypes.DWORD)]
class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('nLength',wintypes.DWORD),('lpSecurityDescriptor',ctypes.c_void_p),('bInheritHandle',wintypes.BOOL)]

u.CreateAppContainerProfile.argtypes=[wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.LPCWSTR,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(ctypes.c_void_p)]
u.CreateAppContainerProfile.restype=ctypes.c_long
u.DeleteAppContainerProfile.argtypes=[wintypes.LPCWSTR];u.DeleteAppContainerProfile.restype=ctypes.c_long
u.DeriveAppContainerSidFromAppContainerName.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(ctypes.c_void_p)]
u.DeriveAppContainerSidFromAppContainerName.restype=ctypes.c_long
u.GetAppContainerFolderPath.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.LPWSTR)];u.GetAppContainerFolderPath.restype=ctypes.c_long
ctypes.windll.ole32.CoTaskMemFree.argtypes=[ctypes.c_void_p]
a.FreeSid.argtypes=[ctypes.c_void_p]
a.ConvertSidToStringSidW.argtypes=[ctypes.c_void_p,ctypes.POINTER(wintypes.LPWSTR)]
a.ConvertStringSidToSidW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(ctypes.c_void_p)]
a.OpenProcessToken.argtypes=[wintypes.HANDLE,wintypes.DWORD,ctypes.POINTER(wintypes.HANDLE)]
a.GetTokenInformation.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
k.LocalFree.argtypes=[ctypes.c_void_p]
k.InitializeProcThreadAttributeList.argtypes=[ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,ctypes.POINTER(ctypes.c_size_t)]
k.UpdateProcThreadAttribute.argtypes=[ctypes.c_void_p,wintypes.DWORD,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p]
k.DeleteProcThreadAttributeList.argtypes=[ctypes.c_void_p]
k.CreateProcessW.argtypes=[wintypes.LPCWSTR,wintypes.LPWSTR,ctypes.c_void_p,ctypes.c_void_p,wintypes.BOOL,wintypes.DWORD,ctypes.c_void_p,wintypes.LPCWSTR,ctypes.POINTER(STARTUPINFOEX),ctypes.POINTER(PROCESS_INFORMATION)]
k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
k.CloseHandle.argtypes=[wintypes.HANDLE]
k.TerminateProcess.argtypes=[wintypes.HANDLE,wintypes.UINT]
k.CreatePipe.argtypes=[ctypes.POINTER(wintypes.HANDLE),ctypes.POINTER(wintypes.HANDLE),ctypes.POINTER(SECURITY_ATTRIBUTES),wintypes.DWORD]
k.SetHandleInformation.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.DWORD]
k.ReadFile.argtypes=[wintypes.HANDLE,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD),ctypes.c_void_p]

def isolated_job_probe(executable, capabilities, *, memory_limit=False):
    """Synthetic suspended launch into a kill-on-close job; no inherited handles."""
    import win32api,win32con,win32job
    size=ctypes.c_size_t();k.InitializeProcThreadAttributeList(None,1,0,ctypes.byref(size))
    buffer=ctypes.create_string_buffer(size.value);attributes=ctypes.cast(buffer,ctypes.c_void_p)
    if not k.InitializeProcThreadAttributeList(attributes,1,0,ctypes.byref(size)):raise ctypes.WinError(ctypes.get_last_error())
    job=None;process=PROCESS_INFORMATION();observed=[]
    try:
        if not k.UpdateProcThreadAttribute(attributes,0,0x20009,ctypes.byref(capabilities),ctypes.sizeof(capabilities),None,None):raise ctypes.WinError(ctypes.get_last_error())
        job=win32job.CreateJobObject(None,'')
        limits=win32job.QueryInformationJobObject(job,win32job.JobObjectExtendedLimitInformation)
        limits['BasicLimitInformation']['LimitFlags']|=win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if memory_limit:
            limits['BasicLimitInformation']['LimitFlags']|=win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY
            limits['ProcessMemoryLimit']=48*1024*1024
        win32job.SetInformationJobObject(job,win32job.JobObjectExtendedLimitInformation,limits)
        keep={'SYSTEMROOT','WINDIR','COMSPEC','OS','PATHEXT','SYSTEMDRIVE','USERPROFILE','APPDATA','LOCALAPPDATA','HOMEDRIVE','HOMEPATH','TEMP','TMP'}
        env={key:value for key,value in os.environ.items() if key.upper() in keep};env['PATH']=r'C:\Windows\System32;C:\Windows'
        environment=ctypes.create_unicode_buffer('\0'.join(key+'='+value for key,value in sorted(env.items(),key=lambda item:item[0].upper()))+'\0\0')
        if memory_limit:
            code='import os,sys\nassert "PORTFOLIO_SYNTHETIC_SECRET" not in os.environ\ntry: value=bytearray(64*1024*1024)\nexcept MemoryError: sys.exit(42)\nsys.exit(1)\n'
        else:
            code='import os,subprocess,sys,time; assert "PORTFOLIO_SYNTHETIC_SECRET" not in os.environ; subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"]); time.sleep(60)'
        command=ctypes.create_unicode_buffer(subprocess.list2cmdline([str(executable),'-I','-B','-c',code]))
        startup=STARTUPINFOEX();startup.StartupInfo.cb=ctypes.sizeof(startup);startup.lpAttributeList=attributes
        if not k.CreateProcessW(str(executable),command,None,None,False,0x08080404,environment,r'C:\Windows\System32',ctypes.byref(startup),ctypes.byref(process)):
            raise ctypes.WinError(ctypes.get_last_error())
        win32job.AssignProcessToJobObject(job,process.hProcess)
        k.ResumeThread.argtypes=[wintypes.HANDLE];k.ResumeThread.restype=wintypes.DWORD
        if k.ResumeThread(process.hThread)==0xffffffff:raise ctypes.WinError(ctypes.get_last_error())
        if memory_limit:
            token=wintypes.HANDLE();is_container=wintypes.DWORD();returned=wintypes.DWORD()
            if not a.OpenProcessToken(process.hProcess,8,ctypes.byref(token)):raise ctypes.WinError(ctypes.get_last_error())
            try:
                if not a.GetTokenInformation(token,29,ctypes.byref(is_container),ctypes.sizeof(is_container),ctypes.byref(returned)) or is_container.value!=1:
                    raise RuntimeError('Synthetic memory process lacks an AppContainer token')
            finally:k.CloseHandle(token)
            if k.WaitForSingleObject(process.hProcess,10000)!=0:raise RuntimeError('Restricted memory probe timed out')
            result=wintypes.DWORD()
            if not k.GetExitCodeProcess(process.hProcess,ctypes.byref(result)) or result.value!=42:raise RuntimeError('Restricted memory allocation was not rejected')
            print('Restricted synthetic job memory limit: oversized allocation rejected')
            return
        deadline=time.monotonic()+8
        while time.monotonic()<deadline:
            pids=win32job.QueryInformationJobObject(job,win32job.JobObjectBasicProcessIdList)
            if len(pids)>=2:break
            time.sleep(.1)
        else:raise RuntimeError('Synthetic restricted child was not observed')
        for pid in pids:
            proc=win32api.OpenProcess(win32con.SYNCHRONIZE|win32con.PROCESS_QUERY_LIMITED_INFORMATION,False,pid)
            observed.append(proc)
            token=wintypes.HANDLE();is_container=wintypes.DWORD();returned=wintypes.DWORD()
            if not a.OpenProcessToken(int(proc),8,ctypes.byref(token)):raise ctypes.WinError(ctypes.get_last_error())
            try:
                if not a.GetTokenInformation(token,29,ctypes.byref(is_container),ctypes.sizeof(is_container),ctypes.byref(returned)) or is_container.value!=1:
                    raise RuntimeError('A synthetic job process lacks an AppContainer token')
            finally:k.CloseHandle(token)
        job.Close();job=None
        if any(k.WaitForSingleObject(int(proc),5000)!=0 for proc in observed):raise RuntimeError('A restricted synthetic process survived job closure')
        print('Restricted synthetic job: parent and child had AppContainer tokens and exited after job closure')
    finally:
        if job is not None:job.Close()
        if process.hProcess:
            if k.WaitForSingleObject(process.hProcess,5000)!=0:k.TerminateProcess(process.hProcess,1)
            k.CloseHandle(process.hProcess)
        if process.hThread:k.CloseHandle(process.hThread)
        for proc in observed:proc.Close()
        k.DeleteProcThreadAttributeList(attributes)

def appserver_probe(executable, allowed, capabilities, explicit_home=True, volume_guid_home=False, sentinel=None, synthetic=False):
    home=allowed/'codex-home';home.mkdir(exist_ok=True)
    workspace=allowed/'workspace';workspace.mkdir(exist_ok=True);(workspace/'AGENTS.md').write_text('Fictional probe',encoding='utf-8')
    config=Config(workspace=workspace,data_dir=allowed,execution_backend='windows',windows_sandbox='unelevated')
    (home/'config.toml').write_text(render(config),encoding='utf-8')
    security=SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES),None,True)
    def pipe():
        reader=wintypes.HANDLE();writer=wintypes.HANDLE()
        if not k.CreatePipe(ctypes.byref(reader),ctypes.byref(writer),ctypes.byref(security),0):raise ctypes.WinError(ctypes.get_last_error())
        return reader,writer
    stdin_read,stdin_write=pipe();stdout_read,stdout_write=pipe();stderr_read,stderr_write=pipe()
    for handle in (stdin_write,stdout_read,stderr_read):
        if not k.SetHandleInformation(handle,1,0):raise ctypes.WinError(ctypes.get_last_error())
    startup=STARTUPINFOEX();startup.StartupInfo.cb=ctypes.sizeof(startup)
    startup.StartupInfo.dwFlags=0x100;startup.StartupInfo.hStdInput=stdin_read
    startup.StartupInfo.hStdOutput=stdout_write;startup.StartupInfo.hStdError=stderr_write
    process=PROCESS_INFORMATION()
    allowed_names={'SYSTEMROOT','WINDIR','COMSPEC','OS','PATHEXT','USERNAME','USERDOMAIN','PROGRAMDATA',
                   'PROGRAMFILES','PROGRAMFILES(X86)','SYSTEMDRIVE'}
    env={key:value for key,value in os.environ.items() if key.upper() in allowed_names}
    env.update({'PATH':r'C:\Windows\System32;C:\Windows','USERPROFILE':str(allowed),
                'APPDATA':str(allowed),'LOCALAPPDATA':str(allowed),'HOMEDRIVE':allowed.drive,
                'HOMEPATH':str(allowed)[len(allowed.drive):],'CODEX_HOME':str(home),
                'TEMP':str(allowed),'TMP':str(allowed)})
    if volume_guid_home:
        volume_name=ctypes.create_unicode_buffer(1024)
        k.GetVolumeNameForVolumeMountPointW.argtypes=[wintypes.LPCWSTR,wintypes.LPWSTR,wintypes.DWORD]
        if not k.GetVolumeNameForVolumeMountPointW(home.anchor,volume_name,len(volume_name)):
            raise ctypes.WinError(ctypes.get_last_error())
        env['CODEX_HOME']=volume_name.value+str(home)[len(home.anchor):]
    if not explicit_home:env.pop('CODEX_HOME')
    if sentinel is not None:env['PORTFOLIO_TEST_SENTINEL']=str(sentinel)
    environment=ctypes.create_unicode_buffer('\0'.join(k+'='+v for k,v in sorted(env.items(),key=lambda x:x[0].upper()))+'\0\0')
    command=ctypes.create_unicode_buffer(subprocess.list2cmdline([str(executable),'app-server','--listen','stdio://']))
    try:
        size=ctypes.c_size_t();k.InitializeProcThreadAttributeList(None,2,0,ctypes.byref(size))
        buffer=ctypes.create_string_buffer(size.value);attributes=ctypes.cast(buffer,ctypes.c_void_p)
        if not k.InitializeProcThreadAttributeList(attributes,2,0,ctypes.byref(size)):raise ctypes.WinError(ctypes.get_last_error())
        try:
            if not k.UpdateProcThreadAttribute(attributes,0,0x20009,ctypes.byref(capabilities),ctypes.sizeof(capabilities),None,None):raise ctypes.WinError(ctypes.get_last_error())
            handles=(wintypes.HANDLE*3)(stdin_read.value,stdout_write.value,stderr_write.value)
            if not k.UpdateProcThreadAttribute(attributes,0,0x20002,handles,ctypes.sizeof(handles),None,None):raise ctypes.WinError(ctypes.get_last_error())
            startup.lpAttributeList=attributes
            if not k.CreateProcessW(str(executable),command,None,None,True,0x08080400,environment,str(home),ctypes.byref(startup),ctypes.byref(process)):
                raise ctypes.WinError(ctypes.get_last_error())
        finally:k.DeleteProcThreadAttributeList(attributes)
    except BaseException:
        for handle in (stdin_read,stdin_write,stdout_read,stdout_write,stderr_read,stderr_write):k.CloseHandle(handle)
        raise
    for handle in (stdin_read,stdout_write,stderr_write):k.CloseHandle(handle)
    input_stream=os.fdopen(msvcrt.open_osfhandle(stdin_write.value,0),'w',encoding='utf-8',buffering=1)
    output_stream=os.fdopen(msvcrt.open_osfhandle(stdout_read.value,os.O_RDONLY),'r',encoding='utf-8')
    error_stream=os.fdopen(msvcrt.open_osfhandle(stderr_read.value,os.O_RDONLY),'r',encoding='utf-8',errors='replace')
    messages=queue.Queue();errors=[];stderr_seen=threading.Event()
    def read_stdout():
        for line in output_stream:
            try:messages.put(json.loads(line))
            except ValueError:messages.put({'bad_protocol':True})
        messages.put({'eof':True})
    def read_stderr():
        for line in error_stream:
            errors.append(line.strip()[:400])
            if line.strip()=='synthetic stderr control':stderr_seen.set()
    threading.Thread(target=read_stdout,daemon=True).start();threading.Thread(target=read_stderr,daemon=True).start()
    def request(identifier,method,params):
        input_stream.write(json.dumps({'id':identifier,'method':method,'params':params})+'\n');input_stream.flush()
        while True:
            try:item=messages.get(timeout=12)
            except queue.Empty:raise RuntimeError('App-server response timed out; diagnostics: '+str(errors[-6:]))
            if item.get('eof'):raise RuntimeError('App-server exited before responding; diagnostics: '+str(errors[-6:]))
            if item.get('id')==identifier:return item
    try:
        result=request(1,'initialize',{'clientInfo':{'name':'portfolio_probe','title':'Portfolio isolated probe','version':'1'},'capabilities':{'experimentalApi':True}})
        if 'result' not in result:raise RuntimeError('App-server initialization was rejected')
        input_stream.write(json.dumps({'method':'initialized','params':{}})+'\n');input_stream.flush()
        profiles=request(2,'permissionProfile/list',{'cwd':str(workspace)})
        if 'error' in profiles:raise RuntimeError('Permission-profile listing rejected: '+str(profiles['error']))
        items=profiles.get('result',{}).get('data',[])
        profile_available=any(p.get('id')=='relay-locked' and p.get('allowed') for p in items)
        print(('Synthetic' if synthetic else 'Native')+' app-server initialized; restricted profile available:',profile_available)
        if not profile_available:raise RuntimeError('The required restricted profile is unavailable')
        result=request(3,'command/exec',{'command':[r'C:\Windows\System32\cmd.exe','/d','/c','echo PORTFOLIO_PROBE'],
                                        'cwd':str(workspace),'permissionProfile':'relay-locked','timeoutMs':10000})
        if 'error' in result:
            raise RuntimeError('Native restricted command probe rejected: '+str(result['error'])[:600])
        else:
            command_result=result.get('result',{})
            if command_result.get('exitCode')!=0 or 'PORTFOLIO_PROBE' not in command_result.get('stdout',''):
                raise RuntimeError('The restricted command probe did not produce its expected output')
            print(('Synthetic' if synthetic else 'Native')+' restricted command probe: passed')
        if synthetic and not stderr_seen.wait(3):raise RuntimeError('Synthetic app-server stderr control was not received')
    finally:
        input_stream.close();k.TerminateProcess(process.hProcess,1);k.WaitForSingleObject(process.hProcess,3000)
        k.CloseHandle(process.hThread);k.CloseHandle(process.hProcess)
        output_stream.close();error_stream.close()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-binary',help='Optional absolute test-only Codex executable; never installed or configured')
    parser.add_argument('--path-api-only',action='store_true',help='Run only the disposable AppContainer handle-path research probe')
    parser.add_argument('--namespace-only',action='store_true',help='Run only disposable read-only namespace replacement probes')
    parser.add_argument('--hold-namespace',action='store_true',help='Keep the disposable namespace parent open without delete sharing')
    parser.add_argument('--protect-profile-root',action='store_true',help='Make the disposable profile staging root read-only to its AppContainer')
    parser.add_argument('--protect-profile-parent',action='store_true',help='Also protect only the unique disposable profile parent')
    parser.add_argument('--replace-parent-grant',action='store_true',help='Remove old package grants from the disposable profile parent before adding read-only access')
    parser.add_argument('--split-layout',action='store_true',help='Test a separate writable synthetic runtime beside the read-only stage')
    parser.add_argument('--two-profiles',action='store_true',help='Compare a separate disposable test identity against synthetic runtime and staged data')
    parser.add_argument('--appserver-stdio-only',action='store_true',help='Test app-server pipe isolation using a fictional local protocol server')
    parser.add_argument('--appcontainer-job-only',action='store_true',help='Test disposable restricted parent/child job cancellation')
    parser.add_argument('--owned-profile-id',help='Use temporary profiles already owned by the acceptance controller')
    args=parser.parse_args()
    # Fictional canary only, scoped to this disposable test process.
    os.environ['PORTFOLIO_SYNTHETIC_SECRET']='fictional-'+uuid.uuid4().hex
    if args.owned_profile_id and not re.fullmatch(r'[0-9a-f]{32}',args.owned_profile_id):
        raise ValueError('Invalid acceptance profile identifier')
    name=('PortfolioManager.A.'+args.owned_profile_id+'.model' if args.owned_profile_id
          else 'PortfolioManager.Probe.'+uuid.uuid4().hex)
    sid=ctypes.c_void_p()
    hr=(u.DeriveAppContainerSidFromAppContainerName(name,ctypes.byref(sid)) if args.owned_profile_id
        else u.CreateAppContainerProfile(name,name,'Disposable isolation probe',None,0,ctypes.byref(sid)))
    if hr != 0:raise OSError('CreateAppContainerProfile failed: 0x%08x'%(hr & 0xffffffff))
    try:
        size=ctypes.c_size_t()
        k.InitializeProcThreadAttributeList(None,1,0,ctypes.byref(size))
        buffer=ctypes.create_string_buffer(size.value)
        attr=ctypes.cast(buffer,ctypes.c_void_p)
        if not k.InitializeProcThreadAttributeList(attr,1,0,ctypes.byref(size)):raise ctypes.WinError(ctypes.get_last_error())
        try:
            caps=SECURITY_CAPABILITIES(sid,None,0,0)
            if not k.UpdateProcThreadAttribute(attr,0,0x20009,ctypes.byref(caps),ctypes.sizeof(caps),None,None):raise ctypes.WinError(ctypes.get_last_error())
            def run(command_line, application='C:\\Windows\\System32\\cmd.exe', capabilities=None):
                startup=STARTUPINFOEX();startup.StartupInfo.cb=ctypes.sizeof(startup)
                read_handle=wintypes.HANDLE();write_handle=wintypes.HANDLE()
                security=SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES),None,True)
                if not k.CreatePipe(ctypes.byref(read_handle),ctypes.byref(write_handle),ctypes.byref(security),0):raise ctypes.WinError(ctypes.get_last_error())
                try:
                    if not k.SetHandleInformation(read_handle,1,0):raise ctypes.WinError(ctypes.get_last_error())
                    local_size=ctypes.c_size_t();k.InitializeProcThreadAttributeList(None,2,0,ctypes.byref(local_size))
                    local_buffer=ctypes.create_string_buffer(local_size.value);local_attr=ctypes.cast(local_buffer,ctypes.c_void_p)
                    if not k.InitializeProcThreadAttributeList(local_attr,2,0,ctypes.byref(local_size)):raise ctypes.WinError(ctypes.get_last_error())
                    try:
                        selected=capabilities if capabilities is not None else caps
                        if not k.UpdateProcThreadAttribute(local_attr,0,0x20009,ctypes.byref(selected),ctypes.sizeof(selected),None,None):raise ctypes.WinError(ctypes.get_last_error())
                        allowed_handles=(wintypes.HANDLE*1)(write_handle.value)
                        if not k.UpdateProcThreadAttribute(local_attr,0,0x20002,allowed_handles,ctypes.sizeof(allowed_handles),None,None):raise ctypes.WinError(ctypes.get_last_error())
                        startup.lpAttributeList=local_attr
                        startup.StartupInfo.dwFlags=0x100;startup.StartupInfo.hStdOutput=write_handle;startup.StartupInfo.hStdError=write_handle
                        process=PROCESS_INFORMATION()
                        command=ctypes.create_unicode_buffer(command_line)
                        keep={'SYSTEMROOT','WINDIR','COMSPEC','OS','PATHEXT','SYSTEMDRIVE','USERNAME','USERDOMAIN',
                              'PROGRAMDATA','PROGRAMFILES','PROGRAMFILES(X86)','USERPROFILE','APPDATA','LOCALAPPDATA',
                              'HOMEDRIVE','HOMEPATH','TEMP','TMP'}
                        clean_env={key:value for key,value in os.environ.items() if key.upper() in keep}
                        clean_env['PATH']=r'C:\Windows\System32;C:\Windows'
                        environment=ctypes.create_unicode_buffer('\0'.join(key+'='+value for key,value in sorted(clean_env.items(),key=lambda item:item[0].upper()))+'\0\0')
                        if not k.CreateProcessW(application,command,None,None,True,0x08080400,environment,'C:\\Windows\\System32',ctypes.byref(startup),ctypes.byref(process)):
                            raise ctypes.WinError(ctypes.get_last_error())
                    finally:k.DeleteProcThreadAttributeList(local_attr)
                except BaseException:
                    k.CloseHandle(read_handle);k.CloseHandle(write_handle);raise
                k.CloseHandle(write_handle)
                try:
                    token=wintypes.HANDLE();is_container=wintypes.DWORD();returned=wintypes.DWORD()
                    if not a.OpenProcessToken(process.hProcess,8,ctypes.byref(token)):raise ctypes.WinError(ctypes.get_last_error())
                    try:
                        if not a.GetTokenInformation(token,29,ctypes.byref(is_container),ctypes.sizeof(is_container),ctypes.byref(returned)):
                            raise ctypes.WinError(ctypes.get_last_error())
                        if is_container.value!=1:raise RuntimeError('Probe process does not have an AppContainer token')
                    finally:k.CloseHandle(token)
                    if k.WaitForSingleObject(process.hProcess,10000)!=0:
                        k.TerminateProcess(process.hProcess,1);k.WaitForSingleObject(process.hProcess,3000)
                        raise TimeoutError('Probe did not finish')
                    result=wintypes.DWORD()
                    if not k.GetExitCodeProcess(process.hProcess,ctypes.byref(result)):raise ctypes.WinError(ctypes.get_last_error())
                    data=ctypes.create_string_buffer(4096);read=wintypes.DWORD()
                    if k.ReadFile(read_handle,data,4096,ctypes.byref(read),None) and read.value:
                        print('Probe output:',data.raw[:read.value].decode(errors='replace'))
                    return result.value
                finally:
                    k.CloseHandle(process.hThread);k.CloseHandle(process.hProcess);k.CloseHandle(read_handle)
            assert run('C:\\Windows\\System32\\cmd.exe /d /c exit 42')==42
            print('Disposable AppContainer launch: passed')
            with tempfile.TemporaryDirectory(prefix='portfolio-native-probe-') as directory:
                protected=Path(directory)/'outside.txt'
                protected.write_text('fictional outside fixture',encoding='utf-8')
                command='C:\\Windows\\System32\\cmd.exe /d /c type "'+str(protected)+'"'
                if run(command)==0:raise RuntimeError('AppContainer could read the outside fixture')
                print('Outside fixture read: denied')
                sid_string=wintypes.LPWSTR()
                if not a.ConvertSidToStringSidW(sid,ctypes.byref(sid_string)):raise ctypes.WinError(ctypes.get_last_error())
                try:
                    sid_text=sid_string.value
                    location=wintypes.LPWSTR()
                    hr=u.GetAppContainerFolderPath(sid_string.value,ctypes.byref(location))
                    if hr:raise OSError('GetAppContainerFolderPath failed: 0x%08x'%(hr & 0xffffffff))
                    try: allowed=Path(location.value)/'LocalState'
                    finally: ctypes.windll.ole32.CoTaskMemFree(ctypes.cast(location,ctypes.c_void_p))
                finally:k.LocalFree(ctypes.cast(sid_string,ctypes.c_void_p))
                allowed.mkdir(parents=True,exist_ok=True)
                if args.path_api_only or args.namespace_only or args.appserver_stdio_only or args.appcontainer_job_only:
                    target=allowed/'path-target';target.mkdir();(target/'marker.txt').write_text('synthetic marker',encoding='utf-8')
                    link=allowed/'path-junction'
                    command=[os.environ.get('COMSPEC',r'C:\Windows\System32\cmd.exe'),'/d','/c','mklink','/J',str(link),str(target)]
                    created=subprocess.run(command,capture_output=True,text=True,timeout=10)
                    if created.returncode:raise RuntimeError('Could not create disposable junction: '+created.stderr[:200])
                    try:
                        (target/'nested').mkdir();(target/'nested'/'inner').mkdir()
                        escape=target/'escape'
                        created=subprocess.run([os.environ.get('COMSPEC',r'C:\Windows\System32\cmd.exe'),'/d','/c','mklink','/J',str(escape),str(protected.parent)],capture_output=True,text=True,timeout=10)
                        if created.returncode:raise RuntimeError('Could not create disposable escape junction')
                        runtime=allowed/'path-python';runtime.mkdir();base=Path(sys.base_prefix)
                        shutil.copy2(Path(__file__).with_name('windows_path_research.py'),allowed/'windows_path_research.py')
                        for name in ('python.exe','python3.dll','python311.dll','vcruntime140.dll','vcruntime140_1.dll'):
                            source=base/name
                            if source.is_file():shutil.copy2(source,runtime/name)
                        shutil.copytree(base/'Lib',runtime/'Lib',ignore=shutil.ignore_patterns('site-packages','__pycache__','test','tests','idlelib','tkinter','turtledemo','ensurepip','venv'))
                        shutil.copytree(base/'DLLs',runtime/'DLLs',ignore=shutil.ignore_patterns('__pycache__'))
                        executable=runtime/'python.exe'
                        if args.appcontainer_job_only:
                            isolated_job_probe(executable,caps)
                            isolated_job_probe(executable,caps,memory_limit=True)
                            return
                        if args.appserver_stdio_only:
                            synthetic=allowed/'synthetic-appserver';synthetic.mkdir()
                            synthetic_home=synthetic/'codex-home';synthetic_home.mkdir()
                            script='''import ctypes,json,os,sys\nfrom ctypes import wintypes\nif "PORTFOLIO_SYNTHETIC_SECRET" in os.environ:raise RuntimeError("unexpected environment canary")\nk=ctypes.WinDLL("kernel32",use_last_error=True);k.SetEvent.argtypes=[wintypes.HANDLE]\ntry:k.SetEvent(int(os.environ["PORTFOLIO_TEST_SENTINEL"]))\nexcept OSError:pass\nprint("synthetic stderr control",file=sys.stderr,flush=True)\nfor line in sys.stdin:\n request=json.loads(line);method=request.get("method");identifier=request.get("id")\n if identifier is None:continue\n if method=="initialize":result={}\n elif method=="permissionProfile/list":result={"data":[{"id":"relay-locked","allowed":True}]}\n elif method=="command/exec":result={"exitCode":0,"stdout":"PORTFOLIO_PROBE","stderr":""}\n else:raise RuntimeError("unexpected method")\n print(json.dumps({"id":identifier,"result":result}),flush=True)\n'''
                            (synthetic_home/'app-server').write_text(script,encoding='utf-8')
                            k.CreateEventW.argtypes=[ctypes.POINTER(SECURITY_ATTRIBUTES),wintypes.BOOL,wintypes.BOOL,wintypes.LPCWSTR]
                            k.CreateEventW.restype=wintypes.HANDLE
                            inherit=SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES),None,True)
                            sentinel=k.CreateEventW(ctypes.byref(inherit),True,False,None)
                            if not sentinel:raise ctypes.WinError(ctypes.get_last_error())
                            try:
                                control='''import ctypes,sys\nfrom ctypes import wintypes\nk=ctypes.WinDLL("kernel32",use_last_error=True);k.SetEvent.argtypes=[wintypes.HANDLE]\nif not k.SetEvent(int(sys.argv[1])):raise RuntimeError("sentinel missing")\n'''
                                result=subprocess.run([sys.executable,'-I','-c',control,str(sentinel)],close_fds=False,capture_output=True,timeout=10)
                                if result.returncode or k.WaitForSingleObject(sentinel,0)!=0:raise RuntimeError('Inheritable app-server sentinel control failed')
                                k.ResetEvent.argtypes=[wintypes.HANDLE]
                                if not k.ResetEvent(sentinel):raise ctypes.WinError(ctypes.get_last_error())
                                appserver_probe(executable,synthetic,caps,sentinel=sentinel,synthetic=True)
                                if k.WaitForSingleObject(sentinel,0)!=258:raise RuntimeError('Synthetic app-server inherited the sentinel')
                                print('Synthetic app-server: protocol streams worked; unlisted inheritable sentinel excluded')
                            finally:k.CloseHandle(sentinel)
                            return
                        if args.namespace_only:
                            import win32api,win32con,win32security
                            token=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_QUERY)
                            try:owner=win32security.ConvertSidToStringSid(win32security.GetTokenInformation(token,win32security.TokenUser)[0])
                            finally:token.Close()
                            parent=allowed/'immutable-parent';parent.mkdir()
                            for grant in ('*'+sid_text+':(OI)(CI)(RX)','*'+owner+':(OI)(CI)(F)','*S-1-5-18:(OI)(CI)(F)'):
                                result=subprocess.run(['icacls.exe',str(parent),'/grant:r',grant],capture_output=True,text=True)
                                if result.returncode:raise RuntimeError('Could not configure disposable namespace')
                            result=subprocess.run(['icacls.exe',str(parent),'/inheritance:r'],capture_output=True,text=True)
                            if result.returncode:raise RuntimeError('Could not protect disposable namespace')
                            stage=parent/'stage';stage.mkdir();(stage/'fixture.txt').write_text('original',encoding='utf-8')
                            if args.split_layout:
                                if not (args.protect_profile_root and args.protect_profile_parent and args.replace_parent_grant):
                                    raise ValueError('Split layout requires all disposable ancestor protections')
                                home=allowed/'synthetic-runtime';home.mkdir()
                                result=subprocess.run(['icacls.exe',str(home),'/inheritance:r'],capture_output=True,text=True)
                                if result.returncode:raise RuntimeError('Could not isolate disposable runtime folder')
                                result=subprocess.run(['icacls.exe',str(home),'/remove:g','*'+sid_text],capture_output=True,text=True)
                                if result.returncode:raise RuntimeError('Could not clear disposable runtime package grants')
                                for grant in ('*'+owner+':(OI)(CI)(F)','*S-1-5-18:(OI)(CI)(F)',
                                              '*'+sid_text+':(RX,W)','*'+sid_text+':(OI)(CI)(IO)(M)'):
                                    result=subprocess.run(['icacls.exe',str(home),'/grant',grant],capture_output=True,text=True)
                                    if result.returncode:raise RuntimeError('Could not configure disposable runtime access: '+result.stderr[:200])
                                from portfolio_manager.tests.windows_path_research import DirectoryHandle
                                with DirectoryHandle(stage) as trusted_stage:
                                    stage_identity=trusted_stage.identity
                                    file_handle,file_info=trusted_stage._probe_open_relative('fixture.txt',directory=False)
                                    trusted_stage.kernel.CloseHandle(file_handle)
                                    file_identity=(file_info.volume,file_info.index_high,file_info.index_low)
                            if args.protect_profile_root:
                                for grant in ('*'+sid_text+':(OI)(CI)(RX)','*'+owner+':(OI)(CI)(F)','*S-1-5-18:(OI)(CI)(F)'):
                                    result=subprocess.run(['icacls.exe',str(allowed),'/grant:r',grant],capture_output=True,text=True)
                                    if result.returncode:raise RuntimeError('Could not protect disposable profile root')
                                result=subprocess.run(['icacls.exe',str(allowed),'/inheritance:r'],capture_output=True,text=True)
                                if result.returncode:raise RuntimeError('Could not remove disposable root inheritance')
                            if args.protect_profile_parent:
                                if not args.protect_profile_root:raise ValueError('Profile parent protection requires protected profile root')
                                if args.replace_parent_grant:
                                    result=subprocess.run(['icacls.exe',str(allowed.parent),'/remove:g','*'+sid_text],capture_output=True,text=True)
                                    if result.returncode:raise RuntimeError('Could not remove old disposable package grants')
                                for grant in ('*'+sid_text+':(OI)(CI)(RX)','*'+owner+':(OI)(CI)(F)','*S-1-5-18:(OI)(CI)(F)'):
                                    result=subprocess.run(['icacls.exe',str(allowed.parent),'/grant:r',grant],capture_output=True,text=True)
                                    if result.returncode:raise RuntimeError('Could not protect disposable profile parent')
                                result=subprocess.run(['icacls.exe',str(allowed.parent),'/inheritance:r'],capture_output=True,text=True)
                                if result.returncode:raise RuntimeError('Could not remove disposable parent inheritance')
                            program='''import os,sys\np=sys.argv[1];s=os.path.join(p,"stage");f=os.path.join(s,"fixture.txt")\nif open(f,encoding="utf-8").read()!="original":raise RuntimeError("read control failed")\nfor label,op in (("file write",lambda:open(f,"w").write("changed")),("file delete",lambda:os.unlink(f)),("stage rename",lambda:os.rename(s,s+"-moved")),("parent rename",lambda:os.rename(p,p+"-moved"))):\n try:op();print(label+": allowed")\n except OSError:print(label+": denied")\n'''
                            if args.split_layout:
                                program+='''\nhome=os.path.join(os.path.dirname(p),"synthetic-runtime")\ntest=os.path.join(home,"state.txt")\nwith open(test,"w",encoding="utf-8") as f:f.write("state")\nwith open(test,"a",encoding="utf-8") as f:f.write("-updated")\nif open(test,encoding="utf-8").read()!="state-updated":raise RuntimeError("runtime data mismatch")\nos.unlink(test)\nsub=os.path.join(home,"subdir");os.mkdir(sub);os.rmdir(sub)\nprint("writable runtime create/update/delete: passed")\ntry:os.rename(home,home+"-moved")\nexcept OSError:print("writable runtime root rename: denied")\nelse:raise RuntimeError("writable runtime root was renamed")\n'''
                                program+='''\nlinkpath=os.path.join(home,"stage-link.txt")\ntry:os.link(os.path.join(s,"fixture.txt"),linkpath)\nexcept OSError:print("hard link to staged file: denied")\nelse:\n try:\n  with open(linkpath,"a",encoding="utf-8") as linked:linked.write("changed")\n except OSError:print("hard-link write to staged file: denied")\n else:raise RuntimeError("staged file changed via hard link")\n'''
                                program+='''\nimport sqlite3\ndbpath=os.path.join(home,"synthetic.sqlite")\nwith sqlite3.connect(dbpath) as db:\n mode=db.execute("PRAGMA journal_mode=WAL").fetchone()[0]\n if mode.lower()!="wal":raise RuntimeError("SQLite WAL mode unavailable")\n db.execute("CREATE TABLE example (value TEXT)")\n db.execute("INSERT INTO example VALUES (?)",("synthetic",))\nwith sqlite3.connect(dbpath) as db:\n if db.execute("SELECT value FROM example").fetchone()!=('synthetic',):raise RuntimeError("SQLite state mismatch")\nprint("writable runtime SQLite WAL create/reopen: passed")\n'''
                                program+='''\nimport json\nsys.path.insert(0,os.path.dirname(p))\nfrom windows_path_research import DirectoryHandle\nexpected_stage=tuple(json.loads(sys.argv[2]));expected_file=tuple(json.loads(sys.argv[3]))\nwith DirectoryHandle(p) as parent:\n with parent.probe_open_verified_child("stage",expected_stage) as stage:\n  if stage.probe_read_verified_file("fixture.txt",expected_file,16)!=b"original":raise RuntimeError("trusted fixture mismatch")\n try:parent.probe_open_verified_child("stage",(0,0,0))\n except OSError:print("staged identity and trusted fixture: matched; wrong identity rejected")\n else:raise RuntimeError("incorrect stage identity accepted")\n'''
                            if args.protect_profile_parent:
                                program+='''\nimport ctypes\nfrom ctypes import wintypes\nk=ctypes.WinDLL("kernel32",use_last_error=True)\nk.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE];k.CreateFileW.restype=wintypes.HANDLE\nk.CloseHandle.argtypes=[wintypes.HANDLE]\nfor path,access,label in ((os.path.dirname(p),0x10000,"staging root DELETE"),(os.path.dirname(p),0x40000,"staging root WRITE_DAC"),(os.path.dirname(p),0x80000,"staging root WRITE_OWNER"),(os.path.dirname(os.path.dirname(p)),0x40,"profile parent DELETE_CHILD"),(os.path.dirname(os.path.dirname(p)),0x40000,"profile parent WRITE_DAC")):\n h=k.CreateFileW(path,access,7,None,3,0x02000000,None)\n if h!=wintypes.HANDLE(-1).value:\n  k.CloseHandle(h);raise RuntimeError(label+" access unexpectedly granted")\n if ctypes.get_last_error()!=5:raise RuntimeError(label+" inconclusive: "+str(ctypes.get_last_error()))\n print(label+": denied")\n'''
                                program+='''\nprofile_parent=os.path.dirname(os.path.dirname(p))\nfor path,access,label in ((profile_parent,0x10000,"profile parent DELETE"),(os.path.dirname(profile_parent),0x40,"package parent DELETE_CHILD")):\n h=k.CreateFileW(path,access,7,None,3,0x02000000,None)\n if h!=wintypes.HANDLE(-1).value:\n  k.CloseHandle(h);print(label+": granted (higher ancestor unprotected)")\n else:print(label+": denied or unavailable; Windows error",ctypes.get_last_error())\n'''
                                program+='''\nancestor=os.path.dirname(profile_parent);level=0\nwhile True:\n results=[]\n for access in (0x10000,0x40):\n  h=k.CreateFileW(ancestor,access,7,None,3,0x02000000,None)\n  if h!=wintypes.HANDLE(-1).value:k.CloseHandle(h);results.append("granted")\n  else:results.append("error:"+str(ctypes.get_last_error()))\n print("ancestor level",level,"DELETE/DELETE_CHILD",*results)\n higher=os.path.dirname(ancestor)\n if higher==ancestor:break\n ancestor=higher;level+=1\n'''
                            held=None
                            if args.hold_namespace:
                                k.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
                                k.CreateFileW.restype=wintypes.HANDLE
                                held=k.CreateFileW(str(parent),0x80,3,None,3,0x02000000,None)
                                if held==wintypes.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
                            try:
                                argv=[str(executable),'-I','-B','-c',program,str(parent)]
                                if args.split_layout:argv.extend([json.dumps(stage_identity),json.dumps(file_identity)])
                                command=subprocess.list2cmdline(argv)
                                if run(command,str(executable))!=0:raise RuntimeError('Namespace probe did not complete')
                            finally:
                                if held is not None:k.CloseHandle(held)
                            moved=allowed/'immutable-parent-moved'
                            if moved.exists():
                                print('Host verification: parent replacement was permitted')
                                moved.rename(parent)
                                if args.protect_profile_root:raise RuntimeError('Protected parent was replaced')
                            else:print('Host verification: parent replacement was blocked')
                            if not (stage/'fixture.txt').is_file() or (stage/'fixture.txt').read_text(encoding='utf-8')!='original':
                                raise RuntimeError('Read-only fixture changed; namespace is not safe')
                            if (parent/'stage-moved').exists():raise RuntimeError('Read-only stage was moved')
                            print('Host verification: protected stage and content unchanged')
                            if args.two_profiles:
                                if not args.split_layout:raise ValueError('Two-profile probe requires split layout')
                                secret=home/'synthetic-private.txt';secret.write_text('fictional private state',encoding='utf-8')
                                test_name=('PortfolioManager.A.'+args.owned_profile_id+'.test' if args.owned_profile_id
                                           else 'PortfolioManager.Tests.'+uuid.uuid4().hex)
                                test_sid=ctypes.c_void_p()
                                hr=(u.DeriveAppContainerSidFromAppContainerName(test_name,ctypes.byref(test_sid)) if args.owned_profile_id
                                    else u.CreateAppContainerProfile(test_name,test_name,'Disposable separate test identity',None,0,ctypes.byref(test_sid)))
                                if hr:raise OSError('Could not create disposable test profile: 0x%08x'%(hr & 0xffffffff))
                                try:
                                    text_sid=wintypes.LPWSTR()
                                    if not a.ConvertSidToStringSidW(test_sid,ctypes.byref(text_sid)):raise ctypes.WinError(ctypes.get_last_error())
                                    try:test_sid_text=text_sid.value
                                    finally:k.LocalFree(ctypes.cast(text_sid,ctypes.c_void_p))
                                    for path in (allowed.parent,allowed,parent,stage,stage/'fixture.txt'):
                                        grant='*'+test_sid_text+':'+('(RX)' if path.is_file() else '(OI)(CI)(RX)')
                                        result=subprocess.run(['icacls.exe',str(path),'/grant',grant],capture_output=True,text=True)
                                        if result.returncode:raise RuntimeError('Could not grant test-only fixture access')
                                    result=subprocess.run(['icacls.exe',str(runtime),'/grant','*'+test_sid_text+':(OI)(CI)(RX)','/T'],capture_output=True,text=True,timeout=30)
                                    if result.returncode:raise RuntimeError('Could not grant test-only synthetic interpreter access')
                                    size2=ctypes.c_size_t();k.InitializeProcThreadAttributeList(None,1,0,ctypes.byref(size2))
                                    buffer2=ctypes.create_string_buffer(size2.value);attr2=ctypes.cast(buffer2,ctypes.c_void_p)
                                    if not k.InitializeProcThreadAttributeList(attr2,1,0,ctypes.byref(size2)):raise ctypes.WinError(ctypes.get_last_error())
                                    try:
                                        test_caps=SECURITY_CAPABILITIES(test_sid,None,0,0)
                                        if not k.UpdateProcThreadAttribute(attr2,0,0x20009,ctypes.byref(test_caps),ctypes.sizeof(test_caps),None,None):raise ctypes.WinError(ctypes.get_last_error())
                                        k.CreateEventW.argtypes=[ctypes.POINTER(SECURITY_ATTRIBUTES),wintypes.BOOL,wintypes.BOOL,wintypes.LPCWSTR]
                                        k.CreateEventW.restype=wintypes.HANDLE
                                        inherit=SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES),None,True)
                                        sentinel=k.CreateEventW(ctypes.byref(inherit),True,False,None)
                                        if not sentinel:raise ctypes.WinError(ctypes.get_last_error())
                                        try:
                                            handle_probe='''import ctypes,os,sys\nfrom ctypes import wintypes\nif ("PORTFOLIO_SYNTHETIC_SECRET" in os.environ)!=(sys.argv[2]=="present"):raise RuntimeError("unexpected environment canary")\nk=ctypes.WinDLL("kernel32",use_last_error=True);k.SetEvent.argtypes=[wintypes.HANDLE]\ntry:k.SetEvent(int(sys.argv[1]))\nexcept OSError:pass\n'''
                                            host=subprocess.run([sys.executable,'-I','-c',handle_probe,str(sentinel),'present'],close_fds=False,capture_output=True,timeout=10)
                                            if host.returncode or k.WaitForSingleObject(sentinel,0)!=0:raise RuntimeError('Inheritable-handle positive control failed')
                                            k.ResetEvent.argtypes=[wintypes.HANDLE]
                                            if not k.ResetEvent(sentinel):raise ctypes.WinError(ctypes.get_last_error())
                                            command=subprocess.list2cmdline([str(executable),'-I','-B','-c',handle_probe,str(sentinel),'absent'])
                                            if run(command,str(executable),test_caps)!=0:raise RuntimeError('Sentinel probe failed')
                                            if k.WaitForSingleObject(sentinel,0)!=258:raise RuntimeError('Unlisted sentinel handle reached separate test identity')
                                            print('Separate test identity: unlisted inheritable sentinel excluded; host positive control passed')
                                            print('Separate test identity: synthetic environment canary excluded; host positive control passed')
                                        finally:k.CloseHandle(sentinel)
                                        cmd=r'C:\Windows\System32\cmd.exe /d /c type '
                                        if run(cmd+'"'+str(secret)+'"')!=0:raise RuntimeError('Model-profile private-data control failed')
                                        if run(cmd+'"'+str(stage/'fixture.txt')+'"',capabilities=test_caps)!=0:raise RuntimeError('Separate test profile could not read stage')
                                        if run(cmd+'"'+str(secret)+'"',capabilities=test_caps)==0:raise RuntimeError('Separate test profile accessed private runtime data')
                                        if run(cmd+'"'+str(protected)+'"',capabilities=test_caps)==0:raise RuntimeError('Separate test profile accessed outside fixture')
                                        run(r'C:\Windows\System32\cmd.exe /d /c echo changed >>"'+str(stage/'fixture.txt')+'"',capabilities=test_caps)
                                        if (stage/'fixture.txt').read_text(encoding='utf-8')!='original':raise RuntimeError('Separate test profile modified stage')
                                        print('Separate test identity: staged read allowed; private runtime read and staged write denied')
                                        with socket.socket() as control:
                                            control.bind(('127.0.0.1',0));control.listen();control.settimeout(.3)
                                            def reply_once():
                                                deadline=time.monotonic()+8
                                                while time.monotonic()<deadline:
                                                    try:connection,_=control.accept()
                                                    except TimeoutError:continue
                                                    except OSError:return
                                                    with connection:
                                                        connection.settimeout(1)
                                                        try:connection.recv(4096);connection.sendall(b'HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nOK')
                                                        except OSError:pass
                                            threading.Thread(target=reply_once,daemon=True).start()
                                            curl=r'C:\Windows\System32\curl.exe';url='http://127.0.0.1:'+str(control.getsockname()[1])+'/'
                                            if subprocess.run([curl,'--silent','--max-time','3','--output','NUL',url],timeout=5).returncode:raise RuntimeError('Network control was unreachable')
                                            status=run(subprocess.list2cmdline([curl,'--silent','--connect-timeout','2','--max-time','3','--output','NUL',url]),curl,test_caps)
                                            if status not in (7,28):raise RuntimeError('Separate test identity network control was inconclusive: '+str(status))
                                            if subprocess.run([curl,'--silent','--max-time','3','--output','NUL',url],timeout=5).returncode:raise RuntimeError('Network control stopped during test')
                                            print('Separate test identity: loopback connection blocked; host control passed')
                                    finally:k.DeleteProcThreadAttributeList(attr2)
                                finally:
                                    a.FreeSid(test_sid)
                                    if not args.owned_profile_id:
                                        hr=u.DeleteAppContainerProfile(test_name)
                                        if hr:raise RuntimeError('Separate test-profile cleanup failed: 0x%08x'%(hr & 0xffffffff))
                            return
                        program='''import ctypes,sys\nfrom ctypes import wintypes\nk=ctypes.WinDLL("kernel32",use_last_error=True)\nk.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]\nk.CreateFileW.restype=wintypes.HANDLE\nk.GetFinalPathNameByHandleW.argtypes=[wintypes.HANDLE,wintypes.LPWSTR,wintypes.DWORD,wintypes.DWORD]\nk.GetFinalPathNameByHandleW.restype=wintypes.DWORD\nk.CloseHandle.argtypes=[wintypes.HANDLE]\ndef inspect(path):\n h=k.CreateFileW(path,0,7,None,3,0x02000000,None)\n if h==wintypes.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())\n try:\n  values=[]\n  for mode in (2,0):\n   b=ctypes.create_unicode_buffer(32768);ctypes.set_last_error(0);n=k.GetFinalPathNameByHandleW(h,b,len(b),mode)\n   values.append((b.value if n and n<len(b) else None,ctypes.get_last_error()))\n  return values\n finally:k.CloseHandle(h)\na=inspect(sys.argv[1]);b=inspect(sys.argv[2])\nif not a[0][0] or a[0][0].casefold()!=b[0][0].casefold():raise RuntimeError("NT paths did not resolve to the same target")\nprint("AppContainer NT handle resolution: ordinary directory and junction match")\nprint("AppContainer DOS resolution:","available" if a[1][0] and b[1][0] else "unavailable", "errors",a[1][1],b[1][1])\n'''
                        program+='''\nfor path,access,label in ((sys.argv[3],0x80000000,"outside"),(sys.argv[1]+"\\\\missing",0,"missing")):\n h=k.CreateFileW(path,access,7,None,3,0x02000000,None)\n if h!=wintypes.HANDLE(-1).value:\n  k.CloseHandle(h);raise RuntimeError(label+" path unexpectedly opened")\n print("AppContainer "+label+" path rejected; Windows error",ctypes.get_last_error())\n'''
                        program+='''\nimport os\ndevice_path="\\\\\\\\?\\\\GLOBALROOT"+a[0][0]\ntry:\n os.chdir(device_path)\n print("AppContainer GLOBALROOT cwd: accepted")\n if open("marker.txt",encoding="utf-8").read()!="synthetic marker":raise RuntimeError("wrong working directory")\n print("AppContainer GLOBALROOT cwd relative read: passed")\n try:\n  os.path.realpath(device_path,strict=True)\n  print("AppContainer GLOBALROOT canonicalization: accepted")\n except OSError as error:\n  print("AppContainer GLOBALROOT canonicalization: rejected; Windows error",error.winerror)\nexcept OSError as error:\n print("AppContainer GLOBALROOT cwd or relative read: rejected; Windows error",error.winerror)\n'''
                        program+='''\nsys.path.insert(0,sys.argv[4])\nfrom windows_path_research import DirectoryHandle\nwith DirectoryHandle(sys.argv[1]) as root:\n with DirectoryHandle(sys.argv[1]+"\\\\nested") as expected:\n  if root.probe_open_child("nested")!=expected.identity:raise RuntimeError("relative child identity mismatch")\n with root.probe_walk(["nested","inner"]) as found:\n  with DirectoryHandle(sys.argv[1]+"\\\\nested\\\\inner") as expected:\n   if found.identity!=expected.identity:raise RuntimeError("relative walk identity mismatch")\n try:root.probe_walk(["escape","nested"])\n except OSError:print("AppContainer relative handle walk: allowed child matched; escape rejected")\n else:raise RuntimeError("escape junction accepted")\n'''
                        program+='''\nwith DirectoryHandle(sys.argv[1]) as root:\n handle,info=root._probe_open_relative("marker.txt",directory=False)\n root.kernel.CloseHandle(handle)\n identity=(info.volume,info.index_high,info.index_low)\n if root.probe_read_verified_file("marker.txt",identity,32)!=b"synthetic marker":raise RuntimeError("verified file read mismatch")\n try:root.probe_read_verified_file("marker.txt",identity,1)\n except ValueError:print("AppContainer verified handle read: contents matched; size limit enforced")\n else:raise RuntimeError("oversized file accepted")\n'''
                        command=subprocess.list2cmdline([str(executable),'-I','-B','-c',program,str(target),str(link),str(protected),str(allowed)])
                        if run(command,str(executable))!=0:raise RuntimeError('AppContainer path API probe failed')
                        return
                    finally:
                        if (target/'escape').exists():(target/'escape').rmdir()
                        link.rmdir()
                fixture=allowed/'allowed.txt';fixture.write_text('fictional approved fixture',encoding='utf-8')
                command='C:\\Windows\\System32\\cmd.exe /d /c type "'+str(fixture)+'"'
                if run(command)!=0:
                    print('Approved fixture ACL:',subprocess.run(['icacls.exe',str(fixture)],capture_output=True,text=True).stdout)
                    print('Profile folder ACL:',subprocess.run(['icacls.exe',str(allowed)],capture_output=True,text=True).stdout)
                    raise RuntimeError('AppContainer could not read its approved fixture')
                print('Approved fixture read: allowed')
                readonly=allowed/'readonly';readonly.mkdir()
                import win32api,win32con,win32security
                token=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_QUERY)
                try:user_sid=win32security.ConvertSidToStringSid(win32security.GetTokenInformation(token,win32security.TokenUser)[0])
                finally:token.Close()
                package_grant='*'+sid_text+':(OI)(CI)(RX)'
                owner_grant='*'+user_sid+':(OI)(CI)(F)'
                system_grant='*S-1-5-18:(OI)(CI)(F)'
                for grant in (package_grant,owner_grant,system_grant):
                    result=subprocess.run(['icacls.exe',str(readonly),'/grant:r',grant],capture_output=True,text=True)
                    if result.returncode:raise RuntimeError('Could not set disposable test access: '+result.stderr[:300])
                result=subprocess.run(['icacls.exe',str(readonly),'/inheritance:r'],capture_output=True,text=True)
                if result.returncode:raise RuntimeError('Could not protect the disposable test folder: '+result.stderr[:300])
                locked=readonly/'locked.txt';locked.write_text('fictional read-only fixture',encoding='utf-8')
                command='C:\\Windows\\System32\\cmd.exe /d /c type "'+str(locked)+'"'
                if run(command)!=0:
                    print('Read-only fixture ACL:',subprocess.run(['icacls.exe',str(locked)],capture_output=True,text=True).stdout)
                    raise RuntimeError('AppContainer could not read its read-only test fixture')
                command='C:\\Windows\\System32\\cmd.exe /d /c echo modified >>"'+str(locked)+'"'
                run(command)
                if locked.read_text(encoding='utf-8')!='fictional read-only fixture':
                    print('Read-only fixture ACL:',subprocess.run(['icacls.exe',str(locked)],capture_output=True,text=True).stdout)
                    raise RuntimeError('AppContainer modified its read-only test fixture')
                command='C:\\Windows\\System32\\cmd.exe /d /c del "'+str(locked)+'"'
                run(command)
                if not locked.exists():raise RuntimeError('AppContainer deleted its read-only test fixture')
                print('Approved read-only fixture: read allowed, write and deletion denied')
                runtime=allowed/'python';runtime.mkdir()
                base=Path(sys.base_prefix)
                for executable in ('python.exe','python3.dll','python311.dll','vcruntime140.dll','vcruntime140_1.dll'):
                    source=base/executable
                    if source.is_file():shutil.copy2(source,runtime/executable)
                shutil.copytree(base/'Lib',runtime/'Lib',ignore=shutil.ignore_patterns('site-packages','__pycache__','test','tests','idlelib','tkinter','turtledemo','ensurepip','venv'))
                shutil.copytree(base/'DLLs',runtime/'DLLs',ignore=shutil.ignore_patterns('__pycache__'))
                executable=runtime/'python.exe'
                command='"'+str(executable)+'" -I -B -c "import unittest; print(\'native Python test runtime ready\')"'
                if run(command,str(executable))!=0:raise RuntimeError('Private Python runtime could not start in AppContainer')
                print('Private Python test runtime: passed')
                (readonly/'calculator.py').write_text('def answer(): return 42\n',encoding='utf-8')
                test_file=readonly/'test_calculator.py'
                driver=_PYTHON_TEST_LOADER+'''\nsys.path.insert(0, sys.argv[1])\nsuite=load_test_file(sys.argv[2], 0, sys.argv[1])\nresult=unittest.TextTestRunner().run(suite)\nif not result.wasSuccessful() or result.testsRun <= len(result.skipped): raise SystemExit(1)\n'''
                for expected,comparison in ((0,'42'),(1,'43')):
                    test_file.write_text('import unittest\nfrom calculator import answer\n'
                                         'class CalculatorTest(unittest.TestCase):\n'
                                         ' def test_answer(self): self.assertEqual(answer(), '+comparison+')\n',encoding='utf-8')
                    command=subprocess.list2cmdline([str(executable),'-I','-B','-c',driver,str(readonly),str(test_file)])
                    if run(command,str(executable))!=expected:raise RuntimeError('Read-only Python test outcome did not match expectation')
                print('Read-only Python test files: passing and failing outcomes correctly classified')
                probe_home=allowed/'probe-home';probe_home.mkdir()
                command=subprocess.list2cmdline([str(executable),'-I','-B','-c','import os,sys; print(os.path.realpath(sys.argv[1], strict=True))',str(probe_home)])
                home_result=run(command,str(executable))
                print('Private directory canonicalization:', 'passed' if home_result==0 else 'blocked')
                for expected, comparison in ((0,'42'),(1,'43')):
                    source=('import unittest\nclass Example(unittest.TestCase):\n'
                            ' def test_answer(self): self.assertEqual(42, '+comparison+')\n'
                            'unittest.main()\n')
                    command=subprocess.list2cmdline([str(executable),'-I','-B','-c',source])
                    if run(command,str(executable))!=expected:raise RuntimeError('Python test outcome did not match expectation')
                print('Passing and failing Python tests: correctly classified')
                codex_source=Path(args.codex_binary) if args.codex_binary else Path(binary(Config.load()))
                if not codex_source.is_absolute() or not codex_source.is_file():raise ValueError('The test Codex executable must be an existing absolute path')
                codex=allowed/'codex.exe';shutil.copy2(codex_source,codex)
                helper=codex_source.with_name('codex-code-mode-host.exe')
                if helper.is_file():shutil.copy2(helper,allowed/helper.name)
                command=subprocess.list2cmdline([str(codex),'--version'])
                if run(command,str(codex))!=0:raise RuntimeError('Windows Codex could not start in AppContainer')
                print('Windows Codex executable: started in AppContainer')
            with socket.socket() as server:
                server.bind(('127.0.0.1',0));server.listen();server.settimeout(8)
                port=server.getsockname()[1]
                def serve():
                    try:
                        while True:
                            connection,_=server.accept()
                            with connection:
                                connection.recv(4096)
                                connection.sendall(b'HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nOK')
                    except OSError:pass
                threading.Thread(target=serve,daemon=True).start()
                curl='C:\\Windows\\System32\\curl.exe'
                url='http://127.0.0.1:'+str(port)+'/'
                subprocess.run([curl,'--silent','--max-time','3','--output','NUL',url],check=True,timeout=5)
                command=curl+' --show-error --connect-timeout 2 --max-time 3 --output NUL '+url
                result=run(command,curl)
                if result not in (7,28):raise RuntimeError('Network probe returned unexpected result: '+str(result))
                print('Local network connection: blocked (curl status '+str(result)+')')
            # Codex itself needs outbound network access; this separate process gets
            # only the documented Internet Client capability, not private-network access.
            host=subprocess.run([curl,'--silent','--show-error','--head','--max-time','5','https://example.com/'],capture_output=True,timeout=8)
            if host.returncode != 0:
                raise RuntimeError('Outbound comparison inconclusive: host could not reach public test site')
            else:
                internet_sid=ctypes.c_void_p()
                if not a.ConvertStringSidToSidW('S-1-15-3-1',ctypes.byref(internet_sid)):raise ctypes.WinError(ctypes.get_last_error())
                try:
                    size2=ctypes.c_size_t();k.InitializeProcThreadAttributeList(None,1,0,ctypes.byref(size2))
                    buffer2=ctypes.create_string_buffer(size2.value);attr2=ctypes.cast(buffer2,ctypes.c_void_p)
                    if not k.InitializeProcThreadAttributeList(attr2,1,0,ctypes.byref(size2)):raise ctypes.WinError(ctypes.get_last_error())
                    try:
                        capability=SID_AND_ATTRIBUTES(internet_sid,4)
                        internet_caps=SECURITY_CAPABILITIES(sid,ctypes.cast(ctypes.byref(capability),ctypes.c_void_p),1,0)
                        if not k.UpdateProcThreadAttribute(attr2,0,0x20009,ctypes.byref(internet_caps),ctypes.sizeof(internet_caps),None,None):raise ctypes.WinError(ctypes.get_last_error())
                        command=subprocess.list2cmdline([curl,'--silent','--show-error','--head','--max-time','5','https://example.com/'])
                        result=run(command,curl,internet_caps)
                        if result!=0:raise RuntimeError('Internet-enabled AppContainer could not reach public comparison site: '+str(result))
                        print('Internet Client capability: outbound comparison passed')
                        runtime_host=allowed/'runtime-host';runtime_host.mkdir()
                        host_codex=runtime_host/'codex.exe';shutil.copy2(codex_source,host_codex)
                        if helper.is_file():shutil.copy2(helper,runtime_host/helper.name)
                        errors=[]
                        for label,explicit,guid in (('Explicit',True,False),('Default',False,False),('Volume GUID',True,True)):
                            try:appserver_probe(host_codex,runtime_host,internet_caps,explicit_home=explicit,volume_guid_home=guid)
                            except RuntimeError as error:
                                errors.append(str(error))
                                print(label+' home startup failed:',str(error)[:600])
                        if errors:raise RuntimeError('Codex app-server is not yet compatible with this AppContainer boundary')
                    finally:k.DeleteProcThreadAttributeList(attr2)
                finally:k.LocalFree(internet_sid)
        finally:k.DeleteProcThreadAttributeList(attr)
    finally:
        a.FreeSid(sid)
        if not args.owned_profile_id:
            result=u.DeleteAppContainerProfile(name)
            if result:raise RuntimeError('Probe profile cleanup failed: 0x%08x'%(result & 0xffffffff))


if __name__ == '__main__':
    main()
