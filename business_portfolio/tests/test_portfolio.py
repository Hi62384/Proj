"""Offline package regression tests; these do not test real customer automations."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('portfolio_builder',ROOT/'tools/build_browser.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=b.load_portfolio(ROOT)
        cls.base=next(r for r in cls.data['archived_records'] if r['id']=='AWA-001')

    def fixture(self, depth=1):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);r=Path(td.name)
        (r/'research').mkdir()
        (r/'research/SOURCE_REGISTER.json').write_text(json.dumps(self.data['sources']))
        parent=None;parts=[]
        for i in range(depth):
            parts.append('d'+str(i));p='/'.join(parts);folder=r/'niches'/p;folder.mkdir(parents=True)
            (folder/'NICHE.json').write_text(json.dumps(dict(id=f'N-test-{i}',title=f'Depth {i}',parent=parent,path=p,priority=i+1,working=False)))
            parent=f'N-test-{i}'
        m={k:v for k,v in self.base.items() if k not in {'body','path','content_sha256','archived','previous_path'}}
        m.update(niche_path='/'.join(parts),niche_id=parent,parent_project=None,related_projects=[])
        dest=r/'niches'/m['niche_path']/'projects'/'awa-001-test.md';dest.parent.mkdir()
        self.write(dest,m)
        return r,dest,m
    @staticmethod
    def write(p,m,body='# Test\n\n## Resume checkpoint\nNext step recorded; no external effects.'):
        p.write_text('---\n'+json.dumps(m)+'\n---\n'+body+'\n')

    def test_snapshot_preserves_all_awa_ids(self):
        ids={x['id'] for x in self.data['archived_records']}
        self.assertTrue({f'AWA-{i:03d}' for i in range(1,121)}<=ids)
    def test_immutable_taxonomy_and_archived_snapshots_remain_intact(self):
        taxonomy=json.loads((ROOT.parent/'opportunity_library/data/taxonomy.json').read_text(encoding='utf-8'))
        self.assertEqual(len(taxonomy['categories']),36)
        self.assertEqual(sum(len(c['subcategories']) for c in taxonomy['categories']),144)
        self.assertEqual(len(self.data['archived_records']),139)
        self.assertEqual(self.data['taxonomy_snapshot'],{'files':185,'projects':3})

    def assert_current_catalogue_matches_files(self, root, data):
        # The live catalogue is owner-editable. Validate identity and structure
        # against the current files rather than freezing the original inventory.
        files=list(b.walk_index_inputs(root/'niches'))
        expected_nodes={p.parent.relative_to(root/'niches').as_posix():
                        json.loads(p.read_text(encoding='utf-8'))
                        for p in files if p.name=='NICHE.json'}
        nodes={n['path']:n for n in data['niches']}
        self.assertEqual(nodes,expected_nodes)
        self.assertEqual(len(nodes),len(data['niches']))
        self.assertEqual(len({n['id'] for n in nodes.values()}),len(nodes))
        for path,node in nodes.items():
            with self.subTest(niche=path):
                self.assertRegex(node['id'],r'^N-[a-zA-Z0-9_-]+$')
                self.assertIsInstance(node['working'],bool)
                self.assertIsInstance(node['title'],str)
                if '/' in path:
                    parent_path=path.rsplit('/',1)[0]
                    self.assertIn(parent_path,nodes)
                    self.assertEqual(node['parent'],nodes[parent_path]['id'])
                else:
                    self.assertIsNone(node['parent'])
        expected_records={p.relative_to(root).as_posix():p for p in files if b.project_record_path(p)}
        records={r['path']:r for r in data['records']}
        self.assertEqual(set(records),set(expected_records))
        self.assertEqual(len(records),len(data['records']))
        self.assertEqual(len({r['id'] for r in records.values()}),len(records))
        for path,record in records.items():
            with self.subTest(project=record['id']):
                raw=expected_records[path].read_bytes()
                metadata,body=b.parse_project(raw.decode('utf-8'),path)
                for key,value in metadata.items():
                    self.assertEqual(record[key],value,key)
                self.assertEqual(record['body'],body)
                self.assertEqual(record['content_sha256'],hashlib.sha256(raw).hexdigest())
                self.assertRegex(record['id'],r'^[A-Z][A-Z0-9_-]*-[0-9]{3,}$')
                actual_niche=b.project_niche_folder(expected_records[path]).relative_to(root/'niches').as_posix()
                self.assertEqual(record['niche_path'],actual_niche)
                self.assertEqual(record['niche_id'],nodes[actual_niche]['id'])
                self.assertIn(record.get('project_phase','working_phase_2'),
                              {f'working_phase_{i}' for i in range(1,7)}|{'complete'})
                self.assertIn(record['work_state'],b.WORK_STATES)
                self.assertIn(record['commercial_validation'],b.VALIDATIONS)
                self.assertIsInstance(record['execution_authorized'],bool)
                if record['commercial_validation'] in {'paid_pilot','repeat_paid','commercially_validated'}:
                    self.assertTrue(record.get('validation_evidence_ref'))
                for field in ('platforms_supported','platforms_proposed'):
                    if field in record:
                        self.assertIsInstance(record[field],list)
                        self.assertTrue(all(isinstance(value,str) and value.strip() for value in record[field]))

    def test_current_niches_and_projects_match_canonical_identity_and_structure(self):
        self.assert_current_catalogue_matches_files(ROOT,self.data)

    def test_current_catalogue_checks_allow_niche_edits_and_project_progress(self):
        root,original,meta=self.fixture()
        parent=root/'niches'/meta['niche_path']
        child=parent/'new-owner-niche'
        child.mkdir()
        (child/'NICHE.json').write_text(json.dumps(dict(
            id='N-owner-created',title='Owner-created subniche',parent=meta['niche_id'],
            path=meta['niche_path']+'/new-owner-niche',priority=11,working=False)))
        project=child/'new-001-product'/'project.md'
        project.parent.mkdir()
        (project.parent/'work').mkdir()
        updated={**meta,'id':'NEW-001','title':'A researched fictional product',
                 'niche_id':'N-owner-created','niche_path':meta['niche_path']+'/new-owner-niche',
                 'workflow_version':2,'project_phase':'working_phase_4',
                 'work_state':'package_ready','platforms_supported':['Fictional Engine'],
                 'platforms_proposed':['Fictional Engine','Another fictional platform']}
        self.write(project,updated)
        data=b.load_portfolio(root)
        self.assert_current_catalogue_matches_files(root,data)
        self.assertEqual({r['id'] for r in data['records']},{meta['id'],'NEW-001'})
        # Authorized removal changes inventory without weakening the checks on
        # the remaining project or the immutable historical snapshots.
        project.unlink();(project.parent/'work').rmdir();project.parent.rmdir()
        (child/'NICHE.json').unlink();child.rmdir()
        data=b.load_portfolio(root)
        self.assert_current_catalogue_matches_files(root,data)
        self.assertEqual([r['id'] for r in data['records']],[meta['id']])
    def test_taxonomy_snapshot_tampering_rejected(self):
        target=ROOT/'archive/2026-11-15-taxonomy-view-v1/niches/games-and-interactive-entertainment/game-development-marketplaces/projects/gdm-001-historical-save-regression-lab.md'
        original=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:original(p)+b'altered' if p==target else original(p)):
            with self.assertRaisesRegex(b.ValidationError,'Taxonomy snapshot file manifest mismatch'):
                b.load_portfolio(ROOT)
    def test_archive_integrity_guard(self):
        target=ROOT/'archive/2026-11-15-legacy/niches/ai-workflow-automation/agency/white-label/builds/projects/awa-001-inbound-form-to-crm-starter.md'
        original=Path.read_bytes
        def changed(path):
            raw=original(path)
            return raw+b'altered' if path==target else raw
        with patch.object(Path,'read_bytes',changed):
            with self.assertRaisesRegex(b.ValidationError,'manifest mismatch'):
                b.load_portfolio(ROOT)
    def test_existing_progress_records_present(self):
        ids={x['id'] for x in self.data['archived_records']}
        self.assertTrue({f'EX-{i:03d}' for i in range(1,13)}|{'SYS-001'}<=ids)
    def test_candidate_validation_not_invented(self):
        for r in self.data['archived_records']:
            if r['origin']=='revised_candidate':
                self.assertEqual(r['commercial_validation'],'unvalidated')
                self.assertFalse(r['execution_authorized'])
                self.assertIsNone(r['actual_revenue'])
    def test_existing_revenue_unknown(self):
        for r in self.data['archived_records']:
            if r['origin']=='existing_work':self.assertIsNone(r['actual_revenue'])
    def test_published_not_commercially_validated(self):
        for id in ['EX-001','EX-002']:
            r=next(r for r in self.data['archived_records'] if r['id']==id)
            self.assertEqual(r['work_state'],'published_reported')
            self.assertEqual(r['commercial_validation'],'published_unvalidated')
    def test_migration_coverage(self):
        x=json.loads((ROOT/'research/MIGRATION_CROSSWALK.json').read_text())
        self.assertEqual({r['id'] for r in x},{f'AWA-{i:03d}' for i in range(1,121)})
        for r in x:self.assertTrue((ROOT/'archive/2026-11-15-legacy'/r['new_path']).is_file())
    def test_unique_scope_acceptance(self):
        cases=[]
        for r in self.data['archived_records']:
            if r['origin']=='revised_candidate':
                case=r['body'].split('**Distinct failure test:** ',1)[1].split('\n',1)[0];cases.append(case)
        self.assertEqual(len(cases),len(set(cases)))
    def test_paths_fit_reported_windows_checkout(self):
        prefix='C:\\Users\\User1\\Documents\\Downloads\\Proj\\business_portfolio\\'
        for r in self.data['archived_records']:self.assertLess(len(prefix+r['path']),240)
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
    def test_project_work_is_not_indexed_but_real_work_niche_is(self):
        root,old,meta=self.fixture()
        niche=old.parent.parent
        project=niche/'awa-001-product'/'project.md'
        project.parent.mkdir();old.rename(project)
        work=project.parent/'work';work.mkdir()
        sample=work/'projects';sample.mkdir()
        (work/'NICHE.json').write_text('{"sample": "not a niche"}')
        (sample/'example.md').write_text('Example product documentation, not a canonical record.')
        actual_work_niche=niche/'work';actual_work_niche.mkdir()
        (actual_work_niche/'NICHE.json').write_text(json.dumps(dict(
            id='N-real-work-niche',title='Work',parent=meta['niche_id'],
            path=meta['niche_path']+'/work',priority=9,working=False)))
        child=actual_work_niche/'work-001-product'/'project.md'
        child.parent.mkdir();(child.parent/'work').mkdir()
        self.write(child,{**meta,'id':'WORK-001','niche_path':meta['niche_path']+'/work',
                          'niche_id':'N-real-work-niche'})
        data=b.load_portfolio(root)
        self.assertEqual({r['id'] for r in data['records']},{meta['id'],'WORK-001'})
        self.assertIn('N-real-work-niche',{n['id'] for n in data['niches']})
        self.assert_current_catalogue_matches_files(root,data)
        self.assertIn(work/'NICHE.json',list(b.walk_files(root/'niches')))
        self.assertNotIn(work/'NICHE.json',list(b.walk_index_inputs(root/'niches')))

    def test_index_still_rejects_unsafe_canonical_work_root(self):
        root,old,meta=self.fixture()
        project=old.parent.parent/'awa-001-product'/'project.md'
        project.parent.mkdir();old.rename(project)
        outside=root/'outside-work';outside.mkdir()
        try:(project.parent/'work').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('symlinks unavailable on this platform')
        with self.assertRaisesRegex(b.ValidationError,'work/ folder is missing or unsafe'):
            b.load_portfolio(root)
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
    def test_working_setting_requires_boolean(self):
        root,p,m=self.fixture();niche=root/'niches'/m['niche_path']/'NICHE.json'
        data=json.loads(niche.read_text());data['working']='false';niche.write_text(json.dumps(data))
        with self.assertRaisesRegex(b.ValidationError,'working must be boolean'):b.load_portfolio(root)
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
