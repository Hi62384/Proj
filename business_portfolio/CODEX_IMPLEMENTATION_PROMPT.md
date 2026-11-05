# Codex v2 update prompt — low-budget, market-tested portfolio plans

Work directly in my existing official Codex project for `Hi62384/Proj`. My expected checkout is:

```text
C:\Users\User1\Documents\Downloads\Proj
```

Implement the portfolio architecture described below using the supplied `business_portfolio` package. Do the local integration and tests; do not just return another design proposal or create a duplicate assistant application. Do not start building all the commercial candidates.


## Revision 2 instructions — apply these before the original integration steps
This is a **planning/marketing/budget update**, not permission to execute any offer, message prospects, launch ads, buy tools or alter live products. Read `research/RESEARCH_V2.md`, `PRIORITIES_V2.md`, `MARKETING_PLAYBOOK.md`, `BUDGET_POLICY.md`, `ECONOMICS_V2.md`, `VALIDATION_GATES.md` and `SOURCES_V2.md`.

### Merge, do not overwrite
If the previous package has already been integrated, use the supplied staging directory outside the checkout. For each stable ID, compare base/current/incoming where the known v1 hash is available. Protect newer completed checklist items, owner assignments, work state, commercial validation, actual financial fields, deliverable paths/hashes, work logs, private checkpoint links, external-action receipts and newer decisions. Merge the incoming commercial sections and metadata additively. Preserve local-only projects. A matching incoming title/date is not permission to replace an entire local file.

The package hash baseline helps identify unchanged files but is not the old file body. Use the previously downloaded v1 archive if a genuine three-way content merge is needed. If it is unavailable, retain changed local content and create a specific reconciliation note; do not invent a common base. Back up affected local files under the existing private backup policy, not inside the public package. Never `git reset --hard`, clean, mass-stash or force-copy over unknown local work.

### Budget interpretation
The user's maximum is **owner startup/launch cash**, not the customer's sale price. CAD0 preferred; CAD100 cumulative hard ceiling per chosen project, including tax/FX/committed renewals and acquisition. First sale or a new calendar month does not reset it. **Current total authorization is CAD0 across the portfolio.** Optional envelopes are not approvals and cannot be multiplied by parallel agents. The user has not selected or funded all 139 records.

The zero-recurring-owner plan relies on existing tools and, for paid client delivery, explicitly accepted customer-owned production accounts. Verify each required feature, usage limit, licence and cost. Do not conceal a subscription as free, rely on trials, self-host client production on the owner's laptop, disable security/QA, or call a production SaaS feasible because its local prototype costs zero. Keep the six software ideas production-deferred unless a viable funded plan is independently approved.

The new `owner_budget` and commercial fields are records and local checks—not external permission grants or enforced bank/provider limits. `tools/commercial_checks.py` validates arithmetic and unresolved costs. Real approval, budgets, consent and account controls remain required. Do not automatically renew, top up, purchase Connects, pay API charges or launch an ad after the checker passes.

### Marketing is an acceptance requirement for a selected commercial project
Retain the revised buyer-specific headline, proof, response/CTA, primary discovery phrase/channel, native alternative, small acquisition batch, all-in time cap, fee sensitivity and stop conditions. Do not replace them with “post on social media” or mass-generated promotional text. An eligible request needs current location, experience, budget and open-status checks. Indexed job text is not a live confirmed opportunity.

Selling work stays separate from building work. Before authorized acquisition, prepare one reusable fictional demonstration and a bounded scope. Before client-specific production, require an agreed paid arrangement and acceptance. Do not promise revenue, guaranteed sales, passivity, platform certification, regulatory compliance or an empirically high chance of success. No exact-offer paid validation was added in this package.

Keep EX-001/EX-002's approved products and reported progress. Their new plans reuse existing screenshots/demo, disclose compatibility limits, compare free substitutes and define organic sales tests. Do not build a new store, start a YouTube channel, modify release bytes or republish by default. The existing supplier reality-check stays intact. Internal/legacy records and components do not need independent advertising.

