"""Rebuild the editable cleaning quotation templates with artifact_tool.

This is optional authoring source. The sold files do NOT require Python or
artifact_tool. Run using a Python environment with artifact_tool installed.
No external APIs, internet access or customer data are accessed.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from artifact_tool import Workbook, SpreadsheetFile

BASE = Path(__file__).resolve().parents[1]
CUSTOMER = BASE / 'customer'
EXAMPLES = BASE / 'examples'
NAVY = '#13263A'
NAVY2 = '#1B354B'
TEAL = '#0A837A'
AQUA = '#D9F4F0'
PALE = '#F3F7FA'
PALE_BLUE = '#EFF6FF'
BLUE = '#1D4ED8'
INK = '#1D3142'
MUTED = '#556879'
WHITE = '#FFFFFF'
YELLOW = '#FFF1C5'
GOLD = '#D59C38'
RED = '#B91C1C'
GREEN = '#0E7C67'
MONEY = '"CAD "#,##0.00;[Red]("CAD "#,##0.00);"-"'
PCT = '0.0%;[Red](0.0%);"-"'
DEC = '#,##0.0;[Red](#,##0.0);"-"'
SERVICES = [
 ('Standard home cleaning',2.5,9.00,'Typical regular residential visit'),
 ('Deep home cleaning',4.0,17.00,'More detailed residential cleaning; check actual scope'),
 ('Move-in / move-out',5.0,22.00,'Empty-unit residential visit; review access'),
 ('Small office cleaning',2.0,10.00,'Light office cleaning without specialty services'),
 ('Apartment turnover',3.0,12.00,'Routine apartment turnover, not restoration'),
 ('Recurring maintenance',2.0,8.00,'Small regular recurring cleaning'),
 ('Interior window cleaning',2.0,6.00,'Interior-accessible windows only; no elevated work'),
]
SETTINGS = [
  ('Loaded labor cost per employee-hour',25.00,'Include pay + employer burden, not the selling rate.'),
  ('Travel vehicle allowance per km',0.55,'Operating expense per round-trip kilometer.'),
  ('Base overhead per job',14.00,'Allocate business insurance, supplies storage, scheduling, etc.'),
  ('Cost contingency rate',0.08,'Applied to estimated operating costs.'),
  ('Target contribution margin',0.30,'Target share of pre-tax sales after estimated processing fees and costs.'),
  ('Estimated payment processing fee',0.03,'Planning % only. Real processor may also charge fixed and FX fees.'),
  ('Minimum pre-tax price AFTER discount',100.00,'A minimum before sales tax; adjust for your business.'),
  ('Round suggested list price to',5.00,'Nearest higher increment in CAD, e.g., 5.'),
  ('Sales tax rate - set for YOUR jurisdiction',0.00,'Default 0 = unconfigured, NOT an exemption. Verify tax rules.'),
  ('Quote validity (calendar days)',14,'Suggested customer quote expiry, not a contract.'),
  ('Business display name','YOUR BUSINESS NAME','Used on CLIENT QUOTE. Do not add private information.'),
  ('Support contact','support@example.com','Used on CLIENT QUOTE; confirm it is monitored.'),
  ('Currency','CAD','All prices are CAD. No currency conversion.'),
  ('Assumptions reviewed?','REVIEW BEFORE USE','Change to READY only after reviewing all costs and tax settings.'),
]

def merge_label(s, target, label, color=WHITE, fill=NAVY, font_size=15, height=28):
    s.merge_cells(target)
    top=target.split(':')[0]
    s.get_range(top).values=[[label]]
    s.get_range(target).format = {
        'fill':fill,
        'font':{'bold':True,'color':color,'size':font_size},
        'vertical_alignment':'center',
        'row_height':height,
    }

def put(s,cell,value): s.get_range(cell).values=[[value]]
def formula(s,cell,value): s.get_range(cell).formulas=[[value]]
def column(s,name,width): s.get_range(f'{name}:{name}').format.column_width = width

def highlight(s,rg,background=PALE_BLUE,font=BLUE,bold=False):
    s.get_range(rg).format={'fill':background, 'font':{'color':font,'bold':bold,'size':10},'vertical_alignment':'center','row_height':23}

def header(s,rg):
    s.get_range(rg).format={'fill':NAVY2,'font':{'color':WHITE,'bold':True,'size':10}, 'row_height':34,'vertical_alignment':'center','wrap_text':True}

def note(s,rg,txt):
    s.merge_cells(rg)
    put(s,rg.split(':')[0],txt)
    s.get_range(rg).format={'fill':YELLOW,'font':{'color':'#80550B','size':10},'wrap_text':True,'vertical_alignment':'center','row_height':30}

def make_book(sample=False):
    wb=Workbook.create()
    rd=wb.worksheets.add('READ ME')
    ov=wb.worksheets.add('OVERVIEW')
    qb=wb.worksheets.add('QUICK QUOTE')
    cq=wb.worksheets.add('CLIENT QUOTE')
    scenarios=wb.worksheets.add('JOB SCENARIOS')
    log=wb.worksheets.add('JOB LOG')
    srv=wb.worksheets.add('SERVICES')
    st=wb.worksheets.add('SETTINGS')
    # READ ME
    for k,w in [('A',22),('B',28),('C',26),('D',28),('E',18),('F',19),('G',19),('H',20)]: column(rd,k,w)
    merge_label(rd,'A1:H2','CLEANING BUSINESS  /  PRICING & PROFIT TOOLKIT',font_size=21,height=27)
    merge_label(rd,'A4:H4','START HERE  ·  5-MINUTE WALKTHROUGH',fill=TEAL,font_size=14)
    notes=[
      ('01','Go to SETTINGS and replace every illustrative assumption with your real costs. Set Assumptions reviewed? to READY only after checking.'),
      ('02','Edit SERVICES: adjust default cleaning hours per employee and standard consumable costs. Do not assume sample hours are industry standards.'),
      ('03','Open QUICK QUOTE: select a service, enter the crew, hours, travel, supplies and discount. Check the visible review status.'),
      ('04','Review cost, estimated contribution and tax settings. CLIENT QUOTE shows customer-facing values without internal cost breakdown.'),
      ('05','Use JOB SCENARIOS for 25 what-if quotes and JOB LOG for real actual-job results. Blank inputs produce blank result rows.'),
      ('06','Use OVERVIEW for a snapshot. The workbook never imports bank, payroll or accounting data automatically.'),
    ]
    for i,(n,t) in enumerate(notes,7):
        put(rd,f'A{i}',n);rd.merge_cells(f'B{i}:H{i}');put(rd,f'B{i}',t)
        highlight(rd,f'A{i}',AQUA,TEAL,True)
        rd.get_range(f'B{i}:H{i}').format={'fill':WHITE if i%2 else PALE,'font':{'color':INK,'size':11},'row_height':35,'wrap_text':True,'vertical_alignment':'center'}
    merge_label(rd,'A15:H15','COLOR GUIDE  ·  BLUE = EDITABLE, DARK = CALCULATED, TEAL = CROSS-SHEET',fill=NAVY2,font_size=11)
    note(rd,'A17:H18','All prices are Canadian dollars. Sales-tax default is zero as a placeholder. Set your applicable rate before issuing a customer quote. If the rate is zero legally, document your reason separately.')
    note(rd,'A20:H21','These are decision-support estimates, NOT guaranteed profit, tax advice, legal forms or certified accounting. Costs not entered (advertising, unexpected work, income tax, owner draw) are NOT included.')
    rd.merge_cells('A23:H23');put(rd,'A23','DEMO DATA' if sample else 'BLANK CUSTOMER TEMPLATE')
    rd.get_range('A23:H23').format={'fill':AQUA if sample else PALE,'font':{'color':TEAL,'bold':True,'size':12},'row_height':27}
    # SETTINGS
    for k,w in [('A',40),('B',25),('C',60),('D',14),('E',16),('F',16),('G',16),('H',15)]: column(st,k,w)
    merge_label(st,'A1:H2','BUSINESS SETTINGS  /  CHANGE BLUE CELLS',font_size=18)
    note(st,'A4:H5','These are illustrative starting assumptions ONLY. Verify local wage costs, payroll burden, driving costs, overhead, processing fees and sales tax before quoting anyone.')
    header(st,'A9:C9');st.get_range('A9:C9').values=[['Assumption / label','Editable value','What this controls']]
    st.get_range('A10:C23').values=[[x[0],x[1],x[2]] for x in SETTINGS]
    st.get_range('A10:A23').format={'font':{'color':INK,'size':10},'row_height':27,'vertical_alignment':'center'}
    st.get_range('C10:C23').format={'font':{'color':MUTED,'size':10},'wrap_text':True,'row_height':28,'vertical_alignment':'center'}
    highlight(st,'B10:B23');st.get_range('B10:B18').set_number_format(MONEY)
    st.get_range('B13:B15').set_number_format(PCT)
    st.get_range('B18').set_number_format(PCT)
    st.get_range('B19').set_number_format('0')
    st.get_range('B23').values=[['READY' if sample else 'REVIEW BEFORE USE']]
    st.get_range('B23').data_validation={'rule':{'type':'list','values':['REVIEW BEFORE USE','READY']}}
    note(st,'A26:H27','Contribution margin is NOT a tax-adjusted net profit and excludes some real-world expenses. Use a fully loaded labor rate including payroll costs, or margin will be overstated.')
    # Oops SETTINGS actual mapping: B10 hourly, B11 mileage, B12 overhead, B13 contingency, B14 margin, B15 fee, B16 min, B17 rounding, B18 tax, B19 validity, B20 business, B21 email, B22 currency, B23 ready.
    # SERVICES
    for k,w in [('A',31),('B',24),('C',23),('D',61),('E',12),('F',12),('G',15),('H',15)]: column(srv,k,w)
    merge_label(srv,'A1:H2','SERVICE CATALOG  /  ADJUST TO YOUR ACTUAL WORK',font_size=18)
    note(srv,'A4:H5','Default hours are PER EMPLOYEE on site; two employees each working 3 hours equals SIX paid labor hours. Supplies are illustrative per-job CAD costs. Special/hazardous cleaning is not included.')
    header(srv,'A8:D8');srv.get_range('A8:D8').values=[['Service','Default hours / employee','Base supplies cost (CAD)','Definition and boundary']]
    srv.get_range('A9:D15').values=[[x[0],x[1],x[2],x[3]] for x in SERVICES]
    highlight(srv,'A9:C15')
    srv.get_range('B9:B15').set_number_format(DEC);srv.get_range('C9:C15').set_number_format(MONEY)
    srv.get_range('D9:D15').format={'font':{'color':MUTED,'size':10},'wrap_text':True,'row_height':31}
    note(srv,'A18:H19','Service names must match the menu in QUICK QUOTE and JOB SCENARIOS. Change default hours/supplies, but for compatibility do not add or remove catalogue rows without updating the formulas and validation.')
    # QUICK QUOTE
    for k,w in [('A',34),('B',25),('C',15),('D',7),('E',37),('F',26),('G',13),('H',16),('I',15)]: column(qb,k,w)
    merge_label(qb,'A1:I2','QUICK QUOTE  /  COST-BASED SERVICE PRICING',font_size=18)
    note(qb,'A4:I5','Edit BLUE input cells only. All costs and quotes are estimates; verify actual labor, tax and service scope. Check STATUS at bottom right before offering a price.')
    header(qb,'A8:B8');qb.get_range('A8:B8').values=[['Job detail','Enter here']]
    header(qb,'E8:F8');qb.get_range('E8:F8').values=[['Automatic calculation','Estimate (CAD)']]
    inputs=[
      ('Quote reference','DEMO-001' if sample else ''),
      ('Cleaning service','Standard home cleaning' if sample else ''),
      ('Crew size - people',2 if sample else 1),
      ('On-site hours / employee (optional)',3 if sample else None),
      ('Paid travel hours / employee',0.25 if sample else 0),
      ('Roundtrip travel distance (km)',12 if sample else 0),
      ('Additional supply costs',4 if sample else 0),
      ('Additional overhead costs',0),
      ('Discount on list price',10 if sample else 0),
      ('Tax rate override (optional)',None),
      ('Customer / project display label','FICTIONAL CUSTOMER' if sample else ''),
      ('Customer quote date (YYYY-MM-DD)','2026-10-14' if sample else ''),
    ]
    qb.get_range('A10:B21').values=[[a,b] for a,b in inputs]
    qb.get_range('A10:A21').format={'fill':PALE,'font':{'color':INK,'size':10},'row_height':26,'vertical_alignment':'center'}
    highlight(qb,'B10:B21')
    qb.get_range('B11').data_validation={'rule':{'type':'list','values':[s[0] for s in SERVICES]}}
    qb.get_range('B12').set_number_format('0')
    qb.get_range('B13:B15').set_number_format(DEC)
    qb.get_range('B16:B18').set_number_format(MONEY)
    qb.get_range('B19').set_number_format(PCT)
    for r,label in enumerate(['Actual on-site hours / employee','Loaded labor cost','Supplies and consumables','Vehicle mileage allowance','Overhead allocation','Subtotal: direct operating cost','Contingency allowance','Total modeled job cost','List price before discount','Discount','Price to customer before sales tax','Estimated sales tax','Total customer quote (incl. tax)','Estimated payment fees','Estimated contribution (before income tax)','Contribution margin (after modeled costs)','STATUS / seller review gate'],11):
        put(qb,f'E{r}',label)
    qb.get_range('E11:E27').format={'fill':PALE,'font':{'color':INK,'size':10},'row_height':26,'vertical_alignment':'center'}
    qb.get_range('F11:F27').format={'fill':WHITE,'font':{'color':INK,'size':11},'row_height':26,'vertical_alignment':'center'}
    qb.get_range('F11').set_number_format(DEC)
    qb.get_range('F12:F25').set_number_format(MONEY)
    qb.get_range('F26').set_number_format(PCT)
    for line,calc in [
      (11,'IF(B13="",IFERROR(VLOOKUP(B11,SERVICES!$A$9:$C$15,2,FALSE),0),B13)'),
      (12,'ROUND(B12*(F11+B14)*SETTINGS!$B$10,2)'),
      (13,'ROUND(IFERROR(VLOOKUP(B11,SERVICES!$A$9:$C$15,3,FALSE),0)+B16,2)'),
      (14,'ROUND(B15*SETTINGS!$B$11,2)'),
      (15,'ROUND(SETTINGS!$B$12+B17,2)'),
      (16,'SUM(F12:F15)'),
      (17,'ROUND(F16*SETTINGS!$B$13,2)'),
      (18,'SUM(F16:F17)'),
      (19,'MAX(ROUNDUP((F18/(1-SETTINGS!$B$14-SETTINGS!$B$15)+B18)/SETTINGS!$B$17,0)*SETTINGS!$B$17,ROUNDUP((SETTINGS!$B$16+B18)/SETTINGS!$B$17,0)*SETTINGS!$B$17)'),
      (20,'B18'),
      (21,'F19-F20'),
      (22,'ROUND(F21*IF(B19="",SETTINGS!$B$18,B19),2)'),
      (23,'F21+F22'),
      (24,'ROUND(F21*SETTINGS!$B$15,2)'),
      (25,'F21-F18-F24'),
      (26,'IF(F21>0,F25/F21,0)'),
    ]:
        formula(qb,f'F{line}',f'=IF(OR(F27="READY TO REVIEW",F27="REVIEW SETTINGS"),{calc},"")')
    formula(qb,'F27','=IF(B11="","SELECT SERVICE",IF(COUNTIF(SERVICES!$A$9:$A$15,B11)=0,"INVALID SERVICE",IF(OR(B12<1,B12<>INT(B12),AND(B13<>"",B13<=0),B14<0,B15<0,B16<0,B17<0,B18<0,AND(B19<>"",OR(B19<0,B19>1)),SETTINGS!$B$14+SETTINGS!$B$15>=1,SETTINGS!$B$17<=0,SETTINGS!$B$16<0),"CHECK INPUTS",IF(SETTINGS!$B$23<>"READY","REVIEW SETTINGS","READY TO REVIEW"))))')
    highlight(qb,'E23:F23',AQUA,TEAL,True)
    highlight(qb,'E25:F26',AQUA,TEAL,True)
    highlight(qb,'E27:F27',YELLOW,'#80550B',True)
    note(qb,'A24:C26','Hours are per employee; total paid hours = crew × (on-site + paid travel). Contribution excludes taxes, ad costs, debt service, owner drawings and unentered business expenses. Verify all charges and assumptions.')
    # CLIENT QUOTE
    for k,w in [('A',18),('B',24),('C',27),('D',18),('E',20),('F',21),('G',16),('H',18)]: column(cq,k,w)
    merge_label(cq,'A1:H3','CUSTOMER QUOTE  /  DRAFT FOR REVIEW',font_size=19,height=27)
    cq.merge_cells('A5:H5');formula(cq,'A5','=SETTINGS!B20')
    cq.get_range('A5:H5').format={'fill':AQUA,'font':{'color':TEAL,'size':17,'bold':True},'row_height':32}
    cq.merge_cells('A6:H6');formula(cq,'A6','=SETTINGS!B21')
    cq.get_range('A6:H6').format={'font':{'color':MUTED,'size':10},'row_height':25}
    for row, lab, f in [(9,'Quote ID',"='QUICK QUOTE'!B10"),(10,'Date',"='QUICK QUOTE'!B21"),(11,'Customer / project',"='QUICK QUOTE'!B20"),(13,'Cleaning service',"='QUICK QUOTE'!B11"),(14,'Crew size',"='QUICK QUOTE'!B12")]:
        put(cq,f'A{row}',lab);cq.merge_cells(f'C{row}:F{row}');formula(cq,f'C{row}',f)
        cq.get_range(f'A{row}:B{row}').format={'font':{'color':MUTED,'size':11},'row_height':30}
        cq.get_range(f'C{row}:F{row}').format={'font':{'color':GREEN,'size':11,'bold':True},'row_height':30}
    header(cq,'A17:F17');cq.get_range('A17:F17').values=[['Service / adjustment',None,None,None,'CAD ex tax','']]
    cq.merge_cells('A18:D18');put(cq,'A18','Cleaning service (agreed scope)')
    formula(cq,'E18','=IF(\'QUICK QUOTE\'!F27="READY TO REVIEW",\'QUICK QUOTE\'!F19,"")')
    cq.merge_cells('A19:D19');put(cq,'A19','Discount')
    formula(cq,'E19','=IF(\'QUICK QUOTE\'!F27="READY TO REVIEW",-\'QUICK QUOTE\'!F20,"")')
    cq.merge_cells('A20:D20');put(cq,'A20','Total before sales tax')
    formula(cq,'E20','=IF(\'QUICK QUOTE\'!F27="READY TO REVIEW",\'QUICK QUOTE\'!F21,"")')
    cq.merge_cells('A21:D21');put(cq,'A21','Estimated applicable sales tax')
    formula(cq,'E21','=IF(\'QUICK QUOTE\'!F27="READY TO REVIEW",\'QUICK QUOTE\'!F22,"")')
    cq.merge_cells('A22:D22');put(cq,'A22','TOTAL CUSTOMER QUOTE')
    formula(cq,'E22','=IF(\'QUICK QUOTE\'!F27="READY TO REVIEW",\'QUICK QUOTE\'!F23,"")')
    cq.get_range('A18:F22').format={'font':{'color':INK,'size':11},'row_height':32,'vertical_alignment':'center'}
    cq.get_range('E18:E22').set_number_format(MONEY)
    highlight(cq,'A22:F22',AQUA,TEAL,True)
    note(cq,'A25:H26','DRAFT QUOTE. NOT AN INVOICE OR A GUARANTEED CONTRACT. Confirm scope, exclusions, cancellation, date, tax obligations and validity before sending. Never send if QUICK QUOTE status is not READY TO REVIEW.')
    # JOB SCENARIOS
    for k,w in [('A',14),('B',29),('C',11),('D',15),('E',13),('F',13),('G',13),('H',13),('I',13),('J',16),('K',18),('L',18),('M',18),('N',18),('O',18),('P',13),('Q',19)]:column(scenarios,k,w)
    merge_label(scenarios,'A1:Q2','SCENARIO PLANNER  /  COMPARE UP TO 25 QUOTES',font_size=18)
    note(scenarios,'A4:Q5','Edit blue columns A–I, including a job ID and exact service name. Every row calculates individually; blank ID rows remain blank. Results use SETTINGS and SERVICES. Dates and taxes are not automatically researched.')
    cols=['Job ID','Service','Crew','On-site override h / person','Paid travel h / person','Roundtrip km','Extra supplies CAD','Extra overhead CAD','Discount CAD','On-site hours / person','Modeled job cost CAD','List price CAD','Quote ex tax CAD','Quote incl tax CAD','Est contribution CAD','Margin %','STATUS']
    header(scenarios,'A9:Q9');scenarios.get_range('A9:Q9').values=[cols]
    highlight(scenarios,'A10:I34')
    scenarios.get_range('B10:B34').data_validation={'rule':{'type':'list','values':[s[0] for s in SERVICES]}}
    fgrid=[]
    for row in range(10,35):
        r=row
        # compute status independently of J..P
        status=(f'=IF(A{r}="","",IF(COUNTIF(SERVICES!$A$9:$A$15,B{r})=0,"CHECK SERVICE",'
                f'IF(OR(C{r}<1,C{r}<>INT(C{r}),AND(D{r}<>"",D{r}<=0),E{r}<0,F{r}<0,G{r}<0,H{r}<0,I{r}<0,'
                f'SETTINGS!$B$14+SETTINGS!$B$15>=1,SETTINGS!$B$17<=0),"CHECK INPUTS",'
                f'IF(SETTINGS!$B$23<>"READY","REVIEW SETTINGS","READY"))))')
        j=f'=IF(OR(Q{r}="READY",Q{r}="REVIEW SETTINGS"),IF(D{r}="",IFERROR(VLOOKUP(B{r},SERVICES!$A$9:$C$15,2,FALSE),0),D{r}),"")'
        direct=(f'ROUND(C{r}*(J{r}+E{r})*SETTINGS!$B$10,2)+ROUND(IFERROR(VLOOKUP(B{r},SERVICES!$A$9:$C$15,3,FALSE),0)+G{r},2)'
                f'+ROUND(F{r}*SETTINGS!$B$11,2)+ROUND(SETTINGS!$B$12+H{r},2)')
        k=f'=IF(OR(Q{r}="READY",Q{r}="REVIEW SETTINGS"),ROUND(({direct})+ROUND(({direct})*SETTINGS!$B$13,2),2),"")'
        l=f'=IF(OR(Q{r}="READY",Q{r}="REVIEW SETTINGS"),MAX(ROUNDUP((K{r}/(1-SETTINGS!$B$14-SETTINGS!$B$15)+I{r})/SETTINGS!$B$17,0)*SETTINGS!$B$17,ROUNDUP((SETTINGS!$B$16+I{r})/SETTINGS!$B$17,0)*SETTINGS!$B$17),"")'
        m=f'=IF(OR(Q{r}="READY",Q{r}="REVIEW SETTINGS"),L{r}-I{r},"")'
        n=f'=IF(OR(Q{r}="READY",Q{r}="REVIEW SETTINGS"),M{r}+ROUND(M{r}*SETTINGS!$B$18,2),"")'
        o=f'=IF(OR(Q{r}="READY",Q{r}="REVIEW SETTINGS"),M{r}-K{r}-ROUND(M{r}*SETTINGS!$B$15,2),"")'
        p=f'=IF(OR(Q{r}="READY",Q{r}="REVIEW SETTINGS"),IF(M{r}>0,O{r}/M{r},0),"")'
        fgrid.append([j,k,l,m,n,o,p,status])
    scenarios.get_range('J10:Q34').formulas=fgrid
    scenarios.get_range('J10:Q34').format={'font':{'color':INK,'size':10},'row_height':25,'vertical_alignment':'center'}
    scenarios.get_range('K10:O34').set_number_format(MONEY);scenarios.get_range('P10:P34').set_number_format(PCT)
    if sample:
        srows=[
          ['EX-001','Standard home cleaning',2,3,.25,12,4,0,10],
          ['EX-002','Deep home cleaning',2,4.5,.40,20,6,0,0],
          ['EX-003','Apartment turnover',1,3.0,.25,8,3,4,0],
          ['EX-004','Small office cleaning',3,2.0,.5,24,7,0,15],
          ['EX-005','Recurring maintenance',2,None,.15,5,0,0,0],
          ['EX-006','Move-in / move-out',2,6,.4,15,8,10,0],
        ]
        scenarios.get_range('A10:I15').values=srows
    scenarios.freeze_panes.freeze_rows(9)
    # JOB LOG
    for k,w in [('A',15),('B',17),('C',26),('D',17),('E',20),('F',18),('G',18),('H',16),('I',20),('J',18),('K',18),('L',15),('M',18),('N',35)]:column(log,k,w)
    merge_label(log,'A1:N2','JOB LOG  /  PLAN VERSUS ACTUAL CONTRIBUTION',font_size=18)
    note(log,'A4:N5','After completing a real job, manually enter actual sales (before tax), all paid labor hours, supplies, kilometers and other expenses. Estimates are NOT imported automatically and should be copied by ID from a reviewed quote.')
    labels=['Job ID','Job date YYYY-MM-DD','Service','Quoted ex tax CAD','Collected ex tax CAD','Actual total paid labor hours','Actual supplies CAD','Actual vehicle km','Other actual costs CAD','Observed job cost + fee CAD','Contribution CAD','Contribution margin %','Sales vs quote CAD','Notes']
    header(log,'A9:N9');log.get_range('A9:N9').values=[labels]
    highlight(log,'A10:I34');highlight(log,'N10:N34')
    log.get_range('J10:M34').format={'font':{'color':INK,'size':10},'row_height':25}
    lf=[]
    for r in range(10,35):
      lf.append([f'=IF(A{r}="","",ROUND(F{r}*SETTINGS!$B$10+G{r}+H{r}*SETTINGS!$B$11+I{r}+SETTINGS!$B$12+E{r}*SETTINGS!$B$15,2))',
                 f'=IF(A{r}="","",E{r}-J{r})',
                 f'=IF(A{r}="","",IF(E{r}>0,K{r}/E{r},0))',
                 f'=IF(A{r}="","",E{r}-D{r})'])
    log.get_range('J10:M34').formulas=lf
    log.get_range('D10:E34').set_number_format(MONEY)
    log.get_range('G10:G34').set_number_format(MONEY)
    log.get_range('I10:K34').set_number_format(MONEY)
    log.get_range('L10:L34').set_number_format(PCT)
    log.get_range('M10:M34').set_number_format(MONEY)
    if sample:
       log.get_range('A10:I12').values=[
         ['EX-001','2026-10-14','Standard home cleaning',320,320,6.50,13,12,4],
         ['EX-002','2026-10-14','Deep home cleaning',475,475,9.25,21,20,6],
         ['EX-003','2026-10-15','Apartment turnover',195,195,3.75,15,8,2],
       ]
       log.get_range('N10:N12').values=[['Fictional sample - not a client'],['Fictional sample - not a client'],['Fictional sample - not a client']]
    log.freeze_panes.freeze_rows(9)
    # OVERVIEW
    for k,w in [('A',20),('B',23),('C',18),('D',15),('E',24),('F',14),('G',15),('H',24),('I',14),('J',14),('K',24),('L',18),('M',18),('N',18),('O',18)]: column(ov,k,w)
    merge_label(ov,'A1:O2','WORKBOOK OVERVIEW  /  ESTIMATES ARE NOT GUARANTEED EARNINGS',font_size=17)
    note(ov,'A4:O5','Scenario figures come from your drafts; job-log figures come only from what you manually enter. No bank data, tax filing, customer accounts or external integrations exist.')
    boxes=[('A7:D7','Drafts with reviewed pricing','B9','=COUNTIF(\'JOB SCENARIOS\'!Q10:Q34,"READY")','0'),
           ('E7:G7','Scenarios · quote ex tax','E9','=SUM(\'JOB SCENARIOS\'!M10:M34)',MONEY),
           ('H7:J7','Scenarios · contribution','H9','=SUM(\'JOB SCENARIOS\'!O10:O34)',MONEY),
           ('K7:O7','Scenarios · margin','K9','=IF(E9>0,H9/E9,0)',PCT),
           ('A13:D13','Completed jobs entered','B15','=COUNTA(\'JOB LOG\'!A10:A34)','0'),
           ('E13:G13','Actual sales before tax','E15','=SUM(\'JOB LOG\'!E10:E34)',MONEY),
           ('H13:J13','Observed contribution','H15','=SUM(\'JOB LOG\'!K10:K34)',MONEY),
           ('K13:O13','Observed margin','K15','=IF(E15>0,H15/E15,0)',PCT)]
    for rg,label,at,f,nf in boxes:
        ov.merge_cells(rg); put(ov,rg.split(':')[0],label)
        ov.get_range(rg).format={'fill':NAVY2,'font':{'color':WHITE,'bold':True,'size':10},'row_height':28}
        formula(ov,at,f)
        ov.get_range(at).format={'fill':PALE,'font':{'color':TEAL,'bold':True,'size':20},'row_height':39}
        ov.get_range(at).set_number_format(nf)
    merge_label(ov,'A19:O19','WORKFLOW / WHAT MATTERS',fill=TEAL,font_size=13)
    guidance=[
      '1. SETTINGS -> Review costs and sales tax; mark READY after checking.',
      '2. SERVICES -> Replace illustrative hours and supplies with your data.',
      '3. QUICK QUOTE -> Build a cost-based quote, then inspect CLIENT QUOTE.',
      '4. JOB SCENARIOS -> Compare up to 25 bids and service mixes.',
      '5. JOB LOG -> Enter actual project results to learn what earned money.',
      '6. Never treat contribution as accounting net profit or sales tax as revenue.',
    ]
    for i,t in enumerate(guidance,21):
        ov.merge_cells(f'A{i}:O{i}');put(ov,f'A{i}',t)
        ov.get_range(f'A{i}:O{i}').format={'fill':WHITE if i%2 else PALE,'font':{'color':INK,'size':11},'row_height':29}
    # important formula guard and sample cue
    ov.merge_cells('A29:O29');formula(ov,'A29','=IF(SETTINGS!B23="READY","ASSUMPTIONS MARKED READY — REVIEW ALL OUTPUTS","SETUP REQUIRED — GO TO SETTINGS AND REVIEW BLUE CELLS")')
    highlight(ov,'A29:O29',YELLOW,'#80550B',True)
    if sample:
        ov.merge_cells('A31:O31');put(ov,'A31','DEMONSTRATION — FICTIONAL VALUES / NOT A CUSTOMER CASE STUDY')
        highlight(ov,'A31:O31',YELLOW,'#80550B',True)
    return wb


def build():
    CUSTOMER.mkdir(parents=True,exist_ok=True)
    EXAMPLES.mkdir(parents=True,exist_ok=True)
    blank=make_book(False)
    SpreadsheetFile.export_xlsx(blank).save(str(CUSTOMER/'Cleaning_Pricing_Calculator.xlsx'))
    print('BLANK export ok')
    example=make_book(True)
    for key in ['QUICK QUOTE!F11:F27','OVERVIEW!A7:L16','JOB SCENARIOS!J10:Q13']:
        try:
            chk=example.inspect({'kind':'table','range':key,'include':'values,formulas','table_max_rows':18,'table_max_cols':9})
            print('INSPECT '+key+' '+chk.ndjson[:2400])
        except Exception as ex:print('INSPECT WARN',key,type(ex).__name__,str(ex)[:200])
    SpreadsheetFile.export_xlsx(example).save(str(EXAMPLES/'Cleaning_Pricing_Calculator_FICTIONAL_DEMO.xlsx'))
    print('DEMO export ok')
    for sheet_name,area,file in [
        ('OVERVIEW','A1:O26','dashboard_preview.png'),
        ('QUICK QUOTE','A1:I27','quote_builder_preview.png'),
        ('CLIENT QUOTE','A1:H26','customer_quote_preview.png'),
        ('JOB SCENARIOS','A1:Q17','scenario_preview.png')]:
        try:
           blob=example.render({'sheet_name':sheet_name,'range':area,'scale':1.5})
           blob.save(str(BASE/'marketing'/'previews'/file))
           print('RENDERED',file)
        except Exception as ex:
           print('RENDER ERROR',file,type(ex).__name__,str(ex)[:300])
    try:
        errs=example.inspect({'kind':'match','search_term':'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A',
                         'options':{'use_regex':True,'max_results':40}})
        print('ERROR SCAN',errs.ndjson[:2600])
    except Exception as ex:print('ERROR SCAN WARN',ex)

if __name__=='__main__':build()
