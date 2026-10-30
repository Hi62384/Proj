# Existing Chrome setup and operation

Run the normal Desktop Assistant setup first. Its project environment supplies
Python, PySide6, pywin32, Pillow and the existing runtime dependencies. No additional
Node server, debugging port or paid service is required for Chrome integration.

1. Run `Setup_Chrome.cmd`, or choose **Existing Chrome → Connect Chrome** in the
   assistant. This prepares the stable extension identity and registers the native
   host under the current Windows user, without an administrator installation.
2. In normal Google Chrome, open `chrome://extensions`, enable Developer mode,
   choose **Load unpacked**, and select this project's `chrome_extension` folder.
   For this checkout the folder is
   `C:\Users\User1\Documents\Downloads\Proj\apps\codex_desktop_assistant\chrome_extension`.
3. Open the teal extension icon in Chrome's toolbar. If it is hidden, find it in
   Chrome's Extensions menu and pin it. Choose **Connect** while the assistant is
   open. **Connected to Desktop Assistant** confirms the channel, not site access.
4. On an ordinary webpage choose **Allow Codex to Control This Tab**. Wait for
   **Authorized tab …**. Use **Allow Site Access** and approve Chrome's prompt
   when Codex should also control new tabs it creates on that site. A tab grant
   by itself does not authorize new tabs or unrelated sites.
5. In the assistant's **Chrome Tabs / Select Window** picker, select the offered
   tab and choose **Attach Tab** for the current chat. A model's first attempt to
   attach an existing tab can instead show the exact-tab approval in chat.
6. Use **Check Connection** for a real round trip. Give the assistant instructions.
   Background DOM work does not need **Show Tab**. That button deliberately brings
   the selected tab forward when you want to see it.

## Tabs and boundaries

`chrome.open_tab` creates a background HTTP(S) tab without requiring a selected tab.
Existing Chrome host permission enables automatic control and chat attachment on
that site; otherwise the tab opens but cannot be inspected until you grant access.
Redirects to unrelated sites do not inherit the original tab grant. Clean attached
tabs close automatically. Tabs created by the extension also close without review
when they were never activated or edited; that exception is session-local and cannot
be asserted by the model. Other possible unsaved editor/form contents require a review;
the worker checks again before closing and refuses a changed tab.

Only authorized tab contents are returned. Discovery of other tabs reveals their
IDs/window/active state, without their titles, URLs or page text. Purchases,
publication, sensitive submissions, destructive and account-security actions keep
their own review. Authentication, CAPTCHA and MFA remain manual. Page scripts
cannot grant permissions or call the native host through this extension.

**Manual Control** holds automation on that tab. Return control and inspect again
before continuing. **Stop automation for this tab** and **Release Tab** revoke its
current controller. **Stop** or emergency Stop in the assistant invalidates chat
authority immediately. Connection recovery never replays a website action.

## Files and screenshots

Uploads use a selected attachment from the current chat, with a separate review of
destination, filename, size and hash. The extension receives real bounded chunks;
it never assigns a local path to a file input. Limit: 25 MB. Ordinary direct-file
Read/Write/Create/Delete permissions still apply independently. Upload results
must be verified on the page or server; dispatch is not proof of a completed save.

Downloads require optional **Enable Download Save Dialogs** permission. An approved
same-site download opens Chrome's Save As dialog; choose the destination yourself.
Automatic selection, overwrite and execution of downloaded files are unsupported.

DOM observations work on supported background pages. Screenshots require separate
consent, an explicitly shown active tab/window, and approved nonsensitive frames.
Hidden-tab screenshots, authentication screens and opaque frames are refused.
There is no debugger permission or arbitrary model-authored JavaScript capability.

## Updates and recovery

Keep the manifest's public `key` and extension folder to preserve the extension ID.
After code updates, reload the installed extension with its circular-arrow button
at `chrome://extensions`; the bundled, non-web-accessible `upgrade.html` page is
also used by development tools for code-only reloads. New Chrome permissions still
need Chrome's supported user approval. Do not repeatedly remove/reinstall it.

A refresh/restart clears tab controllers and chat attachments. The connection may
reconnect automatically after an earlier **Connect**, but revoked tab grants are
not silently restored. Reauthorize a needed existing tab, or open a new tab on an
already site-permitted host. Save human work before refreshing a webpage.

## Troubleshooting

- **Disconnected:** open the assistant, then click Connect. Run
  `.venv\Scripts\python.exe tools\setup_chrome.py health` from the app folder to
  check registration. This checks preparation; the app's **Check Connection**
  verifies communication. If the checkout moved, run `Setup_Chrome.cmd` again.
- **Connected / This tab is not authorized:** these are separate states. On the
  intended page use the tab or site access button, then attach it to the chat.
  Chrome internal pages, the Web Store and restricted screens cannot be controlled.
- **Assistant did not confirm grant:** the popup keeps the tab unauthorized.
  Restart the idle updated assistant and reconnect. Do not treat a connection
  label or an old tab badge as proof of current authority.
- **Earlier controller warning:** save any work and refresh only the affected
  webpage, then authorize it again. Do not reset your browser profile.
- **Rule-size error:** current network guards use literal filters rather than the
  oversized regex from development. Reload the updated extension once.
- **Observation changed / human input has priority:** inspect again after the human
  edit finishes. Never retry an uncertain submission automatically.
- **Scripted control cannot be verified:** review may be needed, or use Manual
  Control. Some websites' opaque commit endpoints cannot be safely automated.
- **Service worker sleeps or channel drops:** reconnection is bounded and does not
  repeat actions. Reinspect after recovery and restore only the scope you intend.

Diagnostics are stored in the current user's private assistant directory.
`chrome-health.json` contains nonsecret connection metadata. Do not share
`chrome-bridge.json`, private connection keys, browser profile files or credentials.

## Revoke and uninstall

First Stop automation and choose **Disconnect** in the popup. Revoke Chrome site
access in the extension's Details/site-permissions controls to remove persistent
host permissions, and remove the extension at `chrome://extensions` if desired.
Run `.venv\Scripts\python.exe tools\setup_chrome.py uninstall` from the app folder
to unregister this user's native host. This does not delete conversations,
attachments, browser profiles or sign-ins. Host identity files remain for a
reversible reinstall. No Windows service or recurring server is installed.
