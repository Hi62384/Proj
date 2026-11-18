"""Synchronous Discord DOM operations. A single thread owns each Playwright page."""
import re
import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout

DOM = Path(__file__).with_name("dom.js").read_text(encoding="utf-8")
ORIGIN = "https://discord.com"
CHANNEL = re.compile(r"/channels/(?:@me|[0-9]+)(?:/[0-9]+)?\Z")
DISCORD_EPOCH = 1420070400000


class BridgeError(RuntimeError):
    pass


class DeliveryUnknown(BridgeError):
    pass


def normal(text):
    return text.replace("\ufeff", "").replace("\u200b", "").replace("\r\n", "\n").replace("\u00a0", " ").rstrip("\n")


def confirmed(before, after, text, names, submitted_ms):
    """Require a new, non-pending row by the authenticated account with matching payload."""
    if after["path"] != before["path"] or not before["self"] or before["self"] != after["self"]:
        return None
    prior = {row["id"] for row in before["messages"]}
    latest = max((int(row["messageId"]) for row in before["messages"]
                  if row["messageId"].isdecimal()), default=0)
    for row in after["messages"]:
        mid = row["messageId"]
        if (row["id"] not in prior and mid.isdecimal() and not row["pending"]
                and int(mid) > latest
                and row["authorId"] == before["self"] and (normal(row["text"]) == normal(text)
                    or (text == "https://klipy.com/gifs/billy-bucher-oi" and not row["text"]
                        and (int(mid) >> 22) + DISCORD_EPOCH >= submitted_ms - 2000
                        and any(asset.get("kind") == "video" and asset.get("url", "").split("?")[0].endswith(
                            "/ii/9294a2e836d178ddc22430dd7765727e/ce/8b/30ML6JApHJrM5In3.mp4")
                            for asset in row.get("assets", []))))
                and sorted(row["attachments"]) == sorted(names)):
            return mid
    return None


