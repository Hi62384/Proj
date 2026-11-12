"""Test cleanup of profiles owned by this synthetic controller after timeout."""
import ctypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import msvcrt

from portfolio_manager.tests.windows_owned_process import run_owned
from portfolio_manager.tests.windows_profile_owner import OwnedProfiles
from portfolio_manager.tests.windows_stale_profile_recovery import inspect_record, windows_owner_state


def main():
    owner = OwnedProfiles()
    names = tuple(owner._created)  # Test-only inspection of this owner's exact resources.
    try:
        code = ('import subprocess,sys,time\n'
                'subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"])\n'
                'print("synthetic started",flush=True)\ntime.sleep(30)\n')
        try:
            run_owned([sys.executable, '-I', '-c', code], timeout=1)
            raise RuntimeError('Synthetic timeout did not occur')
        except subprocess.TimeoutExpired as error:
            if 'synthetic started' not in error.output:
                raise RuntimeError('Synthetic timeout control did not start')
    finally:
        owner.close()
    if owner._created:
        raise RuntimeError('Owned profile cleanup did not finish')
    # Re-creation of precisely these names confirms that each profile was released.
    for name in names:
        sid = ctypes.c_void_p()
        result = owner._u.CreateAppContainerProfile(name, name, 'Synthetic cleanup verification',
                                                    None, 0, ctypes.byref(sid))
        if result:
            raise RuntimeError('Released test-profile name could not be reused')
        try:
            owner._a.FreeSid(sid)
        finally:
            result = owner._u.DeleteAppContainerProfile(name)
            if result:
                raise RuntimeError('Re-created test-profile cleanup failed')
    print('Synthetic timeout recovery: owned process tree stopped and exact owned profiles released')

    # Stop only a controller created by this test; inspect its durable record.
    with tempfile.TemporaryDirectory(prefix='portfolio-profile-crash-') as folder:
        marker = Path(folder) / 'controller.json'
        code = ('import json,os,sys,time\nfrom pathlib import Path\n'
                'dll=os.add_dll_directory(sys.argv[2])\n'
                'from portfolio_manager.tests.windows_profile_owner import OwnedProfiles\n'
                'owner=OwnedProfiles()\nPath(sys.argv[1]).write_text(json.dumps(owner.identifier))\n'
                'time.sleep(30)\n')
        keep = {'SYSTEMROOT','WINDIR','COMSPEC','OS','PATHEXT','SYSTEMDRIVE','USERNAME','USERDOMAIN',
                'PROGRAMDATA','PROGRAMFILES','PROGRAMFILES(X86)','USERPROFILE','APPDATA','LOCALAPPDATA',
                'HOMEDRIVE','HOMEPATH','TEMP','TMP'}
        env = {key:value for key,value in os.environ.items() if key.upper() in keep}
        env['PATH'] = r'C:\Windows\System32;C:\Windows'
        env['PYTHONPATH'] = os.pathsep.join(path for path in sys.path if path)
        site = next(path for path in sys.path if path.endswith('site-packages'))
        dll_dir = str(Path(site) / 'pywin32_system32')
        # Use the base interpreter directly: a venv launcher can create a second PID.
        controller = subprocess.Popen([sys._base_executable, '-c', code, str(marker), dll_dir], env=env,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
        identifier = None
        try:
            deadline = time.monotonic() + 8
            while time.monotonic() < deadline and controller.poll() is None:
                try:
                    identifier = json.loads(marker.read_text(encoding='utf-8'))
                    break
                except (OSError, ValueError):
                    time.sleep(.05)
            if identifier is None:
                raise RuntimeError('Synthetic crash controller did not finish setup')
            controller.terminate()
            controller.wait(timeout=5)
            journal = Path(__file__).resolve().parents[2] / '.tmp' / 'portfolio-acceptance-profile-journals' / (identifier + '.json')
            inspection = inspect_record(journal.parent, identifier, owner_state=windows_owner_state)
            if inspection.get('status') != 'requires_proof':
                raise RuntimeError('Synthetic stale record was not safely recognized: '+str(inspection))
            lock_path = journal.with_suffix('.lock')
            with lock_path.open('r+b') as lock:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                try:
                    record = json.loads(journal.read_text(encoding='utf-8'))
                    expected = {'PortfolioManager.A.' + identifier + '.model', 'PortfolioManager.A.' + identifier + '.test'}
                    if (record.get('version') != 2 or record.get('id') != identifier or record.get('owner_pid') != controller.pid or
                            record.get('pending') is not None or set(record.get('created', [])) != expected):
                        raise RuntimeError('Synthetic crash ownership record was not conclusive')
                    for name in record['created']:
                        result = owner._u.DeleteAppContainerProfile(name)
                        if result:
                            raise RuntimeError('Crash-test profile cleanup failed; journal retained')
                    journal.unlink()
                finally:
                    lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            lock_path.unlink()
            print('Synthetic controller crash: exact owned profile record survived and was safely cleaned')
        finally:
            if controller.poll() is None:
                controller.terminate()
                controller.wait(timeout=5)


if __name__ == '__main__':
    main()
