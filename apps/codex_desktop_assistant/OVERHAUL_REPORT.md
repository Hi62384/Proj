# Desktop Assistant overhaul — October 28, 2026

Implemented directly in the existing application. No Relay source, GitHub issue, storefront, payment account or public listing was changed. No commit or push was made. No dependencies were added.

## Delivered

- A redesigned dark/light native Qt interface, differentiated messages, Markdown/code/tables/images, compact controls, collapsible chat sidebar and activity panel, and expandable detailed activity history.
- Main-screen Model and Reasoning selectors populated from the authenticated runtime catalog. This account returned eight models; efforts are taken separately from each model. Selection is saved atomically and sent as actual `turn/start.model` and `turn/start.effort`. Changes affect the next turn.
- Main-screen Selected Window / Entire Monitor controls, target picker, refresh, enable/revoke, observation indicator and program-launch option. Monitor access dynamically includes ordinary windows fully inside its bounds without granting each individually. Changed display geometry stops access for review; excluded/authentication/security/assistant windows stay protected.
- Discovery and argument-free launching of installed GUI programs through machine/user App Paths and Start Menu entries within protected installation roots. Windows utility launch targets are limited to ordinary supported apps. Console executables, shells, scripts, installers and unknown download paths are refused. Elevation is not requested automatically. Native filesystem/shell-window activation receives additional owner review.
- Independent foreground monitoring and observational Windows keyboard/mouse hooks. Bringing chat forward during a desktop task pauses input; switching away does not resume it. Physical-input signals close the desktop gate. The application never locks or swallows physical input. Cancellation is checked between fallback typing characters and drag steps; already-dispatched atomic operations cannot be undone.
- System-tray Windows notification integration, taskbar attention, unread Requests indicator and focus-to-pending-conversation behavior. Generic notification text avoids filenames, document contents and account details. Preferences independently control requests, errors and completion updates; duplicate notices are suppressed.
- Independent read/write/create/delete Allow/Ask/Deny rules for exact files, direct-child folders and recursive project/folder scopes. Broader scopes require risk acknowledgment. Matching Deny always wins. Preferred policy persists; session approvals expire on Stop or close. Broad desktop authority never reactivates on restart.
- Interactive chat permission cards with exact target, reason, duration, recovery information, text diff where applicable, Allow Once / Allow for This Session / Deny. Requests expire in five minutes and are tied to conversation, action, target and permission generation. Deletion has an additional confirmation. Generic owner decisions cannot grant tool permissions.
- Real file read, listing, text overwrite, creation and recoverable deletion, including empty folders. Binary files return metadata/hash for deletion rather than fabricated text. Parent and file handles reject reparses/hardlinks, prevent replacement, revalidate identity/content after review, preserve uniquely named originals and verify results. Mutations are not replayed automatically.
- Safe pending-action behavior: file approval can complete while desktop input stays suspended. For a consequential desktop/browser action, approval is retained and dispatch waits for explicit Resume when chat has paused input. The same task/thread continues.
- SQLite backup before the first upgrade open. Existing conversation IDs, Codex thread IDs, attachments and authentication are preserved. The installed runtime cannot replace dynamic tools on resume, so older saved tool schemas use compatibility aliases through the current policy; they do not require replacement chats.

## Verification

**61 assistant tests and 81 original Relay tests passed (142 total).** These include real Windows file operations; policy combinations and race/cancellation cases use targeted fault injection where needed. Compilation and whitespace checks passed.

The following were also exercised with the real authenticated Codex runtime and real native Windows/Chromium fixtures, not fabricated model responses:

