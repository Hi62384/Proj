# Compatibility evidence — local development

Status: unpublished development build. These are observed checks, not a promise that all games, hardware or platforms are supported. No engine executable is included in the add-on or a review snapshot.

| Engine on Windows x86-64 | Full 45-script baseline | Final-source 14-test smoke | Clean install / reinstall | Headless editor marker | Two later restore fixtures |
|---|---|---|---|---|---|
| Godot 4.4.1 stable (`49a5bc7b6`) | Pass | Pass | Pass | Pass | Pass individually |
| Godot 4.5.1 stable (`f62fdbde1`) | Pass | Pass | Pass | Pass | Pass individually |
| Godot 4.7.2 stable (`ed1daf0bf`) | Pass | Pass | Pass | Pass | Pass individually |

The full baseline used source fingerprint `12bb93666047101f186cc4f7b4a0de407e149352a3a67b1980a10e3364319498` for all three versions. The exact output and executable fingerprints are recorded in the local machine-readable reports. After the full run, two restore tests were added and the smoke-runner selection was expanded. A per-file comparison confirmed no change to the add-on, demo or example controller. Those two tests passed independently on each version. The final-source 14-test smoke, install/reinstall and editor marker checks also passed on each version with source fingerprint `444ff8bd3b674f2a82356596f09b03649c4393cef0f74362fff075fd44d0b281`. The complete 47-script suite subsequently passed on all three versions against the staged `review-candidate-2026-11-18j` source.

A separate temporary consumer project copied the add-on and example game-owned controller. It completed a one-passenger, two-platform collision transfer, reconstructed the character during boarding, and reconstructed both the character and first platform mid-ride, on each version. The second platform and rest of the scene remained in memory; this is a synthetic original controller, not an integration with an existing customer's game or proof of arbitrary game-world persistence.

At 1152×648, rendered demo images on the tested NVIDIA OpenGL compatibility renderer were inspected. After a HUD grouping defect was fixed, the demo's pause/resume, save/load and service-enable/disable button signals were invoked programmatically and passed their state checks on each version. This is not a hands-on mouse/keyboard, accessibility, scaling, multiplayer or visual-editor acceptance test. The marker plugin's registration, recognition and redraw were exercised headlessly. In one instrumented 4.5.1 editor capture, a faint cyan marker line appeared offset from the world axes; unselected visibility was poor at that zoom. A warning in the initial capture was traced to the temporary fixture's transformed scene root and disappeared when the fixture was corrected.

The sandbox emitted a root-certificate-store warning on offline Godot runs. These checks do not use network certificates and do not establish certificate behavior outside this sandbox. The engine releases are in Godot's official archives: [4.4.1](https://godotengine.org/download/archive/4.4.1-stable/), [4.5.1](https://godotengine.org/download/archive/4.5.1-stable/) and [4.7.2](https://godotengine.org/download/archive/4.7.2-stable/). The additional local archives were checksum-verified against official Godot release data before extraction; they were not bundled or installed into the operating system.

## Reproduce

Run `python tools/run_compatibility.py --godot <console-executable> --output <new-report-name>` for the documented smoke set, or add `--full` to run every `tests/test_*.gd`. Repeat `--godot` for multiple engines. Reports are written locally under `compatibility-results/`, refuse to overwrite existing reports, include source and engine executable fingerprints, and fail if the source changes during the run. The runner rejects script and parse errors even if Godot returns zero.

Other OSes, CPU architectures, graphics drivers, engine versions and external game controllers remain untested. The owner has not selected a license or authorized publication, and no claims of marketplace eligibility, customer demand, comparative advantage or game-level performance follow from these tests.
