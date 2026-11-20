# Coordinator API and integration contract

This document describes the unpublished local prototype. All coordinator and adapter calls must be serialized on the scene's owning thread. `demo/transit_demo.gd` and `tests/test_navigation_adapter.gd` contain runnable examples.

## Configuration

Attach `addons/transit_coordinator/transit_coordinator.gd` to a Node and connect `transit_event` before calling `configure(config, run_id)`. The function returns a boolean and sets `last_error` when configuration fails. Use a distinct stable run ID for each independent simulation so event IDs do not collide across runs.

The configuration has exactly five fields:

```gdscript
var config = {
    "revision": "example-v1", "tick_unit": "simulation_tick",
    "stops": ["origin", "destination"],
    "vehicles": [{"id": "vehicle", "capacity": 4}],
    "services": [{"id": "outbound", "vehicle": "vehicle",
        "from": "origin", "to": "destination", "period": 8,
        "offset": 0, "duration": 2, "enabled": true}]
}
```

A service departs at ticks `offset + n * period`, for nonnegative integers `n`. Times and capacities are integers. Service occupancy uses half-open intervals and recurring services sharing a vehicle cannot overlap, including services initially marked disabled. Vehicle positioning and empty return travel are outside this model. Graph, stop, vehicle and service IDs use 1–64 ASCII letters, digits, `_`, `-` or `.`. The current graph limits are 256 stops, 256 vehicles, 1,024 services, 32 services per vehicle and a simulation horizon of one billion ticks. These are validation limits, not supported performance targets. Agent IDs follow the ledger's separate nonempty string rule with a maximum length of 128.

## Optional vehicle-continuity audit

`core/continuity_audit.gd` provides an advisory `audit(config, reposition, horizon)`. Supply a nested dictionary of conservative empty travel times in ticks, such as `{"destination": {"origin": 2}}`. It expands enabled services up to, but not including, the finite horizon, then checks that each vehicle has enough time between each consecutive scheduled arrival and departure to reposition. Unknown or invalid needed travel times return an error; conflicts report the services and ticks. The audit allows at most 10,000 ticks and 100,000 scheduled events.

A passing audit covers only those scheduled transitions in that finite interval. It does not check initial vehicle position, transitions beyond the horizon, future availability changes, acceleration, obstacles or whether the game actually moves a vehicle. Re-run it after schedule or availability changes, and verify physical readiness in the game before acknowledging boarding.

## Clock and events

Request a journey between ticks with `request_journey(agent, origin, destination)`. Each tick has three calls:

1. `begin_tick()` issues any alighting requests due at this tick.
2. Complete safe alighting and call `open_boarding()`; it allocates eligible seats in FIFO order and issues boarding requests.
3. Complete and acknowledge boarding, then call `finish_tick()` to depart and expire unacknowledged claims.

The game decides how much physical time to allow in each phase. If a passenger cannot alight in time, its occupied seat prevents a conflicting departure and a fresh request is issued later. An unacknowledged boarding claim expires. Service and stop availability may be changed between ticks; unavailable routes cause queued passengers to replan or fail explicitly. Onboard passengers affected by a disruption retain their seats and receive recovery requests.

Events are dictionaries with `id`, `tick`, `type`, `agent`, and `details`. A movement request contains the vehicle, service and seat token. Alighting additionally names a stop; recovery lists currently safe endpoints. Complete the physical action before calling the matching `acknowledge_boarding`, `acknowledge_alighting`, or `acknowledge_recovery` method with the exact agent, vehicle, token and request ID. For recovery also supply a listed, currently available safe stop. A false return means the acknowledgment was rejected; do not assume it changed the journey. Events and acknowledgments can be synchronous and reentrant. Tick phase changes, configuration and snapshots are rejected during event dispatch.

