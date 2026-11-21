"""The normal workspace view has only chat context and shared availability."""
import os
import json
from pathlib import Path
import sys
import threading
from tempfile import TemporaryDirectory
from time import perf_counter
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from portfolio_manager.integration import ManagerHost
from portfolio_manager.tests.test_runner import _record

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
Dashboard = None
try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
except ModuleNotFoundError:
    QApplication = None
    Qt = None
else:
    # The Bridge dashboard imports Windows-only desktop integrations. Headless
    # cross-platform tests can exercise the actual Portfolio Manager workspace
    # without loading those OS-specific modules.
    Dashboard = None
    if os.name == 'nt':
        bridge_path = Path(__file__).resolve().parents[2] / 'apps' / 'codex_desktop_assistant'
        with patch.object(sys, 'path', [str(bridge_path), *sys.path]):
            from bridge.dashboard import Dashboard
    from portfolio_manager.workspace_window import ROLE, NICHE_ID_ROLE, project_entries, search_paths, niche_entries, history_entries


@unittest.skipUnless(QApplication, 'PySide6 is required')
class WorkspaceWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_business_niches_show_order_and_counts(self):
        repo=Path(__file__).resolve().parents[2]
        rows=niche_entries(repo)
        from business_portfolio.tools.build_browser import load_portfolio
        metadata = load_portfolio(repo / 'business_portfolio')['niches']
        self.assertEqual({row[4] for row in rows}, {node['id'] for node in metadata})
        roots = [row for row in rows if row[0].count('/') == 2]
        self.assertEqual(len(roots), sum(node['parent'] is None for node in metadata))
        self.assertEqual([row[3] for row in roots], sorted(row[3] for row in roots))
        # Derive expected totals from canonical project records, not a hardcoded
        # count. Phase 1 can add project folders without changing this test.
        expected_counts = []
        for row in roots:
            category = repo / row[0]
            paths = list(category.glob('**/project.md'))
            paths += list(category.glob('**/projects/*.md'))
            expected_counts.append(sum(
                path.is_file() and 'work' not in path.relative_to(category).parts
                for path in paths
            ))
        self.assertEqual([row[2] for row in roots],expected_counts)
        entries = dict(project_entries(repo))
        self.assertTrue(all(entries.get(row[0]) for row in rows))

    def test_slow_navigation_scan_does_not_block_expanding_tree(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';_record(repo,'DEMO-020')
            host=ManagerHost(repo,root/'state');window=None
            release=threading.Event();started=threading.Event()
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window=WorkspaceWindow(host,host.workspace('b'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda _:None,on_close=lambda _:None)
                window._entry_future.result(timeout=5);window.sync()
                if window._signature_future:
                    window._signature_future.result(timeout=5);window.sync()
                window._signature_future=None;window._next_signature_check=0
                def slow_scan(repo):
                    started.set();release.wait(5);return ()
                with patch.object(window,'_current_working_signature',side_effect=slow_scan):
                    before=perf_counter();window.sync()
                    self.assertLess(perf_counter()-before,1)
                    self.assertTrue(started.wait(1))
                    item=window.tree.topLevelItem(0)
                    item.setExpanded(False);item.setExpanded(True)
                    before=perf_counter();window.sync()
                    self.assertLess(perf_counter()-before,1)
                    self.assertTrue(item.isExpanded())
            finally:
                release.set()
                if window:window.close()
                host.close()

    def test_niche_count_skips_project_work_directories(self):
        with TemporaryDirectory() as temp:
            repo=Path(temp)/'repo';_record(repo,'DEMO-021')
            work=repo/'business_portfolio/niches/demo/projects/example/work'
            work.mkdir(parents=True)
            (work/'NICHE.json').write_text('not portfolio metadata',encoding='utf-8')
            original=os.walk
            visited=[]
            def tracked(*args,**kwargs):
                for folder, dirs, files in original(*args,**kwargs):
                    visited.append(Path(folder))
                    yield folder, dirs, files
            with patch('portfolio_manager.workspace_window.os.walk', side_effect=tracked):
                rows=niche_entries(repo)
            self.assertEqual(rows[0][2],1)
            self.assertNotIn(work,visited)

    def test_closed_window_is_released_without_waiting_for_cyclic_gc(self):
        import weakref
        from PySide6.QtCore import QCoreApplication, QEvent
        from portfolio_manager.workspace_window import WorkspaceWindow
        with TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'; _record(repo, 'DEMO-023')
            host = ManagerHost(repo, root / 'state')
            window = None
            try:
                window = WorkspaceWindow(host, host.workspace('d' * 32, {}),
                                         on_emergency=lambda: None, on_stop_all=lambda: None,
                                         on_access=lambda: None, on_close=lambda _: None)
                window._entry_future.result(timeout=5); window.sync()
                # Recursive visitor closures used to retain the entire Qt window
                # until GC, which may run on a filesystem worker thread.
                for _ in range(5):
                    window._refresh_working_rows()
                    window._refresh_project_phase_rows()
                reference = weakref.ref(window)
                window.close()
                window._pool.shutdown(wait=True, cancel_futures=True)
                QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
                self.app.processEvents()
                window = None
                self.assertIsNone(reference())
            finally:
                if window is not None:
                    window.close()
                host.close()

    def test_slow_folder_preview_does_not_block_or_replace_new_selection(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';_record(repo,'DEMO-022')
            (repo/'sample.txt').write_text('new selection',encoding='utf-8')
            host=ManagerHost(repo,root/'state');window=None
            release=threading.Event();started=threading.Event()
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow, folder_preview
                window=WorkspaceWindow(host,host.workspace('c'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda _:None,on_close=lambda _:None)
                window._entry_future.result(timeout=5);window.sync()
                if window._preview_future:
                    window._preview_future[1].result(timeout=5);window.sync()
                def slow_preview(repo, selection):
                    started.set();release.wait(5);return folder_preview(repo, selection)
                with patch('portfolio_manager.workspace_window.folder_preview', side_effect=slow_preview):
                    before=perf_counter()
                    self.assertTrue(window.select('business_portfolio/niches/demo'))
                    self.assertLess(perf_counter()-before,1)
                    self.assertTrue(started.wait(1))
                    self.assertTrue(window.select('sample.txt'))
                    self.assertEqual(window.preview.toPlainText(),'new selection')
                    release.set();window.sync()
                    self.assertEqual(window.preview.toPlainText(),'new selection')
            finally:
                release.set()
                if window:window.close()
                host.close()

    @staticmethod
    def _copy_templates(repo):
        from portfolio_manager.workspace_window import PROMPTS
        source = Path(__file__).resolve().parents[2]
        for _, filename, _ in PROMPTS.values():
            (repo / filename).write_bytes((source / filename).read_bytes())
        template = repo / 'business_portfolio/tools/browser_template.html'
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_bytes((source / 'business_portfolio/tools/browser_template.html').read_bytes())

    def _open_window(self, repo, state):
        from portfolio_manager.workspace_window import WorkspaceWindow
        host = ManagerHost(repo, state)
        window = WorkspaceWindow(host, host.workspace('a' * 32, {}),
                                 on_emergency=lambda: None, on_stop_all=lambda: None,
                                 on_access=lambda: None, on_close=lambda _: None,
                                 on_resume=lambda: None)
        closed = []
        def close():
            if not closed:
                closed.append(True)
                del window._test_close
                window.close()
                window._pool.shutdown(wait=True, cancel_futures=True)
                from PySide6.QtCore import QCoreApplication, QEvent
                QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
                self.app.processEvents()
                host.close()
        window._test_close = close
        self.addCleanup(close)
        window._entry_future.result(timeout=10)
        window.sync()
        return window

    def _paste_dialog(self, window, text):
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QDialogButtonBox, QPlainTextEdit
        failures = []
        def fill():
            dialog = self.app.activeModalWidget()
            try:
                dialog.findChild(QPlainTextEdit).setPlainText(text)
                dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Save).click()
                if dialog.isVisible():
                    failures.append('The pasted text was rejected.')
                    dialog.reject()
            except Exception as error:
                failures.append(str(error))
                if dialog:
                    dialog.reject()
        QTimer.singleShot(0, fill)
        window._paste_project()
        self.assertEqual(failures, [])

    def test_empty_project_creation_research_text_and_manual_handoffs(self):
        with TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'
            _record(repo, 'DEMO-011')
            self._copy_templates(repo)
            window = self._open_window(repo, root / 'state')
            self.assertTrue(window.research_tools.isHidden())
            self.assertTrue(window.select('business_portfolio/niches/demo'))
            self.assertFalse(window.niche_tools.isHidden())
            self.assertTrue(window.research_tools.isHidden())
            self.assertEqual(window.prompt_menu.actions(), [])
            window.new_project.click()
            selection = window.workspace_state['selection']
            self.assertNotIn('/projects/', selection)
            from business_portfolio.tools.build_browser import parse_project
            from portfolio_manager.project_update import snapshot_sha256
            path = repo / selection
            meta, body = parse_project(path.read_text())
            self.assertEqual((meta['title'], meta['project_phase']), ('Empty project', 'working_phase_1'))
            self.assertEqual(window.copy_prompt.text(), 'Copy research prompt')
            self.assertFalse(window.paste_project.isHidden())
            window.research_budget.setText('50.25')
            window._copy_megaprompt('research')
            copied = self.app.clipboard().text()
            self.assertIn(path.read_text(), copied)
            self.assertIn('BASE_SHA256: ' + snapshot_sha256(path.read_text()), copied)
            self.assertIn('BUSINESS_NICHE: Demo', copied)
            self.assertIn('BUDGET_CEILING_CAD: 50.25', copied)
            self.assertFalse(copied.startswith('/goal'))
            from PySide6.QtWidgets import QInputDialog
            with patch.object(QInputDialog, 'getMultiLineText', return_value=('A useful pathfinding system', True)):
                window._copy_megaprompt('idea')
            self.assertIn('PROJECT_IDEA:\nA useful pathfinding system', self.app.clipboard().text())
            window._copy_megaprompt('recheck')
            self.assertIn('Good to go', self.app.clipboard().text())
            # Empty placeholders cannot advance just by clicking the handoff.
            window.phase_apply.click()
            self.assertEqual(parse_project(path.read_text())[0]['project_phase'], 'working_phase_1')
            meta.update(title='Useful Pathfinding', record_type='software_product', draft=False,
                        next_action='Recheck the product specification.',
                        project_update_base_sha256=snapshot_sha256(path.read_text()))
            research = '---\n' + json.dumps(meta) + '\n---\n# Useful Pathfinding\n' + body + (
                '\nProduct research with concrete buyers, functionality and acceptance tests. '
                'Evidence: https://example.org/research\n')
            self._paste_dialog(window, '```markdown\n' + research + '\n```')
            self.assertEqual(parse_project(path.read_text())[0]['project_phase'], 'working_phase_1')
            self.assertEqual(parse_project(path.read_text())[0]['title'], 'Useful Pathfinding')
            window.phase_apply.click()
            self.assertEqual(parse_project(path.read_text())[0]['project_phase'], 'working_phase_2')
            self.assertEqual(window.copy_prompt.text(), 'Copy release research prompt')
            self.assertEqual(len(window.prompt_menu.actions()), 2)
            window._copy_megaprompt('phase2')
            self.assertIn(path.read_text(), self.app.clipboard().text())
            window._copy_megaprompt('phase2_recheck')
            self.assertIn('Good to go', self.app.clipboard().text())
            window.phase_apply.click()
            self.assertEqual(parse_project(path.read_text())[0]['project_phase'], 'working_phase_3')
            self.assertEqual(window.copy_prompt.text(), 'Copy marketing research prompt')
            window._copy_megaprompt('phase3_recheck')
            self.assertIn('Good to go', self.app.clipboard().text())
            window.phase_apply.click()
            self.assertEqual(parse_project(path.read_text())[0]['project_phase'], 'working_phase_4')
            self.assertEqual(window.copy_prompt.text(), 'Copy build prompt')
            self.assertTrue(window.paste_project.isHidden())
            self.assertFalse(window.phase_apply.isEnabled())
            window._test_close()

    def test_execution_prompt_handoffs_and_full_record_progress(self):
        with TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'
            legacy = _record(repo, 'DEMO-012')
            folder = legacy.parent.parent / 'demo-012'
            (folder / 'work').mkdir(parents=True)
            path = folder / 'project.md'
            from business_portfolio.tools.build_browser import parse_project
            meta, body = parse_project(legacy.read_text())
            meta.update(workflow_version=2, project_phase='working_phase_4')
            path.write_text('---\n' + json.dumps(meta) + '\n---\n' + body +
                            '\n' + 'Preserved research. ' * 8000 +
                            '\nPhase 4 completion estimate: 37% (best guess)\n')
            legacy.unlink()
            self._copy_templates(repo)
            window = self._open_window(repo, root / 'state')
            selection = path.relative_to(repo).as_posix()
            self.assertTrue(window.select(selection))
            self.assertIn('37%', window.project_tasks.toPlainText())
            self.assertIn('37%', window.project_record.toPlainText())
            from portfolio_manager.project_lifecycle import set_phase, read_completions
            for number, label in ((4, 'build'), (5, 'release'), (6, 'marketing')):
                window._preview(selection)
                self.assertEqual(window.copy_prompt.text(), f'Copy {label} prompt')
                self.assertEqual(len(window.prompt_menu.actions()), 1)
                self.assertTrue(window.research_budget.isHidden())
                self.assertTrue(window.paste_project.isHidden())
                window._copy_megaprompt(f'phase{number}')
                self.assertTrue(self.app.clipboard().text().startswith('/goal '))
                self.assertIn(selection, self.app.clipboard().text())
                self.assertIn(f'Phase {number} completion estimate:', self.app.clipboard().text())
                if number < 6:
                    set_phase(repo, selection, f'working_phase_{number+1}', actor='codex',
                              evidence=f'Fictional Phase {number} completed evidence.')
            receipt = set_phase(repo, selection, 'complete', actor='codex', evidence='All marketing checked.',
                                description='Fictional end-to-end completed product.',
                                sale_urls=['https://example.org/shop'], marketing_urls=['https://example.org/post'])
            window._preview(selection)
            self.assertTrue(window.research_tools.isHidden())
            self.assertEqual(len(read_completions(repo)), 1)
            self.assertTrue(Path(receipt['snapshot']).is_file())
            window._test_close()

    def test_niche_buttons_create_child_and_delete_recoverably(self):
        with TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'
            _record(repo, 'DEMO-040')
            self._copy_templates(repo)
            window = self._open_window(repo, root / 'state')
            parent = 'business_portfolio/niches/demo'
            window.select(parent)
            from PySide6.QtWidgets import QInputDialog, QMessageBox
            with patch.object(QInputDialog, 'getText', return_value=('Work', True)):
                window.new_niche.click()
            child = window.workspace_state['selection']
            self.assertEqual(child, parent + '/work')
            self.assertTrue((repo / child / 'NICHE.json').is_file())
            window.new_project.click()
            project = repo / window.workspace_state['selection']
            self.assertTrue(project.is_file())
            window._entry_future.result(timeout=10); window.sync()
            self.assertIn(child, [row[0] for row in window._niche_entries])
            window.select(child)
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.No):
                window.delete_niche.click()
            self.assertTrue(project.is_file())
            with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
                window.delete_niche.click()
            self.assertFalse((repo / child).exists(), window.notice.text())
            self.assertEqual(window.workspace_state['selection'], parent)
            recovery = repo / 'business_portfolio/.local/deleted_niches'
            self.assertEqual(len(list(recovery.rglob('project.md'))), 1)
            self.assertTrue(window.research_tools.isHidden())
            window._test_close()

    def test_drop_update_on_research_detail_preserves_phase_and_work(self):
        with TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'
            legacy = _record(repo, 'DEMO-030')
            folder = legacy.parent.parent / 'demo-030'
            (folder / 'work').mkdir(parents=True)
            path = folder / 'project.md'
            from business_portfolio.tools.build_browser import parse_project
            meta, body = parse_project(legacy.read_text())
            meta.update(workflow_version=2, project_phase='working_phase_3')
            path.write_text('---\n' + json.dumps(meta) + '\n---\n' + body)
            legacy.unlink()
            owned = folder / 'work/keep.txt'; owned.write_text('owned work')
            self._copy_templates(repo)
            window = self._open_window(repo, root / 'state')
            window.show()
            selection = path.relative_to(repo).as_posix()
            window.select(selection)
            window.project_tabs.setCurrentWidget(window.project_record)
            self.app.processEvents()
            from portfolio_manager.project_update import snapshot_sha256
            meta['project_update_base_sha256'] = snapshot_sha256(path.read_text())
            update = root / 'updated.md'
            update.write_text('---\n' + json.dumps(meta) + '\n---\n# Revised marketing plan\n'
                              'Specific audiences, appropriate channels and measured initial actions. '
                              'https://example.org/marketing-policy\n')
            from PySide6.QtCore import QPoint, QPointF, QMimeData, QUrl
            from PySide6.QtGui import QDragEnterEvent, QDropEvent
            mime = QMimeData(); mime.setUrls([QUrl.fromLocalFile(str(update))])
            enter = QDragEnterEvent(QPoint(10, 10), Qt.DropAction.CopyAction, mime,
                                    Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
            target = window.project_record.viewport()
            self.app.sendEvent(target, enter)
            self.assertTrue(enter.isAccepted())
            drop = QDropEvent(QPointF(10, 10), Qt.DropAction.CopyAction, mime,
                              Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
            self.app.sendEvent(target, drop)
            self.assertTrue(drop.isAccepted(), window.notice.text())
            self.assertEqual(parse_project(path.read_text())[0]['project_phase'], 'working_phase_3')
            self.assertIn('Revised marketing plan', window.project_record.toPlainText())
            self.assertEqual(owned.read_text(), 'owned work')
            self.assertEqual(window.copy_prompt.text(), 'Copy marketing research prompt')
            window._test_close()

    def test_working_toggles_persist_and_sync_between_windows(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';_record(repo,'DEMO-010')
            parent=repo/'business_portfolio/niches/demo/NICHE.json'
            meta=json.loads(parent.read_text());meta.update(priority=1,working=False);parent.write_text(json.dumps(meta))
            child=repo/'business_portfolio/niches/demo/child';child.mkdir()
            childfile=child/'NICHE.json'
            childfile.write_text(json.dumps({'id':'N-child','title':'Child','parent':'N-demo','path':'demo/child','priority':1,'working':False}))
            host=ManagerHost(repo,root/'state');windows=[]
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                for client in ('1'*32,'2'*32):
                    window=WorkspaceWindow(host,host.workspace(client,{}),on_emergency=lambda:None,
                                           on_stop_all=lambda:None,on_access=lambda:None,on_close=lambda _:None)
                    windows.append(window)
                first,second=windows
                def find_item(window,ident):
                    def walk(item):
                        if item.data(0,NICHE_ID_ROLE)==ident:return item
                        for i in range(item.childCount()):
                            found=walk(item.child(i))
                            if found:return found
                    return walk(window.tree.topLevelItem(0))
                deadline=perf_counter()+4
                while (not first._entries_ready or not second._entries_ready) and perf_counter()<deadline:
                    first.sync();second.sync();self.app.processEvents()
                self.assertEqual(first._drop_niche_from_item(find_item(first,'N-child')),
                                 'business_portfolio/niches/demo/child')
                self.assertIsNone(first._drop_niche_from_item(first.tree.topLevelItem(0)))
                find_item(first,'N-child').setCheckState(0,Qt.CheckState.Checked)
                with patch.object(first, '_load_navigation_entries', wraps=first._load_navigation_entries):
                    first._entries_ready = False
                    first._root_node()
                    self.assertIsNotNone(find_item(first, 'N-child'))
                    first._entries_ready = True
                deadline=perf_counter()+4
                while not json.loads(childfile.read_text())['working'] and perf_counter()<deadline:
                    first.sync();self.app.processEvents()
                self.assertTrue(json.loads(childfile.read_text())['working'])
                self.assertTrue(json.loads(parent.read_text())['working'])
                self.assertEqual(find_item(first,'N-demo').checkState(0),Qt.CheckState.Checked)
                self.assertEqual(find_item(first,'N-child').icon(0).cacheKey(),first._working_folder_icon.cacheKey())
                deadline=perf_counter()+4
                while (find_item(second,'N-child') is None or find_item(second,'N-child').checkState(0)!=Qt.CheckState.Checked) and perf_counter()<deadline:
                    second.sync();self.app.processEvents()
                self.assertEqual(find_item(second,'N-child').checkState(0),Qt.CheckState.Checked)
                find_item(first,'N-demo').setCheckState(0,Qt.CheckState.Unchecked)
                self.assertTrue(json.loads(parent.read_text())['working'])
                self.assertEqual(find_item(first,'N-demo').checkState(0),Qt.CheckState.Checked)
                find_item(first,'N-child').setCheckState(0,Qt.CheckState.Unchecked)
                self.assertTrue(json.loads(parent.read_text())['working'])
                self.assertFalse(json.loads(childfile.read_text())['working'])
            finally:
                for window in windows:window.close()
                host.close()

    def test_history_contains_both_preserved_archives(self):
        repo = Path(__file__).resolve().parents[2]
        names = {name for name, _ in history_entries(repo)}
        self.assertTrue(any('/2026-11-15-legacy/niches/' in name and name.endswith('.md') for name in names))
        self.assertTrue(any('/2026-11-15-taxonomy-view-v1/niches/' in name and name.endswith('.md')
                            for name in names))

    @unittest.skipUnless(Dashboard, 'Windows-only Computer Bridge integration')
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

    def test_project_folder_navigation_and_independent_completed_receipts(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo'
            old=_record(repo,'DEMO-009')
            folder=old.parent/'demo-009-example'
            (folder/'work').mkdir(parents=True)
            (folder/'work'/'.gitkeep').write_text('')
            project=folder/'project.md'
            project.write_bytes(old.read_bytes())
            old.unlink()
            relative=project.relative_to(repo).as_posix()
            entries=dict(project_entries(repo))
            self.assertIs(entries.get(relative),False)
            self.assertNotIn(folder.relative_to(repo).as_posix(),entries)
            from portfolio_manager.project_lifecycle import set_phase,read_completions
            host=ManagerHost(repo,root/'state');window=None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window=WorkspaceWindow(host,host.workspace('9'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda:None,on_close=lambda _:None)
                window._entry_future.result(timeout=10)
                window.sync()
                self.assertTrue(window.select(relative))
                self.assertFalse(window.project_tabs.isHidden())
                self.assertIn('work',window.project_files.toPlainText())
                set_phase(repo,relative,'working_phase_3')
                set_phase(repo,relative,'working_phase_4')
                set_phase(repo,relative,'working_phase_5',actor='codex',evidence='Build checked.')
                set_phase(repo,relative,'working_phase_6',actor='codex',evidence='Release checked.')
                window.sync()
                receipt=set_phase(repo,relative,'complete',actor='codex',evidence='Marketing checked.',description='Fictional completed project',
                    sale_urls=['https://example.org/shop'],marketing_urls=['https://example.org/post'])
                self.assertEqual(len(read_completions(repo)),1)
                window.sync()
                window.view_mode.setCurrentIndex(window.view_mode.findData('completed'))
                window._change_view()
                window._entry_future.result(timeout=10)
                window.sync()
                self.assertTrue(window.select(Path(receipt['snapshot']).relative_to(repo).as_posix()))
                self.assertFalse(window.completed_detail.isHidden())
                self.assertIn('https://example.org/shop',window.completed_detail.toHtml())
                project.unlink()
                self.assertEqual(len(read_completions(repo)),1)
            finally:
                if window:window.close()
                host.close()

    def test_project_phase_control_uses_validated_transitions(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'repo'
            legacy = _record(repo, 'DEMO-015')
            folder = legacy.parent / 'demo-015'
            folder.mkdir()
            record = folder / 'project.md'
            legacy.rename(record)
            (folder / 'work').mkdir()
            host = ManagerHost(repo, root / 'state')
            window = None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window = WorkspaceWindow(host, host.workspace('b' * 32, {}),
                                         on_emergency=lambda: None, on_stop_all=lambda: None,
                                         on_access=lambda _: None, on_close=lambda _: None)
                selection = record.relative_to(repo).as_posix()
                window._preview(selection)
                self.assertFalse(window.phase_controls.isHidden())
                self.assertEqual(window.phase_selector.currentData(), 'working_phase_2')
                self.assertEqual([window.view_mode.itemText(i)
                                  for i in range(window.view_mode.count())],
                                 ['Projects', 'Completed Projects'])
                window.phase_selector.setCurrentIndex(window.phase_selector.findData('working_phase_3'))
                from PySide6.QtWidgets import QMessageBox
                with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
                    window._apply_project_phase()
                from business_portfolio.tools.build_browser import parse_project
                meta, _ = parse_project(record.read_text(encoding='utf-8'), selection)
                self.assertEqual(meta['project_phase'], 'working_phase_3')
                self.assertEqual(window.phase_selector.currentData(), 'working_phase_3')
                window.phase_selector.setCurrentIndex(window.phase_selector.findData('working_phase_2'))
                with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
                    window._apply_project_phase()
                meta, _ = parse_project(record.read_text(encoding='utf-8'), selection)
                self.assertEqual(meta['project_phase'], 'working_phase_2')

                # The owner can demote a completed project directly to Phase 2.
                # Verified completion itself remains Codex-only.
                from portfolio_manager.project_lifecycle import set_phase, read_completions
                set_phase(repo, selection, 'working_phase_3')
                set_phase(repo, selection, 'working_phase_4')
                set_phase(repo, selection, 'working_phase_5', actor='codex', evidence='Build checked.')
                set_phase(repo, selection, 'working_phase_6', actor='codex', evidence='Release checked.')
                set_phase(repo, selection, 'complete', actor='codex', evidence='Marketing checked.', description='Verified fixture',
                          sale_urls=['https://example.org/release'],
                          marketing_urls=['https://example.org/announcement'])
                window._preview(selection)
                self.assertEqual(window.phase_selector.currentData(), 'complete')
                self.assertFalse(window.phase_selector.model().item(
                    window.phase_selector.findData('complete')).isEnabled())
                window.phase_selector.setCurrentIndex(window.phase_selector.findData('working_phase_2'))
                with patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes):
                    window._apply_project_phase()
                meta, _ = parse_project(record.read_text(encoding='utf-8'), selection)
                self.assertEqual(meta['project_phase'], 'working_phase_2')
                self.assertEqual(read_completions(repo), [])
            finally:
                if window:
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
                # Repository browsing remains supported internally, but is no longer
                # exposed in the two-choice end-user section selector.
                self.assertEqual([window.view_mode.itemText(i) for i in range(window.view_mode.count())],
                                 ['Projects', 'Completed Projects'])
                window._tree_mode = 'files'
                window._root_node()
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
