# Codex Desktop Assistant

A native Windows chat application with persistent Codex conversations, approved screen observation, Windows accessibility control, and a dedicated automation browser. It uses your existing ChatGPT login, without GitHub Issues or a separately billed API key.

**Continuous execution is now the default.** Mouse/keyboard activity, switching apps and opening chat never pause an active task. See [CONTINUOUS_EXECUTION_REPORT.md](CONTINUOUS_EXECUTION_REPORT.md) for current verification; [OVERHAUL_REPORT.md](OVERHAUL_REPORT.md) and [INTEGRATION_REPORT.md](INTEGRATION_REPORT.md) are historical baselines. Tests used disposable Windows and localhost browser fixtures; no storefront, payment account, purchase, publication, or commercial message was touched.

## Open the application

Double-click **Start_Desktop_Assistant.cmd** in this folder. It opens the native application and starts its internal components. You do not need another terminal, server, GitHub Issue, or the normal Codex desktop window.

The managed `.venv` is already installed on this computer. On a fresh checkout the launcher invokes **Setup_Desktop_Assistant.cmd** to install the pinned free dependencies and Playwright Chromium. Python 3.11+ and the existing verified Ubuntu WSL2/Codex installation are required. Installation needs Internet access. A managed Python launcher is supplied rather than a bundled standalone EXE.

On first connection the application copies the official Linux Codex executable, its required `codex-code-mode-host` companion, and the existing supported ChatGPT login into its own private Linux home. Its subsequent runtime configuration and authentication are independent of the Relay. It does not import GitHub credentials, ordinary browser cookies, plugins, or API-key environment variables. Only ChatGPT authentication is accepted. Ordinary startup needs no administrator permission.

## Chat and conversations

- Use **New Chat**, type an instruction, then **Send** or **Ctrl+Enter**. Responses stream into the chat. Markdown, code blocks, tables, links, and attached images are displayed locally.
- Conversations have independent saved Codex thread IDs. Search, rename, pin, archive/restore, or delete local history from the sidebar. Switching views leaves an active task associated with its original conversation; the toolbar identifies work in another conversation.
- A correction sent during work is durably saved and delivered using the installed protocol's `turn/steer`. If delivery is ambiguous it remains explicitly marked for review, with no automatic replay.
- **Stop** prevents new automated input and interrupts the turn. **Continue** is an explicit owner action and retains saved context and held corrections; it cannot restore desktop grants revoked by Stop/restart. Human requests use **Done — Continue** and stay on the same pending call/turn. After a crash, unfinished tasks require review and are never automatically replayed.
- The model picker comes from the actual account's `model/list`. Reasoning efforts are shown only when supported by the selected model. Changes apply to subsequent turns.

## Enable computer access

Computer permissions start disabled and are not silently restored after a restart.

1. Choose **Selected Window** or **Entire Monitor** on the main toolbar. Refresh the picker, select the exact window or display, and choose **Enable Access**. All monitors is an explicit option when multiple displays exist. A first-use consent explains screenshot delivery to your account; the preference is remembered, desktop authority is not.
2. Selected Window authorizes only that exact window identity and ordinary owned dialogs. Entire Monitor authorizes ordinary windows fully inside the selected display, including newly opened windows, without per-window approvals. Windows spanning outside the scope are refused; move them fully inside or authorize all monitors. Changed display geometry requires renewed authorization. Sensitive/excluded windows are masked in monitor captures.
3. Screen observation is enabled with authorized desktop access. **SCREEN OBSERVATION ON** remains visible. Captures are sent only when needed. **Preview approved screen** is local only. Sensitive password fields and authentication/security windows require manual handling.
4. **Allow Program Launches** enables discovery and argument-free launching of ordinary installed apps from machine/user App Paths and Start Menu entries under Windows, Program Files or the protected per-user Programs folder. No shell, scripts, installers, updater, terminal, downloaded executable or elevation path is exposed. Portable apps outside trusted installation roots require manual launch. Console-subsystem executables are also rejected. Launched windows gain control only inside the active monitor scope; Selected Window never expands automatically.
5. Native controls support text, buttons, checkboxes, dropdowns, focus, movement/resizing, bounded shortcuts, mouse movement, scrolling and dragging. Pixel input requires a fresh capture and live geometry. Ordinary semantic actions within desktop scope run without repetitive prompts. Consequential actions and coordinate clicks/drags still require exact local review. Routine desktop/browser controls no longer need a label allowlist. The host distinguishes text entry from actual activation using the live target context.

