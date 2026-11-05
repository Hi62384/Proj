"""Read-only local portfolio view. Standard library; no accounts or automation queue."""
from __future__ import annotations
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import re
import socket
import threading
import time
from urllib.parse import urlsplit
import urllib.error
import urllib.request
import webbrowser

import build_browser as builder

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 22841
SERVICE = 'proj-business-portfolio-v1'
DENIED_PARTS = {'.git', '.local', '.tmp', '.codex', '.agents', '.aws', 'private', 'node_modules', '__pycache__'}
# Deliberately no generic repository file server or recursive directory listing.
# Only these documented, non-sensitive guides can be served as local results.
GUIDES = {
    'EX-001': [('Cleaning product guide', 'products/cleaning-pricing-calculator/README.md', 'Source guide; customer ZIP remains private.')],
    'EX-003': [('Store links', 'outputs/payhip-launch-2026-10-30/CURRENT_LINKS.json', 'Public store links, not an account or receipt.')],
    'EX-007': [('Computer Bridge guide', 'apps/codex_desktop_assistant/COMPUTER_BRIDGE.md', 'Source documentation; not a new application build.')],
    'EX-010': [('Opportunity Library guide', 'opportunity_library/README.md', 'Existing research source guide.')],
    'EX-011': [('Factory guide', 'portfolio_autopilot/factory/README.md', 'Source guide; runtime state is private.')],
    'SYS-001': [('Project format', 'business_portfolio/SCHEMA.md', 'Local project-system documentation.')],
}
PUBLIC_LINKS = {'EX-001': ('Published Cleaning product', 'https://payhip.com/b/bP6YN'),
                'EX-002': ('Published Inventory product', 'https://payhip.com/b/dotFZ'),
                'EX-003': ('Published store', 'https://payhip.com/ArshyaGhafaryan')}

def result_file(root: Path, ident: str, relative: str) -> Path | None:
    parts = Path(relative).parts
    if len(parts)<3 or parts[:2]!=('results',ident) or Path(relative).suffix.lower() not in {'.md','.txt','.csv','.json'}:
        return None
    try:
        file=safe_file(root,relative)
        if file is None:return None
        raw=file.read_bytes()
        if len(raw)>2_000_000 or b'\x00' in raw:return None
        text=raw.decode('utf-8')
        if re.search(r'-----BEGIN .*PRIVATE KEY-----|\bghp_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}|\bAKIA[0-9A-Z]{16}\b|https://payhip\.com/d/l/|https?://[^\s/]+:[^\s/]+@',text):return None
        return file
    except (OSError,UnicodeError):return None


def safe_file(repo: Path, relative: str) -> Path | None:
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or any(p.lower() in DENIED_PARTS or p.startswith('.') for p in path.parts):
        return None
    candidate = repo/path
    # Check each ancestor before resolve; junctions/reparse points are not public sources.
    for part in [candidate, *candidate.parents]:
        if part == repo.parent:
            break
        if part.is_symlink() or getattr(part.stat(follow_symlinks=False), 'st_file_attributes', 0) & 0x400:
            return None
    try:
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(repo.resolve()) or not resolved.is_file() or resolved.stat().st_nlink > 1:
            return None
        return resolved
    except OSError:
        return None


def public_results(root: Path, data: dict) -> tuple[dict, dict]:
    results, files = {}, {}
    repo = root.parent
    for record in data['records']:
        ident = record['id']; rows = []
        for title, relative, note in GUIDES.get(ident, []):
            try:
                actual = safe_file(repo, relative)
            except OSError:
                actual = None
            key = hashlib.sha256((ident + ':' + relative).encode()).hexdigest()[:24]
            rows.append(dict(label=title, kind='Source/documentation', note=note+' Folder: '+str(Path(relative).parent).replace('\\','/'), available=actual is not None, key=key))
            if actual:
                files[key] = (actual, relative)
        if ident in PUBLIC_LINKS:
            title, url = PUBLIC_LINKS[ident]; rows.append(dict(label=title,url=url,note='Public listing; paid customer demand remains unverified.'))
        if ident in {'EX-001','EX-002'}:
            rows.append(dict(label='Customer release ZIP',available=False,note='Preserved privately. Paid product archives and buyer download links are not exposed by this browser.'))
        if ident == 'EX-004':
            rows.append(dict(label='Private demo video',available=False,note='Reported in the saved record; its private file has not been verified here.'))
        for entry in record.get('public_results',[]):
            relative=entry['path'];actual=result_file(root,ident,relative)
            key=hashlib.sha256((ident+':result:'+relative).encode()).hexdigest()[:24]
            row=dict(label=entry['label'],kind='Public project result',key=key,available=actual is not None,
                     note='Public text result.' if actual else 'Missing or not eligible for local sharing. Private paths and binary releases stay protected.')
            if actual:
                raw=actual.read_bytes();row.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest());files[key]=(actual,relative,ident)
            rows.append(row)
        canonical=root.name+'/'+record['path']
        source_key=hashlib.sha256((ident+':record:'+canonical).encode()).hexdigest()[:24]
        try:source=safe_file(repo,canonical)
        except OSError:source=None
        rows.append(dict(label='Saved project instructions',kind='Planning/source record',key=source_key,
                         available=source is not None,note='Canonical Markdown record; this is planning documentation, not a completed commercial deliverable.'))
        if source:files[source_key]=(source,canonical)
        results[ident] = rows
    return results, files


