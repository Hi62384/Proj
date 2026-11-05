**Historical audit snapshot:** the candidate-only status below predates the separately authorized exact 29-file publication. See [publication result](REVIEWED_29_PUBLICATION_RESULT.md) for current GitHub state; the audit findings and earlier rejection remain preserved.

# Computer Bridge candidate audit — local review only

The exact three approved Cleaning documentation files are published on GitHub main in [b831f7f](https://github.com/Hi62384/Proj/commit/b831f7fe24c98d8c6f6862ab11bb731575df5d8a). Fresh remote main and all three returned file contents matched the reviewed payload. No Bridge code, root README, output reports, release packages or private evidence were published.

The 19 Bridge candidates below remain unstaged and uncommitted. All match the independent pre-test manifest byte for byte. Original checkout HEAD and index entries are unchanged. The root checkout still points to the earlier commit; remote documentation publication was isolated to preserve its unrelated dirty work.

## Tests executed

| Suite | Passed |
|---|---:|
| Routine policy | 10 |
| Offscreen Qt dashboard | 9 |
| Computer Bridge policy/metadata | 11 |
| Chrome control | 29 |
| Action classification | 26 |
| File/desktop policy | 25 |
| Total Python | 110 |

Both standalone Node browser regression scripts also passed: `chrome_input_widgets.test.mjs` and `chrome_worker_tabs.test.mjs`. They test bounded widgets/gallery dragging, Quill multiline entry, exact-URL/concurrent reuse, manual controls, restrictions, provenance and grant/regrant/revoke restoration. These are mocked browser tests, not a new live Chrome or Windows capture acceptance test. Qt used `QT_QPA_PLATFORM=offscreen`, with a dummy Runtime. File tests used disposable temporary files. No store, account, payment or capture operation was performed.

The default Python lacked project dependencies; the existing `.venv/Scripts/python.exe` passed without installation. Node's parallel test runner hit child-process EPERM; the same standalone test scripts passed when run directly. These setup errors are distinguished from the successful project-environment results.

## Security and approval review

The local owner toggle defaults off. When enabled it narrowly auto-allows default project Read/list requests, authorized-origin exact-tab reuse/screenshots, and structured saves to an existing Invisible Payhip product. Explicit file Ask/Deny rules and separate Write/Create/Delete remain in force. Uploads, public/unlisted product saves, publication, payments/purchases, credentials/security, destruction, unknown requests, Stop/manual control and sensitive-screen rules retain their checks. Tests exercise those boundaries, ordinary multiline editing and actual form/publication classification.

Added local attachment import requires the source Read policy and expected hash; uploaded content stays separately reviewed. Post-approval inspection reacquires an observation and compares the reviewed control and full context before dispatch. The storage exception permits only the exact Payhip bucket in the reviewed upload scope. No new arbitrary shell/JavaScript execution interface was found in these changes.

This is a targeted diff review and regression run, not a complete security certification. No high-confidence secret or private buyer-receipt URL was found in the 19 text candidates. The embedded `user:password` URL in `test_routine_policy.py:41` is a deliberate negative fixture, not real credentials. No conflict markers were found. Binaries, images, private evidence and unrelated pending files are not cleared for publication.

## Remaining gaps

1. `chrome_extension/worker.js` keeps `originalAutoDiscardable` in memory. Normal revocation restores the original value and is tested; a worker/extension crash or reload loses that restoration record. Durable restoration is unfinished. Long-duration Chrome stability is unverified.
2. Attachment restoration is hash-gated in source, but these targeted tests do not establish live controller-restart acceptance for the new restore path.
3. Show Browser closed-tab recovery, authorization failures and persistent errors pass mocked Qt tests. Foreground behavior and the bundled OpenAI Windows helper/capture path were not live-tested here. The external helper is outside this repository. No screen capture was used.
4. A later review should consider whether comparing every returned control field after approval causes harmless animation/layout changes to reject actions. Current behavior fails closed; no unsafe dispatch or such live failure was observed in this audit.

No candidate source was fixed during the read-only audit.

## Candidate manifest

Paths are relative to `apps/codex_desktop_assistant/`. Full SHA-256 and baseline Git blob identifiers are in `BRIDGE_CANDIDATE_AUDIT.json`.

| Path | Bytes | SHA-256 prefix |
|---|---:|---|
| `COMPUTER_BRIDGE.md` | 8671 | `02d089ed0f7ecab6…` |
| `assistant/action_policy.py` | 8968 | `f3e93100bb54b00d…` |
| `assistant/attachments.py` | 5228 | `c07b070de31f1226…` |
| `assistant/chrome_control.py` | 22770 | `06a6b2dcdae596fb…` |
| `assistant/files.py` | 11088 | `9beabc6741aa35a8…` |
| `assistant/tools.py` | 24783 | `2e8b4dd3ba45e123…` |
| `bridge/dashboard.py` | 15440 | `320da9ac537a531d…` |
| `bridge/runtime.py` | 19756 | `450577a0f7edd947…` |
| `chrome_extension/content.js` | 30645 | `cc939e5e69315c0b…` |
| `chrome_extension/worker.js` | 35941 | `1caecd5c55b39e51…` |
| `tests/chrome_input_widgets.test.mjs` | 7678 | `ec0cc05ba529f6f4…` |
| `tests/chrome_worker_tabs.test.mjs` | 9538 | `1dced80105f08048…` |
| `tests/test_action_policy.py` | 11114 | `acd823e8d88536b0…` |
| `tests/test_bridge_dashboard.py` | 7195 | `319a473d05fb540e…` |
| `tests/test_chrome_control.py` | 15908 | `ce1778704eacb6d9…` |
| `tests/test_computer_bridge.py` | 7329 | `4616fb486fd729fb…` |
| `tests/test_overhaul.py` | 12712 | `9485736fc70910a0…` |
| `bridge/routine_policy.py` | 3480 | `b8eb51312fe93680…` |
| `tests/test_routine_policy.py` | 6724 | `1be6123ff3bd59f8…` |

## Other proposals held locally

The coordinator prepared a separate review-only four-file metadata proposal: root `README.md`, `.gitignore`, historical `outputs/payhip-launch-2026-10-30/website-checks.json`, and `outputs/payhip-launch-2026-10-30/CURRENT_LINKS.json`. It is outside the approved three-file publication and was neither applied nor published here. The README needs its exact CURRENT_LINKS dependency included in a later separately reviewed scope, or its dependency removed. The snapshot proposal preserves dated values and changes only the superseding pointer to the public Cleaning README; it does not rewrite old prices/payment observations. The ignore proposal covers the isolated `.tmp/` checkout and nested disposable review profiles; no ignore change was applied. Ignore rules alone do not clear already tracked or sensitive files.

Do not add all pending files. Keep generated ZIP/XLSX, images, owner/account/tax evidence, application profiles, isolated clone and unrelated demo work held. No credential probes, sign-in, account changes, charges or external messages occurred.

## Broad-publication rejection (verbatim)

This action was rejected due to unacceptable risk. Reason: The prompt could lead to broad public publication of many pending files, including potentially sensitive or unfinished artifacts; although the user requested pushing GitHub changes, exact contents are not yet identified, so this is not sufficiently narrow for an authorized high-risk push. Do not bypass this rejection through a workaround or indirect execution.
