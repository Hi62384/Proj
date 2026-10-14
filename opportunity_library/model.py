"""Deterministic organization and clearly labelled research priors.

Raw research is never modified. Ratings concern potential operating properties,
not probabilities, forecasts, validated demand, or guarantees of privacy.
"""
from __future__ import annotations
from pathlib import Path
import csv
import hashlib
import json
import math
import re
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(__file__).resolve().parent / 'data'
AS_OF = '2026-10-14'
BASE_COMMIT = '57168d5d717a5d93a1c187738c9f0b5d3749c9d3'
SAFE_ID = re.compile(r'^[A-Za-z0-9_-]{1,80}$')
WEIGHTS = {'passivity':25,'profit_potential':25,'public_privacy':20,'acquisition':15,'speed':10,'evidence':5}
SPEED_WEIGHTS = {'speed':35,'profit_potential':25,'fulfillment':20,'evidence':10,'scale':10}
# Model priors. No sector or personal-interest bonus. Manual steps include sales.
PROFILES = {
 'F': dict(name='Fixed-scope service',passivity=2,profit_potential=4,public_privacy=2,acquisition=3,speed=5,fulfillment=3,scale=2,
           setup=[6,24],weekly=[4,14],cost=[0,150],first=[2,21],route='Relevant explicit purchase requests, permissioned introductions, or a small partner pilot.',
           automate='Intake validation, deterministic transformations, test fixtures, packaging and draft delivery notes.',
           manual='Qualifying buyers, scope agreement, ambiguous data, output acceptance, confidentiality and disputes.',
           gate='Two independent accepted paid jobs, bounded scope and measured contribution after sales/delivery time before expanding.',
           stop='Pause expansion when custom exceptions exceed the quote or focused buyer conversations reveal no willingness to pay.'),
 'R': dict(name='Managed recurring monitor',passivity=3,profit_potential=4,public_privacy=3,acquisition=2,speed=3,fulfillment=4,scale=4,
           setup=[16,60],weekly=[3,10],cost=[25,300],first=[7,45],route='Paid recurring pilot with an existing operator or referral partner; no unsolicited mass alerts.',
           automate='Authorized scheduled checks, retry confirmation, deduplicated alerts, quotas and monthly reports.',
           manual='Onboarding, alert investigation, changed inputs, support, incident response and renewal value.',
           gate='At least two genuine paid renewal or repeat-use signals plus a support/false-alert budget before recurring launch.',
           stop='Pause acquisition when alert noise, monitoring costs or retention defeat contribution.'),
 'D': dict(name='Self-service digital download',passivity=4,profit_potential=3,public_privacy=4,acquisition=2,speed=3,fulfillment=5,scale=4,
           setup=[12,50],weekly=[2,6],cost=[0,150],first=[7,75],route='Permitted original-product marketplace, useful sample, opt-in audience or a specialist distribution partner.',
           automate='Reproducible builds, compatibility tests, versioned downloads, licence records and documented onboarding.',
           manual='Original product QA, licensing, customer discovery, accessibility, refunds and compatibility updates.',
           gate='Three independent paid users who can complete the advertised task; test support time before adding variants.',
           stop='Revise after a bounded qualified-traffic test with no purchases; do not respond by mass-producing more files.'),
 'A': dict(name='Original licensed asset',passivity=4,profit_potential=3,public_privacy=4,acquisition=2,speed=3,fulfillment=5,scale=4,
           setup=[20,80],weekly=[2,6],cost=[0,250],first=[7,90],route='Eligible original-asset marketplace, honest previews and a useful sampler with clear commercial rights.',
           automate='File/format QA, original asset variant export, previews, packaging, licensing and digital fulfillment.',
           manual='Art direction, authorship/rights, compatibility, product usefulness, promotion and customer support.',
           gate='Buyers prefer the sample to relevant free/paid alternatives and at least two pay for a finished useful pack.',
           stop='Stop expanding a pack that fails a craft/time test or has no paid adoption after qualified demonstrations.'),
 'L': dict(name='Self-paced education',passivity=3,profit_potential=3,public_privacy=3,acquisition=2,speed=2,fulfillment=4,scale=4,
           setup=[25,100],weekly=[3,8],cost=[0,250],first=[14,120],route='Focused paid pilot lesson, relevant instructors or organization licences before a large course catalogue.',
           automate='Delivery, practice checks, source-controlled examples, enrolment and routine progress reporting.',
           manual='Teaching accuracy, accessibility, student questions, updates and truthful credentials.',
           gate='Paying learners demonstrate the intended learning outcome and support demand fits the price.',
           stop='Revise when learners cannot use the material or acquisition and support overwhelm margin.'),
 'P': dict(name='Licensed information product',passivity=2,profit_potential=4,public_privacy=4,acquisition=2,speed=2,fulfillment=4,scale=4,
           setup=[20,90],weekly=[4,12],cost=[0,400],first=[14,100],route='Source-linked sample for a specific decision maker; paid trial and partner distribution.',
           automate='Licensed ingestion, normalization, provenance, change comparison, packaging and subscriber delivery.',
           manual='Rights review, factual verification, missed-change checks, editorial judgement and renewal usefulness.',
           gate='Redistribution rights confirmed and paid repeat demand demonstrated; document coverage and omissions.',
           stop='Do not sell when source rights, freshness, false negatives or analyst workload are unresolved.'),
 'I': dict(name='Connector or integration',passivity=3,profit_potential=4,public_privacy=3,acquisition=3,speed=2,fulfillment=4,scale=4,
           setup=[24,100],weekly=[3,10],cost=[0,350],first=[7,75],route='Explicit authorized integration problem, native permitted marketplace or established implementation partner.',
           automate='Schema contracts, import/export, retry/deduplication, diagnostics and consented entitlement checks.',
           manual='Credentials/permissions, initial mapping, provider changes, support and production approval.',
           gate='Accepted read-only pilot, least privilege, rollback tests and paid repeat-use proof.',
           stop='Pause when API terms, maintenance, rejected permissions or custom configurations defeat reliability.'),
 'M': dict(name='Hosted software subscription',passivity=3,profit_potential=5,public_privacy=3,acquisition=2,speed=1,fulfillment=4,scale=5,
           setup=[40,160],weekly=[4,12],cost=[50,600],first=[21,150],route='Paid design partners or existing accepted workflows; a public SaaS launch alone is not acquisition.',
           automate='Billing events, access, quotas, jobs, telemetry, tested deployments and basic support triage.',
           manual='Security, onboarding, product quality, retention, customer acquisition, incidents and high-risk releases.',
           gate='Independent paid pilots, repeat usage, cancellation/tenant-isolation tests and an affordable operating reserve.',
           stop='No scale if retention, support, hosting cost or security cannot sustain the recurring promise.'),
 'C': dict(name='Audience, content or affiliate',passivity=2,profit_potential=3,public_privacy=4,acquisition=1,speed=1,fulfillment=4,scale=4,
           setup=[30,150],weekly=[5,15],cost=[0,350],first=[45,365],route='Useful original content, permitted search/community distribution and disclosed affiliate or sponsor relationships.',
           automate='Editorial assistance, original-source checks, scheduling via approved tools and broken-link monitoring.',
           manual='Fact-checking, editorial originality, audience acquisition, sponsor disclosure and continual refresh.',
           gate='A reachable audience and independently measured monetization; check native eligibility before production scale.',
           stop='Stop mass output when quality, originality, terms or unit economics fail; no purchased fake engagement.'),
 'X': dict(name='Directory or marketplace',passivity=2,profit_potential=4,public_privacy=3,acquisition=1,speed=1,fulfillment=3,scale=5,
           setup=[40,180],weekly=[6,18],cost=[50,700],first=[30,365],route='One useful verified directory/matching service with real supply and an explicitly paying demand side.',
           automate='Approved listings, expiry checks, matching support, subscriptions and transaction bookkeeping.',
           manual='Verification, cold-start distribution, trust/safety, moderation and two-sided support.',
           gate='Verified participants and actual payer value; no fabricated jobs, reviews, listings or buyer activity.',
           stop='Do not scale when either side is absent or moderation/support overwhelms revenue.'),
 'CAPITAL': dict(name='Personal capital research — not a business',passivity=None,profit_potential=None,public_privacy=None,acquisition=None,speed=None,fulfillment=None,scale=None,
           setup=None,weekly=None,cost=None,first=None,route='Not a business acquisition channel. No live trading or capital allocation is authorized.',
           automate='Only simulated recordkeeping, educational examples and risk-analysis calculations.',
           manual='Capital at risk, financial suitability, provider verification and qualified advice where needed.',
           gate='Separate capital ledger and suitability/risk review; no forecast returns or customer-money access.',
           stop='No credentials, trade execution or promised returns in this library.')
}

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8-sig'))

