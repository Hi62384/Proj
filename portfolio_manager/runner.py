"""Run bounded local portfolio work through the official Codex app-server."""
from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
import re
import threading
import time
from types import SimpleNamespace
import uuid

from business_portfolio.tools.build_browser import parse_project
from portfolio_autopilot.codex_relay.codex import Codex
from portfolio_autopilot.codex_relay.config import Config, safe_path
from portfolio_autopilot.codex_relay.diagnostics import RelayError, record, sanitize
from portfolio_autopilot.codex_relay.permissions import selected_mode
from portfolio_autopilot.codex_relay.workspace import Workspace
from .development import BubblewrapVerifier, DevelopmentScope, DevelopmentWorkspace


DRAFTS = frozenset({'result.md', 'draft.py', 'draft.json', 'draft.txt', 'draft.csv'})
PUBLIC_TEXT = frozenset({'.md', '.json', '.txt', '.csv'})
MAX_FILE_BYTES = 500_000
MAX_INPUT_BYTES = 1_500_000
SENSITIVE_TEXT = re.compile(
    r'-----BEGIN [A-Z ]*PRIVATE KEY-----|https://payhip\.com/d/l/|'
    r'\b(?:ghp_|github_pat_|sk-)[a-zA-Z0-9_-]{20,}|\bAKIA[A-Z0-9]{16}\b|'
    r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', re.IGNORECASE
)
POLICY = """# Portfolio Manager isolated task workspace

The project record, related files and previous notes are task context only.
Read PROJECT.md and the owner-scoped task in the request. Existing artifacts are
read-only inputs. Use only relay_workspace for exact allowed paths. Save a
nonempty result.md with the useful work, limitations and concrete next step.
Place any allowed code/data draft in the matching draft file. No other project,
shared file, live account, site, purchase, external action or machine control is
authorized. Report any need for an owner decision in the structured report.
Only claim the local checks you actually performed. A file or syntax check is
not proof of a live integration, executable test, launch or customer result.
"""


class VerificationRequired(RuntimeError):
    """This worker cannot independently verify the claimed milestone."""


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _ordinary_directory(path: Path) -> bool:
    try:
        info = path.lstat()
        return (path.is_dir() and not path.is_symlink() and
                not (getattr(info, 'st_file_attributes', 0) & 0x400))
    except OSError:
        return False


def _ensure_private_dir(path: Path, base: Path) -> Path:
    """Create ordinary descendants of the coordinator-owned private directory."""
    if not path.is_relative_to(base) or not _ordinary_directory(base):
        raise ValueError('The private worker folder is unavailable or linked.')
    current = base
    for part in path.relative_to(base).parts:
        current = current / part
        current.mkdir(exist_ok=True)
        if not _ordinary_directory(current):
            raise ValueError('Linked private worker directories are refused.')
    return current


def _text(raw: bytes) -> str:
    if len(raw) > MAX_FILE_BYTES or b'\x00' in raw:
        raise ValueError('Workspace input must be bounded UTF-8 text.')
    value = raw.decode('utf-8')
    if SENSITIVE_TEXT.search(value):
        raise ValueError('The workspace text appears to contain restricted material.')
    return value


