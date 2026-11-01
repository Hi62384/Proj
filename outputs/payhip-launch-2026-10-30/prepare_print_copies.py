"""Print-only review copies. Artifact Tool has no print-area/page-setup API.

Patch only the missing native OOXML print feature; preserve every cell, style,
formula and other archive member. Never touch delivered or uploaded originals.
"""
import json,subprocess
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from review_files import ROOT,REPO,NS,workbook,digest
ns=NS['s'];q=lambda name:'{'+ns+'}'+name
copies=ROOT/'print-review-copies';copies.mkdir(exist_ok=True)
records=[]
for relative in ['customer/Cleaning_Pricing_Calculator.xlsx','examples/Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx']:
    src=REPO/'products/cleaning-pricing-calculator'/relative;out=copies/src.name
    before=workbook(src)
    with ZipFile(src) as z,ZipFile(out,'w') as dest:
        for member in z.infolist():
            data=z.read(member.filename)
            if member.filename=='xl/workbook.xml':
                root=ET.fromstring(data);names=root.find(q('definedNames'))
                if names is None:names=ET.SubElement(root,q('definedNames'))
                ET.SubElement(names,q('definedName'),{'name':'_xlnm.Print_Area','localSheetId':'3'}).text="'CLIENT QUOTE'!$A$1:$H$26"
                data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            elif member.filename=='xl/worksheets/sheet4.xml':
                root=ET.fromstring(data)
                settings=root.find(q('sheetPr'))
                if settings is None:settings=ET.Element(q('sheetPr'));root.insert(0,settings)
                ET.SubElement(settings,q('pageSetUpPr'),{'fitToPage':'1'})
                margins=root.find(q('pageMargins'))
                margins.attrib.update(left='0.4',right='0.4',top='0.4',bottom='0.4')
                ET.SubElement(root,q('pageSetup'),{'paperSize':'1','orientation':'landscape','fitToWidth':'1','fitToHeight':'1'})
                data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            dest.writestr(member,data)
    after=workbook(out)
    assert before['sheets']==after['sheets'] or all(before['sheets'][s]['cells']==after['sheets'][s]['cells'] for s in before['sheets'])
    with ZipFile(src) as a,ZipFile(out) as b:
        changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
    assert set(changed)=={'xl/workbook.xml','xl/worksheets/sheet4.xml'},changed
    assert digest(src)==before['sha256']
    records.append({'name':src.name,'source_sha256':before['sha256'],'review_sha256':after['sha256'],'cells_unchanged':True,'changed_members':changed})
(ROOT/'print-copy-results.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
pdf=ROOT/'qa/print-review-pdf';pdf.mkdir(exist_ok=True)
result=subprocess.run(['C:/Program Files/LibreOffice/program/soffice.com','-env:UserInstallation='+(ROOT/'qa/lo-profile').as_uri(),'--headless','--convert-to','pdf','--outdir',str(pdf),*[str(p) for p in copies.glob('*.xlsx')]],capture_output=True,text=True,timeout=90)
assert result.returncode==0,result.stderr
print(json.dumps(records,indent=2))
