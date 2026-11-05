# Local integration and live explorer — November 5, 2026

**Ready:** double-click **Open_Project_Browser.cmd** for the simple two-panel project explorer. Its read-only Python standard-library service is available at http://127.0.0.1:22841. Canonical Markdown stays authoritative; live changes appear within a few seconds without rebuilding or reloading. Current portfolio spending authorization remains CAD0. No cloud backend, account, subscription, AI engine or scheduler was added.

**Acceptance limitation:** direct automated file:// opening was denied by the browser URL policy (HTTP/HTTPS only). It was not bypassed. Static HTML was generated and structurally/syntax checked and clearly labels itself a snapshot, but direct-file opening remains an optional owner check. SYS-001 retains that exact blocker rather than claiming every original acceptance criterion passed. No screenshot/native capture was used; live browser DOM and responsive geometry were inspected.

## Implemented

One search field, recursive collapsible project folders, clear names/plain-language states and a readable project pane replace all dashboard statistics, filter dropdowns and report controls. Saved checklists provide completed/current/remaining work. No percentage or financial outcome was invented. Full instructions and the complete original record remain available; research, economics and history are lower collapsible sections. Published products remain distinct from verified paid demand.

`tools/serve_browser.py` debounces file scans, keeps the last valid view during incomplete/invalid writes and uses same-origin polling. Stable selection, search, expanded folders and reasonable scroll position survive updates; stable IDs survive rename/move. The actual Windows CMD launcher starts/reuses the loopback service.

Files & Results labels public source/planning records, explicitly declared public text results, product links and missing/private assets separately. A source guide is not presented as a finished application. `public_results` can declare reviewed text files in `results/<same ID>/`; newly created files appear automatically. Traversal, cross-project paths, private folders, symlinks/reparse points, hard-linked files, unsupported binary releases and recognizable credentials/private buyer URLs are refused. Host/Origin checks prevent cross-origin reads. There is no arbitrary filesystem, OS folder-open, command or write endpoint. Secret-pattern screening is a safeguard, not privacy certification.

## Preserved state and reconciliation

All 139 stable IDs, 81 niche nodes and 108 sources remain, including all 133 original IDs and six additions. No earlier tracked local portfolio existed, and all 345 incoming manifest files matched before edits. Original package/checksum/QA records remain historical snapshot evidence; LOCAL_MANIFEST.json describes the edited local files separately. The extracted package and affected root documents are backed up in the existing ignored `.tmp` area outside the public package; ignored storage is not encryption.

README navigation and a scoped AGENTS checkpoint section were added only in the working tree. HEAD, MERGE_HEAD, the raw Git index, its four staged files and unrelated work were preserved. No commit, push, merge completion/abort, reset, clean or stash occurred. Existing product/research/Bridge/legacy/factory/VaultDesk files and runtime/financial state were unchanged. Completed checklist history and actual financial fields were preserved; only SYS-001 was advanced for observed local work.

EX-001/EX-002 gained dated local reconciliation. Inventory's imported v1.0.1-final claim is explicitly superseded by saved transition evidence and the matching local v1.0.2 archive: 206,757 bytes, SHA-256 0ebab37edde6db94b5ea80bc761dc82133ec6c3637a72e4a8489ac3dda0f23c0. Cleaning's existing v1.0.1 archive matched its saved 61,130-byte/hash evidence. Neither archive was changed, downloaded again or uploaded; private locations/receipt URLs/customer bytes are not embedded.

The source register retains imported access limits: 41 revision sources comprise 9 full-page, 31 indexed-primary and 1 connector read; 67 are carried forward. These are not new research reads or verified live eligible buyers.

## Actual verification

