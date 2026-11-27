"""Optional file import into a niche; the primary creation flow uses empty projects."""
from pathlib import Path
import re
import shutil

from business_portfolio.tools import build_browser
from .project_lifecycle import _single_writer
from business_portfolio.tools.project_workflow import VERSION, PHASE_1, phase_of, upgrade_record
from .project_management import (_niche, _record_text, _reserved_project_ids,
                                 _restore_views, _slug, _view_snapshot)
from .project_update import MAX_UPDATE_BYTES, clean_project_text


def import_projects(repo, selection, sources):
    """Import valid research records directly below a niche without advancing them."""
    repo = Path(repo).resolve(strict=True)
    portfolio = repo / 'business_portfolio'
    if not sources:
        raise ValueError('Drop one or more Markdown project files.')
    with _single_writer(portfolio):
        niche, niche_meta = _niche(repo, selection)
        data = build_browser.load_portfolio(portfolio)
        seen = _reserved_project_ids(portfolio, data)
        prepared = []
        for source in sources:
            source = Path(source)
            if source.suffix.lower() != '.md' or not source.is_file() or build_browser.linked_input(source):
                raise ValueError(f'{source.name}: only regular Markdown files can be imported.')
            if source.stat().st_size > MAX_UPDATE_BYTES:
                raise ValueError(f'{source.name}: file exceeds the 5 MB limit.')
            raw = clean_project_text(source.read_text(encoding='utf-8-sig'))
            meta, body = build_browser.parse_project(raw, source.name)
            ident = meta.get('id')
            if not isinstance(ident, str) or not re.fullmatch(r'[A-Z][A-Z0-9_-]*-[0-9]{3,}', ident):
                raise ValueError(f'{source.name}: a valid project ID is required.')
            if ident in seen:
                raise ValueError(f'Duplicate or reserved project ID: {ident}. Select an active project to replace its text; preserve historical identities.')
            seen.add(ident)
            if 'project_phase' in meta and meta.get('workflow_version') not in (2, VERSION):
                raise ValueError('A record with a project phase must declare workflow_version 2 or 3. Migrate ambiguous legacy work before importing it.')
            if 'project_phase' not in meta:
                meta.update(workflow_version=VERSION, project_phase=PHASE_1)
            if phase_of(meta) != PHASE_1:
                raise ValueError('Only Phase 1 research records can be imported; preserve existing execution work through migration.')
            meta, body = upgrade_record(meta, body)
            meta.update(niche_id=niche_meta['id'], niche_path=niche_meta['path'])
            meta.pop('project_update_base_sha256', None)
            meta.pop('project_update_phase_1b', None)
            folder = niche / (ident.lower() + '-' + (_slug(str(meta.get('title', ''))) or 'project'))
            if folder.exists() or folder.is_symlink():
                raise ValueError(f'{folder.name}: destination already exists.')
            prepared.append((ident, folder, _record_text(meta, body)))
        created = []
        views = _view_snapshot(portfolio)
        try:
            for _, folder, contents in prepared:
                folder.mkdir()
                created.append(folder)
                (folder / 'work').mkdir()
                (folder / 'work' / '.gitkeep').write_text('', encoding='utf-8')
                (folder / 'project.md').write_text(contents, encoding='utf-8', newline='\n')
            build_browser.build(portfolio)
        except Exception:
            for folder in reversed(created):
                shutil.rmtree(folder)
            _restore_views(views)
            raise
        return [ident for ident, _, _ in prepared]
