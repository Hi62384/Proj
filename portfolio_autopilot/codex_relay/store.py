"""Transactional local journal, durable inbox and publication outbox."""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
import threading
import time


class Store:
    def __init__(self, directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.depth = 0
        self.db = sqlite3.connect(Path(directory) / "relay.sqlite3", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, issue INTEGER UNIQUE, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS inbox(comment_id INTEGER PRIMARY KEY, message_id TEXT UNIQUE, task_id TEXT, data TEXT, state TEXT);
        CREATE TABLE IF NOT EXISTS history(seq INTEGER PRIMARY KEY, task_id TEXT, kind TEXT, text TEXT, at REAL);
        CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, issue INTEGER, body TEXT, state TEXT DEFAULT 'pending', attempts INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
        ''')

    @contextmanager
    def transaction(self):
        with self.lock:
            outer = self.depth == 0
            if outer:
                self.db.execute("BEGIN IMMEDIATE")
            self.depth += 1
            try:
                yield
            except BaseException:
                self.depth -= 1
                if outer:
                    self.db.rollback()
                raise
            else:
                self.depth -= 1
                if outer:
                    self.db.commit()

    def all(self):
        with self.lock:
            return [json.loads(r[0]) for r in self.db.execute("SELECT data FROM tasks ORDER BY issue DESC")]

    def get(self, task_id):
        with self.lock:
            row = self.db.execute("SELECT data FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not row:
                raise ValueError("Unknown task")
            return json.loads(row[0])

    def save(self, task):
        with self.transaction():
            self.db.execute("INSERT INTO tasks VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                            (task["id"], task["issue"], json.dumps(task)))

    def log(self, task_id, kind, text):
        with self.transaction():
            self.db.execute("INSERT INTO history(task_id,kind,text,at) VALUES(?,?,?,?)",
                            (task_id, kind, str(text)[:50000], time.time()))

    def history(self, task_id):
        with self.lock:
            return [dict(r) for r in self.db.execute("SELECT * FROM history WHERE task_id=? ORDER BY seq", (task_id,))]

    def meta(self, key, value=None):
        with self.transaction():
            if value is not None:
                self.db.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", (key, json.dumps(value)))
            row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
            return json.loads(row[0]) if row else None

    def receive(self, comment_id, value):
        with self.transaction():
            cursor = self.db.execute("INSERT OR IGNORE INTO inbox VALUES(?,?,?,?, 'pending')",
                                     (comment_id, value["message_id"], value["task_id"], json.dumps(value)))
            return bool(cursor.rowcount)

    def pending(self):
        with self.lock:
            return [(r[0], json.loads(r[1])) for r in self.db.execute("SELECT comment_id,data FROM inbox WHERE state='pending' ORDER BY comment_id")]

    def consume(self, comment_id, state="done"):
        with self.transaction():
            self.db.execute("UPDATE inbox SET state=? WHERE comment_id=?", (state, comment_id))

    def enqueue(self, event_id, issue, body):
        with self.transaction():
            self.db.execute("INSERT OR IGNORE INTO outbox(id,issue,body) VALUES(?,?,?)", (event_id, issue, body))

    def outgoing(self):
        with self.lock:
            return [dict(r) for r in self.db.execute("SELECT * FROM outbox WHERE state='pending' AND attempts<5")]

    def delivery(self):
        with self.lock:
            return {r[0]: r[1] for r in self.db.execute("SELECT state,COUNT(*) FROM outbox GROUP BY state")}

    def sent(self, event_id, state):
        with self.transaction():
            self.db.execute("UPDATE outbox SET state=?,attempts=attempts+1 WHERE id=?", (state, event_id))

    def close(self):
        self.db.close()
