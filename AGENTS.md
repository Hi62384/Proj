# Project instructions

<!-- ProjectBridge offline-patch instructions; do not duplicate -->
## ProjectBridge delivery modes — choose based on the request

- **Codex, IDE agents, local coding agents, and any agent working in a writable checkout:** **edit files directly** using the normal coding workflow, then test and report results. **Do NOT produce `ProjectBridge_patch.zip`** unless the user specifically requests it. The presence of these instructions does not mean ZIP delivery was requested.
- **Normal ChatGPT reading GitHub read-only, without a writable checkout:** for coding-change requests, **default to a ProjectBridge patch ZIP** unless the user requests another output. Read `PROJECTBRIDGE_PATCH_INSTRUCTIONS.md` **in full** before building a ZIP, then package only the relevant changes against the GitHub baseline.
- For all other tasks, use the tools and delivery format explicitly requested by the user. Never replace direct Codex edits, commits, or PRs with a ZIP without the user asking.
- Preserve project-specific build/optimization instructions elsewhere in `AGENTS.md`. Report tests honestly.

## Business Portfolio checkpoints

- Canonical records live in `business_portfolio/niches/**/projects/*.md` with strict JSON frontmatter; stable project and niche IDs survive moves. Read the full record and latest authorized private checkpoint before resuming work. Preserve completed work, actual financial evidence and uncertain external effects; do not replay uploads, publication or orders.
- Use one writer per record and compare the expected content before saving. Checkpoint observed work, remaining tasks, blockers, evidence limits and one concrete next action. Generated `PROJECT_INDEX.json` / `PROJECT_BROWSER.html` are read-only views, not a second progress database.
- After producing a reviewed, non-sensitive text result, record its `public_results` entry using `business_portfolio/SCHEMA.md` and place it under `business_portfolio/results/<same project ID>/` so the live Files & Results view updates automatically. Keep private receipts/customer data, paid releases and unreviewed binaries out of that public namespace; do not claim planned files exist.
- Rebuild with `python business_portfolio/tools/build_browser.py`, then run `--check`, `python -m unittest discover -s business_portfolio/tests -v`, and `python business_portfolio/tools/commercial_checks.py --portfolio business_portfolio`. See the local integration report for browser acceptance limitations.
- Portfolio import authorizes planning only: CAD0 current spending, no outreach/ads/accounts/schedules/production workflows. CAD100 is a cumulative planning ceiling, not permission. Keep operational/financial/customer data outside the public records; preserve official Codex/Computer Bridge permissions and retained legacy systems.

## Portfolio Manager

- Portfolio Manager is the primary visual workspace. For “Open the project,” “show the projects,” or “let me see the files,” find the checkout with `git rev-parse --show-toplevel` and call `portfolio_open` through the existing Computer Bridge MCP. It starts or reuses the controller and opens this connection's own window. Use `portfolio_context` for “Continue” or questions about the selection. Use `portfolio_select` when the owner requests a different path. Retain the private reconnect key from the first response in chat context so the same workspace can reconnect if MCP restarts. The owner never needs to enter a key.
- Work on the selected file or ordinary folder within the authorized Codex scope. For a portfolio folder, read shared status and the complete canonical record before working. Register and claim work through the coordinator, renew the lease, and save the verified checkpoint. An explicitly requested background worker uses `portfolio_start_selected`; `portfolio_stop_selected` stops that workspace's worker. Direct chat work uses its own claim and releases it when stopping.
- Use the integrated Computer Access tab and existing Bridge MCP for authorized computer/browser work. AI Only parks actions that require owner input. Human Available displays the exact requests for review. Keep approval, verification and commercial outcomes distinct, and reconcile uncertain effects before retrying. If the coordinator is unavailable or stopped, reconnect or request local help before starting portfolio work.
- See [Portfolio Manager workflow](docs/PORTFOLIO_MANAGER_WORKFLOW.md) for startup, fresh-chat commands, permissions, recovery and rollback. Unrelated repository coding requests use the normal workflow.
