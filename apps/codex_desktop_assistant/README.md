# Codex Desktop Assistant

A native Windows chat application with persistent Codex conversations, approved screen observation, Windows accessibility control, and a dedicated automation browser. It uses your existing ChatGPT login, without GitHub Issues or a separately billed API key.

**Real integration acceptance passed on October 27, 2026.** See [INTEGRATION_REPORT.md](INTEGRATION_REPORT.md) for measured results, recovery work, and limitations. Tests used disposable Windows and localhost browser fixtures; no storefront, payment account, purchase, publication, or commercial message was touched.

## Open the application

Double-click **Start_Desktop_Assistant.cmd** in this folder. It opens the native application and starts its internal components. You do not need another terminal, server, GitHub Issue, or the normal Codex desktop window.

The managed `.venv` is already installed on this computer. On a fresh checkout the launcher invokes **Setup_Desktop_Assistant.cmd** to install the pinned free dependencies and Playwright Chromium. Python 3.11+ and the existing verified Ubuntu WSL2/Codex installation are required. Installation needs Internet access. A managed Python launcher is supplied rather than a bundled standalone EXE.

On first connection the application copies the official Linux Codex executable, its required `codex-code-mode-host` companion, and the existing supported ChatGPT login into its own private Linux home. Its subsequent runtime configuration and authentication are independent of the Relay. It does not import GitHub credentials, ordinary browser cookies, plugins, or API-key environment variables. Only ChatGPT authentication is accepted. Ordinary startup needs no administrator permission.

## Chat and conversations

- Use **New Chat**, type an instruction, then **Send**, **Start**, or **Ctrl+Enter**. Responses stream into the chat. Markdown, code blocks, tables, links, and attached images are displayed locally.
- Conversations have independent saved Codex thread IDs. Search, rename, pin, archive/restore, or delete local history from the sidebar. Switching views leaves an active task associated with its original conversation; the toolbar identifies work in another conversation.
- A correction sent during work is durably saved and delivered using the installed protocol's `turn/steer`. If delivery is ambiguous it remains explicitly marked for review, with no automatic replay.
- Pause retains queued messages. **Resume**, or an explicit **Continue** message, includes held owner instructions and continues the same saved conversation. Continue cannot restore grants revoked by Stop or an application restart. After a crash, unfinished messages/tasks require review rather than restarting computer actions.
- The model picker comes from the actual account's `model/list`. Reasoning efforts are shown only when supported by the selected model. Changes apply to subsequent turns.

## Enable computer access

Computer permissions start disabled and are not silently restored after a restart.

1. Open **Settings → Desktop**. Select the exact windows you authorize, enable observation/input as needed, and save. Transient dialogs owned by the same approved window/process are supported; another document window does not automatically gain access.
2. Optionally approve one monitor or all monitors for observation. Input still requires an approved window. Sensitive/excluded windows are masked in monitor captures. A changed monitor layout requires a fresh review.
3. The persistent observation indicator remains visible even if **View → Computer activity** is hidden. **Preview approved screen** shows a local-only preview; it does not send that preview to Codex.
4. Codex requests screenshots on demand. Tool responses carry actual images, not merely file paths. Pixel input requires a fresh capture token and window inspection; the controller maps resized image pixels to physical window coordinates and rejects moved/resized/DPI-changed captures.
5. Prefer accessible controls. The controller supports text, buttons, checkboxes, dropdowns, focus, window movement, bounded shortcuts, mouse movement, scrolling and dragging. Coordinate clicks/drags always require individual review. No model-authored shell command or arbitrary JavaScript evaluator is exposed.

You can approve exact harmless **routine control labels** under **Privacy and files** to avoid repeated confirmations within a bounded task. Consequential labels, Enter submission, multiline input, unknown actions and pixel clicks retain their local review boundaries. The owner service derives labels from actual controls; webpages cannot grant permissions. Routine-label grants should be narrowly chosen.

The controller refuses authentication/password controls, terminal/security windows, the assistant's own permission UI, and private clipboard paste. Use **Take Over** for those steps. App-specific automation for Excel, Godot, Blender and other applications uses this common accessibility/visual layer; specialist APIs for every application are not included or claimed tested.

## Browser modes

**Dedicated browser:** approve exact HTTP(S) origins in **Settings → Browser** and enable it. Codex opens a separate persistent Chromium profile. Your normal browser stays separate. Additional login/CDN origins must be reviewed explicitly. No ordinary-browser password/cookie import occurs.

**Your existing browser:** select its exact Windows window under Desktop permissions. Codex operates it through the native controller; it does not attach to a debugging port or extract its session. This mode has the same window and human-review boundaries as other Windows applications.

The dedicated browser supports navigation, semantic fields/buttons/dropdowns/checkboxes, tabs, dynamic content, screenshots, approved attachment uploads, and private downloads. Redirect destinations are checked at every hop; approved document redirects are followed as fresh GET navigations without replaying a submission. Unsupported mutation-preserving/subresource redirects stop for review. WebSockets and automatic dialogs are blocked, so some sites may need a specialist adapter or manual handling. This is not a claim of universal compatibility with every website.

