"""Run a synthetic acceptance probe in an owned Windows job, not production code."""
import ctypes
import os
import subprocess
import threading
from ctypes import wintypes


class OwnedCleanupUnconfirmed(RuntimeError):
    """Do not remove owned profiles while process-tree termination is uncertain."""


def run_owned(command, *, capture_output=True, text=True, timeout=45, check=False):
    if os.name != 'nt' or not capture_output or not text or check:
        raise ValueError('Unsupported synthetic process invocation')
    import win32api, win32con, win32event, win32job
    import pywintypes
    from portfolio_manager.tests.live_windows_isolation import (
        k, STARTUPINFOEX, PROCESS_INFORMATION, SECURITY_ATTRIBUTES)

    read_handle = wintypes.HANDLE(); write_handle = wintypes.HANDLE()
    security = SECURITY_ATTRIBUTES(ctypes.sizeof(SECURITY_ATTRIBUTES), None, True)
    if not k.CreatePipe(ctypes.byref(read_handle), ctypes.byref(write_handle), ctypes.byref(security), 0):
        raise ctypes.WinError(ctypes.get_last_error())
    job = None; process = PROCESS_INFORMATION(); attributes = None; observed = []
    chunks = []
    try:
        if not k.SetHandleInformation(read_handle, 1, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        size = ctypes.c_size_t(); k.InitializeProcThreadAttributeList(None, 2, 0, ctypes.byref(size))
        buffer = ctypes.create_string_buffer(size.value); attributes = ctypes.cast(buffer, ctypes.c_void_p)
        if not k.InitializeProcThreadAttributeList(attributes, 2, 0, ctypes.byref(size)):
            attributes = None
            raise ctypes.WinError(ctypes.get_last_error())
        allowed = (wintypes.HANDLE * 1)(write_handle.value)
        if not k.UpdateProcThreadAttribute(attributes, 0, 0x20002, allowed, ctypes.sizeof(allowed), None, None):
            raise ctypes.WinError(ctypes.get_last_error())
        job = win32job.CreateJobObject(None, '')
        limits = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
        limits['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, limits)
        jobs = (wintypes.HANDLE * 1)(int(job))
        if not k.UpdateProcThreadAttribute(attributes, 0, 0x2000d, jobs, ctypes.sizeof(jobs), None, None):
            raise ctypes.WinError(ctypes.get_last_error())
        startup = STARTUPINFOEX(); startup.StartupInfo.cb = ctypes.sizeof(startup)
        startup.StartupInfo.dwFlags = 0x100
        startup.StartupInfo.hStdOutput = write_handle; startup.StartupInfo.hStdError = write_handle
        startup.lpAttributeList = attributes
        keep = {'SYSTEMROOT','WINDIR','COMSPEC','OS','PATHEXT','SYSTEMDRIVE','USERNAME','USERDOMAIN',
                'PROGRAMDATA','PROGRAMFILES','PROGRAMFILES(X86)','USERPROFILE','APPDATA','LOCALAPPDATA',
                'HOMEDRIVE','HOMEPATH','TEMP','TMP'}
        env = {key:value for key,value in os.environ.items() if key.upper() in keep}
        env['PATH'] = r'C:\Windows\System32;C:\Windows'
        environment = ctypes.create_unicode_buffer('\0'.join(key+'='+value for key,value in
            sorted(env.items(),key=lambda item:item[0].upper()))+'\0\0')
        cmd = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
        # The job is supplied at process creation, before the suspended process exists.
        if not k.CreateProcessW(command[0], cmd, None, None, True, 0x08080404, environment,
                                os.getcwd(), ctypes.byref(startup), ctypes.byref(process)):
            raise ctypes.WinError(ctypes.get_last_error())
        k.ResumeThread.argtypes = [wintypes.HANDLE]; k.ResumeThread.restype = wintypes.DWORD
        if k.ResumeThread(process.hThread) == 0xffffffff:
            raise ctypes.WinError(ctypes.get_last_error())
        k.CloseHandle(write_handle); write_handle = None

        def drain():
            buf = ctypes.create_string_buffer(8192); count = wintypes.DWORD()
            while k.ReadFile(read_handle, buf, len(buf), ctypes.byref(count), None) and count.value:
                chunks.append(buf.raw[:count.value])

        reader = threading.Thread(target=drain, daemon=True); reader.start()
        result = k.WaitForSingleObject(process.hProcess, max(1, int(timeout * 1000)))
        if result not in (0, 258):
            raise ctypes.WinError(ctypes.get_last_error())
        timed_out = result == 258
        for pid in win32job.QueryInformationJobObject(job, win32job.JobObjectBasicProcessIdList):
            try:
                observed.append(win32api.OpenProcess(win32con.SYNCHRONIZE, False, pid))
            except pywintypes.error:
                # A process which exited while being inspected no longer needs a wait.
                if pid in win32job.QueryInformationJobObject(job, win32job.JobObjectBasicProcessIdList):
                    raise OwnedCleanupUnconfirmed('Could not obtain an owned descendant wait handle')
        job.Close(); job = None  # Also stops any surviving descendants.
        if k.WaitForSingleObject(process.hProcess, 5000) != 0:
            raise OwnedCleanupUnconfirmed('Owned probe process did not exit after job closure')
        if any(win32event.WaitForSingleObject(handle, 5000) != win32event.WAIT_OBJECT_0 for handle in observed):
            raise OwnedCleanupUnconfirmed('Owned probe descendant did not exit after job closure')
        reader.join(timeout=5)
        if reader.is_alive():
            raise OwnedCleanupUnconfirmed('Owned probe output pipe did not close')
        output = b''.join(chunks).decode('utf-8', errors='replace')
        if timed_out:
            raise subprocess.TimeoutExpired(command, timeout, output=output)
        exit_code = wintypes.DWORD()
        if not k.GetExitCodeProcess(process.hProcess, ctypes.byref(exit_code)):
            raise ctypes.WinError(ctypes.get_last_error())
        return subprocess.CompletedProcess(command, exit_code.value, output, '')
    finally:
        cleanup_uncertain = False
        if job is not None:
            try:
                for pid in win32job.QueryInformationJobObject(job, win32job.JobObjectBasicProcessIdList):
                    try:
                        observed.append(win32api.OpenProcess(win32con.SYNCHRONIZE, False, pid))
                    except pywintypes.error:
                        if pid in win32job.QueryInformationJobObject(job, win32job.JobObjectBasicProcessIdList):
                            cleanup_uncertain = True
            except pywintypes.error:
                cleanup_uncertain = True
            job.Close()
        if process.hProcess:
            if k.WaitForSingleObject(process.hProcess, 5000) != 0:
                k.TerminateProcess(process.hProcess, 1)
                if k.WaitForSingleObject(process.hProcess, 5000) != 0:
                    cleanup_uncertain = True
            k.CloseHandle(process.hProcess)
        if process.hThread:
            k.CloseHandle(process.hThread)
        if attributes is not None:
            k.DeleteProcThreadAttributeList(attributes)
        for handle in observed:
            if win32event.WaitForSingleObject(handle, 5000) != win32event.WAIT_OBJECT_0:
                cleanup_uncertain = True
            handle.Close()
        if write_handle is not None:
            k.CloseHandle(write_handle)
        k.CloseHandle(read_handle)
        if cleanup_uncertain:
            raise OwnedCleanupUnconfirmed('Could not verify termination of the owned process tree')
