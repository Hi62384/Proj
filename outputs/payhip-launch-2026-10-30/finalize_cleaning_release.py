"""Create the validated 1.0.1 candidate without overwriting the 1.0 release."""
import hashlib,json,shutil
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
work=ROOT/'verification-2026-11-01';final=work/'final'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
test=json.loads((work/'qa/candidate/results.json').read_text());assert test['passed']==test['total']==59 and test['originals_unchanged']
files={'Cleaning_Pricing_Calculator.xlsx':final/'customer/Cleaning_Pricing_Calculator.xlsx','Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx':final/'examples/Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx'}
assert sha(files['Cleaning_Pricing_Calculator.xlsx'])==test['sources']['blank']
assert sha(files['Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx'])==test['sources']['demo']
source=REPO/'products/cleaning-pricing-calculator/customer'
for name in ['Quick_Start_Guide.pdf','LICENSE_AND_DISCLAIMER.txt']:
    target=final/'customer'/name;shutil.copyfile(source/name,target);files[name]=target
start=final/'customer/START_HERE.txt'
start.write_text('''CLEANING BUSINESS PRICING & PROFIT CALCULATOR
Customer edition 1.0.1

1. Keep the downloaded original and save a working copy of Cleaning_Pricing_Calculator.xlsx.
2. Read the included Quick_Start_Guide.pdf. The guide's version 1.0 workflow still applies to this maintenance release.
3. In SETTINGS, replace illustrative costs with your own. Rates must be nonnegative, margin plus fee must be below 100%, rounding must be positive, and tax rates must be between 0% and 100%. Mark assumptions READY only after reviewing them. This edition uses CAD labels and does not convert currencies.
4. In SERVICES, edit the existing seven catalogue rows in place. Use unique service names, positive default hours and nonnegative supplies. The quote and scenario dropdowns use that catalogue. Adding or removing catalogue rows is not supported in this edition.
5. In QUICK QUOTE, select a service and enter crew, hours and adjustments. Blank optional cost adjustments mean zero; blank optional hours use the selected service default. A blank tax override uses SETTINGS, while an explicit zero overrides it to 0%. Do not use the customer quote unless its status is READY TO REVIEW.
6. Review CLIENT QUOTE. Enter your own business display details in SETTINGS and the customer's quote reference/date in QUICK QUOTE. Suggested quote validity in SETTINGS is manual guidance; it does not print an automatic expiry. Review all business identity, scope and terms before sharing a quote.
7. To print a customer quote, select CLIENT QUOTE and export/print that sheet only. It is configured for one landscape Letter page. Preview the result in your spreadsheet application before sending. The other worksheets are working tables and are not a single-page customer document.
8. JOB SCENARIOS supports 25 estimates. JOB LOG supports 25 manual actual-job entries. For a log row with a job ID, enter every numeric field D:I, using explicit zero where appropriate. Negative costs are unsupported. Negative contribution can be a legitimate loss and is not hidden.
9. CHECK INPUTS means correct the affected numeric inputs or settings. INVALID SERVICE / CHECK SERVICE means choose a unique catalogue name. CHECK SCENARIOS or CHECK JOB LOG on OVERVIEW means fix those rows before relying on the summary. These warnings must not be treated as zero cost or profit.

COMPATIBILITY
The files use ordinary .xlsx formulas, dropdowns and no macros. This candidate passed 59 independent native recalculation/input checks in LibreOffice Calc. Microsoft Excel-specific opening, editing and PDF-export behaviour has not been tested in this preparation environment. Do not interpret that Calc result as native Excel certification. Google Sheets, Apple Numbers and mobile workbook editing are not claimed as supported.

WHAT IS INCLUDED
Blank workbook, separately named FICTIONAL_DEMO workbook, Quick_Start_Guide.pdf, this startup note, and LICENSE_AND_DISCLAIMER.txt. All demonstration people, dates, costs, jobs and outcomes are fictional illustrations.

LIMITATIONS
Outputs estimate contribution after modeled costs; they are not guaranteed net profit. Taxes, costs and service assumptions need your own review. No cloud access, AI credits, automatic invoicing, payment processing, bank integration or automatic accounting is included. No macros or internet access are needed to use the downloaded workbook.

Keep backups. Do not redistribute or resell the template. Review LICENSE_AND_DISCLAIMER.txt. For a download or product defect, use the actual seller contact shown in the order confirmation; do not treat demonstration contact details inside a workbook as the seller's support address.
''',encoding='utf-8')
files['START_HERE.txt']=start
archive=final/'Cleaning_Pricing_Toolkit_v1.0.1_CUSTOMER.zip'
with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for name,path in sorted(files.items()):
        info=ZipInfo(name,(2026,11,1,12,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
        z.writestr(info,path.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
with ZipFile(archive) as z:
    assert z.testzip() is None and z.namelist()==sorted(files)
    assert all(z.read(n)==p.read_bytes() for n,p in files.items())
original=REPO/'products/cleaning-pricing-calculator/release/Cleaning_Pricing_Toolkit_v1.0_CUSTOMER.zip'
assert sha(original)=='9835184cb1e37a4ca7f4d379d0a234fee3b769fa22a0af0a3ca356a500c0d215'
manifest={'version':'1.0.1','status':'Validated local candidate. Not uploaded or publicly launched. Owner upload approval, checkout and seller readiness remain separate.','native_excel_verified':False,'native_calc_cases_passed':59,'archive':{'name':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive)},'original_release_preserved':{'name':original.name,'sha256':sha(original)},'files':{n:{'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in files.items()}}
(final/'FINAL_RELEASE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
