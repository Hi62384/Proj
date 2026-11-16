# Preserved 182-node research taxonomy view

This is the complete prior active `business_portfolio/niches/` tree: 182 niche metadata files and the three original GDM planning records, **185 files total**. `FILE_MANIFEST.json` records each original file's byte count and SHA-256. `PROJECT_CROSSWALK.json` maps GDM-001/002/003 from their old nested paths to the new primary Game Development Marketplaces paths, with their original hashes, statuses and niche identity. The current records retain their IDs and content history; their niche path was changed and implementation specifications were appended. The archive is a rollback/evidence snapshot, not another active project database.

The separate `opportunity_library/data/taxonomy.json` remains the canonical 36-category/144-subcategory research taxonomy. It is not part of the 13 business niche menu. The older 139-project archive at `../2026-11-15-legacy/` is unchanged and remains available in History & Existing Work.

`business_portfolio/tools/build_browser.py` validates this snapshot's manifest and crosswalk on every rebuild. To recover a prior file, look up its original path here, compare its hash with the manifest and restore a copy in a separate checkout after reviewing current records and private checkpoints. Never replay an external action from a historical checklist.
