"""Disposable native recalculation fixtures; never alter customer originals."""
import importlib.util,json,math,subprocess
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from review_files import ROOT,REPO,INV,NS,workbook

qa=ROOT/'qa';cases=qa/'cases';cases.mkdir(exist_ok=True)
out=qa/'case-results-recalculated';out.mkdir(exist_ok=True)
def fixture(src,name,member,changes):
    target=cases/(name+'.xlsx')
    with ZipFile(src) as z,ZipFile(target,'w') as dest:
        for item in z.infolist():
            data=z.read(item.filename)
            if item.filename==member:
                tree=ET.fromstring(data)
                for cell in tree.findall('.//s:c',NS):
                    if cell.attrib['r'] in changes:
                        cell.attrib.pop('t',None)
                        for child in list(cell):cell.remove(child)
                        val=changes[cell.attrib['r']]
                        if val is not None:ET.SubElement(cell,'{'+NS['s']+'}v').text=str(val)
                data=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
            if item.filename.startswith('xl/worksheets/') and item.filename.endswith('.xml'):
                tree=ET.fromstring(data)
                for cell in tree.findall('.//s:c',NS):
                    if cell.find('s:f',NS) is not None:
                        for val in list(cell.findall('s:v',NS)):cell.remove(val)
                data=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
            if item.filename=='xl/workbook.xml':
                tree=ET.fromstring(data);calc=tree.find('s:calcPr',NS)
                if calc is None:calc=ET.SubElement(tree,'{'+NS['s']+'}calcPr')
                calc.attrib.update(calcMode='auto',fullCalcOnLoad='1',forceFullCalc='1')
                data=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
            dest.writestr(item,data)
    return target

inventory_cases={'zero':([0,0,0,0],[0,0]),'threshold':([12,7,30,114],[114,0]),'overstock':([12,7,30,200],[114,0]),'lead_zero':([12,0,30,0],[30,30]),'fractional':([2.5,3,1,2],[8.5,6.5]),'blank':([None,None,None,None],[0,0])}
paths=[]
for name,(inputs,expected) in inventory_cases.items():paths.append(fixture(INV/'customer/product.xlsx','inventory_'+name,'xl/worksheets/sheet1.xml',dict(zip(['B5','B6','B7','B8'],inputs))))
paths.append(fixture(REPO/'products/cleaning-pricing-calculator/examples/Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx','cleaning_hourly_30','xl/worksheets/sheet8.xml',{'B10':30}))
cmd=['C:/Program Files/LibreOffice/program/soffice.com','-env:UserInstallation='+(qa/'lo-profile').as_uri(),'--headless','--convert-to','xlsx','--outdir',str(out),*[str(p) for p in paths]]
result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
assert result.returncode==0,result.stderr
checks=[]
for name,(inputs,expected) in inventory_cases.items():
    book=workbook(out/('inventory_'+name+'.xlsx'));cells=book['sheets']['Calculator']['cells'];actual=[float(cells[c]['value']) for c in ['B10','B11']]
    checks.append({'case':name,'inputs':inputs,'expected':expected,'actual':actual,'pass':actual==expected})
book=workbook(out/'cleaning_hourly_30.xlsx');cells=book['sheets']['QUICK QUOTE']['cells']
spec=importlib.util.spec_from_file_location('product_tests',REPO/'products/cleaning-pricing-calculator/tests/test_product.py');tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
ref=tests.independent_quote(3,10,2,3,.25,12,3,0,10,hourly=30)
actual={c:float(cells[c]['value']) for c in ['F12','F19','F21','F25']}
expected={'F12':float(ref['labor']),'F19':float(ref['list']),'F21':float(ref['pre_tax']),'F25':float(ref['contribution'])}
checks.append({'case':'cleaning_hourly_30','expected':expected,'actual':actual,'pass':all(math.isclose(actual[c],expected[c],abs_tol=.000001) for c in expected)})
audit=json.loads((ROOT/'file-audit.json').read_text());differences=[]
for key,entry in audit['workbooks'].items():
    for sheet,info in entry['sheets'].items():
        native=entry['native_recalculated']['sheets'][sheet]['cells']
        for cell,value in info['cells'].items():
            if not value['formula']:continue
            a,b=value['value'],native.get(cell,{}).get('value','')
            try:equal=math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-8)
            except ValueError:equal=a==b
            if not equal:differences.append({'workbook':key,'sheet':sheet,'cell':cell,'before':a,'after':b})
report={'engine':'LibreOffice Calc','cases':checks,'baseline_formula_differences_outside_tolerance':differences,'all_pass':all(x['pass'] for x in checks) and not differences}
(ROOT/'native-case-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2));assert report['all_pass']
