"""Experimental disposable restricted-token feasibility probe; not a worker backend."""
import ctypes
from ctypes import wintypes
from contextlib import contextmanager
import argparse
import secrets
import shutil
import tempfile
import uuid
from pathlib import Path

import win32api
import win32con
import win32event
import win32process
import win32security
import win32service
import ntsecuritycon
from portfolio_autopilot.codex_relay.codex import binary
from portfolio_autopilot.codex_relay.config import Config


def station_checks(token):
    """Read-only access checks against the current station, without changing its ACL."""
    security_info=(win32security.OWNER_SECURITY_INFORMATION|win32security.GROUP_SECURITY_INFORMATION|
                   win32security.DACL_SECURITY_INFORMATION)
    descriptor=win32security.GetUserObjectSecurity(win32service.GetProcessWindowStation(),security_info)
    sddl=win32security.ConvertSecurityDescriptorToStringSecurityDescriptor(descriptor,1,security_info)
    advapi=ctypes.WinDLL('advapi32',use_last_error=True);kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,ctypes.POINTER(ctypes.c_void_p),ctypes.c_void_p]
    class GENERIC_MAPPING(ctypes.Structure):
        _fields_=[('GenericRead',wintypes.DWORD),('GenericWrite',wintypes.DWORD),('GenericExecute',wintypes.DWORD),('GenericAll',wintypes.DWORD)]
    advapi.AccessCheck.argtypes=[ctypes.c_void_p,wintypes.HANDLE,wintypes.DWORD,ctypes.POINTER(GENERIC_MAPPING),
                                ctypes.c_void_p,ctypes.POINTER(wintypes.DWORD),ctypes.POINTER(wintypes.DWORD),ctypes.POINTER(wintypes.BOOL)]
    kernel.LocalFree.argtypes=[ctypes.c_void_p]
    value=ctypes.c_void_p()
    if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl,1,ctypes.byref(value),None):raise ctypes.WinError(ctypes.get_last_error())
    impersonation=win32security.DuplicateToken(token,win32security.SecurityImpersonation)
    try:
        mapping=GENERIC_MAPPING(0x20000,0x20000,0x20000,0xF037F)
        result={}
        for name,mask in (('read_attributes',0x2),('global_atoms',0x20),('enumerate',0x100)):
            privileges=ctypes.create_string_buffer(4096);size=wintypes.DWORD(len(privileges))
            granted=wintypes.DWORD();allowed=wintypes.BOOL()
            if not advapi.AccessCheck(value,int(impersonation),mask,ctypes.byref(mapping),privileges,ctypes.byref(size),ctypes.byref(granted),ctypes.byref(allowed)):
                raise ctypes.WinError(ctypes.get_last_error())
            result[name]=bool(allowed.value)
        return result
    finally:
        impersonation.Close();kernel.LocalFree(value)


