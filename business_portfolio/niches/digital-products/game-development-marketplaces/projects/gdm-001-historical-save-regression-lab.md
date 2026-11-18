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
  "work_state": "active",
  "commercial_validation": "unvalidated",
  "evidence_basis": "public_official_and_competitor_research_no_verified_customer_sales",
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
  "next_action": "Implement strict manifest parsing and a generic asynchronous adapter with safe isolation, then compare it against the native Unity baseline.",
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
    "budget_window": "Cumulative incremental owner cash commitments; review before any purchase; never auto-reset. Existing authorization is CAD0.",
    "includes": [
      "tax",
      "currency_conversion_cost",
      "noncancelable_commitments",
      "advertising",
      "hosting",
      "tooling",
      "customer_support",
      "payment_processing",
      "potential_refund_reserves"
    ],
    "unknown_cost_action": "Do not treat unknown as zero; research and prepare a no-spend alternative, and stop external commitment until authorized.",
    "production_runtime": "Offline/local-first. No new paid hosted dependency is authorized.",
    "budget_fit": "CAD0 proposed launch build; external marketplace requirements and final costs remain subject to verification",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  },
  "marketing_execution_authorized": false,
  "production_budget_verified": false,
  "success_probability": "not_established",
  "marketing_lane": "marketplace_demo_and_organic_discovery_no_paid_ads",
  "launch_gate": "synthetic_fixture_free_tool_comparison_qa_then_owner_approved_listing",
  "pre_sale_work_cap_hours": 6,
  "ad_test_cap_cad": 0,
  "offer_price_cad_hypothesis": 69,
  "historical_price_usd_hypothesis": "Prior owner workbook hypothesized USD59–129; separate CAD69 experiment here, not an approved sale price.",
  "platforms_supported": [],
  "platforms_proposed": [
    "Unity",
    "Godot",
    "Unreal",
    "GameMaker",
    "RPG Maker",
    "Construct",
    "GDevelop",
    "Roblox DataStore"
  ],
  "public_results": [
    {
      "label": "Optional Unity interview guide (not a project gate)",
      "path": "results/GDM-001/unity-discovery-interview-guide.md"
    },
    {
      "label": "Competitor comparison template",
      "path": "results/GDM-001/competitor-comparison-template.md"
    },
    {
      "label": "Unity technical feasibility check",
      "path": "results/GDM-001/unity-technical-feasibility-2026-11-15.md"
    },
    {
      "label": "Unity environment readiness check",
      "path": "results/GDM-001/unity-environment-readiness-2026-11-15.md"
    },
    {
      "label": "Unity native baseline",
      "path": "results/GDM-001/unity-baseline-2026-11-17.md"
    }
  ]
}
---
# Historical Save Regression Lab — Complete Business and Implementation Plan

## 1. Executive decision and current status

**Decision: retain as a high-priority, unvalidated technical product candidate.** Make a **Unity editor-only package** that runs historical save fixtures through the customer's *real* load/migration entry point and validates meaningful restored game state. The initial sellable outcome is a reproducible failing assertion such as "the file loaded successfully, but the upgraded player lost a unique item." Its marketable differentiator must be *speed of integration and meaningful diagnostics*, not generic serialization or a new save system.

- **Exact buyer:** independent Unity studios maintaining released save-compatible games; secondarily teams developing long-lived simulation/RPG projects and maintainers of save middleware.
- **Buyer trigger:** an update changes save schema or runtime restoration; regression testing of old versions is difficult and expensive to maintain.
- **Chosen earliest channel:** Unity Asset Store *if accepted*; direct checkout is a fallback, not proof of audience. No seller account is assumed.
- **First contribution target:** a few CAD69-equivalent paid units per month could contribute to the portfolio's CAD150/month milestone; see the transparent scenario math in §8.
- **Scope:** Unity-only initial edition; other engines are independently researched extensions. This **does not** authorize full multi-engine implementation or a universal save parser.
- **Reality check:** no paid customers, interviews, beta trials, engine tests, files from customers, or release have been verified. The project is `planned` and `unvalidated`, not "ready to sell".
- **Why continue rather than cancel today?** A concrete technical test can verify the differentiator locally without human interviews, paid tooling or proprietary games. **Kill** the product if a small set of well-written Unity Test Framework tests offers equivalent results with less setup.

## 2. Repository baseline, duplication and reuse

Verified public repository: `Hi62384/Proj`, `main` at `6f2a420e9a1d7d5b44ec1759918e737059a6772e`, reviewed 2026-11-15. Canonical location is `business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-001-historical-save-regression-lab.md`, niche ID `N-gdm-20261115`, project ID `GDM-001`. The other active game-development records are `GDM-002` (passenger transport) and `GDM-003` (packaging/dependencies): different jobs-to-be-done, not duplicates. Older portfolios/research are preserved in `business_portfolio/archive/2026-11-15-legacy/`, `archive/2026-11-15-taxonomy-view-v1/` and `opportunity_library/`. This file revises GDM-001; **do not create a new project ID**, overwrite an archive or reset historical work.

**Reuse:** the repository's project browser, test/checkpoint system, source register, marketing research, and prior `results/GDM-001/` research files (if present). The historical Unity discovery interview guide is retained for continuity but **is not** a development dependency. No existing production save-test library for this project was observed in the published repository records; Codex must inspect the **current local checkout** before creating a source tree.

**Distinctness screening (not new business ideas):** generic save engines and migration pipelines are adjacent substitutes; Unreal already has a dedicated historical-save test product. The GDM-001 opportunity only survives if a Unity-specific integration/reporting gap is real. Do not repackage a free tester or create a separate "save migrator" as another active project.