def number(value: Any) -> float | None:
    if value is None or value=='': return None
    try: n=float(value)
    except (TypeError,ValueError): return None
    return n if math.isfinite(n) else None

def optional_range(lo: Any, hi: Any) -> list[float] | None:
    lo,hi=number(lo),number(hi)
    return [lo,hi] if lo is not None and hi is not None else None

def safe_csv(value: Any) -> str:
    if value is None:return ''
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        if not math.isfinite(value):raise ValueError('Non-finite CSV number')
        return str(value)
    text=str(value)
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) or text.startswith(('\t','\r','\n')) else text

def weighted(ratings: dict[str,Any], weights:dict[str,int]) -> int | None:
    if any(ratings.get(k) is None for k in weights):return None
    return round(sum(float(ratings[k])*v/5 for k,v in weights.items()))

def tags_for(title:str, mode:str, category_id:str) -> list[str]:
    t=title.lower();tags=[]
    if mode in ('D','A'):tags.append('digital-fulfillment')
    if mode in ('M','I','R','P'):tags.append('recurring-value-test')
    if any(x in t for x in ('report','analytics','reconcil','spreadsheet','calculator','workbook')):tags.append('C20')
    if any(x in t for x in ('template','printable','worksheet','planner')):tags.append('C09')
    if any(x in t for x in ('ai ','copilot','grounded','prompt','synthetic')):tags.append('C01')
    if any(x in t for x in ('email','crm','proposal','quote')):tags.append('C07')
    if any(x in t for x in ('connector','adapter','plugin','extension')):tags.append('C17')
    if any(x in t for x in ('extract','document','workflow','record')):tags.append('C21')
    return sorted(set(x for x in tags if x!=category_id))

