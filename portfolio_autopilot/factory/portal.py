"""Local-only control panel: browse ideas, prepare draft kits, review queue.

The server never accepts customer files, secrets, payment information or
outbound marketing instructions; it has no network clients or live providers.
"""
from __future__ import annotations
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit, unquote
import webbrowser

from .catalog import catalog, select
from .config import PRIVATE, ROOT, SetupError, bootstrap, load_profile, safe_id
from .kits import make_kit
from .first_business import first_business, FILES as FIRST_FILES
from .storefront import create_preview
from .ledger import (create_tasks, get_tasks, finish_task, get_approvals,
                     resolve_approval, summary)


def load_view(root: Path = PRIVATE, rows: list[dict]|None=None) -> dict:
    rows=rows if rows is not None else catalog()
    chosen=select(rows,limit=18,per_mode=3)
    finance=summary(root)
    generated={p.parent.name for p in (root/'launchkits').glob('*/README.md')}
    def compact(r):
        return {'id':r['id'],'name':r.get('name',''),'niche':r.get('niche',''),
                'mode':r.get('revenue_mode',''),'score':r.get('cross_niche_score',''),
                'category':r.get('library_category',''), 'category_id':r.get('library_category_id',''),
                'passivity':r.get('library_passivity',''), 'privacy':r.get('library_privacy',''),
                'evidence':r.get('evidence_grade',''),
                'price':r.get('illustrative_price_cad',''),
                'risk':r.get('legal_class',''),'kit_exists':r['id'] in generated}
    return {'not_live':'Local planning only. No customer, sale, payment, market demand or provider connection is verified.',
            'catalog_records':len(rows), 'shortlist':[compact(r) for r in chosen],
            'all_offers':[compact(r) for r in rows], 'summary':finance,
            'tasks':get_tasks(root), 'approvals':get_approvals(root),
            'first_business_exists':(root/'first_reporting_business'/'00_START_HERE.md').exists(),
            'catalogue_preview_exists':(root/'previews'/'catalogue.html').exists()}


_STYLES='''
:root{color-scheme:dark;--bg:#090f1c;--surface:#132035;--border:#31445d;--txt:#eaf1fc;--muted:#a4b4cd;--highlight:#73cdff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}header{border-bottom:1px solid var(--border);background:#101b2d}main,header>div{margin:auto;max-width:1280px;padding:24px}h1{margin:4px 0;font-size:32px;letter-spacing:-.025em}h2{font-size:20px;margin:8px 0 16px}h3{font-size:16px;margin:0 0 8px}p{color:var(--muted)}strong{color:var(--txt)}.note{background:#28324a;border-left:3px solid #e9c976;padding:14px;border-radius:9px}.layout{display:grid;grid-template-columns:minmax(0,1fr) 350px;gap:20px}.panel{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:20px;margin-bottom:18px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.stat{padding:16px;border:1px solid var(--border);border-radius:12px}.stat b{display:block;font-size:25px}.stat span{font-size:12px;color:var(--muted)}button,input,select{font:inherit;border-radius:9px}button{cursor:pointer;background:#194c76;border:1px solid #418bbe;color:#eaf1fc;padding:7px 12px;min-height:36px}button:hover{background:#26699e}button:disabled{opacity:.5;cursor:not-allowed}input,select{background:#0d1829;color:var(--txt);border:1px solid var(--border);padding:11px;width:100%;margin-bottom:12px}.filters{display:grid;grid-template-columns:1fr 1fr;gap:10px}.idea{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:13px 0;border-bottom:1px solid var(--border)}.idea h3{margin:0 0 3px}.meta{color:var(--muted);font-size:12px}.bad{color:#ffbeac}.ok{color:#a5e5ac}.actions{display:flex;gap:8px;flex-wrap:wrap}.small{font-size:12px}a{color:#9cdbff}#notice{min-height:22px;font-size:13px;color:#c0e6ad;overflow-wrap:anywhere}.task{padding:10px 0;border-bottom:1px solid var(--border)}.label{font-size:11px;letter-spacing:.12em;font-weight:700;color:#b8daff}@media(max-width:900px){.layout{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
'''

