"""Visible Chromium acceptance; disposable websites and read-only public pages.

Runs the production Browser controller, including routing, not a substitute browser.
"""
import base64
import hashlib
import json
import os
import socket
import struct
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from assistant.browser import Browser
from assistant.permissions import Permissions,Denied,origin
from assistant.storage import private_directory


class Site(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    events=[];second=''
    def log_message(self,*args):pass
    def response(self,text,status=200,headers=None,kind='text/html'):
        raw=text.encode() if isinstance(text,str) else text
        self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)))
        for k,v in (headers or {}).items():self.send_header(k,v)
        self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        path=urlsplit(self.path).path
        Site.events.append(('GET',path))
        if path=='/socket':
            Site.events.append(('ws-handshake','received'))
            key=base64.b64encode(hashlib.sha1((self.headers['Sec-WebSocket-Key']+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            self.send_response(101);self.send_header('Upgrade','websocket');self.send_header('Connection','Upgrade');self.send_header('Sec-WebSocket-Accept',key);self.end_headers()
            self.connection.settimeout(10)
            try:
                first=self.rfile.read(2);length=first[1]&127
                if length==126:length=struct.unpack('!H',self.rfile.read(2))[0]
                mask=self.rfile.read(4);data=self.rfile.read(length);data=bytes(c^mask[i%4] for i,c in enumerate(data))
                Site.events.append(('websocket',json.loads(data)))
                answer=b'{"result":"realtime ready"}';self.wfile.write(bytes([129,len(answer)])+answer);self.wfile.flush()
                time.sleep(.2)
            except (OSError,IndexError):pass
            self.close_connection=True;return
        if path=='/redirect':return self.response('',302,{'Location':Site.second+'/landing'})
        if path=='/landing':return self.response('<title>Redirect destination</title><h1>Redirect verified</h1>')
        if path=='/login':return self.response('<title>Synthetic sign in</title><form action="/session" method="post"><label>User<input name="user"></label><label>Password<input type="password" name="password"></label><button>Sign in</button></form>')
        if path=='/account':
            authorized='synthetic_session=synthetic-only' in self.headers.get('Cookie','')
            return self.response('<title>Account</title><h1>'+('Synthetic account ready' if authorized else 'Signed out')+'</h1>')
        if path=='/frame':return self.response('<label>Embedded notes<textarea></textarea></label>')
        if path=='/asset.js':
            Site.events.append(('asset_cookie',self.headers.get('Cookie','')))
            return self.response('window.assetReady=true;',headers={'Set-Cookie':'resource_attempt=blocked; Path=/'},kind='application/javascript')
        if path=='/app':return self.response('''<title>Dynamic application</title><h1>Dynamic application</h1>
<label>Search<input id=q></label><button id=search>Search</button><p id=result></p>
<label>Draft<textarea id=draft></textarea></label><p id=saved></p>
<div contenteditable=true aria-label="Rich editor">Initial text</div>
<button id=socket>Connect realtime</button><p id=realtime></p>
<button id=partner>Search partner</button><p id=partner_result></p>
<button id=hidden>Run unexplained update</button><button id=publish>Publish product</button>
<a href="/landing" target=_blank>Open popup</a><iframe src=/frame></iframe>
<form action=/upload method=post enctype=multipart/form-data><label>Fixture file<input type=file name=fixture></label><button>Upload fixture</button></form>
<a download=fixture.txt href=/download>Download fixture</a>
<script>
search.onclick=async()=>{result.textContent=(await(await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operationName:'SearchProducts',variables:{query:q.value}})})).json()).result};
draft.oninput=()=>{clearTimeout(window.saveTimer);window.saveTimer=setTimeout(async()=>{saved.textContent=await(await fetch('/drafts/1',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:draft.value})})).text()},300)};
socket.onclick=()=>{let w=window.testSocket=new WebSocket(location.origin.replace('http','ws')+'/socket');w.onopen=()=>w.send(JSON.stringify({type:'search',query:'synthetic'}));w.onmessage=e=>realtime.textContent=JSON.parse(e.data).result;w.onclose=e=>window.socketClose=e.code;w.onerror=()=>window.socketError=true};
hidden.onclick=()=>fetch('/opaque',{method:'POST',body:'unexplained=true'});
partner.onclick=async()=>{partner_result.textContent=(await(await fetch('PARTNER_ORIGIN/cors',{method:'POST',headers:{'Content-Type':'text/plain'},body:JSON.stringify({operationName:'SearchProducts',query:'synthetic'})})).json()).result};
publish.onclick=()=>fetch('/api/publish',{method:'POST',body:'title=synthetic'});
window.ticks=0;setInterval(()=>window.ticks++,50);
</script><script src="PARTNER_ORIGIN/asset.js"></script>'''.replace('PARTNER_ORIGIN',Site.second))
        if path=='/download':return self.response('synthetic download',headers={'Content-Disposition':'attachment; filename=fixture.txt'},kind='text/plain')
        self.response('<title>Static fixture</title><h1>Static fixture ready</h1><a href=/app>Open dynamic app</a>')
    def do_POST(self):
        body=self.rfile.read(int(self.headers.get('Content-Length',0)));Site.events.append((self.path,body))
        if self.path=='/session':return self.response('',303,{'Location':'/account','Set-Cookie':'synthetic_session=synthetic-only; Path=/; HttpOnly; Max-Age=3600'})
        if self.path=='/api':return self.response('{"result":"Dynamic search verified"}',kind='application/json')
        if self.path=='/cors':return self.response('{"result":"Partner search verified"}',headers={'Access-Control-Allow-Origin':'*'},kind='application/json')
        if self.path.startswith('/drafts/'):return self.response('Draft saved',kind='text/plain')
        self.response('<h1>Upload verified</h1>' if self.path=='/upload' else 'updated')


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Explicit synthetic acceptance opt-in required')
    directory=private_directory()/'verification'/('browser-'+time.strftime('%Y%m%d-%H%M%S'));directory.mkdir(parents=True)
    results={};requests=[];browser=None
    def record(name,value=True):
        results[name]=value;(directory/'results.json').write_text(json.dumps(results,indent=2));print(name+': '+str(value),flush=True)
    servers=[ThreadingHTTPServer(('127.0.0.1',0),Site) for _ in range(2)]
    for server in servers:threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{servers[0].server_port}';Site.second=f'http://127.0.0.1:{servers[1].server_port}'
    permissions=Permissions();permissions.resume('test');permissions.observe=True
    def ask(label,args):
        requests.append((label,args));return bool(args.get('website_access'))
    try:
        browser=Browser(directory,permissions);browser.ask=ask
        snapshot=browser.call({'operation':'navigate','url':url});assert 'Static fixture ready' in snapshot['text'];assert len(requests)==1
        record('new_website_interactive_visit_grant')
        browser.context.add_cookies([{'name':'profile_marker','value':'PRIVATE-SYNTHETIC','url':url}])
        # Treat only this disposable partner as a public CDN for the resource
        # test. Production still resolves and rejects private network resources.
        is_public=browser.access.is_public
        browser.access.is_public=lambda address:origin(address)==origin(Site.second) or is_public(address)
        snapshot=browser.call({'operation':'navigate','url':url+'/app'});assert len(requests)==1
        record('same_website_navigation_without_reapproval')
        assert browser.page.evaluate('window.assetReady')
        assert all('profile_marker' not in body for path,body in Site.events if path=='asset_cookie')
        assert not any(c['name']=='resource_attempt' for c in browser.context.cookies());record('third_party_assets_cannot_read_or_overwrite_profile_cookies')
        def action(label,op='click',approved=False,**fields):
            snapshot=browser.call({'operation':'inspect'});matches=[c for c in snapshot['controls'] if c['label'].strip()==label]
            assert len(matches)==1,(label,[c['label'] for c in snapshot['controls']])
            return browser.call({'operation':op,'observation':snapshot['observation'],'element':matches[0]['element'],**fields},approved=approved)
        # Search field and button share a label; select by tag, never guess.
        snapshot=browser.inspect();field=next(c for c in snapshot['controls'] if c['label']=='Search' and c['tag']=='INPUT')
        browser.call({'operation':'fill','observation':snapshot['observation'],'element':field['element'],'text':'maple'})
        snapshot=browser.inspect();button=next(c for c in snapshot['controls'] if c['label']=='Search' and c['tag']=='BUTTON')
        browser.call({'operation':'click','observation':snapshot['observation'],'element':button['element']});browser.call({'operation':'wait','milliseconds':400})
        assert 'Dynamic search verified' in browser.inspect()['text'];assert len(requests)==1;record('ordinary_ajax_post_search_without_approval')
        action('Draft','fill',text='First line\nSecond line');browser.call({'operation':'wait','milliseconds':700})
        assert 'Draft saved' in browser.inspect()['text'];assert len(requests)==1;record('delayed_draft_autosave_without_reapproval')
        action('Rich editor','fill',text='Edited rich text\nSecond paragraph');record('contenteditable_edit')
        action('Embedded notes','fill',text='Embedded text');record('iframe_semantic_edit')
        action('Connect realtime');browser.call({'operation':'wait','milliseconds':1200})
        assert 'realtime ready' in browser.inspect()['text'],{'events':[(p,str(v)[:60]) for p,v in Site.events],'diagnostics':browser.diagnostics,'last_error':browser.last_error,'socket':browser.page.evaluate('({state:testSocket?.readyState,error:window.socketError,close:window.socketClose})')};record('real_websocket_request_response')
        before=len(requests);action('Search partner');browser.call({'operation':'wait','milliseconds':400})
        assert 'Partner search verified' in browser.inspect()['text'];assert len(requests)==before+1 and requests[-1][1].get('permission_kind')=='data_connection'
        assert not browser.access.full(Site.second,browser.tab_id());record('cross_origin_api_uses_specific_data_connection_grant')
        before=len(requests)
        try:action('Run unexplained update')
        except Denied:pass
        browser.call({'operation':'wait','milliseconds':300})
        assert not any(p=='/opaque' for p,_ in Site.events);assert len(requests)==before+1;record('unexplained_mutation_denied_before_dispatch')
        before=len(requests)
        try:action('Publish product')
        except Denied:pass
        assert len(requests)==before;assert not any(p=='/api/publish' for p,_ in Site.events);record('publication_requires_real_owner_review')
        action('Open popup');browser.call({'operation':'wait','milliseconds':300})
        tabs=browser.tabs();assert len(tabs)==2;popup=next(t for t in tabs if not t['active'])['tab'];primary=next(t for t in tabs if t['active'])['tab']
        browser.call({'operation':'switch_tab','tab':popup});assert 'Redirect verified' in browser.inspect()['text']
        browser.call({'operation':'close_tab','tab':popup});browser.call({'operation':'switch_tab','tab':primary});record('popup_stable_tab_switch_and_close')
        browser.call({'operation':'new_tab','url':url+'/landing'});third=browser.tab_id();assert third>popup
        browser.call({'operation':'close_tab','tab':third});record('closed_tab_ids_are_not_reused')
        browser.call({'operation':'navigate','url':url+'/redirect'});assert browser.page.url==Site.second+'/landing'
        assert any(a['origin']==origin(Site.second) for _,a in requests if a.get('website_access'));record('cross_origin_redirect_requests_access_and_preserves_url')
        browser.call({'operation':'navigate','url':url+'/app'})
        upload=directory/'synthetic-upload.txt';upload.write_text('SYNTHETIC-FILE-CONTENT')
        action('Fixture file','upload',approved=True,approved_path=str(upload));action('Upload fixture',approved=True)
        assert any(path=='/upload' and b'SYNTHETIC-FILE-CONTENT' in body for path,body in Site.events);record('actual_multipart_file_upload')
        browser.call({'operation':'navigate','url':url+'/app'});action('Download fixture');browser.call({'operation':'wait','milliseconds':400})
        assert browser.downloads and Path(browser.downloads[-1]['path']).read_text()=='synthetic download';record('download_retained_without_execution')
        browser.command('manual',enabled=True)
        try:browser.call({'operation':'inspect'});raise AssertionError('Manual control allowed model inspection')
        except Denied:pass
        # Simulate the human's browser UI step; only synthetic credentials enter
        # this test page. Production model capabilities cannot evaluate scripts.
        browser.page.goto(url+'/login');browser.page.locator('input[name=user]').fill('synthetic-user');browser.page.locator('input[type=password]').fill('SYNTHETIC-ONLY')
        browser.page.get_by_role('button',name='Sign in').click();browser.page.wait_for_url('**/account')
        browser.command('manual',enabled=False);assert 'Synthetic account ready' in browser.inspect()['text'];record('synthetic_auth_manual_handoff_and_return_inspection')
        browser.close();browser=Browser(directory,permissions);browser.ask=ask
        browser.call({'operation':'navigate','url':url+'/account'});assert 'Synthetic account ready' in browser.inspect()['text'];record('persistent_profile_session_survives_browser_restart')
        browser.call({'operation':'navigate','url':url+'/app'});before=browser.page.evaluate('ticks');browser.command('background',enabled=True)
        browser.page.wait_for_timeout(500);assert browser.page.evaluate('ticks')>before;record('background_javascript_continues')
        assert browser.permissions.browser_pids;record('dedicated_browser_process_identity_available')
        if '--public-web' in sys.argv:
            permissions.public_browsing=True;before=len(requests)
            snapshot=browser.call({'operation':'new_tab','url':'https://example.com'});assert 'Example Domain' in snapshot['title'],{k:snapshot[k] for k in ('url','title','error','diagnostics')};record('real_static_public_website')
            snapshot=browser.call({'operation':'new_tab','url':'https://www.wikipedia.org'});assert 'Wikipedia' in snapshot['title'];record('real_dynamic_search_homepage')
            search=next(c for c in snapshot['controls'] if c['tag']=='INPUT' and c['type']=='search')
            snapshot=browser.call({'operation':'fill','observation':snapshot['observation'],'element':search['element'],'text':'Chromium'})
            search=next(c for c in snapshot['controls'] if c['tag']=='INPUT' and c['type']=='search')
            snapshot=browser.call({'operation':'press','observation':snapshot['observation'],'element':search['element'],'key':'Enter'})
            assert 'Chromium' in snapshot['title'];record('real_search_submission_and_subdomain_redirect')
            snapshot=browser.call({'operation':'new_tab','url':'https://playwright.dev'});assert 'Playwright' in snapshot['text'];record('real_javascript_site_and_third_party_assets')
            assert len(browser.tabs())>=4;record('real_public_multisite_tabs_one_session')
        record('complete')
    except Exception as error:
        record('complete',False);record('error',type(error).__name__+': '+str(error));raise
    finally:
        if browser:browser.close()
        for server in servers:server.shutdown();server.server_close()
        print('Private evidence: '+str(directory/'results.json'),flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
