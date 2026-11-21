"""Reversible local project and niche editing for the six-phase workspace."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import unicodedata
import uuid

from business_portfolio.tools import build_browser
from .project_lifecycle import _single_writer
from .workspace import context_path


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _title(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 180 or any(ord(c) < 32 for c in value):
        raise ValueError('Use a name between 1 and 180 characters on one line.')
    return value.strip()


def _slug(value: str) -> str:
    plain = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', plain).strip('-')[:60].rstrip('-')


def _niche(repo: Path, selection) -> tuple[Path, dict]:
    niche = context_path(repo, selection)
    base = repo / 'business_portfolio' / 'niches'
    if not niche.is_dir() or niche == base or not niche.is_relative_to(base):
        raise ValueError('Select an active niche or subniche folder.')
    metadata = niche / 'NICHE.json'
    if not metadata.is_file() or build_browser.linked_input(metadata):
        raise ValueError('Select an active niche or subniche folder.')
    meta = build_browser.loads(metadata.read_text(encoding='utf-8'))
    if meta.get('path') != niche.relative_to(base).as_posix() or not re.fullmatch(r'N-[a-zA-Z0-9_-]+', str(meta.get('id', ''))):
        raise ValueError('The selected niche metadata is invalid.')
    return niche, meta


def _view_snapshot(portfolio: Path) -> dict[Path, bytes | None]:
    result = {}
    for name in ('PROJECT_INDEX.json', 'PROJECT_BROWSER.html'):
        path = portfolio / name
        if path.is_symlink() or (path.exists() and build_browser.linked_input(path)):
            raise ValueError('Linked generated views are not supported.')
        result[path] = path.read_bytes() if path.exists() else None
    return result


def _atomic_bytes(path: Path, content: bytes) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('wb', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _restore_views(snapshot: dict[Path, bytes | None]) -> None:
    for path, contents in snapshot.items():
        if contents is None:
            path.unlink(missing_ok=True)
        else:
            _atomic_bytes(path, contents)


def _local_folder(portfolio: Path, *parts: str) -> Path:
    """Create private recovery storage without following a linked ancestor."""
    current = portfolio
    for part in ('.local', *parts):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', part) or part in {'.', '..'}:
            raise ValueError('Invalid recovery directory.')
        current = current / part
        if current.exists() or current.is_symlink():
            if not current.is_dir() or build_browser.linked_input(current):
                raise ValueError('Recovery storage is unsafe; remove the linked location first.')
        else:
            current.mkdir()
    return current


def _backup_record(portfolio: Path, ident: str, original: bytes) -> Path:
    directory = _local_folder(portfolio, 'project_backups', ident)
    digest = hashlib.sha256(original).hexdigest()
    path = directory / (digest + '.md')
    if path.exists() or path.is_symlink():
        if not path.is_file() or build_browser.linked_input(path) or path.read_bytes() != original:
            raise ValueError('The existing project backup is unsafe or does not match the original.')
    else:
        with path.open('xb') as stream:
            stream.write(original)
            stream.flush()
            os.fsync(stream.fileno())
    return path


def _record_text(metadata: dict, body: str) -> str:
    return '---\n' + json.dumps(metadata, ensure_ascii=False, indent=2) + '\n---\n\n' + body.strip() + '\n'


def _reserved_project_ids(portfolio: Path, data: dict) -> set[str]:
    """Keep identities unique across active, historical, completed and deleted work."""
    used = {row['id'] for key in ('records', 'archived_records') for row in data.get(key, [])}
    crosswalk = portfolio / 'archive/2026-11-15-taxonomy-view-v1/PROJECT_CROSSWALK.json'
    if crosswalk.is_file():
        used.update(row['id'] for row in build_browser.loads(crosswalk.read_text(encoding='utf-8')))
    private = portfolio / '.local'
    if private.exists() or private.is_symlink():
        recovery = _local_folder(portfolio, 'deleted_niches')
        for path in build_browser.walk_files(recovery):
            if build_browser.project_record_path(path):
                prior, _ = build_browser.parse_project(path.read_text(encoding='utf-8'), str(path))
                used.add(prior['id'])
    completed = portfolio / 'completed_projects'
    if completed.exists() or completed.is_symlink():
        if not completed.is_dir() or build_browser.linked_input(completed):
            raise ValueError('The completed-project storage is unsafe.')
        used.update(path.stem for path in completed.glob('*.json')
                    if re.fullmatch(r'[A-Z][A-Z0-9_-]*-[0-9]{3,}', path.stem))
    return used


def create_project(repo, selection, title: str = 'Empty project') -> dict:
    """Create a Phase 1 placeholder directly within the selected niche."""
    repo = Path(repo).resolve(strict=True)
    portfolio = repo / 'business_portfolio'
    title = _title(title)
    with _single_writer(portfolio):
        niche, niche_meta = _niche(repo, selection)
        data = build_browser.load_portfolio(portfolio)
        used = _reserved_project_ids(portfolio, data)
        prefixes = {row['id'].rsplit('-', 1)[0] for row in data['records'] if row['niche_id'] == niche_meta['id']}
        words = re.findall(r'[A-Za-z0-9]+', niche_meta['title'])
        prefix = next(iter(prefixes)) if len(prefixes) == 1 else ''.join(word[0] for word in words).upper()[:12]
        if not prefix or not prefix[0].isalpha():
            prefix = 'PROJ'
        number = max((int(ident.rsplit('-', 1)[1]) for ident in used
                      if ident.rsplit('-', 1)[0] == prefix), default=0) + 1
        while f'{prefix}-{number:03d}' in used:
            number += 1
        ident = f'{prefix}-{number:03d}'
        folder = niche / (ident.lower() + '-' + (_slug(title) or 'project'))
        if folder.exists():
            raise ValueError('The new project directory already exists; refresh and try again.')
        meta = dict(id=ident, title=title, schema_version=1, workflow_version=2,
                    project_phase='working_phase_1', draft=True,
                    niche_id=niche_meta['id'], niche_path=niche_meta['path'],
                    record_type='empty_project', origin='owner_created', priority='P2',
                    work_state='planned', commercial_validation='unvalidated',
                    evidence_basis='No product or market research has been performed yet.',
                    source_ids=[], parent_project=None, related_projects=[],
                    next_action='Copy the Phase 1 research or idea prompt, then paste the researched project text.',
                    last_reviewed=_today(), execution_authorized=False, privacy='public',
                    research_verification={f'phase_{i}': 'unreviewed' for i in range(1, 4)},
                    delivery_window_days={'minimum': 2, 'maximum': 21})
        body = f'''# {title}

## Project brief

This is an empty planning record in {niche_meta['title']}. Research a worthwhile product or supply an existing idea. No research, build, release or marketing work is claimed complete.

## Delivery window

Plan the complete project, including research, build, release and initial marketing, for approximately 2 days to 3 weeks. Select a feasible scope; record constraints and deferred opportunities explicitly.

## Phase 1 — Product research and specification

- [ ] Research the buyer, need, alternatives, value, price and feasibility.
- [ ] Describe the product, features, implementation, acceptance tests and constraints in detail.
- [ ] Recheck the evidence and address material weaknesses.

## Phase 2 — Release platforms and compatibility

- [ ] Research appropriate release platforms and nearby compatible product ecosystems.
- [ ] Define each feasible version, release requirements and source-backed release checklist.
- [ ] Update the product specification and verify the release plan.

## Phase 3 — Marketing research

- [ ] Research suitable channels, tactics, audiences, assets, costs and measurement.
- [ ] Define and recheck the marketing plan; update earlier plans when needed.

## Phase 4 — Build the project

- [ ] Build and test all accepted versions, preserving a completed/remaining checklist.
- [ ] Save all important data, artifacts and URLs; record a best-guess completion percentage at every checkpoint.

## Phase 5 — Release the project

- [ ] Release each accepted version through the researched distribution plan.
- [ ] Record actual upload, listing, download, purchase and edit URLs and verified outcomes.

## Phase 6 — Market the project

- [ ] Execute the approved marketing plan, recording placements, results and remaining tasks.
- [ ] Verify release and marketing evidence before marking the project complete.

## Important data and URLs

No project URLs or operational data have been recorded yet. Keep useful non-sensitive links and facts here as they become known. Never store passwords, tokens, customer information or payment details.

## Progress and next action

Completed: empty planning record created. Remaining: all research and execution. Next: copy a Phase 1 prompt.
'''
        views = _view_snapshot(portfolio)
        folder.mkdir()
        try:
            (folder / 'work').mkdir()
            (folder / 'work' / '.gitkeep').write_text('', encoding='utf-8')
            (folder / 'project.md').write_text(_record_text(meta, body), encoding='utf-8', newline='\n')
            build_browser.build(portfolio)
        except Exception:
            shutil.rmtree(folder)
            _restore_views(views)
            raise
        return {'id': ident, 'path': (folder / 'project.md').relative_to(repo).as_posix(),
                'title': title, 'project_phase': meta['project_phase']}


def create_niche(repo, selection, title: str) -> dict:
    """Create one child niche under the selected niche, with a new stable ID."""
    repo = Path(repo).resolve(strict=True)
    portfolio = repo / 'business_portfolio'
    title = _title(title)
    slug = _slug(title)
    if not slug or not build_browser.safe_niche(slug):
        raise ValueError('Choose a niche name that produces a safe, non-reserved folder name.')
    with _single_writer(portfolio):
        parent, parent_meta = _niche(repo, selection)
        target = parent / slug
        if target.exists() or target.is_symlink():
            raise ValueError('A folder with that niche name already exists.')
        meta = dict(id='N-' + uuid.uuid4().hex, title=title, parent=parent_meta['id'],
                    path=parent_meta['path'] + '/' + slug, priority=999, working=False)
        views = _view_snapshot(portfolio)
        target.mkdir()
        try:
            (target / 'NICHE.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
            build_browser.build(portfolio)
        except Exception:
            shutil.rmtree(target)
            _restore_views(views)
            raise
        return {'id': meta['id'], 'path': target.relative_to(repo).as_posix(), 'title': title}


def delete_niche(repo, selection) -> dict:
    """Move a selected niche subtree out of the active tree into recovery storage.