- **Initial integration run: 68 tests, 67 passed, 1 skipped, zero failures/errors.** The subsequent launcher-fix run is recorded below. Real symlink creation lacked Windows privileges; mocked linked-input rejection, real hard-link rejection and the other privacy tests passed. Coverage includes 24-level niches, IDs/references/cycles, malformed metadata, safe text rendering, budget arithmetic and real loopback/watcher lifecycle tests using temporary fictional records.
- Build, stale-output and commercial checks passed for 139 records. Python tools parse; browser JavaScript passes Node syntax checking. Internal links, ID/source coverage, path lengths and credential/private-link patterns are validated separately.
- Live browser checks verified all records, one search/no dropdowns, nested folders, complete instructions, empty results, opening an actual source guide and published-versus-paid/private-asset distinctions. Synthetic creation, instruction/next-step edits, checkbox completion/active status, rename, move/new fourth-level niche, deletion and malformed-write recovery appeared without browser reload. Selection/search/expanded folders remained. A newly created declared public text result appeared and opened automatically. Fixtures were removed.
- At the requested 390px viewport, document width stayed within viewport width and the layout stacked. The temporary viewport override was reset. No browser JavaScript errors were recorded. This is DOM/geometry acceptance, not screenshot visual certification.
- The actual Windows launcher was executed (same launch path as double-click; no physical mouse gesture claimed). Repeating it twice retained one listening service/PID. No dependencies were installed, and no acquisition, charge, order, product/account change, external publication or schedule was created.

## Operational and file-access limits

The service stops at sign-out/restart; the next launcher run starts it again. The corrected launcher reuses the service and requests the page on every intentional run, including after its tab is closed. The default browser may create a new tab; reliable tab detection is unavailable. The earlier suppression of duplicate tabs caused the reopen regression and has been removed. A developer can run the service in a console and stop it with Ctrl+C. No Windows startup task was installed.

Only curated public guides, canonical records and declared non-sensitive text results are exposed. Paid ZIP/XLSX packages, private videos, arbitrary folders, installers and binary assets remain withheld/unverified. A broader existing-asset registry needs a specific safe review; prose paths are not sharing permission. Existing releases and private queues remain intact.

## Next planning action

If selected by the owner, review AWA-005's saved scope and fictional skill-proof specification. That is a planning recommendation from the supplied revision, not a newly verified job, authorization to build client production, send messages or spend. Preserve the published products and reuse existing assets.


## Launcher reopen correction — November 5, 2026

The original existing-service branch returned before requesting the browser. Its deliberate tab-suppression rule caused a CMD window to flash and exit without reopening a closed page. `serve_browser.py --open` now requests the page in both normal reuse and a concurrent bind-race reuse. The new visible `tools/launch_browser.py` checks/reuses the service, logs hidden child startup to `.local/browser-startup.log`, and requests the default browser on every intentional launcher run. The CMD file pauses with a useful error on failure; it works independently of the caller's working directory. No tab-presence detection is assumed, so a default browser may open another tab. One service remains bound to the local port.

The actual updated CMD was launched via normal Windows file association from C:/Windows: it exited with status 0 and retained the same single listening PID. Eight new launcher regression tests passed, including a real CMD failure in a folder with spaces from an unrelated working directory, a visible error/pause path, default-browser failure, existing-service reuse, and the bind-race --open branch. The final full-suite result is 78 tests run: 77 passed, one Windows symlink-creation test skipped, zero failures/errors. The occupied-port test also exposed Windows address reuse; new service starts now request exclusive binding. A real synthetic cold start passed, and a deliberately occupied synthetic port produced the logged startup error. Only synthetic children were stopped; the existing live service was not restarted. Existing canonical records, progress, releases, runtime state, raw Git index and pending merge were preserved.

Normal-browser inspection could not be completed safely: automatic approval review rejected a full accessibility-tree read because unrelated private chats were in that window. That read was not retried or bypassed. The owner then confirmed “yah” when asked whether closing the portfolio tab and double-clicking the updated launcher reopens the live page. This final reopening outcome is owner-confirmed; exit status 0 and a browser-open request alone were not treated as visual proof. No screen capture or denied file:// operation was attempted. Source changes are local only; no commit, push, account/product change or charge occurred.
