# Business Portfolio — six-phase projects and editable niches

The active portfolio is organized as **Digital Products, Digital Content, Services, Ecommerce and Investing**, with the original 25 niche folders plus nine nested legacy niches retained by stable ID. The owner can create subniches or recoverably delete a selected subtree. Browse Category → Niche → Project. The active portfolio contains two project records in individual project folders: [GDM-002](niches/digital-products/game-development-marketplaces/gdm-002-capacity-aware-npc-transport/project.md) and [BOOK-001](niches/digital-products/books-and-ebooks/book-001-free-candy-chad-bradson-original-novel-and-wide-publishing/project.md). GDM-001 and GDM-003 were explicitly deleted from the active project folders together with their project-specific results. Each project folder contains its canonical `project.md` record and a `work/` folder for project-owned artifacts. Their IDs, plans, status, and progress remain intact. Historical archived projects are intentionally not included in this active-project count.

Each category and niche has a `working` boolean in its `NICHE.json`, initially `false`. Portfolio Manager shows a checkbox and Working/Not Working label in Projects and Niches. Enabling a node enables all its parent niches; disable Working descendants before disabling a parent. Turning off a child leaves its parents enabled. A toggle never starts or stops a worker. Working folders show a green badge on their icon. Settings are atomically written and shared across windows. Category summaries count working descendant leaf niches without counting a parent and its nested legacy children twice. The generated browser displays these values read-only and updates when rebuilt or served live.

Open Portfolio Manager in any Codex chat to use **Projects**, **Niches**, **History & Existing Work**, or **Repository files**. Each chat keeps its own selection. The [project browser](PROJECT_BROWSER.html) shows the category tree; double-click [Open_Project_Browser.cmd](Open_Project_Browser.cmd) for live updates. Empty niches remain selectable.

The 36-category/144-subcategory taxonomy remains in [`opportunity_library/data/taxonomy.json`](../opportunity_library/data/taxonomy.json) as research, separate from the active hierarchy. The [previous 182-node view](archive/2026-11-15-taxonomy-view-v1/README.md), the 139-record archive and the older project records remain preserved and searchable in History. The independent historical snapshots were not modified.

Current authorized spending is CAD0. The CAD100 planning ceiling grants no permission to spend. Existing project records retain their own evidence and authorization boundaries.

## Current project workflow

Select a niche to use **New project**, **New niche folder** or **Delete niche**. New projects start as **Empty project** in Phase 1 and appear directly under the niche. The disk layout is `<niche>/<stable-id>-<slug>/project.md` plus `work/`, without an intermediate `projects/` directory. Deletion moves a confirmed subtree into local recovery storage; historical archives and completed receipts remain intact.

The current sequence is **1 product research → 2 release-platform/compatible-version research → 3 marketing research → 4 build → 5 release → 6 marketing → Complete**. Each research phase has its own recheck and can pass without unnecessary changes. ChatGPT returns complete copyable text; use **Paste project text** and manually advance through phases 1–3 into Phase 4. Phases 4–6 each have a separate Codex `/goal`; Codex records completed/remaining work, all important data and URLs, and an approximate phase completion percentage at every checkpoint, then advances after verified completion.

Scope all six phases together for **2 days to 3 weeks**. Every accepted compatible version, release and initial marketing task must fit that finite scope; optional/deferred opportunities stay documented. Planning budgets are not spending authorization. A complete project is not proof of paid demand.

See [Portfolio Manager workflow](../docs/PORTFOLIO_MANAGER_WORKFLOW.md), [record schema](SCHEMA.md), and [project template](PROJECT_TEMPLATE.md) for the full contract. Old phase references below are historical package descriptions, not instructions for the current workflow.

## Earlier 182-node view (historical description)

The following section describes the immediately prior taxonomy-oriented active view and is retained as migration context. It is not the current navigation.

# Business Portfolio — active niche overhaul (2026-11-15)

The active view contains **three planned game-development product families**: GDM-001 Historical Save Regression Lab (first validation focus), GDM-002 Capacity-Aware NPC Transport System (queued), and GDM-003 Native Dependency Preflight Verifier (queued). None is built, commercially validated, priced for sale or authorized for launch. The owner's marketplace workbook supports research hypotheses, not paid demand.

**Browse:** Open `Open_Project_Browser.cmd`. **Projects** shows the three active records. **Niches** shows 36 taxonomy categories, their 144 subcategories, Game Development Marketplaces and AI Workflow Automation. Empty niches contain no invented project records. **History & Existing Work** searches all 139 preserved prior records by name or stable ID. A record's Overview, Files & Results, Tasks & Progress and Complete record are separate views. The generated `PROJECT_INDEX.json` and `PROJECT_BROWSER.html` are read-only views of canonical files.

The prior 139 records and 301 original niche files were moved byte-for-byte to [`archive/2026-11-15-legacy/`](archive/2026-11-15-legacy/). [`PROJECT_CROSSWALK.json`](archive/2026-11-15-legacy/PROJECT_CROSSWALK.json) maps each stable ID and former path to its archived path; [`FILE_MANIFEST.json`](archive/2026-11-15-legacy/FILE_MANIFEST.json) records each original file's hash and size. The builder verifies both before showing history. Underlying Payhip files, source releases, private checkpoints, Computer Bridge and legacy recovery systems remain in their original locations. The archive is a view change, not a reversal of published or completed work. To restore one record to active planning, review its current private checkpoint and external state, assign a valid current niche, and move a **copy** back with the same ID after checking for collisions; do not replay uploads, orders or publication.

The active spend authorization is CAD0; CAD100 is only a cumulative planning ceiling. No outreach, accounts, ads, uploads, production operation, purchase or publication is approved by this taxonomy change.

## Historical revision 2 notes

The following notes describe the November 5 package and its then-current active view. Its 139 records are now in History, and source counts and project suggestions below are historical rather than current priorities.

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
