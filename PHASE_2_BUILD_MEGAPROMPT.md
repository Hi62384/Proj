/goal Build and finish the selected Phase 2 product, including every accepted compatible version, verify the complete customer experience, preserve all important data and URLs at every checkpoint, then advance it to Phase 3 for its separate release goal.

# Phase 2 — Build and verify

Required phase: `working_phase_2`. This is production and verification after the three internal research stages in Phase 1. Reconcile the product specification, accepted compatibility targets, release requirements, marketing asset requirements and research decisions before implementation. For a migrated existing project, preserve finished work; resolve the recorded missing planning checks with current evidence and bounded investigation rather than starting over or assuming old approvals.

1. Start with the smallest decisive proof where Phase 1 product research identified a technical/quality/differentiation uncertainty. Use fair representative inputs and the strongest relevant alternative; apply the recorded stop/pivot criteria. **Do not demand paid buyers** before a reasonable local TEST-FIRST proof. If an evidenced premise fails, checkpoint the result and revise within authorized scope.
2. Implement the complete selected product and **a genuinely compatible version for every accepted target** in the Stage 2 of Phase 1 matrix. Share a core where useful, but verify engine/runtime/format-specific adapters and customer-facing behavior. For creative products, complete all accepted manuscripts/assets/formats and quality checks. A planned port or copied source folder is not tested support.
3. Complete all product-facing interfaces, error handling, documentation, licensing notices, dependencies, examples/demo, installation/onboarding and release packages. Prepare the screenshots, demonstrations and accurate proof material required by the Stage 3 of Phase 1 marketing plan.
4. Test representative normal and failure cases, integration boundaries, target versions, first-use installation, packaging and regressions. Inspect the actual product in its real environment where available; label simulations, mocks and unavailable platform coverage. Fix material issues until the acceptance criteria are met.
5. Reconcile the accepted compatibility/release/marketing matrices with actual builds and artifacts. Record exact source/build/package paths, versions, test results, limitations, deployment/preview/edit URLs and next release prerequisites. Keep unapproved publication, external contact and spend as release and marketing execution dependencies rather than pretending they occurred.

At every checkpoint save and report **Phase 2 completion estimate: N% (best guess)**, even if uncertain, with evidence, completed/remaining work and the next action.

## Finish and hand off

Phase 2 is complete when the scoped product and every accepted compatible version are built, documented, packaged and meaningfully verified against the agreed acceptance criteria. Unavailable required tests or an unfinished accepted version remain blockers unless an explicit evidence-based scope decision legitimately removes them. A fresh name alone does not complete an Empty project.

Then run, replacing placeholders with the actual project path, evidence and descriptive title:

    python -m portfolio_manager.project_lifecycle set-phase --workflow-version 3 --project "PATH/TO/project.md" --phase working_phase_3 --actor codex --evidence "Actual build, variants, package paths and verification summary" --title "Appropriate Product Name"

Do not mark the whole project complete or carry out the release goal in this run. Report the finished build, remaining release prerequisites and that Phase 3's release prompt is now available.

## Working rules shared by phases 2–4

Read AGENTS.md, docs/PORTFOLIO_MANAGER_WORKFLOW.md, the complete selected canonical project.md, all relevant phase plans, important data/URLs, work/ artifacts and latest checkpoints before acting. Resolve this chat's selection with portfolio_context if available, or use the explicit selected canonical path appended to this prompt. Never substitute another chat's project. Confirm the phase required by this prompt; if it is already later, reconcile the existing completion evidence and stop this phase's goal instead of replaying uploads or marketing.

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
