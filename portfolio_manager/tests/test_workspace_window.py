"""Exercise independent native Qt views over a disposable shared controller."""
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
    from PySide6.QtGui import QImage
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

    def test_two_views_follow_only_their_chat_and_share_mode(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'repo'
            record = _record(repo, 'DEMO-001').relative_to(repo).as_posix()
            (repo / 'source.py').write_text('print("hello")\n', encoding='utf-8')
            (repo / '.env').write_text('private', encoding='utf-8')
            host = ManagerHost(repo, root / 'state')
            dashboard = SimpleNamespace(
                manager=host, runtime=SimpleNamespace(stop=lambda: None), workspace_windows={},
                cancel_bridge_work=lambda: None, show_computer_access=lambda: None, styleSheet=lambda: '',
            )
            try:
                workspaces = [host.workspace(client, {}) for client in ('a' * 32, 'b' * 32)]
                for workspace in workspaces:
                    Dashboard.show_workspace(dashboard, workspace)
                first, second = dashboard.workspace_windows.values()
                Dashboard.show_workspace(dashboard, workspaces[0])
                self.assertEqual(list(dashboard.workspace_windows.values()), [first, second])
                self.assertNotEqual(first.workspace_id, second.workspace_id)
                self.assertTrue(first.select('source.py'))
                self.assertEqual(host.get_workspace(first.workspace_id)['selection'], 'source.py')
                self.assertEqual(first.preview.toPlainText(), 'print("hello")\n')
                self.assertEqual(first.tree.currentItem().data(0, ROLE), 'source.py')
                self.assertEqual(second.workspace_state['selection'], 'business_portfolio/niches')
                self.assertEqual(search_paths(repo, '.env'), [])

                host.select(second.workspace_id, record)
                second.sync()
                self.assertEqual(second.tree.currentItem().data(0, ROLE), record)
                self.assertEqual(second.panel.context_record, record)
                self.assertEqual(first.workspace_state['selection'], 'source.py')

                image = QImage(8, 8, QImage.Format.Format_RGB32)
                image.fill(0xffacb0ae)
                self.assertTrue(image.save(str(repo / 'cover.png')))
                self.assertTrue(first.select('cover.png'))
                self.assertFalse(first.image.pixmap().isNull())
                self.assertTrue(first.select('source.py'))

                first.panel.mode.setCurrentIndex(first.panel.mode.findData('human'))
                first.panel._set_mode()
                second.sync()
                self.assertEqual(second.panel.mode.currentData(), 'human')
                first.close()
                self.assertEqual(list(dashboard.workspace_windows), [second.workspace_id])
                self.assertTrue(second.isVisible())
                self.assertEqual(host.get_workspace(first.workspace_id)['selection'], 'source.py')
            finally:
                for window in list(dashboard.workspace_windows.values()):
                    window.close()
                host.close()
