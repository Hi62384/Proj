"""Render original customer documents to separate QA files."""
import subprocess,json
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from review_files import ROOT,REPO,INV
qa=ROOT/'qa';pdfs=qa/'pdf';pdfs.mkdir(exist_ok=True)
lo='C:/Program Files/LibreOffice/program/soffice.com'
profile=(qa/'lo-profile').as_uri()
sources=[qa/'cleaning_demo.xlsx',INV/'customer/product.xlsx',INV/'customer/Instructions.docx']
proc=subprocess.run([lo,'-env:UserInstallation='+profile,'--headless','--convert-to','pdf','--outdir',str(pdfs),*[str(p) for p in sources]],capture_output=True,text=True,timeout=120)
assert proc.returncode==0,proc.stderr
guide=REPO/'products/cleaning-pricing-calculator/customer/Quick_Start_Guide.pdf'
sources=[pdfs/'cleaning_demo.pdf',pdfs/'product.pdf',pdfs/'Instructions.pdf',guide]
poppler=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
report=[]
for src in sources:
    folder=qa/('render-'+src.stem);folder.mkdir(exist_ok=True)
    result=subprocess.run([str(poppler),'-scale-to','1300','-png',str(src),str(folder/'page')],capture_output=True,text=True,timeout=90)
    assert result.returncode==0,result.stderr
    pages=sorted(folder.glob('page-*.png'));report.append({'source':src.name,'pages':len(pages)})
    canvas=Image.new('RGB',(1000,math_rows:=((len(pages)+1)//2)*700),'#dce3e8')
    draw=ImageDraw.Draw(canvas)
    for i,path in enumerate(pages):
        im=Image.open(path).convert('RGB');im.thumbnail((480,650));x=(i%2)*500+(500-im.width)//2;y=(i//2)*700+30
        canvas.paste(im,(x,y));draw.text(((i%2)*500+15,(i//2)*700+8),f'{src.name} - page {i+1}',fill='black')
    canvas.save(folder/'contact-sheet.png')
(ROOT/'render-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
