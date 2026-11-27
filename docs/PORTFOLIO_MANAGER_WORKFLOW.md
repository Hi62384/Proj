# Portfolio Manager workflow

## Create and organize projects

Select a niche or subniche in **Projects**. The niche offers **New project**, **New niche folder**, and **Delete niche**. It does not display a prompt-copy button. **New project** creates and selects an **Empty project** in Phase 1, with a unique stable ID and a `work/` directory. Project creation and portfolio browser regeneration run off the GUI thread, so the button briefly disables while the rest of the window remains responsive. If the user navigates away, creation does not steal their selection. **New niche folder** asks for a name and creates a subniche under the selected niche. New niche focus defaults to Not Working.

Project entries appear directly under their niche; there is no intermediate `projects` node. The canonical disk layout is:

```text
business_portfolio/niches/<niche>/NICHE.json
business_portfolio/niches/<niche>/<stable-id>-<slug>/project.md
business_portfolio/niches/<niche>/<stable-id>-<slug>/work/
business_portfolio/niches/<niche>/<subniche>/NICHE.json
```

The project folder keeps its record and implementation together. Portfolio Manager presents the record as a leaf directly under the niche and hides that implementation wrapper in the Projects view. All project-owned source, content, assets, builds, tests, release packages and marketing material belong in `work/`. A descriptive project title can change without changing its stable ID or folder path.

**Delete niche** applies equally to a niche or subniche. Its confirmation identifies the subtree and included projects. Confirming moves that whole subtree to ignored `business_portfolio/.local/deleted_niches/` recovery storage, then removes it from the active view. It does not erase historical archives or independent completed-project receipts. Deletion is rejected if another active project would retain a broken parent/related-project reference. Restore recovery folders only after reviewing their original niche path, references and ID collisions; do not blindly merge over newer work.

## Manual fallback and recoverable Delete project

The selected project view includes **Delete project** next to the phase controls. Confirming removes only the selected project from its niche, moving its entire `project.md` plus `work/` to `business_portfolio/.local/deleted_projects/`. Existing completed receipts, history and other projects remain. Deletion is refused if another active project references the target or its files are unsafe. The deleted ID cannot be reused, and failed indexing restores the original directory. Deleting local records does **not** remove a published product or stop external Codex workers.

Codex normally advances execution phases, but owners may manually advance **Phase 4 → 5** or **Phase 5 → 6** if the handoff gets stuck. Manual changes require an explicit Yes confirmation, appear in `phase_history` as **MANUAL OVERRIDE — previous phase NOT VERIFIED**, and preserve all remaining tasks and recorded facts. Before releasing or marketing anything, the next Codex worker must verify any unfinished prior-stage prerequisites. No phase-skipping or false completion is permitted. **Phase 6 → Complete remains Codex-only with verified product and marketing URLs.**

## Six phases and the prompt buttons

| Phase | Purpose | Prompt button and choices | Who advances it |
| --- | --- | --- | --- |
| 1 | Research a worthwhile product or an existing idea; write a detailed build specification | **Copy research prompt**: niche research, existing idea, verification/recheck | User advances to 2 after review |
| 2 | Research release destinations and feasible direct/adjacent compatible versions; update the build specification | **Copy release research prompt**: research and verification/recheck | User advances to 3 after review |
| 3 | Research the full marketing strategy, assets, tactics, channels and measurement; reconcile earlier plans | **Copy marketing research prompt**: research and verification/recheck | User advances to 4 after review |
| 4 | Build, test, document and package every accepted product version | **Copy build prompt**: Codex `/goal` | Codex normally advances to 5; owner has an unverified manual fallback |
| 5 | Release the finished product on every accepted required destination and verify customer access | **Copy release prompt**: Codex `/goal` | Codex normally advances to 6; owner has an unverified manual fallback |
| 6 | Execute and verify the accepted finite initial marketing plan | **Copy marketing prompt**: Codex `/goal` | Codex marks Complete with factual evidence and URLs |

