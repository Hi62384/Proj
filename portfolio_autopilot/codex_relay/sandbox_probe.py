"""Fixed, owner-authored WSL probes. No command or path comes from GitHub prose."""
import json
from .diagnostics import RelayError

SERVER = '''import socket,sys,time
s=socket.socket();s.bind(('127.0.0.1',0));s.listen();s.settimeout(.3)
print(s.getsockname()[1],flush=True)
deadline=time.monotonic()+30
while time.monotonic()<deadline:
 try:c,_=s.accept()
 except TimeoutError:continue
 with c:
  c.settimeout(1)
  try:data=c.recv(100)
  except OSError:continue
  if data==('stop:'+sys.argv[1]).encode():break
  c.sendall(b'relay-probe')
s.close()
'''

PROGRAM = '''import os,sys,json,socket
allowed,denied,link,port=sys.argv[1:]
checks={}
try:
 with open(allowed,'rb') as f:f.read(1)
 checks['authorized_read']=True
except OSError:checks['authorized_read']=False
def blocked_read(path):
 try:
  with open(path,'rb') as f:f.read(1)
  return False
 except OSError:return True
checks['unauthorized_read_blocked']=blocked_read(denied)
checks['traversal_blocked']=blocked_read(os.path.dirname(denied)+'/step/../denied.txt')
checks['symlink_blocked']=blocked_read(link)
try:
 with open(os.path.dirname(denied)+'/unexpected-write','xb') as f:pass
 checks['unauthorized_write_blocked']=False
except OSError:checks['unauthorized_write_blocked']=True
try:
 fd=os.open(allowed,os.O_WRONLY|os.O_APPEND);os.close(fd)
 checks['read_only_write_blocked']=False
except OSError:checks['read_only_write_blocked']=True
try:
 with socket.create_connection(('127.0.0.1',int(port)),timeout=1) as c:
  c.sendall(b'probe');c.recv(100)
 checks['network_blocked']=False
except OSError:checks['network_blocked']=True
print(json.dumps(checks,sort_keys=True))
'''

CHECKS = {'authorized_read', 'unauthorized_read_blocked', 'traversal_blocked', 'symlink_blocked',
          'unauthorized_write_blocked', 'read_only_write_blocked', 'network_blocked'}


def verify(rpc, config):
    from . import wsl_runtime
    fixture = wsl_runtime.python(config, '''import json,sys,pathlib,secrets,subprocess,socket
p=json.load(sys.stdin);base=pathlib.Path(p['home']).parent/'probes';base.mkdir(exist_ok=True)
root=base/secrets.token_hex(12);root.mkdir(mode=0o700);(root/'step').mkdir()
denied=root/'denied.txt';denied.write_text('synthetic relay security fixture')
link=root/'escape-link';link.symlink_to(denied)
nonce=secrets.token_hex(16)
server=subprocess.Popen(['/usr/bin/python3','-I','-S','-c',p['server'],nonce],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,start_new_session=True)
port=int(server.stdout.readline().strip());server.stdout.close()
with socket.create_connection(('127.0.0.1',port),timeout=2) as c:
 c.sendall(b'control');control=c.recv(100)==b'relay-probe'
print(json.dumps({'root':str(root),'denied':str(denied),'link':str(link),'port':port,'nonce':nonce,'control':control}))
''', {'home': config.wsl_home, 'server': SERVER})
    try:
        if fixture.get('control') is not True:
            raise RelayError('sandbox.probe', 'security control', 'The outside-sandbox network control was not reachable.')
        result = rpc.request('command/exec', {
            'command': ['/usr/bin/python3', '-I', '-S', '-c', PROGRAM,
                        rpc.workspace + '/AGENTS.md', fixture['denied'], fixture['link'], str(fixture['port'])],
            'cwd': rpc.workspace, 'permissionProfile': 'relay-locked', 'timeoutMs': 10000}, timeout=20)
        try:
            checks = json.loads(result.get('stdout', ''))
        except ValueError:
            checks = {}
        if result.get('exitCode') != 0 or not isinstance(checks, dict) or set(checks) != CHECKS or not all(v is True for v in checks.values()):
            raise RelayError('sandbox.probe', 'security checks', 'Restricted sandbox security checks failed.',
                             json.dumps({'checks': checks, 'stderr': result.get('stderr', '')}),
                             'Do not enable execution until the operating-system denial checks pass.')
        return checks
    finally:
        try:
            wsl_runtime.python(config, '''import json,sys,pathlib,socket
p=json.load(sys.stdin);root=pathlib.Path(p['root']);base=pathlib.Path(p['home']).parent/'probes'
if root.parent.resolve()!=base.resolve():raise ValueError('Unexpected fixture cleanup target')
try:
 with socket.create_connection(('127.0.0.1',p['port']),timeout=2) as c:c.sendall(('stop:'+p['nonce']).encode())
except OSError:pass
for name in ('denied.txt','escape-link','unexpected-write'):(root/name).unlink(missing_ok=True)
(root/'step').rmdir();root.rmdir();print('{}')
''', {**fixture, 'home': config.wsl_home})
        except (OSError, RuntimeError):
            pass  # The owned listener also has a hard 30-second lifetime.
