---
{
  "id": "EX-006",
  "title": "Synthetic CSV operational-reporting service prototype",
  "niche_path": "services/reporting/csv-delivery",
  "record_type": "existing_service_prototype",
  "origin": "existing_work",
  "priority": "PRESERVE",
  "work_state": "prototype_reported",
  "commercial_validation": "unvalidated",
  "evidence_basis": "repository_or_user_report",
  "source_ids": [
    "R06",
    "V2-33",
    "V2-08"
  ],
  "parent_project": null,
  "related_projects": [],
  "legacy_ids": [],
  "next_action": "Preserve the prototype. Reuse it only when a funded, in-scope reporting request matches the supported schema; do not restart another generic dashboard business.",
  "offer_price_usd": null,
  "delivery_hours_assumption": null,
  "total_first_order_hours_assumption": null,
  "verified_paid_pilots": null,
  "actual_revenue": null,
  "actual_profit": null,
  "owner": "user",
  "execution_authorized": false,
  "privacy": "public_sanitized_progress",
  "schema_version": 1,
  "last_reviewed": "2026-11-05",
  "niche_id": "N-9b8efa3e36ac",
  "commercial_revision": 2,
  "owner_budget": {
    "currency": "CAD",
    "preferred_upfront": 0,
    "planned_upfront": 0,
    "authorized_spend": 0,
    "hard_ceiling": 100,
    "owner_recurring_monthly": 0,
    "budget_window": "Cumulative incremental owner launch cash/commitments; review at first sale or 30 days, whichever comes first. No automatic cap reset after a sale or new month.",
    "includes": [
      "tax",
      "currency_conversion_cost",
      "noncancelable_commitments",
      "proposal_credits",
      "demo_API_cost",
      "advertising",
      "hosting"
    ],
    "unknown_cost_action": "Pause; do not treat missing costs as zero.",
    "production_runtime": "Existing historical costs are unknown. Do not relabel sunk spend as zero or create new subscriptions.",
    "budget_fit": "incremental_preservation_only",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  },
  "marketing_execution_authorized": false,
  "success_probability": "not_established",
  "production_budget_verified": false,
  "marketing_lane": "reuse_prototype_buyer_test",
  "launch_gate": "buyer_test_only",
  "pre_sale_work_cap_hours": 2,
  "ad_test_cap_cad": 0
}
---
# EX-006 — Synthetic CSV operational-reporting service prototype

## Current position
**Work state:** `prototype_reported`. **Commercial validation:** `unvalidated`. Evidence reconciled on 2026-11-05 against repository commit `7a99db00caea8d88a7abae943edeb3439b63d9c5` and the supplied handover.

This record preserves existing work; it does not restart it. Checkmarks below mean the cited repository/handover reports completion, except SYS-001 where they describe files prepared in this package. They are not fresh local Windows, customer-account, payment or native-application tests.

## Completed work
- [x] The factory guide records a tested synthetic reporting builder and sample delivery process.
- [x] Explicit header mapping, preflight checks and HTML/CSV/JSON report packaging are implemented according to repository documentation.
- [x] Portable report runner and synthetic customer-delivery ZIP generation are described; no real delivery is implied.

## Remaining work and blockers
- [ ] No paid customer, validated acquisition route or live deployment is established.
- [ ] Original mapping supports five required fields, not universal arbitrary accounting data.
- [ ] Recover actual legacy opportunity ID from the local first-business pack if one exists; do not guess its identity.

**Unknown / not verified:** This review did not rerun the old builder, inspect the private factory state or verify an exact legacy opportunity ID.

**Revenue, profit, paid orders and owner time:** unknown unless supported by a later private ledger and reconciled evidence. A public listing, free checkout, synthetic fixture or packaged file is not a paid customer. No completion percentage or fictional financial total is assigned.

## Resume checkpoint
**Next action:** Preserve the prototype. Reuse it only when a funded, in-scope reporting request matches the supported schema; do not restart another generic dashboard business.

**Do not repeat:** completed authoring, launch/setup, uploads, publication, test checkouts or infrastructure migrations merely because a new chat began. Read later local evidence first. Any uncertain consequential effect must be reconciled before a retry.

