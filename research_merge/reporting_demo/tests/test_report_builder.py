import csv
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal
from report_builder import (read_records, summarize, safe_csv_text, render_html,
                            ValidationError, parse_money, write_report)

HEADER="date,order_id,channel,revenue,cost\n"
GOOD=HEADER+"2026-10-01,A1,Direct,10.10,2.20\n2026-10-02,A2,Referral,20.20,3.30\n"

class ReportingTests(unittest.TestCase):
    def data(self,text):
        folder=tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        p=Path(folder.name)/"input.csv"; p.write_text(text,encoding="utf-8")
        return p
    def test_decimal_totals(self):
        s=summarize(read_records(self.data(GOOD)))
        self.assertEqual(s["revenue"],"30.30")
        self.assertEqual(s["input_cost"],"5.50")
        self.assertEqual(s["revenue_minus_input_cost"],"24.80")
        self.assertEqual(s["record_count"],2)
    def test_duplicate_rejected(self):
        with self.assertRaises(ValidationError):
            read_records(self.data(GOOD.replace("A2","A1")))
    def test_missing_header_rejected(self):
        with self.assertRaises(ValidationError): read_records(self.data("date,revenue\n2026-10-01,2"))
    def test_bad_money_rejected(self):
        for v in ["NaN","Infinity","1,000","$10","1.001","1e3"]:
            with self.subTest(v=v), self.assertRaises(ValidationError): parse_money(v,2,"revenue")
    def test_signed_adjustment(self):
        self.assertEqual(parse_money("-1.25",2,"revenue"),Decimal("-1.25"))
    def test_invalid_date_rejected(self):
        with self.assertRaises(ValidationError): read_records(self.data(GOOD.replace("2026-10-01","2026-02-30")))
    def test_row_limit(self):
        with self.assertRaises(ValidationError): read_records(self.data(GOOD),max_rows=1)
    def test_no_rows(self):
        with self.assertRaises(ValidationError): read_records(self.data(HEADER))
    def test_html_escaping(self):
        s=summarize(read_records(self.data(GOOD.replace("Direct","<script>alert(1)</script>"))))
        html=render_html(s,"<script>bad</script>","CAD")
        self.assertNotIn("<script>",html)
        self.assertIn("&lt;script&gt;",html)
    def test_csv_formula_guard(self):
        for value in ["=1+1","  @SUM(A1:A2)","+cmd","-cmd","\tbad"]:
            self.assertTrue(safe_csv_text(value).startswith("'"))
        self.assertEqual(safe_csv_text("Direct"),"Direct")
    def test_overwrite_guard(self):
        s=summarize(read_records(self.data(GOOD)))
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"out"
            write_report(s,target,"Test","CAD")
            with self.assertRaises(ValidationError): write_report(s,target,"Test","CAD")
            write_report(s,target,"Test","CAD",overwrite=True)
    def test_unknown_currency_label_rejected(self):
        s=summarize(read_records(self.data(GOOD)))
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValidationError): write_report(s,Path(td),"Test","<bad>")
    def test_duplicate_header_rejected(self):
        with self.assertRaises(ValidationError):
            read_records(self.data("date,order_id,channel,revenue,cost,cost\n2026-10-01,A1,D,1,2,3\n"))
    def test_ragged_row_rejected(self):
        with self.assertRaises(ValidationError): read_records(self.data(GOOD+"2026-10-03,A3,X,1\n"))

if __name__=="__main__": unittest.main()
