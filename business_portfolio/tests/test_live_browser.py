"""Real loopback service and synthetic filesystem checks; no product/account changes."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_browser as b
import serve_browser as s


class LiveBrowserTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name);self.root=self.repo/'business_portfolio';self.root.mkdir()
        for name in ['research','tools','niches']:(self.root/name).mkdir()
        (self.root/'research/SOURCE_REGISTER.json').write_bytes((ROOT/'research/SOURCE_REGISTER.json').read_bytes())
        (self.root/'tools/browser_template.html').write_bytes((ROOT/'tools/browser_template.html').read_bytes())
        base=next(r for r in b.load_portfolio(ROOT)['records'] if r['id']=='AWA-001')
        self.meta={k:v for k,v in base.items() if k not in {'body','path','content_sha256'}}
        self.meta.update(niche_id='N-test',niche_path='test',parent_project=None,related_projects=[])
        folder=self.root/'niches/test/projects';folder.mkdir(parents=True)
        (folder.parent/'NICHE.json').write_text(json.dumps(dict(id='N-test',title='Test niche',path='test',parent=None)),encoding='utf-8')
        self.project=folder/'awa-001.md';self.write(self.project,self.meta,'# Fictional project\n\n## Instructions\nOriginal scope.\n- [ ] Task A')
        self.state=s.PortfolioState(self.root)
    def write(self,path,meta,body):path.write_text('---\n'+json.dumps(meta)+'\n---\n'+body+'\n',encoding='utf-8')
    def serve(self):
        self.server=s.LocalServer(('127.0.0.1',0),self.state);threading.Thread(target=self.server.serve_forever,daemon=True).start()
        self.addCleanup(self.server.server_close);self.addCleanup(self.server.shutdown)
        self.base=f'http://127.0.0.1:{self.server.server_port}'
        self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def get(self,path,headers=None):return self.opener.open(urllib.request.Request(self.base+path,headers=headers or {}),timeout=3)
    def test_http_view_and_health_are_read_only(self):
        self.serve()
        with self.get('/') as r:
            html=r.read().decode();self.assertIn('Project navigation',html);self.assertIn('Search projects',html)
            self.assertIn("connect-src 'self'",r.headers['Content-Security-Policy'])
        self.assertTrue(s.probe(self.server.server_port,self.root))
        self.assertFalse(s.probe(self.server.server_port,self.repo/'other'))
        with self.get('/api/portfolio') as r:self.assertEqual(len(json.load(r)['records']),1)
    def test_listener_cannot_share_an_occupied_port(self):
        self.serve()
        with self.assertRaises(OSError):s.LocalServer(('127.0.0.1',self.server.server_port),self.state)
    def test_cross_origin_and_dns_rebinding_rejected(self):
        self.serve()
        for headers in [{'Host':'evil.example'},{'Origin':'https://evil.example'},{'Sec-Fetch-Site':'cross-site'}]:
            with self.subTest(headers=headers),self.assertRaises(urllib.error.HTTPError) as e:self.get('/api/portfolio',headers)
            self.assertEqual(e.exception.code,403)
    def test_writes_and_arbitrary_files_are_not_routes(self):
        self.serve()
        for method in ['POST','PUT','DELETE','PATCH']:
            with self.subTest(method=method),self.assertRaises(urllib.error.HTTPError) as e:
                self.opener.open(urllib.request.Request(self.base+'/api/portfolio',data=b'{}',method=method),timeout=3)
            self.assertEqual(e.exception.code,405)
        for path in ['/../README.md','/files/../../secret','/.git/config','/api/execute','/niches/test/projects/not-listed.md']:
            with self.subTest(path=path),self.assertRaises(urllib.error.HTTPError) as e:self.get(path)
            self.assertEqual(e.exception.code,404)
    def test_incomplete_writes_keep_the_last_good_state(self):
        old=self.state.version;self.project.write_text('---\n{"partial":',encoding='utf-8')
        self.assertFalse(self.state.refresh());self.assertEqual(self.state.version,old)
        self.assertTrue(self.state.warning);self.assertEqual(len(self.state.data['records']),1)
        self.write(self.project,self.meta,'# Fictional project\n## Instructions\nUpdated scope.\n- [x] Task A')
        self.assertTrue(self.state.refresh());self.assertNotEqual(self.state.version,old);self.assertFalse(self.state.warning)
        self.assertGreater(self.state.data['records'][0]['recently_saved_at'],0)
    def test_real_watcher_detects_new_edit_rename_move_and_delete(self):
        threading.Thread(target=self.state.watch,daemon=True).start();self.addCleanup(self.state.stop.set)
        def changed(action):
            old=self.state.version;action();deadline=time.monotonic()+5
            while self.state.version==old and time.monotonic()<deadline:time.sleep(.05)
            self.assertNotEqual(self.state.version,old,'Watcher did not update within five seconds')
        new=self.project.with_name('awa-002.md');m={**self.meta,'id':'AWA-002','title':'Second fictional project'}
        changed(lambda:self.write(new,m,'# Second project\n## Instructions\nNew instructions.'))
        changed(lambda:self.write(new,m,'# Second project\n## Instructions\nEdited instructions.\n- [x] Task complete'))
        renamed=new.with_name('renamed.md');changed(lambda:new.rename(renamed))
        self.assertEqual({x['id'] for x in self.state.data['records']},{'AWA-001','AWA-002'})
        def move():
            child=self.root/'niches/test/child';(child/'projects').mkdir(parents=True)
            (child/'NICHE.json').write_text(json.dumps(dict(id='N-child',title='Child',path='test/child',parent='N-test')),encoding='utf-8')
            target=child/'projects/awa-002.md';self.write(target,{**m,'niche_id':'N-child','niche_path':'test/child'},'# Second project\n## Instructions\nMoved, same stable ID.');renamed.unlink()
        changed(move)
        moved=next(x for x in self.state.data['records'] if x['id']=='AWA-002');self.assertIn('/child/',moved['path'])
        changed(lambda:(self.root/moved['path']).unlink());self.assertEqual([x['id'] for x in self.state.data['records']],['AWA-001'])
    def test_concurrent_scan_retains_last_valid_data(self):
        old=self.state.version
        with patch.object(s,'fingerprint',side_effect=[('before',),('after',)]):self.assertFalse(self.state.refresh())
        self.assertEqual(self.state.version,old)
    def test_hidden_private_and_credentials_are_not_indexed(self):
        for name in ['.local','private']:
            folder=self.root/'niches'/name;folder.mkdir();(folder/'secret.md').write_text('SECRET_PRIVATE_SENTINEL')
        self.assertTrue(self.state.refresh());self.assertNotIn('SECRET_PRIVATE_SENTINEL',json.dumps(self.state.data))
    def test_allowlisted_guide_can_open_but_a_release_cannot(self):
        guide=self.repo/'public-guide.md';guide.write_text('Verified public source guide',encoding='utf-8')
        with patch.object(s,'GUIDES',{'AWA-001':[('Guide','public-guide.md','Source guide')]}):self.state.refresh()
        self.serve();key=next(iter(self.state.files))
        with self.get('/files/'+key) as response:self.assertEqual(response.read(),b'Verified public source guide')
        self.assertIsNone(s.safe_file(self.repo,'.local/secret.txt'))
        self.assertIsNone(s.safe_file(self.repo,'../outside.txt'))
        guide.unlink()
        with self.assertRaises(urllib.error.HTTPError) as e:self.get('/files/'+key)
        self.assertEqual(e.exception.code,404)
    def test_hardlinked_document_rejected(self):
        source=self.repo/'secret.txt';source.write_text('PRIVATE')
        target=self.root/'README.md'
        try:os.link(source,target)
        except OSError:self.skipTest('Hard links unavailable')
        self.assertFalse(self.state.refresh());self.assertNotIn('PRIVATE',json.dumps(self.state.data))
    def test_windows_reparse_input_rejected_without_link_privileges(self):
        with patch.object(b,'linked_input',return_value=True):
            with self.assertRaises(b.ValidationError):b.load_portfolio(self.root)
    def test_no_dashboard_controls_or_fabricated_percentage(self):
        html=(ROOT/'tools/browser_template.html').read_text(encoding='utf-8')
        for old in ['id="gate"','id="budgetfit"','id="origin"','id="showdoc"','Copy resume prompt']:self.assertNotIn(old,html)
        self.assertIn('Complete original record',html);self.assertIn('No completed tasks recorded.',html)
        self.assertIn('expanded=new Set()',html);self.assertIn('r.id===id',html)
        self.assertNotIn('.innerHTML',html)

    def test_declared_public_result_appears_and_secret_replacement_is_refused(self):
        meta={**self.meta,'public_results':[{'label':'Fictional proof','path':'results/AWA-001/proof.txt'}]}
        self.write(self.project,meta,'# Fictional result test')
        self.assertTrue(self.state.refresh())
        self.assertFalse(self.state.data['deliverables']['AWA-001'][0]['available'])
        result=self.root/'results/AWA-001/proof.txt';result.parent.mkdir(parents=True);result.write_text('Fictional public proof',encoding='utf-8')
        self.assertTrue(self.state.refresh());self.assertTrue(self.state.data['deliverables']['AWA-001'][0]['available'])
        self.serve();key=next(iter(self.state.files))
        with self.get('/files/'+key) as r:self.assertEqual(r.read(),b'Fictional public proof')
        result.write_text('https://user:password@example.invalid/private',encoding='utf-8')
        with self.assertRaises(urllib.error.HTTPError) as e:self.get('/files/'+key)
        self.assertEqual(e.exception.code,404)

    def test_result_paths_cannot_grant_private_or_cross_project_access(self):
        for path in ['../private.txt','results/OTHER-001/proof.txt','C:/secret.txt']:
            self.write(self.project,{**self.meta,'public_results':[{'label':'Unsafe','path':path}]},'# Test')
            self.assertFalse(self.state.refresh())

    def test_archiving_preserves_identity_and_history(self):
        self.write(self.project,{**self.meta,'work_state':'archived'},'# Fictional archived record\n- [x] Existing work')
        self.assertTrue(self.state.refresh());record=self.state.data['records'][0]
        self.assertEqual(record['id'],'AWA-001');self.assertEqual(record['work_state'],'archived')
        self.assertIn('[x] Existing work',record['body'])

    def test_existing_service_open_request_reopens_page(self):
        with patch.object(sys,'argv',['serve_browser.py','--open']),patch.object(s,'probe',return_value=True),patch.object(s.webbrowser,'open') as browser:
            self.assertEqual(s.main(),0)
            browser.assert_called_once_with('http://127.0.0.1:22841/',new=0)

    def test_existing_service_without_open_does_not_open_browser(self):
        with patch.object(sys,'argv',['serve_browser.py']),patch.object(s,'probe',return_value=True),patch.object(s.webbrowser,'open') as browser:
            self.assertEqual(s.main(),0)
            browser.assert_not_called()

    def test_http_template_is_the_last_validated_snapshot(self):
        (self.root/'tools/browser_template.html').write_text('UNVALIDATED_TEMPLATE',encoding='utf-8')
        self.serve()
        with self.get('/') as r:
            body=r.read().decode('utf-8');self.assertNotIn('UNVALIDATED_TEMPLATE',body)
            self.assertIn('Business Portfolio',body)

if __name__=='__main__':unittest.main()
