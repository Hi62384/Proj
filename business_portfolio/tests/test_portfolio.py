"""Offline package regression tests; these do not test real customer automations."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('portfolio_builder',ROOT/'tools/build_browser.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=b.load_portfolio(ROOT)
        cls.base=next(r for r in cls.data['records'] if r['id']=='AWA-001')

    def fixture(self, depth=1):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);r=Path(td.name)
        (r/'research').mkdir()
        (r/'research/SOURCE_REGISTER.json').write_text(json.dumps(self.data['sources']))
        parent=None;parts=[]
        for i in range(depth):
            parts.append('d'+str(i));p='/'.join(parts);folder=r/'niches'/p;folder.mkdir(parents=True)
            (folder/'NICHE.json').write_text(json.dumps(dict(id=f'N-test-{i}',title=f'Depth {i}',parent=parent,path=p)))
            parent=f'N-test-{i}'
        m={k:v for k,v in self.base.items() if k not in {'body','path','content_sha256'}}
        m.update(niche_path='/'.join(parts),niche_id=parent,parent_project=None,related_projects=[])
        dest=r/'niches'/m['niche_path']/'projects'/'awa-001-test.md';dest.parent.mkdir()
        self.write(dest,m)
        return r,dest,m
    @staticmethod
    def write(p,m,body='# Test\n\n## Resume checkpoint\nNext step recorded; no external effects.'):
        p.write_text('---\n'+json.dumps(m)+'\n---\n'+body+'\n')

    def test_snapshot_preserves_all_awa_ids(self):
        ids={x['id'] for x in self.data['records']}
        self.assertTrue({f'AWA-{i:03d}' for i in range(1,121)}<=ids)
    def test_existing_progress_records_present(self):
        ids={x['id'] for x in self.data['records']}
        self.assertTrue({f'EX-{i:03d}' for i in range(1,13)}|{'SYS-001'}<=ids)
    def test_candidate_validation_not_invented(self):
        for r in self.data['records']:
            if r['origin']=='revised_candidate':
                self.assertEqual(r['commercial_validation'],'unvalidated')
                self.assertFalse(r['execution_authorized'])
                self.assertIsNone(r['actual_revenue'])
    def test_existing_revenue_unknown(self):
        for r in self.data['records']:
            if r['origin']=='existing_work':self.assertIsNone(r['actual_revenue'])
    def test_published_not_commercially_validated(self):
        for id in ['EX-001','EX-002']:
            r=next(r for r in self.data['records'] if r['id']==id)
            self.assertEqual(r['work_state'],'published_reported')
            self.assertEqual(r['commercial_validation'],'published_unvalidated')
    def test_migration_coverage(self):
        x=json.loads((ROOT/'research/MIGRATION_CROSSWALK.json').read_text())
        self.assertEqual({r['id'] for r in x},{f'AWA-{i:03d}' for i in range(1,121)})
        for r in x:self.assertTrue((ROOT/r['new_path']).is_file())
    def test_unique_scope_acceptance(self):
        cases=[]
        for r in self.data['records']:
            if r['origin']=='revised_candidate':
                case=r['body'].split('**Distinct failure test:** ',1)[1].split('\n',1)[0];cases.append(case)
        self.assertEqual(len(cases),len(set(cases)))
    def test_paths_fit_reported_windows_checkout(self):
        prefix='C:\\Users\\User1\\Documents\\Downloads\\Proj\\business_portfolio\\'
        for r in self.data['records']:self.assertLess(len(prefix+r['path']),240)
    def test_parser_crlf(self):
        text='---\r\n{"id":"X-001"}\r\n---\r\n# Title\r\n'
        m,body=b.parse_project(text);self.assertEqual(m['id'],'X-001');self.assertEqual(body,'# Title')
    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(b.ValidationError):b.parse_project('---\n{"id":1,"id":2}\n---\nbody')
    def test_nan_rejected(self):
        with self.assertRaises(b.ValidationError):b.loads('{"value":NaN}')
    def test_missing_frontmatter_rejected(self):
        with self.assertRaises(b.ValidationError):b.parse_project('# not a record')
    def test_deep_niche_supported(self):
        root,p,m=self.fixture(24);d=b.load_portfolio(root)
        self.assertEqual(len(d['niches']),24);self.assertEqual(d['records'][0]['niche_id'],'N-test-23')
    def test_duplicate_project_rejected(self):
        root,p,m=self.fixture();(p.parent/'duplicate.md').write_text(p.read_text())
        with self.assertRaisesRegex(b.ValidationError,'Duplicate project'):b.load_portfolio(root)
    def test_missing_source_rejected(self):
        root,p,m=self.fixture();m['source_ids']=['MISSING'];self.write(p,m)
        with self.assertRaises(b.ValidationError):b.load_portfolio(root)
    def test_invalid_status_rejected(self):
        root,p,m=self.fixture();m['work_state']='made_money_automatically';self.write(p,m)
        with self.assertRaises(b.ValidationError):b.load_portfolio(root)
    def test_paid_validation_requires_evidence_reference(self):
        root,p,m=self.fixture();m['commercial_validation']='paid_pilot';self.write(p,m)
        with self.assertRaisesRegex(b.ValidationError,'evidence reference'):b.load_portfolio(root)
    def test_parent_project_cycle_rejected(self):
        root,p,m=self.fixture();m['parent_project']=m['id'];self.write(p,m)
        with self.assertRaisesRegex(b.ValidationError,'cycle'):b.load_portfolio(root)
    def test_missing_parent_project_rejected(self):
        root,p,m=self.fixture();m['parent_project']='UNKNOWN-001';self.write(p,m)
        with self.assertRaises(b.ValidationError):b.load_portfolio(root)
    def test_unknown_related_project_rejected(self):
        root,p,m=self.fixture();m['related_projects']=['UNKNOWN-001'];self.write(p,m)
        with self.assertRaises(b.ValidationError):b.load_portfolio(root)
    def test_niche_id_path_mismatch_rejected(self):
        root,p,m=self.fixture();m['niche_id']='N-missing';self.write(p,m)
        with self.assertRaises(b.ValidationError):b.load_portfolio(root)
    def test_niche_parent_mismatch_rejected(self):
        root,p,m=self.fixture(2);q=p.parent.parent/'NICHE.json';n=json.loads(q.read_text());n['parent']=None;q.write_text(json.dumps(n))
        with self.assertRaises(b.ValidationError):b.load_portfolio(root)
    def test_traversal_rejected(self):
        for s in ['../evil','good/../../evil','a\\b','a/projects/b','a//b']:
            self.assertFalse(b.safe_niche(s))
    def test_windows_reserved_niche_names_rejected(self):
        for name in ['con','prn','aux','nul','com1','com9','lpt1','lpt9']:
            self.assertFalse(b.safe_niche(name))
            self.assertFalse(b.safe_niche('safe/'+name+'/child'))
        self.assertTrue(b.safe_niche('console/com10/lpt-notes'))
    def test_private_directory_excluded(self):
        root,p,m=self.fixture();q=root/'niches'/'.local'/'projects';q.mkdir(parents=True);(q/'bad.md').write_text('not metadata')
        self.assertEqual(len(b.load_portfolio(root)['records']),1)
    def test_symlink_rejected(self):
        root,p,m=self.fixture();q=p.parent/'alias.md'
        try:q.symlink_to(p)
        except OSError:self.skipTest('symlinks unavailable on this platform')
        with self.assertRaises(b.ValidationError):b.load_portfolio(root)
    def test_script_terminator_escaped(self):
        s=b.embedded_json({'payload':'</script><script>window.pwned=true</script> & \u2028'})
        self.assertNotIn('<',s);self.assertNotIn('>',s);self.assertEqual(json.loads(s)['payload'],'</script><script>window.pwned=true</script> & \u2028')
    def test_builder_does_not_write_canonical_records(self):
        before={p:p.read_bytes() for p in (ROOT/'niches').rglob('*.md')}
        b.load_portfolio(ROOT)
        self.assertTrue(all(p.read_bytes()==v for p,v in before.items()))
    def test_stale_check_detects_changes(self):
        root,p,m=self.fixture();(root/'tools').mkdir();(root/'tools/browser_template.html').write_text('<script type="application/json">/*__PORTFOLIO_DATA__*/</script>')
        b.build(root);b.build(root,True);m['next_action']='Changed next step';self.write(p,m)
        with self.assertRaisesRegex(b.ValidationError,'stale'):b.build(root,True)
    def test_fixture_results_not_fabricated(self):
        d=json.loads((ROOT/'fixtures/awa-001-cases.json').read_text());self.assertTrue(all(x['result']=='not_run' for x in d['cases']))
    def test_economics_arithmetic(self):
        net=250*(1-.15)-15
        self.assertEqual(net,197.5);self.assertAlmostEqual(net/8,24.6875)
        self.assertAlmostEqual((30*8+15)/(1-.15),300)
    def test_browser_source_safe_rendering(self):
        s=(ROOT/'tools/browser_template.html').read_text(encoding='utf-8')
        self.assertNotIn('.innerHTML',s);self.assertNotIn('XMLHttpRequest',s)
        self.assertIn("connect-src 'self'",s)

if __name__=='__main__':unittest.main()
