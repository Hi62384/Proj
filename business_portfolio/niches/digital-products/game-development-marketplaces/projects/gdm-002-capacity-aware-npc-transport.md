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
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "owner_research_and_adjacent_engineering_problem_only",
  "source_ids": [
    "GDM-WB-2026",
    "GDM-GODOT-STORE",
    "GDM-FAB",
    "GDM-ROBLOX-STORE"
  ],
  "parent_project": null,
  "related_projects": [
    "GDM-001",
    "GDM-003"
  ],
  "legacy_ids": [],
  "next_action": "After GDM-001's validation decision, compare real unmet transport behavior and competitor coverage in Godot, Unity and Unreal before choosing the first edition.",
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
    "production_runtime": "Customer game runtime only; version/support costs are unknown.",
    "budget_fit": "discovery_only_no_spend",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  },
  "marketing_execution_authorized": false,
  "production_budget_verified": false,
  "success_probability": "not_established",
  "marketing_lane": "queued_discovery_draft_only",
  "launch_gate": "engine_selection_buyer_and_competitor_evidence",
  "pre_sale_work_cap_hours": 2,
  "ad_test_cap_cad": 0,
  "offer_price_cad_hypothesis": null,
  "historical_price_usd_hypothesis": "39-79 for a Godot candidate in the workbook; not a family-wide quote",
  "platforms_supported": [],
  "platforms_proposed": [
    "Godot",
    "Unity",
    "Unreal",
    "Roblox",
    "GameMaker",
    "Construct",
    "GDevelop"
  ]
}
---
# Advanced Capacity-Aware NPC Transport System

**Purpose:** Give simulation/management games coordinated NPC queues, reservations, boarding, riding, transfers, exits and rerouting around finite-capacity vehicles. This is one family with independently validated engine adapters; no edition is selected for development.

## Buyer, problem, buying trigger

The buyer is a developer whose game contains multiple NPCs competing for an elevator, ferry, train or comparable scheduled transport. The trigger is an integration milestone where normal pathfinding or a moving platform fails to handle capacity, queues, interrupted journeys or saved in-transit state. Payment would require a measured advantage over native navigation links, free examples, custom state machines and existing lift/crowd packages. A basic lift animation is not enough.

## Evidence and limits

