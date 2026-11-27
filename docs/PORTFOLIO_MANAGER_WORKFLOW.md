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

Codex normally advances execution phases, but owners may manually advance **Phase 2 → 3** or **Phase 3 → 4** if the handoff gets stuck. Manual changes require explicit confirmation, are recorded as an unverified manual override in phase_history, and preserve remaining tasks. Before consequential external actions the next worker must verify unfinished prerequisites. Phase 1 cannot be bypassed with the phase controls; Phase 4 → Complete requires Codex verification and real product/access and public marketing URLs.

## Four phases and the prompt buttons

| Phase | Purpose | Prompt | Forward handoff |
| --- | --- | --- | --- |
| 1 | Complete research, specification, compatibility, release and marketing planning | **Copy research prompt**: Phase 1a new product or existing idea; Phase 1b independent verification | Paste the final verified record once; automatically advances to Phase 2 |
| 2 | Build, test, document and package every accepted compatible version | **Copy build prompt**: Codex /goal | Codex to Phase 3; confirmed unverified manual fallback |
| 3 | Actually release all accepted required versions and verify customer access | **Copy release prompt**: Codex /goal | Codex to Phase 4; confirmed unverified manual fallback |
| 4 | Execute and verify the finite initial marketing campaign | **Copy marketing prompt**: Codex /goal | Codex to Complete with verified evidence and URLs |

Set the **Budget ceiling (CAD)** and **Project day limit** before copying a prompt. Both fields remain available in each active phase and save between sessions. Budget is a planning ceiling, not spending authorization. The default day limit is 21 days for the entire project, not a fresh budget for each stage. Plan feasible scope, preserve deferred/rejected options and reasons, and record real access or review delays.

Current records use workflow_version 3 and working_phase_1 through working_phase_4, then complete. Phase, work state, commercial validation and niche Working are independent.

## Research: two prompts, one paste

1. Select or create a Phase 1 project. Copy Phase 1a (research a new product, or research your existing idea) and send it in ChatGPT.
2. Phase 1a performs **Stage 1 product research and internal verification → Stage 2 release platforms/compatibility research and internal verification → Stage 3 marketing research and internal verification**. Each stage must verify its evidence and resolve material defects before proceeding. Reject failed finalists and investigate viable alternatives rather than forcing GO. Reconcile all accepted variants and plans in one draft. Do not paste the intermediate draft.
3. In the **same ChatGPT chat**, send Phase 1b. It uses the latest Phase 1a draft, independently rechecks all three stages using fresh evidence, corrects material issues, rechecks affected stages and returns the entire final record. Even “Good to go — no substantive changes needed” must include the full record.
4. Copy the final project record once and choose **Paste project text** in Portfolio Manager. The app validates, saves, backs up and automatically advances a valid verified record to Phase 2. A draft, blocked or unverified record stays in Phase 1. A meaningful failure must not be approved just to move forward.
5. Copy the Phase 2 build goal into Codex. Repeat for the separate Phase 3 release and Phase 4 marketing goals after their verified handoffs.

Each research stage retains its original depth: buyer need and complete free/native/AI/paid alternatives, rights and economics, direct and adjacent compatibility and distribution requirements, and audience, positioning, content, permitted channels, conversion and measurable marketing. Every accepted version needs build/test coverage; every accepted destination and marketing tactic needs an actionable execution plan. No research finding proves future sales. If a response ends early, send "continue" in the same chat and resume from its recorded checkpoint.

### What a paste preserves and validates

Paste accepts a complete Markdown record with strict JSON frontmatter, optionally wrapped in one Markdown fence. The body can be reorganized, but existing facts, work, important data/URLs, decisions, registered sources, identity, permissions, financial evidence, workflow and current phase must remain intact. New direct sources go in the body, not invented register IDs.

The prompt supplies BASE_SHA256 for the temporary project_update_base_sha256 field. The final Phase 1b record may declare project_update_phase_1b = "verified" only with all three research_verification entries (phase_1 = product, phase_2 = release, phase_3 = marketing) approved, a GO verdict, a substantive non-draft project and complete researched/verification/execution/ledger sections. The manager checks the exact snapshot, schema and structure, including source URLs; it does not independently validate market claims. Temporary import fields are stripped. Saving and advancement are one transaction; a failure restores the prior record and generated views. The original file bytes are backed up under business_portfolio/.local/project_backups/<ID>/. Work artifacts are untouched. A concurrent or stale record is rejected.

Drag/drop of a complete research file onto its selected project uses the same validation and advancement. Folder import remains a compatibility option and does not assert approval. No paste grants permission to spend or commits/pushes the local record.

## Execution checkpoints and handoffs

At every Phase 2, 3 or 4 checkpoint, Codex writes and reports an honest approximate line such as **Phase 2 completion estimate: 65% (best guess)**. It explains what is complete, what remains and why the estimate fits. For migrated records, append new numbered estimates below the Four-phase workflow migration heading; the earlier estimates belong to the historical numbering. Estimates may change; they are not measured completion evidence. The project record keeps completed and remaining checklists, observed results, blockers and the next action.

