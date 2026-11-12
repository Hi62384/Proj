"""Disposable Windows job-object cancellation probe; not a worker backend."""
import subprocess
import sys
import time
import os

import win32api
import win32con
import win32event
import win32job
import win32process


def memory_limit_probe():
    job = win32job.CreateJobObject(None, '')
    process = thread = None
    try:
        limits = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
        limits['BasicLimitInformation']['LimitFlags'] |= (
            win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY)
        limits['ProcessMemoryLimit'] = 48 * 1024 * 1024
        win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, limits)
        keep = {'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'OS', 'PATHEXT', 'SYSTEMDRIVE', 'USERPROFILE',
                'APPDATA', 'LOCALAPPDATA', 'HOMEDRIVE', 'HOMEPATH', 'TEMP', 'TMP'}
        env = {key: value for key, value in os.environ.items() if key.upper() in keep}
        env['PATH'] = r'C:\Windows\System32;C:\Windows'
        code = ('import sys\ntry: data=bytearray(64*1024*1024)\n'
                'except MemoryError: sys.exit(42)\nsys.exit(1)\n')
        command = subprocess.list2cmdline([sys.executable, '-I', '-c', code])
        process, thread, _, _ = win32process.CreateProcess(
            sys.executable, command, None, None, False,
            win32process.CREATE_SUSPENDED | win32process.CREATE_NO_WINDOW | win32con.CREATE_UNICODE_ENVIRONMENT,
            env, None, win32process.STARTUPINFO())
        win32job.AssignProcessToJobObject(job, process)
        win32process.ResumeThread(thread)
        if win32event.WaitForSingleObject(process, 10000) != win32event.WAIT_OBJECT_0:
            raise RuntimeError('Synthetic memory-limit probe timed out')
        if win32process.GetExitCodeProcess(process) != 42:
            raise RuntimeError('Synthetic memory allocation was not rejected as expected')
        print('Synthetic job memory limit: oversized allocation rejected')
    finally:
        job.Close()
        if process is not None:
            if win32event.WaitForSingleObject(process, 5000) != win32event.WAIT_OBJECT_0:
                win32process.TerminateProcess(process, 1)
            process.Close()
        if thread is not None:
            thread.Close()


def main():
    job = win32job.CreateJobObject(None, '')
    parent = thread = None
    observed = []
    try:
        limits = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
        limits['BasicLimitInformation']['LimitFlags'] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, limits)
        os.environ['PORTFOLIO_SYNTHETIC_SECRET'] = 'fictional-job-canary'
        keep = {'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'OS', 'PATHEXT', 'SYSTEMDRIVE', 'USERPROFILE',
                'APPDATA', 'LOCALAPPDATA', 'HOMEDRIVE', 'HOMEPATH', 'TEMP', 'TMP'}
        clean_env = {key: value for key, value in os.environ.items() if key.upper() in keep}
        clean_env['PATH'] = r'C:\Windows\System32;C:\Windows'
        code = ('import os,subprocess,sys,time\n'
                'assert "PORTFOLIO_SYNTHETIC_SECRET" not in os.environ\n'
                'subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"])\n'
                'time.sleep(60)\n')
        command = subprocess.list2cmdline([sys.executable, '-I', '-c', code])
        startup = win32process.STARTUPINFO()
        parent, thread, _, _ = win32process.CreateProcess(
            sys.executable, command, None, None, False,
            win32process.CREATE_SUSPENDED | win32process.CREATE_NO_WINDOW | win32con.CREATE_UNICODE_ENVIRONMENT,
            clean_env, None, startup)
        win32job.AssignProcessToJobObject(job, parent)
        win32process.ResumeThread(thread)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            info = win32job.QueryInformationJobObject(job, win32job.JobObjectBasicProcessIdList)
            pids = info
            if len(pids) >= 2:
                break
            time.sleep(.1)
        else:
            raise RuntimeError('Synthetic child was not observed in the job')
        for pid in pids:
            observed.append(win32api.OpenProcess(win32con.SYNCHRONIZE, False, pid))
        job.Close()
        job = None
        if any(win32event.WaitForSingleObject(handle, 5000) != win32event.WAIT_OBJECT_0 for handle in observed):
            raise RuntimeError('A synthetic process survived job closure')
        print('Synthetic job cancellation: parent and child exited after job closure')
    finally:
        if job is not None:
            job.Close()
        if parent is not None:
            # Only this disposable process can be terminated here.
            if win32event.WaitForSingleObject(parent, 5000) != win32event.WAIT_OBJECT_0:
                win32process.TerminateProcess(parent, 1)
            parent.Close()
        if thread is not None:
            thread.Close()
        for handle in observed:
            handle.Close()
    memory_limit_probe()


if __name__ == '__main__':
    main()
