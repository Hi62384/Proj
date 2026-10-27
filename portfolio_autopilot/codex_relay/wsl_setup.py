"""Owner-approved, restartable installation into an existing Ubuntu WSL2 distribution."""
import argparse
from dataclasses import replace
import json
import time

from .__main__ import InstanceLock
from .codex import Codex
from .config import Config
from .diagnostics import RelayError, record
from . import wsl_runtime


INSTALL = r'''import os,sys,json,pathlib,urllib.request,hashlib,base64,tempfile,tarfile,shutil,subprocess
p=json.load(sys.stdin);base=pathlib.Path.home()/'.local/share/codex-relay';base.mkdir(parents=True,exist_ok=True);base.chmod(0o700)
version='0.162.1-linux-x64'
if os.uname().machine!='x86_64':raise RuntimeError('This installer is for x86_64 Ubuntu')
folder=base/'runtime'/version;exe=folder/'vendor/x86_64-unknown-linux-musl/bin/codex'
if not exe.is_file():
 metadata=json.load(urllib.request.urlopen('https://registry.npmjs.org/@openai/codex/'+version,timeout=30))
 if metadata.get('name')!='@openai/codex' or metadata.get('version')!=version:raise RuntimeError('Unexpected official package identity')
 integrity=metadata['dist']['integrity'];algorithm,digest=integrity.split('-',1)
 if algorithm!='sha512':raise RuntimeError('SHA-512 package integrity is required')
 url=metadata['dist']['tarball']
 if not url.startswith('https://registry.npmjs.org/@openai/codex/-/'):raise RuntimeError('Unexpected package host')
 with tempfile.TemporaryDirectory(prefix='install-',dir=base) as d:
  archive=pathlib.Path(d)/'codex.tgz';checksum=hashlib.sha512();total=0
  with urllib.request.urlopen(url,timeout=60) as source,archive.open('wb') as out:
   while True:
    chunk=source.read(1024*1024)
    if not chunk:break
    total+=len(chunk)
    if total>300_000_000:raise RuntimeError('Package download limit exceeded')
    checksum.update(chunk);out.write(chunk)
  if base64.b64encode(checksum.digest()).decode()!=digest:raise RuntimeError('Package integrity check failed')
  extracted=pathlib.Path(d)/'extracted';extracted.mkdir();size=0
  with tarfile.open(archive,'r:gz') as tar:
   for member in tar:
    parts=pathlib.PurePosixPath(member.name).parts
    if not parts or parts[0]!='package' or '..' in parts or member.issym() or member.islnk():raise RuntimeError('Unsafe package path')
    if not member.isfile() or len(parts)<2 or parts[1]!='vendor':continue
    size+=member.size
    if size>600_000_000:raise RuntimeError('Package extraction limit exceeded')
    target=extracted.joinpath(*parts[1:]);target.parent.mkdir(parents=True,exist_ok=True)
    with tar.extractfile(member) as source,target.open('xb') as out:shutil.copyfileobj(source,out)
    target.chmod(0o755 if member.mode&0o111 else 0o644)
  if not (extracted/'vendor/x86_64-unknown-linux-musl/bin/codex').is_file():raise RuntimeError('Native Linux Codex binary missing')
  folder.parent.mkdir(exist_ok=True)
  if folder.exists():raise RuntimeError('Incomplete existing installation; inspect it before retrying')
  extracted.rename(folder)
version_out=subprocess.check_output([str(exe),'--version'],text=True).strip()
print(json.dumps({'binary':str(exe),'home':str(base/'codex-home'),'version':version_out}))
'''


def install(config, approved=False):
    if not approved:
        raise ValueError('Owner approval is required for WSL package installation and ChatGPT login reuse')
    # Query resources/tools first. On VM startup failure, do not install or copy authentication.
    status = wsl_runtime.python(config, "import json,os,shutil; print(json.dumps({'home':os.path.expanduser('~'),'bwrap':shutil.which('bwrap')}))")
    if not status['home'].startswith('/home/'):
        raise RelayError('environment.wsl_user', 'WSL2 setup', 'Choose a normal Ubuntu user; installing the relay as root is unsupported.')
    if not status['bwrap']:
        wsl_runtime.call(config, ['/usr/bin/apt-get', 'update'], timeout=180, user='root')
        wsl_runtime.call(config, ['/usr/bin/apt-get', 'install', '-y', '--no-install-recommends', 'bubblewrap', 'ca-certificates'], timeout=180, user='root')
    result = wsl_runtime.python(config, INSTALL, {}, timeout=180)
    candidate = replace(config, execution_backend='wsl', wsl_home=result['home'], wsl_binary=result['binary'])
    candidate.validate()
    verified = Codex(candidate).doctor()  # Requires strict profile success, never selects a broad fallback.
    if (config.data_dir / 'config.json').is_file():
        import shutil
        folder = config.data_dir / 'repair-backups' / ('pre-wsl-activation-' + str(time.time_ns()))
        folder.mkdir(parents=True)
        shutil.copy2(config.data_dir / 'config.json', folder / 'config.json')
    candidate.save()  # Switch backend only after sign-in and secure sandbox verification.
    return {'installation': result['version'], **verified}


def main():
    parser = argparse.ArgumentParser(description='Set up secure Codex execution in the existing Ubuntu WSL2 distribution')
    parser.add_argument('--approve-installation', action='store_true', help='Approve official Codex, Ubuntu sandbox packages and private ChatGPT login reuse')
    parser.add_argument('--data-dir')
    args = parser.parse_args()
    if not args.approve_installation:
        parser.error('Explicit --approve-installation is required')
    config = Config.load(args.data_dir)
    with InstanceLock(config.data_dir):
        print('Checking WSL2 availability before installing anything or copying authentication.', flush=True)
        try:
            print(json.dumps(install(config, approved=True), indent=2))
        except RelayError as error:
            record(config.data_dir, error)
            print(str(error))
            raise SystemExit(1)


if __name__ == '__main__':
    main()
