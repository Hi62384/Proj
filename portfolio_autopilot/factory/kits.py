"""Generate honest, review-only launch packages for any atlas entry.

The generator does not claim a product is built, demand verified, or a seller
account connected. No network, marketing, publishing, or payment calls.
"""
from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from html import escape
import json
from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlsplit

from .config import PRIVATE, SetupError, init_private, load_profile, safe_id

MODE_GUIDES = {
  'F': ('Bounded service pilot', 'Deliver one agreed result using an approved sample; measure manual hours.',
        'Acceptance fixture, scope document, source-to-output QA, delivery instructions',
        'Explicit in-platform job requests and permissioned introductions',
        'Repeat use only after two independently accepted paid projects'),
  'R': ('Managed recurring monitoring', 'Observe a permitted signal; alert only after retries and false-positive checks.',
        'Monitor contract, probe test, alert test, incident runbook, bounded response time',
        'Existing operators who have recurring failures or deadlines',
        'Pilot with opt-in and verified alert value before recurring billing'),
  'D': ('Self-service download', 'Build one independently testable original file or tool.',
        'Original source file, example, test fixtures, license, install guide, support policy',
        'Relevant marketplace search, paid customer requests, permissioned communities',
        'Seek paid license orders, not free downloads or likes'),
  'I': ('Adapter or integration', 'Start read-only with authorized test data and explicit scope.',
        'Input contract, output fixture, auth/sandbox plan, error handling, rollback notes',
        'Businesses visibly struggling with the precise integration gap',
        'Paid pilot first; no unapproved production-system writes'),
  'M': ('Specialized subscription software', 'Pilot one recurring workflow before multi-tenant hosting.',
        'Minimum capability, cancellation/quotas, access model, tests, support budget',
        'Repeat buyers of the narrowly defined problem',
        'At least three paid pilots and repeat-use evidence before hosted automation'),
  'P': ('Licensed information service', 'Manually verify a lawful, useful change before building a feed.',
        'Original analysis, source rights audit, clear coverage and correction policy',
        'Buyers repeatedly asking for this specific information',
        'Paid sample or renewal signal; no resale of unlicensed source material'),
  'A': ('Original asset license', 'Create and test one original commercially useful mini-pack.',
        'Attribution/provenance, sources, previews, compatibility fixtures, license',
        'Verified marketplace purchase intent and relevant creator communities',
        'Two genuine orders before producing a catalogue'),
  'L': ('Specialist educational material', 'Teach a narrowly scoped, verifiable outcome.',
        'Original curriculum, working exercise, source references, clear limitations',
        'People paying for that defined learning task',
        'Paid preorders or completed purchases before a full course'),
  'C': ('Disclosed affiliate information', 'Publish genuinely useful original comparisons without fake reviews.',
        'Verification record, disclosures, update schedule, rights-cleared materials',
        'Existing qualified search intent; no doorway or spam pages',
        'Treat first-month income as unproven; traffic alone is not profit'),
  'X': ('Two-sided marketplace', 'Start with manual verified transactions and demand on both sides.',
        'Listing permissions, moderation, payment liability, dispute/abuse controls',
        'A real buyer and seller willing to transact',
        'Do not build multi-sided infrastructure before completed transactions'),
  'ORIGINAL': ('Research-stage offer', 'Classify the exact service or product type first.',
        'Buyer scope, prototype, rights audit, acceptance tests',
        'Existing requests and permissioned introductions',
        'No launch until a concrete deliverable and paid buyer need are defined'),
}


def safe_source_url(url: str) -> str:
    try:
        p = urlsplit(url)
    except ValueError:
        return ''
    if p.scheme in ('https', 'http') and p.hostname and not p.username and not p.password:
        return url
    return ''


def _val(row: dict, key: str, default='Not yet established') -> str:
    val = row.get(key)
    return str(val).strip() if val is not None and str(val).strip() else default


def _price(row: dict) -> str:
    try:
        price = Decimal(_val(row, 'illustrative_price_cad', '0'))
        if price.is_finite() and price > 0 and price <= Decimal('1000000'):
            return f'{price:,.2f}'
    except InvalidOperation:
        pass
    return 'TBD'


