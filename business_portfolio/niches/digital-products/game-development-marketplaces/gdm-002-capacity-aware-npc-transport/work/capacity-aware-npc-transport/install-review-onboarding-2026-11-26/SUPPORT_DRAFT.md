# Support and troubleshooting draft

Status: unpublished development build. The maintainer, support channel, response times, license and distribution terms have not been established. Do not publish this draft as a promise of support.

## Before reporting a problem

Record the Godot version and platform, the add-on revision, a minimal sanitized graph configuration, the sequence of calls and event types, and the relevant non-sensitive log messages. A reproducible project using original assets is more useful than a screenshot alone. Do not include private project files, account information, customer data or credentials in an unsolicited report.

## Common symptoms

- **Configuration returns false.** Check `last_error`, required exact field names, unique IDs, valid endpoints, positive capacities, schedules and overlaps between services sharing a vehicle. Disabled services still participate in overlap validation.
- **A passenger stays queued.** Inspect `diagnose(agent)` and `inspect_vehicle(vehicle)`. Confirm that the service is enabled, the stop is accessible, the departure tick has arrived, and the platform is free. Routing does not predict future capacity.
- **Boarding is requested but no one departs.** Ensure the game calls `acknowledge_boarding` only after verifying the passenger actually boarded and before `finish_tick()`. An unacknowledged claim expires. A stale token or event ID is rejected.
- **A vehicle will not take another passenger.** A passenger who has not safely alighted or recovered retains the occupied seat. Complete the current request using its current ID and token; do not acknowledge an action that did not happen.
- **The game-owned controller did not receive a request.** Connect and configure the bridge before advancing the coordinator; after restoring the scene and coordinator, call `refresh_request(agent)`. Handle `request_withdrawn` by stopping obsolete game movement, and return a boolean from the physical-arrival predicate. The bridge never moves the body or verifies a predicate on the game’s behalf.
- **The optional adapter times out.** Check the navigation mesh, target, body dimensions, movement speed and game-supplied physical arrival predicate. The adapter does not create navigation, choose safe stops, move vehicles or decide recovery policy. Inspect its failure signal and arrange a game-specific response.
- **The NPC was destroyed.** Stop any adapter movement and unregister it. After the game confirms that the physical agent is gone, call `remove_destroyed_agent`; do not use this shortcut for an existing passenger.
- **Restoring fails.** Use the original matching configuration, a trusted snapshot and a supported version. Current format is version 5; compatible version 4 is upgraded, and versions 1–3 do not migrate. A mismatched graph or inconsistent ledger is rejected. Preserve the original save before experimenting.
- **A restored passenger is not moving.** Restore the scene separately and use `pending_request(agent)` to reconstruct the current logical request. Reassess the physical world, select a safe target and restart the movement controller. Deduplicate any restored pending event by request ID.

## Escalation evidence

A useful reproduction identifies expected and observed states, current tick and phase, relevant event IDs and reasons, and the smallest graph that reproduces the issue. Confirm that the problem occurs in the same engine version and with no game-specific changes before attributing it to the coordinator. Keep the original save and logs; do not repeatedly replay any real external action.
