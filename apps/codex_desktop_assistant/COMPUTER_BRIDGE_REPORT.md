# Codex Computer Bridge — verification report

## Final saved-listing verification — complete

After the owner explicitly approved read-only access, the existing editor and
Products tabs were reused. Payhip's observed owner download returns a plain-text
signed storage URL rather than ZIP bytes. The verifier now consumes that observed
exact-bucket link inside Chrome, without exporting signed URLs or credentials.
No write scope was renewed; no upload, save or listing creation was repeated.

The saved ZIP is **143072 bytes**, SHA256
`411bef96fc93f85738cbfa440b25ccd4e3a3bffa22159a47a00b0413d008ac91`,
identical to the approved local archive. ZIP integrity passed. All three saved
original PNG hashes and sizes match. Exact title, CAD19 and checked Invisible
were verified in the saved editor. The original calculator remains HIDDEN at
CAD29. Both formerly blocked stages are now completed from this read-only
evidence; no unfinished existing queue requirements remain.

Evidence: `verification/computer-bridge-official/payhip-saved-readonly.json` under
the private application data directory. This final hash check used the Windows
controller's narrow read-only verifier; earlier official-client acceptance is
listed separately below. The already-running desktop-chat discovery limitation
described below remains an integration caveat, not an unfinished queue stage.

## Implemented

Official Codex is the AI interface. Default startup now opens a minimal Windows
dashboard/tray with projects, status, results, requests, Settings and Stop. It
does not instantiate the former AI Engine. Historical conversations are archived.

An official MCP SDK stdio server connects to a singleton current-user Windows
controller through an authenticated private pipe. Existing Chrome/native host,
desktop scope, independent file permissions, native product QA and durable queue
are reused. No public endpoint, arbitrary JavaScript/shell, credential export or
model-authored permission override was added. Desktop and optional debugger input
remain off unless separately granted. The owner explicitly approved trust for
this local bridge; that trust is installed. Local security checks still apply.

Setup preserves unrelated configuration and creates backups. Existing extension
identity, sign-ins, histories, generated products and Relay are preserved.
No commit or push was made.

## Actual official-client tests

These tests used installed official Windows Codex CLI 0.165.0-alpha.1.2 and MCP,
not the legacy application's model engine.

| Check | Observed result |
| --- | --- |
| Dispatch | Actual health, status, capabilities and computer tools returned results through MCP. |
| Cold startup | Required stdio registration starts the fixed controller and reconnects Chrome without a duplicate controller. |
| Public navigation | example.org, example.com and IANA example-domains inspected in real Chrome. |
| Complex builder | Multiline editing, sidebar, color, layout, hover spacing and one unpublished draft save passed. |
| Human keyboard input | Windows input reached the human fixture while MCP edited another tab; 812 foreground samples preserved, exact human text and 44 trusted input events verified, zero approvals. |
| Files | Disposable create/read/hash-checked edit passed; deletion and protected credential reads, including alternate alias, denied. |
| Products | Five different spreadsheets generated, recalculated, rendered, packaged, listed locally and verified: 25/25 stages. |
| Downloads | All five local ZIPs independently downloaded; ZIP integrity and every customer file hash/size checked. |
| Recovery | Same completed project and exactly five local listings survived controller restart and a new official client connection. |
| Partial recovery | A paused 3-complete/1-pending project survived restart, reported Waiting for Codex after resume, and completed its pending reasoning job. Original generation/QA/package attempts stayed at one each; package SHA was unchanged. |
| Sensitive actions | Actual MCP attempts on simulated Publish and Pay now produced genuine approvals, were denied, and receiver counters stayed zero. |
| Emergency Stop | Real MCP typing was denied after Stop; unchanged About text and zero save/publish/payment counters independently returned. The known test Stop was restored locally afterward. |
| Payhip read-only | Authorized Store Builder/custom sections inspected; existing hidden calculator located. |
| Tab reuse | Both requests reused the same existing Products tab, reused=true, created=false, foreground_changed=false. Tab count stayed 12 before and 12 after. |

Five-product project: `0d582a867b6b4ae485bac0626057367f`. Recovered local store:
`http://127.0.0.1:38010`, exactly five listings at the approved test prices.
Private evidence: `%LOCALAPPDATA%\CodexDesktopAssistant\verification\computer-bridge-official`.
Independent-download and background JSON files contain supplementary host
measurements, not model-generated assertions. Earlier failed setup attempts are
not counted as passes. Background screenshots remain unavailable; the bridge
now checks that before requesting screenshot consent.

## Specifically approved Payhip write