def _texts(row: dict, profile: dict) -> dict[str, bytes]:
    ref = safe_id(_val(row,'id'))
    mode = _val(row,'revenue_mode','ORIGINAL')
    title, method, deliverables, buyers, gate = MODE_GUIDES.get(mode, MODE_GUIDES['ORIGINAL'])
    industry = _val(row,'niche')
    offer = _val(row,'name')
    buyer = _val(row,'buyer')
    description = _val(row,'description')
    evidence = _val(row,'evidence_grade', 'Unverified research idea')
    price = _price(row)
    source = safe_source_url(_val(row,'niche_source_url',''))
    banner = '**DRAFT / NOT VALIDATED / NOT FOR PUBLICATION UNTIL OWNER APPROVAL**'
    basic = f'''# {offer} — launch packet ({ref})

{banner}

- **Industry:** {industry}
- **Prospective buyer:** {buyer}
- **Revenue model:** {title} (`{mode}`)
- **Deliverable hypothesis:** {description}
- **Indicative price:** CAD {price} (hypothesis; not a completed sale)
- **Evidence:** {evidence}; exact-offer buyer demand has not been verified
- **Source:** {source or 'Consult the originating research files; no direct link in this record'}
- **Risk class (research-only):** {_val(row,'legal_class')}
- **Owner and contact:** {profile.get('business_name','[Business name]')} · {profile.get('support_email','[Contact email]')}

## Highest-priority next action
Find three recent, genuine examples of this precise buyer problem before building more than a synthetic demo. Record date, source URL, existing alternatives, and whether a paid outcome is currently requested.

## Implementation strategy
{method}

## Bounded acceptance requirements
{deliverables}.

## Acquisition starting point
{buyers}. Respond only to actual permitted requests or introductions, never automated spam.

## Conversion gate
{gate}. No sales, buyers, visits, or revenue have been created by generating this packet.

## External setup
Reuse one approved seller identity/contact and checkout provider across suitable offers. Seller onboarding, marketplace approval and identity verification still require the owner; the generator does not create accounts.
'''
    offer_doc=f'''# DRAFT commercial offer — {offer}

{banner}

**Buyer:** {buyer}. **Industry:** {industry}.

### Buyer problem (to validate)
{description}

### What would be delivered
{deliverables}. Specific details are placeholders until a sample and acceptance test are agreed.

### Pilot scope — must be confirmed before sale
- One defined input and one agreed output; no live write access by default.
- The customer provides authorized, appropriately redacted sample data where needed.
- One explicit revision round and an agreed response/delivery target.
- Excludes regulated conclusions, open-ended custom development, unlimited support and customer data uploads to public repositories.

### Indicative price
CAD {price}; not a validated willingness-to-pay figure. Confirm selling currency, provider fees, tax setup, repair and refund rules.

### Payment readiness
No provider connected by this kit. Do not describe payment as available before testing merchant setup, payment success/failure, refund, cancellation (if relevant) and settlement.

### Do not claim
No previous clients, average savings, testimonials, conversion, earnings, traffic, compliance certification or other unverifiable results.
'''
    validation=f'''# Buyer evidence checklist — {ref}

{banner}

1. Inspect three **current, independently sourced** buyer requests or permissioned interviews with dates.
2. Compare three alternatives, including free ones. Note where this offer is meaningfully different.
3. Document the existing task and buyer's own estimate of its frequency/cost.
4. Show one original synthetic demonstration; ask whether the result solves the problem.
5. Propose a bounded, approved pilot and record actual payment evidence (not intent).
6. After a real order: measure minutes spent on sales, onboarding, delivery and support; record actual fees/refunds.
7. Continue only if demonstrated contribution and acceptable workload justify investment.

| Evidence ID | Date | Source / permitted contact basis | Buyer problem | Competing solution | Verified paid? |
|---|---|---|---|---|---|
| PENDING | | | | | No |

**No automated sending, unauthorized scraping, or bought contact lists.**
'''
    drafts=f'''# Draft-only outreach — {ref}

{banner}

## Reply to an *explicit relevant purchase request* (do not send without checking channel terms)
Hi [recipient first name, only if known from the request], I saw your request about [specific task].
I can evaluate a narrowly scoped pilot to [verified outcome]. My current work includes a synthetic demonstration, not a claimed customer case study.
Would you be comfortable sharing [specific redacted test fixture] through an approved channel? We can then agree scope, acceptance and a funded milestone.

## Project listing headline
I will help automate [the verified recurring task] for [specific buyer type]

## Listing description
[Replace this after buyer validation with the exact deliverable, supported formats, limits, evidence and price.]

## FAQ
- What inputs are supported? [Answer with tested fixtures.]
- What does delivery include? [Answer with accepted tests and versions.]
- What is excluded? [No live system access, extra sources or regulated decisions unless separately reviewed.]
- How are customer files protected? [Answer only after actual storage and retention procedures are verified.]

No mass email, DMs, off-platform fee avoidance, false testimonials or fabricated urgency.
'''
    ops=f'''# Operations and automation plan — {ref}

## Phase 0: pre-sale (already possible locally)
- Generate a draft offer/landing preview, qualification questions, QA checklist, and pricing stress test.
- Track public source evidence and permitted interactions separately from forecasts.
- Build one original synthetic demonstration and reproducible tests.
- Get an owner-approved offer and first sales channel; no automatic contacting.

## Phase 1: bounded paid pilot (requires real buyer)
- Confirm consent, exact inputs and output, acceptance, refund and data-retention terms.
- Verify a funded provider/marketplace order before starting.
- Run the supported deterministic workflow and independently inspect its output.
- Package files, checksums, customer instructions and a reproducibility test.
- Fulfill through the approved channel; collect written acceptance and actual costs.

## Phase 2: repeated product (requires repeat-use evidence)
- Move reusable logic to a versioned adapter and tests.
- Add opt-in subscriptions only for genuine ongoing value.
- Connect verified payment events, signed webhooks, quotas and failure alerts.
- Keep an auditable human exception queue and a manual pause switch.

## Blocked until specifically authorized
- Provider accounts, credentials, billing, publishing, sending messages, hosting spend, live customer data, sensitive/regulated decisions.

## Specific risk
{_val(row,'risk')}. Do not assume the atlas risk label is a complete professional review.
'''
    qa = {'opportunity_id':ref, 'status':'review_only_not_live', 'evidence_required':[
       'current_exact_problem', 'real_alternatives', 'buyer_contact_permission',
       'scope_and_acceptance', 'budget_and_provenance', 'identity_and_compliance',
       'funded_pilot_or_order', 'delivery_quality', 'measured_profit_after_time'],
       'all_passed':False,
       'marketing_enabled':False, 'payments_enabled':False, 'publishing_enabled':False,
       'customer_data_enabled':False, 'auto_spend_enabled':False}
    config={'schema_version':1,'opportunity_id':ref,'title':offer, 'industry':industry,
       'buyer':buyer,'model':mode,'business_model':title,'stage':'research_draft',
       'indicative_price_cad':price,'evidence_grade':evidence,
       'verified_paid_customers':0,'demand_verified':False,
       'allowed_external_actions':[], 'requires_human_approval':True,
       'external_spend_cap_cad':'0', 'source_ref':_val(row,'source_record_ref','original atlas index'),
       'generated_from_atlas':True}
    # No live links, JS or outgoing forms. Escaping is required even for source-derived values.
    h=escape
    preview=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(offer)} — DRAFT</title>
