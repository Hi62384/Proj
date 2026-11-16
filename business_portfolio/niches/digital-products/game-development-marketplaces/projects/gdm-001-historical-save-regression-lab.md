---
{
  "schema_version": 1,
  "id": "GDM-001",
  "title": "Historical Save Regression Lab",
  "niche_id": "N-gdm-20261115",
  "niche_path": "digital-products/game-development-marketplaces",
  "record_type": "product_family",
  "origin": "current_package",
  "priority": "P1",
  "planning_lane": "next_to_validate_focus",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "owner_research_and_adjacent_competitors_only",
  "source_ids": [
    "GDM-WB-2026",
    "GDM-UNITY-RULES",
    "GDM-FAB",
    "GDM-ROBLOX-STORE",
    "GDM-GODOT-STORE"
  ],
  "parent_project": null,
  "related_projects": [
    "GDM-002",
    "GDM-003"
  ],
  "legacy_ids": [],
  "public_results": [
    {"label": "Optional Unity interview guide (not a project gate)", "path": "results/GDM-001/unity-discovery-interview-guide.md"},
    {"label": "Competitor comparison template", "path": "results/GDM-001/competitor-comparison-template.md"},
    {"label": "Unity technical feasibility check", "path": "results/GDM-001/unity-technical-feasibility-2026-11-15.md"}
  ],
  "next_action": "Build a small local Unity save-regression prototype with synthetic old-save fixtures; prove that a silent gameplay-state regression fails while valid loads pass and source fixtures remain unchanged.",
  "last_reviewed": "2026-11-15",
  "offer_price_usd": null,
  "delivery_hours_assumption": null,
  "total_first_order_hours_assumption": null,
  "verified_paid_pilots": 0,
  "actual_revenue": null,
  "actual_profit": null,
  "owner": "owner_decision_pending",
  "execution_authorized": false,
  "privacy": "public_planning_only",
  "commercial_revision": 2,
  "owner_budget": {
    "currency": "CAD",
    "preferred_upfront": 0,
    "planned_upfront": 0,
    "authorized_spend": 0,
    "hard_ceiling": 100,
    "owner_recurring_monthly": 0,
    "budget_window": "Cumulative planning ceiling only; no spending approved and no automatic reset.",
    "includes": [
      "tax",
      "currency_conversion_cost",
      "noncancelable_commitments",
      "advertising",
      "hosting"
    ],
    "unknown_cost_action": "Pause and ask the owner before commitment.",
    "production_runtime": "Local synthetic-fixture prototype first; any hosted dependency or real customer-game integration needs separate approval.",
    "budget_fit": "local_prototype_no_spend",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  },
  "marketing_execution_authorized": false,
  "production_budget_verified": false,
  "success_probability": "not_established",
  "marketing_lane": "no_outreach_prototype_first",
  "launch_gate": "tested_prototype_and_separate_owner_launch_approval",
  "pre_sale_work_cap_hours": 2,
  "ad_test_cap_cad": 0,
  "offer_price_cad_hypothesis": null,
  "historical_price_usd_hypothesis": "59-129; workbook research hypothesis, not a current quote",
  "platforms_supported": [],
  "platforms_proposed": [
    "Unity",
    "Unreal",
    "Godot",
    "GameMaker",
    "RPG Maker",
    "Construct",
    "GDevelop",
    "Roblox DataStore"
  ]
}
---
# Historical Save Regression Lab

**Purpose:** Catch gameplay-state regressions in old saves even when loading and deserialization report success. This is one commercial family with independently evaluated engine editions; no edition has been built or approved for sale.

## Buyer, problem, buying trigger

The buyer is a studio maintaining a released game with real historical player saves. A release or migration may restore the wrong inventory, quest, character or world state without a parse error. The trigger is an upcoming update, an old-save defect, or a release gate requiring repeatable evidence. The buyer would pay only if setup and diagnosis beat its own Unity Test Framework/NUnit fixtures, custom scripts and existing save/migration tools. A generic serializer replacement would not solve this narrower problem.

## Evidence and limits

The owner-supplied workbook, reviewed 2026-11-15, flags adjacent Unity save products and a close Unreal historical-save testing product. These listings establish alternatives and a plausible engineering problem, **not paid demand for this family**. No buyer interview, independent game fixture, price acceptance, paid pilot or product integration has been verified. The workbook is private to the owner and is not a redistributable product asset.

### Competitors and substitutes by candidate edition (research check 2026-11-15)

