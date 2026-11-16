---
{
  "schema_version": 1,
  "id": "GDM-003",
  "title": "Packaged Build / Native Dependency Verifier",
  "niche_id": "N-gdm-20261115",
  "niche_path": "digital-products/game-development-marketplaces",
  "record_type": "product_family",
  "origin": "current_package",
  "priority": "P3",
  "planning_lane": "queued",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "owner_research_and_technical_problem_only",
  "source_ids": [
    "GDM-WB-2026",
    "GDM-DEPENDENCIES",
    "GDM-UNITY-RULES",
    "GDM-FAB"
  ],
  "parent_project": null,
  "related_projects": [
    "GDM-001",
    "GDM-002"
  ],
  "legacy_ids": [],
  "next_action": "After higher-priority validation, compare a Windows x64 build-pipeline preflight against free Dependencies and engine build logs using a real consented game fixture.",
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
    "production_runtime": "Customer build pipeline only; engine and OS support costs are unknown.",
    "budget_fit": "discovery_only_no_spend",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  },
  "marketing_execution_authorized": false,
  "production_budget_verified": false,
  "success_probability": "not_established",
  "marketing_lane": "queued_discovery_draft_only",
  "launch_gate": "free_tool_comparison_and_buyer_evidence",
  "pre_sale_work_cap_hours": 2,
  "ad_test_cap_cad": 0,
  "offer_price_cad_hypothesis": null,
  "historical_price_usd_hypothesis": "The owner's workbook includes a price experiment; no price is approved.",
  "platforms_supported": [],
  "platforms_proposed": [
    "Windows x64 packaged builds: Unity",
    "Unreal",
    "Godot",
    "GameMaker",
    "Stride",
    "Defold"
  ]
}
---
# Packaged Build / Native Dependency Verifier

## Buyer and outcome

Candidate buyers are game teams shipping native plugins or engine exports. The proposed outcome is an actionable, reproducible failure report before packaging a release. The owner-supplied workbook identifies this problem; it does not establish buyer demand or technical success.

## Evidence and competition

