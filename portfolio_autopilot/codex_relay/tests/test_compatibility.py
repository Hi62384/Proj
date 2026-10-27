"""Regressions for the real Windows failures; no inference, network, or admin setup."""
from dataclasses import replace
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import tomllib
import unittest
from unittest.mock import patch

from portfolio_autopilot.codex_relay.codex import Codex, Rpc
from portfolio_autopilot.codex_relay.config import Config, ROOT, safe_path
from portfolio_autopilot.codex_relay.diagnostics import RelayError, protocol_error, sanitize, record, latest
from portfolio_autopilot.codex_relay.permissions import render, preflight, selected_mode
from portfolio_autopilot.codex_relay.sandbox_setup import provision
from portfolio_autopilot.codex_relay import wsl_runtime, wsl_setup
from portfolio_autopilot.codex_relay.compatibility import inspect_binary
from test_relay import MockRpc, MockCodex
import test_relay as fixtures


class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.config = Config(data_dir=self.base / 'runtime')

    def test_profile_has_exact_read_grants_no_broad_workspace_or_legacy_settings(self):
        profile = tomllib.loads(render(self.config, ['codex_relay_demo.txt']))
        self.assertEqual(profile['default_permissions'], 'relay-locked')
        self.assertNotIn('sandbox_mode', profile)
        fs = profile['permissions']['relay-locked']['filesystem']
        self.assertEqual(fs[':root'], 'deny')
        self.assertEqual(fs[str(ROOT / 'codex_relay_demo.txt')], 'read')
        self.assertNotIn(':workspace_roots', fs)
        self.assertFalse(any(v == 'write' for v in fs.values()))
        self.assertFalse(profile['permissions']['relay-locked']['network']['enabled'])
        for name in ('shell_tool', 'unified_exec', 'plugins', 'apps', 'multi_agent', 'code_mode', 'js_repl'):
            self.assertFalse(profile['features'][name])

    def test_selected_windows_mode_survives_generated_config(self):
        folder = self.config.data_dir / 'codex-home'; folder.mkdir(parents=True)
        (folder / 'config.toml').write_text('[windows]\nsandbox="elevated"\n')
        value = tomllib.loads(render(self.config))
        self.assertEqual(selected_mode(self.config), 'elevated')
        if os.name == 'nt': self.assertEqual(value['windows']['sandbox'], 'elevated')
        self.assertEqual(value['permissions']['relay-locked']['filesystem'][':root'], 'deny')

    def test_native_unsupported_read_policy_has_specific_diagnostic(self):
        error = protocol_error('thread/start', {'code': -32603, 'message': 'windows unelevated restricted-token sandbox cannot enforce split filesystem read restrictions directly; refusing to run unsandboxed'})
        self.assertEqual(error.category, 'sandbox.windows_restricted_token')
        self.assertIn('Administrator', error.action)
        root = protocol_error('command/exec', {'message': 'elevated Windows sandbox requires effective `:root` read access'})
        self.assertEqual(root.category, 'sandbox.windows_root_read_required')
        self.assertIn('Do not broaden', root.action)

    def test_authentication_protocol_inference_and_missing_session_are_distinct(self):
        cases = [('Unauthorized 401', 'authentication'), ('Invalid request: readOnly.access is no longer supported', 'protocol.compatibility'),
                 ('no rollout found for thread id demo', 'session.missing'), ('model request failed', 'inference'),
                 ('native MXC is unavailable on this executor', 'sandbox.mxc_unavailable')]
        for message, category in cases:
            with self.subTest(message=message):
                self.assertEqual(protocol_error('turn/start', {'message': message}).category, category)

    def test_diagnostics_are_sanitized_and_local(self):
        error = protocol_error('thread/start', {'message': 'Invalid request C:\\Users\\Private\\auth.json\nBearer abcdef\ngithub_pat_deadbeef\nsk-secret\naccess_token=private-value\nprivate@example.org'})
        value = record(self.config.data_dir, error)
        output = json.dumps(latest(self.config.data_dir))
        for secret in ('abcdef', 'deadbeef', 'sk-secret', 'private-value', 'private@example.org', 'Users\\\\Private'):
            self.assertNotIn(secret, output)
        self.assertEqual(value['stage'], 'thread/start')
        self.assertEqual(value['category'], 'protocol.compatibility')

    def test_diagnostic_write_failure_does_not_mask_original_error(self):
        with patch.object(Path, 'mkdir', side_effect=PermissionError('test fixture')):
            value = record(self.config.data_dir, RelayError('sandbox.test', 'fixture', 'Original error'))
        self.assertEqual(value['category'], 'sandbox.test')
        self.assertIn('persistence_error', value)

    def test_preflight_failure_never_creates_a_thread(self):
        class Unsupported(MockRpc):
            def request(inner, method, params, **kwargs):
                if method == 'command/exec':
                    raise protocol_error(method, {'message': 'windows unelevated restricted-token sandbox cannot enforce split filesystem read restrictions'})
                return super().request(method, params, **kwargs)
        rpc = Unsupported(self.config); saved = []
        client = Codex(self.config, lambda c, **kw: rpc)
        with self.assertRaises(RelayError):
            client.run({}, 'approved task', None, threading.Event(), lambda *x: None, saved.append)
        self.assertEqual(saved, [])
        self.assertFalse(any(m.startswith('thread/') or m == 'turn/start' for m, _ in rpc.calls))
        self.assertTrue(rpc.closed)

    def test_missing_named_profile_does_not_fallback(self):
        class NoProfile(MockRpc):
            def request(inner, method, params, **kwargs):
                return {'data': [{'id': ':read-only', 'allowed': True}]}
        with self.assertRaises(RelayError): preflight(NoProfile(self.config), self.config)

    def test_command_probe_uses_permissionProfile_not_sandboxPolicy(self):
        rpc = MockRpc(self.config); status = preflight(rpc, self.config)
        params = next(p for m, p in rpc.calls if m == 'command/exec')
        self.assertEqual(params['permissionProfile'], 'relay-locked')
        self.assertNotIn('sandboxPolicy', params)
        self.assertEqual(status['sandbox'], 'verified')

    def test_all_thread_and_turn_calls_use_named_permissions(self):
        for saved in (None, 'thread-001'):
            rpc = MockRpc(self.config)
            class Files:
                paths = {'codex_relay_demo.txt'}
                def call(inner, args): return {'paths': sorted(inner.paths)}
            Codex(self.config, lambda c, **kw: rpc).run({'thread_id': saved}, 'task', Files(), threading.Event(), lambda *x: None, lambda x: None)
            for method, params in rpc.calls:
                if method in ('thread/start', 'thread/resume', 'turn/start'):
                    self.assertEqual(params['permissions'], 'relay-locked')
                    self.assertNotIn('sandbox', params); self.assertNotIn('sandboxPolicy', params)
                    self.assertNotIn('readOnly.access', json.dumps(params))
                    self.assertEqual(params['approvalPolicy'], 'never')

    def test_provisioning_controller_cannot_start_inference_or_commands(self):
        rpc = Rpc.__new__(Rpc); rpc.setup_only = True
        for method in ('thread/start', 'thread/resume', 'turn/start', 'command/exec', 'mcpServer/tool/call'):
            with self.assertRaises(ValueError): rpc.request(method, {})

    def test_admin_setup_requires_explicit_approval(self):
        with patch('portfolio_autopilot.codex_relay.sandbox_setup.Rpc') as factory:
            with self.assertRaises(ValueError): provision(self.config)
            factory.assert_not_called()

    def test_rpc_retains_underlying_error_and_category(self):
        rpc = Rpc.__new__(Rpc); rpc.setup_only = False; rpc.config = self.config
        rpc.pending = {}; rpc.lock = threading.Lock(); rpc.next_id = 0
        rpc.compatibility = {'version': 'fixture'}
        def send(value):
            rpc.pending[value['id']].put({'error': {'code': -32602, 'message': 'Invalid request: readOnly.access is no longer supported'}})
        rpc.send = send
        with self.assertRaises(RelayError) as caught: rpc.request('turn/start', {})
        self.assertEqual(caught.exception.category, 'protocol.compatibility')
        self.assertEqual(rpc.last_protocol_error['code'], -32602)
        self.assertIn('no longer supported', latest(self.config.data_dir)['detail'])
        self.assertFalse(rpc.pending)

    def test_rpc_timeout_is_ambiguous_and_not_retried(self):
        rpc = Rpc.__new__(Rpc); rpc.setup_only = False; rpc.config = self.config
        rpc.pending = {}; rpc.lock = threading.Lock(); rpc.next_id = 0; calls = []
        rpc.send = calls.append
        with self.assertRaises(RelayError) as caught: rpc.request('turn/start', {}, timeout=0)
        self.assertEqual(caught.exception.category, 'timeout')
        self.assertEqual(len(calls), 1)

    def test_unsupported_cli_schema_fails_before_app_server_start(self):
        exe = self.base / 'fixture.exe'; exe.write_bytes(b'not an executable')
        version = subprocess.CompletedProcess([], 0, 'codex fixture', '')
        generated = subprocess.CompletedProcess([], 0, '', '')
        with patch('portfolio_autopilot.codex_relay.compatibility.subprocess.run', side_effect=[version, generated]):
            with self.assertRaises(RelayError) as caught: inspect_binary(exe, self.config.data_dir)
        self.assertEqual(caught.exception.category, 'protocol.compatibility')
        self.assertIn('ThreadStartParams', caught.exception.explanation)

    def test_schema_timeout_is_actionable_and_not_retried(self):
        exe = self.base / 'fixture.exe'; exe.write_bytes(b'not an executable')
        with patch('portfolio_autopilot.codex_relay.compatibility.subprocess.run', side_effect=subprocess.TimeoutExpired('fixture', 15)) as calls:
            with self.assertRaises(RelayError) as caught: inspect_binary(exe, self.config.data_dir)
        self.assertEqual(caught.exception.category, 'protocol.compatibility')
        self.assertEqual(calls.call_count, 1)

    def test_wsl_resource_error_decodes_utf16_and_never_installs(self):
        failure = subprocess.CompletedProcess([], 1, 'Wsl/HCS/ERROR_NO_SYSTEM_RESOURCES'.encode('utf-16-le'), b'')
        with patch('portfolio_autopilot.codex_relay.wsl_runtime.subprocess.run', return_value=failure):
            with self.assertRaises(RelayError) as caught: wsl_runtime.call(self.config, ['/usr/bin/true'])
        self.assertEqual(caught.exception.category, 'environment.wsl_resources')
        with patch('portfolio_autopilot.codex_relay.wsl_runtime.python', side_effect=caught.exception), patch('portfolio_autopilot.codex_relay.wsl_runtime.call') as calls:
            with self.assertRaises(RelayError): wsl_setup.install(self.config, approved=True)
            calls.assert_not_called()

    def test_wsl_setup_requires_approval_and_installer_has_valid_python(self):
        compile(wsl_setup.INSTALL, '<wsl installer>', 'exec')
        for source in wsl_runtime.prepare.__code__.co_consts:
            if isinstance(source, str) and source.startswith('import '): compile(source, '<wsl helper>', 'exec')
        with self.assertRaises(ValueError): wsl_setup.install(self.config)

    def test_wsl_paths_and_distribution_are_validated(self):
        for changes in ({'wsl_distribution': '--bad'}, {'wsl_home': '/root/relay'}, {'wsl_binary': '/home/user/../secrets'}):
            with self.assertRaises(ValueError): replace(self.config, **changes).validate()

    def test_wsl_profile_uses_linux_exact_paths_and_no_windows_mode(self):
        value = tomllib.loads(render(replace(self.config, execution_backend='wsl'), ['codex_relay_demo.txt'], path_mapper=lambda p: '/mnt/c/project/' + p.name))
        self.assertNotIn('windows', value)
        fs = value['permissions']['relay-locked']['filesystem']
        self.assertEqual(fs['/mnt/c/project/codex_relay_demo.txt'], 'read')
        self.assertEqual(fs[':root'], 'deny')

    @unittest.skipUnless(os.name == 'nt', 'Windows junction regression')
    def test_windows_directory_junction_is_rejected(self):
        root = self.base / 'fixtures'; root.mkdir(); target = root / 'ordinary'; target.mkdir()
        (target / 'note.txt').write_text('harmless fixture')
        junction = root / 'junction'
        result = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(junction), str(target)], capture_output=True)
        if result.returncode: self.skipTest('Junction creation unavailable in this executor')
        with self.assertRaises(ValueError): safe_path(root, 'junction/note.txt')


