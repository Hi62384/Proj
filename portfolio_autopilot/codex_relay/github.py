"""A deliberately narrow GitHub REST client: read inbox, write comments only."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .credentials import get_token


class GitHubError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class GitHub:
    def __init__(self, config, store, token_provider=get_token, opener=None):
        self.config, self.store = config, store
        self.token_provider = token_provider
        self.opener = opener or build_opener(NoRedirect())
        self.not_before = float(store.meta("github_not_before") or 0)
        self.repo = None  # Unknown means public; refreshed before each polling cycle.

    def request(self, path, body=None):
        if getattr(self, "shutdown_event", None) and self.shutdown_event.is_set():
            raise GitHubError("Relay is shutting down")
        if time.time() < self.not_before:
            raise GitHubError("GitHub rate limit/backoff is active; polling will recover automatically")
        prefix = "/repos/" + self.config.repository
        if not (path == "/user" or path == prefix or path.startswith(prefix + "/issues")):
            raise ValueError("GitHub endpoint is not permitted")
        if body is not None:
            import re
            if not re.fullmatch(re.escape(prefix) + r"/issues/[1-9][0-9]*/comments", path) or set(body) != {"body"}:
                raise ValueError("Only issue comment publication is implemented")
        token = self.token_provider()
        headers = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "CodexRelay/1.0"}
        if body is not None:
            headers['Content-Type'] = 'application/json'
        cache_key = "etag:" + path
        cached = self.store.meta(cache_key)
        if body is None and cached:
            headers["If-None-Match"] = cached["etag"]
        req = Request("https://api.github.com" + path, headers=headers,
                      data=json.dumps(body).encode() if body is not None else None,
                      method="POST" if body is not None else "GET")
        try:
            with self.opener.open(req, timeout=20) as response:
                value = json.loads(response.read(8_000_001))
                if response.headers.get("ETag") and body is None:
                    self.store.meta(cache_key, {"etag": response.headers["ETag"], "value": value})
                if response.headers.get("X-RateLimit-Remaining") == "0":
                    self.defer(float(response.headers.get("X-RateLimit-Reset", time.time() + 60)))
                return value
        except HTTPError as exc:
            if exc.code == 304 and cached:
                return cached["value"]
            if exc.code in (403, 429):
                try:
                    retry = float(exc.headers.get("Retry-After", "60"))
                    reset = float(exc.headers.get("X-RateLimit-Reset", "0"))
                except ValueError:
                    retry, reset = 60, 0
                self.defer(max(time.time() + max(60, retry), reset))
            raise GitHubError(f"GitHub HTTP {exc.code}; check Issues permission, access, or rate limits") from None
        except (URLError, OSError, ValueError):
            self.defer(time.time() + 60)
            raise GitHubError("GitHub network/response failure; retrying after backoff") from None

    def defer(self, until):
        self.not_before = until
        self.store.meta("github_not_before", until)

    def pages(self, path):
        result = []
        for page in range(1, 101):
            value = self.request(path + ("&" if "?" in path else "?") + f"per_page=100&page={page}")
            if not isinstance(value, list):
                raise GitHubError("Unexpected GitHub list response")
            result.extend(value)
            if len(value) < 100:
                return result
        raise GitHubError("Inbox exceeded 10,000 entries; narrow the inbox before continuing")

    def connect(self):
        user = self.request("/user")
        self.repo = self.request("/repos/" + self.config.repository)
        if self.config.owner_id and user["id"] != self.config.owner_id:
            raise GitHubError("Token account differs from the configured owner ID")
        return {"login": user["login"], "id": user["id"], "public": not self.repo.get("private", False)}

    def issues(self):
        return self.pages("/repos/" + self.config.repository + "/issues?state=all&sort=updated&direction=desc")

    def comments(self, issue):
        return self.pages(f"/repos/{self.config.repository}/issues/{int(issue)}/comments")

    def comment(self, issue, body):
        return self.request(f"/repos/{self.config.repository}/issues/{int(issue)}/comments", {"body": body})
