"""Exercise real niche/project creation, recoverable removal and rollback."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from business_portfolio.tools import build_browser
from portfolio_manager.project_management import create_niche, create_project, delete_niche
from portfolio_manager.tests.test_runner import _record


class ProjectManagementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        self.existing = _record(self.repo, 'TEST-001')
        target = self.repo / 'business_portfolio/tools/browser_template.html'
        target.parent.mkdir(parents=True)
        template = Path(__file__).resolve().parents[2] / 'business_portfolio/tools/browser_template.html'
        target.write_bytes(template.read_bytes())
        self.selection = 'business_portfolio/niches/demo'
        self.portfolio = self.repo / 'business_portfolio'
        build_browser.build(self.portfolio)

    def test_new_projects_are_distinct_phase1_placeholders_directly_under_niche(self):
        first = create_project(self.repo, self.selection)
        second = create_project(self.repo, self.selection)
        self.assertNotEqual(first['id'], second['id'])
        self.assertEqual(first['title'], 'Empty project')
        self.assertNotIn('/projects/', first['path'])
        path = self.repo / first['path']
        meta, body = build_browser.parse_project(path.read_text())
        self.assertEqual(meta['project_phase'], 'working_phase_1')
        self.assertEqual(meta['source_ids'], [])
        self.assertTrue(meta['draft'])
        self.assertFalse(meta['execution_authorized'])
        self.assertEqual(meta['commercial_validation'], 'unvalidated')
        self.assertEqual(meta['delivery_window_days'], {'minimum': 2, 'maximum': 21})
        self.assertTrue((path.parent / 'work/.gitkeep').is_file())
        self.assertIn('## Phase 6', body)
        ids = {row['id'] for row in build_browser.load_portfolio(self.portfolio)['records']}
        self.assertEqual(ids, {'TEST-001', first['id'], second['id']})

    def test_create_subniche_and_recoverable_delete_preserve_record_and_work(self):
        child = create_niche(self.repo, self.selection, '3D Tools')
        meta = json.loads((self.repo / child['path'] / 'NICHE.json').read_text())
        self.assertEqual(meta['parent'], 'N-demo')
        self.assertFalse(meta['working'])
        project = create_project(self.repo, child['path'])
        path = self.repo / project['path']
        payload = path.parent / 'work/source.txt'
        payload.write_text('preserved work')
        result = delete_niche(self.repo, child['path'])
        self.assertFalse((self.repo / child['path']).exists())
        self.assertEqual(result['project_ids'], [project['id']])
        recovered = self.repo / result['trash_path'] / path.parent.name
        self.assertEqual((recovered / 'work/source.txt').read_text(), 'preserved work')
        self.assertTrue((recovered / 'project.md').is_file())
        self.assertTrue(self.existing.is_file())
        ids = {row['id'] for row in build_browser.load_portfolio(self.portfolio)['records']}
        self.assertEqual(ids, {'TEST-001'})

    def test_delete_rejects_cross_niche_project_references(self):
        child = create_niche(self.repo, self.selection, 'Linked niche')
        project = create_project(self.repo, child['path'])
        raw = self.existing.read_text()
        meta, body = build_browser.parse_project(raw)
        meta['related_projects'] = [project['id']]
        self.existing.write_text('---\n' + json.dumps(meta) + '\n---\n' + body)
        with self.assertRaisesRegex(ValueError, 'still reference'):
            delete_niche(self.repo, child['path'])
        self.assertTrue((self.repo / child['path']).is_dir())

    def test_failed_creation_or_delete_restores_tree_and_generated_views(self):
        child = create_niche(self.repo, self.selection, 'Rollback')
        original_index = (self.portfolio / 'PROJECT_INDEX.json').read_bytes()
        original_browser = (self.portfolio / 'PROJECT_BROWSER.html').read_bytes()
        real_build = build_browser.build
        def fail_after_write(portfolio):
            real_build(portfolio)
            raise ValueError('simulated rebuild failure')
        with patch('portfolio_manager.project_management.build_browser.build', side_effect=fail_after_write):
            with self.assertRaisesRegex(ValueError, 'simulated'):
                create_project(self.repo, self.selection)
            with self.assertRaisesRegex(ValueError, 'simulated'):
                delete_niche(self.repo, child['path'])
        self.assertTrue((self.repo / child['path']).is_dir())
        self.assertEqual((self.portfolio / 'PROJECT_INDEX.json').read_bytes(), original_index)
        self.assertEqual((self.portfolio / 'PROJECT_BROWSER.html').read_bytes(), original_browser)
        self.assertEqual(len(build_browser.load_portfolio(self.portfolio)['records']), 1)

    def test_reserved_duplicate_and_non_niche_selections_are_rejected(self):
        for title in ('projects', '../', 'CON', '', 'bad\nname'):
            with self.subTest(title=title), self.assertRaises(ValueError):
                create_niche(self.repo, self.selection, title)
        create_niche(self.repo, self.selection, 'Existing')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            create_niche(self.repo, self.selection, 'Existing')
        for selection in ('business_portfolio/niches', self.existing.relative_to(self.repo).as_posix()):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                create_project(self.repo, selection)

    def test_linked_recovery_folder_is_rejected_without_deletion(self):
        private = self.portfolio / '.local'
        private.mkdir()
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        try:
            (private / 'deleted_niches').symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(str(exc))
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            delete_niche(self.repo, self.selection)
        self.assertTrue(self.existing.is_file())
        self.assertEqual(list(outside.iterdir()), [])

    def test_deleted_project_id_is_not_reused_and_completed_receipt_survives(self):
        child = create_niche(self.repo, self.selection, 'Unique')
        project = create_project(self.repo, child['path'])
        completed = self.portfolio / 'completed_projects'
        completed.mkdir()
        receipt = completed / (project['id'] + '.json')
        receipt.write_text(json.dumps({'id': project['id'], 'project_phase': 'complete',
                                       'title': 'Previously completed project'}))
        receipt_bytes = receipt.read_bytes()
        delete_niche(self.repo, child['path'])
        recreated = create_niche(self.repo, self.selection, 'Unique')
        next_project = create_project(self.repo, recreated['path'])
        self.assertNotEqual(next_project['id'], project['id'])
        self.assertEqual(receipt.read_bytes(), receipt_bytes)

    def test_portfolio_writer_lock_prevents_creation(self):
        lock = self.portfolio / '.project-phase.lock'
        lock.write_text('another writer')
        try:
            with self.assertRaisesRegex(ValueError, 'another chat'):
                create_project(self.repo, self.selection)
            self.assertEqual(len(build_browser.load_portfolio(self.portfolio)['records']), 1)
        finally:
            lock.unlink()


if __name__ == '__main__':
    unittest.main()
