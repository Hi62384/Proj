# GDM-003 workflow timing follow-up — 2026-11-18

The plan requests a timed free-tool comparison. On the same host and freshly rebuilt Godot 4.7.2 fixture matrix, one warm run of each workflow was measured end to end: the free workflow ran Dependencies 1.11.1 `-json -chain -depth 4`, saved and validated its JSON, then ran the corrected fixture helper; the integrated workflow ran the fixture spike and its local PE probe. These numbers measure command execution, not engineering integration time, setup, user diagnosis, or a customer experience. Dependencies also traversed host/system chains that the spike did not, so the workloads are not equivalent and these timings do not establish a general speed advantage.

| Fixture | Free workflow elapsed | Integrated spike elapsed | Free helper / spike exit |
|---|---:|---:|---|
| Clean | 15.772 s | 0.956 s | 0 / 3 |
| Omitted leaf declaration | 18.060 s | 0.861 s | 1 / 1 |
| Nested leaf destination | 30.598 s | 0.877 s | 1 / 1 |
| First-matching generic dependency map | 16.524 s | 0.514 s | 1 / 1 |

The free helper's clean result meant only that no unresolved import matched the fixture source bin; the spike's exit 3 explicitly retained unknown checks. In the three negative cases, both identified `extension.dll → root.dll → middle.dll → leaf.dll` and the relevant `windows.x86_64` or `windows` dependency map. For the nested case both reported the `nested` destination; for the other two both reported the leaf absent from the selected map. The spike additionally emitted a structured finding and its unknown-check list. This is a comparison of controlled fixture outputs, not a broad claim of equivalence.

The authoring and human diagnosis time requested by the plan remains **unmeasured**. The operator created both approaches and already knew the cases, so a retrospective stopwatch would not be an independent diagnosis trial. The cases do not establish a general commercial advantage or invalidate the conditional feasibility pause. A materially comparable, independently timed diagnostic workflow or other concrete evidence would be needed to support changing that decision.

`products/game-tools/native-dependency-verifier/fixture/measure_workflows.py` reproduces the timing sequence using separately supplied tools and a fresh output directory. Dependencies JSON is kept in that local directory and can include host paths; it is not included in this public result. The script verifies that Dependencies actually returned JSON because that CLI can emit non-JSON text with exit code 0 for unsupported options. No spending, publication, customer contact or sale occurred.
