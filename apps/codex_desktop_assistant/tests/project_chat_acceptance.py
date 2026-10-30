"""Actual owner-opted synthetic workflow through the saved assistant/model/broker.

No model, queue, artifact, publisher or approval results are mocked. Native UI
Invoke is used only on this project's application to start its explicit local test.
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
    parser=argparse.ArgumentParser();parser.add_argument('--approve-synthetic-tests',action='store_true');args=parser.parse_args()
    if not args.approve_synthetic_tests:raise SystemExit('Explicit synthetic test opt-in required')
    root=private_directory();result_dir=root/'verification/business-chat-acceptance';result_dir.mkdir(parents=True,exist_ok=True);results={}
    def record(key,value=True):results[key]=value;(result_dir/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(key+': '+str(value),flush=True)
    def rows(path,sql,params=()):
        db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
        try:return [dict(r) for r in db.execute(sql,params)]
        finally:db.close()
    db=root/'assistant.sqlite3';queue=root/'projects/queue.sqlite3'
    if rows(db,"SELECT id FROM conversations WHERE status IN ('Working','Waiting for User','Thinking','Acting')"):raise SystemExit('An existing chat is active; test will not interrupt it')
    if queue.is_file() and rows(queue,"SELECT id FROM projects WHERE state='running'"):raise SystemExit('An existing project is active; test will not interrupt it')
    from pywinauto import Desktop
    window=Desktop(backend='uia').window(title='Codex Desktop Assistant').wrapper_object()
    def invoke(name):next(c for c in window.descendants(control_type='Button') if c.window_text()==name).invoke()
    before={r['id'] for r in rows(db,'SELECT id FROM conversations')}
    invoke('Projects');time.sleep(.5);invoke('Run local five-product test')
    deadline=time.monotonic()+30;conversation=None
    while not conversation and time.monotonic()<deadline:
        candidates=rows(db,"SELECT DISTINCT c.id FROM conversations c JOIN messages m ON m.conversation=c.id WHERE m.role='user' AND m.text LIKE 'Create five distinct spreadsheet products%'")
        conversation=next((r['id'] for r in candidates if r['id'] not in before),None);time.sleep(.1)
    assert conversation,'Owner-invoked workflow did not submit the real message';record('conversation',conversation);record('real_workflow_message_sent')
    project=None;deadline=time.monotonic()+1000
    try:
        while time.monotonic()<deadline:
            task=rows(db,'SELECT status,thread FROM conversations WHERE id=?',(conversation,))[0]
            if task['status']=='Waiting for User':raise AssertionError('Fully authorized synthetic test requested human intervention')
            if queue.is_file():
                projects=rows(queue,'SELECT * FROM projects WHERE conversation=?',(conversation,))
                if projects:
                    project=projects[0]['id'];counts=rows(queue,'SELECT state,COUNT(*) count FROM jobs WHERE project=? GROUP BY state',(project,));current={r['state']:r['count'] for r in counts}
                    if results.get('task_counts')!=current:record('task_counts',current)
                    if projects[0]['state']=='completed' and task['status']=='Completed':break
                    failures=rows(queue,"SELECT key,error FROM jobs WHERE project=? AND state IN ('failed','review')",(project,))
                    if failures:raise AssertionError(failures)
            if task['status']=='Error':raise AssertionError('Real Codex turn errored')
            time.sleep(.5)
        assert project and task['status']=='Completed' and projects[0]['state']=='completed','Workflow did not reach verified completion'
        assert task['thread'];record('saved_codex_thread_completed')
        jobs=rows(queue,'SELECT key,kind,state,result FROM jobs WHERE project=?',(project,));assert len(jobs)>=25 and all(j['state']=='completed' for j in jobs)
        assert sum(j['kind']=='verify' for j in jobs)==5;record('full_real_model_planned_queue_completed')
        effects=rows(queue,'SELECT state,result FROM effects WHERE project=?',(project,));assert len(effects)==5 and all(e['state']=='verified' for e in effects)
        record('five_external_local_store_effects_verified')
        from urllib.request import urlopen
        for effect in effects:
            listing=json.loads(effect['result'])
            with urlopen(listing['download_url'],timeout=10) as response:
                import hashlib
                assert hashlib.sha256(response.read()).hexdigest()==listing['sha256']
        record('independent_live_download_hashes_match')
        actions=rows(db,"SELECT operation,state FROM actions WHERE conversation=?",(conversation,));assert any(a['operation'].startswith('projects.') and a['state']=='completed' for a in actions)
        record('real_broker_project_capabilities_exercised')
        approvals=rows(db,"SELECT id FROM messages WHERE conversation=? AND state='Waiting for local approval'",(conversation,));assert not approvals;record('zero_human_interruptions')
        assert before<={r['id'] for r in rows(db,'SELECT id FROM conversations')};record('existing_conversations_preserved')
        record('project',project);record('complete')
    except Exception as error:
        record('complete',False);record('error',type(error).__name__+': '+str(error));raise


if __name__=='__main__':main()
