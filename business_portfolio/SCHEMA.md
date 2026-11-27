# Project format and recursive architecture

## Current editable business view

`niches/` initially has five primary categories: Digital Products, Digital Content, Services, Ecommerce and Investing. Together they contain the original 25 niche folders; nine narrower legacy niches are nested below the closest equivalent and retain their previous stable IDs. Every node has a `working` boolean, initially false for newly created nodes. Enabling a niche also enables its ancestors. Disable Working descendants before disabling a parent. The Working flag is informational focus only and does not represent project completion, authorization or worker activity. `digital-products/game-development-marketplaces` retains stable ID `N-gdm-20261115`; active projects are read from current records, not historical fixed counts. The owner can create nested niches or recoverably delete a selected subtree through Portfolio Manager. Sibling `priority` values control display order. The opportunity library's 36 categories and 144 subcategories remain independent research.

The previous 182-node active tree, including the original GDM record bytes, is preserved in `archive/2026-11-15-taxonomy-view-v1/` with a 185-file checksum manifest and GDM ID/path crosswalk. The older 139-record archive at `archive/2026-11-15-legacy/` is unchanged. The builder validates both snapshots and exposes the 139 older records under `archived_records`; the prior taxonomy snapshot remains a rollback/evidence source, not another active project list. Product implementation specifications were appended to the moved GDM records; their IDs, planned/unvalidated status, commercial permissions and original planning history remain intact.

## Prior taxonomy-view notes (historical)

## Earlier active taxonomy and history (2026-11-15)

`niches/` contains the current 36-category / 144-subcategory taxonomy, Game Development Marketplaces, AI Workflow Automation, and only GDM-001 through GDM-003 as active project-family records. Empty niches need only `NICHE.json`. Prior canonical records retain their original IDs, bytes, metadata and checklist history in `archive/2026-11-15-legacy/niches/`. The dated crosswalk maps former and archived paths; the manifest contains SHA-256 and byte length for all 301 original niche files. `build_browser.py` validates these before including `archived_records` in the generated read-only index. Do not edit the archive in place or treat an archived published record as cancelled. A restored project must be reviewed against the latest private checkpoint and current external state, assigned a valid active niche ID/path, and checked for an ID collision. Private receipts and customer material remain outside the public index.

The generated index has `records` for active projects and `archived_records` for preserved history. Consumers must not infer that absence from `records` means deletion. Niche nodes may have zero projects. `planning_lane` on the three new families distinguishes the first validation focus from queued ideas; it is not commercial authorization. An intentionally restored active copy with an old ID must include `restored_from_archive_sha256` matching the archived crosswalk, so the builder can distinguish restoration from accidental ID reuse.

## Layout

```
business_portfolio/
  README.md
  PROJECT_TEMPLATE.md
  PROJECT_BROWSER.html           generated, read-only, offline
  PROJECT_INDEX.json             generated; never the progress source of truth
  SCHEMA.md
  CODEX_IMPLEMENTATION_PROMPT.md
  REPO_PLACEMENT.md
  QA_REPORT.md
  research/                     evidence, assumptions, reconciliation, crosswalk
  fixtures/                     fictional acceptance specifications, not workflows
  tools/                        standard-library builder + browser template
  tests/                        package tests, not customer workflow tests
  niches/
    <niche>/NICHE.json
    <niche>/README.md
    <niche>/<stable-id>-<slug>/project.md
    <niche>/<stable-id>-<slug>/work/.gitkeep
    <niche>/<child>/NICHE.json
    <niche>/<child>/<stable-id>-<slug>/project.md
    <niche>/<child>/<stable-id>-<slug>/work/.gitkeep
    <niche>/<child>/<grandchild>/...
  .local/                       optional private operational references; ignored
```

Any niche can contain projects, child niches, both or neither. There is **no fixed number of nesting levels**. The filesystem is the canonical hierarchy; `NICHE.json` records its identity and parent. OS path/filename limits still apply. Use short lowercase folder slugs and never use `projects`, `private` or `local` as a niche name. Dot-directories and private folders are excluded from browser indexing. Symlinks are rejected rather than followed.

## Niche metadata

`NICHE.json` has `id`, `title`, `parent`, `path`, integer `priority`, and boolean `working`. IDs are assigned once and remain immutable on a rename/move. `path` is relative to `niches/`; `parent` is the immediate parent node ID or null for one of the five root categories. Parent references, IDs and directory paths must agree. New nodes default to `working: false`. Portfolio Manager updates this boolean in the selected node and, when enabling it, its ancestors through validated atomic metadata updates guarded against concurrent writers. The generated project browser displays the flag read-only. Do not create duplicate directory aliases to make a project appear in several categories; use project links/tags.

