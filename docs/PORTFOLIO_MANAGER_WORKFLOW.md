# Portfolio Manager workflow

## One Copy Prompt menu / Three project phases

The main workspace has ONE **Copy Prompt** button. It offers:

1. **Phase 1 → Research a Business Opportunity:** Select an active niche, copy, then paste into Codex. Research demand and competition, and save a validated business project record at business_portfolio/niches/<niche>/projects/<project-id>-<slug>/project.md plus a sibling work/ folder.
2. **Phase 1 → Create a Project from My Idea:** Paste the copied prompt, replace its PROJECT_IDEA example, validate the resulting project record and create its work/ folder. Do not consider Phase 1 complete without an actual project.md.
3. **Phase 2 → Build, Test & Prepare:** Copy and paste into the selected project's Codex chat. Starts with /goal; develops, tests and polishes the real product in work/, prepares packages for every genuinely suitable platform, and when verified moves the record to working_phase_3.
4. **Phase 3 → Launch & Market:** Paste into Codex to prepare/publish on relevant, permitted marketplaces and market across suitable channels. Document real sale/distribution and marketing URLs. Complete only when live distribution and marketing are verified.

The planning budget (CAD) applies to Phase 1 inputs and never authorizes spending. No project-specific GitHub branches: synchronize against latest upstream and push verified commits directly to main without force-pushing.

### Project files and folder view

Every active project is a folder named after its stable project ID and short slug:

    business_portfolio/niches/<niche>/projects/<id>-<slug>/project.md
    business_portfolio/niches/<niche>/projects/<id>-<slug>/work/

All project-specific code, build files, assets, tests, drafts and release packages belong in work/. In the Projects tree, Portfolio Manager hides the enclosing project folder and shows the project.md record as the selectable leaf. Dragging a valid .md project file onto a niche creates this folder layout with work/.gitkeep automatically. Existing older flat records are readable for compatibility during migration.

The phase icon is 2 (Working Phase 2), 3 (Working Phase 3), or a checkmark (Complete). Phases are independent of project work_state and commercial_validation; completion does not imply commercial success. The phase selector lets the owner move between Phase 2 and Phase 3 in either direction, or demote a completed project directly to either earlier phase. Demoting Complete revokes the corresponding Completed Projects receipt. The Complete choice is disabled for manual updates: Codex must automatically verify the live product and marketing URLs, save the factual description, run the completion command and create the durable receipt without asking the owner to enter links or click Complete.

To advance a project, run:

    python -m portfolio_manager.project_lifecycle set-phase --project "business_portfolio/niches/.../projects/<slug>/project.md" --phase working_phase_3

After a verified public product and at least one verified public marketing placement exist, Phase 3 can run:

    python -m portfolio_manager.project_lifecycle set-phase --project "business_portfolio/niches/.../projects/<slug>/project.md" --phase complete --description "Short accurate summary" --sale-url "https://real-product-link" --marketing-url "https://real-marketing-link"

For supported noncommercial releases, a verified public access link may be recorded with --other-url instead of --sale-url. Never invent launch evidence or URLs.

### Independent Completed Projects

Each completed project has a durable standalone public receipt under business_portfolio/completed_projects/<PROJECT-ID>.json containing the project's description, verified sale/access links, verified marketing links, and other important URLs. The Completed Projects view displays them as clickable links, even after the original project folder has been deleted. There is no delete function in Portfolio Manager; to delete or correct a receipt, edit the JSON on disk. Do not put sensitive information there.

Rebuild the generated project browser/index and run the offline tests after modifying canonical records. The GitHub Actions portfolio regression workflow also rebuilds them from the canonical filesystem after validating tests.

## Current business view (2026-11-15)

Projects and Niches show five primary categories, the 25 required niches, and nine preserved legacy niches nested under their closest equivalents. Digital Products → Game Development Marketplaces contains only GDM-002 as an active project; GDM-001 and GDM-003 and their project-specific results were deleted from active folders. Books & eBooks also contains BOOK-001. Each category and niche has a Working checkbox stored in `NICHE.json`; enabling a niche also enables its parents, and a parent cannot be disabled while a descendant is Working. Working folders carry a green icon badge, leaving text colors available for the empty-folder indicator. This focus setting never starts a worker or changes project status. Changes are atomic, persist across restarts, synchronize across windows, and appear in the generated browser. Category totals count working descendant leaf niches without double-counting parent and nested nodes. History & Existing Work retains the 139 older records and prior niche-layout snapshot. Repository files remains the optional full explorer; the independent 36-category opportunity taxonomy stays in `opportunity_library`.

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