class RecoveryRegressions(unittest.TestCase):
    setUp = fixtures.RelayCase.setUp
    approve = fixtures.RelayCase.approve
    run_task = fixtures.RelayCase.run_task
    reply = fixtures.RelayCase.reply
    def test_environment_failure_blocks_additional_executions_and_survives_restart(self):
        from portfolio_autopilot.codex_relay.scheduler import Relay
        class Unsupported(MockCodex):
            def run(inner, *args, **kwargs):
                raise RelayError('sandbox.windows_root_read_required', 'command/exec', 'Unsupported restricted reads')
        self.approve(); self.relay.codex = Unsupported()
        self.assertEqual(self.run_task()['status'], 'Failed')
        self.assertTrue(self.relay.execution_block)
        self.relay.control('demo-001', 'resume'); self.run_task()
        self.assertEqual(self.store.get('demo-001')['status'], 'Approved')
        fresh = Relay(self.config, self.store, self.github, MockCodex())
        self.assertTrue(fresh.execution_block)
        fresh.test_connection(); self.assertFalse(fresh.execution_block)

    def test_server_interruption_never_leaves_task_running(self):
        class Interrupted(MockCodex):
            def run(inner, *args, **kwargs): raise InterruptedError('fixture interruption')
        self.approve(); self.relay.codex = Interrupted()
        task = self.run_task()
        self.assertEqual(task['status'], 'Needs Owner'); self.assertTrue(task['paused'])
        self.assertIsNone(self.relay.active_id)

    def test_failed_followup_keeps_instruction_for_owner_retry(self):
        task = self.approve(); self.run_task(); task = self.store.get('demo-001')
        self.relay.receive(task, self.reply(text='Use the corrected greeting.'))
        self.relay.process_inbox(); self.codex.fail = True; task = self.run_task()
        self.assertEqual(task['pending_reply'], 'Use the corrected greeting.')
