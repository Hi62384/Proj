# Codex Computer Bridge

Give tasks in official Codex. The local Windows dashboard shows activity, projects,
results and genuine human requests. It does not select a model, start a Codex
app-server or maintain a second AI conversation.

## Start using it

1. Run `Setup_Computer_Bridge.cmd` once. It backs up existing state/configuration
   and registers only `codex_computer_bridge` in the current user's Codex config.
2. Open a fresh official Codex session so it discovers the registered tools.
3. Ask: **Check my computer bridge status.**
4. Chrome uses the existing teal extension and existing sign-in. Its optional
   **Full Browser Access** is a separate, explicit Chrome permission. This computer
   already received that permission; reinstalling the extension is unnecessary.
5. Open the tray icon or `Start_Computer_Bridge.cmd` to view work. Desktop control
   starts OFF. Enable a selected window/monitor in Settings only when needed.

Codex may require its own MCP tool trust decision. Local permission checks still
apply after that decision. Setup does not automatically trust all bridge tools.
The optional `--trust-local-tools` installer flag must only be used after the
owner explicitly approves that powerful integration permission.

## Ordinary use

- Ask Codex to open, inspect, edit and close its background Chrome task tabs.
  An exact requested URL reuses an existing tab without reloading or changing
  focus. A new tab is created only when no match exists. Reused tabs retain
  unsaved work and are not automatically closed as temporary cleanup.
- Ask it to create a persistent project and generate/validate/package products.
- View Projects shows counts, blockers and deliverables. Closing the dashboard
  leaves its tray/controller available; it does not create hidden AI inference.
- Resolve an actual request in the dashboard. **View exact scope** shows why an
  action needs approval, its target and any file/launch manifest.
- **Stop**, **Emergency Stop**, or **Ctrl+Alt+F12** prevents new input and revokes
  launch scopes. Resume must be performed locally in Settings. A restart does
  not silently clear a latched Stop or restore desktop authority.
- **Quit Bridge** stops work and exits. A later Codex connection may start the
  controller again, but a latched Stop remains in effect.

The official agent must inspect and verify outcomes. A dispatched click, accepted
tool call or completed chat turn is not proof of a saved/uploaded/published result.

## Projects, products and reasoning

MCP exposes the existing deterministic generator, native QA, rendered previews,
integrity-checked packaging and dependency queue through `projects_*` tools.
`bridge_get_artifact` returns the path/hash of an owned generated delivery handle.
Ordinary filesystem tools retain independent Read/Write/Create/Delete rules;
explicit Deny is enforced and protected credentials remain unavailable.

`bridge_reason_tasks` returns reasoning jobs for official Codex.
`bridge_reason_result` records its bounded findings. These results cannot certify
native QA or external publication. If official Codex stops reasoning, the dashboard
reports **Waiting for Codex**. Safe deterministic workers can continue while its
UI is minimized, provided Windows and the controller remain running.

The local synthetic business/builder test tools create disposable loopback-only
fixtures. Their fixed no-spending approvals cannot authorize Payhip or any other
real account. Public publication and purchases are never implied by browser access.

## Recovery and preservation

The private data location remains `%LOCALAPPDATA%\CodexDesktopAssistant`.
SQLite backups before migration are in `state-backups\before-computer-bridge`.
Codex configuration backups are beside its `config.toml`. Existing conversation
records, project database, generated products, Chrome extension identity, browser
sign-ins, native-host registration and Codex Relay are preserved. Settings provides
a read-only conversation archive. The former UI guide is retained as
`LEGACY_DESKTOP_ASSISTANT.md`; its old startup instructions are historical.

Interrupted external effects stay in review and are not automatically replayed.
After a channel failure, inspect actual state before retrying an uncertain action.
After a controller crash, the next tool's preflight can start/reuse the fixed
Windows controller; it does not retry that tool's previous mutation.

For Chrome disconnection, open its existing extension popup and Connect. Login,
MFA, CAPTCHA and identity verification remain manual. Optional debugger/trusted
input is separately consented and is not enabled merely by MCP or Full Browser.

## Advanced development

Architecture: official Codex MCP client → official Python MCP SDK stdio adapter →
authenticated user-only Windows pipe → singleton Qt controller → existing Broker →
Chrome native host/extension, Windows UIA, file policy and product/project tools.
There is no public MCP HTTP endpoint, model-selected executable, general shell or
arbitrary JavaScript tool. The stdio adapter starts only the fixed local `run.py`
entrypoint. The current Windows official Codex binary is used for registration;
WSL desktop access is not assumed and the legacy WSL model runtime is not started.

Per-client cancellation closes queued/input/approval authority. Deterministic
project workers are independent of one MCP request. Authentication failures do
not kill the pipe listener. Diagnostic clients do not count as initialized MCP
clients; connected status follows MCP discovery/heartbeat and expires on loss.

Run `tools/setup_computer_bridge.py health` for configuration/controller diagnostics.
Those diagnostics are not proof of an official-client tool call. Never share
`computer-bridge.json`, `chrome-bridge.json`, credentials or browser profile files.

Uninstall with `tools/setup_computer_bridge.py uninstall`, then Quit Bridge from
the tray. This removes only its MCP registration and preserves data and other
servers. Native-host/extension removal remains separately available through the
existing Chrome setup tool. Do not restore an entire old Codex config over later
unrelated changes; restore only the named bridge section if recovering manually.

See `COMPUTER_BRIDGE_REPORT.md` for executed tests and outstanding acceptance.
