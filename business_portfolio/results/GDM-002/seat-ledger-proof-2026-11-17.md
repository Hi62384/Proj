# GDM-002 seat-ledger proof — 2026-11-17

An original, local Godot GDScript prototype is in `products/game-tools/gdm-002-transit-proof/`. It models one FIFO queue per vehicle, finite capacity shared by reservations and boarded passengers, cancellation, idempotent boarding rejection and validated snapshots. It is an early technical proof, not an addon or release.

Godot 4.7.2 stable (official Windows x64 binary), headless, ran `--path products/game-tools/gdm-002-transit-proof --script res://test_transit.gd`: exit 0, `Transit proof: PASS (0 failures)`. The engine also reported inability to write its user log and read the root certificate store in the sandbox. The fixture requested twenty synthetic agents across two independent vehicles and checked five reservations and five waiting per vehicle. It also checked FIFO contention, cancellation and late callback, duplicate boarding, snapshot round trip, overcapacity and duplicate ownership rejection.

No 3D scene, motion, schedule, transfers, disruption, save-to-disk, performance benchmark, integration comparison or paid release exists. This does not establish a market or show an advantage over alternatives. The local official download was used as a development tool; no third-party code was bundled.

Godot's [NavigationLink documentation](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationlinks.html) describes path connections and says game code must implement specialized traversal. [FlowAI's README](https://github.com/a6xdev/FlowAI) describes moving navigation areas and an agent component. Neither source inspection nor this unit fixture is an equivalent scenario test: a timed, same-scenario baseline and FlowAI evaluation remain necessary.
