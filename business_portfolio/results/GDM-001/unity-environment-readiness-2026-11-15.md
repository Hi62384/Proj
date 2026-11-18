# GDM-001 — Unity Environment Readiness

**Checked:** 2026-11-15  
**Purpose:** Determine whether this checkout can begin the Unity-specific S01 baseline and fixture prototype.

## Observed checks

- `Get-Command Unity.exe` found no Unity executable on `PATH`.
- No Unity installation was found in the checked standard locations: `C:\Program Files\Unity\Hub\Editor`, `C:\Program Files\Unity`, `C:\Program Files (x86)\Unity\Hub\Editor`, or the common per-user Unity Hub locations under `%LOCALAPPDATA%`.
- Available .NET SDKs were 6.0.404, 7.0.306, 8.0.302, and 9.0.202. Python was 3.11.3.
- The GDM-001 plan requires pinning an installed Unity version and establishing a native Unity Test Framework baseline before building synthetic saves or the actual-loader adapter. It explicitly says to stop and document the gap when Unity is unavailable.

## Decision and limits

S01 cannot start in this environment. A .NET-only substitute would not exercise Unity Editor APIs, its Test Framework, or a game's real Unity load path, so it would not satisfy the project's acceptance criteria. No Unity project, product code, synthetic save fixture, customer data, or external effect was created. No spending or outreach occurred.

This is a targeted readiness check, not an exhaustive scan of every drive or nonstandard installation directory. No Unity or marketplace compatibility is verified, and commercial validation remains unvalidated.

## Next action

The official Unity Hub Windows installer was subsequently downloaded to `C:\Users\User1\Downloads\UnityHubSetup-x64.exe` (193,133,232 bytes). Its Authenticode signature is valid and names Unity Technologies SF; SHA-256: `2bd8b7086c0bc986f033a31b55bc5d1f5452d10cab66b5f41c98ab5d84cabfa2`.

Unity Hub is not installed yet, and no Unity Editor was downloaded. Unity's official setup guide requires signing in to a Unity account to download the Hub and using the Hub with a Unity ID. The owner must complete that sign-in and choose/install an appropriate Editor version (the plan calls for checking Unity 6 LTS / 6000.3), then record its exact version and run the native Unity Test Framework baseline (S01). Only continue to S02 if that baseline and local project support are available.
