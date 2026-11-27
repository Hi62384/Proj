# Project template — four-phase planning record

Use Portfolio Manager's **New project** on the selected niche to create a valid unique record. It starts as **Empty project** in Phase 1 and already has its stable ID, niche identity, required metadata and sibling `work/`. Send Phase 1a and then Phase 1b in the same ChatGPT chat; paste only the final complete verified record. Do not replace the generated identity with the illustrative placeholders below.

Current records live at `business_portfolio/niches/<niche>/<stable-id>-<slug>/project.md` with all project-owned artifacts in `work/`. The project appears directly under its niche in the Manager. There is no intermediary `projects/` folder.

The following complete record illustrates the format; it is not an already researched product and must not be imported unchanged. Keep every actual record's protected existing field, financial evidence, permissions and work history when adapting it. Empty `source_ids` is valid with `workflow_version: 3`; put new dated research URLs in the body without inventing source-register IDs.

````markdown
---
{
  "schema_version": 1,
  "workflow_version": 3,
  "id": "EXAMPLE-001",
  "title": "Empty project",
  "project_phase": "working_phase_1",
  "draft": true,
  "niche_id": "N-existing-id",
  "niche_path": "existing-niche/child",
  "record_type": "empty_project",
  "origin": "owner_created",
  "priority": "P2",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "No product or market research has been performed yet.",
  "source_ids": [],
  "parent_project": null,
  "related_projects": [],
  "next_action": "Run Phase 1a, then Phase 1b, then paste the final verified record.",
  "last_reviewed": "2026-11-21",
  "execution_authorized": false,
  "privacy": "public_planning_only",
  "research_verification": {
    "phase_1": "unreviewed",
    "phase_2": "unreviewed",
    "phase_3": "unreviewed"
  },
  "delivery_window_days": {
    "minimum": 2,
    "maximum": 21
  }
}
---
# Empty project

## Product brief and shared limits

Describe the buyer/audience, problem or creative promise, proposed outcome and reason to pay. This empty record claims no research, implementation, release or marketing has been completed.

Scope the entire four-phase project for 2 days to 3 weeks. Keep a realistic shared schedule and explicit accepted, conditional, deferred and rejected scope. Do not restart the time budget at each phase or claim completion to meet a deadline. Record actual allowed spending separately from the planning ceiling; this record does not grant external permissions.

## Phase 1 — Research

### Stage 1 — Product research

- [ ] Research buyer context, need, alternatives, demand evidence and uncertainty.
- [ ] Compare complete free/native/open-source/AI alternatives and capable paid substitutes, with dated direct sources and sustainable price assumptions.
- [ ] Assess rights, technical feasibility, owner effort, costs, acquisition feasibility and the total project scope.
- [ ] Specify product features/behavior, user flows, inputs/outputs, architecture or creative production structure, integration, assets, failure behavior and exclusions in detail.
- [ ] Define acceptance criteria, representative tests, deliverables/documentation and the smallest decisive early proof where needed.
- [ ] Verify the evidence. If it is already sound, say good to go without unnecessary revisions.

Evidence, decision, limits, build specification and source URLs: pending research.

### Stage 2 — Release research

- [ ] Research direct and adjacent compatibility targets separately from distribution destinations.
- [ ] Record eligibility, fees, rights, supported versions/formats, submission requirements, assets, review delays, updates/support and direct source URLs.
- [ ] Classify every promising route as accepted, conditional, deferred or rejected with reasons and effort estimates.
- [ ] Update the specification and Phase 2 with a genuinely compatible version and tests for every accepted target.
- [ ] Write a concrete Phase 3 release runbook for every accepted destination.
- [ ] Verify the plan; preserve a sound plan without forced changes.

Platform/variant matrix and release runbook: pending research.

### Stage 3 — Marketing research

