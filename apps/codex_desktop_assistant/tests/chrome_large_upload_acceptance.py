"""Opt-in 1 GiB acceptance test using a disposable Chrome and a loopback receiver."""
import hashlib
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

from chrome_dom_acceptance import Adapter, APP
from assistant.attachments import Attachments, MAX_FILE
from assistant.chrome_control import ChromeControl
from playwright.sync_api import sync_playwright


class Receiver(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b'<input type=file aria-label="Synthetic attachment">')

    def do_POST(self):
        remaining = int(self.headers["Content-Length"])
        digest = hashlib.sha256()
        while remaining:
            block = self.rfile.read(min(remaining, 1024**2))
            if not block:
                raise EOFError("Incomplete upload")
            remaining -= len(block)
            digest.update(block)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(digest.hexdigest().encode())


def main():
    with tempfile.TemporaryDirectory() as tmp, ThreadingHTTPServer(("127.0.0.1", 0), Receiver) as server:
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_port}"
        source = Path(tmp) / "fixture.bin"
        with source.open("wb") as stream:
            for index in range(1024):
                stream.write(index.to_bytes(4, "little") * (1024**2 // 4))
        attachments = Attachments(tmp)
        record = attachments.add(source)
        assert source.stat().st_size == MAX_FILE
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(channel="chrome", headless=True, chromium_sandbox=True)
            page = browser.new_page()
            page.goto(url)
            adapter = Adapter(page, (APP / "chrome_extension/content.js").read_text(encoding="utf-8"))
            assert adapter.call("grant", origin=url)["ok"]
            snapshot = adapter.call("inspect")["result"]
            element = next(c["element"] for c in snapshot["controls"] if c["type"] == "file")

            def request(conversation, operation, arguments, epoch):
                response = adapter.call(operation, **arguments)
                assert response["ok"], response
                return response["result"]

            controller = SimpleNamespace(attachments=attachments, grants={1: {"origin": url}}, request=request)
            receipt = ChromeControl.upload(controller, "fixture", {"tab": 1, "attachment_id": record["id"],
                "observation": snapshot["observation"], "element": element}, {record["id"]: record}, 0,
                {"page_url": url})
            assert receipt["bytes"] == MAX_FILE
            actual = page.evaluate("""async () => (await fetch('/verify', {
                method:'POST', body:document.querySelector('input').files[0]})).text()""")
            assert actual == record["sha256"]
            browser.close()
        server.shutdown()
        print("Verified 1,073,741,824 bytes in Chrome and at the HTTP receiver.")


if __name__ == "__main__":
    main()