Advertising is planned but **off**. Only consider a tiny, separately approved test after genuine sales, measured contribution, a credible conversion model and verified total-budget controls. A daily ad budget is not a cumulative cap; all costs remain within CAD100. Do not install tracking pixels, upload audiences, fabricate reviews, spam DMs or infer permission from a public email address.

### Browser and tests
Keep canonical Markdown as the source of truth. The updated browser adds launch-gate and budget-fit filters, displays the distinction between owner cash and customer quote hypotheses, and embeds the new marketing/research reports. Verify these along with existing deep-niche filters, source links, mobile readability and safe rendering. No SaaS/backend/agent scheduler is needed.

Run both test modules and all supplied checks; current package QA records 51 offline Python tests before local integration. Re-run after changes and report actual results rather than copying that count. Preserve all previous paid/progress evidence and confirm the v2 sources' full-page versus indexed status. Update the integration checkpoint only with work actually completed. Report files merged, conflicts retained, browser path, tests and the next selected planning action. Do not claim a sale, campaign or production workflow exists because this import succeeded.


## My objective

I want a portfolio of many businesses across niches and recursively nested subniches. A niche can contain subniches, which can contain more subniches, with no fixed logical depth limit. Each independently actionable project needs a living file that preserves what is finished, what remains, decisions, blockers, deliverables and a concrete next action. I need to browse the portfolio and resume any selected project without repeating completed work.

The current starting niche is small-business workflow automation, initially bounded n8n/Make/Zapier implementation and repair for agencies with customers. This is the initial research focus, not a permanent restriction on the whole portfolio. Native/deterministic solutions should be preferred when they solve the need; an AI label is not the commercial objective.

## 1. Inspect and reconcile first

Read the root `AGENTS.md`, current README, `business_portfolio/README.md`, `SCHEMA.md`, `REPO_PLACEMENT.md`, `research/REPOSITORY_RECONCILIATION.md`, `research/EXISTING_PROJECTS.md` and `QA_REPORT.md`. Inspect `git status`, branch/HEAD, existing files and applicable project instructions before editing. The research baseline was `7a99db00caea8d88a7abae943edeb3439b63d9c5`; do not assume the local checkout still matches it. Never reset, clean, stash, discard or overwrite unrelated local work automatically.

The new ZIP has the outer `business_portfolio/` directory and belongs at the repository root. If it is staged elsewhere or an earlier portfolio already exists, compare/merge by stable project IDs before copying. Use `research/MIGRATION_CROSSWALK.json` for the initial AWA-001 through AWA-120 paths, `research/V1_BASELINE_FILES.json` for the original package file hashes and `research/V2_PROJECT_AUDIT.json` for the v2 revision inventory. A matching ID is the same project even if its folder/title changed. Preserve any newer work logs and actual completed work; do not replace them wholesale with the planning snapshot.

The v2 package contains 139 records: 126 automation records, 12 existing-work records and SYS-001. There are 56 scoped service candidates (AWA-126 is explicitly an AWA-095 follow-on), 58 bundled components and 12 deferred download/software ideas. All 133 earlier record IDs remain; AWA-121 through AWA-126 are additions. There are 108 source records: 67 carried forward, 41 reviewed for this pass. These are research classifications, not active work orders or validated businesses. Treat the counts as snapshot expectations; legitimate newer local records may increase them.

## 2. Integrate additively, with one source of truth

Use this basic structure:

```text
business_portfolio/
  README.md
  PROJECT_TEMPLATE.md
  SCHEMA.md
  PROJECT_BROWSER.html
  PROJECT_INDEX.json
  research/
  fixtures/
  tools/
  tests/
  niches/
    <niche>/NICHE.json
    <niche>/README.md
    <niche>/projects/<stable-id>-<title>.md
    <niche>/<subniche>/...
```

Reuse and inspect the provided standard-library builder/browser rather than replacing them with a web framework, database, cloud backend, package-manager stack or another AI app. Keep the browser usable through `file://` without a server or API key. A niche may hold projects and child niches simultaneously. There must be no hardcoded “category/subcategory” depth ceiling. Respect Windows path/reserved-name limits with short slugs.

