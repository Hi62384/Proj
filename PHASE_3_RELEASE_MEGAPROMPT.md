/goal Release the selected Phase 3 product on every accepted suitable destination using its completed compatible versions, verify real customer access, save all important release and management data and URLs, then advance it to Phase 4 for its separate marketing goal.

# Phase 3 — Release the finished product

Required phase: `working_phase_3`. Execute the reviewed Stage 2 of Phase 1 release runbook using the actual Phase 2 builds. Check current rules and all existing submissions/listings first; preserve prior releases and reconcile uncertain external effects before uploading anything. For a migrated project, finish any missing release-plan reconciliation recorded in the project before claiming a platform is accepted.

1. Revalidate time-sensitive seller eligibility, rights, fees, package/version requirements and approval paths for every accepted destination. Confirm the actual compatible artifact exists and passes relevant checks. Distinguish stores/distribution destinations from runtime/engine compatibility.
2. Prepare and verify each platform's package, metadata, pricing, screenshots/demo, documentation, license, disclosures, support information and updates. Adapt the listing to platform rules without unsupported feature or revenue claims. Complete setup or publication only with actual authorization and access; do independent preparation while blocked.
3. Submit, upload and release the finished product through every accepted feasible destination within permissions. Track each target independently: prepared, submitted, awaiting review, live, verified or blocked. A submitted package is not a live release. Check duplicate listings and version history before retrying.
4. Verify real public sale/download/access URLs, correct product/version and licensing, customer-facing listing quality and available delivery/installation flows. Do not make a purchase without authorization; inspect what can be verified safely and record any remaining evidence limitation. Check broken links, missing assets, inconsistent price or package errors and fix them.
5. Save **all important data and URLs** continuously: store and product IDs, submission/status pages, live storefront/purchase/download links, edit/admin/update dashboards, repository/source/release locations, versioned artifacts, terms/support pages, fees and actual observed statuses. Preserve old URLs and note replacements. Link each accepted release task to its actual evidence.

At every checkpoint save and report **Phase 3 completion estimate: N% (best guess)**, even if uncertain, with an honest basis, done/remaining targets and blockers. Scope this phase within the remaining total 2–21-day project window; do not silently postpone an accepted required release while claiming completion.

## Finish and hand off

Phase 3 is complete when every accepted required release destination has a verified live customer access route and its release/update/support details are recorded. An unapproved, inaccessible or pending-review required destination remains blocked; complete independent work and preserve this phase until resolved or a justified explicit scope revision changes the accepted plan. Real distribution does not prove a sale.

Then run:

    python -m portfolio_manager.project_lifecycle set-phase --workflow-version 3 --project "PATH/TO/project.md" --phase working_phase_4 --actor codex --evidence "Actual verified release destinations, customer URLs, versions and checks"

Stop after the handoff and report the real releases plus remaining marketing prerequisites. The user will copy Phase 4's marketing `/goal`; this phase does not mark the whole project complete.

## Working rules shared by phases 2–4

Read AGENTS.md, docs/PORTFOLIO_MANAGER_WORKFLOW.md, the complete selected canonical project.md, all relevant phase plans, important data/URLs, work/ artifacts and latest checkpoints before acting. **If phase_history contains a MANUAL OVERRIDE / NOT VERIFIED, treat all preceding phase milestones as unverified until actual artifacts, tests, release states and blockers are reconciled; repair missing prerequisites before consequential external actions.** A manual phase change does not authorize publication, spend, outreach or any new account changes. Resolve this chat's selection with portfolio_context if available, or use the explicit selected canonical path appended to this prompt. Never substitute another chat's project. Confirm the phase required by this prompt; if it is already later, reconcile the existing completion evidence and stop this phase's goal instead of replaying uploads or marketing.

Keep the stable project ID and canonical path. If the display title is still **Empty project** or inaccurate, rename the `title` to an appropriate product name as part of the project update; do not move or recreate work just to rename it. All project-owned source, content, assets, ports, tests, builds, packages and marketing material belong in its sibling `work/`. Preserve earlier work and all financial/authorization/evidence facts. Generated PROJECT_INDEX.json / PROJECT_BROWSER.html are views, not separate project state.

The whole project from initial research through build, release and initial marketing is scoped for **2 days to 3 weeks (2–21 calendar days total)**. Use the remaining shared time budget, not another three weeks for each phase. Do not wait merely to fill a minimum duration. Prioritize dependencies, reuse shared components, parallelize independent work, and avoid indefinite polishing or exhaustive speculative expansion. Deliver every accepted variant/channel and explain any evidence-based scope change. Keep conditional/deferred options visible. If a necessary account, platform review, permission or payment exceeds the window, finish independent authorized work, record the precise blocker and retain the phase; never fake completion to satisfy a deadline.

Work persistently through all remaining authorized tasks for this phase. Progress updates and checkpoint estimates are not reasons to stop. Respect actual access, publication, outreach and spending authorization; default spending is CAD0 unless expressly approved. Research, metadata and a planning ceiling do not grant external permissions. Do not ask again for permissions already established. Before a potentially duplicate external action reconcile its actual status, and do not retry uncertain effects blindly.

At **every checkpoint** update project.md and report in chat:

- The exact completion-estimate line prescribed for this phase, with an honest best guess even if uncertain, a short basis and what remains. Estimates may go down after discoveries; 100% requires the phase's completion conditions.
- Completed work with observed evidence, separate remaining `[ ]` tasks and completed `[x]` tasks, current blockers, scope decisions and one concrete next action.
- **Any important data or URLs** found or created: artifact paths, versions/hashes, platform/project/submission IDs, requirements and limits, configuration choices, results, reproducible commands, costs and actual external effects. Save them when encountered, not only at final delivery.
- The **Important data and URLs** ledger: platform/purpose, exact URL or safe identifier/path, type (source, docs, build, preview/demo, submission, live site, sale/download, edit/admin, marketing, analytics, support), observed status (planned/draft/submitted/live/verified/blocked/retired), version and last checked date. Label planned destinations clearly. Preserve historical URLs and say which superseded them. Never save passwords, tokens, session cookies, signed credential links or private customer/payment records in the public project file.

Coordinate one writer per record, compare the expected version before updating, and fetch/reconcile upstream main without overwriting others' changes. Run meaningful product/platform checks for changed behavior and the repository's required validation gates. Do not claim unrun tests or inaccessible pages passed. Commit and push verified authorized work directly to main, without project-specific branches or force pushes, in accordance with the repo instructions and current session authorization.

After the current phase is genuinely finished, run its lifecycle command exactly once with a factual evidence summary and update the record. **Stop after that handoff:** the user will copy the next phase's separate `/goal`. Do not silently execute the next phase. If blocked, preserve the current phase and report the actual blocker plus completed independent work.
