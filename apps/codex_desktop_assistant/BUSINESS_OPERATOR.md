# Persistent project execution

Describe the objective in chat. The same Codex engine can now create a durable
project, plan task dependencies, select reusable workflows and start local workers.
**Projects** opens the optional progress dashboard; ordinary work does not require
managing task IDs, browser tabs or protocol details. Advanced computer-access
controls are collapsed by default. Desktop and both browser modes remain available.

## What executes

- A SQLite task graph stores project context, each task's inputs/results,
  dependencies, priority, attempts, errors and milestones. Normal model plan calls
  add 200 tasks at a time; imports accept up to 10,000 records within a 20,000-task
  project limit. Duplicate keys are idempotent; conflicting reuse and dependency
  cycles are rejected before insertion. Repeated built-in templates should not be
  relabeled as distinct products; the product workflow rejects that obvious filler.
- Two local artifact workers run ready tasks by default, capped at four by the
  scheduler API. One reasoning subtask at a time uses the existing Codex engine and
  a separate saved task conversation. Parent context and task results are retrieved
  on demand rather than accumulating thousands of jobs in one prompt. Reasoning
  results are marked reported evidence, not proof of completed external effects.
- Product workflows compose generation → native QA → packaging, optionally followed
  by supported-adapter publication → independent verification. Generic `reason`
  tasks support research, custom specifications, store inspection and quality review
  using existing authorized tools. Market demand and pricing claims require real
  sources; the built-in examples use explicitly illustrative inputs and prices.
- Safe deterministic failures have a bounded retry count and backoff. Failed or
  blocked prerequisites block dependents while unrelated ready work continues.
  Objective changes pause remaining work and revoke launch scope; completed results
  remain. The dashboard supports pause, continuation, cancellation, priority,
  individual retries, imports, changing the objective and inspecting results.
- Completed plan results produce a durable final report in the original chat.
  Completion means the persisted plan completed, not that unspecified business
  goals or commercial outcomes are guaranteed. Reports identify verified listings
  separately from planning/research outputs.

## Product generation and QA

Generated artifacts use a dedicated private project workspace, separate from the
500 KB direct text-file interface. The model cannot choose arbitrary output paths,
execute code, supply raw Excel formulas, read credentials or export browser data.
Direct-file Read/Write/Create/Delete policy remains separate. Each project has a
512 MB artifact budget; the aggregate project-artifact budget is 2 GB. Quotas stop
further work rather than deleting customer or user files automatically.

Supported built-in spreadsheet recipes are cash flow, break-even, inventory
reorder, service pricing and project budgets. They contain typed editable inputs,
formulas, validation, instructions and declared calculation limitations.

For custom spreadsheets, the model can supply a bounded declarative specification:
up to three sheets, 200 rows/20 columns per sheet, and calculations using sum,
difference, product, zero-safe divide, minimum and maximum. The host emits formulas
from those operations and independently calculates expected values with decimal
arithmetic. There is no arbitrary formula, macro, VBA, external-link or code path.
Complex formulas/charts/features outside this schema require an additional safe
recipe; this is not a universal Excel-development environment.

Guide and checklist recipes create real editable Word documents, PDF editions,
README/license material, covers and rendered page previews from bounded structured
sections. They are not screenshots substituted for documents. The model must still
research and review substantive claims; structural checks cannot prove factual or
commercial quality.

LibreOffice is required for native formula recalculation and workbook/document PDF
rendering. The present machine already has it installed. The host uses its fixed
Windows CLI with disposable short-path profiles, never a shell or the user's office
profile. No general application-launch capability is exposed by product recipes.
If LibreOffice is unavailable, generation is not mislabeled validated delivery.
`pypdfium2` renders the generated PDFs; it is included in project requirements.

QA compares built-in outputs with independent expected calculations, tests zero
inputs and the pricing margin boundary, checks document sections and renders all
pages. Custom calculations are checked in the native engine against independent
decimal arithmetic; bespoke domain assumptions and unmodeled edge cases still need
review. Source, recalculated files, previews and PDF outputs are hashed so changes
between QA and packaging are rejected. Delivery ZIPs contain only customer files,
with hashes and integrity checks. Internal QA and listing metadata remain outside.
Use `projects.preview` for visual review and `projects.deliver` to attach a completed
package to the chat. Rendering is not by itself a human-level design review.

