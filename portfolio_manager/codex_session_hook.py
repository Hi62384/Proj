"""Optional local Codex SessionStart command hook for stable workspace recovery."""
import json
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'apps' / 'codex_desktop_assistant'


def workspace_context(event, client):
    if not isinstance(event, dict) or event.get('hook_event_name') != 'SessionStart':
        return None
    session_id = event.get('session_id')
    cwd = event.get('cwd')
    source = event.get('source')
    if (not isinstance(session_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', session_id)
            or not isinstance(cwd, str) or not Path(cwd).is_absolute()
            or source not in ('startup', 'resume', 'clear', 'compact', 'fork')):
        return None
    if not Path(cwd).resolve(strict=True).is_relative_to(ROOT):
        return None
    client.ensure()
    # Reserve the binding without opening a window for every repository chat.
    # The explicit portfolio_open operation shows the window when requested.
    key = client.request('bridge_bind_codex_session', {'session_id': session_id, 'show': False})[
        'reconnect_key']
    return {'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': (
        'Portfolio Manager has reserved this Codex chat’s workspace. For this chat’s Portfolio Manager calls, '
        'pass this private reconnect_key in the arguments object: ' + key + '. '
        'Keep it in working context only. Do not disclose it to the owner, include it in files, or share it with '
        'another chat. Use portfolio_open to show this chat’s window and portfolio_context to read its selection.'
    )}}


def main():
    if os.name != 'nt':
        return
    sys.path.insert(0, str(APP))
    from bridge.client import ControllerClient

    try:
        event = json.loads(sys.stdin.read(256 * 1024))
        result = workspace_context(event, ControllerClient())
    except (OSError, ValueError, RuntimeError, KeyError):
        # Fall back to the repository's normal MCP discovery without reporting private input.
        return
    if result is not None:
        print(json.dumps(result))


if __name__ == '__main__':
    main()
