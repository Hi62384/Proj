"""Rebuild known research artifacts only. No network, credentials or live actions."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from .model import ROOT, DATA, construct, factory_rows, safe_csv


def dump(obj:object)->str:
    return json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n'


def csv_text(rows:list[dict], fields:list[str]|None=None)->str:
    fields=fields or sorted({k for r in rows for k in r})
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n')
    w.writeheader()
    for row in rows:
        w.writerow({k:safe_csv(row.get(k)) for k in fields})
    return '\ufeff'+stream.getvalue()


def display_range(v, unit=''):
    if v is None:return 'Not established'
    return str(v[0])+unit if v[0]==v[1] else f'{v[0]}–{v[1]}{unit}'


def md(s:object)->str:
    return str(s).replace('|','\\|').replace('\n',' ').replace('\r',' ')


def flat_row(r:dict)->dict:
    return {'id':r['id'],'name':r['name'],'category_id':r['category_id'],'category':r['category'],
      'subcategory_id':r['subcategory_id'],'subcategory':r['subcategory'],'group':r['group'],
      'industry':r['industry'],'buyer':r['buyer'],'deliverable':r['deliverable'],'model':r['model'],
      'mode':r['mode'],'origin':r['origin'],'income_type':r['income_type'],'risk':r['risk'],
      'whole_business_passivity_prior':r['ratings']['passivity'],'routine_fulfillment_prior':r['ratings']['fulfillment'],
      'public_privacy_prior':r['ratings']['public_privacy'],'profit_mechanism_prior':r['ratings']['profit_potential'],
      'low_touch_score_prior':r['score_low_touch'],'fast_cash_score_prior':r['score_fast_cash'],
      'price_range_hypothesis_cad':display_range(r['economics']['asking_price_hypothesis']),
      'weekly_hours_hypothesis':display_range(r['economics']['weekly_total_hours_hypothesis']),
      'first_sale_days_hypothesis':display_range(r['economics']['first_sale_days_hypothesis']),
      'expected_monthly_profit':'unknown','guaranteed_anonymity':False,'paid_demand_verified':False,
      'privacy_review':r['privacy']['seller_specific_disclosure_review'],'human_work':r['automation']['human_work'],
      'acquisition':r['acquisition'],'first_experiment':r['first_experiment'],'gate':r['gate'],
      'stop_rule':r['stop_rule'],'source_ids':';'.join(r['source_ids']),
      'original_source':r['original_source_reference'],'classification_basis':r['classification_basis'],
      'related_ids':';'.join(r['related_to']),'as_of':r['as_of']}


def category_md(c:dict,lib:dict)->str:
    rows=[r for r in lib['records'] if r['category_id']==c['id']]
    fresh=[r for r in rows if r['id'].startswith('CUR-')]
    out=[f"# {c['id']} · {c['name']}",'',f"**Group:** {c['group']} · **Records:** {len(rows)} · **New curated hypotheses:** {len(fresh)}",
         '', '[Library guide](../../README.md) · [Offline browser](../../../Opportunity_Library.html) · [Methodology](../../docs/METHODOLOGY.md)',
         '', '## Commercial thesis', '',c['strategy'],'', '**Principal obstacle:** '+c['main_obstacle'],'',
         'These are screened concepts, not verified profitable businesses. Current category/platform sources establish alternatives and constraints, not willingness to pay for our exact products. Test-price ranges, effort and scores are unmeasured planning assumptions.',
         '', '## Research: what the primary references actually establish','']
    srcs={s['id']:s for s in lib['sources']}
    for sid in c['source_ids']:
        s=srcs[sid]
        out.extend([f"### {s['title']}",s['finding'],f"[{sid}: primary reference]({s['url']}) · Checked {s['checked_on']} · Evidence type: {s['kind']}.",f"**Limit:** {s['limits']}",''])
    out.extend(['## Six additional concrete experiments',''])
    for r in fresh:
        out.extend([f"### {r['id']} · {r['name']}",f"**Buyer:** {r['buyer']}  ",f"**Deliverable:** {r['deliverable']}  ",
         f"**Mechanism:** {r['model']} · **Unvalidated asking-price range:** {display_range(r['economics']['asking_price_hypothesis'],' CAD')}.",
         '',f"**First test:** {r['first_experiment']}",f"**Distribution path:** {r['acquisition']}",
         f"**What can be automated:** {r['automation']['automatable']}",f"**Human work remains:** {r['automation']['human_work']}",
         f"**Specific obstacle:** {r['risk_note']}",f"**Public privacy:** {r['privacy']['notes']}",
         f"**Advance only when:** {r['gate']}",f"**Stop or revise:** {r['stop_rule']}",
         '**Evidence:** Category-level references above; no paid customer for this offer was verified.',''])
        if r['related_to']:out.extend(['**Related workflows, not independent market proof:** '+', '.join(r['related_to'])+'.',''])
    out.extend(['## Complete category membership, grouped by subcategory','',
      'Every ID has one primary home. Industry and mechanism tags remain searchable in the offline browser. An asterisk marks an inherited domain-default classification that deserves precise subcategory review.',''])
    for sub in c['subcategories']:
        group=[r for r in rows if r['subcategory_id']==sub['id']]
        out.extend([f"### {sub['id']} · {sub['name']} ({len(group)})",'', '| ID | Opportunity | Model | Industry / buyer tag | Review |','|---|---|---|---|---|'])
        for r in sorted(group,key=lambda x:x['id']):
            out.append('| '+' | '.join(md(x) for x in [r['id']+('*' if r['classification_review_needed'] else ''),r['name'],r['mode'],r['industry'],r['risk']])+' |')
        out.append('')
    out.extend(['## Validation questions still unanswered','',
     'Who has a current, repeated problem and authority to buy? What do they use now, including free alternatives? Why would this offer be better enough to pay for? Which channel permits contacting them? What is the real acquisition cost and all-in support time? Which seller and identity details will buyers see? Which rights, data and professional rules constrain delivery?',
     '', 'Do not open an account or pay for tools merely to fill a category. Compare one cheap paid test with the existing CSV offer or another validated line. Keep private customer files and secrets out of this research tree.', '',
     '**Source freshness:** This page is generated from the 14 October 2026 snapshot. Recheck material policies and costs at launch. Rebuilding this page is not fresh research.',''])
    return '\n'.join(out)


def source_md(lib:dict)->str:
    out=['# Primary-source research register','','69 references consulted for this reorganization. Exact-offer customers, sales and provider approvals were not verified. Original source registers are preserved separately and are not claimed freshly revisited.','',
     'Facts below are summarized; prices and terms are snapshots. Read the full current primary source before a commercial commitment. All fields explicitly distinguish category/infrastructure evidence from a proven offer.','']
    for s in lib['sources']:
        out += [f"<a id=\"{s['id'].lower()}\"></a>",f"## {s['id']} · {s['title']}",'',s['finding'],'',
                f"[Primary source]({s['url']}) · Checked {s['checked_on']} · Kind: {s['kind']}",
                f"Retrieval: {s['retrieval']}.",f"**Not established:** {s['limits']}",'']
    return '\n'.join(out)


def readme_md(lib:dict)->str:
    n=lib['counts']
    out=['# Organized Opportunity Library','','**Primary entry point:** open [`../Opportunity_Library.html`](../Opportunity_Library.html).',
     '',f"{n['categories']} categories · {n['subcategories']} subcategories · {n['records']:,} research records · {n['fresh_primary_references']} current primary references.",
     '', 'There are 1,296 preserved records plus 216 new hypotheses. Two are separate personal-capital research notes, not businesses. Every idea has one primary category plus industry and mechanism tags. None has independently verified paid demand in this dataset.','',
     '## Find things quickly','',
     '| Need | Location |','|---|---|',
     '| Browse / filter / compare / save IDs / export a draft | [Offline browser](../Opportunity_Library.html) |',
     '| Understand scores, missing data and limitations | [Methodology](docs/METHODOLOGY.md) |',
     '| Identity, AI content and platform constraints | [Privacy and platform matrix](docs/PRIVACY_AND_PLATFORMS.md) |',
     '| Facts and primary links | [69-source register](docs/SOURCES.md) |',
     '| Go from research to a paid test | [Operating workflow](docs/OPERATING_WORKFLOW.md) |',
     '| Programmatic catalogue | [JSON](data/catalog.json) / [CSV](data/catalog.csv) |',
     '| Edit category and subcategory assignments | [Taxonomy](data/taxonomy.json) / [classifications](data/classifications.json) |',
     '| Edit new hypotheses | [Curated additions](data/curated_additions.json) |',
     '| Industry facet / coverage audit | [Industry index](data/industry_index.json) / [coverage](data/coverage.json) |',
     '', '## Categories','', '| Category | Subcategories | Records |','|---|---:|---:|']
    for c in lib['categories']:
        count=sum(r['category_id']==c['id'] for r in lib['records'])
        out.append(f"| [{c['id']} · {c['name']}](categories/{c['slug']}/README.md) | {len(c['subcategories'])} | {count} |")
    out += ['', '## Existing tools remain intact','',
      'The original `research_merge/` files, the large master plan, legacy reports and financial models remain in place. The factory reads the optional expanded CSV while the original Phase-0 command can still use its old index. FAST-O01 remains the reporting offer; existing generated customer/first-sales packs are not overwritten. VaultDesk is unrelated and unchanged.',
      '', 'The browser stores only selected IDs in local browser storage. It does not encrypt customer data and must never be used as a credential vault. There are no network clients, live accounts, trades, payments or messages in this library.',
      '', '## Rebuild and test','', '```powershell',
      'python -m opportunity_library.build', 'python -m opportunity_library.build --check',
      'python -m unittest discover -s opportunity_library/tests -v',
      'python -m opportunity_library.cli search --category C01 --limit 6',
      'python -m opportunity_library.cli show CUR-01-01', '```','',
      'Generated category pages are views of source data, not files to hand-edit. New evidence requires a reviewed source entry; rebuilding never verifies current demand.','']
    return '\n'.join(out)


def render_outputs(root:Path=ROOT)->dict[str,bytes]:
    lib=construct(root)
    outputs={'opportunity_library/data/catalog.json':dump(lib),
       'opportunity_library/data/catalog.csv':csv_text([flat_row(r) for r in lib['records']]),
       'opportunity_library/data/factory_catalog.csv':csv_text(factory_rows(lib,root)),
       'opportunity_library/README.md':readme_md(lib),
       'opportunity_library/docs/SOURCES.md':source_md(lib)}
    counts=Counter(r['category_id'] for r in lib['records'])
    coverage={'status':'STRUCTURE_VALIDATED_BY_BUILDER_NOT_COMMERCIAL_VALIDATION','counts':lib['counts'],
        'categories':dict(counts),'subcategories':dict(Counter(r['subcategory_id'] for r in lib['records'])),
        'classification_review_needed':[r['id'] for r in lib['records'] if r['classification_review_needed']],
        'source_risk_flags_preserved':True,'expected_profit_unknown':True,'source_snapshot_sha256':lib['original_sha256'],
        'related_offer_links':[{'id':r['id'],'related':r['related_to'],'relation':'related workflow, not proved equivalent'} for r in lib['records'] if r['related_to']],
        'raw_count_not_unique_market_count':True,'note':'Do not use historical crosswalk as automatic deduplication. No records were merged/deleted.'}
    outputs['opportunity_library/data/coverage.json']=dump(coverage)
    for c in lib['categories']:outputs[f"opportunity_library/categories/{c['slug']}/README.md"]=category_md(c,lib)
    template=(root/'opportunity_library/templates/library.html').read_text(encoding='utf-8')
    payload=json.dumps(lib,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    if template.count('__LIBRARY_JSON__')!=1:raise ValueError('Expected exactly one safe JSON placeholder')
    outputs['Opportunity_Library.html']=template.replace('__LIBRARY_JSON__',payload)
    return {p:s.encode('utf-8') for p,s in outputs.items()}


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args(argv)
    try:
        artifacts=render_outputs()
        changed=[]
        for rel,data in artifacts.items():
            path=ROOT/rel
            if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Refusing symlink/escaping output: '+rel)
            if path.is_file() and path.read_bytes()==data:continue
            changed.append(rel)
            if not args.check:
                path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_bytes(data);tmp.replace(path)
        if args.check and changed:
            print('Generated artifacts differ. Run python -m opportunity_library.build:\n'+'\n'.join(changed),file=sys.stderr);return 1
        print(('Checked' if args.check else 'Built')+f' {len(artifacts)} reproducible artifacts; {len(changed)} changed. Offline research only.');return 0
    except (ValueError,OSError,KeyError) as e:
        print('ERROR:',e,file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
