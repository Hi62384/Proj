# Verification report — marketing and budget revision
Run date: 2026-11-05. These are **package/planning-tool tests**, not business, customer-workflow or live-account validation.

## Completed checks
- **51 Python regression tests passed**: 31 preserved architecture tests and 20 new commercial/budget/evidence tests. They include 24-level nested niches, IDs/references/cycles, safe parsing/rendering, price arithmetic, missing-cost/approval rejection, separate parent budgets and preserved progress.
- **139 canonical records** pass schema, source-reference and commercial checks. All 126 AWA candidates remain commercially unvalidated; no actual income was added. The 12 existing records keep their prior evidence basis.
- **133 original records compared against the actual earlier ZIP**: work state, commercial validation, actual revenue/profit, paid-pilot fields and completed checkmark lines are unchanged. Newer Windows edits are outside this comparison and must be merged locally.
- **25 browser behavior checks passed** in container Chromium: rendering, ID search, existing-work/recursive-niche filters, budget/launch-gate filters, new projects, report links, pagination, empty results, mobile-width overflow, no JavaScript errors and no external network calls. Desktop and mobile renderings were visually inspected.
- Local Markdown links were checked; exact count and exclusions are recorded in `research/V2_LINK_CHECK.json`. No broken local file targets were found. External URL freshness is not asserted by that link checker.
- The generated browser/index were rebuilt from canonical records and checked for staleness. ZIP CRC integrity and member SHA-256 checks were verified during packaging; the final manifest and checksum list describe this delivery, not the earlier package.

## Explicit limitations and recovery
The default Playwright-managed browser executable was absent. The installed `/usr/bin/chromium` was used instead. Container policy blocked `file://` navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`; the identical generated HTML was loaded as an in-memory browser document for behavioral and rendering tests. Actual direct-file opening in the user's Windows browser remains a local acceptance check. No server is required by the artifact itself.

No n8n/Make/Zapier/client workflow was implemented or executed. Fictional acceptance cases describe future tests, not observed production passes. No advertisement, proposal, customer contact, live storefront edit, native Excel test, charged checkout, refund or payout was performed. No customer conversion, probability of success or income target is established by these tests.

The arithmetic checker verifies local values and declared evidence fields. It cannot validate the authenticity of an approval reference, enforce provider charges, protect a bank account or confer permission. Missing costs/permissions block a proposed request; actual account-level controls and owner approval remain necessary.

Research access varies: 41 revision-specific records are labeled full-page, indexed-primary or connector reads; 67 older records are carried forward, not individually refreshed. Indexed buyer requests are not a confirmed current eligible prospect list. New source evidence does not mark any offer paid or validated.

## Repeat locally
```powershell
python business_portfolio/tools/build_browser.py
python business_portfolio/tools/build_browser.py --check
python business_portfolio/tools/commercial_checks.py --portfolio business_portfolio
python -m unittest discover -s business_portfolio/tests -v
```

Then open the actual Windows `PROJECT_BROWSER.html`, verify its filters/embedded reports and retain any newer local checkpoint before merging. Do not copy historical test counts into a report of tests not actually rerun.