def fingerprint(root: Path) -> tuple:
    entries = []
    # Only public canonical inputs are watched; never follow links or private trees.
    for start in [root/'niches', root/'research', root/'tools',root/'results']:
        if start.exists() and builder.linked_input(start):raise ValueError('Linked input root refused')
        for directory, dirs, names in os.walk(start, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d.lower() not in DENIED_PARTS)
            for d in dirs:
                p=Path(directory)/d
                if p.is_symlink() or getattr(p.stat(follow_symlinks=False),'st_file_attributes',0)&0x400:
                    raise ValueError('Linked input refused')
            for name in sorted(names):
                p=Path(directory)/name
                if p.suffix.lower() not in {'.md','.json','.html','.py','.txt','.csv'}:continue
                if p.is_symlink() or getattr(p.stat(follow_symlinks=False),'st_file_attributes',0)&0x400:
                    raise ValueError('Linked input refused')
                stat=p.stat();entries.append((str(p.relative_to(root)),stat.st_mtime_ns,stat.st_size))
    for name in ['README.md','SCHEMA.md','QA_REPORT.md','CODEX_IMPLEMENTATION_PROMPT.md','REPO_PLACEMENT.md','INTEGRATION_STATUS.md']:
        p=root/name
        if p.is_file():
            if builder.linked_input(p):raise ValueError('Linked document refused')
            stat=p.stat();entries.append((name,stat.st_mtime_ns,stat.st_size))
    # Observe availability of explicit guide results without discovering other files.
    for rows in GUIDES.values():
        for _, relative, _ in rows:
            p=root.parent/relative
            try:
                stat=p.stat();entries.append(('guide:'+relative,stat.st_mtime_ns,stat.st_size))
            except OSError:entries.append(('guide:'+relative,None,None))
    return tuple(sorted(entries))


class PortfolioState:
    def __init__(self, root: Path):
        self.root=root.resolve();self.lock=threading.RLock();self.stop=threading.Event()
        self.data={};self.files={};self.version='';self.warning='';self.signature=None;self.template=''
        if not self.refresh():raise ValueError('Cannot start: canonical project records are invalid.')

    def refresh(self) -> bool:
        try:
            before=fingerprint(self.root)
            data=builder.load_portfolio(self.root)
            template_path=self.root/'tools/browser_template.html'
            if builder.linked_input(template_path):raise ValueError('Linked template refused')
            template=template_path.read_text(encoding='utf-8')
            with self.lock:
                previous={r['id']:r for r in self.data.get('records',[])};has_snapshot=bool(self.version)
            for record in data['records']:
                record['modified_at']=str((self.root/record['path']).stat().st_mtime_ns)
                prior=previous.get(record['id'])
                if prior and (prior['content_sha256']!=record['content_sha256'] or prior['path']!=record['path']):
                    record['recently_saved_at']=time.time_ns()
                elif prior:
                    record['recently_saved_at']=prior.get('recently_saved_at',0)
                elif has_snapshot:
                    record['recently_saved_at']=time.time_ns()
                else:
                    # Imported archive timestamps are not evidence of recent work.
                    checkpoint=record.get('local_reconciliation') or record.get('local_integration')
                    record['recently_saved_at']=min(int(record['modified_at']),time.time_ns()) if checkpoint else 0
            data['deliverables'],files=public_results(self.root,data)
            if before!=fingerprint(self.root):raise ValueError('Concurrent writes')
            raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
            version=hashlib.sha256(raw).hexdigest()
            with self.lock:
                self.data=data;self.files=files;self.version=version;self.warning='';self.signature=before;self.template=template
            return True
        except (OSError,ValueError,KeyError,TypeError):
            # Never send filesystem exception strings, absolute paths or partial data to the UI.
            with self.lock:self.warning='Incomplete or invalid edits; last valid snapshot retained.'
            return False

    def watch(self):
        pending=None
        while not self.stop.wait(.5):
            try:current=fingerprint(self.root)
            except (OSError,ValueError):
                with self.lock:self.warning='Incomplete or linked input; last valid snapshot retained.'
                continue
            if current==self.signature:
                pending=None
                continue
            if current!=pending:
                pending=current
                continue
            self.refresh()

    def snapshot(self):
        with self.lock:return self.data,self.version,self.warning


