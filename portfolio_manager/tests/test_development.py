import hashlib
import json
import os
import sqlite3
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, patch

from portfolio_manager.development import (BubblewrapVerifier, DevelopmentError, DevelopmentScope, _NODE_TEST_DRIVER, _PYTHON_TEST_LOADER, _test_result,
                                           DevelopmentWorkspace, candidate_review, apply_reviewed_candidate)
from portfolio_manager.runner import OfficialExecutor, Supervisor
from portfolio_manager.coordinator import Coordinator, CoordinatorError
from portfolio_manager.applied_verification import verify_applied
from portfolio_manager.tests.test_runner import _record


class DevelopmentTests(unittest.TestCase):
    def test_python_loader_supports_relative_imports_in_test_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / 'fixture_tests'
            package.mkdir()
            (package / '__init__.py').write_text('', encoding='utf-8')
            (package / 'helper.py').write_text('value = 42\n', encoding='utf-8')
            test_file = package / 'test_relative.py'
            test_file.write_text(
                'from unittest import TestCase\nfrom .helper import value\n'
                'class RelativeTests(TestCase):\n    def test_value(self):\n        self.assertEqual(value, 42)\n',
                encoding='utf-8')
            script = _PYTHON_TEST_LOADER + '''
sys.path.insert(0, sys.argv[1])
result = unittest.TextTestRunner().run(load_test_file(sys.argv[2], 0, sys.argv[1]))
if not result.wasSuccessful() or result.testsRun != 1:
    raise SystemExit(1)
'''
            subprocess.run([sys.executable, '-I', '-B', '-c', script, str(root), str(test_file)],
                           check=True, capture_output=True, timeout=10)
            subprocess.run([sys.executable, '-I', '-B', '-c', script, str(package), str(test_file)],
                           check=True, capture_output=True, timeout=10)

    def test_verifier_result_follows_long_test_output(self):
        with tempfile.TemporaryFile() as output:
            output.write(b'fixture output\n' * 1000)
            output.write(b'{"tests_run": 4}\n')
            self.assertEqual(_test_result(output), 4)

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name).resolve()
        self.repo, self.private = base / 'repo', base / 'private'
        self.private.mkdir()
        self.repo.mkdir()
        self.git('init', '-q')
        (self.repo / 'demo').mkdir()
        (self.repo / 'demo/app.py').write_text('def answer():\n    return 1\n', encoding='utf-8')
        (self.repo / 'demo/helper.py').write_text('def base():\n    return 1\n', encoding='utf-8')
        (self.repo / 'demo/test_app.py').write_text(
            'from unittest import TestCase\nfrom app import answer\n'
            'class TestAnswer(TestCase):\n    def test_answer(self):\n        self.assertEqual(answer(), 42)\n',
            encoding='utf-8')
        self.git('add', 'demo')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
        (self.repo / 'demo/local.txt').write_text('private fixture', encoding='utf-8')
        self.scope = DevelopmentScope('demo', (), ('demo/app.py', 'demo/helper.py', 'demo/extra/value.py'),
                                      ('demo/test_app.py',))
        self.cancelled = threading.Event()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.STDOUT)

    def workspace(self, scope=None):
        return DevelopmentWorkspace(self.repo, self.private, scope or self.scope, self.cancelled)

    def call(self, workspace, operation, path='', content='', sha256=''):
        return workspace.call(dict(operation=operation, path=path, content=content, sha256=sha256))

    def change(self, workspace, path, content):
        original = self.call(workspace, 'read', path)
        return self.call(workspace, 'write', path, content, original['sha256'])

    def implement(self, workspace):
        self.change(workspace, 'demo/app.py',
                    'from helper import base\nfrom extra.value import offset\ndef answer():\n    return base() + offset\n')
        self.change(workspace, 'demo/helper.py', 'def base():\n    return 40\n')
        self.change(workspace, 'demo/extra/value.py', 'offset = 2\n')

    def test_candidate_records_exact_changes_and_leaves_checkout_untouched(self):
        workspace = self.workspace()
        self.implement(workspace)
        evidence = workspace.verify(Mock(run=Mock(return_value=1)))
        checkpoint = Path(evidence['path']).read_bytes()
        self.assertEqual(evidence['sha256'], hashlib.sha256(checkpoint).hexdigest())
        report = json.loads(checkpoint)
        self.assertEqual(report['tests_run'], 1)
        self.assertEqual(report['integration'], 'pending_review')
        self.assertEqual(set(report['changed']), set(self.scope.edit_paths))
        self.assertEqual(self.git('diff', 'HEAD'), b'')
        self.assertFalse((self.repo / 'demo/extra/value.py').exists())

    def test_owner_review_applies_only_unchanged_verified_candidate(self):
        workspace = self.workspace()
        self.implement(workspace)
        evidence = workspace.verify(Mock(run=Mock(return_value=1)))
        review = candidate_review(self.repo, self.private, evidence['path'], evidence['sha256'])
        self.assertEqual({item['path'] for item in review['files']}, set(self.scope.edit_paths))
        self.assertIn('offset = 2', review['patch'])
        result = apply_reviewed_candidate(self.repo, self.private, evidence['path'], evidence['sha256'])
        self.assertEqual(set(result['files']), set(self.scope.edit_paths))
        self.assertEqual((self.repo / 'demo/extra/value.py').read_text(), 'offset = 2\n')
        with self.assertRaisesRegex(DevelopmentError, 'changed'):
            apply_reviewed_candidate(self.repo, self.private, evidence['path'], evidence['sha256'])

    def test_applied_verification_runs_tests_and_detects_source_changes(self):
        workspace = self.workspace()
        self.implement(workspace)
        evidence = workspace.verify(Mock(run=Mock(return_value=1)))
        verifier = Mock(run=Mock(return_value=2))
        with self.assertRaisesRegex(DevelopmentError, 'changed'):
            verify_applied(self.repo, self.private, evidence['path'], evidence['sha256'], verifier, self.cancelled)
        verifier.run.assert_not_called()
        apply_reviewed_candidate(self.repo, self.private, evidence['path'], evidence['sha256'])
        result = verify_applied(self.repo, self.private, evidence['path'], evidence['sha256'], verifier, self.cancelled)
        self.assertEqual(result['tests_run'], 2)
        self.assertEqual(set(result['files']), set(self.scope.edit_paths))
        def mutate(*args):
            (self.repo / 'demo/helper.py').write_text('changed during test\n', encoding='utf-8')
            return 1
        with self.assertRaisesRegex(DevelopmentError, 'changed'):
            verify_applied(self.repo, self.private, evidence['path'], evidence['sha256'], Mock(run=mutate), self.cancelled)

    def test_candidate_integration_holds_coordinator_write_lock(self):
        _record(self.repo, 'DEMO-001')
        coordinator = Coordinator(self.repo)
        evidence = {'path': 'candidate', 'sha256': 'a' * 64}

        def apply(candidate):
            self.assertEqual(candidate, evidence)
            connection = sqlite3.connect(coordinator.db_path, timeout=0.1, isolation_level=None)
            try:
                with self.assertRaisesRegex(sqlite3.OperationalError, 'locked'):
                    connection.execute('BEGIN IMMEDIATE')
            finally:
                connection.close()
            return 'applied'

        with patch.object(coordinator, '_candidate_evidence', return_value=evidence):
            self.assertEqual(coordinator.guard_candidate('DEMO-001', 'work', apply), 'applied')

    def test_candidate_verification_is_recorded_without_completing_task(self):
        _record(self.repo, 'DEMO-001')
        coordinator = Coordinator(self.repo)
        evidence = {'kind': 'passed_test', 'path': 'candidate', 'sha256': 'a' * 64}
        result = {'candidate_sha256': 'a' * 64, 'tests_run': 2, 'files': ['demo/app.py']}
        with patch.object(coordinator, '_candidate_evidence', return_value=evidence):
            self.assertEqual(coordinator.record_candidate_check('DEMO-001', 'work', lambda _: result), result)
            with coordinator._database() as db:
                event = db.execute("SELECT * FROM history WHERE kind='candidate_verified'").fetchone()
                self.assertEqual(json.loads(event['detail'])['tests_run'], 2)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM tasks').fetchone()[0], 0)
            with self.assertRaisesRegex(CoordinatorError, 'Invalid'):
                coordinator.record_candidate_check('DEMO-001', 'work',
                                                   lambda _: {**result, 'candidate_sha256': 'b' * 64})
            coordinator.stop_all()
            with self.assertRaisesRegex(CoordinatorError, 'Resume'):
                coordinator.record_candidate_check('DEMO-001', 'work', lambda _: result)

    def test_review_refuses_changed_source_and_candidate(self):
        workspace = self.workspace()
        self.implement(workspace)
        evidence = workspace.verify(Mock(run=Mock(return_value=1)))
        (self.repo / 'demo/helper.py').write_text('concurrent = True\n', encoding='utf-8')
        with self.assertRaisesRegex(DevelopmentError, 'source file changed'):
            apply_reviewed_candidate(self.repo, self.private, evidence['path'], evidence['sha256'])
        self.assertEqual((self.repo / 'demo/app.py').read_text(), 'def answer():\n    return 1\n')
        (self.repo / 'demo/helper.py').write_text('def base():\n    return 1\n', encoding='utf-8')
        (workspace.root / 'demo/app.py').write_text('changed after review\n', encoding='utf-8')
        with self.assertRaisesRegex(DevelopmentError, 'candidate file changed'):
            candidate_review(self.repo, self.private, evidence['path'], evidence['sha256'])

    def test_scope_blocks_tests_untracked_files_and_out_of_scope_paths(self):
        workspace = self.workspace()
        with self.assertRaisesRegex(DevelopmentError, 'not editable'):
            self.change(workspace, 'demo/test_app.py', 'pass')
        with self.assertRaisesRegex(ValueError, 'outside'):
            self.call(workspace, 'read', 'demo/local.txt')
        with self.assertRaisesRegex(DevelopmentError, 'outside'):
            self.workspace(DevelopmentScope('demo', ('other/app.py',), self.scope.edit_paths, self.scope.test_paths))
        with self.assertRaisesRegex(DevelopmentError, 'tracked'):
            self.workspace(DevelopmentScope('demo', ('demo/local.txt',), self.scope.edit_paths, self.scope.test_paths))

    def test_discovered_scope_uses_tracked_files_and_keeps_tests_read_only(self):
        scope = DevelopmentScope.discover(self.repo, 'demo')
        self.assertEqual(set(scope.edit_paths), {'demo/app.py', 'demo/helper.py'})
        self.assertEqual(scope.test_paths, ('demo/test_app.py',))
        workspace = self.workspace(scope)
        with self.assertRaisesRegex(DevelopmentError, 'not editable'):
            self.change(workspace, 'demo/test_app.py', 'pass')
        with self.assertRaises(DevelopmentError):
            DevelopmentScope.discover(self.repo, '../other')

    def test_discovery_protects_python_suffix_tests(self):
        (self.repo / 'demo/helper_test.py').write_text('import unittest\n', encoding='utf-8')
        self.git('add', 'demo/helper_test.py')
        scope = DevelopmentScope.discover(self.repo, 'demo')
        self.assertIn('demo/helper_test.py', scope.test_paths)
        self.assertNotIn('demo/helper_test.py', scope.edit_paths)
        workspace = self.workspace(scope)
        with self.assertRaises((DevelopmentError, PermissionError, ValueError)):
            self.call(workspace, 'write', 'demo/helper_test.py', 'changed\n', 'new')

    def test_discovery_keeps_test_fixtures_read_only(self):
        tests = self.repo / 'demo/tests'
        tests.mkdir()
        (tests / 'fixtures.py').write_text('expected = 42\n', encoding='utf-8')
        self.git('add', 'demo/tests/fixtures.py')
        scope = DevelopmentScope.discover(self.repo, 'demo')
        self.assertIn('demo/tests/fixtures.py', scope.read_paths)
        self.assertNotIn('demo/tests/fixtures.py', scope.edit_paths)
        with self.assertRaises(DevelopmentError):
            DevelopmentScope('demo', (), ('demo/tests/fixtures.py',), ('demo/test_app.py',)).validate()

    def test_discovery_protects_node_tests(self):
        (self.repo / 'demo/widget.cjs').write_text('module.exports = 1;\n', encoding='utf-8')
        (self.repo / 'demo/widget.test.cjs').write_text("require('node:test')('works', () => {});\n", encoding='utf-8')
        self.git('add', 'demo/widget.cjs', 'demo/widget.test.cjs')
        scope = DevelopmentScope.discover(self.repo, 'demo')
        self.assertIn('demo/widget.cjs', scope.edit_paths)
        self.assertIn('demo/widget.test.cjs', scope.test_paths)
        workspace = self.workspace(scope)
        with self.assertRaisesRegex(DevelopmentError, 'not editable'):
            self.change(workspace, 'demo/widget.test.cjs', 'changed')
        workspace = DevelopmentWorkspace(self.repo, self.private, scope, self.cancelled, allow_new_files=True)
        with self.assertRaises(DevelopmentError):
            self.call(workspace, 'write', 'demo/new.test.js', 'changed', 'new')

    def test_discovery_supports_spec_tests_and_additional_source_formats(self):
        files = {
            'demo/view.jsx': 'export default function View() { return null; }\n',
            'demo/settings.yaml': 'enabled: true\n',
            'demo/view.unit.spec.js': "require('node:test')('works', () => {});\n",
            'demo/view.unit.spec.tsx': "export const test = 'pending';\n",
        }
        for name, content in files.items():
            (self.repo / name).write_text(content, encoding='utf-8')
        self.git('add', *files)
        scope = DevelopmentScope.discover(self.repo, 'demo')
        self.assertIn('demo/view.jsx', scope.edit_paths)
        self.assertIn('demo/settings.yaml', scope.edit_paths)
        self.assertIn('demo/view.unit.spec.js', scope.test_paths)
        self.assertIn('demo/view.unit.spec.tsx', scope.read_paths)
        workspace = self.workspace(scope)
        with self.assertRaisesRegex(DevelopmentError, 'not editable'):
            self.change(workspace, 'demo/view.unit.spec.js', 'changed')
        with self.assertRaisesRegex(DevelopmentError, 'not editable'):
            self.change(workspace, 'demo/view.unit.spec.tsx', 'changed')
        workspace = DevelopmentWorkspace(self.repo, self.private, scope, self.cancelled, allow_new_files=True)
        with self.assertRaises(DevelopmentError):
            self.call(workspace, 'write', 'demo/new.component.spec.js', 'changed', 'new')
        with self.assertRaises(DevelopmentError):
            self.call(workspace, 'write', 'demo/new.component.spec.tsx', 'changed', 'new')

    @unittest.skipUnless(shutil.which('node'), 'Node is required for the runner test')
    def test_node_driver_requires_a_passing_registered_test(self):
        # The sandbox-specific guards are checked in the live opt-in test; this
        # exercises Node's real event protocol using disposable test files.
        driver = "const { run } = require('node:test');\nlet passed = 0;" + _NODE_TEST_DRIVER.split('let passed = 0;', 1)[1]
        fixture = self.repo / 'demo' / 'fixture.test.cjs'
        for contents, expected in (
            ("require('node:test')('works', () => {});\n", True),
            ("require('node:test').skip('skip', () => {});\n", False),
            ("require('node:test')('fails', () => { throw Error('failed'); });\n", False),
            ("module.exports = 1;\n", False),
        ):
            with self.subTest(contents=contents):
                fixture.write_text(contents, encoding='utf-8')
                result = subprocess.run([shutil.which('node'), '-e', driver, str(fixture)],
                                        capture_output=True, timeout=15)
                self.assertEqual(result.returncode == 0, expected, result.stderr.decode(errors='replace'))
                if expected:
                    self.assertGreater(json.loads(result.stdout)['tests_run'], 0)

    def test_selected_folder_can_create_new_source_without_overwriting_existing_files(self):
        scope = DevelopmentScope.discover(self.repo, 'demo')
        workspace = DevelopmentWorkspace(self.repo, self.private, scope, self.cancelled, allow_new_files=True)
        self.assertEqual(self.call(workspace, 'read', 'demo/new/feature.py'),
                         {'exists': False, 'content': '', 'sha256': 'new'})
        with self.assertRaises(ValueError):
            workspace.call({'operation': 'write', 'path': 'demo/new/rejected.py',
                            'content': 'pass', 'sha256': 'new', 'unexpected': ''})
        self.assertNotIn('demo/new/rejected.py', workspace.paths)
        self.call(workspace, 'write', 'demo/new/feature.py', 'answer = 42\n', 'new')
        evidence = workspace.verify(Mock(run=Mock(return_value=1)))
        manifest = json.loads(Path(evidence['path']).read_text(encoding='utf-8'))
        self.assertIn('demo/new/feature.py', manifest['changed'])
        self.assertFalse((self.repo / 'demo/new/feature.py').exists())
        for path in ('demo/local.txt', 'demo/test_new.py', 'other/new.py'):
            with self.subTest(path=path), self.assertRaises(DevelopmentError):
                self.call(workspace, 'write', path, 'blocked', 'new')

    def test_coordinator_dispatches_candidate_for_review_without_completing(self):
        _record(self.repo, 'FAKE-001')
        manager = Coordinator(self.repo, self.private / 'coordinator.sqlite3')
        manual = manager.register('demo', kind='manual')
        claim = manager.claim(manual['id'])
        with self.assertRaises(CoordinatorError):
            manager.set_development_scope(manual['id'], claim['lease_token'],
                                          expected_sha256='0' * 64, folder='demo')
        updated = manager.set_development_scope(manual['id'], claim['lease_token'],
                                               expected_sha256=claim['record_sha256'], folder='demo')
        self.assertEqual(updated['task']['verification'], {'kind': 'development', 'folder': 'demo'})
        manager.finish(manual['id'], claim['lease_token'], outcome='retry', summary='Ready for development')
        worker = manager.register('demo', kind='background')
        task = manager.claim(worker['id'])

        class FixtureExecutor:
            def run_development(self, claim, workspace, verifier, cancelled, emit, save_session):
                self_context = workspace.call({'operation': 'read', 'path': 'PROJECT.md', 'content': '', 'sha256': ''})
                assert 'FAKE-001' in self_context['content']
                original = workspace.call({'operation': 'read', 'path': 'demo/app.py', 'content': '', 'sha256': ''})
                workspace.call({'operation': 'write', 'path': 'demo/app.py',
                                'content': 'def answer():\n    return 42\n', 'sha256': original['sha256']})
                return {'kind': 'result', 'summary': 'Fixture candidate'}, workspace.verify(Mock(run=Mock(return_value=1)))

        supervisor = Supervisor(manager, executor=FixtureExecutor())
        result = supervisor._run_turn(worker['id'], task, threading.Event())
        self.assertTrue(result, manager.worker(worker['id']).get('last_error'))
        view = manager.snapshot('demo')['projects'][0]
        self.assertEqual(view['status'], 'blocked')
        self.assertIn('awaiting review and integration', view['checkpoint'])
        self.assertEqual((self.repo / 'demo/app.py').read_text(encoding='utf-8'), 'def answer():\n    return 1\n')
        self.assertIsNone(manager.claim(worker['id']))

        evidence = manager.candidate_evidence('FAKE-001', task['task_id'])
        with self.assertRaisesRegex(CoordinatorError, 'Verify the applied changes'):
            manager.complete_candidate('FAKE-001', task['task_id'], note='Reviewed all criteria')
        apply_reviewed_candidate(self.repo, self.private, evidence['path'], evidence['sha256'])
        context = Path(evidence['path']).parent / 'workspace' / 'PROJECT.md'
        saved_context = context.read_bytes()
        context.write_text('modified context\n', encoding='utf-8')
        with self.assertRaisesRegex(DevelopmentError, 'project context changed'):
            verify_applied(self.repo, self.private, evidence['path'], evidence['sha256'],
                           Mock(run=Mock(return_value=1)), threading.Event())
        context.write_bytes(saved_context)
        result = verify_applied(self.repo, self.private, evidence['path'], evidence['sha256'],
                                Mock(run=Mock(return_value=1)), threading.Event())
        manager.record_candidate_check('FAKE-001', task['task_id'], lambda _: result)
        with self.assertRaises(CoordinatorError):
            manager.complete_candidate('FAKE-001', task['task_id'], note='')
        manager.complete_candidate('FAKE-001', task['task_id'], note='Reviewed the requested behavior and criteria')
        milestone = manager.snapshot('demo')['projects'][0]['milestones'][0]
        self.assertEqual(milestone['status'], 'completed')
        self.assertTrue(milestone['verified'])
        with self.assertRaises(CoordinatorError):
            manager.reconcile_task('FAKE-001', task['task_id'], note='No invalid evidence')
        (self.repo / 'demo/app.py').write_text('changed after review\n', encoding='utf-8')
        invalid = manager.snapshot('demo')['projects'][0]['milestones'][0]
        self.assertFalse(invalid['verified'])
        self.assertEqual(invalid['status'], 'reconcile')
        manager.reconcile_task('FAKE-001', task['task_id'], note='Source changed; recheck the task')
        self.assertEqual(manager.snapshot('demo')['projects'][0]['milestones'][0]['status'], 'queued')

    def test_changed_inputs_and_nonexecuting_verifier_reject_candidate(self):
        workspace = self.workspace()
        self.implement(workspace)
        with self.assertRaisesRegex(DevelopmentError, 'successful executable checks'):
            workspace.verify(Mock(run=Mock(return_value=0)))
        (self.repo / 'demo/helper.py').write_text('# changed after snapshot\n', encoding='utf-8')
        with self.assertRaisesRegex(DevelopmentError, 'original workspace changed'):
            workspace.verify(Mock(run=Mock(return_value=1)))
        self.assertFalse((workspace.run_dir / 'verified-development.json').exists())

    def test_changed_candidate_and_stop_prevent_evidence(self):
        workspace = self.workspace()
        self.implement(workspace)

        def mutate(*_args):
            self.change(workspace, 'demo/helper.py', '# changed while testing\n')
            return 1

        with self.assertRaisesRegex(DevelopmentError, 'changed during verification'):
            workspace.verify(Mock(run=mutate))
        self.cancelled.set()
        with self.assertRaises(InterruptedError):
            workspace.verify(Mock())

    def test_official_adapter_keeps_new_files_out_of_read_grants_and_requires_tests(self):
        workspace = self.workspace()
        executor = OfficialExecutor()
        config = SimpleNamespace(execution_backend='native')
        claim = {'project_id': 'DEMO-001', 'task': {'title': 'Implement', 'criteria': 'Return the expected value'}}
        verifier = Mock(run=Mock(return_value=1))

        def codex_turn(_config, prompt, restricted, *_args):
            self.assertIn('demo/extra/value.py', json.loads(prompt)['editable_paths'])
            self.assertNotIn('demo/extra/value.py', restricted.paths)
            self.implement(workspace)
            return {'kind': 'result'}

        with patch.object(executor, 'session', return_value=nullcontext(config)), patch.object(
                executor, '_turn', side_effect=codex_turn):
            _, evidence = executor.run_development(claim, workspace, verifier, self.cancelled, Mock(), Mock())
        self.assertEqual(evidence['kind'], 'passed_test')
        verifier.run.assert_called_once_with(workspace, self.cancelled)

    def test_unsupported_verifier_is_rejected_before_model_turn(self):
        workspace = self.workspace()
        executor = OfficialExecutor()
        claim = {'project_id': 'DEMO-001', 'task': {'title': 'Implement', 'criteria': 'Complete'}}
        config = SimpleNamespace(execution_backend='native')
        verifier = BubblewrapVerifier()
        with patch.object(executor, 'session', return_value=nullcontext(config)), patch.object(
                verifier, '_prefix', side_effect=DevelopmentError('No sandbox')), patch.object(
                executor, '_turn') as turn:
            with self.assertRaisesRegex(DevelopmentError, 'No sandbox'):
                executor.run_development(claim, workspace, verifier, self.cancelled, Mock(), Mock())
        turn.assert_not_called()

    @unittest.skipUnless(os.environ.get('PORTFOLIO_TEST_SANDBOX'), 'requires the provisioned Linux sandbox')
    def test_real_networkless_sandbox_rejects_failure_and_verifies_multiple_files(self):
        workspace = self.workspace()
        verifier = BubblewrapVerifier(os.environ['PORTFOLIO_TEST_SANDBOX'] if os.name == 'nt' else None)
        self.change(workspace, 'demo/app.py', 'def answer():\n    return 0\n')
        with self.assertRaisesRegex(DevelopmentError, 'failed'):
            workspace.verify(verifier)
        self.implement(workspace)
        result = workspace.verify(verifier)
        self.assertEqual(json.loads(Path(result['path']).read_bytes())['tests_run'], 1)
        self.assertEqual(self.git('diff', 'HEAD'), b'')
