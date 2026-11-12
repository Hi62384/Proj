"""Exercise persisted selections and proof-based reconnects with disposable files."""
from pathlib import Path
import tempfile
import unittest

from portfolio_manager.coordinator import Coordinator
from portfolio_manager.workspace import ChatWorkspaces, context_path
from portfolio_manager.tests.test_runner import _record


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.record = _record(self.root, 'FAKE-001')
        self.source = self.root / 'example.py'
        self.source.write_text('answer = 42\n', encoding='utf-8')
        self.coordinator = Coordinator(self.root)
        self.store = ChatWorkspaces(self.coordinator)

    def test_two_connections_keep_distinct_selections_and_reconnect(self):
        a = self.store.attach('a' * 32)
        b = self.store.attach('b' * 32)
        self.assertNotEqual(a['id'], b['id'])
        chosen = self.store.select(a['id'], self.source, a['revision'], client='a' * 32)
        self.assertEqual(chosen['selection'], 'example.py')
        self.assertEqual(self.store.get(b['id'])['selection'], b['selection'])
        self.assertEqual(self.store.attach('a' * 32)['id'], a['id'])
        self.assertNotIn('reconnect_key', self.store.get(a['id']))
        restarted = ChatWorkspaces(Coordinator(self.root))
        result = restarted.attach('c' * 32, a['reconnect_key'])
        self.assertEqual(result, chosen)
        with self.assertRaises(PermissionError):
            restarted.select(a['id'], self.record, client='a' * 32)
        with self.assertRaises(PermissionError):
            restarted.attach('b' * 32, a['reconnect_key'])

    def test_stale_edit_and_out_of_scope_paths_are_rejected(self):
        row = self.store.attach('a' * 32)
        self.store.select(row['id'], self.source, 0)
        with self.assertRaisesRegex(ValueError, 'selection changed'):
            self.store.select(row['id'], self.record, 0)
        for path in ('../outside.py', '.git/config', 'outputs/paid.zip', 'auth.json',
                     'business_portfolio/../example.py'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                context_path(self.root, path)
