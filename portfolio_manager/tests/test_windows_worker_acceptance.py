import subprocess
import unittest
from unittest.mock import patch

from portfolio_manager.tests import windows_worker_acceptance as acceptance


class SyntheticAcceptanceTests(unittest.TestCase):
    def test_success_requires_every_marker_and_success_exit(self):
        self.assertTrue(acceptance.classify(0, 'alpha beta', ('alpha', 'beta')))
        self.assertFalse(acceptance.classify(0, 'alpha', ('alpha', 'beta')))
        self.assertFalse(acceptance.classify(1, 'alpha beta', ('alpha', 'beta')))

    def test_synthetic_success_never_marks_real_worker_ready(self):
        responses = []
        for _module, arguments, markers in acceptance._CASES.values():
            responses.append(subprocess.CompletedProcess(arguments, 0, '\n'.join(markers), ''))
        with patch.object(acceptance.os, 'name', 'nt'):
            result = acceptance.run_cases(run=lambda *args, **kwargs: responses.pop(0))
        self.assertEqual(result['status'], 'not_ready')
        self.assertTrue(all(case['passed'] for case in result['synthetic'].values()))
        self.assertIn('reviewed Codex home and cwd startup support', result['remaining'])

    def test_timeout_is_not_counted_as_success(self):
        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired('synthetic', 45)
        with patch.object(acceptance.os, 'name', 'nt'):
            result = acceptance.run_cases(run=timeout)
        self.assertEqual(result['status'], 'not_ready')
        self.assertTrue(all(not case['passed'] for case in result['synthetic'].values()))

    def test_unconfirmed_process_cleanup_does_not_delete_profiles(self):
        class Owner:
            identifier = 'a' * 32
            closed = False
            def close(self): self.closed = True
        owner = Owner()
        def uncertain(*args, **kwargs):
            raise acceptance.OwnedCleanupUnconfirmed('simulated uncertain process')
        with patch.object(acceptance.os, 'name', 'nt'):
            result = acceptance.run_cases(run=uncertain, profile_factory=lambda: owner)
        self.assertFalse(owner.closed)
        self.assertEqual(result['synthetic']['appserver_streams']['owned_profile_id'], owner.identifier)
        self.assertFalse(result['synthetic']['split_profiles']['passed'])

    def test_profile_cleanup_failure_stops_later_cases(self):
        class Owner:
            identifier = 'b' * 32
            def close(self): raise RuntimeError('synthetic cleanup failure')
        _module, arguments, markers = acceptance._CASES['appserver_streams']
        response = subprocess.CompletedProcess(arguments, 0, '\n'.join(markers), '')
        with patch.object(acceptance.os, 'name', 'nt'):
            result = acceptance.run_cases(run=lambda *args, **kwargs: response, profile_factory=Owner)
        self.assertFalse(result['synthetic']['appserver_streams']['passed'])
        self.assertEqual(result['synthetic']['appserver_streams']['owned_profile_id'], Owner.identifier)
        self.assertFalse(result['synthetic']['split_profiles']['passed'])


if __name__ == '__main__':
    unittest.main()