The sidebar and activity panel collapse independently. Activity History hides raw capability details. Model and Reasoning sit side by side and use the actual account catalog; unsupported efforts cannot be selected. A model switch chooses its advertised default when necessary and explains the adjustment. Both selections persist globally and are captured together for the next turn, leaving an active inference unchanged.

The controller refuses authentication/password controls, terminal/security windows, the assistant's own permission UI, and private clipboard paste. Use **Take Over** for those steps. App-specific automation for Excel, Godot, Blender and other applications uses this common accessibility/visual layer; specialist APIs for every application are not included or claimed tested.

## Browser modes

**Dedicated browser:** approve exact HTTP(S) origins in **Settings → Browser website origins** and enable it. Codex opens a separate persistent Chromium profile. Your normal browser stays separate. Additional login/CDN origins must be reviewed explicitly. No ordinary-browser password/cookie import occurs.

**Your existing browser:** select its exact window in the main Desktop Access picker. Codex operates it through the native controller; it does not attach to a debugging port or extract its session. This mode has the same window and human-review boundaries as other Windows applications.

The dedicated browser supports navigation, semantic fields/buttons/dropdowns/checkboxes, tabs, dynamic content, screenshots, approved attachment uploads, and private downloads. Redirect destinations are checked at every hop; approved document redirects are followed as fresh GET navigations without replaying a submission. Unsupported mutation-preserving/subresource redirects stop for review. WebSockets and automatic dialogs are blocked, so some sites may need a specialist adapter or manual handling. This is not a claim of universal compatibility with every website.

Uploads accept only attached files approved for that conversation; the UI reviews the destination/action. Downloads receive generated private filenames and are never automatically executed. Network mutations outside the brief approved action are blocked. During a pending manual step, manual browsing is enabled within the approved origins while automated browser/desktop input is gated. Done returns control to the same task. Password entry, MFA, CAPTCHA, identity checks, purchases, publication and account-security decisions belong to the owner.

## Routine actions and consequential approvals

Text entry, including multiline Notepad editing and browser textarea filling, runs without approval inside the authorized scope. Newline characters and words in a document/field label do not turn text into a submission. Ordinary buttons, selection, scrolling and approved-origin navigation are routine. A standalone Enter key is evaluated separately: it inserts a newline in a verified editor, but can activate a form/default button elsewhere.

Actual POST form submission, send/purchase/publication/security/destructive controls, file transfers and native file saves retain explicit review. Each request shows why it needs authorization and identifies the target. The separate direct-file Read/Write/Create/Delete policy is unchanged; Entire Monitor access grants no direct file rights. Unknown pixel targets still need exact review because their action cannot be established from a semantic control. Credentials, auth prompts and unsafe keyboard fallbacks stay protected.

See [ROUTINE_EDITING_REPORT.md](ROUTINE_EDITING_REPORT.md) for real Notepad/Codex verification.

## Working while you use the computer

Codex keeps reasoning and working when you type, move/click/scroll the mouse, open chat, switch apps or minimize/restore the assistant. There is no focus-triggered pause and ordinary input never sends `turn/interrupt`.

Prefer the **dedicated browser** for website work. Playwright uses semantic browser interactions without moving the Windows pointer or taking keyboard focus. You can type in another application or send chat corrections while browser work proceeds. Account authentication, approved origins and consequential-action permissions still apply.

Windows has one foreground focus and pointer. The input coordinator observes physical activity without logging keystrokes or swallowing input. Injected automation events are distinguished from physical events. Background accessibility actions can proceed in other windows. Shared-pointer/focus actions wait for a short quiet interval, including held modifiers/buttons; actions targeting an actively edited window also wait. Only that host action is deferred, on a bounded worker queue. The model loop continues handling messages and independent browser calls. The activity panel may say **Waiting for input access**; no notification or task interruption is generated for this routine condition.

Before dispatch the controller validates the window identity, authorization epoch, observation token and editable field values. Owner changes since inspection cause a re-inspection request instead of overwriting them. Shared keyboard fallback uses at most 256 characters and checks focus/cancellation between characters, with a two-second transaction budget. If the owner takes input mid-transaction, remaining input stops and the model must inspect partial state; uncertain actions are never replayed automatically. A continuously busy input channel returns a specific blocker after five seconds so the model can choose other work. No independent second cursor is promised.

