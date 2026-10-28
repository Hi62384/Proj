"""Separate Codex home, same supported stdio transport; Relay files are never changed."""
import json
import os
import queue
import subprocess
import threading
from dataclasses import replace
from pathlib import Path

from portfolio_autopilot.codex_relay.config import Config
from portfolio_autopilot.codex_relay.codex import Rpc
from portfolio_autopilot.codex_relay import wsl_runtime
from portfolio_autopilot.codex_relay.diagnostics import RelayError


def configuration(directory):
    directory=Path(directory)
    if (directory/'config.json').is_file():
        own=Config.load(directory)
        if own.execution_backend!='wsl':raise RuntimeError('Only the restricted WSL backend is supported by this desktop client')
        return own
    relay=Config.load()
    if relay.execution_backend!='wsl':
        raise RuntimeError('This client currently requires the verified WSL2 runtime. Original Relay configuration was not changed.')
    base=relay.wsl_home.split('/.local/',1)[0]+'/.local/share/codex-desktop-assistant'
    binary=base+'/runtime/codex'
    # Fixed installation copy only: no model or retrieved content can choose these paths.
    wsl_runtime.python(relay,'''import json,sys,pathlib,shutil,os
p=json.load(sys.stdin);h=pathlib.Path(p['home']);h.mkdir(parents=True,exist_ok=True);h.chmod(0o700)
b=pathlib.Path(p['binary']);b.parent.mkdir(parents=True,exist_ok=True)
source=pathlib.Path(p['source'])
if not b.exists() or b.stat().st_size!=source.stat().st_size:shutil.copy2(source,b)
b.chmod(0o700)
helper=source.parent/'codex-code-mode-host'
if not helper.is_file():raise ValueError('Official runtime tool host is missing')
target=b.parent/helper.name
if not target.exists() or target.stat().st_size!=helper.stat().st_size:shutil.copy2(helper,target)
target.chmod(0o700)
a=h/'auth.json'
if not a.exists():
 v=json.loads(pathlib.Path(p['auth']).read_text())
 if v.get('auth_mode')!='chatgpt' or not v.get('tokens'):raise ValueError('ChatGPT login required')
 fd=os.open(a,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(v,f)
print('{}')
''',{'home':base+'/codex-home','binary':binary,'source':relay.wsl_binary,'auth':relay.wsl_home+'/auth.json'})
    own=replace(relay,data_dir=directory,wsl_home=base+'/codex-home',wsl_binary=binary,model='',owner_id=0,trusted_ids=[]).validate()
    own.save()
    return own


class AssistantRpc(Rpc):
    """Reuse the tested wire protocol, with this app's exact companion-binary grant."""
    def __init__(self,config,stop_event=None):
        self.config=config;self.setup_only=False;self.stderr_lines=[];self.close_lock=threading.Lock()
        command,self.workspace,self.compatibility=wsl_runtime.prepare(config,[])
        helper=str(Path(config.wsl_binary).parent).replace('\\','/')+'/codex-code-mode-host'
        wsl_runtime.python(config,'''import json,sys,pathlib,tomllib
p=json.load(sys.stdin);home=pathlib.Path(p['home']);helper=pathlib.Path(p['helper'])
if helper.parent!=pathlib.Path(p['binary']).parent or helper.name!='codex-code-mode-host' or not helper.is_file():raise ValueError('Unexpected companion executable')
path=home/'config.toml';text=path.read_text();needle='[permissions.relay-locked.filesystem]'
text=text.replace(needle,needle+'\\n'+json.dumps(str(helper))+' = "read"',1)
value=tomllib.loads(text)
if value['permissions']['relay-locked']['filesystem'][':root']!='deny':raise ValueError('Root denial required')
temporary=home/'desktop-config.pending';temporary.write_text(text);temporary.replace(path);print('{}')
''',{'home':config.wsl_home,'helper':helper,'binary':config.wsl_binary})
        system=Path(os.environ.get('SystemRoot','C:/Windows'))
        allowed={'SYSTEMROOT','WINDIR','USERPROFILE','USERNAME','APPDATA','LOCALAPPDATA','SYSTEMDRIVE','HTTPS_PROXY','HTTP_PROXY','NO_PROXY'}
        env={k:v for k,v in os.environ.items() if k.upper() in allowed}
        env['PATH']=os.pathsep.join([str(system/'System32'),str(system)])
        temp=config.data_dir/'tmp';temp.mkdir(exist_ok=True);env['TEMP']=env['TMP']=str(temp)
        if stop_event and stop_event.is_set():raise InterruptedError('Application closed during runtime preparation')
        self.process=subprocess.Popen(command,cwd=config.data_dir,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            text=True,encoding='utf-8',bufsize=1,creationflags=subprocess.CREATE_NO_WINDOW)
        self.events=queue.Queue();self.pending={};self.lock=threading.Lock();self.next_id=0
        self.reader=threading.Thread(target=self._read,daemon=True);self.stderr_reader=threading.Thread(target=self._read_stderr,daemon=True)
        self.reader.start();self.stderr_reader.start()
        try:
            self.initialize_result=self.request('initialize',{'clientInfo':{'name':'codex_desktop_assistant','title':'Codex Desktop Assistant','version':'0.1.0'},'capabilities':{'experimentalApi':True}})
            self.send({'method':'initialized','params':{}})
            account=self.request('account/read',{'refreshToken':False}).get('account')
            if not account or account.get('type')!='chatgpt':raise RelayError('authentication','account/read','ChatGPT authentication is required; API-key billing is disabled.')
            self.authenticated=True
            if stop_event and stop_event.is_set():raise InterruptedError('Application closed during sign-in verification')
        except Exception:self.close();raise


def discover(rpc, config):
    contract=wsl_runtime.python(config,'''import json,sys,pathlib
p=json.load(sys.stdin);root=pathlib.Path(p['home'])/'protocol'
def schema(name):return json.loads((root/name).read_text())
steer=schema('v2/TurnSteerParams.json');output=schema('DynamicToolCallResponse.json')
turn=schema('v2/TurnStartParams.json')
print(json.dumps({'steer':all(x in steer.get('properties',{}) for x in ('threadId','input','expectedTurnId')),
'tool_images':'inputImage' in json.dumps(output),'image_input':'ImageUserInput' in json.dumps(turn)}))
''',{'home':config.wsl_home})
    if not contract.get('tool_images') or not contract.get('image_input'):
        raise RuntimeError('Installed protocol cannot deliver required image inputs; no perception claim is possible')
    models=[];cursor=None
    for _ in range(10):
        params={'limit':50,'includeHidden':False}
        if cursor:params['cursor']=cursor
        response=rpc.request('model/list',params);models.extend(response.get('data',[]))
        cursor=response.get('nextCursor')
        if not cursor:break
    return contract,models