The free [Dependencies project](https://github.com/lucasg/Dependencies) and platform/engine build logs are direct substitutes. A paid tool needs to demonstrate a material improvement in engine-aware packaging, CI integration or diagnosis. A static dependency scan cannot guarantee that delay-loaded libraries, platform-specific runtime paths, graphics drivers or dynamically constructed loads will work. No buyer interview, paid pilot, accepted marketplace listing or working prototype exists.

## Family and candidate editions

One shared specification would define dependency observations, expected package paths, supported architectures, a machine-readable report and reproducible fixtures. The first **candidate**, subject to evidence, is a Windows x64 pipeline preflight. Engine adapters are separate editions, never a claim that one binary works across all engines.

| Edition | Status and feasibility gate | Distribution candidate | Required proof |
| --- | --- | --- | --- |
| Unity | Candidate; verify native plugin import settings, editor/build versions and executable distribution rules. | Direct or Unity Asset Store only if its rules allow the format. | Detect a missing transitive DLL in a packaged Windows build, with a precise remedy. |
| Unreal | Candidate; verify UBT packaging, plugin variants and engine version support. | Fab after policy and license review. | Compare against UBT output on an independent plugin. |
| Godot | Candidate; verify GDExtension packaging and supported versions. | Direct/itch.io; free asset-library discovery if eligible. | Detect a misplaced or wrong-architecture extension dependency. |
| GameMaker / RPG Maker | Candidate; native extension scope and buyer demand unverified. | Direct only after rights and format review. | Reproduce a real missing-library failure. |
| Construct / GDevelop | Candidate; native export/plugin problem may be inapplicable. | No channel selected. | Establish a supported native dependency use case first. |
| Roblox | Likely inapplicable to a Windows DLL checker; no edition promised. | None. | Reframe around a distinct documented dependency problem or drop. |

## Planned narrow acceptance tests

- On a consented disposable Windows x64 game build, detect missing, wrong-architecture and conflicting-version native dependencies before release; compare output with Dependencies and the engine's logs.
- Produce a deterministic machine-readable CI failure and a human-readable report identifying the affected package and search path.
- Correctly mark dynamic loads, optional drivers and platform-specific paths as **unknown** rather than pass; never claim runtime compatibility from a static scan.
- Test a clean fixture, a missing transitive library, a false-positive risk and a corrupted binary. Confirm source fixtures and customer files are unchanged.

All tests are **planned**. No fixture or test result is claimed.

## Rights, support, channel and economics

Do not bundle proprietary game binaries, engine files or third-party tools without their licenses. The free Dependencies tool must remain a visible comparison. Unity marketplace executable restrictions, Fab product requirements and each engine version's maintenance burden need a current review before any submission. No seller account, upload, marketing, outreach or expenditure is authorized. Delivery/support time and price are unknown; the workbook's price discussion is only a hypothesis.

## Validation gate and kill rule

First find an independent team's reproducible packaging failure and measure whether the proposed report saves time versus free tools. Later paid-pilot interest from independent teams is required before a commercial edition decision. Stop if free Dependencies plus build logs solve the problem, the scanner cannot produce reliable actionable advice, marketplace rules reject the needed executable, or maintenance exceeds buyer value.

## Resume checkpoint

- Completed: research classification and candidate scope only. No product implementation or external effect.
- Remaining: [ ] consented real fixture; [ ] free-tool baseline; [ ] engine/package policy checks; [ ] bounded prototype; [ ] negative tests; [ ] independent buyer signal.
- Blockers: owner approval before outreach, account access, customer data, spending, upload or publication.
- Next concrete action: compare one Windows x64 native-plugin build failure with Dependencies and the engine log, with the team's permission, after higher-priority validation.
- Owned deliverables: this planning record only. No binary, listing or customer file exists.
- External effect state: not_started.

## Work log

- 2026-11-15: Recorded a conditional multi-engine family with a Windows x64 first candidate; no implementation or sales claim.

## Implementation-ready specification — queued research candidate

**Finished-product contract.** Given a packaged Windows x64 game build and an engine-specific export manifest, the verifier inventories shipped native modules, checks architecture and resolvable transitive imports, cross-checks engine plugin/export settings against the package, and reports actionable missing/misplaced/conflicting libraries before release. It emits deterministic JSON and a readable report with an `unknown` state for dynamic/runtime-only behavior. A bare DLL dependency tree is insufficient: the proposed advantage must be in packaged-build context and engine-aware diagnosis.

**Buyer and reason to purchase.** Candidate customers are small game/plugin teams shipping desktop builds with native extensions. The buying trigger is a failure that appears only in a packaged build or on a clean customer machine. The free Dependencies viewer, platform loader diagnostics and engine build logs are the baseline. A paid edition must measurably shorten root-cause time or catch package/configuration mismatches they leave unclear. No such advantage or willingness to pay has been proved yet.

**Architecture.** A read-only CLI has five bounded stages: (1) collect package files and engine export/plugin metadata; (2) parse supported PE imports and architecture without executing untrusted binaries; (3) resolve imports against explicit package and documented system search roots; (4) apply a versioned engine rule pack; (5) emit findings with file path, import chain, confidence, evidence and remedy. A stable `Finding` schema distinguishes `missing`, `wrong_architecture`, `misplaced`, `conflict`, `settings_mismatch`, `unknown_dynamic_load` and `unsupported_format`. Engine adapters supply metadata extraction and rule packs; the PE parser and report schema may be shared. Never load a suspicious game DLL to inspect it. Run in a disposable local analysis directory and do not upload customer builds.

**Failure boundaries.** Windows system DLL/API-set resolution, delay-loaded imports, `LoadLibrary` with computed paths, injected modules, GPU drivers, redistributable installers, anti-cheat, signed/protected binaries and platform-specific runtime behavior need explicit uncertainty. Never label a build “works on all machines” from a static scan. File hashes, tool/rule versions and searched paths make each finding reproducible. No remediation automatically alters a buyer build.

| Candidate pipeline | Status | Engine-specific evidence and distribution gate |
| --- | --- | --- |
| Unity Windows x64 | Research candidate; possible first spike | Match plugin importer platform/CPU settings and player output with package files; confirm exact Unity Asset Store executable restrictions or use lawful direct distribution. |
| Unreal Windows x64 | Research candidate | Inspect UBT/plugin descriptors, staging rules and packaged binaries; compare Fab eligibility and existing UBT diagnostics. |
| Godot Windows x64 | Research candidate | Inspect GDExtension descriptors, architecture paths and exported folder; check free addon/library alternatives. |
| GameMaker Windows x64 | Research candidate | Verify extension/export metadata is available and inspectable before promising an edition. |
| Stride Windows x64 | Research candidate | Validate native dependency packaging and buyer/tool ecosystem before investing in rules. |
| Defold Windows x64 | Research candidate | Validate native extension bundle/export format and marketplace feasibility. |
| Construct / GDevelop desktop exports | Research candidate only if a native dependency failure can be reproduced; may be rejected. | Separate extension/export mechanisms and buyer demand needed. |
| Roblox | Rejected for this Windows-native-build scope | No suitable Windows packaged-game pipeline; do not force a port for platform count. |

One pipeline is chosen from real buyer evidence; Unity is only the first **comparison** candidate. Shared parser/report code does not imply an engine adapter works elsewhere. Supported versions, seller channels, licensing and maintenance cost are unknown until tested.

### Sequenced milestones and deliverables

| ID | Dependency | Deliverable and completion evidence |
| --- | --- | --- |
| D1 problem and free-tool baseline | GDM-001/002 priority decision and owner-approved discovery | One consented, reproducible packaged-build failure; report what Dependencies and engine logs do and do not explain, plus buyer debugging time. Stop if free tools suffice. |
| D2 pipeline selection and rights | D1 | Select one Windows x64 engine/export pipeline, pin versions, review sample-binary rights and marketplace executable rules; reject unsupported channels. |
| D3 safe parser contract | D2 and development authorization | Synthetic PE fixture set, architecture/import graph schema, bounded file/CPU limits and explicit unknown states; parser never executes game code. |
| D4 engine rule pack | D3 | Detect missing transitive DLL, wrong CPU architecture, misplaced plugin and import-setting mismatch in four independently labelled package fixtures. |
| D5 diagnostics and CI | D4 | Repeatable JSON/readable output, stable exit codes, import chain and actionable remedy; prove no input files changed and no customer data left the machine. |
| D6 false-confidence evaluation | D5 | Delay-load, API-set/system library, runtime-only path, optional driver, corrupt binary and clean package cases; unknowns remain unknown and false positives are reviewed. |
| D7 buyer/commercial gate | D6 and consent | Three independent team trials, measured debugging/support time and two positive paid-pilot signals or documented alternative; decide price, support and whether a paid edition is viable. |
| D8 release preparation | D7 and owner launch approval | Versioned rule pack, license/dependency notices, supported engine matrix, sample failures/demo, store eligibility, documentation and maintenance policy. |

**Marketing, cost and kill rule.** Demonstrate a packaged build that fails on a clean machine, compare the free viewer and engine log, then show the extra configuration/package diagnosis with reproducible evidence. Publish setup guides or a free synthetic fixture only after rights and channel review. No ads, outreach or listing is authorized. Estimate parser maintenance, engine-version QA and support from real trial hours before pricing; CAD0 spending is authorized. Stop if the paid tool is merely a repackaged free dependency viewer, rule accuracy is poor, marketplace restrictions prevent lawful delivery, or buyers will not pay for the demonstrated diagnostic advantage. No D1–D8 milestone is complete.
