# GDM-002 bounded tick measurement — 2026-11-18

A local measurement on AMD Ryzen 7 6800H, Windows NT 10.0.19045.0 and Godot 4.5.1 stable official (`f62fdbde1`) timed calls to `step()` in the fixed 20-passenger, three-service synthetic fixture. The command was Godot headless with the proof project as `--path` and `--script res://research/test_tick_measurement.gd`, with `APPDATA` redirected to a writable local test directory. It exited 0; Godot warned that it could not read the root certificate store.

The test used two warmup runs and 20 measured runs per implementation and mode, alternating execution order. It collected wall-clock microseconds for each active schedule tick through completion, excluding rendering, physics, external controllers, disk I/O and integration work. The default mode completed in 46 ticks per run; the optional guarded mode completed in 36. Candidate and DIY traces matched within each mode. Percentiles use nearest rank across all active ticks from those runs.

| Fixture and mode | Samples | Mean µs | Median µs | P95 µs | P99 µs | Maximum µs |
|---|---:|---:|---:|---:|---:|---:|
| Ledger, default | 920 | 26.89 | 11 | 129 | 173 | 379 |
| DIY, default | 920 | 25.90 | 8 | 145 | 195 | 293 |
| Ledger, guarded | 720 | 423.21 | 58 | 3,146 | 4,534 | 5,518 |
| DIY, guarded | 720 | 389.36 | 63 | 2,562 | 3,691 | 4,941 |

No measured tick exceeded 16,667 µs in this run. That is not an FPS result or a guarantee of a 60 FPS game: the test excludes almost all game work, uses one small fixed graph and machine, and observed maxima are not worst-case bounds. The guarded policy's mean tick cost in this run was roughly 16 times the ledger default, but the modes perform different work and complete in different numbers of ticks. This is one local measurement, not a representative benchmark, scaling claim or comparison of developer integration effort.

The guarded algorithm assumes known future inputs. A separate documented disruption counterexample delayed one passenger despite the static guard, and the DIY version reproduced the selected guarded traces. Neither measured runtime nor the test establishes a reliability or integration-effort advantage. The technical gate remains unpassed and packaging remains no-go. The work interval from 21:07:16 to 21:07:55 UTC was approximately 39 seconds of wall time; prior focused effort against the six-hour cap remains unknown. No spending, outreach, publication or sales occurred.

## Follow-up: within-tick projection cache

An opt-in guard optimization now reuses the unchanged baseline projection within a tick and invalidates it after an accepted switch. An uncached copy of each pre-optimization fixture is retained under `research/` as the comparison reference. The cache is transient and is not part of saved state. `research/test_guard_cache_equivalence.gd` compared each cached version with its uncached reference on 50 seeded configurations, including a service disruption in half the cases. It compared passenger states and event traces after each of 150 ticks and passed. Across those cases the candidate and DIY each performed 92 baseline projections with caching versus 128 without it. These are bounded fixture checks, not proof for arbitrary graphs, concurrency or controllers.

`research/test_guard_cache_measurement.gd` then measured 20 runs after two warmups on the same machine and Godot version described above, alternating order. Each run had 36 active ticks. In this particular run, the candidate cached/uncached means were 495.19/516.90 µs per tick and P95s were 3,160/3,287 µs; DIY cached/uncached means were 446.52/480.98 µs and P95s were 2,842/2,889 µs. Each cached version performed 140 baseline projections across the measured runs versus 180 for its reference. Traces matched within each pair. One DIY uncached sample reached 19,109 µs; the other three observed maxima were 5,417–10,621 µs. This is a single noisy headless run, not a statistically established speedup, worst-case bound, FPS measurement or integration-effort comparison.

The known unexpected-disruption counterexample still reproduces: the guarded passenger arrives at tick 12 versus tick 8 without the earlier switch. The guard remains experimental and disabled by default, the DIY version received the same optimization, and the technical differentiation gate remains unpassed. Nine affected regression scripts passed; the root-certificate warning remained. The wall interval from 21:09:27 to 21:11:32 UTC was about 2 minutes 5 seconds, including coding and tests; prior focused work against the six-hour cap remains unknown.