def privacy_profile(category:str,mode:str, title:str,risk:str) -> dict:
    if mode=='CAPITAL':kind='provider-and-regulator-identity'
    elif mode=='F':kind='client-identity-exposure'
    elif category in ('C16','C17'):kind='publisher-disclosure-review'
    elif risk!='standard':kind='heightened-disclosure-review'
    else:kind='brand-led-possible'
    note={
      'provider-and-regulator-identity':'Banks, brokers and authorities may require verified identity; not a route to anonymous money movement.',
      'client-identity-exposure':'A brand can reduce personal marketing. Contracts and marketplaces such as Upwork can disclose a verified name to customers.',
      'publisher-disclosure-review':'Review the store, jurisdiction, account type and trader status. App/extension distribution can require public developer or contact details.',
      'heightened-disclosure-review':'Minimize unnecessary public personal details, but determine exact seller, registry, licensing and customer disclosures before launch.',
      'brand-led-possible':'A branded product can avoid face-led promotion. Checkout, invoices, contract documents, registries and mandatory disclosures still need review.'}[kind]
    return {'level':kind,'notes':note,'guaranteed_anonymity':False,'seller_specific_disclosure_review':'not completed',
            'private_identity':'Use genuine legal identity for required KYC, banks, taxes and provider verification. No fake people or extra accounts to evade rules.',
            'source_ids':['R-UPWORK_ID' if mode=='F' else 'R-LEMON_ID','R-ONTARIO','R-FEDERAL']+(['R-APPLE_ID','R-PLAY_ID','R-CHROME'] if category in ('C16','C17') else [])}

