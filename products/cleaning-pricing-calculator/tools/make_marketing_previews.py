"""Compose accurate marketing previews from already-rendered FICTIONAL spreadsheet screenshots.

Pillow is optional authoring dependency; buyers only receive PDFs and XLSX.
No stock imagery, fake testimonials or invented customer results are used.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'marketing'/'previews'; OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NAVY=(16,37,54); BLUE=(20,53,74); TEAL=(9,129,118); PALE=(224,248,242); WHITE=(255,255,255); MUTED=(158,183,196)

def f(sz,bold=False):return ImageFont.truetype(BOLD if bold else FONT,sz)

def text(draw,xy,t,size,fill=WHITE,bold=False,spacing=12):
    draw.multiline_text(xy,t,font=f(size,bold),fill=fill,spacing=spacing)

def pill(draw,rect,title,fill=(28,68,79),txt=(225,248,242)):
    draw.rounded_rectangle(rect,radius=22,fill=fill)
    x1,y1,x2,y2=rect
    b=draw.textbbox((0,0),title,font=f(22,True))
    draw.text((x1+(x2-x1-(b[2]-b[0]))/2,y1+(y2-y1-(b[3]-b[1]))/2-2),title,font=f(22,True),fill=txt)

def rounded_screenshot(img, photo,box, border=13):
    x,y,w,h=box
    original=Image.open(photo).convert('RGB')
    ratio=min((w-border*2)/original.width,(h-border*2)/original.height)
    s=original.resize((int(original.width*ratio),int(original.height*ratio)),Image.Resampling.LANCZOS)
    shadow=Image.new('RGBA',(w+52,h+52),(0,0,0,0))
    ImageDraw.Draw(shadow).rounded_rectangle((22,15,w+27,h+20),radius=25,fill=(2,20,25,110))
    blur=shadow.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(blur,(x-10,y-5))
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((x,y,x+w,y+h),radius=24,fill=(246,250,252))
    ix=x+(w-s.width)//2;iy=y+(h-s.height)//2
    img.paste(s,(ix,iy))

def background():
    im=Image.new('RGBA',(1600,900),NAVY+(255,))
    d=ImageDraw.Draw(im)
    for i in range(0,1600,28):
        d.line((i,0,i,900),fill=(30,66,79,65),width=1)
    for y in range(0,900,28):
        d.line((0,y,1600,y),fill=(30,66,79,55),width=1)
    d.ellipse((1120,-360,1910,490),fill=(10,96,91,60))
    d.rectangle((0,0,16,900),fill=TEAL+(255,))
    return im

def save_cover():
    im=background();d=ImageDraw.Draw(im)
    text(d,(78,67),'CLEANING BUSINESS  /  EXCEL TOOLKIT',22,PALE,True)
    text(d,(78,149),'Price cleaning\njobs with clarity.',60,WHITE,True,22)
    d.rounded_rectangle((76,348,185,357),radius=4,fill=TEAL)
    text(d,(78,392),'Edit your costs. Compare scenarios.\nPrepare consistent cleaning quotes.',27,(222,238,241),False,16)
    pill(d,(76,574,306,637),'NO MACROS');pill(d,(323,574,535,637),'8 EXCEL TABS')
    pill(d,(76,658,535,720),'QUOTE + COST TRACKING')
    rounded_screenshot(im,OUT/'quote_builder_preview.png',(680,121,850,646))
    d=ImageDraw.Draw(im)
    text(d,(75,823),'FICTIONAL DEMO · EDITABLE EXCEL WORKBOOK · NO GUARANTEED BUSINESS RESULTS',19,MUTED,True)
    im.convert('RGB').save(OUT/'01_product_cover.png',optimize=True)

def save_showcase(name,label,headline,subtitle,source):
    im=background();d=ImageDraw.Draw(im)
    text(d,(65,54),label,20,PALE,True)
    text(d,(65,113),headline,45,WHITE,True)
    text(d,(65,187),subtitle,24,(219,236,238))
    rounded_screenshot(im,OUT/source,(75,281,1450,515))
    d=ImageDraw.Draw(im);text(d,(77,835),'PREVIEW USES FICTIONAL DATA — COSTS AND TAX SETTINGS MUST BE REVIEWED',18,MUTED,True)
    im.convert('RGB').save(OUT/name,optimize=True)

if __name__=='__main__':
    save_cover()
    save_showcase('02_quote_builder.png','FEATURE 01  /  COST-BASED PRICING','One job. A clearer price.','Labor + mileage + supplies + overhead + margin + discount', 'quote_builder_preview.png')
    save_showcase('03_customer_quote.png','FEATURE 02  /  CUSTOMER HANDOFF','A clean draft for your customer.','Present the quote without displaying the internal cost breakdown','customer_quote_preview.png')
    save_showcase('04_scenario_planner.png','FEATURE 03  /  WHAT-IF PLANNER','Compare 25 potential jobs.','Adjust crew, hours and cost assumptions across multiple scenarios','scenario_preview.png')
    for x in sorted(OUT.glob('0*.png')):print(x.name,x.stat().st_size)
