"""Native Calc launch checks on disposable copies, with independent Decimal math.

Never modifies customer sources, listings, accounts, or original release archives.
"""
import argparse,hashlib,importlib.util,json,math,subprocess,sys
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('product_reference',BASE/'tests/test_product.py')
ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
Q=lambda tag:'{'+NS['s']+'}'+tag

def fixture(source,target,changes):
    with ZipFile(source) as zin,ZipFile(target,'w') as zout:
        names=ref.WorkbookReader(source).names
        for info in zin.infolist():
            data=zin.read(info.filename)
            if info.filename.startswith('xl/worksheets/sheet') and info.filename.endswith('.xml'):
                index=int(info.filename.rsplit('sheet',1)[1].split('.')[0])-1
                edits=changes.get(names[index],{});tree=ET.fromstring(data)
                cells={c.attrib['r']:c for c in tree.findall('.//s:sheetData/s:row/s:c',NS)}
                for address,value in edits.items():
                    c=cells.get(address)
                    if c is None:
                        rowno=''.join(filter(str.isdigit,address));row=tree.find("s:sheetData/s:row[@r='"+rowno+"']",NS)
                        if row is None:row=ET.SubElement(tree.find('s:sheetData',NS),Q('row'),{'r':rowno})
                        c=ET.SubElement(row,Q('c'),{'r':address})
                    c.attrib.pop('t',None)
                    for child in list(c):c.remove(child)
                    if isinstance(value,str):c.attrib['t']='str'
                    if value is not None:ET.SubElement(c,Q('v')).text=str(value)
                for c in tree.findall('.//s:c',NS):
                    if c.find('s:f',NS) is not None:
                        for v in c.findall('s:v',NS):c.remove(v)
                data=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
            elif info.filename=='xl/workbook.xml':
                tree=ET.fromstring(data);calc=tree.find('s:calcPr',NS)
                if calc is None:calc=ET.SubElement(tree,Q('calcPr'))
                calc.attrib.update(calcMode='auto',fullCalcOnLoad='1',forceFullCalc='1')
                data=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
            zout.writestr(info,data)

def val(book,sheet,cell,changes):return changes.get(sheet,{}).get(cell,book.val(sheet,cell))
def numeric(v):return 0 if v is None or v=='' else float(v)
def quote(book,changes,scenario=None):
    get=lambda s,c:val(book,s,c,changes)
    st=lambda n:numeric(get('SETTINGS','B'+str(n)))
    if scenario:
        r=scenario;v=lambda col:get('JOB SCENARIOS',col+str(r))
        service,crew,hours,travel,km,extra,overhead,discount=v('B'),v('C'),v('D'),v('E'),v('F'),v('G'),v('H'),v('I');tax=st(18)
    else:
        v=lambda n:get('QUICK QUOTE','B'+str(n))
        service,crew,hours,travel,km,extra,overhead,discount=[v(n) for n in range(11,19)];tax=st(18) if v(19) in (None,'') else numeric(v(19))
    row=next(r for r in range(9,16) if get('SERVICES','A'+str(r))==service)
    return ref.independent_quote(numeric(get('SERVICES','B'+str(row))),numeric(get('SERVICES','C'+str(row))),numeric(crew),hours if hours not in (None,'') else None,numeric(travel),numeric(km),numeric(extra),numeric(overhead),numeric(discount),tax_rate=tax,hourly=st(10),mileage=st(11),overhead=st(12),contingency=st(13),margin=st(14),fee=st(15),minimum=st(16),step=st(17))