@contextmanager
def private_desktop(user_sid,restricted_sid):
    """Create a non-visible desktop in the existing station without switching to it."""
    user32=ctypes.WinDLL('user32',use_last_error=True)
    advapi=ctypes.WinDLL('advapi32',use_last_error=True)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_=[('nLength',wintypes.DWORD),('lpSecurityDescriptor',ctypes.c_void_p),('bInheritHandle',wintypes.BOOL)]
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,ctypes.POINTER(ctypes.c_void_p),ctypes.c_void_p]
    user32.CreateDesktopW.argtypes=[wintypes.LPCWSTR,wintypes.LPCWSTR,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,ctypes.POINTER(SECURITY_ATTRIBUTES)]
    user32.CreateDesktopW.restype=wintypes.HANDLE
    user32.CloseDesktop.argtypes=[wintypes.HANDLE]
    kernel.LocalFree.argtypes=[ctypes.c_void_p]
    descriptor=ctypes.c_void_p()
    sddl='D:(A;;GA;;;SY)(A;;GA;;;'+user_sid+')(A;;GA;;;'+restricted_sid+')'
    if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl,1,ctypes.byref(descriptor),None):raise ctypes.WinError(ctypes.get_last_error())
    try:
        security=SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES),descriptor,False)
        name='PMProbe'+uuid.uuid4().hex
        desktop=user32.CreateDesktopW(name,None,None,0,0x201FF,ctypes.byref(security))
        if not desktop:raise ctypes.WinError(ctypes.get_last_error())
        try:yield 'WinSta0\\'+name
        finally:user32.CloseDesktop(desktop)
    finally:kernel.LocalFree(descriptor)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnose-user-sid',action='store_true',help='Use an intentionally broader token for a synthetic fail-closed comparison')
    options=parser.parse_args()
    sid_text='S-1-5-21-'+ '-'.join(str(secrets.randbits(32)) for _ in range(4))
    private_sid=win32security.ConvertStringSidToSid(sid_text)
    system_sid=win32security.ConvertStringSidToSid('S-1-5-32-545')
    original=win32security.OpenProcessToken(win32api.GetCurrentProcess(),win32con.TOKEN_DUPLICATE|win32con.TOKEN_QUERY|win32con.TOKEN_ASSIGN_PRIMARY)
    user_sid=win32security.ConvertSidToStringSid(win32security.GetTokenInformation(original,win32security.TokenUser)[0])
    groups=win32security.GetTokenInformation(original,win32security.TokenGroups)
    logon_sid=next((sid for sid,attributes in groups if attributes & 0xC0000000 == 0xC0000000),None)
    restricted_code=win32security.ConvertStringSidToSid('S-1-5-12')
    everyone=win32security.ConvertStringSidToSid('S-1-1-0')
    interactive=win32security.ConvertStringSidToSid('S-1-5-4')
    sids=[(private_sid,0),(system_sid,0),(restricted_code,0),(everyone,0),(interactive,0)]
    if logon_sid is not None:sids.append((logon_sid,0))
    if options.diagnose_user_sid:sids.append((win32security.ConvertStringSidToSid(user_sid),0))
    restricted=win32security.CreateRestrictedToken(original,1,[],[],sids)
    original.Close()
    try:
        print('Restricted token window-station checks:',station_checks(restricted),flush=True)
        with tempfile.TemporaryDirectory(prefix='portfolio-restricted-token-') as folder:
            root=Path(folder);permitted=root/'permitted';permitted.mkdir()
            descriptor=win32security.GetNamedSecurityInfo(str(permitted),win32security.SE_FILE_OBJECT,win32security.DACL_SECURITY_INFORMATION)
            acl=descriptor.GetSecurityDescriptorDacl()
            acl.AddAccessAllowedAceEx(win32security.ACL_REVISION,
                win32security.OBJECT_INHERIT_ACE|win32security.CONTAINER_INHERIT_ACE,
                ntsecuritycon.FILE_GENERIC_READ|ntsecuritycon.FILE_GENERIC_EXECUTE,private_sid)
            win32security.SetNamedSecurityInfo(str(permitted),win32security.SE_FILE_OBJECT,
                win32security.DACL_SECURITY_INFORMATION,None,None,acl,None)
            allowed=permitted/'allowed.txt';allowed.write_text('fictional allowed data',encoding='utf-8')
            outside=root/'outside.txt';outside.write_text('fictional private data',encoding='utf-8')
            outside_sd=win32security.GetNamedSecurityInfo(str(outside),win32security.SE_FILE_OBJECT,win32security.DACL_SECURITY_INFORMATION)
            outside_acl=outside_sd.GetSecurityDescriptorDacl()
            outside_acl.AddAccessAllowedAce(win32security.ACL_REVISION,ntsecuritycon.FILE_GENERIC_READ,everyone)
            win32security.SetNamedSecurityInfo(str(outside),win32security.SE_FILE_OBJECT,
                win32security.DACL_SECURITY_INFORMATION,None,None,outside_acl,None)
            def run(command,application=r'C:\Windows\System32\cmd.exe'):
                with private_desktop(user_sid,sid_text) as desktop:
                    startup=win32process.STARTUPINFO();startup.lpDesktop=desktop
                    process,thread,_,_=win32process.CreateProcessAsUser(restricted,application,
                        command,None,None,False,win32process.CREATE_NO_WINDOW,None,r'C:\Windows\System32',startup)
                    thread.Close()
                    try:
                        if win32event.WaitForSingleObject(process,10000)!=win32event.WAIT_OBJECT_0:
                            win32process.TerminateProcess(process,1)
                            raise TimeoutError('Disposable probe timed out')
                        return win32process.GetExitCodeProcess(process)
                    finally:process.Close()
            status=run('cmd.exe /d /c exit 42')
            if status!=42:
                print('Restricted Windows command initialization failed: 0x%08x'%(status & 0xffffffff),flush=True)
                minimal_source=Path(__file__).resolve().parents[2]/'.tmp'/'restricted-token-minimal.exe'
                if minimal_source.is_file():
                    minimal=permitted/'minimal.exe';shutil.copy2(minimal_source,minimal)
                    minimal_status=run('"'+str(minimal)+'"',str(minimal))
                    print('Minimal kernel-only process exit: 0x%08x'%(minimal_status & 0xffffffff),flush=True)
                codex=permitted/'codex.exe';shutil.copy2(binary(Config.load()),codex)
                status=run('"'+str(codex)+'" --version',str(codex))
                if status!=0:raise RuntimeError('Restricted Codex executable failed to start: 0x%08x'%(status & 0xffffffff))
                raise RuntimeError('Codex started, but command and file-boundary checks are unavailable; do not enable this backend')
            if run('cmd.exe /d /c type "'+str(allowed)+'"')!=0:raise RuntimeError('Restricted process could not read its allowed fixture')
            if run('cmd.exe /d /c type "'+str(outside)+'"')==0:raise RuntimeError('Restricted process read the broadly shared outside fixture; root-deny is not enforced')
            print('Restricted Windows token: process started; allowed read passed; outside read denied.')
    finally:restricted.Close()


if __name__=='__main__':main()
