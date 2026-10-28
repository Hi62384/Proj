# Codex Desktop Assistant — implementation and acceptance report

Date: **October 27, 2026**, America/Vancouver.

**The native application and the core model-driven desktop/browser workflows passed real acceptance tests.** This is a working Qt application, not a hosted page or simulated chat. No live storefront, payment flow, publication, commercial message or purchase was used for testing. The existing file-only Relay's source is unchanged.

## Delivered application

Open `apps/codex_desktop_assistant/Start_Desktop_Assistant.cmd`. The installed managed environment launches a native `pythonw.exe` window, connects internally, and reuses the existing ChatGPT account. No GitHub Issue, API key, normal Codex desktop window, or separate manually started server is needed.

The application includes independent conversations and saved Codex threads; live streamed Markdown chat; model/effort discovery; durable mid-turn corrections; attachments/previews; native Windows accessibility and bounded pixel input; a dedicated persistent Chromium profile; existing-browser control through Windows; local questions/approvals; pause/takeover/resume/stop; a global emergency shortcut; local SQLite state/recovery; scoped permissions; retention/settings; and the Cedargrid draft-workflow preparer.

Source modules and their responsibilities are listed in [README.md](README.md). Dependencies are installed privately and pinned in `requirements.lock.txt`. A standalone bundled EXE was not produced; the working managed one-click launcher is the supported delivery.

## Actual acceptance results

The full test calls the production native UI/coordinator, real authenticated app-server, image-capable model and real host controllers. Its only pre-approvals are restricted to disposable test-window handles, a localhost origin and synthetic fixture files. It does not use a fake Codex response.

| Requirement / test | Measured result |
| --- | --- |
| A — Application launch | **PASS.** Real native window exposed and responsive. Actual CMD launcher created a native pythonw window, persisted its state and closed through its normal window-close path. |
| B — Real Codex chat | **PASS.** Owner prompt entered through the native UI received the exact requested synthetic response. Streamed delta events were observed and persisted. ChatGPT account authentication was required by the actual runtime. |
| C — Conversation persistence | **PASS.** UI/coordinator closed and reconstructed; the saved thread resumed and recalled the synthetic token. Thread equality was checked. Independent-conversation state and no crash replay also pass unit tests. |
| D — Screenshot perception | **PASS.** A random code was painted in a native widget with no accessible text equivalent. Codex received an actual screenshot tool image and identified the code. Saving a screenshot alone was not counted as perception. |
| E — Windows automation | **PASS.** Codex used the actual controller to fill a native text field, choose Teal, check Ready and activate Apply draft. The resulting fixture state was checked independently. |
| F — Dedicated browser | **PASS.** Codex navigated a localhost form, filled fields/dropdown/checkbox, attached a granted fixture, verified dynamic text and submitted the local upload. The server received the expected file bytes. |
| F — Native/browser Mode B | **PASS.** Codex operated the owned browser window using desktop inspection/actions rather than browser editing capabilities. Changed form output was verified independently through actual accessibility state. Personal browser tabs/cookies were not accessed. |
| G — Attachments | **PASS.** The real model correctly read unique tokens/content from an image, text file, spreadsheet and PDF, and identified a ZIP member without extracting/executing it. DOCX extraction is parser-tested separately. |
| H — Takeover/resume | **PASS.** A real turn was stopped at a pending fixture action. New input was denied. The owner test harness made an actual manual change in the native application. Resume retained the same thread, and Codex recognized/preserved the new random value. The manual change was synthetic; no login was automated. |
| I — Communication during work | **PASS.** A real active turn accepted a correction through `turn/steer` and incorporated the requested marker. Corrections were durable before acknowledgement. |
| J — Unapproved/revoked input | **PASS.** Unapproved windows/origins, revocation, paused input, stale epochs and old-turn tools are denied by the controller/broker/state tests. Native pause/revocation were also exercised live. |
| J — Emergency stop | **PASS.** The actual registered Ctrl+Alt+F12 chord triggered the independent Windows message thread and disabled new input. |
| J — Restricted OS execution | **PASS.** Real preflight must pass authorized read plus denied file read/write, read-only write, traversal, symlink and network probes before the first model turn. Root reads/writes remain denied; only exact runtime executables/instruction file are read-granted. |
| J — Sensitive action review | **PASS in unit/state tests.** Consequential labels and unrecognized actions require local review. Pixel clicks/drags cannot use generic routine-label pre-approval. No real purchase/publication/account-security submission was performed. |
| Windows launcher/lifecycle | **PASS.** Native CMD startup, visible window, normal close and persistent SQLite state independently verified. No owner application was closed by that test. |
| Settings and privacy controls | **PASS.** Actual rename/pin/archive/restore, attachment removal, light-theme save, Stop/revocation and restart-without-grants checks passed. Protected local history, scoped window inventories and URL-query stripping are regression-tested. |
| Existing Relay | **PASS.** Its 81 tests passed; a separate real authenticated strict sandbox health check passed. No Relay turn or public comment was generated by the preservation check. |
| Cedargrid preparation | **PASS locally.** Existing draft and nine local assets were indexed. UI workflow prepares the reviewed unpublished-listing plan. No Payhip account was opened. |