## Task states, human requests and Stop

The main states are **Ready**, **Working**, **Waiting for User**, **Stopped**, **Completed**, and **Error**. Ordinary input is never a human-decision state.

When Codex genuinely needs a manual step, its chat card explains exactly what to do and includes **Done — Continue**. Complete the step in the authorized app/browser and click that button, or type **Done** in the corresponding chat. The same tool call, turn and saved thread continue. Codex must inspect the current interface and verify the condition, preserving manual changes and skipping completed submissions. **Cannot complete** returns a negative result to Codex. Do not put passwords, OTPs or account secrets into chat.

File/operation approvals remain exact: **Allow Once**, **Allow for This Session** where suitable, and **Deny**. The pending operation proceeds when allowed without a separate Resume click. Denial is returned to the current workflow. Outstanding requests expire after five minutes or on Stop/revocation; no permission survives as an unbounded pending approval.

Notifications identify a safe category (for example account verification, CAPTCHA or file deletion) while the full specific instructions stay in the relevant chat. Windows can suppress banners; taskbar attention, the Requests unread count and in-app cards remain. Notification clicks focus the pending conversation. Requests, significant errors and optional completion notices have separate preferences. Ordinary input/conflict deferrals never notify.

- **Stop** immediately closes new-input dispatch, cancels queued host actions and interrupts the active turn. History and verified results remain. Desktop/browser/session file grants are revoked. Nothing restarts automatically.
- **Continue** is an explicit owner action after a stopped workflow. Re-authorize desktop scopes if Stop revoked them. It never replays a previously uncertain side effect.
- **Ctrl+Alt+F12** is an independent global emergency stop. If it cannot register, desktop input stays unavailable until the conflict is resolved.

An owner may still use the programmatic takeover helper for an explicit interruption; the main interface avoids overlapping Pause/Take Over buttons. Routine manual authentication now uses the actionable in-chat request instead.

Security revocation, monitor-layout changes, Windows lock/secure desktop, sleep and genuine technical failure retain their safety boundaries. Sleep/lock does not silently restore authority. Theme/font/notification changes do not halt work; changed security policies invalidate stale queued requests without treating ordinary interaction as Stop.

## Attachments and approved files

Use the file picker or drag/drop, up to **10 files per message**, **25 MB each**. Remove pending attachments before sending; double-click to preview. Sent attachments remain accessible through their chat links. Inputs include PNG/JPEG/WebP/GIF/BMP images, UTF-8 text/code/CSV, text PDFs, DOCX, XLSX/XLSM, and ZIP inventory. Office macros and ZIP contents are never executed. ZIPs are not extracted. Expanded archive size/member limits apply. Legacy DOC/XLS, scanned PDFs requiring OCR, and arbitrary binary formats are identified as unsupported instead of being invented into text. Unsupported files can still be retained for an explicitly approved upload.

Choose **Permissions** on the main toolbar for file rules. Each rule independently sets **allow / ask / deny** for read, overwrite, create, and delete. Add an individual file, a folder (its direct children only), or a project/folder including descendants. Broad locations require a separate risk acknowledgment. Unlisted ordinary paths default to Ask. Explicit matching Deny always wins, including over narrower/session rules. Protected system/security locations, credential stores, linked paths, private runtime, assistant source and original Relay remain denied.

When a tool reaches Ask, the chat shows the exact target, reason, duration, recovery note, and a diff for text replacement. Choose **Allow Once**, **Allow for This Session**, or **Deny**. Session permission is for that exact action and target, not its parent directory or other actions. Requests expire after five minutes and are invalidated by Stop/revocation. Model prose never grants permission. Deletion additionally requires clicking a separate confirmation. Preferred rules persist; session grants disappear on Stop/close.

Tools implement real read, write, create, directory listing and deletion. Direct file operations are limited to 500 KB. Binary reads return metadata and a hash for recoverable deletion; binary contents use attachments. Text replacement is UTF-8 only; folders can be created and deleted only when empty. Nonempty recursive deletion is deliberately refused: inspect and handle individual files or use Windows manually. Existing-file writes/deletes require a current hash. Windows handles lock ancestors against renames and the target against conflicting writes/deletes, reject reparses/hardlinks, and verify identity/content after approval. Recovery originals use uniquely named private backups. Deletion is not a promise of Windows Recycle Bin recovery; the backup location is reported. No destructive action is automatically retried after an uncertain result. Binary file editing/copy/move is not exposed by the text tool; attachments/browser uploads retain their existing capabilities.

