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
        self.assertEqual(len(rows),39)
        roots = [row for row in rows if row[0].count('/') == 2]
        self.assertEqual(len(roots),5)
        self.assertEqual([row[3] for row in roots],list(range(1,6)))
        # Derive expected totals from canonical project records, not a hardcoded
        # count. Phase 1 can add project folders without changing this test.
        expected_counts = []
        for row in roots:
            category = repo / row[0]
            paths = list(category.glob('**/projects/*/project.md'))
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
                def slow_scan():
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

    def test_phase2_prompt_button_copies_complete_goal(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';_record(repo,'DEMO-012')
            source=Path(__file__).resolve().parents[2]/'PHASE_2_DEVELOPMENT_MEGAPROMPT.md'
            (repo/source.name).write_bytes(source.read_bytes())
            host=ManagerHost(repo,root/'state');window=None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window=WorkspaceWindow(host,host.workspace('a'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda _:None,on_close=lambda _:None)
                self.app.clipboard().setText('previous')
                window._copy_megaprompt('phase2')
                self.assertEqual(self.app.clipboard().text().replace('\r\n','\n'), source.read_text(encoding='utf-8'))
                self.assertTrue(self.app.clipboard().text().startswith('/goal '))
                self.assertIn('working_phase_3', self.app.clipboard().text())
                self.assertEqual(window.notice.text(), 'Phase 2 development megaprompt copied.')
                self.assertEqual(host.get_workspace(window.workspace_id)['selection'], 'business_portfolio/niches')
            finally:
                if window:window.close()
                host.close()


    def test_megaprompt_menu_copies_live_templates_and_checks_settings(self):
        with TemporaryDirectory() as temp:
            root=Path(temp); repo=root/'repo'; _record(repo,'DEMO-011')
            sources=Path(__file__).resolve().parents[2]
            names=['BUSINESS_OPPORTUNITY_RESEARCH_MEGAPROMPT.md','BUSINESS_IDEA_TO_PROJECT_MEGAPROMPT.md',
                   'PHASE_1_RECHECK_REPLACE_MEGAPROMPT.md']
            for name in names:
                (repo/name).write_bytes((sources/name).read_bytes())
            host=ManagerHost(repo,root/'state'); window=None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window=WorkspaceWindow(host,host.workspace('f'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda:None,on_close=lambda _:None)
                self.assertEqual([a.text() for a in window.copy_prompt.menu().actions()],
                                 ['Phase 1 · Research, Create & Recheck','Phase 2 · Build, Test & Prepare',
                                  'Phase 3 · Launch & Market'])
                self.assertEqual([a.text() for a in window.copy_prompt.menu().actions()[0].menu().actions()],
                                 ['Research a Business Opportunity','Create a Project from My Idea',
                                  'Recheck or Replace Current Project'])
                window.research_budget.setText('50.25')
                window._copy_megaprompt('idea')
                original=(repo/names[1]).read_text(encoding='utf-8')
                expected=original.replace('**BUDGET_CEILING_CAD:** 100','**BUDGET_CEILING_CAD:** 50.25',1)
                self.assertTrue(self.app.clipboard().text().replace('\r\n','\n').startswith(expected.rstrip()))
                self.assertIn('project.md', self.app.clipboard().text())
                self.assertIn('Never create an active project simply to satisfy Phase 1.', self.app.clipboard().text())
                self.assertIn('For NO_GO, RESEARCH_BLOCKED, or CONDITIONAL_PROOF_ONLY', self.app.clipboard().text())
                self.assertTrue(window.select('business_portfolio/niches/demo'))
                window._copy_megaprompt('research')
                original=(repo/names[0]).read_text(encoding='utf-8')
                expected=original.replace('**BUSINESS_NICHE:** Game Development Marketplaces','**BUSINESS_NICHE:** Demo',1).replace('**BUDGET_CEILING_CAD:** 100','**BUDGET_CEILING_CAD:** 50.25',1)
                self.assertTrue(self.app.clipboard().text().replace('\r\n','\n').startswith(expected.rstrip()))
                self.assertIn('project.md', self.app.clipboard().text())
                self.assertIn('Never create an active project simply to satisfy Phase 1.', self.app.clipboard().text())
                self.assertIn('For NO_GO, RESEARCH_BLOCKED, or CONDITIONAL_PROOF_ONLY', self.app.clipboard().text())
                window._copy_megaprompt('recheck')
                expected_recheck=(repo/names[2]).read_text(encoding='utf-8')
                expected_recheck=expected_recheck.replace('**BUDGET_CEILING_CAD:** 100',
                                                         '**BUDGET_CEILING_CAD:** 50.25',1)
                expected_recheck=expected_recheck.replace('**INITIAL_CONTEXT_HINT:** AUTO',
                                                         '**INITIAL_CONTEXT_HINT:** business_portfolio/niches/demo',1)
                self.assertTrue(self.app.clipboard().text().replace('\\r\\n','\\n').startswith(expected_recheck.rstrip()))
                self.assertIn('For NO_GO, RESEARCH_BLOCKED, or CONDITIONAL_PROOF_ONLY',self.app.clipboard().text())
                self.assertIn('the NEXT paste must naturally target the NEW candidate',self.app.clipboard().text())
                self.assertEqual(window.notice.text(),'Phase 1 recheck/replace prompt copied (CAD 50.25 planning ceiling).')
                project_file=_record(repo,'DEMO-022')
                self.assertTrue(window.select(project_file.relative_to(repo).as_posix()))
                window._copy_megaprompt('recheck')
                self.assertIn('**INITIAL_CONTEXT_HINT:** '+project_file.relative_to(repo).as_posix(),
                              self.app.clipboard().text())
                self.assertIn('It must never pin future repetitions',self.app.clipboard().text())
                (repo/names[1]).write_text((repo/names[1]).read_text(encoding='utf-8')+'\nUpdated source.\n',encoding='utf-8')
                window._copy_megaprompt('idea')
                self.assertIn('Updated source.\n', self.app.clipboard().text().replace('\r\n','\n'))
                prior=self.app.clipboard().text()
                window.research_budget.setText('-1');window._copy_megaprompt('idea')
                self.assertEqual(self.app.clipboard().text(),prior)
                window.research_budget.setText('50');(repo/names[1]).write_text('malformed',encoding='utf-8')
                window._copy_megaprompt('idea');self.assertEqual(self.app.clipboard().text(),prior)
                (repo/names[1]).unlink();window._copy_megaprompt('idea')
                self.assertEqual(self.app.clipboard().text(),prior)
                self.assertEqual(len(list((repo/'business_portfolio/niches').rglob('projects/*.md'))),2)
            finally:
                if window:window.close()
                host.close()

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
                window.sync()
                receipt=set_phase(repo,relative,'complete',description='Fictional completed project',
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
                set_phase(repo, selection, 'complete', description='Verified fixture',
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
