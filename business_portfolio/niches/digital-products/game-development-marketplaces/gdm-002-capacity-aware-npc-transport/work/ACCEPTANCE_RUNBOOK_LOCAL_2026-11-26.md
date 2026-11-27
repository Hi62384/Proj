# GDM-002 hands-on acceptance — local runbook

Status: **not yet performed**. This runbook prepares the remaining human-facing check; it does not record a pass, approve release, authorize publication or grant a license. The owner asked for background testing, so do not take over or change the owner's display settings without a separate instruction.

## Exact subject and preparation

- Development demo: `capacity-aware-npc-transport/review-candidate-scaled-demo-2026-11-26/`. The standalone add-on review is `capacity-aware-npc-transport/install-review-onboarding-2026-11-26/`; the small add-on review does not include the demo.
- Before a run, verify the selected candidate manifest and record the Godot version, OS, graphics driver, display resolution, native display scaling, window size and input devices. Use an isolated temporary project and user data. Do not overwrite existing saves.
- Record actual outcome and evidence for each step, including a description of any failure; an unchecked item is not a pass. Avoid screenshots containing private desktop information.

## Demo checks

- [ ] Open the demo at a typical desktop size at 100% native display scaling. Verify readable status, visible controls and enough scene visibility to understand the demonstration. Use the mouse to pause/resume, save/load and disable/re-enable B-fast. Confirm the corresponding state changes and messages.
- [ ] Use only a physical keyboard to move focus among controls, identify the focused control, activate pause/resume and save/load, and hide/show details. Confirm focus remains visible and the controls work without a mouse.
- [ ] At a smaller supported window and at a chosen native scaling such as 150%, repeat the checks. Verify the controls, status and messages remain readable and reachable, and that Hide details reveals the scene. Record the actual dimensions rather than assuming Godot content scale equals OS DPI.
- [ ] Check the stop marker in an isolated Godot project with the optional plugin enabled: add the marker script to a Node3D, set a Stop ID, select and deselect it, and verify it is identifiable against the current background. Confirm the marker is visual only and that the game configuration contains the stop.

## Accessibility scope

- [ ] Assess keyboard-only operation and visible focus, contrast and text legibility at the tested sizes/scales. Record which assistive technology, if any, was tested and its result. Do not claim general screen-reader support, WCAG conformance or accessibility certification from this limited check.
- [ ] Review visual cues without relying solely on the colors of the two services, and record any unresolved issues and their impact.

## Closure

- [ ] Save the exact engine/package fingerprints and pass/fail observations beside the project record; fix reproducible defects and rerun the affected checks.
- [ ] Review remaining untested hardware, performance limits, rights, license and support decisions. A completed run does not itself authorize publishing or spending; obtain the owner's separate approval before either.
