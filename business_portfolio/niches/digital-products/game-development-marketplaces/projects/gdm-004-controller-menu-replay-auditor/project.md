---
{
  "schema_version": 1,
  "id": "GDM-004",
  "title": "Controller Menu Replay Auditor — Runtime Gamepad UI Regression Evidence",
  "niche_id": "N-gdm-20261115",
  "niche_path": "digital-products/game-development-marketplaces",
  "record_type": "product_family",
  "origin": "revised_candidate",
  "priority": "DEFER",
  "work_state": "paused",
  "project_phase": "working_phase_2",
  "commercial_validation": "unvalidated",
  "evidence_basis": "official_and_source_verified_free_runtime_automation_competitors_independent_adjacent_buyer_purchases_no_verified_paid_exact_QA_demand",
  "source_ids": [
    "GDM-UNITY-RULES",
    "GDM-GODOT-STORE",
    "GDM004-GUA",
    "GDM004-GUA-REL",
    "GDM004-GODOT-UIAUTO",
    "GDM004-GODOT-UIAUTO-REPO",
    "GDM004-GDUNIT",
    "GDM004-FLOW299",
    "GDM004-FOCUS9",
    "GDM004-MENU999",
    "GDM004-BETTERUI",
    "GDM004-PAIDBUYER",
    "GDM004-MODERNREVIEW",
    "GDM004-FREEUSER",
    "GDM004-UNITYSURVEY"
  ],
  "parent_project": null,
  "related_projects": [],
  "legacy_ids": [],
  "next_action": "NO_GO for original standalone paid menu replay auditor after 2026-11-19 second-pass research: Gua MIT offers semantic runtime recording/replay for Godot and Unity, and Godot UI Automation is free; no verified paid demand for this exact QA workflow. Do not run B01, create product code, publish, or market. Reopen only on dated material evidence of buyer willingness plus an objective, meaningful advantage over full free alternatives and acceptable undercut economics.",
  "last_reviewed": "2026-11-19",
  "owner": "owner_decision_pending",
  "offer_price_usd": null,
  "delivery_hours_assumption": null,
  "total_first_order_hours_assumption": null,
  "verified_paid_pilots": 0,
  "actual_revenue": null,
  "actual_profit": null,
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
    "budget_window": "One cumulative CAD100 proposed ceiling for all phases, platforms, charges, tax and contingency; no automatic reset and no cash spending authorization.",
    "includes": [
      "tax",
      "currency_conversion_cost",
      "noncancelable_commitments",
      "testing",
      "listing",
      "payment_processing",
      "refund_reserves",
      "advertising",
      "hosting",
      "support",
      "marketing"
    ],
    "unknown_cost_action": "Unknown is not zero; obtain exact cost then pause external commitments pending separate valid authorization.",
    "production_runtime": "Offline-first and entirely local; no mandatory hosted service, runtime cloud or recurring owner billing.",
    "budget_fit": "Zero-cash local proof and planned package; publication/account verification and payout costs not yet authorized.",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  },
  "marketing_execution_authorized": false,
  "production_budget_verified": false,
  "success_probability": "not_established",
  "marketing_lane": "not_selected",
  "launch_gate": "NO_GO_original_paid_scope_free_full_runtime_testing_and_unproven_purchase_differentiation",
  "pre_sale_work_cap_hours": 0,
  "ad_test_cap_cad": 0,
  "offer_price_cad_hypothesis": 10.01,
  "platforms_supported": [],
  "platforms_proposed": [
    "Godot 4 GUI Control GDScript",
    "Unity 6 uGUI Editor and Play mode"
  ]
}
---


# Controller Menu Replay Auditor — Phase A research and Codex B/C execution record

## Dated second-pass viability reassessment — 2026-11-19 (supersedes CONDITIONAL_PROOF_ONLY below)

**RESEARCH VERDICT: NO_GO FOR THE CURRENT PAID PRODUCT PROPOSAL.** Status = paused, original idea preserved; do not develop even the former 8-hour B01 proof under the earlier planning handoff. Do not delete the record, GDM-002, or historical projects. This new decision is a research decision and does not change the Portfolio Manager project_phase `working_phase_2` historical handoff or fabricate technical work.

**Why verdict changed:** The first pass focused on free static Focus Audit Lite, gdUnit4 and two $9–$9.99 paid static auditors. The independent follow-up found *already operational, MIT-licensed full runtime UI recording/replay alternatives*, including Gua with Godot **and** Unity adapters, semantic UI identification, wait/assertions, recording, image evidence, CI and releases, plus free Godot UI Automation. Thus GDM-004's proposed paid distinguishing feature—runtime, repeatable stateful menu UI replay with useful reports—**is not unique** on currently inspected evidence. This is positive counter-evidence; not simply absence of competitors. A theoretically simpler interface or exact engine-version niche is not a demonstrated reason to pay.

### Corrected strongest substitute/competitor matrix

