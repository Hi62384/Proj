"""Exercise real isolated staging and durable dispatch with fictional Codex turns."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from portfolio_manager.coordinator import Coordinator
from portfolio_manager.runner import IsolatedWorkspace, OfficialExecutor, Supervisor, VerificationRequired
from portfolio_manager import runner_wsl
from portfolio_autopilot.codex_relay.diagnostics import RelayError


def _record(repo, project, *, priority='P1', public_results=()):
    niche = repo / 'business_portfolio' / 'niches' / 'demo'
    (niche / 'projects').mkdir(parents=True, exist_ok=True)
    (niche / 'NICHE.json').write_text(json.dumps({'id': 'N-demo', 'path': 'demo', 'title': 'Demo', 'parent': None}), encoding='utf-8')
    research = repo / 'business_portfolio' / 'research'
    research.mkdir(exist_ok=True)
    (research / 'SOURCE_REGISTER.json').write_text(json.dumps([
        {'id': 'S-001', 'title': 'Fictional source', 'url': 'https://example.invalid/source'}]), encoding='utf-8')
    metadata = dict(id=project, title='Fictional ' + project, schema_version=1, niche_path='demo',
                    niche_id='N-demo', record_type='standalone_service', origin='fictional',
                    priority=priority, work_state='planned', commercial_validation='unvalidated',
                    evidence_basis='unknown', source_ids=['S-001'], parent_project=None,
                    related_projects=[], next_action='Prepare a local handoff for ' + project,
                    execution_authorized=False, privacy='public', last_reviewed='2026-11-11',
                    public_results=list(public_results))
    path = niche / 'projects' / (project.lower() + '.md')
    path.write_text('---\n' + json.dumps(metadata, indent=2) + '\n---\n\nFictional work only.\n', encoding='utf-8')
    return path


def _call(workspace, operation, path='', content='', sha=''):
    return workspace.call({'operation': operation, 'path': path, 'content': content, 'sha256': sha})


def _wait(predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(.025)
    raise AssertionError('Expected worker state was not observed before the deadline.')


class FictionalTurns:
    def __init__(self, actions):
        self.actions = actions
        self.claimed = []

    def run(self, claim, workspace, cancelled, emit, save_session):
        project = claim['project_id']
        self.claimed.append((project, claim['task_id']))
        save_session('fixture-' + project)
        self.assert_record_contains_project(workspace, project)
        action = self.actions.get(project, 'draft')
        if action == 'wait' and not claim.get('human_responses'):
            return {'kind': 'owner', 'summary': 'The fixture needs a review.',
                    'question': 'Confirm the fictional input exists.', 'tests': []}
        if action == 'stall':
            if not cancelled.wait(4):
                raise AssertionError('Cancellation was not delivered to the fake executor.')
            raise InterruptedError('Stopped by test')
        if action != 'no-evidence':
            _call(workspace, 'write', 'result.md', '# Fictional local result\n' + project, 'new')
        return {'kind': 'result', 'summary': 'Prepared a fictional local draft.', 'question': '', 'tests': []}

    @staticmethod
    def assert_record_contains_project(workspace, project):
        if project not in _call(workspace, 'read', 'PROJECT.md')['content']:
            raise AssertionError('A worker received a different project record.')


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name) / 'repo'
        self.private = self.repo / 'business_portfolio' / '.local' / 'portfolio-manager'
        self.private.mkdir(parents=True)
        self.record = _record(self.repo, 'FAKE-001', public_results=[
            {'path': 'results/FAKE-001/source.md', 'label': 'Same-project input'}])
        result = self.repo / 'business_portfolio' / 'results' / 'FAKE-001' / 'source.md'
        result.parent.mkdir(parents=True)
        result.write_text('Fictional prior result', encoding='utf-8')
        self.claim = {'record_path': self.record.relative_to(self.repo).as_posix(), 'project_id': 'FAKE-001',
                      'record_sha256': hashlib.sha256(self.record.read_bytes()).hexdigest()}
        self.cancelled = threading.Event()

    def test_only_staged_outputs_can_change(self):
        workspace = IsolatedWorkspace(self.repo, self.private, self.claim, self.cancelled)
        approved = _call(workspace, 'list')['paths']
        self.assertIn('results/FAKE-001/source.md', approved)
        self.assertNotIn('results/FAKE-002/source.md', approved)
        for candidate in ('PROJECT.md', 'results/FAKE-001/source.md', '../outside.md', '.git/config'):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                _call(workspace, 'write', candidate, 'Blocked', 'new')
        with self.assertRaises(ValueError):
            _call(workspace, 'read', 'results/FAKE-002/source.md')
        with self.assertRaises(ValueError):
            _call(workspace, 'write', 'result.md', 'draft', 'wrong-hash')
        with self.assertRaises(VerificationRequired):
            workspace.evidence('result.md')
        _call(workspace, 'write', 'result.md', 'A saved fictional result', 'new')
        evidence = workspace.evidence('result.md')
        self.assertTrue(Path(evidence['path']).is_relative_to(self.private))
        self.assertEqual(evidence['sha256'], hashlib.sha256(b'A saved fictional result').hexdigest())
        self.assertEqual(hashlib.sha256(self.record.read_bytes()).hexdigest(), self.claim['record_sha256'])
        self.cancelled.set()
        with self.assertRaises(ValueError):
            _call(workspace, 'read', 'PROJECT.md')

    def test_stale_record_and_invalid_draft_are_rejected(self):
        workspace = IsolatedWorkspace(self.repo, self.private, self.claim, self.cancelled)
        _call(workspace, 'write', 'draft.json', 'invalid JSON', 'new')
        with self.assertRaises(VerificationRequired):
            workspace.evidence('draft.json')
        self.record.write_text('A concurrent edit', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'changed after the claim'):
            IsolatedWorkspace(self.repo, self.private, self.claim, self.cancelled)

    def test_executor_runtime_stays_outside_checkout(self):
        workspace = IsolatedWorkspace(self.repo, self.private, self.claim, self.cancelled)
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            OfficialExecutor(runtime_base=self.repo)._config(workspace)
        config = OfficialExecutor(runtime_base=self.repo.parent)._config(workspace).validate()
        self.assertFalse(config.data_dir.is_relative_to(self.repo))
        self.assertEqual(config.workspace, workspace.root)

    def test_prior_artifact_must_belong_to_this_project_and_match_digest(self):
        first = IsolatedWorkspace(self.repo, self.private, self.claim, self.cancelled)
        _call(first, 'write', 'result.md', 'Verified prior fictional artifact.', 'new')
        evidence = first.evidence('result.md')
        tampered = {**evidence, 'sha256': '0' * 64}
        outside = self.private / 'outside.md'
        outside.write_text('Private file unrelated to this project.', encoding='utf-8')
        other = {'path': str(outside), 'sha256': hashlib.sha256(outside.read_bytes()).hexdigest()}
        second = IsolatedWorkspace(self.repo, self.private, {
            **self.claim, 'prior_artifacts': [evidence, tampered, other]}, self.cancelled)
        self.assertEqual(_call(second, 'read', 'prior-1.md')['content'], 'Verified prior fictional artifact.')
        self.assertNotIn('prior-2.md', _call(second, 'list')['paths'])
        self.assertNotIn('prior-3.md', _call(second, 'list')['paths'])
        with self.assertRaises(ValueError):
            _call(second, 'write', 'prior-1.md', 'overwrite', 'new')

    def test_configured_wsl_sessions_get_distinct_private_homes(self):
        workspace = IsolatedWorkspace(self.repo, self.private, self.claim, self.cancelled)
        executor = OfficialExecutor(runtime_base=self.repo.parent)
        from pathlib import PurePosixPath
        old_home = PurePosixPath('/home/example/.local/share/codex-relay/codex-home')
        old_binary = old_home.parent / 'runtime' / 'version' / 'codex'
        with patch.object(runner_wsl, '_owner_config', return_value=('Ubuntu', old_home, old_binary)):
            first = executor._config(workspace)
            second = executor._config(workspace)
            before = runner_wsl.configure(first)
            after = runner_wsl.configure(second)
        self.assertEqual(before['source_home'], str(old_home))
        self.assertEqual(after['source_binary'], str(old_binary))
        self.assertNotEqual(first.wsl_home, second.wsl_home)
        self.assertNotIn(str(old_home.parent) + '/', first.wsl_home)
        self.assertEqual(first.validate().execution_backend, 'wsl')


class DispatchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        for project in ('FAKE-001', 'FAKE-002', 'FAKE-003'):
            _record(self.repo, project)
        self.coordinator = Coordinator(self.repo, lease_seconds=3)

    def _state(self):
        return {p['id']: p for p in self.coordinator.snapshot()['projects']}

    def _supervisor(self, executor, **kwargs):
        supervisor = Supervisor(self.coordinator, executor, poll_seconds=.025, **kwargs)
        self.addCleanup(supervisor.close)
        return supervisor

    def test_afk_parks_request_and_continues_after_missing_evidence(self):
        self.coordinator.set_mode('afk')
        worker = self.coordinator.register('demo', kind='background')
        executor = FictionalTurns({'FAKE-001': 'wait', 'FAKE-002': 'no-evidence'})
        supervisor = self._supervisor(executor)
        supervisor.start(worker['id'])
        _wait(lambda: supervisor.status().get(worker['id'], {}).get('state') == 'idle' and len(executor.claimed) == 3)
        snapshot = self.coordinator.snapshot()
        self.assertEqual(snapshot['mode'], 'afk')
        self.assertEqual(len(snapshot['requests']), 1)
        self.assertEqual(snapshot['requests'][0]['project_id'], 'FAKE-001')
        projects = self._state()
        self.assertEqual(projects['FAKE-002']['milestones'][0]['status'], 'blocked')
        self.assertEqual(projects['FAKE-003']['milestones'][0]['status'], 'completed')
        self.assertEqual([x[0] for x in executor.claimed], ['FAKE-001', 'FAKE-002', 'FAKE-003'])
        self.coordinator.set_mode('human')
        self.coordinator.resolve_request(snapshot['requests'][0]['id'], 'complete')
        _wait(lambda: self._state()['FAKE-001']['milestones'][0]['status'] == 'completed')
        self.assertEqual(executor.claimed[-1], ('FAKE-001', 'next-action'))

    def test_restart_restores_running_worker_without_replaying_saved_task(self):
        worker = self.coordinator.register('demo', kind='background')
        executor = FictionalTurns({})
        supervisor = self._supervisor(executor)
        supervisor.start(worker['id'])
        _wait(lambda: supervisor.status().get(worker['id'], {}).get('state') == 'idle' and len(executor.claimed) == 3)
        supervisor.close()
        self.coordinator = Coordinator(self.repo)
        _record(self.repo, 'FAKE-004')
        after_restart = FictionalTurns({})
        second = self._supervisor(after_restart)
        second.restore()
        _wait(lambda: second.status().get(worker['id'], {}).get('state') == 'idle' and bool(after_restart.claimed))
        self.assertEqual(after_restart.claimed, [('FAKE-004', 'next-action')])
        self.assertEqual(self._state()['FAKE-001']['milestones'][0]['status'], 'completed')

    def test_timeout_blocks_one_task_and_continues(self):
        worker = self.coordinator.register('demo', kind='background')
        executor = FictionalTurns({'FAKE-001': 'stall'})
        supervisor = self._supervisor(executor, turn_timeout=.3)
        supervisor.start(worker['id'])
        _wait(lambda: supervisor.status().get(worker['id'], {}).get('state') == 'idle' and len(executor.claimed) == 3)
        self.assertEqual(self._state()['FAKE-001']['milestones'][0]['status'], 'blocked')
        self.assertEqual(self._state()['FAKE-002']['milestones'][0]['status'], 'completed')

    def test_runtime_failure_pauses_worker_without_claiming_remaining_projects(self):
        class UnavailableRuntime:
            def run(self, *_):
                raise RelayError('authentication', 'account/read', 'Sign-in is unavailable.')

        worker = self.coordinator.register('demo', kind='background')
        supervisor = self._supervisor(UnavailableRuntime())
        supervisor.start(worker['id'])
        _wait(lambda: self.coordinator.snapshot()['workers'][0]['state'] == 'paused')
        projects = self._state()
        self.assertEqual(projects['FAKE-001']['milestones'][0]['status'], 'blocked')
        self.assertFalse(projects['FAKE-002']['milestones'])
        self.assertIn('Sign-in is unavailable', supervisor.status()[worker['id']]['detail'])

    def test_emergency_stop_cancels_active_turn_without_accepting_a_result(self):
        worker = self.coordinator.register('demo', kind='background')
        executor = FictionalTurns({'FAKE-001': 'stall'})
        supervisor = self._supervisor(executor)
        supervisor.start(worker['id'])
        _wait(lambda: bool(executor.claimed))
        supervisor.stop_all(emergency=True)
        _wait(lambda: supervisor.status()[worker['id']]['state'] == 'stopped')
        snapshot = self.coordinator.snapshot()
        self.assertTrue(snapshot['emergency'])
        self.assertEqual(executor.claimed, [('FAKE-001', 'next-action')])
        self.assertEqual(self._state()['FAKE-001']['milestones'][0]['status'], 'reconcile')
        self.assertFalse(list(self.coordinator.db_path.parent.glob('worker-runs/*/*/workspace/result.md')))


if __name__ == '__main__':
    unittest.main()