- [ ] Research audience/intent, positioning, proof, offer, content, demos, SEO/discovery, communities, partnerships and other useful tactics.
- [ ] Verify rules, access, fees, effort, disclosures and source-backed channel suitability.
- [ ] Define the finite initial campaign, asset needs, conversion path, measurement and stop/change rules.
- [ ] Update earlier product/release plans where material evidence requires it.
- [ ] Add actionable Phase 4 tasks and verify the whole execution handoff.

Channel/tactic matrix, assets, sequence and measurement plan: pending research.

## Phase 1b verification

Independently recheck all three stages using fresh evidence. Pending until the separate review; include evidence, corrections, unresolved blockers and approval decisions.

## Phase 2 — Build and verify

- [ ] Reconcile the research and existing work; assign a descriptive product title while retaining its stable ID/path.
- [ ] Complete the decisive initial proof and all accepted compatible versions.
- [ ] Test normal/failure/first-use cases and package the product with documentation and rights notices.
- [ ] Prepare the accepted release/marketing assets and record actual artifact paths and verification.
- [ ] At every checkpoint record Phase 2 completion estimate: N% (best guess), observed results, completed/remaining work, important data/URLs and the next action.
- [ ] Codex advances to Phase 3 only when the scoped build and verification are actually complete.

## Phase 3 — Release execution

- [ ] Recheck current platform requirements and existing external state.
- [ ] Prepare, submit and release each accepted required destination within actual permissions.
- [ ] Verify public customer access, listing/version/package and practical delivery evidence.
- [ ] Save all upload, status, sale/download, edit/admin and support links plus useful IDs and facts.
- [ ] At every checkpoint record Phase 3 completion estimate: N% (best guess) and actual completed/remaining work.
- [ ] Codex advances to Phase 4 after all accepted required releases are complete; pending review is a blocker, not a live release.

## Phase 4 — Marketing execution

- [ ] Complete and adapt the truthful assets for each accepted initial marketing tactic.
- [ ] Execute authorized marketing and inspect the actual public result or applied change.
- [ ] Record placements, public/edit URLs, useful IDs, actual observable outcomes and remaining work.
- [ ] Run the finite initial review and correct material funnel/presentation failures without waiting indefinitely for first sales.
- [ ] At every checkpoint record Phase 4 completion estimate: N% (best guess) and actual evidence.
- [ ] Codex verifies real release/access and public marketing links, writes a factual description and creates the Complete receipt.

## Important data and URLs

Record useful artifact paths, versions/hashes, platform/project/submission IDs, commands, configuration, costs/results and source/docs/build/preview/live/upload/sale/download/edit/admin/marketing/analytics/support URLs as they become known. Include purpose, observed status, version and checked date. Planned destinations are not live evidence. Preserve retired links. Never store passwords, tokens, signed session links, customer data or payment records here.

No project URLs or operational results have been recorded yet.

## Current progress and next action

Completed: this empty planning record exists. Remaining: all research and execution. Next: copy a Phase 1 prompt. Record blockers and external-effect status honestly; never replay an uncertain upload or message without checking its actual state.

## Decisions and work log

Append dated observations, material changes and reasons, verification evidence, unresolved uncertainty and the next action. Preserve prior decisions when superseded and retain actual completed work.
````

After substantive research, use a descriptive title, draft false and record_type product_candidate. Preserve identity, current phase and protected fields. Phase 1a produces an internally verified draft; do not paste it yet. Phase 1b independently rechecks all three stages and supplies the complete record, the exact project_update_base_sha256 and project_update_phase_1b = "verified" only when all three checks are approved and the verdict is GO. A valid verified paste automatically advances to Phase 2; drafts remain in Phase 1. Codex advances 2→3→4→Complete after actual verified completion.

A research recheck can return **“Good to go — no substantive changes needed.”** but must still include the complete final record to paste. Minor cosmetic suggestions are not a gate. Store completed/remaining work and best-guess percentages honestly; a phase or completion receipt never establishes paid demand.
