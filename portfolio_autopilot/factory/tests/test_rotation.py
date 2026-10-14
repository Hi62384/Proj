from pathlib import Path
import tempfile
import unittest

from portfolio_autopilot.factory.catalog import catalog
from portfolio_autopilot.factory.config import SetupError
from portfolio_autopilot.factory.rotation import choose_rotation, create_rotation
from portfolio_autopilot.factory.ledger import summary

class RotationTests(unittest.TestCase):
    def test_rotation_diverse_real_atlas(self):
        rows=catalog()
        a=choose_rotation(rows,rotation_number=1,limit=6)
        b=choose_rotation(rows,rotation_number=2,limit=6)
        self.assertGreaterEqual(len(a),2)
        self.assertNotEqual({r['id'] for r in a},{r['id'] for r in b})
        for selected in (a,b):
            self.assertEqual(len({r['niche'] for r in selected}),len(selected))
            self.assertTrue(all(r['legal_class']=='standard' for r in selected))
            from collections import Counter
            self.assertLessEqual(max(Counter(x['revenue_mode'] for x in selected).values()),2)
    def test_rotation_only_generates_drafts_and_idempotent_tasks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a=create_rotation(root,rotation_number=25,limit=6)
            b=create_rotation(root,rotation_number=25,limit=6)
            self.assertEqual(a['external_actions'],0)
            self.assertGreater(a['candidate_count'],1)
            self.assertTrue(all(r['state']=='existing_draft_preserved' for r in b['candidates']))
            self.assertGreater(summary(root)['pending_tasks'],0)
    def test_invalid_parameters(self):
        with self.assertRaises(SetupError):choose_rotation([],rotation_number=-1)
        with self.assertRaises(SetupError):choose_rotation([],rotation_number=0,limit=99)
