# Compatibility evidence — local development

Status: unpublished development build. These are observed checks, not a promise that all games, hardware or platforms are supported. No engine executable is included in the add-on or a review snapshot.

| Engine on Windows x86-64 | Product suite (50 scripts) | Clean add-on install / reinstall | Headless editor marker | Temporary integration (34 cases) | Temporary main-scene smoke (120 frames) |
|---|---|---|---|---|---|
| Godot 4.4.1 stable (`49a5bc7b6`) | Pass | Pass | Pass | Pass | Pass |
| Godot 4.5.1 stable (`f62fdbde1`) | Pass | Pass | Pass | Pass | Pass |
| Godot 4.7.2 stable (`ed1daf0bf`) | Pass | Pass | Pass | Pass | Pass |

This is a provisional evidence matrix, not a customer support promise. All temporary-game checks use a private synthetic project and fixed scenes. Other operating systems, architectures, graphics drivers and representative customer games are untested.

### Background integration and coordinator load — 2026-11-19 local time

The private synthetic temporary game's complete 34-case suite passed headlessly with isolated user data on all three engine versions above. Its main scene also ran for 120 frames and exited successfully on each version. No test errors occurred; offline runs emitted the known root-certificate-store warning. The direct run with default Godot user data could not create `user://logs`; isolated temporary user data resolved this without changing the normal profile.

The product's synthetic `tests/measure_coordinator.gd` was run on the same Windows x86-64 machine for each engine. It completed six repetitions at each size (five timed totals after one warm-up) with zero failures. Across the three engine versions, the five-run total-duration ranges were 0.88–1.85 ms for 20 agents, 6.01–12.36 ms for 100 agents, and 81.82–122.92 ms for 500 agents. The maximum individual tick observed across repetitions ranged from 0.465–0.543 ms, 1.051–1.555 ms, and 2.977–4.425 ms respectively. The separate 101-agent FIFO test passed without disruptions.

These numbers measure coordinator logic in a small headless synthetic schedule. They exclude scene physics, navigation, rendering, other game systems and representative hardware variation. They are not FPS figures, capacity guarantees, fairness guarantees or customer support limits. The 101-agent test establishes FIFO completion for its fixed no-disruption case only; general starvation/fairness and performance in representative games remain open.

### Final-source run — 2026-11-18 local time

The current source fingerprint `8d34370bb4e2b8e38e28ffa696ea371de7644f4710b2808e94e1f7ca9814026b` passed all 50 `tests/test_*.gd` scripts, copied add-on install/reinstall, and headless editor marker checks on all three versions above. The run verified the source fingerprint was unchanged. Its machine-readable report is `compatibility-results/2026-11-18-final-complete-source-50-tests.json`. This matrix covers Windows x86-64 only and does not establish support for other platforms or representative customer games.

The full baseline used source fingerprint `12bb93666047101f186cc4f7b4a0de407e149352a3a67b1980a10e3364319498` for all three versions. The exact output and executable fingerprints are recorded in the local machine-readable reports. After the full run, two restore tests were added and the smoke-runner selection was expanded. A per-file comparison confirmed no change to the add-on, demo or example controller. Those two tests passed independently on each version. The final-source 14-test smoke, install/reinstall and editor marker checks also passed on each version with source fingerprint `444ff8bd3b674f2a82356596f09b03649c4393cef0f74362fff075fd44d0b281`. The complete 47-script suite subsequently passed on all three versions against the staged `review-candidate-2026-11-18j` source.

A separate temporary consumer project copied the add-on and example game-owned controller. It completed a one-passenger, two-platform collision transfer, reconstructed the character during boarding, and reconstructed both the character and first platform mid-ride, on each version. The second platform and rest of the scene remained in memory; this is a synthetic original controller, not an integration with an existing customer's game or proof of arbitrary game-world persistence.

The synthetic game-owned controller also boards a collision platform, rides it, and walks to a safe stop after the service is disabled. The disruption fixture rejects an unverified recovery and checks that the occupied seat is retained until the controller reaches the station and confirms recovery. It does not model arbitrary dispatch, crowd movement or an existing customer's game.

In a further one-passenger fixture, a save during physical recovery was used to recreate the controller, platform, coordinator and bridge. The restored pending request retained its ID and occupied seat; the controller then completed physical recovery. The fixture passed separately on all three versions both in the product project and in a fresh temporary project containing copied add-on and example source. The surrounding station scene remained in memory during reconstruction; this is not a general world persistence test.

At 1152×648, rendered demo images on the tested NVIDIA OpenGL compatibility renderer were inspected. After a HUD grouping defect was fixed, the demo's pause/resume, save/load and service-enable/disable button signals were invoked programmatically and passed their state checks on each version. This is not a hands-on mouse/keyboard, accessibility, scaling, multiplayer or visual-editor acceptance test. The marker plugin's registration, recognition and redraw were exercised headlessly. In one instrumented 4.5.1 editor capture, a faint cyan marker line appeared offset from the world axes; unselected visibility was poor at that zoom. A warning in the initial capture was traced to the temporary fixture's transformed scene root and disappeared when the fixture was corrected.

After the 47-script staged run, the editor-only marker material was changed for better unselected visibility, and the matching editor smoke instrumentation was updated. The changed plugin passed editor registration, recognition and redraw on all three versions. A capture on 4.5.1 showed a more visible line at the same viewpoint; this is not broad visual acceptance. Runtime coordinator and controller source were unchanged by this later editor-only change.

The demo's actual viewport controls were also exercised in a headless test using injected mouse events and a focused keyboard `ui_accept` action on 4.4.1, 4.5.1 and 4.7.2. The fixture checks pause/resume, save/load and service controls, including their between-ticks restriction. It does not exercise a physical input device, accessibility, scaling or the operating system's window manager.

The sandbox emitted a root-certificate-store warning on offline Godot runs. These checks do not use network certificates and do not establish certificate behavior outside this sandbox. The engine releases are in Godot's official archives: [4.4.1](https://godotengine.org/download/archive/4.4.1-stable/), [4.5.1](https://godotengine.org/download/archive/4.5.1-stable/) and [4.7.2](https://godotengine.org/download/archive/4.7.2-stable/). The additional local archives were checksum-verified against official Godot release data before extraction; they were not bundled or installed into the operating system.

## Reproduce

Run `python tools/run_compatibility.py --godot <console-executable> --output <new-report-name>` for the documented smoke set, or add `--full` to run every `tests/test_*.gd`. Repeat `--godot` for multiple engines. Reports are written locally under `compatibility-results/`, refuse to overwrite existing reports, include source and engine executable fingerprints, and fail if the source changes during the run. The runner rejects script and parse errors even if Godot returns zero.

Other OSes, CPU architectures, graphics drivers, engine versions and external game controllers remain untested. The owner has not selected a license or authorized publication, and no claims of marketplace eligibility, customer demand, comparative advantage or game-level performance follow from these tests.
