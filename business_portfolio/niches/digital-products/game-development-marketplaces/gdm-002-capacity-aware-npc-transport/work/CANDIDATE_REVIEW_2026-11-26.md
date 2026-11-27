# Local review — marker-fix candidate, 2026-11-26

Status: unpublished and unlicensed. Candidate: `capacity-aware-npc-transport/review-candidate-marker-fix-2026-11-26/`. This is an internal review record, not approval to release or spend.

## Verified

- Its 85-entry manifest matched after its complete 50/50 product test run on standard Godot 4.7.2 on Windows x86-64. Its editor registration, marker recognition/redraw, and clean install/reinstall passed on standard 4.4.1, 4.5.1 and 4.7.2. The full 4.4.1 and 4.5.1 50-test runs used the immediately previous candidate before the editor-only marker change. Root-certificate-store warnings persisted.
- The current marker appeared as a cyan diamond and post in background editor captures in all three tested versions on one Windows/NVIDIA setup; a 4.7.2 selected-node capture showed the marker, editor transform controls and Stop ID field. These observations do not test physical input, accessibility, other drivers or display scaling. Captures are in `evidence/`.
- Temporary-game checks are synthetic and use the pre-marker-fix runtime, which is unchanged by the marker fix. Their scenarios do not establish arbitrary integration, navigation or performance. The single physical timing sample and its limits are in `PERFORMANCE_PHYSICAL_2026-11-26.md`.

## Before a release decision

1. Update the candidate's `VISUAL_QA.md`, `COMPATIBILITY.md` and related evidence to distinguish the new marker captures and full-suite coverage from historical statements. Restage and recheck the exact delivered files; do not silently alter an audited snapshot.
2. Finish interactive and accessibility review within the actual intended support scope, and document untested environments. Background rendering and synthetic input are not physical-device acceptance.
3. Confirm provenance and redistribution rights for every selected file, choose distribution and support terms, and assemble the actual delivery inventory. Existing provenance notes are a draft and the candidate has no approved license.
4. Determine and document practical workload guidance with repeatable, representative measurements, explicitly limiting claims. A single scripted headless timing run cannot establish general game performance.
5. Prepare the final release and obtain the owner's separate approval before any publication or expenditure. No account, outreach or external action is authorized by this record.


## Documentation follow-up — 2026-11-26

A separate unpublished snapshot, `capacity-aware-npc-transport/review-candidate-verified-2026-11-26/`, incorporates current visual and compatibility evidence in `VISUAL_QA.md`, `COMPATIBILITY.md` and `TEST_EVIDENCE.md`. Compared byte-for-byte with the marker-fix snapshot, those three documents are the only changes among its 85 manifest entries. Its manifest, Godot 4.7.2 clean install/reinstall and editor marker checks passed. The 50-test regression belongs to the byte-identical executable files in the preceding snapshot; the new snapshot itself has not had the full suite rerun. Rights, final delivery inventory and interactive acceptance remain open.


## Install-review quickstart — 2026-11-26

`capacity-aware-npc-transport/install-review-quickstart-2026-11-26/` is a separate 19-file local review with a logical-only `examples/quickstart.gd` and package-specific onboarding guidance. Clean Godot projects ran that exact example successfully on standard 4.4.1, 4.5.1 and 4.7.2 on Windows. The 19-file manifest matched after preparation. Its add-on bytes match the prior install review, whose clean install/reinstall passed on all three versions and whose exact add-on passed the temporary-game eight-case runner on 4.7.2. The quickstart simulates acknowledgments and does not exercise physical movement. It remains unpublished, unlicensed and subject to the open rights, acceptance and release decisions above.


## Physical integration example — 2026-11-26

`capacity-aware-npc-transport/install-review-physical-example-2026-11-26/` is a separate 21-file local review. It adds a scripted physical transfer and its game-owned passenger controller, adapted from the temporary integration project, alongside the logical quickstart. Both included examples passed in clean projects on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows. All 21 manifest entries matched and its add-on bytes matched the previously tested install review. The physical example demonstrates one passenger and two fixed-route collision platforms; it does not establish arbitrary game compatibility or general obstacle handling. This review remains unlicensed and unpublished.


## Broad exact-install integration — 2026-11-26

`temporary-broad-install-review-game-2026-11-26/` copied the exact 12 add-on files from `install-review-onboarding-2026-11-26/` into a fresh version of the broader synthetic integration game. Its complete 41-case runner passed on standard Godot 4.7.2 on Windows; the package's 22-entry manifest and the copied add-on bytes matched after the run. Cases included bounded game-owned cooperative avoidance, multi-vehicle dispatch, interruptions, reconstruction, footprint clearance and disconnected navigation. The game owns its movement, avoidance and vehicle dispatch; the add-on does not provide a general avoidance policy. The tests do not establish arbitrary production-game integration, general crowd handling or a performance guarantee. The known root-certificate-store warning persisted.


## Crowd and fleet examples — 2026-11-26

`capacity-aware-npc-transport/install-review-fleet-example-2026-11-26/` is a separate unpublished, unlicensed 26-file local review. It adds a bounded game-owned cooperative-yield scenario and a two-vehicle mapped-dispatch scenario to the existing logical and physical examples. All four included examples passed in clean Windows projects on standard Godot 4.4.1, 4.5.1 and 4.7.2; its add-on bytes match the prior onboarding review and its manifest matched. Routes, movement, yielding and safety policy are game-owned and scripted; neither example is a general crowd-avoidance, vehicle-navigation or dispatch system. `FLEET_EXAMPLE_PROVENANCE_TRACE_2026-11-26.json` and `CROWD_EXAMPLE_PROVENANCE_TRACE_2026-11-26.json` record local source observations, not ownership or permission.


## Broader compatibility subset — 2026-11-26

The current performance-notes review add-on was verified byte-identical to the broad temporary game's copy. Eight bounded moving-crowd, mapped-dispatch, capacity-two reconstruction, disconnected-navigation, recovery, footprint and endpoint cases passed on standard Godot 4.4.1 and 4.5.1 on Windows; the reusable subset runner also passed 8/8 on 4.7.2. The full 41-case run applies to 4.7.2 only. Raw per-case results and fingerprints are in `BROAD_INTEGRATION_COMPATIBILITY_2026-11-26.json`. The game owns movement, avoidance and dispatch, and none of these cases establish general production-game compatibility or performance.
