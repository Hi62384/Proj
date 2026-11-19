"""Import validated project records into the currently selected niche."""
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from business_portfolio.tools import build_browser
from .workspace import context_path


def import_projects(repo, selection, sources):
    repo = Path(repo).resolve()
    portfolio = repo / 'business_portfolio'
    niche = context_path(repo, selection)
    base = (portfolio / 'niches').resolve()
    if not niche.is_dir() or niche == base or not niche.is_relative_to(base):
        raise ValueError('Select an active niche folder before dropping project files.')
    metadata = niche / 'NICHE.json'
    if not metadata.is_file() or build_browser.linked_input(metadata):
        raise ValueError('Select an active niche folder before dropping project files.')
    niche_meta = build_browser.loads(metadata.read_text(encoding='utf-8'))
    niche_path = niche.relative_to(base).as_posix()
    if niche_meta.get('path') != niche_path or not niche_meta.get('id'):
        raise ValueError('The selected niche metadata is invalid.')
    if not sources:
        raise ValueError('Drop one or more Markdown project files.')
    prepared = []
    seen = set()
    for source in sources:
        source = Path(source)
        if source.suffix.lower() != '.md' or not source.is_file():
            raise ValueError(f'{source.name}: only Markdown files can be imported.')
        if source.stat().st_size > 5_000_000:
            raise ValueError(f'{source.name}: file exceeds the 5 MB limit.')
        raw = source.read_text(encoding='utf-8-sig')
        meta, _ = build_browser.parse_project(raw, source.name)
        ident = meta.get('id')
        if not isinstance(ident, str) or not re.fullmatch(r'[A-Z][A-Z0-9_-]*-[0-9]{3,}', ident):
            raise ValueError(f'{source.name}: a valid project ID is required.')
        if ident in seen:
            raise ValueError(f'Duplicate project ID in drop: {ident}')
        seen.add(ident)
        meta['niche_id'] = niche_meta['id']
        meta['niche_path'] = niche_path
        meta['project_phase'] = 'working_phase_2'
        normalized = raw.replace('\r\n', '\n')
        body = normalized.split('\n---\n', 1)[1]
        contents = '---\n' + json.dumps(meta, ensure_ascii=False, indent=2) + '\n---\n' + body
        slug = re.sub(r'[^a-z0-9]+', '-', str(meta.get('title', '')).lower()).strip('-')[:70]
        # One owned directory per project, not a loose Markdown record.
        folder = ident.lower() + ('-' + slug[:48] if slug else '')
        prepared.append((ident, folder, contents))
    destination = niche / 'projects'
    if destination.exists():
        context_path(repo, destination)
    # Validate the complete proposed portfolio in a disposable copy before writing.
    with tempfile.TemporaryDirectory(prefix='portfolio-import-') as temp:
        staged = Path(temp) / 'business_portfolio'
        shutil.copytree(portfolio, staged, ignore=shutil.ignore_patterns('.local', '__pycache__', '.niche-working.lock'))
        staged_dest = staged / 'niches' / niche_path / 'projects'
        staged_dest.mkdir(parents=True, exist_ok=True)
        for _, folder, contents in prepared:
            target = staged_dest / folder
            if target.exists():
                raise ValueError(f'{folder}: destination already exists.')
            (target / 'work').mkdir(parents=True)
            (target / 'project.md').write_text(contents, encoding='utf-8', newline='\n')
            (target / 'work' / '.gitkeep').write_text('', encoding='utf-8')
        build_browser.load_portfolio(staged)
    destination.mkdir(exist_ok=True)
    created = []
    try:
        for _, folder, contents in prepared:
            path = destination / folder
            path.mkdir()
            created.append(path)
            (path / 'work').mkdir()
            with (path / 'project.md').open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(contents)
                stream.flush()
                os.fsync(stream.fileno())
            (path / 'work' / '.gitkeep').write_text('', encoding='utf-8')
        build_browser.build(portfolio)
    except Exception:
        for path in reversed(created):
            shutil.rmtree(path)
        raise
    return [ident for ident, _, _ in prepared]
