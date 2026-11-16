# Business Portfolio: 13-niche overhaul completion

**Baseline:** `Hi62384/Proj` `main` at `4dcb633` matched `origin/main` before editing. The checkout was clean, and Portfolio Manager reported no active worker. No other chat's selection, active controller, product source, payment account or store was changed.

## Active business niches, in priority order

| Priority | Folder under `business_portfolio/niches/` | Display name | Active projects |
| ---: | --- | --- | ---: |
| 1 | `game-development-marketplaces` | Game Development Marketplaces | 3 |
| 2 | `marketplace-hosted-automations` | Marketplace-Hosted Automations | 0 |
| 3 | `ai-assisted-freelancing` | AI-Assisted Freelancing | 0 |
| 4 | `platform-specific-apps-and-extensions` | Platform-Specific Apps & Extensions | 0 |
| 5 | `advanced-online-products-and-software` | Advanced Online Products & Software | 0 |
| 6 | `specialized-data-and-intelligence-services` | Specialized Data & Intelligence Services | 0 |
| 7 | `usage-based-apis` | Usage-Based APIs | 0 |
| 8 | `licensing-and-royalties` | Licensing & Royalties | 0 |
| 9 | `affiliate-and-referral-businesses` | Affiliate & Referral Businesses | 0 |
| 10 | `advertising-supported-utility-websites` | Advertising-Supported Utility Websites | 0 |
| 11 | `online-content-and-media` | Online Content & Media | 0 |
| 12 | `online-games-and-virtual-economies` | Online Games & Virtual Economies | 0 |
| 13 | `lead-generation` | Lead Generation | 0 |

Each has only `NICHE.json` except the first, which has the three canonical Markdown records below. The game niche retains stable ID `N-gdm-20261115`. New niches have distinct `N-business-02` through `N-business-13` IDs. The 36-category/144-subcategory taxonomy remains in `opportunity_library/data/taxonomy.json` as independent research; it is absent from the primary business menu.

## Three active project families

| ID and path | Specification expansion | Edition candidates and limits |
| --- | --- | --- |
| `GDM-001` — `business_portfolio/niches/game-development-marketplaces/projects/gdm-001-historical-save-regression-lab.md` | Unity-first real-load/async adapter contract; immutable historical fixtures; gameplay-state assertions, deterministic diff/CI report, failure states; seven sequenced evidence-gated milestones and a buyer comparison. **First validation focus.** | Unity first; Unreal, Godot, GameMaker, RPG Maker, Construct, GDevelop and Roblox DataStore are separate research candidates. Unreal has close competition; Roblox requires a distinct authorized test-store design. |
| `GDM-002` — `business_portfolio/niches/game-development-marketplaces/projects/gdm-002-capacity-aware-npc-transport.md` | Capacity ledger, deterministic queues/routes/events, reservations, transfers, disruption/rerouting, save/restore invariants, diagnostics, 20-agent/2-vehicle bounded benchmark target; seven sequenced milestones. **Queued.** | Godot, Unity, Unreal, Roblox, GameMaker, Construct and GDevelop; 2D and 3D only where tested and commercially justified. No multiplayer or unlimited-scale promise. |
| `GDM-003` — `business_portfolio/niches/game-development-marketplaces/projects/gdm-003-native-dependency-verifier.md` | Read-only packaged-build analysis, PE import graph and engine rule packs, explicit unknowns for dynamic loads, actionable CI findings, safe parser and false-confidence tests; eight sequenced milestones. **Queued.** | A Windows x64 pipeline selected from evidence; Unity, Unreal, Godot, GameMaker, Stride, Defold and suitable desktop exports are candidates. Roblox is rejected for this native-build scope. |

The original planning text and IDs were retained. These additions are specifications, **not completed code, customer validation, pilots or released products**. All three remain `planned`, `commercial_validation: unvalidated`, `execution_authorized: false`, with CAD0 authorized spend and unknown actual revenue/profit. Candidate prices and channels remain hypotheses.

## Preservation and interface

- The prior 182-node taxonomy-oriented active tree, including the three original GDM record files, is preserved byte-for-byte in `business_portfolio/archive/2026-11-15-taxonomy-view-v1/niches/`. Its 185-file SHA-256 manifest and three-ID old/new path crosswalk are validated by the builder. This snapshot is a reversible record of the path/metadata move and does not add active projects.
- The older `business_portfolio/archive/2026-11-15-legacy/` archive remains unchanged with 139 prior project IDs and 301 files. Published product history stays published in its records; external product files remain where they were. The browser's History & Existing Work view and Portfolio Manager retain access by stable ID.
- The project browser now shows 13 ordered business niches with counts (3, then twelve zeros), three active project cards, and separate History. Portfolio Manager's Niches view shows the same order/counts; Projects, History and optional full Repository files remain. Existing per-chat selections, global availability, coordination, Computer Access, Stop and Emergency Stop code was retained.

## Verification

| Check | Result |
| --- | --- |
| Builder and current generated index/snapshot | Pass: 13 niches, 3 active records, 139 historical records, 114 source records; `--check` current. |
| Prior active-tree preservation | All **185/185** original files in the taxonomy snapshot matched the baseline Git blob hashes; none missing or changed. The older 139-record archive also passed its manifest validation. |
| Portfolio tests | 91 run: **90 passed, 1 skipped**. Includes exact niche order/counts, archive integrity and GDM ID/path checks. |
| Commercial checks | Pass for the three active records and explicit scenarios; no actual sales or spending were tested. |
| Opportunity library | Build check: 43 artifacts unchanged; **49 tests passed**. |
| Portfolio Manager regression suite | 141 run: **137 passed, 4 skipped**, using a disposable Windows controller with normal pipe/ACL access. Includes multi-chat, availability, Stop and file-explorer checks. |
| Isolated browser UI | 3 project cards, 13 ordered niche rows with 3/0 counts, 139 archived records, archived `EX-001` lookup; no page-script errors. |
| Diff integrity | `git diff --check` found no whitespace errors. |

The running shared Portfolio Manager was not restarted, so an already-open owner window may still show its prior code until the controller is restarted at a convenient time. The isolated snapshot and disposable-controller checks do not prove every future live UI interaction. No paid demand, native-engine integration, customer fixture, marketplace acceptance or product sale has been verified.

## Single next task

For **GDM-001**, obtain the owner's separate permission for developer outreach, then speak with three independent Unity teams maintaining released games. Record their real old-save failure cases, current test setup/time, gaps in native/free/paid alternatives and willingness to evaluate a bounded prototype. Without that evidence, do not start a broad multi-engine build. A local interview guide and comparison template can be drafted before any outreach.

No purchase, paid account, outreach, upload, publication or advertising occurred in this repository overhaul.
