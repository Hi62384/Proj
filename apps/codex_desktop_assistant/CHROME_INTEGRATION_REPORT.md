# Chrome integration verification — 2026-10-29

Status: implemented and installed; acceptance remains incomplete at a real Chrome
site-permission boundary. No commit or push was made.

## Implemented and installed

- Manifest V3 extension with stable ID `kcfbggelcigbhjgacelpabajednbcfgd` and a
  registered current-user Native Messaging host. Real Chrome connected through
  that host to the running Desktop Assistant; no profile/session export is used.
- Authenticated local user-only pipe, strict framed messages, bounded operations,
  session IDs, deadlines, cancellation and version checks. Webpages have no native
  command channel; the extension exposes no shell or arbitrary filesystem API.
- Existing Chrome mode reuses the saved Codex engine, broker, chat approvals,
  notifications and Stop handling. Desktop and dedicated browser modes remain.
- Explicit tab/frame authority, per-chat attachment, optional host permissions,
  bounded DOM editing, human-edit conflict checks and Manual Control.
- Background tab creation with no selected tab, automatic attachment when Chrome
  already permits the destination site, and clean attached-tab closure without a
  blanket review. Possible editor/form contents require review and are rechecked
  before closing. The model cannot supply its own close proof.
- Actual file bytes for reviewed attachment uploads; same-site, human Save As
  downloads. Active-tab screenshot consent is separate from DOM permission.
- Transactional tab grants require both the content script and assistant to
  acknowledge authorization. Failed grants remain unauthorized. Chrome network
  guard rules use literal filters, avoiding the earlier compiled-regex limit.
- Refresh, disconnect and Stop invalidate session/tab authority rather than replay
  uncertain actions. A newly opened unauthorized tab is handed to the human without
  leaving automation network restrictions behind.

## Verification evidence

| Check | Result and limits |
| --- | --- |
| Assistant regressions | 138 tests passed with the normal Windows user token, including native pipe/host handshake and real Qt mode/attachment/Stop checks. A restricted-token run failed the private-channel authentication test; the normal-user run passed. |
| Relay regressions | 81 tests passed. |
| Extension syntax | Worker and content JavaScript passed Node syntax checks. |
| Installed Chrome DOM/controller acceptance | Eight checks passed: bounded observations/redaction; multiline/rich text/open shadow roots; select/checkbox/dynamic button; same-origin frame; trusted input in a different active tab; same-tab trusted input invalidation; manual hold; actual FileList/multipart bytes verified by a local receiver. This used a separate disposable Chrome test context and fixed controller adapter, not the user's installed extension/native-host/saved-chat path. |
| Actual saved-chat → broker → native host → installed extension → normal Chrome | Real Codex completed a saved-thread turn and the independent synthetic server verified final multiline notes, rich text, select/checkbox, shadow notes and dynamic expansion. No publication, purchase or form submission occurred. The full test did **not** pass: its Windows foreground assertion failed. |
| Latest actual saved-chat tab creation | A real Codex turn created one background tab, ID 5198727, at the disposable `/clean-bc35c7162be5` path. The independent local server recorded the navigation and the broker logged completed `chrome.open_tab`. The model's subsequent tab list reported that the new tab stayed inactive and both previously active tabs remained selected. All original conversation IDs remained present. |
| Automatic control/clean close of that new tab | **Blocked:** Chrome currently has no site grant for the disposable host after the development refresh. The model correctly left the new tab open, did not inspect it and did not claim closure. |
| Physical foreground during latest real creation test | **Not passed:** the test sampled a foreground change. It did not identify its cause. A model report of unchanged active Chrome tabs does not prove unchanged Windows foreground. This still needs a controlled live check after genuine setup/approval phases. |
| Recovery/manual/conflict through the entire installed path | Native transport/session tests and separate actual-Chrome controller checks passed; the complete installed-extension restart/disconnect/conflict sequence is still pending. No successful end-to-end claim is made. |
| Installed-extension upload/download acceptance | The separate actual Chrome controller proved multipart bytes, and host/control regressions cover attachment boundaries. The full saved-chat/installed-extension upload and human Save As sequence remains pending. |
| Payhip | Not inspected in this queue. No current exact Payhip tab grant exists. Read-only acceptance requires the owner to authorize the signed-in Store Builder tab; unpublished draft changes require separate explicit permission afterward. |
| Historical interactive desktop/dedicated-browser acceptance scripts | Existing unit/regression suites passed. Every historical interactive launcher/UI/desktop acceptance script was not rerun as part of this queue; those are not represented as new Chrome live acceptance. |

Local evidence under `%LOCALAPPDATA%\CodexDesktopAssistant\verification`:

- `chrome-dom-20261029-143855\results.json`: eight actual Chrome controller checks.
- `chrome-live-20261029-144750\app-results.json`: installed-path DOM edits, then
  failed foreground assertion.
- `chrome-live-20261029-144750\tab-live-results.json`: latest actual creation,
  independent receiver proof, foreground result and exact permission blocker.
- `chrome-live-20261029-144750\server-results.json`: disposable receiver state.

These are local verification records, not proof of compatibility with every site.
Test scripts create separate verification chats and retain existing history. They
never inspect unrelated personal tabs, autoapprove website scope, or use a browser
debugging port on the user's normal Chrome profile.

## Required owner action and remaining queue

On the newly created disposable tab at
`http://127.0.0.1:22704/clean-bc35c7162be5`, open the extension and choose **Allow
Site Access**, approving Chrome's prompt. This site permission is what lets new
tabs on the test host become controllable automatically; **Allow Codex to Control
This Tab** alone does not grant new-tab access. The second disposable host,
`http://localhost:22705/human`, needs its own grant for multi-site/human-input tests.
No personal or Payhip site permission is needed for these synthetic checks.

Once those grants exist, resume the real saved-chat tests for automatic control,
clean close, foreground/input preservation, same-tab conflict, revocation/recovery,
and reviewed synthetic upload/download behavior. The localhost fixture daemon has
a bounded one-hour lifetime and can be restarted by the test tools at the same
origins without changing browser identity. For Payhip, request exact-tab read-only
scope only after synthetic acceptance passes.

## Supported limits

No hidden background screenshots, debugger permission, arbitrary JavaScript,
closed-shadow-root access, browser-profile copying or security-control bypass is
implemented. Opaque scripted commits may require human control. Cross-site frames
need their own grant. File downloads use human Save As rather than automatic file
placement. Selecting a Chrome window discovers its tabs; it does not grant blanket
access to all personal tabs or unrelated sites in that window. Clean-close checks
are conservative: populated editors/forms and frames can require review even when
the website does not expose a reliable dirty flag.

Installation, troubleshooting, updating, revocation and removal are documented in
[CHROME_SETUP.md](CHROME_SETUP.md). Completion should not be reported until the
remaining live checks pass or their exact human/website blockers are resolved.
