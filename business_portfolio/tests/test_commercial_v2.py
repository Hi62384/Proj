"""V2 planning integrity and arithmetic tests, not customer workflow tests."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import re
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import build_browser as b
import commercial_checks as c

class CommercialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=b.load_portfolio(ROOT);cls.by={x['id']:x for x in cls.data['records']}
    def test_all_original_and_new_ids(self):
        self.assertEqual(len(self.data['records']),139)
        self.assertTrue({f'AWA-{i:03d}' for i in range(1,127)}<=set(self.by))
    def test_budget_all_records(self):
        for r in self.data['records']:
            c.validate_record(r)
            self.assertEqual(r['owner_budget']['preferred_upfront'],0)
            self.assertEqual(r['owner_budget']['planned_upfront'],0)
            self.assertEqual(r['owner_budget']['authorized_spend'],0)
            self.assertFalse(r['marketing_execution_authorized'])
    def test_over_budget_rejected(self):
        r=copy.deepcopy(self.by['AWA-001']);r['owner_budget']['hard_ceiling']=101
        with self.assertRaises(c.CommercialError):c.validate_record(r)
    def test_unknown_cost_not_zero(self):
        for v in [None,float('nan'),float('inf'),True,-1]:
            with self.assertRaises(c.CommercialError):c.number(v)
    def test_optional_envelope_total_checked(self):
        r=copy.deepcopy(self.by['AWA-001']);r['owner_budget']['optional_all_in_envelope']['advertising']=99
        with self.assertRaises(c.CommercialError):c.validate_record(r)
    def test_spend_needs_approval(self):
        r=json.loads((ROOT/'templates/spend-request.example.json').read_text())
        with self.assertRaises(c.CommercialError):c.validate_spend_request(r)
    def test_committed_tax_fx_count(self):
        r=dict(currency='CAD',approval_ref='synthetic-only',costs_verified=True,auto_renewal=False,already_spent=30,existing_commitments=20,proposed_cost=40,tax_and_fx=5,new_noncancelable_commitments=10,approved_total=100)
        with self.assertRaises(c.CommercialError):c.validate_spend_request(r)
        r['new_noncancelable_commitments']=0
        self.assertEqual(c.validate_spend_request(r),Decimal(95))
    def test_explicit_zero_real_sales_not_fabricated(self):
        for r in self.data['records']:
            if r['origin']=='revised_candidate':
                self.assertEqual(r['verified_paid_pilots'],0);self.assertIsNone(r['actual_revenue']);self.assertEqual(r['commercial_validation'],'unvalidated')
    def test_all_original_states_preserved(self):
        audit=json.loads((ROOT/'research/V2_PROJECT_AUDIT.json').read_text())
        for entry in audit:
            r=self.by[entry['id']]
            if entry['id']=='SYS-001' and r.get('local_integration'):
                self.assertEqual(entry['preserved_work_state'],r['local_integration']['imported_work_state'])
                self.assertIn(r['work_state'],['blocked','completed'])
                self.assertEqual(r['local_integration']['evidence'],'INTEGRATION_STATUS.md')
            else:
                self.assertEqual(entry['preserved_work_state'],r['work_state'])
            self.assertEqual(entry['preserved_commercial_validation'],r['commercial_validation'])
            completed=len(re.findall(r'^.*\[x\].*$',r['body'],re.M))
            if entry['id']=='SYS-001' and r.get('local_integration'):
                self.assertGreaterEqual(completed,entry['completed_checkbox_count'])
            else:
                self.assertEqual(completed,entry['completed_checkbox_count'])
    def test_sources_distinguish_new_and_inherited(self):
        self.assertEqual(len(self.data['sources']),108)
        self.assertEqual(sum(s['v2_review_status']=='reviewed_for_this_revision' for s in self.data['sources']),41)
    def test_product_ad_model(self):
        # 5% platform + assumed 3% processor, 5% refund reserve, fixed fee .30 and support 2.50.
        self.assertEqual(c.contribution(15,.08,.05,2.5,.30),Decimal('10.25'))
        self.assertEqual(c.contribution(9,.08,.05,2.5,.30),Decimal('5.03'))
    def test_quote_floor(self):
        self.assertEqual(c.round_money(c.quote_floor(8,30,25,.20,.05)),Decimal('353.33'))
        with self.assertRaises(c.CommercialError):c.quote_floor(8,30,25,.9,.2)
    def test_only_one_explicit_cost_followon(self):
        self.assertEqual(self.by['AWA-126']['parent_project'],'AWA-095')
        self.assertEqual(self.by['AWA-126']['launch_gate'],'prior_paid_client_required')
    def test_deferred_software_not_claimed_budget_ready(self):
        for n in range(115,121):
            r=self.by[f'AWA-{n:03d}'];self.assertEqual(r['launch_gate'],'production_deferred')
            self.assertEqual(r['owner_budget']['budget_fit'],'discovery_only_not_production')
    def test_components_not_independent_budgets(self):
        for r in self.data['records']:
            if r['record_type']=='bundled_component':
                self.assertEqual(r['owner_budget']['optional_total_ceiling'],0)
                self.assertEqual(r['marketing_lane'],'parent_offer_only')
    def test_service_specific_sales_proof(self):
        for r in self.data['records']:
            if r['record_type']=='standalone_service':
                for part in ['Landing/profile headline draft','Specific discovery phrase','Distinct failure test','Advertising decision','Response draft for an invited']:
                    self.assertIn(part,r['body'],r['id'])
                self.assertTrue(r['offer_price_cad_hypothesis'])
    def test_historical_prices_not_current_usd(self):
        for r in self.data['records']:
            if r['id'].startswith('AWA-'):self.assertIsNone(r['offer_price_usd'])
    def test_nonzero_permission_needs_reference(self):
        r=copy.deepcopy(self.by['AWA-001']);r['owner_budget']['authorized_spend']=10
        with self.assertRaises(c.CommercialError):c.validate_record(r)
    def test_hypothetical_fees_invalid(self):
        with self.assertRaises(c.CommercialError):c.contribution(10,.5,.5)
        with self.assertRaises(c.CommercialError):c.contribution(-10,.1,.1)
    def test_positive_marketing_permission_needs_reference(self):
        r=copy.deepcopy(self.by['AWA-001']);r['marketing_execution_authorized']=True
        with self.assertRaises(c.CommercialError):c.validate_record(r)
if __name__=='__main__':unittest.main()
