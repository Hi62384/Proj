# GDM-002 release decisions — local draft

This is preparation for owner review, not a license, legal advice, release approval, support promise, or permission to spend.

## Candidate for review

`capacity-aware-npc-transport/install-review-physical-example-2026-11-26/` contains the add-on, logical and scripted physical examples, guides and draft support/provenance notes. Its 21-file manifest was checked after testing. The add-on bytes match the copy used in the nine-case temporary-game run on Godot 4.7.2; both included examples ran in clean projects on standard 4.4.1, 4.5.1 and 4.7.2. This is Windows-only local evidence, with scripted routes and no physical-device or accessibility acceptance. It is not a final approved delivery.

A later local review, `capacity-aware-npc-transport/install-review-onboarding-2026-11-26/`, adds an installation guide and adjusts the README; its add-on and examples match the 21-file review above. Its 22-file manifest and clean packaged-editor checks passed on the three tested standard versions. The development demo's synthetic mouse and keyboard focus checks also passed at three viewport sizes; the demo itself is not part of this install review. This does not close physical-input or accessibility acceptance.

## Decisions still required before release

1. **Rights and license:** Verify ownership and any third-party rights for the exact files, decide what a recipient may do with the add-on and examples, and prepare appropriate license and notice text. The package currently grants no approved license. Choosing a distribution platform does not establish rights.
2. **Support and maintenance:** Decide who receives issues, a real support contact and the scope and duration of any maintenance or updates. Do not promise response times or services that have not been approved.
3. **Compatibility and claims:** Approve an accurate support scope and concise known-limits statement. Current evidence covers standard Godot 4.4.1, 4.5.1 and 4.7.2 on one Windows machine; synthetic scenarios are not proof for all games or platforms. No performance guarantee, proven commercial advantage or sales claim is established.
4. **Accessibility and hands-on acceptance:** Decide how to complete the still-open real-input and accessibility checks, or document an explicit scope decision after review. Background screenshots and injected events do not replace them.
5. **Delivery and consent:** Select the actual final file list, check the target platform's then-current terms and fees, inspect the final artifact and obtain separate owner approval before publication or spending. No account creation, outreach, price, publication, purchase or schedule is authorized here.

## Preserved evidence

See `CANDIDATE_REVIEW_2026-11-26.md`, `PERFORMANCE_PHYSICAL_2026-11-26.md`, `temporary-install-review-game-2026-11-26/` and `evidence/`. Final publication requires its own exact-file integrity check and cannot be inferred from this draft.


## Scaled development-demo follow-up — 2026-11-26

The separate `capacity-aware-npc-transport/review-candidate-scaled-demo-2026-11-26/` contains the improved development demo and retains the same add-on as the onboarding install review. Its 51-test product suite passed on standard Godot 4.7.2 and its 86-entry manifest matched after testing. Focused demo tests passed on 4.4.1, 4.5.1 and 4.7.2; background 4.7.2 captures at 150% Godot content scale showed the expanded and compact layouts. The prior `review-candidate-verified-2026-11-26` demo did not contain the later dark backdrop; the scaled-demo candidate restores that backdrop from the working development source. The smaller 22-file onboarding install review does not include a demo. These checks do not establish native OS DPI, physical-input or accessibility acceptance.


## Concrete choices to review later

These are proposals for discussion, not selected or binding terms.

- **Usage rights:** Decide whether a customer may use and modify the add-on in commercial games; whether teammates and contractors on the same project may access it; and whether redistribution of source, resale as an asset, or sharing standalone copies is allowed. Confirm ownership and third-party obligations before drafting any license.
- **Support scope:** A bounded starting proposal is best-effort help for reproducible issues in the documented add-on, with no response-time guarantee, custom integration, engine-porting or multiplayer commitment. Decide the support contact and duration before making any promise.
- **Compatibility presentation:** Identify the exact tested Windows/Godot combinations and state that platform and hardware outside that test matrix remain unverified. Do not turn local test evidence into a promise of universal support.
- **Hands-on approval:** The exact proposed steps and pass/fail criteria are in `ACCEPTANCE_RUNBOOK_LOCAL_2026-11-26.md`. The owner has asked for background work, so physical-device testing and display-setting changes await a separate instruction or another authorized reviewer.

