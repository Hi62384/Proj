"""One-command review-only sales package for the already-tested CSV demo."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import tempfile

from .config import PRIVATE, ROOT, SetupError, init_private, load_profile
from .reporting import create_delivery

FILES: dict[str, str] = {
'00_START_HERE.md': """# Reporting automation service — first-sale launch pack

**Status: REVIEW-ONLY. No live listing, seller account, customer or payment was created.**

1. Review the attached synthetic report and confirm it runs on your computer.
2. Complete a truthful freelancer profile; use the prepared draft below.
3. Look for five actual buyer-posted reporting/CSV automation requests.
4. Write individualized proposals only through channels where permitted.
5. Ask for 10 redacted sample rows and exact expected output; do not request secrets.
6. Confirm one written, capped scope and funded milestone before starting.
7. Use the header preflight and report-packaging commands for agreed work.
8. Review the output against source totals; deliver via the permitted channel.
9. Record the real payment, fees, owner time, and whether the client accepts.

Do not wait for an entire SaaS platform before making a genuine sales test.
""",
'01_UPWORK_PROFILE_DRAFT.md': """# Freelancer profile — draft

**Headline:** Python Automation | Excel, CSV & Business Reports

I build practical tools to replace repetitive CSV and spreadsheet reporting tasks.

My synthetic Python demonstration validates record IDs, dates and amounts, then generates HTML, CSV and JSON summaries.

I can evaluate your real reporting workflow and build a tested, repeatable script with documented input requirements and clear acceptance criteria.

I do not claim previous paying customers or guaranteed business results.

**Contact:** [Your approved business contact]
""",
'02_PROJECT_CATALOG_DRAFT.md': """# Project Catalog offer — NOT PUBLISHED

**Headline:** I will automate a CSV sales report using Python

**Proposed introductory price:** CAD 299 (set an appropriate USD price if the marketplace requires USD; verify current fees).

**Includes:** One agreed CSV export format; one HTML/CSV/JSON report; deterministic validation; reusable Python program; run instructions; one in-scope revision.

**Requires:** Customer-authorized redacted sample, exact field mapping, a defined acceptance test, written scope and funded milestone.

**Excludes:** Two-file joins unless separately agreed, live APIs, private/regulated data without proper agreements, unlimited changes and regulated financial conclusions.

**Delivery time:** Agree after sample review. Do not guarantee 48 hours for unseen data.

**Portfolio image:** Screenshot of the synthetic example report clearly labeled demonstration.

**Channel rules:** Follow Upwork terms, currency requirements, review policies and permitted workflows. No unauthorized application automation or off-platform payment diversion.
""",
'03_PORTFOLIO_ENTRY_DRAFT.md': """# Synthetic portfolio demonstration

**Title:** Automated Sales & Revenue Reporting Tool (Synthetic Demonstration)

I built a local Python reporting tool that processes CSV data and generates repeatable HTML and machine-readable summaries. The tool checks required columns and duplicate IDs, validates decimals and dates, calculates group totals and provides an export package.

This uses made-up example data and is not a completed customer project. Revenue minus input cost is not accounting net profit.
""",
'04_PERMISSIONED_PROPOSAL_DRAFT.md': """# Tailor only to an actual explicit buyer request

Hi [recipient from the request], your posting mentions [exact reporting pain from their request].

I have built a Python CSV reporting demonstration with input checks and repeatable HTML/CSV summaries. This uses synthetic data; I am not claiming previous customer case studies.

For a simple single-export workflow, I can quote an introductory CAD 299 fixed-scope pilot after reviewing a few redacted example rows and the expected report.

Could you share the relevant columns through this platform? We can then confirm exact acceptance and a funded milestone before beginning.

**Review before sending:** Current request, channel rules, skill fit, truthfulness, currency and buyer consent. No mass or unsolicited commercial messages.
""",
'05_BUYER_INTAKE_AND_ACCEPTANCE.md': """# Buyer intake — resolve before paid work

