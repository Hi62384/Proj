# Business Portfolio: 12-category restructuring

## Outcome

The active portfolio now has 12 ordered categories and 13 preserved niches. Only Digital Products → Game Development Marketplaces contains active project records: GDM-001, GDM-002 and GDM-003. All three remain planned and commercially unvalidated. The other 12 niches have no active project records. No external commercial action or spending was performed.

```text
business_portfolio/niches/
  digital-products/
    game-development-marketplaces/projects/ (GDM-001, GDM-002, GDM-003)
  software/
    advanced-online-products-and-software/
    platform-specific-apps-and-extensions/
  apis/usage-based-apis/
  automation/marketplace-hosted-automations/
  digital-content/online-content-and-media/
  data-and-intelligence/specialized-data-and-intelligence-services/
  services/ai-assisted-freelancing/
  gaming/online-games-and-virtual-economies/
  advertising/advertising-supported-utility-websites/
  affiliate-marketing/affiliate-and-referral-businesses/
  lead-generation/
  licensing-and-royalties/
```

Top-level `priority` values 1–12 follow this order. Lead Generation and Licensing & Royalties retain their original niche IDs while serving as categories without redundant children. The other 11 niche IDs are unchanged; ten new parent category IDs use `N-category-*`. The category tree has 23 metadata nodes in total.

## Preservation and navigation

The three canonical files are under `business_portfolio/niches/digital-products/game-development-marketplaces/projects/`. A comparison with the pre-move Git version found all three project bodies and all existing metadata fields unchanged except `niche_path`; the existing 13 niche IDs, titles and descriptions were also preserved. Each record now explicitly labels supported platforms as unverified and lists its proposed platforms based on the existing plan. No product was built or launched.

The 139 older historical project records and their manifest remain unchanged. The 185-file pre-overhaul taxonomy snapshot remains intact; only its path crosswalk was advanced to point to the current canonical GDM paths. The 36-category/144-subcategory opportunity library remains separate from the active menu. `PROJECT_INDEX.json` and `PROJECT_BROWSER.html` were regenerated from canonical records.

The browser's Projects and Niches sections now show Category → Niche → Project, including faded empty niches with zero projects. Portfolio Manager shows the same hierarchy, preserves separate chat selections, and redirects a saved selection from an old active niche path to the new path when that chat reconnects. History labels distinguish earlier projects from the previous niche layout. The existing Computer Bridge, permissions, Stop and Emergency Stop code was retained.

## Verification

| Check | Result |
| --- | --- |
| Category/niche/record integrity | 12 categories, 13 original niches, 3 GDM records, unique IDs and valid parents/paths verified by builder and tests |
| Archived history and research | 139 older records, 185-file taxonomy snapshot and independent 36/144 research taxonomy verified |
| Browser generation | Build and `--check` passed; JavaScript syntax check passed |
| Portfolio tests | 91 run, 90 passed, 1 symlink test skipped because symlinks were unavailable |
| Commercial checks | Passed for 3 records; no actual sales or external permissions were verified |
| Portfolio Manager focused UI tests | 5 passed using the project's PySide6 environment |
| Saved selection move test | Passed; another chat's selection remained unchanged |
| Disposable multi-chat MCP integration | Passed outside the restricted Windows test sandbox |
| Full Portfolio Manager suite | 143 run, 9 errors and 4 skips in the restricted Windows test sandbox; errors were named-pipe access/timeout and ACL-permission failures, not assertion failures in the category or selection tests |

## Remaining limits

The shared, already-running Portfolio Manager controller must restart before its open windows load the new code. It was not restarted during this change, to avoid interrupting other chats. A live screenshot of the new tree and a browser rendering check remain unverified; headless Chrome did not start in this restricted test environment. No real external checkout, publication, upload, outreach or spend was attempted.
