"""Start and reuse the actual controller with an empty disposable Windows profile."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


APP = Path(__file__).resolve().parents[2] / 'apps' / 'codex_desktop_assistant'
sys.path.insert(0, str(APP))
from bridge.client import ControllerClient


@unittest.skipUnless(os.name == 'nt', 'Windows controller required')
class WindowsStartupTests(unittest.TestCase):
    def test_startup_reuses_one_integrated_controller(self):
        with tempfile.TemporaryDirectory(prefix='portfolio-launch-') as temporary:
            local = Path(temporary)
            environment = {**os.environ, 'LOCALAPPDATA': str(local), 'QT_QPA_PLATFORM': 'offscreen'}
            # Call the normal entry point. Let exceptions exit without the interactive error box.
            # The Windows venv launcher starts a second executable. Use the base
            # interpreter with the same dependencies so this test owns the PID.
            invoke = ('import runpy,site,sys; site.addsitedir(sys.argv.pop(1)); '
                      'sys.exit(runpy.run_path(sys.argv.pop(1))["main"]())')
            packages = Path(sys.prefix) / 'Lib' / 'site-packages'
            command = [sys._base_executable, '-c', invoke, str(packages), str(APP / 'run.py'), '--background']
            flags = subprocess.CREATE_NO_WINDOW
            first = subprocess.Popen(command, cwd=APP, env=environment, creationflags=flags,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                client = ControllerClient(local / 'CodexDesktopAssistant')
                deadline = time.monotonic() + 16
                while True:
                    if first.poll() is not None:
                        self.fail(first.stderr.read().decode(errors='replace')[-2000:])
                    try:
                        health = client.request('bridge_health')
                        break
                    except (OSError, ValueError, RuntimeError):
                        if time.monotonic() > deadline:
                            raise
                        time.sleep(.1)
                self.assertTrue(health['portfolio_manager'])
                self.assertEqual(health['pid'], first.pid)
                self.assertEqual(client.request('portfolio_status')['workers'], [])
                duplicate = subprocess.run(command, cwd=APP, env=environment, creationflags=flags,
                                           capture_output=True, timeout=10)
                self.assertEqual(duplicate.returncode, 0, duplicate.stderr.decode(errors='replace')[-2000:])
                self.assertEqual(client.request('bridge_health')['pid'], first.pid)
            finally:
                first.terminate()
                first.wait(timeout=10)
                first.stderr.close()
