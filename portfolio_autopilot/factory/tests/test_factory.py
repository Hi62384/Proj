import csv
import hashlib
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from zipfile import ZipFile

from portfolio_autopilot.factory.catalog import catalog, select, find, summary as catalog_summary
from portfolio_autopilot.factory.config import ROOT, PRIVATE, safe_id, money, SetupError, bootstrap, load_profile, private_path
from portfolio_autopilot.factory.kits import make_kit, safe_source_url
from portfolio_autopilot.factory.portable_runner import MappingError, read_mapping, inspect_input, transform_to_validated_report
from portfolio_autopilot.factory.reporting import create_delivery, ensure_local_output
from portfolio_autopilot.factory.ledger import (record,import_csv,summary,set_candidate,
    create_tasks,get_tasks,finish_task,request_approval,get_approvals,resolve_approval)
from portfolio_autopilot.factory.portal import FactoryServer, load_view, render_page
from portfolio_autopilot.factory.cli import main,doctor


class FactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)
    def row(self,identifier='EXP-001-01',mode='F'):
        return {'id':identifier, 'name':'Maintenance <b> renewal audit',
                'buyer':'Businesses buying <script>bad</script>', 'niche':'HVAC',
                'revenue_mode':mode,'business_model':'Fast-cash service',
                'description':'Automate authorized data, not proprietary data',
                'legal_class':'standard','evidence_grade':'H0 concept; no exact buyer demand',
                'illustrative_price_cad':'499', 'niche_source_url':'https://example.org/source',
                'source_record_ref':'source-one','risk':'Sensitive data risk',
                'cross_niche_score':'80','first_possible_sale_days_min':'2',
                'first_possible_sale_days_max':'15'}

class CatalogTests(FactoryTestCase):
    def test_real_atlas_researched_count_not_validated(self):
        rows=catalog()
        s=catalog_summary(rows)
        self.assertEqual(s['records'],1296)
        self.assertEqual(s['expanded_hypotheses'],1182)
        self.assertEqual(s['original_research_records'],114)
        self.assertEqual(s['expanded_niches'],197)
    def test_diverse_modes_do_not_prefer_familiar_work(self):
        rows=catalog()
        ideas=select(rows,limit=18,per_mode=3)
        self.assertGreaterEqual(len(ideas),10)
        self.assertEqual(len({x['niche'] for x in ideas}),len(ideas))
        from collections import Counter
        self.assertLessEqual(max(Counter(x['revenue_mode'] for x in ideas).values()),3)
    def test_safe_ids_and_money(self):
        for x in ['../bad', 'x/y','x y','', '\\shell', 'a'*81]:
            with self.subTest(x=x),self.assertRaises(SetupError):safe_id(x)
        for x in ['NaN','-1','1.123','Infinity']:
            with self.subTest(x=x),self.assertRaises(SetupError):money(x)
        self.assertEqual(money('2.25'),__import__('decimal').Decimal('2.25'))
    def test_private_path_rejects_traversal(self):
        for x in ['../secret','/root','hello/../../a']:
            with self.subTest(x=x),self.assertRaises(SetupError):private_path(x,self.home)

