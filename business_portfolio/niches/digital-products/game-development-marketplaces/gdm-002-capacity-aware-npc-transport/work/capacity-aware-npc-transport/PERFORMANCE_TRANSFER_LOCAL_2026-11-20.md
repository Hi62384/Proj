# Local two-service transfer measurement — 2026-11-20

`tests/measure_transfer.gd` runs 20 passengers over two scheduled services, with vehicle capacities three and two. It measures journey creation separately from a sequence of 51 coordinator ticks. Boarding and alighting requests are collected and acknowledged in reverse order within their respective tick phases; no real-time delay or physical movement is simulated. Each version completed all passengers with no fixture failures in one warm-up and five measured repetitions.

The run used standard Godot on Windows 10 x86-64, AMD64 Family 25 Model 68 Stepping 1. Durations are microseconds for each complete measured sequence; maximum tick is the largest observed across the five measured runs. Sequence durations include the fixture's per-tick completion checks.

| Godot | Journey creation, five runs (µs) | Transfer sequence, five runs (µs) | Maximum observed tick (µs) |
| --- | --- | --- | --- |
| 4.4.1 | 993, 953, 938, 959, 991 | 7270, 7104, 7863, 7173, 7228 | 214 |
| 4.5.1 | 905, 1008, 1509, 924, 1194 | 6770, 8486, 8815, 7955, 8275 | 382 |
| 4.7.2 | 1791, 2501, 1595, 1359, 1391 | 18700, 23542, 11047, 10978, 11336 | 5878 |

These are small, non-isolated samples on one machine and are not a reliable comparison between versions. They exclude navigation, physics, rendering, save/load, multiple changing routes and external game logic; they do not establish frame rate, a supported scale, or fairness under unbounded or disrupted demand. All versions reported the existing root-certificate-store warning. Representative game performance remains unverified.
