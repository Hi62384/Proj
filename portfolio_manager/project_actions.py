"""Owner actions on canonical project records."""
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import tempfile
from uuid import uuid4

from business_portfolio.tools import build_browser
from .workspace import context_path


def _record(repo, selection, expected_hash):
    repo = Path(repo).resolve()
    path = context_path(repo, selection)
    base = repo / 'business_portfolio' / 'niches'
    if not (path.is_file() and path.suffix.lower() == '.md' and path.parent.name == 'projects'
            and path.is_relative_to(base)):
        raise ValueError('Select an active project record.')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError('The project changed. Refresh it before trying again.')
    meta, _ = build_browser.parse_project(raw.decode('utf-8'), str(path))
    return path, raw, meta


def update_project(host, selection, expected_hash, action):
    if action not in {'complete', 'reopen', 'delete'}:
        raise ValueError('Unknown project action.')
    repo = Path(host.repo).resolve()
    path, raw, meta = _record(repo, selection, expected_hash)
    portfolio = repo / 'business_portfolio'
    with host.coordinator._database(write=True) as db:
        if db.execute('SELECT 1 FROM leases WHERE project_id=?', (meta['id'],)).fetchone():
            raise ValueError('This project is currently claimed. Finish or stop that work first.')
        _record(repo, selection, expected_hash)
        if action == 'delete':
            data = build_browser.load_portfolio(portfolio)
            dependents = [r['id'] for r in data['records'] if r['id'] != meta['id'] and
                          (r['parent_project'] == meta['id'] or meta['id'] in r['related_projects'])]
            if dependents:
                raise ValueError('Other project records reference this project: ' + ', '.join(dependents) +
                                 '. Resolve those references before deleting it.')
            trash = portfolio / '.local' / 'project-trash'
            trash.mkdir(parents=True, exist_ok=True)
            saved = trash / (meta['id'] + '-' + uuid4().hex + '.md')
            os.replace(path, saved)
            try:
                build_browser.build(portfolio)
            except Exception:
                os.replace(saved, path)
                raise
            return saved
        if action == 'complete':
            if meta['work_state'] == 'completed':
                return None
            meta['owner_completion_previous_work_state'] = meta['work_state']
            meta['work_state'] = 'completed'
            note = ('The owner marked this project complete in Portfolio Manager. '
                    'This records the owner’s status choice; the existing evidence and checklist remain as recorded.')
        else:
            if meta['work_state'] != 'completed':
                raise ValueError('The project is no longer marked complete. Refresh it and try again.')
            previous = meta.pop('owner_completion_previous_work_state', None)
            if previous not in build_browser.WORK_STATES or previous == 'completed':
                previous = 'planned'
            meta['work_state'] = previous
            note = ('The owner removed the complete status in Portfolio Manager. '
                    f'The work state is now {previous}; existing evidence and checklist remain as recorded.')
        text = raw.decode('utf-8').replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
        body = text.split('\n---\n', 1)[1]
        text = ('---\n' + json.dumps(meta, ensure_ascii=False, indent=2) + '\n---\n' + body.rstrip() +
                '\n\n## Owner completion status — ' + date.today().isoformat() +
                '\n\n' + note + '\n')
        fd, temporary = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(text.encode('utf-8')); stream.flush(); os.fsync(stream.fileno())
            _record(repo, selection, expected_hash)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
        try:
            build_browser.build(portfolio)
        except Exception:
            build_browser.atomic_text(path, raw.decode('utf-8'))
            raise
        return None
