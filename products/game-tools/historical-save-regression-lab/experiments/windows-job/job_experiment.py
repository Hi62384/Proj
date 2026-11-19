"""Synthetic lifecycle experiment only. This is NOT a security sandbox or Unity integration."""
import ctypes as c
from ctypes import wintypes as w
import subprocess
import sys
import time

k = c.WinDLL('kernel32', use_last_error=True)
class STARTUPINFO(c.Structure):
    _fields_ = [('cb', w.DWORD), ('lpReserved', w.LPWSTR), ('lpDesktop', w.LPWSTR), ('lpTitle', w.LPWSTR), ('dwX', w.DWORD), ('dwY', w.DWORD), ('dwXSize', w.DWORD), ('dwYSize', w.DWORD), ('dwXCountChars', w.DWORD), ('dwYCountChars', w.DWORD), ('dwFillAttribute', w.DWORD), ('dwFlags', w.DWORD), ('wShowWindow', w.WORD), ('cbReserved2', w.WORD), ('lpReserved2', c.POINTER(c.c_byte)), ('hStdInput', w.HANDLE), ('hStdOutput', w.HANDLE), ('hStdError', w.HANDLE)]
class PROCESS_INFORMATION(c.Structure):
    _fields_ = [('hProcess', w.HANDLE), ('hThread', w.HANDLE), ('dwProcessId', w.DWORD), ('dwThreadId', w.DWORD)]
class IO_COUNTERS(c.Structure):
    _fields_ = [(n, c.c_ulonglong) for n in ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount', 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
class BASIC_LIMIT(c.Structure):
    _fields_ = [('PerProcessUserTimeLimit', c.c_longlong), ('PerJobUserTimeLimit', c.c_longlong), ('LimitFlags', w.DWORD), ('MinimumWorkingSetSize', c.c_size_t), ('MaximumWorkingSetSize', c.c_size_t), ('ActiveProcessLimit', w.DWORD), ('Affinity', c.c_size_t), ('PriorityClass', w.DWORD), ('SchedulingClass', w.DWORD)]
class EXTENDED_LIMIT(c.Structure):
    _fields_ = [('BasicLimitInformation', BASIC_LIMIT), ('IoInfo', IO_COUNTERS), ('ProcessMemoryLimit', c.c_size_t), ('JobMemoryLimit', c.c_size_t), ('PeakProcessMemoryUsed', c.c_size_t), ('PeakJobMemoryUsed', c.c_size_t)]
class ACCOUNTING(c.Structure):
    _fields_ = [('TotalUserTime', c.c_longlong), ('TotalKernelTime', c.c_longlong), ('ThisPeriodTotalUserTime', c.c_longlong), ('ThisPeriodTotalKernelTime', c.c_longlong), ('TotalPageFaultCount', w.DWORD), ('TotalProcesses', w.DWORD), ('ActiveProcesses', w.DWORD), ('TotalTerminatedProcesses', w.DWORD)]
def api(name, restype, *types):
    f = getattr(k, name); f.restype = restype; f.argtypes = types; return f
CreateJob = api('CreateJobObjectW', w.HANDLE, w.LPVOID, w.LPCWSTR)
SetJob = api('SetInformationJobObject', w.BOOL, w.HANDLE, c.c_int, w.LPVOID, w.DWORD)
QueryJob = api('QueryInformationJobObject', w.BOOL, w.HANDLE, c.c_int, w.LPVOID, w.DWORD, w.LPVOID)
CreateProcess = api('CreateProcessW', w.BOOL, w.LPCWSTR, w.LPWSTR, w.LPVOID, w.LPVOID, w.BOOL, w.DWORD, w.LPVOID, w.LPCWSTR, c.POINTER(STARTUPINFO), c.POINTER(PROCESS_INFORMATION))
Assign = api('AssignProcessToJobObject', w.BOOL, w.HANDLE, w.HANDLE)
Resume = api('ResumeThread', w.DWORD, w.HANDLE)
Wait = api('WaitForSingleObject', w.DWORD, w.HANDLE, w.DWORD)
TerminateJob = api('TerminateJobObject', w.BOOL, w.HANDLE, w.UINT)
TerminateProcess = api('TerminateProcess', w.BOOL, w.HANDLE, w.UINT)
Close = api('CloseHandle', w.BOOL, w.HANDLE)
ExitCode = api('GetExitCodeProcess', w.BOOL, w.HANDLE, c.POINTER(w.DWORD))
def check(value):
    if not value: raise c.WinError(c.get_last_error())
    return value

def run(command, timeout_ms, force_assignment_failure=False):
    """Run synthetic child, returning status and exit code; exceptions mean no valid result.

    Failure to establish the job never resumes the suspended worker. No untrusted input.
    """
    if timeout_ms <= 0: raise ValueError('positive timeout required')
    job = check(CreateJob(None, None)); pi = PROCESS_INFORMATION(); assigned = False
    try:
        limits = EXTENDED_LIMIT(); limits.BasicLimitInformation.LimitFlags = 0x2000 # KILL_ON_JOB_CLOSE
        check(SetJob(job, 9, c.byref(limits), c.sizeof(limits)))
        si = STARTUPINFO(); si.cb = c.sizeof(si)
        line = c.create_unicode_buffer(subprocess.list2cmdline(command))
        check(CreateProcess(None, line, None, None, False, 0x4 | 0x08000000, None, None, c.byref(si), c.byref(pi)))
        try:
            # Exercise a real failed Win32 assignment using an invalid job handle.
            if force_assignment_failure:
                check(Assign(None, pi.hProcess))
                raise RuntimeError('invalid assignment unexpectedly succeeded')
            check(Assign(job, pi.hProcess)); assigned = True
            if Resume(pi.hThread) == 0xffffffff: raise c.WinError(c.get_last_error())
            wait = Wait(pi.hProcess, timeout_ms)
            if wait == 0x102:
                check(TerminateJob(job, 124)); status = 'timeout'
            elif wait == 0: status = 'exited'
            else: raise c.WinError(c.get_last_error())
            # Also terminate remaining children on an ordinary exit. A process exit
            # alone does not prove the associated job is empty.
            if status == 'exited': check(TerminateJob(job, 125))
            if Wait(pi.hProcess, 5000) != 0: raise RuntimeError('worker termination not confirmed')
            end = time.monotonic() + 5
            while True:
                info = ACCOUNTING(); check(QueryJob(job, 1, c.byref(info), c.sizeof(info), None))
                if info.ActiveProcesses == 0: break
                if time.monotonic() >= end: raise RuntimeError('job did not empty')
                time.sleep(.01)
            code = w.DWORD(); check(ExitCode(pi.hProcess, c.byref(code)))
            return status, code.value, info.TotalProcesses
        finally:
            if assigned:
                TerminateJob(job, 126)
            else:
                TerminateProcess(pi.hProcess, 126)
            Wait(pi.hProcess, 5000)
            Close(pi.hThread); Close(pi.hProcess)
    finally:
        Close(job)
