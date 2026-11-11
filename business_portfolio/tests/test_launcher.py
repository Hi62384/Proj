"""Launcher regressions; no live browser opens in unit tests."""
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock,patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import launch_browser as launcher
import serve_browser as service


class LauncherTests(unittest.TestCase):
    def test_reused_service_still_requests_browser_open(self):
        with patch.object(launcher,'ensure_service',return_value=None) as ensure,patch.object(launcher.webbrowser,'open',return_value=True) as browser:
            self.assertEqual(launcher.main([]),0)
            ensure.assert_called_once_with(ROOT,22841)
            browser.assert_called_once_with('http://127.0.0.1:22841/',new=0)
    def test_existing_health_does_not_spawn_another_service(self):
        with patch.object(service,'probe',return_value=True),patch.object(launcher.subprocess,'Popen') as start:
            self.assertIsNone(launcher.ensure_service(ROOT,22841));start.assert_not_called()
    def test_browser_failure_is_visible_and_nonzero(self):
        error=io.StringIO()
        with patch.object(launcher,'ensure_service'),patch.object(launcher.webbrowser,'open',return_value=False),patch.object(sys,'stderr',error):
            self.assertEqual(launcher.main([]),1)
        self.assertIn('default browser',error.getvalue());self.assertIn('http://127.0.0.1:22841/',error.getvalue())
    def test_startup_failure_reports_local_log_and_returns_nonzero(self):
        error=io.StringIO()
        with patch.object(launcher,'ensure_service',side_effect=RuntimeError('Synthetic startup failure')),patch.object(sys,'stderr',error):
            self.assertEqual(launcher.main([]),1)
        self.assertIn('Synthetic startup failure',error.getvalue());self.assertIn('browser-startup.log',error.getvalue())
    def test_failed_child_is_logged_and_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);child=Mock();child.poll.return_value=2
            with patch.object(service,'probe',return_value=False),patch.object(launcher.subprocess,'Popen',return_value=child):
                with self.assertRaisesRegex(RuntimeError,'stopped during startup'):launcher.ensure_service(root,22841)
            self.assertTrue((root/'.local/browser-startup.log').is_file())
    def test_bind_race_reuse_with_open_still_opens_page(self):
        with patch.object(sys,'argv',['serve_browser.py','--open']),patch.object(service,'probe',side_effect=[False,True]),patch.object(service,'PortfolioState'),patch.object(service,'LocalServer',side_effect=OSError()),patch.object(service.webbrowser,'open',return_value=True) as browser:
            self.assertEqual(service.main(),0);browser.assert_called_once_with('http://127.0.0.1:22841/',new=0)
    def test_unrelated_working_directory_does_not_change_root(self):
        with tempfile.TemporaryDirectory() as directory:
            run=subprocess.run([sys.executable,'-c',"import sys;sys.path.insert(0,sys.argv[1]);import launch_browser;print(launch_browser.ROOT)",str(ROOT/'tools')],cwd=directory,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(Path(run.stdout.strip()),ROOT)
    def test_actual_cmd_failure_stays_visible(self):
        if sys.platform!='win32':self.skipTest('Windows CMD check')
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'launcher with spaces';folder.mkdir();cmd=folder/'Open_Project_Browser.cmd';cmd.write_bytes((ROOT/'Open_Project_Browser.cmd').read_bytes())
            # Deliberately omit its Python entry point, and acknowledge the test-only pause via stdin.
            run=subprocess.run(['cmd.exe','/d','/c',str(cmd)],cwd=Path(directory),input='\n',text=True,capture_output=True,timeout=15)
            self.assertNotEqual(run.returncode,0);self.assertIn('Read the error above',run.stdout);self.assertIn('browser-startup.log',run.stdout)

if __name__=='__main__':unittest.main()
