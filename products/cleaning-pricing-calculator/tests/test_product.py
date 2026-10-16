"""Independent standard-library audit of delivered XLSX formulas and seller ZIP.

No artifact_tool/openpyxl dependency; no network or customer data.
These tests do not substitute for opening the workbook in native Excel.
"""
import csv
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
import json
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import package_release as pkg

NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
TWO=Decimal('0.01')

def D(x):return Decimal(str(x))
def money(x):return x.quantize(TWO,rounding=ROUND_HALF_UP)
def roundup_step(value,step):return (value/step).to_integral_value(rounding=ROUND_CEILING)*step

def independent_quote(service_hours,base_supplies,crew,on_site_override,travel_hours,km,extra_supplies,extra_overhead,discount,tax_rate=0,
                     hourly=25,mileage=.55,overhead=14,contingency=.08,margin=.30,fee=.03,minimum=100,step=5):
    """External reference math; no spreadsheet/evaluator or hardcoded quote output."""
    vals=[service_hours,base_supplies,travel_hours,km,extra_supplies,extra_overhead,discount,hourly,mileage,overhead,contingency,margin,fee,minimum,step,tax_rate]
    if any(D(v)<0 for v in vals):raise ValueError('Negative input')
    if int(crew)!=crew or crew<1:raise ValueError('Crew must be positive whole')
    onsite=D(service_hours if on_site_override in (None,'') else on_site_override)
    if onsite<=0:raise ValueError('Onsite hours must be positive')
    if D(margin)+D(fee)>=1 or D(step)<=0:raise ValueError('Invalid pricing assumptions')
    labor=money(D(crew)*(onsite+D(travel_hours))*D(hourly))
    supplies=money(D(base_supplies)+D(extra_supplies))
    car=money(D(km)*D(mileage))
    oh=money(D(overhead)+D(extra_overhead))
    direct=labor+supplies+car+oh
    buffer=money(direct*D(contingency))
    jobcost=money(direct+buffer)
    list_price=max(roundup_step(jobcost/(1-D(margin)-D(fee))+D(discount),D(step)),
                   roundup_step(D(minimum)+D(discount),D(step)))
    pretax=money(list_price-D(discount))
    tax=money(pretax*D(tax_rate))
    fees=money(pretax*D(fee))
    contribution=money(pretax-jobcost-fees)
    return {'labor':labor,'supplies':supplies,'mileage':car,'overhead':oh,'subtotal':direct,'contingency':buffer,
            'job_cost':jobcost,'list':list_price,'discount':D(discount),'pre_tax':pretax,'tax':tax,
            'total':pretax+tax,'fees':fees,'contribution':contribution,'margin':contribution/pretax}

class WorkbookReader:
    def __init__(self,path):
        self.path=path
        with ZipFile(path) as z:
            self.members=z.namelist()
            self.workbook=ET.fromstring(z.read('xl/workbook.xml'))
            self.names=[x.attrib['name'] for x in self.workbook.findall('x:sheets/x:sheet',NS)]
            self.sheets={name:ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml'))
                         for i,name in enumerate(self.names,1)}
            self.strings=[]
            if 'xl/sharedStrings.xml' in self.members:
                root=ET.fromstring(z.read('xl/sharedStrings.xml'))
                for elem in root.findall('x:si',NS):
                    self.strings.append(''.join((p.text or '') for p in elem.findall('.//x:t',NS)))
    def element(self,sheet,ref):
        for cell in self.sheets[sheet].findall('.//x:c',NS):
            if cell.attrib.get('r')==ref:return cell
        return None
    def val(self,sheet,ref):
        cell=self.element(sheet,ref)
        if cell is None:return None
        v=cell.find('x:v',NS)
        if v is None:return None
        if cell.attrib.get('t')=='s':return self.strings[int(v.text)]
        if cell.attrib.get('t')=='str':return v.text or ''
        if cell.attrib.get('t')=='e':return v.text
        return D(v.text)
    def formula(self,sheet,ref):
        c=self.element(sheet,ref)
        f=c.find('x:f',NS) if c is not None else None
        return f.text if f is not None else None

