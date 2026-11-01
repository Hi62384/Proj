"""Build a separate candidate bundle; never replace the existing release ZIP."""
import hashlib,json
from zipfile import ZipFile,ZIP_DEFLATED
from review_files import ROOT,REPO,digest
original=REPO/'products/cleaning-pricing-calculator/release/Cleaning_Pricing_Toolkit_v1.0_CUSTOMER.zip'
before=digest(original)
candidate=ROOT/'Cleaning_Pricing_Toolkit_PRINT_FIX_REVIEW.zip'
with ZipFile(original) as source,ZipFile(candidate,'w',compression=ZIP_DEFLATED) as dest:
    records=[]
    for info in source.infolist():
        replacement=ROOT/'print-review-copies'/info.filename
        data=replacement.read_bytes() if replacement.exists() else source.read(info.filename)
        dest.writestr(info.filename,data)
        records.append({'name':info.filename,'sha256':hashlib.sha256(data).hexdigest(),'print_fix':replacement.exists()})
with ZipFile(candidate) as check:assert check.testzip() is None;assert len(check.namelist())==5
assert digest(original)==before
(ROOT/'print-review-manifest.json').write_text(json.dumps({'status':'Review only. Not uploaded or published.','original_zip_unchanged':True,'source_sha256':before,'candidate_sha256':digest(candidate),'candidate_bytes':candidate.stat().st_size,'files':records},indent=2),encoding='utf-8')
print('PASS: separate five-file review ZIP, CRC valid, original ZIP unchanged')