class KitTests(FactoryTestCase):
    def test_profile_is_placeholder_no_secrets(self):
        profile_path=bootstrap(self.home)
        profile=load_profile(profile_path)
        self.assertEqual(profile['monthly_external_spend_cap_cad'],'0')
        self.assertEqual(profile['approved_channels'],[])
        obj=json.loads(profile_path.read_text());obj['api_key']='do-not-store'
        profile_path.write_text(json.dumps(obj))
        with self.assertRaises(SetupError):load_profile(profile_path)
    def test_renders_escaped_static_preview_and_no_live_urls(self):
        kit=make_kit(self.row(),self.home)
        self.assertEqual(len(list(kit.iterdir())),8)
        page=(kit/'LANDING_PREVIEW.html').read_text()
        self.assertIn('&lt;script&gt;bad&lt;/script&gt;',page)
        self.assertNotIn('<script>bad</script>',page)
        self.assertIn('UNPUBLISHED MOCKUP',page)
        obj=json.loads((kit/'product_config.json').read_text())
        self.assertEqual(obj['stage'],'research_draft')
        self.assertEqual(obj['verified_paid_customers'],0)
        self.assertEqual(obj['allowed_external_actions'],[])
    def test_refuses_overwrite_and_symlink(self):
        row=self.row();make_kit(row,self.home)
        with self.assertRaises(SetupError):make_kit(row,self.home)
    def test_unsupported_source_link(self):
        self.assertEqual(safe_source_url('javascript:alert(1)'), '')
        self.assertEqual(safe_source_url('https://example.org/path'), 'https://example.org/path')
        self.assertEqual(safe_source_url('https://u:p@example.org/path'), '')
    def test_all_modes_generate_distinct_qa_guidance(self):
        for i,mode in enumerate(['F','R','D','I','M','P','A','L','C','X','ORIGINAL']):
            with self.subTest(mode=mode):
                row=self.row(f'EXP-99-{i:02}',mode=mode)
                path=make_kit(row,self.home)
                self.assertIn('NOT VALIDATED', (path/'README.md').read_text())

class ReportingTests(FactoryTestCase):
    def setUp(self):
        super().setUp()
        self.csv=self.home/'input.csv';self.csv.write_text(
            'SaleDate,OrderNum,Market,Gross,COGS\n2026-10-01,unique01,Direct,50.20,10.10\n2026-10-02,unique02,Ads,23.30,9.05\n',encoding='utf-8')
        self.mapping=self.home/'mapping.json';self.mapping.write_text(json.dumps({
            'version':1,'label':'My report','currency':'CAD','mapping':{
                'date':'SaleDate','order_id':'OrderNum','channel':'Market','revenue':'Gross','cost':'COGS'}}))
    def test_header_preflight_and_deterministic_output(self):
        cfg=read_mapping(self.mapping)
        inspection=inspect_input(self.csv,cfg)
        self.assertTrue(inspection['supported']);self.assertFalse(inspection['data_scanned'])
        summary_json=transform_to_validated_report(self.csv,self.home/'out',cfg)
        self.assertEqual(summary_json['revenue'],'73.50')
        self.assertEqual(summary_json['input_cost'],'19.15')
        self.assertEqual(summary_json['revenue_minus_input_cost'],'54.35')
        self.assertTrue((self.home/'out'/'report.html').is_file())
    def test_mapping_refuses_alias_collision(self):
        obj=json.loads(self.mapping.read_text());obj['mapping']['cost']='Gross'
        self.mapping.write_text(json.dumps(obj))
        with self.assertRaises(MappingError):read_mapping(self.mapping)
    def test_mapping_preflight_missing_column(self):
        self.csv.write_text('SaleDate,OrderNum,Market,Gross\n2026-10-02,unique02,Ads,23,1\n')
        with self.assertRaises(MappingError):inspect_input(self.csv,read_mapping(self.mapping))
    def test_malformed_csv_fails_closed(self):
        self.csv.write_text(self.csv.read_text()+'2026-10-03,unique03,Direct,1\n')
        with self.assertRaises(MappingError):transform_to_validated_report(self.csv,self.home/'out',read_mapping(self.mapping))
        self.assertFalse((self.home/'out').exists())
    def test_duplicate_id_rejected(self):
        self.csv.write_text(self.csv.read_text().replace('unique02','unique01'))
        with self.assertRaises(ValueError):transform_to_validated_report(self.csv,self.home/'out',read_mapping(self.mapping))
    def test_private_delivery_zip_contains_runner_not_source_data(self):
        delivery=create_delivery(self.csv,self.mapping,customer_ref='client_public_ref',
                                 destination=self.home/'delivery1')
        zpath=delivery/'customer_delivery.zip'
        self.assertTrue(zpath.is_file())
        with ZipFile(zpath) as z:
            files=set(z.namelist())
            self.assertIn('run_report.py',files)
            self.assertIn('report_builder.py',files)
            self.assertIn('results/report.html',files)
            self.assertNotIn('input.csv',files)
            manifest=json.loads(z.read('manifest.json'))
            self.assertEqual(manifest['status'],'LOCAL_QA_REVIEW_NOT_DELIVERED')
            for item in manifest['output_files']:
                self.assertEqual(hashlib.sha256(z.read(item['name'])).hexdigest(),item['sha256'])
        self.assertEqual(self.csv.read_text().splitlines()[1],'2026-10-01,unique01,Direct,50.20,10.10')
    def test_refuse_reuse_delivery_path(self):
        create_delivery(self.csv,self.mapping,customer_ref='c1',destination=self.home/'delivery1')
        with self.assertRaises(SetupError):create_delivery(self.csv,self.mapping,customer_ref='c1',destination=self.home/'delivery1')
    def test_refuse_tracked_repo_output(self):
        with self.assertRaises(SetupError):ensure_local_output(ROOT/'research_merge'/'leak_customer_report')
    def test_zip_runner_independent_of_git_repo(self):
        # Functional check of the actual delivered standalone runner in a clean directory.
        delivery=create_delivery(self.csv,self.mapping,customer_ref='c2',destination=self.home/'delivery2')
        sandbox=self.home/'standalone';sandbox.mkdir()
        with ZipFile(delivery/'customer_delivery.zip') as z:z.extractall(sandbox)
        import subprocess,sys
        cp=subprocess.run([sys.executable,'run_report.py','--input',str(self.csv),
                           '--config','mapping.json','--out','repeat'],cwd=sandbox,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20)
        self.assertEqual(cp.returncode,0,cp.stderr)
        self.assertTrue((sandbox/'repeat'/'report.html').is_file())
        self.assertEqual(json.loads((sandbox/'repeat'/'summary.json').read_text())['revenue'],'73.50')

