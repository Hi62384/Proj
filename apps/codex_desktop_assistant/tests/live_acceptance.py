"""Opt-in real Qt/Codex/Windows/Chromium acceptance, using synthetic fixtures only.

Run with the managed Python. Uses the existing ChatGPT plan and never contacts a store.
"""
import argparse
import hashlib
import io
import json
import os
import random
import subprocess
import sys
import threading
import time
import zipfile
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

APP=Path(__file__).resolve().parents[1];ROOT=APP.parents[1]
sys.path[:0]=[str(APP),str(ROOT)]

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from assistant.ui import MainWindow
from assistant.permissions import origin,Denied
from assistant.storage import private_directory


class Site(BaseHTTPRequestHandler):
    uploaded=None
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/safe-redirect':
            self.send_response(302);self.send_header('Location','/');self.end_headers();return
        if self.path=='/blocked-redirect':
            self.send_response(302);self.send_header('Location','http://127.0.0.1:1/unapproved');self.end_headers();return
        raw=(APP/'tests/browser_fixture.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_POST(self):
        size=int(self.headers.get('Content-Length','0'))
        if size>100000:self.send_error(413);return
        Site.uploaded=self.rfile.read(size)
        raw=b'<html><title>Upload verified</title><h1>Fixture received</h1><p>The local synthetic upload succeeded.</p></html>'
        self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(raw)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--approve-synthetic-tests',action='store_true');args=parser.parse_args()
    if not args.approve_synthetic_tests:raise SystemExit('Requires explicit --approve-synthetic-tests')
    directory=private_directory()/'verification'/time.strftime('%Y%m%d-%H%M%S');directory.mkdir(parents=True)
    results={'started':time.strftime('%Y-%m-%d %H:%M:%S'),'tests':{},'errors':[]}
    evidence=directory/'results.json'
    def record(name,value=True):
        results['tests'][name]=value;evidence.write_text(json.dumps(results,indent=2));print(name+': '+json.dumps(value),flush=True)
    app=QApplication([]);app.setStyle('Fusion');window=MainWindow(directory/'app-state');window.show()
    events=[];window.bridge.event.connect(lambda kind,conversation,data:events.append((kind,conversation,data)))
    def wait(predicate,timeout=90):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            app.processEvents();time.sleep(.02)
            if predicate():return
            if any(kind=='error' and target is None for kind,target,_ in events):
                raise RuntimeError(next(str(data) for kind,target,data in reversed(events) if kind=='error' and target is None))
        raise TimeoutError('Acceptance step timed out')
    def send(text,timeout=120):
        conversation=window.selected;offset=len(events)
        previous={x['id'] for x in window.store.messages(conversation)}
        window.input.setPlainText(text);QTest.keyClick(window.input,Qt.Key_Return,Qt.ControlModifier)
        wait(lambda:any(kind=='idle' and target==conversation for kind,target,_ in events[offset:]),timeout)
        errors=[data for kind,target,data in events[offset:] if kind=='error' and target==conversation]
        if errors:raise RuntimeError(str(errors[-1]))
        return '\n'.join(x['text'] for x in window.store.messages(conversation) if x['role']=='assistant' and x['id'] not in previous),events[offset:]
    fixture=None;site=None
    try:
        wait(lambda:bool(window.engine.models) and 'Connected' in window.connection.text(),90)
        record('native_window',window.isVisible() and window.width()>900)
        record('chatgpt_connection','Connected' in window.connection.text())
        text,turn_events=send('Remember the synthetic token cedar-482. Reply exactly: Ready cedar-482.')
        assert 'Ready cedar-482' in text
        record('real_ui_chat',True);record('streamed_deltas',sum(x[0]=='delta' for x in turn_events)>0)
        conversation=window.selected;thread=window.store.conversation(conversation)['thread']
        # Reconstruct both coordinator and native UI from saved state.
        window.close();app.processEvents()
        window=MainWindow(directory/'app-state');window.show();window.bridge.event.connect(lambda kind,c,data:events.append((kind,c,data)))
        wait(lambda:bool(window.engine.models) and 'Connected' in window.connection.text(),90);window.choose(conversation)
        text,_=send('Return only the synthetic token I asked you to remember.')
        assert 'cedar-482' in text and window.store.conversation(conversation)['thread']==thread
        record('restart_same_thread',True)
        state=directory/'fixture-state.json';code='MINT-'+str(random.randrange(100,999))
        manual_file=directory/'owner-manual.json'
        fixture=subprocess.Popen([sys.executable,str(APP/'tests/fixture_window.py'),'--state',str(state),'--code',code,'--manual-file',str(manual_file)])
        matches=[]
        def find():
            nonlocal matches
            matches=[w for w in window.desktop.windows() if w['title']=='Assistant Control Lab']
            return len(matches)==1
        wait(find,25);hwnd=matches[0]['hwnd']
        with window.permissions.lock:
            window.permissions.windows[hwnd]=window.desktop.identity(hwnd)
            window.permissions.observe=window.permissions.desktop=True
            window.permissions.routine_labels={'greeting','theme','ready','apply draft','name','style','reviewed'}
        window.permissions.resume(conversation)
        approved_fixture_windows={hwnd}
        def fixture_approval(target,label,action):
            # Test-only owner approval for this disposable window/local origin and fixture.
            assert target==conversation
            if 'window' in action:return int(action['window']) in approved_fixture_windows
            return bool(site) and origin(window.browser.page.url)==site_origin
        window.broker.approve=fixture_approval
        text,control_events=send(f'Use desktop.observe for window {hwnd}. Read the large painted code from the actual screenshot and include it in your reply. Then use desktop.inspect and desktop.action to set Greeting to Hello desktop, choose Theme Teal, check Ready, and click Apply draft. Inspect after each action, verify the saved draft, and report the visual code. Only operate this disposable Control Lab window.',180)
        assert code in text,'Model did not identify the painted image-only code'
        record('screenshot_perception',True)
        wait(lambda:state.exists(),3)
        assert json.loads(state.read_text())=={'greeting':'Hello desktop','theme':'Teal','ready':True}
        record('real_native_desktop_actions',True)
        # Attach real text, spreadsheet, PDF, image and ZIP fixtures.
        from PIL import Image,ImageDraw
        from openpyxl import Workbook
        from pypdf import PdfWriter
        files=directory/'fixtures';files.mkdir()
        (files/'fixture.txt').write_text('Synthetic attachment token: maple-619')
        book=Workbook();book.active.append(['Code','Amount']);book.active.append(['sheet-537',17]);book.save(files/'fixture.xlsx')
        image=Image.new('RGB',(600,150),'#083344');draw=ImageDraw.Draw(image);draw.text((30,50),'IMAGE BIRCH 824',fill='white',font_size=40);image.save(files/'fixture.png')
        # A minimal PDF with a text content stream, no embedded code.
        from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
        writer=PdfWriter();page=writer.add_blank_page(500,300)
        font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
        stream=DecodedStreamObject();stream.set_data(b'BT /F1 20 Tf 30 230 Td (PDF token pine-268) Tj ET');page[NameObject('/Contents')]=writer._add_object(stream)
        with (files/'fixture.pdf').open('wb') as output:writer.write(output)
        with zipfile.ZipFile(files/'fixture.zip','w') as archive:archive.writestr('inventory-only.txt','Not executed')
        window.add_files([str(files/name) for name in ('fixture.txt','fixture.xlsx','fixture.png','fixture.pdf','fixture.zip')])
        text,_=send('Read these five attachments. Return the text token, spreadsheet code and amount, PDF token, image words and number, and ZIP member name. Do not execute or extract the archive.',120)
        for expected in ('maple-619','sheet-537','17','pine-268','824','inventory-only.txt'):assert expected in text,expected
        record('five_attachment_formats',True)
        upload=next(x for row in window.store.messages(conversation) for x in json.loads(row['attachments']) if x['name']=='fixture.txt')
        site=ThreadingHTTPServer(('127.0.0.1',0),Site);threading.Thread(target=site.serve_forever,daemon=True).start()
        url=f'http://127.0.0.1:{site.server_port}/';site_origin=origin(url)
        window.permissions.origins={site_origin};window.permissions.browser=True;window.permissions.resume(conversation)
        text,_=send(f'Use the dedicated browser to open {url}. Fill Name with Cedar test, select Style teal, check Reviewed, upload attachment ID {upload["id"]} using the Fixture file control. Click Apply draft and verify dynamic result. Finally click Upload fixture to submit this synthetic fixture to the local test server. Verify Fixture received. Do not open any other site.',180)
        assert Site.uploaded and b'maple-619' in Site.uploaded
        record('real_browser_form_and_upload',True)
        send(f'Navigate the dedicated browser back to {url}, then stop this turn. Do not edit any fields yet.')
        matches=[w for w in window.desktop.windows() if w['title'].startswith('Assistant Browser Lab')]
        assert len(matches)==1,'Expected exactly one owned local-fixture browser window'
        browser_hwnd=matches[0]['hwnd'];approved_fixture_windows.add(browser_hwnd)
        window.permissions.windows[browser_hwnd]=window.desktop.identity(browser_hwnd)
        window.permissions.browser=False
        try:
            native_text,native_events=send(f'For the second browser mode, use only desktop.inspect and desktop.action to operate native browser window {browser_hwnd}. Do not use browser capabilities for the edits. Set the Name field to Desktop browser check, then click Apply draft and verify its displayed JSON result. This is still the disposable local test page.',180)
            assert any(kind=='action' and cap=='desktop.action' for kind,_,cap in native_events)
        finally:window.permissions.browser=True
        native_snapshot=window.desktop.inspect(browser_hwnd)
        assert any('Desktop browser check' in c['name'] and '"name"' in c['name'] for c in native_snapshot['controls']),'Native browser result was not verified from actual accessibility state'
        record('native_existing_browser_window_control',True)
        # A correction while the real model is working must reach turn/steer.
        offset=len(events);window.input.setPlainText('Inspect the local browser page, then give a detailed numbered explanation of the verification steps.');window.send()
        wait(lambda:window.engine.turn is not None,40)
        window.input.setPlainText('Correction: end your response with exactly STEERED-913.');window.send()
        wait(lambda:any(kind=='steered' and target==conversation for kind,target,_ in events[offset:]),40)
        wait(lambda:any(kind=='idle' and target==conversation for kind,target,_ in events[offset:]),120)
        assert any('STEERED-913' in x['text'] for x in window.store.messages(conversation) if x['role']=='assistant')
        record('real_active_turn_steering',True)
        # Stop a real turn at a pending synthetic action; no input after takeover.
        boundary=threading.Event()
        def pause_at_click(target,label,action):
            if action.get('operation')=='click' and 'apply draft' in label.lower():
                boundary.set()
                while not window.permissions.halted.wait(.05):pass
                return False
            return fixture_approval(target,label,action)
        window.permissions.routine_labels.discard('apply draft');window.broker.approve=pause_at_click
        original_review=window.broker._review
        def test_boundary(target,label,action,generation,context=None):
            if action.get('operation')=='click' and 'apply draft' in label.lower():
                if not pause_at_click(target,label,action):raise Denied('Synthetic takeover boundary')
            return original_review(target,label,action,generation,context)
        window.broker._review=test_boundary
        offset=len(events)
        window.input.setPlainText(f'In Control Lab window {hwnd}, inspect and set Greeting to Before takeover, then click Apply draft. If interrupted by the owner, inspect on resume, preserve any manual changes to Greeting, and report its exact current value.');window.send()
        wait(boundary.is_set,120)
        window.takeover();assert window.permissions.halted.is_set()
        wait(lambda:window.engine.active is None,15)
        try:
            window.broker.call(conversation,{'capability':'desktop.action','arguments':json.dumps({'window':hwnd,'operation':'click'})})
            raise AssertionError('Takeover allowed a new input action')
        except Denied:pass
        record('takeover_denies_new_input',True)
        manual_greeting='Owner edited '+str(random.randrange(1000,9999))
        manual_file.write_text(json.dumps({'greeting':manual_greeting}));wait(lambda:manual_file.with_suffix('.applied').exists(),5)
        window.broker.approve=fixture_approval;window.broker._review=original_review
        previous={x['id'] for x in window.store.messages(conversation)};offset=len(events)
        window.resume()
        wait(lambda:any(kind=='idle' and target==conversation for kind,target,_ in events[offset:]),120)
        text='\n'.join(x['text'] for x in window.store.messages(conversation) if x['role']=='assistant' and x['id'] not in previous)
        assert manual_greeting in text,'Resume did not recognize the actual manual UI change'
        assert window.store.conversation(conversation)['thread']==thread
        record('human_takeover_manual_change_same_thread_resume',True)
        # Test actual global registered hotkey dispatch, independent of AI.
        import ctypes
        window.permissions.resume(conversation)
        user=ctypes.windll.user32
        for key in (0x11,0x12,0x7B):user.keybd_event(key,0,0,0)
        for key in (0x7B,0x12,0x11):user.keybd_event(key,0,2,0)
        wait(lambda:window.permissions.halted.is_set(),5)
        record('global_emergency_shortcut',window.hotkey.registered)
        window.permissions.revoke();record('permissions_revoked',not window.permissions.windows and not window.permissions.origins)
        window.grab().save(str(directory/'synthetic-ui.png'))
        record('complete',True)
    except Exception as error:
        results['errors'].append(type(error).__name__+': '+str(error));record('complete',False);raise
    finally:
        window.close();app.processEvents()
        if site:site.shutdown();site.server_close()
        if fixture and fixture.poll() is None:fixture.terminate();fixture.wait(timeout=8)
        evidence.write_text(json.dumps(results,indent=2));print('Private evidence: '+str(evidence),flush=True)


if __name__=='__main__':main()
