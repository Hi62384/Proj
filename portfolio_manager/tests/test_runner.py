"""Exercise real isolated staging and durable dispatch with fictional Codex turns."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
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

    @unittest.skipUnless(os.name == 'nt', 'WSL sessions require Windows')
    def test_cancelled_wait_skips_wsl_cleanup_but_partial_staging_cleans_up(self):
        workspace = IsolatedWorkspace(self.repo, self.private, self.claim, self.cancelled)
        executor = OfficialExecutor(runtime_base=self.repo.parent)
        from pathlib import PurePosixPath
        old_home = PurePosixPath('/home/example/.local/share/codex-relay/codex-home')
        old_binary = old_home.parent / 'runtime' / 'version' / 'codex'
        with patch.object(runner_wsl, '_owner_config', return_value=('Ubuntu', old_home, old_binary)):
            with patch.object(runner_wsl, 'prepare', side_effect=runner_wsl.StagingCancelledBeforeStart('stopped')):
                with patch.object(runner_wsl, 'remove_login') as cleanup:
                    with self.assertRaises(runner_wsl.StagingCancelledBeforeStart):
                        with executor.session(workspace, self.cancelled):
                            self.fail('Cancelled staging cannot start a session')
                    cleanup.assert_not_called()
            with patch.object(runner_wsl, 'prepare', side_effect=RuntimeError('partial staging')):
                with patch.object(runner_wsl, 'remove_login') as cleanup:
                    with self.assertRaisesRegex(RuntimeError, 'partial staging'):
                        with executor.session(workspace, self.cancelled):
                            self.fail('Failed staging cannot start a session')
                    cleanup.assert_called_once()

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

    def test_wsl_staging_serializes_and_waiting_worker_can_stop(self):
        entered = threading.Event()
        release = threading.Event()
        cancelled = threading.Event()
        calls = []
        errors = []

        def stage(*args, **kwargs):
            calls.append(threading.current_thread().name)
            if len(calls) == 1:
                entered.set()
                if not release.wait(5):
                    raise RuntimeError('Staging test timed out.')

        def prepare(cancel=None):
            try:
                runner_wsl.prepare(None, {}, cancelled=cancel)
            except Exception as error:
                errors.append(error)

        with patch.object(runner_wsl, 'python', side_effect=stage):
            first = threading.Thread(target=prepare, name='first')
            waiting = threading.Thread(target=prepare, args=(cancelled,), name='waiting')
            first.start()
            self.assertTrue(entered.wait(5))
            waiting.start()
            cancelled.set()
            waiting.join(3)
            self.assertFalse(waiting.is_alive())
            self.assertEqual(calls, ['first'])
            self.assertEqual(len(errors), 1)
            self.assertIsInstance(errors[0], InterruptedError)
            release.set()
            first.join(5)
            self.assertFalse(first.is_alive())
            runner_wsl.prepare(None, {})
            self.assertEqual(len(calls), 2)

    @unittest.skipUnless(os.name == 'nt' and os.environ.get('PORTFOLIO_TEST_SANDBOX'),
                         'requires the provisioned WSL runtime')
    def test_wsl_staging_reuses_only_matching_compatibility_metadata(self):
        script = r'''
import json, os, pathlib, subprocess, sys, tempfile
source = json.load(sys.stdin)['script']
with tempfile.TemporaryDirectory(prefix='portfolio-stage-fixture-') as temp:
 home = pathlib.Path(temp).resolve() / 'home'
 source_home = home / '.local/share/codex-relay/codex-home'
 source_home.mkdir(parents=True)
 binary = home / '.local/share/codex-relay/runtime/version/codex'
 binary.parent.mkdir(parents=True)
 binary.write_text('fictional executable')
 binary.chmod(0o700)
 host = binary.with_name('codex-code-mode-host')
 host.write_text('fictional companion')
 host.chmod(0o700)
 (source_home / 'auth.json').write_text(json.dumps({'auth_mode':'chatgpt','tokens':{'fixture':'not-real'}}))
 protocol = source_home / 'protocol'
 protocol.mkdir()
 cache = protocol / 'verified.json'
 fingerprint = str(binary.stat().st_size) + ':' + str(binary.stat().st_mtime_ns)
 env = dict(os.environ, HOME=str(home))
 results = []
 for index, stored in enumerate((fingerprint, 'stale')):
  cache.write_text(json.dumps({'version':'codex-cli 0.162.1','fingerprint':stored,'contract':2,'compatible':True,'extra':'discard'}))
  run = home / '.local/share/portfolio-manager-runs' / str(index)
  target_home = run / 'codex-home'
  target_binary = run / 'runtime/codex'
  payload = {'source_home':str(source_home),'source_binary':str(binary),'target_home':str(target_home),'target_binary':str(target_binary)}
  subprocess.run([sys.executable,'-I','-c',source],input=json.dumps(payload),text=True,env=env,check=True,capture_output=True)
  target_cache = target_home / 'protocol/verified.json'
  results.append({'host':target_binary.with_name('codex-code-mode-host').is_file(),
                  'cache':json.loads(target_cache.read_text()) if target_cache.exists() else None})
 print(json.dumps(results))
'''
        result = subprocess.run(
            ['wsl.exe', '-d', os.environ['PORTFOLIO_TEST_SANDBOX'], '--exec', '/usr/bin/python3', '-I', '-c', script],
            input=json.dumps({'script': runner_wsl._PREPARE}), text=True, capture_output=True, timeout=60, check=True,
        )
        matching, stale = json.loads(result.stdout)
        self.assertTrue(matching['host'])
        self.assertTrue(stale['host'])
        self.assertEqual(set(matching['cache']), {'version', 'fingerprint', 'contract', 'compatible'})
        self.assertIsNone(stale['cache'])


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

    def test_worker_exits_after_coordinator_pauses_it_and_can_restart(self):
        worker = self.coordinator.register('demo', kind='background')
        supervisor = self._supervisor(FictionalTurns({}))
        supervisor.start(worker['id'])
        _wait(lambda: supervisor.status().get(worker['id'], {}).get('state') == 'idle')
        self.coordinator.set_worker_state(worker['id'], 'paused')
        _wait(lambda: not supervisor._running[worker['id']][0].is_alive())
        self.assertEqual(supervisor.status()[worker['id']]['state'], 'paused')
        supervisor.start(worker['id'])
        _wait(lambda: supervisor.status().get(worker['id'], {}).get('state') == 'idle')
        self.assertEqual(self.coordinator.worker(worker['id'])['state'], 'running')

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

    def test_fresh_host_process_reconciles_interrupted_background_without_revoking_chat(self):
        state = self.repo / 'disposable-host-state'
        self.coordinator = Coordinator(self.repo, state / 'portfolio-manager' / 'coordinator.sqlite3')
        background = self.coordinator.register('demo', kind='background')
        manual = self.coordinator.register('demo', kind='manual')
        interrupted = self.coordinator.claim(background['id'], project_id='FAKE-001')
        independent = self.coordinator.claim(manual['id'], project_id='FAKE-002')
        self.assertIsNotNone(interrupted)
        self.assertIsNotNone(independent)
        script = ('import sys; from portfolio_manager.integration import ManagerHost; '
                  'host=ManagerHost(sys.argv[1],sys.argv[2]); host.supervisor.close()')
        subprocess.run([sys.executable, '-c', script, str(self.repo), str(state)],
                       check=True, capture_output=True, timeout=20)
        self.assertFalse(self.coordinator.heartbeat(background['id'], interrupted['lease_token']))
        self.assertTrue(self.coordinator.heartbeat(manual['id'], independent['lease_token']))
        snapshot = self.coordinator.snapshot()
        projects = {item['id']: item for item in snapshot['projects']}
        workers = {item['id']: item for item in snapshot['workers']}
        self.assertEqual(projects['FAKE-001']['milestones'][0]['status'], 'reconcile')
        self.assertEqual(workers[background['id']]['state'], 'paused')
        self.assertEqual(workers[manual['id']]['status'], 'working')

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

    def test_start_cannot_race_between_stop_signal_and_global_stop(self):
        worker = self.coordinator.register('demo', kind='background')
        self.coordinator.set_worker_state(worker['id'], 'paused')
        supervisor = self._supervisor(FictionalTurns({}))
        signalled = threading.Event()
        release = threading.Event()
        start_done = threading.Event()
        original_signal = supervisor._signal
        errors = []

        def slow_signal(worker_id=None):
            original_signal(worker_id)
            signalled.set()
            if not release.wait(5):
                raise RuntimeError('Test did not release Stop.')

        def start_worker():
            try:
                supervisor.start(worker['id'])
            except Exception as error:
                errors.append(error)
            finally:
                start_done.set()

        with patch.object(supervisor, '_signal', side_effect=slow_signal):
            stopping = threading.Thread(target=supervisor.stop_all)
            starting = threading.Thread(target=start_worker)
            stopping.start()
            try:
                self.assertTrue(signalled.wait(5))
                starting.start()
                self.assertFalse(start_done.wait(.1))
            finally:
                release.set()
                stopping.join(5)
                if starting.ident is not None:
                    starting.join(5)
        self.assertTrue(start_done.is_set())
        self.assertEqual(len(errors), 1)
        self.assertIn('Resume Portfolio Manager', str(errors[0]))
        self.assertTrue(self.coordinator.control()['stopped'])


if __name__ == '__main__':
    unittest.main()
