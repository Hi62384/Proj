import copy,hashlib,json,subprocess,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
R=Path(__file__).resolve().parent;N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};Q=lambda t:'{'+N['s']+'}'+t
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
final=R/'candidate';final.mkdir(exist_ok=True)
edits=json.loads((R/'authored/edits.json').read_text());source=R/'source/product.xlsx';dest=final/'Inventory_Reorder_Planner.xlsx'
with zipfile.ZipFile(source) as src,zipfile.ZipFile(R/'authored/Inventory_Reorder_Planner.xlsx') as authored,zipfile.ZipFile(dest,'w') as out:
 for info in src.infolist():
  raw=src.read(info.filename)
  if info.filename in ['xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml']:
   name='Calculator' if 'sheet1.' in info.filename else 'Read me';tree=E.fromstring(raw);new=E.fromstring(authored.read(info.filename));cells={c.get('r'):c for c in tree.findall('.//s:c',N)};newcells={c.get('r'):c for c in new.findall('.//s:c',N)}
   for address,edit in edits[name].items():
    c=cells[address]
    if 'formula' in edit:
     f=newcells[address].find('s:f',N);assert f is not None and f.text==edit['formula'][1:]
     c.remove(c.find('s:f',N));c.insert(0,copy.deepcopy(f))
    else:
     for child in list(c):c.remove(child)
     c.set('t','str');E.SubElement(c,Q('v')).text=edit['value']
   raw=E.tostring(tree,encoding='utf-8',xml_declaration=True)
  out.writestr(info,raw)
with zipfile.ZipFile(source) as a,zipfile.ZipFile(dest) as b:
 assert b.testzip() is None and a.read('xl/styles.xml')==b.read('xl/styles.xml')
 for i,name in enumerate(edits,1):
  p=f'xl/worksheets/sheet{i}.xml';old=E.fromstring(a.read(p));new=E.fromstring(b.read(p))
  before={c.get('r'):E.tostring(c) for c in old.findall('.//s:c',N)};after={c.get('r'):E.tostring(c) for c in new.findall('.//s:c',N)}
  assert before.keys()==after.keys() and all(before[k]==after[k] for k in before if k not in edits[name])
  for tag in ['cols','mergeCells','pageSetup','pageMargins','sheetViews']:
   assert E.tostring(old.find('s:'+tag,N))==E.tostring(new.find('s:'+tag,N)) if old.find('s:'+tag,N) is not None else new.find('s:'+tag,N) is None
cases=[('default',[12,7,30,80],[114,34]),('zero',[0,0,0,0],[0,0]),('above_threshold',[12,7,30,200],[114,0]),('fractional',[1.5,2.5,.25,1],[4,3]),('large',[1000000,365,5000,123],[365005000,365004877]),('missing',[None,7,30,80],None),('text',['twelve',7,30,80],None)]
for i in range(4):
 v=[12,7,30,80];v[i]=-1;cases.append(('negative_'+str(i),v,None))
casepath=R/'qa/cases';native=R/'qa/native';casepath.mkdir(parents=True,exist_ok=True);native.mkdir(exist_ok=True)
for name,values,expected in cases:
 with zipfile.ZipFile(dest) as z,zipfile.ZipFile(casepath/(name+'.xlsx'),'w') as out:
  for info in z.infolist():
   raw=z.read(info.filename)
   if info.filename=='xl/worksheets/sheet1.xml':
    tree=E.fromstring(raw);cells={c.get('r'):c for c in tree.findall('.//s:c',N)}
    for row,value in enumerate(values,5):
     c=cells['B'+str(row)]
     for child in list(c):c.remove(child)
     c.attrib.pop('t',None)
     if value is not None:
      if isinstance(value,str):c.set('t','str')
      E.SubElement(c,Q('v')).text=str(value)
    for address in ['B10','B11']:
     c=cells[address];v=c.find('s:v',N)
     if v is not None:c.remove(v)
    raw=E.tostring(tree,encoding='utf-8',xml_declaration=True)
   out.writestr(info,raw)
exe='C:/Program Files/LibreOffice/program/soffice.com';profile=(R/'qa/lo-profile').as_uri()
run=subprocess.run([exe,'-env:UserInstallation='+profile,'--headless','--convert-to','xlsx','--outdir',str(native),*[str(p) for p in casepath.glob('*.xlsx')]],capture_output=True,text=True,timeout=120)
assert run.returncode==0,run.stderr
results=[]
for name,values,expected in cases:
 with zipfile.ZipFile(native/(name+'.xlsx')) as z:
  t=E.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={c.get('r'):c for c in t.findall('.//s:c',N)}
  actual=[cells[a].findtext('s:v',namespaces=N) for a in ['B10','B11']]
  strings=[]
  if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(v.itertext()) for v in E.fromstring(z.read('xl/sharedStrings.xml'))]
  actual=[strings[int(v)] if cells[a].get('t')=='s' else v for a,v in zip(['B10','B11'],actual)]
  ok=all(float(a)==e for a,e in zip(actual,expected)) if expected else actual==['CHECK INPUTS','CHECK INPUTS']
  results.append({'case':name,'pass':ok,'actual':actual});assert ok,(name,actual,expected)
record={'source_hash':H(source),'candidate_hash':H(dest),'styles_and_unrelated_cells_preserved':True,'native_engine':'LibreOffice Calc','passed':len(results),'total':len(cases),'results':results,'native_excel_verified':False}
(R/'qa/results.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