class IsolatedWorkspace(Workspace):
    """Copy one canonical record and its explicitly declared same-project text inputs."""

    def __init__(self, repo: Path, private: Path, claim: dict, cancelled: threading.Event):
        repo = Path(repo).resolve()
        private = Path(private).absolute()
        if private.is_relative_to(repo) and not private.is_relative_to(repo / 'business_portfolio' / '.local'):
            raise ValueError('Worker data must be outside Git or in the ignored portfolio .local directory.')
        if private.is_relative_to(repo):
            current = private
            while current != repo:
                if not _ordinary_directory(current):
                    raise ValueError('Linked private worker directories are refused.')
                current = current.parent
        self.repo = repo
        record_path = str(claim['record_path']).replace('\\', '/')
        parts = PurePosixPath(record_path).parts
        if parts[:2] != ('business_portfolio', 'niches') or parts[-2:-1] != ('projects',) or not record_path.endswith('.md'):
            raise ValueError('Only canonical portfolio records can be staged.')
        record_file = safe_path(repo, record_path)
        if record_file.stat().st_size > MAX_FILE_BYTES:
            raise ValueError('The canonical record exceeds the input size limit.')
        record_bytes = record_file.read_bytes()
        if _digest(record_bytes) != claim['record_sha256']:
            raise ValueError('The project record changed after the claim. Review it before resuming.')
        record_text = _text(record_bytes)
        meta, _ = parse_project(record_text, record_path)
        project_id = claim['project_id']
        if not re.fullmatch(r'[A-Z][A-Z0-9_-]*-[0-9]{3,}', project_id) or meta.get('id') != project_id:
            raise ValueError('The claimed project identity no longer matches the record.')

        self.run_dir = _ensure_private_dir(private / 'worker-runs' / project_id / uuid.uuid4().hex, private)
        root = _ensure_private_dir(self.run_dir / 'workspace', private)
        (root / 'AGENTS.md').write_text(POLICY, encoding='utf-8')
        (root / 'PROJECT.md').write_bytes(record_bytes)
        paths = {'PROJECT.md', *DRAFTS}
        total = len(record_bytes)
        for result in meta.get('public_results', []):
            name = result.get('path') if isinstance(result, dict) else None
            if not isinstance(name, str):
                continue
            result_path = PurePosixPath(name)
            if (result_path.parts[:2] != ('results', claim['project_id']) or
                    result_path.suffix.lower() not in PUBLIC_TEXT):
                continue
            try:
                source = safe_path(repo, 'business_portfolio/' + name)
                if source.stat().st_size > MAX_FILE_BYTES:
                    continue
                raw = source.read_bytes()
                _text(raw)
                if total + len(raw) > MAX_INPUT_BYTES:
                    break
            except (OSError, ValueError):
                continue
            target = safe_path(root, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            total += len(raw)
            paths.add(name)
        prior_root = private / 'worker-runs' / project_id
        for index, evidence in enumerate(claim.get('prior_artifacts', [])[:3], 1):
            if not isinstance(evidence, dict):
                continue
            source_path = Path(str(evidence.get('path', '')))
            if (not source_path.is_absolute() or not source_path.is_relative_to(prior_root) or
                    source_path.suffix.lower() not in PUBLIC_TEXT | {'.py'} or
                    not _ordinary_directory(prior_root)):
                continue
            try:
                source = safe_path(prior_root, source_path.relative_to(prior_root).as_posix())
                if source.stat().st_size > MAX_FILE_BYTES:
                    continue
                raw = source.read_bytes()
                if _digest(raw) != evidence.get('sha256') or total + len(raw) > MAX_INPUT_BYTES:
                    continue
                _text(raw)
            except (OSError, ValueError):
                continue
            name = f'prior-{index}{source_path.suffix.lower()}'
            (root / name).write_bytes(raw)
            total += len(raw)
            paths.add(name)
        super().__init__(root, paths, lambda: not cancelled.is_set(), lambda *_: None, self.run_dir / 'backups')

    def call(self, args):
        if isinstance(args, dict) and args.get('operation') == 'write':
            if args.get('path') not in DRAFTS:
                raise ValueError('The canonical record and copied inputs are read-only.')
            content = args.get('content')
            if not isinstance(content, str):
                raise ValueError('A draft must contain text.')
            _text(content.encode('utf-8'))
        return super().call(args)

    def evidence(self, name: str) -> dict:
        if name not in DRAFTS:
            raise VerificationRequired('The milestone requests an unsupported output file.')
        artifact = safe_path(self.root, name)
        if not artifact.is_file() or artifact.stat().st_size > MAX_FILE_BYTES:
            raise VerificationRequired('The expected local result is missing or exceeds the file limit.')
        raw = artifact.read_bytes()
        if not _text(raw).strip():
            raise VerificationRequired('The expected local result is empty.')
        try:
            if name.endswith('.json'):
                json.loads(raw)
            if name.endswith('.py'):
                compile(raw, name, 'exec', dont_inherit=True)
        except (ValueError, SyntaxError, RecursionError) as error:
            raise VerificationRequired('The local draft did not pass the syntax check.') from error
        return {'kind': 'verified_artifact', 'path': str(artifact), 'sha256': _digest(raw)}


class OfficialExecutor:
    """Adapt the Relay's restricted official Codex transport without sharing its state."""

    def __init__(self, codex_factory=Codex, *, runtime_base=None, prefer_wsl=True):
        self._codex_factory = codex_factory
        self._runtime_base = runtime_base
        self._prefer_wsl = prefer_wsl

    def _config(self, workspace: IsolatedWorkspace | DevelopmentWorkspace) -> Config:
        # The existing Relay's choice of Windows sandbox is read, never rewritten.
        # Separate, per-run homes prevent concurrent permission configuration races.
        mode = selected_mode(Config())
        if self._runtime_base is not None:
            base = Path(self._runtime_base).absolute()
        else:
            local = os.environ.get('LOCALAPPDATA')
            base = Path(local).absolute() if local else Path.home()
        # Authentication is held outside the repository, including ignored folders.
        candidate = base / 'PortfolioManager' / 'worker-runtime' / workspace.run_dir.name
        if candidate.resolve().is_relative_to(workspace.repo):
            raise ValueError('The Codex runtime directory must be outside the repository.')
        runtime = _ensure_private_dir(candidate, base)
        return Config(workspace=workspace.root, data_dir=runtime, windows_sandbox=mode)

    @contextmanager
    def session(self, workspace: IsolatedWorkspace | DevelopmentWorkspace):
        from . import runner_wsl

        config = self._config(workspace)
        locations = runner_wsl.configure(config) if self._prefer_wsl and os.name == 'nt' else None
        config.validate()
        failed = False
        try:
            if locations:
                runner_wsl.prepare(config, locations)
            yield config
        except BaseException:
            failed = True
            raise
        finally:
            try:
                if locations:
                    runner_wsl.remove_login(config)
                else:
                    # Remove only the disposable login after the app-server exits.
                    (config.data_dir / 'codex-home' / 'auth.json').unlink(missing_ok=True)
            except (OSError, RuntimeError, ValueError) as error:
                record(config.data_dir, error, operation='disposable login cleanup')
                if not failed:
                    raise RuntimeError('The disposable runtime could not confirm login cleanup.') from error

    def run(self, claim, workspace, cancelled, emit, save_session):
        if cancelled.is_set():
            raise InterruptedError('Stopped before starting Codex.')
        with self.session(workspace) as config:
            return self._run(config, claim, workspace, cancelled, emit, save_session)

    def _run(self, config, claim, workspace, cancelled, emit, save_session):
        task = claim['task']
        responses = [
            {key: sanitize(response.get(key, ''))[:600]
             for key in ('status', 'action', 'scope', 'after')}
            for response in claim.get('human_responses', [])
        ]
        prompt = json.dumps({
            'project_id': claim['project_id'], 'title': sanitize(task['title'])[:500],
            'criteria': sanitize(task['criteria'])[:4_000],
            'previous_checkpoint': sanitize(claim.get('checkpoint', ''))[:12_000],
            'owner_responses': responses,
            'scope': 'Complete one bounded local preparation increment. Read AGENTS.md and PROJECT.md in the isolated workspace. '
                     'Save result.md and any permitted draft. Independently check the result of a reported manual step using '
                     'the evidence available in this workspace. Report an unmet criterion or owner dependency truthfully.',
        }, ensure_ascii=False)
        # Candidate paths do not need filesystem grants or model-visible command access.
        restricted = SimpleNamespace(paths=tuple(sorted(workspace.paths - DRAFTS)), call=workspace.call)
        return self._turn(config, prompt, restricted, cancelled, emit, save_session)

    def run_development(self, claim, workspace, verifier, cancelled, emit, save_session):
        """Run an explicitly host-scoped task and return private verification evidence."""
        if not isinstance(workspace, DevelopmentWorkspace) or workspace.cancelled is not cancelled:
            raise ValueError('Development requires an explicit host-scoped workspace.')
        if cancelled.is_set():
            raise InterruptedError('Stopped before starting development.')
        prompt = json.dumps({
            'project_id': claim['project_id'], 'title': sanitize(claim['task']['title'])[:500],
            'criteria': sanitize(claim['task']['criteria'])[:4_000],
            'editable_paths': sorted(workspace.scope.edit_paths),
            'scope': 'Read AGENTS.md and PROJECT.md and implement the requested changes using only relay_workspace. '
                     'You may create bounded source files inside the selected folder by writing with sha256=new. '
                     'Keep the trusted tests and other input files read-only. The host will run the trusted tests.',
        }, ensure_ascii=False)
        existing = {name for name, digest in workspace.original.items() if digest != 'new'}
        restricted = SimpleNamespace(paths=tuple(sorted(existing)), call=workspace.call)
        with self.session(workspace) as config:
            if verifier is None:
                verifier = BubblewrapVerifier(config.wsl_distribution if config.execution_backend == 'wsl' else None)
            # Reject an unsupported host before making a model call. A candidate
            # cannot be accepted without a sandbox capable of running its tests.
            if isinstance(verifier, BubblewrapVerifier):
                verifier._prefix()
            response = self._turn(config, prompt, restricted, cancelled, emit, save_session)
        if cancelled.is_set():
            raise InterruptedError('Stopped before verifying development.')
        return response, workspace.verify(verifier) if response['kind'] == 'result' else None

    def _turn(self, config, prompt, restricted, cancelled, emit, save_session):
        codex = self._codex_factory(config)
        done = threading.Event()

        def interrupt_on_stop():
            while not done.wait(.1):
                if cancelled.is_set():
                    codex.cancel()
                    return

        interrupter = threading.Thread(target=interrupt_on_stop, daemon=True)
        interrupter.start()
        try:
            if cancelled.is_set():
                raise InterruptedError('Stopped before starting Codex.')
            return codex.run({}, prompt, restricted, cancelled, emit, save_session)
        finally:
            done.set()
            interrupter.join(timeout=1)


class Supervisor:
    """Continuously claim eligible work while a registered background worker runs."""

    def __init__(self, coordinator, executor=None, *, poll_seconds=1.0, turn_timeout=1800):
        self.coordinator = coordinator
        self.executor = executor if executor is not None else OfficialExecutor()
        self.poll_seconds = poll_seconds
        self.turn_timeout = turn_timeout
        self._lock = threading.RLock()
        self._running = {}
        self._status = {}
        self._closed = False

    def status(self):
        with self._lock:
            return {key: dict(value) for key, value in self._status.items()}

    def _describe(self, worker_id, state, detail=''):
        with self._lock:
            self._status[worker_id] = {'state': state, 'detail': sanitize(detail)[:900]}

    def start(self, worker_id):
        with self._lock:
            if self._closed:
                raise RuntimeError('The worker supervisor has shut down.')
            running = self._running.get(worker_id)
            if running and running[0].is_alive():
                if running[1].is_set():
                    raise RuntimeError('The worker is still stopping. Try again after it has stopped.')
                return
            self.coordinator.set_worker_state(worker_id, 'running')
            stop = threading.Event()
            thread = threading.Thread(target=self._loop, args=(worker_id, stop), daemon=True,
                                      name='portfolio-worker-' + str(worker_id)[:10])
            self._running[worker_id] = (thread, stop)
            thread.start()

    def restore(self):
        snapshot = self.coordinator.snapshot()
        if snapshot.get('stopped') or snapshot.get('emergency'):
            return
        for worker in snapshot.get('workers', []):
            if (worker.get('kind') == 'background' and worker.get('state') == 'running'
                    and worker.get('project_id') is None):
                self.start(worker['id'])

    def _signal(self, worker_id=None):
        with self._lock:
            for key, (_, event) in self._running.items():
                if worker_id is None or key == worker_id:
                    event.set()

    def stop(self, worker_id):
        with self._lock:
            self._signal(worker_id)
            self.coordinator.set_worker_state(worker_id, 'stopped')

    def pause(self, worker_id):
        with self._lock:
            self._signal(worker_id)
            self.coordinator.set_worker_state(worker_id, 'paused')

    def stop_all(self, *, emergency=False):
        with self._lock:
            self._signal()
            return self.coordinator.stop_all(emergency=emergency)

    def close(self):
        with self._lock:
            self._closed = True
            threads = [thread for thread, _ in self._running.values()]
            self._signal()
        deadline = time.monotonic() + 5
        for thread in threads:
            thread.join(max(0, deadline - time.monotonic()))

    def _loop(self, worker_id, stop):
        blocked = False
        while not stop.is_set():
            try:
                claim = self.coordinator.claim(worker_id)
                if not claim:
                    self._describe(worker_id, 'idle', 'Waiting for eligible local work.')
                    stop.wait(self.poll_seconds)
                    continue
                self._describe(worker_id, 'working', claim['task']['title'])
                if not self._run_turn(worker_id, claim, stop):
                    blocked = not stop.is_set()
                    break
            except Exception as error:
                self._describe(worker_id, 'blocked', error)
                blocked = not stop.is_set()
                break
        if blocked:
            try:
                self.coordinator.set_worker_state(worker_id, 'paused')
            except (RuntimeError, ValueError, KeyError):
                pass
        if stop.is_set():
            self._describe(worker_id, 'stopped')

    def _run_turn(self, worker_id, claim, stop):
        lease = claim['lease_token']
        cancelled = threading.Event()
        finished = threading.Event()
        session_ref = None
        timed_out = threading.Event()

        def watch():
            lease_seconds = getattr(self.coordinator, 'lease_seconds', 120)
            heartbeat = min(2.0, lease_seconds / 4)
            next_heartbeat = time.monotonic()
            deadline = time.monotonic() + self.turn_timeout
            while not finished.wait(.1):
                now = time.monotonic()
                if stop.is_set() or now >= deadline:
                    if now >= deadline:
                        timed_out.set()
                    cancelled.set()
                    return
                if now >= next_heartbeat:
                    try:
                        active = self.coordinator.heartbeat(worker_id, lease)
                    except Exception:
                        active = False
                    if not active:
                        cancelled.set()
                        return
                    next_heartbeat = now + heartbeat

        monitor = threading.Thread(target=watch, daemon=True, name='portfolio-lease-heartbeat')
        monitor.start()
        try:
            task = claim['task']
            verification = task.get('verification')
            if not verification and (task.get('provisional') or task.get('id') == 'next-action'):
                verification = {'kind': 'artifact', 'name': 'result.md'}
            development = isinstance(verification, dict) and verification.get('kind') == 'development'
            if not development and (not isinstance(verification, dict) or verification.get('kind') != 'artifact' or
                                    verification.get('name') not in DRAFTS):
                raise VerificationRequired('This milestone needs a verification method the worker does not support.')
            if development:
                record = self.coordinator.guard_lease(worker_id, lease, lambda item: safe_path(
                    self.coordinator.repo, item['record_path']).read_bytes())
                private = self.coordinator.db_path.parent
                run_root = _ensure_private_dir(private / 'worker-runs' / claim['project_id'], private)
                scope = DevelopmentScope.discover(self.coordinator.repo, verification['folder'])
                workspace = DevelopmentWorkspace(self.coordinator.repo, run_root, scope, cancelled,
                                                 project_context=record, allow_new_files=True)
            else:
                workspace = IsolatedWorkspace(self.coordinator.repo, self.coordinator.db_path.parent, claim, cancelled)

            def save_session(value):
                nonlocal session_ref
                if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
                    raise ValueError('Invalid Codex session reference.')
                session_ref = value
                (workspace.run_dir / 'session.json').write_text(
                    json.dumps({'session_ref': value, 'project_id': claim['project_id'], 'task_id': claim['task_id']}),
                    encoding='utf-8')

            if stop.is_set() or cancelled.is_set():
                raise InterruptedError('Stopped before starting the task.')
            # Never persist raw reasoning or full tool/event transcripts in the coordinator.
            if development:
                response, development_evidence = self.executor.run_development(
                    claim, workspace, None, cancelled, lambda *_: None, save_session)
            else:
                response = self.executor.run(claim, workspace, cancelled, lambda *_: None, save_session)
            if stop.is_set() or cancelled.is_set():
                raise InterruptedError('The task stopped before its output was verified.')
            if response['kind'] in ('owner', 'question'):
                request = self.coordinator.request_human(
                    worker_id, lease, action='Review project dependency',
                    reason=sanitize(response.get('question') or response['summary'])[:1_000],
                    scope='This portfolio task only. No permission or payment is granted by recording this request.',
                    after='The task can be reassessed from its saved checkpoint.', kind='manual')
                if request.get('status') == 'manual_completed':
                    self._finish_if_current(worker_id, lease, 'blocked',
                                            'The previous response could not be verified from the available evidence.',
                                            session_ref)
                return True
            if response['kind'] != 'result':
                raise VerificationRequired('Codex returned an unrecognized result.')
            if development:
                if not development_evidence:
                    raise VerificationRequired('The development candidate has no verified test evidence.')
                self.coordinator.guard_lease(worker_id, lease, lambda _: development_evidence)
                self.coordinator.finish(
                    worker_id, lease, outcome='blocked', session_ref=session_ref, evidence=development_evidence,
                    summary='Verified development candidate awaiting review and integration: '
                            + development_evidence['path'] + ' SHA-256 ' + development_evidence['sha256'])
                return True
            evidence = self.coordinator.guard_lease(
                worker_id, lease, lambda _claim: workspace.evidence(verification['name']))
            self.coordinator.finish(
                worker_id, lease, outcome='completed',
                summary='Verified local artifact. ' + sanitize(response['summary'])[:850],
                evidence=evidence, session_ref=session_ref)
            return True
        except InterruptedError:
            reason = 'The worker reached its time limit.' if timed_out.is_set() else 'The worker was interrupted.'
            if timed_out.is_set():
                outcome = 'blocked'
            else:
                # A normal app shutdown can return unfinished local drafts to the
                # queue. Stop controls separately revoke the claim before reuse.
                outcome = 'retry' if self._closed else 'paused'
            self._finish_if_current(worker_id, lease, outcome, reason, session_ref)
            return not stop.is_set() and timed_out.is_set()
        except VerificationRequired as error:
            self._finish_if_current(worker_id, lease, 'blocked', str(error), session_ref)
            return True
        except RelayError as error:
            detail = str(error)
            if re.search(r'rate[ -]limit|usage limit|quota exceeded|\b429\b', error.detail, re.IGNORECASE):
                detail = 'Codex reported a usage or rate limit. Review the existing account before resuming this worker.'
            self._finish_if_current(worker_id, lease, 'blocked', detail, session_ref)
            # This is a runtime/account dependency, not a reason to attempt every project.
            self._describe(worker_id, 'blocked', detail)
            return False
        except Exception as error:
            self._finish_if_current(worker_id, lease, 'blocked', str(error), session_ref)
            self._describe(worker_id, 'blocked', error)
            return False
        finally:
            finished.set()
            monitor.join(timeout=2)

    def _finish_if_current(self, worker_id, lease, outcome, reason, session_ref):
        try:
            self.coordinator.finish(worker_id, lease, outcome=outcome,
                                    summary=sanitize(reason)[:950], session_ref=session_ref)
        except (RuntimeError, ValueError, KeyError):
            # An expired or revoked lease belongs to the coordinator's reconciliation path.
            pass
