"""Combine prepared draft business kits into one offline multi-product showcase."""
from __future__ import annotations
from html import escape
import json
from pathlib import Path

from .config import PRIVATE, SetupError, init_private, safe_id


def create_preview(root: Path = PRIVATE) -> Path:
    init_private(root)
    kits=root/'launchkits'
    items=[]
    if kits.exists():
        for path in sorted(kits.iterdir()):
            if not path.is_dir() or path.is_symlink():continue
            try:safe_id(path.name)
            except SetupError:continue
            config=path/'product_config.json'
            if not config.exists():continue
            data=json.loads(config.read_text(encoding='utf-8'))
            if data.get('opportunity_id')!=path.name or data.get('stage')!='research_draft':
                continue
            items.append({k:data.get(k,'') for k in ('opportunity_id','title','industry','model','indicative_price_cad')})
    cards=[]
    for r in items:
        cards.append('<article><div class="tag">'+escape(str(r['industry']))+'</div><h2>'+escape(str(r['title']))+
            '</h2><p>Opportunity ID '+escape(str(r['opportunity_id']))+' · Mode '+escape(str(r['model']))+
            '</p><strong>Hypothetical CAD '+escape(str(r['indicative_price_cad']))+
            '</strong><p><a href="../launchkits/'+escape(str(r['opportunity_id']),quote=True)+
            '/LANDING_PREVIEW.html">Open internal draft</a></p></article>')
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portfolio preview — NOT A STORE</title>
<style>body{background:#101827;color:#edf4ff;font:16px/1.5 system-ui,sans-serif;max-width:1200px;margin:5vh auto;padding:20px}h1{font-size:40px}header p{color:#b9cbe2}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}article{background:#1b2a41;border:1px solid #364b69;padding:22px;border-radius:16px}article h2{font-size:19px}.tag{font-size:12px;color:#b2dbff}a{color:#8dd7ff}</style>
<header><p>PRIVATE PREVIEW · NO PRODUCTS FOR SALE · NO CHECKOUT · NO BUYER VALIDATION</p><h1>Multi-industry catalogue preview</h1><p>This is generated from draft kits. A single future storefront could sell unrelated original products where permitted, but each offer needs actual buyer validation and approval.</p></header><main>'''+''.join(cards)+'''</main><p>Nothing here has been published, bought or connected to a merchant account.</p></html>'''
    target=root/'previews'/'catalogue.html';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(html,encoding='utf-8')
    return target
