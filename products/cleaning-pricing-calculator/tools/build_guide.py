"""Optional source to rebuild the existing Quick_Start_Guide.pdf with ReportLab.

Customers do not need this package. This script does not connect to internet.
"""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable

BASE=Path(__file__).resolve().parents[1]
PDF=BASE/'customer'/'Quick_Start_Guide.pdf'
C=colors.HexColor
NAVY=C('#13263A'); TEAL=C('#0A837A'); MUTED=C('#556879'); LIGHT=C('#EFF6FF'); PALE=C('#F3F7FA'); GOLD=C('#D59C38'); AMBER=C('#FFF1C5')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='KickerX',fontName='Helvetica-Bold',fontSize=10,leading=13,textColor=TEAL,spaceAfter=10))
styles.add(ParagraphStyle(name='H1X',fontName='Helvetica-Bold',fontSize=24,leading=28,textColor=NAVY,spaceAfter=10))
styles.add(ParagraphStyle(name='H2X',fontName='Helvetica-Bold',fontSize=15,leading=19,textColor=NAVY,spaceBefore=12,spaceAfter=8))
styles.add(ParagraphStyle(name='H3X',fontName='Helvetica-Bold',fontSize=11,leading=15,textColor=TEAL,spaceBefore=10,spaceAfter=5))
styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=9.7,leading=15,textColor=NAVY,spaceAfter=8))
styles.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=8.5,leading=12,textColor=MUTED,spaceAfter=6))
styles.add(ParagraphStyle(name='CellX',fontName='Helvetica',fontSize=9,leading=12,textColor=NAVY))
styles.add(ParagraphStyle(name='CellBoldX',fontName='Helvetica-Bold',fontSize=9,leading=12,textColor=NAVY))
styles.add(ParagraphStyle(name='TagX',fontName='Helvetica-Bold',fontSize=8,leading=11,textColor=TEAL))

def P(s,style='BodyX'):return Paragraph(s,styles[style])
def panel(txt):
    t=Table([[P(txt,'SmallX')]],colWidths=[488])
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),AMBER),('BOX',(0,0),(-1,-1),.6,GOLD),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    return t

def bullet(title,desc):
    return P(f'<font color="#0A837A"><b>{title}</b></font> {desc}')

def table(rows,widths,header=True):
    converted=[[P(str(v),'CellBoldX' if header and i==0 else 'CellX') for v in r] for i,r in enumerate(rows)]
    tb=Table(converted,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.3,C('#DAE4E7'))]
    if header:commands.extend([('BACKGROUND',(0,0),(-1,0),C('#E3F4F0')),('LINEBELOW',(0,0),(-1,0),1,TEAL)])
    tb.setStyle(TableStyle(commands))
    return tb

def footer(canvas,doc):
    canvas.saveState()
    w,h=doc.pagesize
    canvas.setStrokeColor(C('#DFE8ED')); canvas.line(48,48,w-48,48)
    canvas.setFillColor(MUTED);canvas.setFont('Helvetica',8)
    canvas.drawString(48,33,'CLEANING PRICING TOOLKIT  /  CUSTOMER GUIDE')
    canvas.drawRightString(w-48,33,f'V1.0  /  PAGE {doc.page}')
    canvas.restoreState()