class ModelTests(unittest.TestCase):
    def test_fictional_example_reference(self):
        q=independent_quote(2.5,9,2,3,.25,12,4,0,10)
        self.assertEqual(q['labor'],D('162.50'))
        self.assertEqual(q['subtotal'],D('196.10'))
        self.assertEqual(q['contingency'],D('15.69'))
        self.assertEqual(q['job_cost'],D('211.79'))
        self.assertEqual(q['list'],D('330'))
        self.assertEqual(q['pre_tax'],D('320.00'))
        self.assertEqual(q['fees'],D('9.60'))
        self.assertEqual(q['contribution'],D('98.61'))
    def test_tax_comes_after_price_and_not_into_contribution(self):
        a=independent_quote(2.5,9,2,3,.25,12,4,0,10,tax_rate=0)
        b=independent_quote(2.5,9,2,3,.25,12,4,0,10,tax_rate='.13')
        self.assertEqual(a['pre_tax'],b['pre_tax']);self.assertEqual(a['contribution'],b['contribution'])
        self.assertEqual(b['tax'],D('41.60'));self.assertEqual(b['total'],D('361.60'))
    def test_minimum_quote_survives_discount(self):
        q=independent_quote(1,0,1,1,0,0,0,0,25,minimum=160,step=5)
        self.assertEqual(q['list'],D('185'));self.assertEqual(q['pre_tax'],D('160.00'))
    def test_incorrect_margin_math_rejected(self):
        with self.assertRaises(ValueError):independent_quote(1,0,1,1,0,0,0,0,0,margin='.99',fee='.03')
        with self.assertRaises(ValueError):independent_quote(1,0,1,1,0,0,0,0,0,step=0)
    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):independent_quote(1,0,0,1,0,0,0,0,0)
        with self.assertRaises(ValueError):independent_quote(1,0,2,0,0,0,0,0,0)
        with self.assertRaises(ValueError):independent_quote(1,0,1,1,0,0,-1,0,0)
    def test_more_crewmembers_cost_more(self):
        one=independent_quote(2,6,1,None,0,10,0,0,0)
        three=independent_quote(2,6,3,None,0,10,0,0,0)
        self.assertTrue(three['job_cost']>one['job_cost'])
        self.assertGreaterEqual(three['margin'],D('.30'))
    def test_discount_compensation_preserves_margin(self):
        a=independent_quote(2.5,9,2,3,.25,12,4,0,0)
        b=independent_quote(2.5,9,2,3,.25,12,4,0,35)
        self.assertEqual(a['job_cost'],b['job_cost'])
        self.assertTrue(b['pre_tax']>=a['pre_tax'])
        self.assertGreaterEqual(b['margin'],D('.30'))

class SpreadsheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blank=WorkbookReader(ROOT/'customer'/'Cleaning_Pricing_Calculator.xlsx')
        cls.demo=WorkbookReader(ROOT/'examples'/'Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx')
    def test_eight_worksheets(self):
        expect=['READ ME','OVERVIEW','QUICK QUOTE','CLIENT QUOTE','JOB SCENARIOS','JOB LOG','SERVICES','SETTINGS']
        self.assertEqual(self.blank.names,expect)
        self.assertEqual(self.demo.names,expect)
    def test_workbooks_have_no_macro_or_external_link(self):
        for wb in (self.blank,self.demo):
            self.assertFalse(any('vbaProject' in n or n.startswith('xl/externalLinks') for n in wb.members))
            with ZipFile(wb.path) as z:
                self.assertIsNone(z.testzip())
                self.assertFalse(any(v.attrib.get('t')=='e'
                    for sheet in wb.sheets.values() for v in sheet.findall('.//x:c',NS)))
    def test_demo_quote_cached_results_agree_with_independent_model(self):
        q=independent_quote(2.5,9,2,3,.25,12,4,0,10)
        ref_map={'F12':'labor','F13':'supplies','F14':'mileage','F15':'overhead','F16':'subtotal',
                 'F17':'contingency','F18':'job_cost','F19':'list','F20':'discount',
                 'F21':'pre_tax','F22':'tax','F23':'total','F24':'fees','F25':'contribution','F26':'margin'}
        for cell,key in ref_map.items():
            with self.subTest(cell=cell):
                actual=self.demo.val('QUICK QUOTE',cell)
                self.assertIsNotNone(actual,cell)
                self.assertLess(abs(actual-q[key]),D('0.0000001'))
        self.assertEqual(self.demo.val('QUICK QUOTE','F27'),'READY TO REVIEW')
    def test_scenarios_match_ref_and_demonstration_data(self):
        with open(ROOT/'examples'/'FICTIONAL_SAMPLE_DATA.csv',newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
        services={n:(hours,supplies) for n,hours,supplies,_ in [
             ('Standard home cleaning',2.5,9.00,''),('Deep home cleaning',4.0,17.00,''),
             ('Move-in / move-out',5.0,22.00,''),('Small office cleaning',2.0,10.00,''),
             ('Apartment turnover',3.0,12.00,''),('Recurring maintenance',2.0,8.00,''),
             ('Interior window cleaning',2.0,6.00,'')]}
        for i,row in enumerate(rows,10):
            hrs,sups=services[row['service']]
            expected=independent_quote(hrs,sups,int(row['crew']),row['on_site_hours_per_employee'] or None,
                             row['paid_travel_hours_per_employee'],row['roundtrip_km'],row['extra_supplies_cad'],
                             row['extra_overhead_cad'],row['discount_cad'])
            self.assertEqual(self.demo.val('JOB SCENARIOS',f'A{i}'),row['job_id'])
            self.assertEqual(self.demo.val('JOB SCENARIOS',f'Q{i}'),'READY')
            for col,key in [('K','job_cost'),('L','list'),('M','pre_tax'),('N','total'),('O','contribution')]:
                with self.subTest(row=i,col=col):
                    self.assertLess(abs(self.demo.val('JOB SCENARIOS',f'{col}{i}')-expected[key]),D('0.0000001'))
        self.assertEqual(self.demo.val('OVERVIEW','B9'),D('6'))
        self.assertEqual(self.demo.val('OVERVIEW','B15'),D('3'))
    def test_blank_version_requires_assumptions_review(self):
        self.assertEqual(self.blank.val('SETTINGS','B23'),'REVIEW BEFORE USE')
        self.assertEqual(self.blank.val('QUICK QUOTE','F27'),'SELECT SERVICE')
        self.assertEqual(self.blank.val('SETTINGS','B18'),D('0'))
        self.assertEqual(self.blank.val('SETTINGS','B20'),'YOUR BUSINESS NAME')
        self.assertNotEqual(self.blank.val('QUICK QUOTE','B10'),'DEMO-001')
    def test_core_estimate_cells_are_excel_formulas(self):
        for c in ['F11','F12','F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24','F25','F26','F27']:
            self.assertIsNotNone(self.blank.formula('QUICK QUOTE',c),c)
        self.assertIn('ROUNDUP',self.blank.formula('QUICK QUOTE','F19'))
        self.assertIn('VLOOKUP',self.blank.formula('QUICK QUOTE','F11'))
        self.assertIn('SETTINGS!',self.blank.formula('QUICK QUOTE','F22'))
        self.assertIn('COUNTA',self.blank.formula('OVERVIEW','B15'))
        self.assertTrue(all(self.blank.formula('JOB SCENARIOS',f'K{r}') for r in range(10,35)))
        self.assertTrue(all(self.blank.formula('JOB LOG',f'K{r}') for r in range(10,35)))
    def test_client_quote_does_not_show_internal_cost_components(self):
        s=self.demo.sheets['CLIENT QUOTE']
        displayed=[v.text or '' for v in s.findall('.//x:v',NS)]
        xml=ET.tostring(s,encoding='unicode')
        self.assertNotIn('QUICK QUOTE\'!F18',xml)
        self.assertNotIn('QUICK QUOTE\'!F25',xml)
        self.assertIn('CUSTOMER QUOTE',xml)
    def test_no_personal_information_embedded(self):
        patterns=['strathearn','ghafaryan','james bennett','@gmail.com','@yahoo.com']
        for w in (self.blank,self.demo):
            with ZipFile(w.path) as z:
                for name in z.namelist():
                    if name.endswith('.xml'):
                        lower=z.read(name).lower()
                        for term in patterns:
                            self.assertNotIn(term.encode(),lower,(w.path.name,name,term))
    def test_customer_quote_amounts_and_settings_visible_in_example(self):
        self.assertEqual(self.demo.val('CLIENT QUOTE','E22'),D('320'))
        self.assertEqual(self.demo.val('CLIENT QUOTE','C11'),'FICTIONAL CUSTOMER')
        self.assertEqual(self.demo.val('SETTINGS','B23'),'READY')

class PackagingTests(unittest.TestCase):
    def test_source_artifacts_present(self):
        self.assertTrue((ROOT/'customer'/'Quick_Start_Guide.pdf').read_bytes().startswith(b'%PDF-'))
        for name in pkg.SOURCES:self.assertTrue(pkg.SOURCES[name].is_file())
    def test_release_zip_reproducibly_matches_manifest(self):
        self.assertTrue(pkg.check())
    def test_customer_bundle_contains_no_seller_source(self):
        with ZipFile(ROOT/'release'/pkg.ZIP_NAME) as z:
            self.assertEqual(sorted(z.namelist()),sorted(pkg.SOURCES))
            self.assertFalse(any(x.endswith('.py') or 'marketing/' in x for x in z.namelist()))
            self.assertNotIn(b'@gmail.com',z.read('START_HERE.txt').lower())
    def test_previews_are_real_png_at_expected_size(self):
        for name in ['01_product_cover.png','02_quote_builder.png','03_customer_quote.png','04_scenario_planner.png']:
            p=ROOT/'marketing'/'previews'/name
            data=p.read_bytes()
            self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual((int.from_bytes(data[16:20],'big'),int.from_bytes(data[20:24],'big')),(1600,900))
    def test_sales_listing_is_draft_and_honest(self):
        txt=(ROOT/'marketing'/'PAYHIP_LISTING_DRAFT.md').read_text(encoding='utf8').lower()
        for term in ['not published','fictional','not guaranteed','cad $29','no macros','privacy']:
            self.assertIn(term,txt)
        self.assertIn('no payments', (ROOT/'README.md').read_text(encoding='utf8').lower())

if __name__=='__main__':unittest.main()