Codex records important information as it works: artifact paths, versions/hashes, project/submission IDs, commands, configuration, relevant costs/results and all source, build, preview, live, upload, sale/download, edit/admin, marketing, support and analytics URLs. Each ledger entry states purpose, observed status and verification date; planned links are not labelled live. Preserve retired links as history. Credentials, session tokens and private customer/payment information never belong in the public project file.

After genuinely finishing the current phase, Codex uses the lifecycle command with its actual evidence summary:

```text
python -m portfolio_manager.project_lifecycle set-phase --workflow-version 3 --project "PATH/TO/project.md" --phase working_phase_3 --actor codex --evidence "Actual build and test evidence" --title "Appropriate Product Name"
python -m portfolio_manager.project_lifecycle set-phase --workflow-version 3 --project "PATH/TO/project.md" --phase working_phase_4 --actor codex --evidence "Actual verified release evidence"
python -m portfolio_manager.project_lifecycle set-phase --workflow-version 3 --project "PATH/TO/project.md" --phase complete --actor codex --evidence "Actual verified marketing evidence" --description "Factual product and launch summary" --sale-url "VERIFIED_PRODUCT_URL" --marketing-url "VERIFIED_MARKETING_URL"
```

The optional Phase 2 `--title` changes the display title while retaining the ID and path. For public delivery without a sale page, completion can use `--other-url` instead of `--sale-url`; additional verified URLs can be supplied with repeated flags. These example placeholders must be replaced with real observed URLs. `--actor codex` describes the handoff and is not a credential or permission grant; Codex must actually inspect the work and external results. The UI supports confirmed unverified Phase 2 → 3 and Phase 3 → 4 recovery overrides, but never manually marks Complete. Earlier phases can be reopened for corrections, which also revokes a matching completion receipt when applicable.

Completion creates `business_portfolio/completed_projects/<ID>.json` with the factual description and verified sale/access and public marketing links. The Completed Projects view retains that receipt after the original niche/project is removed. Editing or deleting a receipt requires a deliberate filesystem action; niche deletion does not delete it. Unfinished required tasks, pending required releases or inaccessible required marketing evidence remain blockers rather than being recorded as completed.

## Existing-project migration

The version-2 six-phase workflow maps former research Phases 1–3 to Phase 1, build Phase 4 to Phase 2, release Phase 5 to Phase 3, marketing Phase 6 to Phase 4, and Complete to Complete. Version-1 development Phase 2 maps to build Phase 2; launch research Phase 3 maps to research Phase 1; combined execution Phase 4 maps to release Phase 3. Stable paths, work, permission fields, prior evidence and phase history remain intact. Migrated execution estimates are carried forward only from the corresponding old execution phase. The manager also interprets compatible older local-only records and upgrades them on their next save. It does not invent missing research approvals. Historical snapshots and phase references remain historical evidence. Use current copied prompts and the explicit --workflow-version 3 flag; obsolete handoff commands are rejected.

## Open, reconnect and stop controls

In a Codex chat attached to the repository, ask to open Portfolio Manager. The chat uses the existing Computer Bridge `portfolio_open`, passing its project ID or canonical project record path when it already knows the project. The window selects that project, opens the Projects view, and expands the folders to reveal it. Otherwise it preserves the existing selection. The manager cannot independently see what the chat knows; the chat must pass the identifier or select the record. It retrieves this chat's selection with `portfolio_context`, and changes it with `portfolio_select` when requested. Each chat has its own window/selection; selecting a project displays its title in that window, and without a project the full chat identifier is shown. Selecting an item does not start an AI worker. The optional trusted SessionStart hook supplies the private reconnect key automatically; the owner need not enter it. Keep session identity and another chat's selection separate.

**AI Only (AFK)** / **Human Available** is shared availability information, not an execution-permission switch. The header's **Resume after stop** uses the existing Computer Bridge resume action. It clears the current stop state without granting permissions or starting a worker. Computer Access and Emergency Stop remain available through the main menu and retain their existing controls.

The Working checkbox on each niche is a shared informational focus flag. Enabling a child enables its ancestors; disable Working descendants before disabling their parent. History & Existing Work preserves prior records; Repository files remains the optional full explorer. These view choices do not authorize actions or alter commercial state.

## Validation and practical limits

Canonical project records and `NICHE.json` files are authoritative; `PROJECT_INDEX.json` / `PROJECT_BROWSER.html` are generated views. Rebuild and validate after edits. The regression workflow also checks the canonical records and regenerated views. Use current test results when reporting changes rather than copying historical test counts.

Current planning/import actions do not authorize spending, ads, account creation, outreach or publication. Actual session authorization and Computer Bridge controls remain authoritative. The nominal CAD100 cumulative planning ceiling is separate from CAD0 default authorized spending. Keep one writer per record, preserve external-effect history and never claim an unrun test or unseen live page was verified.
