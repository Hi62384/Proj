# Cleaning Business Pricing & Profit Calculator — original digital download

**Current status (November 4, 2026):** [Published at CA$15](https://payhip.com/b/bP6YN) in the [Arshya Ghafaryan store](https://payhip.com/ArshyaGhafaryan). PayPal connection and the CA$0 delivery flow are verified; no charged payment or payout has been tested. Paid customer demand remains unverified.

The current customer archive is **Cleaning_Pricing_Toolkit_v1.0.1_CUSTOMER.zip**, 61,130 bytes, SHA-256 `334518208388483457c8849cfdf9c73955c80e929d38c1afa6631e9459d990d5`. Its delivered buyer download matched that hash. This directory retains original authoring sources; do not assume rebuilding them reproduces the current live package or replace the live download without release review.

Released-workbook calculation/input checks passed in LibreOffice Calc. Native Microsoft Excel and Excel for web remain untested; Calc results are not Excel certification. No spreadsheet-software licence is included. The existing [Support and Refunds policy](https://payhip.com/ArshyaGhafaryan/support-and-refunds) and [Contact page](https://payhip.com/ArshyaGhafaryan/contact) use the current seller identity.

This product is an original, Excel-based cost-aware quoting tool intended for cleaning businesses. Pricing, sample hours, consumables and tax settings are illustrative. The product must be validated with a real buyer before advertising market fit; no revenue has been earned by creating it.

## Folders

- `customer/` — **blank** Excel workbook, license and start note. These belong inside the customer ZIP.
- `examples/` — separate fully marked fictional demonstration workbook and sample CSV. The demo workbook belongs inside the customer ZIP; the sample CSV is seller evidence/test fixture.
- `documentation/` — text source for the bundled PDF quick-start guide.
- `marketing/` — historical Payhip listing draft, launch checklist, preview artwork and privacy review. The current publication, price, policy and delivery status is summarized above; these drafts do not override the live release.
- `release/` — the pre-packaged customer ZIP, plus a SHA-256 manifest.
- `tests/` — stdlib tests for model math, workbook formula signatures, safety and packaging.
- `tools/` — reproducible release packaging and optional workbook/PDF authoring code.

## The product at a glance

Eight worksheet tabs: READ ME, OVERVIEW, QUICK QUOTE, CLIENT QUOTE, JOB SCENARIOS, JOB LOG, SERVICES and SETTINGS. The editable input fields are blue. Formula outputs are computed in the workbook, not hardcoded. The first quote uses a configurable loaded hourly cost, crew count, per-person time, travel, supplies, overhead, target contribution, fees, discount and sales tax. It has a scenario planner for 25 jobs and a manual actual-job log.

The workbook is **not** an automated bookkeeping, tax-reporting, or payroll system. Its margin metric is an **estimated contribution margin**, not net profit or guaranteed earnings. The default 0% tax is explicitly an unconfigured placeholder.

## Build and inspect

From the repository root, run independent standard-library tests (no third-party package needed):

```powershell
python -m unittest discover -s products/cleaning-pricing-calculator/tests -v
python products/cleaning-pricing-calculator/tools/package_release.py --check
```

The provided Excel workbooks and PDF guide are already built and do not require Python to use. Optional rebuild scripts require separate authoring libraries (`artifact_tool` for XLSX, `reportlab` for PDF) and are not needed by customers.

To package after editing customer files, run:

```powershell
python products/cleaning-pricing-calculator/tools/package_release.py
```

Do not upload a newly edited ZIP without testing formulas and inspecting its contents. No payments, accounts, domains, messages or websites are created by running any of these files.

## Before any sale

1. Open both `.xlsx` files in a modern version of Microsoft Excel on a separate test computer or profile. Test editing blue inputs, formula recalculation, PDF export and layout. Python-based checks are not a replacement for native Excel QA.
2. Have at least two actual cleaning business operators assess whether the defaults and workflow match real quoting requirements, using only fictional or permissioned data.
3. Confirm the exact marketplace's seller identity, category acceptance, consumer/disclosure rules, currency, fees, refund rules and privacy presentation. Do not assume PayPal or Payhip automatically conceals your home address.
4. Create an honest listing based on `marketing/PAYHIP_LISTING_DRAFT.md`. Use screenshots of **the fictional demonstration**, not invented buyer results.
5. Test purchase and download as a buyer in the provider's permitted sandbox/test mode, then obtain explicit approval to publish.

## Product/version boundaries

- No macros, Excel add-ins, hidden external links, or automatic data uploads.
- Only one currency, **CAD**, in this version (the label is not a converter).
- The seven sample service categories can be **edited in place**, but formula and dropdown ranges have a fixed 7-row table. Expanding the service catalogue requires formula changes/testing.
- Batch planner covers 25 rows. Job log covers 25 manual entries; it does not synchronize estimates automatically.
- Compatibility with Google Sheets, Numbers or very old Excel versions is not claimed.
- Product delivery can be automated by the chosen marketplace after seller verification and publication; customer discovery and support are not inherently passive.
