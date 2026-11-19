# Local release preparation (unfinished)

This file is a working checklist for an unpublished prototype. It does not authorize a release.

- [x] Keep coordinator and example in a separate project directory.
- [x] Check a copied `addons` folder in a clean local Godot 4.5.1 project.
- [x] Exercise synthetic multi-agent journeys, save/replay, availability changes, stale acknowledgments and selected physics scenes.
- [x] Provide local examples of navigation-adapter and game-owned-controller integration, with request validation and a small collision-platform transfer.
- [ ] Validate both controller styles against a representative existing game, including movement cancellation, timeouts, recovery, body lifecycle and in-flight save/restore. The supplied controllers remain examples.
- [ ] Verify movement and recovery across disconnected navigation regions, realistic obstacles, multiple agents, save/restore and game-specific vehicle motion. The current physics scenes are small and scripted.
- [ ] Validate onboard cancellation in representative scenes and resolve or explicitly scope scene deletion integration, missed callbacks, and vehicle physical continuity.
- [ ] Establish practical performance, fairness and tested limits for the final implementation on representative hardware and scenes.
- [ ] Complete final-source regression checks and define an honest support matrix. Prior Windows x86-64 tests cover Godot 4.4.1, 4.5.1 and 4.7.2; other platforms and versions remain untested.
- [ ] Decide a license and confirm rights and redistribution terms for every shipped file; the intended product's license has not been chosen. The local engine binary, prior third-party research fixtures and unrelated project assets are not part of the copied add-on.
- [ ] Complete API, migration, support, known-limits and example documentation; audit claims against evidence.
- [ ] Check the final files in a clean project and perform a human-facing visual review and acceptance run.
- [ ] Prepare a reviewable release candidate and obtain the owner's separate approval before publication or any spending.

Do not describe synthetic timing as an FPS guarantee, assume purchase demand or claim a measured advantage over existing solutions. No price or distribution terms have been approved.
