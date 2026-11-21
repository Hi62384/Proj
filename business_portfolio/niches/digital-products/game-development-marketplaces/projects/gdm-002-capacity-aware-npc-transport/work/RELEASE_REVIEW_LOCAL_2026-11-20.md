# Local release review — 2026-11-20

Candidate: `capacity-aware-npc-transport/review-candidate-current-2026-11-20`. This is an unlicensed local review copy, not an approved release. Its 85 original manifest entries were hash-checked; its later-generated compatibility report is additional local evidence and was not part of the original manifest.

## Evidence available

- The staged product passed all 50 tests, clean installation and reinstallation, and instrumented editor marker registration/recognition/redraw on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows x86-64. The matrix reported unchanged source fingerprints. The Mono 4.5.1 editor check had a separate missing .NET SDK failure; standard 4.5.1 passed.
- A repeat hash audit found no mismatches among the 85 manifest entries and no executable, shared library, archive or packaged game files by extension. This is a file inventory, not a provenance or license clearance.
- The recovered temporary game contains add-on files matching the candidate, excluding generated UID/cache files. Its complete 41-case integration suite passed together on Godot 4.7.2 after recovery. The game is original synthetic test material, with bounded scripted routes; it is not evidence of integration into an existing external game.
- Hidden 4.7.2 demo renders were inspected at 800×600 and 1152×648 after fixing clipped status text. Viewport-injected mouse and keyboard input tests passed on the three tested standard engine versions. These are not physical-device, accessibility, DPI, or visual editor-gizmo acceptance.
- A local 20-passenger two-service coordinator measurement completed on the three standard versions; it excludes game physics, rendering and real-time movement. It does not establish practical game performance or general fairness.

## Open before release

1. Integrate and test in a representative existing game with rights to use it, including lifecycle, movement, recovery and save/restore; record its scope and any findings.
2. Complete hands-on visual, keyboard/mouse and editor marker review, including relevant display scaling and accessibility scope.
3. Establish practical supported workloads and complete final documentation and source regression against the candidate that will actually ship.
4. Verify rights and redistribution terms for the selected files, choose a license and support terms, and check the actual distribution channel's current requirements.
5. Prepare the exact release for review and obtain the owner's separate approval before publishing or spending.

No payment, account, customer contact, publication or release is authorized by this document.
