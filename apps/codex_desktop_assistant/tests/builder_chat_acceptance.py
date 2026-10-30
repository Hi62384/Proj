"""Actual saved-chat complex Store Builder with independently verified receiver."""
import json
import sqlite3
import sys
import time
from pathlib import Path
APP=Path(__file__).resolve().parents[1];sys.path[:0]=[str(APP),str(Path(__file__).resolve().parent),str(APP.parents[1])]
from assistant.storage import private_directory
from live_app import LiveApp


def main():
    if '--approve-synthetic-tests' not in sys.argv:raise SystemExit('Synthetic test opt-in required')
    app=LiveApp();app.idle();before={r['id'] for r in app.rows('SELECT id FROM conversations')}
    app.invoke('Control Center');time.sleep(.3)
    dialog=next(c for c in app.window.descendants(control_type='Window') if c.window_text()=='Control Center')
    from pywinauto.controls.uia_controls import TabControlWrapper
    tabs=next(c for c in dialog.descendants(control_type='Tab') if any(i.window_text()=='Diagnostics' for i in c.descendants(control_type='TabItem')))
    dialog.set_focus();tabs.select('Diagnostics');time.sleep(.2);app.invoke('Run local builder test',dialog);dialog.close()
    conversation=app.wait(lambda:next((r['id'] for r in app.rows('SELECT id FROM conversations') if r['id'] not in before),None))
    deadline=time.monotonic()+240;started=False
    while time.monotonic()<deadline:
        state=app.rows('SELECT status,thread FROM conversations WHERE id=?',(conversation,))[0];started|=state['status']=='Working'
        if state['status'] in ('Waiting for User','Waiting for Approval','Error'):break
        if state['status']=='Completed' and started:break
        time.sleep(.25)
    from urllib.request import urlopen
    root=private_directory();info=json.loads((root/'verification/current-builder-fixture.json').read_text());assert info['conversation']==conversation
    with urlopen(info['url'].replace('/builder','/state'),timeout=5) as response:receiver=json.loads(response.read())
    actions=app.rows('SELECT operation,state FROM actions WHERE conversation=?',(conversation,));report='\n'.join(r['text'] for r in app.rows("SELECT text FROM messages WHERE conversation=? AND role='assistant' ORDER BY at",(conversation,)))
    result={'conversation':conversation,'state':state['status'],'saved_thread':bool(state['thread']),'receiver':receiver,'actions':actions,'report':report,'zero_human_interruptions':not app.rows("SELECT id FROM messages WHERE conversation=? AND state='Waiting for local approval'",(conversation,))}
    result['complete']=state['status']=='Completed' and receiver['draft_saves']==1 and receiver['publication_requests']==0 and receiver['payment_requests']==0 and receiver.get('dom',{}).get('color')=='#125e77' and receiver.get('dom',{}).get('layout')=='Editorial' and receiver.get('dom',{}).get('spacing')=='Comfortable' and result['zero_human_interruptions']
    out=root/'verification/builder-chat-20261029';out.mkdir(parents=True,exist_ok=True);(out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2),flush=True);assert result['complete']


if __name__=='__main__':main()
