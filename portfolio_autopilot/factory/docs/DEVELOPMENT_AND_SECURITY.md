# Engineering guide and threat boundaries

## Architecture

`portfolio_autopilot/factory/` is independent of the old `portfolio_autopilot/cli.py`; the factory reuses the proven atlas reader/shortlist and reporting core without rewriting the source financial models.

- `config.py`: private paths, seller profile allowlist, safe IDs.
- `catalog.py`: complete existing research index and diversified selection.
- `kits.py`: original review-only launch docs, intake, preliminary offer and locally viewable landing preview across business models.
- `first_business.py`: packaged synthetic reporting demonstration plus review-only sales materials.
- `portable_runner.py`: strict configured CSV columns, limits and the existing report-builder tests/renderer.
- `reporting.py`: ZIP packaging, manifests with SHA-256, private workspace boundaries and no source-file upload.
- `ledger.py`: SQLite pseudonymous tasks, human-reported financial/owner-time events, idempotent CSV import and local review requests.
- `storefront.py`: combines prepared product drafts into one unpublished catalogue mockup.
- `portal.py`: loopback-only HTTP server; CSRF token, restrictive Host/Origin checks, request limit, no network clients, only safe draft writes.
- `cli.py`: single entry point for all actions.

## What is deliberately NOT implemented

No agentic browser automation, unauthorized crawling, live provider polling, unsolicited email sending, token-consuming AI inference, hosted SaaS, production checkout, webhooks, credential collection, real-time customer account management, or automatic deployments. Those require provider connections, user approval, separate threat modeling and real tests.

## Security invariants

- Products are in `research_draft`; the local UI cannot publish anything. Approval requests only record a local reviewed/declined note.
- The server binds to **127.0.0.1** only, rejects unexpected Host/Origin, accepts bounded JSON with CSRF token, and serves no customer files or payment data.
- Seller profile has an allowlist; unknown keys (such as API credentials) cause failure. Limit defaults to CAD 0.
- All generated business kits carry unvalidated-demand warnings and omit claims of actual sales or proof.
- Regulated ideas are excluded from automatic shortlist and kit preparation unless separately reviewed; original legacy research references can be drafted but require their own review.
- Reporting rejects missing/mapped-header collisions, malformed rows, duplicates, unapproved currencies/formatting, enormous inputs, and unexpected overwrite paths.
- Customer delivery is staged atomically, hashed and ZIP-tested before being made available. This is **a local QA package**, never a claim of completed delivery.
- The imported manual ledger enforces unique provider-style IDs and all-or-nothing CSV import. Payout events are not counted as new revenue.
- The original 14 reporting tests remain untouched and should continue to pass.

## Privacy limitations

`portfolio_autopilot/.local/` is Git-ignored but **not encrypted**. Do not store secrets, raw customer documents or personal information there without additional controls. For real confidential client work use a separately approved private storage location, restrictive file permissions, deletion/retention rules and contracts. For multitenant hosted products, add proper authentication, tenant isolation, independently reviewed webhook handling, secrets management, audit logging and restore tests.

The static offline landing preview is intentionally not a public checkout and must not be represented as a launched business.

## Test instructions

From repository root:

```powershell
python -m unittest discover -s portfolio_autopilot/tests -v
python -m unittest discover -s portfolio_autopilot/factory/tests -v
cd research_merge\reporting_demo
python -m unittest discover -s tests -v
```

Return to root before using the factory CLI. GitHub Actions runs the same suites in a clean runner and prepares a synthetic smoke build; never give CI secrets just to generate preview packs.

## Extension procedure (future work)

Each provider adapter is a separate, reviewed implementation. It needs typed inputs, least privileges, explicit permission scope, idempotency, retries, cost caps and log redaction. For production payment events: verify signatures, prevent replay/double fulfillment, reconcile provider payouts and cancellations, and enforce entitlement and retention rules. A cloned placeholder is not a working integration.
