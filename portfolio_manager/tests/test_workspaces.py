"""Exercise persisted selections and proof-based reconnects with disposable files."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from portfolio_manager.coordinator import Coordinator
from portfolio_manager.workspace import ChatWorkspaces, context_path
from portfolio_manager.integration import ManagerHost
from portfolio_manager.tests.test_runner import _record
from portfolio_manager.codex_session_hook import ROOT, workspace_context
from unittest.mock import Mock
from types import SimpleNamespace


class WorkspaceTests(unittest.TestCase):
    def test_session_hook_reserves_without_opening_a_window(self):
        client = Mock()
        client.request.return_value = {'reconnect_key': 'a' * 64}
        for source in ('startup', 'resume', 'clear', 'compact', 'fork'):
            event = {'hook_event_name': 'SessionStart', 'session_id': 'session_1',
                     'cwd': str(ROOT), 'source': source}
            result = workspace_context(event, client)
            self.assertIn('a' * 64, result['hookSpecificOutput']['additionalContext'])
            client.request.assert_called_with('bridge_bind_codex_session',
                                              {'session_id': 'session_1', 'show': False})

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.record = _record(self.root, 'FAKE-001')
        self.source = self.root / 'example.py'
        self.source.write_text('answer = 42\n', encoding='utf-8')
        self.coordinator = Coordinator(self.root)
        self.store = ChatWorkspaces(self.coordinator)

    def test_two_connections_keep_distinct_selections_and_reconnect(self):
        a = self.store.attach('a' * 32)
        b = self.store.attach('b' * 32)
        self.assertNotEqual(a['id'], b['id'])
        chosen = self.store.select(a['id'], self.source, a['revision'], client='a' * 32)
        self.assertEqual(chosen['selection'], 'example.py')
        self.assertEqual(self.store.get(b['id'])['selection'], b['selection'])
        self.assertEqual(self.store.attach('a' * 32)['id'], a['id'])
        self.assertNotIn('reconnect_key', self.store.get(a['id']))
        restarted = ChatWorkspaces(Coordinator(self.root))
        result = restarted.attach('c' * 32, a['reconnect_key'])
        self.assertEqual(result, chosen)
        with self.assertRaisesRegex(PermissionError, 'disconnected'):
            restarted.attach('a' * 32)
        with self.assertRaises(PermissionError):
            restarted.select(a['id'], self.record, client='a' * 32)
        with self.assertRaises(PermissionError):
            restarted.attach('b' * 32, a['reconnect_key'])

    def test_stale_edit_and_out_of_scope_paths_are_rejected(self):
        row = self.store.attach('a' * 32)
        self.store.select(row['id'], self.source, 0)
        with self.assertRaisesRegex(ValueError, 'selection changed'):
            self.store.select(row['id'], self.record, 0)
        for path in ('../outside.py', '.git/config', 'outputs/paid.zip', 'auth.json',
                     'business_portfolio/../example.py'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                context_path(self.root, path)

    def test_selected_portfolio_folder_includes_live_project_summary(self):
        second = _record(self.root, 'FAKE-002')
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        workspace = host.workspace('d' * 32, {'path': 'business_portfolio/niches/demo'})
        context = host.context_info(workspace)
        self.assertEqual(context['kind'], 'folder')
        self.assertEqual(context['portfolio']['counts']['total'], 2)
        projects = context['portfolio']['projects']
        self.assertEqual({row['id'] for row in projects}, {'FAKE-001', 'FAKE-002'})
        self.assertEqual(next(row for row in projects if row['id'] == 'FAKE-002')['record_path'],
                         second.relative_to(self.root).as_posix())
        self.assertFalse(context['portfolio']['truncated'])
        ordinary = host.workspace('e' * 32, {'path': self.source.as_posix()})
        self.assertNotIn('portfolio', host.context_info(ordinary))

    def test_chat_can_claim_only_the_project_it_selected(self):
        _record(self.root, 'FAKE-002')
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        first = host.call('portfolio_register', {'folder': 'business_portfolio/niches/demo'})
        second = host.call('portfolio_register', {'folder': 'business_portfolio/niches/demo'})
        first_args = {'worker_id': first['id'], 'worker_key': first['worker_key'], 'project_id': 'FAKE-001'}
        second_args = {'worker_id': second['id'], 'worker_key': second['worker_key'], 'project_id': 'FAKE-001'}
        self.assertEqual(host.call('portfolio_claim', first_args)['project_id'], 'FAKE-001')
        self.assertIsNone(host.call('portfolio_claim', second_args))
        second_args['project_id'] = 'FAKE-002'
        self.assertEqual(host.call('portfolio_claim', second_args)['project_id'], 'FAKE-002')

    def test_selected_project_starts_a_persistently_targeted_worker(self):
        _record(self.root, 'FAKE-002')
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        workspace = host.workspace('b' * 32, {'path': self.record.as_posix()})
        with patch.object(host.supervisor, 'start'):
            worker = host.start_workspace_worker(workspace['id'])
        self.assertEqual(host.get_workspace(workspace['id'])['worker_id'], worker['id'])
        competing = host.coordinator.register('demo', kind='background', project_id='FAKE-001')
        # A second coordinator represents recovery after a controller restart.
        recovered = Coordinator(self.root, host.coordinator.db_path)
        claim = recovered.claim(worker['id'])
        self.assertEqual(claim['project_id'], 'FAKE-001')
        self.assertIsNone(recovered.claim(competing['id']))
        recovered.finish(worker['id'], claim['lease_token'], outcome='blocked', summary='Needs review')
        self.assertIsNone(recovered.claim(worker['id']))
        with self.assertRaisesRegex(ValueError, 'another project'):
            recovered.claim(worker['id'], project_id='FAKE-002')

    def test_failed_workspace_assignment_stops_the_started_worker(self):
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        workspace = host.workspace('c' * 32, {'path': self.record.as_posix()})
        with patch.object(host.supervisor, 'start'), patch.object(
                host.workspaces, 'assign', side_effect=RuntimeError('assignment failed')):
            with self.assertRaisesRegex(RuntimeError, 'assignment failed'):
                host.start_workspace_worker(workspace['id'])
        workers = host.coordinator.snapshot()['workers']
        self.assertEqual(len(workers), 1)
        self.assertEqual(workers[0]['state'], 'stopped')
        self.assertIsNone(host.get_workspace(workspace['id'])['worker_id'])

    def test_selected_project_development_binds_only_its_next_task(self):
        _record(self.root, 'FAKE-002')
        (self.root / 'source').mkdir()
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        workspace = host.workspace('c' * 32, {'path': self.record.as_posix()})
        args = dict(expected_selection=workspace['selection'], expected_revision=workspace['revision'])
        with patch('portfolio_manager.development.DevelopmentScope.discover',
                   return_value=SimpleNamespace(folder='source')), patch.object(host.supervisor, 'start'):
            worker = host.prepare_selected_development(workspace['id'], 'source', **args)
        claim = host.coordinator.claim(worker['id'])
        self.assertEqual(claim['project_id'], 'FAKE-001')
        self.assertEqual(claim['task']['verification'], {'kind': 'development', 'folder': 'source'})
        self.assertEqual(host.get_workspace(workspace['id'])['worker_id'], worker['id'])

    def test_development_setup_rejects_changed_selection_and_existing_claim(self):
        (self.root / 'source').mkdir()
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        workspace = host.workspace('c' * 32, {'path': self.record.as_posix()})
        args = dict(expected_selection=workspace['selection'], expected_revision=workspace['revision'])
        host.select(workspace['id'], self.source)
        with self.assertRaisesRegex(ValueError, 'selection changed'):
            host.prepare_selected_development(workspace['id'], 'source', **args)
        workspace = host.select(workspace['id'], self.record)
        args = dict(expected_selection=workspace['selection'], expected_revision=workspace['revision'])
        competing = host.coordinator.register('demo', kind='manual')
        host.coordinator.claim(competing['id'], project_id='FAKE-001')
        with patch('portfolio_manager.development.DevelopmentScope.discover',
                   return_value=SimpleNamespace(folder='source')):
            with self.assertRaisesRegex(ValueError, 'already being worked on'):
                host.prepare_selected_development(workspace['id'], 'source', **args)
        self.assertIsNone(host.get_workspace(workspace['id'])['worker_id'])

    def test_development_setup_releases_claim_on_scope_failure(self):
        (self.root / 'source').mkdir()
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        workspace = host.workspace('c' * 32, {'path': self.record.as_posix()})
        args = dict(expected_selection=workspace['selection'], expected_revision=workspace['revision'])
        with patch('portfolio_manager.development.DevelopmentScope.discover',
                   return_value=SimpleNamespace(folder='source')), patch.object(
                       host.coordinator, 'set_development_scope', side_effect=ValueError('scope changed')):
            with self.assertRaisesRegex(ValueError, 'scope changed'):
                host.prepare_selected_development(workspace['id'], 'source', **args)
        worker = host.coordinator.register('demo', kind='manual')
        claim = host.coordinator.claim(worker['id'], project_id='FAKE-001')
        self.assertEqual(claim['project_id'], 'FAKE-001')
        self.assertIsNone(host.get_workspace(workspace['id'])['worker_id'])

    def test_selected_project_includes_bounded_work_and_ownership_context(self):
        host = ManagerHost(self.root, self.root / 'state')
        self.addCleanup(host.close)
        host.coordinator.configure_plan('FAKE-001', [{
            'id': 'first', 'title': 'Prepare the project',
            'criteria': 'Create the requested result and verify it.', 'weight': 1,
        }])
        workspace = host.workspace('f' * 32, {'path': self.record.as_posix()})
        project = host.context_info(workspace)['project']
        self.assertEqual(project['record_path'], self.record.relative_to(self.root).as_posix())
        self.assertEqual(len(project['content_sha256']), 64)
        self.assertIsNone(project['worker_id'])
        self.assertIsNone(project['current_task'])
        self.assertEqual(project['milestones'][0]['id'], 'first')
        self.assertEqual(project['milestones'][0]['criteria'], 'Create the requested result and verify it.')
        self.assertFalse(project['milestones'][0]['verified'])
        self.assertFalse(project['milestones_truncated'])

    def test_active_connection_cannot_be_displaced_by_another_connection(self):
        row = self.store.attach('a' * 32)
        self.store.select(row['id'], self.source, client='a' * 32)
        with self.assertRaisesRegex(PermissionError, 'already connected'):
            self.store.attach('b' * 32, row['reconnect_key'], active_clients={'a' * 32, 'b' * 32})
        self.assertEqual(self.store.attach('a' * 32)['selection'], 'example.py')
        restored = self.store.attach('b' * 32, row['reconnect_key'], active_clients={'b' * 32})
        self.assertEqual(restored['id'], row['id'])
        with self.assertRaises(PermissionError):
            self.store.attach('a' * 32)

    def test_codex_hook_binding_survives_restarts_and_rejects_other_bindings(self):
        first = self.store.reserve_codex_session('thr_one')
        second = self.store.reserve_codex_session('thr_two')
        self.assertNotEqual(first['id'], second['id'])
        self.assertNotEqual(first['reconnect_key'], second['reconnect_key'])
        self.store.attach('a' * 32, first['reconnect_key'])
        self.store.select(first['id'], self.source, client='a' * 32)

        restarted = ChatWorkspaces(Coordinator(self.root))
        recovered = restarted.reserve_codex_session('thr_one')
        self.assertEqual(recovered['reconnect_key'], first['reconnect_key'])
        self.assertEqual(recovered['selection'], 'example.py')
        self.assertEqual(restarted.attach('b' * 32, recovered['reconnect_key'])['id'], first['id'])
        with self.assertRaises(PermissionError):
            restarted.attach('b' * 32, second['reconnect_key'])
        with self.assertRaises(ValueError):
            restarted.reserve_codex_session('../invalid')
