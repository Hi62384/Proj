"""Read-only product audit. Native conversions use separate review copies."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
INV=Path(os.environ['LOCALAPPDATA'])/'CodexDesktopAssistant/projects/811d41672eed4b009822b111e0411a30/artifacts/inventory-test'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def workbook(path):
    with ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets={}
        for s in wb.find('s:sheets',NS):
            target=rels[s.attrib['{'+NS['r']+'}id']]
            member=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            tree=ET.fromstring(z.read(member));cells={}
            for c in tree.findall('.//s:sheetData/s:row/s:c',NS):
                val=c.findtext('s:v',default='',namespaces=NS);typ=c.attrib.get('t','')
                if typ=='s':val=strings[int(val)]
                elif typ=='inlineStr':val=''.join(c.find('s:is',NS).itertext())
                f=c.findtext('s:f',namespaces=NS)
                if val or f:cells[c.attrib['r']]={'value':val,'formula':f,'type':typ}
            sheets[s.attrib['name']]={'cells':cells,'errors':{k:v for k,v in cells.items() if v['type']=='e'},'print_area':tree.find('s:pageSetup',NS).attrib if tree.find('s:pageSetup',NS) is not None else {}}
        return {'sha256':digest(path),'sheets':sheets,'macros':any('vbaproject' in n.lower() for n in z.namelist()),'external_links':[n for n in z.namelist() if 'externalLinks/' in n]}

def run():
    qa=ROOT/'qa';qa.mkdir(exist_ok=True)
    sources={'cleaning_blank':REPO/'products/cleaning-pricing-calculator/customer/Cleaning_Pricing_Calculator.xlsx','cleaning_demo':REPO/'products/cleaning-pricing-calculator/examples/Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx','inventory':INV/'customer/product.xlsx'}
    report={'workbooks':{},'archives':{},'native':[]}
    for key,path in sources.items():report['workbooks'][key]=workbook(path)
    for key,path in {'cleaning':REPO/'products/cleaning-pricing-calculator/release/Cleaning_Pricing_Toolkit_v1.0_CUSTOMER.zip','inventory':INV/'delivery.zip'}.items():
        with ZipFile(path) as z:report['archives'][key]={'bytes':path.stat().st_size,'sha256':digest(path),'crc_failure':z.testzip(),'files':z.namelist()}
    with ZipFile(INV/'customer/Instructions.docx') as z:
        t=ET.fromstring(z.read('word/document.xml'));report['inventory_instructions']=[''.join(p.itertext()) for p in t.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')]
    (ROOT/'file-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'archives':report['archives'],'workbooks':{k:{'sheets':list(v['sheets']),'errors':{s:len(x['errors']) for s,x in v['sheets'].items()},'macros':v['macros'],'external_links':v['external_links']} for k,v in report['workbooks'].items()},'instructions':report['inventory_instructions']},indent=2),flush=True)
    native=qa/'recalculated';native.mkdir(exist_ok=True)
    profile=(qa/'lo-profile').as_uri()
    exe=Path('C:/Program Files/LibreOffice/program/soffice.com')
    for key,path in sources.items():
        copy=qa/(key+'.xlsx');shutil.copyfile(path,copy)
        result=subprocess.run([str(exe),'-env:UserInstallation='+profile,'--headless','--convert-to','xlsx','--outdir',str(native),str(copy)],capture_output=True,text=True,timeout=90)
        out=native/copy.name
        item={'workbook':key,'returncode':result.returncode,'stdout':result.stdout.strip(),'stderr':result.stderr.strip(),'created':out.exists()}
        if out.exists():
            check=workbook(out);item['errors']={s:x['errors'] for s,x in check['sheets'].items()};report['workbooks'][key]['native_recalculated']=check
        report['native'].append(item);print(json.dumps(item),flush=True)
    report['source_hashes_unchanged']=all(digest(p)==report['workbooks'][k]['sha256'] for k,p in sources.items())
    (ROOT/'file-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if __name__=='__main__':run()
