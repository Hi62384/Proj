# Business Portfolio — revision 2
**Research-informed plans and a local project explorer · November 5, 2026**

**Double-click [Open_Project_Browser.cmd](Open_Project_Browser.cmd) for the live project explorer.** It starts or reuses the read-only local service. Changes to canonical Markdown appear within a few seconds. The [static snapshot](PROJECT_BROWSER.html) remains available offline, clearly labelled as a snapshot. The complete ZIP retains individual Markdown files and rebuild tools. No customer workflow, advertisement, account or payment executes from the browser.

## What is in this revision
**139 resumable records:** 56 scoped service candidates (including one explicit audit follow-on), 58 bundled components, six deferred downloads, six deferred software ideas, 12 existing-work records and one integration record. All 133 prior IDs/progress records are retained; AWA-121 through AWA-126 are new. These are not 139 independent businesses or validated income sources.

Each applicable record has a buyer-specific outcome, proof asset, native-first delivery shortcut, acquisition route/draft, effort boundary, budget gate, measurement/stop rule and honest economic sensitivity. Bundle/internal records explicitly do not need independent advertising. Existing product records contain specific launch/promotion drafts without changing their approved releases.

**Budget:** CAD0 preferred, CAD100 absolute cumulative owner-launch ceiling per selected project, no automatic reset. Current authorized spend is CAD0 portfolio-wide. Proposed service prices are separate from startup costs. Production costs must be identified and accepted by the customer; free prototypes do not establish affordable production. Six software candidates remain discovery-only.

**Evidence:** 108 source records, including 41 additional policy/technical/competitor/channel/buyer/repository records reviewed for this revision. The other 67 are carried forward, not newly reverified. No new paid order or measured success probability is claimed.

## Start with the evidence and a small test
[Research findings](research/RESEARCH_V2.md) · [Priorities](research/PRIORITIES_V2.md) · [Marketing and advertising](research/MARKETING_PLAYBOOK.md) · [Budget policy](research/BUDGET_POLICY.md) · [Economics](research/ECONOMICS_V2.md) · [Validation gates](research/VALIDATION_GATES.md) · [New sources](research/SOURCES_V2.md).

An eligible requested problem, scoped skill proof and buyer-funded delivery are stronger starting points than a generic “AI agent” catalogue. Consider AWA-005, AWA-001, AWA-007 or AWA-012; AWA-122 is a narrower new document-assembly option. Choose one primary and at most one related fallback. Existing EX-001/EX-002 promotions should reuse assets, not restart product development.

## Existing work is preserved
Published calculator/inventory records retain their reported status and unknown paid demand. Storefront, prototype, supplier reality-check, current Computer Bridge and legacy tools remain traceable. No local Windows, native Excel, private order or live-store re-verification was performed here. Checkmarks keep their original evidence basis; no fictional progress percentage or revenue is added.

## Install or merge safely
Read [REPO_PLACEMENT.md](REPO_PLACEMENT.md). The ZIP contains the outer `business_portfolio/` directory. If no local folder exists, extract into the repository root. If a prior package or newer local changes exist, **stage outside the checkout and merge by ID** using [CODEX_IMPLEMENTATION_PROMPT.md](CODEX_IMPLEMENTATION_PROMPT.md). Never overwrite newer local progress.

```powershell
python business_portfolio/tools/build_browser.py
python business_portfolio/tools/build_browser.py --check
python -m unittest discover -s business_portfolio/tests -v
python business_portfolio/tools/commercial_checks.py --portfolio business_portfolio
```

The tools require Python 3.10+ and only its standard library. They validate local records and arithmetic; they do not spend, enforce bank/provider limits, contact prospects or operate the bridge. The optional developer browser QA uses a separately available Playwright environment; no browser-test dependency is needed to browse/rebuild this package.

Read [QA_REPORT.md](QA_REPORT.md) for checks actually run and remaining acceptance limitations. Source Markdown is canonical; the HTML/JSON are generated. Keep all credentials, customer documents, real leads, orders, consent evidence and financial ledgers outside the public repository.

## Local integration and live view

Read [INTEGRATION_STATUS.md](INTEGRATION_STATUS.md) for current local tests, state preservation and limits. The supplied MANIFEST.json, CHECKSUMS.sha256 and QA_REPORT.md are historical delivery-snapshot evidence after local edits; they are not claims that edited files still match the ZIP. LOCAL_MANIFEST.json records the edited local snapshot separately.

The service listens only on http://127.0.0.1:22841 and uses the Python standard library. It serves validated portfolio data plus explicitly listed source guides and public product links. It never serves arbitrary paths, private releases, customer records or a filesystem browser. There is no account, scheduler, AI engine or spending capability. No dependencies were installed.

Each intentional launcher run opens or requests reuse of the browser page while reusing the running service. The default browser may create another tab; reliable tab detection is not available, so the launcher does not suppress reopening. The service stops at Windows sign-out/restart; the next launcher run starts it again. Temporary incomplete/invalid edits keep the last valid view and display a warning. A developer can run `python business_portfolio/tools/serve_browser.py` in a console and use Ctrl+C to stop it.

Files & Results labels source guides separately from actual delivery assets. Paid customer archives and the private demo stay protected; no containing-folder OS command is exposed through HTTP. Additional deliverables need a specific safe entry in the service guide registry, not a broad folder permission.

Declared non-sensitive text results can appear automatically; see [the public-results format](SCHEMA.md). The service does not guess at paid releases, private videos or complete build folders. Those remain explicitly withheld or unverified.

Startup failures keep the CMD window open with an error. Background service startup output is written to the ignored `.local/browser-startup.log` when available. The visible Python launcher checks service health before requesting the page; it no longer hides all failures behind pythonw.
