# Codex Relay repair report — October 27, 2026

**Status: code repairs and regression tests completed; secure live execution and the full two-way acceptance test remain blocked.** The owner instructed this run to finish independent repairs and report the environment blocker rather than close unrelated apps or change shared WSL settings.

## Verified root causes

| Failure | Evidence and resolution |
| --- | --- |
| Deprecated restricted-read request | The local patch had replaced `readOnly.access`, which the installed protocol no longer accepts. That patch was preserved and extended. Thread creation, resumption and turns now consistently use `permissions: relay-locked`; deterministic standalone probes use `permissionProfile: relay-locked`. No legacy or unrestricted fallback is sent. |
| Different executables selected | The npm CLI reports **0.162.1**, while the desktop application's bundled executable reports **0.164.0-alpha.11.1**. The old PATH-first resolver selected the latter. The relay now prefers the stable npm native executable, respects an explicit native executable selection, and checks generated schemas when the executable changes. |
| Unelevated Windows isolation | The required root-deny filesystem profile cannot be enforced by the unelevated restricted-token backend. The relay now detects this before creating an AI thread and retains a specific local diagnostic. |
| Elevated setup policy | The official setup API itself requires root-read access. Provisioning is now isolated in an explicitly approved, setup-only controller that forbids threads, turns and command execution. Its temporary setup policy does not replace the restricted task policy. |
| Elevated provisioning refresh | Approved provisioning created/refreshed dedicated sandbox users and firewall controls, then failed during runtime access validation with Windows sharing error 32 on a live desktop Node runtime. Removing inherited PATH/runtime variables did not resolve that helper-level validation. |
| Elevated task policy | A separate real, fixed-command test returned **`elevated Windows sandbox requires effective :root read access`** (the actual error encloses `:root` in backticks). Thus fixing the runtime file lock alone would not make this installed native backend compatible with the required policy. Broad task reads remain prohibited. |
| MXC | The owner's earlier probe reported native MXC unavailable on this executor. This repair did not present MXC as a working alternative or change machine settings to force it. |
| WSL2 | Existing Ubuntu/WSL2 was inspected. Later startup and the approved package-update attempt failed before Ubuntu could execute with **`Wsl/Service/CreateInstance/CreateVm/HCS/ERROR_NO_SYSTEM_RESOURCES`**. Windows reported about **700 MB** free physical memory. Low memory is a plausible constraint; the HCS resource condition was not fully resolved. No Linux packages or authentication were installed/copied. |
| Misleading diagnostics | Errors previously collapsed into generic CLI/authentication advice. Diagnostics now retain a sanitized underlying detail, RPC stage, category, explanation and action locally. Authentication, protocol, sandbox, transport, timeout and inference failures are separated. |
| Repeated unusable sessions | Sandbox preflight precedes thread creation. Persistent execution blocking prevents additional tasks repeating a configuration/environment failure. Only a successful explicit connection/sandbox check clears the block. |
| Interrupted task state | A server-side interruption could leave a task Running. It now becomes paused Needs Owner. Failed follow-up instructions remain queued for an explicit owner retry. |
| ChatGPT GitHub writes | The connected GitHub integration read existing Issue #1 and comments successfully. One deduplicated structured follow-up attempt returned **HTTP 403, `Resource not accessible by integration`**. No new Issue or comment was created. The local relay credential authenticates separately and does not expand the connector's permissions. |

## Selected sandbox path

**WSL2 with a native Linux Codex runtime and the same exact-file, root-deny profile** is the prepared next path. Native Windows execution remains blocked on this machine rather than weakened.

The new WSL installer:

- Reuses the existing Ubuntu distribution; no new Windows feature or reboot is requested.
- Requires explicit installation approval and checks VM readiness before installing packages or copying sign-in state.
- Installs required Ubuntu sandbox packages only if absent and an official Linux Codex package, with SHA-512 integrity verification and validated archive paths. It does not execute package post-install scripts.
- Uses private Linux-owned configuration/authentication directories and a controlled environment. Only the existing ChatGPT login needed by Codex is imported when necessary. GitHub credentials, SQLite state and approvals remain on Windows.
- Maps only approved project paths into the read-only OS policy. Windows-hosted `relay_workspace` remains the only project write capability.
- Switches the saved backend only after authentication and a restrictive OS sandbox probe succeed. No automatic native or unrestricted fallback is available.

