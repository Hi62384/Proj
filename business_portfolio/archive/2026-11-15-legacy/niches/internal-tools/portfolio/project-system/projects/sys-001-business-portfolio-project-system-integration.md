---
{
  "id": "SYS-001",
  "title": "Business Portfolio Project System integration",
  "niche_path": "internal-tools/portfolio/project-system",
  "record_type": "current_system_project",
  "origin": "current_package",
  "priority": "INTEGRATE",
  "work_state": "blocked",
  "commercial_validation": "not_applicable",
  "evidence_basis": "prepared_artifact",
  "source_ids": [
    "R01",
    "R03",
    "R07",
    "H01"
  ],
  "parent_project": null,
  "related_projects": [],
  "legacy_ids": [],
  "next_action": "Use Open_Project_Browser.cmd for the tested live view. Optional owner check: open PROJECT_BROWSER.html directly to confirm the static fallback; automated file:// access was blocked by browser policy. No commercial execution is authorized.",
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
  "niche_id": "N-ac49c3b7920a",
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
  "marketing_lane": "preserve_existing_work",
  "launch_gate": "preserve_or_reconcile",
  "pre_sale_work_cap_hours": 0,
  "ad_test_cap_cad": 0,
  "local_integration": {
    "imported_work_state": "package_ready",
    "evidence": "INTEGRATION_STATUS.md",
    "date": "2026-11-05",
    "browser_acceptance": "live_http_verified; direct_file_automation_blocked_by_policy",
    "index_and_merge_preserved": true,
    "implementation": "complete_local; manual_static_acceptance_pending",
    "python_tests_run": 68,
    "python_tests_passed": 67,
    "python_tests_skipped": 1
  }
}
---
# SYS-001 — Business Portfolio Project System integration

## Current position
**Work state:** `blocked` pending local browser acceptance; imported state was `package_ready`. **Commercial validation:** `not_applicable`. Evidence reconciled on 2026-11-05 against repository commit `7a99db00caea8d88a7abae943edeb3439b63d9c5` and the supplied handover.

This record preserves existing work; it does not restart it. Checkmarks below mean the cited repository/handover reports completion, except SYS-001 where they describe files prepared in this package. They are not fresh local Windows, customer-account, payment or native-application tests.

## Completed work
- [x] Researched and organized the new automation project records while retaining all 120 prior AWA identifiers.
- [x] Added evidence-bounded progress records for existing products, operations, tools and prototypes.
- [x] Prepared recursive folders, source register, read-only offline browser, rebuild/validation tooling, migration crosswalk and Codex instructions in this deliverable.

## Remaining work and blockers
- [x] User must stage/extract this new package into the Windows checkout as directed. Local integration performed November 5; detailed verification limits are in INTEGRATION_STATUS.md.
- [x] Codex must reconcile current local changes and any existing business_portfolio folder; remote inspection does not reveal them. Local integration performed November 5; detailed verification limits are in INTEGRATION_STATUS.md.
- [x] Codex must add minimal navigation/instructions and run relevant local tests without resetting legacy state. Local integration performed November 5; detailed verification limits are in INTEGRATION_STATUS.md.
- [ ] No live deployment, publication, payment, marketing or customer workflow execution is authorized.

**Unknown / not verified:** Local integration and Windows/browser acceptance remain pending. The package’s own checks are documented separately in QA_REPORT.md.

**Revenue, profit, paid orders and owner time:** unknown unless supported by a later private ledger and reconciled evidence. A public listing, free checkout, synthetic fixture or packaged file is not a paid customer. No completion percentage or fictional financial total is assigned.

## Resume checkpoint
**Next action:** Read CODEX_IMPLEMENTATION_PROMPT.md, inspect the current checkout and stage this package. Verify the included package QA record; then integrate additively.

**Do not repeat:** completed authoring, launch/setup, uploads, publication, test checkouts or infrastructure migrations merely because a new chat began. Read later local evidence first. Any uncertain consequential effect must be reconciled before a retry.

**Deliverable/source locations:**
- `business_portfolio/`
- `business_portfolio/CODEX_IMPLEMENTATION_PROMPT.md`

Locations are repository references or historically reported private roots, not proof a particular local file still exists. Current private release bytes, signatures, customer data and credentials are deliberately absent from this ZIP.

## Important decisions to preserve
- The files in this ZIP are prepared; the user’s repository/local checkout has not been modified.
- A browser is not an autonomous agent scheduler; candidates do not auto-run.

## Evidence and state reconciliation
- [R01](https://github.com/Hi62384/Proj/blob/7a99db00caea8d88a7abae943edeb3439b63d9c5/README.md) — Repository README. Access: `connector_full`; evidence type: `repository_report`.
- [R03](https://github.com/Hi62384/Proj/blob/7a99db00caea8d88a7abae943edeb3439b63d9c5/apps/codex_desktop_assistant/COMPUTER_BRIDGE.md) — Computer Bridge guide. Access: `connector_full`; evidence type: `repository_report`.
- [R07](https://github.com/Hi62384/Proj/blob/7a99db00caea8d88a7abae943edeb3439b63d9c5/AGENTS.md) — Repository agent instructions. Access: `connector_full`; evidence type: `repository_report`.
- [H01](attachment:Pasted text(20261105-164628).txt) — User handover — Resume Codex Relay Tasks. Access: `full_attachment`; evidence type: `user_handover`.

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

## V2 efficiency decision
Integrate this v2 package additively and by stable project ID. Preserve local progress, completed external actions and the previous research. The browser remains read-only with no network, account or scheduler features. The new budget fields are planning checks, not transaction enforcement or permission to spend. Run the included schema, economics and preservation tests; do not turn integration into another infrastructure overhaul.

Independent marketing/advertising allocation: CAD0. No claimed direct revenue, no new launch and no recurring owner subscription are attached to this internal or unassessed record.

## Local implementation checkpoint — November 5, 2026

Added working-tree navigation and checkpoint instructions without modifying the existing Git index or pending merge. The latest owner request replaces the old filter dashboard with a two-panel explorer and read-only localhost synchronization service. Commercial records, CAD0 authorization, published releases and legacy state remain preserved. Tests and live acceptance are in progress; direct file:// automation was denied by browser policy and was not bypassed.

## Live explorer verification — November 5, 2026

The live two-panel browser and standard-library service were implemented and tested locally. Synthetic tests exercised creation, editing, checklist completion, rename, move, new nested niches, deletion, last-valid-state recovery and declared public text results. Browser inspection verified one search, full instructions, existing guide opening, preserved selection/search/folders, protected releases and narrow-screen geometry. The Windows launcher was executed; repeated launch reused one listener. The 68-test run passed 67 tests with one real Windows symlink test skipped. Fixtures were removed. No customer-workflow, payment or native Excel validation is implied.

The system record stays blocked only for the original direct file:// acceptance: browser policy rejected that automated action. No bypass or screenshot was used. Local implementation and live synchronization are ready; the static HTML is generated and structurally checked, not claimed as directly browser-opened. See [the local report](../../../../../INTEGRATION_STATUS.md). Git index and pending merge remain unchanged.
