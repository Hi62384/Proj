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
  "commercial_validation": "unvalidated",
  "evidence_basis": "public_official_and_competitor_research_no_verified_customer_sales",
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
  "next_action": "Build and test the scheduled 3D two-vehicle scenario with transfer and save/load, then compare the same trace and integration effort with native NavigationLink and FlowAI.",
  "last_reviewed": "2026-11-17",
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
    }
  ]
}
---
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

`Hi62384/Proj`, `main`, commit `6f2a420e9a1d7d5b44ec1759918e737059a6772e` inspected 2026-11-15. The existing canonical project is `business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-002-capacity-aware-npc-transport.md`, project ID `GDM-002`, niche `N-gdm-20261115`. Preserve active projects `GDM-001` and `GDM-003`; their actual jobs differ. Archive/research locations: `business_portfolio/archive/2026-11-15-legacy`, `archive/2026-11-15-taxonomy-view-v1` and `opportunity_library`. Do not create a new ID, new niche, duplicate project, or touch another chat's owned files.

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

Construct **two** demos in the same original Godot project. A baseline uses NavigationAgent/NavigationLink plus a minimal custom queue script; the proposed addon uses the transport core and two different movement-controller adapters. Record how many edge cases fail in baseline, implementation time, code modification burden and repeatable restart behavior. The tool passes its *technical differentiation* gate only if a vehicle's scheduled reservation and mid-ride save/recovery work more reliably with less integration effort. No survey or team evaluation is required.

**Kill/no-go:** if adding a FIFO array to a moving platform solves all target uses at lower complexity; if save/restore is inconsistent; if controllers need invasive rewrites; if paid checkout/discovery cannot be established affordably; or if support effort is disproportionate. Production polish alone does not rescue a missing market.

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
| T11 | 2–4 | T10 | Baseline comparison vs native/FlowAI; install from fresh project. | Meaningful advantage survives; otherwise pause/kill. |
| T12 | 3–6 | T11 pass | Package paid addon source and original demo, docs, licence, QA and release manifest. | Works after uninstall/reinstall; examples and version matrix honest. |
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

**Open first:** repository root `AGENTS.md`, `business_portfolio/SCHEMA.md`, `PROJECT_TEMPLATE.md`, this exact canonical file `business_portfolio/niches/digital-products/game-development-marketplaces/projects/gdm-002-capacity-aware-npc-transport.md`, `business_portfolio/research/SOURCE_REGISTER.json`, the selected niche's `NICHE.json`, and `docs/PORTFOLIO_MANAGER_WORKFLOW.md`. Inspect other active GDM IDs and the archives; do not assume their project folders are available for modification. Keep unrelated projects untouched.

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
