# Portfolio niche and project overhaul — completion report

**Date:** 2026-11-15  
**Repository baseline:** `Hi62384/Proj` `main` and `origin/main` both at `167b15f70666d249e1726c4f7885f53c77671f17` before changes. These changes are in the local checkout; no commit or push was made.

## Outcome

| Item | Before | Now |
| --- | ---: | ---: |
| Active canonical project records | 139 | **3**, all in Game Development Marketplaces |
| Preserved historical project records | 0 in separate archive | **139**, original metadata and bytes retained |
| Active niche nodes | Legacy structure | **182**: 36 taxonomy categories, 144 subcategories, Game Development Marketplaces, AI Workflow Automation |
| Original niche files preserved | 301 in old active tree | **301** in dated archive; all Git blob hashes match the original `HEAD` |
| New commercial product implementations | 0 | 0; only three planning records were added |

The owner workbook `Game_Marketplace_Research_REPAIRED.xlsx` (SHA-256 `4AB2E94010A87D19509407E94AAC7106BED439617226C16DB0A567CC5910507A`) was read as research, not copied into the public repository or treated as proof of paid demand. The 1,512 opportunity-library research records remain research, not active projects.

## What changed

- The migration script `business_portfolio/tools/overhaul_niches.py` inventoried and moved the original niche tree into `business_portfolio/archive/2026-11-15-legacy/niches/`. Its file manifest and ID/path crosswalk preserve original status, source IDs and project links. The builder verifies all archived file hashes and crosswalk fields before indexing history. A documented `restored_from_archive_sha256` check permits an intentional future restoration without silently reusing an ID.
- The current `niches/` tree uses the checked-in taxonomy names and contains no placeholder project records. The only active projects are **GDM-001 Historical Save Regression Lab** (first validation focus), **GDM-002 Advanced Capacity-Aware NPC Transport System** (queued), and **GDM-003 Packaged Build / Native Dependency Verifier** (queued). Each has an engine-edition plan, competitor/free-tool comparison, bounded MVP, negative tests, rights/channel constraints, kill rule and honest checkpoint. All remain `planned`, `unvalidated`, `execution_authorized: false`, with CAD0 authorized spend and unknown revenue/profit.
- The Business Portfolio browser opens on Projects, with separate Niches and History & Existing Work views. Old records are searchable by stable ID, and their source record is available through the local allowlisted read-only file route. Project details have Overview, Files, Results, Tasks & Progress and Complete record panels. Empty leaf niches display “No active projects”; no progress percentage is invented. Generated `PROJECT_INDEX.json` and `PROJECT_BROWSER.html` were rebuilt from source.
- Portfolio Manager retains per-chat selection and the global availability and Computer Access controls. Its normal project tree is small; History & Existing Work exposes old records, and the optional Repository files view loads arbitrary folders in a background task. Selecting a project shows plain-language Overview, Files, Results, Tasks & Progress and Complete record tabs. The coordinator excludes queued GDM families from eligibility. A selected archived record provides an explicit restoration warning, without starting a worker.
- `AGENTS.md`, portfolio schema, README and workflow guide explain the active/history split. Existing product source directories, private checkpoints, Payhip listings, Computer Bridge permissions, Stop/Emergency Stop, legacy recovery code and other chats' selections were not changed.

## Verification performed

| Check | Result |
| --- | --- |
| Archive compared with original Git tree | **301/301 tracked files matched** Git blob hashes; no missing or changed original file. |
| Portfolio build and `--check` | Pass: 3 active records, 139 historical records, 182 niche nodes, 114 source records. |
| `business_portfolio` tests | **89 passed, 1 skipped** (90 run); archived-history and integrity tests included. |
| Commercial checks | Pass for 3 active records and explicit scenarios; no actual sale or spending verified. |
| Opportunity library build check and tests | 43 reproducible artifacts unchanged; **49 tests passed**. |
| Portfolio Manager full suite | **136 passed, 4 skipped** (140 run) with normal local Windows pipe/ACL access. The restricted run could not exercise Windows pipe/ACL tests and is not counted as a code failure. |
| Browser UI in isolated headless Chromium | Projects showed 3 cards; History showed 139; Niches showed 37 top-level nodes (36 categories plus AI Workflow Automation); an archived `EX-001` ID opened with an offline source-file link; no page-script errors. |
| `git diff --check` | Passed. |

The running shared Portfolio Manager/Business Portfolio service was **not restarted** to avoid interrupting other chats. Therefore this report does not claim that an already-open window has loaded the new code. The isolated UI check used the rebuilt snapshot. The optional repository-file explorer passed a disposable window test; the owner's existing live window has not been manually exercised after this change. Browser link availability to protected product ZIPs remains intentionally limited.

## Remaining work

1. **Single next task:** validate GDM-001 with three independent Unity teams maintaining released games, with owner approval before any outreach. Obtain permission for anonymized historical-save failure examples; compare the teams' current testing setup, time and willingness to evaluate a bounded prototype. This is discovery, not a build or sales claim.
2. Recheck candidate engine versions, marketplace submission rules, prices and competitor capabilities before any product or listing decision. GDM-002/003 remain queued until the first focus decision and their own evidence gates.
3. When convenient, reopen or restart the shared Portfolio Manager/browser service to load the new views, then visually inspect the live owner window and its per-chat selection. Do this only when connected chats can tolerate a brief interruption.
4. An intentional restoration of any archived project requires its current private checkpoint and external-state review; the archive itself remains preserved. No historical uploads, orders or publication should be replayed.

No account, store, purchase, outreach, upload, publication, spend, commit or push was performed for this overhaul.
