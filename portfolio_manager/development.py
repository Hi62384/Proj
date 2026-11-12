"""Prepare and verify exact, owner-selected development files in a private copy."""
from __future__ import annotations

from dataclasses import dataclass, replace
import difflib
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


_TEXT_TYPES = {
    '.py', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx', '.css', '.html',
    '.md', '.json', '.toml', '.txt', '.csv', '.yaml', '.yml', '.ini', '.xml',
    '.sql', '.rst', '.sh', '.ps1', '.go', '.rs', '.java', '.cs',
}
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


def _test_result(output):
    """Read the verifier's final result even when tests print earlier output."""
    output.seek(0, os.SEEK_END)
    end = output.tell()
    output.seek(max(0, end - 4096))
    result = json.loads(output.read().splitlines()[-1].decode('utf-8'))
    if (not isinstance(result, dict) or set(result) != {'tests_run'} or
            type(result['tests_run']) is not int or result['tests_run'] < 1):
        raise DevelopmentError('The sandboxed verifier returned unexpected test evidence.')
    return result['tests_run']


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


def _test_kind(name):
    filename = PurePosixPath(name).name
    if re.fullmatch(r'(?:test_[A-Za-z0-9_]+|[A-Za-z0-9_]+_test)\.py', filename):
        return 'python'
    if re.fullmatch(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*\.(?:test|spec)\.(?:js|mjs|cjs)', filename):
        return 'node'
    return None


def _looks_like_test(name):
    """Keep common unsupported test formats read-only as well."""
    path = PurePosixPath(name)
    filename = path.name
    return bool(any(part.casefold() in {'tests', '__tests__'} for part in path.parts[:-1]) or
                _test_kind(name) or re.fullmatch(
        r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*\.(?:test|spec)\.(?:ts|tsx|jsx)', filename
    ))


@dataclass(frozen=True)
class DevelopmentScope:
    """Host-approved inputs. File content or model output cannot grant this scope."""

    folder: str
    read_paths: tuple[str, ...]
    edit_paths: tuple[str, ...]
    test_paths: tuple[str, ...]

    @classmethod
    def discover(cls, repo, folder):
        """Propose a bounded scope from tracked source and existing supported tests."""
        repo = Path(repo).resolve(strict=True)
        folder_path = PurePosixPath(folder)
        if (not folder_path.parts or folder_path.is_absolute() or str(folder_path) != folder
                or any(part.startswith('.') for part in folder_path.parts)):
            raise DevelopmentError('Choose a specific repository folder for development.')
        try:
            output = subprocess.check_output(
                ['git', '--literal-pathspecs', '-C', str(repo), 'ls-files', '-z', '--', folder],
                timeout=10,
            )
            names = output.decode('utf-8').split('\0')
        except (OSError, UnicodeError, subprocess.SubprocessError) as exc:
            raise DevelopmentError('Could not inspect tracked project files.') from exc
        editable, tests, readonly = [], [], []
        for name in filter(None, names):
            try:
                path = _scoped_name(name)
            except DevelopmentError:
                continue
            if not path.is_relative_to(folder_path):
                continue
            if _test_kind(name):
                tests.append(name)
            elif _looks_like_test(name):
                readonly.append(name)
            else:
                editable.append(name)
        scope = cls(folder, tuple(sorted(readonly)), tuple(sorted(editable)), tuple(sorted(tests)))
        scope.validate()
        return scope

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
        if any(_looks_like_test(path) for path in self.edit_paths):
            raise DevelopmentError('Test files and fixtures must be read-only during development verification.')
        for path in paths:
            if not _scoped_name(path).is_relative_to(folder):
                raise DevelopmentError('A development file is outside the approved folder.')
        if any(not _test_kind(p) for p in self.test_paths):
            raise DevelopmentError('Use explicit Python unittest or Node built-in test files.')
        return paths


class DevelopmentWorkspace(Workspace):
    """An isolated snapshot of a Git worktree plus exact, bounded new file paths."""

    def __init__(self, repo, private, scope, cancelled, *, project_context=None, allow_new_files=False):
        self.repo = Path(repo).resolve(strict=True)
        private = Path(private).absolute()
        if not private.is_dir() or private.resolve(strict=True) != private or not _ordinary(private):
            raise DevelopmentError('The private development directory must be an ordinary absolute path.')
        if private.is_relative_to(self.repo) and not private.is_relative_to(self.repo / 'business_portfolio' / '.local'):
            raise DevelopmentError('Development runs must be outside Git or in the ignored portfolio state.')
        self.scope = scope
        self.cancelled = cancelled
        self.allow_new_files = allow_new_files
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
        self.policy = _POLICY
        if allow_new_files:
            self.policy += '\nNew source files may be created inside the selected folder with sha256=new.\n'
        (root / 'AGENTS.md').write_text(self.policy, encoding='utf-8')
        for name, raw in source.items():
            if raw is not None:
                target = safe_path(root, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        self.original = {name: _digest(raw) if raw is not None else 'new' for name, raw in source.items()}
        if project_context is not None:
            if not isinstance(project_context, bytes):
                raise DevelopmentError('Project context must be a verified record.')
            _text(project_context)
            (root / 'PROJECT.md').write_bytes(project_context)
            self.original['PROJECT.md'] = _digest(project_context)
            paths = paths | {'PROJECT.md'}
        super().__init__(root, paths, lambda: not cancelled.is_set(), lambda *_: None, self.run_dir / 'backups')

    def call(self, args):
        with self.lock:
            if (self.allow_new_files and isinstance(args, dict) and
                    set(args) == {'operation', 'path', 'content', 'sha256'} and
                    all(isinstance(value, str) for value in args.values()) and
                    args['operation'] == 'read' and args['path'] not in self.paths):
                if not self.active():
                    raise ValueError('Task is paused or cancelled')
                name = args['path']
                path = _scoped_name(name)
                if (not path.is_relative_to(PurePosixPath(self.scope.folder)) or
                        _looks_like_test(name) or
                        safe_path(self.repo, name).exists() or safe_path(self.root, name).exists()):
                    raise DevelopmentError('The new file is outside the available development scope.')
                return {'exists': False, 'content': '', 'sha256': 'new'}
            if isinstance(args, dict) and args.get('operation') == 'write':
                name = args.get('path')
                if name not in self.scope.edit_paths:
                    if not self.allow_new_files:
                        raise DevelopmentError('The exact file is not editable in this development workspace.')
                    path = _scoped_name(name)
                    if (not path.is_relative_to(PurePosixPath(self.scope.folder)) or
                            _looks_like_test(name) or
                            safe_path(self.repo, name).exists() or len(self.paths) >= _MAX_FILES):
                        raise DevelopmentError('The new file is outside the available development scope.')
                    if args.get('sha256') != 'new':
                        raise DevelopmentError('A new file requires the new-file hash.')
                    previous_scope, previous_paths = self.scope, self.paths
                    self.scope = replace(self.scope, edit_paths=(*self.scope.edit_paths, name))
                    self.original[name] = 'new'
                    self.paths = self.paths | {name}
                    try:
                        if isinstance(args.get('content'), str):
                            _text(args['content'].encode())
                        return super().call(args)
                    except Exception:
                        self.scope, self.paths = previous_scope, previous_paths
                        self.original.pop(name, None)
                        raise
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
        if (self.root / 'AGENTS.md').read_text(encoding='utf-8') != self.policy:
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
                if name == 'PROJECT.md' and name not in self.scope.validate():
                    continue
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


def candidate_review(repo, private_root, checkpoint_path, expected_sha256):
    """Read and revalidate a host-generated development candidate for owner review."""
    repo = Path(repo).resolve(strict=True)
    private_root = Path(private_root).resolve(strict=True)
    checkpoint = Path(checkpoint_path)
    if not checkpoint.is_absolute() or not checkpoint.is_relative_to(private_root):
        raise DevelopmentError('The candidate checkpoint is outside private state.')
    relative = checkpoint.relative_to(private_root).as_posix()
    checkpoint = safe_path(private_root, relative)
    if checkpoint.name != 'verified-development.json' or checkpoint.stat().st_size > _MAX_TOTAL:
        raise DevelopmentError('Invalid development checkpoint.')
    raw = checkpoint.read_bytes()
    if not re.fullmatch(r'[0-9a-f]{64}', str(expected_sha256)) or _digest(raw) != expected_sha256:
        raise DevelopmentError('The development checkpoint changed.')
    try:
        report = json.loads(raw)
        folder = PurePosixPath(report['scope'])
        original, candidate, changed = report['original'], report['candidate'], report['changed']
        if (report['integration'] != 'pending_review' or type(report['tests_run']) is not int or
                report['tests_run'] < 1 or not isinstance(original, dict) or
                not isinstance(candidate, dict) or not isinstance(changed, dict) or
                set(original) != set(candidate) or not changed or len(candidate) > _MAX_FILES + 1 or
                changed != {name: value for name, value in candidate.items() if value != original[name]}):
            raise ValueError('Invalid manifest')
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise DevelopmentError('The development checkpoint is invalid.') from exc
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], timeout=10).decode('ascii').strip()
    if head != report['base']:
        raise DevelopmentError('The source revision changed after verification.')
    root = checkpoint.parent / 'workspace'
    if not root.is_dir() or not _ordinary(root):
        raise DevelopmentError('The candidate workspace is unavailable.')
    files = []
    patch = []
    for name, expected in sorted(candidate.items()):
        if name == 'PROJECT.md':
            context = safe_path(root, name)
            if (not context.is_file() or context.stat().st_size > _MAX_FILE or
                    _digest(context.read_bytes()) != expected or original[name] != expected):
                raise DevelopmentError('The candidate project context changed after verification.')
            continue
        path = _scoped_name(name)
        if not path.is_relative_to(folder):
            raise DevelopmentError('The candidate contains a path outside its source folder.')
        current = safe_path(repo, name)
        staged = safe_path(root, name)
        before = current.read_bytes() if current.exists() else None
        after = staged.read_bytes() if staged.exists() else None
        for data in (before, after):
            if data is not None:
                _text(data)
        if (_digest(before) if before is not None else 'new') != original[name]:
            raise DevelopmentError('A source file changed after verification.')
        if (_digest(after) if after is not None else 'new') != expected:
            raise DevelopmentError('A candidate file changed after verification.')
        if name not in changed:
            continue
        if after is None:
            raise DevelopmentError('Removing files is not supported by candidate review.')
        if (before is not None and before and not before.endswith(b'\n')) or (after and not after.endswith(b'\n')):
            raise DevelopmentError('Files without a final newline require manual integration.')
        diff = ''.join(difflib.unified_diff(
            before.decode('utf-8').splitlines(keepends=True) if before is not None else [],
            after.decode('utf-8').splitlines(keepends=True),
            fromfile='/dev/null' if before is None else 'a/' + name, tofile='b/' + name))
        files.append({'path': name, 'original_sha256': original[name], 'candidate_sha256': expected, 'diff': diff})
        patch.append(diff)
    if len(files) != len(changed):
        raise DevelopmentError('The candidate contains an invalid change.')
    return {'checkpoint': str(checkpoint), 'sha256': expected_sha256, 'base': head,
            'record_sha256': original.get('PROJECT.md'), 'files': files, 'patch': ''.join(patch)}


