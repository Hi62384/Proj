"""Bundled controller tests in installed Google Chrome, with disposable pages.

Chrome uses a disposable test context and a private inherited debugging PIPE,
never a network debugging port or the owner's profile. Runtime messaging is a
test adapter in an isolated world: this suite does NOT claim extension install
or Native Messaging acceptance (the separate live extension suite does that).
"""
import base64
import hashlib
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from assistant.storage import private_directory


class Site(BaseHTTPRequestHandler):
    uploaded=b''
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/frame':body='<label>Frame notes<textarea></textarea></label>'
        else:body='''<!doctype html><meta charset=utf-8><title>Disposable Chrome DOM Lab</title>
<label>Notes<textarea></textarea></label><label>Human input<input autofocus></label>
<div contenteditable=true aria-label="Rich editor">Initial rich text</div>
<label>Theme<select><option value=teal>Teal</option><option value=blue>Blue</option></select></label>
<label>Ready<input type=checkbox></label><button aria-expanded=false onclick="this.setAttribute('aria-expanded','true');document.querySelector('#result').textContent='Expanded'">Expand</button>
<p id=result>Ready</p><div id=shadow></div><script>let r=document.querySelector('#shadow').attachShadow({mode:'open'});r.innerHTML='<label>Shadow notes<textarea></textarea></label>';</script>
<iframe src=/frame></iframe><table><tr><th>Name</th><th>Value</th></tr><tr><td>Maple</td><td>42</td></tr></table>
<input type=hidden name=csrf_token value=PRIVATE-SYNTHETIC-TOKEN>
<form action=/upload method=post enctype=multipart/form-data><label>Fixture file<input name=fixture type=file></label><button>Upload fixture</button></form>'''
        if self.path=='/human':body=body.replace('Disposable Chrome DOM Lab','Disposable Human Input Tab')
        raw=body.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_POST(self):
        Site.uploaded=self.rfile.read(int(self.headers.get('Content-Length',0)))
        raw=b'<title>Upload verified</title><h1>Uploaded synthetic file</h1>';self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)


