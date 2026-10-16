"""Build/check a deterministic seller-review-ready customer digital download ZIP.

Stdlib only. No networking, publishing, payments, account writes, or uploads.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED,BadZipFile

ROOT=Path(__file__).resolve().parents[1]
RELEASE=ROOT/'release'
ZIP_NAME='Cleaning_Pricing_Toolkit_v1.0_CUSTOMER.zip'
MANIFEST='RELEASE_MANIFEST.json'
SOURCES={
  'Cleaning_Pricing_Calculator.xlsx': ROOT/'customer'/'Cleaning_Pricing_Calculator.xlsx',
  'Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx':ROOT/'examples'/'Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx',
  'Quick_Start_Guide.pdf':ROOT/'customer'/'Quick_Start_Guide.pdf',
  'START_HERE.txt':ROOT/'customer'/'START_HERE.txt',
  'LICENSE_AND_DISCLAIMER.txt':ROOT/'customer'/'LICENSE_AND_DISCLAIMER.txt',
}

def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def read_source():
    result={}
    for name,path in SOURCES.items():
        if not path.is_file():raise RuntimeError('Missing customer file: '+str(path))
        data=path.read_bytes()
        if not data:raise RuntimeError('Empty product file: '+name)
        result[name]=data
    return result

def verify_bundle(path:Path, sources:dict[str,bytes]):
    if not path.is_file(): raise RuntimeError('Missing ZIP '+str(path))
    with ZipFile(path) as z:
        names=z.namelist()
        if names!=sorted(sources): raise RuntimeError('Incorrect zip entries: '+str(names))
        if z.testzip() is not None:raise RuntimeError('ZIP failed CRC integrity test')
        for name in names:
            member=z.getinfo(name)
            if member.file_size>10*1024*1024:raise RuntimeError('Unexpectedly large product entry')
            if z.read(name)!=sources[name]:raise RuntimeError('ZIP bytes do not match product source: '+name)
    return {'file':ZIP_NAME,'sha256':digest(path.read_bytes()),'bytes':path.stat().st_size}

def build():
    sources=read_source()
    RELEASE.mkdir(parents=True,exist_ok=True)
    target=RELEASE/ZIP_NAME
    if target.exists():target.unlink()  # only our exact known target, never original repo files
    with ZipFile(target,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(sources):
            info=ZipInfo(name,date_time=(2026,10,14,12,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=(0o100644<<16)
            z.writestr(info,sources[name],compress_type=ZIP_DEFLATED,compresslevel=9)
    bundle=verify_bundle(target,sources)
    manifest={
      'version':'1.0.0',
      'status':'READY FOR SELLER QA, NOT PUBLISHED OR PAYMENT CONNECTED',
      'license_type':'single-business use, no redistribution',
      'currency':'CAD',
      'demo_data':'entirely fictional',
      'files':{n:{'bytes':len(v),'sha256':digest(v)} for n,v in sorted(sources.items())},
      'release':bundle,
    }
    (RELEASE/MANIFEST).write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest

def check():
    sources=read_source()
    manifest=json.loads((RELEASE/MANIFEST).read_text(encoding='utf-8'))
    for name,data in sources.items():
        expected=manifest['files'].get(name)
        if not expected or expected['bytes']!=len(data) or expected['sha256']!=digest(data):
            raise RuntimeError('Manifest mismatch for '+name)
    current=verify_bundle(RELEASE/ZIP_NAME,sources)
    if current!=manifest['release']:raise RuntimeError('ZIP hash/size differs from manifest')
    print('PASS: bundled entries, source bytes, manifest hashes and ZIP CRC verified')
    return True

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Deterministic offline product ZIP packaging')
    parser.add_argument('--check',action='store_true',help='Verify without modifying files')
    args=parser.parse_args()
    if args.check:check()
    else:
        m=build();print('Built',RELEASE/ZIP_NAME,'bytes',m['release']['bytes'],'sha256',m['release']['sha256'])
