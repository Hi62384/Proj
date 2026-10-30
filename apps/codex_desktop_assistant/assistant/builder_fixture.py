"""Explicitly opted-in, disposable Payhip-like draft-builder acceptance website."""
import json
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import parse_qs,urlsplit

PAGE='''<!doctype html><meta charset=utf-8><title>Disposable Store Builder</title>
<style>body{font:16px system-ui;background:#f1f5f9;margin:0;color:#172033}aside{width:190px;background:#142133;color:white;padding:20px;float:left;height:90vh}.item{padding:14px;cursor:pointer;border-radius:8px}.item:hover{background:#34445a}main{margin-left:250px;padding:28px}button,input,textarea,select{font:inherit;padding:9px}.swatch{display:inline-block;width:38px;height:38px;cursor:pointer;border-radius:50%;border:3px solid white;margin:5px}#preview{padding:24px;background:#334155;color:white;border-radius:12px}#hover{cursor:pointer;padding:12px;background:#dbeafe;display:inline-block}</style>
<aside><h2>Store design</h2><div class=item role=button tabindex=0 aria-controls=about-panel onclick="document.querySelector('#about-panel').hidden=false">About Me</div><div class=item role=button tabindex=0 aria-controls=colors-panel onclick="document.querySelector('#colors-panel').hidden=false">Colors</div><div class=item onclick="document.querySelector('#layout-panel').hidden=false" aria-label="Layout controls">Layout</div></aside>
<main><h1>Design the synthetic store</h1><p>Disposable test data. No account, public storefront or money.</p>
<section id=about-panel hidden><h2>About Me</h2><div contenteditable=true aria-label="About text">Original about text</div></section>
<section id=colors-panel hidden><h2>Brand colors</h2><span class=swatch style="background:#0f766e" aria-label="Teal swatch" onclick="document.querySelector('#color').value='#0f766e';update()"></span><span class=swatch style="background:#7c3aed" aria-label="Violet swatch" onclick="document.querySelector('#color').value='#7c3aed';update()"></span><label>Brand color<input id=color type=color value=#334155 onchange=update()></label></section>
<section id=layout-panel hidden><h2>Layout</h2><span role=button aria-controls=choices aria-expanded=false onclick="document.querySelector('#choices').hidden=!document.querySelector('#choices').hidden;this.setAttribute('aria-expanded',String(!document.querySelector('#choices').hidden))">Choose layout</span><div id=choices role=listbox hidden><div role=option tabindex=0 style="cursor:pointer" onclick="document.querySelector('#layout').value='Editorial';document.querySelector('#choices').hidden=true;update()">Editorial layout</div><div role=option tabindex=0 onclick="document.querySelector('#layout').value='Grid';update()">Grid layout</div></div><input id=layout type=hidden value=Grid></section>
<span id=hover aria-label="Show spacing menu" onmouseenter="document.querySelector('#hover-menu').hidden=false">Spacing</span><div id=hover-menu role=menu hidden><span role=menuitem style="cursor:pointer" onclick="document.querySelector('#spacing').value='Comfortable';update()">Comfortable spacing</span></div><input id=spacing type=hidden value=Compact>
<form id=synthetic-draft action=/save-draft method=post><input type=hidden name=visibility value=draft><input type=hidden name=color><input type=hidden name=layout><input type=hidden name=about><button>Save draft</button></form><button type=button onclick="fetch('/publish',{method:'POST'})">Publish</button><button type=button onclick="fetch('/pay',{method:'POST'})">Pay now</button>
<p id=status>Not saved</p><div id=preview>Preview</div></main>
<script>function state(){return {color:document.querySelector('#color').value,layout:document.querySelector('#layout').value,spacing:document.querySelector('#spacing').value,about:document.querySelector('[contenteditable]').innerText}}
function update(){const s=state();document.querySelector('#preview').style.background=s.color;document.querySelector('#preview').textContent=s.layout+' / '+s.spacing+' / '+s.about;fetch('/capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(s)});for(const name of ['color','layout','about'])document.querySelector('[name='+name+']').value=s[name]}
document.addEventListener('input',update);document.querySelector('form').addEventListener('submit',async e=>{e.preventDefault();update();const r=await fetch('/save-draft',{method:'POST',body:new URLSearchParams(new FormData(e.target))});if(r.ok)document.querySelector('#status').textContent='Unpublished draft saved'});update();</script>'''


class BuilderFixture:
    def __init__(self):
        self.state={'draft_saves':0,'publication_requests':0,'payment_requests':0};self.lock=threading.RLock();self.closed=False;owner=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def send(self,data,kind='application/json'):
                raw=data.encode();self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
            def do_GET(self):
                if self.path=='/human':
                    return self.send('''<!doctype html><meta charset=utf-8><title>Disposable human keyboard test</title><h1>Human input test</h1><textarea aria-label="Human notes" autofocus></textarea><script>document.querySelector('textarea').addEventListener('input',e=>fetch('/human-capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:e.target.value,trusted:e.isTrusted})}));</script>''','text/html; charset=utf-8')
                self.send(json.dumps(owner.state) if self.path=='/state' else PAGE,'application/json' if self.path=='/state' else 'text/html; charset=utf-8')
            def do_POST(self):
                size=min(20000,int(self.headers.get('Content-Length','0')));raw=self.rfile.read(size)
                with owner.lock:
                    if self.path=='/human-capture':owner.state['human']=json.loads(raw);owner.state['human_input_events']=owner.state.get('human_input_events',0)+1
                    elif self.path=='/capture':owner.state['dom']=json.loads(raw)
                    elif self.path=='/save-draft':
                        data=parse_qs(raw.decode())
                        if data.get('visibility')!=['draft']:self.send_error(403);return
                        owner.state['draft_saves']+=1;owner.state['saved']=data
                    elif self.path=='/publish':owner.state['publication_requests']+=1
                    elif self.path=='/pay':owner.state['payment_requests']+=1
                self.send('{}')
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.url='http://127.0.0.1:'+str(self.server.server_port)+'/builder'
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def close(self):
        if self.closed:return
        self.closed=True;self.server.shutdown();self.server.server_close()