**This WSL path has not been validated live.** Its VM cannot currently start. Syntax and mocked regression checks do not establish kernel sandbox enforcement or successful inference. Dedicated live negative-access tests should be completed after setup can run, before treating the environment as fully accepted.

## Security and state preservation

- Initial Git status was inspected against local commit `65ec53cd0560cd753ba13aee8cd0f34b8ef2a2b5`. The existing edits in `codex.py` and `tests/test_relay.py` were preserved as the starting point. The two preexisting `Fix_Codex_Relay_*.py` scripts were not changed or removed.
- Source bytes and the original diff were backed up under `portfolio_autopilot/.local/relay-repair-20261027-114841/`, which is Git-ignored.
- Configuration and a consistent SQLite backup were saved under `%LOCALAPPDATA%\CodexRelay\repair-backups\20261027-115225/`. Further setup configuration backups also remain outside Git. Authentication files were excluded from these backups.
- No database schema migration was required. Existing Issue #1, `relay-demo-001`, its approval, scope grant, reply anchor and history were retained. The failed task was not silently retried or replaced by a new task/conversation.
- Per-task file grants, root-read denial, no direct sandbox filesystem writes, disabled command/external-tool capabilities, local approvals, trusted numeric GitHub IDs, message deduplication and public-output review remain enforced in application logic/configuration. Actual Windows junction and hard-link fixture tests pass.
- Local errors and full execution details are not automatically published. Normal status comments still use fixed text. The GitHub write test did not include credentials, full local paths or private logs.
- Approved native provisioning partially changed machine-level sandbox account/firewall controls before failing. Those shared controls were not globally uninstalled or rolled back, since other Codex sessions may use them. No broader read policy was enabled for AI tasks.
- Unrelated applications, WSL/Docker instances and shared WSL memory settings were not stopped or changed. No repository reset, commit, push, deployment, purchase or paid API-key execution occurred. No AI inference turn was started during this repair.

## Automated verification

| Suite | Result |
| --- | --- |
| Codex Relay | **71 passed** |
| Original Portfolio Autopilot | **10 passed** |
| Autopilot factory | **40 passed** |
| Opportunity Library | **49 passed** |
| Cleaning Business Pricing & Profit Calculator | **21 passed** |
| Original reporting demo | **14 passed** |
| **Total** | **205 passed** |

The reporting demo was run from `research_merge/reporting_demo`, its required import working directory; invoking it from the repository root initially produced an import error, and the correct invocation passed without modifying its code. Expected negative-test error text in the Autopilot/factory suites is not a suite failure.

Additional checks: Python compilation, JavaScript syntax, Git whitespace validation, authenticated loopback HTTP behavior, actual Windows `.cmd` launcher startup/exit, and schema discovery for both installed Windows executables. The live optional test was corrected to use the exact requested greetings and assert an unchanged thread ID, but **was not executed**.

New regressions cover named-profile call shapes, unavailable profiles, unsupported Windows policies, provisioning approval guards, preflight before threads, schema incompatibility/timeouts, secret/path redaction, diagnostic persistence failures, WSL UTF-16 resource errors, no installation on failed VM startup, exact Linux path grants, junction rejection, persistent execution blocking, interruption recovery and retained failed follow-ups.

## Live acceptance matrix

| Criterion | Actual result |
| --- | --- |
| Relay/dashboard starts | Passed launcher and authenticated HTTP smoke tests. |
| Relay GitHub authentication | Passed live as the configured owner. |
| Codex ChatGPT authentication | Passed live; reported separately from sandbox readiness. |
| Secure OS sandbox starts | **Blocked:** native backends reject the strict policy; WSL VM cannot start. |
| Current secure thread creation | Intentionally prevented by preflight; not claimed passed. |
| Current secure inference | Not run; blocked. The owner's previous broader-read CLI OK test is not equivalent. |
| Dynamic tool execution | Mocked protocol/file-tool tests passed; live test blocked. |
| Exact first greeting file | Not created by this repair; blocked. |
| Same-thread file correction | Mocked resumption tests passed; live test blocked. |
| OS negative-access/network tests | Not verified live in a functioning restricted sandbox. Application scope, traversal, junction, publishing and approval tests passed. |
| Failure/cancellation recovery | Unit and regression tests passed; live interrupted-inference resumption remains unverified. |
| GitHub inbox read through connection | Passed on the existing test Issue. |
| ChatGPT structured GitHub submission | Attempted once; denied with 403. No duplicate/spam Issue or comment created. |
| Reviewed completion retrieval | Existing historical comments retrieved. No new successful inference/result exchange claimed. |
| Correct local diagnostics/status | Passed; runtime retains the explicit execution blocker and successful sign-in status. |
| Complete end-to-end acceptance | **Not passed.** Requires both a working strict OS sandbox and an Issue-write-capable ChatGPT connection. |

