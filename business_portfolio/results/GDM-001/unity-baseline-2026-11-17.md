# GDM-001 Unity baseline

Unity Editor 6000.6.9f1 ran the sample project's Edit Mode test using Unity Test Framework 1.8.0. The generated result reported one test passed and zero failed. The test parses synthetic JSON and uses native NUnit assertions for a shield field; it is a toolchain smoke test, not a migrated game save or a comparison with the proposed product.

The sample lives at `products/game-tools/historical-save-regression-lab/SampleProject`. A subsequent run passed six Edit Mode tests: the smoke test, three inline synthetic save versions, a future-version rejection and a deliberate v1 shield-loss case. The deliberately broken loader returned normally; an ordinary NUnit assertion caught the missing shield and included `inventory.unique.shield_01` in its failure message. The negative assertion was intentionally captured by the test, so the overall run passed. This demonstrates that native tests can report this simple error; it does not establish comparative setup time or a product advantage.

Unity 6.6 is the installed version; the plan's Unity 6.3 compatibility remains unverified. The sample loader is a small synthetic approximation, not a real game's migration pipeline. No product adapter, Play Mode run, or commercial advantage has been established. The fixture-file follow-up below supersedes the original inline-only setup.

## Fixture-file follow-up

Three separate synthetic JSON fixtures now replace the inline save strings. Their SHA-256 hashes after the run are:

- v1: `462a55994a843bf1eaa4bf350a533d2a498edf01b5726f5820e4b2e68dcd22bc`
- v2: `aad6fb81678b3cd0bc49669338d61acfc9bd43a4101e31c767acf030f9ee04a5`
- v3: `c93bf46eedaf15bd39329f66bb25199c846237d18affc657e2d50fddbc23cab1`

Nine Edit Mode tests passed on Unity 6000.6.9f1. For each fixture, five fresh temporary directories were created; each copied file matched its source hash, loaded successfully, and was modified while the original remained unchanged. The test deletes its own temporary directory after each run. This only verifies the synthetic test's copy procedure; it does not yet implement or prove a general-purpose safe sandbox, validate a manifest, or establish behavior after a crash. The sample loader currently reads JSON text supplied by the test and does not write user profiles. Native setup time and adapter comparison have not been measured.

## Validation and runner spike

The sample now includes an in-memory fixture validator that rejects duplicate IDs, unsupported schema versions, malformed or mismatched hashes, linked files, and paths other than a single file in the fixture root. A synchronous experimental runner validates the fixture, copies it to a temporary directory, invokes the sample loader and reports either a pass or the hard-coded shield regression. Twenty Edit Mode tests passed on Unity 6000.6.9f1, including validation and runner cases.

This is a spike, not the planned package: there is no strict JSON manifest parser, generic adapter, asynchronous completion or timeout, independent loader, arbitrary state assertions, editor UI, CI report, crash recovery, measured comparison or release package. File validation and copying are separate operations and do not guarantee safety against concurrent filesystem changes. Only the direct root/file reparse points are checked; ancestor links and hard links are not ruled out. It must not be used with real saves. Native NUnit already reports the same simple shield failure; no advantage or demand has been demonstrated.

## Async adapter experiment

Unity 6000.6.9f1 ran 24 Edit Mode tests successfully. The experimental interface awaits reset, restore completion, and capture; tests exercise an explicitly completed asynchronous restore, a boolean regression, cancellation before reset, a restore exception, and a missing property. It is a synthetic test double, not a real gameplay loader. Cancellation is cooperative; there is no timeout, isolation, generic typed assertion engine, strict manifest parser, or measured comparison. It is not safe for real saves.

The previous sandboxed Unity launch failed to connect to its local Package Manager IPC server. Running the same Editor outside the restricted sandbox connected and registered the cached packages; no Unity installation or system configuration was changed. The initial run exposed a test expecting the exact `OperationCanceledException` type rather than its `TaskCanceledException` subtype; the corrected test accepts cancellation subclasses. The following run passed all 24 tests.
