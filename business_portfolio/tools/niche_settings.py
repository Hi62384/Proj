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
        rows = {}
        for path in (root / 'niches').rglob('NICHE.json'):
            meta = json.loads(path.read_text(encoding='utf-8'))
            ident = meta.get('id')
            if not ident or ident in rows:
                raise ValueError('Unknown or duplicate niche ID.')
            if meta.get('path') != path.parent.relative_to(root / 'niches').as_posix():
                raise ValueError('Niche path changed; refresh Portfolio Manager.')
            if not isinstance(meta.get('working'), bool):
                raise ValueError('Niche working metadata is invalid.')
            rows[ident] = (path, meta)
        if niche_id not in rows:
            raise ValueError('Unknown niche ID.')
        path, meta = rows[niche_id]
        if not working:
            prefix = meta['path'] + '/'
            if any(other['path'].startswith(prefix) and other['working'] for _, other in rows.values()):
                raise ValueError('Turn off Working in descendant niches first.')
            changes = [(path, meta)]
        else:
            changes = []
            seen = set()
            current = niche_id
            while current is not None:
                if current in seen or current not in rows:
                    raise ValueError('Niche parent chain is invalid.')
                seen.add(current)
                parent_path, parent_meta = rows[current]
                expected = parent_meta['path'].rsplit('/', 1)[0] if '/' in parent_meta['path'] else None
                parent_id = parent_meta.get('parent')
                if (expected is None) != (parent_id is None) or (parent_id is not None and
                        (parent_id not in rows or rows[parent_id][1]['path'] != expected)):
                    raise ValueError('Niche parent chain is invalid.')
                changes.append((parent_path, parent_meta))
                current = parent_id
            changes.reverse()  # Parent first keeps the visibility invariant during writes.
        for target, entry in changes:
            if entry['working'] == working:
                continue
            entry['working'] = working
            content = json.dumps(entry, ensure_ascii=False, indent=2) + '\n'
            temp = None
            try:
                with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n',
                                                 dir=target.parent, delete=False) as stream:
                    temp = Path(stream.name)
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temp, target)
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
