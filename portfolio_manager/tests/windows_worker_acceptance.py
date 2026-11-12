"""Run bounded, synthetic Windows worker prerequisites; never starts a real worker.

The live modules create and remove their own temporary AppContainer profiles.
This runner uses no account credentials and deliberately reports NOT_READY even
when every synthetic prerequisite passes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from portfolio_manager.tests.windows_owned_process import OwnedCleanupUnconfirmed

_CASES = {
    'appserver_streams': (
        'portfolio_manager.tests.live_windows_isolation',
        ['--appserver-stdio-only'],
        ('Synthetic app-server initialized; restricted profile available: True',
         'Synthetic restricted command probe: passed',
         'Synthetic app-server: protocol streams worked; unlisted inheritable sentinel excluded'),
    ),
    'split_profiles': (
        'portfolio_manager.tests.live_windows_isolation',
        ['--namespace-only', '--protect-profile-root', '--protect-profile-parent',
         '--replace-parent-grant', '--split-layout', '--two-profiles'],
        ('writable runtime SQLite WAL create/reopen: passed',
         'file write: denied', 'file delete: denied', 'stage rename: denied',
         'parent rename: denied', 'writable runtime root rename: denied',
         'staging root DELETE: denied', 'profile parent DELETE_CHILD: denied',
         'staging root WRITE_DAC: denied', 'staging root WRITE_OWNER: denied',
         'profile parent WRITE_DAC: denied',
         'staged identity and trusted fixture: matched; wrong identity rejected',
         'Host verification: protected stage and content unchanged',
         'Separate test identity: unlisted inheritable sentinel excluded; host positive control passed',
         'Separate test identity: synthetic environment canary excluded; host positive control passed',
         'Separate test identity: staged read allowed; private runtime read and staged write denied',
         'Separate test identity: loopback connection blocked; host control passed'),
    ),
    'job_lifecycle': (
        'portfolio_manager.tests.live_windows_job_lifecycle', [],
        ('Synthetic job cancellation: parent and child exited after job closure',
         'Synthetic job memory limit: oversized allocation rejected'),
    ),
    'restricted_job_lifecycle': (
        'portfolio_manager.tests.live_windows_isolation', ['--appcontainer-job-only'],
        ('Restricted synthetic job: parent and child had AppContainer tokens and exited after job closure',
         'Restricted synthetic job memory limit: oversized allocation rejected'),
    ),
    'owned_timeout_cleanup': (
        'portfolio_manager.tests.live_windows_profile_recovery', [],
        ('Synthetic timeout recovery: owned process tree stopped and exact owned profiles released',
         'Synthetic controller crash: exact owned profile record survived and was safely cleaned'),
    ),
}

_REMAINING = (
    'trusted root provisioning and ACL verification',
    'reviewed Codex home and cwd startup support',
    'real app-server authentication and bounded model turn',
    'real Windows test verifier, process limits and descendant controls',
    'full cancellation, crash recovery and cleanup verification',
)


def classify(returncode, output, required):
    """Demand successful execution and every exact case marker."""
    forbidden = ('file write: allowed', 'file delete: allowed', 'stage rename: allowed',
                 'parent rename: allowed', 'Host verification: parent replacement was permitted')
    return (returncode == 0 and all(marker in output for marker in required)
            and not any(marker in output for marker in forbidden))


def run_cases(run=None, profile_factory=None):
    if os.name != 'nt':
        raise RuntimeError('Synthetic acceptance checks require Windows')
    if run is None:
        from portfolio_manager.tests.windows_owned_process import run_owned
        from portfolio_manager.tests.windows_profile_owner import OwnedProfiles
        run = run_owned
        if profile_factory is None:
            profile_factory = OwnedProfiles
    results = {}
    cases = list(_CASES.items())
    for index, (name, (module, arguments, markers)) in enumerate(cases):
        owner = None
        cleanup_safe = True
        try:
            case_arguments = list(arguments)
            if profile_factory is not None and module == 'portfolio_manager.tests.live_windows_isolation':
                owner = profile_factory()
                case_arguments.extend(['--owned-profile-id', owner.identifier])
            completed = run([sys.executable, '-u', '-m', module, *case_arguments],
                            capture_output=True, text=True, timeout=45, check=False)
            passed = classify(completed.returncode, completed.stdout, markers)
            results[name] = {'passed': passed, 'exit_code': completed.returncode,
                             'missing_markers': [marker for marker in markers if marker not in completed.stdout]}
            if not passed:
                results[name]['diagnostic'] = (completed.stderr or completed.stdout)[-700:]
        except subprocess.TimeoutExpired:
            results[name] = {'passed': False, 'error': 'synthetic probe timed out; owned process tree stopped'}
            for skipped, _ in cases[index + 1:]:
                results[skipped] = {'passed': False, 'error': 'skipped after timeout'}
            break
        except OwnedCleanupUnconfirmed as error:
            cleanup_safe = False
            results[name] = {'passed': False, 'error': 'owned cleanup unconfirmed: '+str(error)}
            if owner is not None:
                results[name]['owned_profile_id'] = owner.identifier
            for skipped, _ in cases[index + 1:]:
                results[skipped] = {'passed': False, 'error': 'skipped after unconfirmed cleanup'}
            break
        finally:
            if owner is not None and cleanup_safe:
                try:
                    owner.close()
                except (OSError, RuntimeError) as error:
                    results[name] = {'passed': False, 'error': 'owned profile cleanup failed: '+str(error)}
                    results[name]['owned_profile_id'] = owner.identifier
        if results[name].get('error', '').startswith('owned profile cleanup failed:'):
            for skipped, _ in cases[index + 1:]:
                results[skipped] = {'passed': False, 'error': 'skipped after profile cleanup failure'}
            break
    return {'status': 'not_ready', 'synthetic': results, 'remaining': list(_REMAINING)}


def main():
    result = run_cases()
    print(json.dumps(result, indent=2))
    return 0 if all(item['passed'] for item in result['synthetic'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
