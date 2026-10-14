from __future__ import annotations
import contextlib
import copy
import csv
import io
import json
from pathlib import Path
import re
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from opportunity_library.model import (ROOT, DATA, construct, factory_rows, query, validate, read_json,
    safe_csv, number, optional_range, weighted, WEIGHTS, SPEED_WEIGHTS)
from opportunity_library.build import render_outputs, csv_text, main as build_main
from opportunity_library.cli import main as cli_main
from portfolio_autopilot.factory import catalog as factory_module
from portfolio_autopilot.factory.portal import FactoryServer, load_view, render_page


class ResearchIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib=construct();cls.ids={r['id']:r for r in cls.lib['records']}
        cls.old=read_json(ROOT/'research_merge/opportunity_atlas_expanded.json')['opportunities']
        cls.outputs=render_outputs();cls.compat=factory_rows(cls.lib)

    def test_all_counts(self):
        self.assertEqual(self.lib['counts']['records'],1512)
        self.assertEqual(self.lib['counts']['legacy_records'],1296)
        self.assertEqual(self.lib['counts']['curated_records'],216)
        self.assertEqual(self.lib['counts']['business_offer_records'],1510)
        self.assertEqual(self.lib['counts']['capital_research_records'],2)

    def test_every_original_id_preserved(self):
        self.assertEqual({r['id'] for r in self.old},{x for x in self.ids if not x.startswith('CUR-')})

    def test_exactly_one_primary_home(self):
        self.assertEqual(len(self.ids),len(self.lib['records']))
        for r in self.ids.values():
            self.assertEqual(r['subcategory_id'].split('-')[0],r['category_id'])

    def test_all_categories_and_subcategories_populated(self):
        self.assertEqual(len({r['category_id'] for r in self.ids.values()}),36)
        self.assertEqual(len({r['subcategory_id'] for r in self.ids.values()}),144)

    def test_each_category_has_six_new_experiments(self):
        for c in self.lib['categories']:
            self.assertEqual(sum(r['id'].startswith('CUR-') and r['category_id']==c['id'] for r in self.ids.values()),6)

    def test_industry_axes_preserved(self):
        self.assertEqual(len({r['industry'] for r in self.ids.values() if r['id'].startswith('EXP-')}),197)
        self.assertEqual(self.ids['EXP-001-03']['category_id'],'C20')
        self.assertIn('C30',self.ids['EXP-001-03']['secondary_tags'])

    def test_no_false_sales_or_anonymity(self):
        for r in self.ids.values():
            self.assertFalse(r['paid_customers_verified']);self.assertFalse(r['privacy']['guaranteed_anonymity'])
            self.assertEqual(r['phase'],'unvalidated concept')
            self.assertEqual(r['privacy']['seller_specific_disclosure_review'],'not completed')

    def test_profit_unknown_not_zero(self):
        for r in self.ids.values():self.assertIsNone(r['economics']['expected_monthly_profit'])

    def test_capital_never_ranked(self):
        for r in self.ids.values():
            if r['mode']=='CAPITAL':
                self.assertEqual(r['income_type'],'personal_capital')
                self.assertIsNone(r['score_low_touch']);self.assertIsNone(r['score_fast_cash'])
                self.assertIsNone(r['economics']['capital_return_forecast'])
                self.assertIsNone(r['economics']['asking_price_hypothesis'])

    def test_capital_excluded_by_default(self):
        self.assertEqual(len(query(self.lib)),1510)
        self.assertEqual(len(query(self.lib,include_capital=True)),1512)

    def test_original_risk_not_downgraded(self):
        for old in self.old:
            if old['legal_class']=='regulated':self.assertNotEqual(self.ids[old['id']]['risk'],'standard')

    def test_sensitive_new_categories_flagged(self):
        for r in self.ids.values():
            if r['id'].startswith('CUR-') and r['category_id'] in ('C26','C27','C28','C33'):
                self.assertEqual(r['risk'],'regulated')

    def test_human_work_in_every_record(self):
        for r in self.ids.values():
            self.assertGreater(len(r['automation']['human_work']),20)
            self.assertTrue(r['gate']);self.assertTrue(r['stop_rule']);self.assertTrue(r['first_experiment'])

    def test_separate_fulfillment_and_passivity(self):
        r=self.ids['CUR-09-01']
        self.assertGreater(r['ratings']['fulfillment'],r['ratings']['passivity'])
        self.assertFalse(r['automation']['actual_automation_measured'])

    def test_unknown_legacy_workload_retained(self):
        self.assertIsNone(self.ids['REPO-O01']['economics']['weekly_total_hours_hypothesis'])

    def test_current_source_register(self):
        self.assertEqual(len(self.lib['sources']),69)
        for s in self.lib['sources']:
            self.assertFalse(s['supports_exact_offer_demand'])
            self.assertEqual(s['checked_on'],'2026-10-14')
            self.assertEqual(urlparse(s['url']).scheme,'https')
            self.assertTrue(s['limits']);self.assertTrue(s['retrieval'])

    def test_source_and_related_refs_resolve(self):
        validate(self.lib)
        for r in self.ids.values():
            for x in r['related_to']:self.assertIn(x,self.ids)

    def test_original_fields_unchanged_in_compatibility_object(self):
        byid={r['id']:r for r in self.compat}
        for old in self.old:
            for key,value in old.items():self.assertEqual(byid[old['id']][key],value,(old['id'],key))

    def test_factory_capital_is_blocked(self):
        for r in self.compat:
            if r['library_income_type']=='personal_capital':self.assertEqual(r['legal_class'],'regulated')
        chosen=factory_module.select(self.compat,limit=300,per_mode=300)
        self.assertFalse(any(r['library_income_type']=='personal_capital' for r in chosen))

    def test_default_factory_sees_new_index(self):
        s=factory_module.summary(factory_module.catalog())
        self.assertEqual(s['records'],1512);self.assertEqual(s['original_research_records'],114)
        self.assertEqual(s['curated_library_hypotheses'],216);self.assertEqual(s['library_categories'],36)

    def test_explicit_legacy_source_still_supported(self):
        self.assertEqual(len(factory_module.catalog(ROOT/'research_merge/opportunity_atlas_expanded.csv')),1296)

    def test_missing_optional_library_falls_back(self):
        with patch.object(factory_module,'LIBRARY_ATLAS',Path('/not/a/real/library.csv')):
            self.assertEqual(len(factory_module.catalog()),1296)

    def test_both_ranking_weights_total_100(self):
        self.assertEqual(sum(WEIGHTS.values()),100);self.assertEqual(sum(SPEED_WEIGHTS.values()),100)
        for r in self.ids.values():
            self.assertEqual(r['score_low_touch'],weighted(r['ratings'],WEIGHTS))
            self.assertEqual(r['score_fast_cash'],weighted(r['ratings'],SPEED_WEIGHTS))

    def test_query_filters(self):
        rs=query(self.lib,category='C09',mode='D',min_privacy=4,min_passivity=4,include_review=False,limit=4)
        self.assertTrue(rs)
        for r in rs:self.assertEqual(r['category_id'],'C09');self.assertEqual(r['mode'],'D');self.assertEqual(r['risk'],'standard')
        self.assertEqual(query(self.lib,text='NO_MATCH_489274'),[])

    def test_query_id_and_buyer(self):
        self.assertEqual(query(self.lib,text='CUR-01-01')[0]['id'],'CUR-01-01')
        self.assertTrue(query(self.lib,text='contractors'))

    def test_bad_query_arguments(self):
        with self.assertRaises(ValueError):query(self.lib,lens='money_guaranteed')
        with self.assertRaises(ValueError):query(self.lib,limit=0)

    def test_csv_formula_injection_protection(self):
        for text in ['=cmd','+cmd',' -cmd','@SUM(1)','\tfoo','\rbar']:
            self.assertTrue(safe_csv(text).startswith("'"))
        self.assertEqual(safe_csv(-30),'-30');self.assertEqual(safe_csv('normal'),'normal')

    def test_invalid_numbers_remain_unknown(self):
        for x in ['',None,'oops','NaN','Infinity']:self.assertIsNone(number(x))
        self.assertEqual(number('25'),25)
        self.assertIsNone(optional_range('',10))
        with self.assertRaises(ValueError):safe_csv(float('inf'))

    def test_csv_quotes_and_roundtrip(self):
        text=csv_text([{'x':'a,"b"\nc','y':-2.5}])
        data=list(csv.DictReader(io.StringIO(text.lstrip('\ufeff'))))
        self.assertEqual(data,[{'x':'a,"b"\nc','y':'-2.5'}])

    def test_generated_html_is_self_contained(self):
        html=self.outputs['Opportunity_Library.html'].decode()
        self.assertNotIn('__LIBRARY_JSON__',html)
        payload=re.search(r'<script id="library-data" type="application/json">(.*?)</script>',html,re.S).group(1)
        self.assertEqual(json.loads(payload)['counts']['records'],1512)
        self.assertNotIn('<',payload)
        self.assertNotRegex(html,r'<(?:script|link)[^>]+(?:src|href)="https?://')
        self.assertIn("connect-src 'none'",html)

    def test_all_generated_paths_stay_scoped(self):
        for name in self.outputs:
            self.assertFalse(Path(name).is_absolute());self.assertNotIn('..',Path(name).parts)
            self.assertTrue(name=='Opportunity_Library.html' or name.startswith('opportunity_library/'))

    def test_no_public_credentials_in_sources(self):
        for rel,body in self.outputs.items():
            self.assertNotIn(b'JamesBennett10000',body)
            self.assertNotRegex(body,rb'sk_live_[A-Za-z0-9]+')

    def test_category_document_count(self):
        self.assertEqual(sum(p.startswith('opportunity_library/categories/') for p in self.outputs),36)

    def test_all_category_record_memberships(self):
        for r in self.ids.values():
            path='opportunity_library/categories/'+r['category_slug']+'/README.md'
            self.assertIn(r['id'].encode(),self.outputs[path])

    def test_rebuild_check_is_clean(self):
        with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(build_main(['--check']),0)

    def test_deterministic_generated_bytes(self):
        self.assertEqual(self.outputs,render_outputs())

    def test_validation_rejects_duplicate_id(self):
        x=dict(self.lib);x['records']=self.lib['records']+[self.lib['records'][0]]
        with self.assertRaises(ValueError):validate(x)

    def test_unsafe_source_url_rejected(self):
        x=dict(self.lib);x['sources']=[dict(s) for s in self.lib['sources']]
        x['sources'][0]['url']='javascript:alert(1)'
        with self.assertRaises(ValueError):validate(x)

    def test_category_path_traversal_rejected(self):
        x=dict(self.lib);x['categories']=[dict(c) for c in self.lib['categories']]
        x['categories'][0]['slug']='../../VaultDesk'
        with self.assertRaises(ValueError):validate(x)

    def test_duplicate_source_id_rejected(self):
        x=dict(self.lib);x['sources']=self.lib['sources']+[self.lib['sources'][0]]
        with self.assertRaises(ValueError):validate(x)

    def test_shared_filter_does_not_copy_local_identity_path(self):
        html=self.outputs['Opportunity_Library.html'].decode()
        self.assertIn("clipboard.writeText(fragment)",html)
        self.assertNotIn("location.href.split",html)

    def test_cli_show_and_search(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli_main(['show','CUR-01-01']),0)
        self.assertEqual(json.loads(out.getvalue())['id'],'CUR-01-01')
        with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(cli_main(['search','--category','C02','--limit','3']),0)

    def test_cli_invalid_id_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):self.assertEqual(cli_main(['show','BAD']),2)


class LocalIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.server=FactoryServer(root=Path(cls.tmp.name))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.tmp.cleanup()
    def test_library_route_and_headers(self):
        with urlopen(self.url+'/opportunity-library') as r:
            self.assertEqual(r.status,200);self.assertIn('text/html',r.headers['Content-Type'])
            self.assertEqual(r.headers['Referrer-Policy'],'no-referrer')
            self.assertIn(b'Opportunity Library',r.read())
    def test_public_docs_route(self):
        with urlopen(self.url+'/opportunity_library/docs/METHODOLOGY.md') as r:self.assertEqual(r.status,200)
    def test_private_and_traversal_routes_blocked(self):
        for path in ['/opportunity_library/../VaultDesk/app.py','/opportunity_library/data/../../portfolio_autopilot/.local/seller_profile.json','/opportunity_library/data/classifications.json','/VaultDesk/app.py']:
            with self.subTest(path=path),self.assertRaises(HTTPError) as e:urlopen(self.url+path)
            self.assertEqual(e.exception.code,404)
    def test_wrong_host_rejected(self):
        with self.assertRaises(HTTPError) as e:urlopen(Request(self.url+'/opportunity-library',headers={'Host':'evil.example'}))
        self.assertEqual(e.exception.code,403)
    def test_workbench_has_category_and_library_link(self):
        with urlopen(self.url+'/') as r:
            text=r.read().decode();self.assertIn('category-filter',text);self.assertIn('/opportunity-library',text)
            self.assertNotIn('Entire 1,296-record atlas',text)
    def test_review_state_includes_facets_and_all_records(self):
        with urlopen(self.url+'/api/state') as r:data=json.load(r)
        self.assertEqual(data['catalog_records'],1512)
        self.assertEqual(len({r['category_id'] for r in data['all_offers']}),36)

if __name__=='__main__':unittest.main()
