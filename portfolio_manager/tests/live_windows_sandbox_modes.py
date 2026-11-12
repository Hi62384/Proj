"""Opt-in native Codex sandbox preflight; no inference or project changes."""
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
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=('unelevated','elevated','mxc'),required=True)
    parser.add_argument('--binary',help='Optional existing absolute native executable for a test-only preflight')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='portfolio-native-mode-') as folder:
        base=Path(folder);repo=base/'repo';private=repo/'business_portfolio'/'.local'/'portfolio-manager'
        private.mkdir(parents=True)
        project=_record(repo,'FAKE-001')
        claim={'project_id':'FAKE-001','task_id':'prepare','record_path':project.relative_to(repo).as_posix(),
               'record_sha256':hashlib.sha256(project.read_bytes()).hexdigest()}
        workspace=IsolatedWorkspace(repo,private,claim,threading.Event())
        executor=OfficialExecutor(runtime_base=base,prefer_wsl=False)
        config=executor._config(workspace);config.windows_sandbox=args.mode
        if args.binary:
            candidate=Path(args.binary)
            if not candidate.is_absolute() or not candidate.is_file() or candidate.suffix.lower()!='.exe':
                raise ValueError('The test executable must be an existing absolute Windows executable')
            config.codex_binary=str(candidate)
        config.validate()
        try:
            result=Codex(config).doctor()
            print(json.dumps({'mode':args.mode,'result':'passed','profile':result.get('profile'),
                              'security_checks':result.get('security_checks',{})}))
        except RelayError as error:
            print(json.dumps({'mode':args.mode,'result':'blocked','category':error.category,
                              'stage':error.stage,'explanation':sanitize(error.explanation),
                              'detail':sanitize(error.detail)[:1000]}))
            return 1
        finally:
            (config.data_dir/'codex-home'/'auth.json').unlink(missing_ok=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