**Deliverable/source locations:**
- `research_merge/reporting_demo/report_builder.py`
- `portfolio_autopilot/factory/first_business.py`
- `portfolio_autopilot/.local/factory/`

Locations are repository references or historically reported private roots, not proof a particular local file still exists. Current private release bytes, signatures, customer data and credentials are deliberately absent from this ZIP.

## Important decisions to preserve
- Keep synthetic samples separate from customer data.
- Manually entered revenue/settlement ledger data are unreconciled; a payout is not another sale.
- AWA reporting candidates are related hypotheses, not evidence the existing prototype has customers.

## Evidence and state reconciliation
- [R06](https://github.com/Hi62384/Proj/blob/7a99db00caea8d88a7abae943edeb3439b63d9c5/portfolio_autopilot/factory/README.md) — Factory guide. Access: `connector_full`; evidence type: `repository_report`.

Newer current product/launch summaries override older hidden-listing prices in historical integration tests. Keep the original evidence and its date rather than rewriting it to look current. If a later local record conflicts, record both, inspect actual authorized state and explain the resolution.

## Work log
- 2026-11-05: added this sanitized progress record; did not edit the original project, queue, live store or customer account.
- Next entry: append observed action, artifact/hash or evidence reference, result, blockers and next action. Do not store credentials, private order details or client documents here.

## V2 budget and execution boundary
**Preferred incremental owner cash: CAD0. Current authorized spend: CAD0. Absolute project ceiling: CAD100, not a target.** The ceiling includes tax, FX cost, committed renewals, proposal credits, demonstrations and advertising through the first-sale/first-30-day experiment. Optional envelope for this record: **CAD0**, available only after separate itemized approval. No automatic replenishment, account creation or paid trial. Unknown required costs block execution instead of being entered as zero.

**Budget fit:** `incremental_preservation_only`. Existing equipment/software are reused; electricity, past development and sunk subscriptions are not asserted to be free. Owner recurring subscription allocation is CAD0. Customer production accounts/plans/usage are a separate disclosed preflight cost, never silently subsidized from the owner's budget or described as universally free. If safe completion requires an unaffordable owner commitment, simplify or keep the work deferred.

No customer acquisition, publication, payment or account access has occurred in this revision. A marketing plan cannot ensure sales; exact-offer success probability and paid validation remain unestablished. Project execution must also respect the portfolio-wide **CAD0 current authorization**, so starting many projects cannot multiply spending rights. [Budget rules](../../../../../research/BUDGET_POLICY.md) · [Current research](../../../../../research/SOURCES_V2.md).

## V2 revision note
2026-11-05: added the applicable marketing, effort and cash gates; preserved recorded completed work and commercial validation. Frontmatter next_action is the current proposed planning step. Older checkpoint instructions remain historical where superseded by this revision; do not repeat completed external actions.

## V2 commercialization of the existing reporting prototype
Reuse the existing tested synthetic report generator and mapping/preflight tools; do not commission a new dashboard. **Candidate buyer:** an agency or operations owner already producing the same non-regulated report from a structured export. **Draft outcome:** “Turn one agreed CSV export into a checked, repeatable operational report with a visible rejection list.” Keep the original supported field model; unsupported source semantics are a reason to decline, not improvise accounting.

**Proof:** use the existing synthetic sample and generated HTML/CSV/JSON output; show source reconciliation, a bad-row case and the portable rerun instructions. **Discovery phrase:** `CSV weekly operational report mapping automation`. Review explicit eligible requests or a genuine opt-in referral; do not send broad cold email. No free customized client report before a funded scope.

Cap a new proof/offer test at two unpaid hours because the prototype already exists. Customer-funded delivery must cover mapping, validation, review, communication and support; past prototype work is not evidence of paid demand. AWA-122 is an adjacent Docs/PDF assembly option, not a replacement or duplicate of this reporting business. Compare them based on the requested output rather than inventing a second customer.

Current owner cash and ads: CAD0. Any production tool cost belongs in a disclosed customer plan. Paid ads and recurring service claims wait for actual profitable sales and repeat use.
