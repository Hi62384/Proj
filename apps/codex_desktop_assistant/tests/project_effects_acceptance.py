"""Real HTTP lost-response/restart reconciliation using previously QA'd packages."""
import argparse
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.projects import ProjectQueue
from assistant.test_storefront import TestStorefront,LocalStoreAdapter


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--approve-synthetic-tests',action='store_true');parser.add_argument('--directory',required=True);parser.add_argument('--project',required=True);args=parser.parse_args()
    if not args.approve_synthetic_tests:raise SystemExit('Explicit synthetic scope required')
    root=Path(args.directory);results={}
    def record(key,value=True):results[key]=value;(root/'recovery-results.json').write_text(json.dumps(results,indent=2));print(key+': '+str(value),flush=True)
    q=ProjectQueue(root);project=args.project;p=q.rows('SELECT * FROM projects WHERE id=?',(project,))[0];owner=p['conversation']
    store=TestStorefront(root/'recovery-store');adapter=LocalStoreAdapter(store);store_id='synthetic-recovery';q.adapters[store_id]=adapter
    products=[json.loads(j['payload'])['product'] for j in q.rows("SELECT payload FROM jobs WHERE project=? AND kind='package' AND state='completed'",(project,))];assert len(products)==5
    jobs=[]
    for product in products:
        key=product['id'];jobs.extend([{'key':key+':recovery-publish','kind':'publish','payload':{'product':product,'store':store_id},'needs':[key+':package']},{'key':key+':recovery-verify','kind':'verify','payload':{'product':product,'store':store_id},'needs':[key+':recovery-publish']}])
    q.add(project,owner,jobs);q.approve_scope(q.scope_manifest(project,owner,store_id,[p['id'] for p in products]));calls={};original=adapter.publish;lost={'once':False}
    def publish(key,package,path):
        calls[key]=calls.get(key,0)+1;result=original(key,package,path)
        if not lost['once']:lost['once']=True;raise TimeoutError('Synthetic receiver committed but response was lost')
        return result
    adapter.publish=publish
    try:
        q.control(project,owner,'resume');deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            if q.rows("SELECT id FROM jobs WHERE project=? AND state='review'",(project,)):break
            time.sleep(.05)
        assert lost['once'];record('real_receiver_commit_followed_by_lost_response')
        q.close();q=ProjectQueue(root);q.adapters[store_id]=adapter
        review=q.rows("SELECT * FROM jobs WHERE project=? AND kind='publish' AND state='review'",(project,));assert review;record('restart_kept_uncertain_writes_in_review')
        # Explicit reconciliation request; the handler must look up first and
        # must not submit the already-created listing a second time.
        for job in q.rows("SELECT id FROM jobs WHERE project=? AND state IN ('review','blocked')",(project,)):q.retry(project,owner,job['id'])
        q.control(project,owner,'resume');deadline=time.monotonic()+45
        while time.monotonic()<deadline:
            if q.summary(project,owner)['state']=='completed':break
            errors=q.rows("SELECT key,error FROM jobs WHERE project=? AND state IN ('failed','review')",(project,))
            if errors:raise AssertionError(errors)
            time.sleep(.1)
        assert q.summary(project,owner)['state']=='completed';assert store.count()==5
        assert len(calls)==5 and all(count==1 for count in calls.values());record('each_product_written_once_across_restart_and_reconciliation')
        assert len(q.rows("SELECT key FROM effects WHERE project=? AND store=? AND state='verified'",(project,store_id)))==5;record('all_five_reconciled_effects_durably_verified')
        q.revoke_scope(project,owner);record('scope_revoked_after_test');record('complete')
    except Exception as error:record('complete',False);record('error',type(error).__name__+': '+str(error));raise
    finally:q.close();store.close()


if __name__=='__main__':main()