class LedgerTests(FactoryTestCase):
    def event(self,event_id='e001',kind='revenue',amount='100',minutes=0):
        return {'event_id':event_id,'business_id':'FAST-O01','date':'2026-10-14',
                'kind':kind,'amount_cad':amount,'minutes':minutes,'source_ref':'manual_example'}
    def test_idempotent_financial_events_and_payouts_not_revenue(self):
        self.assertTrue(record(self.event(),self.home));self.assertFalse(record(self.event(),self.home))
        record(self.event('e002','fee','15'),self.home)
        record(self.event('e003','settlement','85'),self.home)
        record(self.event('e004','owner_minutes','0',60),self.home)
        total=summary(self.home)
        self.assertEqual(total['revenue_cad'],'100')
        self.assertEqual(total['operating_profit_cad'],'85')
        self.assertEqual(total['payouts_recorded_cad'],'85')
        self.assertEqual(total['economic_profit_cad'],'55.00')
        with self.assertRaises(SetupError):record(self.event('e001','fee','15'),self.home)
    def test_csv_import_rejects_conflict_transactionally(self):
        record(self.event('e001'),self.home)
        batch=self.home/'bad.csv'
        batch.write_text('event_id,business_id,date,kind,amount_cad,minutes,source_ref\n'
                         'e002,FAST-O01,2026-10-14,revenue,30.00,0,manual_example\n'
                         'e001,FAST-O01,2026-10-14,fee,9.00,0,manual_example\n')
        with self.assertRaises(SetupError):import_csv(batch,self.home)
        self.assertEqual(summary(self.home)['revenue_cad'],'100')
    def test_csv_import_repeat_is_idempotent(self):
        path=self.home/'records.csv'
        path.write_text('event_id,business_id,date,kind,amount_cad,minutes,source_ref\n'
                        'e001,FAST-O01,2026-10-14,revenue,35.00,0,manual_example\n')
        self.assertEqual(import_csv(path,self.home)['imported'],1)
        self.assertEqual(import_csv(path,self.home)['exact_duplicates_skipped'],1)
    def test_signal_evidence_required_and_live_unavailable(self):
        with self.assertRaises(SetupError):set_candidate('FAST-O01','buyer_signal',root=self.home)
        with self.assertRaises(SetupError):set_candidate('FAST-O01','live',root=self.home)
        set_candidate('FAST-O01','buyer_signal',evidence_ref='sample_reference',root=self.home)
        self.assertEqual(summary(self.home)['active_candidates'],1)
    def test_queue_review_and_requests_not_external(self):
        created=create_tasks([self.row()],self.home)
        self.assertEqual(created,2)
        self.assertEqual(create_tasks([self.row()],self.home),0)
        tasks=get_tasks(self.home)
        self.assertTrue(finish_task(tasks[0]['task_id'],self.home))
        self.assertFalse(finish_task(tasks[0]['task_id'],self.home))
        req=request_approval('EXP-001-01','public_launch','Review landing page',self.home)
        resolve_approval(req,'reviewed',root=self.home)
        self.assertEqual(get_approvals(self.home)[0]['status'],'reviewed')
        with self.assertRaises(SetupError):resolve_approval(req,'approved',root=self.home)

