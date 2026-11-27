"""Real paste/file replacement, verified automatic advancement and rollback."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from business_portfolio.tools import build_browser
from portfolio_manager.project_management import create_project
from portfolio_manager.project_update import replace_project_text, replace_project_from_file, snapshot_sha256
from portfolio_manager.tests.test_runner import _record


VERIFIED_BODY = """# Fictional verified product

## Phase 1 — Research

### Stage 1 — Product research

Buyer and alternatives evidence: https://example.org/product. Bounded TEST-FIRST GO.

### Stage 2 — Release research

Compatible format and accepted channel evidence: https://example.org/release.

### Stage 3 — Marketing research

Audience, channel and policy evidence: https://example.org/marketing.

## Phase 1b verification

All three fictional independent evidence checks passed; no decisive blocker remains.

## Phase 2 — Build and verify

- [ ] Build the fixture and run its acceptance tests.

## Phase 3 — Release execution

- [ ] Prepare package and verify customer access.

## Phase 4 — Marketing execution

- [ ] Publish authorized material and inspect the real result.

## Important data and URLs

All example sources above are research fixtures, not real releases.

## Decisions and work log

Fixture research complete; execution has not begun.
"""


def verified_fields():
    return {'research_verification': {f'phase_{n}': 'approved' for n in (1, 2, 3)},
            'research_verdict': 'GO', 'project_update_phase_1b': 'verified'}


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

    def test_verified_final_paste_advances_once_and_preserves_work(self):
        original = self.path.read_bytes()
        artifact = self.path.parent / 'work/keep.txt'
        artifact.write_bytes(b'preserved work')
        text = self.replacement(change=verified_fields(), body=VERIFIED_BODY)
        result = replace_project_text(self.repo, self.selection, text)
        meta, body = build_browser.parse_project(self.path.read_text())
        self.assertEqual(meta['workflow_version'], 3)
        self.assertEqual(meta['project_phase'], 'working_phase_2')
        self.assertTrue(result['advanced'])
        self.assertEqual(meta['phase_history'][-1]['from'], 'working_phase_1')
        self.assertEqual(meta['phase_history'][-1]['to'], 'working_phase_2')
        self.assertEqual(meta['commercial_validation'], 'unvalidated')
        self.assertFalse(meta['execution_authorized'])
        self.assertNotIn('project_update_base_sha256', meta)
        self.assertNotIn('project_update_phase_1b', meta)
        self.assertEqual(body, VERIFIED_BODY.strip())
        self.assertEqual(Path(result['backup']).read_bytes(), original)
        self.assertEqual(artifact.read_bytes(), b'preserved work')
        with self.assertRaisesRegex(ValueError, 'only in Phase 1'):
            replace_project_text(self.repo, self.selection, text)
        self.assertEqual(build_browser.parse_project(self.path.read_text())[0]['project_phase'], 'working_phase_2')

    def test_unverified_draft_and_no_go_remain_in_phase_one(self):
        for verdict in ('GO', 'NO_GO', 'RESEARCH_BLOCKED', 'CONDITIONAL_PROOF_ONLY'):
            with self.subTest(verdict=verdict):
                result = replace_project_text(self.repo, self.selection, self.replacement(
                    change={'research_verdict': verdict,
                            'research_verification': {f'phase_{n}': 'unreviewed' for n in (1, 2, 3)}},
                    body=VERIFIED_BODY))
                self.assertFalse(result['advanced'])
                self.assertEqual(result['project_phase'], 'working_phase_1')

    def test_invalid_final_review_cannot_advance_or_replace(self):
        original = self.path.read_bytes()
        for changes in (
            {'research_verdict': 'NO_GO'}, {'research_verdict': 'RESEARCH_BLOCKED'},
            {'research_verdict': 'CONDITIONAL_PROOF_ONLY'}, {'draft': True},
            {'research_verification': {'phase_1': 'approved', 'phase_2': 'approved'}},
            {'research_verification': {'phase_1': 'approved', 'phase_2': 'blocked', 'phase_3': 'approved'}},
            {'project_update_base_sha256': '0' * 64},
            {'project_update_phase_1b': 'bogus'}, {'record_type': 'empty_project'},
            {'id': 'OTHER-001'}, {'execution_authorized': True},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                replace_project_text(self.repo, self.selection,
                    self.replacement(change={**verified_fields(), **changes}, body=VERIFIED_BODY))
            self.assertEqual(self.path.read_bytes(), original)
        with self.assertRaisesRegex(ValueError, 'BASE_SHA256'):
            replace_project_text(self.repo, self.selection,
                self.replacement(digest=False, change=verified_fields(), body=VERIFIED_BODY))
        for body in ('Incomplete text', VERIFIED_BODY.replace('### Stage 2 — Release research', '### Missing release'),
                     VERIFIED_BODY.replace('## Phase 1b verification', '## Missing independent check')):
            with self.subTest(body=body[:35]), self.assertRaisesRegex(ValueError, 'missing required'):
                replace_project_text(self.repo, self.selection,
                    self.replacement(change=verified_fields(), body=body))
            self.assertEqual(self.path.read_bytes(), original)

    def test_verified_import_rollback_is_atomic(self):
        original = self.path.read_bytes()
        root = self.repo / 'business_portfolio'
        index = (root / 'PROJECT_INDEX.json').read_bytes()
        browser = (root / 'PROJECT_BROWSER.html').read_bytes()
        real_build = build_browser.build
        def fail_after_write(portfolio):
            real_build(portfolio)
            raise ValueError('injected verified import failure')
        with patch('portfolio_manager.project_update.build_browser.build', side_effect=fail_after_write):
            with self.assertRaisesRegex(ValueError, 'injected verified'):
                replace_project_text(self.repo, self.selection,
                    self.replacement(change=verified_fields(), body=VERIFIED_BODY))
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual((root / 'PROJECT_INDEX.json').read_bytes(), index)
        self.assertEqual((root / 'PROJECT_BROWSER.html').read_bytes(), browser)

    def test_legacy_research_record_advances_with_original_snapshot(self):
        meta, body = build_browser.parse_project(self.path.read_text())
        meta.update(workflow_version=2, project_phase='working_phase_3')
        self.path.write_text('---\n' + json.dumps(meta) + '\n---\n' + body)
        result = replace_project_text(self.repo, self.selection,
            self.replacement(change=verified_fields(), body=VERIFIED_BODY))
        self.assertTrue(result['advanced'])
        updated, body = build_browser.parse_project(self.path.read_text())
        self.assertEqual(updated['project_phase'], 'working_phase_2')
        self.assertEqual(updated['workflow_v3_migration']['previous_project_phase'], 'working_phase_3')
        self.assertFalse(updated['workflow_v3_migration']['research_approval_inferred'])

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
        with self.assertRaisesRegex(ValueError, 'only in Phase 1'):
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