def create():
    PDF.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(PDF),pagesize=(595.28,841.89),topMargin=44,bottomMargin=66,leftMargin=54,rightMargin=54,title='Cleaning Pricing & Profit Toolkit — Quick Start',author='Cleaning Pricing Toolkit',subject='Offline Excel user instructions; fictional examples')
    elements=[]
    elements.extend([P('EXCEL TOOLKIT  /  CUSTOMER EDITION','KickerX'),P('Price cleaning jobs with<br/>more consistent math.','H1X'),P('QUICK START GUIDE  •  VERSION 1.0','KickerX'),Spacer(1,12)])
    elements.append(panel('<b>Important:</b> All sample wages, supply costs, hours and quote prices are fictional teaching values. Enter your own actual costs and confirm your sales-tax rules before making a customer quote. The workbook does not guarantee profit.'))
    elements.extend([Spacer(1,16),P('Start in six simple steps','H2X')])
    steps=[
        ('1  OPEN THE BLANK WORKBOOK','Open <b>Cleaning_Pricing_Calculator.xlsx</b> in desktop Microsoft Excel. Save a working copy. The example workbook is only a demonstration.'),
        ('2  CONFIGURE SETTINGS','Replace blue values with your loaded labor cost, mileage, overhead, contingency, target margin, estimated payment fees, minimum price, rounding step and applicable sales tax.'),
        ('3  ADJUST SERVICES','Update default <b>hours per employee</b> and per-job supply costs. These are example service names; change supported entries in place.'),
        ('4  ENTER ONE JOB','In <b>QUICK QUOTE</b>, select a service and enter crew size, paid hours, mileage, extra costs and discount. Check that status reads <b>READY TO REVIEW</b>.'),
        ('5  REVIEW THE CUSTOMER DRAFT','Open <b>CLIENT QUOTE</b>, which hides your cost breakdown. Verify the scope, tax, customer details and legal terms before sharing.'),
        ('6  PLAN AND IMPROVE','Use <b>JOB SCENARIOS</b> to compare up to 25 estimates, then manually record real completed-job costs in <b>JOB LOG</b>.'),
    ]
    for a,b in steps:elements.append(bullet(a,b))
    elements.append(Spacer(1,8));elements.append(P('<b>Blue cells</b> are editable inputs. <b>Dark text</b> shows calculated values. <b>Teal totals</b> emphasize the quote. Orange review messages need attention.','SmallX'))
    elements.append(PageBreak())
    elements.extend([P('What each tab does','H1X'),Spacer(1,6)])
    elements.append(table([
      ['TAB','USE IT FOR'],
      ['READ ME','How to start, review and understand color conventions.'],
      ['OVERVIEW','Snapshot of planned quotes and manually-entered actual jobs.'],
      ['QUICK QUOTE','Build one cost-based service estimate; see internal margin.'],
      ['CLIENT QUOTE','Draft amount to communicate to customers; no internal costs shown.'],
      ['JOB SCENARIOS','Compare up to 25 possible jobs using the same assumptions.'],
      ['JOB LOG','Record actual money received and expenses after a job.'],
      ['SERVICES','Edit service hours per employee and supplies.'],
      ['SETTINGS','Your operating cost and quoting assumptions.'],
    ],[125,362]))
    elements.extend([Spacer(1,12),P('Critical setup details','H2X')])
    elements.append(bullet('Loaded hourly labor cost','Enter the actual cost of a worker-hour including employer burden; do not confuse employee cost with the rate charged to customers.'))
    elements.append(bullet('Hours per employee','For two workers, each on site 3 hours, the workbook counts <b>six</b> paid labor hours. Paid travel time per employee is additional.'))
    elements.append(bullet('Overhead and driving','Overhead is per job; mileage is round-trip kilometers times your entered vehicle allowance. Fuel and insurance should not be double counted if already included.'))
    elements.append(bullet('Taxes','The default 0% tax is an <b>unconfigured placeholder</b>. Verify any tax collection duties and rates for your jurisdiction before issuing real quotes.'))
    elements.append(bullet('Fee assumption','The processing rate is a rough percentage; real payment processors may charge fixed, cross-border or conversion fees as well.'))
    elements.append(PageBreak())
    elements.extend([P('The pricing method','H1X'),P('Designed to make the math visible and reproducible.','SmallX')])
    elements.append(table([
        ['1','Total paid labor','Crew × (hours per person onsite + paid travel) × loaded hourly cost'],
        ['2','Operating cost before buffer','Labor + supplies + vehicle allowance + overhead'],
        ['3','Modeled job cost','Operating cost + rounded contingency allowance'],
        ['4','Price for your margin','Cost ÷ (1 − target margin − estimated payment fee rate)'],
        ['5','Pre-tax customer amount','Round list price upward; subtract any entered discount.'],
        ['6','Customer total','Pre-tax amount + estimated applicable sales tax.'],
        ['7','Contribution','Pre-tax amount − modeled job cost − estimated payment fee.'],
    ],[23,157,307]))
    elements.extend([Spacer(1,14),P('FICTIONAL worked example','H2X')])
    elements.append(table([
        ['MODEL INPUT / STEP','ILLUSTRATIVE CAD'],
        ['2 staff × (3 onsite + 0.25 travel) × $25/h','$162.50 labor'],
        ['Base + extra supplies','$13.00'],
        ['12 km × $0.55','$6.60'],
        ['Job overhead','$14.00'],
        ['Operating subtotal','$196.10'],
        ['8% contingency','$15.69'],
        ['Modeled cost','$211.79'],
        ['List price rounded up','$330.00'],
        ['Discount','−$10.00'],
        ['Customer amount BEFORE tax','$320.00'],
        ['3% processing-fee estimate','$9.60'],
        ['Estimated contribution','$98.61'],
    ],[330,157]))
    elements.append(P('The contribution margin for this fictional example is 30.8%. It is not accounting net profit, a typical cleaning price or a forecast of earnings.','SmallX'))
    elements.append(PageBreak())
    elements.extend([P('Quote workflow & review checks','H1X')])
    elements.append(P('Before you share a quote','H2X'))
    for t in [
        'Confirm cleaning tasks, property access, expected condition, excluded work and cancellation or change terms with the customer.',
        'Set your own wage, insurance, travel and overhead assumptions. Check whether extra labor, disposal or specialty products change the scope.',
        'Verify your tax status and applicable tax rate. The workbook does not research tax law or determine if you must register.',
        'Check QUICK QUOTE status = READY TO REVIEW; review amounts, customer name, date and draft terms on CLIENT QUOTE.',
        'Export the approved CLIENT QUOTE as PDF using your spreadsheet application if you need a printable file. Never treat the tab as a completed legal contract.',
    ]:elements.append(bullet('•',t))
    elements.append(P('If you see a warning','H2X'))
    elements.append(table([
        ['MESSAGE','RESPONSE'],
        ['SELECT SERVICE','Choose a service in the input dropdown.'],
        ['INVALID / CHECK SERVICE','Use an exact service name listed on SERVICES.'],
        ['CHECK INPUTS','Review crew, times, negative values, margin+fee and rounding.'],
        ['REVIEW SETTINGS','Check costs and tax; set SETTINGS review flag to READY only after verification.'],
    ],[163,324]))
    elements.append(Spacer(1,15))
    elements.append(panel('<b>Privacy:</b> Use buyer-authorized data only. Do not put bank credentials, government ID numbers, residential addresses or unnecessary private customer records into quote examples, screenshots or public files.'))
    elements.append(PageBreak())
    elements.extend([P('Important limitations & license','H1X')])
    elements.append(P('Business judgment remains essential','H2X'))
    elements.append(P('This downloadable workbook is an offline tool for internal administrative calculations. It does not take payments, invoice customers, access bank records, calculate your actual taxes or guarantee an operating margin. Demand for the product and successful quote acceptance must be tested.'))
    elements.append(P('Changes in wages, travel, supplies, bad debt, discounts, refunds, paid marketing, accounting costs and unexpected work can materially change real outcomes. Do not assume the fictional defaults are market rates.'))
    elements.append(P('What the purchase license allows','H2X'))
    elements.append(P('A purchaser can use and modify the workbook for internal operations in one business, keep private backups and export their own customer quotes. Redistribution, resale, and hosting a downloadable copy of the template for others are not granted. Full terms are in LICENSE_AND_DISCLAIMER.txt.'))
    elements.append(P('Compatibility & files','H2X'))
    elements.append(P('The customer package includes a blank .xlsx template, a separately named FICTIONAL DEMO workbook, this guide, a start note and the license. Neither workbook contains macros, external links or scripts that upload your information. It is authored for recent Microsoft Excel; other spreadsheet applications may differ.'))
    elements.append(P('Support and next steps','H2X'))
    elements.append(P('Use the legitimate seller contact supplied in the order confirmation for product defects. Keep your original download unchanged, and make a separate working copy. Seller support promises and refund rights depend on the final storefront terms and applicable law; this guide does not override them.'))
    elements.append(Spacer(1,22));elements.append(HRFlowable(width='100%',color=TEAL,thickness=1.4))
    elements.append(Spacer(1,10));elements.append(P('VERSION 1.0  |  NO COMPANY OR REAL CUSTOMER RESULTS ARE REPRESENTED IN THE FICTIONAL EXAMPLES.','TagX'))
    doc.build(elements,onFirstPage=footer,onLaterPages=footer)
    print('PDF',PDF,'pages created')

if __name__=='__main__':create()
