# Codex Relay completion report — October 27, 2026

**Verified working:** secure local development execution, real inference, exact-file creation/correction on the same persisted conversation, interruption/recovery, restart, GitHub pickup, reviewed-result delivery/readback, and normal Windows startup.

**Blocked externally:** posting a structured ChatGPT follow-up through the actual connected GitHub integration returns **HTTP 403, `Resource not accessible by integration`**. The complete remote follow-up cycle cannot be claimed passed. All independent repair and acceptance work is finished.

## What was broken and why

| Root cause | Repair and measured result |
| --- | --- |
| Native Windows isolation does not implement the required split restricted reads | Prior live native probes rejected the root-deny policy; elevated provisioning also encountered a locked desktop runtime (Windows error 32). Native task execution remains unselected. No broad-root task policy was enabled. |
| WSL2 startup failed with HCS `ERROR_NO_SYSTEM_RESOURCES` | Following explicit owner approval, created the previously absent `.wslconfig` containing only `[wsl2]` and `memory=1GB`. Ubuntu subsequently started and approved provisioning completed. The observation supports a resource constraint; it does not prove memory was the only possible HCS cause. |
| Private Linux Codex executable was hidden from Bubblewrap's bootstrap | `:minimal` includes system tools/loaders but not the privately installed static Codex executable. A separate diagnostic without its grant reproduced `bwrap: execvp …/bin/codex: No such file or directory`. Preserved the owner's exact-binary read grant, documented it, and regenerated the stale runtime profile. No root or whole-home read grant was added. Echo and its loader both worked after that grant. |
| Health checks could replace the profile during execution | A client lock now serializes health checks and runs. During an active task, health returns its last verified result with a busy indication. Live overlapping health/turn test passed. Linux config and schema-cache writes now replace files atomically. |
| Protocol validation cache could accept stale contracts or fail on damaged JSON | Cache contract 2 validates current required fields, including `excludeTurns` and permission-profile listing. Invalid cache JSON causes rediscovery. Earlier repairs already fixed named-profile request fields and stable executable selection. |
| Model interpreted its OS read-only policy as forbidding the approved host write tool | Clarified the bounded Windows-hosted capability in policy/tool descriptions. Reading an absent approved file returns `exists=false` and `sha256=new`; subsequent writes still enforce scope and hash checks. Actual tool calls then created and corrected the file. |
| No local answer/correction control | Added an authenticated, scope-reviewed local reply endpoint and dashboard control. It preserves the saved thread and approval. The production HTTP correction passed. |
| Pausing could discard the instruction being executed | Pause now retains the active instruction. A real turn acknowledged interruption, entered Needs Owner, then resumed the same thread to a read-only completion report. |
| Incoming replies could bind to an unpublished status anchor | Added a separately persisted last-published anchor, updated only after confirmed delivery/reconciliation; legacy state derives it from sent outbox records. Replies validate current scope and the actual published anchor. Obsolete fixed status notices are superseded without posting. |
| ChatGPT GitHub integration lacks usable comment-write access | It reads the existing Issue/result, but the approved real follow-up POST returned 403. Relay outbound authentication is separate and cannot repair that connector permission. No substitute PAT was used to simulate a ChatGPT-originating follow-up. |

## Active backend and setup

Saved backend: **WSL**, existing **Ubuntu WSL2**, normal Linux user, kernel **6.18.54.1-microsoft-standard-WSL2**, official Linux **Codex 0.162.1**, **Bubblewrap 0.9.0**. The approved installer reused the existing ChatGPT login in a private Linux home. GitHub credentials and the SQLite journal remain on Windows. Activation occurred only after authentication and strict preflight succeeded.

The named `relay-locked` profile denies root reads, permits minimal runtime reads plus approved exact files, root AGENTS.md and the exact private Codex executable, grants no OS writes, and disables model shell/JavaScript/web/plugin/app/multi-agent capabilities. The only model write capability is the Windows-hosted scope/hash-enforcing workspace tool. The deterministic preflight command is fixed owner-authored code, unavailable as a general model tool. External MCP server presence fails closed.

The 1 GB WSL limit affects other WSL2 distributions, including Docker, at their next start. The previous absence of `.wslconfig` was recorded at `%LOCALAPPDATA%\CodexRelay\repair-backups\wsl-memory-20261027-133844\previous-state.json`. No unrelated application/distribution was stopped and Windows was not rebooted.

## Live acceptance checklist

These are measured production-path results, separate from mocked tests.

