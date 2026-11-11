"""Visible launcher front-end; hidden server startup is logged and health checked."""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time
import webbrowser

import serve_browser as service

ROOT=Path(__file__).resolve().parents[1]


def ensure_service(root: Path,port: int,timeout: float=10):
    if service.probe(port,root):return None
    local=root/'.local'
    if local.is_symlink() or local.exists() and getattr(local.stat(follow_symlinks=False),'st_file_attributes',0)&0x400:
        raise RuntimeError('The local startup-log folder must not be a link.')
    local.mkdir(exist_ok=True)
    logpath=local/'browser-startup.log'
    if logpath.is_symlink() or logpath.exists() and logpath.stat().st_nlink>1:
        raise RuntimeError('The startup log must be an ordinary private local file.')
    with logpath.open('ab') as log:
        log.write(('\n'+datetime.now().isoformat(timespec='seconds')+' Starting local portfolio service\n').encode())
        log.flush()
        child=subprocess.Popen([sys.executable,str(ROOT/'tools/serve_browser.py'),'--root',str(root),'--port',str(port)],
            cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),close_fds=True)
        log.write(('Started process '+str(child.pid)+'\n').encode());log.flush()
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if service.probe(port,root):return child
        if child.poll() is not None:
            # A concurrent intentional launch may have won the single listener.
            if service.probe(port,root):return child
            raise RuntimeError('The service stopped during startup. See '+str(logpath))
        time.sleep(.15)
    raise RuntimeError('The service did not become ready. It may still be starting; check '+str(logpath)+' before retrying.')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--port',type=int,default=service.DEFAULT_PORT)
    args=parser.parse_args(argv);root=args.root.resolve();url=f'http://127.0.0.1:{args.port}/'
    try:
        if sys.version_info<(3,10):raise RuntimeError('Python 3.10 or newer is required.')
        if not 1<=args.port<=65535:raise RuntimeError('Invalid local service port.')
        ensure_service(root,args.port)
        # Every intentional launcher invocation requests the page. Browser reuse
        # is best-effort; tab presence cannot be detected reliably here.
        if not webbrowser.open(url,new=0):raise RuntimeError('The default browser did not open. Open '+url+' manually.')
        print('Opened Business Portfolio at '+url)
        return 0
    except Exception as error:
        print('Business Portfolio could not open: '+str(error),file=sys.stderr)
        print('Startup details, when available: '+str(root/'.local/browser-startup.log'),file=sys.stderr)
        return 1
if __name__=='__main__':raise SystemExit(main())
