"""Durable local project coordination for Portfolio Manager.

The canonical portfolio describes projects. This database owns claims, task plans,
and approval records. It never executes an external operation. The host owns
access to the database and calls owner controls from its trusted interface.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import sqlite3
import tempfile
import threading
import time
from uuid import uuid4

from business_portfolio.tools import build_browser


class CoordinatorError(ValueError):
    """A requested transition would violate coordinator policy."""


_SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK(id=1), mode TEXT NOT NULL, stopped INTEGER NOT NULL,
    emergency INTEGER NOT NULL, max_workers INTEGER NOT NULL, mode_epoch INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY, folder TEXT NOT NULL, kind TEXT NOT NULL, label TEXT NOT NULL,
    state TEXT NOT NULL, session_ref TEXT, heartbeat_at REAL NOT NULL, last_error TEXT
);
CREATE TABLE IF NOT EXISTS worker_credentials (
    worker_id TEXT PRIMARY KEY REFERENCES workers(id), proof_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    project_id TEXT NOT NULL, id TEXT NOT NULL, position INTEGER NOT NULL,
    title TEXT NOT NULL, criteria TEXT NOT NULL, weight REAL NOT NULL,
    depends_on TEXT NOT NULL, verification TEXT, provisional INTEGER NOT NULL,
    status TEXT NOT NULL, checkpoint TEXT, evidence TEXT, updated_at REAL NOT NULL,
    PRIMARY KEY(project_id,id)
);
CREATE TABLE IF NOT EXISTS leases (
    project_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, worker_id TEXT NOT NULL UNIQUE,
    token TEXT NOT NULL UNIQUE, record_path TEXT NOT NULL, record_sha256 TEXT NOT NULL,
    expires_at REAL NOT NULL, FOREIGN KEY(worker_id) REFERENCES workers(id),
    FOREIGN KEY(project_id,task_id) REFERENCES tasks(project_id,id)
);
CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, task_id TEXT NOT NULL,
    worker_id TEXT NOT NULL, kind TEXT NOT NULL, action TEXT NOT NULL, reason TEXT NOT NULL,
    scope TEXT NOT NULL, cost_cad REAL NOT NULL, consequences TEXT NOT NULL,
    after_action TEXT NOT NULL, record_sha256 TEXT NOT NULL, status TEXT NOT NULL,
    decision TEXT, created_at REAL NOT NULL, expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS effects (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, task_id TEXT NOT NULL,
    approval_id TEXT NOT NULL UNIQUE, dedup_key TEXT NOT NULL, action TEXT NOT NULL,
    scope TEXT NOT NULL, cost_cad REAL NOT NULL, state TEXT NOT NULL, evidence TEXT,
    created_at REAL NOT NULL, updated_at REAL NOT NULL, UNIQUE(project_id,dedup_key)
);
CREATE TABLE IF NOT EXISTS history (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT, worker_id TEXT,
    kind TEXT NOT NULL, detail TEXT NOT NULL, created_at REAL NOT NULL
);
"""

_DISPATCH_STATES = {'planned', 'active', 'ready_for_test', 'package_ready'}
_SKIP_TYPES = {'bundled_component', 'deferred_download', 'deferred_software',
               'inventory_only', 'existing_legacy_tool', 'existing_unassessed'}
_PRIORITY = {'P1': 0, 'INTEGRATE': 1, 'P2': 2, 'P3': 3}
_TASK_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z')


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def _text(value, label, limit=4000, *, empty=False):
    if not isinstance(value, str) or len(value) > limit or '\x00' in value:
        raise CoordinatorError(f'Invalid {label}')
    if not value.strip() and not empty:
        raise CoordinatorError(f'Missing {label}')
    return value.strip()


def _digest(path):
    if build_browser.linked_input(path):
        raise CoordinatorError('Linked evidence or record is unsafe')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_path(root, path):
    """Accept an existing descendant and reject aliases before resolving it."""
    if '..' in path.parts or not path.is_relative_to(root):
        raise CoordinatorError('Path is outside the permitted directory')
    for ancestor in (path, *path.parents):
        if build_browser.linked_input(ancestor):
            raise CoordinatorError('Linked paths are unsafe')
        if ancestor == root:
            break
    return path.resolve(strict=True)