Set **Project day limit** beside the planning budget before copying a prompt. It defaults to 21 days, saves between sessions, and applies to the entire project across research, build, releases and initial marketing. This is one shared window, not a new limit for each phase and not an instruction to wait before completing useful work. Plans search broadly but select a feasible finite scope; other options remain conditional, deferred or rejected with reasons. Required external review/access delays must be recorded honestly rather than concealed by a completion estimate.

Phases are stored as `working_phase_1` through `working_phase_6`, then `complete`, with `workflow_version: 2`. They are independent of work status, commercial validation and the niche's Working checkbox. A completed project has not necessarily made a sale.

## Research by copying and pasting text

1. Create or select a Phase 1 project and copy the niche research or existing-idea prompt. The idea option lets you supply the idea. The copied prompt includes the full current record, niche, planning budget, canonical path and a SHA-256 snapshot marker.
2. Run it in ChatGPT. It researches the product and returns the complete revised project as one copyable block of text, including its JSON frontmatter. A download is not required.
3. Select the same project in Portfolio Manager and choose **Paste project text**. Paste the complete block and save. The project stays in the current phase. Run that phase's recheck as needed.
4. When the research is satisfactory, use the phase control to advance one step to the next research phase. Repeat the research/paste/recheck process for release platforms in Phase 2 and marketing in Phase 3. After Phase 3, manually advance to Phase 4.
5. Copy the Phase 4 build `/goal` into the project's Codex chat. Once Codex finishes and advances it to Phase 5, copy that release `/goal`; repeat for Phase 6 marketing. Each goal stops at its handoff so the next phase starts from its own prompt.

Verification is allowed to conclude **“Good to go — no substantive changes needed.”** If the plan is already good, there is no replacement text to paste. Minor cosmetic suggestions must not force changes. A meaningful defect warrants a corrected complete record and another review; a genuine blocker must not be approved simply to move on. A research verdict is not proof of future sales.

Phase 2 distinguishes compatibility targets from distribution destinations. It investigates adjacent useful versions, such as other engines for an engine-specific pathfinding product. Every accepted version must appear in the Phase 1 specification and Phase 4 build/tests, and every accepted release route in Phase 5. Phase 3 covers much more than website lists: audience intent, positioning, proof, content, SEO/discovery, permitted communities, partnerships, conversion and measurement, with concrete Phase 6 tasks.

### What a paste preserves and validates

Paste accepts a full strict JSON-frontmatter Markdown record, optionally wrapped in one Markdown code fence. It replaces the planning body; it is not restricted to appending duplicate sections. Identity, current phase, workflow, work state, permission and financial/evidence/history metadata remain protected. Planned title, specification and research fields can change. Old source-register IDs must remain intact; new direct research citations can be written in the body without inventing source IDs. The research prompts require preservation of important existing facts, decisions, completed work, important data and URLs when reorganizing the text.

The supplied `BASE_SHA256` goes in `project_update_base_sha256`; the importer checks it against the current LF-normalized record and removes it. The dialog also guards against changes since it was opened. Invalid metadata, identity/phase changes, stale content and unsafe paths are rejected. Before replacing, the manager backs up the actual original file bytes under `business_portfolio/.local/project_backups/<ID>/`. Failed validation restores the record and previous generated views. The `work/` directory is never replaced by this action. Pasting is available only in phases 1–3 and never advances the phase or commits/pushes the local edit.

Dragging one external Markdown file onto the selected research project remains an optional input route to the same replacement behavior. Folder import is a compatibility option for valid research project files, not the default creation workflow. Use **New project** and **Paste project text** for normal work.

## Execution checkpoints and handoffs

At every Phase 4, 5 or 6 checkpoint, Codex writes and reports an honest approximate line such as **Phase 4 completion estimate: 65% (best guess)**. It explains what is complete, what remains and why the estimate fits. Estimates may change; they are not measured completion evidence. The project record keeps completed and remaining checklists, observed results, blockers and the next action.

Codex records important information as it works: artifact paths, versions/hashes, project/submission IDs, commands, configuration, relevant costs/results and all source, build, preview, live, upload, sale/download, edit/admin, marketing, support and analytics URLs. Each ledger entry states purpose, observed status and verification date; planned links are not labelled live. Preserve retired links as history. Credentials, session tokens and private customer/payment information never belong in the public project file.