| Provider / actual observed offer | Verified/claimed feature overlap with first release | Price and actual limitations | Buyer purchasing significance |
|---|---|---|---|
| [Gua source](https://github.com/gua-project/gua) / [v1.2.0 release](https://github.com/gua-project/gua/releases/tag/gua-v1.2.0) (GDM004-GUA, GDM004-GUA-REL) | Runtime semantic UI tree, find/focus/click/press keys/waits/assertions, scripted and recorded test journeys, failure artifacts, CI, Godot 4.7 GDScript GDExtension addon, Unity 6000.5+ uGUI/UI Toolkit Mono package | **Free, MIT**, source and actual downloadable release; requires integration incl. native packages, sometimes .NET/agent tooling; *not* a trivial no-install editor dock. No local test performed. Godot older 4.6 and Unity 6000.3 are not covered by this Gua version; do not claim parity there | **Fatal challenge** to selling a basic recorded replay/schema/report across both engines |
| [Godot UI Automation official asset](https://godotengine.org/asset-library/asset/4665) / [code](https://github.com/graydwarf/godot-ui-automation) (GDM004-GODOT-UIAUTO, GDM004-GODOT-UIAUTO-REPO) | Visual in-game keyboard/mouse UI record/replay, screenshots, edit steps, test management, regression capture | **Free, MIT**; official 4.5 listing, README requires 4.5+ and reports Windows tested, lacks verified automatic gamepad focus assertions and large-suite scale | Strong one-clickish free workflow for Godot test recording; not proven exact controller QA parity |
| [gdUnit4](https://github.com/godot-gdunit-labs/gdUnit4) + engine native UI APIs (GDM004-GDUNIT) | Scripted assertions, scene runner, CI and simulated input; AI can help write tests | **Free, MIT**, significant script-writing/setup overhead for first test, but reusable | Allows user to create exact game-specific checks without buying separate QA tool |
| [Focus Audit Lite](https://github.com/aandk1024/focus-audit-lite) + [$9 paid Focus Audit](https://theidlehands.itch.io/focus-audit) (GDM004-FOCUS9) | Godot saved-scene directional reachability, missing focus, loop/dead-end; paid export/report CI | Free static lite or **USD9** full; normal runtime scripts not executed | Partial substitute; original plan already captured this, but does not rescue replay differentiator |
| [MenuPath QA](https://pocketnori.itch.io/menupath-qa) (GDM004-MENU999) | Unity uGUI directional/static path and unreachable-control audit | **USD9.99** one developer seat, static, not full input script emulation | Similar buyer segment; published price, no public sales confirmation |
| [Controller Menu Flow Tester](https://mtw1man2.itch.io/controller-menu-flow-tester) (GDM004-FLOW299) | Offline HTML manual menu layout, live flow graph, simulated D-pad/stick/keyboard input, focus anomalies, JSON/PNG exports | **USD2.99**; IMPORTANT: separate reconstructed layout, **NOT** verified import/replay of customer's Godot/Unity runtime scene. It is NOT established as a capable full substitute; do not dishonestly call USD2.99 a matched end-to-end price benchmark | Inexpensive partial UX-audit substitute undercuts perceived value of a light flow-graph tool |
| [Unity Test Framework](https://unity.com/how-to/automated-tests-unity-test-framework) | Free editor/PlayMode test runner, user-coded uGUI focus assertions | **Free** but requires coding, setup and scenario coverage | Strong native comparison to a paid Unity helper |
| [Better UI](https://assetstore.unity.com/packages/tools/gui/better-ui-79031) (GDM004-BETTERUI) | UI building + gamepad navigation **fix** toolkit | **USD64**, 44 ratings, 1,021 favorites shown 2026-11-19; not a QA replay tool | Positive evidence some developers obtain paid UI workflow tools, not proof of specific audit purchases |

**Do not conflate paid static checks with full free runtime replay.** The lowest priced publisher-advertised *potentially comparable static focus auditor* remains USD9 on Godot and USD9.99 on Unity; the USD2.99 browser layout product is not yet equivalent, so the paid undercut gate is not considered to have **independently** failed solely due to this cheap listing. The fatal challenge is the full free workflow and no observed reason to choose the paid runner. Published listing prices are not buyer-paid amounts.

### Buyer demand / actual willingness-to-pay verification

| Evidence | Strength and implications |
|---|---|
| [Unity forum 2024 purchaser statement](https://discussions.unity.com/t/ui-ugui-navigation-wizard/951273) GDM004-PAIDBUYER | Independent developer specifically **says they purchased** UI Navigation Wizard and asks for device-related functionality. One direct first-person report of paying for **navigation FIX**, not a replay tester. Strongest verifiable adjacent buyer purchase evidence; not a verified invoice and not representative market-size data. |
| [Unity Better UI](https://assetstore.unity.com/packages/tools/gui/better-ui-79031) GDM004-BETTERUI | Paid $64 listing has 44 ratings and 1,021 favourites (snapshot); demonstrates demand proxy for mature UI development package, not sales count or demand for an auditor. |
| [Modern UI Pack customer review](https://assetstore.unity.com/packages/tools/gui/modern-ui-pack-201717/reviews) GDM004-MODERNREVIEW | Public reviewer complains that selected gamepad state is absent/uneven and asks about alternatives. Direct buyer pain on paid menu asset, but buyer's proposed solution could be a navigation FIX, not a test runner. |
| [Independent Godot UI Automation adoption anecdote](https://www.reddit.com/r/godot/comments/1sdbx59/i_used_godot_ui_automation_gdvm_to_run_a/) GDM004-FREEUSER | Developer used free record/replay for multi-version regression and caught an incompatibility; another commenter appreciated not needing to build it. Strengthens the **free substitute**, not paid demand. |
| [Unity 2026 research](https://unity.com/resources/gaming-report) GDM004-UNITYSURVEY | Unity reports 35% of a 300-respondent Cint survey used AI for automated playtesting, *not* 35% willing to pay for our focus plugin. Broad adoption is not purchase intent. |
| Focus Audit ($9), MenuPath QA ($9.99), Controller Menu Flow Tester ($2.99) live asking-price pages | Real publisher offers. Public pages do **not** expose verified purchases, revenue, conversion rates or credible buyer testimonials for this exact product family. Do not invent sales or interpret nonzero listing/price as demand. |

**Finding:** A developer would plausibly *consider* buying a quality, easy-to-use menu builder/fixer because there is direct anecdotal paid behavior and paid asset reviews. We did **not** find equivalent evidence that enough developers would pay for a standalone focus replay auditor when free runtime recording, semantic automation, native testing and AI code are available. This is not a claim of zero buyers. The prior research's demand ledger was UNKNOWN; it remains UNKNOWN and is no longer sufficient to recommend a full paid build.

**Demand disproof search coverage:** competitor job phrases: controller menu flow audit, Godot UI automation free record replay, Godot visual UI testing MIT, gamepad focus CI, Unity uGUI runtime UI automation, Godot Unity cross-engine semantic replay, Unity navigation tester, controller plugin sales reviews, actual purchaser discussions, paid Asset Store navigation reviews, itch paid focus audit and cheap QA browser tools. Cross-checked official engine/store pages, GitHub code + MIT licenses + Gua release artifacts, independent Reddit reports, Unity forum and customer reviews, and official Unity survey. Search does not have access to merchant private sales dashboards, storefront conversion analytics, checkout records, physical device installs or direct customer purchase commitments. **No independent on-device functionality benchmark was performed.**

### Commercial and operational re-evaluation

- Proposed USD6.99 ≈ CAD10 at the original dated 1.4317 reference FX. Existing hypothesis modeled ~CAD6–7 worst route after fees/refund reserve, *before owner labor*. 1/3/12 monthly one-time sales remain hypothetical. If three actual monthly units yielded roughly CAD20, an initial 26–47h build plus 2–4h monthly multi-engine maintenance and continual low-traffic discovery is not a credible attractive background-business investment on available evidence. That does **not** establish a forecast of three sales; actual volume could be zero.
- A 15-minute synthetic time-saving threshold in the old B01 gate is weak economic justification for this buyer: a developer who can script or record with free tools may prefer to save USD6.99 and adapt a test themselves, while an indie might need less than an hour of total menu QA. No verified weekly testing cadence or external buyer return-on-investment figures support paid adoption.
- Most exact paid tester listings are new, with no accessible independent paid buyer transactions. Mature UI building/fixing tools attract reviews, but the user value, price, support expectation and distribution are different. No empirical conversion or storefront impressions were observed.
- Full Gua may be harder to integrate than a hypothetical lightweight UI-specific editor dock; this is **unproven potential difference**, not a basis for paid recommendation. A new paying product requires demonstrable (not assumed) time savings on a real existing game and results significantly beyond both Gua and Godot UI Automation, *not* a renamed wrapper around MIT primitives.
- Spend and authority unchanged: CAD100 maximum *planning ceiling*; CAD0 authorized, no publication/accounts/ads/outreach.

### Updated gate ledger

| Gate | New verdict | Explanation |
|---|---|---|
| Real problem | PASS | Developer buyer complaints plus active competitors; menu/gamepad focus fails |
| Buyers pay in adjacent sector | PASS, narrow scope | First-person purchase of navigation **fixer**; Better UI ratings |
| Buyers pay for standalone **runtime audit** | UNKNOWN (critical) | No independent actual paid order or purchase intent for exact user job |
| Significant paid advantage over free | **FAIL for current proposed scope** | Released MIT Gua plus free Godot UI Automation cover central runtime replay/report job; remaining simplicity advantage not proven |
| Under cheaper paid capable substitute | UNKNOWN / not independently fatal | USD2.99 manual HTML tool not same in-engine job; USD9/9.99 paid static auditors but free tools already strong |
| Passive economics + acquisition | UNKNOWN with negative risk | Low unit contribution, high initial two-engine development/ongoing upkeep, no demonstrated qualified exposure |
| Duplicate/rights | No active-project collision known; non-unique solution category | Keep GDM-002 and history unchanged; no commercial rights infringement planned |
| Overall **NO_GO** | **Do not spend developer time creating current offer** | Hard free-equivalent/differentiation gate fails on observed competitor capabilities |

### Reopen conditions and explicit revised Codex instruction

**Stop prior B00/B01/B02/B03... production and C marketing.** Do NOT create a prototype or run an 8-hour comparison merely because a Phase 1 record was indexed. Set no price, listing, launch or Complete status. Preserve all original research and existing project ID. Do not claim a competitive proof experiment ran; it did not.

Only reopen after **material new dated evidence** changes the conclusion, such as (a) credible independent buyers explicitly requesting/committing to buy a specific missing runtime focus-check workflow that free Gua/UI Automation/gdUnit4 cannot provide at reasonable effort, **or** (b) a narrow workflow shown with existing code/docs or a *separately authorized tiny bounded comparison* to work materially better (reliability/coverage/setup/CI) than the strongest full free stack with comparable product quality, AND evidence of buyer value at a lower sustainable price than capable paid alternatives, AND a real low-workload acquisition route. Do not demand interviews as a generic prerequisite, but do not label anonymous developer complaints as paid demand. Without changed evidence, leave **GDM-004 paused** and research a genuinely distinct opportunity instead; do not quietly rescope into a different tool under the same ID.

**Decision reversal record:** prior conditional reasoning 2026-11-19 assumed no free end-to-end dynamic runtime competitor verified. New evidence on 2026-11-19: MIT Gua shipped v1.2.0 in 2026-11 with both Godot and Unity semantic UI action/replay, plus an independently used MIT Godot UI Automation visual recorder released January 2026. This contradicts the assumed unmet functionality and invalidates the production recommendation despite credible general menu-navigation pain. Future reviewers should check original source URLs and account for version/installation limits before reversing again.

--- 



**HISTORICAL INITIAL RESEARCH VERDICT (SUPERSEDED BY SECOND-PASS NO_GO ABOVE): CONDITIONAL_PROOF_ONLY — 2026-11-19.** **Repository record:** planned/unvalidated; Phase 1 record in the working_phase_2 handoff, NOT a successful proof, release, approval, sale or completed project. **Market outcome is unvalidated.** Broad production is NOT approved by this research and must wait for B01 and B02 decision gates. No spending, public listing, person-directed outreach or new account action is authorized.

## 1. Executive decision and immutable scope

- **Business niche:** Game Development Marketplaces, a digital product/tool business. Buyer: solo/indie developers who already have an existing Godot Control or Unity uGUI menu and face unreliable gamepad focus across pause/resume, tab changes, modal overlays, hidden buttons and scene changes.
- **Paid result (only after proof):** an offline editor-usable utility that runs a deterministic set of synthetic controller action journeys on a live test scene, captures focus ownership and transitions, flags deterministic regressions with a reproducible step log, and exports sanitized machine-readable JSON plus an actionable Markdown report. It must NOT claim physical-gamepad emulation, automatic bug repair, universal accessibility compliance, full UI Toolkit support or freedom from engine bugs.
- **Why not just another static auditor:** both the free Focus Audit Lite and paid Focus Audit already inspect Godot focus graphs; Unity MenuPath QA does structural reachability. The *hypothesis* is repeatable **runtime lifecycle replay and state-dependent focus checks** with smaller setup than ordinary test-framework scripts, not broader static graph scans. If free/native/AI-assisted existing tools can do the same end-to-end job as easily, stop.
- **First committed technical candidates (conditionally):** Godot GUI Control (4.6 and 4.7 on Windows; 4.4 and other OSs if actually verified), Unity 6 uGUI (6000.3 on Windows). They are separate executable adapters and must be independently tested, not renamed copies. Only the shared normalized report shape/fixtures need be portable. No external server, subscription, telemetry or accounts to run the tool.
- **Commercial hypothesis:** one-time USD $6.99 per developer, included commercial use in owned games, no tool/source resale, no cloud service. Godot comparator USD $9; Unity comparator USD $9.99. No prices or rights are approved listings yet.
- **Status separation:** commercial_research = CONDITIONAL_PROOF_ONLY; implementation = unstarted; compatibility_support = none yet; release = none; marketing = none; sales = unobserved; money_spend_authorized = CAD0. The JSON phase is a work-queue handoff only.
- **First actual next action:** B00 duplicate/source/checkout preflight, B01 no-cash fair Godot comparison (max 8 operator/Codex hours total), then B02 Unity feasibility (conditional). NO unbounded production.
- **Project reuse:** GDM-002 is a separate active NPC transit implementation; GDM-001 and GDM-003 remain deleted from active projects by owner instruction, preserved as history ONLY. Do not revive, reskin or erase them.

## 2. Phase A acceptance ledger and hard-gate state

| Gate | State | Evidence and honest limit | Required next action |
|---|---|---|---|
| Useful buyer outcome | PASS as a problem / UNKNOWN as a saleable implementation | S07, S08, S09 show focus failures, not verified purchase intent | B01 test concrete lifecycle detection |
| Credible demand/buying reason | UNKNOWN | S07 is a genuine developer complaint; S03 and S06 are *asking* prices, not transaction counts; cannot infer sales | Launch only as measured, bounded commercial experiment after proof |
| Full free/native substitute gap | UNKNOWN, gating | S01, S02, S04 and S05 collectively may solve the same job; no fair stopwatch comparison performed | B01/B02 equal-fixture AI-assisted side-by-side |
| Nontrivial AI/DIY advantage | UNKNOWN, gating | Writing a few gdUnit4 tests with AI could match an addon | B01 measure first-use effort, honest correction costs and output |
| Sustainably lower paid pricing | PASS only as a mathematical **hypothesis** | USD6.99 below verified scoped USD9 and USD9.99 advertised prices (S03,S06); licenses/customer jobs differ | B06 refresh prices, account, rights and actual fee terms; cancel if true capable cheap tier <= sustainable offer |
| Budget | PASS for proposed local proof only | CAD0 startup under CAD100 cap; unknown payout/verification costs are NOT zero | B08/C review commitments, no spend without authorization |
| Passive/background workload | UNKNOWN | Local self-service fulfillment credible, but two-engine upkeep and promotion may exceed acceptable time | B10 measurement, cap recurring owner time and support |
| Technical / rights feasibility | UNKNOWN until tests | Godot native focus API and Unity uGUI available, but no verified runtime support | B01/B02, rights audit, device QA |
| Reachable legal distribution | CONDITIONAL | itch, existing Payhip and Unity Asset Store rules found; Canada seller setup, eligibility, payouts and accounts unverified | B08 owner-gated actual eligibility/publishing checks |
| Duplicate and reuse clearance | PASS on active/archives, PARTIAL on large historical catalogue | Main active folder, GDM archive crosswalk, prior 139 crosswalk, products/game-tools inspected; oversized opportunity_library/data/catalog.json and PROJECT_INDEX.json could not be fully materialized via GitHub connector | B00 local semantic search before allowing B01; update record if collision |
| Commercial launch authorization | FAIL (by design) | No owner authorization to spend, list, post, contact or create accounts | B08/C publisher actions require scoped authorization |

**Decision:** A ranked score cannot override UNKNOWN gates. This is neither GO_TO_PHASE_B unrestricted nor market validation. B01 is the only next new technical activity; no large implementation effort may precede its evidence.

## 3. Repository baseline and semantic duplication

- Inspected **Hi62384/Proj/main** 2026-11-19. Observed baseline commit before import: **860ff65e700acafcd492e3e642c11029e1d5174e** (recheck immediately before edits; no claim to local uncommitted work). Root AGENTS.md, README.md and root tree, business_portfolio/README.md, SCHEMA.md, PROJECT_TEMPLATE.md, source register, niche metadata, active GDM-002, archives and product directory were inspected.
- Canonical niche identity: N-gdm-20261115, digital-products/game-development-marketplaces. Proposed stable new ID **GDM-004**; active folder lists GDM-002 only, archive snapshot GDM-001/002/003, no 004 observed. The generated project index is a view and not primary evidence of record ownership.
- Target: business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-004-controller-menu-replay-auditor/project.md; sibling work/.gitkeep. All B/C source, test fixtures, packaging, images, descriptions and reports go into **this sibling work/**, not arbitrary computer folders.
- Closest semantic overlap: **GDM-001** tests old save-state regression, not controller focus/navigation; **GDM-003** tests binary/native dependencies, not menu journeys; **GDM-002** implements multi-agent transit, not UI QA. Neither archived concept should be revived under a new title. Existing products/game-tools directories retain original owners.
- Historical 139-record project crosswalk was inspected by IDs/paths; no clear gamepad-menu QA project found. Historical taxonomy has GDM-001/002/003 preserved. 1,512-item opportunity research catalogue could not be fully read in the connected interface due to size; this is a **limited-visibility duplicate check**, not a declaration that no idea was ever recorded.
- **B00 mandatory before expanding scope:** in a writable checkout search active/project history and all opportunity library catalog descriptions by job, keywords 'controller focus', 'UI replay', 'gamepad menu audit', 'navigation regression', 'runtime focus', and candidate source/tool terms. If semantic duplicate or existing implementation found, preserve its ID/progress; compare complement vs extension before creating a second deliverable. Use current AGENTS.md and coordinator ownership; do not edit GDM-002.

## 4. Broad idea discovery (25 distinct angles)

**Pass one:** consider digital utilities, engine plugins, 2D/3D/audio assets, original creative tools, passive affiliate/content and services; reject low-quality commodity, ongoing client labor, cheap native or archived concepts. This is a deliberately *desk-researched qualitative longlist*, not 25 independently measured markets.

| # | Opportunity | Model | Initial disposition and why |
|---|---|---|---|
| 01 | Runtime menu journey replay | Editor QA software | conditional finalist; dynamic focus, back/menu lifecycle |
| 02 | Static controller focus graph scan | Editor QA software | reject; Focus Audit Lite/paid Focus Audit perform it |
| 03 | Historical save regression harness | QA software | duplicate GDM-001 archived; do not recreate |
| 04 | Native export dependency preflight | Build QA | duplicate GDM-003 archived; do not recreate |
| 05 | Capacity-aware NPC vehicle scheduler | Gameplay plugin | active GDM-002; preserve actual implementation |
| 06 | Localization overflow analyzer | UI QA | serious finalist; Loc Audit competing paid tool and native pseudolocalization |
| 07 | Gamepad input-map consistency audit | Tooling | Input Audit paid USD12 and native map inspection; weak separateness |
| 08 | Low-poly laboratory prop kit | 3D assets | reject; free lab assets and low-price paid substitutes |
| 09 | Generic low-poly furniture kit | 3D assets | reject; saturated, generic AI-assisted alternatives |
| 10 | Original narrative puzzle component | Creative gameplay | high taste/testing burden and audience acquisition |
| 11 | Controller icon sprite atlas | UI assets | strong free icons and easy generic recreation; poor moat |
| 12 | Scene asset/license provenance scanner | Dev utility | real rights value but difficult reliable third-party provenance |
| 13 | Godot signal/scene stale-link checker | QA utility | native inspection and existing cheap tools; need separate research |
| 14 | Cross-engine dialogue graph validator | QA utility | complex graph format adapters; competing native graph plugins |
| 15 | 2D tilemap migration inspector | Tooling | engine update dependent; narrow compatibility and upkeep |
| 16 | Animation retargeting profiles | Rigging assets | many free engine/native helpers and rights risks |
| 17 | Synthetic NPC crowds performance test | QA utility | free profilers plus high benchmarking complexity |
| 18 | Mobile touch safe-area QA | UI tooling | native preview and device tests; hardware breadth exceeds low-cost gate |
| 19 | Shader portability diagnostics | Render tooling | native shader compilers and OS-specific costly testing |
| 20 | Sound loudness QA pack | Audio utility | free LUFS analyzers; weak differential |
| 21 | Custom game UI QA agency | Service | ongoing client delivery violates passive owner workload |
| 22 | Playable original menu demo packs | Creative assets | copyable without distinctive original art |
| 23 | Niche game asset review newsletter | Affiliate/content | ongoing audience-building labor, no reliable traffic |
| 24 | Roblox plugin test harness | Tooling | Roblox policies and different API; not equivalent port |
| 25 | Unity build-size report | Dev utility | native build reports and low willingness-to-pay signals |

**Pass two / serious candidates:**

| Candidate | Buyer/trigger | Strongest disproof | Relative evidence and launch cost | Screen /100 (subjective decision aid, NOT success chance) | Verdict |
|---|---|---|---|---|---|
| Runtime menu replay, 2 engine adapters | indie UI QA before console/controller release | gdUnit4 plus AI and free Focus Audit Lite likely enough | real pain reports S07–S09, cheap zero-runtime core, but no buyer payment | 56–69, low confidence | CONDITIONAL_PROOF_ONLY |
| Localization overflow QA | translation QA before release | Godot pseudolocalization and an existing USD12 Loc Audit; custom fonts/RTL expensive | adjacent pain but paid/freemium and exact buyer value unverified | 45–60 | reject pending distinct edge |
| Laboratory interactive prop system | indie science/escape game creator | free and sub-USD10 asset packs; art and cross-engine complexity | easy to create generic pack, insufficient differentiation | 31–48 | NO_GO generic scope |
| Dialogue-flow error tester | branching narrative author | native graph engines + AI static analyzers; schema fragmentation | no verified cross-engine need or affordable launch | 41–55 | RESEARCH_BLOCKED |
| Controller input-map checker | PC/console indie | USD12 Input Audit plus direct engine settings | narrower, may be a small add-on not distinct paid product | 40–54 | reject separate project |

Screen weighting: demand 20, gap 20, buyer/AI resistance 15, first test 15, acquisition 10, economics 10, upkeep 5, compliance 5. No candidate scored a hard-gate PASS from numbers. Runtime replay is merely most **efficiently falsifiable**, not proven best-selling.

### Selection disproofs and why near alternatives lost

- Free lab props from S20 and inexpensive paid laboratory assets S21 undermine a generic science/education prop pack; real custom original designs would be more expensive and risk poor differentiation.
- Localization QA has legitimate work but Godot native pseudolocalization and other commercial auditing packages compete with cheap detection; more language/rendering coverage and quality burden than B01.
- A static Godot focus inspector would directly compete with Focus Audit Lite (free), an unacceptable near-clone. A generic 'AI writes tests' offering is trivially replicated. Runtime state changes are the only tested hypothesis left.
- Engine-specific dialogue tooling requires a different data format per asset and uncertain acquisition; a claimed universal validator would overpromise.
- Building a service bureau of gamepad testers creates recurring human testing/support work; model fails passive gate even if AI reports efficiently.

## 5. Precise buyer/problem and observable value

**Buyer:** technical director or solo developer maintaining 3–25 menu screens in a Godot or Unity indie game with pause, inventory, settings, popup and return-to-game transitions. Purchase moment: a QA pass before a controller-compatible build, and a bug that reappears after a minor menu refactor. User must have edit rights to the game project; no external login needed by end user.

**Job:** from existing scene + a manifest of allowed actions and expected focus outcomes → replay representative safe journeys → see exactly which transitions are not reproducible/lose focus → keep regression evidence in CI. **Core payoff:** less repetitive manual controller checking and fewer unspecific 'menu broke' bug reports. Hypothesis requires fair confirmation. Nonbuyers: teams with one simple menu; teams happy scripting gdUnit4; UI Toolkit-only Unity projects; games without keyboard/controller navigation; studios whose event system has proprietary behaviors or cannot run test scenes.

**Buyer signal versus willingness to pay:** S07 is a specific bug complaint including mouse-first startup workaround; S08 is an adjacent UI Toolkit report (outside uGUI first target); S09 is an official bug report. All are *pain proxies*, not buyer requests for this exact product or paid conversion. Asking USD9 and USD9.99 listings show a market for offers, not actual units sold. Launch as a priced test **only after B01 pass and authorization**; zero actual customers and zero sales known.

## 6. Evidence ledger, dates, scope and source registration

Checked links and documentation 2026-11-19 where accessible. Official policy is authoritative for platform rules, store listings for observed asking price/vendor claims, Reddit/issues for reported pain, and future setup/runtime/sales metrics remain hypotheses.

| ID | Specific checked source or claim | URL | Evidence class | Qualification / strongest objection |
|---|---|---|---|---|
| S01 | Godot focus navigation reference; native focus actions and links | [Source](https://docs.godotengine.org/en/stable/tutorials/ui/gui_navigation.html) | official | Native navigation reduces need for paid add-on; not an audit/replay tool |
| S02 | Free Focus Audit Lite; checks open scene; MIT; published 2026-09-29 | [Source](https://store.godotengine.org/asset/theidlehands/focus-audit-lite/) | free_competitor | Open saved scene focus graph, unreachable/stuck/missing initial focus; published page flags unstable, does not replay gameplay transitions |
| S03 | Paid Focus Audit; USD9, Godot 4.4–4.7 | [Source](https://theidlehands.itch.io/focus-audit) | paid_competitor | Scans scenes and exports JSON/Markdown; no claim of transaction volume |
| S04 | gdUnit4 scene runner, action input simulation, CI and reports | [Source](https://github.com/godot-gdunit-labs/gdUnit4) | free_framework | MIT scene runner plus reasonable AI-assisted code could duplicate the core idea |
| S05 | Unity Test Framework; Edit and Play mode | [Source](https://unity.com/how-to/automated-tests-unity-test-framework) | native_framework | Free test runner; plugin must add concrete setup/outcome convenience |
| S06 | Paid Unity MenuPath QA; USD9.99/seat, Unity 6 uGUI | [Source](https://pocketnori.itch.io/menupath-qa) | paid_competitor | Structural reachability and return path reports; vendor states no runtime scripting simulation |
| S07 | Unity slider/controller UX complaint, 2026-07-30 | [Source](https://www.reddit.com/r/Unity3D/comments/1varlbu/ui_how_to_do_navigation_with_sliders/) | direct_user_report | One developer reports unreachable sliders and loss of controller selection; community suggests DIY workaround |
| S08 | Unity UI Toolkit pause-menu input focus issue, 2026-01-26 | [Source](https://www.reddit.com/r/unity/comments/1qnn2mu/enabling_gamepad_controller_xbox_with_unity_ui/) | adjacent_user_report | Two days debug reported; UI Toolkit not selected Unity target, so only adjacent evidence |
| S09 | Godot 4.7.2 Windows regression #124614 | [Source](https://github.com/godotengine/godot/issues/124614) | bug_tracker | Confirmed mouse motion overrides controller input; impossible to promise engine-bug repair |
| S10 | Official itch fees, open revenue sharing and payouts | [Source](https://itch.io/docs/creators/payments) | official | Default 10% revenue share example, typical 2.9%+$0.30 processing, one-time $3 tax interview for collected payouts, possible fees |
| S11 | Unity publishing / 70% provider share / no upload fee | [Source](https://assetstore.unity.com/publishing/publish-and-sell-assets) | official | Publisher profile/acceptance needed, USD4.99 minimum asking price, no publisher upload fee |
| S12 | Unity paid UPM unavailable, use .unitypackage | [Source](https://docs.unity.com/en-us/engine/6000.3/manual/assets-and-media/asset-store/publishing/upm/submit) | official | Cannot submit paid UPM through publisher portal; different packaging task |
| S13 | Unity review process and lead time | [Source](https://docs.unity.com/en-us/asset-store/publishing/asset-packages/submit) | official | At least five business days review after submission; not a launch guarantee |
| S14 | Godot official paid-store policy | [Source](https://docs.godotengine.org/en/stable/community/asset_store/faq.html) | official | Official Godot Asset Store cannot charge as of inspection; free companion only |
| S15 | Payhip free-plan 5% platform cut | [Source](https://payhip.com/pricing) | official | Payment gateway fees extra; existing storefront may be reused only within authorization |
| S16 | Payhip file ZIP allowance and downloadable formats | [Source](https://payhip.com/faq) | official | ZIP bundles supported; executable format restrictions apply |
| S17 | Bank of Canada 2026-11-19 USD-to-CAD 1.4317 | [Source](https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/) | official | Indicative FX only; bank and payment conversions differ |
| S18 | Canada GST/HST small supplier rules | [Source](https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst-businesses/when-register-charge.html) | official | Typically CAD30000 worldwide taxable supplies over four quarters; aggregate all related businesses, exceptions apply |
| S19 | Unity Asset Store USD payout terms | [Source](https://docs.unity.com/en-us/asset-store/publishing/asset-packages/revenue/payouts) | official | Monthly PayPal or quarterly bank USD payouts, tax and identity setup |
| S20 | Low-poly lab props given away free | [Source](https://fxxmorgan.itch.io/low-poly-lab-props) | free_asset_substitute | Generic lab prop pack has poor relative differentiation |
| S21 | Historical low-poly laboratory asset | [Source](https://assetstore.unity.com/packages/3d/environments/low-poly-laboratory-162723) | paid_asset_substitute | Low-priced lab model competitor; quality/rights comparison would require hands-on files |
| S22 | Free UI routing and focus framework alternative | [Source](https://github.com/indieshade/uiflow) | opensource_substitute | No verified same-job runtime audit; potentially reduces integration effort |
| S23 | Unity Asset Store package submission guidelines | [Source](https://assetstore.unity.com/publishing/submission-guidelines) | official | Current submission/version/rights and screenshot requirements must be rechecked at submission |
| S24 | Unity .unitypackage publishing workflow | [Source](https://docs.unity.com/en-us/asset-store/publishing/asset-packages/workflow) | official | Editor validation, uploader and portal submission; requires publisher credentials |
| S25 | Free code-level menu focus audit base | [Source](https://github.com/aandk1024/focus-audit-lite) | unverified_repository_reference | If repository not reachable/verified, use official free-store listing S02 as ground truth |
| S26 | Godot local input dispatch API | [Source](https://docs.godotengine.org/en/stable/classes/class_input.html) | official | Input event/action dispatch and device semantics must be measured, not assumed |
| S27 | Unity uGUI Selectable API | [Source](https://github.com/Unity-Technologies/uGUI/blob/main/com.unity.ugui/Runtime/UGUI/UI/Core/Selectable.cs) | source_code | Potential bounded navigator adapter; not automatic testing |
| S28 | Gamepad focus community report 2025 | [Source](https://www.reddit.com/r/godot/comments/1l6kv6i) | user_report | Older pain proxy, cannot treat one complaint as willingness to pay |
| S29 | Gumroad seller charges | [Source](https://gumroad.com/help/article/66-gumroads-fees) | official | Higher per-sale fixed/percentage than free-plan Payhip under working scenario; verify before channel inclusion |
| S30 | Unity Asset Store provider agreement | [Source](https://unity.com/legal/provider) | official | Licenses, refunds, withholding, rights and 70% basis apply |

**Source registration handoff:** The strict browser source_ids list already includes two *existing* valid registered IDs: GDM-UNITY-RULES (Unity official publishing guidance) and GDM-GODOT-STORE (Godot store policy). New sources in this body are **plain public URLs not registered identifiers**. During B00, before claiming complete research lineage, Codex must validate and add *genuinely relevant, nonduplicate* source records below to business_portfolio/research/SOURCE_REGISTER.json using the register schema, assign unique IDs, and then replace/augment project frontmatter source_ids. This later repository update does not constitute an extra output file from Phase A. Do not invent source registration success.

- Proposed GDM004-S01: Godot focus navigation reference; native focus actions and links; https://docs.godotengine.org/en/stable/tutorials/ui/gui_navigation.html; reviewed 2026-11-19; official; limit: Native navigation reduces need for paid add-on; not an audit/replay tool. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S02: Free Focus Audit Lite; checks open scene; MIT; published 2026-09-29; https://store.godotengine.org/asset/theidlehands/focus-audit-lite/; reviewed 2026-11-19; free_competitor; limit: Open saved scene focus graph, unreachable/stuck/missing initial focus; published page flags unstable, does not replay gameplay transitions. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S03: Paid Focus Audit; USD9, Godot 4.4–4.7; https://theidlehands.itch.io/focus-audit; reviewed 2026-11-19; paid_competitor; limit: Scans scenes and exports JSON/Markdown; no claim of transaction volume. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S04: gdUnit4 scene runner, action input simulation, CI and reports; https://github.com/godot-gdunit-labs/gdUnit4; reviewed 2026-11-19; free_framework; limit: MIT scene runner plus reasonable AI-assisted code could duplicate the core idea. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S05: Unity Test Framework; Edit and Play mode; https://unity.com/how-to/automated-tests-unity-test-framework; reviewed 2026-11-19; native_framework; limit: Free test runner; plugin must add concrete setup/outcome convenience. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S06: Paid Unity MenuPath QA; USD9.99/seat, Unity 6 uGUI; https://pocketnori.itch.io/menupath-qa; reviewed 2026-11-19; paid_competitor; limit: Structural reachability and return path reports; vendor states no runtime scripting simulation. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S07: Unity slider/controller UX complaint, 2026-07-30; https://www.reddit.com/r/Unity3D/comments/1varlbu/ui_how_to_do_navigation_with_sliders/; reviewed 2026-11-19; direct_user_report; limit: One developer reports unreachable sliders and loss of controller selection; community suggests DIY workaround. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S08: Unity UI Toolkit pause-menu input focus issue, 2026-01-26; https://www.reddit.com/r/unity/comments/1qnn2mu/enabling_gamepad_controller_xbox_with_unity_ui/; reviewed 2026-11-19; adjacent_user_report; limit: Two days debug reported; UI Toolkit not selected Unity target, so only adjacent evidence. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S09: Godot 4.7.2 Windows regression #124614; https://github.com/godotengine/godot/issues/124614; reviewed 2026-11-19; bug_tracker; limit: Confirmed mouse motion overrides controller input; impossible to promise engine-bug repair. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S10: Official itch fees, open revenue sharing and payouts; https://itch.io/docs/creators/payments; reviewed 2026-11-19; official; limit: Default 10% revenue share example, typical 2.9%+$0.30 processing, one-time $3 tax interview for collected payouts, possible fees. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S11: Unity publishing / 70% provider share / no upload fee; https://assetstore.unity.com/publishing/publish-and-sell-assets; reviewed 2026-11-19; official; limit: Publisher profile/acceptance needed, USD4.99 minimum asking price, no publisher upload fee. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S12: Unity paid UPM unavailable, use .unitypackage; https://docs.unity.com/en-us/engine/6000.3/manual/assets-and-media/asset-store/publishing/upm/submit; reviewed 2026-11-19; official; limit: Cannot submit paid UPM through publisher portal; different packaging task. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S13: Unity review process and lead time; https://docs.unity.com/en-us/asset-store/publishing/asset-packages/submit; reviewed 2026-11-19; official; limit: At least five business days review after submission; not a launch guarantee. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S14: Godot official paid-store policy; https://docs.godotengine.org/en/stable/community/asset_store/faq.html; reviewed 2026-11-19; official; limit: Official Godot Asset Store cannot charge as of inspection; free companion only. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S15: Payhip free-plan 5% platform cut; https://payhip.com/pricing; reviewed 2026-11-19; official; limit: Payment gateway fees extra; existing storefront may be reused only within authorization. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S16: Payhip file ZIP allowance and downloadable formats; https://payhip.com/faq; reviewed 2026-11-19; official; limit: ZIP bundles supported; executable format restrictions apply. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S17: Bank of Canada 2026-11-19 USD-to-CAD 1.4317; https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/; reviewed 2026-11-19; official; limit: Indicative FX only; bank and payment conversions differ. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S18: Canada GST/HST small supplier rules; https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst-businesses/when-register-charge.html; reviewed 2026-11-19; official; limit: Typically CAD30000 worldwide taxable supplies over four quarters; aggregate all related businesses, exceptions apply. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S19: Unity Asset Store USD payout terms; https://docs.unity.com/en-us/asset-store/publishing/asset-packages/revenue/payouts; reviewed 2026-11-19; official; limit: Monthly PayPal or quarterly bank USD payouts, tax and identity setup. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S20: Low-poly lab props given away free; https://fxxmorgan.itch.io/low-poly-lab-props; reviewed 2026-11-19; free_asset_substitute; limit: Generic lab prop pack has poor relative differentiation. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S21: Historical low-poly laboratory asset; https://assetstore.unity.com/packages/3d/environments/low-poly-laboratory-162723; reviewed 2026-11-19; paid_asset_substitute; limit: Low-priced lab model competitor; quality/rights comparison would require hands-on files. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S22: Free UI routing and focus framework alternative; https://github.com/indieshade/uiflow; reviewed 2026-11-19; opensource_substitute; limit: No verified same-job runtime audit; potentially reduces integration effort. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S23: Unity Asset Store package submission guidelines; https://assetstore.unity.com/publishing/submission-guidelines; reviewed 2026-11-19; official; limit: Current submission/version/rights and screenshot requirements must be rechecked at submission. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S24: Unity .unitypackage publishing workflow; https://docs.unity.com/en-us/asset-store/publishing/asset-packages/workflow; reviewed 2026-11-19; official; limit: Editor validation, uploader and portal submission; requires publisher credentials. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S25: Free code-level menu focus audit base; https://github.com/aandk1024/focus-audit-lite; reviewed 2026-11-19; unverified_repository_reference; limit: If repository not reachable/verified, use official free-store listing S02 as ground truth. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S26: Godot local input dispatch API; https://docs.godotengine.org/en/stable/classes/class_input.html; reviewed 2026-11-19; official; limit: Input event/action dispatch and device semantics must be measured, not assumed. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S27: Unity uGUI Selectable API; https://github.com/Unity-Technologies/uGUI/blob/main/com.unity.ugui/Runtime/UGUI/UI/Core/Selectable.cs; reviewed 2026-11-19; source_code; limit: Potential bounded navigator adapter; not automatic testing. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S28: Gamepad focus community report 2025; https://www.reddit.com/r/godot/comments/1l6kv6i; reviewed 2026-11-19; user_report; limit: Older pain proxy, cannot treat one complaint as willingness to pay. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S29: Gumroad seller charges; https://gumroad.com/help/article/66-gumroads-fees; reviewed 2026-11-19; official; limit: Higher per-sale fixed/percentage than free-plan Payhip under working scenario; verify before channel inclusion. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.
- Proposed GDM004-S30: Unity Asset Store provider agreement; https://unity.com/legal/provider; reviewed 2026-11-19; official; limit: Licenses, refunds, withholding, rights and 70% basis apply. Verify uniqueness and exact claims before adding to SOURCE_REGISTER.json; this proposal is NOT a registered source ID.

## 7. Full competitor, native and AI/DIY comparison — must be rechecked before release

*Paid advertised prices on 2026-11-19; no paid conversions/transaction counts observed. Source license and platform versions are from store pages and frameworks, not from executing binary installations.*

| Exact buyer job/outcome | Native Godot / free Focus Audit Lite | Free gdUnit4 + reasonable AI coding | Paid Focus Audit USD9 | Unity native test framework | Paid MenuPath QA USD9.99 | Proposed USD6.99 (not implemented) |
|---|---|---|---|---|---|---|
| Initial focus, arrow reachability | Godot has input/focus primitives; free Lite reports one scene | Possible via scene runner and script | Advertises all saved scenes and findings | Can script UI tests | Advertises uGUI path inspector | Must first match useful baseline; no claim of novel static algorithm |
| Runtime pause/modal/hidden transitions | Free Lite scene-only view, not scripted flow | **Yes, author can script**; free is a potentially complete substitute | Advertises saved-scene structural analysis, not scripted runtime transitions | **Yes, with custom tests** | Describes structural analyzer; no runtime user-script emulation | **Hypothesis:** prebuilt validated journey runner with less setup |
| Repeat action sequence and summarize focus owner each step | Native API access; DIY script | Feasible with test scripts | No comparable feature advertised; confirm with vendor/code | Feasible with custom scripts | Not advertised as runtime action replay | Proposed action/expected state schema and event trace |
| Report exit code/CI artifact | DIY work | Already JUnit/CI capable | JSON/MD static export | Standard test reporting | MD path logs | JSON schema + MD, fail on known regression, UNKNOWN on unsupported |
| Supports dynamic game scripts | Native scripts can be included | Yes with authored tests | Vendor says hidden branches skipped | Yes custom tests | Vendor explicitly excludes full script execution | Limited only safe permitted scripts in synthetic fixtures; never assert universal |
| Time to first comparable useful result | Manual effort unknown | Must **measure** with same fixtures and AI prompt | Installation/scan fast for static; runtime test not advertised | Needs custom tests; time unknown | Installation/scan for static | B01 pass requires demonstrably less setup/change effort |
| Versions/license | Godot 4; Focus Lite 4.4–4.7 MIT | MIT, releases vary by version | 4.4–4.7, store license | Unity test framework, bundled/editor | Unity 6 uGUI, USD9.99/seat | Godot 4.6/4.7 and Unity 6000.3 after independent QA; own-source commercial tool license |
| Customer cost | CAD0 | CAD0 plus development time | USD9 one-time | CAD0 plus development time | USD9.99 seat | USD6.99 per developer if proven, exact total depends on processor/tax |
| Reliability/output edge cases | Lite reports limited static cases | Can be made comprehensive by user | Vendor notes skipped hidden/binary scenes | Can exercise project state with developer expertise | Unknown findings for custom controls | Must report UNSUPPORTED/UNKNOWN on unhandled hooks; no false clear report |
| Confidence in superiority | Verified native capabilities, not benchmark | **High confidence it is a real threat** | Vendor-claimed feature description | Verified test framework exists | Vendor-claimed feature description | **UNVERIFIED** until B01/B02 |

**Sustainable undercut rule:** Actual price is USD6.99 versus the *lowest capable comparable scoped paid option observed* of USD9 (Godot S03) or USD9.99 (Unity S06). It is not proven globally cheapest and $6.99 only remains defensible if offered same core supported job with reproducible quality. The product is not justified solely because it is cheaper: free combined tooling is the principal threat.

**Independent disconfirming search, performed separately:** after initial selection, checked Focus Audit *Lite* feature table (stronger than a vague 'free checker'), gdUnit4 scene runner/CI and MIT reuse, Unity native test framework, the paid Godot scanner's exported reports, paid Unity auditor's custom-control UNKNOWN behavior, Godot issue #124614, the specific posted slider/controller workaround, cheap generic asset pack, current fees and required publishing accounts. Search phrasings included 'runtime gamepad focus automation', 'Godot focus audit free', 'UI focus gamepad gdUnit4 scene runner', 'Unity navigation auditor uGUI', 'dynamic menu pause controller focus lost', 'Godot controller regression 4.7', and 'low poly lab props'. The largest unresolved disproof is that a modest AI-assisted test fixture plus gdUnit4 may equal the proposed buyer journey quickly; **do not code around this objection rhetorically**. Price alone is not a substitute for customer value. Full demand after listing is UNKNOWN.

### B01: small falsifiable, fair first proof (zero cash; maximum 8 hours, including baseline)

Create only TWO original synthetic menu fixtures in the new project's work/proof/ folder, not a broad add-on. Fixture A = settings with slider, navigation links and back; fixture B = pause modal, hidden submenu, scene swap and return. Plant exactly five diagnosed independent problems: (F1) no initial selected item, (F2) D-pad-unreachable required button, (F3) modal focus trap with no safe return, (F4) focus reference invalid after hiding/revealing, (F5) wrong action-map activation on resume; include clean variants and a deliberately unsupported custom control.

Run **the same fixtures** first with native Godot tooling plus Focus Audit Lite and gdUnit4 scene runner using a single reasonable documented AI-assistance pass, then with a minimal, nonmarketable replay harness written after baseline. Record download/version/license, setup, test writing, execution, retry/fix time, false positives, omissions, reports and screenshots/terminal log. Compare total time and exact faults; no synthetic estimate masquerades as independent customer benchmark.

Objective B01 **PASS iff**: (1) the new harness actually simulates input in a live scene rather than static graph guesses; (2) catches at least four of five planted faults including both F4 and F5 (or explain inaccessible engine bug as UNKNOWN, which does not count as catch); (3) zero incorrect PASS on unsupported/unexecuted steps; (4) healthy fixtures do not yield more than one false positive; (5) identical three-run artifact hashes after removing timestamps/nonessential ordering; (6) an uninvolved developer can follow setup docs in at most five minutes; and (7) against a competent gdUnit4+Focus Lite+AI workflow it saves **at least fifteen minutes** to reproduce and hand off both fixtures with equivalent diagnostic evidence, without more serious false positives. Record side-by-side methodology, artifacts, versions, skill level, and direct observations. The 15-minute hurdle is a commercial management test, NOT a measured buyer need.

**FAIL/STOP** if either free workflow matches buyer outcome within 15 minutes, if F4/F5 cannot be safely exercised, if edge cases are unstable, if input APIs cannot represent actual relevant action, or if more than 8 hours is required. Stop project as independent paid product, preserve the proof, mark blocked/NO_GO with changed fact; do not pivot without another Phase A review. If B01 passes, start B02 scoped Unity proof: compare Unity uGUI native tests and MenuPath QA with same five *behavioral classes* adapted to Unity; maximum 3 extra hours. If Unity loses the fair advantage, remove the Unity committed adapter through a dated narrowing decision, not by pretending it is supported; still release a viable Godot-only product only if price and passive gates remain true. **No mandatory customer interviews or paid pilots.**

## 8. First salable scope and buyer-facing offer

**After BOTH technical proof gates for the corresponding selected edition pass**: a Godot editor plugin and Unity editor utility that each (i) import/define concise safe journeys, (ii) execute synthetic input on isolated test scenes, (iii) capture state changes and selected control path before/after each action, (iv) fail on missing focus, unexpected target and trapped return, (v) expose UNKNOWN on custom controls/incompatible flows, (vi) output normalized JSON, readable Markdown, deterministic stable test IDs and console exit status, (vii) have fixtures, docs, demos, accurate license and support limits. Essential differentiator is **live stateful journey replay**; no UI builder/auto-fixer/AI service/analytics SDK.

**Deferred:** magical 'scan every menu without specification', consoles/physical device certification, automatic accessibility compliance, Unity UI Toolkit, UXML, Unreal UMG, Roblox UI, screen OCR, shader testing, native packaging for every OS, multi-engine monorepo framework. Broad auto-discovery is not a hidden prerequisite. Build only adapters for selected verified engines and document code reuse honestly.

**Short honest store headline draft:** "Replay gamepad menu journeys; catch focus loss when screens change."  
**Short description draft:** "An offline QA tool for Godot Control and Unity uGUI projects. Define safe controller actions, replay them on test menus, and export steps showing the control that had focus before and after each change. Includes reproducible sample menus and clear UNKNOWN results for unsupported flows. Version and platform support are edition-specific and verified before listing."  
**Honest limitations:** Actions are simulated inside the target engine; physical hardware, OS/driver bugs, console certification, accessibility review and other engine versions require independent testing. Not a replacement for hands-on controller QA.  
**FAQ draft:** "Does this fix the menu? No; it reports and reproduces a likely focus regression." / "Does it work with UI Toolkit? The first Unity edition is uGUI only." / "Does it run in a shipping game? No cloud/runtime paid dependency; editor/testing integration." / "Do I need a subscription? No." / "What if a custom UI control cannot be inspected? It is marked UNKNOWN, not passed."

**Proof screenshots/video specifications (not existing):** before/after working demo with F4, a visible replay step trace, a safe failure report with exact scene/action/selected control, a side-by-side free baseline table, version compatibility matrix, a 45–75s actual capture with UI labels readable. No AI mockups passing as screenshots. Maintain original art and owned samples.

## 9. Pricing, licenses, budget, CAD150 economics

**FX reference:** Bank of Canada USD1 = CAD 1.4317 on 2026-11-19, S17. USD6.99 ≈ CAD 10.01 before checkout tax, conversion spread and issuer/merchant fees. Godot paid equivalent USD9 ≈ CAD 12.89; Unity USD9.99 ≈ CAD 14.30. Source prices are *asking prices*, not observed paid outcomes. Proposed Payhip native CAD9.99 is roughly comparable to USD6.99 at the indicative rate. No subscriptions: monthly sales below are hypothetical counts of *irregular one-time purchases*, not MRR.

**Explicit economic model per USD6.99 sale (forecast assumptions not platform statements):**

- itch route: default nominal marketplace share 10% gross, processor 2.9% + USD0.30 as its documented typical example; assumed 5% gross refund allowance and 2% FX/payout/currency reserve. **USD 5.299 = CAD 7.59** per non-zero-gross sale equivalent. May also incur USD3 total one-time tax-interview charge and payout fees; reserve/account approval is a B08 blocker until established.
- Unity Asset Store: publisher receives 70% of gross as official share, subtract modeled 5% gross refunded and 2% FX/transfer reserve, giving **USD 4.404 = CAD 6.30** per modeled sale. Unity may withhold applicable taxes; fee/threshold and account currency details need check. No invented Unity bank expenses.
- Payhip CAD9.99 sale: 5% Payhip + assumed 2.9% processor and equivalent USD0.30 fixed transaction + assumed 5% refund + 2% FX buffer = about **CAD 8.07**, before Canadian tax; actual domestic CAD processors can differ.
- A **conservative route-independent unit contribution** for threshold planning is **CAD 6.30** (Unity worst of modeled channels), before owner labor and any unexpected transfer fee. Sales via separate destinations are NOT counted twice.
- Startup incremental CAD0 proposed: research 0 cash, local fixture/proof 0, tools/add-on/free CI 0, packaging 0, listing creation 0 under verified free tiers, organic content 0, ads 0, hosting/server 0. Any paid plugin, device, subscription, sample, business fee or account charge is not authorized (unknown, not assumed zero). One cumulative CAD100 ceiling across all phases, not reset; authorized spend CAD0. Suggested optional budget envelope NONE until justified and approved. Existing liabilities and bank/card fees require reconciliation.
- Normal fixed monthly cash commitment **CAD0 only if free-account policy/terms remain available**; no unapproved paid subscriptions. Actual self-employment income tax is excluded from portfolio operating contribution, not from real fiscal obligations.
- One-time itch tax identity cost USD3 ≈ CAD 4.30 if it applies and is deducted from future payouts; first itch contribution after it ≈ CAD 3.29, before payout/FX surprises. Do not spend personally to solve a gate without authorization.
- **Break-even under zero recurring fixed expenses:** at least one successful nonrefunded sale with net per-order value above any incurred fees. For an itch-only hypothetical first sale including the USD3 identity cost, USD price must satisfy P×(1−0.10−0.029−0.05−0.02) −0.30 −3 >0, i.e. P > USD 4.12. Thus a mathematical interval exists from ~USD4.12 to strictly below USD9; the proposed USD6.99 is in it. This is **not proof of customers**. Cash marketing CAC must be zero under current authorization, and if later proposed its cost per incremental sale must remain below expected customer contribution after refunds/payouts; reserve a safety margin rather than bidding the whole amount.
- **Sensitivity:** each extra 1pp refund allowance removes USD0.0699 gross or ~CAD0.10 per sale; +1pp payment/platform fee similarly ~CAD0.10. Another USD0.30 fixed payment charge removes CAD0.43. A price fall to USD5.99 gives itch ≈ CAD 6.44 and Unity ≈ CAD 5.40, before support. A sale channel claiming hidden fixed monthly fee breaks zero-cash assumptions. At 2 owner hours for 3 sales, estimated operating contribution under worst route is CAD 18.91, about CAD 9.46/owner hour, an unattractive return unless work is reduced or volume improves.
- **Owner work sensitivity:** 3 minutes manual support/order at 12 sales = 36 minutes plus monthly upkeep. 15 minutes/order at 12 = 3 hours before marketing/platform maintenance and likely breaks low-touch fit. Automated self-delivery must be independently demonstrated and exception rate measured.

| Monthly hypothesis | Distinct sales | Expected contribution using conservative route (not measured) | Explanation |
|---|---:|---:|---|
| No sales | 0 | CAD 0.00 at worst-route 5% refund buffer except stress | CAD0; owner still incurs review time |
| Stress | 1 | CAD 6.30 at worst-route 5% refund buffer except stress | 20% refunds, 3% FX, Unity 70% route; CAD 4.70 before optional one-time payout costs |
| Base hypothesis | 3 | CAD 18.91 at worst-route 5% refund buffer except stress | 3 one-time sales; no claim of recurrent subscription income |
| Upside hypothesis | 12 | CAD 75.66 at worst-route 5% refund buffer except stress | 12 one-time sales; not an observed market forecast |
| Portfolio target illustration | 24 | CAD 151.31 at worst-route 5% refund buffer except stress | 24 Unity-price-unit sales at worst-route model pass CAD150 before labor |

The project's possible **portfolio contribution** is incremental. At base 3 sales, ~CAD 18.91 toward CAD150, leaving CAD 131.09 for other *nonoverlapping* projects; upside 12 sales ≈ CAD 75.66. Reaching CAD150 from this product alone would require about **24** comparable worst-route units per month, currently unsubstantiated. Stress assumes one sale with markedly higher refunds; no-sales contributes CAD0 even if work was spent. No guaranteed income or sales probability is claimed.

**Money permissions:** do not spend, activate monthly recurring payments, create accounts, post marketing, publish a listing, perform a real checkout charge, or distribute software based on this file. Keep recorded authority separate from budget, source registrations, operational statuses and lifecycle phase.

## 10. Three separate target matrices and committed release set

### 10.1 Technical compatibility matrix (buyer/runtime capability, NOT a storefront)

| Target | Use evidence; API/shared core/adaptation | Dependency, rights, test access, acceptance | Decision; task; recurring burden |
|---|---|---|---|
| Godot 4.6 GUI Control on Windows | S01–S04; GDScript harness using Control focus owner, Input action trace, scene changes | Engine installation; input map, export reproducible fixture log, keyboard+D-pad; no true physical device claim | SELECTED **conditional on B01 pass**; B03/B05/B07; about 0.4h/month review |
| Godot 4.7 and 4.7.2 GUI Control on Windows | same core, Godot S09 bug regression | Explicit negative case with mouse/analog interference; distinguish engine fault from add-on fault | SELECTED conditional; B03/B05/B07; about 0.3h/month incremental |
| Unity 6 / 6000.3 uGUI on Windows | S05, S06, S27; standalone C# adapter, EventSystem and Selectable, shared report schema | Unity Test Framework and Unity Editor; input-system/legacy UI module variants as documented, no undocumented reflection | SELECTED conditional on independent B02; B04/B05/B07; about 0.6h/month |
| Godot 4.4/4.5 and Linux/macOS | same GDScript, different focus APIs/platform behavior | B05 must actually execute tests on available systems; 4.4 release behind exact API support | CONDITIONAL, not automatically supported; B05; only add when free access |
| Unity UI Toolkit | different VisualElement focus/input semantics; S08 only adjacent demand | Needs separate adapter and new proof; extra maintenance | EXCLUDED first scope; revisit if genuine use/price evidence |
| Unity 2022 legacy, mobile and consoles | version/device/platform licensing, CI/hardware testing uncertain | No platform test access verified; real controller required for hardware claims | EXCLUDED until resources/rights/QA justified |
| Unreal UMG, Roblox, GameMaker, Construct, GDevelop | unrelated focus APIs, export/asset rules and test rigs | 5+ separate architectures exceed useful shared work; no credible advantage verified | EXCLUDED, not 'universal' |
| Browser-based demo video | static video/HTML can be viewed in browser but is not a browser runtime port | demo playback accessibility; no data exchange | Marketing asset only, NOT software compatibility |

*Committed launch set after each respective proof:* tested Godot 4.6 and 4.7 Windows edition, plus tested Unity 6000.3 uGUI Windows edition; first-stage Godot release may go live while Unity review processes, but **does not finish Phase B** if Unity remains selected. If an adapter genuinely fails B02, document objective failure and an authorized narrowing/research revision; do not silently drop it for convenience. Recheck Godot and Unity version numbers before claiming support.

### 10.2 Sale, distribution and delivery matrix (where buyers pay)

| Destination | Buyer fit, seller/policy/fees | Package/rights and owner access | Decision, tasks and acceptance |
|---|---|---|---|
| itch.io paid tool listing | Indie game creators browse tools/tags; S10 default 10% share + processors, payout/tax interview, Canadian identity case not account-verified | One buyer-facing page, independent Godot and Unity ZIP downloads correctly labelled; commercial own-game license; owner authorizes account/listing | SELECTED conditional; B08/B09; store public URL, price, tax/payout terms and successful free/sandbox delivery |
| Existing Payhip storefront | Direct link/owned page route; S15 5% free + gateway; existing account mentioned in root repo README (public record, current login not inspected) | Same edition ZIPs; price CAD9.99 hypothesis and honest version info; existing account not permission to upload | SELECTED conditional; B08/B09; observed sale page and a legitimate free/order delivery check only if permitted |
| Unity Asset Store | Direct Unity-uGUI tool buyer; S11, S12, S13, S19: free publisher submission, 70% revenue, USD payout, tax identity and review | Unity .unitypackage, NOT paid UPM; Unity-specific QA, reviewer assets, license/EULA rights; account setup and approval required | SELECTED conditional after B02; B07/B08/B09; observed approved public listing, actual version/delivery; owner may block publish |
| Official Godot Asset Store | S14 cannot take paid purchases currently | A free limited demo companion only if truthful/rights compatible; no access to paid ZIP | CONDITIONAL DISCOVERY, not a paid channel; B09 later; skip unless worthwhile and authorized |
| Gumroad | marketplace fit but higher fixed fees and uncertain advantage over existing Payhip | same downloadable ZIP, extra storefront upkeep | EXCLUDED for first launch; research S29 if economics change |
| Fab/Unreal Marketplace | product-type/Unreal consumer fit not established; Unity/Godot editor package not a ready Unreal asset | would need new native UMG adapter and QA | EXCLUDED |
| Roblox Creator Store | Roblox plugin/module type not our Godot/Unity UI tester | platform-specific code and seller eligibility | EXCLUDED |
| Steam | not a sensible plugin checkout; Steam Direct fee exceeds no-spend policy | would require consumer app binary and upfront fee | EXCLUDED |

Storefronts are not substitute technical runtimes. No registration, tax status, sales or page-publication confirmation is implied. Each selected row has a B08/B09 implementation and B05 QA dependency. If account approval is blocked, complete local packages/listing drafts then preserve blocker; do not claim Phase B distribution done.

### 10.3 Promotion / demand-generation matrix (separate from stores)

| Channel | Real audience / path to exposure, approval/policy | Specific authentic assets and adapted copy; cadence/cost | Status and assigned tasks/evidence |
|---|---|---|---|
| itch.io tag search and devlog | Search developer tools, 'controller', 'gamepad', 'Godot'; listing must exist, exact tag availability/account required | Optimized title/tags, 1 real F4 GIF and useful devlog describing reproducible test and free baseline; one launch post then only meaningful updates; CAD0 ads | SELECTED conditional; C01; store link + tagged indexed page, viewed metadata + visits if available |
| Payhip indexed product/how-to page | Existing store may provide direct discovery but no guaranteed traffic; search relevance weak without owned distribution | Short guide 'Why your pause menu loses gamepad focus' with owned fixture and link to verified offer; one main guide + correction only as needed; CAD0 | SELECTED conditional; C02; observed public URL, search accessibility and referred visits if available |
| One genuine YouTube demo/tutorial | Viewer searching Godot/Unity focus bug; account/channel and posting authority required | 60–120s captured comparison and walkthrough, separate Godot/Unity chapters, visible limitations & CTA; no fake renders; one video and factual update | SELECTED conditional; C03; public video URL, description links to sale page, analytics if accessible |
| Unity Asset Store listing search assets | Native in-store buyer filters, keywords, official publisher portal rules | Accurate title/short description, actual editor screenshots, tagged supported versions; no impersonated reviews | SELECTED as listing discovery effort; C04/B09; approved live page URL and observable listing data |
| Reddit r/godot or r/Unity3D | Community guidelines may ban unsolicited promotions / AI content; relevant conversations only | Useful non-promotional diagnostic writeup; no auto self-promo | CONDITIONAL on fresh subreddit rules and individual post approval; C05; no scheduled spam |
| Engine docs/Q&A comments | Help-desk and thread replies risk unsolicited promotion/CASL concerns | Link only when explicitly allowed and substantively responsive | EXCLUDED for automatic marketing; person-directed posting requires authorization |
| Paid search or socials | No verified conversion economics; low ticket and one-time revenue | CAD0 cap, no paid tests | EXCLUDED unless actual organic funnel justifies owner-approved new allocation |
| Affiliate/reseller outreach | Unverified partners/audience and ongoing administration | Possible later with formal permission and compliant disclosure | EXCLUDED first cycle |

**Committed first promotion cycle after observed live distribution + permission:** C01, C02, C03, C04 with independent URLs, distinct authentic copy, accurate claims, and metric collection. A blocked account does not authorize auto-posting elsewhere. C05 remains conditional. Do not publish identical spam to multiple groups, use mass DMs, synthetic reviews, purchased engagement or invented screenshots.

## 11. Technical design after passing the proof (not existing files)

**Minimal architecture:** Each engine owns its adapter/runner; both write the same immutable normalized Result v1 schema. A thin output formatter is duplicated if necessary; do not create an overgeneral cross-engine runtime requiring a new server. All runtime checks offline, local, opt-in, no telemetry, no workspace auto-discovery or hidden file uploads.

Proposed project-owned work tree (paths FUTURE, not claiming existence):

~~~
work/
  .gitkeep
  proof/
    godot_case_a.tscn, godot_case_b.tscn, baseline_notes.md
    unity_cases/, comparison_evidence.md, tool_versions.json
  schema/
    journey-v1.schema.json, result-v1.schema.json, test_vectors.json
  godot/
    addons/menu_replay_auditor/plugin.cfg
    addons/menu_replay_auditor/plugin.gd
    addons/menu_replay_auditor/runner.gd
    addons/menu_replay_auditor/event_trace.gd
    addons/menu_replay_auditor/report_writer.gd
    tests/, demo/, docs/, LICENSE.txt
  unity/
    Assets/MenuReplayAuditor/Editor/MenuReplayWindow.cs
    Assets/MenuReplayAuditor/Runtime/FocusJourneyRunner.cs
    Assets/MenuReplayAuditor/Tests/
    Samples~/, Docs/, LICENSE.txt
  packaging/
    releases.json, checksums.sha256, asset_manifest.json
    itch/, payhip/, unity_asset_store/
  marketing/
    itch_devlog.md, tutorial_script.md, payhip_guide.md
    demo_capture_manifest.json, campaign_evidence.json
  evidence/
    compatibility.json, qa.json, channel_register.json, task_status.json
  operations/
    support_triage.md, financial_observation_private_pointer.md
~~~

**Versioned input schema (example, NOT yet running):**

~~~json
{
  "schema_version": 1,
  "test_id": "pause-submenu-return",
  "scene": "res://test_ui/pause_fixture.tscn",
  "initial_focus": "Pause/Resume",
  "steps": [
    {"at": "scene_ready", "expect_focus": "Pause/Resume"},
    {"action": "ui_down", "expect_focus": "Pause/Settings", "max_frames": 3},
    {"action": "ui_accept", "expect_screen": "settings", "max_frames": 5},
    {"action": "ui_cancel", "expect_focus": "Pause/Settings", "max_frames": 5}
  ],
  "allow_side_effects": false
}
~~~

Godot paths use stable project-owned IDs or known scene-relative node paths. Unity edition maps equivalent steps to hierarchy selectors and uGUI EventSystem currentSelectedGameObject. **Never silently bind by arbitrary label when duplicate controls exist.** Compiler and schema validation should reject unknown actions, infinite frame waits, external URLs, duplicate test IDs, illegal path escapes and missing expected fields.

**Output contract:** {schema_version, test_id, engine, engine_version, adapter_version, platform, fixture_hash, result_status: PASS|FAIL|UNKNOWN|SKIPPED, steps:[{index,action,focused_before,focused_after,expected,observed,frames,reason}], assertion_count, replay_digest}. A run result cannot be PASS when any expected step was skipped/unsupported/unexecuted; FAIL when a supported, deterministic expectation differs; UNKNOWN when plugin cannot inspect behavior; SKIPPED only for declared excluded fixture. Include human-readable negative-case description and safe handoff. Strip absolute home paths and player/user data; no personal/session analytics.

**State machine:** NOT_STARTED → LOADING_SCENE → SETTLING → REPLAYING_STEP → OBSERVING → {NEXT_STEP | FAILED | UNKNOWN} → REPORTING → ENDED. Every transition has a maximum frame count. A cancelled/closed scene or runtime crash must yield incomplete/UNKNOWN evidence, never a false PASS. Avoid emitting an action twice on retries. On failed validation, leave project scenes unmodified. Input mutations occur solely in isolated copy/synthetic QA project; production project replay requires an explicit allowlist and user choice. Input.parse_input_event focus owner correctness is NOT assumed until B01; verify with scene runner and actual API behavior. For Unity, test use of Input System UI Input Module and EventSystem separately; do not mix old/new input pipelines without declaring support.

**Core check pseudocode:**

~~~text
validate_manifest(journey, allowed_scene_root, max_steps=100, max_frames=600)
load isolated scene and attach observer
wait readiness within timeout; else UNKNOWN
for each step once:
  before = read_focus_owner()
  if unsupported custom control or unsafe submit handler: UNKNOWN and stop
  dispatch matching engine input event/action
  advance bounded frames, inspect changes, log timestamps only in volatile data
  after = read_focus_owner()
  compare expected observable state AND focused node
  if mismatch: mark FAIL, retain input and before/after evidence
  if success: continue
report ordered normalized records and machine exit status
cleanup scene, connections, temporary state; never write outside work/
~~~

**Invariants and performance tests:** no unknown→PASS coercion; no accept/submit on untrusted shipping scenes; no report success if step count != expected; every test ID unique; duplicate scheduled replay has stable digest; 100 steps capped at 600 total simulated frames unless explicitly validated; no read of private customer data; UI graph size up to 500 active controls measured in a disposable fixture (not asserted performant without measurement). Verify leak-free teardown after 100 bounded runs on one hardware/engine environment and record elapsed time/memory; if insufficient test hardware available, document unverified coverage rather than claiming support.

**Security, rights and license:** Original GDScript/C# source, original synthetic menus, no copied paid code/competitor logo/stock graphics. MIT gdUnit4 may be used as a *development dependency* with required license notices if copied/bundled; avoid shipping its internals where unnecessary. Focus Audit Lite MIT is a comparison input, **not** a source base to relabel as proprietary. Owner retains copyrights to original files; commercial-use license allows developer's game and CI integration but disallows reselling standalone tool. No runtime network, secrets, user telemetry or remote jobs; do not auto-scan sensitive files outside requested project. Keep seller tax/customer records private off the public repo.

## 12. Exact dependency-ordered Phase B task plan

**Task format:** Task ID; effort is rough Codex/operator time, NOT a completion deadline. A task may only begin after its predecessor proof/authority. Only one writer per project.md, assign separate paths when parallel. For every task update work/evidence/task_status.json, relevant hashes, status, dated facts and precise next action in project.md.

| ID / priority / rough hours | Prerequisites and exact operation | Owned output and acceptance evidence | Unattended/permission/cost / stop |
|---|---|---|---|
| B00 P0 0.5–1.5h | Refresh main, AGENTS, niche/project record; inspect catalogue, archive crosswalk, actual products and research; import nonduplicative source records; confirm ID uniqueness and git lock | project.md updated source_ids; duplicate_checked.md under work/evidence; dry-run builder diagnostics and current SHA | Local desk review allowed; stop and preserve state on duplicate or write conflict; CAD0 |
| B01 P0 <=8h | Full same-fixture Godot native+Lite+gdUnit4(+AI) vs bounded replay runner experiment above; exact versions/reports, negative and healthy cases | work/proof/comparison_evidence.md, two owned fixture scenes, measured setup time, three repeat hashes, PASS/FAIL ledger | Local code only allowed when explicitly asked to execute Phase 2; CAD0; if fail STOP broad build |
| B02 P0 <=3h | Only after Godot PASS, compare Unity Test Framework+AI/uGUI against adapted same 5 negative behaviors; check available Unity editor | work/proof/unity_cases and unity_comparison.md | Local permission only, CAD0; if no editor/technical edge, record blocker or narrow via dated decision |
| B03 P1 4–8h | After B01 PASS, implement Godot plugin UI, manifest parser, fail-closed runner, report schema and cleanup | work/godot addons+schema, demo and docs; 5 planted faults, 3 clean repeats, malformed manifest negative tests | CAD0 local, do not open public store |
| B04 P1 4–10h | After B02 PASS, build Unity editor/uGUI adapter respecting Test Framework and stable JSON contract | work/unity scripts+tests; same five cases, Unsupported→UNKNOWN; store-ready .unitypackage source | CAD0 local, must not falsely claim UI Toolkit |
| B05 P1 3–6h | After B03/B04, run committed versions/OS, manual gamepad sanity if hardware exists, CI/test commands, install/uninstall/rollback, 500-control benchmark | evidence/compatibility.json plus logs/screens, matrix row status verified/blocked/unsupported | CAD0; no blanket OS support; if hardware absent note simulated only |
| B06 P1 1–2h | Recheck cheapest scoped comparable paid offer, current free full version, license/price and technical market gap | competition_refresh.md and stop gate | If price <= price-floor or free equivalent now equal, stop/pivot; no paid test |
| B07 P1 2–5h | Only passing B05, package deterministic original ZIPs, Unity .unitypackage via official validator, checksums, edit-release manifest and end-user onboarding | work/packaging release bundles, hashes, zipped license/readme; safe package installation in clean project; screenshots from actual app | CAD0 local; reject hidden deps/missing licenses; not publication |
| B08 P1 1–3h desk + external time unknown | Verify owner/Canada eligibility, tax, payout, fees, account access, rights, license, store preview; prepare public copy but do not publish | listing drafts/screens, account_gate.md and budget ledger (privacy-clean) | Login/identity or account updates require owner action; CAD0 authorized; owner decision if needed |
| B09 P1 2–5h local + approval/review latency | After QA AND explicitly scoped publication approval, publish itch and Payhip editions; submit Unity asset for review and publish only on approval; capture verified deliveries | work/packaging/releases.json per destination with URL/price/version/actual status, tax payout verification and tested delivery evidence | External actions separately permission-gated; USD/CAD account charges must be approved; no invented URLs or duplicate uploads |
| B10 P1 0.5–1.5h | Assess support burden on all selected editions and deliverable recovery; create checklist, no scheduler until authorized | work/operations/support_triage.md and workload review, expected <=4 owner hr/mo assumption | If >4h recurring owner time under conservative sales scenarios, narrow/stop; no hidden subscriptions |
| B11 P1 0.5–1h | All required releases verified or exact publication blockage documented; update lifecycle only for truthful attained stage | project.md and lifecycle evidence; command below to advance working_phase_3 only after verified build/QA/package and selected release readiness | Don't mark complete; if selected destination blocked, record dependency and keep next action |

**CLI integration after local release QA:** run python -m portfolio_manager.project_lifecycle set-phase --project "business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-004-controller-menu-replay-auditor/project.md" --phase working_phase_3 **only** after appropriate B QA/packaging acceptance, following current CLI help. A project waiting on Unity store approval can be at working_phase_3 only if factual release state and remaining distribution tasks remain explicit; it is not complete.

**Realistic critical-path estimate (hypotheses):** B00 <2h → B01 up to 8h → B02 3h if Godot passes → B03 and B04 8–18h partly independent → B05 ~3–6h → B07/B08/B09 ~5–10h plus approval lead time. About **26–47h** of active implementation/review if gates pass; store review at least five business days per S13 and could be longer. These are planning ranges, not promised lead times. Agent can parallelize Godot source vs Unity source after B02, but one record writer and one release manifest owner. If time/margin outstrips value, kill/narrow rather than expand infrastructure.

## 13. Phase C executable marketing, evidence, review and operations

**C00 (0.5h):** Read actual work/packaging/releases.json and confirm at least one live, accessible paid offer with truthful README, rights, delivery path and price. No promotion to an unpublished link; unauthorized/uncertain prior upload must be reconciled before retries. Prepare a public evidence register only containing public URLs and redacted analytics.

**C01 — itch discovery + devlog (1–2h):** Use platform’s real supported tool tags, verified live Godot/Unity links, and show exact 45s replay evidence for F4. Publish one genuine developer note, not a generic AI announcement. Draft copy: "I kept losing controller selection when a pause submenu closed, so I tested it with a reproducible scene. The capture shows focus before and after each button press. Here's the workflow and its limits [actual public listing URL]." Publish only after account/post authority; capture public URL, date/time and observed listing discovery/visits; no fake share counts. Initial status planned; after proof may be produced; publish observed only with URL.

**C02 — Payhip/owned guide (1–2h):** Write a short technically useful tutorial using original fixtures and a fair mention of the free Focus Audit Lite/gdUnit4 path, then link the *observed* paid option as an easier alternative **only if B01 demonstrated it**. Publish through approved existing channel, record public page URL/analytics if available. Draft CTA: "Download the tested Godot/Unity edition and sample failure fixtures" with actual edition limits. Initial status planned.

**C03 — real video tutorial (1.5–3h):** Capture actual plugin and free baseline in Godot, plus Unity only if supported. Include visual action→focus timeline and UNKNOWN screen, no generated screenshot pretending to show product. 60–120s, captions, honest title e.g. "Test a gamepad pause-menu focus bug in Godot [tested version]". Upload/post only with owner-approved account access; public URL, description links and watch/visit metrics if available. Initial status planned; channel-specific human gate account access.

**C04 — Unity listing discoverability (0.5–1h):** Post only true uGUI/Unity6 version/screenshot/keyword information via approved Unity publisher portal; once approved, inspect public listing and capture URL/search visibility/traffic. No false claims for UI Toolkit or physical gamepads. Initial status planned; require B09.

**C05 optional community contribution (up to 1h):** Recheck current subreddit/forum guidelines and moderation norms; post useful free diagnostic only where self-promotion is explicitly allowed and owner approved. Otherwise skip, record exclusion and use C01–04. Do not mass-message developers. No arbitrary recurring posting schedule.

**C06 first measurement/review (1–1.5h):** Use first **30 days after the last essential selected paid listing is public** or earlier once **50 qualified listing visits** are observed, whichever produces a useful sample; if neither occurs, record exposure insufficient, not 'product rejected'. Event schedule is a proposed review queue, not an active automation. Read available source-specific metrics: page impressions (if exposed), visits, downloads/trials, actual paid orders, successful deliveries, refunds, reported issues, cash paid out/held and owner support minutes. Keep revenue and net operating contribution distinct and private. Unknown metrics stay UNKNOWN; do not reverse-engineer personal buyer info. Once at least 50 relevant visits, compare conversion as an observation, not a guaranteed prior. At ~0–5 qualified visits test acquisition/keywords rather than re-engineer product; at visits/no sales test clarity, proof, audience, price within undercut interval and trust; at refunds/support improve reproducibility/compatibility first; at sales with negative contribution stop spend and investigate fees. Limit first corrective cycle to two evidence-backed 1–2h changes and CAD0 spend; only expand if actual data supports it.

**C07 complete/verifiable lifecycle (0.5–1h, after first review and authorized marketing):** Codex must independently discover and verify real public sale/download/delivery URL(s), each actual marketing placement URL, observed delivery, honest completion description and finished initial campaign review. Update record's task ledger and run:

~~~text
python -m portfolio_manager.project_lifecycle set-phase --project "business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-004-controller-menu-replay-auditor/project.md" --phase complete --description "Verified Godot and Unity controller-menu replay releases, permitted campaigns and initial observation with documented limits" --sale-url "REAL_VERIFIED_PRIMARY_SALE_URL" --marketing-url "REAL_VERIFIED_MARKETING_POST_URL"
~~~

Use **actual verified values in place of examples** and check current CLI help for multiple sale/other URLs; do not invent them. If actual sale/download cannot be accessed, or any mandatory committed listing/approved campaign/review remains incomplete, **leave project in working_phase_3**, checkpoint blocker and continue authorized work. Successful completion is a release/marketing *process milestone*, **not a sales claim**. The command writes persistent business_portfolio/completed_projects/GDM-004.json completion receipt; Codex itself commits and pushes it to main, NEVER asks owner to set Complete or manually enter links. Owner may later downgrade phase and revoke receipt; re-verification required.

**C08 operating cadence:** Once genuinely deployed, propose first compatibility check on actual engine update, support inbox after actual incidents and limited periodic financial review (e.g. monthly), but **do not claim an automated task or watcher exists** unless configured with a permitted real executor and verified scheduling record. On future sessions Codex reads the queue, checks trigger and works independently without authorizing public posting or spend. Restore from versioned ZIP on regression, suspend sales if exploitable/unsafe, preserve refund and public communications only when authorized.

### Passive/background workload model (planning hypothesis, not measured)

Use conservative *working assumption* <=4 owner hours/month total at a small sales level, **not** a user-approved strict limit. If real platform update burden exceeds this, reevaluate commercial fit. Every row includes both owner and agent work.

| Recurring function | Expected frequency, owner time | Agent/automation, access needed | Cash cost / exceptional manual work |
|---|---|---|---|
| ZIP delivery and license handoff | Per order, 0min routine; 3min allowance for unusual case | Store-native digital download; seller account and approved listing; no custom backend | Platform fee per order; manual help if provider fails |
| Refund/support triage | Illustrative 3min/order at 3 sales =9min/mo; at 12=36min/mo | Template diagnostics, reproduction fixture, optional permissioned inbox view | No fixed cash; unusual chargeback/escalation 20–40min each |
| Godot version compatibility | Per engine release/change, 20–45min/mo averaged | Codex version scan and rerun owned fixtures when resumed | Free tools if available; actual OS hardware caveat |
| Unity uGUI updates | Per engine change, 30–60min/mo averaged | Test Framework and package checks in authorized runtime | Publisher account approval/payout status if needed |
| Monitoring/incidents | 10–20min/mo | No always-on monitoring assumed; manual review queue | Emergency remediation may consume 1–3h |
| Marketing/content | 30–60min/mo after initial assets; bounded to evidence-triggered meaningful updates | Reusable verified demo capture and listing copy | No ads/paid tools approved; extra channel upkeep is not 'free time' |
| Account/financial administration | 15–30min/mo | Obtain permitted transaction totals, not customer details; tax/account decisions owner | Platform/payout/FX fees variable; tax compliance not zero |
| Supplier/data refresh | Not applicable: own offline software | None; no external data feed | No paid supplier dependency |

**Steady state estimate:** zero-sale minimum owner 1–2h/mo while checking policy/compatibility, base 3-sale ~2–3h/mo, 12-sale ~3–4h/mo if automation truly works and no major engine break. These are guesses and exclude the initial 26–47h project build. At 12+ sales plus two simultaneous engine changes or 15min/order support, the <=4h assumption is likely **violated** and should trigger simplification/pause rather than claims of passivity. At portfolio scale, each extra two-engine plugin increases shared update burden; track duplicated global admin once rather than per project.

## 14. Buyer QA, negative cases, release and compliance gates

**Observable QA gates, all must be independently recorded:**

1. B01 and B02 baseline experiments meet all positive/negative timing criteria with explicit source commit/version, not merely unit test pass.
2. F1 initial unselected; F2 unreachable via D-pad; F3 modal trap; F4 hidden/revealed focus loss; F5 input map stale: each produces correct FAIL when relevant; clean fixtures PASS; unsupported controls UNKNOWN; corrupted manifest error/UNKNOWN; escaped path rejected.
3. Each selected Godot and Unity target independently installs into clean original test project, runs same scenes twice and yields stable digest/explainable failure.
4. Accidental state-changing submit not sent into an unallowlisted real user game scene; all tests synthetic/owned. No secrets/telemetry; output redacts paths.
5. Tested Godot 4.6 and 4.7 (including documented S09 regression boundary) and Unity 6000.3 uGUI *actually run* on recorded OS. Results explicitly differentiate engine defect from product defect; no claims of console/real-device coverage without measured test.
6. Uninstall leaves project clean, license includes rights of all sources, cross-store package version/price text accurate, ZIP checksums match.
7. Practical demo can reproduce focus-loss/unknown in front of a reviewer; installation guide from scratch and uninstall instructions exist. Screenshots are authentic captures.
8. Real store accounts/Canada payout/taxes and platform content policies verified; Unity Publisher Portal validator passed (if Unity selected), review approval actually observed. Copyright and trademark of examples reviewed.
9. Listing/checkout/download from approved safe preview or legitimate authorized free test observed; no unapproved live charge. Refund/support instructions and private data policy visible.
10. All selected release destinations have observed status/URLs, not merely drafted sales pages; separate C campaign and C06 observation required for final complete.

**Canadian/tax constraints:** official CRA S18 small-supplier threshold is generally CAD30,000 worldwide taxable supplies across four consecutive quarters but must consider all businesses/associated persons and special digital rules; not legal/tax advice or exemption claim. Store merchant-of-record treatment varies; Payhip expressly handles EU/UK VAT but other taxes require setup and review. Unity payout USD and tax interview requirements are documented, but owner identity, available payout rail, regional eligibility and actual withholding must be verified in the account. No customer personal records in GitHub.

**Budget and authority failure:** If a mandatory device, package, publisher account, payment onboarding or compliance charge cannot be handled within CAD0 *authorized*, finish independent code/documentation work and produce a clearly scoped action for approval; do not silently charge. Hard cap CAD100 cumulative, not phase-scoped or per-store.

**Rollback:** retain last SHA/version and release manifests; if bad update published, use documented marketplace update/reversion mechanism with authorization, keep old verified ZIP and notify affected buyers only with appropriate consent/authorization. If an upload attempt has uncertain result, inspect provider listing before retrying. Do not roll a sale/license back by rewriting receipt evidence. Preserve actual external effects.

## 15. Exact first-session Codex runbook and state preservation

1. Open only current checkout and read AGENTS.md, business_portfolio/SCHEMA.md, PROJECT_TEMPLATE.md, business_portfolio/research/SOURCE_REGISTER.json, the new canonical project.md **entirely**, and current relevant GDM-002 and archive crosswalks without editing others. Run git rev-parse --show-toplevel; git status --short; git fetch and compare main before changes. Check another agent's coordination claims and the GDM-004 file SHA; claim a single writer; do not make a branch. If local edits differ from main, reconcile, never overwrite.
2. B00 search active+archive+all research catalogue locally to close semantic duplication gap; confirm a unique ID, valid source_ids (only already registered IDs count), canonical niche ID/path, work/.gitkeep and current generated views. Recheck live decisive source links/fees. Update source register and project frontmatter for relevant new source IDs with proper sources. Record exact changed baseline commit and a dated decision.
3. Run python business_portfolio/tools/build_browser.py; then python business_portfolio/tools/build_browser.py --check; python -m unittest discover -s business_portfolio/tests -v; python business_portfolio/tools/commercial_checks.py --portfolio business_portfolio. **These checks are first-session tasks for a writable local checkout; a chat reading remote GitHub alone must not claim to have run them.** If failures occur, fix only relevant record/source validation; don't change schema to force a PASS.
4. First five execution tasks: (a) duplicate/source preflight B00, (b) write the exact negative+clean fixture plan and identify strongest fair free baseline, (c) run native+Focus Lite+gdUnit4 baseline, including AI-assisted reasonable scripts, (d) write minimal safe Godot journey comparator and rerun same fixtures three times, (e) document exact measured result and stop/pass gate (then B02 only on PASS). No unnecessary production architecture detours.
5. Confirm budgets/permissions: CAD0 current spend and no approved new external act; never interpret repository phase as authorization. B01 can be performed locally only within current Codex execution permission; this Phase A research run has NOT done it. Save all source/tests/reports under sibling work/; evidence in work/evidence; no external live checkout.

**Persistence instruction for all future project work:** When the owner asks you to work on this project, continue autonomously through all remaining authorized tasks possible with available access and resources. Do not stop merely because a few minutes passed, after one task, a plan, or a progress update. Continue implementation, appropriate verification, evidence recording, and the next actionable task until the requested work is finished or no further authorized work can be performed. Give progress updates without ending longer work. If authorization, access, payment, another person, or external state blocks an action, complete independent authorized work first, then checkpoint and report the precise blocker and next action. Preserve completed progress, financial evidence, and uncertain external effects; respect existing scope, budget, permissions, and safety controls. Never claim unverified completion.

**Git rule:** do not create individual project branches. Fetch upstream, check existing writes, commit only reviewed files directly to main, no force pushes. Keep source-of-truth project.md and evidence one-writer. If worker claims conflict, work on a nonoverlapping subpath with the coordinator and wait on the record write safely, not an unsafe overwrite.

## 16. Resume checkpoint (Phase A actual vs future B/C)

- Phase A actual, 2026-11-19: inspected public main branch/root/niche/source register, active GDM-002, historical GDM-001/003, prior archive crosswalk and products/game-tools directory; researched native/free/paid alternatives, developer pain, cash policies, seller payouts, Canada FX/tax and distribution; wrote this conditional research record. Does **not** claim prototype or execution.
- Known Phase A limitations: big catalog/index could not be fully parsed via current connector; live private accounts, storefront sellers' orders, real installations, physical device, local Windows work and seller tax interviews not accessed. Existing registered source IDs validate submission rules, newly proposed sources not yet in register.
- Current task: **B00** local semantic duplicate/source and main reconciliation, followed by bounded B01 side-by-side.
- B00 → B01 (hard stop on failure) → B02 (Unity distinct proof) → B03/04 → B05 → B06 → B07 → B08 → B09 → B10/11 → C00–C08. All **unstarted** as of this Phase A file.
- Required compatibility rows: Godot4.6, Godot4.7, Unity6000.3 remain untested and unsupported until evidence. Godot4.4/Linux/macOS conditional; other engines excluded.
- Required sales rows: itch, existing Payhip and Unity Asset Store only *planned*; none published for GDM-004. Godot free companion conditional; all external account/publication actions awaiting authorization.
- Required marketing rows: itch devlog, Payhip guide, YouTube tutorial and truthful Unity listing optimization only *planned*; no URL, impressions or buyer analytics verified.
- Actual-money evidence: revenue null, profit null, verified paid pilots 0 (none established by this research); owner spend authorized CAD0; no observed external financial actions.
- Latest external action/side-effect state for GDM-004: **not_started** (no new ads, posts, listings, account changes, payments, outreach or scheduler). Historical repo storefront is an unrelated preexisting asset, not a fresh sale.
- Last owner approval state: unknown/ungranted for this product's public distribution and marketing.
- Exact next action: **B00** semantically search all catalogue project hypotheses for runtime controller-focus QA, preserve any existing work, register current sources with truthfully scoped IDs, run portfolio browser validation in writable checkout, then start B01 only on no-cash local Codex authority.
- Long-term completion action: executor independently verifies actual release and promotion URLs and updates lifecycle receipt, commits/pushes main. Owner is NEVER required to manually mark Complete or type URLs; absence of links leaves Phase 3 blocked, not fabricated.
- Scheduler status: **none created/verified**. Notes are a future manual/approved automation queue only.

## 17. Dated decision and objection log

- 2026-11-19 — live main inspected; active niche contains GDM-002 only; deleted GDM-001/GDM-003 intentionally not restored. Historical catalog content remains partially inaccessible through current connector.
- 2026-11-19 — reject static navigation audit as free-equivalent; Focus Audit Lite already solves an important part of the buyer job. Paid competitor USD9 is lower than many utility prices; aggressive undercut leaves thin per-order margin.
- 2026-11-19 — confirm independent Godot and Unity menu-focus pain reports but **no observed purchase**. Dynamic runtime transitions are a defensible hypothesis, not an implemented differentiator.
- 2026-11-19 — distinct post-selection disconfirmation considered gdUnit4 AI-assisted test scripts, Focus Audit paid report, Unity native framework/MenuPath QA, engine regression, existing store/payment/tax fees and low-margin marketing/support. All decisive uncertainties are explicitly gated by B00/B01/B02/B08 and real launch measurement.
- Reopen/no-go on a later change ONLY with dated new fact/measurement: new free native complete tool, proven cheaper fully capable paid equivalent, side-by-side difference below threshold, update burden >4 owner hr/month, blocked Canadian account/payout, rights failure, unaffordable required payment or no qualified exposure after bounded acquisition improvements.
- After launch do not infer failure from an unexposed listing. Continue on actual positive net contribution; improve measured acquisition/UX deficits; expand only when real sales justify new platform; pause on low-maintenance low-exposure result; discontinue on sufficient qualified visits + failed bounded improvements or when substitute/rights/cost gate collapses. Keep original release and payment evidence.

**Final integrity statement:** This one project record is Phase A research only. It is not evidence of a built/sold product, a full duplicate search through the oversized opportunity catalogue, account enrollment, a passed test, a scheduled worker, or an authorized public action. It specifies concrete, bounded B/C work and automatic truthful lifecycle completion if the later worker successfully executes them.

