# Local physical transfer measurement — 2026-11-26

Unpublished development evidence; not a performance guarantee.

The temporary project `temporary-independent-transit-game` ran `measure_staggered_twenty_physics.gd` using standard Godot 4.7.2 on Windows x86-64. It is an instrumented copy of the product's existing staggered physical-transfer test: 20 passengers, two collision platforms, capacity three, seven scripted cohorts, fixed paths, and passenger-to-passenger collisions disabled. The fixture passed all its existing assertions. No rendering or navigation-agent crowd simulation was included. Other background work, including an editor visual capture, ran concurrently; this was not an isolated benchmark.

The script sampled Godot's `TIME_PHYSICS_PROCESS` monitor once per physics frame, converted seconds to milliseconds and sorted the samples. This is the engine's physics-process monitor for this scenario, not total frame time, GPU time, customer performance, or an add-on-only measurement. One run produced 4,761 samples, mean 1.849 ms, 95th percentile 10.141 ms, and maximum 15.704 ms. Elapsed wall time was 79.223 s. The known root-certificate-store warning was emitted. A sample is not independent, and no repeatability or other hardware claim follows.

Reproduce with a standard Godot console executable: `godot --headless --path <temporary-independent-transit-game> --script res://measure_staggered_twenty_physics.gd`, using isolated Godot user-data directories. Retain the PASS line, measurement JSON, machine and concurrent-load context when comparing runs. Broader game-level performance, collisions among passengers and navigation-agent scaling remain unverified.


## Blocked navigation and recovery — additional single run

The separate `temporary-install-review-game-2026-11-26/measure_blocked_crowd.gd` instruments its four-passenger blocked-exit and coordinator-restore case with the exact earlier install-review add-on. On standard Godot 4.7.2, Windows x86-64, one headless run passed all existing assertions. For 721 physics-frame samples of Godot's `TIME_PHYSICS_PROCESS` monitor it recorded a mean of 6.224 ms, a 95th percentile of 31.027 ms and a maximum of 31.027 ms; elapsed wall time was 11.880 s. The root-certificate-store warning persisted.

The physics monitor can report repeated/coarse values, so the sample distribution must not be interpreted as independent per-frame measurements or an FPS guarantee. The run includes navigation, physics and scripted game logic, but excludes rendering and is not isolated from unrelated system activity. It is one fixed scene with one obstacle and four passengers, not evidence of general scaling or a supported workload. Reproduce with `godot --headless --path <temporary-install-review-game-2026-11-26> --script res://measure_blocked_crowd.gd` and isolated user data.


## Blocked-navigation version matrix — 2026-11-26

The same instrumented four-passenger scenario was run once each, sequentially, on standard Godot 4.4.1, 4.5.1 and 4.7.2. All three runs passed; each took approximately 11.9 seconds and sampled the same coarse engine monitor. Raw measurements, executable fingerprints, fixture fingerprint and known warning are recorded in `PERFORMANCE_BLOCKED_MATRIX_2026-11-26.json`. This is not a controlled engine comparison: other host activity was not isolated, the monitor values can repeat, rendering was disabled, and there was only one run per version. The measurements do not establish FPS or a supported crowd size.


## Twenty-agent navigation-platform probe — 2026-11-26

`temporary-install-review-game-2026-11-26/measure_navigation_twenty.gd` adapts a product fixture with 20 navigation agents, one scripted moving collision platform, fixed parallel approach lanes, passenger-to-passenger collisions disabled and scripted alighting. Three sequential headless Godot 4.7.2 runs on this Windows machine passed the assertions. `PERFORMANCE_NAVIGATION_TWENTY_2026-11-26.json` contains the results and source/executable fingerprints. Two runs recorded very large coarse physics-monitor readings (maxima 783.942 ms and 564.197 ms); the third maximum was 10.124 ms. Elapsed times were 9.896, 8.507 and 7.868 seconds.

To investigate, a second instrumented fixture, `diagnose_navigation_twenty.gd`, recorded the times of monitor observations at or above 50 ms. Three subsequent runs passed and recorded none, with maxima between 7.629 and 9.682 ms. See `PERFORMANCE_NAVIGATION_DIAGNOSTIC_2026-11-26.json`. Host activity was uncontrolled, and the monitor can repeat cached/coarse values. These runs do not identify the cause, establish whether the earlier readings represent actual frame hitches, or prove a fix. Keep workload/performance acceptance open; do not claim an FPS, capacity or engine-comparison guarantee. No rendering, arbitrary routes or interacting passenger collisions were measured.