class Coordinator:
    def __init__(self, repo, db_path=None, *, max_workers=4, lease_seconds=120):
        self.repo = Path(repo).resolve(strict=True)
        self.portfolio = self.repo / 'business_portfolio'
        self.niches = self.portfolio / 'niches'
        _safe_path(self.repo, self.niches)
        if type(max_workers) is not int or not 1 <= max_workers <= 32:
            raise CoordinatorError('Worker limit must be between 1 and 32')
        if not isinstance(lease_seconds, (int, float)) or not 0 < lease_seconds <= 86400:
            raise CoordinatorError('Invalid lease duration')
        self.lease_seconds = lease_seconds
        self.db_path = Path(db_path or self.portfolio / '.local' / 'portfolio-manager' / 'coordinator.sqlite3').absolute()
        existing = next(parent for parent in self.db_path.parents if parent.exists())
        _safe_path(Path(self.db_path.anchor), existing)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        _safe_path(Path(self.db_path.anchor), self.db_path.parent)
        if self.db_path.exists() and build_browser.linked_input(self.db_path):
            raise CoordinatorError('Linked database is unsafe')
        self._catalog_lock = threading.Lock()
        self._catalog_key = None
        self._catalog_data = None
        with self._database() as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript(_SCHEMA)
            db.execute('INSERT OR IGNORE INTO settings(id,mode,stopped,emergency,max_workers) VALUES (1,?,0,0,?)',
                       ('afk', max_workers))

    @contextmanager
    def _database(self, *, write=False):
        db = sqlite3.connect(self.db_path, timeout=8, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('BEGIN IMMEDIATE' if write else 'PRAGMA busy_timeout=8000')
            yield db
            if write:
                db.commit()
        except BaseException:
            if write:
                db.rollback()
            raise
        finally:
            db.close()

    def _catalog(self):
        # Reuse the portfolio's validator and derived metadata. The generated JSON
        # is a view and can lag behind canonical edits, so it is not an input.
        with self._catalog_lock:
            files = [p for p in build_browser.walk_files(self.niches)
                     if p.name == 'NICHE.json' or (p.parent.name == 'projects' and p.suffix.lower() == '.md')]
            files.append(self.portfolio / 'research' / 'SOURCE_REGISTER.json')
            key = tuple((str(p), info.st_mtime_ns, info.st_size) for p in files for info in (p.stat(),))
            if key != self._catalog_key:
                data = build_browser.load_portfolio(self.portfolio)
                self._catalog_data = ({r['id']: r for r in data['records']}, data['niches'])
                self._catalog_key = key
            return self._catalog_data

    def _folder(self, folder):
        candidate = self.niches if folder is None or folder == '' else Path(folder)
        if not candidate.is_absolute():
            prefix = Path('business_portfolio') / 'niches'
            candidate = self.repo / candidate if candidate.is_relative_to(prefix) else self.niches / candidate
        try:
            candidate = _safe_path(self.niches, candidate)
        except OSError as exc:
            raise CoordinatorError('Choose an existing portfolio folder') from exc
        if not candidate.is_dir() or any(part.startswith('.') or part in {'private', 'projects'}
                                         for part in candidate.relative_to(self.niches).parts):
            raise CoordinatorError('Choose a folder in the project tree')
        return candidate.relative_to(self.repo).as_posix()

    @staticmethod
    def _control(db):
        row = db.execute('SELECT * FROM settings WHERE id=1').fetchone()
        return {'mode': row['mode'], 'stopped': bool(row['stopped']),
                'emergency': bool(row['emergency']), 'max_workers': row['max_workers'], 'mode_epoch': row['mode_epoch']}

    def control(self):
        with self._database() as db:
            return self._control(db)

    @staticmethod
    def _log(db, kind, detail, *, project_id=None, worker_id=None):
        db.execute('INSERT INTO history(project_id,worker_id,kind,detail,created_at) VALUES (?,?,?,?,?)',
                   (project_id, worker_id, kind, detail, time.time()))

    @staticmethod
    def _worker(db, worker_id):
        row = db.execute('SELECT * FROM workers WHERE id=?', (worker_id,)).fetchone()
        if row is None:
            raise CoordinatorError('Unknown worker')
        return row

    def worker(self, worker_id):
        """Look up one registered worker for trusted host routing."""
        with self._database() as db:
            return dict(self._worker(db, worker_id))

    def register(self, folder=None, *, kind='manual', label=None, session_ref=None, worker_key=None):
        folder = self._folder(folder)
        if kind not in {'manual', 'background'}:
            raise CoordinatorError('Unknown worker kind')
        label = _text(label or 'Codex worker', 'worker label', 120)
        if session_ref is not None:
            session_ref = _text(session_ref, 'session reference', 200)
        if worker_key is not None and (kind != 'manual' or not isinstance(worker_key, str)
                                       or not re.fullmatch(r'[a-f0-9]{64}', worker_key)):
            raise CoordinatorError('Invalid chat registration key')
        with self._database(write=True) as db:
            self._expire(db)
            control = self._control(db)
            if control['stopped'] or control['emergency']:
                raise CoordinatorError('Resume Portfolio Manager before starting a worker')
            self._worker_limit(db, control['max_workers'])
            worker_id = uuid4().hex
            db.execute('INSERT INTO workers VALUES (?,?,?,?,?,?,?,NULL)',
                       (worker_id, folder, kind, label, 'running', session_ref, time.time()))
            if worker_key:
                db.execute('INSERT INTO worker_credentials VALUES (?,?)',
                           (worker_id, hashlib.sha256(worker_key.encode()).hexdigest()))
            self._log(db, 'worker_registered', label, worker_id=worker_id)
            return dict(self._worker(db, worker_id))

    def verify_manual_worker(self, worker_id, worker_key):
        if not isinstance(worker_key, str) or not re.fullmatch(r'[a-f0-9]{64}', worker_key):
            raise CoordinatorError('Use the private key returned by chat registration')
        with self._database() as db:
            row = db.execute('SELECT proof_hash FROM worker_credentials WHERE worker_id=?', (worker_id,)).fetchone()
        if row is None or not secrets.compare_digest(row['proof_hash'], hashlib.sha256(worker_key.encode()).hexdigest()):
            raise CoordinatorError('The chat registration key does not match this worker')

    @staticmethod
    def _worker_limit(db, maximum):
        if db.execute("SELECT COUNT(*) FROM workers WHERE state='running'").fetchone()[0] >= maximum:
            raise CoordinatorError('The worker limit has been reached')

    def set_mode(self, mode):
        if mode not in {'afk', 'human'}:
            raise CoordinatorError('Choose AI Only or Human Available')
        with self._database(write=True) as db:
            previous = self._control(db)['mode']
            if mode != previous:
                db.execute('UPDATE settings SET mode=?,mode_epoch=mode_epoch+1 WHERE id=1', (mode,))
                db.execute("UPDATE requests SET status='revoked' WHERE status='approved'")
                self._log(db, 'mode_changed', mode)
            return self._control(db)

    def _withdraw(self, db, lease, reason):
        db.execute("UPDATE tasks SET status='reconcile',checkpoint=?,updated_at=? WHERE project_id=? AND id=?",
                   (reason, time.time(), lease['project_id'], lease['task_id']))
        db.execute("UPDATE workers SET state='paused',last_error=? WHERE id=?", (reason, lease['worker_id']))
        db.execute('DELETE FROM leases WHERE token=?', (lease['token'],))
        self._log(db, 'reconciliation_required', reason,
                  project_id=lease['project_id'], worker_id=lease['worker_id'])

    def _expire(self, db):
        for lease in db.execute('SELECT * FROM leases WHERE expires_at<=?', (time.time(),)).fetchall():
            self._withdraw(db, lease, 'Worker contact was lost. Review the checkpoint and any external effects before resuming.')
        now = time.time()
        db.execute("UPDATE requests SET status='expired' WHERE status IN ('approved','manual_completed') AND expires_at<=?", (now,))
        expired = db.execute("SELECT DISTINCT project_id,task_id FROM requests WHERE status IN ('pending','deferred') AND expires_at<=?", (now,)).fetchall()
        db.execute("UPDATE requests SET status='expired' WHERE status IN ('pending','deferred') AND expires_at<=?", (now,))
        for row in expired:
            db.execute("UPDATE tasks SET status='blocked',checkpoint=?,updated_at=? WHERE project_id=? AND id=? AND status='waiting'",
                       ('The human request expired. Review the task before asking again.', now, row['project_id'], row['task_id']))
        db.execute("""UPDATE workers SET state='paused',last_error=? WHERE state='running' AND kind='manual' AND heartbeat_at<=?
                   AND id NOT IN (SELECT worker_id FROM leases)""",
                   ('Worker contact was lost. Resume or attach again to continue.', now - self.lease_seconds * 2))

    def recover_controller(self, *, include_manual=False):
        """Called once by a newly started singleton host before worker restore.

        An independently connected manual chat still owns its claim and must
        heartbeat it. Every background execution belonged to the previous host.
        """
        with self._database(write=True) as db:
            self._expire(db)
            leases = db.execute('SELECT leases.* FROM leases JOIN workers ON workers.id=leases.worker_id '
                                'WHERE workers.kind=? OR ?', ('background', int(include_manual))).fetchall()
            for lease in leases:
                self._withdraw(db, lease, 'The controller restarted during work. Review the saved checkpoint before resuming.')
            return len(leases)

    def stop_all(self, *, emergency=False):
        with self._database(write=True) as db:
            db.execute('UPDATE settings SET stopped=1,emergency=MAX(emergency,?),mode_epoch=mode_epoch+1 WHERE id=1',
                       (int(emergency),))
            db.execute("UPDATE requests SET status='revoked' WHERE status='approved'")
            for lease in db.execute('SELECT * FROM leases').fetchall():
                self._withdraw(db, lease, 'Stopped by the owner. Review the checkpoint before restarting this task.')
            db.execute("UPDATE workers SET state='paused' WHERE state='running'")
            self._log(db, 'emergency_stop' if emergency else 'stop_all', 'Stopped by owner')
            return self._control(db)

    def resume(self, *, clear_emergency=False):
        with self._database(write=True) as db:
            if self._control(db)['emergency'] and not clear_emergency:
                raise CoordinatorError('Emergency Stop requires an explicit reset')
            db.execute('UPDATE settings SET stopped=0,emergency=0 WHERE id=1')
            self._log(db, 'resumed', 'Owner resumed the coordinator')
            return self._control(db)

    def set_worker_state(self, worker_id, state):
        if state not in {'running', 'paused', 'stopped'}:
            raise CoordinatorError('Unknown worker state')
        with self._database(write=True) as db:
            worker = self._worker(db, worker_id)
            if state == 'running' and worker['state'] != 'running':
                control = self._control(db)
                if control['stopped'] or control['emergency']:
                    raise CoordinatorError('Resume Portfolio Manager before starting a worker')
                self._worker_limit(db, control['max_workers'])
            if state != 'running':
                lease = db.execute('SELECT * FROM leases WHERE worker_id=?', (worker_id,)).fetchone()
                if lease:
                    self._withdraw(db, lease, 'Worker interrupted. Review the checkpoint before retrying.')
            db.execute('UPDATE workers SET state=?,heartbeat_at=? WHERE id=?', (state, time.time(), worker_id))
            return dict(self._worker(db, worker_id))

    @staticmethod
    def _canonical_eligible(record):
        return record['work_state'] in _DISPATCH_STATES and record['record_type'] not in _SKIP_TYPES

    @staticmethod
    def _tasks(db, project_id):
        return db.execute('SELECT * FROM tasks WHERE project_id=? ORDER BY position', (project_id,)).fetchall()

    @staticmethod
    def _task(row):
        task = dict(row)
        task['depends_on'] = json.loads(task['depends_on'])
        task['verification'] = json.loads(task['verification']) if task['verification'] else None
        task['evidence'] = json.loads(task['evidence']) if task['evidence'] else None
        task['provisional'] = bool(task['provisional'])
        return task

    @staticmethod
    def _insert_task(db, project_id, position, milestone, *, provisional=False):
        db.execute("""INSERT INTO tasks(project_id,id,position,title,criteria,weight,depends_on,
                   verification,provisional,status,updated_at) VALUES (?,?,?,?,?,?,?,?,?,'queued',?)""",
                   (project_id, milestone['id'], position, milestone['title'], milestone['criteria'],
                    milestone['weight'], _json(milestone['depends_on']),
                    _json(milestone['verification']) if milestone['verification'] else None,
                    int(provisional), time.time()))

    def configure_plan(self, project_id, milestones):
        records, _ = self._catalog()
        if project_id not in records:
            raise CoordinatorError('Unknown project')
        if not isinstance(milestones, list) or not 1 <= len(milestones) <= 100:
            raise CoordinatorError('Provide between 1 and 100 milestones')
        plan = {}
        for raw in milestones:
            if not isinstance(raw, dict):
                raise CoordinatorError('Invalid milestone')
            name = _text(raw.get('id'), 'milestone ID', 80)
            if not _TASK_ID.fullmatch(name) or name in plan:
                raise CoordinatorError('Invalid or duplicate milestone ID')
            weight = raw.get('weight')
            if type(weight) not in (int, float) or not math.isfinite(weight) or not 0 < weight <= 100000:
                raise CoordinatorError('Milestone weight must be positive and finite')
            deps = raw.get('depends_on', [])
            if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
                raise CoordinatorError('Invalid task dependencies')
            verification = raw.get('verification')
            if verification is not None:
                if (not isinstance(verification, dict) or set(verification) != {'kind', 'name'}
                    or verification['kind'] != 'artifact' or not isinstance(verification['name'], str)
                    or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\.(md|txt|json|csv)', verification['name'])):
                    raise CoordinatorError('Artifact verification requires a simple text filename')
            plan[name] = dict(id=name, title=_text(raw.get('title'), 'milestone title', 500),
                              criteria=_text(raw.get('criteria'), 'completion criteria'), weight=weight,
                              depends_on=deps, verification=verification)
        self._validate_dependencies(plan)
        with self._database(write=True) as db:
            previous = self._tasks(db, project_id)
            if any(row['status'] != 'queued' and not row['provisional'] for row in previous):
                raise CoordinatorError('Existing verified or in-progress milestones must be preserved')
            if any(row['status'] in {'working', 'waiting', 'reconcile'} for row in previous):
                raise CoordinatorError('Finish or reconcile current work before replacing the plan')
            for row in previous:
                if row['checkpoint']:
                    self._log(db, 'prior_checkpoint', _json(self._task(row)), project_id=project_id)
            db.execute("UPDATE requests SET status='revoked' WHERE project_id=? AND status IN ('approved','manual_completed')",
                       (project_id,))
            db.execute('DELETE FROM tasks WHERE project_id=?', (project_id,))
            for position, milestone in enumerate(plan.values()):
                self._insert_task(db, project_id, position, milestone)
            self._log(db, 'plan_configured', f'{len(plan)} milestones', project_id=project_id)
            return [self._task(row) for row in self._tasks(db, project_id)]

    @staticmethod
    def _validate_dependencies(plan):
        visited = set()
        active = set()

        def visit(name):
            if name in active:
                raise CoordinatorError('Task dependencies contain a cycle')
            if name not in plan:
                raise CoordinatorError('Unknown task dependency')
            if name in visited:
                return
            active.add(name)
            for dep in plan[name]['depends_on']:
                visit(dep)
            active.remove(name)
            visited.add(name)

        for name in plan:
            visit(name)

    def _ready_task(self, record, rows):
        if not rows:
            return None
        completed = {row['id'] for row in rows if row['status'] == 'completed' and self._evidence_valid(record['id'], row)}
        for row in rows:
            if row['status'] == 'queued' and set(json.loads(row['depends_on'])).issubset(completed):
                return row
        return None

    @staticmethod
    def _project_dependencies(record, records, verified):
        deps = record.get('depends_on', [])
        return (isinstance(deps, list) and all(isinstance(dep, str) and dep in records
                    and dep in verified for dep in deps))

    def _verified_projects(self, tasks_by_id):
        return {pid for pid, tasks in tasks_by_id.items() if tasks and
                all(row['status'] == 'completed' and not row['provisional']
                    and self._evidence_valid(pid, row) for row in tasks)}

    def claim(self, worker_id):
        records, _ = self._catalog()
        with self._database(write=True) as db:
            self._expire(db)
            worker = self._worker(db, worker_id)
            control = self._control(db)
            if control['stopped'] or control['emergency'] or worker['state'] != 'running':
                return None
            existing = db.execute('SELECT * FROM leases WHERE worker_id=?', (worker_id,)).fetchone()
            if existing:
                raise CoordinatorError('Worker already has an active claim')
            leased = {row[0] for row in db.execute('SELECT project_id FROM leases')}
            if len(leased) >= control['max_workers']:
                return None
            tasks_by_id = self._tasks_by_id(db)
            verified = self._verified_projects(tasks_by_id)
            candidates = sorted(records.values(), key=lambda r: (_PRIORITY.get(r['priority'], 10),
                                r['work_state'] != 'active', r['id']))
            for record in candidates:
                pid = record['id']
                if (pid in leased or not self._canonical_eligible(record)
                    or not PurePosixPath('business_portfolio/' + record['path']).is_relative_to(worker['folder'])
                    or not self._project_dependencies(record, records, verified)
                    or self._unreconciled_effect(db, pid)):
                    continue
                rows = tasks_by_id.get(pid, [])
                if not rows:
                    provisional = {'id': 'next-action', 'title': record['next_action'],
                                   'criteria': 'Record verified work and the next safe step for this project.',
                                   'weight': 1, 'depends_on': [], 'verification': None}
                    self._insert_task(db, pid, 0, provisional, provisional=True)
                    rows = self._tasks(db, pid)
                task = self._ready_task(record, rows)
                if task is None or any(row['status'] == 'reconcile' for row in rows):
                    continue
                record_path = 'business_portfolio/' + record['path']
                if _digest(_safe_path(self.niches, self.repo / record_path)) != record['content_sha256']:
                    continue  # Catalog changed during selection. A later claim re-reads it.
                token = uuid4().hex
                now = time.time()
                db.execute('INSERT INTO leases VALUES (?,?,?,?,?,?,?)',
                           (pid, task['id'], worker_id, token, record_path, record['content_sha256'], now + self.lease_seconds))
                db.execute("UPDATE tasks SET status='working',updated_at=? WHERE project_id=? AND id=?", (now, pid, task['id']))
                db.execute('UPDATE workers SET heartbeat_at=?,last_error=NULL WHERE id=?', (now, worker_id))
                self._log(db, 'claimed', task['id'], project_id=pid, worker_id=worker_id)
                lease = db.execute('SELECT * FROM leases WHERE token=?', (token,)).fetchone()
                return self._claim_info(db, lease)
            db.execute('UPDATE workers SET heartbeat_at=? WHERE id=?', (time.time(), worker_id))
            return None

    @staticmethod
    def _tasks_by_id(db):
        tasks = {}
        for row in db.execute('SELECT * FROM tasks ORDER BY project_id,position'):
            tasks.setdefault(row['project_id'], []).append(row)
        return tasks

    @staticmethod
    def _unreconciled_effect(db, project_id):
        return bool(db.execute("SELECT 1 FROM effects WHERE project_id=? AND state='uncertain'", (project_id,)).fetchone())

    def _claim_info(self, db, lease):
        task = self._task(db.execute('SELECT * FROM tasks WHERE project_id=? AND id=?',
                                    (lease['project_id'], lease['task_id'])).fetchone())
        requests = db.execute("SELECT * FROM requests WHERE project_id=? AND task_id=? AND status IN ('approved','manual_completed') AND expires_at>?",
                              (lease['project_id'], lease['task_id'], time.time())).fetchall()
        return {'project_id': lease['project_id'], 'record_path': lease['record_path'],
                'record_sha256': lease['record_sha256'], 'lease_token': lease['token'],
                'worker_id': lease['worker_id'], 'task_id': lease['task_id'], 'task': task,
                'checkpoint': task['checkpoint'], 'human_responses': [self._request(row) for row in requests
                                                                      if row['record_sha256'] == lease['record_sha256']],
                'prior_artifacts': self._prior_artifacts(db, lease['project_id']),
                'expires_at': lease['expires_at']}

    def _prior_artifacts(self, db, project_id):
        rows = [self._task(row) for row in self._tasks(db, project_id) if row['status'] == 'completed']
        rows.extend(json.loads(row['detail']) for row in db.execute(
            "SELECT detail FROM history WHERE project_id=? AND kind='prior_checkpoint' ORDER BY sequence DESC LIMIT 20",
            (project_id,)))
        artifacts = []
        seen = set()
        for row in sorted(rows, key=lambda item: item['updated_at'], reverse=True):
            evidence = row.get('evidence')
            if not evidence or evidence['path'] in seen:
                continue
            try:
                self._verify_evidence(project_id, evidence, row)
            except (ValueError, OSError):
                continue
            artifacts.append(evidence)
            seen.add(evidence['path'])
            if len(artifacts) == 3:
                break
        return artifacts

    def _lease(self, db, worker_id, token):
        lease = db.execute('SELECT * FROM leases WHERE worker_id=? AND token=? AND expires_at>?',
                           (worker_id, token, time.time())).fetchone()
        control = self._control(db)
        if lease is None or control['stopped'] or control['emergency'] or self._worker(db, worker_id)['state'] != 'running':
            raise CoordinatorError('The worker claim is no longer active')
        return lease

    def heartbeat(self, worker_id, lease_token):
        with self._database(write=True) as db:
            self._expire(db)
            try:
                self._lease(db, worker_id, lease_token)
            except CoordinatorError:
                return False
            now = time.time()
            db.execute('UPDATE leases SET expires_at=? WHERE token=?', (now + self.lease_seconds, lease_token))
            db.execute('UPDATE workers SET heartbeat_at=? WHERE id=?', (now, worker_id))
            return True

    def _record_path(self, lease):
        path = _safe_path(self.niches, self.repo / lease['record_path'])
        if _digest(path) != lease['record_sha256']:
            raise CoordinatorError('Project record changed. Reconcile before applying this work.')
        return path

    def guard_lease(self, worker_id, lease_token, callback):
        """Run a short, trusted host-only publication callback under the claim lock."""
        with self._database(write=True) as db:
            lease = self._lease(db, worker_id, lease_token)
            self._record_path(lease)
            return callback(self._claim_info(db, lease))

    def apply_checkpoint(self, worker_id, lease_token, *, expected_sha256, text):
        """Append an exact, validated canonical checkpoint under the claim lock."""
        if not isinstance(text, str) or len(text) > 500_000:
            raise CoordinatorError('Invalid checkpoint document')
        with self._database(write=True) as db:
            lease = self._lease(db, worker_id, lease_token)
            path = self._record_path(lease)
            if lease['record_sha256'] != expected_sha256:
                raise CoordinatorError('Checkpoint is based on a stale project record')
            old_meta, old_body = build_browser.parse_project(path.read_text(encoding='utf-8'))
            new_meta, new_body = build_browser.parse_project(text)
            if new_meta != old_meta or not new_body.startswith(old_body + '\n'):
                raise CoordinatorError('Checkpoint must preserve metadata and append to the existing record')
            self._record_path(lease)
            build_browser.atomic_text(path, text)
            digest = _digest(path)
            db.execute('UPDATE leases SET record_sha256=? WHERE token=?', (digest, lease_token))
            self._log(db, 'canonical_checkpoint', digest, project_id=lease['project_id'], worker_id=worker_id)
            return {'record_path': lease['record_path'], 'record_sha256': digest}

    def _verify_evidence(self, project_id, evidence, task=None):
        if not isinstance(evidence, dict) or evidence.get('kind') not in {'verified_artifact', 'passed_test'}:
            raise CoordinatorError('Completion requires an artifact or test result verified by the host')
        name = _text(evidence.get('path'), 'evidence path', 600)
        expected = evidence.get('sha256')
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
            raise CoordinatorError('Completion evidence requires a SHA-256 digest')
        path = Path(name)
        if not path.is_absolute():
            path = self.repo / path
        # A private artifact is scoped by the verified task's lease, never by
        # a model-controlled URL or by a general repository file path.
        scopes = (self.portfolio / 'results' / project_id, self.db_path.parent / 'worker-runs' / project_id)
        scope = next((r for r in scopes if path.is_relative_to(r)), None)
        if scope is None:
            raise CoordinatorError('Evidence is outside the project result or private state directory')
        try:
            root = self.portfolio if scope.is_relative_to(self.portfolio) else self.db_path.parent
            resolved = _safe_path(root, path)
            if not resolved.is_file() or resolved.stat().st_size > 8_000_000 or _digest(resolved) != expected:
                raise CoordinatorError('Completion evidence is missing or has changed')
        except OSError as exc:
            raise CoordinatorError('Completion evidence is unavailable') from exc
        if task and task.get('verification') and resolved.name != task['verification']['name']:
            raise CoordinatorError('Completion evidence does not match the milestone verification rule')
        return {'kind': evidence['kind'], 'path': name, 'sha256': expected, 'verified_at': time.time()}

    def _evidence_valid(self, project_id, row):
        try:
            self._verify_evidence(project_id, json.loads(row['evidence']) if row['evidence'] else None, self._task(row))
        except (ValueError, OSError, TypeError):
            return False
        return True

    def finish(self, worker_id, lease_token, *, outcome, summary, evidence=None, session_ref=None):
        transitions = {'completed': 'completed', 'blocked': 'blocked', 'waiting': 'waiting',
                       'paused': 'queued', 'retry': 'queued'}
        if outcome not in transitions:
            raise CoordinatorError('Unknown task outcome')
        summary = _text(summary, 'checkpoint summary', 12000)
        if session_ref is not None:
            session_ref = _text(session_ref, 'session reference', 200)
        with self._database(write=True) as db:
            lease = self._lease(db, worker_id, lease_token)
            pid, task_id = lease['project_id'], lease['task_id']
            verified = None
            status = transitions[outcome]
            if self._unreconciled_effect(db, pid):
                status = 'reconcile'
            elif outcome == 'completed':
                self._record_path(lease)
                verified = self._verify_evidence(pid, evidence, self._claim_info(db, lease)['task'])
            elif outcome == 'waiting':
                raise CoordinatorError('Use request_human to save a specific waiting request')
            now = time.time()
            db.execute('UPDATE tasks SET status=?,checkpoint=?,evidence=?,updated_at=? WHERE project_id=? AND id=?',
                       (status, summary, _json(verified) if verified else None, now, pid, task_id))
            db.execute('DELETE FROM leases WHERE token=?', (lease_token,))
            db.execute('UPDATE workers SET heartbeat_at=?,session_ref=COALESCE(?,session_ref),last_error=? WHERE id=?',
                       (now, session_ref, summary if status in {'blocked', 'reconcile'} else None, worker_id))
            if outcome == 'paused':
                db.execute("UPDATE workers SET state='paused' WHERE id=?", (worker_id,))
            self._log(db, status, summary, project_id=pid, worker_id=worker_id)
            return self._task(db.execute('SELECT * FROM tasks WHERE project_id=? AND id=?', (pid, task_id)).fetchone())

    @staticmethod
    def _request(row):
        request = dict(row)
        request['after'] = request.pop('after_action')
        return request

    def request_human(self, worker_id, lease_token, *, action, reason, scope, cost_cad=0,
                      consequences='', after='', kind='approval', ttl_seconds=3600):
        action = _text(action, 'requested action', 500)
        reason = _text(reason, 'request reason')
        scope = _text(scope, 'exact scope')
        consequences = _text(consequences, 'consequences', empty=True)
        after = _text(after, 'follow-up', empty=True)
        if kind not in {'approval', 'manual', 'login'}:
            raise CoordinatorError('Unknown request kind')
        if type(cost_cad) not in (int, float) or not math.isfinite(cost_cad) or cost_cad < 0:
            raise CoordinatorError('Invalid request cost')
        if kind != 'approval' and cost_cad:
            raise CoordinatorError('A manual or login request cannot authorize spending')
        if type(ttl_seconds) not in (int, float) or not 1 <= ttl_seconds <= 86400:
            raise CoordinatorError('Requests must expire within 24 hours')
        with self._database(write=True) as db:
            lease = self._lease(db, worker_id, lease_token)
            self._record_path(lease)
            pid, task_id = lease['project_id'], lease['task_id']
            now = time.time()
            existing = db.execute("""SELECT * FROM requests WHERE project_id=? AND task_id=?
                  AND record_sha256=? AND action=? AND scope=? AND cost_cad=? AND kind=?
                  AND status IN ('approved','manual_completed') AND expires_at>?""",
                                  (pid, task_id, lease['record_sha256'], action, scope, cost_cad, kind, now)).fetchone()
            if existing:
                return self._request(existing)
            request_id = uuid4().hex
            db.execute("""INSERT INTO requests(id,project_id,task_id,worker_id,kind,action,reason,scope,
                   cost_cad,consequences,after_action,record_sha256,status,created_at,expires_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'pending',?,?)""",
                       (request_id, pid, task_id, worker_id, kind, action, reason, scope, cost_cad,
                        consequences, after, lease['record_sha256'], now, now + ttl_seconds))
            db.execute("UPDATE tasks SET status='waiting',checkpoint=?,updated_at=? WHERE project_id=? AND id=?",
                       (reason, now, pid, task_id))
            db.execute('DELETE FROM leases WHERE token=?', (lease_token,))
            self._log(db, 'human_request', request_id, project_id=pid, worker_id=worker_id)
            return self._request(db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone())

    def resolve_request(self, request_id, decision):
        """Host owner control. A decision queues verification of the saved scope."""
        states = {'approve': 'approved', 'deny': 'denied', 'complete': 'manual_completed', 'later': 'deferred',
                  'revoke': 'revoked'}
        if decision not in states:
            raise CoordinatorError('Unknown request decision')
        records = self._catalog()[0] if decision in {'approve', 'complete'} else {}
        with self._database(write=True) as db:
            self._expire(db)
            row = db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone()
            available = {'approved', 'manual_completed'} if decision == 'revoke' else {'pending', 'deferred'}
            if row is None or row['status'] not in available or row['expires_at'] <= time.time():
                raise CoordinatorError('This request is no longer available')
            if decision in {'approve', 'complete'}:
                control = self._control(db)
                if control['mode'] != 'human' or control['stopped'] or control['emergency']:
                    raise CoordinatorError('Resume in Human Available mode before resolving this request')
                if (decision == 'approve') != (row['kind'] == 'approval'):
                    raise CoordinatorError('Use the matching approval or manual-completion action')
                record = records.get(row['project_id'])
                if (record is None or _digest(_safe_path(self.niches, self.portfolio / record['path'])) != row['record_sha256']):
                    raise CoordinatorError('The project changed while waiting. Review this request again.')
            now = time.time()
            db.execute('UPDATE requests SET status=?,decision=? WHERE id=?', (states[decision], decision, request_id))
            if decision in {'approve', 'complete', 'deny'}:
                status = 'blocked' if decision == 'deny' else 'queued'
                summary = ('The owner declined this request.' if decision == 'deny' else
                           'The owner responded. Verify the result and exact scope before continuing.')
                db.execute("UPDATE tasks SET status=?,checkpoint=?,updated_at=? WHERE project_id=? AND id=? AND status='waiting'",
                           (status, summary, now, row['project_id'], row['task_id']))
            self._log(db, 'human_' + decision, request_id, project_id=row['project_id'], worker_id=row['worker_id'])
            return self._request(db.execute('SELECT * FROM requests WHERE id=?', (request_id,)).fetchone())

    def begin_effect(self, worker_id, lease_token, *, approval_id, dedup_key, action, scope, cost_cad=0):
        """Reserve one exact owner-approved effect before the host dispatches it.

        Reservations start uncertain. An interruption never makes them eligible
        for replay. The authoritative external integration must still check its
        permissions and the provider state, then reconcile this reservation.
        """
        dedup_key = _text(dedup_key, 'effect identity', 300)
        action = _text(action, 'action', 500)
        scope = _text(scope, 'scope')
        if type(cost_cad) not in (int, float) or not math.isfinite(cost_cad) or cost_cad < 0:
            raise CoordinatorError('Invalid effect cost')
        with self._database(write=True) as db:
            lease = self._lease(db, worker_id, lease_token)
            self._record_path(lease)
            pid, task_id = lease['project_id'], lease['task_id']
            if self._control(db)['mode'] != 'human':
                raise CoordinatorError('An external effect requires Human Available mode')
            prior = db.execute('SELECT state FROM effects WHERE project_id=? AND dedup_key=?', (pid, dedup_key)).fetchone()
            if prior is not None or self._unreconciled_effect(db, pid):
                raise CoordinatorError('An earlier effect must be reconciled and cannot be replayed')
            row = db.execute("SELECT * FROM requests WHERE id=? AND status='approved' AND expires_at>?",
                             (approval_id, time.time())).fetchone()
            expected = (pid, task_id, 'approval', lease['record_sha256'], action, scope, cost_cad)
            if row is None or tuple(row[k] for k in ('project_id','task_id','kind','record_sha256','action','scope','cost_cad')) != expected:
                raise CoordinatorError('No valid owner approval for this exact effect')
            now = time.time()
            effect_id = uuid4().hex
            db.execute("INSERT INTO effects VALUES (?,?,?,?,?,?,?,?,'uncertain',NULL,?,?)",
                       (effect_id, pid, task_id, approval_id, dedup_key, action, scope, cost_cad, now, now))
            db.execute("UPDATE requests SET status='consumed' WHERE id=?", (approval_id,))
            self._log(db, 'effect_reserved', effect_id, project_id=pid, worker_id=worker_id)
            return dict(db.execute('SELECT * FROM effects WHERE id=?', (effect_id,)).fetchone())

    def reconcile_effect(self, effect_id, *, status, evidence):
        """Record trusted provider read-back. No provider request is made here."""
        if status not in {'verified', 'failed_verified'}:
            raise CoordinatorError('Use a verified provider outcome')
        evidence = _text(evidence, 'provider verification', 6000)
        with self._database(write=True) as db:
            row = db.execute("SELECT * FROM effects WHERE id=? AND state='uncertain'", (effect_id,)).fetchone()
            if row is None:
                raise CoordinatorError('No uncertain effect with that identity')
            db.execute('UPDATE effects SET state=?,evidence=?,updated_at=? WHERE id=?',
                       (status, evidence, time.time(), effect_id))
            self._log(db, 'effect_' + status, effect_id, project_id=row['project_id'])
            return dict(db.execute('SELECT * FROM effects WHERE id=?', (effect_id,)).fetchone())

    def reconcile_task(self, project_id, task_id, *, note):
        """Release a blocked or interrupted task after an owner reviews its state."""
        note = _text(note, 'reconciliation note')
        with self._database(write=True) as db:
            self._expire(db)
            if self._unreconciled_effect(db, project_id) or db.execute('SELECT 1 FROM leases WHERE project_id=?', (project_id,)).fetchone():
                raise CoordinatorError('Reconcile the external effect and release active work first')
            updated = db.execute("UPDATE tasks SET status='queued',checkpoint=?,updated_at=? WHERE project_id=? AND id=? AND status IN ('blocked','reconcile')",
                                 (note, time.time(), project_id, task_id))
            if updated.rowcount != 1:
                raise CoordinatorError('This task is not waiting for reconciliation')
            self._log(db, 'task_reconciled', note, project_id=project_id)

    def history(self, project_id, *, limit=50):
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise CoordinatorError('Invalid history limit')
        with self._database() as db:
            return [dict(row) for row in db.execute('SELECT * FROM history WHERE project_id=? ORDER BY sequence DESC LIMIT ?',
                                                     (project_id, limit))]

    def _project_view(self, record, rows, lease, ready, verified, uncertain):
        tasks = [self._task(row) for row in rows]
        for task, row in zip(tasks, rows):
            task['verified'] = row['status'] == 'completed' and self._evidence_valid(record['id'], row)
        progress = None
        if rows and not any(row['provisional'] for row in rows):
            achieved = sum(task['weight'] for task in tasks if task['verified'])
            progress = round(100 * achieved / sum(row['weight'] for row in rows), 1)
        checkpoint = max((row for row in rows if row['checkpoint']), key=lambda row: row['updated_at'], default=None)
        status = record['work_state']
        if lease:
            status = 'working'
        elif uncertain or any(row['status'] == 'reconcile' for row in rows):
            status = 'blocked'
        elif any(row['status'] == 'waiting' for row in rows):
            status = 'waiting'
        elif verified:
            status = 'completed'
        elif ready:
            status = 'queued'
        elif rows:
            status = ('checkpointed' if all(row['provisional'] and row['status'] == 'completed' for row in rows)
                      and tasks[0]['verified'] else 'blocked')
        elif self._canonical_eligible(record):
            status = 'blocked'
        active = next((task for task in tasks if lease and task['id'] == lease['task_id']), None)
        return {**record, 'project_id': record['id'], 'record_path': 'business_portfolio/' + record['path'],
                'status': status, 'worker_id': lease['worker_id'] if lease else None, 'current_task': active,
                'progress_pct': progress, 'checkpoint': checkpoint['checkpoint'] if checkpoint else None,
                'milestones': tasks, 'eligible': ready and lease is None}

    def snapshot(self, folder=None):
        selected = self._folder(folder)
        records, niches = self._catalog()
        with self._database(write=True) as db:
            self._expire(db)
            control = self._control(db)
            leases = {row['project_id']: row for row in db.execute('SELECT * FROM leases')}
            worker_leases = {row['worker_id']: row for row in leases.values()}
            tasks_by_id = self._tasks_by_id(db)
            verified = self._verified_projects(tasks_by_id)
            uncertain = {row[0] for row in db.execute("SELECT DISTINCT project_id FROM effects WHERE state='uncertain'")}
            requests = [self._request(row) for row in db.execute("SELECT * FROM requests WHERE status IN ('pending','deferred') ORDER BY created_at")]
            waiting = {row['worker_id'] for row in requests}
            workers = []
            for row in db.execute('SELECT * FROM workers ORDER BY heartbeat_at DESC'):
                lease = worker_leases.get(row['id'])
                status = row['state'] if row['state'] != 'running' else ('working' if lease else
                         'waiting' if row['id'] in waiting else 'idle')
                workers.append({**dict(row), 'status': status, 'project_id': lease['project_id'] if lease else None,
                                'task_id': lease['task_id'] if lease else None})
            projects = []
            for pid, record in records.items():
                if not PurePosixPath('business_portfolio/' + record['path']).is_relative_to(selected):
                    continue
                rows = tasks_by_id.get(pid, [])
                ready = (self._canonical_eligible(record) and self._project_dependencies(record, records, verified)
                         and pid not in uncertain and not any(row['status'] == 'reconcile' for row in rows)
                         and (not rows or self._ready_task(record, rows) is not None))
                projects.append(self._project_view(record, rows, leases.get(pid), ready, pid in verified, pid in uncertain))
                if control['stopped']:
                    projects[-1]['eligible'] = False
            completed = sum(p['status'] == 'completed' for p in projects)
            counts = {'total': len(projects), 'eligible': sum(p['eligible'] for p in projects),
                      'active': sum(p['status'] == 'working' for p in projects), 'completed': completed,
                      'blocked': sum(p['status'] in {'blocked', 'waiting', 'needs_reconciliation'} for p in projects),
                      'remaining': sum(p['status'] in {'queued','working','waiting','blocked','needs_reconciliation'} for p in projects)}
            return {**control, 'folder': selected, 'projects': projects, 'workers': workers,
                    'requests': requests, 'counts': counts, 'niches': niches}