After genuinely finishing the current phase, Codex uses the lifecycle command with its actual evidence summary:

```text
python -m portfolio_manager.project_lifecycle set-phase --project "PATH/TO/project.md" --phase working_phase_5 --actor codex --evidence "Actual build and test evidence" --title "Appropriate Product Name"
python -m portfolio_manager.project_lifecycle set-phase --project "PATH/TO/project.md" --phase working_phase_6 --actor codex --evidence "Actual verified release evidence"
python -m portfolio_manager.project_lifecycle set-phase --project "PATH/TO/project.md" --phase complete --actor codex --evidence "Actual verified marketing evidence" --description "Factual product and launch summary" --sale-url "VERIFIED_PRODUCT_URL" --marketing-url "VERIFIED_MARKETING_URL"
```

The optional Phase 4 `--title` changes the display title while retaining the ID and path. For public delivery without a sale page, completion can use `--other-url` instead of `--sale-url`; additional verified URLs can be supplied with repeated flags. These example placeholders must be replaced with real observed URLs. `--actor codex` describes the handoff and is not a credential or permission grant; Codex must actually inspect the work and external results. The UI does not manually advance execution phases or mark Complete. Earlier phases can be reopened for corrections, which also revokes a matching completion receipt when applicable.

Completion creates `business_portfolio/completed_projects/<ID>.json` with the factual description and verified sale/access and public marketing links. The Completed Projects view retains that receipt after the original niche/project is removed. Editing or deleting a receipt requires a deliberate filesystem action; niche deletion does not delete it. Unfinished required tasks, pending required releases or inaccessible required marketing evidence remain blockers rather than being recorded as completed.

## Existing-project migration

The six-phase migration moves each old project directory out of its intermediary `projects/` folder without discarding `work/`. It preserves stable IDs, recorded progress and evidence. Old development Phase 2 becomes new Phase 4; old launch-research Phase 3 becomes new Phase 2; old combined execution Phase 4 becomes new Phase 5; Complete remains Complete. The migration records old phase values and source paths, updates current references and adds explicit remaining research/execution reconciliation tasks. It does not invent approvals for research that predates this workflow or reset existing work.

Historical archive snapshots and their original paths remain unchanged as evidence. Old phase numbers in historical text refer to the previous workflow; use the current metadata and appended migration note to resume the right stage.

## Open, reconnect and stop controls

In a Codex chat attached to the repository, ask to open Portfolio Manager. The chat uses the existing Computer Bridge `portfolio_open`, retrieves this chat's selection with `portfolio_context`, and changes it with `portfolio_select` when requested. Each chat has its own window/selection. Selecting an item does not start an AI worker. The optional trusted SessionStart hook supplies the private reconnect key automatically; the owner need not enter it. Keep session identity and another chat's selection separate.

**AI Only (AFK)** / **Human Available** is shared availability information, not an execution-permission switch. The header's **Resume after stop** uses the existing Computer Bridge resume action. It clears the current stop state without granting permissions or starting a worker. Computer Access and Emergency Stop remain available through the main menu and retain their existing controls.

The Working checkbox on each niche is a shared informational focus flag. Enabling a child enables its ancestors; disable Working descendants before disabling their parent. History & Existing Work preserves prior records; Repository files remains the optional full explorer. These view choices do not authorize actions or alter commercial state.

## Validation and practical limits

Canonical project records and `NICHE.json` files are authoritative; `PROJECT_INDEX.json` / `PROJECT_BROWSER.html` are generated views. Rebuild and validate after edits. The regression workflow also checks the canonical records and regenerated views. Use current test results when reporting changes rather than copying historical test counts.

Current planning/import actions do not authorize spending, ads, account creation, outreach or publication. Actual session authorization and Computer Bridge controls remain authoritative. The nominal CAD100 cumulative planning ceiling is separate from CAD0 default authorized spending. Keep one writer per record, preserve external-effect history and never claim an unrun test or unseen live page was verified.