## Files modified or added

Short filenames below are under `portfolio_autopilot/codex_relay/`; explicitly prefixed paths are relative to the repository root.

| Files | Change |
| --- | --- |
| `portfolio_autopilot/codex_relay/codex.py` | Stable executable preference, native/WSL transport, schema checks, named permissions, preflight, safer environment, local diagnostics, event/error handling and cancellation. |
| `config.py`, `permissions.py` | Validated backend settings, exact-file root-deny profiles, no shell writes, preserved Windows mode and lstat-based junction rejection. |
| `compatibility.py`, `diagnostics.py` | Fingerprinted protocol discovery and sanitized categorized local diagnostics. |
| `sandbox_setup.py` | Explicitly approved setup-only native provisioning helper. |
| `wsl_runtime.py`, `wsl_setup.py` | Prepared private WSL2 runtime, installer, login reuse and switch-on-verification behavior. |
| `scheduler.py` | Persistent execution circuit breaker, accurate interruption state and retained follow-up instructions. |
| `dashboard.py`, `static/index.html`, `static/app.js` | Authenticated local diagnostics, explicit execution-block display and separate sign-in/readiness status. |
| `__main__.py`, `__init__.py` | Diagnostics CLI, failing doctor exit status, safer config-save ordering and version 1.1.0. |
| `github.py` | Explicit JSON content type for outbound comments. |
| `live_test.py` | Exact greeting contents, same-thread assertion and explicit blocked/failure output. |
| `tests/test_relay.py`, `tests/test_compatibility.py` | Updated protocol mocks, isolated temporary diagnostic state and new regressions. |
| `portfolio_autopilot/Setup_Codex_Relay_WSL.cmd` | One-click, explicitly approved WSL2 setup. |
| `README.md`, `REPAIR_REPORT.md` | Current limitations, repair evidence, setup and acceptance instructions. |

## Exact next steps

1. Free enough Windows resources for Ubuntu WSL2 to start. This repair did not force a reboot or close unrelated work. If HCS resource errors persist after memory is available, the VM resource problem needs resolution before setup can proceed.
2. With the relay console closed, double-click `portfolio_autopilot/Setup_Codex_Relay_WSL.cmd`. Review its approval prompt. It can resume installation without changing source code.
3. Double-click the existing `portfolio_autopilot/Start_Codex_Relay.cmd`. Choose **Test connections**. Do not Resume tasks while the execution block remains.
4. After sandbox verification, run the opt-in two-turn test (`python -m portfolio_autopilot.codex_relay.live_test --approve-chatgpt-usage`) with the relay console stopped, or locally Resume the existing approved test task through the dashboard. Inspect the exact file and saved thread ID. Then run harmless OS deny-read/write/network fixture checks in the functioning environment.
5. Review the connected GitHub App's permissions for Hi62384/Proj. The connection must support **Issues read/write**. Approve a requested permission update or use a connection that actually offers those operations. Repository selection alone cannot add permissions the app never requested. Until then, manually posting the structured reply to the existing Issue is the limited fallback; the no-copy objective remains unmet.
6. Complete the README's reviewed-result and same-thread follow-up workflow. Do not mark the full acceptance test passed until those live steps actually succeed. Commit/push only if you decide to do so yourself.

Relevant primary documentation: [OpenAI app-server](https://learn.chatgpt.com/docs/app-server), [permission profiles](https://learn.chatgpt.com/docs/permissions), [Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox), [GitHub inaccessible-resource errors](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api#resource-not-accessible), and [installed GitHub App permissions](https://docs.github.com/en/apps/using-github-apps/reviewing-and-modifying-installed-github-apps).
