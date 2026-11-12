"""Install the optional Codex session hook while preserving existing hooks."""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MATCHER = '^(startup|resume|clear|compact|fork)$'


def _ordinary(path):
    if not path.exists():
        return not path.is_symlink()
    info = path.lstat()
    return not path.is_symlink() and not (getattr(info, 'st_file_attributes', 0) & 0x400)


def configuration(root, existing):
    """Return the merged configuration without changing the input."""
    root = Path(root).resolve(strict=True)
    python = root / 'apps' / 'codex_desktop_assistant' / '.venv' / 'Scripts' / 'python.exe'
    script = root / 'portfolio_manager' / 'codex_session_hook.py'
    if not python.is_file() or not script.is_file():
        raise ValueError('Portfolio Manager Python or its session hook is missing.')
    try:
        result = json.loads(existing.decode('utf-8-sig')) if existing else {}
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('Existing hooks.json is not valid UTF-8 JSON; it was not changed.') from exc
    if not isinstance(result, dict):
        raise ValueError('Existing hooks.json must contain a JSON object.')
    hooks = result.setdefault('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('Existing hooks must be a JSON object.')
    groups = hooks.setdefault('SessionStart', [])
    if not isinstance(groups, list):
        raise ValueError('Existing SessionStart hooks must be a JSON array.')
    # Encode the PowerShell command so spaces and shell metacharacters in the
    # checkout path cannot change how the hook command is interpreted.
    python_literal = str(python).replace("'", "''")
    script_literal = str(script).replace("'", "''")
    invocation = f"& '{python_literal}' '{script_literal}'"
    encoded = base64.b64encode(invocation.encode('utf-16le')).decode('ascii')
    command = f'powershell.exe -NoProfile -NonInteractive -EncodedCommand {encoded}'
    entry = {'matcher': MATCHER, 'hooks': [{'type': 'command', 'command': command,
             'timeout': 35, 'statusMessage': 'Connecting Portfolio Manager'}]}
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get('hooks'), list):
            raise ValueError('An existing SessionStart hook group is invalid.')
        for hook in group['hooks']:
            if isinstance(hook, dict) and (hook == entry['hooks'][0] or
                    hook.get('statusMessage') == 'Connecting Portfolio Manager' or
                    'codex_session_hook.py' in str(hook.get('command', ''))):
                if group == entry:
                    return existing, False
                raise ValueError('A Portfolio Manager session hook already exists with different settings; review it first.')
    groups.append(entry)
    return (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'), True


def install(root):
    """Write the owner-requested setup, refusing aliases and concurrent changes."""
    root = Path(root).resolve(strict=True)
    directory = root / '.codex'
    if not _ordinary(directory):
        raise ValueError('The project configuration folder is a link.')
    directory.mkdir(exist_ok=True)
    target = directory / 'hooks.json'
    if not _ordinary(target):
        raise ValueError('The hook configuration is a link.')
    previous = target.read_bytes() if target.exists() else b''
    if len(previous) > 1_000_000:
        raise ValueError('Existing hook configuration is too large.')
    updated, changed = configuration(root, previous)
    if not changed:
        return False
    if previous:
        # Exclusive creation preserves earlier backups and makes an existing backup visible.
        backup = directory / 'hooks.json.portfolio-backup'
        with backup.open('xb') as file:
            file.write(previous)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix='portfolio-hooks-', suffix='.tmp', delete=False) as file:
            temp_path = Path(file.name)
            file.write(updated)
            file.flush()
            os.fsync(file.fileno())
        if not _ordinary(target) or (target.read_bytes() if target.exists() else b'') != previous:
            raise ValueError('Hook configuration changed during setup; no settings were replaced.')
        os.replace(temp_path, target)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Add the hook to project configuration.')
    args = parser.parse_args()
    if not args.install:
        print('Use --install to add the Portfolio Manager session hook to this project.')
        return
    try:
        changed = install(ROOT)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Setup could not finish: {exc}\n')
    print('Hook added.' if changed else 'Hook is already configured.')
    print('Review and trust the hook in Codex. Open a new chat to use it.')


if __name__ == '__main__':
    main()
