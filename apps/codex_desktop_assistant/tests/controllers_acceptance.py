"""Real Windows/Playwright tests independent of model availability; synthetic data only."""
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from http.server import ThreadingHTTPServer

APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from assistant.permissions import Permissions,Denied,origin
from assistant.desktop import Desktop,EmergencyStop
from assistant.browser import Browser
from assistant.storage import private_directory
from live_acceptance import Site


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Explicit synthetic-test opt-in required')
    directory=private_directory()/'verification'/('controllers-'+time.strftime('%Y%m%d-%H%M%S'));directory.mkdir(parents=True)
    results={};fixture=None;site=None;browser=None;hotkey=None
    def record(name,value=True):results[name]=value;print(name+': '+str(value),flush=True);(directory/'results.json').write_text(json.dumps(results,indent=2))
    permissions=Permissions();desktop=Desktop(permissions)
    import pythoncom
    pythoncom.CoInitialize()
    try:
        state=directory/'state.json'
        fixture=subprocess.Popen([sys.executable,str(APP/'tests/fixture_window.py'),'--state',str(state),'--code','LEAF-583'])
        deadline=time.monotonic()+30;matches=[]
        while time.monotonic()<deadline:
            matches=[x for x in desktop.windows() if x['title']=='Assistant Control Lab']
            if len(matches)==1:break
            time.sleep(.2)
        assert len(matches)==1,'Disposable native fixture not found'
        hwnd=matches[0]['hwnd'];permissions.windows[hwnd]=desktop.identity(hwnd)
        permissions.observe=permissions.desktop=True;permissions.resume('test')
        try:desktop.window(hwnd+1);raise AssertionError('Unapproved window was allowed')
        except Denied:record('unapproved_window_denied')
        observation=desktop.inspect(hwnd);record('real_accessibility_tree',len(observation['controls'])>3)
        def find(name,role=None):
            nonlocal observation
            observation=desktop.inspect(hwnd)
            matches=[x for x in observation['controls'] if name.lower() in x['name'].lower() and (role is None or x['role']==role)]
            assert len(matches)==1,(name,observation)
            return matches[0]['element']
        def action(name,op,**fields):
            element=find(name)
            return desktop.control({'window':hwnd,'observation':observation['observation'],'element':element,'operation':op,**fields})
        action('Greeting','type',text='Controller test')
        action('Theme','select',text='Teal')
        action('Ready','check',checked=True)
        action('Apply draft','click')
        deadline=time.monotonic()+3
        while not state.exists() and time.monotonic()<deadline:time.sleep(.05)
        assert json.loads(state.read_text())=={'greeting':'Controller test','theme':'Teal','ready':True}
        record('native_edit_dropdown_checkbox_button')
        raw=desktop.capture(hwnd)
        from PIL import Image
        import io
        image=Image.open(io.BytesIO(raw));assert image.width>100 and image.height>100
        image.save(directory/'synthetic-window.png');record('actual_window_capture',{'width':image.width,'height':image.height,'nonuniform':image.getextrema()[0][0]!=image.getextrema()[0][1]})
        permissions.halt()
        try:
            with permissions.action('test'):desktop.control({'window':hwnd,'operation':'click'})
            raise AssertionError('Pause allowed input')
        except Denied:record('pause_denies_new_input')
        permissions.resume('test');hotkey=EmergencyStop(permissions.halt);assert hotkey.registered,'Emergency shortcut is already in use'
        import ctypes
        user=ctypes.windll.user32
        for key in (0x11,0x12,0x7B):user.keybd_event(key,0,0,0)
        for key in (0x7B,0x12,0x11):user.keybd_event(key,0,2,0)
        deadline=time.monotonic()+3
        while not permissions.halted.is_set() and time.monotonic()<deadline:time.sleep(.02)
        assert permissions.halted.is_set();record('real_global_emergency_shortcut')
        site=ThreadingHTTPServer(('127.0.0.1',0),Site);threading.Thread(target=site.serve_forever,daemon=True).start()
        url=f'http://127.0.0.1:{site.server_port}/';permissions.origins={origin(url)};permissions.browser=True;permissions.resume('test')
        browser=Browser(directory,permissions);snapshot=browser.call({'operation':'navigate','url':url})
        browser.call({'operation':'navigate','url':url+'safe-redirect'})
        assert browser.page.url==url;record('approved_redirect_preserves_real_url')
        try:
            browser.call({'operation':'navigate','url':url+'blocked-redirect'})
            raise AssertionError('Unapproved redirect was followed')
        except Exception as error:
            assert not isinstance(error,AssertionError)
            record('unapproved_redirect_blocked')
        browser.call({'operation':'navigate','url':url})
        def browser_action(label,op,**fields):
            snapshot=browser.call({'operation':'inspect'})
            matches=[x for x in snapshot['controls'] if x['label'].strip()==label]
            assert len(matches)==1,(label,snapshot['controls'])
            return browser.call({'operation':op,'element':matches[0]['element'],'observation':snapshot['observation'],**fields},approved=True)
        browser_action('Name','fill',text='Browser test');browser_action('Style','select',text='teal');browser_action('Reviewed','check',checked=True)
        upload=directory/'fixture.txt';upload.write_text('maple-619 synthetic fixture')
        browser_action('Fixture file','upload',approved_path=str(upload))
        snapshot=browser_action('Apply draft','click');assert 'Browser test' in snapshot['text'] and 'teal' in snapshot['text']
        record('browser_dynamic_form_verified')
        upload_result=browser_action('Upload fixture','click')
        assert Site.uploaded and b'maple-619' in Site.uploaded,{'received_bytes':len(Site.uploaded or b''),'browser_error':browser.last_error,'page':upload_result['text'][:300]}
        record('browser_real_file_upload')
        try:browser.call({'operation':'navigate','url':'https://example.org'});raise AssertionError('Unapproved origin allowed')
        except Denied:record('browser_unapproved_origin_denied')
        permissions.revoke()
        try:
            with permissions.action('test'):browser.call({'operation':'inspect'})
            raise AssertionError('Revoked permissions allowed action')
        except Denied:record('revocation_denies_actions')
        record('complete')
    except Exception as error:
        record('error',type(error).__name__+': '+str(error));record('complete',False);raise
    finally:
        if browser:browser.close()
        if hotkey:hotkey.close()
        if site:site.shutdown();site.server_close()
        if fixture and fixture.poll() is None:fixture.terminate();fixture.wait(timeout=5)
        pythoncom.CoUninitialize()
        print('Private evidence: '+str(directory/'results.json'),flush=True)


if __name__=='__main__':main()
