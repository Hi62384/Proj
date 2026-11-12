"""Stop remains responsive while a sandbox verification is running."""
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from portfolio_manager.integration import ManagerHost


class VerificationStopTests(unittest.TestCase):
    def test_success_accepts_revalidated_evidence_with_new_timestamp(self):
        class Coordinator:
            db_path = Path('state/coordinator.sqlite3')

            def candidate_evidence(self, project_id, task_id):
                return {'kind': 'passed_test', 'path': 'candidate', 'sha256': 'a' * 64, 'verified_at': 1}

            def control(self):
                return {'stopped': False, 'emergency': False}

            def record_candidate_check(self, project_id, task_id, callback):
                return callback({'kind': 'passed_test', 'path': 'candidate', 'sha256': 'a' * 64, 'verified_at': 2})

            def _catalog(self):
                return {'project': {'content_sha256': 'record'}}, None

        host = ManagerHost.__new__(ManagerHost)
        host.coordinator = Coordinator()
        host.repo = Path('.')
        result = {'record_sha256': 'record', 'tests_run': 1}
        with patch('portfolio_manager.applied_verification.verify_applied', return_value=result), \
             patch('portfolio_manager.development.BubblewrapVerifier', return_value=SimpleNamespace()):
            self.assertEqual(host.verify_candidate('project', 'task'), result)
            host.coordinator.record_candidate_check = lambda project, task, callback: callback(
                {'kind': 'passed_test', 'path': 'other', 'sha256': 'a' * 64, 'verified_at': 2})
            with self.assertRaisesRegex(ValueError, 'candidate changed'):
                host.verify_candidate('project', 'task')

    def test_stop_cancels_without_holding_candidate_guard(self):
        started = threading.Event()
        stopped = threading.Event()
        evidence = {'path': 'candidate', 'sha256': 'a' * 64}

        class Coordinator:
            db_path = Path('state/coordinator.sqlite3')

            def candidate_evidence(self, project_id, task_id):
                return evidence

            def control(self):
                return {'stopped': stopped.is_set(), 'emergency': False}

            def record_candidate_check(self, project_id, task_id, callback):
                raise AssertionError('Cancelled verification must not enter the integration guard')

        host = ManagerHost.__new__(ManagerHost)
        host.coordinator = Coordinator()
        host.repo = Path('.')
        host.workspace_lock = threading.RLock()
        errors = []

        def fake_verify(repo, private, path, sha256, verifier, cancelled):
            started.set()
            if not cancelled.wait(3):
                raise AssertionError('Stop did not cancel verification')
            raise InterruptedError('Verification was cancelled.')

        def run():
            try:
                host.verify_candidate('project', 'task')
            except Exception as error:
                errors.append(error)

        with patch('portfolio_manager.applied_verification.verify_applied', fake_verify), \
             patch('portfolio_manager.development.BubblewrapVerifier', return_value=SimpleNamespace()):
            thread = threading.Thread(target=run)
            thread.start()
            self.assertTrue(started.wait(3))
            stopped.set()
            thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], InterruptedError)


if __name__ == '__main__':
    unittest.main()