def construct(root:Path=ROOT) -> dict:
    folder=root/'opportunity_library/data'
    taxonomy=read_json(folder/'taxonomy.json');cats={c['id']:c for c in taxonomy['categories']}
    sources=read_json(folder/'research_sources.json'); bysrc={s['id']:s for s in sources}
    original_path=root/'research_merge/opportunity_atlas_expanded.json'
    original=read_json(original_path)['opportunities']
    assignments=read_json(folder/'classifications.json')['assignments']
    additions=read_json(folder/'curated_additions.json')['records']
    rows=[]
    for raw in original+additions:
        new=raw['id'].startswith('CUR-')
        a=raw if new else assignments[raw['id']]
        c=cats[a['category_id']];mode=raw['mode'] if new else a['normalized_mode'];prof=PROFILES[mode]
        capital=mode=='CAPITAL'
        rawrisk='regulated' if new and c['id'] in ('C26','C27','C28','C33') else 'standard' if new else raw.get('legal_class','refer to original')
        # Risk flags are screening aids, not a claim that an entire industry needs a licence.
        risk=rawrisk if rawrisk in ('standard','regulated') else 'review-required'
        ratings={k:prof[k] for k in ('passivity','profit_potential','public_privacy','acquisition','speed','fulfillment','scale')}
        ratings['evidence']=None if capital else 2 if any(bysrc[s]['kind'] in ('pricing','marketplace','spending') for s in c['source_ids']) else 1
        if not capital and risk!='standard':
            ratings['passivity']=max(1,ratings['passivity']-1)
            ratings['public_privacy']=min(3,ratings['public_privacy'])
        # Audience-heavy and editorial workflows remain work even when publishing is automated.
        if not capital and c['id'] in ('C01','C02','C04','C08','C25') and mode not in ('D','A'):
            ratings['passivity']=min(2,ratings['passivity'])
        legacy_price=number(raw.get('illustrative_price_cad'))
        price=None if capital else raw['price_hypothesis_cad'] if new else [legacy_price,legacy_price] if legacy_price is not None else None
        first=prof['first'] if new else optional_range(raw.get('first_possible_sale_days_min'),raw.get('first_possible_sale_days_max'))
        weekly=prof['weekly'] if new else ([number(raw.get('standard_mature_weekly_owner_hours_including_sales'))]*2 if number(raw.get('standard_mature_weekly_owner_hours_including_sales')) is not None else None)
        row={
          'id':raw['id'],'name':raw['name'],'origin':'Curated 216' if new else raw['parent_study'],
          'category_id':c['id'],'category':c['name'],'category_slug':c['slug'],'group':c['group'],
          'subcategory_id':a['subcategory_id'],'subcategory':next(s['name'] for s in c['subcategories'] if s['id']==a['subcategory_id']),
          'industry':raw['buyer'] if new else raw['niche'],'buyer':raw['buyer'],
          'deliverable':raw['deliverable'] if new else raw.get('description',''),
          'mode':mode,'model':prof['name'],'income_type':'personal_capital' if capital else 'business_offer',
          'classification_basis':'Individually authored new offer' if new else a['basis'],
          'classification_review_needed':not new and a['basis']=='domain-default-review',
          'secondary_tags':sorted(set(tags_for(raw['name'],mode,c['id']) + ([a['industry_category_id']] if a.get('industry_category_id') and a['industry_category_id']!=c['id'] else []))),
          'risk':risk,'source_risk_flag':rawrisk,'risk_note':raw.get('main_barrier') or raw.get('risk') or c['main_obstacle'],
          'risk_context':'Screening flag, not a legal determination. Retained source flags are not silently downgraded.',
          'phase':'unvalidated concept','paid_customers_verified':False,'evidence_scope':'category or platform only; exact-offer demand unverified',
          'original_evidence_label':raw.get('evidence_grade','New hypothesis informed by primary sources'),
          'source_ids':list(c['source_ids']),'original_source_url':raw.get('niche_source_url',''),
          'original_source_reference':raw.get('source_record_ref') or ('opportunity_library/data/curated_additions.json' if new else 'research_merge/opportunity_atlas_expanded.json'),
          'original_record_id':raw['id'],'related_to':raw.get('related_source_ids',[]),
          'ratings':ratings,'score_low_touch':weighted(ratings,WEIGHTS),'score_fast_cash':weighted(ratings,SPEED_WEIGHTS),
          'score_note':'Editorial model/risk priors on a 1–5 scale; not expected returns, comparative market research or probabilities. Small differences are ties.',
          'privacy':privacy_profile(c['id'],mode,raw['name'],risk),
          'economics':{'currency':'CAD','asking_price_hypothesis':price,'price_basis':'Unvalidated test-price range; not an observed customer contract.',
                       'startup_cash_hypothesis':prof['cost'] if new else optional_range(raw.get('startup_budget_cad_min'),raw.get('startup_budget_cad_max')),
                       'setup_hours_hypothesis':prof['setup'] if new else None,
                       'weekly_total_hours_hypothesis':weekly,'workload_basis':'Planning assumption including acquisition/support, not measured. Customer count and workflow change the actual workload.',
                       'first_sale_days_hypothesis':first,'time_to_profit':'Unknown; no sale is possible.',
                       'expected_monthly_profit':None,'source_conditional_profit':number(raw.get('illustrative_conditional_monthly_operating_profit_cad')),
                       'source_profit_warning':'Inherited what-if arithmetic only. Assumed sales volumes, owner time and acquisition may not occur; never add across records.',
                       'capital_return_forecast':None},
          'automation':{'fulfillment_target_score':ratings['fulfillment'],'passivity_target_score':ratings['passivity'],
                        'automatable':prof['automate'],'human_work':prof['manual'],
                        'actual_automation_measured':False,'reuse':'Shared original code, delivery, billing adapters and tests where compatible; separate data, contracts and cost centres.'},
          'acquisition':raw.get('acquisition_method') or prof['route'],
          'first_experiment':raw.get('first_paid_test') or raw.get('earliest_paid_test') or ('Read the full original source and demonstrate one bounded outcome before quoting.'),
          'gate':prof['gate'],'stop_rule':prof['stop'],'as_of':AS_OF,
        }
        rows.append(row)
    result={'version':'1.0.0','as_of':AS_OF,'baseline_commit':BASE_COMMIT,
      'original_sha256':hashlib.sha256(original_path.read_bytes()).hexdigest(),
      'warning':'Research inventory, not live businesses or verified earnings. Category references are not exact-offer demand. Brand privacy is not guaranteed anonymity. Capital research is separate.',
      'counts':{'records':len(rows),'legacy_records':len(original),'curated_records':len(additions),
                'business_offer_records':sum(r['income_type']=='business_offer' for r in rows),
                'capital_research_records':sum(r['income_type']=='personal_capital' for r in rows),
                'categories':len(cats),'subcategories':sum(len(c['subcategories']) for c in cats.values()),
                'inherited_industry_slices':197,'fresh_primary_references':len(sources),'verified_paid_offers':0},
      'weights':{'low_touch_privacy':WEIGHTS,'fast_cash':SPEED_WEIGHTS},'categories':taxonomy['categories'],'sources':sources,'records':rows}
    validate(result)
    return result

