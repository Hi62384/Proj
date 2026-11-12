"""Persistent chat contexts backed by the coordinator database."""
import hashlib
from pathlib import Path
import re
import secrets

from business_portfolio.tools.build_browser import linked_input


def context_path(repo, value):
    if not isinstance(value, (str, Path)) or len(str(value)) > 1000:
        raise ValueError('Choose a repository file or folder.')
    repo = Path(repo).resolve(strict=True)
    path = Path(value)
    candidate = path if path.is_absolute() else repo / path
    if not candidate.is_relative_to(repo):
        raise ValueError('Choose a file or folder inside this repository.')
    relative = candidate.relative_to(repo)
    for part in relative.parts:
        name = part.lower()
        if (part.startswith('.') or ':' in part or name in {
            'private', 'outputs', 'node_modules', '__pycache__', 'credentials',
            'auth.json', 'secrets', 'secret', 'venv', 'id_rsa', 'id_ed25519',
        } or name.endswith(('.sqlite', '.sqlite3', '.pem', '.key', '.pfx'))):
            raise ValueError('This location is excluded from the workspace explorer.')
    for path in (candidate, *candidate.parents):
        if linked_input(path):
            raise ValueError('Linked files and folders are excluded.')
        if path == repo:
            break
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(repo) or not (resolved.is_dir() or resolved.is_file()):
        raise ValueError('Choose an ordinary repository file or folder.')
    return resolved


class ChatWorkspaces:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        with coordinator._database(write=True) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS chat_workspaces(
                id TEXT PRIMARY KEY, client TEXT UNIQUE NOT NULL, proof TEXT NOT NULL,
                selection TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0, worker_id TEXT
            )""")

    @staticmethod
    def _public(row):
        return {k: row[k] for k in ('id', 'selection', 'revision', 'worker_id')}

    def attach(self, client, key=None):
        if not isinstance(client, str) or not re.fullmatch(r'[a-f0-9]{32}', client):
            raise ValueError('A valid authenticated connection is required.')
        with self.coordinator._database(write=True) as db:
            current = db.execute('SELECT * FROM chat_workspaces WHERE client=?', (client,)).fetchone()
            if key is not None:
                if not isinstance(key, str) or not re.fullmatch(r'[a-f0-9]{64}', key):
                    raise ValueError('Invalid workspace reconnect key.')
                proof = hashlib.sha256(key.encode()).hexdigest()
                row = db.execute('SELECT * FROM chat_workspaces WHERE proof=?', (proof,)).fetchone()
                if not row or (current and current['id'] != row['id']):
                    raise PermissionError('This connection cannot reconnect that workspace.')
                db.execute('UPDATE chat_workspaces SET client=? WHERE id=?', (client, row['id']))
                return self._public(row)
            if current:
                return self._public(current)
            key = secrets.token_hex(32)
            ident = secrets.token_hex(16)
            selection = 'business_portfolio/niches'
            db.execute('INSERT INTO chat_workspaces(id,client,proof,selection) VALUES(?,?,?,?)',
                       (ident, client, hashlib.sha256(key.encode()).hexdigest(), selection))
            return dict(id=ident, selection=selection, revision=0, worker_id=None, reconnect_key=key)

    def get(self, ident):
        with self.coordinator._database() as db:
            row = db.execute('SELECT * FROM chat_workspaces WHERE id=?', (ident,)).fetchone()
            if not row:
                raise ValueError('Unknown chat workspace.')
            return self._public(row)

    def select(self, ident, selection, revision=None, *, client=None):
        repo = self.coordinator.repo
        relative = context_path(repo, selection).relative_to(repo).as_posix()
        with self.coordinator._database(write=True) as db:
            row = db.execute('SELECT * FROM chat_workspaces WHERE id=?', (ident,)).fetchone()
            if not row or (client is not None and client != row['client']):
                raise PermissionError('This connection does not own the workspace.')
            if revision is not None and revision != row['revision']:
                raise ValueError('The selection changed. Refresh it before updating.')
            if relative != row['selection']:
                db.execute('UPDATE chat_workspaces SET selection=?,revision=revision+1 WHERE id=?',
                           (relative, ident))
            return self._public(db.execute('SELECT * FROM chat_workspaces WHERE id=?', (ident,)).fetchone())

    def assign(self, ident, worker_id):
        with self.coordinator._database(write=True) as db:
            db.execute('UPDATE chat_workspaces SET worker_id=?,revision=revision+1 WHERE id=?',
                       (worker_id, ident))
