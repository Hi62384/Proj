import csv
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from portfolio_autopilot.cli import (
    load_catalog, shortlist, task_packet, snapshot_html, record_event,
    summarize_ledger, parse_money, read_statuses, save_statuses, main
)


class TestAutopilot(unittest.TestCase):
    def sample(self):
        return [
            dict(id="EXP-1-01", niche="HVAC", name="Audit", revenue_mode="F", cross_niche_score="90",
                 legal_class="standard", first_possible_sale_days_min="2", first_possible_sale_days_max="14", evidence_grade="H0"),
            dict(id="EXP-1-02", niche="HVAC", name="Toolkit", revenue_mode="D", cross_niche_score="88",
                 legal_class="standard", first_possible_sale_days_min="7", first_possible_sale_days_max="20", evidence_grade="H0"),
            dict(id="EXP-2-01", niche="Cafe", name="Alerts", revenue_mode="R", cross_niche_score="85",
                 legal_class="standard", first_possible_sale_days_min="5", first_possible_sale_days_max="30", evidence_grade="H0"),
            dict(id="EXP-3-01", niche="Healthcare", name="Patient docs", revenue_mode="F", cross_niche_score="97",
                 legal_class="regulated", first_possible_sale_days_min="2", first_possible_sale_days_max="10", evidence_grade="H0"),
            dict(id="EXP-4-01", niche="Ecommerce", name="Mapper", revenue_mode="I", cross_niche_score="84",
                 legal_class="standard", first_possible_sale_days_min="10", first_possible_sale_days_max="30", evidence_grade="H0"),
            dict(id="EXP-5-01", niche="Manufacturing", name="Workbook", revenue_mode="D", cross_niche_score="83",
                 legal_class="standard", first_possible_sale_days_min="8", first_possible_sale_days_max="30", evidence_grade="H0"),
        ]

    def test_diverse_shortlist_and_regulated_exclusion(self):
        result = shortlist(self.sample(), limit=5, max_per_mode=2)
        self.assertEqual([x['niche'] for x in result], ["HVAC", "Cafe", "Ecommerce", "Manufacturing"])
        self.assertNotIn("Healthcare", [x['niche'] for x in result])

    def test_include_regulated_is_display_only(self):
        r=shortlist(self.sample(), limit=2, include_regulated=True)
        self.assertEqual(r[0]['niche'], 'Healthcare')

    def test_paused_and_live_not_selected(self):
        r=shortlist(self.sample(), states={'EXP-1-01':{'status':'paused'}, 'EXP-2-01':{'status':'live'}})
        self.assertNotIn('EXP-1-01',[x['id'] for x in r]);self.assertNotIn('EXP-2-01',[x['id'] for x in r])

    def test_packet_warns_and_prohibits_live(self):
        s=task_packet(self.sample()[0]);self.assertIn('NOT VALIDATED',s);self.assertIn('Blocked by default',s)

    def test_snapshot_escapes_titles(self):
        x=self.sample();x[0]['name']='<script>alert(1)</script>'
        out=snapshot_html(x,1296)
        self.assertNotIn('<script>alert(1)</script>',out)
        self.assertIn('&lt;script&gt;',out)

    def test_ledger_dedup_and_math(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for ev in [dict(event_id='a',type='revenue',amount_cad='500',minutes=0),
                       dict(event_id='b',type='fee',amount_cad='20',minutes=0),
                       dict(event_id='c',type='expense',amount_cad='30',minutes=0),
                       dict(event_id='d',type='owner_time',amount_cad='0',minutes=120)]:
                record_event(ev, root)
            out=summarize_ledger(root)
            self.assertEqual(out['operating_profit_cad'],'450')
            self.assertEqual(out['profit_after_imputed_owner_time_cad'],'390.00')
            with self.assertRaisesRegex(ValueError,'Duplicate'):
                record_event(dict(event_id='a',type='revenue',amount_cad='500',minutes=0),root)

    def test_money_validation(self):
        for bad in ['-1','NaN','1.111','Infinity','nope']:
            with self.assertRaises(ValueError):parse_money(bad)
        self.assertEqual(parse_money('0.10'),Decimal('0.10'))

    def test_load_catalog_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'c.csv'
            with p.open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=['id','name','niche','revenue_mode','cross_niche_score','legal_class'])
                w.writeheader();w.writerow({'id':'A','name':'first'});w.writerow({'id':'A','name':'second'})
            with self.assertRaisesRegex(ValueError,'duplicate'):load_catalog(p)

    def test_status_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            save_statuses({'abc':{'status':'paused'}},p)
            self.assertEqual(read_statuses(p)['abc']['status'],'paused')

    def test_main_prevents_unsourced_payment_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a.csv'
            with p.open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=['id','name','niche','revenue_mode','cross_niche_score','legal_class'])
                w.writeheader();w.writerow(dict(id='a',name='A',niche='A',revenue_mode='F',cross_niche_score=90,legal_class='standard'))
            self.assertEqual(main(['--catalog',str(p),'review','a','--status','funded']),2)
            self.assertEqual(main(['--catalog',str(p),'review','a','--status','live','--evidence-ref','receipt']),2)


if __name__ == '__main__':unittest.main()
