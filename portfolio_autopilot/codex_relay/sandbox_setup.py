"""Explicitly opt-in administrator provisioning through the official app-server API."""
import argparse
import json
import os
import queue
import shutil
import time

from .__main__ import InstanceLock
from .codex import Codex, Rpc, binary
from .config import Config
from .diagnostics import RelayError, record


def provision(config, approved=False, rpc_factory=Rpc):
    if not approved:
        raise ValueError('Explicit owner approval is required for sandbox accounts, ACL and firewall changes')
    if os.name != 'nt':
        raise ValueError('Windows sandbox provisioning requires Windows')
    path = config.data_dir / 'config.json'
    if path.is_file():
        backup = config.data_dir / 'repair-backups' / ('pre-sandbox-setup-' + str(time.time_ns()))
        backup.mkdir(parents=True)
        shutil.copy2(path, backup / 'config.json')
    rpc = rpc_factory(config, setup_only=True)
    try:
        response = rpc.request('windowsSandbox/setupStart', {'mode': 'elevated', 'cwd': str(config.workspace)}, timeout=20)
        if response.get('started') is not True:
            raise RelayError('sandbox.setup', 'windowsSandbox/setupStart', 'Sandbox setup did not start.')
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            try:
                event = rpc.events.get(timeout=.3)
            except queue.Empty:
                continue
            if event.get('method') == 'windowsSandbox/setupCompleted':
                result = event.get('params', {})
                if result.get('mode') != 'elevated' or result.get('success') is not True:
                    raise RelayError('sandbox.setup', 'windowsSandbox/setupCompleted', 'Elevated sandbox setup failed or was declined.',
                                     result.get('error', ''), 'Inspect diagnostics; the relay will not run without a verified sandbox.')
                config.windows_sandbox = 'elevated'
                config.codex_binary = binary(config)  # Pin the executable used for provisioning.
                config.save()
                return {'setup': 'completed', 'mode': 'elevated', 'inference_started': False}
            if event.get('method') == 'relay/disconnected':
                raise RelayError('transport', 'sandbox setup', 'App-server disconnected during setup.')
        raise RelayError('timeout', 'sandbox setup', 'Administrator setup did not finish within five minutes.',
                         action='Review any outstanding UAC prompt. Do not retry until its outcome is known.')
    except RelayError as error:
        record(config.data_dir, error)
        raise
    finally:
        rpc.close()


def main():
    parser = argparse.ArgumentParser(description='Provision the isolated relay’s elevated Windows sandbox')
    parser.add_argument('--approve-admin-changes', action='store_true',
                        help='Approve dedicated sandbox accounts, filesystem permissions, firewall rules and a Windows UAC prompt')
    parser.add_argument('--data-dir')
    args = parser.parse_args()
    if not args.approve_admin_changes:
        parser.error('--approve-admin-changes is required. This changes Windows security configuration; task commands stay unprivileged.')
    config = Config.load(args.data_dir)
    with InstanceLock(config.data_dir):
        print('Starting owner-approved Windows sandbox provisioning. Review the Windows administrator/UAC prompt.', flush=True)
        print(json.dumps(provision(config, approved=True)))
        print(json.dumps(Codex(config).doctor(), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1)