def run(args):
    sources={'demo':Path(args.demo).resolve(),'blank':Path(args.blank).resolve()}
    books={k:ref.WorkbookReader(v) for k,v in sources.items()}
    root=Path(args.output).resolve();inputs=root/'cases';outputs=root/'recalculated'
    inputs.mkdir(parents=True,exist_ok=True);outputs.mkdir(exist_ok=True)
    fingerprints={k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in sources.items()}
    cases=[]
    def add(name,changes=None,**extra):cases.append({'name':name,'changes':changes or {},'source':'demo',**extra})
    edits=[('labor','SETTINGS','B10',31.75),('mileage','SETTINGS','B11',.82),('base_overhead','SETTINGS','B12',28.5),('contingency','SETTINGS','B13',.17),('margin','SETTINGS','B14',.55),('fees','SETTINGS','B15',.08),('minimum','SETTINGS','B16',600),('rounding','SETTINGS','B17',2.5),('default_tax','SETTINGS','B18',.13),('crew','QUICK QUOTE','B12',3),('hours','QUICK QUOTE','B13',4.75),('travel','QUICK QUOTE','B14',.75),('distance','QUICK QUOTE','B15',80.5),('extra_supplies','QUICK QUOTE','B16',18.6),('extra_overhead','QUICK QUOTE','B17',42.25),('discount','QUICK QUOTE','B18',80),('override_tax','QUICK QUOTE','B19',.07),('service_hours','SERVICES','B9',5.25),('service_supplies','SERVICES','C9',27)]
    for name,sheet,cell,value in edits:add(name,{sheet:{cell:value}})
    add('default_service_hours',{'QUICK QUOTE':{'B13':None}})
    add('zero_tax_override',{'SETTINGS':{'B18':.13},'QUICK QUOTE':{'B19':0}})
    add('zero_optional_costs',{'QUICK QUOTE':{'B14':0,'B15':0,'B16':0,'B17':0,'B18':0}})
    add('blank_optional_costs',{'QUICK QUOTE':{'B14':None,'B15':None,'B16':None,'B17':None,'B18':None}})
    add('high_valid_margin',{'SETTINGS':{'B14':.95,'B15':.04}})
    add('blank_template_start',source='blank',status='SELECT SERVICE')
    add('blank_template_configured',{'SETTINGS':{'B23':'READY'},'QUICK QUOTE':{'B11':'Standard home cleaning'}},source='blank')
    invalid=[('invalid_crew','QUICK QUOTE','B12',1.5),('zero_crew','QUICK QUOTE','B12',0),('zero_hours','QUICK QUOTE','B13',0),('negative_supplies','QUICK QUOTE','B16',-1),('tax_out_of_range','QUICK QUOTE','B19',1.1),('negative_hourly','SETTINGS','B10',-5),('negative_fee','SETTINGS','B15',-.03),('negative_margin','SETTINGS','B14',-.2),('negative_default_tax','SETTINGS','B18',-.1),('blank_hourly','SETTINGS','B10',None),('text_hourly','SETTINGS','B10','oops'),('unsupported_currency','SETTINGS','B22','USD')]
    for name,sheet,cell,value in invalid:add(name,{sheet:{cell:value}},status='CHECK INPUTS')
    add('margin_fee_denominator',{'SETTINGS':{'B14':.97,'B15':.03}},status='CHECK INPUTS')
    add('unknown_service',{'QUICK QUOTE':{'B11':'Unknown service'}},status='INVALID SERVICE')
    add('unreviewed_settings',{'SETTINGS':{'B23':'REVIEW BEFORE USE'}},status='REVIEW SETTINGS')
    add('text_and_date',{'SETTINGS':{'B20':'FICTIONAL QA BUSINESS','B21':'qa@example.invalid','B19':21},'QUICK QUOTE':{'B10':'QA-001','B20':'FICTIONAL QA CUSTOMER','B21':'2026-11-01'}},checks={('CLIENT QUOTE','A5'):'FICTIONAL QA BUSINESS',('CLIENT QUOTE','A6'):'qa@example.invalid',('CLIENT QUOTE','C9'):'QA-001',('CLIENT QUOTE','C10'):'2026-11-01',('CLIENT QUOTE','C11'):'FICTIONAL QA CUSTOMER'})
    add('renamed_service',{'SERVICES':{'A9':'QA renamed service'},'QUICK QUOTE':{'B11':'QA renamed service'}})
    for row in [10,22,34]:
        data=dict(zip('ABCDEFGHI',['QA-'+str(row),'Deep home cleaning',3,2.75,.5,24.5,7.2,15.8,35]))
        add('scenario_'+str(row),{'JOB SCENARIOS':{c+str(row):v for c,v in data.items()}},scenario=row)
        data=dict(zip('ABCDEFGHI',['QA-'+str(row),'2026-11-01','Fictional service',420,390,7.25,22,18,9]));data['N']='Fictional QA note'
        add('job_log_'+str(row),{'JOB LOG':{c+str(row):v for c,v in data.items()}},log=row)
    add('zero_revenue_log',{'JOB LOG':{'A34':'QA-zero','D34':100,'E34':0,'F34':2,'G34':0,'H34':0,'I34':0}},log=34)
    add('negative_log_expense',{'JOB LOG':{'A34':'QA-invalid','D34':100,'E34':100,'F34':2,'G34':-20,'H34':0,'I34':0}},log=34,log_invalid=True)
    add('duplicate_service',{'SERVICES':{'A10':'Standard home cleaning'}},status='INVALID SERVICE')
    add('negative_service_supply',{'SERVICES':{'C9':-5}},status='CHECK INPUTS')
    add('text_optional_cost',{'QUICK QUOTE':{'B16':'oops'}},status='CHECK INPUTS')
    add('blank_rounding',{'SETTINGS':{'B17':None}},status='CHECK INPUTS')
    add('scenario_settings_guard',{'SETTINGS':{'B10':-5},'JOB SCENARIOS':{'A34':'QA-invalid','B34':'Standard home cleaning','C34':1}},status='CHECK INPUTS',checks={('JOB SCENARIOS','Q34'):'CHECK INPUTS',('OVERVIEW','E9'):'CHECK SCENARIOS'})
    add('log_summary_guard',{'JOB LOG':{'A34':'QA-invalid','D34':100,'E34':100,'F34':2,'G34':-20,'H34':0,'I34':0}},checks={('JOB LOG','K34'):'CHECK INPUTS',('OVERVIEW','H15'):'CHECK JOB LOG',('OVERVIEW','K15'):'CHECK JOB LOG'})
    add('blank_log_expense',{'JOB LOG':{'A34':'QA-incomplete','D34':100,'E34':100,'F34':2,'G34':None,'H34':0,'I34':0}},checks={('JOB LOG','K34'):'CHECK INPUTS'})
    add('blank_selected_service_hours',{'SERVICES':{'B9':None},'QUICK QUOTE':{'B13':None}},status='CHECK INPUTS')
    for case in cases:fixture(sources[case['source']],inputs/(case['name']+'.xlsx'),case['changes'])
    command=['C:/Program Files/LibreOffice/program/soffice.com','-env:UserInstallation='+(root/'lo-profile').as_uri(),'--headless','--convert-to','xlsx','--outdir',str(outputs),*[str(inputs/(c['name']+'.xlsx')) for c in cases]]
    process=subprocess.run(command,capture_output=True,text=True,timeout=240)
    if process.returncode:raise RuntimeError(process.stderr)
    results=[]
    for case in cases:
        wb=ref.WorkbookReader(outputs/(case['name']+'.xlsx'));base=books[case['source']];change=case['changes'];issues=[];actual_status=wb.val('QUICK QUOTE','F27')
        expected_status=case.get('status','READY TO REVIEW')
        if actual_status!=expected_status:issues.append('Expected status '+expected_status+', got '+str(actual_status))
        def compare(sheet,cell,expected):
            actual=wb.val(sheet,cell)
            if isinstance(expected,(str,type(None))):ok=actual==expected or (expected is None and actual=='')
            else:
                try:ok=abs(float(actual)-float(expected))<1e-7
                except (TypeError,ValueError):ok=False
            if not ok:issues.append(f'{sheet}!{cell}: expected {expected}, got {actual}')
        if expected_status in ('READY TO REVIEW','REVIEW SETTINGS'):
            expected=quote(base,change)
            fields={'F12':'labor','F13':'supplies','F14':'mileage','F15':'overhead','F16':'subtotal','F17':'contingency','F18':'job_cost','F19':'list','F20':'discount','F21':'pre_tax','F22':'tax','F23':'total','F24':'fees','F25':'contribution','F26':'margin'}
            for cell,key in fields.items():compare('QUICK QUOTE',cell,expected[key])
            if expected_status=='READY TO REVIEW':compare('CLIENT QUOTE','E22',expected['total'])
        else:compare('CLIENT QUOTE','E22',None)
        for (sheet,cell),expected in case.get('checks',{}).items():compare(sheet,cell,expected)
        if case.get('scenario'):
            r=case['scenario'];expected=quote(base,change,scenario=r)
            for col,key in [('K','job_cost'),('L','list'),('M','pre_tax'),('N','total'),('O','contribution'),('P','margin')]:compare('JOB SCENARIOS',col+str(r),expected[key])
            compare('JOB SCENARIOS','Q'+str(r),'READY')
        if case.get('log'):
            r=str(case['log']);get=lambda c:numeric(val(base,'JOB LOG',c+r,change));st=lambda n:numeric(val(base,'SETTINGS','B'+str(n),change))
            if case.get('log_invalid'):compare('JOB LOG','K'+r,'CHECK INPUTS')
            else:
                cost=round(get('F')*st(10)+get('G')+get('H')*st(11)+get('I')+st(12)+get('E')*st(15),2)
                for col,expected in [('J',cost),('K',get('E')-cost),('L',(get('E')-cost)/get('E') if get('E')>0 else 0),('M',get('E')-get('D'))]:compare('JOB LOG',col+r,expected)
        results.append({'case':case['name'],'pass':not issues,'issues':issues})
    unchanged=all(hashlib.sha256(p.read_bytes()).hexdigest()==fingerprints[k] for k,p in sources.items())
    report={'engine':'LibreOffice Calc','sources':fingerprints,'originals_unchanged':unchanged,'passed':sum(r['pass'] for r in results),'total':len(results),'results':results}
    (root/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2));print(json.dumps([r for r in results if not r['pass']],indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--blank',required=True);p.add_argument('--demo',required=True);p.add_argument('--output',required=True)
    result=run(p.parse_args());sys.exit(0 if result['passed']==result['total'] and result['originals_unchanged'] else 1)