Canonical project records are Markdown with strict JSON frontmatter between `---` delimiters. Generated index/HTML must never become a second editable progress database. Read `SCHEMA.md` and preserve stable project and niche IDs. A niche rename/move changes its path and immediate-parent reference as needed, not its identity. Validate unknown/duplicate IDs, invalid paths, missing parents, cycles, malformed metadata, invalid state values and unresolved source/project references. Keep symlinks/private directories outside indexing.

Add a small root README navigation link to the new portfolio while retaining the Opportunity Library and current product links. Add a narrowly scoped section to existing project instructions explaining where canonical project records live and how agents checkpoint them; preserve all unrelated instructions. Add an existing dashboard link only if it is a small, compatible change—do not make desktop integration a large prerequisite to using the offline browser.

## 3. Preserve research and existing projects

Do not move/delete/rewrite the original `opportunity_library/`, `buissiness_research/`, `research_merge/`, product folders, launch outputs, master execution manual, source archives, private releases or legacy tools merely to make the new folders look tidy. `buissiness_research` is the actual spelling. Link to existing sources; promote a legacy candidate only after explicit selection and identity review. Do not create 1,512 active project tasks from the research library.

Reconcile these existing records against newer authorized local evidence:

- EX-001 cleaning calculator: reported public at CA$15; current v1.0.1 customer release and buyer hash recorded; Calc/file-format checks are not native Excel certification; paid demand/charged payment/payout unverified. Preserve current delivered bytes, not an unreviewed rebuild of authoring sources.
- EX-002 inventory planner: reported public at CA$9; final v1.0.1 filename; free-order delivery and buyer matching reported; native Excel and paid behavior unverified. Output is a reorder threshold/gap, not optimized order quantity. Recover actual private release path/hash locally if needed; do not invent them.
- EX-003 legal-name Payhip storefront/support: reuse existing store, PayPal connection, policies and contact setup. Old Cedargrid links and hidden CA$29/CA$19 test states are historical. Do not republish, rebrand or redo checkout tests just because a new chat started.
- EX-004 cleaning demo: reported 70-second captioned video, unpublished/private. Reuse only as an EX-001 proof asset after its actual private file is located and checked. Do not restart the withdrawn YouTube-channel proposal or recreate a missing video by default.
- EX-005 supplier service: preserve the reality check. K05/B01/K01/J01 are components of one unvalidated experiment, not four markets. Do not build its 96-entry catalog. Link overlapping AWA catalog modules rather than double-counting them.
- EX-006 synthetic reporting prototype: preserve its real existing builder and schema limitations; no paid customers are established. Recover an actual legacy ID only from evidence, never guess.
- EX-007 Computer Bridge: current internal tool, not a new commercial launch. Official Codex remains the interface.
- EX-008/009 Relay and standalone assistant: retained legacy. Preserve historical state/shared modules, do not revive these as the normal work interface.
- EX-010 Opportunity Library: preserve 1,512 research records and IDs; none automatically becomes commercially validated.
- EX-011 factory: preserve .local state, draft-only boundaries and unreconciled manual ledger semantics.
- EX-012 VaultDesk: inventory-only, progress unknown and unrelated. Do not restart or modify it without a separate task.
- SYS-001: update the integration checkpoint with changes/tests actually performed. Mark local integration complete only when its stated acceptance criteria pass.

Do not invent percent-complete numbers, actual revenue, orders, test results or progress for inaccessible private files. A checkmark imported from a report remains “reported” until you actually verify it. Keep chronology/conflicts visible; newer evidence may supersede old status without erasing the old record.

## 4. Progress, resuming and parallel work

Keep implementation/work state separate from commercial validation. “Published” does not mean paid demand; “tests passed” does not mean a successful business. Any paid/repeat-validation state requires a meaningful non-sensitive evidence reference to reconciled private records; a field populated by an agent is not proof of payment.

For each selected task, read the project record, relevant sources and latest private checkpoint before acting. Record current objective, completed work, remaining checklist, blockers, important decisions, exact artifact paths/version/hash when useful, test evidence and next action. On pause/interruption, leave a usable checkpoint. Do not regenerate an existing product or replay an upload/publication/order/payment because an earlier session ended.

