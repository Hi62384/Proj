"""Reuse the real repository atlas; do not invent demand validation."""
from __future__ import annotations
from pathlib import Path
from portfolio_autopilot.cli import load_catalog, shortlist
from .config import ATLAS, ROOT, SetupError

MODES = {'F','R','D','I','M','P','A','L','C','X','ORIGINAL'}

LIBRARY_ATLAS = ROOT / 'opportunity_library' / 'data' / 'factory_catalog.csv'

def catalog(path: Path | None = None) -> list[dict[str,str]]:
    """Prefer the optional organized library; preserve explicit/legacy source paths."""
    selected = path if path is not None else LIBRARY_ATLAS if LIBRARY_ATLAS.is_file() else ATLAS
    return load_catalog(selected)

def find(rows: list[dict[str,str]], identifier: str) -> dict[str,str]:
    for row in rows:
        if row.get('id') == identifier:
            return row
    raise SetupError(f'Unknown opportunity ID: {identifier}.')

def select(rows: list[dict[str,str]], *, limit: int = 12, per_mode: int = 3,
           modes: set[str] | None = None, include_regulated: bool = False) -> list[dict[str,str]]:
    if modes and (modes - MODES):
        raise SetupError('Unknown opportunity modes: '+', '.join(sorted(modes-MODES)))
    pool = [r for r in rows if not modes or r.get('revenue_mode') in modes]
    return shortlist(pool, limit=limit, max_per_mode=per_mode, include_regulated=include_regulated)

def summary(rows: list[dict[str,str]]) -> dict:
    return {'records': len(rows),
            'expanded_hypotheses': sum(x.get('id','').startswith('EXP-') for x in rows),
            'original_research_records': sum(x.get('id','').startswith(('REPO-','FAST-')) for x in rows),
            'curated_library_hypotheses': sum(x.get('id','').startswith('CUR-') for x in rows),
            'library_categories': len({x['library_category_id'] for x in rows if x.get('library_category_id')}),
            'capital_research_only': sum(x.get('library_income_type') == 'personal_capital' for x in rows),
            'expanded_niches': len({r['niche'] for r in rows if r.get('id','').startswith('EXP-')}),
            'paid_offer_validation': 'Not independently established by the atlas.'}
