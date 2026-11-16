"""The normal workspace view has only chat context and shared availability."""
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
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
    from portfolio_manager.workspace_window import ROLE, project_entries, search_paths


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
                self.assertNotIn('source.py', [name for name, _ in project_entries(repo)])
                self.assertIn(record, [name for name, _ in project_entries(repo)])
                self.assertEqual(first.tree.topLevelItem(0).childCount(), 1)
                self.assertEqual(second.workspace_state['selection'], 'business_portfolio/niches')
                self.assertTrue(second.select(record))
                self.assertEqual(first.workspace_state['selection'], 'source.py')
                self.assertIn('DEMO-001', second.preview.toPlainText())
                self.assertTrue(second.project_tabs.isVisible())
                self.assertIn('Next step:', second.project_overview.toPlainText())
                self.assertIn('Progress percentage: not measured.', second.project_tasks.toPlainText())
                for item in (second.tree.topLevelItem(0), second.tree.topLevelItem(0).child(0)):
                    second._expand(item)
                self.assertEqual(second.tree.topLevelItem(0).childCount(), 1)
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

    def test_optional_repository_explorer_loads_without_blocking(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'repo'
            _record(repo, 'DEMO-003')
            (repo / 'architecture.html').write_text('ordinary repository file', encoding='utf-8')
            host = ManagerHost(repo, root / 'state')
            window = None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                workspace = host.workspace('e' * 32, {})
                window = WorkspaceWindow(host, workspace, on_emergency=lambda: None,
                                         on_stop_all=lambda: None, on_access=lambda: None,
                                         on_close=lambda _: None)
                self.assertNotIn('architecture.html', [name for name, _ in project_entries(repo)])
                window.view_mode.setCurrentIndex(window.view_mode.findData('files'))
                window._change_view()
                deadline = perf_counter() + 3
                while window._file_loads and perf_counter() < deadline:
                    window.sync()
                    self.app.processEvents()
                self.assertFalse(window._file_loads)
                self.assertIn('architecture.html', [window.tree.topLevelItem(0).child(i).data(0, ROLE)
                    for i in range(window.tree.topLevelItem(0).childCount())])
                self.assertTrue(window.select('architecture.html'))
                self.assertEqual(window.preview.toPlainText(), 'ordinary repository file')
            finally:
                if window:
                    window.close()
                host.close()

    def test_project_tree_omits_unrelated_files_and_expands_without_scanning(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'repo'
            record = _record(repo, 'DEMO-002').relative_to(repo).as_posix()
            (repo / 'architecture.html').write_text('unrelated', encoding='utf-8')
            (repo / 'business_portfolio' / 'niches' / 'unrelated.txt').write_text('unrelated', encoding='utf-8')
            host = ManagerHost(repo, root / 'state')
            workspace = host.workspace('c' * 32, {})
            other = host.workspace('d' * 32, {})
            window = None
            other_window = None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window = WorkspaceWindow(host, workspace, on_emergency=lambda: None,
                                         on_stop_all=lambda: None, on_access=lambda: None,
                                         on_close=lambda _: None)
                other_window = WorkspaceWindow(host, other, on_emergency=lambda: None,
                                               on_stop_all=lambda: None, on_access=lambda: None,
                                               on_close=lambda _: None)
                names = [name for name, _ in project_entries(repo)]
                self.assertIn(record, names)
                self.assertNotIn('architecture.html', names)
                self.assertNotIn('business_portfolio/niches/unrelated.txt', names)
                with patch('portfolio_manager.workspace_window.children', side_effect=AssertionError('filesystem scan')):
                    parent = window.tree.topLevelItem(0)
                    while parent.childCount():
                        parent.setExpanded(True)
                        parent = parent.child(0)
                    self.app.processEvents()
                folder = str(Path(record).parent.parent).replace('\\', '/')
                host.select(workspace['id'], folder)
                window.sync()
                self.assertEqual(window.workspace_state['selection'], folder)
                self.assertEqual(window.tree.currentItem().data(0, ROLE), folder)
                started = perf_counter()
                for _ in range(30):
                    window.tree.topLevelItem(0).setExpanded(False)
                    window.tree.topLevelItem(0).setExpanded(True)
                    window.sync()
                    other_window.sync()
                    self.app.processEvents()
                self.assertLess(perf_counter() - started, 5)
                self.assertEqual(other_window.workspace_state['selection'], 'business_portfolio/niches')
            finally:
                if window:
                    window.close()
                if other_window:
                    other_window.close()
                host.close()
