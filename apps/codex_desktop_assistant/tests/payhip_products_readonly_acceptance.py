"""Real saved-chat automatic new-tab/read-only Products/clean-close acceptance.

Requires the owner's separately granted Payhip site scope. Never edits products.
"""
import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.storage import private_directory


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--owner-authorized-site-readonly',action='store_true');parser.add_argument('--conversation',required=True);args=parser.parse_args()
    if not args.owner_authorized_site_readonly:raise SystemExit('Owner site/read-only scope required')
    root=private_directory();out=root/'verification/payhip-readonly-20261029/products-results.json';results={}
    def record(key,value=True):results[key]=value;out.write_text(json.dumps(results,indent=2),encoding='utf-8');print(key+': '+str(value),flush=True)
    def db(sql,params=()):
        c=sqlite3.connect((root/'assistant.sqlite3').as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
        try:return [dict(r) for r in c.execute(sql,params)]
        finally:c.close()
    if db("SELECT id FROM conversations WHERE status IN ('Working','Waiting for User','Thinking','Acting')"):raise SystemExit('An existing turn is active')
    from pywinauto import Desktop
    import win32gui
    window=Desktop(backend='uia').window(title='Codex Desktop Assistant').wrapper_object()
    start=time.time()
    prompt='''The owner has now explicitly granted Payhip site access and authorized this read-only Products check. Preserve the original Store Builder tab and all its unsaved work. Use only chrome.list_tabs, chrome.open_tab, chrome.inspect, chrome.frames if needed, and chrome.close_tab for the ONE new tab you create. First list tabs to remember active tabs. Open exactly one background tab at https://payhip.com/products with chrome.open_tab; the granted site should make it controllable and attached automatically. Inspect ONLY that returned tab ID. Identify whether the Cleaning Business Pricing & Profit Calculator appears as an actual product listing and whether a Hidden/unlisted visibility label is actually visible. Do not infer visibility from About Me text or absence on the storefront. Do not click links/buttons, open menus, change filters, navigate existing tabs, upload, publish, edit, download, request screenshots or use desktop/files. Do not expose account authentication or unrelated private data. After inspection, close ONLY this newly created tab if the host's clean-close check allows it; leave original tabs untouched. If any step is denied or requires further authorization, stop that step and report it; do not work around the restriction or create extra tabs. Finally list tabs to verify the new tab is removed and that prior active tabs remain active. Give a concise report of actual findings and unsupported checks.'''
    composer=next(c for c in window.descendants(control_type='Edit') if c.automation_id().endswith('.Composer'));composer.set_edit_text(prompt)
    next(c for c in window.descendants(control_type='Button') if c.window_text()=='Send').invoke();record('real_site_authorized_products_message_submitted')
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        if db("SELECT id FROM messages WHERE conversation=? AND role='user' AND at>=?",(args.conversation,start)):break
        time.sleep(.1)
    time.sleep(1);foreground=win32gui.GetForegroundWindow();changed=False;deadline=time.monotonic()+180
    try:
        while time.monotonic()<deadline:
            changed|=win32gui.GetForegroundWindow()!=foreground
            state=db('SELECT status FROM conversations WHERE id=?',(args.conversation,))[0]['status']
            if state=='Waiting for User':
                # Preserve possibly unsaved content rather than granting a close.
                for card in window.descendants(control_type='Group'):
                    texts='\n'.join(c.window_text() for c in card.descendants(control_type='Text'))
                    if 'Close tab with possible unsaved edits' in texts:
                        next(c for c in card.descendants(control_type='Button') if c.window_text()=='Deny').invoke();record('close_review_denied_to_preserve_possible_edits')
            if state in ('Completed','Error'):break
            time.sleep(.2)
        record('turn_state',state);assert state=='Completed'
        actions=db('SELECT operation,state FROM actions WHERE conversation=? AND at>=?',(args.conversation,start));permitted={'chrome.list_tabs','chrome.open_tab','chrome.inspect','chrome.frames','chrome.close_tab'}
        assert all(a['operation'] in permitted or (a['operation']=='assistant_control' and a['state']=='denied or failed') for a in actions),actions
        record('no_product_mutation_or_original_tab_navigation')
        opened=sum(a['operation']=='chrome.open_tab' and a['state']=='completed' for a in actions);assert opened==1;record('one_real_background_tab_created')
        inspected=any(a['operation']=='chrome.inspect' and a['state']=='completed' for a in actions);record('new_tab_automatically_authorized_and_inspected',inspected)
        closed=any(a['operation']=='chrome.close_tab' and a['state']=='completed' for a in actions);record('new_clean_tab_closed_without_approval',closed)
        record('foreground_stable_after_send_setup',not changed)
        report='\n'.join(m['text'] for m in db("SELECT text FROM messages WHERE conversation=? AND role='assistant' AND at>=? ORDER BY at",(args.conversation,start)));record('readonly_findings',report[-8000:])
        record('complete',inspected and closed)
    except Exception as error:record('complete',False);record('error',type(error).__name__+': '+str(error));raise


if __name__=='__main__':main()