## Markdown with JSON frontmatter

Every project begins with `---`, a JSON object, and another `---`. JSON is deliberately used as a strict subset of YAML so Python’s standard library can parse it without PyYAML or permissive object deserialization. No comments, trailing commas, duplicate keys, NaN or Infinity in metadata. Markdown below contains the living human-readable record.

Required fields:
- `id`, `title`, `schema_version` (1), `niche_id`, `niche_path`.
- `record_type`, `origin`, `priority`, `work_state`, `commercial_validation`, `evidence_basis`.
- `source_ids`, `parent_project` (ID or null), `related_projects` (IDs), `next_action`, `last_reviewed` (date).
- `execution_authorized` (boolean), `privacy`.

For the six-phase workflow, new records also set `workflow_version: 2`, `project_phase: "working_phase_1"`, `draft: true`, `record_type: "empty_project"`, and `delivery_window_days: {"minimum": 2, "maximum": 21}`. Empty projects are valid planning records; no GO verdict, source or completed work is invented. They cannot advance until replaced with meaningful research and a descriptive title. A researched record uses `draft: false` and an appropriate record type such as `product_candidate`.

Version-2 and version-3 records may use an empty `source_ids` array: direct dated research URLs can be recorded in the Markdown. Nonempty source IDs must still exist in SOURCE_REGISTER.json; preserve original IDs when updating. Optional `research_verification` uses `phase_1`, `phase_2`, `phase_3` with values `unreviewed`, `approved`, `needs_revision` or `blocked`. This is research assessment, not execution authorization or proof of commercial success. `research_verdict` records the evidence-based recommendation; inherited GO_TO_PHASE_B wording is historical, not a current phase name. `platforms_proposed` lists planning targets; `platforms_supported` requires observed product evidence.

The supplied records also include historical IDs, owner, hypothetical quote/hour ranges, verified-pilot count and unknown actual revenue/profit. Null means unknown/not established, never zero. `verified_paid_pilots: 0` for candidates means this research verified none; it does not claim to inspect all user accounts.

`record_type` describes whether a record is a standalone service candidate, bundled component, deferred download/software, existing product/tool/operation, inventory-only record or system task. Classification is a planning judgement, not a license or a measured success probability. The browser supports further non-empty record types; add meaningful types rather than duplicating offers.

`origin` distinguishes `revised_candidate`, `existing_work` and `current_package`. `priority` is one of P1, P2, P3, BUNDLE, DEFER, PRESERVE or INTEGRATE. The first three are proposed commercial sequencing, not automatic execution priority. PRESERVE is explicitly not “start over.”

## Work and commercial state are independent

Allowed work states: planned, deferred, active, blocked, ready_for_test, completed, cancelled, archived, paused, published_reported, operational_reported, prototype_reported, legacy_preserved, needs_reconciliation, package_ready.

Allowed commercial states: unvalidated, published_unvalidated, not_applicable, unknown, unvalidated_catalogue, buyer_signal, paid_pilot, repeat_paid, commercially_validated.

A product can be published and commercially unvalidated. A prototype can pass tests and have no buyers. Internal tooling has no commercial validation requirement. `commercially_validated` must not imply guaranteed future profit; document the exact evidence and remaining uncertainty.

Paid/repeat/commercial validation requires a `validation_evidence_ref` pointing to a non-sensitive reference for reconciled private evidence. Never put receipts, buyer identity or payment details in public records. The validator can require the reference’s presence but **cannot verify the payment**. A human/authorized evidence review still must establish the claim.

`execution_authorized` is descriptive metadata, never an access-control grant. Even setting it true does not authorize a purchase, message, publication or customer-account action. Existing permission systems remain authoritative.

## Resumable body requirements

Keep purpose/buyer, evidence and alternatives, scope/exclusions, acceptance tests, costs/owner labor, completed work, remaining checklist, blocker, next action, decisions, deliverable locations, uncertain external effects and dated work log. Distinguish observed events from estimates. A parent project can have separately tracked components, but do not double-count their hypothetical revenue.

Before resuming: read the whole record and relevant later private checkpoint; inspect the actual owned artifacts; reconcile uncertain external effects; preserve completed work; append new evidence; update one concrete next action. Use one writer per record or compare the expected file hash/version before replacing it. Do not mark old work incomplete merely because it was absent from a new conversation.

## Fast build-and-learn default

