import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from portfolio_manager.integration import ManagerHost
from portfolio_manager.project_actions import update_project
from portfolio_manager.tests.test_runner import _record


class ProjectActionsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.repo = root / 'repo'
        self.record = _record(self.repo, 'DEMO-001')
        tools = self.repo / 'business_portfolio/tools'
        tools.mkdir(parents=True)
        source = Path(__file__).resolve().parents[2] / 'business_portfolio/tools/browser_template.html'
        (tools / 'browser_template.html').write_bytes(source.read_bytes())
        self.host = ManagerHost(self.repo, root / 'state')
        self.addCleanup(self.host.close)
        self.selection = self.record.relative_to(self.repo).as_posix()

    def digest(self):
        return hashlib.sha256(self.record.read_bytes()).hexdigest()

    def test_completion_keeps_body_and_updates_index(self):
        before = self.record.read_text(encoding='utf-8')
        update_project(self.host, self.selection, self.digest(), 'complete')
        after = self.record.read_text(encoding='utf-8')
        self.assertIn('Fictional work only.', after)
        self.assertIn('owner marked this project complete', after)
        index = json.loads((self.repo / 'business_portfolio/PROJECT_INDEX.json').read_text(encoding='utf-8'))
        self.assertEqual(index['records'][0]['work_state'], 'completed')
        self.assertIn('"work_state": "planned"', before)

    def test_reopen_restores_previous_state_and_keeps_completion_history(self):
        raw = self.record.read_text(encoding='utf-8').replace('"work_state": "planned"', '"work_state": "blocked"')
        self.record.write_text(raw, encoding='utf-8')
        update_project(self.host, self.selection, self.digest(), 'complete')
        update_project(self.host, self.selection, self.digest(), 'reopen')
        text = self.record.read_text(encoding='utf-8')
        self.assertIn('"work_state": "blocked"', text)
        self.assertNotIn('owner_completion_previous_work_state', text)
        self.assertIn('owner marked this project complete', text)
        self.assertIn('owner removed the complete status', text)

    def test_reopen_older_completed_record_defaults_to_planned(self):
        text = self.record.read_text(encoding='utf-8').replace('"work_state": "planned"', '"work_state": "completed"')
        self.record.write_text(text, encoding='utf-8')
        update_project(self.host, self.selection, self.digest(), 'reopen')
        self.assertIn('"work_state": "planned"', self.record.read_text(encoding='utf-8'))

    def test_delete_is_recoverable_and_updates_index(self):
        original = self.record.read_bytes()
        saved = update_project(self.host, self.selection, self.digest(), 'delete')
        self.assertFalse(self.record.exists())
        self.assertEqual(saved.read_bytes(), original)
        index = json.loads((self.repo / 'business_portfolio/PROJECT_INDEX.json').read_text(encoding='utf-8'))
        self.assertEqual(index['records'], [])

    def test_stale_record_is_not_changed(self):
        with self.assertRaisesRegex(ValueError, 'changed'):
            update_project(self.host, self.selection, '0' * 64, 'complete')
        self.assertTrue(self.record.exists())

    def test_referenced_project_cannot_be_deleted(self):
        other = _record(self.repo, 'DEMO-002')
        raw = other.read_text(encoding='utf-8')
        other.write_text(raw.replace('"related_projects": []', '"related_projects": ["DEMO-001"]'), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'reference'):
            update_project(self.host, self.selection, self.digest(), 'delete')
        self.assertTrue(self.record.exists())

