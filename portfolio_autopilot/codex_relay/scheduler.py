from __future__ import annotations

import json
import re
import secrets
import threading
import time
import uuid

from . import messages
from .config import safe_path
from .workspace import Workspace


class Relay:
    def __init__(self, config, store, github, codex):
        self.config, self.store, self.github, self.codex = config, store, github, codex
        self.lock = threading.RLock()
        self.running = False
        self.shutdown = threading.Event()
        self.github.shutdown_event = self.shutdown
        self.cancelled = threading.Event()
        self.worker = None
        self.active_id = None
        self.connections = {"github": "Not tested", "codex": "Not tested", "public": True}
        self.last_error = ""
        self.next_poll = 0
        # Never replay an execution after ambiguous process termination.
        for t in store.all():
            if t["status"] == "Running":
                t.update(status="Needs Owner", paused=True, blocked="Execution interrupted by application restart")
                store.save(t)
                store.log(t["id"], "RECOVERY", "Interrupted run retained. Review files, then explicitly resume; no automatic replay.")

    def snapshot(self):
        with self.lock:
            return {"running": self.running, "connections": dict(self.connections),
                    "error": self.last_error, "tasks": self.store.all(), "active": self.active_id,
                    "repository": self.config.repository, "data_dir": str(self.config.data_dir),
                    "configured": bool(self.config.owner_id), "owner_id": self.config.owner_id,
                    "trusted_ids": self.config.trusted_ids,
                    "delivery": self.store.delivery()}

    def test_connection(self):
        try:
            connection = self.github.connect()
            self.connections.update(github=f"Connected: {connection['login']} (ID {connection['id']})", public=connection["public"])
        except Exception as exc:
            self.connections["github"] = str(exc)
            connection = {}
        try:
            self.codex.doctor()
            self.connections["codex"] = "Available · ChatGPT login · no inference test"
        except Exception as exc:
            self.connections["codex"] = str(exc)
        return connection

    def poll(self):
        if not self.config.owner_id:
            raise ValueError("Configure and verify the owner account before starting")
        connection = self.github.connect()  # Privacy checked every cycle; unknown is public.
        self.connections.update(github=f"Connected: {connection['login']}", public=connection["public"])
        issues = self.github.issues()
        observed = set()
        for issue in issues:
            if "pull_request" in issue:
                continue
            number = issue["number"]
            observed.add(number)
            existing = next((t for t in self.store.all() if t["issue"] == number), None)
            # Any edit to an approved issue invalidates approval, even if malformed or by another actor.
            revision = messages.digest({"body": issue.get("body"), "title": issue.get("title"), "author": issue.get("user", {}).get("id")})
            with self.lock:
                if existing:
                    existing = self.store.get(existing["id"])
                if existing and (revision != existing["revision"] or issue.get("state") == "closed"):
                    self._revoke(existing, "Issue changed or closed; review and approve the new scope locally")
            if issue.get("state") != "open" or issue.get("user", {}).get("id") not in self.trusted():
                continue
            try:
                payload = messages.task(issue.get("body"))
                for path in payload["paths"]:
                    safe_path(self.config.workspace, path)
                messages.text(issue.get("title"), 300)
            except (ValueError, TypeError):
                continue
            if existing and payload["task_id"] != existing["id"]:
                with self.lock:
                    self._revoke(existing, "Task ID is immutable. Create a new Issue for a different task ID.")
                continue
            with self.lock:
                if not existing:
                    if any(t["id"] == payload["task_id"] for t in self.store.all()):
                        continue
                    existing = {"id": payload["task_id"], "issue": number, "title": issue["title"],
                        "payload": payload, "revision": revision, "status": "Proposed", "approved": False,
                        "scope": "", "anchor": "", "thread_id": None, "paused": False,
                        "files_changed": [], "test_results": [], "report": "", "elapsed": 0,
                        "created": time.time(), "pending_reply": None, "public_test": False, "blocked": ""}
                    self.store.save(existing)
                    self.store.log(existing["id"], "PROPOSED", "Trusted GitHub task received; execution requires local approval")
                elif revision != existing["revision"]:
                    existing.update(payload=payload, title=issue["title"], revision=revision,
                                    status="Proposed", approved=False, pending_reply=None, thread_id=None)
                    self.store.save(existing)
            if existing.get("approved"):
                for comment in self.github.comments(number):
                    self.receive(existing, comment)
        # A hidden/deleted issue must never remain an executable grant.
        for t in self.store.all():
            if t.get("approved") and t["issue"] not in observed:
                with self.lock:
                    self._revoke(t, "Issue no longer accessible; approval revoked")
        self.process_inbox()
        self.flush()

    def trusted(self):
        return {self.config.owner_id, *self.config.trusted_ids} - {0}

    def _revoke(self, task, reason):
        if not task["approved"] and task["status"] == "Needs Owner" and task.get("blocked") == reason:
            return
        if self.active_id == task["id"]:
            self.cancelled.set()
            getattr(self.codex, "cancel", lambda: None)()
        task.update(approved=False, status="Needs Owner", paused=True, blocked=reason, pending_reply=None)
        self.store.save(task)
        self.store.log(task["id"], "APPROVAL_REVOKED", reason)

    def receive(self, task, comment):
        if comment.get("user", {}).get("id") not in self.trusted():
            return False
        # Edited comments cannot acquire new execution authority.
        if comment.get("updated_at") != comment.get("created_at"):
            return False
        try:
            value = messages.message(comment.get("body"))
        except (ValueError, TypeError):
            return False
        if value["type"] not in ("CHATGPT_REPLY", "OWNER_DECISION") or value["task_id"] != task["id"]:
            return False
        if value["scope"] != task["scope"] or value["reply_to"] != task["anchor"] or not task["approved"]:
            return False
        # Comments predating approval cannot be replayed into a new approval.
        from datetime import datetime
        try:
            timestamp = datetime.fromisoformat(comment["created_at"].replace("Z", "+00:00")).timestamp()
            if timestamp < task["approved_at"] - 1:
                return False
        except (KeyError, ValueError, TypeError):
            return False
        with self.store.transaction():
            inserted = self.store.receive(comment["id"], value)
            if inserted:
                self.store.log(task["id"], value["type"], value["text"])
        return inserted

    def process_inbox(self):
        with self.lock:
            for comment_id, value in self.store.pending():
                task = self.store.get(value["task_id"])
                if not task["approved"] or value["scope"] != task["scope"] or value["reply_to"] != task["anchor"]:
                    self.store.consume(comment_id, "rejected")
                    continue
                if task["status"] == "Running":
                    if value["action"] not in ("pause", "cancel"):
                        continue  # Keep it durable until this turn finishes; never steer an active execution.
                with self.store.transaction():
                    self.store.consume(comment_id)
                    action = value["action"]
                    if action in ("pause", "cancel"):
                        self._stop_task(task, action)
                    elif value["type"] == "OWNER_DECISION" or task["paused"] or task["status"] in ("Needs Owner", "Completed", "Cancelled", "Failed"):
                        task["pending_reply"] = value["text"]
                        task["blocked"] = "New reply requires local review and Resume"
                        self.store.save(task)
                    elif action in ("continue", "report"):
                        task.update(status="Approved", pending_reply=value["text"], anchor="")
                        self.store.save(task)

    def approve(self, task_id, public_test=False):
        with self.lock, self.store.transaction():
            task = self.store.get(task_id)
            if task["status"] != "Proposed" or not self.config.owner_id:
                raise ValueError("Only a proposed task can receive initial approval")
            if not public_test:
                raise ValueError("Confirm this task is nonsensitive and safe for public Issues")
            for path in task["payload"]["paths"]:
                if path.replace("\\", "/").split("/")[-1].lower() in ("agents.md", "skill.md"):
                    raise ValueError("Project instruction files cannot be edited by the relay")
                safe_path(self.config.workspace, path)
            task.update(approved=True, scope=secrets.token_hex(16), approved_at=time.time(),
                        status="Approved", paused=False, public_test=True, blocked="")
            self.store.save(task)
            self.store.log(task_id, "LOCAL_APPROVAL", json.dumps({"revision": task["revision"], "paths": task["payload"]["paths"]}))
            self.announce(task, "CODEX_PROGRESS")

    def announce(self, task, kind):
        # Fixed vocabulary only: never publish generated text, logs, paths, tests or source.
        event_id = uuid.uuid4().hex
        task["anchor"] = event_id
        body = messages.encode({"type": kind, "task_id": task["id"], "message_id": event_id,
            "reply_to": "status", "scope": task["scope"], "action": "report",
            "text": "Status: " + task["status"] + ". Detailed output stays local until the owner releases a reviewed message."})
        with self.store.transaction():
            self.store.save(task)
            self.store.enqueue(event_id, task["issue"], body)

    def publish(self, task_id, text, acknowledge_public):
        with self.lock:
            task = self.store.get(task_id)
            if not task["approved"] or not acknowledge_public:
                raise ValueError("Local approval and explicit public-message review are required")
            messages.text(text, 4000)
            if re.search(r"(?i)(gh[pousr]_|github_pat_|sk-[a-z0-9]|bearer\s|-----BEGIN|[A-Z]:[\\/]|/Users/|/home/)", text):
                raise ValueError("Possible credential or local path detected; remove it before publication")
            event_id = uuid.uuid4().hex
            kind = "CODEX_QUESTION" if task["status"] in ("Needs ChatGPT", "Needs Owner") else "CODEX_RESULT"
            task["anchor"] = event_id
            body = messages.encode({"type": kind, "task_id": task_id, "message_id": event_id,
                "reply_to": "owner-reviewed", "scope": task["scope"], "action": "report", "text": text})
            with self.store.transaction():
                self.store.save(task)
                self.store.enqueue(event_id, task["issue"], body)
                self.store.log(task_id, "LOCAL_PUBLICATION_APPROVAL", text)

    def flush(self):
        for row in self.store.outgoing():
            # Reconcile ambiguous POST outcomes by durable message ID before trying again.
            comments = self.github.comments(row["issue"])
            found = False
            for comment in comments:
                if comment.get("user", {}).get("id") != self.config.owner_id:
                    continue
                try:
                    found |= messages.message(comment.get("body"))["message_id"] == row["id"]
                except (ValueError, TypeError):
                    pass
            if found:
                self.store.sent(row["id"], "sent")
                continue
            try:
                self.github.comment(row["issue"], row["body"])
                self.store.sent(row["id"], "sent")
            except Exception:
                # POST may have succeeded even if its response was lost. Never retry automatically.
                self.store.sent(row["id"], "uncertain")
                self.last_error = "Comment delivery uncertain. Review the Issue; automatic repost is disabled to prevent duplicates."
                raise

    def control(self, task_id, action):
        with self.lock:
            task = self.store.get(task_id)
            if action == "reject":
                if task["status"] != "Proposed":
                    raise ValueError("Only proposed tasks can be rejected")
                task.update(status="Cancelled", approved=False, blocked="Rejected locally")
            elif action in ("pause", "cancel"):
                self._stop_task(task, action)
                return
            elif action == "resume":
                if not task["approved"] or task["status"] in ("Running", "Cancelled", "Completed", "Proposed"):
                    raise ValueError("Task cannot be resumed; changed scopes require a fresh approval")
                task.update(status="Approved", paused=False, blocked="")
                self.store.log(task_id, "LOCAL_RESUME", "Owner reviewed and resumed the existing approved scope")
            elif action == "complete":
                if task["status"] != "Awaiting Review":
                    raise ValueError("Review a finished task before completing it")
                task.update(status="Completed", paused=True)
            elif action == "reset-session":
                if task["status"] != "Failed" or not task["approved"]:
                    raise ValueError("Only an approved failed task can have its session reset")
                self.store.log(task_id, "LOCAL_SESSION_RESET", "Owner discarded unavailable/failed session: " + str(task.get("thread_id")))
                task.update(thread_id=None, status="Needs Owner", paused=True,
                            blocked="Session reset locally. Resume starts a new conversation within the same approved file scope.")
            else:
                raise ValueError("Unknown action")
            self.store.save(task)
            self.store.log(task_id, "LOCAL_CONTROL", action)
            if task["approved"]:
                self.announce(task, "CODEX_PROGRESS")

    def _stop_task(self, task, action):
        if self.active_id == task["id"]:
            self.cancelled.set()
            getattr(self.codex, "cancel", lambda: None)()
        task.update(status="Cancelled" if action == "cancel" else "Needs Owner", paused=True,
                    blocked="Cancelled locally" if action == "cancel" else "Paused; local Resume required")
        self.store.save(task)
        self.store.log(task["id"], "STOP", action)
        if task["approved"]:
            self.announce(task, "CODEX_PROGRESS")

    def start(self):
        if not self.config.owner_id:
            raise ValueError("Complete Setup first")
        self.running = True
        self.next_poll = 0

    def stop(self):
        with self.lock:
            self.running = False
            if self.active_id:
                self._stop_task(self.store.get(self.active_id), "pause")

    def launch_ready(self):
        with self.lock:
            if not self.running or self.worker and self.worker.is_alive():
                return
            for task in sorted(self.store.all(), key=lambda t: ({"high": 0, "normal": 1, "low": 2}[t["payload"]["priority"]], t["created"])):
                if task["status"] != "Approved" or not task["approved"] or task["paused"]:
                    continue
                states = {t["id"]: t["status"] for t in self.store.all()}
                if any(states.get(d) != "Completed" for d in task["payload"]["dependencies"]):
                    continue
                self.cancelled = threading.Event()
                self.active_id = task["id"]
                prompt = json.dumps({"approved_task": task["payload"], "follow_up": task.get("pending_reply")}, ensure_ascii=False)
                task.update(status="Running", pending_reply=None, started_at=time.time())
                with self.store.transaction():
                    self.store.save(task)  # Claim durably before spawning: ambiguous starts are never replayed.
                    self.announce(task, "CODEX_PROGRESS")
                    self.store.log(task["id"], "EXECUTION_CLAIM", "Execution durably claimed before starting app-server")
                self.worker = threading.Thread(target=self.execute, args=(task, prompt), daemon=True)
                self.worker.start()
                return

    def execute(self, task, prompt):
        task_id, started = task["id"], time.monotonic()
        def active():
            return not self.cancelled.is_set() and self.store.get(task_id)["status"] == "Running"
        def emit(kind, value):
            with self.lock:
                self.store.log(task_id, kind, value)
                current = self.store.get(task_id)
                current["latest_message"] = str(value)[:50000]
                current["history_updated"] = time.time()
                if kind == "FILE_CHANGED" and value not in current["files_changed"]:
                    current["files_changed"].append(value)
                if kind == "TEST_RESULT":
                    current["test_results"].append(value)
                self.store.save(current)
        def save_thread(thread_id):
            with self.lock:
                current = self.store.get(task_id)
                current["thread_id"] = thread_id
                self.store.save(current)
        try:
            workspace = Workspace(self.config.workspace, task["payload"]["paths"], active, emit,
                                  self.config.data_dir / "backups" / task["scope"])
            workspace.lock = self.lock  # Stop and file writes share one gate.
            value = self.codex.run(task, prompt, workspace, self.cancelled, emit, save_thread)
            with self.lock:
                current = self.store.get(task_id)
                if active():
                    current.update(status={"result": "Awaiting Review", "question": "Needs ChatGPT", "owner": "Needs Owner"}[value["kind"]],
                                   report=value["summary"], question=value["question"], model_test_claims=value["tests"],
                                   paused=value["kind"] == "owner")
                    self.store.save(current)
                    self.store.log(task_id, "CODEX_RESULT", json.dumps(value))
                    self.announce(current, "CODEX_QUESTION" if value["kind"] != "result" else "CODEX_RESULT")
        except InterruptedError:
            pass
        except Exception as exc:
            with self.lock:
                current = self.store.get(task_id)
                if current["status"] == "Running":
                    current.update(status="Failed", paused=True, blocked=str(exc)[:2000])
                    self.store.save(current)
                    self.store.log(task_id, "CODEX_ERROR", str(exc))
                    self.announce(current, "CODEX_ERROR")
        finally:
            with self.lock:
                current = self.store.get(task_id)
                current["elapsed"] += round(time.monotonic() - started, 2)
                self.store.save(current)
                self.active_id = None

    def loop(self):
        while not self.shutdown.wait(.3):
            if not self.running:
                continue
            if time.monotonic() >= self.next_poll:
                try:
                    self.poll()
                    self.last_error = ""
                except Exception as exc:
                    self.connections["public"] = True
                    self.last_error = str(exc)
                    # A lost connection prevents new starts; an already approved local turn may finish.
                    self.next_poll = time.monotonic() + self.config.poll_seconds
                    continue
                self.next_poll = time.monotonic() + self.config.poll_seconds
                self.launch_ready()

    def close(self):
        self.stop()
        self.shutdown.set()
        if self.worker:
            self.worker.join(timeout=12)
