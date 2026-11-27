---
{
  "schema_version": 1,
  "id": "GDM-002",
  "title": "Advanced Capacity-Aware NPC Transport System",
  "niche_id": "N-gdm-20261115",
  "niche_path": "digital-products/game-development-marketplaces",
  "record_type": "product_family",
  "origin": "current_package",
  "priority": "P2",
  "planning_lane": "queued",
  "work_state": "active",
  "project_phase": "working_phase_2",
  "commercial_validation": "unvalidated",
  "evidence_basis": "public_official_and_competitor_research_no_verified_customer_sales",
  "source_ids": [
    "GDM-WB-2026",
    "GDM-GODOT-STORE",
    "GDM-FAB",
    "GDM-ROBLOX-STORE"
  ],
  "parent_project": null,
  "related_projects": [],
  "legacy_ids": [],
  "next_action": "Investigate the editor warning and visually verify the stop marker and interactive demo, then integrate a representative real-game controller and complete rights and release QA; retain CAD0 and require owner approval for publication.",
  "last_reviewed": "2026-11-18",
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
  "marketing_lane": "direct_paid_edition_with_authentic_demo_no_paid_ads",
  "launch_gate": "local_capacity_disruption_save_restore_demo_qa_then_owner_approved_marketplace",
  "pre_sale_work_cap_hours": 6,
  "ad_test_cap_cad": 0,
  "offer_price_cad_hypothesis": 79,
  "historical_price_usd_hypothesis": "Owner workbook originally proposed USD39–79 for a Godot candidate; CAD79 is a new illustrative scenario, not an approved price.",
  "platforms_supported": [],
  "platforms_proposed": [
    "Godot 3D",
    "Godot 2D",
    "Unity 3D",
    "Unity 2D",
    "Unreal Engine",
    "Roblox",
    "GameMaker",
    "Construct",
    "GDevelop"
  ],
  "public_results": [
    {
      "label": "Seat-ledger proof and evidence limits",
      "path": "results/GDM-002/seat-ledger-proof-2026-11-17.md"
    },
    {
      "label": "Scheduled transfer fixture and evidence limits",
      "path": "results/GDM-002/scheduled-fixture-2026-11-18.md"
    },
    {
      "label": "3D movement callback experiment and limitations",
      "path": "results/GDM-002/movement-callback-proof-2026-11-18.md"
    },
    {
      "label": "DIY negative-case comparison and gate decision",
      "path": "results/GDM-002/diy-comparison-2026-11-18.md"
    },
    {
      "label": "Local technical gate assessment",
      "path": "results/GDM-002/gate-assessment-2026-11-18.md"
    },
    {
      "label": "Alternative-route feasibility comparison",
      "path": "results/GDM-002/route-comparison-2026-11-18.md"
    },
    {
      "label": "Bounded coordinator tick measurement",
      "path": "results/GDM-002/tick-measurement-2026-11-18.md"
    },
    {
      "label": "Local coordinator and demo development checkpoint",
      "path": "results/GDM-002/local-development-2026-11-18.md"
    },
    {
      "label": "Controller integration and three-version compatibility",
      "path": "results/GDM-002/controller-compatibility-2026-11-18.md"
    }
  ],
  "local_development_authorized": true,
  "technical_gate": "Owner revised 2026-11-18: comparative advantage is evidence to report, not a blocker to local development or testing; release still requires technical QA and separate owner approval.",
  "workflow_version": 3,
  "workflow_migration": {
    "previous_project_phase": "working_phase_2",
    "previous_record_path": "business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-002-capacity-aware-npc-transport/project.md",
    "migrated_at": "2026-11-21T20:17:03+00:00",
    "research_approval_inferred": false
  },
  "research_verification": {
    "phase_1": "unreviewed",
    "phase_2": "unreviewed",
    "phase_3": "unreviewed"
  },
  "delivery_window_days": {
    "minimum": 2,
    "maximum": 21
  },
  "workflow_v3_migration": {
    "previous_workflow_version": 2,
    "previous_project_phase": "working_phase_4",
    "research_approval_inferred": false
  }
}
---

## Phase A evidence and Phase B/C handoff alignment (2026-11-19)

This section is a compatibility crosswalk to the current Phase 1 research/idea megaprompt. **No fresh market validation, technical test, sales, platform approval, publication or legal clearance is claimed by this formatting update.** Existing research, source citations, plans, dated logs and assets in this record remain authoritative. Keep the current JSON `project_phase`; prior Phase 2 progress must not be erased.

### A. Idea, buyer and decision
- Preserve the original project concept, intended buyer/reader, jobs-to-be-done, scope, hard constraints and specific purchase trigger in the existing decision and buyer sections.
- Project: **GDM-002**. Real buyer-paid demand remains unverified unless independently supported in the project evidence ledger. Evaluate the fastest *credible complete offer*, not an untested prototype.
- Strongest free/paid/AI-DIY challenges: NavMeshAgent and custom/marketplace transport scripts. Recheck present-day capability and pricing before a sale decision.
- Critical adversarial proof: capacity, boarding, rerouting, crash/reload tests versus DIY baseline. Reject, narrow or stop if no differentiated reason to buy survives a fair reproducible comparison.

### B. Phase A acceptance ledger
| Gate | Source of truth | Requirement before claiming it passed |
| --- | --- | --- |
| Original idea and duplication | Existing baseline/idea/reuse sections | Same project identity; no conflicting duplicate |
| Dated evidence and substitutes | Competition/research/source sections | Verifiable sources, free alternatives, AI DIY, adverse case |
| Differentiation | Offer, technical evidence and risks | Independent meaningful buyer advantage |
| Price and CAD150/month portfolio contribution | Economics section | Net contribution scenarios after costs and refunds, not gross sales |
| Compatibility | Technical and QA sections | Real-target reproducible verification before `platforms_supported` |
| Distribution and eligibility | Distribution/legal sections | Store/publisher eligibility, fees, accounts, rights and payout requirements |
| Acquisition and ongoing marketing | Marketing/operations sections | Realistic channels, permissions, experiments and upkeep time |
| Low-touch operating fit | Support/operations/risk sections | Owner minutes/order and hours/month, exceptions and maintenance costs |

This ledger locates old evidence and identifies outstanding checks. It does **not** turn missing proof into a pass.

### C. Distinct Phase B and C matrices
- **Technical compatibility:** Unity NPC transport and proposed other engine adapters. Track proposed versus verified targets separately; cross-platform marketing does not imply compatibility.
- **Sale/distribution channels:** For each selected storefront, document seller eligibility, fees, format/policy requirements, approval state and verified publication URL. A proposed listing is not live.
- **Acquisition channels:** Different from storefronts. Document buyer discovery, reusable assets, permitted promotion, attribution metrics, recurring maintenance and channel stop rules.
- **Background-work requirements:** Estimate startup and steady-state owner workload, agent workload, manual exceptions, support, refunds, compatibility updates, channel management and monthly cash obligations. Unknown automation is not completed automation.

### D. Explicit execution handoffs and resume instructions
- **Phase 1 · Research/create:** This preserved plan is the Phase A handoff. Revisit unresolved demand, competitor, legality, compatibility and workload assumptions when evidence becomes available. Do not redo earlier completed work.
- **Phase 2 · Build/test/prepare:** Read the most recent work log before starting; continue the existing dependency-ordered tasks, build or edit only necessary work, record evidence for real-platform tests, QA and release readiness. Store new project-owned code, assets, drafts, tests and packaging under sibling `work/`; preserve and reconcile already-existing locations.
- **Phase 3 · Market/operate:** Only after actual readiness and authorization, execute selected storefront and marketing plans, capture URLs and receipts, track real net contribution, owner time and evidence-driven improvements.
- **Completed:** Only after verified Phase 3 delivery and marketing. Portfolio Manager completion requires a truthful description, a verified sale/download/delivery URL and a verified marketing URL.

**Authorization:** CAD100 is a proposed cumulative ceiling where enforced, not spending approval. New spending remains CAD0 unless separately authorized. Do not create accounts, publish, run paid ads, contact customers or spend solely because this file says to plan those actions.

**Resume checkpoint:** Read this record's latest dated checkpoint and the current `work/` tree, check shared worker assignments, identify the next unmet task and continue all independently authorized work. Never reset verified progress or invent evidence. Commit through `main` after checking for concurrent edits; no per-project branches or force pushes.

---

## Execution persistence for this project

When the owner asks you to work on this project, continue autonomously through all remaining authorized tasks possible with available access and resources. Do not stop merely because a few minutes passed, after one task, a plan, or a progress update. Continue implementation, appropriate verification, evidence recording, and the next actionable task until the requested work is finished or no further authorized work can be performed. Give progress updates without ending longer work. If authorization, access, payment, another person, or external state blocks an action, complete independent authorized work first, then checkpoint and report the precise blocker and next action. Preserve completed progress, financial evidence, and uncertain external effects; respect existing scope, budget, permissions, and safety controls. Never claim unverified completion.

# Advanced Capacity-Aware NPC Transport System — Complete Business and Implementation Plan

## 1. Executive decision and current status

**Decision: retain as a differentiated but niche, unvalidated gameplay-system candidate.** Build an engine-integrated passenger *journey coordinator*, not another general pathfinder or elevator motion asset. It handles scheduled finite-capacity vehicles, stations, queue discipline, seat allocation, transfers, missed departures, disruptions and reliable save/load with multiple NPCs.

- **Exact buyer:** small Godot simulation, colony, factory, hospital, transport, school or city-builder studios that already have NPC movement and need multiple agents to share transport resources.
- **Buying trigger:** a game design requires NPCs to queue for elevators/ferries/buses and recover from changes; wiring navigation, reservations and persistence together is costly.
- **First technical edition:** **Godot 4 3D** with an original, readable GDScript state-machine core. This selection is for the *shortest credible initial local proof*; the first paid channel must be checked independently. Do not automatically promise 2D or Unity.
- **First paid route candidate:** itch.io or existing Payhip direct checkout; the official Godot Asset Store currently accepts free listings only. Revenue must not be assumed from a free asset listing.
- **Commercial state:** no observed sales, licensed demo, tested game adapter or benchmark. The scope below is a **proposed** integration product, not a completed plugin.
- **Deciding experiment:** compare native Godot navigation links and FlowAI against a local twenty-agent/two-vehicle transport schedule. If our component saves no meaningful implementation/QA effort, reject or narrow the family.

## 2. Repository baseline, duplicate analysis and reuse

`Hi62384/Proj`, `main`, commit `6f2a420e9a1d7d5b44ec1759918e737059a6772e` inspected 2026-11-15. The existing canonical project is `business_portfolio/niches/digital-products/game-development-marketplaces/gdm-002-capacity-aware-npc-transport/project.md`, project ID `GDM-002`, niche `N-gdm-20261115`. Preserve active projects `GDM-001` and `GDM-003`; their actual jobs differ. Archive/research locations: `business_portfolio/archive/2026-11-15-legacy`, `archive/2026-11-15-taxonomy-view-v1` and `opportunity_library`. Do not create a new ID, new niche, duplicate project, or touch another chat's owned files.

The repo contains no **verified implemented GDM-002 package** in the inspected public business record. Codex must search the current *local* repo for existing game AI/transport code before making a new module; the user has unrelated Godot game work outside this business portfolio, which cannot be assumed to be licensed for commercial reuse. Reuse only code/assets with proven rights and isolation. Shared test-vector descriptions and the project's prior state-machine research are legitimate planning assets.

## 3. Reassessment of nearby products and why this one survives conditionally

The previous 33-direction game-marketplace research narrowed to three active projects; this is a revision of GDM-002 rather than a new opportunity contest. The differentiation is **complete passenger lifecycle + recovery + integration into an existing controller**. It is not "more realistic graphics" or "50,000 agents".

