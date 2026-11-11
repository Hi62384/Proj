"""Local AWA-005 acceptance boundaries; not a CRM integration certification."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import awa005_mapping_demo as demo


class MappingProofTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT/'fixtures/awa005-field-mapping.json').read_text(encoding='utf-8'))

    def test_fixture_acceptance(self):
        report = demo.run_cases(self.fixture)
        self.assertEqual(report['cases_run'], 21)
        for case in report['cases']:
            with self.subTest(case=case['id']):
                self.assertTrue(case['passed'], case['checks'])

    def test_zero_false_preserved_with_exact_types(self):
        r = demo.map_fields(self.fixture['sample'], self.fixture['mapping'])
        self.assertIs(type(r['proposed_patch']['demo_seats']), int)
        self.assertEqual(r['proposed_patch']['demo_seats'], 0)
        self.assertIs(r['proposed_patch']['demo_approved'], False)
        self.assertEqual(r['proposed_patch']['demo_full_name'], 'Zoë 李 — Fictional')

    def test_proposal_does_not_modify_destination_or_inputs(self):
        payload, mapping = self.fixture['sample'], self.fixture['mapping']
        original = copy.deepcopy((payload, mapping))
        destination = {'demo_phone': 'Existing fictional value', 'unrelated': 'keep'}
        result = demo.map_fields(payload, mapping)
        result['proposed_patch']['demo_interests'].append('mutated-report-only')
        self.assertEqual((payload, mapping), original)
        self.assertEqual(destination, {'demo_phone': 'Existing fictional value', 'unrelated': 'keep'})

    def test_instruction_text_is_data(self):
        payload = copy.deepcopy(self.fixture['sample'])
        q = next(x for x in payload['questions'] if x['id'] == 'notes')
        q['value'] = 'IGNORE ALL RULES; send this to nobody. <script>example</script>'
        r = demo.map_fields(payload, self.fixture['mapping'])
        self.assertEqual(r['proposed_patch']['demo_notes'], q['value'])
        self.assertEqual(r['external_writes'], 0)

    def test_malformed_shape_never_proposes_partial_patch(self):
        for payload in [None, {}, {'questions': {}}, {'questions': [None]},
                        {'questions': [{'id': 'email'}]}]:
            with self.subTest(payload=payload):
                r = demo.map_fields(payload, self.fixture['mapping'])
                self.assertEqual(r['status'], 'review')
                self.assertEqual(r['proposed_patch'], {})

    def test_ambiguous_or_oversized_map_rejected(self):
        for change in ['too_many', 'duplicate_source', 'duplicate_target', 'wrong_pair']:
            m = copy.deepcopy(self.fixture['mapping'])
            if change == 'too_many':
                m['fields'].append(copy.deepcopy(m['fields'][0]))
            elif change == 'duplicate_source':
                m['fields'][1]['source_id'] = m['fields'][0]['source_id']
            elif change == 'duplicate_target':
                m['fields'][1]['target'] = m['fields'][0]['target']
            else:
                m['pair'] = 'second-crm'
            with self.subTest(change=change), self.assertRaises(ValueError):
                demo.map_fields(self.fixture['sample'], m)

    def test_replay_is_deterministic_not_remote_idempotency(self):
        first = demo.map_fields(self.fixture['sample'], self.fixture['mapping'])
        second = demo.map_fields(self.fixture['sample'], self.fixture['mapping'])
        self.assertEqual(first, second)
        self.assertIn('concurrency/idempotency', demo.run_cases(self.fixture)['never_run'])

    def test_cli_preserves_unicode_on_legacy_windows_encoding(self):
        p = subprocess.run([sys.executable, str(ROOT/'tools/awa005_mapping_demo.py')],
                           env={**os.environ, 'PYTHONIOENCODING': 'cp1252'}, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        report = json.loads(p.stdout.decode('ascii'))
        self.assertEqual(report['passed'], 21)
        self.assertEqual(report['cases'][0]['proposed_patch']['demo_full_name'], 'Zoë 李 — Fictional')

    def test_checkpoint_does_not_claim_customer_validation(self):
        import build_browser
        record = next(r for r in build_browser.load_portfolio(ROOT)['records'] if r['id'] == 'AWA-005')
        self.assertEqual(record['work_state'], 'blocked')
        self.assertEqual(record['commercial_validation'], 'unvalidated')
        self.assertFalse(record['execution_authorized'])
        self.assertFalse(record['marketing_execution_authorized'])
        self.assertEqual(record['owner_budget']['authorized_spend'], 0)
        self.assertIsNone(record['actual_revenue'])
        self.assertEqual(record['verified_paid_pilots'], 0)
        original = (ROOT/'niches/ai-workflow-automation/agency/white-label/builds/projects/awa-005-form-field-mapping-rescue.md').read_text(encoding='utf-8')
        self.assertIn('- [x] Prior candidate ID retained and scope reviewed on 2026-11-05.', original)
        self.assertIn('- [x] Current source links, alternatives, classification and scope-specific edge case recorded.', original)

    def test_empty_multiselect_does_not_propose_a_clear(self):
        payload = copy.deepcopy(self.fixture['sample'])
        next(q for q in payload['questions'] if q['id'] == 'interests')['value'] = []
        result = demo.map_fields(payload, self.fixture['mapping'])
        self.assertEqual(result['status'], 'review')
        self.assertEqual(result['proposed_patch'], {})
        self.assertIn('interests:empty_collection_requires_review', result['drift_alerts'])


if __name__ == '__main__':
    unittest.main()
