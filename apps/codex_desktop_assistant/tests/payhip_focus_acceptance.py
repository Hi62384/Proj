"""Isolate real read-only DOM work from the UI Send/Attach setup phase."""
import argparse
import ctypes
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.storage import private_directory


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--owner-authorized-readonly',action='store_true');parser.add_argument('--conversation',required=True);args=parser.parse_args()
    if not args.owner_authorized_readonly:raise SystemExit('Read-only owner scope required')
    root=private_directory();out=root/'verification/payhip-readonly-20261029/focus-followup.json'
    def db(sql,params=()):
        c=sqlite3.connect((root/'assistant.sqlite3').as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
        try:return [dict(r) for r in c.execute(sql,params)]
        finally:c.close()
    if db("SELECT id FROM conversations WHERE status IN ('Working','Waiting for User','Thinking','Acting')"):raise SystemExit('An existing turn is active')
    from pywinauto import Desktop
    import win32gui,win32process
    window=Desktop(backend='uia').window(title='Codex Desktop Assistant').wrapper_object()
    # The prior exact-tab read-only test left this verification chat selected.
    # Verify its latest user-message timestamp after sending rather than switching
    # app/browser windows, tabs or permissions during this measurement.
    before=db('SELECT MAX(at) at FROM messages WHERE conversation=?',(args.conversation,))[0]['at']
    composer=next(c for c in window.descendants(control_type='Edit') if c.automation_id().endswith('.Composer'))
    composer.set_edit_text('Continue only the authorized read-only Payhip check in this same chat: call chrome.inspect once on the same attached Payhip tab. Do not click, navigate, edit, show tabs, access another page or use desktop/files/screenshots. Report whether the current page remains inspectable; do not reproduce private details.')
    next(c for c in window.descendants(control_type='Button') if c.window_text()=='Send').invoke()
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        if db('SELECT MAX(at) at FROM messages WHERE conversation=?',(args.conversation,))[0]['at']>before:break
        time.sleep(.1)
    time.sleep(1)  # Exclude the explicit user Send accessibility invocation.
    baseline=win32gui.GetForegroundWindow();seen=[];start=time.time();deadline=time.monotonic()+120
    while time.monotonic()<deadline:
        handle=win32gui.GetForegroundWindow();pid=win32process.GetWindowThreadProcessId(handle)[1] if handle else 0
        state={'handle':handle,'pid':pid,'class':win32gui.GetClassName(handle) if handle else '', 'seconds':round(time.time()-start,2)}
        if not seen or seen[-1]['handle']!=handle:seen.append(state)
        current=db('SELECT status FROM conversations WHERE id=?',(args.conversation,))[0]['status']
        if current in ('Completed','Error','Waiting for User'):break
        time.sleep(.1)
    actions=db('SELECT operation,state FROM actions WHERE conversation=? AND at>=?',(args.conversation,start))
    results={'state':current,'foreground_stable_after_send':all(s['handle']==baseline for s in seen),'foreground_transitions_metadata_only':seen,'actions_after_measurement_started':actions,'real_inspection_completed':any(a['operation']=='chrome.inspect' and a['state']=='completed' for a in actions),'no_mutations':all(a['operation']=='chrome.inspect' for a in actions)}
    out.write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2),flush=True)
    assert current=='Completed' and results['real_inspection_completed'] and results['no_mutations']


if __name__=='__main__':main()