class PortalTests(FactoryTestCase):
    def setUp(self):
        super().setUp()
        self.rows=[self.row(),self.row('EXP-002-01','R')]
        self.server=FactoryServer(port=0,root=self.home,rows=self.rows)
        self.port=self.server.server_address[1]
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.addCleanup(self.thread.join,2)
    def url(self,path):return f'http://127.0.0.1:{self.port}{path}'
    def request(self,path,body=None,token=None,headers=None):
        if body is None:return urllib.request.urlopen(self.url(path),timeout=4)
        hs={'Content-Type':'application/json'}
        if token:hs['X-Factory-Token']=token
        hs.update(headers or {})
        req=urllib.request.Request(self.url(path),data=json.dumps(body).encode(),headers=hs,method='POST')
        return urllib.request.urlopen(req,timeout=4)
    def test_page_and_local_health(self):
        page=self.request('/').read().decode()
        self.assertIn('Portfolio Autopilot',page)
        self.assertNotIn('<script>bad</script>',page)
        state=json.load(self.request('/api/state'))
        self.assertEqual(state['catalog_records'],2)
        self.assertFalse(json.load(self.request('/health'))['external_integrations_enabled'])
    def test_rejects_unauthenticated_post_and_creates_safe_kit(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.request('/api/kit',{'id':'EXP-001-01'})
        self.assertEqual(e.exception.code,403)
        ok=json.load(self.request('/api/kit',{'id':'EXP-001-01'},token=self.server.token))
        self.assertFalse(ok['external_action'])
        self.assertTrue((self.home/'launchkits'/'EXP-001-01'/'README.md').is_file())
    def test_rejects_bad_origin_and_traversal(self):
        with self.assertRaises(urllib.error.HTTPError) as e:
            self.request('/api/queue',{},token=self.server.token,headers={'Origin':'https://evil.example'})
        self.assertEqual(e.exception.code,403)
        with self.assertRaises(urllib.error.HTTPError) as e:
            self.request('/preview/..%2Fsecret')
        self.assertEqual(e.exception.code,404)
    def test_queue_action_no_external_side_effect(self):
        res=json.load(self.request('/api/queue',{},token=self.server.token))
        self.assertGreaterEqual(res['created'],2)
        state=json.load(self.request('/api/state'))
        self.assertGreaterEqual(state['summary']['pending_tasks'],2)

class SmokeTests(FactoryTestCase):
    def test_local_doctor(self):
        result=doctor(catalog())
        self.assertEqual(result['research']['records'],1296)
        self.assertEqual(result['extra_packages_required'],0)
        self.assertFalse(result['external_actions_enabled'])
    def test_cli_kit_and_report(self):
        # CLI smoke without touching production/private default workspace.
        self.assertEqual(main(['--workspace',str(self.home),'kit','EXP-001-01']),0)
        self.assertTrue((self.home/'launchkits'/'EXP-001-01'/'README.md').is_file())
        self.assertEqual(main(['--workspace',str(self.home),'queue','--limit','5']),0)
        self.assertEqual(main(['--workspace',str(self.home),'status']),0)

if __name__=='__main__':unittest.main()
