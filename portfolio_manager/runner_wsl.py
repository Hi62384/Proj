"""Reuse a provisioned Relay runtime in a separate Linux home for each turn."""
from __future__ import annotations

import json
from pathlib import PurePosixPath
import re
import threading
import uuid

from portfolio_autopilot.codex_relay.config import data_directory
from portfolio_autopilot.codex_relay.wsl_runtime import python


_prepare_lock = threading.Lock()


class StagingCancelledBeforeStart(InterruptedError):
    """A waiting worker stopped before it created any WSL runtime files."""


_PREPARE = '''import json, os, pathlib, stat, sys
p = json.load(sys.stdin)
home = pathlib.Path.home().resolve(strict=True)
source_home = pathlib.Path(p['source_home'])
source_binary = pathlib.Path(p['source_binary'])
target_home = pathlib.Path(p['target_home'])
target_binary = pathlib.Path(p['target_binary'])
uid = os.getuid()
def check(path, is_dir=False):
 if not path.is_relative_to(home) or path.resolve(strict=True) != path:
  raise ValueError('Expected an ordinary path inside the current Linux user home')
 s = path.stat()
 if s.st_uid != uid or not (stat.S_ISDIR(s.st_mode) if is_dir else stat.S_ISREG(s.st_mode)):
  raise ValueError('Expected an owner-controlled runtime file')
 return s
check(source_home, True)
binary_info = check(source_binary)
if not (binary_info.st_mode & stat.S_IXUSR):
 raise ValueError('The existing Codex runtime is not executable')
manager = target_home.parent.parent
if not manager.parent.is_relative_to(home / '.local'):
 raise ValueError('Expected a private manager location')
check(manager.parent, True)
manager.mkdir(mode=0o700, exist_ok=True)
check(manager, True)
if manager.stat().st_mode & 0o077:
 raise ValueError('The manager runtime directory must be private')
run = target_home.parent
run.mkdir(mode=0o700)
target_home.mkdir(mode=0o700)
target_binary.parent.mkdir(mode=0o700)
os.link(source_binary, target_binary, follow_symlinks=False)
source_host = source_binary.parent / 'codex-code-mode-host'
if source_host.exists():
 host_info = check(source_host)
 if not (host_info.st_mode & stat.S_IXUSR):
  raise ValueError('The existing Codex workspace host is not executable')
 os.link(source_host, target_binary.parent / source_host.name, follow_symlinks=False)
cache = source_home / 'protocol' / 'verified.json'
try:
 if check(cache).st_size > 100000:
  raise ValueError('Compatibility cache is too large')
 with os.fdopen(os.open(cache, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as f:
  metadata = json.load(f)
 fingerprint = str(binary_info.st_size) + ':' + str(binary_info.st_mtime_ns)
 version = metadata.get('version')
 if (metadata.get('fingerprint') == fingerprint and metadata.get('contract') == 2
     and metadata.get('compatible') is True and isinstance(version, str)
     and len(version) <= 100 and version.startswith('codex-cli ')):
  protocol = target_home / 'protocol'
  protocol.mkdir(mode=0o700)
  clean = {'version': version, 'fingerprint': fingerprint, 'contract': 2, 'compatible': True}
  with os.fdopen(os.open(protocol / 'verified.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), 'w') as f:
   json.dump(clean, f)
except (OSError, ValueError, TypeError, AttributeError):
 pass  # A missing or invalid cache triggers the normal compatibility inspection.
auth = source_home / 'auth.json'
if check(auth).st_size > 1000000:
 raise ValueError('Unexpected existing ChatGPT login size')
with os.fdopen(os.open(auth, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as f:
 data = f.read(1000001)
if len(data) > 1000000:
 raise ValueError('Unexpected existing ChatGPT login size')
value = json.loads(data)
if value.get('auth_mode') != 'chatgpt' or not value.get('tokens'):
 raise ValueError('The existing Relay runtime needs ChatGPT authentication')
with os.fdopen(os.open(target_home / 'auth.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), 'wb') as f:
 f.write(data)
print('{}')
'''


_REMOVE_LOGIN = '''import json, os, pathlib, re, sys
p = json.load(sys.stdin)
home = pathlib.Path.home().resolve(strict=True)
target = pathlib.Path(p['home'])
if (not target.is_relative_to(home / '.local') or target.name != 'codex-home' or
    target.parent.parent.name != 'portfolio-manager-runs' or not re.fullmatch('[0-9a-f]{32}', target.parent.name)):
 raise ValueError('Unexpected worker login cleanup target')
if target.is_dir():
 if target.resolve(strict=True) != target or target.stat().st_uid != os.getuid():
  raise ValueError('Unsafe worker login cleanup target')
 (target / 'auth.json').unlink(missing_ok=True)
print('{}')
'''


def _owner_config():
    path = data_directory() / 'config.json'
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding='utf-8'))
    if value.get('execution_backend') != 'wsl':
        return None
    distro = value.get('wsl_distribution', '')
    raw_home, raw_binary = value.get('wsl_home', ''), value.get('wsl_binary', '')
    if not (isinstance(distro, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', distro)
            and isinstance(raw_home, str) and isinstance(raw_binary, str)):
        raise ValueError('The existing Relay WSL runtime is not configured correctly.')
    home, binary = PurePosixPath(raw_home), PurePosixPath(raw_binary)
    if (len(home.parts) < 6 or home.parts[:2] != ('/', 'home') or home.parts[3] != '.local'
            or home.name != 'codex-home' or '..' in home.parts or '..' in binary.parts
            or not binary.is_relative_to(home.parent / 'runtime') or binary.name != 'codex'
            or any('\x00' in part or '\n' in part for part in (*home.parts, *binary.parts))):
        raise ValueError('The existing Relay WSL runtime needs a private home and an official executable.')
    return distro, home, binary


def configure(config):
    existing = _owner_config()
    if existing is None:
        return None
    distro, source_home, source_binary = existing
    run = source_home.parent.parent / 'portfolio-manager-runs' / uuid.uuid4().hex
    config.execution_backend = 'wsl'
    config.wsl_distribution = distro
    config.wsl_home = str(run / 'codex-home')
    config.wsl_binary = str(run / 'runtime' / 'codex')
    return {'source_home': str(source_home), 'source_binary': str(source_binary),
            'target_home': config.wsl_home, 'target_binary': config.wsl_binary}


def prepare(config, locations, *, cancelled=None):
    # WSL can stall when multiple cold starts race. Serialize only staging,
    # then release the lock before either app-server runs a task.
    while not _prepare_lock.acquire(timeout=.1):
        if cancelled is not None and cancelled.is_set():
            raise StagingCancelledBeforeStart('Stopped while waiting for WSL runtime staging.')
    try:
        if cancelled is not None and cancelled.is_set():
            raise StagingCancelledBeforeStart('Stopped before WSL runtime staging.')
        python(config, _PREPARE, locations, timeout=35)
    finally:
        _prepare_lock.release()


def remove_login(config):
    python(config, _REMOVE_LOGIN, {'home': config.wsl_home}, timeout=12)