The UI confirms the subtree removal before calling this. Existing completion
receipts and historical archives remain independent and untouched.
"""
    repo = Path(repo).resolve(strict=True)
    portfolio = repo / 'business_portfolio'
    with _single_writer(portfolio):
        niche, meta = _niche(repo, selection)
        data = build_browser.load_portfolio(portfolio)
        prefix = meta['path'] + '/'
        removed = {row['id'] for row in data['records'] if row['niche_path'] == meta['path'] or row['niche_path'].startswith(prefix)}
        referring = [row['id'] for row in data['records'] if row['id'] not in removed and
                     (row.get('parent_project') in removed or removed.intersection(row.get('related_projects', [])))]
        if referring:
            raise ValueError('Other projects still reference this niche\'s projects: ' + ', '.join(sorted(referring)) + '. Resolve those links before deleting the niche.')
        list(build_browser.walk_files(niche))
        trash_root = _local_folder(portfolio, 'deleted_niches')
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        trash = trash_root / (stamp + '-' + uuid.uuid4().hex[:8] + '-' + niche.name)
        views = _view_snapshot(portfolio)
        original = niche.relative_to(repo).as_posix()
        os.replace(niche, trash)
        try:
            build_browser.build(portfolio)
        except Exception:
            os.replace(trash, niche)
            _restore_views(views)
            raise
        return {'id': meta['id'], 'path': original, 'trash_path': trash.relative_to(repo).as_posix(),
                'project_ids': sorted(removed)}