class LocalServer(ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=os.name!='nt'
    def server_bind(self):
        if os.name=='nt' and hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()
    def __init__(self,address,state):
        self.state=state
        super().__init__(address,Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send(self,status,body,kind='application/json; charset=utf-8',attachment=False):
        if isinstance(body,str):body=body.encode('utf-8')
        self.send_response(status);self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        if attachment:self.send_header('Content-Disposition','attachment')
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        port=self.server.server_port
        hosts={f'127.0.0.1:{port}',f'localhost:{port}'}
        origins={f'http://{h}' for h in hosts}
        if self.headers.get('Host') not in hosts or self.headers.get('Origin') not in origins|{None}:
            self.send(403,'Forbidden','text/plain');return
        if self.headers.get('Sec-Fetch-Site') not in {None,'none','same-origin'}:
            self.send(403,'Forbidden','text/plain');return
        state=self.server.state;route=urlsplit(self.path).path
        if route=='/api/health':
            self.send(200,json.dumps({'service':SERVICE,'root_id':hashlib.sha256(str(state.root).encode()).hexdigest()}));return
        data,version,warning=state.snapshot()
        if route=='/api/state':self.send(200,json.dumps(dict(version=version,warning=warning)));return
        if route=='/api/portfolio':self.send(200,json.dumps(data,ensure_ascii=False));return
        if route in {'/','/PROJECT_BROWSER.html'}:
            with state.lock:template=state.template
            self.send(200,builder.render_browser(data,template),'text/html; charset=utf-8');return
        if route.startswith('/files/'):
            key=route.removeprefix('/files/')
            with state.lock:entry=state.files.get(key)
            if entry:
                file,relative,*ident=entry
                try:
                    current=result_file(state.root,ident[0],relative) if ident else safe_file(state.root.parent,relative)
                    if current!=file:raise OSError()
                    raw=current.read_bytes()
                    if len(raw)>2_000_000:raise OSError()
                    self.send(200,raw,'text/plain; charset=utf-8');return
                except OSError:pass
        allowed = {r['path'] for r in data['records']} | {d['path'] for d in data['documents']}
        relative = route.removeprefix('/')
        if relative in allowed:
            try:
                current = safe_file(state.root, relative)
                if current:
                    self.send(200,current.read_bytes(),'text/plain; charset=utf-8');return
            except OSError:pass
        self.send(404,'Not found','text/plain')
    def do_POST(self):self.send(405,'Read only','text/plain')
    do_PUT=do_DELETE=do_PATCH=do_POST


def probe(port:int,root:Path)->bool:
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f'http://127.0.0.1:{port}/api/health',timeout=1) as response:d=json.load(response)
        return d=={'service':SERVICE,'root_id':hashlib.sha256(str(root.resolve()).encode()).hexdigest()}
    except (OSError,ValueError,urllib.error.URLError):return False


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--port',type=int,default=DEFAULT_PORT);parser.add_argument('--open',action='store_true')
    args=parser.parse_args();root=args.root.resolve();url=f'http://127.0.0.1:{args.port}/'
    if probe(args.port,root):
        if args.open and not webbrowser.open(url,new=0):
            raise RuntimeError('Could not open the default browser. Open '+url+' manually.')
        print('Portfolio is already running at '+url);return 0
    state=PortfolioState(root)
    try:server=LocalServer(('127.0.0.1',args.port),state)
    except OSError:
        if probe(args.port,root):
            if args.open and not webbrowser.open(url,new=0):
                raise RuntimeError('Could not open the default browser. Open '+url+' manually.')
            return 0
        raise SystemExit('Port is occupied by another service; no duplicate server was started.')
    threading.Thread(target=state.watch,daemon=True).start()
    if args.open and not webbrowser.open(url,new=0):
        state.stop.set();server.server_close()
        raise RuntimeError('Could not open the default browser. Open '+url+' manually.')
    print('Portfolio live at '+url,flush=True)
    try:server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:pass
    finally:state.stop.set();server.server_close()
    return 0
if __name__=='__main__':raise SystemExit(main())
