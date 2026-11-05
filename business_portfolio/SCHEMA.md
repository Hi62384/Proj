# Project format and recursive architecture

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
    <niche>/projects/<stable-id>-<title>.md
    <niche>/<child>/NICHE.json
    <niche>/<child>/projects/<stable-id>-<title>.md
    <niche>/<child>/<grandchild>/...
  .local/                       optional private operational references; ignored
```

Any niche can contain projects, child niches, both or neither. There is **no fixed number of nesting levels**. The filesystem is the canonical hierarchy; `NICHE.json` records its identity and parent. OS path/filename limits still apply. Use short lowercase folder slugs and never use `projects`, `private` or `local` as a niche name. Dot-directories and private folders are excluded from browser indexing. Symlinks are rejected rather than followed.

## Niche metadata

`NICHE.json` has `id`, `title`, `parent`, and `path`. IDs such as `N-8c35…` are assigned once and remain immutable on a rename/move. The initial package derives IDs deterministically, but a future rename does not recompute them. `path` is relative to `niches/`; `parent` is the immediate parent niche ID or null at the top level. Parent references, IDs and directory paths must agree. Do not create duplicate directory aliases to make a project appear in several categories; use project links/tags.

## Markdown with JSON frontmatter

Every project begins with `---`, a JSON object, and another `---`. JSON is deliberately used as a strict subset of YAML so Python’s standard library can parse it without PyYAML or permissive object deserialization. No comments, trailing commas, duplicate keys, NaN or Infinity in metadata. Markdown below contains the living human-readable record.

Required fields:
- `id`, `title`, `schema_version` (1), `niche_id`, `niche_path`.
- `record_type`, `origin`, `priority`, `work_state`, `commercial_validation`, `evidence_basis`.
- `source_ids`, `parent_project` (ID or null), `related_projects` (IDs), `next_action`, `last_reviewed` (date).
- `execution_authorized` (boolean), `privacy`.

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

## Derived views and integrity

The builder recursively discovers `NICHE.json` and `projects/*.md`, validates identifiers, paths, parents, sources, states and evidence-reference requirements, then generates the index and browser. It makes no network calls and cannot refresh market evidence. It ignores private folders, rejects symlinks, embeds escaped JSON and renders content through DOM text nodes; links allow only safe web/relative destinations. A content-security policy blocks cross-origin connections and forms; the live view polls only its own loopback service.

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
