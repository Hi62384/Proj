# Portfolio Manager workflow

Portfolio Manager is a visual file explorer for normal official Codex chats. It remembers one selected repository file or folder per chat and one shared availability setting. The chat does the work with its usual tools and permissions. Selecting an item does not start an AI worker.

## Open and use

In a Codex chat attached to this repository, say “Open Portfolio Manager” or “Open the project.” The chat uses `portfolio_open` through the existing Computer Bridge integration. The controller starts if necessary and opens or focuses that chat's window. Pick a file or folder in the repository tree, then return to the same chat and ask it to explain or work on the selection. The chat calls `portfolio_context` to retrieve the path and global mode. It may call `portfolio_select` when you explicitly name a different path. Ordinary coding requests that do not refer to Portfolio Manager follow the normal Codex workflow.

Each chat has its own window and selection. Closing a window leaves its selection saved. Reopening it in the same chat restores that selection. A SessionStart hook reserves a stable private reconnect key for a normal Codex chat. The key is passed automatically through trusted session context and never needs to be entered by the owner. `Setup_Portfolio_Session.cmd` installs the hook for this checkout if it is missing; Codex may require a one-time trust review. Without a stable hook identity, a new MCP connection cannot be proven to belong to an earlier chat, so it receives a separate workspace.

## Availability and computer access

The window header offers **AI Only (AFK)** and **Human Available**. This single setting lives in the controller's SQLite database, updates all open windows and survives restarts. It tells the chat whether you are available for questions. It does not change Codex execution or grant permissions. In AI Only, the chat should continue authorized work and defer actions needing you.

The header's More menu opens Computer Access and keeps Emergency Stop reachable. The existing Bridge continues to enforce browser, desktop, file and action permissions. Stop and Emergency Stop retain their original effects. Legacy background-worker code and saved data are preserved, but the normal workspace has no worker controls and does not launch a separate Codex model process.

## Working on a portfolio record

For a selected canonical business project record, the chat reads the complete record and latest authorized private checkpoint before editing. It uses the coordinator to claim canonical record changes when required by `AGENTS.md`, compares the expected content before saving, and records verified progress. This coordination is separate from opening a file or using the explorer. External uploads, orders, publication and other consequential actions retain their existing approvals.

## Verification limits

On November 12, 2026, all 138 Portfolio Manager tests passed, with four legacy WSL fixtures skipped. A disposable controller passed separate MCP chat connections, selection and availability persistence after restart, and Bridge Stop checks. Three fresh official Codex chats then opened distinct live windows; a chat prompted only with “Open the project” opened its window automatically. Two chats selected different paths, ran separate ordinary coding tasks at the same time, and passed four independent fixture tests without starting workers. Closing and reopening one chat window restored its selection, while the other window stayed open. A temporary global Human Available change reached both live windows; AI Only was restored and verified. The temporary source folders were removed. The live shared controller was restarted once for this acceptance run. After the owner resumed its Stop control, a live read-only Chrome tab discovery succeeded through Computer Bridge with no pending requests. Desktop access was off, so a live desktop action was not tested. Live screenshot inspection and direct mouse interaction with the window remain unverified because window capture timed out. These results do not prove every future Codex chat or external computer action will work.
