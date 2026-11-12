"""Opt-in fictional live Codex Stop check; uses ChatGPT inference and temporary state."""
import json
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path.cwd() / 'apps' / 'codex_desktop_assistant'))
from assistant.permissions import Permissions
from bridge.runtime import Runtime
from portfolio_autopilot.codex_relay.codex import Codex
from portfolio_manager.coordinator import Coordinator
from portfolio_manager.integration import ManagerHost
from portfolio_manager.runner import OfficialExecutor, Supervisor
from portfolio_manager.tests.test_runner import _record

def main():
    with tempfile.TemporaryDirectory(prefix='portfolio-live-stop-') as temp:
        base = Path(temp)
        repo = base / 'repo'
        _record(repo, 'FAKE-001')
        coordinator = Coordinator(repo)
        worker = coordinator.register('demo', kind='background')
        codex_instances = []
        def factory(config):
            instance = Codex(config)
            codex_instances.append(instance)
            return instance
        executor = OfficialExecutor(codex_factory=factory, runtime_base=base)
        supervisor = Supervisor(coordinator, executor, poll_seconds=.1)
        host = ManagerHost.__new__(ManagerHost)
        host.coordinator, host.supervisor = coordinator, supervisor
        runtime = Runtime.__new__(Runtime)
        runtime.permissions = Permissions()
        runtime.permissions.resume('fictional-owner')
        runtime.manager = host
        runtime.inflight = {}
        runtime.requests = []
        runtime.reference_queries = set()
        runtime.broker = Mock()
        runtime.store = Mock()
        runtime.emit = Mock()
        try:
            supervisor.start(worker['id'])
            deadline = time.monotonic() + 100
            while time.monotonic() < deadline:
                if codex_instances and codex_instances[0].turn_id:
                    break
                status = supervisor.status().get(worker['id'], {})
                if status.get('state') in ('blocked', 'stopped'):
                    raise RuntimeError('Worker stopped before the live turn: ' + status.get('detail', ''))
                time.sleep(.05)
            else:
                raise TimeoutError('No live turn began before the deadline')
            result = runtime.stop('Fictional acceptance stop')
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if supervisor.status().get(worker['id'], {}).get('state') == 'stopped':
                    break
                time.sleep(.05)
            state = coordinator.snapshot()
            project = next(item for item in state['projects'] if item['id'] == 'FAKE-001')
            assert result['stopped'] and not result['needs_review']
            assert state['stopped'] and state['emergency']
            assert project['milestones'][0]['status'] == 'reconcile'
            assert supervisor.status()[worker['id']]['state'] == 'stopped'
            assert runtime.permissions.halted.is_set()
            recovered = Coordinator(repo)
            recovered.recover_controller()
            recovered_project = next(item for item in recovered.snapshot()['projects'] if item['id'] == 'FAKE-001')
            assert recovered_project['milestones'][0]['status'] == 'reconcile'
            assert recovered.claim(worker['id']) is None
            print(json.dumps({'real_turn_started': True, 'stop_handler': 'passed',
                              'worker': 'stopped', 'task': 'reconcile', 'recovery': 'no automatic replay',
                              'desktop_access': 'revoked'}), flush=True)
        finally:
            supervisor.close()


if __name__ == '__main__':
    main()
