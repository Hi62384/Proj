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
    from PySide6.QtWidgets import QApplication, QTreeWidgetItem
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
            (repo / 'expanded-folder').mkdir()
            (repo / 'expanded-folder' / 'child.py').write_text('pass\n', encoding='utf-8')
            (repo / 'expanded-folder' / 'README.md').write_text('Folder purpose\n', encoding='utf-8')
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
                self.assertTrue(first.select('expanded-folder'))
                self.assertIn('Folder purpose', first.preview.toPlainText())
                self.assertIn('child.py', first.preview.toPlainText())
                (repo / 'expanded-folder' / 'README.md').write_text('Updated folder purpose\n', encoding='utf-8')
                first.sync()
                self.assertIn('Updated folder purpose', first.preview.toPlainText())
                Dashboard.show_workspace(dashboard, workspaces[0])
                self.assertEqual(list(dashboard.workspace_windows.values()), [first, second])
                self.assertNotEqual(first.workspace_id, second.workspace_id)
                self.assertTrue(first.select('source.py'))
                self.assertEqual(host.get_workspace(first.workspace_id)['selection'], 'source.py')
                self.assertEqual(first.preview.toPlainText(), 'print("hello")\n')
                self.assertEqual(first.tree.currentItem().data(0, ROLE), 'source.py')
                # Background synchronization should not pull a user's scrolled
                # tree back to the already selected item every 400 ms.
                with patch.object(first.tree, 'scrollToItem') as scroll_to_item:
                    first.sync()
                    scroll_to_item.assert_not_called()
                root_item = first.tree.topLevelItem(0)
                folder_item = next(root_item.child(i) for i in range(root_item.childCount())
                                   if root_item.child(i).data(0, ROLE) == 'expanded-folder')
                folder_item.setExpanded(True)
                self.assertTrue(folder_item.isExpanded())
                root_item.setExpanded(False)
                first.sync()
                self.assertFalse(root_item.isExpanded())
                root_item.setExpanded(True)
                (repo / 'new-file.py').write_text('pass\n', encoding='utf-8')
                first.sync()
                self.assertTrue(folder_item.isExpanded())
                self.assertEqual(folder_item.child(0).data(0, ROLE), 'expanded-folder/child.py')
                self.assertEqual(first.tree.currentItem().data(0, ROLE), 'source.py')
                self.assertIn('new-file.py', [first.tree.topLevelItem(0).child(i).data(0, ROLE)
                                              for i in range(first.tree.topLevelItem(0).childCount())])
                (repo / 'source.py').write_text('print("updated externally")\n', encoding='utf-8')
                first.sync()
                self.assertEqual(first.preview.toPlainText(), 'print("updated externally")\n')
                self.assertEqual(second.workspace_state['selection'], 'business_portfolio/niches')
                (repo / 'source.py').unlink()
                first.sync()
                self.assertEqual(first.preview.toPlainText(), 'The selected path is unavailable.')
                (repo / 'source.py').write_text('print("restored")\n', encoding='utf-8')
                first.sync()
                self.assertEqual(first.preview.toPlainText(), 'print("restored")\n')
                self.assertEqual(first.detail_stack.currentIndex(), 0)
                first.activity_button.click()
                self.assertEqual(first.detail_stack.currentIndex(), 1)
                self.assertTrue(first.tree.isVisible())
                first.activity_button.click()
                self.assertEqual(second.workspace_state['selection'], 'business_portfolio/niches')
                self.assertEqual(search_paths(repo, '.env'), [])

                # A later search must replace a still-running earlier query.
                from concurrent.futures import Future
                old_search = Future()
                first._search = old_search
                first._search_query = 'old'
                first.find.setText('source')
                first._find_files()
                self.assertEqual(first.search_status.text(), 'Searching files…')
                old_search.set_result([('cover.png', False)])
                first.sync()
                self.assertEqual(first._search_query, 'source')
                self.assertIsNotNone(first._search)

                # An empty result has an explanation instead of a blank tree.
                empty_search = Future()
                empty_search.set_result([])
                first._search = empty_search
                first._search_query = 'missing'
                first._pending_search = None
                first.sync()
                self.assertEqual(first.search_status.text(), 'No matches found in the folders searched.')
                first.find.clear()
                first._find_files()
                self.assertTrue(first.search_status.isHidden())

                host.select(second.workspace_id, record)
                second.sync()
                self.assertEqual(second.tree.currentItem().data(0, ROLE), record)
                self.assertEqual(second.panel.context_record, record)
                self.assertEqual(second.detail_stack.currentIndex(), 1)
                self.assertTrue(second.tree.isVisible())
                self.assertEqual(first.workspace_state['selection'], 'source.py')
                self.assertTrue(second._is_worker_selection())
                state = host.coordinator.snapshot()
                project = next(item for item in state['projects'] if item['record_path'] == record)
                project['eligible'] = True
                second.panel._apply_state(state, {'eligible': 1})
                self.assertTrue(second.panel.start.isEnabled())
                self.assertFalse(second.panel.develop.isHidden())
                self.assertTrue(second.panel.develop.isEnabled())
                revision = second.workspace_state['revision']
                with patch('portfolio_manager.workspace_window.QFileDialog.getExistingDirectory',
                           return_value=str(repo / 'expanded-folder')):
                    with patch.object(host, 'prepare_selected_development', return_value={'id': 'worker'}) as prepare:
                        second.panel.develop.click()
                        prepare.assert_called_once_with(
                            second.workspace_id, 'expanded-folder', expected_selection=record,
                            expected_revision=revision)
                with patch.object(host, 'start_workspace_worker', return_value={'id': 'worker'}) as start:
                    second.panel.start.click()
                    start.assert_called_once_with(second.workspace_id)
                project['eligible'] = False
                second.panel._apply_state(state, {'eligible': 1})
                self.assertFalse(second.panel.start.isEnabled())

                # Switching context clears the previous project's controls and
                # results immediately, before its replacement is loaded.
                first.panel._selected_project = 'DEMO-001'
                first.panel.review_task.show()
                first.panel.results.addTopLevelItem(QTreeWidgetItem(['Old result', 'Available']))
                first.panel.open_result.setEnabled(True)
                self.assertTrue(first.select(record))
                self.assertIsNone(first.panel._selected_project)
                self.assertTrue(first.panel.review_task.isHidden())
                self.assertEqual(first.panel.results.topLevelItemCount(), 0)
                self.assertFalse(first.panel.open_result.isEnabled())

                image = QImage(8, 8, QImage.Format.Format_RGB32)
                image.fill(0xffacb0ae)
                self.assertTrue(image.save(str(repo / 'cover.png')))
                self.assertTrue(first.select('cover.png'))
                self.assertFalse(first.image.pixmap().isNull())
                self.assertEqual(first.tree.currentItem().data(0, ROLE), 'cover.png')
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