Existing local SQLite state is backed up consistently into `state-backups` before the first upgrade open. Conversations, attachments and original Codex thread IDs are retained. Older saved tool definitions use compatibility aliases through the same current policy; no replacement conversation is needed.

## Privacy and storage

Windows state: `%LOCALAPPDATA%\CodexDesktopAssistant` — conversations/messages/checkpoints in SQLite, private attachment copies, browser profile/downloads, sanitized diagnostics and backups. The Linux runtime lives in `~/.local/share/codex-desktop-assistant/`. The official Codex runtime manages its own private authentication files; the application's ordinary settings contain no passwords/tokens.

Screenshots are held in memory by this application and are not written during ordinary use. Explicit synthetic test runs save their own harmless evidence separately. **Codex may retain image inputs in its conversation rollout, and account/provider retention is outside this application's control. Zero runtime/provider screenshot retention is not promised.** Revoke desktop access during private steps.

Local chat/attachment retention can be manual, 7/30/90/365 days. Expired local histories and their attachment copies are pruned at the next startup. Deleting local history does not claim to erase provider-managed conversation records. Local history, attachments and file backups are not application-encrypted; protect your Windows user profile. Action logs record capability names/status, not screenshot bytes, typed text, cookies or passwords.

## Cedargrid Digital

Use **Workflows → Prepare Cedargrid draft**. Review the existing cleaning-calculator draft and choose local assets to attach. The plan is placed in the composer for review. This does not open an account, change PayPal details, or publish anything.

The workflow instructs Codex to inspect the actual approved Payhip interface, preserve the existing hidden listing, verify saved state, keep everything unpublished, and hand verification/payment steps to you. It uses the browser capability rather than assuming an official Payhip listing API. An actual account session still requires your express authorization and local website/window grants.

## Diagnostics and tests

Errors appear in the chat/status area and sanitized local settings/diagnostics. Startup errors also produce a visible Windows message and `startup-error.json`. WSL startup resource failures are retried at most three times **before any AI turn**. Authentication, protocol, inference, action or ambiguous-submission failures are not automatically replayed. A shared WSL service recovery helper exists under `tools/`, but is never called automatically and requires explicit owner approval.

From the repository root, offline regressions:

```powershell
apps\codex_desktop_assistant\.venv\Scripts\python.exe -m unittest discover -s apps/codex_desktop_assistant/tests
python -m unittest discover -s portfolio_autopilot/codex_relay/tests
```

Opt-in real tests use only synthetic fixtures and your existing ChatGPT plan:

```powershell
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/routine_editing_acceptance.py --approve-synthetic-tests
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/continuous_acceptance.py --approve-synthetic-tests
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/overhaul_acceptance.py --approve-synthetic-tests
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/live_acceptance.py --approve-synthetic-tests
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/controllers_acceptance.py --approve-synthetic-tests
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/ui_acceptance.py
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/launcher_acceptance.py
```

Close any owner assistant instance before isolated launcher/hotkey tests. These are verification commands, not required for normal startup.

## Source map

`assistant/ui.py` owns the redesigned native widgets, inline approvals and main selectors; `ui_base.py` retains the tested history/attachment/lifecycle helpers; `attention.py` owns notifications and the action-level input coordinator; `file_policy.py` and `files.py` own scoped rules and safe file operations; `applications.py` discovers bounded installed launch targets; `engine.py` owns background coordination, streaming, bounded host workers and a dedicated COM desktop worker; Playwright stays on its owning engine thread; `integration.py` owns the separate official runtime; `permissions.py`/`tools.py` own capability enforcement; `action_policy.py` classifies actual activations separately from text editing; `desktop.py` and `browser.py` own the two controllers; `attachments.py` owns bounded extraction; `storage.py` owns durable state; `workflows.py` prepares the Cedargrid plan. `tests/` contains offline and real acceptance fixtures. Voice can later submit through the same coordinator/event interface without bypassing permissions.

Protocol implementation was checked against the installed generated schemas and [official app-server documentation](https://learn.chatgpt.com/docs/app-server). Browser interception follows the [Playwright API](https://playwright.dev/python/docs/api/class-browsercontext); Qt renders the local interface without public hosting. Dynamic-tool APIs are experimental: incompatible runtime/schema changes fail closed. Dependencies are pinned in `requirements.lock.txt`.
