import json
from pathlib import Path
import tempfile
import unittest

from portfolio_manager.project_import import import_projects
from portfolio_manager.tests.test_runner import _record


class ProjectImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        self.example = _record(self.repo, 'TEST-001')
        tools = self.repo / 'business_portfolio/tools'
        tools.mkdir(parents=True)
        template = Path(__file__).resolve().parents[2] / 'business_portfolio/tools/browser_template.html'
        (tools / 'browser_template.html').write_bytes(template.read_bytes())
        self.selection = 'business_portfolio/niches/demo'

    def make_file(self, ident):
        raw = self.example.read_text(encoding='utf-8')
        front, body = raw[4:].split('\n---\n', 1)
        meta = json.loads(front)
        meta.update(id=ident, niche_id='N-other', niche_path='other', title='Imported ' + ident)
        path = Path(self.temp.name) / (ident + '.md')
        path.write_text('---\n' + json.dumps(meta) + '\n---\n' + body, encoding='utf-8')
        return path

    def test_multiple_imports_update_destination_and_index(self):
        ids = import_projects(self.repo, self.selection, [self.make_file('TEST-002'), self.make_file('TEST-003')])
        self.assertEqual(ids, ['TEST-002', 'TEST-003'])
        index = json.loads((self.repo / 'business_portfolio/PROJECT_INDEX.json').read_text(encoding='utf-8'))
        records = {r['id']: r for r in index['records']}
        self.assertEqual(records['TEST-002']['niche_id'], 'N-demo')
        self.assertEqual(records['TEST-003']['niche_path'], 'demo')
        for ident in ids:
            folder = self.repo / 'business_portfolio/niches/demo/projects'
            matching = list(folder.glob(ident.lower() + '-*/project.md'))
            self.assertEqual(len(matching), 1)
            self.assertTrue((matching[0].parent / 'work').is_dir())
            self.assertEqual(records[ident]['path'], matching[0].relative_to(self.repo / 'business_portfolio').as_posix())
            self.assertEqual(records[ident]['project_phase'], 'working_phase_2')

    def test_duplicate_and_invalid_batch_leave_existing_records_untouched(self):
        original = self.example.read_bytes()
        with self.assertRaises(ValueError):
            import_projects(self.repo, self.selection, [self.make_file('TEST-002'), self.make_file('TEST-001')])
        self.assertEqual(self.example.read_bytes(), original)
        self.assertEqual(len(list(self.example.parent.glob('*.md'))), 1)
