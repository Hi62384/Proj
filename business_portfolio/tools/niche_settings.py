"""Atomic, validated writes for the niche-level focus flag."""
import json
import os
from pathlib import Path
import tempfile
import time


def set_working(root: Path, niche_id: str, working: bool) -> dict:
    if not isinstance(working, bool):
        raise ValueError('working must be a boolean')
    root = Path(root).resolve(strict=True)
    lock = root / '.niche-working.lock'
    deadline = time.monotonic() + 3
    fd = None
    while fd is None:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > 30:
                    lock.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError('Another window is updating niche settings.')
            time.sleep(.025)
    try:
        rows = []
        for path in (root / 'niches').rglob('NICHE.json'):
            meta = json.loads(path.read_text(encoding='utf-8'))
            if meta.get('id') == niche_id:
                rows.append((path, meta))
        if len(rows) != 1:
            raise ValueError('Unknown or duplicate niche ID.')
        path, meta = rows[0]
        if meta.get('path') != path.parent.relative_to(root / 'niches').as_posix():
            raise ValueError('Niche path changed; refresh Portfolio Manager.')
        if not isinstance(meta.get('working', False), bool):
            raise ValueError('Niche working metadata is invalid.')
        meta['working'] = working
        content = json.dumps(meta, ensure_ascii=False, indent=2) + '\n'
        temp = None
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n',
                                             dir=path.parent, delete=False) as stream:
                temp = Path(stream.name)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if temp and temp.exists():
                temp.unlink()
        return meta
    finally:
        os.close(fd)
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
