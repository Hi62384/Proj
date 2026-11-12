import os
import subprocess
import sys
import json
from pathlib import Path
import tempfile
import time
import unittest

from portfolio_manager.tests.windows_owned_process import run_owned


@unittest.skipUnless(os.name == 'nt', 'Windows jobs are required')
class OwnedProcessTests(unittest.TestCase):
    def test_normal_exit_preserves_output_and_status(self):
        result = run_owned([sys.executable, '-I', '-c', 'print("synthetic completed")'], timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn('synthetic completed', result.stdout)

    def test_timeout_stops_owned_process_and_preserves_output(self):
        code = 'import time; print("synthetic ready",flush=True); time.sleep(30)'
        with self.assertRaises(subprocess.TimeoutExpired) as caught:
            run_owned([sys.executable, '-I', '-c', code], timeout=1)
        self.assertIn('synthetic ready', caught.exception.output)

    def test_controller_crash_stops_owned_process_and_child(self):
        import win32api, win32con, win32event
        with tempfile.TemporaryDirectory(prefix='portfolio-owned-crash-') as folder:
            marker = Path(folder) / 'owned.json'
            worker = ('import json,os,subprocess,sys,time\n'
                      'child=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"])\n'
                      'open(sys.argv[1],"w").write(json.dumps([os.getpid(),child.pid]))\n'
                      'time.sleep(30)\n')
            supervisor = ('import sys\nfrom portfolio_manager.tests.windows_owned_process import run_owned\n'
                          'run_owned([sys.executable,"-I","-c",sys.argv[1],sys.argv[2]],timeout=20)\n')
            proc = subprocess.Popen([sys.executable, '-c', supervisor, worker, str(marker)],
                                    creationflags=subprocess.CREATE_NO_WINDOW)
            handles = []
            try:
                deadline = time.monotonic() + 8
                pids = None
                while time.monotonic() < deadline and proc.poll() is None:
                    try:
                        pids = json.loads(marker.read_text(encoding='utf-8'))
                        break
                    except (OSError, ValueError):
                        time.sleep(.05)
                self.assertIsNotNone(pids, 'Synthetic worker did not start')
                for pid in pids:
                    handles.append(win32api.OpenProcess(win32con.SYNCHRONIZE, False, pid))
                proc.terminate()  # This is only the synthetic controller created above.
                proc.wait(timeout=5)
                for handle in handles:
                    self.assertEqual(win32event.WaitForSingleObject(handle, 5000), win32event.WAIT_OBJECT_0)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)
                for handle in handles:
                    handle.Close()
