"""Prepare and verify exact, owner-selected development files in a private copy."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import time

from portfolio_autopilot.codex_relay.config import safe_path
from portfolio_autopilot.codex_relay.workspace import Workspace


_TEXT_TYPES = {'.py', '.js', '.mjs', '.ts', '.tsx', '.css', '.html', '.md', '.json', '.toml', '.txt', '.csv'}
_RESTRICTED = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|https://payhip\.com/d/l/|'
                         r'\b(?:ghp_|github_pat_|sk-)[A-Za-z0-9_-]{20,}|\bAKIA[A-Z0-9]{16}\b|'
                         r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', re.I)
_MAX_FILE = 500_000
_MAX_TOTAL = 8_000_000
_MAX_FILES = 120
_POLICY = """# Scoped development

Use relay_workspace to inspect and edit the exact files provided for this task.
Only the listed editable paths may change. Tests and other inputs are read-only.
The host runs the approved tests after the turn. Do not use a shell, request
broader access, contact external systems, or claim that the tests ran yourself.
"""


class DevelopmentError(RuntimeError):
    """A development candidate cannot safely proceed or be verified."""


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _text(data):
    if len(data) > _MAX_FILE or b'\0' in data:
        raise DevelopmentError('A development input exceeds the text-file limit.')
    try:
        value = data.decode('utf-8')
    except UnicodeError as exc:
        raise DevelopmentError('Development inputs must use UTF-8.') from exc
    if _RESTRICTED.search(value):
        raise DevelopmentError('A development input appears to contain restricted material.')
    return value


def _ordinary(path):
    info = path.lstat()
    return not path.is_symlink() and not (getattr(info, 'st_file_attributes', 0) & 0x400)


def _scoped_name(name):
    if not isinstance(name, str) or '\\' in name:
        raise DevelopmentError('Use repository-relative paths with forward slashes.')
    value = PurePosixPath(name)
    if (str(value) != name or value.is_absolute() or len(value.parts) < 2 or
            value.parts[0].casefold() in {'outputs', 'releases', 'private', 'accounts'} or
            any(part.startswith('.') for part in value.parts) or
            value.name.casefold() == 'agents.md' or value.suffix.lower() not in _TEXT_TYPES):
        raise DevelopmentError('The file is outside the supported development scope.')
    return value


@dataclass(frozen=True)
class DevelopmentScope:
    """Host-approved inputs. File content or model output cannot grant this scope."""

    folder: str
    read_paths: tuple[str, ...]
    edit_paths: tuple[str, ...]
    test_paths: tuple[str, ...]

    def validate(self):
        folder = PurePosixPath(self.folder)
        if not folder.parts or folder.is_absolute() or str(folder) != self.folder or '..' in folder.parts:
            raise DevelopmentError('Choose a specific repository folder for development.')
        if not self.edit_paths or not self.test_paths:
            raise DevelopmentError('Development requires explicit editable files and trusted tests.')
        paths = {*self.read_paths, *self.edit_paths, *self.test_paths}
        if len(paths) > _MAX_FILES or len({p.casefold() for p in paths}) != len(paths):
            raise DevelopmentError('The development scope has too many or ambiguous paths.')
        if set(self.edit_paths) & set(self.test_paths):
            raise DevelopmentError('Trusted tests must be read-only during the development task.')
        for path in paths:
            if not _scoped_name(path).is_relative_to(folder):
                raise DevelopmentError('A development file is outside the approved folder.')
        if any(not re.fullmatch(r'test_[A-Za-z0-9_]+\.py', PurePosixPath(p).name) for p in self.test_paths):
            raise DevelopmentError('Only explicit Python unittest files are supported by this verifier.')
        return paths


class DevelopmentWorkspace(Workspace):
    """An isolated snapshot of a Git worktree plus exact, bounded new file paths."""

    def __init__(self, repo, private, scope, cancelled):
        self.repo = Path(repo).resolve(strict=True)
        private = Path(private).absolute()
        if not private.is_dir() or private.resolve(strict=True) != private or not _ordinary(private):
            raise DevelopmentError('The private development directory must be an ordinary absolute path.')
        if private.is_relative_to(self.repo) and not private.is_relative_to(self.repo / 'business_portfolio' / '.local'):
            raise DevelopmentError('Development runs must be outside Git or in the ignored portfolio state.')
        self.scope = scope
        self.cancelled = cancelled
        paths = scope.validate()
        def git(*args):
            return subprocess.check_output(['git', '--literal-pathspecs', '-C', str(self.repo), *args], timeout=10)
        if Path(os.fsdecode(git('rev-parse', '--show-toplevel').strip())).resolve() != self.repo:
            raise DevelopmentError('The development scope must be rooted in its Git checkout.')
        self.base = git('rev-parse', 'HEAD').decode('ascii').strip()
        tracked = set(git('ls-files', '-z', '--', scope.folder).decode('utf-8').rstrip('\0').split('\0'))
        if git('ls-files', '-u', '-z', '--', scope.folder):
            raise DevelopmentError('Resolve the existing conflicts in the development scope first.')
        source = {}
        for name in sorted(paths):
            if cancelled.is_set():
                raise InterruptedError('Development preparation was cancelled.')
            path = safe_path(self.repo, name)
            if not path.exists():
                if name in tracked or name not in scope.edit_paths:
                    raise DevelopmentError('A required source or trusted test is missing.')
                source[name] = None
                continue
            if name not in tracked or path.stat().st_size > _MAX_FILE:
                raise DevelopmentError('Only bounded tracked input files can enter this workspace.')
            raw = path.read_bytes()
            _text(raw)
            source[name] = raw
        if sum(len(raw) for raw in source.values() if raw is not None) > _MAX_TOTAL:
            raise DevelopmentError('The development snapshot exceeds its total size limit.')
        self.run_dir = Path(tempfile.mkdtemp(prefix='development-', dir=private))
        root = self.run_dir / 'workspace'
        root.mkdir()
        (root / 'AGENTS.md').write_text(_POLICY, encoding='utf-8')
        for name, raw in source.items():
            if raw is not None:
                target = safe_path(root, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        self.original = {name: _digest(raw) if raw is not None else 'new' for name, raw in source.items()}
        super().__init__(root, paths, lambda: not cancelled.is_set(), lambda *_: None, self.run_dir / 'backups')

    def call(self, args):
        if isinstance(args, dict) and args.get('operation') == 'write':
            if args.get('path') not in self.scope.edit_paths:
                raise DevelopmentError('The exact file is not editable in this development workspace.')
            if isinstance(args.get('content'), str):
                _text(args['content'].encode())
        return super().call(args)

    def _manifest(self):
        if self.cancelled.is_set():
            raise InterruptedError('Development verification was cancelled.')
        manifest = {}
        total = 0
        for folder, dirs, files in os.walk(self.root):
            for name in dirs + files:
                path = Path(folder) / name
                if not _ordinary(path):
                    raise DevelopmentError('The candidate contains a linked path.')
                if name in files and path.relative_to(self.root).as_posix() not in self.paths | {'AGENTS.md'}:
                    raise DevelopmentError('The candidate contains an unapproved file.')
        if (self.root / 'AGENTS.md').read_text(encoding='utf-8') != _POLICY:
            raise DevelopmentError('The workspace policy changed.')
        for name in sorted(self.paths):
            path = safe_path(self.root, name)
            if not path.exists() and self.original[name] != 'new':
                raise DevelopmentError('A candidate file was removed.')
            raw = path.read_bytes() if path.exists() and path.stat().st_size <= _MAX_FILE else None
            if raw is None and path.exists():
                raise DevelopmentError('A candidate file exceeds its size limit.')
            if raw is not None:
                _text(raw)
                total += len(raw)
            actual = _digest(raw) if raw is not None else 'new'
            if name not in self.scope.edit_paths and actual != self.original[name]:
                raise DevelopmentError('A read-only input or trusted test changed.')
            manifest[name] = actual
        if total > _MAX_TOTAL:
            raise DevelopmentError('The development candidate exceeds its total size limit.')
        return manifest

    def verify(self, verifier):
        """Execute the host-selected tests and retain a hash-bound review checkpoint."""
        with self.lock:
            candidate = self._manifest()
            changed = {name: value for name, value in candidate.items() if value != self.original[name]}
            if not changed:
                raise DevelopmentError('The candidate contains no scoped edits.')
            checks = verifier.run(self, self.cancelled)
            if type(checks) is not int or checks < 1:
                raise DevelopmentError('The sandbox did not report successful executable checks.')
            if candidate != self._manifest():
                raise DevelopmentError('The candidate changed during verification.')
            current_head = subprocess.check_output(['git', '-C', str(self.repo), 'rev-parse', 'HEAD'], timeout=10)
            if current_head.decode('ascii').strip() != self.base:
                raise DevelopmentError('The source revision changed during development.')
            for name, original in self.original.items():
                path = safe_path(self.repo, name)
                if path.exists() and path.stat().st_size > _MAX_FILE:
                    raise DevelopmentError('The source file grew during development.')
                if (_digest(path.read_bytes()) if path.exists() else 'new') != original:
                    raise DevelopmentError('The original workspace changed; review before integrating.')
            checkpoint = self.run_dir / 'verified-development.json'
            payload = {'base': self.base, 'scope': self.scope.folder, 'tests_run': checks,
                       'test_paths': list(self.scope.test_paths), 'original': self.original,
                       'changed': changed, 'candidate': candidate, 'integration': 'pending_review'}
            with checkpoint.open('x', encoding='utf-8') as stream:
                json.dump(payload, stream, sort_keys=True, indent=2)
            return {'kind': 'passed_test', 'path': str(checkpoint), 'sha256': _digest(checkpoint.read_bytes())}


_TEST_DRIVER = '''import importlib.util, json, os, sys, unittest
sys.path.insert(0, '/work')
sys.path.insert(0, sys.argv[1])
if any(os.path.exists(path) for path in ('/mnt/c', '/home', '/sys', '/run/WSL')):
    raise SystemExit('Unexpected host paths in verifier')
if not os.statvfs('/work').f_flag & os.ST_RDONLY:
    raise SystemExit('The candidate mount is writable')
with open('/proc/net/route') as routes:
    if len(routes.readlines()) != 1:
        raise SystemExit('Unexpected network routes in verifier')
suite = unittest.TestSuite()
for i, path in enumerate(sys.argv[2:]):
    spec = importlib.util.spec_from_file_location('_approved_test_' + str(i), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful() or result.testsRun <= len(result.skipped):
    raise SystemExit(1)
print(json.dumps({'tests_run': result.testsRun - len(result.skipped)}))
'''


class BubblewrapVerifier:
    """Run exact trusted tests inside a networkless Linux namespace."""

    def __init__(self, distribution=None, *, timeout=30):
        if distribution is not None and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', distribution):
            raise ValueError('An exact provisioned WSL distribution is required.')
        if not 1 <= timeout <= 120:
            raise ValueError('Verification timeout is outside its bounds.')
        self.distribution = distribution
        self.timeout = timeout

    def _prefix(self):
        if os.name == 'nt':
            if not self.distribution:
                raise DevelopmentError('An isolated WSL test runtime must be configured.')
            return ['wsl.exe', '-d', self.distribution, '--exec']
        if os.sys.platform != 'linux':
            raise DevelopmentError('An isolated Linux test runtime is required.')
        return []

    def run(self, workspace, cancelled):
        prefix = self._prefix()
        env = {key: value for key, value in os.environ.items() if key.upper() in
               {'SYSTEMROOT', 'WINDIR', 'USERPROFILE', 'SYSTEMDRIVE', 'PATH'}}
        mapped = str(workspace.root)
        if prefix:
            try:
                mapped = subprocess.check_output(
                    [*prefix, '/usr/bin/wslpath', '-a', '-u', mapped],
                    timeout=10, env=env, stderr=subprocess.STDOUT,
                ).decode('utf-8').strip()
            except subprocess.CalledProcessError as exc:
                diagnostic = exc.output.replace(b'\0', b'')
                if b'ERROR_NO_SYSTEM_RESOURCES' in diagnostic:
                    raise DevelopmentError('Windows reported insufficient resources to start WSL.') from exc
                if b'E_ACCESSDENIED' in diagnostic:
                    raise DevelopmentError('The current Windows process cannot access the WSL service.') from exc
                raise DevelopmentError('WSL could not resolve the isolated test workspace.') from exc
            except (OSError, subprocess.SubprocessError) as exc:
                raise DevelopmentError('WSL could not resolve the isolated test workspace.') from exc
        if not mapped.startswith('/') or '\n' in mapped or '\0' in mapped:
            raise DevelopmentError('The isolated test workspace mapping is invalid.')
        folder = '/work/' + workspace.scope.folder
        command = [*prefix, '/usr/bin/prlimit', '--cpu=20', '--as=805306368', '--fsize=1048576', '--',
                   '/usr/bin/bwrap', '--unshare-all', '--new-session', '--die-with-parent', '--clearenv',
                   '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
                   '--proc', '/proc', '--dev', '/dev', '--size', '16777216', '--tmpfs', '/tmp',
                   '--ro-bind', mapped, '/work', '--chdir', folder, '--setenv', 'HOME', '/tmp',
                   '--setenv', 'LANG', 'C.UTF-8', '--', '/usr/bin/python3', '-I', '-B', '-c', _TEST_DRIVER,
                   folder, *('/work/' + name for name in workspace.scope.test_paths)]
        # The host waits for an isolated child and stores bounded output. No shell or
        # model-provided executable, command option, working directory or test script.
        try:
            with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
                with subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=output, stderr=errors, env=env) as process:
                    deadline = time.monotonic() + self.timeout
                    while process.poll() is None:
                        if cancelled.wait(.05) or time.monotonic() >= deadline:
                            process.kill()
                            if cancelled.is_set():
                                raise InterruptedError('The sandboxed tests were cancelled.')
                            raise DevelopmentError('The sandboxed tests timed out.')
                    if process.returncode != 0:
                        raise DevelopmentError('The sandboxed tests failed or the isolated runtime was unavailable.')
                output.seek(0)
                result = json.loads(output.read(4096).decode('utf-8').splitlines()[-1])
        except (OSError, ValueError, IndexError) as exc:
            raise DevelopmentError('The sandboxed verifier did not return a valid test result.') from exc
        if not isinstance(result, dict) or set(result) != {'tests_run'}:
            raise DevelopmentError('The sandboxed verifier returned unexpected test evidence.')
        return result['tests_run']
