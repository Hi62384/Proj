# Routine editing approval repair — October 28, 2026

Implemented directly in the existing application. No commit or push was made, no dependencies were added, and the Relay source/authentication configuration was not changed.

## Cause

`tools.py` replaced the label of every multiline native typing action with `Submit multiline input`, then matched the word `submit` in a broad sensitive-label regular expression. It also labeled every Enter key as a submission and applied unanchored label/URL matching. Browser routine actions required label pre-approval even when the owner had already authorized the origin/session.

This confused document contents, control names and navigation with activation of a consequential action.

## Change

- Added `action_policy.py`, a shared host-context classifier. Ordinary text entry, selections, scrolling, editing/navigation and semantic routine controls run within the existing authorized scope without a label allowlist or repeated approval.
- Removed multiline-to-submit relabeling entirely. Newlines and words such as publish, purchase or password in a verified plain editor are document data. Verified Notepad process identity comes from Windows, not a model hint/window title.
- Distinguished Enter in an editor from activating a button/default form. An actual Save button, filename dialog, unknown default activation or submit control is not exempt merely because its process is Notepad. Typing into a button cannot bypass activation review.
- Added browser target metadata: actual element/tag/type, editable state, form method/action, submit controls, Enter-to-send indication and credential-form context. A misleading ARIA edit role cannot disguise an actual submit button. Multiline fill is text entry; a POST form submit is a separate action.
- Matched bounded action verbs on actual activating controls rather than arbitrary label fragments. Publisher, Submitter notes, Display and Purchase history do not imply publication/submission/purchase. Actual Buy now, Publish product, Send, Delete, credential/security changes and similar actions still require exact review.
- Preserved an HTTP backstop: unreviewed navigation submissions, DELETE, explicit action query parameters and known consequential request endpoints are blocked before forwarding. Routine draft/edit requests remain scoped to the brief authorized action; observation does not acquire mutation permission. No blocked request is automatically replayed.
- Kept authentication/password fields and credential-form activation as human steps even if an action is approved. File uploads remain reviewed. Direct file Read/Write/Create/Delete policy is unchanged; Entire Monitor grants no file-tool permission.
- Approval cards now display why review is required and the website/application target prominently, with the reason retained in chat history. The obsolete routine-label editor was replaced by an explanation of session-scope authorization; existing saved label data was not deleted.
- Retained exact origin/window/monitor authorization, fresh observations, human-input coordination, Stop/emergency cancellation, protected application/credential locations and old saved-thread compatibility.

## Verification

**98 assistant tests and 81 original Relay tests passed (179 total).** New regression coverage includes multiline Notepad text, repeated edits, routine labels/buttons, browser multiline fill, GET search versus POST form submission, Enter-to-send, purchases, publication, credential/destructive controls, button-typing/file-dialog bypass attempts, model-supplied authority hints and independent file denies. Compilation and whitespace checks passed.

Real Windows/Codex acceptance used actual Windows Notepad, not the synthetic Qt editor:

| Workflow | Measured result |
|---|---|
| Entire Monitor grant, no individual-window grants, empty routine-label list | Passed |
| Actual Codex replaces a synthetic Notepad document with three lines | Passed with **zero approval requests** |
| Actual Codex replaces those lines again and verifies the edited text | Passed with **zero approval requests** |
| Plain editor content contains password/command/publish/purchase words | Passed; treated as data |
| Existing synthetic disk file remains unchanged while editing the unsaved document | Passed; no save/file-tool permission granted |
| Real Chromium multiline textarea fill and Publisher button | Passed without approval |
| Real local POST form Continue button | Required an explained owner approval; exactly one submission recorded |
| Denied form submit | No second request forwarded |
| Real local Buy now / Publish product controls | Each required the appropriate payment/publication review |
| Innocuous-looking button dispatches a hidden publish request | Blocked before forwarding; publication count unchanged |

All purchase/publication tests used a disposable localhost counter. No real purchase, account, public listing or message was touched. The Notepad document was uniquely named and synthetic, and its unsaved test edits were discarded at cleanup.

Private evidence under `%LOCALAPPDATA%\CodexDesktopAssistant\verification\`:

- `routine-editing-20261028-182819/results.json`: complete actual Notepad/Codex and Chromium approval acceptance.
- `routine-editing-20261028-183151/results.json`: repeated complete acceptance, including harmless security/action words in document text.
- `routine-editing-20261028-184723/results.json`: final Notepad-only confirmation on the updated controller, again with zero approvals and an empty routine-label list.
- `routine-owner-launch-20261028-184924/results.json`: the updated native app opened and connected with restricted-runtime checks passing. Hash comparisons preserved both existing conversations, all 54 existing messages and saved thread IDs. Desktop access starts off as before; re-enable the intended session scope after restart.

The broader original integration was also rerun. One partial native-browser run stopped safely when its field changed during input rather than overwriting the changed value. A separate startup attempt encountered the existing intermittent WSL resource error before inference. The existing Ubuntu runtime subsequently started without any service restart or WSL settings change; the final complete rerun passed. Evidence:

- `20261028-184126/results.json`: original full real integration passed, including native browser editing, steering, takeover/resume and emergency stop.
- `controllers-20261028-184431/results.json`: native controls, actual browser upload bytes, redirect isolation, revocation and global shortcut passed.
- `ui-20261028-184435/results.json`: native UI controls, preferences save/light theme, a real Codex reply, Stop and restart/history passed.

## Boundaries

Unknown pixel clicks/drags, file/shell activation, native saves and ambiguous default-button Enter still require review when the host cannot establish a safe semantic operation. This does not affect ordinary semantic Notepad editing. A keyboard fallback is used for newlines/tabs only in a verified multiline/editor target, so an unknown single-line field cannot silently turn text into send/submit keystrokes.

Arbitrary application/website business logic is not universally inferable from accessibility or DOM metadata. Exact target semantics, recognized commit operations and the request backstop are used; authentication and consequential uncertain cases remain manual/reviewed. Existing browser compatibility, protected-file and shared-input limits remain documented in README.

## Use

Enable the desired desktop scope and give Codex the editing task. Multiline Notepad text needs no separate approval. Use the dedicated browser's semantic fill for webpage text. Genuine external commits explain their reason in chat; Allow Once applies only to that operation. File policies remain configured separately through Permissions.