| Acceptance criterion | Status | Evidence |
| --- | --- | --- |
| Ubuntu WSL2 starts | PASS | Actual Linux commands and app-server processes ran. |
| Linux Codex installation | PASS | Version 0.162.1 and generated app-server schemas validated. |
| Strict sandbox starts | PASS | Named-profile echo and Python security probes exit successfully. |
| Authorized read | PASS | Root AGENTS.md readable under the restricted policy. |
| Unauthorized filesystem access | PASS | Synthetic denied file read/create, no-byte write-open of read-only AGENTS.md, traversal and symlink reads all blocked. Existing Windows hard-link/junction tests also pass. |
| Network isolation | PASS | Synthetic WSL loopback listener reachable from outside the restricted process; connection blocked inside it. Listener has an owned stop nonce and a 30-second lifetime. This tests the measured local control, not every possible network topology. |
| GitHub relay authentication | PASS | Actual saved owner credential verified and existing Issue polled. |
| Codex ChatGPT authentication | PASS | Actual app-server authentication, followed by successful inference. No API-key billing mode used. |
| App-server thread and inference | PASS | Real production scheduler and dynamic-tool turns completed. |
| Exact first file | PASS | `codex_relay_demo.txt` created with bytes `Hello from Codex Relay\n`. |
| Exact correction on same thread | PASS | Authenticated dashboard local reply resumed the same saved thread; final bytes `Hello again from Codex Relay\n`. Every tracked-file hash was unchanged across this correction. |
| Restricted workspace tool | PASS | Real read/write requests recorded; only the approved demo was listed as changed. |
| Cancellation and recovery | PASS | Real `turn/interrupt` acknowledged; task paused, file unchanged, active instruction retained; same-thread read-only resumption completed. |
| Restart/history/no replay | PASS | Saved thread and 67 history rows present at restart check; duplicate polling did not claim or execute another turn. |
| Invalid RPC handling | PASS | Intentionally malformed `turn/start` rejected without inference; connection health subsequently passed. |
| Accurate dashboard/lifecycle | PASS | Real authenticated session/reply/start requests succeeded. Final task Awaiting Review. Runner stopped after verification. |
| Automated regressions | PASS | 215 tests across six suites. |
| GitHub task pickup | PASS | Existing Issue #1 read through the real relay; repeated pickup preserves the existing approved task. A new duplicate Issue was not created. |
| Reviewed result delivered and retrieved | PASS | Approved report posted once through the relay and read back through the actual ChatGPT GitHub integration. |
| Actual ChatGPT follow-up POST | BLOCKED | Approved connected-integration attempt returned 403. No follow-up was created; no connector-originated execution claimed. |
| Full remote follow-up cycle | BLOCKED | Depends on that external comment-write permission. Local same-thread continuation is verified. |
| Normal one-click startup | PASS | Actual Windows `.cmd` launcher with saved production configuration; authenticated dashboard, automatic GitHub/restricted health, preserved task, stopped runner, clean exit. Browser auto-opening is normal launcher behavior; this smoke test used `--no-browser` to inspect the same server without opening another window. |

Private detailed evidence is retained in `%LOCALAPPDATA%\CodexRelay\live-acceptance.json` and the local task journal. It contains private thread identifiers and must not be posted publicly. This report is the local completed/blocked acceptance checklist.

## GitHub communication result

Existing task: `relay-demo-001`, existing Issue #1. Approval, file scope and saved conversation were retained.

