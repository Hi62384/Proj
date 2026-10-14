# Reporting Sprint — local launch kit

This is an original working local CSV demonstration and a launch plan. It is NOT a deployed business,
hosted SaaS, legal contract, universal importer, financial/accounting system, or evidence of actual customers.
No account integrations, payment processing, emails, or external uploads have been performed.

## Run on Windows
Install/use Python 3.10+ if available, open a terminal in this folder, then:

```powershell
py report_builder.py synthetic_sample.csv --out demo_output
py -m unittest discover -s tests -v
```

On macOS/Linux use `python3` instead of `py`. Open `demo_output/report.html` in a browser.
A pregenerated sample is supplied in that folder. To recreate it explicitly use `--overwrite`,
or choose another output folder. The tool never modifies the input CSV.

## Supported data — one small proof of concept
Required headers: `date,order_id,channel,revenue,cost`.
Dates: YYYY-MM-DD. order_id must actually be a unique record ID; real line-item exports need an agreed mapping.
Money: one currency per file, plain signed decimals, at most two decimal places. No currency conversion.
Limit: 10 MB / 10,000 rows. Extra columns are ignored; no personal data is required.
Invalid input fails closed; duplicate IDs are NOT silently removed. All values must be reconciled to the source.
"Revenue minus input cost" is NOT net business profit.

## Before offering a real paid adaptation
Read PILOT_OFFER.md and INTAKE_AND_ACCEPTANCE.md. Demonstrate the workflow honestly using synthetic data.
Confirm customer authority, a redacted sample, safe data handling, exact KPI definitions, supported formats,
objective acceptance, pricing, and what happens when the input changes. Do not promise integrations you have not built.
Use funded marketplace milestones for marketplace customers. Use direct payment only for independently sourced
customers where permitted. Do not move marketplace buyers elsewhere to avoid fees.

## Files
- report_builder.py / tests: local deterministic demonstrator and tests.
- synthetic_sample.csv / demo_output: synthetic demonstration, not actual business results.
- PILOT_OFFER.md, OUTREACH.md, INTAKE_AND_ACCEPTANCE.md: editable launch documents.
- COMPLETE_PLAYBOOK.md: strategic decisions, five 20-part blueprints, daily plan, architecture and sources.
- Actuals_template.csv / Operations_template.csv: empty import schemas for the workbook dashboards.
- research_sources.json, opportunities.csv and scenario_assumptions.json: audit material.

The workbook is the central financial planning and actual tracking dashboard. It is not connected to your accounts.
A production system needs access control, encrypted storage, tenant isolation, reliable scheduling, monitoring,
retention rules, rate/usage limits, safe payment webhooks and responsible human review.