Use one writer per canonical project record. Re-read and compare expected content/hash before a save, or use appropriate separate worktrees and reconcile changes. Fail visibly on concurrent modification rather than silently overwriting. Independent projects may proceed in parallel only within existing resources and actual authorization. Do not invent unlimited agents or hidden ongoing reasoning.

If a bridge project mapping is genuinely needed, store the mapping privately, preserve existing runtime ownership and IDs, and reuse the bridge’s durable queue/recovery model. Do not auto-create queue jobs for candidate records, re-key completed immutable jobs, wipe SQLite state, widen permissions, disable Stop or grant new browser/file authority. A JSON `execution_authorized` flag is descriptive, not a permission grant.

Uncertain external effects require actual-state reconciliation before retry. Record intent, target, stable event key, authorized scope and observed outcome; preserve ambiguity when it cannot be resolved. No automatic replay of consequential actions after a crash.

## 5. Keep commercial research honest and practical

The source register distinguishes full-page evidence, indexed snippets, repository reports and the handover. Job budgets are not earnings; market interest is not paid validation; template availability proves competition, not demand. Recheck dated or inaccessible evidence before consequential use, without turning this integration into weeks of new research.

The first proposed tests are AWA-005 or AWA-001 (one form → CRM → internal notification), with AWA-005/007/012 as alternative mapping/diagnostic entries. Preparation fixtures are fictional and have `not_run` results; do not label them as an implemented n8n workflow or a passed production test. Existing tools and native platform features should be checked before creating custom code.

The user’s goal is meaningful income with little upfront spending and limited ongoing manual work. Count all acquisition, communication, permissions, QA, rework and support hours. Keep hypothetical prices/hours separate from actual receipts and costs. Do not start a new storefront, SaaS, audience-building campaign or infrastructure overhaul by default.

## 6. Privacy and action boundaries

This task authorizes local architecture/content integration and relevant tests—not buying Connects/subscriptions/API credits/hosting, sending proposals or prospect messages, publishing products, changing accounts, placing orders, moving money or executing customer production workflows. No new recurring/scheduled tasks are implied. Preserve existing platform rules and sensitive-action approvals.

Do not automate Upwork scraping/applications through the bridge. Do not export credentials, signed URLs, real customer payloads, private payment records or paid product packages into this public repository or generated browser. Keep operational data in appropriately protected private storage; `.gitignore` is not encryption. Preserve legal-name storefront choices and existing policies; do not claim legal/tax/privacy/security certification.

Do not modify root-wide settings or unrelated user projects to make the import pass. Do not commit/push or publish changes externally unless my standing permissions for this project actually authorize that action; otherwise leave a tested local diff and report it.

## 7. Test and deliver the integration

Run the supplied checks and fix real failures:

```powershell
python business_portfolio/tools/build_browser.py
python business_portfolio/tools/build_browser.py --check
python -m unittest discover -s business_portfolio/tests -v
python business_portfolio/tools/commercial_checks.py --portfolio business_portfolio
```

Also run only relevant existing suites if their code is touched. Verify the browser in the user’s actual browser: offline open, search by ID/text, filtering a parent niche includes deeper descendants, existing-work filter, readable progress and source references, report view, empty results and mobile-width layout. Check that copied resume prompts identify the correct canonical record and do not grant external authority.

Exercise a temporary deeply nested niche/project fixture; duplicate IDs, invalid metadata/parents, cycles, unsafe URL/script text and unknown source IDs should fail safely or render as inert text. Verify private folders and symlinks are not exposed. Ensure a published-but-unvalidated product displays both states without converting it to “commercially complete.”

Check missing internal links, stale generated views, migration ID coverage and Windows path lengths. Confirm the original product/research paths and current launch links remain intact. Update/reconcile snapshot hashes only for the files you actually changed; never claim the original manifest matches edited content.

When finished, report what was merged, original files preserved, any unresolved local differences, exact browser path, commands/tests actually executed and their results, and the next actionable project recommendation. Distinguish package tests from Windows/bridge/customer/live-account tests. Do not end with an invented claim that the business is launched or money has been earned.
