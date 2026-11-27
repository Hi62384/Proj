"""Real paste/file replacements: same-phase updates, protected facts and rollback."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from business_portfolio.tools import build_browser
from portfolio_manager.project_management import create_project
from portfolio_manager.project_update import replace_project_text, replace_project_from_file, snapshot_sha256
from portfolio_manager.tests.test_runner import _record


class ResearchUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        _record(self.repo, 'TEST-001')
        template = Path(__file__).resolve().parents[2] / 'business_portfolio/tools/browser_template.html'
        target = self.repo / 'business_portfolio/tools/browser_template.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(template.read_bytes())
        self.project = create_project(self.repo, 'business_portfolio/niches/demo')
        self.selection = self.project['path']
        self.path = self.repo / self.selection

    def replacement(self, *, phase=None, change=None, digest=True, body=None):
        raw = self.path.read_text()
        meta, _ = build_browser.parse_project(raw)
        if phase is not None:
            meta['project_phase'] = phase
        meta.update(title='Useful original tool', record_type='product_candidate', draft=False)
        if digest:
            meta['project_update_base_sha256'] = snapshot_sha256(raw)
        if change:
            meta.update(change)
        return '---\n' + json.dumps(meta) + '\n---\n\n' + (body or '# Useful original tool\n\nA detailed revised plan describing buyer needs, differentiators, features, acceptance tests and viable cost constraints.\n\nSource: https://example.org/research\n')

    def test_rewrites_planning_body_and_preserves_same_phase_and_work(self):
        original = self.path.read_bytes()
        payload = self.path.parent / 'work/preserved.txt'
        payload.write_text('actual existing work')
        result = replace_project_text(self.repo, self.selection, self.replacement())
        meta, body = build_browser.parse_project(self.path.read_text())
        self.assertEqual(meta['project_phase'], 'working_phase_1')
        self.assertFalse(meta['draft'])
        self.assertNotIn('This is an empty planning record', body)
        self.assertNotIn('project_update_base_sha256', meta)
        self.assertEqual(Path(result['backup']).read_bytes(), original)
        self.assertEqual(payload.read_text(), 'actual existing work')

    def test_all_research_phases_accept_approved_reviews_without_advancing(self):
        for number in (1, 2, 3):
            with self.subTest(phase=number):
                raw = self.path.read_text()
                meta, body = build_browser.parse_project(raw)
                meta['project_phase'] = f'working_phase_{number}'
                self.path.write_text('---\n' + json.dumps(meta) + '\n---\n' + body)
                text = self.replacement(change={'research_verification': {f'phase_{number}': 'approved'}})
                outcome = replace_project_text(self.repo, self.selection, text)
                self.assertEqual(outcome['project_phase'], f'working_phase_{number}')

    def test_custom_delivery_window_is_accepted_and_invalid_windows_rejected(self):
        original = self.path.read_bytes()
        for value in ({'minimum': 0, 'maximum': 10}, {'minimum': True, 'maximum': 10},
                      {'minimum': 11, 'maximum': 10}, {'minimum': 2},
                      {'minimum': 2, 'maximum': 1000000},
                      {'minimum': 2, 'maximum': 10, 'extra': 1}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                replace_project_text(self.repo, self.selection, self.replacement(change={'delivery_window_days': value}))
            self.assertEqual(self.path.read_bytes(), original)
        window = {'minimum': 2, 'maximum': 10}
        replace_project_text(self.repo, self.selection, self.replacement(change={'delivery_window_days': window}))
        self.assertEqual(build_browser.parse_project(self.path.read_text())[0]['delivery_window_days'], window)

    def test_accepts_outer_fence_crlf_and_external_file(self):
        text = '````markdown\n' + self.replacement() + '\n````\n'
        source = Path(self.tmp.name) / 'update.md'
        source.write_bytes(text.replace('\n', '\r\n').encode('utf-8'))
        replace_project_from_file(self.repo, self.selection, source)
        self.assertIn('Useful original tool', self.path.read_text())
        self.assertEqual(snapshot_sha256('a\r\nb'), snapshot_sha256('a\nb'))

    def test_rejects_stale_snapshot_phase_identity_and_permission_changes(self):
        original = self.path.read_bytes()
        for change in ({'project_update_base_sha256': '0' * 64}, {'project_phase': 'working_phase_2'},
                       {'id': 'OTHER-001'}, {'niche_path': 'other'}, {'execution_authorized': True},
                       {'commercial_validation': 'commercially_validated'}, {'owner_budget': {'authorized_spend': 100}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                replace_project_text(self.repo, self.selection, self.replacement(change=change))
            self.assertEqual(self.path.read_bytes(), original)
        with self.assertRaisesRegex(ValueError, 'stale'):
            replace_project_text(self.repo, self.selection, self.replacement(digest=False), expected_sha256='f' * 64)

    def test_invalid_schema_or_failed_build_restores_original_and_views(self):
        original = self.path.read_bytes()
        portfolio = self.repo / 'business_portfolio'
        index = (portfolio / 'PROJECT_INDEX.json').read_bytes()
        browser = (portfolio / 'PROJECT_BROWSER.html').read_bytes()
        with self.assertRaises(ValueError):
            replace_project_text(self.repo, self.selection, self.replacement(change={'source_ids': ['UNKNOWN']}))
        self.assertEqual(self.path.read_bytes(), original)
        real_build = build_browser.build
        def fail_after_write(root):
            real_build(root)
            raise ValueError('injected failure')
        with patch('portfolio_manager.project_update.build_browser.build', side_effect=fail_after_write):
            with self.assertRaisesRegex(ValueError, 'injected'):
                replace_project_text(self.repo, self.selection, self.replacement())
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual((portfolio / 'PROJECT_INDEX.json').read_bytes(), index)
        self.assertEqual((portfolio / 'PROJECT_BROWSER.html').read_bytes(), browser)

    def test_execution_phase_replacements_are_rejected(self):
        meta, body = build_browser.parse_project(self.path.read_text())
        meta['project_phase'] = 'working_phase_4'
        self.path.write_text('---\n' + json.dumps(meta) + '\n---\n' + body)
        with self.assertRaisesRegex(ValueError, 'Phases 1–3'):
            replace_project_text(self.repo, self.selection, self.replacement())

    def test_partial_records_and_truncated_fences_do_not_replace_record(self):
        original = self.path.read_bytes()
        for text in ('Project is good to go.', '```markdown\n' + self.replacement(), '---\n{}\n---\nbody'):
            with self.subTest(text=text[:25]), self.assertRaises(ValueError):
                replace_project_text(self.repo, self.selection, text)
            self.assertEqual(self.path.read_bytes(), original)

    def test_links_in_recovery_storage_are_rejected(self):
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        local = self.repo / 'business_portfolio/.local'
        local.mkdir()
        try:
            (local / 'project_backups').symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(str(exc))
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            replace_project_text(self.repo, self.selection, self.replacement())
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