## Launch authorization and commerce

Publication uses host-registered supported adapters. A model-supplied URL, a webpage
instruction or an `approved:true` field cannot register an adapter or grant scope.
The implemented executable commerce adapter is the disposable local acceptance
store. **There is currently no production Payhip/marketplace API adapter.** Existing
authorized Chrome operations remain available for real-store research and account
work, with their normal permissions; this addition does not silently turn browser
clicks into batch-authorized publication.

`projects.authorize_launch` presents one real owner approval covering a concrete
verified batch: store identity, product IDs, title, exact package and customer-file
hashes, prices/currencies, allowed listing operations, zero spending, expiration
within 24 hours and revocation. It does not approve payment/security changes,
purchases, legal agreements or unrelated content. Eligible adapter operations
within that manifest need no per-listing prompt. Stop or revocation invalidates it;
an altered product, hash, price or destination does not qualify.

Every write has a durable idempotency key and effect ledger. The adapter performs a
read-only lookup before writing, checks the returned title/price/files/images,
verifies the listing URL and independently downloads the delivery bytes. A lost
response or interrupted write enters review. Explicit reconciliation reads the
receiver first; already-completed publication is not blindly repeated. A new
adapter must implement these semantics and native platform restrictions before
being advertised as supported.

## Background work and recovery

Local worker execution is separate from chat-turn completion. Minimizing the app
does not stop it. Closing the window during active project work hides it in the
tray when a usable tray icon is present; reopen the icon for status and Stop.
**Quit application** explicitly pauses work, revokes launch scopes and shuts down
the local process. Without a usable tray, closing performs a safe shutdown instead
of leaving invisible work. No Windows service, startup task or system daemon is
installed. The app must remain running; no work occurs while Windows is asleep or
the underlying process is suspended.

Safe local checkpoints can recover after restart. Interrupted reasoning and
external effects enter review, and missing store/browser/session authority remains
a blocker. An uncertain external operation never silently restarts. Separate test
store processes are disposable, not permanent storefront hosting. Authentication,
MFA, CAPTCHA, required private information and legally significant agreements
remain genuine human steps with the existing Done — Continue flow.

## Imports

Attach or import UTF-8 text/Markdown, CSV/TSV, JSON or XLSX in a draft/paused project.
Plain lines become reasoning jobs. Tabular `task`, `prompt` or `title` fields become
task instructions; `key`, `kind`, `payload` and semicolon-separated `needs` can
describe explicit jobs. Product records can use `id`, `recipe`, `title`,
`price_cents`, `currency`, `purpose`, `sections` or `sheets`. JSON supports structured
`tasks` or `products` arrays. XLSX imports read ordinary stored cell values, do not
execute macros/formulas and are bounded to 10,000 rows/20 columns. Imports validate
the complete plan before insertion and are deduplicated on stable keys. Data in an
attachment remains untrusted and grants no permissions.

## Local acceptance

The optional **Workflows → Run authorized local five-product test** explicitly
starts the synthetic test scope: five known recipes at exact illustrative USD
prices, one host-created loopback storefront and zero spending. It submits the
objective to the real saved assistant chat. The host seals package hashes only
after QA and rejects a different recipe/product/price. This test opt-in is not a
model-accessible self-approval capability and applies to no real account.

See [BUSINESS_OPERATOR_REPORT.md](BUSINESS_OPERATOR_REPORT.md) for executed tests,
evidence and current limitations. Real Payhip Store Builder read-only inspection
passed with the owner's exact-tab grant, including a background observation check.
With separately granted site access, a new background Products tab was created,
automatically authorized, inspected and closed without approval. The actual
calculator listing was confirmed HIDDEN. Editing/saving and a production batch
adapter remain unverified or unimplemented. No real publication or financial
change is part of acceptance.