## 3. Opportunity discovery and selection record

The owner's earlier marketplace workbook evaluated **33 directions** and retained six candidates. This revision re-evaluates *this existing selected family*, not a fresh 15–30-idea opportunity generation run. Nearby options and decisions:

| Adjacent direction | Decision | Specific reason |
|---|---|---|
| Sell a general JSON/binary save framework | Reject | Numerous free and paid options; easy to build a basic version. |
| Sell schema migration steps only | Reject | Unity Save Migrator already provides field migrations, validation, backup/recovery and tests. |
| Port a historical-save tester straight to Unreal | Defer | Save Compatibility Lab already offers fixtures, adapters, diffs and commandlet testing in Unreal. |
| Provide generic NUnit assertion helpers | Reject | Unity's Test Framework already supports automated tests; insufficient purchase advantage. |
| **Unity actual-gameplay restoration regression workbench** | Conditional choice | It could shorten old-save test setup and isolate silent logical failures; an independent, runnable local comparison must prove value. |

**Qualitative screen, not success probability:** problem severity high for released games, customer base narrow, technical difficulty moderate-high, competitor/DIY pressure high, organic discovery possible but unproven. Red-team conclusion: **product value is technically falsifiable; commercial demand remains unproven**. No mandatory interviews or pilot programs.

## 4. Buyer, buying trigger, and reasons to decline

Buyer A maintains an RPG with old player characters/inventory; Buyer B maintains a survival or simulation title with evolving world-state flags. At release time a save can parse while gameplay state is wrong. If the team currently must hand-write fixtures, start games, wait for asynchronous initialization, inspect nested state and compare results, a structured tool may reduce repeated work. Customer pays only if integration takes less effort than maintaining their own tests and the output tells them *where* corruption occurred.

Nonbuyers: greenfield projects with no existing saves; studios already using robust gameplay-level migration tests; games with inaccessible encrypted formats and no adapter hooks; teams requiring a fully automatic parser or arbitrary game-state discovery. The product must not market itself as detecting every compatibility bug or fixing corrupted saves.

**Customer-visible promise (conditional):** "Run your old saves through today's game code, verify actual restored gameplay state, and see exactly what an update broke—without replacing your save system." The phrase may be used in a listing **only after** a real fixture demonstrates it.

## 5. Evidence, competition, AI substitute and commercial uncertainty