## Reproducible private evidence

Results, fixture state and explicitly captured harmless test images remain under `%LOCALAPPDATA%\CodexDesktopAssistant\verification\`. The files contain local conversation metadata and should not be published wholesale.

- `20261027-201323/results.json`: real chat/streaming, same-thread restart, screenshot perception, native actions, five attachment formats, browser upload, steering and takeover/manual-change/resume passed.
- `20261027-203427/results.json`: repeated full core model-driven acceptance passed on the completed runtime/image integration.
- `20261027-204113/results.json`: both browser modes, followed by active steering and takeover/manual-change/resume, passed.
- `controllers-20261027-200314/results.json`: real native input/capture, pause/hotkey, approved redirect, rejected redirect, dynamic browser form, actual uploaded bytes and revocation passed.
- `ui-20261027-202739/results.json`: native controls, real model response, settings save, Stop and reconstructed UI/state passed.
- `launcher-20261027-201812/results.json`: actual CMD/native pythonw launch, normal close and persistent state passed.

Latest complete real acceptance: **`20261027-204837/results.json` — every recorded criterion passed**, including both browser modes, screenshot perception, five attachment types, steering, takeover/manual change/same-thread resume and emergency stop. Its capability journal was independently checked: native-browser editing used desktop operations, with no completed Playwright edit operation during that phase. All seven strict OS security checks were also read back as true.

Later UI smoke tests can end their short model wait while startup is still retrying; that is not used as evidence of a model failure or fabricated success. The full acceptance waits for actual connection and checks actual model output.

## Root causes repaired during implementation

1. **Incomplete private runtime copy.** Copying only the Codex executable allowed chat but dynamic tools failed because `codex-code-mode-host` was absent. The application now copies that official packaged companion too and grants read access to that exact private executable. It keeps shell/JavaScript/plugin/app tools disabled and checks the installed schemas rather than replacing the policy with unrestricted execution.
2. **Windows label/value confusion.** Accessible edit names and values are separate; the controller now uses the actual accessibility name, reports current values/toggle state and checks the real Windows password property.
3. **Qt dropdown selection was unreliable through its reported selection pattern.** The Qt adapter uses focused, escaped text search when needed and verifies the resulting selection. It does not infer success from an attempted input call.
4. **Navigation/read race.** A successful form action could replace the page while inspection was reading it. Only the subsequent read is retried; the action itself is not replayed.
5. **Redirects bypassed a naive route check.** A two-server localhost experiment demonstrated that continuing an allowed request can follow a redirect without a second route callback. The final implementation fetches without automatic redirects, checks each destination and follows allowed document redirects explicitly. Disallowed destinations are not contacted. Unsupported mutation-preserving redirects stop for review.
6. **Intercepted multipart bodies omitted uploaded file bytes.** Upload reconstruction restores only the exact owner-approved origin/field/file mapping and enforces the file limit. The test server verifies actual bytes, not just the displayed filename.
7. **Pause, late calls and shutdown races.** Held messages are persisted; explicit Resume/Continue retains their content. Approval epochs and turn IDs invalidate stale actions. Closing-state guards/timer shutdown prevent queued Qt callbacks from touching a closed database.
8. **Windows WSL startup was intermittent.** It failed with HCS resource errors/timeouts even when several GB were free. The owner-approved 512 MB experiment failed and was restored to the prior 1 GB limit. The approved service restart stalled in Stop Pending; a guarded administrator helper finished recovery only after checking no WSL VM existed and that the process hosted WSL alone. The service returned to Running. Startup-only failures now have three bounded retries before any AI turn, with no task/action replay. This is not proof that RAM was the sole cause or that future Windows startup faults are impossible.

The 512 MB experiment's original config is preserved under `%LOCALAPPDATA%\CodexDesktopAssistant\system-backups\20261027-193018\wslconfig.previous`; the active `.wslconfig` was restored to `[wsl2]` / `memory=1GB`. `%LOCALAPPDATA%\CodexDesktopAssistant\service-recovery.json` records successful guarded recovery. No reboot, virtualization-host service restart, feature change or unrelated application shutdown was performed.

## Automated verification

**35 application regression tests and 81 original Relay tests passed** on Windows. New tests cover exact origins, scoped window inventories, real Office extraction, ZIP non-execution/bounds, image transport/geometry metadata, protected files, stale hashes, local retention, crash/no-replay state, same-thread protocol resumption, actual steer request shape, ambiguous starts, stale tool calls, queued corrections, typed Continue without re-granting stopped scopes, approval/revocation, enforced authentication handoff, renamed-console denial, and lock/sleep detection transitions. Python compilation and new-source whitespace validation passed.

Mocked transport/fault cases are explicitly unit evidence. Real acceptance evidence is the production-path matrix above. Windows was not intentionally locked or suspended; active-desktop recognition was verified live and sleep/secure-desktop transitions were tested with injected state. Other monitor arrangements and every possible application/browser version were not exhaustively exercised.

## First-run permissions and remaining limits

- Normal startup reuses the supported ChatGPT login and private runtime. Select exact windows, observation/input capabilities, website origins, files and application launches locally. Grants are session-bound and disabled after restart. Opening a website is not a payment/publication grant.
- The generic Windows accessibility/visual layer supports approved applications, including browser windows; specialist Excel/Godot/Blender APIs and their complete business workflows were not individually acceptance-tested. Voice is an extension point, not an included engine.
- WebSockets, arbitrary JavaScript, unknown server tools, and unsupported redirect/form patterns remain unavailable. Some websites require additional explicitly approved origins, manual steps or an adapter. Broad routine-label grants are not a semantic proof that every button is harmless; keep them tied to the intended task and review consequential operations.
- This application does not write ordinary screenshots to disk. Codex/runtime/provider conversation retention is separate; **zero provider/runtime image retention cannot be guaranteed**. Local history/attachments/backups are private user files, not application-encrypted storage.
- UTF-8 text, modern Office formats, text PDFs, supported images and ZIP inventories are supported. OCR for scanned PDFs and native interpretation of every binary/legacy format are not included.
- Actual Payhip login, draft account modifications, uploads and hidden-listing changes await the owner's explicit account-session authorization. Publication, payments, account security, CAPTCHA/MFA and identity steps require owner handling/review. No such real account action was part of acceptance.
- Windows WSL resource faults can still prevent a future connection. The application reports them and fails closed; it does not silently weaken isolation. Service recovery is owner-approved maintenance, never a model capability or automatic startup action.

## Repository preservation

Starting Git HEAD was `8fc8aa56a419f281aca0b3ba174e19278ea7ef66`; initial Git status was clean. All delivery files are under `apps/codex_desktop_assistant/`. Existing tracked source and the Relay permission profile implementation were not edited. Runtime databases/authentication/browser data stay outside Git. No reset, commit, push or public release was performed.

The Relay remains a separate file-only tool. New desktop permissions, browser sessions, conversations, data directory and Linux Codex home belong solely to this application. Its GitHub workflow/token is not used by the new chat application.
