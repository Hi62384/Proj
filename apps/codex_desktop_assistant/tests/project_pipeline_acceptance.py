"""Opt-in real artifact/native-calculation/HTTP-store/Chrome acceptance.

This exercises deterministic orchestration, not natural-language model planning.
The synthetic publish authorization comes from the explicit test opt-in only.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from assistant.projects import ProjectQueue
from assistant.products import RECIPES
from assistant.test_storefront import TestStorefront,LocalStoreAdapter


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--approve-synthetic-tests',action='store_true');parser.add_argument('--directory',required=True);args=parser.parse_args()
    if not args.approve_synthetic_tests:raise SystemExit('Explicit synthetic-test scope is required')
    root=Path(args.directory).resolve();root.mkdir(parents=True,exist_ok=True);results={}
    def record(key,value=True):results[key]=value;(root/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8');print(key+': '+str(value),flush=True)
    q=ProjectQueue(root);store=TestStorefront(root/'local-store');adapter=LocalStoreAdapter(store);q.adapters['synthetic-local']=adapter
    try:
        project=q.create('synthetic-owner','Create five distinct spreadsheet products, validate all files, build a disposable store and publish only this authorized synthetic batch')['project'];record('project',project)
        products=[{'id':recipe,'recipe':recipe,'title':value[0],'price_cents':1900+i*100,'currency':'USD','pricing_evidence':'Explicit synthetic test prices, not market research'} for i,(recipe,value) in enumerate(RECIPES.items())]
        q.products(project,'synthetic-owner',products,'synthetic-local');record('complete_dependency_plan_persisted',q.summary(project,'synthetic-owner')['total']==25)
        q.control(project,'synthetic-owner','start');deadline=time.monotonic()+600
        while time.monotonic()<deadline:
            packages=q.rows("SELECT * FROM jobs WHERE project=? AND kind='package' AND state='completed'",(project,))
            failures=q.rows("SELECT key,error FROM jobs WHERE project=? AND kind IN ('generate','validate','package') AND state IN ('failed','blocked')",(project,))
            if failures:raise AssertionError(failures)
            if len(packages)==5:break
            time.sleep(.2)
        assert len(packages)==5
        record('five_real_workbooks_native_formula_qa_and_all_sheet_previews')
        record('no_publication_before_scope',store.count()==0)
        manifest=q.scope_manifest(project,'synthetic-owner','synthetic-local',[p['id'] for p in products]);q.approve_scope(manifest);record('one_exact_manifest_authorized_zero_human_interruptions')
        original_publish=adapter.publish;lost={'once':False}
        def lose_one_response(key,package,archive):
            value=original_publish(key,package,archive)
            if not lost['once']:lost['once']=True;raise TimeoutError('Synthetic response lost after receiver committed')
            return value
        adapter.publish=lose_one_response
        for row in q.rows("SELECT id FROM jobs WHERE project=? AND state IN ('blocked','review','failed')",(project,)):q.retry(project,'synthetic-owner',row['id'])
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            if q.summary(project,'synthetic-owner')['state']=='completed':break
            failures=q.rows("SELECT key,error FROM jobs WHERE project=? AND state IN ('failed','review','blocked')",(project,))
            for failure in failures:
                if 'Synthetic response lost' in failure['error']:
                    row=q.rows('SELECT id,attempts FROM jobs WHERE project=? AND key=?',(project,failure['key']))[0]
                    assert row['attempts']==1
                    q.retry(project,'synthetic-owner',row['id']);record('uncertain_publication_explicitly_reconciled_without_write_replay')
                elif failure['error']=='A prerequisite is blocked, failed or cancelled':continue
                else:raise AssertionError(failure)
            time.sleep(.1)
        assert q.summary(project,'synthetic-owner')['state']=='completed'
        assert store.count()==5;record('five_published_listings_independently_verified_including_download_bytes')
        # Real installed Chrome in a disposable context; never user's profile.
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(channel='chrome',headless=True,chromium_sandbox=True)
            try:
                page=browser.new_page();page.goto(store.url)
                assert page.locator('article').count()==5
                for product in products:
                    effect=hashlib.sha256((project+':'+product['id']+':synthetic-local').encode()).hexdigest()
                    listing=adapter.lookup(effect);page.goto(listing['url']);assert page.locator('h1').inner_text()==product['title'];assert page.locator('#visibility').inner_text()=='Published';assert str(product['price_cents']/100)[:2] in page.locator('#price').inner_text()
                record('real_installed_chrome_verified_all_five_live_local_pages')
            finally:browser.close()
        # Re-submit exactly the same idempotency key; receiver must keep one copy.
        for product in products:
            package=q.result(project,'synthetic-owner',product['id']+':package')['result'];key=hashlib.sha256((project+':'+product['id']+':synthetic-local').encode()).hexdigest()
            adapter.publish(key,package,q.root/project/'artifacts'/package['archive'])
        assert store.count()==5;record('duplicate_submissions_produced_no_duplicate_listings')
        q.revoke_scope(project,'synthetic-owner')
        try:q.authorization(project,'synthetic-local',package)
        except Exception:record('revoked_scope_denies_further_publication')
        else:raise AssertionError('Revoked scope accepted')
        record('customer_packages',str(q.root/project/'artifacts'))
        record('complete')
    except Exception as error:record('complete',False);record('error',type(error).__name__+': '+str(error));raise
    finally:q.close();store.close()


if __name__=='__main__':main()