| Candidate | Current substitute or competitor and dated source | Gap to validate; current decision |
| --- | --- | --- |
| Unity | Unity Test Framework/NUnit; [Save Migrator listing](https://assetstore.unity.com/packages/tools/utilities/save-migrator-version-safe-save-data-migration-411584), [SaveArchitect](https://singhaniialabs.itch.io/save-architect) (workbook review 2026-11-15). | Candidate first MVP. Prove real asynchronous load and gameplay invariants are simpler than custom tests; listing existence does not show demand. |
| Unreal | [Save Compatibility Lab](https://www.unrealtools.com/save-compatibility-lab/) (workbook review 2026-11-15). | Close competitor; any local port should first prove a distinct technical workflow with synthetic tests. Buyer feedback is optional evidence, not a build prerequisite. |
| Godot | Native test scripts and [Godot asset discovery](https://docs.godotengine.org/en/stable/community/asset_store/faq.html) (policy check 2026-11-15). | Format/API and competing addon scan outstanding; candidate only. |
| GameMaker | Native project-specific load tests; [GameMaker marketplace guidance](https://stage.gamemaker.io/en/help/articles/marketplace-setting-up-a-publisher-account) (workbook review 2026-11-15). | Buyer and distribution check outstanding; candidate only. |
| RPG Maker | Game-specific save migration scripts; [official product documentation](https://www.rpgmakerweb.com/products/rpg-maker-mz) (research pointer checked 2026-11-15). | Save format, rights, automation and competitor check outstanding; candidate only. |
| Construct / GDevelop | Native event/test workflows; [Construct assets](https://www.construct.net/en/game-assets), [GDevelop assets](https://wiki.gdevelop.io/gdevelop5/community/sell-asset-pack-store/) (research pointers 2026-11-15). | API/format and competitor check outstanding; candidate only. |
| Roblox DataStore | Native [DataStore APIs](https://create.roblox.com/docs/cloud-services/data-stores) (research pointer 2026-11-15). | A separate cloud-state model; no generic file-save promise. Candidate only after privacy/API proof. |

These are a dated screening matrix, not a completed market census. Exact prices, supported versions and current rules must be checked before any listing or development decision.

## Narrow MVP and editions

Unity is the first **local prototype target**, not a claim of buyer demand. Start with synthetic-but-realistic fixtures and a minimal sample adapter; use immutable old-save fixtures, await asynchronous reconstruction, assert explicit gameplay invariants, and emit a deterministic CI-readable diff. Prove one intentionally introduced regression that still deserializes. Access to any real buyer game or save is optional for the initial prototype and requires the owner's permission and the rights-holder's consent; no private save data leaves its owner's environment.

Shared family assets: test-vector specification, immutable fixture hashes, invariant schema, expected/actual report format, setup guide and comparison protocol. Each edition versions its engine adapter and package independently. Exclude universal format conversion, replacing the game's save system, cloud-fault simulation without a storage adapter, arbitrary encrypted saves, console certification, and production write access.

| Edition | Status | Feasibility / API and maintenance gate | Package and channel candidate | Required acceptance |
| --- | --- | --- | --- | --- |
| Unity | candidate | Confirm supported LTS versions, async callbacks, fixture injection and third-party save-package integration; medium-high support. | Unity package via Asset Store if accepted; itch.io/direct alternative. | Catch silent inventory/quest regression and avoid modifying baseline saves. |
| Godot | candidate | Confirm resource/user-data access and supported versions; competing tools unknown. | Engine addon, free library sample plus paid direct edition if allowed. | Exercise actual load path and invariant diff. |
| Unreal | candidate | Existing close competitor and plugin version burden. | Fab only if product-format and license review passes. | Demonstrate a material difference from Save Compatibility Lab. |
| GameMaker | candidate | Confirm test hooks and packaging. | Direct/itch.io; free marketplace discovery only if policy permits. | Headless or reproducible run proven. |
| RPG Maker | candidate | Confirm save structure and automation rights. | Direct/itch.io after license review. | Old-save fixture and event-state assertion. |
| Construct / GDevelop | candidate | Separate APIs and export checks. | Their own eligible asset routes or direct sales after review. | Representative load/state checks. |
| Roblox DataStore | candidate | Must use authorized DataStore access; cloud state and credentials remain owner controlled. | Creator Store only if an eligible plugin/model; direct alternative after review. | Safe read-only fixture approach, no account secrets or live writes. |

No prototype or verified edition exists. A theoretical port is not evidence that an engine supports the required test path.

## Acceptance and negative tests

- A deliberately changed migration restores a wrong item/quest flag while deserialization succeeds; the harness fails with an exact state diff and fixture/version label.
- A correct migration passes deterministically across repeated headless/CI runs; asynchronous load completion is awaited rather than inferred from a fixed sleep.
- Baseline old-save bytes and hashes remain identical; test writes go to disposable copies.
- Corrupt, missing, encrypted/unknown-format and unexpectedly newer saves receive explicit unsupported/failure states, not a misleading PASS.
- Compare setup steps, adapter size and diagnostic usefulness against a straightforward synthetic native-test baseline and documented alternatives. Real-team comparison is optional follow-up.

These are **planned tests**, not completed results.

## Rights, distribution, effort and support

Historical saves may contain personal player data, copyrighted game assets or account identifiers. Use owner-provided, consented fixtures, sanitize public examples, check dependency redistribution and never include customer saves in a public package. Unity Asset Store submission and package rights need review; no seller account, listing or upload is authorized. Fab, Roblox and Superhive are not default channels for this Unity-first test harness. Godot's official library is a free discovery route under current research; itch.io or direct stores may be paid candidates after policy review.

Effort is **unestimated** until one local integration spike. Likely costs are adapter setup, fixture curation, engine-version QA and support for custom loaders; record actual build and support effort. The workbook's US$59–129 is a price experiment only, not a CAD quote or forecast. First demonstrate one deserialization-success/state-failure case with synthetic data and compare it with native tests. No outreach or paid ads; optional external feedback can follow a working prototype with separate owner approval.

## Validation gate and kill rule

Build and test the bounded local prototype before seeking outside input. Use synthetic fixtures to measure whether the harness catches silent state regressions, preserves source saves, runs deterministically, and gives useful diagnostics; compare against native tests using reproducible local examples. Interviews and independent evaluations are optional follow-up evidence, not development gates. Real game/save access requires rights-holder consent and separate owner approval. Record demand as unknown until real market evidence exists; stop, narrow, or continue based on prototype results and available time, without treating technical success as proof of sales.

## Resume checkpoint

- Completed with evidence: taxonomy and project-family plan; owner workbook reviewed as research; optional interview guide, competitor comparison template, and Unity technical feasibility note in `results/GDM-001/`. No product implementation or external commercial action.
- Current task: start a local synthetic-fixture prototype; no interview or outside contact is required.
- Remaining checklist: [ ] bounded prototype; [ ] synthetic valid, silent-regression, corrupt and unsupported fixture tests; [ ] fixture immutability and repeatability checks; [ ] current competitor/version check before any commercial claim; [ ] optional owner-approved external evaluation only if it would answer an unresolved integration question.
- Blockers/decisions needed: owner approval before outreach, account access, use of customer data, spending, upload or publication.
- Next concrete action: implement a minimal Unity test adapter/demo around synthetic old-save fixtures and one deserialization-success/gameplay-state-failure case; document setup time, test outcome, and limitations.
- Owned deliverables and hashes/versions: planning record plus the three public research/feasibility notes listed above; no binaries or customer fixtures.
- External effect state: not_started. Do not infer a paid sale or replay any historical action.
- Private checkpoint reference: none for this new family.

## Decisions and work log

- 2026-11-15: Reviewed official Unity test-runner, asynchronous Play Mode test, command-line, and persistent-data-path documentation. Recorded a technical feasibility check in `results/GDM-001/unity-technical-feasibility-2026-11-15.md`; no project, save fixture, package, or external account was accessed.
- 2026-11-15: Created one family record, with Unity as the first validation target and all other engines as unverified editions. No build, listing, contact or payment occurred.
- 2026-11-15: Added a neutral interview guide and blank competitor/workflow comparison template. These are drafts for later owner-approved discovery; no studio was contacted and no current competitor, buyer, or pricing claim was newly verified.
- 2026-11-15: Updated the development sequence to prototype with synthetic fixtures before optional interviews, following the owner's direction to maximize low-cost product experiments. No outreach, real game access, spending, or implementation occurred in this update.

## Implementation-ready specification — research candidate, not an implemented product

**Finished-product contract.** A team supplies copies of historical saves, the exact game build or test harness that contains its real load/migration entry point, and explicit gameplay assertions. The tool runs each fixture in an isolated temporary game profile, waits for a completion signal from the game, captures normalized post-load state, compares it with versioned expectations, and emits a report plus a nonzero CI exit on any unexplained difference. It must never rewrite the source fixtures. It is valuable only if it catches semantic regressions and reduces setup/debugging effort versus the team's own test code.

**Actors and boundaries.** A local CLI orchestrator reads a manifest; an engine adapter invokes the game-owned load function and emits state; a small comparison core checks typed assertions; a reporter writes JSON and readable diff. Game saves and proprietary game code remain local to the buyer. The shared interface is a versioned JSON schema for `fixture_id`, source/target game versions, fixture SHA-256, timeout, expected invariant paths/types, observed state, engine/adapter version, and outcome (`pass`, `regression`, `invalid_fixture`, `unsupported`, `timeout`, `adapter_error`). Engine-specific adapters may be separate implementations. No universal save parser or upload service is part of the MVP.

**Unity-first adapter requirements.** Pin one Unity LTS version available for the local prototype and record it as a support assumption, not a market commitment. Provide a minimal test-scene or PlayMode adapter hook that exercises a synthetic sample loader, signals migration/load completion rather than sleeping, then reads inventory, quest, progression, character and world-state values through sample accessors. Run with disposable test data and prove its isolation. Support deterministic fixture ordering and CI/headless invocation where the installed Unity version and licensing permit it. A later adapter for a real game requires that game's owner's consent and an observable completion/state interface.

**Functional and failure requirements.** Verify missing, duplicate, stale-version, corrupt, encrypted and future-version fixtures; schema path/type mismatches; changed IDs, item quantities, quest flags, character stats and world switches; asynchronous timeout; partial migration; nondeterministic state; and loader exceptions. Preserve fixture byte hashes before/after each run. Separate an actual game regression from a malformed expected-state manifest. Report exact fixture/version/property path, expected value, actual value, engine log excerpt and reproduction command. Never print personal save content by default; opt-in redaction and local retention rules need review.

| Candidate edition | Current status | Engine-specific integration / evidence needed |
| --- | --- | --- |
| Unity | **Research candidate; first validation focus** | Real PlayMode/headless load hook, game-owned accessors, supported LTS, comparison against Test Framework and save-package tests. |
| Unreal | Research candidate | GameInstance/SaveGame migration hook and Automation Test execution; compare directly with the close historical-save competitor before any port. |
| Godot | Research candidate | `user://` fixture isolation, scene-ready signal and GDScript/C# version matrix; check existing addons. |
| GameMaker | Research candidate | Determine whether target games expose deterministic load and test hooks, and whether packaging is feasible. |
| RPG Maker | Research candidate | Determine save-data and scripting rights plus event-state assertions across supported versions. |
| Construct / GDevelop | Research candidate | Determine export/runtime test hook, save data access and repeatable headless execution separately for each engine. |
| Roblox DataStore | Research candidate, distinct design | Never run against production DataStores by default; prove authorized mock/test-store and state observation with no live customer writes. |

No edition is technically or commercially verified. An edition may be rejected if game-owned code cannot expose state safely, the marketplace disallows its package, or a native/free workflow is better.

### Sequenced milestones and deliverables

| ID | Dependency | Deliverable and completion evidence |
| --- | --- | --- |
| S1 synthetic prototype | Local work; no outreach | Versioned schema, synthetic old-save pair, expected state and source hashes; one intentionally silent inventory or quest regression. |
| S2 Unity spike | S1 | Minimal sample adapter exercises an asynchronous load path, records completion/state without fixed sleeps, and proves test-data isolation. Real game integration is optional and requires consent. |
| S3 comparison | S1–S2 | Dated matrix of Unity Test Framework, save migrators and public alternatives; compare behavior and local setup effort using reproducible examples. State where native tools already suffice. |
| S4 diagnostics and negative tests | S2 | Deterministic JSON/readable diff, CI exit codes, redaction, fixture immutability and repeatability across five runs; corrupt/unsupported fixtures fail clearly. |
| S5 optional external evaluation | Working prototype and separate owner approval | If useful, invite teams to evaluate with their consent and without sharing private data by default. Record feedback as anecdotal; it is not required to build and is not paid-demand proof. |
| S6 release preparation | Prototype results and owner launch approval | Version-pinned support matrix, license/dependency review, setup docs, sample project, accurate demo, marketplace-format check, price/cost assumptions and support boundary. No listing until approved. |

**Marketing and economics.** A truthful demo must show an old save loading successfully but restoring the wrong gameplay state, then the exact failing assertion and unchanged fixture hash. Offer a free synthetic fixture/example only if its rights are clear. Candidate distribution is Unity Asset Store if policy and package review pass, with itch.io/direct alternatives; later editions need independent channel checks. Measure integration/setup/support hours during local experiments; any customer-value or pricing claim remains unverified until separately supported. The workbook's US$59–129 remains an experiment, not an offer or revenue forecast. CAD0 spending is authorized.

**Development approach:** Start with a bounded local synthetic-data prototype and record both successful and failed experiments. Interviews are optional follow-up research, not a prerequisite to coding. Separate owner approval remains necessary for outreach, real customer/game data, spending, uploads and publication. All S1–S6 milestones are pending.
