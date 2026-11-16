# GDM-001 — Unity Technical Feasibility Check

**Reviewed:** 2026-11-15  
**Scope:** Official Unity documentation only. This is a technical screening note, not a product test, market validation, or compatibility guarantee.

## Findings

| Question | Evidence checked | Finding | Consequence for the candidate |
| --- | --- | --- | --- |
| Can Unity tests exercise runtime behavior? | [Unity Test Framework manual](https://docs.unity3d.com/ja/current/Manual/com.unity.test-framework.html) | Unity documents Edit Mode and Play Mode tests. | A runtime-state check can be implemented inside a buyer's Unity project; a generic external save parser is not required for the MVP. |
| Can tests wait for asynchronous game work? | [Unity Test Framework `UnityTest` API](https://docs.unity3d.com/kr/Packages/com.unity.test-framework%402.0/api/UnityEngine.TestTools.UnityTestAttribute.html) | A Play Mode `UnityTest` runs as a coroutine and can yield frames while work completes. | A buyer-owned adapter can await the game's real load/migration completion signal instead of relying on a fixed sleep. The documentation does not provide that game-specific signal; each target game must expose one. |
| Can tests be automated from a build/CI command? | [Unity command-line arguments](https://docs.unity3d.com/ru/current/Manual/CommandLineArguments.html) | Unity lists `-runTests`, `-testPlatform`, and `-testResults` as test-run options. | A command-line invocation and result file are plausible, but exact Editor version, license, project setup, test assembly, and CI behavior still need a real project spike. |
| Does Unity automatically provide an isolated save profile? | [Application.persistentDataPath](https://docs.unity3d.com/cn/current/ScriptReference/Application-persistentDataPath.html) | The path varies by platform and is derived in part from app identity; for several platforms it is a persistent user-data location. Reusing an app identity can reuse the same location across updates. | The tool must not assume that copying a fixture into the default path is safe. A game-owned adapter needs an explicitly disposable save root or another verified isolation method, and the test must prove the source fixture remains unchanged. |

## Decision

The Unity route is **technically plausible as an in-project adapter**, with a real load-completion hook and explicit test-data isolation as mandatory requirements. The docs support a test runner and asynchronous Play Mode tests; they do not show that an off-the-shelf harness can inspect arbitrary games' private state or safely redirect every game's save path.

Unity's own test framework is a meaningful substitute. Therefore this research does not establish that a separate product saves setup time, provides better diagnostics, or has a paid market. That uncertainty is recorded as a risk to test with a local synthetic-data prototype; buyer interviews are optional and are not a prerequisite to building.

## Not verified

- No Unity project or sample game was opened or modified.
- No adapter, package, fixture, or executable prototype was built.
- No real save file was read, copied, changed, or tested.
- No current Unity Editor/LTS version matrix, marketplace listing feature set, price, licensing terms, or buyer demand was tested in this check.
- No studio was contacted; no customer materials or save files were requested.

## Next step

Start with a local synthetic old-save fixture and a bounded Play Mode prototype. Compare its result with Unity Test Framework behavior and record setup effort, false positives, and limits. The existing interview guide is optional follow-up research only. Any real game project or save fixture requires its rights-holder's consent and separate owner approval.
