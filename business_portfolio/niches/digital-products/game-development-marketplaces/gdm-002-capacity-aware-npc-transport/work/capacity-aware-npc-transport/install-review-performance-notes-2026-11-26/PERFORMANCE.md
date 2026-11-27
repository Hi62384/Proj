# Performance and scope — local review

This file describes local observations, not a performance guarantee, supported NPC count, benchmark comparison or license. This review is unlicensed and not approved for distribution.

The coordinator does not move vehicles or create a crowd-avoidance policy. The included physical and cooperative-yield examples use small, fixed, game-owned controllers and routes. Profile the actual game's navigation, movement, collisions, rendering and target devices before choosing a workload. Graph input-validation limits in `API.md` are not performance targets.

The local Windows development fixtures exercised up to 20 passengers in constrained headless scenarios. Some physics-callback intervals exceeded 100 ms in standard Godot 4.4.1 on one machine; later runs often did not reproduce them. The cause is unknown, and the tests did not measure rendered FPS. These observations neither establish an add-on defect nor prove the absence of one. No performance or compatibility claim is made for arbitrary projects, hardware or other operating systems.

For integration, start with the included examples, verify physical arrival before acknowledging transit actions, and increase your own workload gradually. Check stalled requests, seat retention, callback timing and visual frame pacing under representative conditions. Preserve logs and a minimal reproduction for any issue. The support terms for this unapproved review have not been established.