The one owner-approved reviewed result was published to [Issue #1, verified result comment](https://github.com/Hi62384/Proj/issues/1#issuecomment-6453301604). The actual connected integration fetched that exact receipt. Nine obsolete queued status notices were suppressed; no duplicate result was posted.

The one approved structured follow-up requested: “Confirm the final greeting and return a completion report without modifying files.” Its real connected-integration submission failed with **403 Resource not accessible by integration**. No credentials, full local paths, private logs or session identifiers were included in the public receipt. Further POST attempts were stopped. Outbound relay credential success is not evidence of ChatGPT connector write access.

**Smallest required owner action:** inspect the GitHub App installation used by the ChatGPT GitHub connection. Confirm that Hi62384/Proj is included and approve Issues read/write if the app requests it. If comment-write access is not among its requested permissions, a supported write-capable connection is required; reconnecting alone is not a demonstrated fix. After access changes, one structured follow-up on the existing Issue can complete the remaining test. The local reply control already works without that external permission.

## Automated and unit-only verification

| Suite | Passed |
| --- | ---: |
| Codex Relay | 81 |
| Original Portfolio Autopilot | 10 |
| Autopilot factory | 40 |
| Opportunity Library | 49 |
| Cleaning pricing calculator | 21 |
| Original reporting demo | 14 |
| **Total** | **215** |

The reporting suite ran from its required `research_merge/reporting_demo` working directory. Expected negative-test error messages are not test failures. New regressions cover local reply authorization, last-published anchors, unpublished-anchor denial, obsolete-status suppression, interrupted instructions, absent-file creation, health/run serialization, exact bootstrap grants, and incomplete/failed security-probe rejection. Existing tests cover scope revocation, trusted identities, duplicates, restart, ambiguous publication, HTTP authorization, traversal, links, protocol failures, and stale file hashes.

**Unit-tested only:** specific simulated transport/rate-limit/ambiguous-POST faults, hostile-message variants and schema failure combinations were not all injected into the real GitHub account. Future runtime upgrades, other computers/distributions and native MXC were not acceptance-tested. The standalone opt-in live-test helper was not rerun over the existing demo; actual production scheduler/dashboard tests supplied the live evidence above. Python compilation, JavaScript syntax and Git whitespace checks supplement the suites.

## Files modified in this repair

Paths below are relative to the repository root. Earlier committed repair infrastructure is distinguished from this working-tree change; no commit or push was made.

| File | Change |
| --- | --- |
| `portfolio_autopilot/codex_relay/__main__.py` | Automatic configured startup health; wait for health before closing the journal. |
| `portfolio_autopilot/codex_relay/codex.py` | Host capability clarification, health/run serialization, request-denial audit and interrupt acknowledgement. |
| `portfolio_autopilot/codex_relay/dashboard.py` | Authenticated local reply endpoint and health after setup. |
| `portfolio_autopilot/codex_relay/permissions.py` | Preserve/extend owner's exact WSL bootstrap grant; invoke live negative-access probes. |
| `portfolio_autopilot/codex_relay/sandbox_probe.py` | New fixed security probes, positive network control, bounded cleanup. |
| `portfolio_autopilot/codex_relay/scheduler.py` | Local replies, retained paused instruction, published-anchor handling, obsolete statuses and read-only inbox sync. |
| `portfolio_autopilot/codex_relay/store.py` | Durable outbox supersession and legacy published-anchor lookup. |
| `portfolio_autopilot/codex_relay/static/app.js` | Local answer/correction form with scope review. |
| `portfolio_autopilot/codex_relay/workspace.py` | Explicit host write authorization and coherent absent/read/hash results. |
| `portfolio_autopilot/codex_relay/wsl_runtime.py` | Atomic generated config/cache replacement and cache contract validation. |
| `portfolio_autopilot/codex_relay/tests/test_relay.py` | Remote fixtures now reference actually delivered messages. |
| `portfolio_autopilot/codex_relay/tests/test_live_repairs.py` | Ten new regression tests. |
| `portfolio_autopilot/codex_relay/README.md` | Current verified status and normal operation. |
| `portfolio_autopilot/codex_relay/REPAIR_REPORT.md` | This report/checklist, replacing superseded blocked-state report. |
| `codex_relay_demo.txt` | Actual model-created/corrected harmless acceptance artifact, left for owner review. |

## Preservation and normal startup

Starting HEAD was `40b8310a2bbb2202f95bee707d9e55dfcad22c4d`; the initial permissions.py edit was preserved. Source snapshot/diff: `portfolio_autopilot/.local/relay-live-repair-20261027-133526/`. Config and consistent SQLite backup: `%LOCALAPPDATA%\CodexRelay\repair-backups\live-20261027-133547/`. Authentication was excluded from those backups. Existing task, approval, scope, conversation and history remain intact. Older native setup controls were not globally uninstalled because other Codex sessions may use them. No repository reset, commit, push or unrelated application shutdown was performed.

1. Double-click `portfolio_autopilot/Start_Codex_Relay.cmd`. Saved configuration and sign-ins are reused; automatic connection checks appear in the dashboard. No setup command is needed.
2. Click **Start runner**, then approve new task scopes locally. The existing demo is **Awaiting Review** and is not automatically rerun.
3. For a local correction, select the task, open **Answer or correct this task locally**, enter the instruction, review the scope checkbox, and click **Send local reply / resume**. This keeps the existing conversation.
4. Review each report before releasing its text to GitHub. Use **Stop runner** to pause, or close the console/Ctrl+C to exit.

The local development path is usable now. Fully automatic ChatGPT-originated GitHub follow-ups remain blocked by the precisely observed external permission failure above.
