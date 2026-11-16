#!/usr/bin/env python3
"""One-time move of the 13 existing niches under 12 business categories."""
from __future__ import annotations

import json
from pathlib import Path

from build_browser import load_portfolio, parse_project

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = [
    ('digital-products', 'Digital Products', ('game-development-marketplaces',)),
    ('software', 'Software', ('advanced-online-products-and-software', 'platform-specific-apps-and-extensions')),
    ('apis', 'APIs', ('usage-based-apis',)),
    ('automation', 'Automation', ('marketplace-hosted-automations',)),
    ('digital-content', 'Digital Content', ('online-content-and-media',)),
    ('data-and-intelligence', 'Data & Intelligence', ('specialized-data-and-intelligence-services',)),
    ('services', 'Services', ('ai-assisted-freelancing',)),
    ('gaming', 'Gaming', ('online-games-and-virtual-economies',)),
    ('advertising', 'Advertising', ('advertising-supported-utility-websites',)),
    ('affiliate-marketing', 'Affiliate Marketing', ('affiliate-and-referral-businesses',)),
    ('lead-generation', 'Lead Generation', ()),
    ('licensing-and-royalties', 'Licensing & Royalties', ()),
]


def write_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def migrate(root: Path = ROOT):
    root = Path(root).resolve(strict=True)
    data = load_portfolio(root)
    old = root / 'niches'
    current = {n['path']: n for n in data['niches']}
    desired = {child for _, _, children in CATEGORIES for child in children}
    desired.update(('lead-generation', 'licensing-and-royalties'))
    partial = (old / 'digital-products/NICHE.json').exists()
    expected = desired | ({'digital-products'} if partial else set())
    if (len(current) != len(expected) or set(current) != expected or
            {r['id'] for r in data['records']} != {'GDM-001', 'GDM-002', 'GDM-003'} or
            any(n['parent'] is not None for n in current.values())):
        raise ValueError('Unexpected active baseline; leave newer changes untouched')
    for slug, _, children in CATEGORIES:
        category = old / slug
        if children and category.exists():
            metadata = category / 'NICHE.json'
            if (not metadata.is_file() or json.loads(metadata.read_text(encoding='utf-8')).get('id') !=
                    f'N-category-{slug}' or any(p.name != 'NICHE.json' for p in category.iterdir())):
                raise ValueError('A destination category already exists; inspect it before moving')
    original = {r['id']: (r['path'], r['niche_id'], r['body'], r['work_state'],
                           r['commercial_validation']) for r in data['records']}
    for priority, (slug, title, children) in enumerate(CATEGORIES, 1):
        category = old / slug
        if children:
            category.mkdir(exist_ok=True)
            category_id = f'N-category-{slug}'
            write_json(category / 'NICHE.json', {
                'id': category_id, 'title': title, 'parent': None,
                'path': slug, 'priority': priority,
                'description': 'Business category; select a niche to see its projects.',
            })
        else:
            category_id = current[slug]['id']
            meta = current[slug].copy()
            meta['priority'] = priority
            write_json(category / 'NICHE.json', meta)
        for child_order, child in enumerate(children, 1):
            source = old / child
            target = category / child
            if not source.resolve(strict=True).is_relative_to(root) or not target.resolve(strict=False).is_relative_to(root):
                raise ValueError('Move target leaves the portfolio checkout')
            source.rename(target)
            meta = current[child].copy()
            meta.update(path=f'{slug}/{child}', parent=category_id, priority=child_order)
            write_json(target / 'NICHE.json', meta)
    project_dir = old / 'digital-products/game-development-marketplaces/projects'
    for path in sorted(project_dir.glob('*.md')):
        meta, body = parse_project(path.read_text(encoding='utf-8'), str(path))
        meta['niche_path'] = 'digital-products/game-development-marketplaces'
        path.write_text('---\n' + json.dumps(meta, ensure_ascii=False, indent=2) +
                        '\n---\n' + body + '\n', encoding='utf-8')
    crosswalk = root / 'archive/2026-11-15-taxonomy-view-v1/PROJECT_CROSSWALK.json'
    rows = json.loads(crosswalk.read_text(encoding='utf-8'))
    for row in rows:
        row['new_path'] = 'niches/digital-products/game-development-marketplaces/projects/' + Path(row['new_path']).name
    write_json(crosswalk, rows)
    revised = load_portfolio(root)
    if len(revised['niches']) != 23 or len(revised['records']) != 3:
        raise ValueError('Unexpected migrated counts')
    for record in revised['records']:
        previous = original[record['id']]
        if (record['niche_id'], record['body'], record['work_state'], record['commercial_validation']) != previous[1:]:
            raise ValueError(f'Project content/state changed unexpectedly: {record["id"]}')
    return {'categories': 12, 'niches': 13, 'active_projects': 3}


if __name__ == '__main__':
    print(json.dumps(migrate(), indent=2))
