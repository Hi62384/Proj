"""One named profile, exact read grants, no shell access or filesystem writes."""
import json
import os
from pathlib import Path
import tomllib

from .config import safe_path

PROFILE = 'relay-locked'

FEATURES = {'shell_tool': False, 'unified_exec': False, 'shell_snapshot': False,
            'plugins': False, 'apps': False, 'multi_agent': False, 'code_mode': False, 'js_repl': False}


def selected_mode(config):
    if config.windows_sandbox != 'auto':
        return config.windows_sandbox
    path = config.data_dir / 'codex-home/config.toml'
    if path.is_file():
        previous = tomllib.loads(path.read_text(encoding='utf-8'))
        mode = previous.get('windows', {}).get('sandbox')
        if mode in ('elevated', 'unelevated', 'mxc'):
            return mode
    return 'unelevated'


def render(config, paths=None, path_mapper=str):
    grants = {path_mapper(safe_path(config.workspace, path)) for path in (paths or [])}
    grants.add(path_mapper(safe_path(config.workspace, 'AGENTS.md')))
    if config.execution_backend == 'wsl' and config.wsl_binary:
        base = config.wsl_home.removesuffix('/codex-home')
        if not config.wsl_home.endswith('/codex-home') or not config.wsl_binary.startswith(base + '/runtime/'):
            raise ValueError('Unexpected WSL Codex runtime path')
        grants.add(config.wsl_binary)
        # Bubblewrap re-executes this static binary as its sandbox bootstrap.
        # :minimal covers system tools/loaders, but not a binary in the private runtime home.
    lines = ['forced_login_method = "chatgpt"', 'model_provider = "openai"',
             'approval_policy = "never"', 'web_search = "disabled"',
             'cli_auth_credentials_store = "file"', f'default_permissions = "{PROFILE}"',
             'project_doc_max_bytes = 0']  # Instructions are read through the bounded tool.
    lines.extend([f'[permissions.{PROFILE}.filesystem]', '":root" = "deny"', '":minimal" = "read"'])
    lines.extend(f'{json.dumps(p)} = "read"' for p in sorted(grants))
    lines.extend([f'[permissions.{PROFILE}.network]', 'enabled = false', '[features]'])
    lines.extend(f'{key} = false' for key in FEATURES)
    lines.extend(['[apps._default]', 'enabled = false'])
    if os.name == 'nt' and config.execution_backend == 'windows':
        lines.extend(['[windows]', f'sandbox = "{selected_mode(config)}"'])
    return '\n'.join(lines) + '\n'


def overrides():
    return {**{f'features.{k}': v for k, v in FEATURES.items()},
            'mcp_servers': {}, 'web_search': 'disabled', 'project_doc_max_bytes': 0}


def preflight(rpc, config):
    cwd = getattr(rpc, 'workspace', str(config.workspace))
    profiles = rpc.request('permissionProfile/list', {'cwd': cwd})
    if not any(p.get('id') == PROFILE and p.get('allowed') is True for p in profiles.get('data', [])):
        from .diagnostics import RelayError
        raise RelayError('permissions.profile', 'permissionProfile/list', 'The restricted relay profile is unavailable or denied.',
                         action='Inspect managed requirements and the local protocol diagnostic; do not select a broader profile.')
    # Owner-authored constant probe only. Never accept an argv vector from a task or model.
    command = [str(Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32/cmd.exe'), '/d', '/c', 'echo CODEX_RELAY_SANDBOX_OK'] if os.name == 'nt' and config.execution_backend == 'windows' else ['/bin/echo', 'CODEX_RELAY_SANDBOX_OK']
    result = rpc.request('command/exec', {'command': command, 'cwd': cwd,
                         'permissionProfile': PROFILE, 'timeoutMs': 10000}, timeout=20)
    if result.get('exitCode') != 0 or 'CODEX_RELAY_SANDBOX_OK' not in result.get('stdout', ''):
        from .diagnostics import RelayError
        raise RelayError('sandbox.probe', 'command/exec', 'The restricted sandbox probe did not complete successfully.',
                         str(result.get('stderr', '')), 'Inspect local diagnostics before approving execution.')
    security_checks = {}
    if config.execution_backend == 'wsl':
        from .sandbox_probe import verify
        security_checks = verify(rpc, config)
    return {'sandbox': 'verified', 'profile': PROFILE, 'security_checks': security_checks, 'mode': selected_mode(config) if os.name == 'nt' and config.execution_backend == 'windows' else 'wsl2' if config.execution_backend == 'wsl' else 'native'}