The owner workbook reviewed 2026-11-15 cites a [Godot discussion](https://forum.godotengine.org/t/pathfinding-with-elevator-platform/45444) describing wait/board/ride/exit needs, [FlowAI](https://github.com/a6xdev/FlowAI) moving graphs and [Smart Platforms](https://asago.itch.io/smart-platforms). This is an engineering pain signal and substitute inventory, **not verified paid demand**. Buyer count, edition feasibility, current asset rules and actual performance are unknown.

### Candidate-engine competition screen (research check 2026-11-15)

| Engine | Native/free/paid substitute and dated source | Gap and status |
| --- | --- | --- |
| Godot | [NavigationLink](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationlinks.html), FlowAI and Smart Platforms (workbook review 2026-11-15). | Candidate; free motion/path links do not establish a capacity/recovery gap without comparative demo. |
| Unity | [NavMesh links](https://docs.unity3d.com/Manual/class-OffMeshLink.html) and Asset Store crowd/elevator search (research pointer 2026-11-15). | Candidate; catalog comparison and buyer interviews still needed. |
| Unreal | [Smart Objects](https://dev.epicgames.com/documentation/en-us/unreal-engine/smart-objects-in-unreal-engine) and navigation/crowd tooling (research pointer 2026-11-15). | Candidate; existing systems may cover reservations; no edition promise. |
| Roblox | [PathfindingService](https://create.roblox.com/docs/characters/pathfinding) and Creator Store models/plugins (research pointer 2026-11-15). | Candidate; server authority, replication and store eligibility need proof. |
| GameMaker | Native path/grid workflows and [GameMaker manual](https://manual.gamemaker.io/) (research pointer 2026-11-15). | Candidate; integration API, state persistence and distribution are unknown. |
| Other engines | Engine-specific navigation and customer code are default substitutes. | No named edition until independent demand, API and support review. |

This table records research leads, not a complete competitor audit. Exact paid competitor coverage must be refreshed before choosing an edition.

## Narrow MVP and edition architecture

Choose the first engine through a scored review of unmet buyer demand, competitor coverage, implementation feasibility and test/support cost; **Godot is a candidate, not a preselected winner**. A bounded demo uses at most 20 NPCs, two finite-capacity vehicles and one transfer route on a fixed test machine. This is an initial **test target**, not a measured supported scale. It should exercise reservations, fair queues, schedules, missed departures, service disruption, rerouting, save/load mid-trip and deterministic recovery. Define a small integration API for route requests, vehicle events and state serialization.

Share a behavior specification, state-machine test vectors, disruption fixtures, debug semantics and documentation. Isolate navigation, movement-controller, save-system and packaging adapters per engine with independent versions. Exclude multiplayer, arbitrary scale, full traffic simulation, every 2D/3D movement system and production integration until separate proof.

| Edition | Status | Feasibility / maintenance gate | Potential package/channel | Negative test before claim |
| --- | --- | --- | --- | --- |
| Godot | candidate | Moving links, 3D boarding, engine versions and customer controller glue; high support. | Godot addon; free library sample, paid itch.io/direct if rights permit. | Full queue with cancelled ride and mid-trip restore. |
| Unity | candidate | NavMesh updates, physics and save adapter; medium-high support. | Unity package/Asset Store after review, or itch.io/direct. | Two vehicles contend for one transfer route without duplicate boarding. |
| Unreal | candidate | Smart Object/crowd interaction and plugin versioning; high support. | Fab only after format/license review. | Interrupted reservation recovers without deadlock. |
| Roblox | candidate | Server-side capacity and replicated movement; high operational burden. | Eligible model/plugin on Creator Store if approved. | Disconnect/rejoin cannot duplicate seats. |
| GameMaker | candidate | 2D path and state persistence API feasibility unknown. | Direct/itch.io, free discovery route only if eligible. | Restore deterministic queue order. |

No prototype/verified edition exists. Potential channels are not approved listings.

## Acceptance and negative tests

- Competing NPCs cannot overbook capacity; queue order and fairness policy are explicit and deterministic.
- Service disruption cancels or reroutes only affected reservations; stranded agents receive a defined result, not silent disappearance.
- Save/load during boarding and transit restores each agent, vehicle occupancy and schedule once; duplicate boarding is rejected.
- A bounded stress fixture measures frame time and memory on a specified machine and engine version; the initial 20-agent target may be revised after evidence.
- Compare integration steps, bugs found and behavior against native links, free examples and paid crowd/lift packages. A pretty moving-platform demo alone fails acceptance.

These are planned tests; none has been executed.

## Rights, distribution, effort and marketing

Check license compatibility for engine APIs, borrowed example code, artwork and demo models. No customer game assets should be included without rights. Godot's official asset library is a free discovery route under current research; Fab, Unity Asset Store and Roblox Creator Store are conditional on a genuine engine-compatible edition and seller policy. Superhive is for Blender-specific products and is not a default channel for this family. itch.io/direct are candidate paid routes only. No uploads or seller-account changes authorized.

Effort and support cost are **unknown**, likely high because movement controllers and save systems vary. Measure adapter hours and support per pilot before pricing. The workbook's US$39–79 Godot range is an experiment, not accepted pricing or expected income. A low-cost demo plan would show a capacity bottleneck, disruption and restored journey side by side with native/free approaches, with honest limits and permission-based discovery only.

## Validation gate and kill rule

This family is **queued behind GDM-001**, not a parallel build. First edition requires a buyer/competitor/feasibility comparison. A later three-team evaluation and at least two paid-pilot signals is a decision heuristic; an alternative meaningful signal requires explicit documentation. Stop or pivot if existing solutions already deliver the behavior, integration forces major customer AI rewrites, or support cost makes a sale uneconomic.

## Resume checkpoint

- Completed with evidence: family planning record and dated research screen only.
- Current task: queued engine and buyer review; no development started.
- Remaining checklist: [ ] edition selection; [ ] current paid competitor audit; [ ] permission-based buyer interviews; [ ] bounded prototype; [ ] disruption/save tests; [ ] support-cost measurement.
- Blockers/decisions needed: GDM-001 validation decision, buyer evidence and owner authorization for contact, build costs or publication.
- Next concrete action: after GDM-001's decision, compare Godot, Unity and Unreal transport substitutes with three target developers before selecting the first edition.
- Owned deliverables and hashes/versions: this planning record only.
- External effect state: not_started.
- Private checkpoint reference: none for this new family.

## Decisions and work log

- 2026-11-15: Created one multi-engine family plan. No engine edition, buyer pilot, product code, listing or payment was completed.

## Implementation-ready specification — queued research candidate

**Finished-product contract.** A game integrates a transport graph with stops, finite-capacity vehicles and schedules into its own navigation/controller system. Agents can request a journey, enter a waiting area, reserve a place if policy allows, board once, transfer, exit, change/cancel destination, miss a departure, reroute around service interruption and recover deterministically after save/load. The system reports why an agent is waiting or stranded. It is not a standalone pathfinder, visual elevator animation or promise of multiplayer-scale simulation.

**Buyer and reason to purchase.** The candidate buyer is a small simulation/management/city-builder team with multiple simultaneous agents and vehicles. A paid edition must save meaningful engineering and debugging time over engine navigation, free queue examples and commercial lift/crowd packages. Competing packages and buyer demand require fresh per-engine investigation; the existence of an elevator asset is not validation.

**Conceptual architecture.** A deterministic route/transport core models `Stop`, `Service`, `Vehicle`, `Trip`, `Leg`, `Reservation` and `AgentJourney` with stable IDs. A capacity ledger owns seat transitions; a queue scheduler applies a documented FIFO/priority policy; a route planner computes feasible transfer legs and handles schedule windows; an event journal records boarding, departure, cancellation, disruption and arrival. Engine adapters translate route points and movement callbacks to the game's controller. A versioned save snapshot records the journey, queue position, reservation, vehicle occupancy and service timetable, then validates invariants on restore. UI/animations are optional adapter surfaces, never the source of truth.

**Core invariants.** Occupancy is between zero and capacity; an agent has at most one active seat/reservation for a leg; a cancelled reservation cannot board; no agent is both on board and in a waiting queue; each departure has one event identity; an interrupted journey ends in a defined `rerouting`, `waiting`, `completed` or `failed` state. Stable tie-breaking and seeded fixture clocks make replay deterministic. No real-time networking or persistent live-service dependency is in scope.

**Functional edge cases.** Simultaneous reservations for the last seat; delayed vehicle; missed transfer; inaccessible stop; service outage mid-ride; destination cancellation while boarded; vehicle removal; route cycle; queue starvation; save exactly between capacity allocation and animation callback; duplicate event replay; invalid or older snapshot; and an agent/nav controller that rejects a requested move. Each must produce a defined state and diagnostic event, not lost agents or overbooking.

| Candidate edition | Status | Shared core vs engine-specific work and commercial gate |
| --- | --- | --- |
| Godot 2D/3D | Research candidate | State-machine and test vectors may be shared; NavigationAgent, signals, serialization and scene integration differ. Compare paid/free Godot transport and crowd addons before choosing. |
| Unity 2D/3D | Research candidate | Share conceptual state/tests; NavMesh or 2D controller bridge, job/performance model and save hooks are specific. Compare Unity navigation/crowd/lift products. |
| Unreal 3D | Research candidate | Core schema may transfer; Mass/Smart Object/AI controller, Blueprint/C++ packaging and version maintenance are distinct. Compare Fab packages. |
| Roblox | Research candidate | Server authority, replication and rejoin persistence require a separate design and moderation/store review; no multiplayer promise. |
| GameMaker 2D | Research candidate | Separate path/state API and viable package format need proof. |
| Construct / GDevelop 2D | Research candidate | Separate event-system integration and extension rules need proof; may be rejected if no affordable adapter. |

All rows are untested. The first edition is chosen **after** comparing buyer pain, substitutes, feasibility and support cost, not by engine preference. Potential channels are Godot's free Asset Library for discovery, Unity Asset Store, Fab, Roblox Creator Store, itch.io or direct distribution only where the exact edition and seller rules allow it; no listing is approved.

### Sequenced milestones and deliverables

| ID | Dependency | Deliverable and completion evidence |
| --- | --- | --- |
| T1 market/engine selection | GDM-001 decision and owner-approved discovery | Dated competitor matrix for Godot, Unity and Unreal plus three target-team problem accounts; choose one engine/2D-or-3D edition or stop. |
| T2 behavior contract | T1 | State-transition table, event IDs, capacity/queue policy, save schema and 12 synthetic journey traces, including cancellations and disruptions. |
| T3 core spike | T2 and development authorization | Reproducible 20-agent/2-vehicle fixture on a stated machine and engine version; no overbooking or duplicate boarding; measured frame time and memory, not a universal performance claim. |
| T4 adapter | T3 | A sample game integrates existing navigation/controller callbacks without replacing its movement system; a second controller shape documents integration cost. |
| T5 recovery and diagnostics | T3–T4 | Save during boarding and transit, resume, replay a duplicate event, interrupt a service and compare deterministic final state; visual state inspector identifies agent, vehicle, reservation and reason for wait. |
| T6 buyer evaluation | T5 and consent | Three independent team evaluations compare native/free/paid alternatives, integration hours and support load; positive paid-pilot signal from two or documented alternative before commercial build. |
| T7 release preparation | T6 and owner launch approval | Versioned API, migration guide, test/demo project, license rights, channel review, measured support budget, price experiment and clear limitations. |

**Demonstration and economics.** Show several agents competing for the last seat, a missed transfer, a disrupted service and save/load during transit, with counters and invariant report visible. Compare against a basic lift/pathfinding demo to prove the additional behavior. Marketing may include useful setup documentation and a free bounded sample after rights review; no unsolicited messages or ads. Price and support cost remain unknown; the workbook's Godot US$39–79 idea is only a hypothesis. CAD0 is authorized for spending.

**Stop rule:** reject or narrow an edition if a free/paid existing system already meets the same behavior, adapter work requires rewriting buyer AI, deterministic save/recovery cannot be achieved, or measured support cost makes the proposed sale uneconomic. The next local Codex action, once GDM-001's decision is recorded, is a dated competitor/engine comparison sheet. No T1–T7 milestone is complete.
