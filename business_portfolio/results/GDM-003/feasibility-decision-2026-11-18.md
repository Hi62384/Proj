# GDM-003 feasibility decision — 2026-11-18

**Subsequent evidence:** A [dependency-collision follow-up](dependency-collision-2026-11-18.md) found an actual loader failure missed by the initial spike and library-only script. The spike and a separate free-tool symbol comparison were then extended to detect that controlled case. This reinforces the conditional nature of the decision below; neither general parity nor commercial advantage is established.

## Decision

**Pause expansion beyond the feasibility experiment at the project's differentiation gate.** The integrated spike now exists and has been compared with Godot's logs, Dependencies, MSVC `dumpbin`, and two small fixture-specific scripts. The integrated workflow emits one JSON report, but the tested cases do not yet show that its additional value justifies maintaining a general, safe product. This is a conditional pause, not proof that the free alternatives are equivalent across arbitrary games or that no market exists. Preserve the spike, fixtures, results and existing planned/unvalidated commercial state.

## What the bounded comparison established

| Controlled case | Integrated fixture spike | Free baseline | Limit |
|---|---|---|---|
| Clean export, separate or embedded PCK | No fixture finding; exit 3 for unresolved checks | Godot loaded the owned extension; Dependencies resolved the fixture imports | Neither proves clean-host or arbitrary runtime compatibility. |
| Missing direct or transitive DLL | Package-root finding and import chain | Dependencies exposed the unresolved chain; the small helper related it to the controlled descriptor | Host-specific loader resolution remains unknown. |
| Omitted dependency or nested destination | Chain and selected fixture map/destination | Dependencies plus the corrected helper exposed the chain and tested map/destination | The helper and spike both have deliberately limited Godot syntax and feature support. |
| Missing selected source library | Names the selected fixture field and source | Godot's export returned 1 and named the missing file | Godot left partial output; callers must check the export result. |
| Wrong x86 extension in x64 export | Reports machine mismatch | Godot reported error 193; `dumpbin` showed x86 | No independent clean-machine or full loader compatibility proof. |
| Byte-distinct extension DLLs with same staged name | Reports source declarations and hashes | A separate small fixture-specific hash script found the same conflict | The owned test marker changed bytes but did not prove a runtime defect; general staging rules remain unproven. |
| Dynamic or delay load and host resolution | Reports those checks as unknown | The static tools have the same inherent runtime limits; the helper can flag the tested outside-package resolution | The integrated script is not race-safe, and its Windows handle experiment is only partial. |

The first DIY helper initially misread one dependency-map ordering case; it was corrected and rerun. Both DIY helpers are narrow experiments, and their authoring effort was not timed. Dependencies traversed a broader host/system graph than the integrated spike, so the recorded single-run execution times are not an apples-to-apples performance benchmark. The reusable product's general Godot parser, PCK handling, race-resistant input traversal, comprehensive PE safety, reliable loader policy, clean-host support, release QA, licensing, and customer demand remain unproven. These remaining costs matter to the go/kill decision; no estimate of completed hours or user willingness to pay is asserted.

The decision follows the plan's instruction to stop expansion when the free workflow and small scripts explain the defined examples without demonstrated material differentiation. Reconsider if new concrete cases or a revised scope establish a repeatable advantage that survives a fair comparison, including the cost of safely supporting that scope. The owner may also direct a different scope in a future request. No listing, purchase, outreach, sale, or release was made or authorized by this decision.

Evidence and reproducible inputs: [integrated spike](integrated-spike-2026-11-18.md), [free baseline](godot-free-baseline-2026-11-18.md), and [secure input design](secure-input-design-2026-11-18.md).
