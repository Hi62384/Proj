"""Opt-in actual saved-chat/installed-extension tab test; never grants permissions.

Only this project's application is driven through accessibility. Real Codex does
all browser work. An independent disposable HTTP fixture proves navigation.
"""
import argparse
import json
import sqlite3
import sys
import time
import uuid
from pathlib import Path

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from assistant.storage import private_directory


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--approve-synthetic-tests',action='store_true')
    parser.add_argument('--directory',required=True)
    args=parser.parse_args()
    directory=Path(args.directory).resolve()
    if not args.approve_synthetic_tests or not directory.is_relative_to((private_directory()/'verification').resolve()):
        raise SystemExit('Explicit opt-in and private fixture directory required')
    fixture=json.loads((directory/'fixture.json').read_text())
    results={}
    def record(name,value=True):
        results[name]=value
        (directory/'tab-live-results.json').write_text(json.dumps(results,indent=2))
        print(name+': '+str(value),flush=True)
    def db(sql,params=()):
        connection=sqlite3.connect((private_directory()/'assistant.sqlite3').as_uri()+'?mode=ro',uri=True)
        connection.row_factory=sqlite3.Row
        try:return [dict(r) for r in connection.execute(sql,params)]
        finally:connection.close()
    if db("SELECT id FROM conversations WHERE status IN ('Working','Waiting for User','Thinking','Acting')"):
        raise SystemExit('An existing task is active; this test will not interrupt it')
    from pywinauto import Desktop
    import win32gui
    window=Desktop(backend='uia').window(title='Codex Desktop Assistant').wrapper_object()
    def invoke(name):
        next(c for c in window.descendants(control_type='Button') if c.window_text()==name).invoke()
    try:
        original={r['id'] for r in db('SELECT id FROM conversations')}
        invoke('+ New Chat')
        deadline=time.monotonic()+10
        conversation=None
        while conversation is None and time.monotonic()<deadline:
            conversation=next((r['id'] for r in db('SELECT id FROM conversations') if r['id'] not in original),None)
            time.sleep(.1)
        assert conversation,'The app did not create the verification chat'
        record('verification_conversation',conversation)
        mode=next(c for c in window.descendants(control_type='ComboBox') if c.selected_text() in ('Dedicated Browser','Existing Chrome'))
        mode.select('Existing Chrome')
        time.sleep(.3)
        if mode.selected_text()!='Existing Chrome':
            window.set_focus()  # Setup only, before measuring background work.
            mode.set_focus()
            mode.type_keys('{HOME}{DOWN}{ENTER}',set_foreground=False)
            time.sleep(.3)
        assert mode.selected_text()=='Existing Chrome'
        marker=uuid.uuid4().hex[:12]
        path='/clean-'+marker
        target=fixture['work'].split('/work')[0]+path
        record('synthetic_path',path)
        prompt=f'''Run a disposable Chrome tab-management integration test. Use only chrome.* capabilities through assistant_control; do not use desktop, shell, files, screenshots or unrelated websites. First list_tabs and remember which tabs are active, without inspecting unrelated tabs. Open exactly one background tab at {target} with chrome.open_tab. No selected/attached tab is required. If the new tab is authorized, inspect it, verify its clean disposable title, then close only that newly created clean tab with chrome.close_tab and list_tabs to verify its removal. If site authorization is required, leave the new tab open and report the exact permission needed; do not attempt to grant permission or open more tabs. Never show/activate a tab. Finally list_tabs and check that the previously active tabs remain active. Do not close or modify any preexisting tab. Report the new tab ID, authorization state and verified outcome.'''
        composer=next(c for c in window.descendants(control_type='Edit') if c.automation_id().endswith('.Composer'))
        composer.set_edit_text(prompt)
        foreground=win32gui.GetForegroundWindow()
        invoke('Send')
        record('real_message_submitted')
        deadline=time.monotonic()+180
        changed=False
        while time.monotonic()<deadline:
            changed|=win32gui.GetForegroundWindow()!=foreground
            state=db('SELECT status,thread FROM conversations WHERE id=?',(conversation,))[0]
            if state['status'] in ('Completed','Error','Waiting for User'):break
            time.sleep(.2)
        record('turn_state',state['status'])
        assert state['status']=='Completed',state['status']
        assert state['thread']
        record('saved_codex_thread_completed')
        state=json.loads((directory/'server-results.json').read_text())
        assert state.get('visits',{}).get(path,0)>=1,'Independent local server did not receive the created tab navigation'
        record('independent_server_verified_created_tab_navigation')
        actions=db('SELECT operation,state FROM actions WHERE conversation=?',(conversation,))
        assert any(a['operation']=='chrome.open_tab' and a['state']=='completed' for a in actions),actions
        record('real_broker_open_tab_completed')
        record('windows_foreground_unchanged_throughout',not changed)
        messages=db("SELECT text FROM messages WHERE conversation=? AND role='assistant' ORDER BY at",(conversation,))
        # Test prompt and replies contain only synthetic fixture metadata.
        report='\n'.join(m['text'] for m in messages)
        record('synthetic_model_report',report[-8000:])
        closed=any(a['operation']=='chrome.close_tab' and a['state']=='completed' for a in actions)
        record('clean_tab_close_live_verified',closed)
        record('original_conversations_retained',original.issubset({r['id'] for r in db('SELECT id FROM conversations')}))
        record('no_consequential_fixture_requests',all(state.get(k,0)==0 for k in ('publication_requests','purchase_requests','submissions','uploads')))
        record('complete',closed and not changed)
        if not closed:record('blocker','Chrome site permission is required for content access and safe close verification')
    except Exception as error:
        record('complete',False)
        record('error',type(error).__name__+': '+str(error))
        raise


if __name__=='__main__':main()