For new product projects, do not make interviews, outreach, or access to another person's project a prerequisite for starting useful work. Prefer a small local prototype, synthetic or public test data with clear rights, automated checks, and a written record of what worked or failed. Build breadth through bounded experiments, then use those results to decide what to improve, pause, or revisit. Keep demand and technical evidence separate: a passing prototype does not prove buyers, and a failed prototype is useful learning rather than a reason to require a survey before the next idea.

Human participation is required only where the task itself depends on consent, private/customer data, access to a third party's project or account, a legally required review, or a real buyer's acceptance/payment. In those cases, keep the dependency narrowly scoped and owner-approved. Interviews and buyer feedback can be optional evidence, but must not block a local prototype by default. Existing budget, privacy, licensing, publication, contact, and safety permissions remain unchanged; this policy does not authorize spending or external actions.

## Derived views and integrity

The builder recursively discovers `NICHE.json` and direct niche-owned `<stable-id>-<slug>/project.md` records, while recognizing old `projects/*/project.md` and standalone `projects/*.md` layouts during migration, validates identifiers, paths, parents, sources, states and evidence-reference requirements, then generates the index and browser. It makes no network calls and cannot refresh market evidence. It ignores private folders, rejects symlinks, embeds escaped JSON and renders content through DOM text nodes; links allow only safe web/relative destinations. A content-security policy blocks cross-origin connections and forms; the live view polls only its own loopback service.

Rebuild after record changes. `--check` fails on stale/missing generated views and invalid records without writing source files. Generated views include public record bodies; marking a public file “private” is not a substitute for keeping actual sensitive data outside the indexed tree.

`MANIFEST.json` and `CHECKSUMS.sha256` describe this delivered snapshot. They are not a runtime signature, encryption or a paid-validation certificate. If Codex edits the package, it must regenerate/reconcile the manifest or label it historical rather than pretend the original hashes still match.


## Revision 2 commercial fields
Schema version 1 remains readable; `commercial_revision: 2` enables stricter optional commercial metadata checks. No project or niche ID changes are needed.

`owner_budget` contains currency (CAD), preferred/planned upfront amounts, authorized spending, cumulative hard ceiling (at most 100), optional itemized envelope and its total, budget fit, review window, recurring owner allocation and production-cost responsibility. A later positive authorization needs an explicit approval reference; data fields do not themselves authorize a tool or payment. Unknown costs must remain unknown until preflight, not silently become zero.

`launch_gate`, `marketing_lane`, `pre_sale_work_cap_hours`, `ad_test_cap_cad`, `production_budget_verified`, `marketing_execution_authorized`, `success_probability` and `offer_price_cad_hypothesis` keep marketing readiness distinct from execution/commercial state. `historical_price_usd_hypothesis` preserves an old proposed price; `offer_price_usd` is null in v2 candidates to prevent treating it as the current quote. Current CAD quotes are editorial hypotheses, not FX conversions or verified buyer acceptance.

`economics_scenarios` and `stress_quote_floor_cad_assumption` are optional explicit sensitivity calculations, not actual financial records. No scenario may populate `actual_revenue`, `actual_profit` or paid-pilot counts. Follow-on AWA-126 points to AWA-095; components retain their parent-only classification. The local validator is not a transaction-control system.


## Live view and public results

`Open_Project_Browser.cmd` starts/reuses the standard-library, read-only loopback service. It rescans public inputs, debounces edits and retains the last valid snapshot on incomplete writes. The browser preserves stable selection, search and expanded niche folders during updates. Generated HTML/JSON remain offline snapshots, not an editable database. Direct HTML opening clearly says live updates require the launcher.

A record may declare up to 20 explicitly public text results:

```json
"public_results": [
  {"label": "Fictional acceptance report", "path": "results/AWA-001/acceptance.md"}
]
```

Use only reviewed, non-sensitive `.md`, `.txt`, `.csv` or `.json` files inside `business_portfolio/results/<the same stable project ID>/`. The record and result file are watched; a new file appears without a browser rebuild. This declaration is not an external publication, spending or filesystem-permission grant. Do not put credentials, real leads/customer documents, private receipts, account information or paid product packages here. The namespace is public planning content, not protected private storage. A narrow secret-pattern check is a safeguard, not privacy certification.

The local service rejects cross-project paths, traversal, symlinks/reparse points, hard-linked files, private folders, unsupported binary releases and recognizable credentials/private buyer links. Files & Results separately labels canonical records/source guides, public results, existing product URLs and withheld/missing assets. Existing arbitrary repository folders are never automatically exposed. Adding another existing asset requires an explicit safe source-guide registry entry and review. No OS folder-open or arbitrary command endpoint exists.


## Project folders, phases and retained completions

