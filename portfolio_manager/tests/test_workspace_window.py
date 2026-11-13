"""The normal workspace view has only chat context and shared availability."""
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from portfolio_manager.integration import ManagerHost
from portfolio_manager.tests.test_runner import _record

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtWidgets import QApplication
except ModuleNotFoundError:
    QApplication = None
else:
    bridge_path = Path(__file__).resolve().parents[2] / 'apps' / 'codex_desktop_assistant'
    with patch.object(sys, 'path', [str(bridge_path), *sys.path]):
        from bridge.dashboard import Dashboard
    from portfolio_manager.workspace_window import ROLE, search_paths


@unittest.skipUnless(QApplication, 'PySide6 is required')
class WorkspaceWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_two_chat_windows_share_mode_but_not_selection(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'repo'
            record = _record(repo, 'DEMO-001').relative_to(repo).as_posix()
            (repo / 'source.py').write_text('answer = 42\n', encoding='utf-8')
            (repo / '.env').write_text('secret', encoding='utf-8')
            host = ManagerHost(repo, root / 'state')
            dashboard = SimpleNamespace(
                manager=host, runtime=SimpleNamespace(stop=lambda: None), workspace_windows={},
                cancel_bridge_work=lambda: None, show_computer_access=lambda: None, styleSheet=lambda: '',
            )
            try:
                a, b = [host.workspace(client, {}) for client in ('a' * 32, 'b' * 32)]
                Dashboard.show_workspace(dashboard, a)
                Dashboard.show_workspace(dashboard, b)
                first, second = dashboard.workspace_windows.values()
                self.assertGreaterEqual(first.tree.width(), 270)
                Dashboard.show_workspace(dashboard, a)
                self.assertEqual(len(dashboard.workspace_windows), 2)
                self.assertNotEqual(first.workspace_id, second.workspace_id)
                self.assertTrue(first.select('source.py'))
                self.assertEqual(first.preview.toPlainText(), 'answer = 42\n')
                self.assertEqual(first.tree.currentItem().data(0, ROLE), 'source.py')
                self.assertEqual(second.workspace_state['selection'], 'business_portfolio/niches')
                self.assertTrue(second.select(record))
                self.assertEqual(first.workspace_state['selection'], 'source.py')
                self.assertIn('DEMO-001', second.preview.toPlainText())
                self.assertEqual(search_paths(repo, '.env'), [])
                self.assertFalse(hasattr(first, 'panel'))
                self.assertFalse(hasattr(first, 'stop_worker'))
                first.mode.setCurrentIndex(first.mode.findData('human'))
                first._set_mode()
                second.sync()
                self.assertEqual(second.mode.currentData(), 'human')
                self.assertEqual(host.control()['mode'], 'human')
                first.close()
                self.assertIn(second.workspace_id, dashboard.workspace_windows)
                self.assertEqual(host.get_workspace(first.workspace_id)['selection'], 'source.py')
                reopened = host.workspace('a' * 32, {})
                Dashboard.show_workspace(dashboard, reopened)
                self.assertEqual(dashboard.workspace_windows[reopened['id']].workspace_state['selection'], 'source.py')
            finally:
                for window in list(dashboard.workspace_windows.values()):
                    window.close()
                host.close()