class Adapter:
    def __init__(self,page,source,frame=None):
        self.page=page;self.session=page.context.new_cdp_session(page);tree=self.session.send('Page.getFrameTree')['frameTree']
        target=tree['frame']['id'] if frame is None else tree['childFrames'][frame]['frame']['id']
        self.context=self.session.send('Page.createIsolatedWorld',{'frameId':target,'worldName':'codex-disposable-test'})['executionContextId']
        bootstrap="globalThis.chrome={runtime:{id:'synthetic-extension',onMessage:{addListener(handler){globalThis.testHandler=handler;}}}};"
        self.session.send('Runtime.evaluate',{'expression':bootstrap+source,'contextId':self.context})
    def call(self,operation,**args):
        result=self.session.send('Runtime.callFunctionOn',{'executionContextId':self.context,'functionDeclaration':"function(args){return new Promise(resolve=>{globalThis.testHandler(args,{id:'synthetic-extension'},resolve);});}",
            'arguments':[{'value':{'channel':'codex-content','operation':operation,'session':'test-session',**args}}],'awaitPromise':True,'returnByValue':True})
        if result.get('exceptionDetails'):raise RuntimeError('Isolated controller execution failed')
        return result['result']['value']


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Explicit synthetic-test opt-in required')
    directory=private_directory()/'verification'/('chrome-dom-'+time.strftime('%Y%m%d-%H%M%S'));directory.mkdir(parents=True);results={}
    def record(name):results[name]=True;print(name+': True',flush=True);(directory/'results.json').write_text(json.dumps(results,indent=2))
    server=ThreadingHTTPServer(('127.0.0.1',0),Site);threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_port}';source=(APP/'chrome_extension/content.js').read_text(encoding='utf-8')
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as runtime:
            browser=runtime.chromium.launch(channel='chrome',headless=False,chromium_sandbox=True)
            try:
                context=browser.new_context();page=context.new_page();page.goto(url)
                controller=Adapter(page,source);assert controller.call('grant',origin=url)['ok'];snapshot=controller.call('inspect')['result']
                assert snapshot['tables'][0][1]==['Maple','42'];assert 'PRIVATE-SYNTHETIC' not in json.dumps(snapshot);record('real_google_chrome_bounded_dom_and_private_field_redaction')
                def action(label,operation,**args):
                    snapshot=controller.call('inspect')['result'];found=[c for c in snapshot['controls'] if c['label']==label];assert len(found)==1,(label,snapshot['controls'])
                    response=controller.call('action',observation=snapshot['observation'],element=found[0]['element'],action=operation,**args)
                    assert response['ok'],response
                action('Notes','fill',text='First line\nSecond line');action('Rich editor','fill',text='Two\nRich lines');action('Shadow notes','fill',text='Shadow editor works')
                assert page.locator('textarea').first.input_value()=='First line\nSecond line';record('multiline_rich_text_and_open_shadow_dom')
                action('Theme','select',text='blue');action('Ready','check',checked=True);action('Expand','click');assert page.locator('#result').inner_text()=='Expanded';record('select_checkbox_and_dynamic_button')
                frame=Adapter(page,source,frame=0);assert frame.call('grant',origin=url)['ok'];assert 'Frame notes' in frame.call('inspect')['result']['text'];record('same_origin_frame_inspection')
                human=context.new_page();human.goto(url+'/human');human.bring_to_front();human.locator('input').first.focus()
                # Playwright enables focus emulation on its own CDP session,
                # which makes visibilityState unsuitable for this assertion.
                # Inspect only our disposable Chrome window's real omnibox.
                browser_session=browser.new_browser_cdp_session();pid=next(p['id'] for p in browser_session.send('SystemInfo.getProcessInfo')['processInfo'] if p['type']=='browser')
                import win32gui,win32process
                windows=[]
                win32gui.EnumWindows(lambda hwnd,_:windows.append(hwnd) if win32gui.IsWindowVisible(hwnd) and win32process.GetWindowThreadProcessId(hwnd)[1]==pid and win32gui.GetClassName(hwnd)=='Chrome_WidgetWin_1' else None,None)
                def active_title():return [win32gui.GetWindowText(hwnd) for hwnd in windows]
                assert any('Disposable Human Input Tab' in title for title in active_title()),active_title()
                foreground=win32gui.GetForegroundWindow()
                for character in 'Human typing stays independent':
                    human.keyboard.insert_text(character);action('Notes','fill',text='Background iteration '+character)
                assert human.locator('input').first.input_value()=='Human typing stays independent'
                assert any('Disposable Human Input Tab' in title for title in active_title()) and win32gui.GetForegroundWindow()==foreground;record('trusted_input_in_active_tab_and_independent_background_dom_work')
                page.bring_to_front();page.locator('textarea').first.focus();snapshot=controller.call('inspect')['result'];element=next(c['element'] for c in snapshot['controls'] if c['label']=='Notes')
                page.keyboard.insert_text('Human priority');response=controller.call('action',observation=snapshot['observation'],element=element,action='fill',text='Should not overwrite')
                assert not response['ok'];assert 'Human priority' in page.locator('textarea').first.input_value();record('trusted_same_tab_input_invalidates_queued_edit')
                assert controller.call('manual',enabled=True)['ok'];assert not controller.call('inspect')['ok'];assert controller.call('manual',enabled=False)['ok'];record('manual_hold_blocks_observation')
                page.wait_for_timeout(1000);snapshot=controller.call('inspect')['result'];file=next(c['element'] for c in snapshot['controls'] if c['type']=='file')
                raw=b'Synthetic upload bytes verified independently\x00\xff'*10000;digest=hashlib.sha256(raw).hexdigest();upload='synthetic-upload'
                assert controller.call('upload_begin',observation=snapshot['observation'],element=file,upload=upload,name='synthetic.bin',size=len(raw),sha256=digest)['ok']
                for offset in range(0,len(raw),128*1024):assert controller.call('upload_chunk',upload=upload,offset=offset,data=base64.b64encode(raw[offset:offset+128*1024]).decode())['ok']
                assert controller.call('upload_finish',upload=upload)['result']['sha256']==digest
                try:action('Upload fixture','click')
                except Exception:pass  # Navigation may destroy the reply context; never replay.
                page.wait_for_url('**/upload');assert raw in Site.uploaded;record('real_filelist_selection_and_independently_verified_multipart_bytes')
                record('complete')
            finally:browser.close()
    finally:
        server.shutdown();server.server_close();print('Private evidence: '+str(directory/'results.json'),flush=True)


if __name__=='__main__':main()