class DiscordBridge:
    def __init__(self, page, *, origin=ORIGIN):
        self.page = page
        self.origin = origin

    def _check(self, path=None):
        from urllib.parse import urlsplit
        current = urlsplit(self.page.url)
        if (f"{current.scheme}://{current.netloc}" != self.origin
                or not CHANNEL.fullmatch(current.path)
                or (path is not None and current.path != path)):
            raise BridgeError("Discord changed pages. Refresh the view and try again.")
        return current.path

    def read(self, op="snapshot", arg=None):
        self._check()
        return self.page.evaluate(DOM, [op, arg])

    def element(self, op, arg=None, *, required=True):
        self._check()
        handle = self.page.evaluate_handle(DOM, [op, arg])
        element = handle.as_element()
        if element is None:
            handle.dispose()
            if required:
                raise BridgeError(f"Discord's {op} control is unavailable or ambiguous.")
        return element

    def click(self, op, arg=None):
        element = self.element(op, arg)
        try:
            element.click(timeout=2500)
        finally:
            element.dispose()

    def navigate(self, path):
        state = self.read()
        allowed = {item["path"] for key in ("channels", "dms") for item in state[key]}
        if path != "/channels/@me" and path not in allowed:
            raise BridgeError("That channel is not in the current Discord navigation.")
        if path == "/channels/@me":
            home = self.element("friendTab", required=False)
            if home:
                home.evaluate("e => e.click()")
                home.dispose()
                return
            home = self.page.get_by_role("button", name="Friends", exact=True)
            if home.count():
                home.click(timeout=2500)
                return
        link = self.page.locator(f'a[href="{path}"]').first
        if not link.count():
            raise BridgeError("Discord's in-page navigation link is unavailable. Refresh the bridge view and retry.")
        link.evaluate("element => element.click()")
        try:
            self.page.wait_for_function("target => location.pathname === target", arg=path, timeout=10000)
        except PlaywrightTimeout:
            raise BridgeError("Discord did not open the requested chat. Retry navigation.") from None

    def server(self, identity):
        self.click("server", identity)

    def members(self):
        button = self.element("memberButton", required=False)
        if button:
            try:
                button.click(timeout=2500)
            finally:
                button.dispose()

    def open_member(self, name):
        member = self.element("member", name)
        try:
            member.click(timeout=3000)
        finally:
            member.dispose()

    def open_friends(self):
        tab = self.element("friendTab")
        try:
            tab.click(timeout=3000)
        finally:
            tab.dispose()
        # Home from a server opens the DM sidebar; select Friends within it
        # before waiting for its Pending tab.
        friends = self.page.locator('a[href="/channels/@me"]').first
        try:
            friends.wait_for(state="attached", timeout=3000)
            friends.evaluate("e => e.click()")
        except PlaywrightTimeout:
            pass
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            pending = self.element("pendingTab", required=False)
            if pending:
                try:
                    pending.evaluate("e => e.click()")
                    return
                finally:
                    pending.dispose()
            self.page.wait_for_timeout(100)
        raise BridgeError("Discord did not load the Pending friend requests tab.")

    def more_members(self):
        self.page.evaluate('''() => {
            const root = document.querySelector('[class*="membersWrap"]');
            if (!root) throw new Error('Member list is not open');
            const scroller = [root, ...root.querySelectorAll('*')].find(e =>
                e.scrollHeight > e.clientHeight && /auto|scroll/.test(getComputedStyle(e).overflowY));
            if (scroller) scroller.scrollTop += Math.max(200, scroller.clientHeight - 80);
        }''')

    def older_messages(self):
        self.page.evaluate('''() => {
            const row=document.querySelector('li[id^="chat-messages-"]');
            let scroller=row?.parentElement;
            while(scroller && !(scroller.scrollHeight>scroller.clientHeight &&
                /auto|scroll/.test(getComputedStyle(scroller).overflowY)))scroller=scroller.parentElement;
            if(!scroller)throw new Error('Message history is not available');
            scroller.scrollTop=0;
            scroller.dispatchEvent(new Event('scroll',{bubbles:true}));
        }''')
        self.page.wait_for_timeout(900)

    def accept_request(self, name):
        button = self.element("acceptRequest", name)
        try:
            button.click(timeout=3000)
        finally:
            button.dispose()

    def message_action(self, row_id, action):
        path = self._check()
        row = self.element("row", row_id)
        article = row.query_selector('[role="article"]')
        target = article or row
        try:
            try:
                target.hover(timeout=900, force=True)
            except PlaywrightTimeout:
                pass
            button = self.element(action, row_id, required=False)
            if button:
                try:
                    self._check(path)
                    button.click(timeout=1500)
                    return
                except PlaywrightTimeout:
                    pass
                finally:
                    button.dispose()
            self.page.keyboard.press("Escape")
            self.page.bring_to_front()
            self._check(path)
            self.page.locator(f'li[id="{row_id}"] [role="article"]').dispatch_event("contextmenu")
            menu_label = {"reply": "Reply", "addReaction": "Add Reaction"}[action]
            menu_id = {"reply": "message-reply", "addReaction": "message-add-reaction"}[action]
            try:
                item = self.page.locator(f'#{menu_id}[role="menuitem"]')
                item.wait_for(state="attached", timeout=3000)
                self._check(path)
                item.evaluate("element => element.click()")
            except PlaywrightTimeout:
                self.page.keyboard.press("Escape")
                raise BridgeError(f"Discord did not expose {menu_label} for this message.") from None
        finally:
            if article:
                article.dispose()
            row.dispose()

    def react(self, row_id, *, label=None, emoji=None):
        if label:
            self.click("toggleReaction", {"id": row_id, "label": label})
            return
        if not emoji or not re.fullmatch(r"[A-Za-z0-9_+\-]{1,64}", emoji):
            raise BridgeError("Enter an emoji name, such as thumbsup.")
        self.message_action(row_id, "addReaction")
        picker = self.element("emojiPicker")
        try:
            search = picker.query_selector('input[type="search"],input[placeholder*="Search" i],[role="searchbox"],input[aria-label*="Search" i]')
            if search:
                search.fill(emoji, timeout=2000)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                matches = picker.evaluate_handle("""(root, name) => {
                    const names = [name.toLowerCase(), ':' + name.toLowerCase() + ':'];
                    const items = [...root.querySelectorAll('button,[role=button],[role=option]')].filter(
                        e => e.getClientRects().length &&
                        [e.getAttribute('aria-label'),e.getAttribute('title'),e.querySelector('img')?.alt]
                        .some(s => names.includes(s?.toLowerCase())));
                    return items.length === 1 ? items[0] : null;
                }""", emoji)
                try:
                    if matches.as_element():
                        matches.as_element().click(timeout=2000)
                        return
                finally:
                    matches.dispose()
                self.page.wait_for_timeout(100)
            raise BridgeError("Discord did not show exactly one matching emoji.")
        finally:
            picker.dispose()

    def send(self, path, text="", files=(), reply=None, *, timeout=12):
        """files: Playwright FilePayload dicts with name, mimeType and bytes buffer."""
        self._check(path)
        names = [file["name"] for file in files]
        if not text.strip() and not files:
            raise BridgeError("Enter a message or add an attachment.")
        if len(set(names)) != len(names):
            raise BridgeError("Attachments must have distinct filenames.")
        box = None
        step = "prepare composer"
        try:
            # Escape dismisses Discord's call/profile popouts and modal layers.
            for _ in range(3):
                try:
                    self.page.keyboard.press("Escape")
                except PlaywrightTimeout:
                    break
            # If Escape did not dismiss a modal, click only a visible, explicitly
            # labelled close control belonging to a dialog/popout.
            self.page.evaluate("""() => {
                const visible = e => !!(e && e.getClientRects().length);
                const roots = [...document.querySelectorAll(
                    '[role="dialog"], [aria-modal="true"], [class*="userPopout"], [class*="callContainer"]'
                )].filter(visible);
                for (const root of roots.reverse()) {
                    const close = [...root.querySelectorAll('button,[role="button"]')].find(e => {
                        const label = (e.getAttribute('aria-label') || e.getAttribute('title') || '').trim();
                        return visible(e) && /^close(?: dialog| popout)?$/i.test(label);
                    });
                    if (close) { close.click(); return true; }
                }
                return false;
            }""")
            box = self.element("composer")
            box.evaluate("element => { element.focus(); element.click(); }")
            initial = self.read("inputState")
            if normal(initial["text"]).strip() or initial["files"] or initial["reply"]:
                raise BridgeError("Clear the existing draft, attachments, or reply in Edge before sending.")
            if files:
                step = "attach files"
                upload = self.element("upload")
                try:
                    upload.set_input_files(list(files), timeout=3000)
                finally:
                    upload.dispose()
                deadline = time.monotonic() + 4
                while self.read("inputState")["files"] < len(files):
                    self._check(path)
                    if time.monotonic() >= deadline:
                        raise BridgeError("Discord did not show the attachment previews. Check the draft in Edge.")
                    self.page.wait_for_timeout(100)
            if reply:
                step = "start reply"
                self._check(path)
                self.message_action(reply, "reply")
                deadline = time.monotonic() + 3
                while not self.read("inputState")["reply"]:
                    self._check(path)
                    if time.monotonic() >= deadline:
                        raise BridgeError("Discord did not show a reply draft. Nothing was submitted.")
                    self.page.wait_for_timeout(100)
            # Attaching/replying may replace the Slate node.
            box.dispose()
            box = self.element("composer")
            self._check(path)
            if text:
                step = "enter message text"
                # The composer can be clipped by Discord's narrow layout.
                # Fill the selected editable directly without viewport checks.
                box.fill(text, force=True, timeout=3000)
            actual = self.read("inputState")
            if normal(actual["text"]) != normal(text) or actual["reply"] != bool(reply):
                raise BridgeError("Discord's draft does not match the requested message. Check Edge.")
            self._check(path)
            before = self.read("delivery")
            if before["path"] != path:
                raise BridgeError("Discord changed pages before submission.")
            button = self.element("sendButton", required=False)
            step = "submit message"
            submitted = int(time.time() * 1000)
            try:
                if button:
                    # Invoke Discord's visible submit control without relying on
                    # its position in the current Edge viewport.
                    button.evaluate("element => element.click()")
                else:
                    box.press("Enter", timeout=3000)
                deadline = time.monotonic() + timeout
                while time.monotonic() < deadline:
                    match = confirmed(before, self.read("delivery"), text, names, submitted)
                    if match:
                        return {"status": "sent", "messageId": match}
                    self.page.wait_for_timeout(150)
            except Exception as exc:
                raise DeliveryUnknown("Delivery could not be verified. Check Discord before retrying.") from exc
            finally:
                if button:
                    button.dispose()
            raise DeliveryUnknown("Delivery could not be verified. Check Discord before retrying.")
        except PlaywrightTimeout as exc:
            raise BridgeError(f"Discord timed out while trying to {step}. The draft is still in Disco; check Discord before retrying.") from exc
        finally:
            if box:
                box.dispose()