def render_page(state: dict, csrf_token: str) -> str:
    payload=json.dumps(state,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    token=json.dumps(csrf_token)
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portfolio Autopilot — Local Workbench</title><style>'''+_STYLES+'''</style></head><body>
<header><div><div class="label">OFFLINE BUSINESS FACTORY · NO LIVE ACCOUNTS</div><h1>Portfolio Autopilot</h1><p>Prepare, validate and review business launch kits across every niche. Your private files stay on this computer.</p></div></header>
<main><p class="note"><strong>Draft mode:</strong> No external API calls, storefront publication, email, payment processing, paid ads or customer data access. Prices, scores and buyer demand are not verified.</p>
<div class="stats" id="stats"></div><div class="layout"><section>
<div class="panel"><h2>Explore opportunities across industries</h2><p><a href="/opportunity-library" target="_blank" rel="noopener">Open the organized Opportunity Library →</a></p><div class="filters"><select id="scope" aria-label="Which opportunities"><option value="shortlist">Top cross-industry shortlist</option><option value="all">All installed research records</option></select><select id="model" aria-label="Income model"><option value="">Any income model</option><option value="F">Fixed-scope services</option><option value="R">Recurring monitoring</option><option value="D">Digital downloads</option><option value="I">Integrations</option><option value="M">Micro SaaS</option><option value="P">Paid data</option><option value="A">Original assets</option><option value="L">Courses</option><option value="C">Affiliate/content</option><option value="X">Marketplaces</option><option value="ORIGINAL">Original studies</option></select><select id="category-filter" aria-label="Category"><option value="">All research categories</option></select></div><input id="search" type="search" placeholder="Search all industries, IDs, offers or models" aria-label="Filter opportunity list"/><p id="matches" class="small"></p><div id="ideas"></div></div>
<div class="panel"><h2>Draft storefront generator</h2><p class="small">Preview every prepared offer in one local showcase. This does not publish a website or create checkout.</p><button id="catalogue">Create offline catalogue preview</button><p id="catalogue-status" class="small"></p></div><div class="panel"><h2>Review queue</h2><p class="small">These are local reminders, not tasks an AI is secretly doing.</p><div class="actions"><button id="refresh">Prepare review queue</button></div><div id="tasks"></div></div>
</section><aside><div class="panel"><h2>First business — CSV reports</h2><p class="small">A fully synthetic, runnable report demo and draft Upwork listing. No real account is connected.</p><button id="first">Prepare first sales pack</button><p id="first-status" class="small"></p><hr><h2>First steps</h2><ol><li>Choose a real buyer problem.</li><li>Prepare its draft kit.</li><li>Validate against actual buying intent.</li><li>Review the synthetic prototype.</li><li>Connect accounts only when you approve a launch.</li></ol><p class="small">A sales profile, a Stripe account and remote deployment are NOT included or connected here.</p></div>
<div class="panel"><h2>Approval requests</h2><p class="small">Reviewing here only marks a note locally. It cannot authorize an external action.</p><div id="approvals"></div></div>
<div class="panel"><h2>Local operations</h2><p id="ops"></p><p class="small">Financial entries are manually asserted and unreconciled—not bank balances or expected income. Never add confidential customer data here.</p></div></aside></div><p id="notice" role="status"></p></main>
<script id="initial" type="application/json">'''+payload+'''</script><script>
const csrf='''+token+''';let data=JSON.parse(document.getElementById('initial').textContent);const $=(s)=>document.querySelector(s);
function elem(tag,text,cls){const e=document.createElement(tag);e.textContent=String(text??'');if(cls)e.className=cls;return e}
function clear(el){while(el.firstChild)el.removeChild(el.firstChild)}
function formatCAD(v){const n=Number(v);return Number.isFinite(n)?'CAD '+n.toLocaleString('en-CA',{minimumFractionDigits:2,maximumFractionDigits:2}):String(v)}
async function post(path,body){let response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Factory-Token':csrf},body:JSON.stringify(body)});let obj=await response.json();if(!response.ok)throw Error(obj.error||'Request failed');return obj}
async function reload(){let response=await fetch('/api/state',{cache:'no-store'});data=await response.json();render()}
function notify(s,isBad=false){const n=$('#notice');n.textContent=s;n.style.color=isBad?'#ffb4a5':'#b1ecb7'}
function render(){
 const s=$('#stats');clear(s);const stats=[['Research records',data.catalog_records],['Shortlisted',data.shortlist.length],['Pending reviews',data.summary.pending_tasks],['Manual operating profit',formatCAD(data.summary.operating_profit_cad)]];
 stats.forEach(([a,b])=>{let v=elem('div','','stat');v.append(elem('b',b),elem('span',a));s.append(v)});
 const root=$('#ideas');clear(root);const term=$('#search').value.toLowerCase();const src=$('#scope').value==='all'?data.all_offers:data.shortlist;const mode=$('#model').value;const category=$('#category-filter').value;
 const matching=src.filter(r=>(!mode||r.mode===mode)&&(!category||r.category_id===category)&&[r.id,r.name,r.niche,r.mode,r.category].join(' ').toLowerCase().includes(term));
 $('#matches').textContent='Showing '+Math.min(60,matching.length)+' of '+matching.length+' matches. This is unvalidated research, not a list of buyers.';
 matching.slice(0,60).forEach(r=>{
   let card=elem('div','','idea'),copy=elem('div');copy.append(elem('h3',r.name),elem('div',r.id+' · '+(r.category?r.category+' · ':'')+r.niche+' · '+r.mode+' · score '+r.score,'meta'),elem('div',r.evidence+' · CAD '+r.price+' hypothesis','meta'));
   let act=elem('div','','actions'),blocked=r.risk!=='standard'&&r.risk!=='refer to original';let button=elem('button',blocked?'Needs risk review':r.kit_exists?'Kit created':'Prepare kit');button.disabled=r.kit_exists||blocked;
   button.onclick=async()=>{try{let out=await post('/api/kit',{id:r.id});notify('Prepared local draft for '+r.id+'. Open preview from the new link below.');await reload()}catch(e){notify(e.message,true)}};act.append(button);
   if(r.kit_exists){let l=elem('a','Preview');l.href='/preview/'+encodeURIComponent(r.id);l.target='_blank';l.rel='noopener';act.append(l)}card.append(copy,act);root.append(card)});
 const tasks=$('#tasks');clear(tasks);data.tasks.filter(t=>t.status==='pending').slice(0,20).forEach(t=>{let row=elem('div','','task');row.append(elem('div',t.business_id+' — '+t.headline,'small'));let b=elem('button','Mark reviewed');b.onclick=async()=>{try{await post('/api/review-task',{task_id:t.task_id});await reload()}catch(e){notify(e.message,true)}};row.append(b);tasks.append(row)});if(!tasks.childElementCount)tasks.append(elem('p','No pending review notes.'));
 const approvals=$('#approvals');clear(approvals);data.approvals.filter(x=>x.status==='pending').slice(0,10).forEach(x=>{let row=elem('div','','task');row.append(elem('b',x.action_name+' ('+x.business_id+')'),elem('p',x.details));let btn=elem('button','Mark locally reviewed');btn.onclick=async()=>{try{await post('/api/review-approval',{request_id:x.request_id});await reload()}catch(e){notify(e.message,true)}};row.append(btn);approvals.append(row)});if(!approvals.childElementCount)approvals.append(elem('p','No review requests.'));
 $('#first').disabled=data.first_business_exists;let box=$('#first-status');clear(box);box.append(elem('span',data.first_business_exists?'Sales pack prepared. ':'Requires one click. No account signup.'));if(data.first_business_exists){let link=elem('a','View checklist');link.href='/first-offer';link.target='_blank';box.append(link);box.append(elem('span',' · '));link=elem('a','View sample report');link.href='/demo-report';link.target='_blank';box.append(link);box.append(elem('span',' · '));link=elem('a','Get demonstration ZIP');link.href='/download-synthetic';box.append(link)}
 box=$('#catalogue-status');clear(box);if(data.catalogue_preview_exists){box.append(elem('span','Offline draft ready. '));let link=elem('a','View catalogue');link.href='/catalogue-preview';link.target='_blank';box.append(link)};
 $('#ops').textContent='Owner hours: '+data.summary.owner_hours+' · Expenses: '+formatCAD(data.summary.expenses_cad)+' · No payment integrations.';
}
$('#first').onclick=async()=>{try{await post('/api/first-business',{});notify('Synthetic sales pack prepared. See .local/factory/first_reporting_business.');await reload()}catch(e){notify(e.message,true)}};
$('#catalogue').onclick=async()=>{try{await post('/api/catalogue-preview',{});notify('Generated local catalogue preview: .local/factory/previews/catalogue.html');await reload()}catch(e){notify(e.message,true)}};
for(const r of data.all_offers){if(!r.category_id||[...$('#category-filter').options].some(o=>o.value===r.category_id))continue;const o=elem('option',r.category);o.value=r.category_id;$('#category-filter').append(o)}
$('#category-filter').addEventListener('change',render);
$('#search').addEventListener('input',render);$('#scope').addEventListener('change',render);$('#model').addEventListener('change',render);$('#refresh').onclick=async()=>{try{let out=await post('/api/queue',{});notify('Created '+out.created+' local review tasks.');await reload()}catch(e){notify(e.message,true)}};
render();
</script></body></html>'''


# Whitelisted research documents only; no credentials, vault, private state or arbitrary paths.
LIBRARY_PUBLIC_FILES = {
    '/opportunity_library/docs/METHODOLOGY.md': 'opportunity_library/docs/METHODOLOGY.md',
    '/opportunity_library/docs/PRIVACY_AND_PLATFORMS.md': 'opportunity_library/docs/PRIVACY_AND_PLATFORMS.md',
    '/opportunity_library/docs/OPERATING_WORKFLOW.md': 'opportunity_library/docs/OPERATING_WORKFLOW.md',
    '/opportunity_library/docs/SOURCES.md': 'opportunity_library/docs/SOURCES.md',
    '/opportunity_library/data/catalog.csv': 'opportunity_library/data/catalog.csv',
    '/opportunity_library/data/catalog.json': 'opportunity_library/data/catalog.json',
}


class FactoryServer(ThreadingHTTPServer):
    allow_reuse_address=True
    daemon_threads=True
    def __init__(self, host: str='127.0.0.1', port: int=0, root: Path=PRIVATE,
                 rows: list[dict]|None=None):
        if host!='127.0.0.1':
            raise SetupError('The factory only binds to 127.0.0.1 (local computer).')
        self.root=root
        bootstrap(root)
        self.rows=rows if rows is not None else catalog()
        self.token=secrets.token_urlsafe(32)
        super().__init__((host,port),FactoryHandler)

class FactoryHandler(BaseHTTPRequestHandler):
    server: FactoryServer
    def log_message(self,fmt,*args):
        # Do not log request bodies, customer details, or URL queries.
        return
    def _headers(self,code:int,content_type:str,content_length:int):
        self.send_response(code)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(content_length))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.end_headers()
    def _reply(self,code:int,body:str,ctype:str='application/json; charset=utf-8'):
        b=body.encode('utf-8');self._headers(code,ctype,len(b));self.wfile.write(b)
    def _json(self,code:int,body:dict):
        self._reply(code,json.dumps(body,ensure_ascii=False), 'application/json; charset=utf-8')
    def _host_ok(self) -> bool:
        port=self.server.server_address[1]
        return self.headers.get('Host') in (f'127.0.0.1:{port}',f'localhost:{port}')
    def do_GET(self):
        if not self._host_ok():
            self._json(403,{'error':'Invalid Host header.'});return
        path=urlsplit(self.path).path
        if path=='/':
            self._reply(200,render_page(load_view(self.server.root,self.server.rows),self.server.token),
                        'text/html; charset=utf-8')
        elif path=='/opportunity-library' or path in LIBRARY_PUBLIC_FILES:
            relative = 'Opportunity_Library.html' if path=='/opportunity-library' else LIBRARY_PUBLIC_FILES[path]
            target = ROOT / relative
            if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(ROOT.resolve()):
                self._json(404,{'error':'Organized library unavailable. Apply the library patch or rebuild it.'});return
            ctype = 'text/html; charset=utf-8' if target.suffix=='.html' else 'application/json; charset=utf-8' if target.suffix=='.json' else 'text/csv; charset=utf-8' if target.suffix=='.csv' else 'text/plain; charset=utf-8'
            self._reply(200,target.read_text(encoding='utf-8'),ctype)
        elif path=='/api/state':
            self._json(200,load_view(self.server.root,self.server.rows))
        elif path=='/health':
            self._json(200,{'local_only':True,'external_integrations_enabled':False})
        elif path=='/first-offer':
            paths=sorted(FIRST_FILES)
            home=self.server.root/'first_reporting_business'
            if not (home/'00_START_HERE.md').is_file():
                self._json(404,{'error':'Generate the sales pack first.'});return
            links=''.join(f'<li><a href="/first-file/{name}">{escape(name)}</a></li>' for name in paths)
            self._reply(200,
               '<!doctype html><meta charset="utf-8"><title>First-business sales pack</title>'
               '<style>body{max-width:920px;padding:30px;margin:auto;background:#101827;color:#f4f8ff;font:16px/1.5 system-ui}a{color:#91d4ff}</style>'
               '<h1>Reporting business: review-only sales pack</h1>'
               '<p>Created locally. There are no live clients, account connections, charges or public listings.</p><ul>'+links+'</ul>'
               '<p><a href="/demo-report">View genuine synthetic demonstration</a> · <a href="/download-synthetic">Get synthetic delivery ZIP</a></p>',
               'text/html; charset=utf-8')
        elif path.startswith('/first-file/'):
            name=unquote(path[len('/first-file/'):])
            if name not in FIRST_FILES:
                self._json(404,{'error':'Draft not found.'});return
            target=self.server.root/'first_reporting_business'/name
            if not target.is_file():self._json(404,{'error':'Not generated.'});return
            content=escape(target.read_text(encoding='utf-8'))
            self._reply(200, '<!doctype html><meta charset="utf-8"><title>Review draft</title>'
                 '<style>body{max-width:1000px;margin:auto;padding:20px;background:#101827;color:#edf5ff}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.55 system-ui}</style>'
                 '<pre>'+content+'</pre>', 'text/html; charset=utf-8')
        elif path=='/demo-report':
            sample=self.server.root/'synthetic_reporting_demo'/'results'/'report.html'
            if not sample.is_file():self._json(404,{'error':'Generate first-business pack first.'});return
            self._reply(200,sample.read_text(encoding='utf-8'),'text/html; charset=utf-8')
        elif path=='/download-synthetic':
            sample=self.server.root/'first_reporting_business'/'SYNTHETIC_REPORT_DEMONSTRATION.zip'
            if not sample.is_file():self._json(404,{'error':'Generate first-business pack first.'});return
            content=sample.read_bytes()
            self._headers(200,'application/zip',len(content))
            self.wfile.write(content)
        elif path=='/catalogue-preview':
            loc=self.server.root/'previews'/'catalogue.html'
            if not loc.is_file():self._json(404,{'error':'Build the offline catalogue first.'});return
            content=loc.read_text(encoding='utf-8')
            # The standalone file uses relative links; in the local server, use only safe ID previews.
            import re
            content=re.sub(r'\.\./launchkits/([A-Za-z0-9_-]{1,80})/LANDING_PREVIEW\.html',r'/preview/\1',content)
            self._reply(200,content,'text/html; charset=utf-8')
        elif path.startswith('/preview/'):
            ref=unquote(path[len('/preview/'):])
            try:
                safe_id(ref)
                target=self.server.root/'launchkits'/ref/'LANDING_PREVIEW.html'
                if not target.resolve().is_relative_to((self.server.root.resolve()/'launchkits')) or not target.is_file():
                    raise SetupError('Draft preview unavailable.')
                self._reply(200,target.read_text(encoding='utf-8'),'text/html; charset=utf-8')
            except (OSError,SetupError):self._json(404,{'error':'Preview not found.'})
        else:
            self._json(404,{'error':'Not found.'})
    def do_POST(self):
        if not self._host_ok() or self.headers.get('X-Factory-Token')!=self.server.token:
            self._json(403,{'error':'Local CSRF/Host verification failed.'});return
        origin=self.headers.get('Origin')
        port=self.server.server_address[1]
        if origin and origin not in (f'http://127.0.0.1:{port}',f'http://localhost:{port}'):
            self._json(403,{'error':'Foreign origin.'});return
        if not self.headers.get('Content-Type','').startswith('application/json'):
            self._json(415,{'error':'Only JSON is accepted.'});return
        try:
            length=int(self.headers.get('Content-Length','-1'))
            if not 0<length<=4096:raise SetupError('Request too large or empty.')
            payload=json.loads(self.rfile.read(length))
            if not isinstance(payload,dict):raise SetupError('Expected JSON object.')
            path=urlsplit(self.path).path
            if path=='/api/queue':
                if payload:raise SetupError('No parameters expected.')
                count=create_tasks(select(self.server.rows,limit=18,per_mode=3),self.server.root)
                self._json(200,{'created':count,'external_action':False})
            elif path=='/api/kit':
                if set(payload)!={'id'}:raise SetupError('Only id is allowed.')
                ref=safe_id(payload['id'])
                row=next((r for r in self.server.rows if r['id']==ref),None)
                if row is None:raise SetupError('ID not found in atlas.')
                if row.get('legal_class','').strip().lower() not in ('standard','refer to original'):
                    raise SetupError('Regulated opportunity: review compliance manually first.')
                dest=make_kit(row,self.server.root,load_profile(self.server.root/'seller_profile.json'))
                self._json(200,{'created':ref,'files':len(list(dest.iterdir())),'preview':'/preview/'+ref,
                                'external_action':False})
            elif path=='/api/first-business':
                if payload:raise SetupError('No parameters expected.')
                dest=first_business(self.server.root)
                self._json(200,{'created':str(dest),'external_action':False})
            elif path=='/api/catalogue-preview':
                if payload:raise SetupError('No parameters expected.')
                dest=create_preview(self.server.root)
                self._json(200,{'created':str(dest),'external_action':False})
            elif path=='/api/review-task':
                if set(payload)!={'task_id'}:raise SetupError('Only task_id is allowed.')
                if not finish_task(payload['task_id'],self.server.root):
                    raise SetupError('Task is absent or already reviewed.')
                self._json(200,{'local_only':True})
            elif path=='/api/review-approval':
                if set(payload)!={'request_id'}:raise SetupError('Only request_id is allowed.')
                resolve_approval(payload['request_id'],'reviewed',root=self.server.root)
                self._json(200,{'local_only':True,'external_action_authorized':False})
            else:self._json(404,{'error':'Unknown local-only action.'})
        except (ValueError,KeyError,TypeError,SetupError,json.JSONDecodeError,OSError) as e:
            self._json(400,{'error':str(e)[:260]})


def serve(port: int=0, *,no_browser:bool=False,root:Path=PRIVATE, rows:list[dict]|None=None):
    with FactoryServer(port=port,root=root,rows=rows) as server:
        url=f'http://127.0.0.1:{server.server_address[1]}/'
        print('PORTFOLIO AUTOPILOT — LOCAL DRAFT WORKBENCH')
        print('Open:',url)
        print('No accounts, emails, charges, providers, purchases or public deployments are connected.')
        print('Press Ctrl+C in this terminal to stop.')
        if not no_browser:
            webbrowser.open(url)
        try:server.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:pass
