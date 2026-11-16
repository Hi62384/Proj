#!/usr/bin/env python3
"""One-time, reversible migration from the old active catalogue to niche-first planning.

This moves only business_portfolio/niches metadata and Markdown records. It never
touches product source, paid downloads, accounts, or the private coordinator DB.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import unicodedata

from build_browser import parse_project, linked_input

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = '2026-11-15-legacy'


def slug(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = value.lower().replace('&', ' and ')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', value)).strip('-')


def migrate(root=ROOT, taxonomy_path=None):
    root = Path(root).resolve()
    taxonomy_path = Path(taxonomy_path or root.parent / 'opportunity_library/data/taxonomy.json')
    taxonomy = json.loads(taxonomy_path.read_text(encoding='utf-8'))
    categories = taxonomy['categories']
    if len(categories) != 36 or sum(len(c['subcategories']) for c in categories) != 144:
        raise ValueError('Expected the reviewed 36-category, 144-subcategory taxonomy')
    old = root / 'niches'
    archive = root / 'archive' / ARCHIVE
    if archive.exists() or not old.is_dir():
        raise FileExistsError('Archive already exists or old niches are missing; inspect before retrying')
    files = sorted(path for path in old.rglob('*') if path.is_file())
    if any(linked_input(path) for path in [old, *files]):
        raise ValueError('Linked source input refused')
    manifest = []
    crosswalk = []
    old_niches = {}
    for path in files:
        relative = path.relative_to(old).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.append({'path': 'niches/' + relative, 'sha256': digest, 'bytes': path.stat().st_size})
        if path.name == 'NICHE.json':
            row = json.loads(path.read_text(encoding='utf-8'))
            old_niches[row['path']] = row
        if path.parent.name == 'projects' and path.suffix.lower() == '.md':
            meta, _ = parse_project(path.read_text(encoding='utf-8'), relative)
            crosswalk.append({
                'id': meta['id'], 'old_path': 'business_portfolio/niches/' + relative,
                'archive_path': 'business_portfolio/archive/' + ARCHIVE + '/niches/' + relative,
                'sha256': digest, 'work_state': meta['work_state'],
                'commercial_validation': meta['commercial_validation'],
                'niche_id': meta['niche_id'], 'source_ids': meta['source_ids'],
                'parent_project': meta['parent_project'], 'related_projects': meta['related_projects'],
                'evidence_basis': meta['evidence_basis'],
                'private_checkpoint_pointer': meta.get('private_checkpoint_ref'),
            })
    ids = [row['id'] for row in crosswalk]
    if len(ids) != len(set(ids)) or any(x in ids for x in ('GDM-001', 'GDM-002', 'GDM-003')):
        raise ValueError('Duplicate legacy ID or selected new ID already exists')
    archive.mkdir(parents=True)
    os.rename(old, archive / 'niches')
    (archive / 'FILE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (archive / 'PROJECT_CROSSWALK.json').write_text(json.dumps(sorted(crosswalk, key=lambda r: r['id']), indent=2) + '\n', encoding='utf-8')
    old.mkdir()
    seen = set()

    def write_niche(path, title, ident, parent, description):
        if path in seen:
            raise ValueError('Duplicate new niche path: ' + path)
        seen.add(path)
        folder = old / path
        folder.mkdir(parents=True, exist_ok=False)
        data = {'id': ident, 'title': title, 'parent': parent, 'path': path,
                'description': description}
        (folder / 'NICHE.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    for category in categories:
        path = category['slug']
        original = old_niches.get(path)
        ident = original['id'] if original else 'N-tax-' + category['id']
        write_niche(path, category['name'], ident, None, category.get('strategy', ''))
        for sub in category['subcategories']:
            child = path + '/' + slug(sub['name'])
            original = old_niches.get(child)
            child_id = original['id'] if original else 'N-tax-' + sub['id']
            write_niche(child, sub['name'], child_id, ident,
                        'No active projects. Research area from the opportunity taxonomy.')
    games = 'games-and-interactive-entertainment'
    games_id = json.loads((old / games / 'NICHE.json').read_text(encoding='utf-8'))['id']
    write_niche(games + '/game-development-marketplaces', 'Game Development Marketplaces',
                'N-gdm-20261115', games_id,
                'Multi-engine product families for developer marketplaces; engine editions are evaluated separately.')
    ai = old_niches['ai-workflow-automation']
    write_niche(ai['path'], ai['title'], ai['id'], None,
                'Existing AI workflow automation niche retained as a browseable empty area; prior records are in History.')
    return {'archived_records': len(crosswalk), 'archived_files': len(manifest), 'active_niches': len(seen)}


if __name__ == '__main__':
    print(json.dumps(migrate(), indent=2))