| Workflow | Result |
|---|---|
| Account catalog, supported effort lists, actual turn parameters | Passed; eight account models, actual Sol/low turn traced |
| Native dark/light UI and resizing | Passed; synthetic screenshots saved |
| Selected-window isolation | Passed with disposable native editors; unrelated editor denied |
| Real window movement/resizing | Passed after repairing an unsupported UIA wrapper method |
| Two real windows under one monitor grant | Passed without individual window grants |
| Actual Codex edit within monitor scope | Passed and independently inspected |
| Installed Notepad launch through Codex | Passed; no private Notepad document was inspected or modified |
| Chat focus auto-pause, no resume on switch-away | Passed using actual foreground changes during real inference |
| Explicit Resume retaining thread | Passed |
| Sensitive synthetic action, chat approval and explicit Resume | Passed on the same pending operation |
| Native input hooks | Registered successfully; physical-input callback path additionally tested with an injected signal |
| Read/create/write/delete through real Codex and local approval buttons | Passed, including recovery bytes and deletion confirmation |
| Allow Once, reusable session read approval, denial | Passed; denied change did not occur |
| Old saved tool schema using current file policy | Passed on a retained real Codex thread |
| Notification fallback/unread/focus routing | Passed; native notification API integration is present |
| Existing chat streaming, saved thread restart, screenshot perception | Passed |
| Existing five-format model attachments | Passed |
| Dedicated browser form, upload, dynamic page and redirect isolation | Passed |
| Existing browser via native Windows control | Passed |
| Active corrections, takeover, manual change and same-thread resume | Passed |
| Actual Ctrl+Alt+F12 and revoked-input denial | Passed |
| CMD launcher, native pythonw window, normal close and retained state | Passed |

Private, synthetic evidence is under `%LOCALAPPDATA%\CodexDesktopAssistant\verification\`:

- `overhaul-20261028-155815/results.json`: complete new UI/model/file/monitor/launch/focus/resume acceptance.
- `overhaul-20261028-160152/results.json`: old saved-tool-schema compatibility, including real session approval and recoverable deletion.
- `overhaul-20261028-160903/results.json`: final redesigned controls and sensitive-action approval followed by explicit Resume, plus monitor, program launch and foreground checks.
- `20261028-155930/results.json`: complete original real Codex/browser/desktop/attachment/steering/takeover/hotkey regression.
- `controllers-20261028-160421/results.json`: actual controller, browser upload, redirect and emergency-stop checks.
- `launcher-20261028-160426/results.json`: native Windows launcher verification.
- `ui-20261028-154346/results.json`: original UI controls and real Codex response. A later short UI smoke run passed controls/persistence but ended its 20-second model wait while startup was still queued; the longer real integration runs above confirmed inference.
- `owner-launch-20261028-161518/results.json`: finished app opened through the actual launcher, connected successfully with all restricted-runtime checks passing. The two existing conversations and 22 existing messages were compared by content hashes and preserved; a consistent pre-upgrade backup was confirmed. The application was left open with desktop authority disabled.

Earlier partial runs remain marked as failed in their own evidence. They exposed a test-driver confirmation issue, redirected Python child-process identification, native window-resize support and the turn-completion/interrupt race. The implementation now waits for confirmed turn completion after interruption, refuses late tools and never replays an uncertain action.

## Practical limits and remaining validation boundaries

- Physical hardware typing/mouse collisions were not performed by a human during acceptance. Actual hooks registered; injected physical-input signals and real focus changes tested the gate. Input already dispatched to an application remains subject to that application's atomic boundary.
- Windows notification settings may suppress a native banner. Taskbar/in-app fallback, unread state and focus routing were verified; a visible OS banner and clicking that OS banner were not independently observed.
- The actual machine's display was used; live monitor unplug/reconfiguration, all multi-monitor/DPI combinations, Windows lock and sleep were not forced. Scope/layout rejection has automated coverage. Windows crossing a monitor boundary must be moved fully inside or explicitly authorized via all-monitor scope.
- Notepad launching was live-tested. Editing/observation and isolation were verified using disposable Qt editors to avoid exposing existing Notepad tabs or private documents. This is not a claim of exhaustive testing in every Windows application.
- Direct file operations are limited to 500 KB and UTF-8 text replacement. Binary read returns metadata/hash. Directory deletion is limited to empty folders; recursive destructive deletion is refused. Recovery uses private backups rather than a guaranteed Recycle Bin transaction. Backups are not encrypted by the application.
- Portable programs outside the trusted installation roots require manual launch. Installers, scripts, terminal commands and administrator actions remain manual/separately authorized workflows.
- Original browser limitations remain: exact approved origins, blocked WebSockets and unsupported redirect patterns, human authentication/CAPTCHA/MFA and consequential external-action review. No universal website compatibility is claimed.
- Screenshots are captured as needed and held in memory by the UI; Codex/provider retention is separate. No promise of zero provider retention is made.

## Open and use

Run `Start_Desktop_Assistant.cmd`. Select Model and Reasoning, choose the desktop mode/target and Enable Access, optionally enable program launching, and set file rules using Permissions. Send your task. Use Requests for pending decisions, Resume after an intentional pause, and Ctrl+Alt+F12 for emergency stop. See README for the detailed operating guide and test commands.
