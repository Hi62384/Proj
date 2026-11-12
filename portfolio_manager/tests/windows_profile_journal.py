"""Crash-visible test-profile ownership records. Never deletes profiles itself."""
import json
import os
from pathlib import Path
import re
import uuid
import msvcrt


class ProfileJournal:
    def __init__(self, root, identifier):
        if not re.fullmatch(r'[0-9a-f]{32}', identifier):
            raise ValueError('Invalid journal identifier')
        self.identifier = identifier
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        if self.root.is_symlink():
            raise ValueError('Journal directory cannot be a symlink')
        self.path = self.root / (identifier + '.json')
        self.lock_path = self.root / (identifier + '.lock')
        self._lock = self.lock_path.open('x+b')
        try:
            self._lock.write(b'1'); self._lock.flush(); self._lock.seek(0)
            msvcrt.locking(self._lock.fileno(), msvcrt.LK_NBLCK, 1)
            self.value = {'version': 2, 'id': identifier, 'owner_pid': os.getpid(), 'pending': None, 'created': []}
            # Exclusive creation prevents claiming an existing record.
            with self.path.open('x', encoding='utf-8') as file:
                json.dump(self.value, file); file.flush(); os.fsync(file.fileno())
        except BaseException:
            self._lock.close(); self.lock_path.unlink(missing_ok=True)
            raise

    def update(self, *, pending, created):
        expected = {'PortfolioManager.A.' + self.identifier + '.model',
                    'PortfolioManager.A.' + self.identifier + '.test'}
        if pending is not None and pending not in expected:
            raise ValueError('Unexpected pending profile')
        if len(created) != len(set(created)) or not set(created).issubset(expected):
            raise ValueError('Unexpected owned profile list')
        value = {'version': 2, 'id': self.identifier, 'owner_pid': os.getpid(),
                 'pending': pending, 'created': list(created)}
        temp = self.root / (self.identifier + '.' + uuid.uuid4().hex + '.tmp')
        try:
            with temp.open('x', encoding='utf-8') as file:
                json.dump(value, file); file.flush(); os.fsync(file.fileno())
            os.replace(temp, self.path)
            self.value = value
        finally:
            temp.unlink(missing_ok=True)

    def finish(self):
        if self.value['pending'] is not None or self.value['created']:
            raise RuntimeError('Cannot remove a journal with unresolved profiles')
        self.path.unlink()
        self._lock.seek(0); msvcrt.locking(self._lock.fileno(), msvcrt.LK_UNLCK, 1)
        self._lock.close(); self.lock_path.unlink()