`change_destination` is available between ticks for supported active states. `cancel_journey` immediately cancels queued or unconfirmed boarding claims. For an onboard, alighting or stranded passenger, cancellation starts a safe recovery and the seat remains held until the game confirms the exit. A boarding-confirmed passenger must wait until departure before cancellation can be requested. If the game has verified that the physical agent has been destroyed, `remove_destroyed_agent` explicitly releases its claim or occupied seat. Never use that method as a substitute for safe recovery of an existing passenger.

Use `journey(id)` or `diagnose(id)` for an agent's current status and reason, and `inspect_vehicle(id)` for a copied ledger. These are observations, not mutation methods. Handle `journey_failed`, timeout and missing-agent cases in the game; the prototype does not decide how to rebuild a scene or move an NPC around an obstacle.

## Save and recovery

Call `save_snapshot()` outside event dispatch and store the returned `snapshot` with the game's trusted local persistence. `restore_snapshot(original_config, snapshot)` validates the original graph fingerprint and ledger/journey consistency before replacing live state. It does not migrate changed graphs or safely deserialize arbitrary untrusted objects. Version 5 is current; compatible version 4 data is upgraded on a copy, while versions 1–3 are unsupported. Restore can emit events saved in the pending event queue; deduplicate by event ID.

The coordinator does not save scene objects. Restore the physical world and agent/vehicle controllers separately. `pending_request(agent)` reconstructs an outstanding boarding, alighting or recovery request with its original event ID and token, while its reported tick is the current coordinator tick. Re-evaluate current safety, choose a target, and restart the movement controller. Do not assume a passenger has moved merely because the logical snapshot says a request exists.

## Game-owned controller bridge

`controller_bridge.gd` is an alternative for an existing game controller: it does not set body velocity, create navigation or call `move_and_slide()`. Configure it with the coordinator and connect `movement_requested(event)` to the game's own movement logic. Connect `request_withdrawn(agent, request_id, reason)` so the game can stop a movement when the coordinator expires, replaces or ends its request. Once movement finishes, call `complete_movement(event, arrival_check, safe_stop)`. The game-supplied `arrival_check(event)` must return a boolean only after verifying the actual passenger is aboard the intended vehicle or safely at the stop. The bridge rejects modified, stale and duplicate requests, rechecks current state after the callback and reports accepted or rejected completions through `movement_result`.

After restoring the coordinator and the game's scene separately, call `refresh_request(agent)` for each known agent with pending work; repeated refreshes do not emit duplicate requests. `detach()` disconnects the coordinator and withdraws pending requests so the game can stop movement. The bridge also detaches when it or its coordinator leaves the scene tree; withdrawal does not acknowledge a passenger or release a seat. Restore and validate the physical scene before resuming any movement. The bridge cannot verify the truth of the game's predicate or recover a destroyed game object on its own. `examples/game_owned_character.gd` and `tests/test_game_owned_controller.gd` show a small independent controller and collision-platform transfer; they are examples, not production obstacle or crowd handling.

## Optional navigation bridge

`navigation_adapter.gd` can drive a registered `CharacterBody3D` and `NavigationAgent3D` on the horizontal plane. Configure it with the coordinator, register the body and navigation agent, and call `move_for_request(event, target, arrival_check, safe_stop, speed, tolerance, timeout)`. The game must supply `arrival_check(body, event)` and return true only after it verifies actual physical boarding or a safe exit. For recovery, `safe_stop` must be in the request's safe-stop list. The bridge rejects requests that are no longer current and stops an active movement when its request expires, is superseded or its journey ends. Movement reports completion or failure through signals. A timeout or stale request does not release a seat; canceling movement does not cancel a journey.

The bridge is an example starting point, with fixed gravity, no saved movement state and no automatic vehicle motion, navigation mesh setup, collision avoidance policy, target selection or object lifecycle management. Games must provide and test those pieces. See `TEST_EVIDENCE.md` for tested scenarios and `RELEASE_CHECKLIST.md` for remaining limitations.
