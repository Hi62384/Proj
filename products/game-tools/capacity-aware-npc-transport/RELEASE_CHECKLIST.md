# Local release preparation (unfinished)

This file is a working checklist for an unpublished prototype. It does not authorize a release.

- [x] Keep coordinator and example in a separate project directory.
- [x] Check a copied `addons` folder in a clean local Godot 4.5.1 project.
- [x] Exercise synthetic multi-agent journeys, save/replay, availability changes, stale acknowledgments and selected physics scenes.
- [x] Provide local examples of navigation-adapter and game-owned-controller integration, with request validation and a small collision-platform transfer.
- [x] In the private temporary game, exercise physical CharacterBody boarding, capacity-two riders, crossing dispatch, safe-stop recovery, and reconstruction during crossing and recovery on Godot 4.4.1, 4.5.1 and 4.7.2. This remains a synthetic integration test, not an existing game.
- [ ] Validate both controller styles against a representative existing game, including movement cancellation, timeouts, recovery, body lifecycle and in-flight save/restore. The supplied controllers remain examples.
- [ ] Verify movement and recovery across disconnected navigation regions, realistic obstacles, multiple agents, save/restore and game-specific vehicle motion. The current physics scenes are small and scripted.
- [ ] Validate onboard cancellation in representative scenes and resolve or explicitly scope scene deletion integration, missed callbacks, and vehicle physical continuity.
- [ ] Establish practical performance, fairness and tested limits for the final implementation on representative hardware and scenes.
- [x] Run final-source regression checks: all 50 test scripts, copied add-on install/reinstall and headless editor marker checks passed on Godot 4.4.1, 4.5.1 and 4.7.2 for Windows x86-64. See the machine-readable report in `compatibility-results/2026-11-18-final-complete-source-50-tests.json`.
- [ ] Decide and publish an honest support matrix. Only the Windows x86-64 configurations above were tested; other platforms and versions remain untested and none is approved as a customer support promise.
- [ ] Decide a license and confirm rights and redistribution terms for every shipped file; the intended product's license has not been chosen. The local engine binary, prior third-party research fixtures and unrelated project assets are not part of the copied add-on.
- [x] Complete the local API, migration, support, known-limits and example documentation and audit its technical claims against the current tests. These drafts do not set support or distribution terms.
- [ ] Check the final files in a clean project and perform a human-facing visual review and acceptance run.
- [x] Prepare hash-manifested unpublished review snapshot `review-candidate-2026-11-18q/` for owner inspection. It is local to this workspace and not included in the GitHub branch; it is not licensed or approved for distribution.
- [ ] Obtain the owner's license and release decisions and separate approval before marketplace publication or any spending.

Do not describe synthetic timing as an FPS guarantee, assume purchase demand or claim a measured advantage over existing solutions. No price or distribution terms have been approved.
