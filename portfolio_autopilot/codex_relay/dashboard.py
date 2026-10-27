"""Authenticated loopback UI. No telemetry, CDNs, HTML from GitHub, or public listener."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
from urllib.parse import urlsplit

from .credentials import save_token
from .github import GitHub
from .diagnostics import latest


class Server(ThreadingHTTPServer):
    daemon_threads = True


def make_server(relay, port=None):
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # URLs, tokens and request contents never go to terminal logs.

        def host_ok(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def auth(self):
            cookies = dict(s.strip().split("=", 1) for s in self.headers.get("Cookie", "").split(";") if "=" in s)
            return secrets.compare_digest(cookies.get("relay", ""), token)

        def send(self, status, value, content_type="application/json", cookie=False):
            data = value if isinstance(value, bytes) else json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if cookie:
                self.send_header("Set-Cookie", f"relay={token}; HttpOnly; SameSite=Strict; Path=/")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if not self.host_ok():
                return self.send(403, {"error": "Invalid Host"})
            path = urlsplit(self.path).path
            assets = {"/": ("index.html", "text/html; charset=utf-8"),
                      "/app.js": ("app.js", "application/javascript; charset=utf-8"),
                      "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in assets:
                name, mime = assets[path]
                return self.send(200, (Path(__file__).parent / "static" / name).read_bytes(), mime)
            if not self.auth():
                return self.send(401, {"error": "Open the dashboard using the Windows launcher"})
            if path == "/api/state":
                return self.send(200, relay.snapshot())
            if path == '/api/diagnostics':
                return self.send(200, latest(relay.config.data_dir))
            if path.startswith("/api/history/"):
                return self.send(200, relay.store.history(path.rsplit("/", 1)[-1]))
            return self.send(404, {"error": "Not found"})

        def do_POST(self):
            if not self.host_ok():
                return self.send(403, {"error": "Invalid Host"})
            origin = self.headers.get("Origin")
            if origin and origin != f"http://127.0.0.1:{self.server.server_port}":
                return self.send(403, {"error": "Cross-origin action denied"})
            if not secrets.compare_digest(self.headers.get("X-Relay-Token", ""), token):
                return self.send(403, {"error": "Missing or invalid action token"})
            if self.path != "/api/session" and not self.auth():
                return self.send(401, {"error": "Session required"})
            if self.headers.get("Content-Type") != "application/json":
                return self.send(400, {"error": "JSON required"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 24000:
                    raise ValueError("Invalid request size")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Expected object")
                if self.path == "/api/session":
                    return self.send(200, {"ok": True}, cookie=True)
                if self.path == "/api/start":
                    relay.start()
                elif self.path == "/api/stop":
                    relay.stop()
                elif self.path == "/api/exit":
                    relay.stop()
                    self.send(200, {"ok": True})
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                    return
                elif self.path == "/api/test":
                    return self.send(200, relay.test_connection())
                elif self.path == "/api/setup":
                    if relay.running or relay.active_id:
                        raise ValueError("Stop the runner before changing setup")
                    token_value = body.get("token", "")
                    if not isinstance(token_value, str) or len(token_value) > 2000:
                        raise ValueError("Invalid token")
                    trusted = body.get("trusted_ids", [])
                    if not isinstance(trusted, list) or any(type(i) is not int or i <= 0 for i in trusted):
                        raise ValueError("Trusted identities must be numeric GitHub account IDs")
                    client = GitHub(relay.config, relay.store, token_provider=lambda: token_value) if token_value else relay.github
                    identity = client.connect()
                    if token_value:
                        save_token(token_value)
                    relay.config.owner_id = identity["id"]
                    relay.config.trusted_ids = trusted
                    relay.config.save()
                    relay.store.log("system", "SETUP", "Owner and trusted numeric account IDs configured locally")
                    return self.send(200, {"owner_id": identity["id"], "login": identity["login"]})
                elif self.path == "/api/approve":
                    # Re-fetch immediately before creating a new execution grant.
                    relay.poll()
                    relay.approve(body["task_id"], body.get("public_test") is True)
                elif self.path == "/api/control":
                    relay.control(body["task_id"], body["action"])
                elif self.path == "/api/publish":
                    relay.publish(body["task_id"], body["text"], body.get("reviewed") is True)
                else:
                    return self.send(404, {"error": "Not found"})
                return self.send(200, {"ok": True})
            except (ValueError, KeyError, TypeError, RuntimeError) as exc:
                return self.send(400, {"error": str(exc)[:1000]})
            except Exception:
                return self.send(500, {"error": "Local operation failed; verify configuration and permissions"})

    server = Server(("127.0.0.1", relay.config.port if port is None else port), Handler)
    server.relay_token = token
    return server
