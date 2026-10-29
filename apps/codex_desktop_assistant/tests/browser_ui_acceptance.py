"""Real Qt approval cards and production Chromium; no model response is mocked.

Account connection is disabled for this controller/UI test. Separate live suites
exercise real Codex inference. All approvals here concern disposable local sites.
"""
import json
import sys
import threading
import time
from concurrent.futures import Future
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from PySide6.QtWidgets import QApplication,QPushButton,QLabel
from PySide6.QtCore import Qt,QTimer
from PySide6.QtTest import QTest
from assistant.engine import Engine
from assistant.ui import MainWindow
from assistant.permissions import origin,Denied
from assistant.storage import private_directory
from browser_acceptance import Site


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Synthetic-test opt-in required')
    app=QApplication([]);results={};events=[];decisions=[];choice='Allow for This Session'
    directory=private_directory()/'verification'/('browser-ui-'+time.strftime('%Y%m%d-%H%M%S'));directory.mkdir(parents=True)
    servers=[ThreadingHTTPServer(('127.0.0.1',0),Site) for _ in range(2)]
    for server in servers:threading.Thread(target=server.serve_forever,daemon=True).start()
    urls=[f'http://127.0.0.1:{server.server_port}' for server in servers]
    connecting=threading.Event();release_connection=threading.Event();connected=threading.Event()
    def slow_connection(self):
        connecting.set();release_connection.wait(30);connected.set()
    connection_patch=patch.object(Engine,'ensure_connection',slow_connection);connection_patch.start()
    window=MainWindow(directory/'state')
    window.show();window.bridge.event.connect(lambda *args:events.append(args))
    original=window.browser.command
    def command(operation,**args):
        if operation=='verification':
            future=args['future']
            try:future.set_result(args['function']())
            except Exception as error:future.set_exception(error)
            return original('tabs')
        return original(operation,**args)
    window.browser.command=command
    def wait(predicate,timeout=30):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            app.processEvents();time.sleep(.02)
            if predicate():return
        raise TimeoutError(window.notice.text())
    def record(name):results[name]=True;print(name+': True',flush=True)
    def click(label):
        matches=[b for b in window.findChildren(QPushButton) if b.text()==label]
        assert len(matches)==1,(label,len(matches));QTest.mouseClick(matches[0],Qt.LeftButton)
    def run(function):
        future=Future();window.engine.queue.put(('browser_ui',window.selected,{'operation':'verification','function':function,'future':future}))
        wait(future.done);return future.result()
    def call(cap,args):return json.loads(window.broker.call(window.selected,{'capability':cap,'arguments':json.dumps(args)})[0]['text'])
    def decide():
        for request,card in window.request_cards:
            if request['event'].is_set():continue
            assert request['args'].get('website_access'),request['label']
            assert request['args']['origin'] in {origin(url) for url in urls},request['label']
            labels='\n'.join(l.text() for l in card.findChildren(QLabel))
            assert 'Website:' in labels and 'Page content' in labels
            decisions.append(request['args']);QTest.mouseClick(next(b for b in card.findChildren(QPushButton) if b.text()==choice),Qt.LeftButton)
    timer=QTimer();timer.timeout.connect(decide);timer.start(50)
    try:
        click('Open Browser');wait(lambda:bool(window.browser_tabs_state));assert window.permissions.browser;record('open_browser_from_main_ui_without_settings')
        assert connecting.is_set() and not connected.is_set();release_connection.set();record('browser_controls_work_while_account_connection_is_pending')
        snapshot=run(lambda:call('browser.navigate',{'url':urls[0]+'/app'}))
        assert origin(urls[0]) in window.permissions.origins and len(decisions)==1;record('chat_website_session_button_records_exact_origin')
        run(lambda:call('browser.navigate',{'url':urls[0]+'/landing'}));assert len(decisions)==1;record('session_grant_avoids_repeat_cards')
        choice='Allow Once';run(lambda:call('browser.navigate',{'url':urls[1]+'/app'}));assert origin(urls[1]) not in window.permissions.origins;record('allow_once_does_not_create_session_grant')
        click('Browser Tabs');wait(lambda:bool(window.browser_tabs_dialog));assert window.browser_tabs_dialog[1].count()==1;record('tabs_dialog_lists_real_browser_state')
        window.browser_tabs_dialog[0].close();app.processEvents()
        window.public_browser.setChecked(True);assert window.permissions.public_browsing;record('public_research_session_control')
        window.manual_browser.setChecked(True);assert window.permissions.browser_manual
        try:run(lambda:call('browser.inspect',{}));raise AssertionError('Manual hold allowed automated observation')
        except Denied:pass
        run(lambda:window.browser.page.locator('textarea#draft').fill('Owner edit preserved'))
        # Native window capabilities cannot bypass the dedicated-browser hold.
        windows=[w for w in window.desktop.windows() if w['pid'] in window.permissions.browser_pids]
        assert windows
        hwnd=windows[0]['hwnd'];window.permissions.windows[hwnd]=window.desktop.identity(hwnd)
        try:window.desktop.window(hwnd);raise AssertionError('Native input bypassed manual hold')
        except Denied:pass
        record('manual_control_blocks_browser_and_native_bypass')
        window.manual_browser.setChecked(False)
        snapshot=run(lambda:call('browser.inspect',{}));assert any(c['value']=='Owner edit preserved' for c in snapshot['controls']);record('return_control_reinspects_and_preserves_owner_edits')
        import win32gui
        window.activateWindow();window.raise_();app.processEvents()
        from pywinauto import Desktop as Native
        Native(backend='uia').window(handle=int(window.winId())).set_focus()
        foreground=win32gui.GetForegroundWindow()
        assert foreground==int(window.winId())
        run(lambda:call('browser.action',{'operation':'new_tab','url':urls[0]+'/landing'}))
        assert win32gui.GetForegroundWindow()==foreground;record('background_model_tab_does_not_steal_foreground')
        click('Show Browser');wait(lambda:win32gui.GetForegroundWindow()!=foreground);record('show_browser_explicitly_brings_browser_forward')
        click('Stop');window.refresh_status();assert not window.permissions.origins and not window.permissions.public_browsing and not window.public_browser.isChecked();record('stop_revokes_session_website_and_public_grants')
        choice='Deny';click('Open Browser')
        try:run(lambda:call('browser.navigate',{'url':urls[1]+'/landing'}));raise AssertionError('Denied website navigated')
        except Denied:pass
        count=len(decisions)
        try:run(lambda:call('browser.navigate',{'url':urls[1]+'/landing'}))
        except Denied:pass
        assert len(decisions)==count;record('denied_visit_does_not_repeat_approval')
        record('complete')
    finally:
        timer.stop();release_connection.set();window.close();app.processEvents();connection_patch.stop()
        for server in servers:server.shutdown();server.server_close()
        (directory/'results.json').write_text(json.dumps(results,indent=2));print('Private evidence: '+str(directory/'results.json'),flush=True)


if __name__=='__main__':main()
