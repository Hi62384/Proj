# Portfolio Manager workflow

## Selection-aware Copy Prompt — four phases

**When a niche or its `projects/` folder is selected:** Copy Prompt offers only **Research a Business Opportunity**, **Create a Project from My Idea**, and **Recheck or Replace**. These are Phase 1 ChatGPT research prompts; their outputs must still pass evidence and repository import checks before becoming an active project. Current budget settings are planning ceilings only and authorize no spend.

**When an active project is selected**, Copy Prompt changes to the phase-specific task:

1. **Phase 2 — Build, Test & Prepare:** only the Phase 2 Codex `/goal`. Work and artifacts stay in that project's `work/`, and every checkpoint records a best-guess Phase 2 completion percentage, the true next action, and important real URLs with precise statuses. Once actual selected platform packages and tests are verified, Codex advances the project to `working_phase_3` using the lifecycle CLI.
2. **Phase 3a — Research Platforms & Plan:** a ChatGPT research prompt with the **complete current project.md** appended, along with exact original SHA-256 and path. ChatGPT evaluates actual finished assets, suitable sale/access platforms, Canadian payout eligibility, rights, costs, formats, release instructions and marketing channels, then returns one **additive** Markdown update. Drag that file onto the **selected same project** in Portfolio Manager; it remains in Phase 3.
3. **Phase 3b — Validate & Improve Plan:** enabled only after the Phase 3a plan was imported. Copy this ChatGPT prompt to independently challenge and improve all platforms/marketing options. It includes the latest complete project file and an updated SHA-256. ChatGPT returns one **additive** Markdown update with an explicit APPROVED or NEEDS_REVISION verdict. An approved, structurally valid imported file automatically moves the selected project to `working_phase_4`; NEEDS_REVISION remains Phase 3 so the validation prompt can be repeated. No amount of repeated research guarantees market sales.
4. **Phase 4 — Execute Launch & Marketing:** only the Phase 4 Codex `/goal`. Codex actually performs all permitted suitable releases and promotion, records live links/evidence and the best-guess Phase 4 completion percentage at **every checkpoint**, and updates the source project's Important URLs table (sale/download, submission, edit/admin, promotion, analytics, demos, documentation). Only real verified public product delivery plus public marketing can advance Phase 4 to **Complete**; completion doesn't imply paid sales.

### Drag-and-drop UPDATE, never rewrite

While the exact Phase 3 project leaf is selected, drop one external `.md` file onto Portfolio Manager to replace that project's canonical record with an additive ChatGPT update. The importer verifies the project/niche identity, complete verbatim original Markdown body, unchanged protected JSON metadata (including actual financial/work facts), a matching source SHA-256, the current phase, valid research/validation status, and linked sources before updating. New material must be APPENDED, not overwrite existing project details. The importer preserves `work/` and writes the prior version under `business_portfolio/.local/phase3_backups/<id>/`. Unsafe, stale or truncated files are rejected. Approved Phase 3b imports automatically advance Phase 4; draft/needs-revision imports do not. These local updates do not automatically commit or push to GitHub.

Dropping a new project Markdown onto a niche folder still creates a NEW validated `project.md` plus `work/`; it does not replace other projects. Select the intended project file before attempting replacement, rather than dropping onto an unrelated project.

### Resume after stop

The main Portfolio Manager window shows **Resume after stop** in its header, using the same Computer Bridge stop-resume logic as the existing settings option. It resets the stopped state; it does not restore deleted permissions, authorize transactions, or start workers.

### Evidence and safety

External publication, outreach, account changes and spending require actual authorization; the nominal CAD100 planning cap is not a grant. Record actual URLs with observed state, never invent live pages or store passwords/tokens in the public project file. Coordinate one writer per record, preserve original project decisions/results and source chronology, update `main` without per-project branches or force pushes, and do not report an unrun QA step as successful.

Phase 4 verified completion creates the durable `business_portfolio/completed_projects/<PROJECT-ID>.json` receipt with factual sale/access and marketing links, independent of the original work folder. User-initiated demotion may revoke an existing completion receipt; Phase 4 promotion is not a manual shortcut.

### Project files and folder view

Every active project is a folder named after its stable project ID and short slug:

    business_portfolio/niches/<niche>/projects/<id>-<slug>/project.md
    business_portfolio/niches/<niche>/projects/<id>-<slug>/work/

All project-specific code, build files, assets, tests, drafts and release packages belong in work/. In the Projects tree, Portfolio Manager hides the enclosing project folder and shows the project.md record as the selectable leaf. Dragging a valid .md project file onto a niche creates this folder layout with work/.gitkeep automatically. Existing older flat records are readable for compatibility during migration.

The phase icon is 2 (Working Phase 2), 3 (Research & Validation), 4 (Launch & Marketing), or a checkmark (Complete). Phases are independent of project work_state and commercial_validation; completion does not imply commercial success. The phase selector lets the owner move between Phase 2 and Phase 3 or demote Phase 4/Complete; advancement to Phase 4 requires an imported approved Phase 3b update. Demoting Complete revokes the corresponding Completed Projects receipt. The Complete choice is disabled for manual updates: Codex must automatically verify the live product and marketing URLs, save the factual description, run the completion command and create the durable receipt without asking the owner to enter links or click Complete.

To advance a project, run:

    python -m portfolio_manager.project_lifecycle set-phase --project "business_portfolio/niches/.../projects/<slug>/project.md" --phase working_phase_3

After a verified Phase 4 public product and at least one verified public marketing placement exist, Phase 4 Codex can run:

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