Uploads accept only attached files approved for that conversation; the UI reviews the destination/action. Downloads receive generated private filenames and are never automatically executed. Network mutations outside the brief approved action are blocked. During an explicit takeover, manual browsing is enabled only after the model action has stopped, within the approved origins. Password entry, MFA, CAPTCHA, identity checks, purchases, publication and account-security decisions belong to the owner.

## Pause, takeover and emergency stop

- **Pause:** prevents new computer input and interrupts the active Codex turn. Held corrections remain available.
- **Take Over:** stops automation and hands the approved interface back to you. Finish the manual step, then Resume. Codex must inspect the current state before continuing.
- **Stop:** interrupts and revokes all window/browser/file/application grants. Re-authorize before another computer task.
- **Ctrl+Alt+F12:** global emergency stop, handled by a dedicated Windows message thread independently of the AI process. If the shortcut cannot register, desktop input remains unavailable until the conflict is resolved.

An already dispatched UI operation cannot be undone. No new action starts after revocation; a held mouse button is released as cleanup. Pending approvals are invalidated when permissions change. Late tool calls from an old turn are rejected.

An independent session guard pauses input on a secure/locked desktop or a detected sleep gap. Unlock/wake does not restore control; review the current interface and explicitly Resume. Actual Windows sleep/lock was not forced during tests; detection/state transitions were tested with injected clock/desktop state and the active desktop check was verified live.

## Attachments and approved files

Use the file picker or drag/drop, up to **10 files per message**, **25 MB each**. Remove pending attachments before sending; double-click to preview. Sent attachments remain accessible through their chat links. Inputs include PNG/JPEG/WebP/GIF/BMP images, UTF-8 text/code/CSV, text PDFs, DOCX, XLSX/XLSM, and ZIP inventory. Office macros and ZIP contents are never executed. ZIPs are not extracted. Expanded archive size/member limits apply. Legacy DOC/XLS, scanned PDFs requiring OCR, and arbitrary binary formats are identified as unsupported instead of being invented into text. Unsupported files can still be retained for an explicitly approved upload.

For direct file work, approve exact paths under **Privacy and files**. Overwrites require the previous content hash and keep a private backup. Links/junctions, credential files, the assistant's own code/runtime and the original Relay are protected. No unrestricted filesystem or command capability is provided.

## Privacy and storage

Windows state: `%LOCALAPPDATA%\CodexDesktopAssistant` — conversations/messages/checkpoints in SQLite, private attachment copies, browser profile/downloads, sanitized diagnostics and backups. The Linux runtime lives in `~/.local/share/codex-desktop-assistant/`. The official Codex runtime manages its own private authentication files; the application's ordinary settings contain no passwords/tokens.

Screenshots are held in memory by this application and are not written during ordinary use. Explicit synthetic test runs save their own harmless evidence separately. **Codex may retain image inputs in its conversation rollout, and account/provider retention is outside this application's control. Zero runtime/provider screenshot retention is not promised.** Disable observation during private steps.

Local chat/attachment retention can be manual, 7/30/90/365 days. Expired local histories and their attachment copies are pruned at the next startup. Deleting local history does not claim to erase provider-managed conversation records. Local history, attachments and file backups are not application-encrypted; protect your Windows user profile. Action logs record capability names/status, not screenshot bytes, typed text, cookies or passwords.

## Cedargrid Digital

Use **Workflows → Prepare Cedargrid hidden-listing workflow**. Review the existing cleaning-calculator draft and choose local assets to attach. The plan is placed in the composer for review. This does not open an account, change PayPal details, or publish anything.

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
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/live_acceptance.py --approve-synthetic-tests
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/controllers_acceptance.py --approve-synthetic-tests
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/ui_acceptance.py
apps\codex_desktop_assistant\.venv\Scripts\python.exe apps/codex_desktop_assistant/tests/launcher_acceptance.py
```

Close any owner assistant instance before isolated launcher/hotkey tests. These are verification commands, not required for normal startup.

## Source map

`assistant/ui.py` owns native widgets; `engine.py` owns background coordination and streaming; `integration.py` owns the separate official runtime; `permissions.py`/`tools.py` own capability enforcement; `desktop.py` and `browser.py` own the two controllers; `attachments.py` owns bounded extraction; `storage.py` owns durable state; `workflows.py` prepares the Cedargrid plan. `tests/` contains offline and real acceptance fixtures. Voice can later submit through the same coordinator/event interface without bypassing permissions.

Protocol implementation was checked against the installed generated schemas and [official app-server documentation](https://learn.chatgpt.com/docs/app-server). Browser interception follows the [Playwright API](https://playwright.dev/python/docs/api/class-browsercontext); Qt renders the local interface without public hosting. Dynamic-tool APIs are experimental: incompatible runtime/schema changes fail closed. Dependencies are pinned in `requirements.lock.txt`.