A further three sequential 4.7.2 runs used `diagnose_navigation_intervals.gd` to record elapsed wall-clock time between physics callbacks as well as the coarse monitor. All passed; the largest observed callback intervals were 20.866, 21.683 and 21.769 ms, and no interval exceeded 100 ms in these three runs. See `PERFORMANCE_NAVIGATION_INTERVALS_2026-11-26.json`. This follow-up did not reproduce the original large readings. Callback intervals include scheduling and are not rendered FPS or add-on-only timings. The initial variability remains unexplained; do not treat the follow-up as proof that the issue cannot recur.


## Monitor interpretation source

Godot's official `Performance` documentation, checked 2026-11-26, describes `TIME_PHYSICS_PROCESS` as the time for a physics frame and cautions that some built-in monitors can lag updates by up to one second: https://docs.godotengine.org/en/latest/classes/class_performance.html . It does not establish that these particular large readings were caused by delayed updates. Repeated samples and subsequent non-reproduction are reasons to avoid interpreting them as a precise count of slow frames, not proof that no hitch occurred.


## Cross-version callback interval follow-up

`PERFORMANCE_NAVIGATION_INTERVAL_MATRIX_2026-11-26.json` records two sequential headless runs per standard Godot 4.4.1, 4.5.1 and 4.7.2 on the same Windows machine, using `diagnose_navigation_intervals.gd`. All six scenarios passed. One 4.4.1 run recorded six physics-callback intervals over 100 ms, with a maximum of 240.286 ms; the other five runs recorded no interval over 100 ms. Coarse physics-monitor readings of at least 50 ms appeared in all six runs. The raw report includes the individual maximum intervals, sample counts and executable/fixture fingerprints.

Unlike the previous follow-ups, this confirms that longer wall-clock callback gaps can occur in this environment; it does not identify whether the game, engine, OS scheduling, host contention or another factor caused them. Godot physics callbacks are not rendered frames. The test has no rendering, uses a fixed scripted scene and does not establish game FPS, general crowd scalability or an engine ranking. Performance acceptance remains open.


## Host-load follow-up

`PERFORMANCE_NAVIGATION_HOST_CORRELATION_2026-11-26.json` records three more sequential runs on standard Godot 4.4.1 and three on 4.7.2 while sampling overall host CPU and the Godot process tree at approximately 0.2-second intervals. All six functional scenarios passed. One 4.4.1 run recorded a 133.2 ms maximum callback interval and one interval above 100 ms; the other five did not. Sampled peak overall host CPU ranged from 70.8% to 100% across runs; process-tree CPU uses a one-core 100% scale and can exceed 100%.

These are coarse, run-level peak observations, not timestamp-correlated CPU data for the individual callback gap. The sampler can miss brief peaks or subprocesses and itself adds overhead. High host utilization is observed, but these results cannot establish that it caused a specific gap or exclude an engine/add-on issue. Runs are headless on one Windows host with a fixed scenario; no rendering FPS, general scalability, cross-engine ranking or performance guarantee is established.


## Adapter callback diagnostic

An isolated copy of the 20-agent fixture wrapped the navigation adapter's physics callback with a wall-clock timer; see `temporary-adapter-profile-2026-11-26/` and `PERFORMANCE_ADAPTER_PROFILE_2026-11-26.json`. Four sequential headless Godot 4.4.1 runs passed. No run reproduced a physics-callback gap over 100 ms; the largest measured adapter-callback durations were 5.781, 11.392, 10.109 and 5.954 ms. Two runs each had one adapter callback at or above 10 ms.

The wrapper changes the copied source and adds measurement overhead. It times the adapter callback, including work invoked from it, but excludes other engine physics, rendering and unrelated game work. Because the original long gap did not recur during these runs, the measurements do not establish or exclude the adapter as its cause. Host activity remained uncontrolled and this is not an FPS or crowd-capacity guarantee.


## Timestamped host follow-up

`temporary-install-review-game-2026-11-26/diagnose_navigation_host_timeline.gd` emits a wall-clock timestamp for physics-callback gaps over 100 ms. Five sequential headless runs on standard Godot 4.4.1 passed while sampling system and Godot process-tree CPU approximately every 100 ms. No gap over 100 ms occurred, so there were no events to correlate; maximum observed intervals were 31.233, 21.291, 20.786, 54.924 and 47.146 ms. Raw summary and fixture hash are in `PERFORMANCE_NAVIGATION_GAP_TIMELINE_2026-11-26.json`.

This does not explain or invalidate the earlier gaps. CPU samples, logging and the diagnostic alter timing; host activity remained uncontrolled, and a correlation would not prove causation. The fixture excludes rendering and uses a fixed synthetic scene. It is not an FPS, general scalability or release-acceptance guarantee.
