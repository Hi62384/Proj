# GDM-001 native comparison scorecard — 2026-11-18

## Decision at this checkpoint

**Gate not passed; no product advantage established.** The native Unity Test Framework has reproduced the synthetic faults and CI failure paths demonstrated by the prototype. The prototype adds manifest handling, a report experiment and fixture-copy orchestration, but its own integration requires an adapter and expected-state mapping, and its strongest differentiators—safe isolation and easier real-game integration—have not been verified. This is substantial counterevidence to a paid generic assertion tool, not a final no-go: the required independent, equivalent-scope installation and maintenance comparison has not been completed. Do not advance to release preparation or imply a sale-ready tool.

## Evidence against the project plan

| Criterion | Observed evidence | Decision limit |
|---|---|---|
| Three historical inputs and two faults | In a copied Unity project without the source project's Library, both paths passed three synthetic saves and detected v1 shield and v2 quest faults; ten tests passed. | Sample code and project settings were shared; not an independent buyer or actual game. |
| Callback restoration | A second synthetic callback loader ran in a separate diagnostic project. Native assertions and the prototype both caught the sword fault, and each independent intentional failure exited 2 with `inventory.sword`. | One fictional callback implementation; no proof of a general Unity adapter or full game restoration. |
| CLI | Native NUnit and prototype tests both produced nonzero Unity exits in controlled failures. The prototype's synthetic manifest runner returned 0 for three passing cases and 1 for a regression, bad hash and malformed JSON. | The prototype runner is hard-coded to the synthetic loader/root; full general CI integration remains incomplete. |
| Failure localization | Both native and prototype identified the tested property paths. | No broad nested-state, array or object comparison, and no buyer assessment. |
| Fixture copies | Tests observed unchanged synthetic source bytes. The prototype verifies a pinned source hash before copying. | A copied fixture is not OS confinement. Race, hard-link, arbitrary adapter I/O and crash behavior remain open. |
| Async and deadlines | The prototype waits for a callback in the second example; native tests can observe the same callback. Cooperative deadline is tested. | A noncooperative adapter can hang; no verified hard timeout or safe containment. |
| Reports and redaction | Prototype experiments produce sorted JSON omitting expected/observed values, and an incomplete journal marker. | IDs and property paths remain visible; report coverage, durability and a real-game workflow are incomplete. Native NUnit XML is a competing built-in report, not a proven equivalent privacy design. |
| Setup and change effort | A single same-author exploratory write measured roughly 14.6 seconds native and 21.4 seconds prototype, excluding design, setup and testing; adding a derived check touched one native assertion versus adapter mapping plus manifest entry. | Unequal safety checks, shared knowledge and prepared scripts make these numbers unsuitable for a customer time-saving claim or a definitive no-go. |
| Enforced isolation | A no-capability AppContainer denied selected workspace canaries, but the installed Unity Editor failed its Package Manager IPC startup in one bounded test. A temporary SID-granted pipe worked only for an owned synthetic endpoint. | Unity with safe isolation remains unverified. Job Objects alone do not restrict file or network access. |

Detailed commands, version and limits are in [the isolation and baseline review](isolation-and-baseline-review-2026-11-18.md). The original `SampleProject` Unity process is still live without `callback-results.xml` at this checkpoint; the successful callback comparison used a distinct copied project.

## Competition and remaining falsification

Unity's test framework already supplies a test runner and NUnit-style reports; the project must demonstrate a real workflow advantage rather than merely wrapping assertions. [Unity's Test Framework documentation](https://docs.unity3d.com/Packages/com.unity.test-framework@1.8/manual/index.html) describes the framework, not any advantage of this prototype. The [Save Migrator listing](https://assetstore.unity.com/packages/tools/utilities/save-migrator-version-safe-save-data-migration-411584) advertises migration, validation, backup and recovery; its claims have not been independently tested here and do not prove sales or substitute for gameplay-state tests.

To pass the original gate, use comparable implementations with the same three saves, asynchronous completion and two faults; record independent setup and change effort, native and prototype CI output, original hashes, default redaction, and genuine recordings. Establish a realistic, enforceable isolation boundary for the actual Unity workflow and test failure recovery. If the equivalent native solution is equally useful with less setup, or isolation cannot be guaranteed, apply the plan's no-go/defer rule rather than publish. Do not broaden the product to other engines or make paid commitments while this is unresolved.

## New safety counterexample

A controlled synthetic adapter wrote a canary outside its fixture-copy directory while the current runner returned `pass` (`adapter-escape-results.xml`). The present in-process design therefore fails the plan's enforced-isolation requirement. This is a no-go for releasing that design with a safety claim; it is not proof that a separately engineered boundary cannot satisfy the requirement. The product-family decision remains conditional on the remaining comparison and isolation work.

## Standalone-player feasibility update

A small original synthetic Unity player read a copied save and produced state inside a no-capability AppContainer; its attempted outside write did not create the canary and raised `DirectoryNotFoundException`, while an unrestricted control wrote it. This is an alternative architecture worth testing, not a general game integration or isolation guarantee. The current in-Editor runner still fails the isolation gate, and the potential cost of building/adapting actual games has not been measured. Details and limits are in the isolation review.

A later synthetic standalone-player probe also signaled asynchronous completion, returned a nonzero exit for one injected shield fault, and was externally terminated after a marked non-completing restore. Two passing result files were byte-identical and omitted the synthetic observed values. This remains a one-fixture, one-fault sample with no real game adapter or measured integration advantage; it does not close the safety or comparison gates.

## Report trust limitation

A deliberately dishonest restricted synthetic player fabricated a start marker and passing result without restoring state; the current supervisor accepted it. Resource isolation and result truth are distinct requirements. The current worker-produced report cannot support a claim that untrusted game or adapter code was honestly observed. The intended trust model and independently verifiable checks need to be specified and tested before release.


The restricted standalone experiment now exercises the sample loader across three synthetic versions and detects shield and quest faults. This is not yet an equivalent timed native comparison or evidence of a product advantage; the integration burden and trust boundary remain unresolved. The parent report contract rejects inconsistent data and defaults to untrusted, but an explicitly trusted fabricated report still appears to pass. The safety and commercial decision gates remain open.


## Separate synthetic Unity CI comparison

On Unity 6000.6.9f1, independent test-run invocations of `NativeIntegrationExercise` and `PrototypeIntegrationExercise` each passed all three matching synthetic save versions and the same shield, potion, derived-potion and quest expectations. The paired `ComparativeFixtureTests` run passed six cases, including shield, quest and potion faults; its two opt-in negative tests were skipped in that run. Four further invocations enabled the negative tests separately: native shield, prototype shield, native quest and prototype quest each produced one actual failed test, exit 2, and the expected `inventory.unique.shield_01` or `quests.complete` message. XML and logs are in `experiments/equivalent-comparison-2026-11-18/`. The original fixture source hashes were checked by the paired tests.

These runs show equivalent observed synthetic behavior and native CI failure localization; they do not measure independent setup or maintenance, establish a real-game advantage, or equate the in-Editor prototype with the separate restricted-player experiment. Both implementations share a synthetic loader and author; timings are not valid buyer productivity evidence. This strengthens the case for deferring any generic paid-tool claim until a real integration and independently measured advantage exist. The current in-Editor runner still fails the isolation requirement.