<style>:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{font:16px/1.65 system-ui, sans-serif;background:#0c1424;color:#dfe9f7;margin:0}}main{{max-width:920px;margin:7vh auto;padding:36px}}.tag{{color:#ffda82;font-size:13px;font-weight:750;letter-spacing:.08em}}h1{{font-size:clamp(30px,5vw,56px);line-height:1.1;margin:18px 0}}.lead{{color:#b8cbe5;font-size:19px}}.card{{background:#14223a;border:1px solid #324665;border-radius:20px;padding:24px;margin:26px 0}}small{{color:#99aac1}}.pill{{display:inline-block;border:1px solid #58739d;border-radius:99px;padding:5px 12px;margin:4px;color:#dfe9f7}}footer{{margin-top:32px;color:#a3b5d2}}</style></head><body><main>
<div class="tag">UNPUBLISHED MOCKUP · NO PRODUCT OR PAYMENT IS LIVE</div><h1>{h(offer)}</h1><div class="lead">A proposed {h(title.lower())} for {h(buyer)}.</div>
<section class="card"><span class="pill">{h(industry)}</span><span class="pill">CAD {h(price)} proposed</span><h2>What this would do</h2><p>{h(description)}</p><h2>Draft deliverable</h2><p>{h(deliverables)}.</p><p><small>Price, scope, availability, delivery and fit are unverified; nothing can be purchased here.</small></p></section>
<footer>Owner: {h(str(profile.get('business_name','[Business name]')))} · This is an internal preview only. It is not a live store or a customer case study.</footer></main></body></html>'''
    obj={
       'README.md': basic,
       'OFFER_DRAFT.md':offer_doc,
       'BUYER_VALIDATION.md':validation,
       'SALES_DRAFTS.md':drafts,
       'OPERATIONS.md':ops,
       'LANDING_PREVIEW.html':preview,
       'QA_GATES.json':json.dumps(qa,indent=2,ensure_ascii=False)+'\n',
       'product_config.json':json.dumps(config,indent=2,ensure_ascii=False)+'\n'
    }
    return {key:value.encode('utf-8') for key,value in obj.items()}


def make_kit(row: dict, root: Path = PRIVATE, profile: dict | None = None) -> Path:
    """Generate a complete draft kit. Refuse to overwrite or follow symlink targets."""
    init_private(root)
    ref=safe_id(_val(row,'id'))
    dest=(root/'launchkits'/ref).absolute()
    allowed=(root.resolve()/'launchkits').resolve()
    if not dest.resolve().is_relative_to(allowed) or dest.exists() or dest.is_symlink():
        raise SetupError('Draft kit already exists or unsafe path; do not overwrite reviewed work.')
    dest.parent.mkdir(parents=True,exist_ok=True)
    data=_texts(row,profile or load_profile())
    temp=Path(tempfile.mkdtemp(prefix='new-kit-',dir=dest.parent))
    try:
        for name,value in data.items():
            (temp/name).write_bytes(value)
        temp.rename(dest)
    except BaseException:
        shutil.rmtree(temp,ignore_errors=True)
        raise
    return dest
