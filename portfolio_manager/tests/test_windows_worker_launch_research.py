"""Tests for an intentionally non-launching Windows worker research contract."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from portfolio_manager.tests.windows_path_research import DirectoryHandle
from portfolio_manager.tests.windows_worker_launch_research import ExpectedLayout, ResearchLaunchPlan


@unittest.skipUnless(os.name == 'nt', 'Windows path APIs are required')
class ResearchLaunchPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='portfolio-launch-research-')
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name) / 'parent'
        self.parent.mkdir()
        (self.parent / 'home').mkdir()
        (self.parent / 'workspace').mkdir()
        (self.parent / 'workspace' / 'fixture.txt').write_bytes(b'fixture')
        with DirectoryHandle(self.parent) as parent, DirectoryHandle(self.parent / 'home') as home, \
             DirectoryHandle(self.parent / 'workspace') as workspace:
            handle, info = workspace._probe_open_relative('fixture.txt', directory=False)
            workspace.kernel.CloseHandle(handle)
            self.file_id = (info.volume, info.index_high, info.index_low)
            self.layout = ExpectedLayout(parent.identity, home.identity, workspace.identity)

    def test_verified_plan_reads_fixture_but_cannot_launch(self):
        with ResearchLaunchPlan(self.parent, self.layout) as plan:
            self.assertEqual(plan.read_workspace_fixture('fixture.txt', self.file_id, 7), b'fixture')
            with self.assertRaises(NotImplementedError):
                plan.launch()
        with self.assertRaises(ValueError):
            plan.read_workspace_fixture('fixture.txt', self.file_id, 7)

    def test_changed_parent_and_workspace_are_rejected(self):
        wrong = (0, 0, 0)
        with self.assertRaises(OSError):
            ResearchLaunchPlan(self.parent, ExpectedLayout(wrong, self.layout.home, self.layout.workspace))
        workspace = self.parent / 'workspace'
        workspace.rename(self.parent / 'old-workspace')
        workspace.mkdir()
        with self.assertRaises(OSError):
            ResearchLaunchPlan(self.parent, self.layout)

    def test_open_descendant_handles_block_parent_rename_in_this_fixture(self):
        with ResearchLaunchPlan(self.parent, self.layout) as plan:
            with self.assertRaises(OSError):
                self.parent.rename(Path(self.temp.name) / 'moved')
            self.assertEqual(plan.read_workspace_fixture('fixture.txt', self.file_id, 7), b'fixture')
            with self.assertRaises(NotImplementedError):
                plan.launch()

    def test_workspace_junction_is_rejected(self):
        workspace = self.parent / 'workspace'
        workspace.rename(self.parent / 'old-workspace')
        result = subprocess.run([os.environ.get('COMSPEC', r'C:\Windows\System32\cmd.exe'),
                                 '/d', '/c', 'mklink', '/J', str(workspace),
                                 str(self.parent / 'old-workspace')], capture_output=True, timeout=10)
        if result.returncode:
            self.skipTest('Disposable junction creation unavailable')
        self.addCleanup(lambda: workspace.rmdir() if workspace.exists() else None)
        with self.assertRaises(OSError):
            ResearchLaunchPlan(self.parent, self.layout)

    def test_parent_junction_is_rejected_even_if_target_identity_matches(self):
        alias = Path(self.temp.name) / 'parent-alias'
        result = subprocess.run([os.environ.get('COMSPEC', r'C:\Windows\System32\cmd.exe'),
                                 '/d', '/c', 'mklink', '/J', str(alias), str(self.parent)],
                                capture_output=True, timeout=10)
        if result.returncode:
            self.skipTest('Disposable junction creation unavailable')
        self.addCleanup(lambda: alias.rmdir() if alias.exists() else None)
        with self.assertRaises(OSError):
            ResearchLaunchPlan(alias, self.layout)


if __name__ == '__main__':
    unittest.main()
