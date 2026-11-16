#!/usr/bin/env python3
"""One-time, lossless transition from the 182-node research view to 13 business niches."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from build_browser import load_portfolio, parse_project, linked_input

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = '2026-11-15-taxonomy-view-v1'
BUSINESS_NICHES = [
    ('game-development-marketplaces', 'Game Development Marketplaces'),
    ('marketplace-hosted-automations', 'Marketplace-Hosted Automations'),
    ('ai-assisted-freelancing', 'AI-Assisted Freelancing'),
    ('platform-specific-apps-and-extensions', 'Platform-Specific Apps & Extensions'),
    ('advanced-online-products-and-software', 'Advanced Online Products & Software'),
    ('specialized-data-and-intelligence-services', 'Specialized Data & Intelligence Services'),
    ('usage-based-apis', 'Usage-Based APIs'),
    ('licensing-and-royalties', 'Licensing & Royalties'),
    ('affiliate-and-referral-businesses', 'Affiliate & Referral Businesses'),
    ('advertising-supported-utility-websites', 'Advertising-Supported Utility Websites'),
    ('online-content-and-media', 'Online Content & Media'),
    ('online-games-and-virtual-economies', 'Online Games & Virtual Economies'),
    ('lead-generation', 'Lead Generation'),
]


def migrate(root=ROOT):
    root = Path(root).resolve()
    data = load_portfolio(root)
    if len(data['niches']) != 182 or {r['id'] for r in data['records']} != {'GDM-001', 'GDM-002', 'GDM-003'}:
        raise ValueError('Unexpected active baseline; do not overwrite newer portfolio changes')
    old = root / 'niches'
    archive = root / 'archive' / ARCHIVE
    if archive.exists() or linked_input(old):
        raise ValueError('Archive already exists or linked input refused')
    source_niche = old / 'games-and-interactive-entertainment' / 'game-development-marketplaces'
    source_meta = json.loads((source_niche / 'NICHE.json').read_text(encoding='utf-8'))
    if source_meta['id'] != 'N-gdm-20261115':
        raise ValueError('Game niche identity changed')
    files = sorted(p for p in old.rglob('*') if p.is_file())
    if any(linked_input(p) for p in files):
        raise ValueError('Linked input refused')
    manifest = [{'path': p.relative_to(old).as_posix(),
                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                 'bytes': p.stat().st_size} for p in files]
    originals = {r['id']: {'old_path': r['path'], 'sha256': r['content_sha256'],
                           'niche_id': r['niche_id'], 'niche_path': r['niche_path'],
                           'work_state': r['work_state'], 'commercial_validation': r['commercial_validation']}
                 for r in data['records']}
    archive.mkdir(parents=True)
    os.rename(old, archive / 'niches')
    (archive / 'FILE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    old.mkdir()
    for priority, (slug, title) in enumerate(BUSINESS_NICHES, 1):
        folder = old / slug
        folder.mkdir()
        ident = source_meta['id'] if priority == 1 else f'N-business-{priority:02d}'
        (folder / 'NICHE.json').write_text(json.dumps({
            'id': ident, 'title': title, 'parent': None, 'path': slug, 'priority': priority,
            'description': ('One multi-engine game-development product family per canonical record.'
                            if priority == 1 else 'No active projects. Research and validate this niche before adding a project.')
        }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    destination = old / BUSINESS_NICHES[0][0] / 'projects'
    destination.mkdir()
    crosswalk = []
    for record in data['records']:
        source = archive / 'niches' / Path(record['path']).relative_to('niches')
        meta, body = parse_project(source.read_text(encoding='utf-8'), str(source))
        meta['niche_path'] = BUSINESS_NICHES[0][0]
        meta['niche_id'] = source_meta['id']
        meta['last_reviewed'] = '2026-11-15'
        target = destination / source.name
        target.write_text('---\n' + json.dumps(meta, ensure_ascii=False, indent=2) + '\n---\n' +
                          body + '\n', encoding='utf-8')
        crosswalk.append({'id': record['id'], **originals[record['id']],
                          'new_path': target.relative_to(root).as_posix(),
                          'preserved_snapshot': source.relative_to(root).as_posix()})
    (archive / 'PROJECT_CROSSWALK.json').write_text(json.dumps(crosswalk, indent=2) + '\n', encoding='utf-8')
    return {'old_niches': len(data['niches']), 'preserved_files': len(manifest),
            'new_primary_niches': len(BUSINESS_NICHES), 'active_project_ids': sorted(originals)}


if __name__ == '__main__':
    print(json.dumps(migrate(), indent=2))
