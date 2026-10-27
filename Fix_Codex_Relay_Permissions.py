"""Fix Proj/Codex Relay's deprecated restricted-read app-server request.

Run from the Proj repository root with Codex Relay fully closed:
    python Fix_Codex_Relay_Permissions.py

This changes only portfolio_autopilot/codex_relay/codex.py, after a backup.
No GitHub pushes, external connections, package installs, or AI calls.
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path
import re
import sys
import tomllib

TARGET = Path('portfolio_autopilot/codex_relay/codex.py')
PROFILE_NAME = 'relay-locked'


def single_replace(src: str, old: str, new: str, description: str) -> str:
    matches = src.count(old)
    if matches != 1:
        raise ValueError(f'{description}: expected exactly one matching source section, found {matches}. No changes were made.')
    return src.replace(old, new, 1)


def main() -> None:
    if not TARGET.is_file() or not Path('AGENTS.md').is_file():
        raise SystemExit('ERROR: Run from the root of your Proj repository (the folder containing AGENTS.md).')
    original_bytes = TARGET.read_bytes()
    try:
        original = original_bytes.decode('utf-8')
        newline = '\r\n' if b'\r\n' in original_bytes else '\n'
        # Match the repository's native line endings without rewriting the entire file.
        original_lf = original.replace('\r\n', '\n')
        if 'default_permissions = "relay-locked"' in original_lf:
            raise ValueError('A relay-locked profile already exists. No changes made; inspect the existing code first.')

        changed = single_replace(original_lf,
            'sandbox_mode = "read-only"\n', '',
            'Remove mutually exclusive legacy sandbox mode')

        profile = '''default_permissions = "relay-locked"

[permissions.relay-locked.filesystem]
":root" = "deny"
":minimal" = "read"

[permissions.relay-locked.filesystem.":workspace_roots"]
"." = "read"
".git" = "deny"
".local" = "deny"
".codex" = "deny"
".env" = "deny"

[permissions.relay-locked.network]
enabled = false

'''
        changed = single_replace(changed,
            'cli_auth_credentials_store = "file"\n[features]\n',
            'cli_auth_credentials_store = "file"\n' + profile + '[features]\n',
            'Configure restricted read-only permission profile')

        changed = single_replace(changed,
            '"cwd": str(self.config.workspace), "sandbox": "read-only",',
            '"cwd": str(self.config.workspace), "permissions": "relay-locked",',
            'Select permission profile at thread start and resume')

        old_turn = ('"sandboxPolicy": {"type": "readOnly", "access": {"type": "restricted",\n'
                    '                    "includePlatformDefaults": True, "readableRoots": [str(self.config.workspace)]}},')
        changed = single_replace(changed, old_turn,
            '"permissions": "relay-locked",',
            'Select permission profile for each turn')

        compile(changed, str(TARGET), 'exec')
        match = re.search(r"config_text = '''(.*?)'''", changed, flags=re.DOTALL)
        if not match:
            raise ValueError('Isolated Codex config block was not found; no changes made.')
        config = tomllib.loads(match.group(1))
        if config.get('default_permissions') != PROFILE_NAME or 'sandbox_mode' in config:
            raise ValueError('Permission profile config did not validate; no changes made.')
        if config['permissions'][PROFILE_NAME]['filesystem'][':root'] != 'deny':
            raise ValueError('Root read deny rule was missing; no changes made.')
        if config['permissions'][PROFILE_NAME]['network']['enabled'] is not False:
            raise ValueError('Network deny was missing; no changes made.')
        if changed.count('"permissions": "relay-locked"') != 2 or 'readOnly.access' in changed:
            raise ValueError('Expected permissions call sites did not validate; no changes made.')

        backup_dir = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'CodexRelay' / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / ('codex_before_profile_fix_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.py')
        with backup.open('xb') as f:
            f.write(original_bytes)
        TARGET.write_bytes(changed.replace('\n', newline).encode('utf-8'))
    except Exception as exc:
        raise SystemExit(f'ERROR: {exc}') from None

    print('SUCCESS: Updated Codex Relay to use the restricted relay-locked permission profile.')
    print(f'Updated: {TARGET}')
    print(f'Backup: {backup}')
    print('No other project files were changed.')
    print('NEXT: Run the offline unit tests, then restart Codex Relay.')
    print('python -m unittest discover -s portfolio_autopilot/codex_relay/tests -v')


if __name__ == '__main__':
    main()
