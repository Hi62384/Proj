"""Deterministic regressions for failures observed in the live WSL acceptance run."""
import json
import tomllib
import unittest
from dataclasses import replace
from unittest.mock import Mock, patch

import test_relay as fixtures
from portfolio_autopilot.codex_relay import sandbox_probe
from portfolio_autopilot.codex_relay.codex import Codex
from portfolio_autopilot.codex_relay.diagnostics import RelayError
from portfolio_autopilot.codex_relay.permissions import render
from portfolio_autopilot.codex_relay.workspace import Workspace


class LiveRepairRegressions(unittest.TestCase):
    setUp = fixtures.RelayCase.setUp
    approve = fixtures.RelayCase.approve
    run_task = fixtures.RelayCase.run_task
    reply = fixtures.RelayCase.reply

    def test_local_reply_requires_review_and_retains_scope_and_thread(self):
        self.approve()
        before = self.run_task()
        with self.assertRaises(ValueError):
            self.relay.owner_reply('demo-001', 'Correct the spelling')
        self.relay.owner_reply('demo-001', 'Correct the spelling', True)
        task = self.store.get('demo-001')
        self.assertEqual(task['scope'], before['scope'])
        self.assertEqual(task['thread_id'], before['thread_id'])
        self.assertEqual(task['pending_reply'], 'Correct the spelling')
        self.assertEqual(task['status'], 'Approved')
        with self.assertRaises(ValueError):
            self.relay.owner_reply('demo-001', 'Another instruction', True)

    def test_local_reply_cannot_approve_a_proposal(self):
        self.relay.poll()
        with self.assertRaises(ValueError):
            self.relay.owner_reply('demo-001', 'Execute', True)
        self.assertFalse(self.store.get('demo-001')['approved'])

    def test_reply_binds_to_last_published_message_despite_unsent_status(self):
        self.approve()
        self.run_task()
        comment = self.reply()
        task = self.store.get('demo-001')
        published = task['published_anchor']
        self.relay.announce(task, 'CODEX_PROGRESS')
        self.assertNotEqual(self.store.get('demo-001')['anchor'], published)
        self.assertTrue(self.relay.receive(task, comment))
        self.relay.process_inbox()
        task = self.store.get('demo-001')
        self.assertEqual(task['status'], 'Approved')
        self.assertIn('spelling', task['pending_reply'])

    def test_unpublished_anchor_is_rejected_and_publication_advances_anchor(self):
        self.approve()
        self.run_task()
        comment = self.reply()
        task = self.store.get('demo-001')
        self.relay.announce(task, 'CODEX_PROGRESS')
        value = fixtures.messages.message(comment['body'])
        value['reply_to'] = task['anchor']
        comment['body'] = fixtures.messages.encode(value)
        self.assertFalse(self.relay.receive(task, comment))
        self.relay.flush()
        self.assertEqual(self.store.get('demo-001')['published_anchor'], value['reply_to'])
        self.assertTrue(self.relay.receive(task, comment))

    def test_obsolete_status_is_superseded_without_post(self):
        self.approve()
        task = self.store.get('demo-001')
        self.relay.announce(task, 'CODEX_PROGRESS')
        self.relay.announce(task, 'CODEX_PROGRESS')
        count = len(self.github.posts)
        self.relay.flush()
        self.assertEqual(len(self.github.posts), count + 1)
        self.assertGreaterEqual(self.store.delivery()['superseded'], 2)
        self.assertEqual(self.store.outgoing(), [])

    def test_pause_retains_active_instruction(self):
        task = self.approve()
        task.update(status='Running', active_instruction='Correct the greeting', pending_reply=None)
        self.store.save(task)
        self.relay.control('demo-001', 'pause')
        task = self.store.get('demo-001')
        self.assertEqual(task['pending_reply'], 'Correct the greeting')
        self.assertEqual(task['status'], 'Needs Owner')

    def test_absent_file_read_supplies_new_write_token(self):
        self.approve()
        workspace = Workspace(self.root, ['demo.py'], lambda: True, lambda *args: None,
                              self.config.data_dir / 'backups')
        value = workspace.call({'operation': 'read', 'path': 'demo.py', 'content': '', 'sha256': ''})
        self.assertEqual(value, {'exists': False, 'content': '', 'sha256': 'new'})
        workspace.call({'operation': 'write', 'path': 'demo.py', 'content': 'x = 1\n', 'sha256': value['sha256']})
        self.assertEqual((self.root / 'demo.py').read_bytes(), b'x = 1\n')

    def test_health_check_never_rewrites_profile_during_execution(self):
        factory = Mock()
        codex = Codex(self.config, factory)
        codex.last_health = {'available': True, 'sandbox': 'verified'}
        with codex.execution_lock:
            self.assertEqual(codex.doctor(), {**codex.last_health, 'busy': True})
        factory.assert_not_called()
        factory.side_effect = RelayError('environment', 'fixture', 'Unavailable')
        with self.assertRaises(RelayError):
            codex.doctor()
        self.assertFalse(codex.execution_lock.locked())

    def test_private_codex_bootstrap_is_an_exact_read_grant(self):
        config = replace(self.config, execution_backend='wsl',
                         wsl_home='/home/user/.local/share/codex-relay/codex-home',
                         wsl_binary='/home/user/.local/share/codex-relay/runtime/1/bin/codex')
        fs = tomllib.loads(render(config))['permissions']['relay-locked']['filesystem']
        self.assertEqual(fs[config.wsl_binary], 'read')
        self.assertEqual(fs[':root'], 'deny')
        self.assertNotIn('/home/user', fs)
        with self.assertRaises(ValueError):
            render(replace(config, wsl_binary='/home/user/unrelated/codex'))

    def test_security_probe_requires_every_denial_and_positive_control(self):
        fixture = {'control': True, 'denied': '/fixture/denied', 'link': '/fixture/link',
                   'root': '/fixture', 'port': 1234, 'nonce': 'fixture'}
        for checks in ({key: True for key in sandbox_probe.CHECKS},
                       {key: key != 'network_blocked' for key in sandbox_probe.CHECKS},
                       {'network_blocked': True}):
            rpc = Mock(workspace='/workspace')
            rpc.request.return_value = {'exitCode': 0, 'stdout': json.dumps(checks)}
            with patch('portfolio_autopilot.codex_relay.wsl_runtime.python', side_effect=[fixture, {}]) as helper:
                if set(checks) == sandbox_probe.CHECKS and all(checks.values()):
                    self.assertEqual(sandbox_probe.verify(rpc, self.config), checks)
                else:
                    with self.assertRaises(RelayError):
                        sandbox_probe.verify(rpc, self.config)
                self.assertEqual(helper.call_count, 2)
                self.assertEqual(rpc.request.call_args.args[0], 'command/exec')
                self.assertEqual(rpc.request.call_args.args[1]['permissionProfile'], 'relay-locked')
        rpc = Mock(workspace='/workspace')
        with patch('portfolio_autopilot.codex_relay.wsl_runtime.python', side_effect=[{**fixture, 'control': False}, {}]):
            with self.assertRaises(RelayError):
                sandbox_probe.verify(rpc, self.config)
        rpc.request.assert_not_called()
