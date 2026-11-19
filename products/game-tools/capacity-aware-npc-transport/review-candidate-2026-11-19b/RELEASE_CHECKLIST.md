# Local release preparation (unfinished)

This file is a working checklist for an unpublished prototype. It does not authorize a release.

- [x] Keep coordinator and example in a separate project directory.
- [x] Check a copied `addons` folder in a clean local Godot 4.5.1 project.
- [x] Exercise synthetic multi-agent journeys, save/replay, availability changes, stale acknowledgments and selected physics scenes.
- [x] Provide local examples of navigation-adapter and game-owned-controller integration, with request validation and a small collision-platform transfer.
- [x] In the private temporary game, exercise physical CharacterBody boarding, capacity-two riders, crossing dispatch, safe-stop recovery, and reconstruction during crossing and recovery on Godot 4.4.1, 4.5.1 and 4.7.2. This remains a synthetic integration test, not an existing game.
- [x] Exercise the navigation adapter and game-owned controller bridge in synthetic product tests for movement cancellation/supersession, timeouts, safe recovery, body/coordinator lifecycle and in-flight request restore. They remain examples; this does not validate an existing game's controller.
- [ ] Validate both controller styles against a representative existing game with rights-cleared code/assets, including movement cancellation, timeouts, recovery, body lifecycle and in-flight save/restore.
- [x] Verify the navigation adapter times out without false boarding when the vehicle is in a disconnected navigation region; the coordinator retains the seat claim until the unconfirmed boarding window closes. This is a synthetic safe-failure test.
- [x] Test connected-mesh navigation success with adapter restore, disconnected-region safe timeout, crowd/obstacle interruption fixtures, and physical multi-agent dispatch/reconstruction in synthetic scenes. These are bounded fixtures, not representative-world routing.
- [ ] Validate successful movement and recovery across connected/disconnected navigation regions, realistic obstacles, multiple agents, save/restore and game-specific vehicle motion in a representative rights-cleared game.
- [x] Verify the synthetic onboard-cancellation, explicitly confirmed destroyed-agent release, missed/stale callback and seat-retention contracts in product tests; document that physical continuity and scene lifecycle stay game-owned.
- [ ] Validate cancellation, scene deletion, missed callbacks and vehicle physical continuity in representative game scenes.
- [x] Measure coordinator-only timing at 20, 100 and 500 agents across Godot 4.4.1, 4.5.1 and 4.7.2, and verify 101-agent FIFO completion without disruptions; results and limits are in `COMPATIBILITY.md`.
- [ ] Establish practical performance, fairness and tested limits for the final implementation on representative hardware and scenes.
- [x] Run final-source regression checks: all 50 product test scripts, the private 34-case temporary integration suite, copied add-on install/reinstall and headless editor marker checks passed on Godot 4.4.1, 4.5.1 and 4.7.2 for Windows x86-64. The product suite report is `compatibility-results/2026-11-18-final-complete-source-50-tests.json`; temporary-project details are in the GDM-002 portfolio result.
- [x] Record a provisional tested-configuration matrix in `COMPATIBILITY.md`; it is evidence only and makes no customer support commitment.
- [ ] Owner decides any customer-facing support promise after broader platform and game validation.
- [x] Inventory the local review snapshot's file formats and dependency declarations; no binary/media assets or GDExtension declaration were found. This is not a copyright or redistribution determination.
- [ ] Decide a license and confirm rights and redistribution terms for every shipped file; the intended product's license has not been chosen. The local engine binary, prior third-party research fixtures and unrelated project assets are not part of the copied add-on.
- [x] Complete the local API, migration, support, known-limits and example documentation and audit its technical claims against the current tests. These drafts do not set support or distribution terms.
- [x] Check the current add-on copy through clean install/reinstall and headless editor-marker tests on all three tested Godot versions.
- [ ] Perform human-facing mouse/keyboard, rendered interaction and editor-gizmo visual acceptance; headless checks and prior captures do not satisfy this step.
- [x] Prepare a hash-manifested unpublished local review snapshot; the current snapshot name is listed in `REVIEW_INDEX.md`. Snapshots stay workspace-local, unlicensed and unapproved for distribution.
- [ ] Obtain the owner's license and release decisions and separate approval before marketplace publication or any spending.

Do not describe synthetic timing as an FPS guarantee, assume purchase demand or claim a measured advantage over existing solutions. No price or distribution terms have been approved.