| Alternative | Observed capabilities (source) | Why we might still be distinct | Kill signal |
|---|---|---|---|
| Native Godot NavigationLink / signals | Navigation can connect areas; movement/behavior still belongs to game logic. [Godot NavigationLink docs](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationlinks.html) | No ready-made passenger reservations, guaranteed capacity, transfers or in-transit persistence assumed. | Buyer can add it with a trivial script. |
| Free FlowAI for Godot 4 | Moving graph areas can follow ships/elevators. [FlowAI](https://github.com/a6xdev/FlowAI) | We coordinate schedule/capacity/state on top of existing navigation. | FlowAI already has a direct equivalent passenger workflow in the required version. |
| Unity Marchline (future edition competitor) | Deterministic crowds, door capacity, queues, multi-storey, save/load. [Unity listing](https://assetstore.unity.com/packages/tools/behavior-ai/marchline-rts-pathfinding-crowd-navigation-400596) | NOT a claim of low Unity competition. A port would need unique vehicle/passenger itinerary functions. | Its use in the buyer's game is already sufficient. |
| Generic elevator/moving-platform scripts | Move between floors and synchronize doors. | Do not generally model shared queues, transfers and recovery. | A moving platform actually meets this buyer's full use case. |
| Large all-in-one city simulation toolkit | May already provide vehicles/riders. | Our system integrates with *existing* NPC AI rather than replacing it. | Adapter cost exceeds DIY or toolkit adoption. |

**Market evidence limit:** a developer forum describes elevator wait/board/exit needs; this is an engineering problem signal, not a measured paid market. Unity Marchline proves *competition*, not our demand. No credible number of Godot buyers, conversion rate, or unit sales is known. Godot-first is a **technical experiment**, subject to paid-route/customer reachability.

## 4. Buyer/job-to-be-done and reasons not to purchase

Buyer A is developing a hospital/office building with multiple floors and NPCs sharing lifts. Buyer B has a colony simulation with ferries/buses on timed routes. They need reliable agent progression: request route → wait for transport → reserve capacity → board exactly once → ride → transfer/exit → arrive or recover with an understandable reason. The system should not demand replacement of their existing movement or quest AI.

Nonbuyers: games with one player-triggered lift, games without persistent NPC populations, teams already running a purpose-built passenger coordinator, developers who need road vehicle physics/networked traffic from day one, customers unable to provide stable agent and stop identifiers.

**Why buy versus AI?** A quick AI-generated queue can work in one demonstration, but event ordering, last-seat races, cancellations, save/restore at every transition and interoperable diagnostics require many tests and maintenance. The product only deserves a price if its tested implementation and integration API measurably reduce engineering and debugging effort.

## 5. First useful commercial edition — no overbuilding

### Must ship

1. One complete Godot 4 3D addon with a transport graph (`Stop`, `Service`, `Vehicle`), deterministic scheduler, seat ledger, station queues and agent journey state machine.
2. A simple integration API: register stops/vehicles, request/cancel journeys, notify a boarding/movement callback, receive transport events and serialize/restore state.
3. Configurable small multi-stop elevator/ferry/bus *behavior presets* using the same capacity engine—not simulated traffic physics or a full vehicle model. At least one reliable moving 3D platform demo.
4. End-to-end journey from external NPC navigation through wait/board/ride/transfer/arrival, with clearly defined delays, failures and rerouting.
5. Reproducible save/load snapshots including mid-queue and mid-boarding state, deterministic event IDs and a debugger that explains every agent's waiting reason.
6. Bounded performance fixture: initially **20 agents, two capacity-limited vehicles and one transfer**, then measure on a pinned PC and Godot version. Do not advertise capacity larger than actually tested.
7. Source, demo project, API reference, integration recipes for two movement-controller patterns, troubleshooting guide, supported versions, licensing and QA report.

### Excluded from first sale

Unrestricted multiplayer replication, Roblox server economies, dynamic rail/road construction, physics/traffic simulation, all movement controllers, unrestricted train timetables, 10,000 agents, procedural map generation, visual editors for every topology, universal engine compatibility and fully autonomous crowds. These are separate products/features requiring proven demand. Animations and 3D meshes are replaceable demonstration assets; do not promise high-end artwork.

| Engine | Candidate edition / market feasibility | Proposed next action |
|---|---|---|
| **Godot 4 3D** | **Chosen for local proof**, direct paid sales; official Godot store free-only at this review. | Demonstrate actual capacity/transfer/recovery and verify paid-channel discovery. |
| Godot 2D | Different movement signals and navigation integration. | Port only after demonstrated 3D traction or stronger independent buyer evidence. |
| Unity 3D/2D | Marchline and many crowd/lift products; competition substantial. | Evaluate specific *vehicle itinerary* gap, not a broad navigation rewrite. |
| Unreal Engine | Blueprint/C++ plugin and Smart Objects/lift products. | Re-assess against Fab's current paid systems before any port. |
| Roblox | Server-authoritative reservations, replication, disconnections and abuse cases. | Independent edition; not a trivial module conversion. |
| GameMaker | 2D room/path/instance model, save compatibility to test. | Needs viable SDK and marketplace pathway. |
| Construct / GDevelop | Event/extension architectures and distribution rules differ. | Feasibility/reachability only; reject when integration is costly. |

A shared **behavior contract and test fixtures** can be reused; cross-engine source may need complete reimplementation. Do not count port listings as sales or separate businesses.

## 6. Competition and evidence ledger

| Source | Verified information / limitation | Review |
|---|---|---|
| [Godot forum elevator pathfinding question](https://forum.godotengine.org/t/pathfinding-with-elevator-platform/45444) | Documents a concrete wait/board/ride/exit problem, **not** willingness to pay. | 2026-11-15 research review |
| [FlowAI repository](https://github.com/a6xdev/FlowAI) | Moving pathnode graph/area can follow lifts or ships; no claim that its listed capabilities are incomplete without testing. | 2026-11-15 |
| [Godot NavigationLink](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationlinks.html) | Native navigation links are baseline primitives. | 2026-11-15 |
| [Unity Marchline listing](https://assetstore.unity.com/packages/tools/behavior-ai/marchline-rts-pathfinding-crowd-navigation-400596) | Advertises capacity-limited passages, queues, cross-floor routing and saved queue state; high overlap for a Unity edition. | 2026-11-15 |
| [Godot official store FAQ](https://docs.godotengine.org/en/stable/community/asset_store/faq.html) | Paid assets not available on official store currently; future plans are not current revenue. | 2026-11-15 |
| [Payhip pricing](https://payhip.com/pricing) | Free seller plan lists 5% platform fee *plus separate card/PayPal processor fees*. | 2026-11-15 |

These sources do not establish how many people would purchase *this* system. Search current Godot/itch.io competitors again immediately before a paid listing. If a complete existing passenger transport addon already satisfies this specification for less, stop rather than copy it.

## 7. Competitive baseline and bounded proof without interviews

**Owner revision, 2026-11-18:** The comparative test is informative, not a stop condition for local development or testing. Preserve and report the observed DIY overlap and do not claim an advantage without evidence. All release-quality checks and separate owner approval for publication remain required.

Construct **two** demos in the same original Godot project. A baseline uses NavigationAgent/NavigationLink plus a minimal custom queue script; the proposed addon uses the transport core and two different movement-controller adapters. Record how many edge cases fail in baseline, implementation time, code modification burden and repeatable restart behavior. The original proposed differentiation criterion was more reliable scheduled reservation and mid-ride save/recovery with less integration effort; this remains an evidence standard for any such claim, not a blocker to local development. No survey or team evaluation is required.

**Original risk signals (no longer a mandatory stop for local development under the owner revision):** if adding a FIFO array to a moving platform solves all target uses at lower complexity; if save/restore is inconsistent; if controllers need invasive rewrites; if paid checkout/discovery cannot be established affordably; or if support effort is disproportionate. Production polish alone does not rescue a missing market.

## 8. Business model and first CAD150/month economics

**Proposed direct digital download:** CAD79 initial price experiment, one-time engine-edition license with versioned updates under a stated support policy; license and actual checkout price require owner approval. Prefer use of the repo's existing store infrastructure only if license/redistribution and merchant-of-record terms work. No subscription, paid backend or per-seat billing infrastructure in v1.

**Illustrative unit math:** Payhip free seller fee is currently 5% (source above). *Assume*, do not claim as sourced, payment processing 3% + CAD0.35 per completed order, refund allowance 5% of gross, CAD0 hosting/ads/new tooling. Per completed CAD79 order, provisional contribution before owner labor = `79 × (1 - 0.05 - 0.03 - 0.05) - 0.35 = CAD68.38`. Actual payment provider fees, FX/tax and refund rules must be checked.

| Monthly scenario | Hypothetical paid orders | Gross CAD | Fee/reserve total CAD | Contribution CAD | CAD150 portfolio target share |
|---|---:|---:|---:|---:|---:|
| Stress | 0 | 0.00 | 0.00 | 0.00 | 0% |
| Base hypothesis | 2 | 158.00 | 21.24 | 136.76 | 91.2% |
| Upside hypothesis | 5 | 395.00 | 53.10 | 341.90 | 227.9% |

**Three orders** in a month would yield approximately CAD205.14 under these unverified assumptions; one successful month is not automatically recurring. With CAD0 upfront, the first positive order is nominal cash break-even before owner labor. If a planned CAD60 cost were separately approved, break-even would require one paid order at the assumed unit contribution. If refund/processing/marketplace total variable deductions rise to 25% plus CAD0.35, each CAD79 sale yields CAD58.90 and three orders are still needed for CAD150. A one-order month yields CAD68.38, so the product can contribute partially toward the **portfolio-wide** goal.

**Effort hypothesis:** 35–75 focused AI-assisted engineering and QA hours; 2–6 hours of owner review/approval; after release ~1–3 hours/month maintenance plus incident support (not observed). Worst-case revenue is CAD0 while engineering and maintenance consume time. If support averages 2 hours *per* CAD79 sale, it may be economically unattractive even with positive cash contribution. Do not hide owner labor in a positive margin number.

## 9. Distribution, listing drafts and organic launch

**Primary paid route:** itch.io/direct download or existing Payhip checkout after owner-approved account/licensing setup. **Do not** place the full paid source in the official free Godot store. A genuinely free, separable tutorial/demo is an optional discovery channel *only if its license and the official store rules are compatible*; don't give away paid functionality unintentionally. Fab/Unity Asset Store are relevant only once genuine engine editions exist and qualify under those stores.

**Qualified search terms to test (not measured search volume):** `Godot NPC elevator queue`, `Godot ferry NPC boarding`, `Godot passenger transport simulation`, `Godot AI transport network`, `Godot save queue lift addon`.

**Draft title:** *Passenger Transit Coordinator for Godot — Queues, Capacity, Transfers and Save/Load*.

**Draft teaser:** *Let NPCs take scheduled lifts and transport without overbooking, duplicate boarding, or losing their place after a save/load. Integrate with your movement controller; visualize the journey and recover from delays.*

**Main demo storyboard:** 20 differently colored NPC markers compete for two transport vehicles; an NPC misses a transfer; a vehicle goes out of service; midway through boarding, save and reload; HUD shows occupancy, queue length and journey state; replay final outcome and show no duplicate seat. Capture real software footage only after QA. Provide an original sample Godot project, integration gif/video, explanatory diagrams and an API checklist. Licensing must not overpromise multiplayer or all NPC controller types.

**Launch sequence:** build scenario replay → capture authentic demonstration → make paid sample and setup docs → prepare product cover/thumbs → compare direct checkout usability and store discoverability → owner-approve any account/publication actions → publish → record genuine page visits and sales → adjust pricing or demo based on observed bottleneck. Ads remain CAD0 absent later authorization and conversion evidence.

## 10. Architecture: pure transport rules plus engine adapters

**First edition design:** GDScript for Godot 4 with a deterministic simulation tick and minimal Node-facing adapter. Navigation and rendered movement remain owned by the customer. The core must not depend on scene hierarchy, 3D animations or external networking; use explicit callback events from the controller.

```text
Proposed source tree (not yet built):
products/game-tools/capacity-aware-npc-transport/
  addons/transit_coordinator/plugin.cfg
  addons/transit_coordinator/core/{transit_graph,route_planner,schedule_clock}.gd
  addons/transit_coordinator/core/{seat_ledger,queue_policy,journey_machine,event_journal}.gd
  addons/transit_coordinator/contracts/{transport_config,journey_result,snapshot_schema}.gd
  addons/transit_coordinator/adapters/{movement_adapter_3d,navigation_link_adapter}.gd
  addons/transit_coordinator/editor/{transit_inspector,network_gizmo,config_validator}.gd
  demo/{project.godot,worlds,scenes,scripts,assets}
  tests/unit/{ledger_test,queue_test,planner_test,snapshot_test}.gd
  tests/integration/{lift_transfer_test,disruption_test,controller_adapter_test}.gd
  tests/fixtures/{two_vehicle_trace,restoration_trace,disabled_service_trace}.json
  docs/{quickstart,api,controller_adapters,save_restore,version_support,limitations}.md
  tools/{run_fixture.py,package.py,verify_release.py}
  LICENSE, CHANGELOG.md, THIRD_PARTY_NOTICES.md
```

**Ownership:** `transit_graph` is the source of stop/service edges and stable IDs. `route_planner` consumes graph + timetable and proposes legs but never allocates seats. `seat_ledger` is the **only seat allocator**, synchronized on one authoritative simulation tick. `journey_machine` orchestrates agent state; `event_journal` deduplicates each transition; `snapshot_schema` persists exact state; adapters issue/acknowledge movement but cannot change core occupancy. View/UI are read-only projections and never own reservations.

**Configuration requirements:** stable `stop_id`, `service_id`, `vehicle_id`, `agent_id` strings; versioned service schedule, stop order, capacity >=1, dwell/departure times, queue discipline, deadlines and required agent movement callbacks. Validate missing endpoints, duplicate identifiers, nonpositive capacity, cyclic zero-time schedules, unreachable legs and timezone/unit mismatch. Simulation time is integer ticks, not wall-clock milliseconds.

## 11. State machine, schemas, algorithms and invariants

**Journey states:** `requested → routing → walking_to_stop → queued → reserved → boarding → onboard → alighting → transfer_waiting → completed`; side transitions to `rerouting`, `cancelled`, `failed`. Event IDs are stable `run_id:tick:vehicle_id:sequence` or another collision-safe deterministic scheme. Saved state includes current leg index, queue ticket, seat claim, boarded vehicle, last processed event and schedule tick.

**Immutable invariants:** for every vehicle, `0 <= occupied_seats <= capacity`; no agent in two vehicle seats; no agent simultaneously marked queued and onboard; a seat claim is owned by exactly one agent; reprocessing the same event ID changes nothing; cancellation cannot create a later boarding; snapshot load reconstructs identical eventual state under identical inputs.

**Public proposed API:**

```gdscript
var journey = transit.request_journey(agent_id, destination_stop_id, options)
transit.cancel_journey(journey.id)
transit.register_vehicle(vehicle_id, route_id, capacity)
transit.notify_arrived_at_stop(agent_id, stop_id)
transit.acknowledge_boarded(agent_id, vehicle_id, event_id)
transit.acknowledge_disembarked(agent_id, vehicle_id, event_id)
var state = transit.serialize_snapshot() # versioned data, NOT scene nodes
transit.restore_snapshot(state)
# Signals: journey_changed, boarding_requested, vehicle_departed, service_disrupted
```

All APIs above are **proposals**, not confirmed GDScript implementations; specify true Godot types once engine version is pinned.

**Route planning (bounded deterministic Dijkstra/time-dependent graph):** a node is `(stop_id, arrival_tick)`; edges include walk or service departure with wait and ride time; compute earliest feasible itinerary given current schedule; tie-break by stable service/stop ID. Before boarding, journey state machine asks ledger for seat claim. If no capacity, queue by `(priority_class, request_tick, agent_id)` to avoid nondeterministic race. A missed departure invalidates only that leg and triggers replanning; do not strand other agents. For large recurrent schedules, cache schedule indexes only after correctness passes.

```text
on_tick(T):
    collect input events; stable_sort by (tick, priority, vehicle_id, agent_id, event_id)
    ignore event_id if processed; emit typed 'duplicate_event_ignored'
    advance departures/arrivals and close boarding windows
    for vehicle: allocate free seats FIFO to eligible waiting agents
    for boarding ACK: verify active reserved seat+same vehicle, then commit occupancy once
    for cancellation or disruption: release claims, journal cause, reroute affected agents
    publish immutable state view and diagnostic reason codes
```

**Atomicity rule:** one authoritative event loop owns ledger writes; no thread can directly mutate seats. A boarding reservation is a *claim*, not occupancy; occupancy commits on acknowledgment. If a callback never arrives by timeout, release claim safely. If boarding animation finishes after cancellation, reject stale ACK and request adapter recovery. A save taken between reservation and animation persists a clearly identified `reserved` or `boarding` state and restores it once. Restore validates graph revisions and runs a migration function only for explicitly supported snapshot versions; unsupported versions return an error, not a quietly reset world.

**Proposed snapshot excerpt:**

```json
{
  "schema_version": 1, "tick": 240, "graph_version": "demo-v1",
  "vehicles": [{"id":"lift-a", "capacity":2, "occupied":["npc-02"], "claimed":["npc-03"]}],
  "journeys": [{"agent":"npc-03", "state":"boarding", "vehicle":"lift-a",
                "current_leg":1, "queue_ticket":"ticket-37", "last_event":"demo:240:lift-a:4"}],
  "processed_event_ids": ["demo:239:lift-a:3"]
}
```

The example is a schema sketch; snapshots must never trust the `occupied` list without enforcing capacity, uniqueness and version validation. Use compact event retention with a proven safe replay window; do not store unbounded event IDs forever in a production game.

**Performance target:** first demonstration 20 NPCs/two vehicles with deterministic replay. Record elapsed simulation time per tick, queue length, outstanding reservations and allocation operations on a specified Windows PC and pinned Godot build. No 1,000-agent performance claim until a real measured fixture establishes it.

## 12. Dependency-aware engineering backlog

Proposed file locations are not existing implementations. Estimates are focused engineering hours with substantial uncertainty. Work may proceed locally without human interviews if owner/normal Codex tool permissions allow. No file may be simultaneously written by unrelated chats without coordinator ownership.

| ID | Hours est. | Depends | Action and precise deliverable | Verification / stop rule |
|---|---:|---|---|---|
| T01 | 1–3 | None | Pin available Godot 4 3D version; assemble native NavigationLink + FlowAI comparison in `research/free-baseline.md`. | Document exact native capabilities; drop if already turnkey. |
| T02 | 2–4 | T01 | Create synthetic 20-agent/2-vehicle scenario with time ticks, routes, stops and deterministic input traces in `tests/fixtures/`. | Two routes incl transfer, no third-party assets, legal to distribute. |
| T03 | 3–5 | T02 | Implement graph and config validators (`core/transit_graph.gd`, `contracts/transport_config.gd`). | Duplicate IDs, unreachable endpoints, invalid capacity/schedules rejected. |
| T04 | 4–7 | T03 | Implement single-writer `seat_ledger` and FIFO policy; independently seeded unit fixture. | Simultaneous final-seat requests never overbook; canceled claims release once. |
| T05 | 4–7 | T03–T04 | Implement deterministic `journey_machine` and `event_journal` with typed reason codes. | Same seed/input trace = same state hash and event sequence. |
| T06 | 4–7 | T03–T05 | Implement schedule/route planner with time-dependent transfers and disruption rerouting. | Missed connection is handled; impossible itinerary returns explicit no-route. |
| T07 | 4–7 | T05–T06 | Add 3D movement callback adapter, lift/boat motion reference and two controller styles. | Can replace demo controller without rewriting core; no lost/duplicated rider. |
| T08 | 4–6 | T05–T07 | Versioned snapshots, migrations, hash fixtures, restore halfway through boarding. | Snapshot restored with identical ledger/journey state and no ghost seats. |
| T09 | 3–5 | T07–T08 | Inspector gizmo and debug HUD for queue order, occupancy, current leg, wait reason. | Every waiting NPC exposes a reason; no editor crash on missing graph. |
| T10 | 3–5 | T08–T09 | Build Godot 3D sample and reproduce at least 12 failure traces; measure performance. | No invariant violation; report actual FPS/tick and tested hardware. |
| T11 | 2–4 | T10 | Baseline comparison vs native/FlowAI; install from fresh project. | Record measured outcomes and limitations; no unverified superiority claims. |
| T12 | 3–6 | T10 and documented T11 | Prepare a local addon package, original demo, docs, licence, QA and release manifest. | Works after uninstall/reinstall; examples and version matrix honest; publication remains separately owner-approved. |
| T13 | 1–3 | T12 | Draft genuine demonstration video script, storefront title/FAQ, page, customer support guide. | No claims without actual video/test output. |
| T14 | Variable | T13 + authorization | Publish through eligible direct/marketplace channel, verify checkout/delivery once permitted. | Real listing URL and delivery evidence only. |
| T15 | 0.5–2/review | T14 | Observe actual page visits, orders, refunds and support; choose improve/pause/expand. | Keep financial and work states separate. |

**Critical path:** T01→T02→T03→T04/T05→T06→T07→T08→T10→T11→T12→T14. T09 UI and T13 listing copy can proceed in owned files in parallel after stable APIs. Estimated **~35–75 focused engineering hours**, not a guaranteed elapsed duration. The initial demo, not a full city-builder, is the quality milestone.

## 13. Test fixtures and release-blocking QA

| Fixture / situation | Expected result |
|---|---|
| Two agents request the final seat during one tick | Exactly one successful claim; second remains queued with reason `capacity_full`. |
| One agent cancels while reserved | Claim released once; late boarding callback rejected; next in queue eligible. |
| Boarding ACK duplicated after restore | Only one occupancy transition, one ticket used, one journal event committed. |
| Vehicle departs before another agent arrives | Missed-trip condition; new feasible route or explicit failed/unreachable status. |
| Vehicle breaks down mid-ride | Rider transitions to defined waiting/rerouting/failed, never silently vanishes. |
| Stop becomes inaccessible during transfer | Replan or terminate with reason, preserve other trips. |
| Agent changes destination twice | Older request canceled; no leaked queue ticket or seat. |
| Save in `boarding` and reload | Identical seat/queue ownership, eventually same state under same replay. |
| Restore snapshot with `occupied > capacity` | Reject invalid snapshot; do not spawn overlapping passenger state. |
| Two controllers move at different speeds | Core remains correct; adapters correctly signal stop arrival/board/exit. |
| Cyclic route with no service | Planner terminates bounded; returns explicit no-route, no infinite loop. |
| Scene closed while NPC awaiting | Cleanup releases reservations and emits diagnostics. |

**Run guidance (after implementation):** `godot --headless --path <DEMO_PROJECT> --script <TEST_RUNNER_SCRIPT>` and `godot --headless --path <DEMO_PROJECT> --quit-after <TICKS>` are **proposed** examples; Codex must verify the installed Godot command-line flags and actual script paths. Measure on an identified Windows workstation before making speed claims. Require all deterministic input traces and a clean fresh import to pass before sale.

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

**Release-blocking acceptance:** no overbooking, duplicate boarding or corrupted save/restore in 12 negative traces; a clean demo project installs and runs on the pinned Godot version; a documented controller adapter works with another movement implementation; any claimed performance is measured and labelled.

## 16. Post-release operations and customer support

- Publish a clear supported version matrix; request *reproducible, redacted* bug reports rather than sensitive project archives. Disclose current limitations; do not promise unlimited bespoke integrations at the base price.
- Triage: verify report/version → reproduce on minimal fixture → classify `supported bug`, `integration`, `unsupported use`, or `feature request` → provide workaround/patch → regression-test all prior fixtures → version release. Preserve previous packages for rollback.
- Maintenance cost is uncertain. Reserve an illustrative 0.5–2 hours/month per product plus 0.25–1 hour per meaningful support incident, **not** a measured commitment. If the real load materially exceeds this, revise economics, reduce supported configurations or pause expansion.
- Collect no product telemetry by default. Use actual accessible marketplace analytics and private support records without placing personal customer data in this public project record.

## 17. Performance measurement, portfolio decisions, and future products

Measure after actual publication: direct store product views where available, download and demo completion counts when legitimate, orders, price/discount applied, real payment fees, refunds, bug categories, supported Godot versions, time spent helping users. Record the date, currency, fee deductions, refunded transactions, hours of support and net contribution in the appropriate authorized private financial systems; report only non-sensitive aggregates publicly. A pageview is not a sale and a listing favorite is not a verified purchase.

Decision heuristics (not statistical proof): **continue** if actual positive net contribution and low support persist; **improve** when a specific demo, pricing, installation or discovery weakness can be addressed in a bounded update; **expand** only if there is proven traction plus a justified additional engine/channel; **pause** if exposure is tiny and costs are near-zero; **discontinue** if a free/native passenger queue example is sufficient for the identified buyer, an already available paid addon provides the same end-to-end function, or integration into ordinary NPC controllers costs more than DIY. Do not infer a bad idea solely from zero sales without evidence that qualified customers saw it.

## 18. Adversarial review and kill conditions

The strongest reasons the business could fail are: the target market for intricate passenger AI may be small; the first paid channel may be discoverability-poor; free FlowAI/navigation tools and paid Unity crowd systems already overlap; open-ended support requests could consume the revenue. Before implementation, run a *free/AI DIY challenge*: reproduce the promised result using native engine tools, a public alternative and a short AI-assisted script. Record setup time, bug count and diagnostic quality for the same fixtures. If the new tool has no real advantage, cut the scope or stop—no rebranding a duplicate as a new project.

Other fail conditions: insufficient legally permitted distribution, accuracy/privacy defects, platform/SDK changes exceeding support economics, or the release depending on paid/forbidden services outside the authorized budget. No human interviews or paid pilots are mandatory. Technical QA and official permission gates remain mandatory.

## 19. First-session Codex handoff — ready for local work

**Open first:** repository root `AGENTS.md`, `business_portfolio/SCHEMA.md`, `PROJECT_TEMPLATE.md`, this exact canonical file `business_portfolio/niches/digital-products/game-development-marketplaces/gdm-002-capacity-aware-npc-transport/project.md`, `business_portfolio/research/SOURCE_REGISTER.json`, the selected niche's `NICHE.json`, and `docs/PORTFOLIO_MANAGER_WORKFLOW.md`. Inspect other active GDM IDs and the archives; do not assume their project folders are available for modification. Keep unrelated projects untouched.

**First session steps (local work, no commercial actions):**

1. `git status --short` and `git rev-parse HEAD`; reconcile uncommitted or newer work and guard the project record from conflicting writers.
2. Confirm `GDM-002` ID/niche/source IDs and source register; keep all existing evidence links and work history. Regenerate the browser only after canonical content changes.
3. Execute T01–T05 locally without waiting for GDM-001: pin Godot version, build the two-vehicle synthetic route fixture, validate graph/contracts, enforce atomic capacity ledger, then implement a deterministic journey/event core. Compare results immediately with native NavigationLink baseline, not customer interviews.
4. Run the small fixture(s) immediately, capture exact command, exit status and test outputs. Identify which results are observed rather than planned.
5. Record the task state and a specific next action in the canonical record, without claiming that a plan means implementation is done. If the root workspace differs from the verified remote repository, adapt carefully instead of clobbering local work.

**On future import/update**, the existing non-sensitive source IDs are registered. New URLs in §21 are *not* automatically registered: Codex must add evidence entries to `business_portfolio/research/SOURCE_REGISTER.json` only when used as cited source IDs, then update `source_ids`. Run `python business_portfolio/tools/build_browser.py`, `python business_portfolio/tools/build_browser.py --check`, `python -m unittest discover -s business_portfolio/tests -v`, and `python business_portfolio/tools/commercial_checks.py --portfolio business_portfolio` from repo root **where tools exist**. Check optional budget math separately. Do not invent tests that could not run.

## 20. Resume checkpoint and work log

- **Completed with evidence:** detailed existing GDM plan read from the remote repo; current official/public source and product-feature review; this more specific architecture, test plan, financial *hypotheses*, launch drafts and Codex work breakdown. No source code, verified engine integration, published listing, confirmed sale, private buyer interview or paid market validation was generated by the document revision.
- **Work state:** `planned`; **commercial validation:** `unvalidated`; **actual revenue/profit:** `null`; **authorized spending:** CAD0; **external effects:** `not_started`.
- **Current task:** capacity-limited passenger journey system — begin the first no-cost implementation/feasibility task once the owner separately authorizes local development in the normal Codex workflow.
- **Remaining checklist:** [ ] baseline comparison; [ ] working core; [ ] failing/negative fixtures; [ ] engine adapter; [ ] real package and installation; [ ] truthful demo; [ ] policy/rights check; [ ] publication authorization; [ ] real sales/maintenance review.
- **Owned deliverables:** this planning file only; no product code, fixture package, test output, or listing exists. Proposed future artifact paths in this file do not yet exist.
- **Original source revision:** `6f2a420e9a1d7d5b44ec1759918e737059a6772e` (`main`, inspected 2026-11-15); original frontmatter IDs, priority, status, related links and existing research continuity preserved. The local repository record was inspected and reconciled during the 2026-11-15 merge; project IDs and paths were retained.
- **History:** original 2026-11-15 candidate selection and planning are preserved conceptually, including the original competing-product research and proposed platform editions. This revision **removes mandatory interviews and paid-pilot blockers** and replaces them with local comparative proofs and marketplace-as-validation, without falsely changing the commercial state.
- **Next concrete action:** Execute T01–T05 locally without waiting for GDM-001: pin Godot version, build the two-vehicle synthetic route fixture, validate graph/contracts, enforce atomic capacity ledger, then implement a deterministic journey/event core. Compare results immediately with native NavigationLink baseline, not customer interviews.

### Work log

- 2026-11-15 — Local repository reconciliation before replacement: Pre-replacement local record was planned/unvalidated; its latest action already called for a synthetic local prototype. No product source, engine integration, fixture results, customer evaluation, outreach, spending, or external action was present. The attachment supplies the more specific Godot 4 prototype plan; this carries forward the no-code/no-external-progress checkpoint without retaining the superseded research-first plan.

- 2026-11-15 — Previously recorded: project family identified from game-development marketplace research; candidate engine list and launch risks captured, without product implementation or sales.
- 2026-11-15 — Current revision: expanded the execution-ready specification and removed research-interview/paid-pilot gates. This file is an updated planning artifact, not proof of completed tasks.

## 21. Dated source and registration handoff

The `source_ids` in the strict JSON frontmatter remain restricted to IDs already in the repository's `SOURCE_REGISTER.json` (verified from GitHub). All additional public URLs used below are **in-file evidence** until Codex registers them. Each source should be rechecked at the time of listing or toolchain/version selection.

| Source / proposed register ID | Fact supported, limits | Date checked |
|---|---|---|
| `GDM-WB-2026` (registered) — owner workbook attachment | Earlier concept selection, not verified sales. | 2026-11-15 |
| `GDM-GODOT-STORE` (registered) — https://docs.godotengine.org/en/stable/community/asset_store/faq.html | Official Godot store cannot charge yet. | 2026-11-15 |
| `GDM-FLOWAI-2026` — https://github.com/a6xdev/FlowAI | FlowAI supplies moving navigation graph support; partial substitute. | 2026-11-15 |
| `GDM-GODOT-LINK-2026` — https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationlinks.html | Native navigation links need evaluation as free starting point. | 2026-11-15 |
| `GDM-MARCHLINE-2026` — https://assetstore.unity.com/packages/tools/behavior-ai/marchline-rts-pathfinding-crowd-navigation-400596 | Strong Unity competitor with capacity/queues/multistorey/saved state. | 2026-11-15 |
| `GDM-PAYHIP-2026` — https://payhip.com/pricing | Direct checkout free tier 5% plus separate payment processing. | 2026-11-15 |
| `GDM-ROBLOX-STORE` (registered) — https://create.roblox.com/docs/production/creator-store | Conditional future Roblox model/plugin store eligibility; no Roblox edition built. | 2026-11-15 |
| `GDM-FAB` (registered) — https://dev.epicgames.com/documentation/fab/publisher-get-started-in-fab | Fab rules matter only for independently implemented Unreal edition. | 2026-11-15 |

**Evidence limits:** competitors' existence/prices/features are not proven sales; official revenue shares are gross-before-other-cost rules; market size, traffic, conversion and support time have **not** been measured for this offer. The historical owner workbook is research context, not a public redistributable asset. No source has been used as evidence of this project's own paid transactions.


### 2026-11-17 local proof checkpoint

- Built an original Godot 4.7.2 GDScript FIFO seat/queue proof at `products/game-tools/gdm-002-transit-proof/`. The headless test passed with exit 0; see the public result for commands, observed checks and engine log warnings.
- No schedule, 3D scene, transfers, persistent disk save, performance measurements, comparable baseline, paid package or publication is complete. Commercial validation remains unvalidated; no spending, sales or other external commercial effects were observed.
- Next: build and test the scheduled 3D two-vehicle scenario with transfer and save/load, then compare the same trace and integration effort with native NavigationLink and FlowAI.


### 2026-11-18 local feasibility checkpoint

- Added a fixed 20-passenger, two-vehicle scheduled transfer fixture and trusted local disk snapshot test. Godot 4.5.1 headless passed with 80 events; a primitive 3D view also started headlessly. See the public result for exact evidence, warnings, and limitations.
- The view has not been visually validated; the fixture does not use the earlier seat ledger or implement a general coordinator, disruption recovery, real movement callbacks, or a same-trace native/FlowAI comparison. Commercial state and CAD0 authorization remain unchanged; no external commercial effects occurred.
- Next: validate the 3D view, integrate movement callbacks and compare the same trace and integration effort with native NavigationLink and FlowAI before judging differentiation.


### 2026-11-18 movement callback checkpoint

- Added a separate single-vehicle callback experiment using the earlier seat ledger and a simple moving Node3D controller. Four headless scripts passed on Godot 4.5.1; the public result records exact coverage and limitations.
- The scheduled two-vehicle fixture remains separate, cancellation does not recover the moving node, and no comparative baseline or commercial validation has been achieved. No spending or external commercial effect occurred.
- Next: connect the movement callbacks to the scheduled transfer fixture, test save/load during boarding, then compare native NavigationLink and FlowAI on the same trace.


### 2026-11-18 ledger-backed transfer checkpoint

- A fixed two-leg schedule now uses seat ledgers and explicit boarding acknowledgments. Its headless test reproduces the prior 80-event trace and resumes identically from a trusted disk save during boarding; see the movement callback result for scope and limitations.
- The 3D mover is not connected to that schedule. Unique callback tokens, missed-boarding recovery, disruption and a native/FlowAI comparison remain unimplemented. No spending, publication or other commercial effect occurred.
- Next: connect the mover, add callback identity and recovery, then compare the same trace and integration effort against native NavigationLink and FlowAI.


### 2026-11-18 scheduled movement and native link checkpoint

- Added per-departure boarding tokens, version 2 snapshots and a synthetic test wiring 20 Node3D movers to the fixed two-leg ledger schedule. A separate native NavigationServer3D primitive test verified linked and disconnected paths. Seven local Godot tests passed; the public result records exact scope and warnings.
- The mover test resets positions and does not simulate actual vehicle travel or save mover state. Timeout and physical recovery, visual inspection, full native and FlowAI same-trace comparisons and measured integration effort remain outstanding. No commercial action or spending occurred.
- Next: implement recovery, validate the 3D view and build equivalent native/FlowAI baselines before deciding differentiation.


### 2026-11-18 missed-boarding checkpoint

- Unacknowledged boarding claims now return to the queue in FIFO order at the end of the fixture departure window. The test confirms old-token rejection and next-window acceptance. Physical repositioning and full disruption recovery remain outstanding; see the public result for details.
- Next: add physical recovery, validate the 3D view, and compare equivalent native and FlowAI scenarios. No spending or external commercial effect occurred.


### 2026-11-18 visual and recovery checkpoint

- Inspected the original synthetic projection at ticks 0 and 6 and improved camera framing and labels. A separate adapter test returned a partially moved passenger to its waiting point after a missed departure and boarded it on a subsequent departure.
- Fetched FlowAI source into an isolated ignored project and tested a three-node route. It passed with shutdown resource warnings; neither FlowAI nor native NavigationLink has been tested on an equivalent passenger trace. The displayed projection remains independent of the callback-ledger scenario. Details and limits are in the public result.
- Next: integrate recovery and visual movement into the ledger-backed schedule and perform the same-scenario comparisons. No spending or external commercial action occurred.


### 2026-11-18 integrated view and baseline checkpoint

- Connected the ledger schedule, mover and missed-boarding recovery in a simple 3D scene. Headless simulation completed 20 passengers with one planned miss; one rendered frame was inspected. Its movement is synthetic and mover state is not saved.
- Native NavigationLink and FlowAI graph checks paired with the same independent minimal FIFO scheduler reproduced the 80-event happy path and trusted disk-save continuation. Neither baseline covers actual agent navigation, delayed callbacks, cancellation or disruption, and integration effort is unmeasured. Ten proof scripts passed; FlowAI still reports shutdown resource warnings.
- Next: run equivalent negative and save/restore traces with each baseline, measure integration effort and apply the differentiation gate. No spending or external commercial effects occurred.


### 2026-11-18 visual replay checkpoint

- Added trusted local snapshots of the fixed ledger scene and its simple mover/recovery state. A headless disk restore during boarding reproduced the complete continuation to 20 arrivals; one invalid actor state was rejected without mutation. See the public result for scope and test evidence.
- The baseline happy path alone does not establish differentiation. Compare delayed callbacks, missed boarding, cancellation and save/restore on equivalent inputs and measure integration effort; real navigation, generalized routing and production-quality save handling remain unverified. No spending or external commercial effect occurred.


### 2026-11-18 cancellation checkpoint

- The fixed schedule now cancels queued or boarding passengers and rejects late and duplicate callbacks; a test covers canceled-state restore and preservation of other queue entries. Onboard cancellation and physical cancellation recovery are not implemented.
- Next: compare equivalent negative traces and integration effort against the native and FlowAI baselines and apply the technical differentiation gate. No spending or external commercial effect occurred.


### 2026-11-18 DIY negative-case comparison checkpoint

- A separate fixed-route FIFO baseline and the ledger fixture produced the same 78-event trace for a cancellation, missed boarding, stale callbacks and a trusted mid-boarding disk restore. The initial DIY baseline accepted duplicate ownership in a corrupt snapshot; an added validation version rejected it and passed the trace. The public result records test commands, wall-clock observations and their strict limits.
- The technical differentiation gate has not passed. The same AI authored both implementations with knowledge of the test, and no comparable real-controller integration time or disruption result exists. Do not package or market a claimed advantage.
- Next: run a bounded, equivalently timed real-controller and disruption comparison, then apply the project go/no-go rule. Commercial validation remains unvalidated and no spending or external commercial effect occurred.


### 2026-11-18 disruption comparison checkpoint

- Both the ledger fixture and validated DIY baseline now pass the same fixed no-route disruption test, applied after two passengers board but before departure. Both explicitly fail unfinished journeys, clear simulated claims and reject a repeated disruption and late callback. The public comparison result records an initial test-timing error and the corrected test.
- This is not a mid-ride breakdown, rerouting or physical recovery, and no equivalent real-controller integration effort has been measured. The technical differentiation gate remains unpassed; do not package on the present evidence. No spending or external commercial effects occurred.
- Next: compare a real-controller integration and mid-ride safe recovery with the DIY alternative, time equivalent setups and apply the go/no-go rule.


### 2026-11-18 mid-ride and navigation comparison checkpoint

- Both fixtures now hold stranded seats through disruption and trusted disk restore until token-checked rescue. A fixed mid-ride trace matched between them. The ledger snapshot is version 3 and has no migration for earlier fixture versions.
- A single CharacterBody3D completed the same two-leg and interrupted recovery traces with native NavigationAgent3D and FlowAI for both implementations. FlowAI reported resource warnings and its default target tolerance required adjustment. See the public DIY comparison for exact scope, results and evidence limits.
- No advantage in reliability or integration effort has been demonstrated; the gate remains unpassed. Next: test 20 real agents and a second controller pattern, measure equivalent integration work and apply the go/no-go rule. No spending or external commercial effects occurred.


### 2026-11-18 twenty-agent controller checkpoint

- Both ledger and validated DIY fixtures completed identical 20-body NavigationAgent3D and FlowAI happy-path traces (49 ticks, 80 events), and matched 26-event interruption traces with three bodies returned to a designated safe point. FlowAI reported its existing shutdown resource warnings. See the public result for commands and timing limitations.
- Tests use an AI-authored shared adapter, immediate boarding, direct obstacle-free recovery and no physical vehicle. Twenty-body controller-state restore and equivalent integration/QA effort have not been measured. No advantage is demonstrated and the technical gate remains unpassed.
- Next: assess equivalent fresh-controller integration effort and controller-state restore and obstacle-aware disruption, then apply the go/no-go rule. No spending or external commercial effects occurred.


### 2026-11-18 twenty-agent controller restore checkpoint

- Native and FlowAI tests saved fixed schedule and body position/target state during movement, destroyed and reconstructed the 20 controllers, and reproduced the original 80-event trace for both fixtures. The first native draft saved too late and failed its in-motion assertion; the corrected test passed with an explicit between-stops position check. FlowAI retained its shutdown resource warnings.
- These are trusted synthetic snapshots, not a general save API. Obstacle-aware recovery and equivalent integration/QA effort remain untested, and no differentiation advantage has been demonstrated. The technical gate remains unpassed.
- Next: compare obstacle-aware recovery and consistently measured fresh-controller integration work before applying the go/no-go rule. No spending or external commercial effects occurred.


### 2026-11-18 technical gate assessment

- Native and FlowAI controller tests now recover a stranded body around a physical obstacle; the validated DIY and ledger fixtures matched the same trace. Separate small adapter harnesses passed an identical callback contract, but the second reused the first and their wall-clock intervals are not a fair independent integration-effort comparison. FlowAI retained shutdown resource warnings.
- Decision: no-go for packaging or paid release on present evidence. The required reliability and integration-effort advantage has not been demonstrated. The public gate assessment lists incomplete requirements and the limits of the comparison. This is not proof that every target use is solved or every transport product lacks demand.
- No reliable total focused engineering time was tracked against the six-hour pre-sale cap; future validation must track it. Next: identify a specific untested differentiation hypothesis and record focused time before further validation; do not package or publish absent a passed technical gate. No spending or external commercial effects occurred.


### 2026-11-18 alternative-route experiment checkpoint

- Added two bounded time-dependent route-planner prototypes and a seeded comparison. Across 500 small graphs they agreed on reachability and earliest arrival; eight equal-arrival itineraries differed because their deterministic tie policies differ. A manual single-passenger ledger exercise rerouted after a failed connection. See the public result for the initial failed tests, validation, limitations and recorded local work interval.
- Neither planner is integrated into an automatic multi-agent coordinator, and no comparable integration-effort advantage is demonstrated. The technical gate remains unpassed; packaging and paid release remain no-go. Earlier focused work time is unknown; this bounded session recorded approximately 3 minutes 31 seconds of wall time.
- Next: define the tie contract and assess automatic multi-agent rerouting and comparable integration effort before reconsidering the gate. No spending or external commercial effects occurred.


### 2026-11-18 automatic reroute checkpoint

- Added a fixed three-service coordinator that automatically replans 20 synthetic passengers when a waiting connection is disabled. Both planners produced the same 144-event trace, completed all journeys, and resumed identically from trusted disk state; no-route, invalid snapshot and in-transit disable refusal checks passed. The candidate graph validator, coordinator and ledger are shared, so this is not an independent end-to-end baseline.
- In-transit breakdown rescue, actual movement controllers, general dynamic routing and a fair integration-effort comparison remain unverified. The technical gate remains unpassed; packaging remains no-go. See the public route result for the exact evidence and approximately 2-minute-2-second additional wall interval.
- Next: assess in-transit recovery, real-controller integration and equivalent DIY effort for the rerouting scenario before reconsidering the gate. No spending or external commercial effects occurred.


### 2026-11-18 rerouting comparison and technical-gate decision

- A separate FIFO coordinator and planner matched the ledger-based fixed coordinator on a 150-event disruption, stranded-seat restore, token-checked rescue and automatic reroute trace for 20 passengers. An initial DIY restore missed a wrong-stop corruption; an added validation version rejected it. Both implementations also completed the same 20-body native and FlowAI navigation scenario in 71 schedule ticks; FlowAI retained shutdown resource warnings. The public route result records the shared-controller, collision, save-format, timing and independence limits.
- A bounded public-source review found partial free queue/navigation alternatives and an elevator engineering question, but no independent evidence of paid demand or measured integration advantage. No narrower validated commercial opportunity was established.
- **Decision: paused at the project technical gate; no packaging or paid release on current evidence.** The project plan directs pause or kill when a meaningful advantage does not survive comparison. This preserves the prototypes and does not assert that all possible transport products lack value. Reassess only with specific new differentiation evidence or an explicit owner-directed change to the gate or scope.
- Three measured local work windows total approximately 10 minutes 54 seconds of wall time, not focused-human time; earlier and intervening effort remains unknown against the six-hour pre-sale cap. Commercial validation remains unvalidated; no spending, outreach, publication, sales or other external commercial effects occurred.


### 2026-11-18 graph-revision validation checkpoint

- A follow-up test found that both fixed automatic coordinators accepted a snapshot with a changed service duration. Both now reject changes to their expected ordered fixed graph while preserving legitimate disabled-service state. The graph-revision, reroute, rescue and validated DIY comparison tests passed. See the public route result for the initial failure and scope.
- This does not establish a candidate advantage or provide a general migration system. The project remains paused at the technical gate. A further approximately 1-minute-8-second wall interval was recorded; focused prior effort remains unknown. No spending or external commercial effects occurred.
- Next: reassess only if new evidence demonstrates the required advantage, or the owner explicitly changes the gate or scope.


### 2026-11-18 missed-capacity validation checkpoint

- Reproduced a capacity-routing gap in both default fixed coordinators: a passenger missed B and arrived at tick 10 although a later replan could use C and arrive at tick 7. An opt-in experimental replan mode in both coordinators achieved tick 7, matched event traces, survived a trusted snapshot and avoided retroactive boarding when services departed simultaneously. The default remains unchanged for reproducibility.
- The heuristic does not predict future capacity and has no general liveness, fairness, starvation or real-controller proof. Both implementations were written by the same AI for the same scenario, so no technical advantage is demonstrated. Snapshot versions changed without migrations; see the public route result for exact limits and approximately 1-minute-54-second additional wall interval.
- The project remains paused at its technical gate. Reassess only if specific new evidence demonstrates an advantage or the owner explicitly changes the gate or scope. No spending or external commercial effects occurred.


### 2026-11-18 capacity-policy counterexample checkpoint

- A 100-case seeded synthetic check found a case where opt-in missed-departure replanning delayed `npc08` from tick 14 to tick 18; the DIY coordinator reproduced it. A candidate-only forecast of currently visible queues did not fix that case. The initial expected-improvement assertion failed; the final test explicitly reproduces the failure. The public route result records the sample counts and limits.
- Both policies remain experimental and disabled by default. They do not prove no harm, fairness, starvation freedom or future-capacity awareness; the forecast covers only direct hub-to-end legs. Candidate fixture snapshots are now version 4 with no earlier-version migration. No advantage or technical-gate pass is established.
- The project remains paused. Reassess only with specific new differentiation evidence or an explicit owner-directed gate or scope change. This validation used approximately 3 minutes 9 seconds of recorded wall time; prior focused effort is unknown. No spending or external commercial effects occurred.


### 2026-11-18 guarded-replan validation checkpoint

- Added an opt-in fixed-fixture guard that simulates currently known passengers before a queue switch. It produced no later passenger in 30 seeded static cases, and a separately written FIFO version matched those traces. An unexpected service disruption produced a counterexample: `npc01` arrived at tick 12 instead of tick 8; the same pre-disruption history gave tick 7 instead of tick 8 without the disruption. The public route result records the initial compile error, sample counts and limits.
- The guard is not a general no-harm guarantee: it assumes no unknown changes, has no real-controller or scalability proof, and is disabled by default. Candidate and DIY snapshot formats are now versions 5 and 3 with no migrations. No technical advantage is established, so the project remains paused at its gate.
- Next: reassess only with specific new differentiation evidence or an explicit owner-directed gate or scope change. Approximately 4 minutes 29 seconds of additional wall time were recorded; prior focused effort remains unknown. No spending or external commercial effects occurred.


### 2026-11-18 bounded tick measurement checkpoint

- Measured 20 repeated headless fixed-fixture runs after two warmups on a Ryzen 7 6800H and Godot 4.5.1. Candidate and DIY traces matched within each mode. The guarded candidate averaged about 423 microseconds per active tick versus about 27 microseconds in default mode; maxima and percentiles, methodology and warnings are recorded in the public result. This excludes physics, rendering and integration work, and is not an FPS or worst-case guarantee.
- The guarded policy still has an unexpected-disruption counterexample, and no reliability or integration-effort advantage has been established. The project remains paused at its technical gate. This measurement used approximately 39 seconds of recorded wall time; total prior focused effort remains unknown. No spending or external commercial effects occurred.
- Next: reassess only with specific new evidence demonstrating an advantage or an explicit owner-directed change to the gate or scope.


### 2026-11-18 projection-cache checkpoint

- Added a transient within-tick baseline-projection cache to the experimental guarded mode and to the DIY comparison. Against retained uncached references, 50 seeded cases including disruptions matched passenger state and trace after every tested tick and reduced baseline projection counts from 128 to 92 for each implementation.
- One 20-run headless timing sample showed modest lower means for cached versions, but it is noisy and excludes game integration. The dynamic-disruption counterexample remains and no candidate advantage is established. The public tick measurement records the timings, maxima, caveats and approximately 2-minute-5-second wall interval.
- The project remains paused at its technical gate; reassess only with specific new differentiation evidence or an explicit owner-directed gate or scope change. No spending or external commercial effects occurred.


### 2026-11-18 owner gate revision and local development authorization

- The owner explicitly directed that the technical gate be changed so local development and testing can continue toward completion. The prior no-go decision and comparison evidence remain in the historical checkpoints; comparative advantage is not established and must not be claimed.
- Local development, testing, and preparation of reviewable artifacts are authorized. No spending or publication is authorized without the owner’s approval; account, marketing, outreach and other external action permissions are unchanged. The `execution_authorized` field remains false for commercial execution, and authorized spend remains CAD0.
- Technical correctness, truthful documentation, licensing, installation QA and owner approval for publication remain required. Next: implement the general Godot 4 graph, timetable and reservation contracts and meaningful tests, then continue through the local integration and release-preparation backlog. Prior focused effort against the planning work cap is incompletely recorded; track new work honestly.


### 2026-11-18 local coordinator and demo checkpoint

- Implemented an unpublished configurable timetable graph, FIFO capacity ledger, journey lifecycle, Node interface and synthetic 20-passenger 3D demo with local save/replay and service disruption recovery. Eight Godot 4.5.1 headless scripts pass; see the reviewed public result for test scope, initial test correction and the sandbox certificate warning.
- Physical vehicle feasibility, real movement integration, onboard cancellation, broader QA and production readiness remain open. Timetable routes do not forecast future capacity and comparative advantage remains unproven. Prior focused engineering time is unknown; do not infer it from wall time.
- Next: integrate and test actual Godot movement controllers and physical platform behavior, then continue the remaining local QA and documentation. Commercial execution remains unauthorized, spend remains CAD0 and publication requires owner approval. No external commercial action occurred.


### 2026-11-18 initial engine integration checkpoint

- A single CharacterBody3D completed a coordinator-controlled journey on an explicitly carried translating platform. A separate collision scene used a capsule body, an AnimatableBody3D and a station: the passenger stayed on the moving platform and walked onto the station before the alighting acknowledgment. The public result records the initial test failure and both scenes’ limitations.
- All ten local Godot 4.5.1 scripts pass, including the 20-agent synthetic disruption and replay tests. The physical scene has one passenger and does not establish crowd behavior, obstacle recovery, a reusable production adapter or physical boarding across navigation. Godot emitted a sandbox root-certificate-store warning during offline tests.
- Next: extend physical-controller integration to multiple agents, blocked movement and disruption recovery, then continue installation, compatibility and remaining technical QA. No spend, outreach or publication was authorized or performed.


### 2026-11-18 further local integration checkpoint

- A flat NavigationAgent3D scene now boards in response to a request and rides a collision platform; four passengers rode together in another controlled scene, a blocked exit retained its seat until resolved, and a disabled-service passenger reached a safe stop before recovery. A clean copied-add-on loading check also passed. The public result records earlier failed attempts, their corrections and scope limitations.
- All fourteen Godot test scripts pass on 4.5.1. A small 20/100/500-agent headless coordinator-only timing sample is documented with setup exclusions; it is not a game-performance guarantee. The sandbox root-certificate-store warning persisted.
- A reusable controller adapter, disconnected-region navigation, broader disruption/save recovery, real game performance, licensing and release QA remain open. Prior focused work and the current session duration were not reliably tracked. No spending or publishing occurred; commercial execution still requires approval. Next: build and validate a reusable adapter and continue the local release checklist.


### 2026-11-18 optional navigation adapter checkpoint

- Added an optional navigation movement bridge with game-supplied targets and physical-arrival verification, timeout reporting and token-checked coordinator acknowledgments. A flat collision scene passed end-to-end boarding and ride; safety tests passed for unverified timeout, nonfinite target rejection, reentrant cancellation and a stale request. A fresh copied-add-on loading check included the adapter.
- All sixteen Godot test scripts passed on 4.5.1; Godot continued to emit a sandbox certificate-store warning. The adapter currently assumes horizontal movement and fixed gravity; it does not manage vehicle control, object lifecycle or save/restore of in-flight movement. The local release checklist and public result record evidence and remaining work.
- Next: validate the adapter with multiple agents, interruption and save/restore, then continue compatibility, rights and release QA. The prior and current focused work duration are not reliably known. CAD0 spending authorization and the requirement for owner approval before publication remain unchanged; no external commercial action occurred.


### 2026-11-18 navigation and request-restore checkpoint

- Four agents navigated along separate lanes onto a collision platform through the optional adapter and completed the trip in a controlled scene. The coordinator now reconstructs outstanding boarding, alighting and recovery requests after snapshot restore with original IDs and tokens. Tests passed for boarding and recovery reconstruction and resuming an adapter acknowledgment. The current tick is reported on reconstruction; actual body state and movement remain the game’s responsibility.
- Evidence is limited to scripted scenes, not congested navigation, general avoidance, reliable vehicle positioning or real-game performance. Onboard cancellation, broader physical recovery, compatibility, rights and release QA remain open. The current and prior focused work duration are not reliably known.
- Next: test restored adapter movement and disruption in representative scenes, address remaining lifecycle gaps, and continue the local release checklist. No spending, outreach or publishing occurred; owner approval remains required before spending or publication.


### 2026-11-18 safe cancellation and movement restore checkpoint

- Onboard cancellation now requests a safe exit while retaining the seat, completes only after recovery acknowledgment, and survives availability changes and save/restore. It passed coordinator and one controlled collision-scene test. Cancellation during confirmed boarding is retried after departure. Snapshot format is version 5 with no migration from earlier experimental versions.
- A navigation scene saved while an agent was moving, restored the coordinator, reconstructed the pending request and resumed with the same physical body; the agent boarded, rode and exited. This does not serialize the body, navigation state or vehicle. Twenty scripts passed as a suite after the format change; the additional movement-restore script passed separately. The offline sandbox certificate-store warning persisted.
- Next: expand multi-agent and interruption QA, resolve vehicle continuity and scene lifecycle, and continue compatibility, licensing and release preparation. Work duration remains incompletely recorded; no spending or publication occurred, and separate owner approval is still required for either.


### 2026-11-18 destroyed-agent handling checkpoint

- A missing body causes the optional adapter to report failure without a false movement acknowledgment. A new explicit game assertion releases a destroyed agent’s queue claim or occupied seat and cancels the journey; safe recovery remains required for an existing physical passenger. Tests cover queued, boarding, onboard and stranded removal, duplicates, stale callbacks and snapshot restore.
- All 23 Godot scripts passed locally on 4.5.1 after this change. The sandbox root-certificate-store warning remained. The game is responsible for verifying destruction; representative integration, physical vehicle continuity, broader lifecycle handling, compatibility, licensing and release QA remain open.
- Next: continue multi-agent navigation and interruption QA and the local release checklist. The work interval was not reliably measured. No spending, outreach or publication occurred; separate owner approval remains required before spending or publication.


### 2026-11-18 diagnostics, lift and migration checkpoint

- Added a copied vehicle-ledger inspection API and a demo queue/occupancy HUD; automated checks verify inspection cannot mutate the ledger. One passenger rode a collision-based vertical lift and exited onto a raised station. A local evidence matrix maps twelve failure and edge cases to their tests.
- Compatible version-4 snapshots now migrate on a copy to version 5 and then pass full validation; synthetic migration and invalid-version-content tests pass. Versions 1–3 remain unsupported. This supersedes the earlier checkpoint’s statement that version 4 lacked migration. All 24 Godot scripts passed on 4.5.1; the sandbox certificate-store warning persisted.
- The demo HUD has not received visual acceptance. Broader integration, physical vehicle continuity, compatibility, rights and release QA remain open. Next: review the real demo, expand integration tests and continue the local release checklist. The work interval was not reliably measured. No spending, outreach or publication occurred; separate owner approval remains required before spending or publication.


### 2026-11-18 installation and documentation checkpoint

- Added a repeatable isolated copy/remove/reinstall smoke script; both installation cycles passed on Godot 4.5.1. Added a coordinator API and integration guide and a twelve-case evidence matrix. Compatible version-4 migration checks now cover pending boarding, alighting and stranded recovery; these use synthetic older-shape fixtures.
- The complete 24-script Godot suite passed after the migration and HUD changes, with a root-certificate-store warning in the offline sandbox; the two migration scripts were rerun successfully after their extra assertions. The portfolio browser check, commercial checks and 94 portfolio tests passed, with one platform symlink test skipped.
- Visual acceptance, broader real-game integration, physical vehicle continuity, version/platform coverage, rights review and release QA remain incomplete. Next: continue those local tasks. The work interval was not reliably measured. No spending, outreach or publication occurred, and either spending or publication requires owner approval.


### 2026-11-18 seeded invariants and support preparation checkpoint

- A seeded local exercise covered 25 disruption scenarios of 50 ticks each with 20 passengers, checking capacity, unique ledger ownership and exact snapshot restoration after each tick. It passed on one small graph and does not prove fairness, liveness or physical safety.
- Added an API guide, draft troubleshooting and storefront notes, and a repeatable isolated install/remove/reinstall smoke tool; both install cycles passed. These are local drafts and do not authorize distribution, pricing or support promises. The complete 24-script Godot suite passed before the new invariant script; that additional script passed separately. Sandbox root-certificate warnings persisted.
- Remaining work includes visual demo acceptance, realistic integration, physical vehicle continuity, version/platform compatibility and rights/release QA. Next: continue those local tasks. Work duration was not reliably measured. No spending, outreach or publication occurred; owner approval is required before spending or publication.


### 2026-11-18 adapter physical recovery checkpoint

- Two controlled single-passenger collision scenes exercised the navigation adapter after service interruption. One reached the safe stop and acknowledged recovery; the second saved during recovery, restored the coordinator and resumed the request with the same physical body. Both passed. They use a simple flat navigation mesh and do not serialize physical objects or prove general evacuation.
- The 24-script Godot suite passed before these two scripts and the seeded invariant script were added; all three additions passed individually. Godot 4.5.1 emitted the sandbox certificate-store warning. The local public result records scope and earlier corrections.
- Next: expand realistic multi-agent and interruption QA, inspect the real demo and resolve vehicle continuity, compatibility, rights and release issues. Work duration was not reliably measured. No spending, outreach or publication occurred; spending and publication still require owner approval.


### 2026-11-18 adapter supersession and runtime diagnostics checkpoint

- In a controlled four-passenger disruption, three reached safety while one blocked passenger retained its seat; the last completed after the obstruction was removed and movement retried. The adapter now stops superseded or expired movement and rejects outdated requests before movement starts. Focused tests cover boarding expiry, refreshed recovery and deleted objects. The first implementation attempt had a GDScript inference error; it was corrected, and the task-owned hung test was stopped.
- All 30 Godot scripts then passed on 4.5.1. A separately added runtime diagnostic CanvasLayer also passed its headless test and install/reinstall smoke check. The sandbox root-certificate-store warning persisted. The overlay and demo have not had visual acceptance; the existing editor-gizmo and broader integration requirements remain open.
- Next: continue realistic multi-agent integration and physical continuity QA, visually review the demo/overlay and complete compatibility, rights and release preparation. Work duration was not reliably measured. No spending, outreach or publication occurred; spending and publication require owner approval.


### 2026-11-18 editor tool and local review snapshot checkpoint

- Added an optional editor stop marker and gizmo. A temporary instrumented headless Godot 4.5.1 editor project confirmed plugin registration, marker recognition and redraw; the marker does not modify the graph. The public result records the initial runtime-only gizmo test failure, editor cache restriction and corrected checks. Visual acceptance remains outstanding.
- Staged an unpublished local review-only directory with 58 hashed source, demo, test and draft-documentation files. The manifest verified, the staged main scene started headlessly and the staged add-on passed install/reinstall smoke checks. The candidate is not licensed or approved for publication. The last complete Godot suite had 30 passing scripts; the separately added overlay and marker tests passed. Sandbox root-certificate-store warnings persisted.
- Next: visually review the staged candidate and continue realistic integration, vehicle continuity, compatibility, licensing and release QA. Work duration was not reliably measured. No spending, outreach or publication occurred; spending and publication require owner approval.


### 2026-11-18 bounded continuity audit and updated review snapshot

- Added an advisory finite-horizon vehicle-continuity audit using game-supplied empty repositioning times. Tests cover feasible and late returns, missing/invalid estimates, disabled services and the demo schedule. It cannot establish initial vehicle position, future changes, actual movement or feasibility beyond its horizon.
- Staged a fresh 60-file review-only snapshot, `review-candidate-2026-11-18c`; hashes, headless demo startup, install/reinstall and editor-marker smoke checks passed. The intermediate `18b` snapshot had an installation-probe type-inference error, corrected before staging `18c`; earlier snapshots are preserved and are not release candidates. The sandbox certificate-store warning persisted.
- The most recent complete Godot suite passed 30 scripts before the new editor marker, runtime overlay and continuity audit tests; each of those additions passed separately. The snapshot is not licensed, visually accepted or approved for publication. Next: review it visually and continue representative integration, compatibility, rights and release QA. Work duration remains unmeasured; no spending, outreach or publication occurred.


### 2026-11-18 staged regression checkpoint

- All 33 Godot test scripts passed against the staged `review-candidate-2026-11-18c` snapshot on Godot 4.5.1. Its hashes, install/reinstall and instrumented editor marker checks also passed. The root-certificate-store warning persisted in the offline sandbox. The snapshot is a local, unlicensed review artifact, not an approved release.
- Next: visually review the demo and overlay, continue realistic game integration and vehicle continuity QA, and complete compatibility, licensing and release preparation. Work duration remains unmeasured. No spending, outreach or publication occurred; the owner must approve spending or publication separately.


### 2026-11-18 twenty-agent navigation and updated review snapshot

- Connected 20 CharacterBody3D/NavigationAgent3D agents to the new coordinator across three navigation regions and two scheduled services. All reached their expected stops before movement acknowledgments and completed in 51 logical ticks. Bodies in this fixture have no collision shapes and traverse navigation links directly; it is not a 20-passenger moving-platform or crowd-avoidance test.
- The latest 61-file local review-only snapshot is `review-candidate-2026-11-18d`. Its manifest, install/reinstall, editor marker and new navigation fixture passed. Comparison with the fully tested 33-script `18c` snapshot found unchanged executable source; only an evidence note changed and the new test was added. Sandbox root-certificate warnings persisted. The hidden demo window was not targetable, so visual acceptance remains open.
- Next: visually review the demo and overlay, continue realistic physical integration and compatibility QA, and complete licensing and release preparation. Work duration remains unmeasured. No spending, outreach or publication occurred; owner approval is required before spending or publication.


### 2026-11-18 finite FIFO and updated review snapshot

- In a finite uninterrupted fixture, 101 agents boarded one capacity-three recurring service in FIFO order and all completed. This does not prove starvation freedom under disruptions, changing destinations or unbounded arrivals.
- The latest 62-file local review-only snapshot is `review-candidate-2026-11-18e`. Its manifest, staged FIFO test, install/reinstall and editor-marker checks passed. Relative to `18d`, executable source is unchanged; only an evidence note and the new test differ. The preceding 33-script suite and 20-agent navigation test passed on the equivalent source. Godot 4.5.1 continued to report the sandbox root-certificate warning.
- Next: visually review the demo/overlay, expand representative collision-platform integration and compatibility QA, and complete licensing and release preparation. Work duration remains unmeasured. No spending, outreach or publication occurred; owner approval is required before spending or publication.


### 2026-11-18 twenty-agent physical platform checkpoint

- Twenty agents with capsule collision shapes boarded, rode and exited one translating collision platform through the optional navigation adapter. Passenger-to-passenger collision was disabled and the agents used separate lanes, so this is not a crowd-avoidance or two-vehicle transfer test. The separate 20-agent navigation-link transfer fixture has no collision shapes.
- The latest 63-file review-only snapshot is `review-candidate-2026-11-18f`. Its manifest, staged physical fixture, install/reinstall and editor-marker checks passed. Relative to `18e`, executable source is unchanged; only an evidence note and the new test differ. Godot 4.5.1 continued to report the sandbox root-certificate warning.
- Next: visually review the demo/overlay, integrate a representative two-vehicle collision transfer and real-game controller, and complete compatibility, licensing and release preparation. Work duration remains unmeasured. No spending, outreach or publication occurred; owner approval is required before spending or publication.


### 2026-11-18 twenty-agent two-platform collision transfer

- A scripted collision fixture transferred one passenger, then 20 passengers, across two physical platforms and a shared station. Passengers reached each surface before their boarding/alighting acknowledgment. In the 20-passenger case, all started on the first platform, each vehicle had capacity 20, passenger-to-passenger collisions were disabled and lanes were separate. This does not establish staggered capacity contention, crowd avoidance, real-game controller integration or realistic vehicle dispatch.
- The latest 65-file local review-only snapshot is `review-candidate-2026-11-18g`. Its manifest, both staged transfer tests, install/reinstall and editor-marker checks passed. Relative to `18f`, executable source is unchanged; only an evidence note and the two tests differ. Godot 4.5.1 continued to report the sandbox root-certificate warning.
- Next: visually review the demo/overlay, integrate a real-game controller and staggered collision transfers, and complete compatibility, licensing and release preparation. Work duration remains unmeasured. No spending, outreach or publication occurred; owner approval is required before spending or publication.


### 2026-11-18 staggered capacity-three physical transfer

- A controlled collision fixture transferred six passengers in two cohorts across two capacity-three platforms. The second cohort stayed queued while the first traveled; both platforms made scripted empty returns before the next departures, and all six completed. Passenger-to-passenger collision was disabled, lanes were separate, and walking and return movement were scripted; general crowd behavior, real-game integration and arbitrary dispatch remain unproven.
- The latest 66-file local review-only snapshot is `review-candidate-2026-11-18h`. Its manifest, staged staggered fixture, install/reinstall and editor-marker checks passed. Relative to `18g`, executable source is unchanged; only an evidence note and the new test differ. Godot 4.5.1 continued to report the sandbox root-certificate warning.
- Next: visually review the demo/overlay, integrate a representative real-game controller and broader collision scenarios, and complete compatibility, licensing and release preparation. Work duration remains unmeasured. No spending, outreach or publication occurred; owner approval is required before spending or publication.


### 2026-11-18 twenty-agent staggered capacity-three transfer

- Expanded the physical fixture to 20 passengers in seven cohorts on two capacity-three platforms. Every cohort completed both rides after scripted empty returns, while later cohorts remained queued at the first departure. Passenger-to-passenger collision was disabled, lanes were separate and movement was scripted; this does not prove crowd avoidance, dynamic routing or real-game dispatch.
- The latest 67-file local review-only snapshot is `review-candidate-2026-11-18i`. Its manifest, staged 20-agent staggered fixture, install/reinstall and editor-marker checks passed. Relative to `18h`, executable source is unchanged; only an evidence note and the new test differ. Godot 4.5.1 continued to report the sandbox root-certificate warning.
- One later portfolio unittest run reported a PermissionError in the concurrent niche-settings test; the same targeted test passed immediately, and earlier full runs passed. The cause was not established. Next: rerun the full portfolio suite, visually review the demo/overlay, continue realistic integration and compatibility QA, and complete licensing and release preparation. Work duration remains unmeasured. No spending, outreach or publication occurred; owner approval is required before spending or publication.


### 2026-11-18 controller integration and three-version compatibility

- Added an optional game-owned controller bridge and original CharacterBody3D example, with request validation, physical-arrival confirmation and lifecycle recovery. Synthetic clean-consumer fixtures completed a two-platform transfer and reconstruction during boarding and mid-ride; an airborne-arrival bug and a demo HUD counting defect were identified by failing regressions and corrected. The second platform and rest of the scene remained in memory; no existing third-party game was integrated.
- The complete 47-script suite passed on Windows x86-64 against local review snapshot `18j` on Godot 4.4.1, 4.5.1 and 4.7.2. Install/reinstall and instrumented editor registration, marker recognition and redraw passed on each version, including the documentation-updated 80-file `18k` snapshot with identical executable source and verified manifest. Offline Godot runs emitted a root-certificate-store warning.
- Rendered demo captures and scripted control signals were checked on the three versions; they do not establish hands-on input, accessibility or scaling. An editor capture did not clearly establish the custom marker's appearance and showed a warning indicator, which needs investigation. Other operating systems, architectures, real-game controllers and crowd behavior remain untested. Work duration was not reliably measured. No spending, outreach or publication occurred; publication and spending require owner approval.
- Next: investigate the editor warning, visually verify the marker and interactive demo, integrate a representative real-game controller, and complete rights and release QA.

## Current six-phase delivery plan

This project now uses the six-phase workflow. Its prior `working_phase_2` was
mapped to `working_phase_4` to preserve its actual stage of work.
Earlier phase numbers in the dated record above describe the former workflow;
they are history, not instructions to skip current research or repeat completed work.
The project remains **Advanced Capacity-Aware NPC Transport System** with the same ID, artifacts, evidence and permissions.
Migration is not approval of any unverified research, publication or marketing. Historical paths inside preserved work evidence may still name the old `projects/` container; resolve artifacts from the current project folder and repair only active path references when resuming, without changing historical evidence.

Target the whole product/release/marketing cycle to **2 days–3 weeks**. Reuse the
existing work. Before expanding scope, estimate the remaining time across all
phases; prioritize compatible ports and channels that fit this total window.
Record researched exclusions, blockers and any necessary owner scope decision.
Do not invent progress, drop a viable selected platform silently, or leave an
unbounded maintenance/marketing task as a completion requirement.

### Phase 1 — Product research and specification

- [ ] Reconcile the existing buyer, problem, differentiation, price, costs, rights,
  detailed product specification and acceptance tests with current evidence.
- [ ] Recheck material risks. If the idea is sound and only cosmetic changes remain,
  record “Good to go”; no forced rewrite or new idea is required.

### Phase 2 — Release platform and compatibility research

- [ ] Research all appropriate direct and adjacent release platforms; document
  eligibility, policies, costs, required formats, submission steps and sources.
- [ ] Update the Phase 1 specification with a compatible version and acceptance
  tests for every selected feasible platform; keep excluded/deferred options with
  reasons and respect the total 2–21 day delivery window.
- [ ] Independently recheck the release plan before relying on it for execution.

### Phase 3 — Marketing research

- [ ] Research suitable advertising/discovery platforms and non-platform tactics,
  audiences, positioning, search, demos, content, communities, timing and measurement.
- [ ] Save the concrete bounded marketing plan, dependencies, rules, sources and
  an independent recheck; update earlier requirements only where necessary.

### Phase 4 — Build and test

- [ ] Continue from the completed work and actual remaining checklist above;
  reconcile missing research first, then build, port, test and package every
  selected compatible version. Assign an appropriate product title without
  changing the stable ID or discarding the existing work directory.
- [ ] Record acceptance evidence and advance to Phase 5 with the lifecycle CLI
  using `--actor codex --evidence`, then stop at that handoff for the next prompt.

### Phase 5 — Release

- [ ] Execute the researched release plan on each selected feasible platform
  within the current permissions; record actual live/submission/download URLs,
  access, versions and verification. Keep outstanding approvals explicitly blocked.
- [ ] When release work is verified, advance to Phase 6 using
  `--actor codex --evidence`; wait for the Phase 6 prompt before marketing execution.

### Phase 6 — Marketing and completion

- [ ] Execute the bounded researched marketing plan and verify the actual
  placements and relevant links. Preserve costs, results and evidence limits.
- [ ] Mark Complete only after verified release and marketing evidence, with a
  factual description and live release/access and marketing URLs in the receipt.
  Completion does not establish sales or profit.

### Checkpoints and important data

At every execution checkpoint write and report `Phase N completion estimate: X% (best guess)`
for N=4, 5 or 6, explaining completed work, remaining work, blockers,
tests and the next action. Preserve all important non-secret facts, decisions,
identifiers, artifact locations and URLs in this project file as work happens.
Maintain an **Important URLs** ledger for source/edit/admin/build/upload/live/
purchase/download/demo/marketing/analytics/support locations, with purpose,
version, access/status and verification date. Keep replaced links as history.
Never put passwords, access tokens or private customer/payment information here.


### Phase 4 checkpoint — 2026-11-26: temporary-game navigation adapter

Phase 4 completion estimate: 80% (best guess)

- [x] Emergency Stop was cleared by the owner. Added `work/temporary-independent-transit-game/test_navigation_adapter.gd`, adapted from the product fixture, and added it to the project's isolated runner. Standard Godot 4.4.1, 4.5.1 and 4.7.2 passed the new case individually; the six-case temporary-game runner passed on 4.7.2. Each engine reported the existing root-certificate-store warning.
- [x] The synthetic scene exercises optional navigation-adapter boarding and a physical platform ride alongside prior game-owned controller tests. The fixture controls the final walk and alighting acknowledgment; it is not a complete adapter-driven journey or evidence from an existing external game.
- [ ] Complete visual/editor acceptance, broader representative integration and performance confidence, rights/license and final release preparation. The owner confirmed no existing game is available and requested the temporary project. Physical-device/editor interaction remains unverified.
- Decision and external effects: continue local Phase 4 work; no spend, account, outreach, publication or deployment occurred. Spending and publication require separate owner approval.
- Next action: extend the temporary project's navigation-adapter scenario through physically verified alighting using the adapter, then rerun the affected checks. The estimate is a judgment based on tested core and remaining acceptance work, not measured completion.


### Phase 4 checkpoint — 2026-11-26: adapter-controlled exit

Phase 4 completion estimate: 81% (best guess)

- [x] Extended `work/temporary-independent-transit-game/test_navigation_adapter.gd` so the optional navigation adapter handles physically verified boarding and alighting, with a scripted platform ride between them. The expanded navigation mesh covers one fixed straight route. Standard Godot 4.4.1, 4.5.1 and 4.7.2 passed this case individually; the complete six-case temporary-game runner passed on 4.7.2. The known root-certificate-store warning was emitted.
- [ ] Complete hands-on demo and editor-gizmo acceptance, broader integration/performance confidence, rights/license and final release preparation. The temporary project is synthetic; no existing game was supplied. The navigation mesh and platform are fixed, and this result does not prove arbitrary dynamic navigation.
- Decision and external effects: local Phase 4 development only; no spending, publication, outreach, accounts or external release occurred. Owner approval remains necessary for spending or publication.
- Next action: inspect the editor marker visually in a background-friendly way and prepare a precise acceptance record; if hands-on access is needed, keep it explicitly open. Estimate is a best guess based on completed integration and remaining acceptance, not measured completion.


### Phase 4 verification note — 2026-11-26

Phase 4 completion estimate: 81% (best guess)

- [x] Portfolio browser build and check and commercial checks passed after the navigation checkpoint. The business portfolio suite ran 108 tests successfully with two skips under Python UTF-8 mode. Its first run under the Windows default encoding had two `UnicodeDecodeError` errors in migration fixtures; the UTF-8 rerun passed.
- [ ] The Portfolio Manager MCP-session regression did not pass in this environment: system Python lacked PySide6; the existing application virtual environment had PySide6 but its test failed with Windows named-pipe `PermissionError` (WinError 5). No permissions were bypassed. This is a manager test limitation, not a failed Godot navigation test.
- No spending, publication or external action occurred. Next action: investigate the editor marker visually without taking control of the owner's desktop and keep hands-on acceptance open where background evidence cannot establish it. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: navigation recovery

Phase 4 completion estimate: 82% (best guess)

- [x] Added `work/temporary-independent-transit-game/test_navigation_recovery.gd`, adapted from the product fixture, to exercise one passenger's physically verified recovery using the navigation adapter after service disruption. Standard Godot 4.4.1, 4.5.1 and 4.7.2 passed the case individually; the expanded seven-case temporary-game runner passed on 4.7.2. The known root-certificate-store warning was emitted.
- [x] Inspected the preserved earlier editor screenshot and compared the marker implementation: the image came from a different instrumented, opaque-material implementation than the current marker. It cannot establish the current marker's appearance.
- [ ] Complete visual/editor and physical-device acceptance, broader realistic integration and performance confidence, licensing/rights and final release preparation. Navigation recovery remains one scripted platform and fixed navigation mesh, not general safe-stop selection or crowd avoidance.
- External effects: no spending, publication, outreach, account changes or deployment. Owner approval remains required for spending or publication.
- Next action: create a current-source, background-friendly editor marker capture or explicitly retain visual acceptance as open if that cannot be done without desktop control. Estimate is a best guess, not measured completion.


### Phase 4 verification note — 2026-11-26: background editor capture

Phase 4 completion estimate: 82% (best guess)

- [x] After the recovery checkpoint, the portfolio browser build and check and commercial checks passed. The portfolio suite passed 108 tests with two skips using Python UTF-8 mode.
- [ ] An isolated background Godot 4.7.2 editor capture using the current candidate marker timed out after 90 seconds without producing an image. The copied test plugin only instruments capture; it did not change product source. Current-marker visual acceptance therefore remains open; the earlier screenshot is not evidence for this version.
- No spending, publishing or external deployment occurred. Next action: diagnose the background editor capture or arrange hands-on marker acceptance, then finish documented release preparation. The percentage is a best guess, not measured completion.


### Phase 4 checkpoint — 2026-11-26: current-build compatibility and integrity

Phase 4 completion estimate: 83% (best guess)

- [x] The current 50-test product suite passed 50/50 on standard Godot 4.4.1 and 50/50 on standard 4.5.1 on this Windows machine, closing the previous full-suite gap for these versions. Each run emitted 50 root-certificate-store warnings. A prior full run passed 50/50 on 4.7.2; these results do not establish support on other hardware or operating systems.
- [x] Audited all 85 entries in the historical candidate manifest: 52 byte hashes matched and 33 differed only in reconstructible line endings. Saved the present-byte hashes and per-file comparison in `work/CANDIDATE_INTEGRITY_2026-11-26.json`; all 85 present hashes remained unchanged after the tests. This inventory does not establish provenance, rights or release approval. The historical manifest remains unchanged.
- [x] A hidden Godot 4.7.2 editor loaded the current marker and reported one gizmo, but produced no screenshot before the frame limit. This verifies loading only, not marker appearance.
- [ ] Complete visual and physical-device acceptance, establish practical workload limits, resolve license/rights and final release preparation. The temporary game remains synthetic.
- No spending, publication, outreach or deployment occurred. Next action: review the current marker visually without interrupting the desktop, or retain that acceptance as open; finish bounded performance and release preparation. This estimate is a best guess, not observed completion.


### Phase 4 verification note — 2026-11-26: integration matrix

Phase 4 completion estimate: 83% (best guess)

- [x] The full seven-case temporary independent game runner passed 7/7 on each of standard Godot 4.4.1 and 4.5.1; the prior 4.7.2 full run also passed 7/7. These checks cover bounded synthetic transfer, restore, interruption, cancellation and navigation recovery, not arbitrary real-game behavior.
- [x] The portfolio browser build and check, commercial checks and 108-test portfolio suite passed (two skips).
- [ ] The Portfolio Manager MCP session test failed again with Windows named-pipe access denied (WinError 5); no permissions were bypassed. Visual editor acceptance, physical input, practical workload limits and final licensing/release review remain open.
- No spending, publication or deployment occurred. Next action: resolve visual review and bounded performance evidence, then prepare the exact candidate and owner decisions for release. Estimate remains a best guess.


### Phase 4 verification note — 2026-11-26: revised candidate regression

Phase 4 completion estimate: 84% (best guess)

- [x] The staged marker-fix candidate passed the complete 50/50 product tests on standard Godot 4.7.2. All 85 manifest entries matched their recorded byte hashes after testing. Standard 4.4.1 and 4.5.1 passed focused editor and installation checks on this candidate; their 50/50 full suites were run against the immediately preceding candidate before the editor-only change. Root-certificate-store warnings persisted.
- [x] Portfolio suite passed 108 tests with two skips; commercial checks passed. The browser build/check is to be refreshed after this record update.
- [ ] Hands-on and accessibility acceptance, broader game-level performance, rights and license, and final release preparation remain open. The prior manager MCP session test still has a documented Windows access-denial limitation.
- No spending or publication occurred. Next action: finish release preparation and outstanding acceptance using the marker-fix candidate. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: blocked recovery and visual review

Phase 4 completion estimate: 85% (best guess)

- [x] Added `work/temporary-independent-transit-game/test_blocked_crowd_restore.gd`, extending the existing four-passenger blocked recovery fixture: three passengers reach safety while one remains stranded with a seat held; a new coordinator and adapter restore the mixed state, and the last passenger exits after the obstacle is removed. This case passed individually on standard Godot 4.4.1, 4.5.1 and 4.7.2; the expanded temporary-game runner passed 8/8 on 4.7.2. The platform and obstacle are scripted, bodies are reused, and this is not general world restoration or obstacle avoidance.
- [x] The marker-fix candidate's unselected stop marker was inspected in hidden editor captures on 4.4.1, 4.5.1 and 4.7.2; a 4.7.2 selected capture showed its Stop ID and transform controls. The marker uses an opaque unshaded material and diamond outline to address the previously faint unselected marker. Evidence is under `work/evidence/`; each capture used marker source matching the staged candidate. This is one Windows/NVIDIA configuration and does not establish physical-input or accessibility acceptance.
- [x] Earlier work staged `work/capacity-aware-npc-transport/review-candidate-marker-fix-2026-11-26`, passed 50/50 product tests on 4.7.2, passed editor registration/recognition/redraw and install/reinstall on 4.4.1, 4.5.1 and 4.7.2, and verified its 85-entry manifest. A single bounded physical performance sample is recorded in `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. A local evidence and remaining-work review is in `work/CANDIDATE_REVIEW_2026-11-26.md`. Root-certificate-store warnings persisted.
- [ ] Finish interactive and accessibility acceptance, broaden realistic performance evidence, reconcile outdated candidate documentation, settle rights/license and prepare the exact release for owner review. The Portfolio Manager MCP session test has a prior Windows named-pipe access-denied limitation.
- External effects: no spending, publication, outreach or deployment. Next action: update and restage truthful candidate documentation, verify the exact resulting files and continue outstanding acceptance. Estimate is a best guess, not observed completion.


### Phase 4 checkpoint — 2026-11-26: documentation-aligned candidate

Phase 4 completion estimate: 85% (best guess)

- [x] Created `work/capacity-aware-npc-transport/review-candidate-verified-2026-11-26` from the marker-fix candidate, updating the compatibility, visual QA and test-evidence documents to reflect the current checks and their limits. The other 82 manifest entries are byte-identical to the previous candidate. All 85 manifest entries matched; clean install/reinstall and editor registration/recognition/redraw passed on standard Godot 4.7.2, with the existing certificate-store warning. Its byte-identical executable files had passed the previous candidate's 50-test suite; a full suite was not rerun against the documentation-only snapshot.
- [x] Recorded outstanding decisions, evidence and scope in `work/CANDIDATE_REVIEW_2026-11-26.md`. The temporary game's new four-passenger blocked-exit restore case passed individually on 4.4.1, 4.5.1 and 4.7.2 and the full expanded runner passed 8/8 on 4.7.2. Captures under `work/evidence/` show the unselected marker on all three tested versions and the selected marker on 4.7.2.
- [ ] Physical-device and accessibility acceptance, broader game-level performance, definitive rights/license and final delivery preparation remain open. The earlier Portfolio Manager session test remains limited by Windows named-pipe access denial.
- No spending, publication, outreach or deployment occurred. Next action: finish feasible acceptance and delivery preparation, preserve honest limitations and obtain separate approval before publishing or spending. Estimate is a best guess.


### Phase 4 checkpoint — 2026-11-26: exact install-review integration

Phase 4 completion estimate: 86% (best guess)

- [x] Prepared unpublished, unlicensed `work/capacity-aware-npc-transport/install-review-marker-2026-11-26` with the updated marker add-on, integration and compatibility guides, draft rights/support material and an 18-file manifest. Every add-on byte matched `review-candidate-verified-2026-11-26`; its 18 manifest entries matched after testing.
- [x] Copied that exact install-review add-on into clean isolated Godot projects and verified install/reinstall on standard 4.4.1, 4.5.1 and 4.7.2. Also copied the exact add-on into `work/temporary-install-review-game-2026-11-26` and passed the full eight-case synthetic game runner on 4.7.2; its copy still matched after testing. The existing certificate-store warning was emitted. These checks do not validate an independently developed game or arbitrary navigation/obstacles.
- [x] Portfolio suite passed 108 tests with two skips; commercial checks and browser build/check passed. The related manager MCP-session test again failed on Windows named-pipe access denied (WinError 5); no access controls were bypassed.
- [ ] Complete remaining physical-input/accessibility review, broader game-level performance confidence, rights/license and final delivery review. The install-review folder is not an approved or licensed release.
- No spending, publication, outreach or deployment occurred. Next action: review unresolved acceptance and rights decisions for a final candidate; obtain separate approval before publishing or spending. The percentage is a best guess, not measured completion.


### Phase 4 checkpoint — 2026-11-26: self-contained quickstart

Phase 4 completion estimate: 87% (best guess)

- [x] Created unpublished, unlicensed `work/capacity-aware-npc-transport/install-review-quickstart-2026-11-26`, adding a runnable logical-only quickstart and package-specific guidance to the previous install review. It explicitly simulates acknowledgments and warns that a real game must verify physical boarding and exit; the package references to unavailable development examples were clarified. The exact quickstart passed in clean projects on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows.
- [x] The 19-entry manifest matched after preparation and every add-on file matched the earlier install review byte-for-byte. That earlier add-on passed clean install/reinstall on all three versions and the eight-case temporary-game suite on 4.7.2. The known root-certificate-store warning persisted. The local review record contains the scope and open work.
- [ ] Finish hands-on and accessibility acceptance, establish wider representative performance confidence, resolve rights/license and finalize the delivery inventory and support terms. No external game was provided; synthetic cases and a logical quickstart do not prove arbitrary integration.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete feasible product acceptance and prepare remaining owner-dependent license and release decisions; separate approval remains required before spending or publication. Estimate is a best guess.


### Phase 4 checkpoint — 2026-11-26: physical integration example

Phase 4 completion estimate: 88% (best guess)

- [x] Prepared `work/capacity-aware-npc-transport/install-review-physical-example-2026-11-26`, an unpublished, unlicensed 21-file local review that adds a logical quickstart and a scripted physical transfer with a game-owned passenger controller. The physical example is adapted from the temporary integration project and demonstrates one passenger, two moving collision platforms and verified movement callbacks. Its fixed targets are not general obstacle or crowd handling.
- [x] Both included examples passed from clean projects on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows. The 21-entry manifest matched and all add-on bytes matched the previously tested install review, which passed clean install/reinstall on those three versions and the eight-case temporary-game suite on 4.7.2. Root-certificate-store warnings persisted.
- [x] Earlier this checkpoint the portfolio suite passed 108 tests with two skips, the Portfolio Manager lifecycle suite passed 12 tests, commercial checks passed, and the browser build/check passed.
- [ ] Hands-on and accessibility acceptance, representative game-level performance confidence, rights/license, support terms and final delivery review remain open. No existing external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete feasible acceptance and prepare concrete remaining license and release decisions; obtain separate owner approval before spending or publication. Estimate is a best guess.


### Phase 4 verification note — 2026-11-26: blocked-navigation measurement

Phase 4 completion estimate: 88% (best guess)

- [x] Instrumented the temporary install-review game's four-passenger blocked recovery and coordinator restore. A single Godot 4.7.2 headless run passed its assertions and recorded engine physics-process monitor samples; the result, reproducible command and limits are in `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. The monitor can repeat coarse values and is not an independent per-frame or FPS measure. Rendering, broad navigation and other machines remain untested.
- [ ] Hands-on and accessibility acceptance, wider representative workload evidence, rights/license, support terms and final delivery review remain open. The local install review is unpublished and unlicensed.
- No spending, publication or deployment occurred. Next action: resolve feasible release-preparation work and retain owner-dependent decisions for approval; percentage remains a best guess.


### Phase 4 checkpoint — 2026-11-26: destroyed-passenger recovery

Phase 4 completion estimate: 89% (best guess)

- [x] Added `work/temporary-install-review-game-2026-11-26/test_crowd_destroyed_recovery.gd`: four passengers start physical disruption recovery; the game removes one body while three others reach safety. The adapter reports the missing body, the coordinator retains its occupied seat until the game explicitly calls `remove_destroyed_agent`, and cleanup cancels the journey and rejects duplicate removal. The case passed individually on standard Godot 4.4.1, 4.5.1 and 4.7.2; the exact-install temporary-game runner passed 9/9 on 4.7.2. This is one scripted scene, not automatic world reconciliation or general crowd proof.
- [x] Verified all 21 entries in `work/capacity-aware-npc-transport/install-review-physical-example-2026-11-26/MANIFEST.json` and confirmed its add-on is byte-identical to the temporary game's tested copy. Prepared `work/RELEASE_DECISIONS_DRAFT_2026-11-26.md` to make remaining rights, licensing, support, acceptance and release choices reviewable. Root-certificate-store warnings persisted.
- [ ] Complete physical-input and accessibility acceptance, broaden game-level performance evidence, establish rights/license and support terms, and approve the exact final delivery. The review is unlicensed and unpublished; no existing external game was supplied.
- No spending, publication, outreach, account changes or deployment occurred. Next action: continue feasible acceptance and evidence, then obtain explicit owner approval before any publication or spending. This percentage is a best guess.


### Phase 4 checkpoint — 2026-11-26: installation onboarding

Phase 4 completion estimate: 89% (best guess)

- [x] Prepared the unpublished, unlicensed `work/capacity-aware-npc-transport/install-review-onboarding-2026-11-26` with a new installation guide. It explains how to copy the add-on, enable its optional editor plugin, attach the stop-marker script, set a stop ID, run the included examples and safely remove the tool. It explicitly states that the marker is only visual and does not create graph stops or verify movement.
- [x] The 22-entry manifest matched. Add-on and example files are byte-identical to the previous install-review copy, whose two examples passed on standard Godot 4.4.1, 4.5.1 and 4.7.2. A clean-project packaged-editor registration, recognition and redraw check also passed on each of those versions. These checks do not establish hands-on or accessibility acceptance.
- [x] Ran the bounded four-passenger blocked-recovery measurement once on each standard 4.4.1, 4.5.1 and 4.7.2; all passed. Raw data and source/executable hashes are in `work/PERFORMANCE_BLOCKED_MATRIX_2026-11-26.json`, with limitations in `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. This is one scripted headless scene with uncontrolled host activity and coarse monitor values, not a supported workload or FPS guarantee. Root-certificate-store warnings persisted.
- [ ] Complete physical-input/accessibility acceptance, broader game-level performance confidence, rights/license, support terms and final delivery review. The selected local review remains unlicensed and unpublished.
- No spending, publication, outreach, accounts or deployment occurred. Next action: continue feasible acceptance and prepare exact final delivery and owner decisions; separate approval is required before spending or publication. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: demo input sizes

Phase 4 completion estimate: 90% (best guess)

- [x] Created `work/temporary-demo-input-review-2026-11-26` from the verified review candidate's add-on and development demo. At 640×480, 800×600 and 1152×648, it checked the requested viewport size and bounds of pause, save and load controls, then injected mouse clicks and a focused keyboard action. All three sizes passed on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows. The known certificate-store warning persisted. These are synthetic events and geometric bounds checks; they do not establish physical input, DPI scaling, accessibility, visual legibility or other-platform behavior. The development demo is not included in the small install review.
- [x] The local onboarding review documents optional plugin activation, stop-marker setup and its visual-only semantics. The exact packaged editor registration/recognition/redraw checks passed on all three standard versions; its add-on and examples are byte-identical to the earlier tested install review. The 22-entry manifest matched.
- [ ] Physical-device and accessibility acceptance, broader game-level performance confidence, rights/license, support terms and final delivery review remain open. The package is unpublished and unlicensed; comparative commercial advantage is unproven.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete feasible acceptance and prepare remaining owner-dependent release decisions; obtain separate owner approval before publishing or spending. The percentage is a best guess.


### Phase 4 checkpoint — 2026-11-26: keyboard focus coverage

Phase 4 completion estimate: 90% (best guess)

- [x] Extended the three temporary demo viewport tests to inject keyboard focus traversal from Save to Load and activate Load with a keyboard action, in addition to existing mouse, keyboard resume, viewport-size and control-bounds checks. All three viewport sizes passed on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows. The development demo is not included in the smaller install review. These are synthetic events and do not establish physical-device input, DPI, assistive technology or full accessibility acceptance. Root-certificate-store warnings persisted.
- [x] Updated `work/RELEASE_DECISIONS_DRAFT_2026-11-26.md` with the newer 22-file onboarding review and the precise limits of its evidence. It remains an unpublished, unlicensed draft.
- [ ] Hands-on and broader accessibility acceptance, representative performance confidence, rights/license, support terms and final delivery review remain open. No existing external game was supplied.
- No spending, publication, outreach, account changes or deployment occurred. Next action: complete feasible acceptance and prepare owner-dependent decisions; obtain separate owner approval before publishing or spending. The estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: scaled demo layout fix

Phase 4 completion estimate: 90% (best guess)

- [x] A background test at 150% Godot content scaling exposed Save and Load outside the small visible viewport. Updated the development demo to wrap its controls, reduce status font size at narrow widths, wrap its message, and allow the details panel to be hidden or shown. This retains the newer status backdrop from development source. The demo is not included in the small install review.
- [x] Inspected 4.7.2 background captures of the scaled expanded and compact states in `work/temporary-demo-input-review-2026-11-26/`; the compact state exposes the scene. Eight focused demo, layout, keyboard/mouse-injection and scaled tests passed on each of standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows. These are synthetic checks, not physical-device or comprehensive accessibility acceptance.
- [x] Staged `work/capacity-aware-npc-transport/review-candidate-scaled-demo-2026-11-26` with the fixed demo, an added scaled-input test and updated evidence notes. Clean install/reinstall passed on 4.7.2; its full product suite is in progress. The add-on runtime is unchanged. Root-certificate-store warnings persisted.
- [ ] Finish the staged regression and manifest audit, physical-input and accessibility acceptance, broader representative performance confidence, rights/license, support terms and final delivery review. No existing external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: finish the candidate regression and record its exact result; keep owner-dependent decisions and separate publication/spending approval open. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: scaled demo regression

Phase 4 completion estimate: 91% (best guess)

- [x] The staged `work/capacity-aware-npc-transport/review-candidate-scaled-demo-2026-11-26` passed its full 51/51 product suite on standard Godot 4.7.2; all 86 manifest entries matched after testing. Focused checks on byte-identical demo/add-on source passed on standard 4.4.1, 4.5.1 and 4.7.2, including 150% Godot content scaling, simulated input, hide/show details and normal viewport sizes. A separate scaled state-change and service-message bounds check passed on all three. The existing root-certificate-store warnings persisted.
- [x] Inspected background 4.7.2 expanded and compact scaled renders in `work/temporary-demo-input-review-2026-11-26/`. The fix restores the dark status backdrop from the working development source; the earlier `review-candidate-verified-2026-11-26` demo did not contain that backdrop, so its prior backdrop evidence must not be attributed to that snapshot. The smaller 22-file onboarding install review does not include the development demo. The add-on runtime is unchanged.
- [x] The portfolio suite passed 108 tests with two skips, the relevant lifecycle suite passed 12 tests and commercial checks passed.
- [ ] Native OS DPI, physical-input and broader accessibility acceptance, representative game-level performance, rights/license, support terms and final delivery review remain open. The install review is unpublished and unlicensed.
- No spending, publication, outreach, accounts or deployment occurred. Next action: retain the tested demo candidate, finish feasible acceptance and owner-dependent decisions, and obtain separate owner approval before publication or spending. Estimate is a best guess.


### Phase 4 checkpoint — 2026-11-26: acceptance and provenance preparation

Phase 4 completion estimate: 91% (best guess)

- [x] Prepared `work/ACCEPTANCE_RUNBOOK_LOCAL_2026-11-26.md` with reproducible physical mouse/keyboard, native scaling, marker and limited accessibility checks. They are not yet performed; the owner requested background testing, so no desktop takeover or display-setting change was made.
- [x] Saved `work/INSTALL_REVIEW_PROVENANCE_TRACE_2026-11-26.json`, tracing all 22 local install-review manifest files to their observed sources; add-on and passenger-controller byte matches and the physical example transformations were checked. This trace does not establish ownership, redistribution rights or a license. Added concrete nonbinding rights and support choices to `work/RELEASE_DECISIONS_DRAFT_2026-11-26.md`.
- [ ] Full 51-test runs on standard Godot 4.4.1 and 4.5.1 against the scaled-demo candidate are in progress. Physical-input/accessibility acceptance, representative performance confidence, rights/license, support terms and final delivery review remain open. The prior 4.7.2 full suite passed; the product remains unlicensed and unpublished.
- No spending, publication, outreach, accounts or deployment occurred. Next action: record the two full regression outcomes and retain the acceptance and owner-dependent decisions for review. The estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: full scaled-demo compatibility

Phase 4 completion estimate: 92% (best guess)

- [x] The exact `work/capacity-aware-npc-transport/review-candidate-scaled-demo-2026-11-26` passed its full 51/51 product tests on standard Godot 4.4.1 and 4.5.1 on Windows, matching the earlier 51/51 run on 4.7.2. All 86 candidate manifest entries matched after the later runs. The known root-certificate-store warnings were emitted. This is local Windows evidence, not a guarantee for other hardware, engines or arbitrary games.
- [x] Prepared the unperformed physical-input, native display scaling and limited accessibility checklist at `work/ACCEPTANCE_RUNBOOK_LOCAL_2026-11-26.md`. Saved `work/INSTALL_REVIEW_PROVENANCE_TRACE_2026-11-26.json` for the 22-file local install review and added nonbinding rights and support choices to `work/RELEASE_DECISIONS_DRAFT_2026-11-26.md`. Source tracing does not establish rights or grant a license.
- [x] Portfolio tests passed 108 with two skips, lifecycle tests passed 12 and commercial checks passed.
- [ ] Perform hands-on physical-input/accessibility acceptance within owner-authorized access, establish an honest final performance/support scope, confirm rights and license, and review the exact final delivery. No existing external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete feasible remaining acceptance and resolve owner-dependent license, support and release decisions; separate approval is required before publication or spending. This estimate is a best guess, not completion evidence.


### Phase 4 checkpoint — 2026-11-26: twenty-agent navigation timing

Phase 4 completion estimate: 92% (best guess)

- [x] Added local 20-navigation-agent physical-platform measurement and diagnostic fixtures under `work/temporary-install-review-game-2026-11-26/`, using the exact previously tested add-on. Three initial, three monitor-diagnostic and three wall-interval diagnostic runs passed on standard Godot 4.7.2 on Windows. The scripted scene uses fixed parallel lanes, one platform, disabled passenger collisions and scripted alighting; rendering is excluded.
- [ ] Two initial runs emitted very large coarse physics-monitor readings and longer elapsed times; six follow-up runs did not reproduce high readings, and the last three observed no physics-callback interval over 100 ms. The cause remains unknown. These are uncontrolled headless samples, not independent per-frame metrics, FPS, general capacity or a resolved performance guarantee. Details and fingerprints are in `work/PERFORMANCE_NAVIGATION_TWENTY_2026-11-26.json`, `work/PERFORMANCE_NAVIGATION_DIAGNOSTIC_2026-11-26.json`, `work/PERFORMANCE_NAVIGATION_INTERVALS_2026-11-26.json` and `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. The known certificate-store warning persisted.
- [ ] Hands-on physical-input and accessibility acceptance, representative performance confidence including this unexplained variability, rights/license, support terms and final delivery review remain open. No existing external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: investigate reproducibility with controlled profiling or record the workload limit honestly, and finish remaining owner-dependent acceptance and licensing decisions. Separate owner approval is required before publication or spending. Estimate is a best guess.


### Phase 4 verification note — 2026-11-26: performance monitor source

Phase 4 completion estimate: 92% (best guess)

- [x] Checked the official Godot Performance documentation on 2026-11-26: https://docs.godotengine.org/en/latest/classes/class_performance.html . It describes `TIME_PHYSICS_PROCESS` as physics-frame time and warns that some built-in monitors can lag. The source is recorded in `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. This does not establish that delayed updates caused the earlier unusually high readings.
- [ ] Controlled, representative performance acceptance remains open along with physical-input/accessibility acceptance, rights/license, support terms and final delivery review. No spending, publication or external commercial action occurred. Next action: investigate or explicitly scope the unresolved timing variability and complete the owner-dependent acceptance and release decisions. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: navigation timing follow-up

Phase 4 completion estimate: 91% (best guess)

- [x] Ran the 20-agent scripted navigation/platform interval diagnostic twice each on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows; all six functional runs passed. One 4.4.1 run recorded six physics-callback intervals over 100 ms, maximum 240.286 ms. The other five had no intervals over 100 ms. Raw observations and limits are in `work/PERFORMANCE_NAVIGATION_INTERVAL_MATRIX_2026-11-26.json`.
- [x] Added three further runs each on 4.4.1 and 4.7.2 with coarse host and Godot process-tree CPU sampling; all six functional runs passed. One 4.4.1 run recorded one callback interval over 100 ms, maximum 133.2 ms. Host CPU peaks were high during the run set, but samples were not timestamp-correlated to the gap and cannot establish cause. Details are in `work/PERFORMANCE_NAVIGATION_HOST_CORRELATION_2026-11-26.json` and `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. The existing root-certificate-store warning persisted.
- [x] Prepared `work/PERFORMANCE_SCOPE_DRAFT_2026-11-26.md` with observed workload, exact constraints, unresolved variability and proposed non-guarantee integration guidance. It is a local draft, not release approval.
- [ ] Investigate or explicitly accept a bounded scope for the recurrent timing variability; complete physical-input/accessibility acceptance, rights/license, support terms and exact final delivery review. Callback gaps are not rendered frames; these headless uncontrolled tests do not prove a game FPS hitch, identify a cause or establish general crowd performance.
- No spending, publication, outreach, accounts or deployment occurred. Next action: perform a more targeted investigation of the timing gaps or preserve an explicit limitation for owner review, then resolve the owner-dependent acceptance and release decisions. Estimate reduced from 92% because the gap recurred and remains unexplained.


### Phase 4 checkpoint — 2026-11-26: isolated adapter profiling

Phase 4 completion estimate: 91% (best guess)

- [x] Prepared `work/temporary-adapter-profile-2026-11-26`, an isolated copy with timing instrumentation around the navigation adapter physics callback. Four sequential 20-agent fixed-lane headless runs passed on standard Godot 4.4.1 for Windows. No run reproduced a callback interval over 100 ms; adapter callback maxima were 5.781, 11.392, 10.109 and 5.954 ms, including wrapper overhead. Raw data and the instrumented source hash are in `work/PERFORMANCE_ADAPTER_PROFILE_2026-11-26.json`; the known root-certificate-store warning persisted.
- [ ] The original long callback gaps did not recur under this instrumented run, so this does not establish or exclude the adapter as their cause. The wrapper changes copied source and excludes other engine physics, rendering, scheduling and game work. Representative performance, physical-input/accessibility acceptance, rights/license, support terms and final delivery review remain open. The install review remains unlicensed and unpublished.
- [x] Documented the profiling result and its limits in `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. Prior portfolio suite passed 108 tests with two skips; lifecycle tests passed 12, commercial checks and browser build/check passed.
- No spending, publication, outreach, accounts or deployment occurred. Next action: retain the unresolved timing variability as a release-scope decision or reproduce under controlled profiling, and complete the owner-dependent acceptance and licensing decisions. Separate owner approval is required before spending or publication. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: broad exact-install integration

Phase 4 completion estimate: 91% (best guess)

- [x] Created `work/temporary-broad-install-review-game-2026-11-26` from the original synthetic broad integration project and copied the exact add-on from `install-review-onboarding-2026-11-26` into it. The product runtime was already equivalent to the older game's copy apart from the editor marker; the fresh copy was byte-checked against the install review.
- [ ] The complete broader game integration runner is in progress on standard Godot 4.7.2. Early passenger, disruption, blocking, dispatch and cooperative-avoidance cases passed; the complete outcome has not yet been established. Avoidance and vehicle movement belong to the temporary game controller, not an automatic add-on feature, and scenarios are bounded.
- [ ] The recurrent timing variability, physical-input/accessibility acceptance, rights/license, support terms and final delivery review remain open. No existing external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete the broad runner, verify the add-on bytes after testing and record the precise results. The estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: broad exact-install integration result

Phase 4 completion estimate: 92% (best guess)

- [x] The fresh `work/temporary-broad-install-review-game-2026-11-26` passed its complete 41/41 integration runner on standard Godot 4.7.2 on Windows using the exact `install-review-onboarding-2026-11-26` add-on. All 22 package manifest entries matched and all 12 copied add-on files remained byte-identical after the run. Root-certificate-store warnings persisted.
- [x] The bounded cases include game-owned cooperative crowd avoidance, moving crowds, multiple physical vehicles, generated dispatch, interruption, scene reconstruction, footprint and endpoint clearance, and disconnected navigation. The game owns avoidance, movement and vehicle dispatch; the add-on does not provide general automatic crowd avoidance. These synthetic fixtures do not prove arbitrary game compatibility or a performance guarantee.
- [x] Portfolio suite passed 108 tests with two skips, the lifecycle suite passed 12 tests and commercial checks passed.
- [ ] The recurrent timing variability, physical-input/accessibility acceptance, rights/license, support terms and final delivery review remain open. No independently developed external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: continue feasible investigation and acceptance, then resolve owner-dependent license, support and release decisions; separate owner approval is required before spending or publication. The estimate is a best guess.


### Phase 4 checkpoint — 2026-11-26: packaged crowd and fleet examples

Phase 4 completion estimate: 93% (best guess)

- [x] Prepared the separate unlicensed, unpublished `work/capacity-aware-npc-transport/install-review-fleet-example-2026-11-26` with 26 manifest files. It adds a two-passenger cooperative-yield example and a two-vehicle mapped physical-dispatch example adapted from the temporary integration game, in addition to the logical and one-passenger physical quickstarts. Documentation makes clear the game owns yielding, targets, routes and vehicle motion; these are bounded scripted scenarios, not general automatic crowd or vehicle navigation.
- [x] All four included examples passed in clean Windows projects on standard Godot 4.4.1, 4.5.1 and 4.7.2. The 26-entry manifest, all documented `res://` package paths and the add-on byte comparison against the prior install review passed. Root-certificate-store warnings persisted. Local transformation/source observations are in `work/CROWD_EXAMPLE_PROVENANCE_TRACE_2026-11-26.json` and `work/FLEET_EXAMPLE_PROVENANCE_TRACE_2026-11-26.json`; they do not establish ownership or grant redistribution rights.
- [ ] The recurrent timing variability, native physical-input/accessibility acceptance, rights/license, support terms and exact final delivery review remain open. No independently developed external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: finish feasible acceptance and investigate or document the performance limitation; resolve owner-dependent rights/support decisions and obtain separate approval before publishing or spending. Estimate is a best guess, not measured completion.


### Phase 4 checkpoint — 2026-11-26: timestamped timing follow-up and package guidance

Phase 4 completion estimate: 93% (best guess)

- [x] Added `work/temporary-install-review-game-2026-11-26/diagnose_navigation_host_timeline.gd` and ran five sequential headless 20-agent fixed-scene checks on standard Godot 4.4.1 for Windows with coarse host/Godot-process CPU sampling. All five functional runs passed, with no physics-callback interval over 100 ms, so there was no event to correlate with CPU. The earlier gaps remain unexplained; instrumentation, clock alignment and uncontrolled host activity limit the result. Raw summaries are in `work/PERFORMANCE_NAVIGATION_GAP_TIMELINE_2026-11-26.json`, with explanation in `work/PERFORMANCE_PHYSICAL_2026-11-26.md`. Root-certificate-store warnings persisted.
- [x] Prepared separate unlicensed, unpublished `work/capacity-aware-npc-transport/install-review-performance-notes-2026-11-26`, adding `PERFORMANCE.md` and README guidance that disclose observed timing variability and do not promise FPS, a supported crowd size or general navigation. Its 27-entry manifest and documented `res://` paths passed; all add-on and example files are byte-identical to the previous review whose four examples passed on standard Godot 4.4.1, 4.5.1 and 4.7.2. This draft does not constitute accepted release scope or a license.
- [ ] Resolve or explicitly review the unexplained earlier timing gaps, complete physical-input and accessibility acceptance, establish rights/license and support terms, and review the exact final delivery. No independently developed external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: finish feasible controlled acceptance and owner-dependent scope/rights decisions; separate owner approval is required before spending or publishing. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: broad integration compatibility subset

Phase 4 completion estimate: 94% (best guess)

- [x] Verified that the broad temporary game's add-on is byte-identical to `work/capacity-aware-npc-transport/install-review-performance-notes-2026-11-26`; the 27-entry package manifest matched. Eight selected moving-crowd, mapped-dispatch, capacity-two reconstruction, disconnected-navigation, parallel-recovery, footprint and endpoint cases passed on each of standard Godot 4.4.1 and 4.5.1 on Windows. The full 41-case broad runner had previously passed on 4.7.2.
- [x] Added `work/temporary-broad-install-review-game-2026-11-26/run_compatibility_subset.py`; it passed the same eight cases on 4.7.2. Per-case 4.4.1/4.5.1 results and fixture/engine fingerprints are in `work/BROAD_INTEGRATION_COMPATIBILITY_2026-11-26.json`. The known certificate-store warnings persisted.
- [ ] The 4.4.1/4.5.1 results are a subset, not full 41-case suite results. Avoidance, vehicle movement and dispatch policy are owned by the synthetic game, and these fixed scenarios do not prove general crowd behavior or production-game compatibility. Recurrent timing variability, physical-input/accessibility acceptance, rights/license, support terms and exact final delivery review remain open.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete feasible remaining acceptance and resolve the explicitly owner-dependent release decisions; separate owner approval is required before publication or spending. Estimate is a best guess.


### Phase 4 checkpoint — 2026-11-26: local review artifact

Phase 4 completion estimate: 95% (best guess)

- [x] Added `work/prepare_local_review.py`, which builds a local-only review archive from the exact performance-notes manifest, rejects missing, unexpected, changed, unsafe or duplicate file paths and refuses to overwrite an existing artifact. The resulting `work/local-review-artifacts/GDM-002-LOCAL-REVIEW-2026-11-26.zip` has SHA-256 `7b58ad30f8e61a9a730539c5980bd56155e0495a0c23e6821461224f60fc47ee`; its 28 entries are the 27 manifest files plus the manifest, including the local-only notice. Archive entries were verified byte-for-byte against the source; repeat creation correctly refused overwrite.
- [x] Extracted the archive's add-on and examples into isolated clean projects. All four examples passed from the archived copy on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows. The known root-certificate-store warning persisted. `work/RELEASE_DECISIONS_DRAFT_2026-11-26.md` records the artifact and exact hash.
- [ ] The archive is unpublished, unlicensed and not the approved final delivery. Physical-input and accessibility acceptance, recurrent timing uncertainty, rights/license, support terms and final delivery review remain open; synthetic tests do not establish arbitrary game compatibility or general crowd/vehicle navigation.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete feasible remaining acceptance and obtain owner-dependent rights/support decisions; separate owner approval is required before publication or spending. Estimate is a best guess.


### Phase 4 checkpoint — 2026-11-26: seeded opposing crowd angles

Phase 4 completion estimate: 95% (best guess)

- [x] Added `work/temporary-broad-install-review-game-2026-11-26/test_seeded_opposing_avoidance.gd`, exercising two game-owned, capsule-shaped walkers on an open flat floor at twelve deterministic randomized opposing approach angles. The case checks both original destinations, yielding by the lower-priority walker, grounding and minimum center separation. It passed individually on standard Godot 4.4.1, 4.5.1 and 4.7.2 for Windows. Raw outputs and fixture/controller/engine hashes are in `work/SEEDED_CROWD_COMPATIBILITY_2026-11-26.json`; root-certificate-store warnings persisted.
- [x] Confirmed that the packaged cooperative-yield example's controller matches the tested game-owned controller apart from an explanatory comment. Added the new case to the broad runner for future runs; the earlier full 41/41 run did not include it, and the expanded 42-case runner has not been rerun as a whole.
- [ ] This test has only two walkers and no transit coordinator, dynamic obstacles or arbitrary terrain; it does not establish general crowd avoidance or an add-on-provided avoidance policy. Timing variability, physical-input/accessibility acceptance, rights/license, support terms and exact final delivery review remain open.
- No spending, publication, outreach, accounts or deployment occurred. Next action: complete feasible remaining acceptance and owner-dependent rights/support decisions; separate owner approval remains required before spending or publishing. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: expanded full integration and archive audit

Phase 4 completion estimate: 95% (best guess)

- [x] The expanded `work/temporary-broad-install-review-game-2026-11-26/run_checks.py` passed its complete 42/42 integration cases on standard Godot 4.7.2 on Windows, including the new twelve-angle game-owned crowd test. Root-certificate-store warnings persisted. The prior full run covered 41 cases; standard 4.4.1 and 4.5.1 have the previously recorded eight-case compatibility subset and separate seeded-angle case, not a full 42-case run.
- [x] After testing, verified that all 27 review-manifest entries and the manifest itself match the 28 entries in `work/local-review-artifacts/GDM-002-LOCAL-REVIEW-2026-11-26.zip`, that all copied add-on files match the test game, and that the archive SHA-256 remains `7b58ad30f8e61a9a730539c5980bd56155e0495a0c23e6821461224f60fc47ee`. The archive remains unlicensed, unpublished and not an approved final delivery.
- [x] The portfolio suite passed 108 tests with two skips, lifecycle tests passed 12 and commercial checks passed.
- [ ] The game owns its bounded crowd avoidance, movement and dispatch; the tests do not prove general crowd handling or arbitrary production-game compatibility. Recurrent timing variability, physical-input/accessibility acceptance, rights/license, support terms and final delivery review remain open. No independently developed game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: resolve the remaining owner-dependent acceptance and rights/support decisions and review the known timing limitation; obtain separate owner approval before publication or spending. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: owner-selected terms and acceptance setup

Phase 4 completion estimate: 95% (best guess)

- [x] The owner selected a local draft direction allowing commercial game use and modification while prohibiting standalone redistribution. Prepared `work/LICENSE_TERMS_DRAFT_2026-11-26.md`; it is non-operative, not a rights grant or approved final license. Ownership, final wording, collaborators, source-available games, support terms and applicable rights remain to be resolved before release. The chosen restriction must not be described as an OSI-approved open-source license; see https://opensource.org/osd (checked 2026-11-26).
- [x] The owner chose to perform physical-input acceptance personally and asked when and what to do. Prepared `work/owner-acceptance-2026-11-26` with a copy of the current scaled-demo candidate, isolated user-data launchers and `START_HERE.md`; its headless startup probe passed on standard Godot 4.7.2. No visible window was launched and no physical acceptance has yet occurred. The user will be given steps after background tests finish.
- [ ] Full 42-case temporary-game runs on standard Godot 4.4.1 and 4.5.1 are in progress; no full result is claimed yet. Timing variability, physical/accessibility acceptance, final rights/license wording, support and exact final delivery review remain open.
- No spending, publication, outreach, accounts or deployment occurred. Next action: finish and record the compatibility runs, then provide the owner-operated acceptance steps. Separate owner approval is required before publication or spending. Estimate remains a best guess.


### Phase 4 checkpoint — 2026-11-26: full compatibility and owner acceptance handoff

Phase 4 completion estimate: 96% (best guess)

- [x] The exact broad temporary game's expanded 42/42 integration suite passed in full on standard Godot 4.4.1 and 4.5.1 on Windows, matching its earlier 42/42 run on 4.7.2. Afterward the 27-file local review, the tested add-on and the local review archive matched the manifest; archive SHA-256 remained `7b58ad30f8e61a9a730539c5980bd56155e0495a0c23e6821461224f60fc47ee`. Root-certificate-store warnings persisted. Game-owned movement, cooperative avoidance and vehicle dispatch are bounded scripted examples, not general add-on features.
- [x] The owner selected commercial game use and modification with no standalone redistribution; prepared non-operative `work/LICENSE_TERMS_DRAFT_2026-11-26.md`. Ownership and final license/support wording remain unverified. The restrictive draft is not an OSI-approved open-source license; source checked 2026-11-26: https://opensource.org/osd .
- [x] The owner chose to perform the physical-input check personally. Prepared isolated `work/owner-acceptance-2026-11-26`, with `START_DEMO.cmd`, `START_MARKER_EDITOR.cmd` and `START_HERE.md`. The candidate add-on and demo files were byte-checked; the demo startup and marker editor load passed headlessly on 4.7.2. No visible window was launched by the agent, and no manual pass is claimed.
- [ ] Owner hands-on results, wider accessibility, recurrent timing variability, rights/final license, support terms and final delivery review remain open. No independent external game was supplied.
- No spending, publication, outreach, accounts or deployment occurred. Next action: owner runs the prepared acceptance check and reports any issues; continue authorized fixes and obtain separate owner approval before publication or spending. Estimate is a best guess, not completion evidence.


## Four-phase workflow migration

Mapped former working_phase_4 to working_phase_2. Historical research, execution evidence, phase history, and all existing work remain intact. No research approvals or execution authorization were inferred.

Phase 2 completion estimate: 96% (best guess)
