"""WSL2 transport: no GitHub secrets or database enter the Linux environment."""
import json
import os
from pathlib import Path
import subprocess

from .diagnostics import RelayError, protocol_error
from .permissions import render


def decode(data):
    return data.decode('utf-16-le' if b'\x00' in data else 'utf-8', errors='replace')


def call(config, argv, payload=None, timeout=30, user=None):
    command = ['wsl.exe', '-d', config.wsl_distribution]
    if user:
        command += ['-u', user]
    command += ['--exec', *argv]
    env = {k: v for k, v in os.environ.items() if k.upper() in
           ('SYSTEMROOT', 'WINDIR', 'PATH', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA', 'SYSTEMDRIVE')}
    try:
        result = subprocess.run(command, input=json.dumps(payload).encode() if payload is not None else None,
            capture_output=True, env=env, timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except subprocess.TimeoutExpired:
        raise RelayError('timeout', 'WSL2', 'WSL2 did not respond before the deadline.',
                         action='Check distribution startup and resources before retrying.') from None
    if result.returncode:
        raise protocol_error('WSL2', {'message': decode(result.stderr + result.stdout)})
    return decode(result.stdout)


def python(config, source, payload=None, timeout=30):
    return json.loads(call(config, ['/usr/bin/python3', '-I', '-c', source], payload, timeout))


def prepare(config, paths):
    if not config.wsl_home or not config.wsl_binary:
        raise RelayError('environment.wsl_setup', 'WSL2', 'The WSL2 Codex runtime has not been provisioned.',
                         action='When memory is available, run Setup_Codex_Relay_WSL.cmd. No Windows fallback will be used.')
    windows_paths = [str(config.workspace / 'AGENTS.md')] + [str(config.workspace / p) for p in paths]
    # Map approved Windows paths using the distribution's actual automount configuration.
    layout = python(config, '''import json,sys,subprocess,os
p=json.load(sys.stdin)
def mapped(value):
 return subprocess.check_output(['/usr/bin/wslpath','-a','-u',value],text=True).strip()
print(json.dumps({'workspace':mapped(p['workspace']),'paths':{x:mapped(x) for x in p['paths']},'user':os.environ.get('USER','')}))
''', {'workspace': str(config.workspace), 'paths': windows_paths})
    content = render(config, paths, path_mapper=lambda p: layout['paths'][str(p)])
    # Reuse a Linux-owned login when it exists; only import the existing ChatGPT login once.
    state = python(config, '''import json,sys,pathlib,os
p=json.load(sys.stdin);h=pathlib.Path(p['home']).resolve();base=pathlib.Path.home().resolve()
if not h.is_relative_to(base) or h==base: raise ValueError('Private relay home required')
h.mkdir(parents=True,exist_ok=True);h.chmod(0o700)
(h/'config.toml').write_text(p['config'],encoding='utf-8')
a=h/'auth.json'
if a.exists():
 v=json.loads(a.read_text());valid=v.get('auth_mode')=='chatgpt' and bool(v.get('tokens'))
 if not valid:raise ValueError('Only ChatGPT authentication is supported')
print(json.dumps({'needs_auth':not a.exists()}))
''', {'home': config.wsl_home, 'config': content})
    if state['needs_auth']:
        auth = config.data_dir / 'codex-home/auth.json'
        if not auth.is_file():
            raise RelayError('authentication', 'WSL2', 'Sign in with ChatGPT in the Windows relay home before importing its login.')
        value = json.loads(auth.read_text(encoding='utf-8'))
        if value.get('auth_mode') != 'chatgpt' or not value.get('tokens'):
            raise RelayError('authentication', 'WSL2', 'Only an existing ChatGPT login can be imported.')
        python(config, '''import sys,json,pathlib,os
p=json.load(sys.stdin);path=pathlib.Path(p['home'])/'auth.json'
fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(p['auth'],f)
print('{}')
''', {'home': config.wsl_home, 'auth': value})
    compatibility = python(config, '''import json,sys,pathlib,subprocess,hashlib
p=json.load(sys.stdin);exe=pathlib.Path(p['binary']);h=pathlib.Path(p['home']);folder=h/'protocol';folder.mkdir(exist_ok=True)
import os
env={'HOME':str(pathlib.Path.home()),'PATH':'/usr/bin:/bin','CODEX_HOME':str(h),'LANG':'C.UTF-8'}
version=subprocess.check_output([str(exe),'--version'],text=True,env=env).strip()
fingerprint=str(exe.stat().st_size)+':'+str(exe.stat().st_mtime_ns)
cache=folder/'verified.json'
if cache.exists() and json.loads(cache.read_text()).get('fingerprint')==fingerprint:
 print(cache.read_text());sys.exit()
subprocess.run([str(exe),'app-server','generate-json-schema','--experimental','--out',str(folder)],check=True,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
required={'ThreadStartParams':['permissions','dynamicTools'],'ThreadResumeParams':['permissions'],'TurnStartParams':['permissions','outputSchema'],'CommandExecParams':['permissionProfile']}
for name,fields in required.items():
 v=json.loads((folder/'v2'/(name+'.json')).read_text())
 if any(x not in v.get('properties',{}) for x in fields):raise ValueError('Unsupported Codex protocol: '+name)
value={'version':version,'compatible':True,'fingerprint':fingerprint};cache.write_text(json.dumps(value));print(json.dumps(value))
''', {'binary': config.wsl_binary, 'home': config.wsl_home}, timeout=60)
    linux_user_home = config.wsl_home.split('/.local/', 1)[0]
    command = ['wsl.exe', '-d', config.wsl_distribution, '--exec', '/usr/bin/env', '-i',
               'HOME=' + linux_user_home, 'USER=' + layout['user'], 'LANG=C.UTF-8',
               'PATH=/usr/local/bin:/usr/bin:/bin', 'CODEX_HOME=' + config.wsl_home,
               config.wsl_binary, 'app-server', '--listen', 'stdio://']
    return command, layout['workspace'], compatibility
