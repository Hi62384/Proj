"""Layout/phase migration preserves canonical evidence and all work bytes."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from business_portfolio.tools import build_browser
from business_portfolio.tools.migrate_six_phase import migrate
from portfolio_manager.tests.test_runner import _record


class SixPhaseMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        self.legacy = _record(self.repo, 'DEMO-101')
        self.portfolio = self.repo / 'business_portfolio'

    def set_old_phase(self, phase):
        meta, body = build_browser.parse_project(self.legacy.read_text())
        meta['project_phase'] = phase
        self.legacy.write_text('---\n' + json.dumps(meta) + '\n---\n' + body + '\n')

    def folder_record(self):
        nested = self.legacy.parent / 'demo-101' / 'project.md'
        nested.parent.mkdir()
        (nested.parent / 'work').mkdir()
        nested.write_bytes(self.legacy.read_bytes())
        self.legacy.unlink()
        self.legacy = nested
        return nested

    def test_flat_record_migrates_to_direct_niche_with_no_fake_approval(self):
        before = self.legacy.read_bytes()
        _, old_body = build_browser.parse_project(before.decode())
        old_path = self.legacy.relative_to(self.repo).as_posix()
        rows = migrate(self.repo, rebuild=False)
        target = self.repo / rows[0]['to']
        self.assertNotIn('/projects/', rows[0]['to'])
        self.assertFalse(self.legacy.exists())
        self.assertTrue((target.parent / 'work/.gitkeep').is_file())
        meta, body = build_browser.parse_project(target.read_text())
        self.assertEqual(meta['project_phase'], 'working_phase_4')
        self.assertEqual(meta['workflow_version'], 2)
        self.assertEqual(meta['workflow_migration']['previous_record_path'], old_path)
        self.assertFalse(meta['workflow_migration']['research_approval_inferred'])
        self.assertTrue(body.startswith(old_body))
        self.assertEqual(set(meta['research_verification'].values()), {'unreviewed'})
        self.assertEqual(meta['commercial_validation'], 'unvalidated')
        backups = list((self.portfolio / '.local/workflow_migration/DEMO-101').glob('*.md'))
        self.assertEqual([p.read_bytes() for p in backups], [before])
        self.assertEqual(migrate(self.repo, rebuild=False), [])

    def test_nested_record_keeps_artifacts_byte_identical(self):
        old = self.folder_record()
        artifact = old.parent / 'work/product.bin'
        artifact.write_bytes(b'\x00\xffSome actual artifact\n')
        meta, body = build_browser.parse_project(old.read_text())
        old_folder = old.parent.relative_to(self.repo).as_posix()
        old.write_text('---\n' + json.dumps(meta) + '\n---\n' + body + '\n' + old_folder + '/work/product.bin\n')
        rows = migrate(self.repo, rebuild=False)
        target = self.repo / rows[0]['to']
        self.assertEqual((target.parent / 'work/product.bin').read_bytes(), b'\x00\xffSome actual artifact\n')
        self.assertIn(target.parent.relative_to(self.repo).as_posix() + '/work/product.bin', target.read_text())
        self.assertFalse(old.parent.parent.exists())

    def test_old_platform_research_maps_to_release_research(self):
        self.set_old_phase('working_phase_3')
        self.assertEqual(migrate(self.repo, rebuild=False)[0]['project_phase'], 'working_phase_2')

    def test_old_execution_maps_to_release_execution(self):
        self.set_old_phase('working_phase_4')
        self.assertEqual(migrate(self.repo, rebuild=False)[0]['project_phase'], 'working_phase_5')

    def test_complete_receipt_keeps_completion_and_updates_record_location(self):
        self.set_old_phase('complete')
        receipt_path = self.portfolio / 'completed_projects/DEMO-101.json'
        receipt_path.parent.mkdir()
        receipt = {'id': 'DEMO-101', 'project_phase': 'complete', 'description': 'Preserved evidence',
                   'source_project': self.legacy.relative_to(self.repo).as_posix()}
        receipt_path.write_text(json.dumps(receipt))
        rows = migrate(self.repo, rebuild=False)
        changed = json.loads(receipt_path.read_text())
        self.assertEqual(changed, {**receipt, 'source_project': rows[0]['to']})
        self.assertEqual(rows[0]['project_phase'], 'complete')

    def test_validation_failure_rolls_back_record_and_artifact_move(self):
        self.folder_record()
        artifact = self.legacy.parent / 'work/product.bin'
        artifact.write_bytes(b'Preserve me')
        original = self.legacy.read_bytes()
        load = build_browser.load_portfolio
        calls = []
        def fail_after_mutation(root):
            calls.append(root)
            if len(calls) > 1:
                raise ValueError('Simulated post-move failure')
            return load(root)
        with patch.object(build_browser, 'load_portfolio', side_effect=fail_after_mutation):
            with self.assertRaisesRegex(ValueError, 'post-move failure'):
                migrate(self.repo, rebuild=False)
        self.assertEqual(self.legacy.read_bytes(), original)
        self.assertEqual(artifact.read_bytes(), b'Preserve me')
        self.assertFalse((self.legacy.parent.parent.parent / 'demo-101').exists())

    def test_destination_collision_does_not_overwrite(self):
        target = self.legacy.parent.parent / 'demo-101'
        target.mkdir()
        (target / 'unrelated.txt').write_text('Keep me')
        original = self.legacy.read_bytes()
        with self.assertRaisesRegex(ValueError, 'destination already exists'):
            migrate(self.repo, rebuild=False)
        self.assertEqual(self.legacy.read_bytes(), original)
        self.assertEqual((target / 'unrelated.txt').read_text(), 'Keep me')

    def test_failed_rebuild_restores_original_generated_views(self):
        original = self.legacy.read_bytes()
        index = self.portfolio / 'PROJECT_INDEX.json'
        browser = self.portfolio / 'PROJECT_BROWSER.html'
        index.write_bytes(b'Original index snapshot')
        browser.write_bytes(b'Original browser snapshot')
        def partial_rebuild(root):
            index.write_bytes(b'New partial index')
            raise OSError('Simulated disk error')
        with patch.object(build_browser, 'build', side_effect=partial_rebuild):
            with self.assertRaisesRegex(OSError, 'disk error'):
                migrate(self.repo)
        self.assertEqual(self.legacy.read_bytes(), original)
        self.assertEqual(index.read_bytes(), b'Original index snapshot')
        self.assertEqual(browser.read_bytes(), b'Original browser snapshot')

    def test_six_phase_draft_may_have_no_sources_but_not_unknown_sources(self):
        meta, body = build_browser.parse_project(self.legacy.read_text())
        meta.update(workflow_version=2, project_phase='working_phase_1', source_ids=[], title='Empty project')
        self.legacy.write_text('---\n' + json.dumps(meta) + '\n---\n' + body)
        self.assertEqual(len(build_browser.load_portfolio(self.portfolio)['records']), 1)
        meta['source_ids'] = ['MADE-UP']
        self.legacy.write_text('---\n' + json.dumps(meta) + '\n---\n' + body)
        with self.assertRaisesRegex(ValueError, 'missing/unknown sources'):
            build_browser.load_portfolio(self.portfolio)


if __name__ == '__main__':
    unittest.main()
