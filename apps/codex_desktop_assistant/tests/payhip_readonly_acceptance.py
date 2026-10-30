"""Owner-authorized exact-tab read-only Payhip check via the real saved chat.

No edits, clicks, navigation, publication, screenshots or private profile access.
"""
import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.storage import private_directory


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--owner-authorized-readonly',action='store_true');args=parser.parse_args()
    if not args.owner_authorized_readonly:raise SystemExit('Exact-tab owner authorization required')
    root=private_directory();out=root/'verification/payhip-readonly-20261029';out.mkdir(parents=True,exist_ok=True);results={}
    def record(key,value=True):results[key]=value;(out/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(key+': '+str(value),flush=True)
    def db(sql,params=()):
        c=sqlite3.connect((root/'assistant.sqlite3').as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
        try:return [dict(r) for r in c.execute(sql,params)]
        finally:c.close()
    if db("SELECT id FROM conversations WHERE status IN ('Working','Waiting for User','Thinking','Acting')"):raise SystemExit('An existing task is active; it will not be interrupted')
    from pywinauto import Desktop
    import win32gui
    window=Desktop(backend='uia').window(title='Codex Desktop Assistant').wrapper_object()
    def invoke(parent,name):next(c for c in parent.descendants(control_type='Button') if c.window_text()==name).invoke()
    def wait(predicate,seconds=20):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            value=predicate()
            if value:return value
            time.sleep(.1)
        raise TimeoutError('Application did not reach the required read-only test state')
    try:
        original={r['id'] for r in db('SELECT id FROM conversations')};invoke(window,'+ New Chat')
        conversation=wait(lambda:next((r['id'] for r in db('SELECT id FROM conversations') if r['id'] not in original),None));record('conversation',conversation)
        mode=next(c for c in window.descendants(control_type='ComboBox') if c.selected_text() in ('Dedicated Browser','Existing Chrome'))
        mode.select('Existing Chrome');time.sleep(.3)
        if mode.selected_text()!='Existing Chrome':window.set_focus();mode.set_focus();mode.type_keys('{HOME}{DOWN}{ENTER}',set_foreground=False);time.sleep(.3)
        assert mode.selected_text()=='Existing Chrome'
        invoke(window,'Chrome Tabs / Select Window');dialog=wait(lambda:next(iter(window.descendants(control_type='Window',title='Chrome Tabs')),None))
        candidates=[item for item in dialog.descendants(control_type='ListItem') if re.search(r'https://(?:www\.)?payhip\.com(?::443)?(?:\s|$|/)',item.window_text())]
        assert len(candidates)==1,'Exactly one extension-authorized Payhip tab is required'
        item=candidates[0];tab=int(re.search(r'Tab (\d+)',item.window_text()).group(1));item.set_focus();item.select();invoke(dialog,'Attach Tab');time.sleep(.2);dialog.close()
        record('exact_owner_authorized_payhip_tab_attached')
        prompt=f'''Perform ONLY the owner-authorized read-only Payhip compatibility check on attached Chrome tab {tab}. Use chrome.list_tabs and chrome.inspect, optionally chrome.frames and inspection of already-authorized same-origin frames. Do not use any other tab, other site, desktop, shell, files, screenshots, click/fill/check/select/upload/download, navigation/back/forward/reload, or Show Tab. Preserve unsaved human edits and the selected browser tab. Inspect the Store Builder page in the background. Briefly identify visible editable store sections and their safe element/control types, distinguish structural support from untested editing, and state whether an existing hidden calculator listing is actually visible and identifiable. If it is not visible, say it cannot be confirmed from this page; do not infer it exists or navigate elsewhere. Authentication secrets, tokens and unrelated personal data must not be reproduced. No publishing, payment settings, draft edits or financial changes. Finish with a concise factual capability/limitation report based on actual observations.'''
        composer=next(c for c in window.descendants(control_type='Edit') if c.automation_id().endswith('.Composer'));composer.set_edit_text(prompt)
        window.set_focus();foreground=win32gui.GetForegroundWindow();invoke(window,'Send');record('real_readonly_message_submitted')
        deadline=time.monotonic()+180;changed=False
        while time.monotonic()<deadline:
            changed|=win32gui.GetForegroundWindow()!=foreground
            state=db('SELECT status,thread FROM conversations WHERE id=?',(conversation,))[0]
            if state['status'] in ('Completed','Error','Waiting for User'):break
            time.sleep(.2)
        record('turn_state',state['status']);assert state['status']=='Completed'
        actions=db('SELECT operation,state FROM actions WHERE conversation=?',(conversation,));operations={a['operation'] for a in actions}
        assert operations<={'chrome.list_tabs','chrome.inspect','chrome.frames'},operations
        assert any(a['operation']=='chrome.inspect' and a['state']=='completed' for a in actions),'No real Payhip inspection succeeded'
        record('installed_extension_inspected_real_payhip_via_saved_model_thread')
        record('no_mutating_navigation_file_or_desktop_capabilities_used')
        record('windows_foreground_unchanged_throughout',not changed)
        report='\n'.join(m['text'] for m in db("SELECT text FROM messages WHERE conversation=? AND role='assistant' ORDER BY at",(conversation,)))
        record('readonly_findings',report[-9000:]);assert original<={r['id'] for r in db('SELECT id FROM conversations')};record('existing_conversations_preserved');record('complete')
    except Exception as error:record('complete',False);record('error',type(error).__name__+': '+str(error));raise


if __name__=='__main__':main()
