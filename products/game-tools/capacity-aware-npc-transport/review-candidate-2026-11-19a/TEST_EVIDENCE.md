# Failure and edge-case evidence matrix

The rows below map existing automated checks to behaviors. They are small local fixtures, not a certification for every game scene. Run the individual scripts in `tests/` with Godot 4.5.1 and inspect output as well as the process status.

| Trigger | Observed behavior | Script |
|---|---|---|
| Overlapping recurring services for one vehicle | Invalid graph rejected. | `test_edges.gd` |
| Two services share a FIFO vehicle queue | Only eligible waiters are allocated; other waiters keep their place. | `test_edges.gd` |
| Boarding acknowledgment never arrives | Claim expires; stale token and request are rejected at the next window. | `test_journeys.gd` |
| Alighting acknowledgment is delayed | Occupied vehicle cannot board its next service; a new request supersedes the old one. | `test_edges.gd` |
| Physical exit is blocked | Passenger stays in alighting state; stale request is rejected after a tick; exit completes after obstacle removal. | `test_blocked_exit.gd` |
| Service fails with passengers onboard | Seats remain occupied until safe recovery; queued passengers reroute where a route exists. | `test_disruption.gd` |
| Transfer stop closes | Affected journey fails with an explicit reason; unrelated passenger continues. | `test_stops.gd` |
| Recovery stop closes or availability changes | Closed stop and old request are rejected; a refreshed request can be acknowledged at a safe stop. | `test_stops.gd` |
| Snapshot graph changes or seat ownership is corrupted | Restore rejects the incompatible or inconsistent data. | `test_journeys.gd` |
| Arrival predicate is false or request has expired | Adapter times out without acknowledging; an expired request is rejected before movement starts. | `test_adapter_safety.gd` |
| Passenger cancels while onboard | Seat remains held until safe recovery; cancellation intent survives restore and availability change. | `test_onboard_cancel.gd` |
| Physical agent is destroyed | Adapter reports failure; explicit game assertion releases the agent's claim or seat, and duplicates are rejected. | `test_adapter_deleted.gd`, `test_destroyed_agent.gd` |

Other tests cover a game-owned controller bridge with a single-passenger collision transfer, recreation of the game-owned character during boarding, recreation of the character and first platform during a ride, a finite 101-agent FIFO run without disruption, a synthetic 20-agent transfer with deterministic replay, a 20-agent navigation-link transfer without collision shapes, separate 20-agent one- and two-platform collision fixtures and six-agent and 20-agent staggered capacity-three two-platform transfers, all with agent-to-agent collision disabled, flat navigation boarding, horizontal and vertical collision platforms, a four-passenger platform, a safe-stop recovery, a cancelled passenger physically exiting and movement resumption after coordinator restore. These do not establish general obstacle avoidance, arbitrary crowd behavior, realistic vehicle return paths, broad engine compatibility, or game-level performance. See `RELEASE_CHECKLIST.md` for remaining work.
# Game-owned physical disruption continuation

An additional synthetic one-passenger fixture connects the example game-owned CharacterBody3D through the controller bridge to a translating collision platform. After boarding and riding, the service is disabled; an unverified recovery is rejected, and the seat remains occupied until the character walks onto the station and confirms recovery. This checks integration of the existing bridge and physical recovery paths, not customer-game behavior or crowd avoidance.

The subsequent disruption-restore fixture saves during the walk to a safe stop and recreates the passenger, platform, coordinator and bridge from saved state. On Godot 4.4.1, 4.5.1 and 4.7.2, it retained the occupied seat and pending request ID until the recreated controller reached the station and verified recovery. It passed in the product project and a separate freshly copied consumer fixture; the station and rest of the scene were retained in memory, so this does not establish full world persistence.

## Current-source compatibility

The current source's full 50-script suite, clean copied add-on install/reinstall and headless editor-marker checks passed on Windows x86-64 with Godot 4.4.1, 4.5.1 and 4.7.2. The three newest product tests cover injected demo mouse/keyboard events, game-owned physical disruption recovery, and reconstruction during physical recovery. The machine-readable report records a stable source fingerprint and per-version results at `compatibility-results/2026-11-18-final-complete-source-50-tests.json`. Physical input, customer-game integration, other operating systems and hardware, and performance guarantees remain unverified.