| Claim or baseline | Public evidence checked 2026-11-15 | What it does **not** prove |
|---|---|---|
| Unity has a viable editor test runner and headless CLI | [Unity 6000.3 Test Framework command line](https://docs.unity.com/en-us/engine/6000.3/manual/programming-environment/test-framework-introduction/running-tests/run-tests-from-command-line) | This new product would outperform NUnit. |
| Migration alternatives can be inexpensive and feature-rich | [Save Migrator](https://assetstore.unity.com/packages/tools/utilities/save-migrator-version-safe-save-data-migration-411584) currently advertises sequential field migration, inspector and tests; observed sale price USD13.99 (may change) | How many copies it sells or a gap large enough for our asking price. |
| A close historical-save tester already exists in Unreal | [Save Compatibility Lab](https://www.unrealtools.com/save-compatibility-lab/) details fixtures, explicit state assertions, commandlet, isolated copies and reports | That Unreal ports have low competition. |
| Unity submission is reviewed and requires real compatibility | [Unity Asset Store guidelines](https://assetstore.unity.com/publishing/submission-guidelines), last updated Oct 23, 2026 | That our package will be accepted. |
| Publisher revenue share | [Unity publisher FAQ](https://marketplace.unity.com/publishing/publish-and-sell-assets) states 70% publisher share | Actual net payout after taxes, refunds, FX or local obligations. |

**Free/AI challenge:** create the same old-save fixture in Unity Test Framework and write a custom `Assert.AreEqual` test with an AI assistant. Measure *wall-clock setup, lines of buyer-specific glue, repeatability, readable failure paths, untouched save hashes and ability to run in CI*. Passing the same test isn't enough: the paid tool must make ongoing tests materially easier. A code-generation assistant may recreate much of the tool; the defensible purchase reasons are *curated adapters, testing fixtures, version maintenance, reliable isolation, and troubleshooting*—all still to be demonstrated.

**Counterevidence:** migration products are inexpensive, the closest analogous Unreal product already exists, and only studios with older saves need this. Do not imply high sales from this market.

## 6. Offer, scope and cross-platform strategy

### Minimum useful paid release (one Unity edition)

1. Unity Editor window: suites, fixture validation, expected-state editor, Run Selected/Run All, navigation from result to failing property, export report; clean empty/error states.
2. Load adapter that invokes a buyer-supplied **real gameplay save loader** (not a test-only replacement), signals asynchronous completion, exposes explicit observables, and uses a disposable sandbox.
3. Strict versioned fixture manifest; SHA-256 immutability; supported scalar/array/object assertions, numeric tolerance, selected ignored volatile paths, exact typed diffs and clear failure categories.
4. Deterministic CLI/batch testing through Unity Test Framework; JSON report, readable Markdown or HTML report, controlled exit/failure classification, reproduction command and redaction default.
5. At least one complete original sample game: three historical save versions, one intentional inventory regression, one quest-state regression, two passing fixtures and a documented install in a fresh Unity project.
6. Versioned package, docs, actual captured screenshots, changelog, licence notices, basic support instructions, rollback/uninstall and explicit limitations.

**Out of scope:** automatic game save format discovery, changing source files, universal encryption handling, cloud test servers, production DataStore writes, arbitrary world restoration, user analytics, console certification, network uploading, migration authoring, Unreal/Godot editions and automatic bug repair.

| Target | Candidate status and required separate proof | Candidate route |
|---|---|---|
| Unity | **First edition only.** Check Unity 6 LTS / 6000.3 (installed version must be pinned), asset pipeline and test runner. | Unity Asset Store if accepted; Payhip/itch.io alternative. |
| Godot | Later: `user://` sandbox, GDScript/C# hooks, native test comparison; don't assume Unity code is reusable. | Direct / itch.io; official Godot store free-only now. |
| Unreal | **Defer unless material competitive gap** over Save Compatibility Lab is established. | Fab, conditional. |
| GameMaker | Later: verify test hook/format/marketplace access; not promised. | Direct, conditional. |
| RPG Maker | Later: verify event/save migration and plugin rights; no automatic support. | Direct, conditional. |
| Construct / GDevelop | Later: separate runtime/browser persistence and test runner feasibility. | Eligible channel only after proof. |
| Roblox DataStore | A fundamentally different cloud/authorization model; no production-write default. | Creator Store only for eligible supported plugin. |

**Shared family assets:** fixture vocabulary, invariant semantics, result schema, redaction rules, demo scripts and test vectors; source implementations and engine APIs remain edition-specific. Don't build a universal multi-engine framework before one useful release.

## 7. Competitive differentiation proof and staged development decision

- **Technical comparison (no buyer meeting):** benchmark the *same* three old-save versions, two failure cases and one asynchronous load against (A) native Unity Test Framework + a reasonable AI-assisted test script and (B) the proposed adapter. Make a short screen recording of both processes.
- **Pass:** exact gameplay-state diff and stable CI result; original save bytes untouched; default redaction; setup time, change effort and failure localization convincingly better, or a specific tested capability impossible with the straightforward alternative. Use a written benchmark; do not invent a numerical advantage before measuring.
- **No-go:** the native/AI approach produces equally good reports with fewer moving parts, adapters need bespoke high-effort work for each game, or fixture isolation cannot be guaranteed. If no winning scope remains, mark project `deferred` rather than launch a clone.
- **Commercial gate:** after passing the proof, release preparation may proceed directly; public marketplace demand is tested after launch. No required interviews, surveys, or pilots.

## 8. Business model and CAD150/month portfolio economics

**Proposed single Unity editor-tool edition**, one-time licence under the chosen marketplace agreement; no subscription, hosting or recurring platform service. **Price experiment:** CAD69-equivalent display price (the actual Asset Store may require USD pricing and its own conversion). Historical owner research separately hypothesized USD59–129; neither is accepted customer pricing.

**Illustrative assumptions, NOT measured financial performance:** 30% store share, 5% gross-sales allowance for refunds/reversals, CAD0 owner hosting, CAD0 paid ads, no per-order delivery cost, no production QA subscription. Cash contribution per completed sale = `69 × (1 − 0.30 − 0.05) = CAD44.85`, before personal taxes, FX/tax adjustments and owner labor. The fee assumption is anchored by Unity's published 70% publisher share; refunds are a stress reserve, not an observed average.

| Scenario (monthly) | Hypothetical completed paid copies | Gross CAD | Estimated fees + reserve | Net contribution CAD | Share of CAD150 portfolio milestone |
|---|---:|---:|---:|---:|---:|
| Stress / no traction | 0 | 0.00 | 0.00 | 0.00 | 0% |
| Base hypothesis | 2 | 138.00 | 48.30 | 89.70 | 59.8% |
| Upside hypothesis | 6 | 414.00 | 144.90 | 269.10 | 179.4% |

To contribute **CAD150/month alone** at these assumptions requires `ceil(150 / 44.85) = 4` completed paid sales/month. One month with 4 sales is **not recurring income**. The zero-cash first-release model breaks even on cash after its first sale *if* all startup and monthly cash costs are genuinely zero; it does **not** recover creator time. If unforeseen CAD50 upfront tooling becomes necessary and separately authorized, cash break-even becomes `ceil(50/44.85)=2` sales, subject to the CAD100 cumulative ceiling.

**Sensitivity:** at a 10% refund allowance per sale, contribution becomes CAD41.40 and 4 sales are still needed; at 50% combined fee/refund cost, CAD34.50 and 5 sales are needed. If maintaining the product costs 2 owner hours per month with only two sales, the illustrative effective contribution is CAD44.85/hour *for maintenance alone*, which ignores initial development time and buyer support; it is not a wage or realized return. Development effort assumption 25–55 focused AI-assisted engineering/test hours + 2–6 owner review/setup hours, **not observed**. Actual time/ROI must be recorded from implementation.

**Owner budget:** CAD0 planned and authorized. CAD100 is only a ceiling; unknown seller payout costs, tax/FX and mandatory tools must be verified before any commitment. Do not start paid advertising until paid conversion economics justify it and the owner approves a controlled test.

## 9. Acquisition, distribution and launch positioning

**Primary channel:** Unity Asset Store, whose publisher FAQ says submission is free and publishers retain 70% (current policy must be rechecked). Users search for technical solutions; the first practical discovery artifact is an actual 30–60 second failure demonstration, not mass posts. **Secondary:** reuse the repository's existing Payhip store only if software delivery/licensing/refund rights are compatible and the owner authorizes account changes. Paid acquisition default CAD0. No unsanctioned community marketing, fake reviews or customer messages.

**Search terms to test:** `Unity old saves update regression`, `Unity save migration testing`, `Unity save compatibility CI`, `Unity save data tests`, `Unity inventory save loss`; these are positioning candidates, not verified search-volume numbers.

**Listing draft headline:** *Historical Save Regression Lab — Catch Silent Save-Update Bugs in Unity*.

**Listing teaser (publish only after QA):** *Replay old saves against your current game's real load logic and verify inventory, quests and progress—not just whether the file parses. See property-level diffs, reproduce failed fixtures and run tests in CI.*

**Feature copy:** fixture gallery; safe isolated testing; game-specific adapter API; typed expected/actual diffs; deterministic batch results; redacted report export; sample old-save regressions. **Honest limitations:** requires the game's own loader/state accessor; does not support arbitrary encrypted saves out of the box; no automatic save repair; supported Unity versions must match release evidence.

**Demo storyboard:** (1) game v1 has shield + 3 potions; (2) v3 loads v1 save with no parse error but drops shield; (3) workbench highlights `inventory.unique[shield]` expected true/actual false; (4) export failing CI report and fixture hash; (5) fix migration and rerun pass. Capture real editor footage only once built. Offer an original sample project and 2-minute integration guide. Publish factual FAQ and support page.

**Marketing sequence:** compile store copy while coding → produce real demo/results when tests pass → prepare thumbnails/screenshots and accurate supported-version panel → get owner approval → submit listing → track page visits and actual sales/reviews → revise demo/search terms if people view but do not buy. Measure qualified exposure before concluding demand is absent.

## 10. Technical architecture and module ownership

**Selected architecture:** editor-focused **C# Unity package** using pure C# comparison/schemas, Unity Editor workbench, and a minimal Test Framework runner. Avoid a separate executable, hosted API, native DLL and runtime plugin when possible. The customer's loader remains unmodified except for explicit adapter registration; no reflection-driven guessing or unsafe serialization tricks.

```text
Proposed (NOT YET CREATED) product tree under a new owned folder:
products/game-tools/historical-save-regression-lab/
  package.json
  Runtime/Contracts/{FixtureSchema,ResultSchema,IHistoricalLoadAdapter}.cs
  Runtime/Core/{TypedPath,SnapshotCanonicalizer,InvariantEvaluator,DiffEngine,FixtureHash}.cs
  Editor/{SuiteWindow,FixtureBrowser,ResultInspector,ReportExport}.cs
  Editor/Execution/{SandboxManager,SuiteOrchestrator,TimeoutPolicy}.cs
  Editor/TestRunner/{UnityFixtureTestBridge,CommandLineEntry}.cs
  Samples~/SaveRegressionExample/{Scenes,Scripts,Fixtures,Expected}
  Tests/Editor/{SchemaTests,DiffTests,SecurityTests}.cs
  Tests/PlayMode/{LegacySaveIntegrationTests,AsyncRestoreTests}.cs
  Documentation~/{Quickstart,AdapterGuide,SupportMatrix,Limitations,FAQ}.md
  Tools/{package_release.py,verify_package.py}
  LICENSE.txt, THIRD_PARTY_NOTICES.md, CHANGELOG.md
```

**Responsibilities:** `Contracts` owns versioned JSON model and `IHistoricalLoadAdapter` only; `Core` performs parsing and assertions without calling game objects; `SandboxManager` copies and hashes fixtures, tracks disposable directories and cleanup; `SuiteOrchestrator` executes fixtures serially for safety, handles explicit cancellation and timeouts; `Editor` presents summary and diff; `TestRunner` maps results to Unity tests and exits; `Samples~` demonstrates integration without shipping a framework. No module may mutate original baseline fixtures.

**Interfaces (design contracts, not compiled API):**

```csharp
public interface IHistoricalLoadAdapter
{
    string AdapterId { get; }
    Task<RestoreOutcome> RestoreAsync(string isolatedFixturePath, CancellationToken cancellation);
    Task<ObservedState> CaptureStateAsync(CancellationToken cancellation);
    Task ResetAsync(CancellationToken cancellation);
}
public sealed record RestoreOutcome(bool Success, string? Reason, string GameVersion);
public sealed record ObservedState(IReadOnlyDictionary<string, object?> Properties);
```

The exact Unity async/thread lifecycle must be adjusted to Unity's supported runtime and main-thread requirements. *Do not* assume Unity engine objects are safe from arbitrary `Task` threads. An adapter that exposes a `Coroutine`/event callback may need a Unity-main-thread wrapper. The runner **awaits a true completion signal**, rather than sleeps for an arbitrary number of frames.

## 11. Data contracts, deterministic algorithms and failure recovery

**Proposed fixture manifest (version 1):**

```json
{
  "schema_version": 1,
  "suite_id": "example-v1-to-v3",
  "fixtures": [{
    "fixture_id": "player-before-inventory-refactor",
    "source_game_version": "1.0.0",
    "target_game_version": "3.0.0",
    "file": "fixtures/player-v1.save",
    "sha256": "REPLACE_WITH_REAL_64_HEX_SHA256",
    "timeout_seconds": 30,
    "assertions": [
      {"path": "inventory.unique.shield_01", "type": "boolean", "equals": true},
      {"path": "quests.main.completed", "type": "boolean", "equals": false},
      {"path": "player.hp", "type": "number", "equals": 75, "tolerance": 0}
    ]
  }]
}
```

`sha256` is an *illustrative placeholder*, not a fabricated fixture fingerprint. Before executing, verify actual fixture hash, schema, and relative path beneath an allowlisted root. Reject absolute/traversal/symlink escapes. Sandbox path must be distinct and disposable; cleanup must respect an opt-in debug-retain mode. Nested property paths use a documented escaped-dot grammar; explicit strict type comparison prevents strings passing as numbers. Numeric tolerance is only applied to declared numeric paths; NaN/Infinity are invalid for deterministic manifests. Each result includes fixture and game versions, adapter identity, source hash, expected/observed values **redacted by default**, repro command, and one of `pass`, `regression`, `invalid_fixture`, `unsupported`, `timeout`, `adapter_error`.

**Core algorithm:**

```text
for fixture in suite.sorted_by_stable_id:
    validate_manifest_and_hash(fixture) -> reject invalid before touching game
    sandbox = fresh_private_copy(fixture)
    adapter.ResetAsync(); await adapter.RestoreAsync(sandbox.path, timeout)
    observed = await adapter.CaptureStateAsync()
    normalized = canonicalize(observed, approved_schema, deterministic_sorting)
    for assertion in fixture.assertions:
        if path_absent/type_mismatch: emit explicit regression-or-adapter-error
        else compare typed value with declared numeric tolerance
    emit structured result with stable diagnostic code and redacted diff
    assert original fixture SHA256 unchanged; cleanup sandbox
return report; fail CI when any regression/adapter_error/timeout/invalid_fixture exists
```

**Performance / privacy:** initial QA target ≤25 original synthetic fixtures and up to 1,000 explicit assertions per suite without unsupported memory growth; *measure* on a specified Windows machine/Unity version before claiming capacity. Avoid fixture-content logs by default, verify no network egress and no filesystem write outside sandbox and approved report folder. Do not use `Application.persistentDataPath` blindly—confirm the selected game's loader can be redirected to a disposable profile without modifying real user saves.

**Failure recovery:** crash mid-test leaves source untouched; incomplete report explicitly says aborted; next run makes a new sandbox. Unexpected external I/O requests are refused or reported unsupported. Multiple suite runs must not race on the same game profile; serialize until isolation is proven.

## 12. Dependency-ordered Codex work breakdown

All paths below are **proposed** and do not exist as completed deliverables. Estimates are uncertain focused engineering hours, not promises. `LOCAL` means normal permitted coding in an authorized checkout; `HUMAN` marks only genuinely unavoidable external approvals. Do not require interviews or paid pilots.

| ID | Effort estimate | Depends on | Action, deliverable and evidence | Acceptance/failure test |
|---|---:|---|---|---|
| S01 | 1–2 h | None | Pin installed Unity version, capture baseline `git status`, record competing Test Framework/Save Migrator APIs in `research/comparison.md` **inside new owned project**, with exact links. LOCAL | A working native Unity test baseline exists; state unsupported assumptions. |
| S02 | 2–4 h | S01 | Create owned sample Unity project with `v1`, `v2`, `v3` save/migration and three copies of original synthetic files; record actual hashes. LOCAL | Old save v1 loads into v3; one deliberate inventory regression remains silent at parse level. |
| S03 | 2–4 h | S02 | Define strict `FixtureSchema`, `ResultSchema`, parser/version checks and golden manifest fixtures. LOCAL | Reject duplicate ID, corrupted checksum, traversal and future-version fixture. |
| S04 | 3–5 h | S03 | Implement sandbox creation/hash/cleanup with read-only baseline handling. LOCAL | Five repeated runs preserve original SHA-256 and do not alter user profile. |
| S05 | 4–7 h | S02–S04 | Build main-thread-safe Unity adapter, callbacks, reset and timeout orchestration. LOCAL | Real async game load finishes without fixed sleeps; timeout/error are distinct. |
| S06 | 4–6 h | S03–S05 | Typed state capture, canonicalization and assertion engine. LOCAL | Loss of unique item, quest-flag change and wrong type fail with exact paths. |
| S07 | 2–4 h | S06 | Deterministic machine-readable report and CLI/Test Framework mapping. LOCAL | Same fixtures yield same normalized report (excluding explicitly volatile runtime details) and nonzero CI failure. |
| S08 | 3–5 h | S06–S07 | Unity Editor suite window, fixture list, inspectable diffs and error states. LOCAL | Keyboard-useful navigation, no crash on missing fixture, clear unknown statuses. |
| S09 | 3–5 h | S05–S08 | Two independent synthetic save loaders; install guide and original samples. LOCAL | Fresh Unity project can run examples following docs; record setup time. |
| S10 | 2–4 h | S09 | Compare with a well-written AI/NUnit fixture; document actual setup/maintenance delta, defects and value. LOCAL | If no meaningful advantage, mark candidate for pause; do not conceal negative result. |
| S11 | 3–5 h | S10 pass | QA across pinned Unity versions, packaging, licences, versioned docs, real captures and sample reports. LOCAL | Clean install, all regression tests, no unwanted data egress; store policy checklist. |
| S12 | 1–3 h | S11 | Draft assets, publisher metadata, FAQs, product description, help and pricing report. LOCAL | No unverified performance claims; all screenshots are authentic. |
| S13 | Variable | S12 + explicit authorization | Submit/approve listing through official seller flow and confirm public URL. HUMAN | Record actual approved publication and checkout observation; no inferred sales. |
| S14 | 0.5–2 h/review | S13 | Measure genuine impressions/purchases/refunds/support and decide improve/expand/pause. LOCAL read only if authorized | Update measured economics without counting scenarios as actual revenue. |

**Critical path:** S01→S02→S03/S04→S05→S06→S07→S09→S10→S11→S12→S13. S08 UI and marketing copy can be independently prepared by an assigned Codex chat after stable schemas exist; two chats must not edit the same canonical/project files concurrently. **Initial effort hypothesis:** ~30–60 focused agent engineering hours before official review; review time and support unknown. Make a short end-to-end paid-ready edition rather than building every engine variant.

## 13. Reproducible validation, tests, performance and support matrix

| Test | Input and expected result | Blocking severity |
|---|---|---|
| Good v1 save + correct v3 migration | After real game restoration, assertions on inventory/quests match; stable `pass`. | Required |
| Silent removed item | Deserialization success + `inventory.unique.shield_01=false`; `regression` at exact key. | Required |
| Partial quest migration | Wrong quest flag after load yields `regression`, not `invalid_fixture`. | Required |
| Invalid baseline hash | Fail before calling game loader; original remains unchanged. | Required |
| Duplicate fixture ID / wrong type | Parse error with line/fixture ID and no run. | Required |
| Async load never completes | Bounded `timeout`, sandbox cleanup, nonzero CLI. | Required |
| Adapter throws mid-load | `adapter_error`, no false pass; repro and redacted details. | Required |
| Restore twice after crash | Fresh isolated run, no corrupted baseline or stale state. | Required |
| Expected numeric tolerance | In-range floating difference passes; wrong type or out-of-range fails. | Required |
| Two loader designs | Both integrate using API without modifying core library. | Required |
| No permission to write profile | Clear unsupported/error status; never overwrite real save. | Required |
| Load 25 fixture suite | Report timing and memory with exact machine/version; no performance promise until measured. | Pre-release measurement |

**Runnable commands after files exist** (validate actual Unity executable and project paths; do not claim they have run):

```powershell
# Example invocation adapted from current Unity test-framework docs:
& "$Env:ProgramFiles\Unity\Hub\Editor\<PINNED_VERSION>\Editor\Unity.exe" -batchmode -nographics -projectPath "<SAMPLE_PROJECT>" -runTests -testPlatform PlayMode -testResults "<RESULTS_XML>" -quit
python products/game-tools/historical-save-regression-lab/Tools/verify_package.py
```

**Important:** Unity `-runTests` CLI verifies Unity tests; it does not automatically prove packaged player builds run correctly. The supported scope is editor-based save regression testing unless separate player-build tests are implemented and verified. Existing Unity API/version-specific behavior must be checked in the selected installed version.

## 14. Legal, marketplace eligibility, privacy, and financial authority

- Source code, sample game assets, screenshots and logos must be original, permissively licensed for redistribution, or used with documented written rights. Provide a THIRD_PARTY_NOTICES file if any dependency is redistributable. Audit all package licenses before release; do not bundle competitor code because it is public.
- Prefer a free local development environment and original synthetic fixtures. Do not ship private customer saves, proprietary production packages, or credentials. No analytics/telemetry by default; any opt-in diagnostics must be documented and deletable.
- The owner is in Canada. Confirm current seller eligibility, tax declarations, identity verification, payout currency, marketplace EULA, applicable Canadian tax obligations and merchant-of-record treatment before opening accounts or publishing; recorded platform statements are **not** approval of this seller account.
- A marketplace application is not a guaranteed listing. Draft locally, complete permitted QA, and then request the smallest actual owner approval/account verification required. The CAD100 ceiling is *not* a spending grant, and the proposed first release has no authorized cash outlay.
- Observe `AGENTS.md`, `business_portfolio/SCHEMA.md`, `PROJECT_TEMPLATE.md`, `business_portfolio/tools/build_browser.py` and `commercial_checks.py`. Maintain stable IDs, one writer per canonical file, guarded checkpoint updates, and the current historical archives.

## 15. Release-preparation and seller handoff

1. Build the exact edition pinned by the acceptance matrix. Generate a repeatable versioned package from a clean checkout with a source revision identifier, checksums and licenses.
2. Run the unit, integration, negative-case, performance, and installation tests on the declared support matrix. Capture tool output and real screenshots/videos, not generated stand-ins falsely described as the product.
3. Have a second *self-created* test project/user journey consume the package following only the public quickstart. Measure setup time, record failed steps and revise documentation.
4. Prepare a listing draft, concise feature and limitation statements, supported versions, demonstration script, meaningful search keywords, support route, update policy, cancellation/refund treatment and a release checklist.
5. Confirm product-class eligibility and country payout requirements on the intended marketplace. Owner completes required identity/account/publishing steps; do not silently attempt them through other accounts or unofficial APIs.
6. Archive hashes/manifest, signed-off QA evidence, actual uploaded package identifier and resulting public URL when genuinely observed. Do not mark `published` before a real listing is visible or before any required official review finishes.
7. Once released, inspect real traffic/sales/support, not hypothetical product-page rank. Reuse the release pipeline for a second edition only when the edition's expected benefit exceeds extra testing/support cost.

**Release-blocking acceptance:** the editor suite catches a deliberately silent gameplay regression, produces deterministic CI failure, preserves original fixture SHA-256, completes on a clean sample project and has documented unsupported cases. Real product screenshot and versioned docs must exist.

## 16. Post-release operations and customer support

- Publish a clear supported version matrix; request *reproducible, redacted* bug reports rather than sensitive project archives. Disclose current limitations; do not promise unlimited bespoke integrations at the base price.
- Triage: verify report/version → reproduce on minimal fixture → classify `supported bug`, `integration`, `unsupported use`, or `feature request` → provide workaround/patch → regression-test all prior fixtures → version release. Preserve previous packages for rollback.
- Maintenance cost is uncertain. Reserve an illustrative 0.5–2 hours/month per product plus 0.25–1 hour per meaningful support incident, **not** a measured commitment. If the real load materially exceeds this, revise economics, reduce supported configurations or pause expansion.
- Collect no product telemetry by default. Use actual accessible marketplace analytics and private support records without placing personal customer data in this public project record.

## 17. Performance measurement, portfolio decisions, and future products

Measure after actual publication: approved-listing status, qualified product-page visits when visible, gross purchases, verified net payments, fee statements, refund count, game versions and support labor. Record the date, currency, fee deductions, refunded transactions, hours of support and net contribution in the appropriate authorized private financial systems; report only non-sensitive aggregates publicly. A pageview is not a sale and a listing favorite is not a verified purchase.

Decision heuristics (not statistical proof): **continue** if actual positive net contribution and low support persist; **improve** when a specific demo, pricing, installation or discovery weakness can be addressed in a bounded update; **expand** only if there is proven traction plus a justified additional engine/channel; **pause** if exposure is tiny and costs are near-zero; **discontinue** if a small AI/NUnit test package is objectively simpler, native tools already solve the stated job, or support requires bespoke customer migration work for each sale. Do not infer a bad idea solely from zero sales without evidence that qualified customers saw it.

## 18. Adversarial review and kill conditions

The strongest reasons the business could fail are: a capable studio can write its own tests; the target market of old-save-heavy games is narrow; inexpensive competing migration software may satisfy most customers; engine adapters may be too intrusive. Before implementation, run a *free/AI DIY challenge*: reproduce the promised result using native engine tools, a public alternative and a short AI-assisted script. Record setup time, bug count and diagnostic quality for the same fixtures. If the new tool has no real advantage, cut the scope or stop—no rebranding a duplicate as a new project.

Other fail conditions: insufficient legally permitted distribution, accuracy/privacy defects, platform/SDK changes exceeding support economics, or the release depending on paid/forbidden services outside the authorized budget. No human interviews or paid pilots are mandatory. Technical QA and official permission gates remain mandatory.

## 19. First-session Codex handoff — ready for local work

**Open first:** repository root `AGENTS.md`, `business_portfolio/SCHEMA.md`, `PROJECT_TEMPLATE.md`, this exact canonical file `business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-001-historical-save-regression-lab.md`, `business_portfolio/research/SOURCE_REGISTER.json`, the selected niche's `NICHE.json`, and `docs/PORTFOLIO_MANAGER_WORKFLOW.md`. Inspect other active GDM IDs and the archives; do not assume their project folders are available for modification. Keep unrelated projects untouched.

**First session steps (local work, no commercial actions):**

1. `git status --short` and `git rev-parse HEAD`; reconcile uncommitted or newer work and guard the project record from conflicting writers.
2. Confirm `GDM-001` ID/niche/source IDs and source register; keep all existing evidence links and work history. Regenerate the browser only after canonical content changes.
3. Begin S01–S05 in the task table: pin installed Unity, create the three-version synthetic save example, write fixture schema and hash tests, build disposable sandbox, and implement the real async loader adapter. No interview is required. Stop and document the gap if no suitable Unity installation is available or if the native baseline already solves the full problem.
4. Run the small fixture(s) immediately, capture exact command, exit status and test outputs. Identify which results are observed rather than planned.
5. Record the task state and a specific next action in the canonical record, without claiming that a plan means implementation is done. If the root workspace differs from the verified remote repository, adapt carefully instead of clobbering local work.

**On future import/update**, the existing non-sensitive source IDs are registered. New URLs in §21 are *not* automatically registered: Codex must add evidence entries to `business_portfolio/research/SOURCE_REGISTER.json` only when used as cited source IDs, then update `source_ids`. Run `python business_portfolio/tools/build_browser.py`, `python business_portfolio/tools/build_browser.py --check`, `python -m unittest discover -s business_portfolio/tests -v`, and `python business_portfolio/tools/commercial_checks.py --portfolio business_portfolio` from repo root **where tools exist**. Check optional budget math separately. Do not invent tests that could not run.

## 20. Resume checkpoint and work log

- **Completed with evidence:** detailed existing GDM plan read from the remote repo; current official/public source and product-feature review; this more specific architecture, test plan, financial *hypotheses*, launch drafts and Codex work breakdown. No source code, verified engine integration, published listing, confirmed sale, private buyer interview or paid market validation was generated by the document revision.
- **Work state:** `active`; **commercial validation:** `unvalidated`; **actual revenue/profit:** `null`; **authorized spending:** CAD0; **external effects:** `not_started`.
- **Current task:** Unity 6000.6.9f1 passed 20 Edit Mode tests for synthetic fixtures, in-memory validation and a synchronous sample-only runner. Native NUnit reports the same shield loss. Strict manifest parsing, generic async adapter, robust isolation, version 6000.3 and product advantage remain unverified.
- **Remaining checklist:** [ ] locate/install Unity and complete S01 baseline; [ ] baseline comparison; [ ] working core; [ ] failing/negative fixtures; [ ] engine adapter; [ ] real package and installation; [ ] truthful demo; [ ] policy/rights check; [ ] publication authorization; [ ] real sales/maintenance review.
- **Owned deliverables:** this planning file and the already-existing public research artifacts listed in frontmatter; this revision did not create product code, Unity fixtures, or customer materials. Proposed future artifact paths do not yet exist.
- **Original source revision:** `6f2a420e9a1d7d5b44ec1759918e737059a6772e` (`main`, inspected 2026-11-15); original frontmatter IDs, priority, status, related links and existing research continuity preserved. The local repository record was inspected and reconciled during the 2026-11-15 merge; project IDs and paths were retained.
- **History:** original 2026-11-15 candidate selection and planning are preserved conceptually, including the original competing-product research and proposed platform editions. This revision **removes mandatory interviews and paid-pilot blockers** and replaces them with local comparative proofs and marketplace-as-validation, without falsely changing the commercial state.
- **Next concrete action:** Implement strict manifest parsing and a generic asynchronous adapter with safe isolation, then measure native tests against it. Verify Unity 6.3 separately before claiming support.

### Work log

- 2026-11-17 — Added in-memory fixture validation and a synchronous sample-only runner. Twenty Unity Edit Mode tests passed. The validator and runner have documented filesystem race/link limitations and are not suitable for real saves; strict parsing, generic asynchronous integration and measured comparative advantage remain open.

- 2026-11-17 — Added three separately hashed synthetic fixture files and tested five disposable copies per fixture. Nine Unity Edit Mode tests passed; the source hashes remained unchanged while copies were modified. This is a bounded test procedure, not a completed reusable sandbox or crash-safety proof.

- 2026-11-17 — Added a synthetic version-aware sample loader and native Edit Mode tests. Six tests passed on Unity 6000.6.9f1; a deliberately silent shield loss was caught by a standard assertion with the property name. Inline test strings are not yet isolated fixture files, and the comparison does not establish a paid-tool advantage.

- 2026-11-17 — Unity 6000.6.9f1 installed and licensed. A new sample project ran one Edit Mode JSON/assertion smoke test successfully with Unity Test Framework 1.8.0. No historical save migration or adapter is implemented; see `results/GDM-001/unity-baseline-2026-11-17.md`.

- 2026-11-15 — Local repository reconciliation before replacement: Pre-replacement local record was planned/unvalidated and contained no product implementation, Unity integration, customer fixture, outreach, or external action. The existing `results/GDM-001/` guide, competitor-comparison worksheet, and Unity technical-feasibility note are retained; the technical-feasibility note is added to `public_results` because the attached version did not list it. The attached specification supersedes the old discovery-first wording.

- 2026-11-15 — Previously recorded: project family identified from game-development marketplace research; candidate engine list and launch risks captured, without product implementation or sales.
- 2026-11-15 — Current revision: expanded the execution-ready specification and removed research-interview/paid-pilot gates. This file is an updated planning artifact, not proof of completed tasks.
- 2026-11-15 — Environment readiness check: Unity was not found on `PATH` or in the listed standard install locations. .NET SDKs and Python are available, but they cannot substitute for the Unity-native baseline required by S01. No prototype was created; the project is marked blocked pending a suitable Unity Editor. Details: `results/GDM-001/unity-environment-readiness-2026-11-15.md`.
- 2026-11-15 — Downloaded the official Windows Unity Hub installer to the owner's Downloads folder. Authenticode signature valid (Unity Technologies SF); 193,133,232 bytes; SHA-256 `2bd8b7086c0bc986f033a31b55bc5d1f5452d10cab66b5f41c98ab5d84cabfa2`. Unity Hub and Editor are not installed; official setup requires the owner's Unity account sign-in. GDM-001 remains blocked at S01 until a suitable Editor and native test baseline are available.

## 21. Dated source and registration handoff

The `source_ids` in the strict JSON frontmatter remain restricted to IDs already in the repository's `SOURCE_REGISTER.json` (verified from GitHub). All additional public URLs used below are **in-file evidence** until Codex registers them. Each source should be rechecked at the time of listing or toolchain/version selection.

| Source / proposed new ID if registered later | Fact supported; research limit | Date checked |
|---|---|---|
| `GDM-WB-2026` (registered) — owner research workbook attachment | Prior research shortlisted this concept; no verified sales. | 2026-11-15 |
| `GDM-UNITY-RULES` (registered) — https://assetstore.unity.com/publishing/submission-guidelines | Unity Asset Store submission limitations; acceptance remains conditional. | 2026-11-15 |
| `GDM-TEST-CLI-2026` — https://docs.unity.com/en-us/engine/6000.3/manual/programming-environment/test-framework-introduction/running-tests/run-tests-from-command-line | Unity Test Framework supports command-line test runs; does not prove a paid improvement. | 2026-11-15 |
| `GDM-SAVE-MIGRATOR-2026` — https://assetstore.unity.com/packages/tools/utilities/save-migrator-version-safe-save-data-migration-411584 | Competing migration product's features and observed listed price; not observed sales. | 2026-11-15 |
| `GDM-UNREAL-SAVE-LAB-2026` — https://www.unrealtools.com/save-compatibility-lab/ | Unreal has a very close historical-save regression workbench; strong reason not to clone it. | 2026-11-15 |
| `GDM-UNITY-PUBLISH-2026` — https://marketplace.unity.com/publishing/publish-and-sell-assets | Publisher FAQ advertises no publication fee and a 70% publisher revenue share; actual payouts vary. | 2026-11-15 |
| `GDM-GODOT-STORE` (registered) — https://docs.godotengine.org/en/stable/community/asset_store/faq.html | Official Godot paid assets unavailable at this check; later port needs direct paid route. | 2026-11-15 |

**Evidence limits:** competitors' existence/prices/features are not proven sales; official revenue shares are gross-before-other-cost rules; market size, traffic, conversion and support time have **not** been measured for this offer. The historical owner workbook is research context, not a public redistributable asset. No source has been used as evidence of this project's own paid transactions.


### 2026-11-17 async adapter checkpoint

An experimental boolean-state async adapter contract and tests for completion ordering and cancellation were added. Unity 6000.6.9f1 did not run the tests because its Package Manager local IPC server failed to connect; no new passing test is claimed. The spike has no timeout enforcement, safe sandbox, strict manifest parser, real game integration or product comparison. Next: restore Package Manager connectivity and run the tests before extending it.


### 2026-11-17 Unity async verification

Unity Package Manager connected when the Editor was run outside the restricted sandbox; no system configuration was changed. Unity 6000.6.9f1 passed 24 Edit Mode tests after correcting the cancellation test and adding restore-error and missing-property cases. The async contract remains a synthetic boolean-only spike, without strict manifest parsing, timeout, safe sandbox, real loader integration, or measured native comparison. See the Unity baseline result for evidence and limitations. Next: implement and test a strict manifest parser before integrating it with a safely isolated runner.
