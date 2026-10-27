"""Actionable local diagnostics. Never send this information to GitHub."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import threading
import uuid


def sanitize(value):
    text = str(value)[:16000]
    text = re.sub(r'(?i)(?:github_pat_|gh[pousr]_|sk-)[a-z0-9_-]+', '[credential]', text)
    text = re.sub(r'(?i)bearer\s+[^\s"\']+', 'Bearer [credential]', text)
    text = re.sub(r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)?', '[token]', text)
    text = re.sub(r'(?i)((?:access_token|refresh_token|id_token|api_key|password)\s*[=:]\s*)[^\s,}]+', r'\1[redacted]', text)
    text = re.sub(r'[A-Za-z]:[\\/][^\n\r"<>]*', '[local path]', text)
    text = re.sub(r'/(?:home|Users)/[^\s"\']+', '[local path]', text)
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email]', text)
    text = re.sub(r'S-1-5-21-(?:\d+-){2}\d+(?:-\d+)?', '[local account SID]', text)
    return text


class RelayError(RuntimeError):
    def __init__(self, category, stage, explanation, detail='', action='', code=None):
        self.category, self.stage = category, stage
        self.explanation, self.detail, self.action, self.code = explanation, sanitize(detail), action, code
        super().__init__(f'{stage}: {explanation}' + (f' {action}' if action else ''))

    def as_dict(self):
        return {'category': self.category, 'stage': self.stage, 'explanation': self.explanation,
                'detail': self.detail, 'action': self.action, 'code': self.code,
                'authentication_verified': getattr(self, 'authentication_verified', False)}


def protocol_error(stage, error):
    raw = str(error.get('message', 'App-server rejected the request'))
    low = raw.lower()
    if 'requires effective `:root` read access' in low:
        return RelayError('sandbox.windows_root_read_required', stage,
            'This native Windows backend requires broad root reads and cannot enforce the relay profile.', raw,
            'Use the approved WSL2 setup when resources are available. Do not broaden the task profile.', error.get('code'))
    if 'error_no_system_resources' in low or 'insufficient system resources' in low:
        return RelayError('environment.wsl_resources', stage, 'WSL2 could not start because Windows reports insufficient system resources.', raw,
                          'Free memory by closing unused applications, then rerun the approved WSL2 setup.', error.get('code'))
    if 'restricted-token' in low or 'split filesystem' in low or 'unelevated' in low and 'cannot' in low:
        return RelayError('sandbox.windows_restricted_token', stage,
            'The Windows unelevated sandbox cannot enforce the required restricted reads.', raw,
            'Administrator-approved elevated sandbox setup is required, or configure a verified WSL2 runtime. Broad-read and unsandboxed fallbacks are disabled.', error.get('code'))
    if 'mxc' in low and any(x in low for x in ('unavailable', 'not supported', 'unsupported')):
        return RelayError('sandbox.mxc_unavailable', stage, 'MXC is unavailable on this executor.', raw,
                          'Use an explicitly provisioned elevated sandbox or a verified WSL2 runtime.', error.get('code'))
    if 'sandbox' in low or 'permission' in low and 'denied' in low:
        return RelayError('sandbox.setup', stage, 'The selected sandbox could not enforce the permission profile.', raw,
                          'Inspect local diagnostics and complete the approved sandbox setup. Do not disable isolation.', error.get('code'))
    if 'no rollout found' in low:
        return RelayError('session.missing', stage, 'The saved thread has no persisted rollout.', raw,
                          'Review files, choose Reset failed session locally, then Resume.', error.get('code'))
    if 'routing discovery' in low or any(x in low for x in ('unauthorized', 'authentication', 'not logged in', '401')):
        return RelayError('authentication', stage, 'ChatGPT sign-in or workspace discovery failed.', raw,
                          'Check network access and refresh the relay’s isolated ChatGPT login.', error.get('code'))
    if error.get('code') in (-32600, -32601, -32602) or any(x in low for x in ('no longer supported', 'unknown variant', 'invalid request')):
        return RelayError('protocol.compatibility', stage, 'The CLI rejected the request or permission configuration.', raw,
                          'Run Test connections to recheck the selected executable and protocol. No permissive fallback is used.', error.get('code'))
    return RelayError('inference' if stage.startswith('turn') else 'protocol', stage,
                      'Codex rejected the operation.', raw, 'Inspect the local diagnostic detail before retrying.', error.get('code'))


_lock = threading.Lock()


def record(directory, error, **context):
    value = error.as_dict() if isinstance(error, RelayError) else {
        'category': 'local', 'stage': 'relay', 'explanation': 'Local operation failed', 'detail': sanitize(error)}
    value.update(at=datetime.now(timezone.utc).isoformat(), **context)
    value = json.loads(json.dumps(value, default=str))
    try:
        with _lock:
            folder = Path(directory) / 'diagnostics'
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8] + '.json')
            path.write_text(json.dumps(value, indent=2), encoding='utf-8')
            temp = folder / 'latest.tmp'
            temp.write_text(json.dumps(value, indent=2), encoding='utf-8')
            temp.replace(folder / 'latest.json')
    except OSError:
        value['persistence_error'] = 'Could not save diagnostic; original failure preserved'
    return value


def latest(directory):
    path = Path(directory) / 'diagnostics/latest.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
