# Preserved portfolio history — 2026-11-15

This archive contains the **original 301 files** from the previous `business_portfolio/niches/` tree, including all **139 project records**, old niche metadata and README files. The migration moved the tree within the same checkout; no record was rewritten to change its status, ID, evidence, progress or external-effect warnings.

- `FILE_MANIFEST.json`: former `niches/`-relative path, exact byte length and SHA-256 for each original file.
- `PROJECT_CROSSWALK.json`: stable project ID, former path, archived path, SHA-256, prior work/commercial status, source IDs and links.
- `niches/`: the original planning tree, byte-for-byte. Existing application and product files elsewhere in the repository were not moved.

`business_portfolio/tools/build_browser.py` checks the archive manifest and crosswalk before including these records in History. Archive records can be opened through Portfolio Manager's **History & Existing Work** view. Keep this folder unchanged for a reliable recovery point.

## Restore a record for active work

1. Look up its stable ID in the crosswalk. Read the complete archived record and latest authorized private checkpoint; verify current external state separately.
2. Choose an existing active niche, or create one with a unique stable niche ID. Check that the project ID is absent from the active tree.
3. **Copy** the record into that niche's `projects/` folder and update only its `niche_id` and `niche_path` after reviewing its status and evidence. Keep the archived original and crosswalk intact. Do not replay any upload, publication, order or purchase.
4. Record the archived record's SHA-256 in the active frontmatter field `restored_from_archive_sha256`, then rebuild and check the index and run the portfolio tests. The builder accepts the same ID in active and history only when that hash matches the crosswalk. History stays preserved.

To restore the *entire previous tree* in a separate checkout, copy `niches/` from this archive to a clean `business_portfolio/niches/` after moving that checkout's current active tree aside. Compare every file against the manifest. This is a filesystem recovery procedure, not a request to reverse today's active view.