def apply_reviewed_candidate(repo, private_root, checkpoint_path, expected_sha256):
    """Apply the exact reviewed candidate through Git's all-or-nothing patch operation."""
    review = candidate_review(repo, private_root, checkpoint_path, expected_sha256)
    command = ['git', '-C', str(repo), 'apply', '--whitespace=nowarn']
    patch = review['patch'].encode('utf-8')
    try:
        subprocess.run([*command, '--check', '-'], input=patch, check=True, capture_output=True, timeout=30)
        subprocess.run([*command, '-'], input=patch, check=True, capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        raise DevelopmentError('The reviewed changes could not be applied. Review the current files again.') from exc
    return {'sha256': expected_sha256, 'files': [item['path'] for item in review['files']]}


_PYTHON_TEST_LOADER = '''import importlib, importlib.util, os, sys, unittest
def load_test_file(path, index, root):
    parent = os.path.dirname(path)
    root = os.path.abspath(root)
    packages = []
    while parent != root and os.path.isfile(os.path.join(parent, '__init__.py')):
        name = os.path.basename(parent)
        if not name.isidentifier():
            break
        packages.insert(0, name)
        parent = os.path.dirname(parent)
    root_name = os.path.basename(root)
    if parent == root and root_name.isidentifier() and os.path.isfile(os.path.join(root, '__init__.py')):
        packages.insert(0, root_name)
        sys.path.insert(0, os.path.dirname(root))
    if packages:
        importlib.import_module('.'.join(packages))
    name = '.'.join([*packages, '_portfolio_test_' + str(index)])
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError('Could not load an approved test file')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module)
'''

_TEST_DRIVER = _PYTHON_TEST_LOADER + '''
import json
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
    suite.addTests(load_test_file(path, i, sys.argv[1]))
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful() or result.testsRun <= len(result.skipped):
    raise SystemExit(1)
print(json.dumps({'tests_run': result.testsRun - len(result.skipped)}))
'''

_NODE_TEST_DRIVER = r'''const fs = require('node:fs');
const { run } = require('node:test');
for (const path of ['/mnt/c', '/home', '/sys', '/run/WSL']) {
  if (fs.existsSync(path)) throw new Error('Unexpected host paths in verifier');
}
const workMount = fs.readFileSync('/proc/mounts', 'utf8').split('\n')
  .map(line => line.split(' ')).find(parts => parts[1] === '/work');
if (!workMount || !workMount[3].split(',').includes('ro')) {
  throw new Error('The candidate mount is writable');
}
if (fs.readFileSync('/proc/net/route', 'utf8').trim().split('\n').length !== 1) {
  throw new Error('Unexpected network routes in verifier');
}
let passed = 0;
let failed = false;
if (Number(process.versions.node.split('.')[0]) < 22) {
  throw new Error('Node 22 or later is required for isolated test verification');
}
const stream = run({ files: process.argv.slice(1), concurrency: 1, isolation: 'none' });
stream.on('test:pass', event => {
  if (event.details.type === 'test' && typeof event.file === 'string' &&
      Number.isInteger(event.line) && !event.skip && !event.todo) passed++;
});
stream.on('test:fail', () => { failed = true; });
stream.on('error', () => { failed = true; });
stream.on('end', () => {
  if (failed || passed < 1) process.exitCode = 1;
  else process.stdout.write(JSON.stringify({ tests_run: passed }) + '\n');
});
stream.resume();
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
        sandbox = [*prefix, '/usr/bin/prlimit', '--cpu=20', '--as=805306368', '--fsize=1048576', '--',
                   '/usr/bin/bwrap', '--unshare-all', '--new-session', '--die-with-parent', '--clearenv',
                   '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
                   '--proc', '/proc', '--dev', '/dev', '--size', '16777216', '--tmpfs', '/tmp',
                   '--ro-bind', mapped, '/work', '--chdir', folder, '--setenv', 'HOME', '/tmp',
                   '--setenv', 'LANG', 'C.UTF-8', '--']
        python_tests = [name for name in workspace.scope.test_paths if _test_kind(name) == 'python']
        node_tests = [name for name in workspace.scope.test_paths if _test_kind(name) == 'node']
        commands = []
        if python_tests:
            commands.append([*sandbox, '/usr/bin/python3', '-I', '-B', '-c', _TEST_DRIVER,
                             folder, *('/work/' + name for name in python_tests)])
        if node_tests:
            commands.append([*sandbox, '/usr/bin/node', '-e', _NODE_TEST_DRIVER,
                             *('/work/' + name for name in node_tests)])
        # The host waits for an isolated child and stores bounded output. No shell or
        # model-provided executable, command option, working directory or test script.
        deadline = time.monotonic() + self.timeout
        total = 0
        for command in commands:
            try:
                with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
                    with subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=output, stderr=errors, env=env) as process:
                        while process.poll() is None:
                            if cancelled.wait(.05) or time.monotonic() >= deadline:
                                process.kill()
                                if cancelled.is_set():
                                    raise InterruptedError('The sandboxed tests were cancelled.')
                                raise DevelopmentError('The sandboxed tests timed out.')
                        if process.returncode != 0:
                            raise DevelopmentError('The sandboxed tests failed or the isolated runtime was unavailable.')
                    count = _test_result(output)
            except (OSError, ValueError, IndexError, UnicodeError) as exc:
                raise DevelopmentError('The sandboxed verifier did not return a valid test result.') from exc
            total += count
        return total
