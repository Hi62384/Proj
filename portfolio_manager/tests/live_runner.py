"""Opt-in disposable official runtime check. No project or account writes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import threading

from portfolio_autopilot.codex_relay.codex import Codex
from portfolio_autopilot.codex_relay.diagnostics import RelayError, sanitize
from portfolio_manager.runner import IsolatedWorkspace, OfficialExecutor
from portfolio_manager.tests.test_runner import _record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inference', action='store_true', help='Run one synthetic ChatGPT turn after successful preflight.')
    parser.add_argument('--native', action='store_true', help='Check the native Windows backend instead of the provisioned Relay backend.')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='portfolio-manager-runtime-check-') as temp:
        base = Path(temp)
        repo = base / 'repo'
        private = repo / 'business_portfolio' / '.local' / 'portfolio-manager'
        private.mkdir(parents=True)
        project = _record(repo, 'FAKE-001')
        expected = 'PORTFOLIO MANAGER FICTIONAL CHECK.'
        claim = {
            'project_id': 'FAKE-001', 'task_id': 'prepare',
            'record_path': project.relative_to(repo).as_posix(),
            'record_sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
            'task': {'id': 'prepare', 'title': 'Fictional workspace smoke check',
                     'criteria': f'Write only this exact sentence in result.md: {expected}'},
        }
        stopped = threading.Event()
        staged = IsolatedWorkspace(repo, private, claim, stopped)
        executor = OfficialExecutor(runtime_base=base, prefer_wsl=not args.native)
        try:
            with executor.session(staged) as config:
                info = Codex(config).doctor()
            print(json.dumps({'preflight': 'passed', 'mode': info.get('mode'),
                              'profile': info.get('profile'), 'version': info.get('version'),
                              'authentication': info.get('authentication')}), flush=True)
        except RelayError as error:
            print(json.dumps({'preflight': 'blocked', 'category': error.category, 'stage': error.stage,
                              'explanation': error.explanation, 'detail': sanitize(error.detail), 'action': error.action}))
            return 2
        except (RuntimeError, ValueError, OSError) as error:
            print(json.dumps({'preflight': 'blocked', 'error': sanitize(error)}))
            return 2
        if args.inference:
            result = None
            events = []
            def capture_event(kind, detail):
                if kind in ('WORKSPACE_REQUEST', 'WORKSPACE_DENIED', 'POLICY_DENIED'):
                    events.append({'kind': kind, 'detail': sanitize(detail)[:300]})
            try:
                result = executor.run(claim, staged, stopped, capture_event, lambda _: None)
                if result.get('kind') != 'result':
                    print(json.dumps({'inference': 'blocked', 'response_kind': result.get('kind'),
                                      'summary': sanitize(result.get('summary', ''))[:500],
                                      'question': sanitize(result.get('question', ''))[:500], 'events': events}))
                    return 3
                evidence = staged.evidence('result.md')
                if (staged.root / 'result.md').read_text(encoding='utf-8').strip() != expected:
                    raise RuntimeError('The fictional artifact failed the exact expected-content check.')
                print(json.dumps({'inference': 'passed', 'verified_artifact': True, 'sha256': evidence['sha256']}))
            except (RuntimeError, ValueError, OSError) as error:
                failure = {'inference': 'blocked', 'error': sanitize(error)}
                if isinstance(result, dict):
                    failure['response_kind'] = result.get('kind')
                    failure['summary'] = sanitize(result.get('summary', ''))[:500]
                failure['events'] = events
                print(json.dumps(failure))
                return 3
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
