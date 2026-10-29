"""Real account, native Qt approval buttons, foreground and scope acceptance.

Only disposable fixtures and generated files. No mocked model responses.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(APP.parents[1])]
from PySide6.QtCore import Qt,QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QPushButton,QMessageBox
from assistant.ui import MainWindow
from assistant.storage import private_directory
from assistant.permissions import Denied


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Requires explicit synthetic test opt-in')
    app=QApplication([]);app.setStyle('Fusion')
    directory=private_directory()/'verification'/('overhaul-'+time.strftime('%Y%m%d-%H%M%S'));directory.mkdir(parents=True)
    window=MainWindow(directory/'state');window.show();events=[];results={};fixtures=[]
    window.bridge.event.connect(lambda *event:events.append(event))
    def record(key,value=True):
        results[key]=value;(directory/'results.json').write_text(json.dumps(results,indent=2));print(key+': '+str(value),flush=True)
    def wait(predicate,timeout=120):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            app.processEvents();time.sleep(.02)
            if predicate():return
        raise TimeoutError('Acceptance step timed out: '+window.notice.text())
    approved=[];answer='Allow Once';fixture_handles=set()
    def owner_controls():
        modal=QApplication.activeModalWidget()
        if isinstance(modal,QMessageBox) and modal.windowTitle()=='Confirm recoverable deletion':modal.button(QMessageBox.Yes).click()
        for request,card in window.request_cards:
            if request['event'].is_set():continue
            args=request['args']
            if not args.get('file_permission'):
                if int(args.get('window',0)) not in fixture_handles:continue
                window.attention.open()
                approved.append((args['operation'],'synthetic-window',answer))
            else:
                if not Path(args['path']).is_relative_to(directory/'synthetic'):continue
                approved.append((args['operation'],Path(args['path']).name,answer))
            control=next(x for x in card.findChildren(QPushButton) if x.text()==answer)
            if args['operation']=='delete' and answer!='Deny':
                def confirm():
                    dialog=QApplication.activeModalWidget()
                    if isinstance(dialog,QMessageBox) and dialog.windowTitle()=='Confirm recoverable deletion':dialog.button(QMessageBox.Yes).click()
                QTimer.singleShot(100,confirm)
            QTest.mouseClick(control,Qt.LeftButton)
    approval_timer=QTimer();approval_timer.timeout.connect(owner_controls);approval_timer.start(100)
    def send(text,timeout=150):
        offset=len(events);window.input.setPlainText(text);window.send()
        wait(lambda:any(k=='idle' and c==window.selected for k,c,_ in events[offset:]),timeout)
        errors=[d for k,c,d in events[offset:] if k=='error' and c==window.selected]
        assert not errors,errors
        return events[offset:]
    try:
        wait(lambda:bool(window.engine.models) and 'Connected' in window.connection.text())
        record('real_account_catalog',{'models':window.model.count(),'efforts':window.effort.count()})
        assert window.model.count() and window.effort.count()
        for index in range(window.model.count()):
            window.model.setCurrentIndex(index)
            entry=window.models_catalog[index]
            assert [window.effort.itemData(i) for i in range(window.effort.count())]==[x['reasoningEffort'] for x in entry.get('supportedReasoningEfforts',[])]
        index=next((i for i,x in enumerate(window.models_catalog) if x.get('isDefault')),0);window.model.setCurrentIndex(index)
        supported=[window.effort.itemData(i) for i in range(window.effort.count())]
        window.effort.setCurrentIndex(supported.index('low') if 'low' in supported else 0)
        selected={'model':window.model.currentData(),'effort':window.effort.currentData()}
        calls=[];original=window.engine.rpc.request
        def real_request(method,params,**kwargs):
            if method=='thread/start' and '--legacy-tools' in sys.argv:
                import copy
                from assistant.tools import TOOL
                tool=copy.deepcopy(TOOL)
                tool['inputSchema']['properties']['capability']['enum']=[c for c in tool['inputSchema']['properties']['capability']['enum'] if c not in ('files.read','files.write','files.create','files.delete','files.list','desktop.list_apps')]
                tool['description']='Earlier saved assistant tool. files.read_approved reads an approved path. files.write_approved writes an approved path. Arguments is a JSON-encoded object. Desktop and browser operations are available.'
                params={**params,'dynamicTools':[tool]}
            if method=='turn/start':calls.append({k:params.get(k) for k in ('model','effort')})
            return original(method,params,**kwargs)
        window.engine.rpc.request=real_request
        send('Reply exactly OVERHAUL-READY-721.')
        assert calls[-1]==selected;assert any('OVERHAUL-READY-721' in x['text'] for x in window.store.messages(window.selected) if x['role']=='assistant')
        record('real_turn_model_effort_parameters',selected)
        window.resize(1100,720);app.processEvents();window.grab().save(str(directory/'dark.png'))
        window.store.setting('theme','Light');window.apply_settings();app.processEvents();window.grab().save(str(directory/'light.png'))
        window.store.setting('theme','Dark');window.apply_settings();record('native_dark_light_resize')
        if '--desktop-only' not in sys.argv:
            synthetic=directory/'synthetic';synthetic.mkdir();path=synthetic/'permission.txt'
            send(f'Use assistant_control files.create to create this synthetic text file: {path}. Content exactly BEFORE-642. Explain that this is a disposable permission test in the reason. Wait for the genuine local owner approval. Then report completion.')
            assert path.read_text()=='BEFORE-642';assert any(a[0]=='create' for a in approved);record('real_codex_create_with_chat_approval')
            send(f'Read {path} using files.read, then replace its content with AFTER-319 using files.write and the exact hash you read. Reason: disposable permission test. Report completion.')
            assert path.read_text()=='AFTER-319';assert any(a[0]=='read' for a in approved) and any(a[0]=='write' for a in approved);record('real_codex_read_write_with_chat_approval')
            answer='Allow for This Session';count=len(approved)
            send(f'Read {path} with files.read. Report the current content, using the tool even if you remember it.')
            assert len(approved)==count+1
            send(f'Read {path} again with files.read to verify it is unchanged. Report the result.')
            assert len(approved)==count+1;record('real_session_read_approval_reused')
            window.permissions.file_policy.session.clear()
            answer='Deny'
            send(f'Read {path} and use files.write to replace it with SHOULD-NOT-APPEAR. If owner denies permission, stop attempting the operation and briefly report denial without another handoff tool.')
            assert path.read_text()=='AFTER-319';record('denied_chat_request_prevents_mutation')
            answer='Allow Once';window.permissions.resume(window.selected)
            send(f'Read {path} using files.read and then delete only this disposable file using files.delete with its exact hash. Reason: clean up synthetic permission test. Request genuine owner approval. Report the result.')
            assert not path.exists();assert any(a[0]=='delete' for a in approved);record('real_codex_delete_confirm_and_recovery')
            record('notification_unread_and_focus',window.attention.unread>0)
            window.attention.open();app.processEvents();assert window.attention.unread==0
        if '--files-only' in sys.argv:
            record('legacy_saved_thread_compatibility','--legacy-tools' in sys.argv);record('approval_controls_used',approved);record('complete');return
        # Two independent, disposable native editor processes.
        fixture_prefix='Assistant Control Lab '+directory.name
        for i in range(2):
            fixtures.append(subprocess.Popen([sys.executable,str(APP/'tests/fixture_window.py'),'--state',str(directory/f'fixture-{i}.json'),'--code',f'SCOPE-{i}','--title',fixture_prefix+'-'+str(i),'--action-label','Submit synthetic draft']))
        wait(lambda:len([w for w in window.desktop.windows() if w['title'].startswith(fixture_prefix)])==2,30)
        targets=[w for w in window.desktop.windows() if w['title'].startswith(fixture_prefix)]
        fixture_handles.update(target['hwnd'] for target in targets)
        first,second=targets;window.permissions.windows={first['hwnd']:window.desktop.identity(first['hwnd'])};window.permissions.desktop_mode='Selected Window'
        window.permissions.desktop=window.permissions.observe=True;window.permissions.resume(window.selected)
        window.desktop.inspect(first['hwnd'])
        try:window.desktop.inspect(second['hwnd']);raise AssertionError('Unrelated window accessible')
        except Denied:pass
        record('selected_window_excludes_other_fixture')
        monitors=window.desktop.monitors();scope=monitors[0]
        # Fit only our own fixtures into the selected display.
        import win32gui,win32con
        for target in targets:win32gui.SetWindowPos(target['hwnd'],0,scope[0]+20,scope[1]+20,min(700,scope[2]-scope[0]-40),min(600,scope[3]-scope[1]-40),win32con.SWP_NOZORDER|win32con.SWP_NOACTIVATE)
        window.desktop.control({'window':first['hwnd'],'operation':'move_window','bounds':[scope[0]+30,scope[1]+30,min(700,scope[2]-scope[0]-60),min(600,scope[3]-scope[1]-60)]})
        record('real_window_move_resize')
        window.permissions.windows.clear();window.permissions.desktop_mode='Entire Monitor';window.permissions.capture_bounds=scope;window.permissions.monitor_layout=tuple(monitors)
        for target in targets:window.desktop.inspect(target['hwnd'])
        assert not window.permissions.windows;record('monitor_two_real_windows_without_individual_grants')
        # A real model task controls only the synthetic fixture, never personal apps.
        window.permissions.resume(window.selected)
        send(f'Use desktop.inspect then desktop.action to set Greeting in synthetic window {first["hwnd"]} to MONITOR-572. Do not click buttons or observe the whole monitor. Verify the field value after setting it.')
        observed=window.desktop.inspect(first['hwnd']);assert any(c['value']=='MONITOR-572' for c in observed['controls']);record('real_codex_monitor_window_control')
        send(f'In synthetic window {first["hwnd"]}, inspect and click Submit synthetic draft. This only saves disposable fixture JSON. Attempt desktop.action click directly; the host automatically requests exact permission. Do not call human.request_approval or human.request_input. Then verify the saved status. Do not use browser tools.')
        assert any(json.loads(path.read_text())['greeting']=='MONITOR-572' for path in directory.glob('fixture-*.json'))
        record('real_sensitive_action_chat_approval_continues_automatically')
        # Guarded ordinary installed program launch through the actual model tool.
        apps=window.desktop.installed_apps();notepad=next((name for name,path in apps.items() if Path(path).stem.lower()=='notepad'),None)
        assert notepad,apps
        window.permissions.allow_launches=True;window.permissions.resume(window.selected)
        before={w['hwnd'] for w in window.desktop.windows()}
        send(f'Use desktop.open_app with name {notepad!r} to open Notepad. Do not inspect, capture, type into or close any Notepad window. Report only the launch result.')
        wait(lambda:any('notepad' in w['title'].lower() and w['hwnd'] not in before for w in window.desktop.windows()),20)
        record('real_codex_installed_notepad_launch')
        # Opening chat is ordinary activity and must not interrupt inference.
        window.permissions.resume(window.selected);offset=len(events)
        window.input.setPlainText('Explain a careful ten-step plan for organizing synthetic project files. Do not use any tools.');window.send()
        wait(lambda:window.engine.turn is not None,40)
        window.desktop._api().window(handle=first['hwnd']).wrapper_object().set_focus()
        window.showNormal();window.raise_();window.activateWindow();QTest.qWait(200)
        assert not window.permissions.halted.is_set() and not window.engine.interrupt.is_set()
        record('real_foreground_chat_does_not_pause')
        window.input.setPlainText('Correction: end with exactly FOCUS-CONTINUES-783.');window.send()
        wait(lambda:any(k=='steered' for k,c,d in events[offset:]),30)
        wait(lambda:window.engine.active is None and any(k=='idle' for k,c,d in events[offset:]),120)
        record('focus_and_correction_preserve_current_thread')
        record('physical_input_hooks_registered',getattr(window.input_guard,'hooks_ready',False))
        window.stop();assert window.permissions.halted.is_set();record('stop_revokes_authority')
        record('approval_controls_used',approved);record('complete')
    except Exception as error:
        record('complete',False);record('error',type(error).__name__+': '+str(error));record('pause_events',[(k,str(d)) for k,c,d in events if k in ('paused','focus_paused')]);raise
    finally:
        approval_timer.stop();window.close();app.processEvents()
        if 'fixture_prefix' in locals():
            import win32gui
            for target in window.desktop.windows():
                if target['title'].startswith(fixture_prefix):win32gui.PostMessage(target['hwnd'],0x10,0,0)
            time.sleep(.5)
        for fixture in fixtures:
            if fixture.poll() is None:fixture.terminate();fixture.wait(timeout=10)
        print('Private evidence: '+str(directory/'results.json'),flush=True)


if __name__=='__main__':main()