Exactly one **Inventory Reorder Planner - Private Integration Test** listing
was saved **HIDDEN at CAD19.00**. Reopened fields show full title and checked
**Invisible**. The original Cleaning Business Pricing & Profit Calculator
remains **HIDDEN at CAD29.00**.

The guard initially blocked an unapproved storage destination. After the owner's
exact-bucket approval, one controlled archive retry was consumed in the original
unsaved editor. All four files obtained completed receipts. The site's initial
Save warning rejected submission locally; its own upload flag later cleared
naturally. A bounded continuation reconciled receipts and saved once. Website
validation/progress flags were never overridden. No public/unlisted publication,
purchase, payment or account change occurred. No further upload/save is allowed.

Saved receipts: delivery.zip 143072 bytes, Cover.png 22445, Preview-1.png 45528,
Preview-2.png 54860. Public image originals were independently downloaded; SHA256
values match the approved package:

- Cover: `87018545de312215771e3770f62be625acda042daabcfddcc4b021edd126f4a5`
- Preview-1: `3b2665751fd16125271f90be916439984f7bacf599933aa5e0bf3519d05f5b90`
- Preview-2: `415e52a614d2f8e13f5514152947e33426f0723afa0015280ee8b4c0e9502856`

Original ZIP SHA256:
`411bef96fc93f85738cbfa440b25ccd4e3a3bffa22159a47a00b0413d008ac91`.
Saved filename/size alone was insufficient proof. The final read-only verification
above now establishes the exact saved ZIP hash and integrity without repeated
creation or transfers.

### Prior read-only audit, before the owner's new read-only grant

The controller and Chrome are connected and Stop is no longer latched, but every
persisted Payhip test scope is revoked. `PayhipBrowserAdapter.guard()` requires
an unrevoked, unexpired scope even for saved-asset verification. `asset_digest`
is an internal adapter operation, not a separately exposed read-only MCP tool.
Consequently the ZIP hash/integrity check cannot currently proceed through the
supported verifier without another authorization. No permission was requested
or reapplied, no stage retried, and no tab opened during this audit.

At that audit, the only unfinished existing queue requirements were `inventory-test:prepare-hidden`
(blocked on saved ZIP verification) and its dependent `inventory-test:verify-hidden`
(blocked prerequisite). Generation, native QA and packaging are complete. The
queue contained no other unfinished non-cancelled project. That audit did not
establish a saved ZIP hash or change the earlier confirmed listing state.

## Regression checks

- Final full assistant/bridge suite: **200 passed**.
- Three additional read-only reconciliation regressions passed: denied approval
  prevents download, hash mismatch cannot complete work or renew write scope,
  and a missing existing tab cannot create another.
- Subsequent focused Payhip tests: **13 passed**; bridge/security/dependency tests:
  **11 passed**.
- Existing Codex Relay: **81 passed**.
- Worker VM tests passed: exact-URL/concurrent reuse, unchanged human tabs,
  manual takeover, restricted sites, creation provenance, close races and bounded
  owner-download verification.
- Earlier isolated real Chrome DOM integration: **9 passed**, including
  custom/rich-text/shadow/frame controls and actual multipart transfer.
- Real Windows pipe and Qt dashboard tests are included in the Python suite.
  The sample dashboard image is explicitly labelled representative data.

## Limits and starting use

Actual dispatch was proved through the official CLI. This already-running
desktop chat has not acquired the newly registered namespace. Open a fresh
official Codex session after configuration/reload; registration alone does not
prove a call in this particular chat. Ask: **Check my computer bridge status**.
The dashboard needs no second AI chat.

The official CLI can terminate descendants it started when the CLI exits. A
controller started separately through Start_Computer_Bridge.cmd remains
available. Minimized UI supports work; an ended AI session does not secretly
continue reasoning. Pending reasoning waits for official Codex.

Exact-URL reuse preserves live documents, unsaved work and foreground state. It
does not make existing tabs disposable or bypass manual control. Only the exact
requested URL within granted browser/site scope is reused; unrelated personal
tabs are not inspected. Genuine login, MFA/CAPTCHA, new Chrome permissions and
consequential actions outside an approved scope still require human input.

See COMPUTER_BRIDGE.md for setup, recovery and uninstall instructions.

## References

- [Codex MCP](https://developers.openai.com/codex/mcp)
- [Codex configuration](https://developers.openai.com/codex/config-reference)
- [MCP stdio](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [Chrome Native Messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging)
- [Payhip digital products](https://help.payhip.com/article/59-adding-a-digital-product)