- [ ] Buyer is authorized to share and use the data.
- [ ] Source file is UTF-8 CSV, <=10MB and <=10,000 rows, one currency.
- [ ] Exact mapping of date, unique record ID, group, revenue and input cost.
- [ ] Buyer confirms currency label (no conversion), rounding and metric meaning.
- [ ] Duplicates, negative values, missing fields and exceptions have agreed rules.
- [ ] Buyer supplies sample expected output; define objective reconciliation.
- [ ] Funded milestone, deliverables, deadline, revision cap and remedy agreed.
- [ ] Delivery channel and retention/deletion terms documented.
- [ ] No sensitive, regulated or unapproved client data processed in prototype.
- [ ] Test report matches source record count, groups and totals.
- [ ] Buyer accepts the final in-scope deliverable in writing.
""",
'06_DELIVERY_RUNBOOK.md': """# Repeatable fulfillment (offline, review required)

1. Copy the sample mapping and replace field names with the agreed CSV headers.
2. From repository root run: `python -m portfolio_autopilot.factory.cli report-preflight --input INPUT.csv --mapping MAPPING.json`.
3. When the input and mapping pass, run: `python -m portfolio_autopilot.factory.cli report-package --input INPUT.csv --mapping MAPPING.json --customer-ref CUST001`.
4. Under `portfolio_autopilot/.local/factory/deliveries/CUST001/`, open the output report and verify the totals against the source and agreed fixture.
5. Examine `manifest.json` and `customer_delivery.zip`. Original source files are not copied into the ZIP.
6. Confirm permissions, quality, customer acceptance requirements and retention period. Then deliver through the APPROVED channel yourself; the program cannot send anything.
7. Record actual revenue, marketplace fees, delivery expenses, refunds and owner minutes using the local ledger.

The .local folder is ignored by Git but is **not encrypted**. Obtain suitable secure private storage and permission before processing confidential or regulated customer data. Client-specific data must never be committed.
""",
'07_NEXT_BUSINESSES.md': """# Reuse strategy after the first paid sale

Use the shared mapping, validation, portable runner, packaging and testing code for *related problems in any industry* only where the input/output contract fits. Each new buyer segment requires its own acquisition testing and evidence.

Candidate adjacent experiments: shop inventory reports; supplier import checks; weekly agency sales summaries; small operations KPI snapshots. None has confirmed customers.

A productized maintenance plan is appropriate only when customers demonstrate an ongoing need and accept bounded support. The next important improvement is finding a repeatable acquisition channel—not generating 100 speculative storefronts.
""",
}


def first_business(root: Path = PRIVATE) -> Path:
    """Prepare review-only sales docs plus portable validated synthetic ZIP."""
    init_private(root)
    target=root/'first_reporting_business'
    demo_out=root/'synthetic_reporting_demo'
    if target.exists() or demo_out.exists():
        raise SetupError('First-business pack already exists; preserve it instead of overwriting.')
    sample=ROOT/'research_merge'/'reporting_demo'/'synthetic_sample.csv'
    mapping=Path(__file__).parent/'templates'/'report_mapping.sample.json'
    if not sample.is_file():
        raise SetupError('Repository synthetic reporting sample missing.')
    delivery=create_delivery(sample,mapping,customer_ref='SYNTHETIC_DEMO',destination=demo_out)
    staging=Path(tempfile.mkdtemp(prefix='first-offer-',dir=root))
    try:
        for name,content in FILES.items():
            (staging/name).write_text(content,encoding='utf-8')
        # Profile is non-sensitive; do not include even it in the portable customer ZIP.
        profile=load_profile(root/'seller_profile.json')
        path=staging/'01_UPWORK_PROFILE_DRAFT.md'
        path.write_text(path.read_text(encoding='utf-8').replace('[Your approved business contact]',
                             profile.get('support_email','[Your business email]')),encoding='utf-8')
        shutil.copy2(delivery/'customer_delivery.zip',staging/'SYNTHETIC_REPORT_DEMONSTRATION.zip')
        (staging/'STATUS.json').write_text(json.dumps({
          'stage':'draft_not_published','linked_opportunity_id':'FAST-O01',
          'real_sales_count':0,'demo_data':'synthetic','stripe_connected':False,
          'upwork_profile_created':False,'published':False,
          'remaining_user_steps':['Create/verify an appropriate freelancer account',
            'Review exact listing and price','Find five current matching buyer requests',
            'Review and submit individual relevant proposals']},indent=2)+'\n',encoding='utf-8')
        staging.rename(target)
    except BaseException:
        shutil.rmtree(staging,ignore_errors=True)
        raise
    return target
