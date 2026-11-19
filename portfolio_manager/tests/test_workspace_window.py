"""The normal workspace view has only chat context and shared availability."""
import os
import json
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
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QMessageBox
except ModuleNotFoundError:
    QApplication = None
    Qt = None
else:
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
        self.assertEqual([row[2] for row in roots],
                         [len(list((repo/row[0]).rglob('projects/*.md'))) for row in roots])
        entries = dict(project_entries(repo))
        self.assertTrue(all(entries.get(row[0]) for row in rows))

    def test_copy_work_prompt_button_copies_complete_goal(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';_record(repo,'DEMO-012')
            host=ManagerHost(repo,root/'state');window=None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow, WORK_PROMPT
                window=WorkspaceWindow(host,host.workspace('a'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda:None,on_close=lambda _:None)
                self.app.clipboard().setText('previous')
                window.copy_work_prompt.click()
                self.assertEqual(self.app.clipboard().text(), WORK_PROMPT)
                self.assertTrue(WORK_PROMPT.startswith('/goal Complete the project currently selected'))
                self.assertIn('Mark the goal complete only when', WORK_PROMPT)
                self.assertEqual(window.notice.text(), 'Work prompt copied to the clipboard.')
                self.assertEqual(host.get_workspace(window.workspace_id)['selection'], 'business_portfolio/niches')
            finally:
                if window:window.close()
                host.close()

    def test_project_actions_mark_complete_and_offer_recoverable_delete(self):
        with TemporaryDirectory() as temp:
            root=Path(temp); repo=root/'repo'; record=_record(repo,'DEMO-013')
            tools=repo/'business_portfolio/tools';tools.mkdir(parents=True)
            source=Path(__file__).resolve().parents[2]/'business_portfolio/tools/browser_template.html'
            (tools/'browser_template.html').write_bytes(source.read_bytes())
            host=ManagerHost(repo,root/'state');window=None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window=WorkspaceWindow(host,host.workspace('a'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda:None,on_close=lambda _:None)
                self.assertTrue(window.select(record.relative_to(repo).as_posix()))
                window.complete_project_button.click()
                self.assertIn('"work_state": "completed"',record.read_text(encoding='utf-8'))
                self.assertTrue(window.complete_project_button.isEnabled())
                self.assertEqual(window.complete_project_button.text(), 'Mark Not Complete')
                window.complete_project_button.click()
                self.assertIn('"work_state": "planned"',record.read_text(encoding='utf-8'))
                self.assertEqual(window.complete_project_button.text(), 'Mark Complete')
                with patch('portfolio_manager.workspace_window.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
                    window.delete_project_button.click()
                self.assertFalse(record.exists())
                self.assertEqual(len(list((repo/'business_portfolio/.local/project-trash').glob('*.md'))),1)
            finally:
                if window:window.close()
                host.close()

    def test_project_with_windows_crcrlf_shows_project_actions(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';record=_record(repo,'DEMO-014')
            raw=record.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\r\n')
            record.write_bytes(raw)
            host=ManagerHost(repo,root/'state');window=None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window=WorkspaceWindow(host,host.workspace('a'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda:None,on_close=lambda _:None)
                self.assertTrue(window.select(record.relative_to(repo).as_posix()))
                self.assertFalse(window.project_actions.isHidden())
                self.assertFalse(window.project_tabs.isHidden())
            finally:
                if window:window.close()
                host.close()

    def test_megaprompt_menu_copies_live_templates_and_checks_settings(self):
        with TemporaryDirectory() as temp:
            root=Path(temp); repo=root/'repo'; _record(repo,'DEMO-011')
            sources=Path(__file__).resolve().parents[2]
            names=['BUSINESS_OPPORTUNITY_RESEARCH_MEGAPROMPT.md','BUSINESS_IDEA_TO_PROJECT_MEGAPROMPT.md']
            for name in names:
                (repo/name).write_bytes((sources/name).read_bytes())
            host=ManagerHost(repo,root/'state'); window=None
            try:
                from portfolio_manager.workspace_window import WorkspaceWindow
                window=WorkspaceWindow(host,host.workspace('f'*32,{}),on_emergency=lambda:None,
                                       on_stop_all=lambda:None,on_access=lambda:None,on_close=lambda _:None)
                self.assertEqual([a.text() for a in window.copy_research_prompt.menu().actions()],
                                 ['Research a Business Opportunity','Develop My Business Idea'])
                window.research_budget.setText('50.25')
                window._copy_megaprompt('idea')
                original=(repo/names[1]).read_text(encoding='utf-8')
                expected=original.replace('**BUDGET_CEILING_CAD:** 100','**BUDGET_CEILING_CAD:** 50.25',1)
                self.assertEqual(self.app.clipboard().text().replace('\r\n','\n'),expected)
                self.assertTrue(window.select('business_portfolio/niches/demo'))
                window._copy_megaprompt('research')
                original=(repo/names[0]).read_text(encoding='utf-8')
                expected=original.replace('**BUSINESS_NICHE:** Game Development Marketplaces','**BUSINESS_NICHE:** Demo',1).replace('**BUDGET_CEILING_CAD:** 100','**BUDGET_CEILING_CAD:** 50.25',1)
                self.assertEqual(self.app.clipboard().text().replace('\r\n','\n'),expected)
                (repo/names[1]).write_text((repo/names[1]).read_text(encoding='utf-8')+'\nUpdated source.\n',encoding='utf-8')
                window._copy_megaprompt('idea')
                self.assertTrue(self.app.clipboard().text().replace('\r\n','\n').endswith('Updated source.\n'))
                prior=self.app.clipboard().text()
                window.research_budget.setText('-1');window._copy_megaprompt('idea')
                self.assertEqual(self.app.clipboard().text(),prior)
                window.research_budget.setText('50');(repo/names[1]).write_text('malformed',encoding='utf-8')
                window._copy_megaprompt('idea');self.assertEqual(self.app.clipboard().text(),prior)
                (repo/names[1]).unlink();window._copy_megaprompt('idea')
                self.assertEqual(self.app.clipboard().text(),prior)
                self.assertEqual(len(list((repo/'business_portfolio/niches').rglob('projects/*.md'))),1)
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
