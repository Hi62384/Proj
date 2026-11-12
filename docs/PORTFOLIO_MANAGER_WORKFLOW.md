# Portfolio Manager

Open `Start_Portfolio_Manager.cmd` from the repository. It uses the installed Computer Bridge environment and opens the same Windows controller. If an older Bridge process is running, quit it from the Windows tray and reopen the launcher. The `Computer Access` tab holds the existing Chrome, desktop, file permission and approval controls.

Choose **AI Only (AFK)** to keep approval prompts quiet, or **Human Available** when you can respond. Choose a folder under `business_portfolio/niches` and start a worker. A parent folder includes its descendants. The Portfolio tab shows project records, worker assignments, verified milestones and available results. Review requested actions in the Portfolio or Computer Access tab. A completed manual step needs a fresh verification before any dependent action.

**Stop All** stops dispatch and cancels in-flight work. **Emergency Stop** and the existing `Ctrl+Alt+F12` shortcut also revoke computer access. Resume workers in the Portfolio tab, and restore computer permissions separately in Computer Access Settings. Closing the window to the tray keeps the controller alive. Quit from the tray to shut it down. A Windows Startup shortcut to `Start_Portfolio_Manager.cmd --background` is optional. Create it in your own Startup folder if you want the controller to open at sign-in.

## Start from a fresh Codex chat

Use the actual repository root returned by `git rev-parse --show-toplevel`. Read its `AGENTS.md`, then use the existing `codex_computer_bridge` MCP integration when available. `portfolio_open` opens the integrated window, `portfolio_status` reads the saved mode and assignments, and `portfolio_start_worker` assigns a requested folder to the shared supervisor. Supply a `folder` argument relative to `business_portfolio/niches`, such as `ai-workflow-automation`, or a full path within it. The owner's instruction to work on the folder is the authority to start local work. Other requests should follow their normal repository workflow.

The equivalent commands run from the repository root:

```powershell
python -m portfolio_manager open
python -m portfolio_manager status --folder ai-workflow-automation
python -m portfolio_manager start_worker --folder ai-workflow-automation
```

A chat that coordinates work directly can use `portfolio_register`, `portfolio_claim`, `portfolio_heartbeat`, `portfolio_request_human` and `portfolio_release`. Pass the private `worker_key` from registration with the `worker_id` on subsequent calls. Lease operations after a claim also require its `lease_token`. Keep these values in the chat's local working context. Read the full record at `record_path`, the returned task and checkpoint before work, and renew the lease while working. Use the background worker path for isolated draft execution and verified completion. A direct chat may release blocked or interrupted work with a short checkpoint. Its lease cannot certify a successful result or grant permissions. Check shared status before requesting a different project. If the controller is stopped or unavailable, reconnect or wait for the owner to resume it.

Example chat requests:

- “Open Portfolio Manager and show me the unfinished projects in ai-workflow-automation.”
- “Start a Portfolio Manager worker for ai-workflow-automation/agency.”
- “Check the last verified checkpoint and tell me which decision is holding this project.”

## Work and permissions

Canonical project records remain under `business_portfolio/niches`. The coordinator keeps its operational database in the Bridge's private user profile under `portfolio-manager`. It records workers, leases, tasks, requests, evidence and effect history. A worker with a valid lease holds the project. On interruption the coordinator retains the checkpoint and applies its lease and reconciliation rules before redispatch. Check external provider state for any uncertain upload, payment, message or publication before considering a retry.

Background reasoning uses the existing Relay connection to the official Codex app-server. A worker opens a separate task workspace and reads the approved project context through exact file grants. The app checks the configured WSL or native sandbox and existing ChatGPT sign-in before dispatch. Account operations go through the owner-controlled Computer Access tab and existing MCP bridge, where the original per-site and per-action rules apply. Background workspace tools produce reviewable local draft files and evidence. Use a scoped, authorized interactive chat for an actual desktop/browser operation or production change. The coordinator records approved actions separately from verified outcomes. [Official OpenAI documentation](https://developers.openai.com/blog/codex-as-a-platform)

In AFK, computer actions that require fresh approval are parked. Their status appears in Computer Access. On returning, inspect the current target and request the action again. A mode change invalidates pending Bridge confirmations. The portfolio request queue retains task decisions independently of the Bridge's short-lived action cards. Approval, login, MFA, CAPTCHA, purchase, outreach, publication, financial changes and sensitive access each require their applicable owner permission. The budget for new spending remains CAD0.

## Progress and recovery

Development percentages require weighted milestones and verified evidence. Checkpoints and draft files represent preparation. Publication and commercial evidence have separate fields. A test checkout, a test sale or a successful build does not establish verified customer revenue. The explorer serves existing reviewed results from the canonical record's `public_results` and shows verified private workspace artifacts to the owner.

The integrated launcher makes a SQLite backup of the existing Bridge message and project stores in `state-backups/before-portfolio-manager` before opening them. Its migration adds a separate coordinator database. Chrome Native Messaging, existing Codex MCP registration and the Bridge's permissions remain in their established locations. To return to the Bridge-only window, quit the current process and run `Start_Portfolio_Manager.cmd --bridge-only`. This retains the saved database for later use. Restore SQLite backups only with the controller closed and after saving the current database. Keep worker drafts, databases, logs, account records and releases outside Git.

## Current acceptance

The Windows tests used a disposable profile to start the actual controller twice, checked that both launches used the same process, and connected independent CLI processes through its authenticated named pipe. Fictional worker tests exercised overlapping claims, progress verification, AFK requests, manual handoff, restart recovery and continued dispatch. An existing Bridge window can stay open until you are ready to switch to the new launcher.

The live runtime checks on November 11, 2026 stopped before a model turn. Native Windows rejected the restricted sandbox profile because the elevated sandbox required effective root read access. The configured Ubuntu WSL2 installation, bubblewrap and Codex executable were present, but the WSL preflight timed out. The live fictional inference requires separate acceptance. To recheck runtime availability, run `python -m portfolio_manager.tests.live_runner` in the existing Bridge Python environment. It checks the disposable runtime without starting a model turn.

Background workers currently complete bounded local drafts and verify file contents, hashes and supported syntax. Keep executable acceptance tests, substantial canonical edits and account or provider work in an explicitly authorized interactive Codex session. Progress stays uncalculated for projects that lack a weighted milestone plan. Automatic provider login verification, live browser or desktop acceptance from this build, and commercial performance integrations remain outstanding.