For file-level source observations see `INSTALL_REVIEW_PROVENANCE_TRACE_2026-11-26.json`; byte matches are not proof of rights or consent.


## Full scaled-demo candidate matrix — 2026-11-26

The exact `review-candidate-scaled-demo-2026-11-26` subsequently passed the full 51/51 product suite on standard Godot 4.4.1 and 4.5.1, as well as the earlier 51/51 on 4.7.2. Its 86-file manifest matched after the two later runs. The known root-certificate-store warnings occurred. This does not close the still-unperformed hands-on and accessibility runbook or establish other platforms and hardware.


## Expanded install-review option — 2026-11-26

`capacity-aware-npc-transport/install-review-fleet-example-2026-11-26/` is a newer 26-file unlicensed local review. It includes tested game-owned cooperative-yield and mapped two-vehicle dispatch examples in addition to the logical and physical quickstarts. All four examples passed on each tested standard Godot version; the add-on bytes match the prior review. This is a review option, not a finalized or approved license or delivery. The game's example code supplies yielding and routes; no general automatic crowd or vehicle-navigation capability is claimed for the add-on.


## Performance-notes review — 2026-11-26

The later `capacity-aware-npc-transport/install-review-performance-notes-2026-11-26/` is a separate 27-file local review that adds `PERFORMANCE.md` and links it from the README. It explicitly describes the observed callback variability and avoids FPS or crowd-size guarantees. All add-on and example files are byte-identical to the four-example review tested on standard Godot 4.4.1, 4.5.1 and 4.7.2; its manifest and documented `res://` paths were checked. The note does not resolve the unknown cause or constitute an accepted release scope. Licensing, physical-input/accessibility acceptance, support terms and publication approval remain open.


## Local-only artifact review — 2026-11-26

`local-review-artifacts/GDM-002-LOCAL-REVIEW-2026-11-26.zip` was built by `prepare_local_review.py` from the performance-notes review manifest. Its SHA-256 is `7b58ad30f8e61a9a730539c5980bd56155e0495a0c23e6821461224f60fc47ee`. It contains the 27 manifest files plus `MANIFEST.json`, including the local-only notice; it has no approved license. Archive entries were compared byte-for-byte with the verified source. Its four examples passed from extracted copies in isolated projects on standard Godot 4.4.1, 4.5.1 and 4.7.2 on Windows. A repeat build refused to overwrite the existing artifact. This is a local review artifact, not an approved final release, and does not resolve the timing uncertainty, physical-input/accessibility acceptance, rights or support decisions.


## Expanded broad integration — 2026-11-26

The full expanded 42-case runner passed on standard Godot 4.7.2 on Windows using add-on files identical to the local review archive. This includes the later twelve-angle game-owned crowd test. The review directory, archive entries, manifest and copied add-on were rechecked after the run. The crowd and vehicle controllers are game-owned and synthetic; this is not a general crowd or production-game guarantee. Physical-input/accessibility acceptance, timing uncertainty, rights, license, support terms and publication approval remain open.


## Owner direction and hands-on setup — 2026-11-26

The owner selected the direction **commercial game use and modification, with no standalone redistribution**. `LICENSE_TERMS_DRAFT_2026-11-26.md` contains a local non-operative draft and lists unresolved ownership, team access, source-available game, legal and support questions. It is not an approved final license or a grant of rights.

The owner chose to perform the physical-input check personally. `owner-acceptance-2026-11-26/START_HERE.md` and its two launchers prepare that check in a separate local project and isolated user-data directory. The project startup probe passed headlessly; no hands-on pass has been recorded and no visible window was launched by the agent.


## Full broad-game compatibility — 2026-11-26

The expanded synthetic game's complete 42-case runner subsequently passed on standard Godot 4.4.1 and 4.5.1 on Windows, matching the earlier 4.7.2 full run. The tested add-on remained byte-identical to the local review archive after the runs. Avoidance, routes and vehicle movement belong to the test game, not a general add-on policy. The physical owner check, rights/license completion, performance uncertainty and final release approval remain open.
