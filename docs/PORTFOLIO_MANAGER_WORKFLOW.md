# Portfolio Manager workflow

## Copy a business megaprompt

Use the **Budget ceiling (CAD)** field and **Copy Megaprompt** menu in the right pane. The budget is saved for future sessions and does not authorize spending.

- **Research a Business Opportunity:** Select an active niche folder, copy the prompt, and paste it into ChatGPT to research an opportunity in that niche.
- **Develop My Business Idea:** Copy the prompt from any selection, paste it into ChatGPT, and replace the example in the `PROJECT_IDEA` block with your idea.

Both prompts request one comprehensive Markdown project file that can be imported into the Business Portfolio after its metadata and sources are validated.

## Current business view (2026-11-15)

Projects and Niches show five primary categories, the 25 required niches, and nine preserved legacy niches nested under their closest equivalents. Digital Products → Game Development Marketplaces contains GDM-001, GDM-002 and GDM-003. Each category and niche has an independent Working checkbox stored in `NICHE.json`; it is an informational focus setting and never starts a worker or changes project status. Changes are atomic, persist across restarts, synchronize across windows, and appear in the generated browser. Category totals count working descendant leaf niches without double-counting parent and nested nodes. History & Existing Work retains the 139 older records and prior niche-layout snapshot. Repository files remains the optional full explorer; the independent 36-category opportunity taxonomy stays in `opportunity_library`.

The material below describes the prior active view and remains for migration history. Current verification is in `docs/BUSINESS_NICHES_13_REPORT_2026-11-15.md`.

## Current navigation (2026-11-15)

Use **Projects** for the three current GDM families, **Niches** for the mostly empty taxonomy, and **History & Existing Work** for preserved prior project records. **Repository files** is the optional full file explorer for an arbitrary file or folder. Its folders load in the background when expanded, so the default project view stays small. The web project browser offers the same three primary views and separate Overview, Files & Results, Tasks & Progress and Complete record panels. History is read-only in the browser; changes to an archived plan require a reviewed restoration into an active niche. Each Codex chat retains its own selection, while AI Only/Human Available and Computer Access remain shared as before.

The test results later in this document refer to the earlier version. Consult the current completion report for this overhaul's checks; historical test counts are not a claim that the new views passed every live UI action.

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
