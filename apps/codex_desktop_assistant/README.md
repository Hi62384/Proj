# Codex Computer Bridge

The local Windows computer-control bridge for **official Codex**. Give instructions
in official Codex; this application shows status, projects, deliverables and human
requests. It no longer starts a second AI chat or model service.

Run **Setup_Computer_Bridge.cmd** once, then open a fresh official Codex session and
ask: **Check my computer bridge status.** Its registered local MCP entrypoint starts
or reuses the controller automatically. Codex may require a one-time integration
trust decision. Local desktop, file and sensitive-action permissions still apply.

Open **Start_Computer_Bridge.cmd** or its tray icon to view the dashboard. Desktop
access starts off. Chrome reuses the existing installed extension and sign-in.
Stop/Emergency Stop revokes execution; resume is a local Settings action.

Migration and real official-client acceptance are still in progress. Tool discovery
has passed, but successful official-client calls are waiting on its tool-approval
boundary. Do not treat server startup or old custom-chat tests as proof of the new
workflow.

- [Setup, use, recovery and uninstall](COMPUTER_BRIDGE.md)
- [Actual verification and remaining work](COMPUTER_BRIDGE_REPORT.md)
- [Historical Desktop Assistant guide](LEGACY_DESKTOP_ASSISTANT.md)
- [Historical business operator evidence](BUSINESS_OPERATOR_REPORT.md)

Existing conversations, products, project checkpoints, authentication and Codex
Relay data are preserved. No public network MCP endpoint is exposed.
