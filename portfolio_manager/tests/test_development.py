import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock, patch

from portfolio_manager.development import BubblewrapVerifier, DevelopmentError, DevelopmentScope, DevelopmentWorkspace
from portfolio_manager.runner import OfficialExecutor


class DevelopmentTests(unittest.TestCase):
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
