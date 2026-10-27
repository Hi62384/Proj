"""Discover the selected binary's protocol instead of assuming a CLI version."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from .diagnostics import RelayError


def inspect_binary(executable, data_dir):
    exe = Path(executable)
    fingerprint = hashlib.sha256(f'{exe.resolve()}:{exe.stat().st_size}:{exe.stat().st_mtime_ns}'.encode()).hexdigest()
    folder = Path(data_dir) / 'protocol' / fingerprint[:20]
    report = folder / 'compatibility.json'
    if report.is_file():
        try:
            cached = json.loads(report.read_text(encoding='utf-8'))
            if cached.get('contract') == 1 and cached.get('compatible') is True:
                return cached
        except (ValueError, OSError):
            pass
    folder.mkdir(parents=True, exist_ok=True)
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    try:
        version = subprocess.run([str(exe), '--version'], capture_output=True, text=True, encoding='utf-8', timeout=15, creationflags=flags)
        generated = subprocess.run([str(exe), 'app-server', 'generate-json-schema', '--experimental', '--out', str(folder)],
                                   capture_output=True, text=True, encoding='utf-8', timeout=30, creationflags=flags)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RelayError('protocol.compatibility', 'schema', 'Could not inspect the selected Codex executable.', str(exc),
                         'Check the configured executable and local permissions. No task or inference was started.') from None
    if version.returncode or generated.returncode:
        raise RelayError('protocol.compatibility', 'schema', 'The selected CLI cannot generate its app-server protocol.',
                         generated.stderr, 'Select a supported native Codex executable; no CLI reinstall is automatic.')
    required = {'ThreadStartParams': ('permissions', 'dynamicTools'), 'ThreadResumeParams': ('permissions', 'excludeTurns'),
                'TurnStartParams': ('permissions', 'outputSchema'), 'CommandExecParams': ('permissionProfile',),
                'PermissionProfileListResponse': ('data',)}
    for name, fields in required.items():
        path = folder / 'v2' / (name + '.json')
        try:
            value = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        except (ValueError, OSError):
            value = {}
        if any(field not in value.get('properties', {}) for field in fields):
            raise RelayError('protocol.compatibility', 'schema', f'The CLI lacks required {name} fields.',
                             action='Select a CLI supporting named permission profiles and dynamic tools.')
    result = {'version': version.stdout.strip(), 'fingerprint': fingerprint, 'compatible': True, 'contract': 1}
    temp = folder / 'compatibility.tmp'
    temp.write_text(json.dumps(result, indent=2), encoding='utf-8')
    temp.replace(report)
    return result