Current projects use `niches/<niche>/<stable-id>-<slug>/project.md` plus a sibling `work/`. There is no active `projects/` intermediary folder. The manager shows the record directly beneath its niche. Every niche may contain child niches and projects; the builder identifies their metadata and rejects duplicate IDs and unsafe linked paths. All project-owned implementation, content, tests, assets, builds, releases and marketing files belong in `work/`, which is required for folder-based canonical records.

workflow_version 3 defines four phases independently of work state and commercial validation:

| Value | Meaning | Forward handoff |
| --- | --- | --- |
| working_phase_1 | Phase 1a product, release and marketing research, with each stage verified before proceeding; Phase 1b independent verification of all three | Verified final paste automatically advances to Phase 2 |
| working_phase_2 | Build, test and package accepted versions | Codex to Phase 3 |
| working_phase_3 | Actually release and verify accepted destinations | Codex to Phase 4 |
| working_phase_4 | Execute and verify the finite initial marketing plan | Codex to Complete |
| complete | Verified delivery/release/initial marketing receipt | Reopen explicitly for corrections |

Forward handoffs are sequential. Research cannot be advanced via the phase control or execution command. Codex execution handoffs require --workflow-version 3, actor codex and factual evidence, recorded in phase_history; the actor label is not authentication or independent verification. Build completion may supply a meaningful title without changing ID/path. Confirmed owner execution overrides remain unverified. Reopening preserves work and revokes a matching completion receipt when applicable.

Version 2 maps old Phases 1–3 to research Phase 1, old 4 to build Phase 2, old 5 to release Phase 3 and old 6 to marketing Phase 4. Complete is unchanged. Older local records are interpreted according to their original workflow version and upgraded on save, preserving historical evidence, work and progress without inferring approvals.

### Pasted research updates

Only Phase 1 accepts complete replacement research text, with strict JSON frontmatter, optionally enclosed in one Markdown fence. Preserve identity, current phase, workflow, work state, financial evidence, permissions, source IDs and existing history. Planning fields can be revised, including title, draft, record_type, priority, evidence_basis, source_ids, research_verification, research_verdict, platforms_proposed, next_action, last_reviewed and the delivery window. The day limit is shared across all stages and phases.

project_update_base_sha256 is the exact temporary BASE_SHA256 fingerprint from the copied prompt. Phase 1a must not declare verification complete. In Phase 1b only, project_update_phase_1b may be "verified" after all three internal stage approvals (research_verification.phase_1 product, phase_2 release, phase_3 marketing), a GO verdict, a substantive non-draft record and complete required headings with content and research URLs. A verified valid paste automatically advances to Phase 2 in one transaction. Other drafts remain in Phase 1. Even a no-change Phase 1b review returns the full record. Both transport fields are removed. The importer checks schema, identity, snapshot and structure, not independent truth of market claims. The original bytes are backed up under ignored .local/project_backups/<ID>/. Invalid metadata, concurrent edits and rebuild failure leave the prior record/views intact. Work artifacts, execution permissions and paid evidence are never created or replaced by paste.

### Progress, important data and URLs

Each execution-phase checkpoint records the exact plain-text line `Phase N completion estimate: X% (best guess)` for N=2,3,4. Include the basis, completed and remaining checklist, evidence, blockers, decisions, external-effect state and one next action. This is an estimate, not a measured fact or evidence of completion. The owner-selected project day limit covers all four phases; required external delays remain visible.

Maintain an Important data and URLs ledger incrementally for useful artifact paths, versions/hashes, IDs, configuration/results/commands/costs and source/docs/build/preview/live/upload/purchase/download/edit/admin/marketing/support/analytics links. Record purpose, status and last checked date, preserve retired URLs, and distinguish planned destinations from observed live pages. Do not put passwords, tokens, signed session URLs or private customer/payment data in public records.

### Durable completion receipts and recoverable niche deletion

On verified Phase 4 completion, `completed_projects/<PROJECT-ID>.json` records a factual description, actual verified public sale/download/delivery URLs, verified public marketing links and other relevant URLs. Completion requires the factual summary plus at least one sale/access link and at least one marketing link. Codex supplies them after checking; the owner is not asked to enter links or click Complete. A receipt is independent of the original project folder and survives its removal. Completion does not assert sales, profit or commercial validation.

A confirmed niche/subniche deletion moves the selected subtree to `.local/deleted_niches/` and rebuilds the active view. Historical archives and completion receipts remain independent. References from surviving active projects must be resolved before deletion; restoration requires reviewing original paths and ID collisions. New niches start Not Working. The original taxonomy counts are historical starting structure, not a restriction against owner-created or deleted niches.
