import json
import tempfile
import unittest
import os

from portfolio_manager.tests.windows_profile_journal import ProfileJournal
from portfolio_manager.tests.windows_stale_profile_recovery import inspect_record, windows_owner_state


class StaleRecordInspectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='portfolio-stale-record-')
        self.addCleanup(self.temp.cleanup)
        self.identifier = 'd' * 32
        self.journal = ProfileJournal(self.temp.name, self.identifier)
        self.addCleanup(lambda: self.journal._lock.close() if not self.journal._lock.closed else None)

    def test_live_lock_is_never_treated_as_stale(self):
        result = inspect_record(self.temp.name, self.identifier, owner_state=lambda _pid: 'dead')
        self.assertEqual(result['status'], 'busy')
        self.assertEqual(windows_owner_state(os.getpid()), 'alive')

    def test_pending_operation_and_unknown_owner_fail_closed(self):
        name = 'PortfolioManager.A.' + self.identifier + '.model'
        self.journal.update(pending=name, created=[])
        self.journal._lock.close()
        result = inspect_record(self.temp.name, self.identifier, owner_state=lambda _pid: 'dead')
        self.assertEqual(result['status'], 'ambiguous')
        record = json.loads(self.journal.path.read_text(encoding='utf-8'))
        record['pending'] = None
        self.journal.path.write_text(json.dumps(record), encoding='utf-8')
        self.assertEqual(inspect_record(self.temp.name, self.identifier, owner_state=lambda _pid: 'unknown')['status'], 'ambiguous')
        self.assertEqual(inspect_record(self.temp.name, self.identifier, owner_state=lambda _pid: 'alive')['status'], 'busy')

    def test_even_confirmed_stale_record_does_not_authorize_deletion(self):
        name = 'PortfolioManager.A.' + self.identifier + '.model'
        self.journal.update(pending=None, created=[name])
        self.journal._lock.close()
        before = self.journal.path.read_bytes()
        result = inspect_record(self.temp.name, self.identifier, owner_state=lambda _pid: 'dead')
        self.assertEqual(result['status'], 'requires_proof')
        self.assertEqual(self.journal.path.read_bytes(), before)

    def test_foreign_profile_name_is_rejected(self):
        self.journal._lock.close()
        record = json.loads(self.journal.path.read_text(encoding='utf-8'))
        record['created'] = ['unrelated-profile']
        self.journal.path.write_text(json.dumps(record), encoding='utf-8')
        self.assertEqual(inspect_record(self.temp.name, self.identifier, owner_state=lambda _pid: 'dead')['status'], 'ambiguous')
