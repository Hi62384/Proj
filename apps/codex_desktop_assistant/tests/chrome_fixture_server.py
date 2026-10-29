"""Disposable localhost sites for the installed extension's live acceptance.

No authentication, external endpoints, shell, or arbitrary-file handler.
"""
import argparse
import hashlib
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from assistant.storage import private_directory


class Site(BaseHTTPRequestHandler):
    state={'submissions':0,'uploads':0,'publication_requests':0,'purchase_requests':0,'last_upload_bytes':0,'expected_bytes_found':False}
    expected=b'CODEX-CHROME-SYNTHETIC-UPLOAD\x00\xff'*12000
    lock=threading.Lock();directory=None
    def log_message(self,*args):pass
    def respond(self,body,kind='text/html; charset=utf-8'):
        raw=body.encode('utf-8') if isinstance(body,str) else body
        self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=='/state':return self.respond(json.dumps(self.state),'application/json')
        # Only disposable fixture paths are recorded; never external URLs or headers.
        if path.startswith(('/created-','/clean-')):
            with self.lock:
                visits=self.state.setdefault('visits',{});visits[path]=visits.get(path,0)+1
                (self.directory/'server-results.json').write_text(json.dumps(self.state,indent=2))
        if path.startswith('/clean-'):return self.respond('<title>Chrome verification — clean disposable tab</title><h1>Disposable clean tab</h1><p>No forms, editors or external requests.</p>')
        if path=='/human':return self.respond('<title>Chrome verification — human tab</title><h1>Your independent test tab</h1><label>Human notes<input autofocus></label><p>This page contains only synthetic test data.</p>')
        if path=='/frame':return self.respond('<title>Embedded fixture</title><label>Embedded notes<textarea></textarea></label>')
        if path=='/accepted':return self.respond('<title>Synthetic form accepted</title><h1>Synthetic form accepted</h1><a href=/work>Return to work fixture</a>')
        self.respond('''<!doctype html><meta charset=utf-8><title>Chrome verification — work tab</title>
<h1>Codex Chrome synthetic work fixture</h1><p>All text and actions here are disposable local test data.</p>
<label>Notes<textarea></textarea></label><div contenteditable=true aria-label="Rich editor">Initial rich text</div>
<label>Theme<select><option value=teal>Teal</option><option value=blue>Blue</option></select></label>
<label>Reviewed<input type=checkbox></label><button type=button aria-expanded=false onclick="this.setAttribute('aria-expanded','true');document.querySelector('#result').textContent='Expanded successfully'">Expand</button>
<p id=result>Not expanded</p><div id=shadow></div><script>document.querySelector('#shadow').attachShadow({mode:'open'}).innerHTML='<label>Shadow notes<textarea></textarea></label>';</script>
<iframe src=/frame></iframe><table><tr><th>Item</th><th>Count</th></tr><tr><td>Maple</td><td>42</td></tr></table>
<form action=/accepted method=post><label>Synthetic form notes<input name=notes></label><button>Submit synthetic form</button></form>
<form action=/upload method=post enctype=multipart/form-data><label>Fixture file<input type=file name=fixture></label><button>Upload synthetic fixture</button></form>
<button type=button onclick="fetch('/publish',{method:'POST'})">Publish product</button>
<button type=button onclick="fetch('/purchase',{method:'POST'})">Buy now</button>
<p id=native></p><script>
document.querySelector('#native').textContent='Native messaging visible to webpage: '+Boolean(globalThis.chrome?.runtime?.connectNative);
let captureTimer;
function capture(){clearTimeout(captureTimer);captureTimer=setTimeout(()=>fetch('/capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({notes:document.querySelector('textarea').value,rich:document.querySelector('[contenteditable]').innerText,theme:document.querySelector('select').value,reviewed:document.querySelector('input[type=checkbox]').checked,shadow:document.querySelector('#shadow').shadowRoot.querySelector('textarea').value,expanded:document.querySelector('#result').innerText})}),30);}
for(const event of ['input','change','click']){document.addEventListener(event,capture);document.querySelector('#shadow').shadowRoot.addEventListener(event,capture);}
capture();</script>''')
    def do_POST(self):
        raw=self.rfile.read(int(self.headers.get('Content-Length',0)))
        with self.lock:
            if self.path=='/capture':
                try:self.state['dom']=json.loads(raw)
                except ValueError:pass
            elif self.path=='/accepted':self.state['submissions']+=1
            elif self.path=='/upload':self.state.update(uploads=self.state['uploads']+1,last_upload_bytes=len(raw),expected_bytes_found=self.expected in raw)
            elif self.path=='/publish':self.state['publication_requests']+=1
            elif self.path=='/purchase':self.state['purchase_requests']+=1
            (self.directory/'server-results.json').write_text(json.dumps(self.state,indent=2))
        if self.path=='/upload':return self.respond('<title>Synthetic upload accepted</title><h1>Synthetic upload accepted</h1><p>Expected bytes verified: '+str(self.state['expected_bytes_found'])+'</p><a href=/work>Return to work fixture</a>')
        return self.respond('<title>Synthetic form accepted</title><h1>Synthetic form accepted</h1><a href=/work>Return to work fixture</a>')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--approve-synthetic-tests',action='store_true');parser.add_argument('--directory',required=True);parser.add_argument('--ports',nargs=2,type=int,default=[0,0]);args=parser.parse_args()
    if not args.approve_synthetic_tests:raise SystemExit('Explicit synthetic-test opt-in required')
    directory=Path(args.directory).resolve()
    if not directory.is_relative_to((private_directory()/'verification').resolve()):raise SystemExit('Use a private verification directory')
    directory.mkdir(parents=True,exist_ok=True);Site.directory=directory
    servers=[ThreadingHTTPServer(('127.0.0.1',port),Site) for port in args.ports]
    for server in servers:threading.Thread(target=server.serve_forever,daemon=True).start()
    fixture=directory/'synthetic-upload.bin';fixture.write_bytes(Site.expected)
    info={'work':f'http://127.0.0.1:{servers[0].server_port}/work','human':f'http://localhost:{servers[1].server_port}/human','file':str(fixture),'sha256':hashlib.sha256(Site.expected).hexdigest(),'pid':__import__('os').getpid()}
    (directory/'fixture.json').write_text(json.dumps(info,indent=2));(directory/'server-results.json').write_text(json.dumps(Site.state,indent=2));print(json.dumps(info),flush=True)
    # Bounded lifetime; no recurring server is installed.
    try:threading.Event().wait(3600)
    finally:
        for server in servers:server.shutdown();server.server_close()


if __name__=='__main__':main()