def validate(lib:dict) -> None:
    cats={c['id']:c for c in lib['categories']}; refs={s['id'] for s in lib['sources']}
    if len(cats)!=len(lib['categories']) or len(refs)!=len(lib['sources']):raise ValueError('Duplicate category or source ID')
    slugs=[c['slug'] for c in cats.values()]
    if len(slugs)!=len(set(slugs)) or any(not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',x) for x in slugs):raise ValueError('Invalid category path slug')
    for s in lib['sources']:
        u=urlsplit(s['url'])
        if u.scheme!='https' or not u.netloc or u.username or u.password:raise ValueError('Source must be a public HTTPS reference')
    ids=[r['id'] for r in lib['records']]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate opportunity ID')
    for r in lib['records']:
        if not SAFE_ID.fullmatch(r['id']):raise ValueError('Unsafe opportunity ID')
        if r['category_id'] not in cats:raise ValueError('Missing category')
        if r['subcategory_id'] not in {s['id'] for s in cats[r['category_id']]['subcategories']}:raise ValueError('Invalid subcategory')
        if not set(r['source_ids']+r['privacy']['source_ids']).issubset(refs):raise ValueError('Unresolved source')
        if not set(r['related_to']).issubset(ids):raise ValueError('Unresolved related ID')
        if r['privacy']['guaranteed_anonymity'] or r['paid_customers_verified']:raise ValueError('Unsubstantiated validation or anonymity')
        if r['income_type']=='personal_capital' and any(r[k] is not None for k in ('score_fast_cash','score_low_touch')):raise ValueError('Capital research must not have earnings priority')
        if r['risk']!='standard' and r['source_risk_flag']=='standard':pass # Allowed conservative screening.
        if r['source_risk_flag']=='regulated' and r['risk']=='standard':raise ValueError('Risk flag silently downgraded')
        for k,v in r['ratings'].items():
            if v is not None and not 1<=v<=5:raise ValueError('Score outside 1–5')


def factory_rows(lib:dict, root:Path=ROOT) -> list[dict]:
    """Compatibility export. Keep all old fields; add facets without rewriting sources."""
    original=read_json(root/'research_merge/opportunity_atlas_expanded.json')['opportunities']
    byid={r['id']:r for r in original};out=[]
    for r in lib['records']:
        row=dict(byid.get(r['id'],{}))
        ec=r['economics']; price=ec['asking_price_hypothesis']; time=ec['first_sale_days_hypothesis']
        if not row:
            row={'id':r['id'],'name':r['name'],'parent_study':r['origin'],'niche':r['industry'],
              'buyer':r['buyer'],'description':r['deliverable'],'revenue_mode':r['mode'] if r['mode']!='CAPITAL' else 'ORIGINAL',
              'business_model':r['model'],'income_track':'Unvalidated business offer' if r['income_type']=='business_offer' else 'Capital research; blocked',
              'illustrative_price_cad':price[0] if price else '', 'first_possible_sale_days_min':time[0] if time else '',
              'first_possible_sale_days_max':time[1] if time else '',
              'legal_class':'regulated' if r['risk']!='standard' else 'standard',
              'acquisition_method':r['acquisition'],'earliest_paid_test':r['first_experiment'],
              'build_strategy':r['automation']['automatable'],'gate':r['gate'],'risk':r['risk_note'],
              'evidence_grade':'H0: exact-offer demand unverified; category sources only',
              'niche_source_url':next(s['url'] for s in lib['sources'] if s['id']==r['source_ids'][0]),
              'market_demand_verified_for_exact_offer':False,'independent_paid_validation':False,
              'cross_niche_score':r['score_fast_cash'] if r['score_fast_cash'] is not None else 0,
              'cross_niche_score_method':'New model/risk prior; not comparable measured demand. See opportunity library lenses.'}
        row.update({'library_category_id':r['category_id'],'library_category':r['category'],
                    'library_subcategory_id':r['subcategory_id'],'library_subcategory':r['subcategory'],
                    'library_mode':r['mode'],'library_income_type':r['income_type'],
                    'library_low_touch_score':r['score_low_touch'],'library_fast_cash_score':r['score_fast_cash'],
                    'library_passivity':r['ratings']['passivity'],'library_privacy':r['ratings']['public_privacy'],
                    'library_evidence_scope':r['evidence_scope']})
        out.append(row)
    return out


def query(lib:dict, *, text:str='',category:str='',mode:str='',min_privacy:int=0,min_passivity:int=0,
          include_review:bool=True, include_capital:bool=False,lens:str='low_touch',limit:int|None=None) -> list[dict]:
    if lens not in ('low_touch','fast_cash'):raise ValueError('Unknown ranking lens')
    if limit is not None and limit<1:raise ValueError('Limit must be positive')
    term=text.casefold();out=[]
    for r in lib['records']:
        if category and r['category_id']!=category:continue
        if mode and r['mode']!=mode:continue
        if not include_capital and r['income_type']=='personal_capital':continue
        if not include_review and r['risk']!='standard':continue
        if (r['ratings']['public_privacy'] or 0)<min_privacy or (r['ratings']['passivity'] or 0)<min_passivity:continue
        if term not in ' '.join(str(r[k]) for k in ('id','name','buyer','deliverable','industry','category','subcategory')).casefold():continue
        out.append(r)
    key='score_'+lens
    out.sort(key=lambda r:(-(r[key] if r[key] is not None else -1),r['id']))
    return out[:limit] if limit else out
