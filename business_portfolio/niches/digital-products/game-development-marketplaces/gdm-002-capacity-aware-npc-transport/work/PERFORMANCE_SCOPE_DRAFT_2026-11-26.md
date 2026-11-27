# Observed workload and performance scope — local draft

Status: unapproved, unpublished. This is not an FPS promise, maximum supported crowd size, benchmark ranking or release acceptance.

## What has been exercised

- The temporary installation game passed nine scripted integration cases with the exact reviewed add-on on standard Godot 4.7.2 for Windows. The scenarios include a single physical two-platform transfer, restore, interruption, four-passenger blocked recovery and a missing passenger. They do not represent an independently developed production game.
- Product fixtures have exercised a 20-passenger navigation-assisted boarding scenario with one physical platform and fixed parallel lanes, and a 20-passenger, two-platform staggered scenario. Passenger-to-passenger collision was disabled in those larger fixtures; movement, alighting and routes were constrained by the tests.
- The detailed local measurements and reproduction scripts are in `PERFORMANCE_PHYSICAL_2026-11-26.md` and its linked JSON reports. Headless tests exclude rendering and use one Windows machine with uncontrolled host activity.

## Known uncertainty

Some early 20-agent navigation runs reported unusually high coarse physics-monitor values. A follow-up observed a 240.286 ms callback interval in one 4.4.1 run and a 133.2 ms interval in a later 4.4.1 run. Several other runs did not reproduce intervals over 100 ms. Later coarse host-CPU samples showed high host load during the run set but were not timestamp-correlated with the individual gaps. Cause remains unknown. These observations do not prove a rendered frame hitch or a defect in the add-on, and they do not rule either out.

## Proposed honest integration guidance

Treat the component as a coordination library and profile the actual game, agent controllers, vehicle physics, navigation, collision settings, rendering and target hardware under representative load. Start from the included single-passenger physical example, increase load gradually and check for missed movement, stale requests, occupied-seat retention and long frame/physics steps. Do not advertise a fixed supported NPC count, guaranteed FPS or comparative speed advantage based on these fixtures. Graph validation caps in `API.md` are input limits, not performance targets.

## Before choosing a release scope

Decide how to investigate or document the observed timing variability, complete physical-input and accessibility review, establish rights/license and support terms, and inspect the exact final delivery. Owner approval is required before spending or publishing.
