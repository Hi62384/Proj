import json
from pathlib import Path
import tempfile
import unittest
import urllib.error
import urllib.request
import threading
from zipfile import ZipFile

from portfolio_autopilot.factory.catalog import catalog
from portfolio_autopilot.factory.config import ROOT, SetupError
from portfolio_autopilot.factory.first_business import first_business, FILES
from portfolio_autopilot.factory.storefront import create_preview
from portfolio_autopilot.factory.kits import make_kit
from portfolio_autopilot.factory.portal import FactoryServer
from portfolio_autopilot.factory.cli import main

class LaunchWorkflowTests(unittest.TestCase):
    def setUp(self):
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.work=Path(td.name)
    def test_first_business_complete_no_sales_claims(self):
        p=first_business(self.work)
        self.assertEqual(set(x.name for x in p.iterdir()),set(FILES)|{'STATUS.json','SYNTHETIC_REPORT_DEMONSTRATION.zip'})
        for name in FILES:
            content=(p/name).read_text()
            self.assertNotIn("\n          '",content)
            self.assertGreater(len(content),100)
        with ZipFile(p/'SYNTHETIC_REPORT_DEMONSTRATION.zip') as z:
            self.assertIn('results/report.html',z.namelist())
            self.assertIn('run_report.py',z.namelist())
        status=json.loads((p/'STATUS.json').read_text())
        self.assertEqual(status['real_sales_count'],0)
        self.assertFalse(status['stripe_connected'])
        with self.assertRaises(SetupError):first_business(self.work)
    def test_offline_catalogue_cards_are_escaped_and_not_buys(self):
        row={'id':'EXP-001-01','name':'Unsafe <script>pay</script>','niche':'Wholesale',
             'buyer':'Small retailers','revenue_mode':'D',
             'description':'Original template', 'legal_class':'standard',
             'illustrative_price_cad':'39','evidence_grade':'H0'}
        make_kit(row,self.work)
        html=create_preview(self.work).read_text()
        self.assertIn('&lt;script&gt;pay&lt;/script&gt;',html)
        self.assertNotIn('<script>pay</script>',html)
        self.assertIn('NO CHECKOUT',html)
        self.assertEqual(html.count('<article>'),1)
    def test_cli_batch_runs_variety_and_preview(self):
        status=main(['--workspace',str(self.work),'batch','--limit','4','--per-mode','4','--modes','D'])
        self.assertEqual(status,0)
        self.assertEqual(len(list((self.work/'launchkits').glob('*/README.md'))),4)
        self.assertEqual(main(['--workspace',str(self.work),'storefront-preview']),0)
        self.assertTrue((self.work/'previews'/'catalogue.html').is_file())
    def test_cli_first_business_in_one_command(self):
        self.assertEqual(main(['--workspace',str(self.work),'first-business']),0)
        self.assertTrue((self.work/'first_reporting_business'/'02_PROJECT_CATALOG_DRAFT.md').exists())
    def test_factory_refuses_writes_to_tracked_paths(self):
        self.assertEqual(main(['--workspace','portfolio_autopilot/factory','init']),2)

class LocalPortalLaunchTests(unittest.TestCase):
    def setUp(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup)
        self.root=Path(td.name)
        rows=[{'id':'FAST-O01','name':'Recurring report sprint','buyer':'Small agencies',
               'niche':'Service','revenue_mode':'ORIGINAL','legal_class':'refer to original',
               'cross_niche_score':'76','first_possible_sale_days_min':'2',
               'description':'One report from CSV'}]
        self.server=FactoryServer(port=0,root=self.root,rows=rows)
        self.port=self.server.server_address[1]
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.addCleanup(self.thread.join,2)
    def post(self,path,body,token=None):
        data=json.dumps(body).encode()
        headers={'Content-Type':'application/json'}
        if token:headers['X-Factory-Token']=token
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}{path}',data=data,headers=headers,method='POST')
        return urllib.request.urlopen(req,timeout=4)
    def test_first_business_ui_requires_csrf_and_generates_only_local_docs(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.post('/api/first-business',{})
        self.assertEqual(ctx.exception.code,403)
        data=json.load(self.post('/api/first-business',{},token=self.server.token))
        self.assertFalse(data['external_action'])
        self.assertTrue((self.root/'first_reporting_business'/'STATUS.json').is_file())
    def test_existing_research_can_be_drafted_without_publishing(self):
        r=json.load(self.post('/api/kit',{'id':'FAST-O01'},token=self.server.token))
        self.assertFalse(r['external_action'])
        self.assertEqual(json.loads((self.root/'launchkits'/'FAST-O01'/'product_config.json').read_text())['stage'],'research_draft')

if __name__=='__main__':unittest.main()

# Kept separate so regression tests also cover the locally accessible sample.
class LocalLinksTests(unittest.TestCase):
    def test_synthetic_download_and_draft_links(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            rows=[{'id':'EXP-001-01','name':'Test','niche':'HVAC','buyer':'Service companies',
                   'revenue_mode':'F','legal_class':'standard','cross_niche_score':'80'}]
            server=FactoryServer(port=0,root=root,rows=rows)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                first_business(root)
                make_kit({**rows[0],'description':'A genuine example','illustrative_price_cad':'299'},root)
                create_preview(root)
                addr=f'http://127.0.0.1:{server.server_address[1]}'
                for end in ('/first-offer','/demo-report','/first-file/00_START_HERE.md', '/catalogue-preview'):
                    with self.subTest(end=end):
                        self.assertEqual(urllib.request.urlopen(addr+end,timeout=4).status,200)
                with urllib.request.urlopen(addr+'/download-synthetic',timeout=4) as response:
                    self.assertEqual(response.headers.get('Content-Type'),'application/zip')
                    self.assertEqual(response.read(2),b'PK')
            finally:
                server.shutdown();server.server_close();thread.join(2)
