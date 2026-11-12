"""Exercise the same policy and transport used by the desktop controller."""
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

APP = Path(__file__).resolve().parents[2] / 'apps' / 'codex_desktop_assistant'
sys.path.insert(0, str(APP))
from assistant.permissions import Denied, Permissions
from assistant.storage import Store
from bridge.client import ControllerClient
from bridge.runtime import Runtime


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.runtime = Runtime.__new__(Runtime)
        self.runtime.store = Store(Path(temporary.name) / 'CodexDesktopAssistant')
        self.addCleanup(self.runtime.store.close)
        self.runtime.manager = Mock()
        self.control = {'mode': 'human', 'stopped': False, 'emergency': False, 'mode_epoch': 0}
        self.runtime.manager.control.side_effect = lambda: dict(self.control)
        self.runtime.permissions = Permissions()
        self.runtime.permissions.resume('owner')
        self.runtime.closed = threading.Event()
        self.runtime.requests = []
        self.runtime.clients = {}
        self.runtime.inflight = {}
        self.runtime.reference_queries = set()
        self.runtime.lock = threading.RLock()
        self.runtime.operation_lock = threading.RLock()
        self.runtime.owner = 'owner'
        self.runtime.broker = Mock()
        self.runtime.emit = Mock()

    def test_afk_does_not_open_approval_card_or_reuse_it_as_consent(self):
        self.control['mode'] = 'afk'
        self.assertFalse(self.runtime.approve('owner', 'Manual test step', {'question': 'synthetic detail'}))
        self.assertFalse(self.runtime.approve('owner', 'Manual test step', {'question': 'synthetic detail'}))
        self.assertEqual(self.runtime.requests, [])
        self.runtime.emit.assert_not_called()
        saved = self.runtime.store.settings()['portfolio_parked_bridge_requests']
        self.assertEqual(len(saved), 1)
        self.assertNotIn('synthetic detail', str(saved))
        self.control.update(mode='human', mode_epoch=1)
        self.assertEqual(self.runtime.pending(), [])

    def test_mode_round_trip_invalidates_pending_approval(self):
        def owner_decides(kind, conversation, request):
            self.control.update(mode='human', mode_epoch=2)
            request['allowed'] = True
            request['event'].set()

        self.runtime.emit.side_effect = owner_decides
        self.assertFalse(self.runtime.approve('owner', 'Synthetic pending approval', {}))

    def test_human_mode_preserves_exact_owner_approval(self):
        def owner_decides(kind, conversation, request):
            request['allowed'] = True
            request['event'].set()

        self.runtime.emit.side_effect = owner_decides
        self.assertTrue(self.runtime.approve('owner', 'Synthetic pending approval', {}))

    def test_stop_blocks_legacy_computer_capability(self):
        self.control['stopped'] = True
        with self.assertRaises(Denied):
            self.runtime.call('a' * 32, 'chrome.inspect', {})
        self.runtime.broker.call.assert_not_called()

    def test_mode_change_cancels_at_dispatch_guard_after_prior_checks(self):
        def refresh_then_dispatch(owner, action, *, cancel_event):
            self.assertFalse(cancel_event.is_set())
            self.control.update(mode='afk', mode_epoch=1)
            self.assertTrue(cancel_event.is_set())
            self.control.update(mode='human', mode_epoch=2)
            self.assertTrue(cancel_event.is_set())
            raise Denied('Cancelled at dispatch')

        self.runtime.broker.call.side_effect = refresh_then_dispatch
        with self.assertRaisesRegex(Denied, 'Cancelled at dispatch'):
            self.runtime.call('a' * 32, 'chrome.action', {})

    def test_emergency_revokes_bridge_and_stops_manager(self):
        self.runtime.permissions.desktop = True
        self.runtime.stop()
        self.assertFalse(self.runtime.permissions.desktop)
        self.assertTrue(self.runtime.permissions.halted.is_set())
        self.runtime.manager.emergency_stop.assert_called_once()

    @unittest.skipUnless(os.name == 'nt', 'Windows authenticated pipe required')
    def test_fresh_clients_share_manager_and_owner_controls_are_absent(self):
        self.runtime.start_pipe()
        self.addCleanup(self.runtime.listener.close)
        self.addCleanup(self.runtime.closed.set)
        self.runtime.manager.call.return_value = {'mode': 'afk', 'workers': []}
        for _ in range(3):
            client = ControllerClient(self.runtime.store.directory)
            self.assertEqual(client.request('portfolio_status')['mode'], 'afk')
            with self.assertRaises(RuntimeError):
                client.request('portfolio_resolve_request', {'decision': 'approve'})
            client.close()
        self.assertEqual(self.runtime.manager.call.call_count, 3)

    @unittest.skipUnless(os.name == 'nt', 'Windows authenticated pipe required')
    def test_fresh_cli_processes_claim_separate_projects_and_preserve_login_request(self):
        from portfolio_manager.coordinator import Coordinator
        from portfolio_manager.integration import ManagerHost
        from portfolio_manager.tests.test_runner import _record

        local = self.runtime.store.directory.parent
        repo = local / 'fictional-repo'
        for project in ('FAKE-001', 'FAKE-002'):
            _record(repo, project)
        database = local / 'manager' / 'coordinator.sqlite3'
        manager = ManagerHost.__new__(ManagerHost)
        manager.coordinator = Coordinator(repo, database)
        manager.coordinator.set_mode('afk')
        self.runtime.manager = manager
        self.runtime.status = lambda: {'controller_ready': True}
        self.runtime.start_pipe()
        self.addCleanup(self.runtime.listener.close)
        self.addCleanup(self.runtime.closed.set)

        def cli(action, arguments=None):
            command = [sys.executable, '-m', 'portfolio_manager', action]
            if arguments is not None:
                command.extend(['--arguments', json.dumps(arguments)])
            result = subprocess.run(command, cwd=APP.parents[1], timeout=12, check=True,
                                    capture_output=True, env={**os.environ, 'LOCALAPPDATA': str(local)})
            return json.loads(result.stdout)

        a = cli('register', {'folder': 'demo'})
        b = cli('register', {'folder': 'business_portfolio/niches'})
        key_a = {'worker_id': a['id'], 'worker_key': a['worker_key']}
        key_b = {'worker_id': b['id'], 'worker_key': b['worker_key']}
        one = cli('claim', key_a)
        two = cli('claim', key_b)
        with self.assertRaises(subprocess.CalledProcessError):
            cli('claim', {**key_a, 'worker_key': b['worker_key']})
        self.assertNotEqual(one['project_id'], two['project_id'])
        self.assertEqual(cli('status')['mode'], 'afk')
        waiting = cli('request_human', {**key_a, 'lease_token': one['lease_token'],
                       'kind': 'login', 'action': 'Fictional account sign-in',
                       'reason': 'Test manual handoff', 'scope': 'Fictional project only'})
        restarted = Coordinator(repo, database)
        self.assertEqual(restarted.snapshot()['requests'][0]['id'], waiting['id'])
        with self.assertRaises(ValueError):
            restarted.resolve_request(waiting['id'], 'complete')
        restarted.set_mode('human')
        restarted.resolve_request(waiting['id'], 'complete')
        resumed = cli('claim', key_a)
        self.assertEqual(resumed['project_id'], one['project_id'])
        self.assertTrue(resumed['human_responses'])

    def test_single_dashboard_embeds_portfolio_and_computer_access(self):
        from PySide6.QtWidgets import QApplication
        from bridge.dashboard import Dashboard
        from portfolio_manager.coordinator import Coordinator
        from portfolio_manager.tests.test_runner import _record

        application = QApplication.instance() or QApplication([])
        local = self.runtime.store.directory.parent
        repo = local / 'fictional-repo'
        _record(repo, 'FAKE-001')
        manager = self.runtime.manager
        manager.coordinator = Coordinator(repo, local / 'manager' / 'coordinator.sqlite3')
        manager.supervisor.status.return_value = {}
        runtime = Mock()
        runtime.store = self.runtime.store
        runtime.permissions = self.runtime.permissions
        runtime.requests = []
        runtime.status.return_value = {'mcp_clients_connected': 0, 'chrome_connected': False,
                                       'full_browser_access': False, 'desktop_authorized': False,
                                       'stopped': False, 'active_tool': None, 'latest_action': 'Ready',
                                       'reasoning_state': 'Ready', 'pending_requests': 0}
        with patch('bridge.dashboard.Runtime', return_value=runtime) as runtime_factory:
            dashboard = Dashboard(self.runtime.store.directory, manager)
        try:
            application.processEvents()
            self.assertEqual(dashboard.windowTitle(), 'Portfolio Manager')
            self.assertEqual([dashboard.tabs.tabText(i) for i in range(dashboard.tabs.count())],
                             ['Portfolio', 'Computer Access'])
            runtime_factory.assert_called_once()
            runtime.start_pipe.assert_called_once()
            manager.restore.assert_called_once()
        finally:
            dashboard.explicit_quit = True
            dashboard.close()
            application.processEvents()
        manager.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
