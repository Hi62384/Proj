"""Recheck applied development files and rerun their isolated tests."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from types import SimpleNamespace

from portfolio_autopilot.codex_relay.config import safe_path
from .development import DevelopmentError, DevelopmentScope, _MAX_FILE, _MAX_TOTAL, _digest, _scoped_name


def validate_applied(repo, private_root, checkpoint_path, expected_sha256):
    """Check applied files and return the verified manifest's test scope."""
    repo = Path(repo).resolve(strict=True)
    private_root = Path(private_root).resolve(strict=True)
    checkpoint = Path(checkpoint_path)
    if not checkpoint.is_absolute() or not checkpoint.is_relative_to(private_root):
        raise DevelopmentError('The candidate checkpoint is outside private state.')
    checkpoint = safe_path(private_root, checkpoint.relative_to(private_root).as_posix())
    if checkpoint.name != 'verified-development.json' or checkpoint.stat().st_size > _MAX_TOTAL:
        raise DevelopmentError('Invalid development checkpoint.')
    raw = checkpoint.read_bytes()
    if not re.fullmatch(r'[0-9a-f]{64}', str(expected_sha256)) or _digest(raw) != expected_sha256:
        raise DevelopmentError('The development checkpoint changed.')
    try:
        report = json.loads(raw)
        candidate = report['candidate']
        original = report['original']
        changed = report['changed']
        folder = PurePosixPath(report['scope'])
        tests = tuple(report['test_paths'])
        if (report['integration'] != 'pending_review' or not isinstance(candidate, dict)
                or not isinstance(original, dict) or not isinstance(changed, dict)
                or set(candidate) != set(original) or not changed
                or changed != {name: value for name, value in candidate.items() if value != original[name]}):
            raise ValueError('Invalid manifest')
        scope = DevelopmentScope(str(folder), (), tuple(changed), tests)
        scope.validate()
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise DevelopmentError('The development checkpoint is invalid.') from exc
    workspace_root = checkpoint.parent / 'workspace'
    if not workspace_root.is_dir():
        raise DevelopmentError('The candidate workspace is unavailable.')

    def check_files():
        for name, expected in candidate.items():
            if name == 'PROJECT.md':
                context = safe_path(workspace_root, name)
                if (original[name] != expected or not context.is_file() or
                        context.stat().st_size > _MAX_FILE or _digest(context.read_bytes()) != expected):
                    raise DevelopmentError('The staged project context changed. Review the task again.')
                continue
            if not _scoped_name(name).is_relative_to(folder):
                raise DevelopmentError('The candidate contains a path outside its source folder.')
            staged = safe_path(workspace_root, name)
            actual = safe_path(repo, name)
            if expected == 'new' and not staged.exists() and not actual.exists():
                continue
            if (not staged.is_file() or not actual.is_file() or staged.stat().st_size > _MAX_FILE
                    or actual.stat().st_size > _MAX_FILE):
                raise DevelopmentError('Applied or candidate files changed. Review the task again.')
            staged_bytes = staged.read_bytes()
            actual_bytes = actual.read_bytes()
            if (hashlib.sha256(staged_bytes).hexdigest() != expected or
                    actual_bytes.replace(b'\r\n', b'\n') != staged_bytes.replace(b'\r\n', b'\n')):
                raise DevelopmentError('Applied or candidate files changed. Review the task again.')
        if _digest(checkpoint.read_bytes()) != expected_sha256:
            raise DevelopmentError('The development checkpoint changed.')

    check_files()
    return {'candidate_sha256': expected_sha256, 'record_sha256': original.get('PROJECT.md'),
            'files': sorted(changed)}, SimpleNamespace(root=workspace_root, scope=scope), check_files


def verify_applied(repo, private_root, checkpoint_path, expected_sha256, verifier, cancelled):
    """Verify that applied files equal the tested snapshot before and after tests."""
    if cancelled.is_set():
        raise InterruptedError('Verification was cancelled.')
    result, workspace, check_files = validate_applied(repo, private_root, checkpoint_path, expected_sha256)
    checks = verifier.run(workspace, cancelled)
    if cancelled.is_set():
        raise InterruptedError('Verification was cancelled.')
    if type(checks) is not int or checks < 1:
        raise DevelopmentError('The sandbox did not report successful executable checks.')
    check_files()
    return {**result, 'tests_run': checks}
