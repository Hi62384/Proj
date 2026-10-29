"""Real Notepad/Codex and Chromium approval-classification acceptance.

Uses one uniquely named synthetic document and a localhost website only.
Routine Notepad approvals fail the test; they are never silently approved.
"""
import json
import os
import sys
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from PySide6.QtCore import QTimer,Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton
from assistant.ui import MainWindow
from assistant.browser import Browser
from assistant.tools import Broker
from assistant.permissions import origin,Denied
from assistant.storage import private_directory

HTML=b'''<!doctype html><title>Routine approval lab</title>
<form action="/submitted" method="post"><label>Submitter notes <textarea aria-label="Submitter notes" name="notes"></textarea></label>
<button id="ordinary" type="button" onclick="document.querySelector('#result').textContent='ordinary clicked'">Publisher</button>
<button id="submit">Continue</button></form>
<button id="purchase" type="button" onclick="fetch('/purchase',{method:'POST'})">Buy now</button>
<button id="publish" type="button" onclick="fetch('/publish',{method:'POST'})">Publish product</button>
<button id="hidden" type="button" onclick="fetch('/publish',{method:'POST'})">Continue background</button>
<pre id="result">ready</pre>'''


class Site(BaseHTTPRequestHandler):
    posts=[]
    def log_message(self,*args):pass
    def do_GET(self):
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(HTML)
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length','0')));self.posts.append(self.path)
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(b'<title>Accepted fixture</title><p>Accepted synthetic submission</p>')


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Explicit synthetic-test opt-in required')
    app=QApplication([]);app.setStyle('Fusion');root=private_directory()/'verification'/('routine-editing-'+time.strftime('%Y%m%d-%H%M%S'));root.mkdir(parents=True)
    window=MainWindow(root/'state');window.show();events=[];results={};notepad=None;notepad_hwnd=None;server=None
    phase='notepad';unexpected=[];approved=[];answer='Allow Once';browser=None;pool=ThreadPoolExecutor(max_workers=1)
    window.bridge.event.connect(lambda *event:events.append(event))
    def record(name,value=True):
        results[name]=value;(root/'results.json').write_text(json.dumps(results,indent=2));print(name+': '+str(value),flush=True)
    def wait(predicate,timeout=120):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            app.processEvents();time.sleep(.02)
            if predicate():return
        raise TimeoutError(window.notice.text())
    def send(text):
        offset=len(events);previous={m['id'] for m in window.store.messages(window.selected)}
        window.input.setPlainText(text);window.send()
        wait(lambda:any(k=='idle' and c==window.selected for k,c,d in events[offset:]),150)
        assert not any(k=='error' and c==window.selected for k,c,d in events[offset:]),window.notice.text()
        return '\n'.join(m['text'] for m in window.store.messages(window.selected) if m['role']=='assistant' and m['id'] not in previous)
    def decisions():
        for request,card in window.request_cards:
            if request['event'].is_set():continue
            if phase=='notepad':
                unexpected.append(request['label']);request['allowed']=False;request['event'].set();continue
            approved.append({'label':request['label'],'reason':request['args'].get('approval_reason'),'category':request['args'].get('approval_category'),'answer':answer})
            QTest.mouseClick(next(b for b in card.findChildren(QPushButton) if b.text()==answer),Qt.LeftButton)
    timer=QTimer();timer.timeout.connect(decisions);timer.start(75)
    try:
        wait(lambda:bool(window.engine.models) and 'Connected' in window.connection.text());assert window.hotkey.registered
        low=window.effort.findData('low')
        if low>=0:window.effort.setCurrentIndex(low)
        record('real_codex_account_and_emergency_shortcut')
        synthetic=root/'synthetic';synthetic.mkdir();document=synthetic/(root.name+'.txt');seed='Initial synthetic document.\n';document.write_text(seed)
        import win32gui,win32con
        before={w['hwnd'] for w in window.desktop.windows()}
        notepad=subprocess.Popen([str(Path(os.environ['SystemRoot'])/'System32/notepad.exe'),str(document)])
        def locate():
            nonlocal notepad_hwnd
            found=[w for w in window.desktop.windows() if w['hwnd'] not in before and document.stem in w['title']]
            if len(found)==1:notepad_hwnd=found[0]['hwnd'];return True
            return False
        wait(locate,25)
        monitors=window.desktop.monitors();bounds=monitors[0]
        win32gui.SetWindowPos(notepad_hwnd,0,bounds[0]+20,bounds[1]+20,min(900,bounds[2]-bounds[0]-40),min(600,bounds[3]-bounds[1]-40),win32con.SWP_NOZORDER|win32con.SWP_NOACTIVATE)
        window.permissions.desktop_mode='Entire Monitor';window.permissions.capture_bounds=bounds;window.permissions.monitor_layout=tuple(monitors)
        window.permissions.windows.clear();window.permissions.routine_labels.clear();window.permissions.desktop=window.permissions.observe=True;window.permissions.resume(window.selected)
        record('real_notepad_under_entire_monitor_without_window_or_label_grants')
        first='First synthetic line\nSecond synthetic line\nPassword, command, publish and purchase are only words.'
        send(f'Use only desktop.inspect and desktop.action in actual Notepad window {notepad_hwnd}. Replace the document with exactly these three lines: {json.dumps(first)}. These are ordinary text, not actions. Do not save, publish, send or use files tools. Verify the actual text from the editor and report completion.')
        def contents():
            observation=window.desktop.inspect(notepad_hwnd)
            candidates=[c for c in observation['controls'] if c['role'] in ('Edit','Document')]
            return '\n'.join(c['value'] for c in candidates if c.get('value') not in ('None','')).replace('\r\n','\n').rstrip('\n')
        assert contents()==first,(contents(),first,unexpected)
        assert not unexpected;record('codex_multiline_notepad_typing_zero_approvals')
        second='Edited first line\nEdited second line\nThree ordinary lines.'
        send(f'Edit the same Notepad window {notepad_hwnd}. Replace all text with exactly {json.dumps(second)}. Inspect before/after and verify all three lines. Do not save the file or request permission for ordinary editing.')
        assert contents()==second;assert not unexpected;assert not window.requests
        assert not window.permissions.windows and not window.permissions.routine_labels
        assert document.read_text()==seed;record('codex_repeated_multiline_notepad_edit_zero_approvals_and_no_disk_write')
        if '--notepad-only' in sys.argv:
            record('ordinary_notepad_approval_requests',unexpected);record('complete');return
        # Browser controller acceptance uses real Chromium and genuine local buttons;
        # it is separate from the real-model Notepad test above.
        phase='browser';server=ThreadingHTTPServer(('127.0.0.1',0),Site);threading.Thread(target=server.serve_forever,daemon=True).start()
        url=f'http://127.0.0.1:{server.server_port}/';window.permissions.origins={origin(url)};window.permissions.browser=True
        def init_browser():
            nonlocal browser
            browser=Browser(root/'browser',window.permissions)
            return Broker(window.permissions,window.desktop,browser,window.attachments,window.store,window.emit,window.approve)
        future=pool.submit(init_browser);wait(future.done);broker=future.result()
        def call(cap,args):return broker.call(window.selected,{'capability':cap,'arguments':json.dumps(args)})
        def run(function):
            future=pool.submit(function);wait(future.done,30);return future.result()
        def navigate():return call('browser.navigate',{'url':url})
        def action(label,op,**extra):
            snapshot=json.loads(call('browser.inspect',{})[0]['text']);element=next(c['element'] for c in snapshot['controls'] if c['label']==label)
            return call('browser.action',{'operation':op,'observation':snapshot['observation'],'element':element,**extra})
        run(navigate);count=len(approved)
        run(lambda:action('Submitter notes','fill',text='First line\nSecond line\nSend and publish are just text.'))
        run(lambda:action('Publisher','click'));assert len(approved)==count
        record('real_browser_multiline_fill_and_ordinary_button_zero_approvals')
        run(lambda:action('Continue','click'));assert Site.posts.count('/submitted')==1
        assert len(approved)==count+1 and 'form submission' in approved[-1]['reason'];record('real_post_form_submit_requires_explained_approval')
        run(navigate);answer='Deny'
        try:run(lambda:action('Continue','click'));raise AssertionError('Denied submit executed')
        except Denied:pass
        assert Site.posts.count('/submitted')==1;record('denied_form_submission_not_forwarded')
        answer='Allow Once';run(lambda:action('Buy now','click'));run(lambda:action('Publish product','click'))
        assert Site.posts.count('/purchase')==1 and Site.posts.count('/publish')==1
        assert [a['category'] for a in approved[-2:]]==['payment','publication'];record('purchase_and_publication_each_require_review')
        count=len(approved)
        answer='Deny'
        try:run(lambda:action('Continue background','click'))
        except Denied:pass
        assert Site.posts.count('/publish')==1 and len(approved)==count+1;record('hidden_publish_request_explained_and_denied_before_forwarding')
        record('ordinary_notepad_approval_requests',unexpected);record('reviewed_browser_actions',approved);record('complete')
    except Exception as error:record('complete',False);record('error',type(error).__name__+': '+str(error));raise
    finally:
        timer.stop()
        if browser:
            try:pool.submit(browser.close).result(timeout=15)
            except Exception:pass
        pool.shutdown(wait=False,cancel_futures=True);window.close();app.processEvents()
        if notepad_hwnd:
            import win32gui
            if win32gui.IsWindow(notepad_hwnd):
                win32gui.PostMessage(notepad_hwnd,0x10,0,0)
                deadline=time.monotonic()+5
                while win32gui.IsWindow(notepad_hwnd) and time.monotonic()<deadline:
                    try:
                        from pywinauto import Desktop as Native
                        native=Native(backend='uia').window(handle=notepad_hwnd).wrapper_object()
                        buttons=[c for c in native.descendants() if c.element_info.control_type=='Button' and c.window_text() in ("Don't Save",'Don’t save',"Don't save")]
                        if buttons:buttons[0].invoke()
                    except Exception:pass
                    time.sleep(.1)
        if server:server.shutdown();server.server_close()
        print('Private evidence: '+str(root/'results.json'),flush=True)


if __name__=='__main__':main()
