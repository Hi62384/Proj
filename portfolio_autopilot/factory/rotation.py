"""Stable cross-sector, diverse weekly *research hypothesis* rotation.

A rotation is not live market discovery: no source checking, customer contacts,
sales, or external actions occur here.
"""
from __future__ import annotations
from collections import Counter
from datetime import date
import json
from pathlib import Path

from .catalog import catalog
from .config import PRIVATE, SetupError, init_private
from .kits import make_kit
from .ledger import create_tasks


def choose_rotation(rows: list[dict], *, rotation_number: int, limit: int = 6,
                    score_floor: float = 65, max_per_mode: int = 2) -> list[dict]:
    """One highest-scoring non-regulated idea per eligible niche, rotating sectors."""
    if rotation_number<0 or limit<1 or limit>20 or max_per_mode<1:
        raise SetupError('Invalid rotation/limit.')
    candidates_by_niche={}
    for row in rows:
        if not row.get('id','').startswith('EXP-'):
            continue
        if row.get('legal_class','').strip().lower()!='standard':
            continue
        try:score=float(row.get('cross_niche_score') or 0)
        except (TypeError,ValueError):continue
        if score<score_floor:continue
        niche=row.get('niche','').strip()
        if niche:
            candidates_by_niche.setdefault(niche,[]).append(row)
    niches=sorted(candidates_by_niche)
    if not niches:return []
    for bucket in candidates_by_niche.values():
        bucket.sort(key=lambda r:(-float(r.get('cross_niche_score') or 0),r['id']))
    start=(rotation_number*limit)%len(niches)
    ordered=niches[start:]+niches[:start]
    selected=[];per_mode=Counter()
    for niche in ordered:
        # Choose the strongest eligible mode not already saturated.
        candidate=next((r for r in candidates_by_niche[niche]
                        if per_mode[r.get('revenue_mode','')]<max_per_mode),None)
        if candidate is None:continue
        mode=candidate.get('revenue_mode','')
        selected.append(candidate);per_mode[mode]+=1
        if len(selected)>=limit:break
    # If only one mode is available, don't pretend there were enough diverse ideas.
    return selected


def create_rotation(root: Path = PRIVATE, *, rotation_number: int|None=None,
                    limit: int=6) -> dict:
    init_private(root)
    today=date.today()
    rotation_number=rotation_number if rotation_number is not None else (today.isocalendar().year*53+today.isocalendar().week)
    rows=catalog()
    selected=choose_rotation(rows,rotation_number=rotation_number,limit=limit)
    result={'status':'DRAFT_ROTATION_ONLY_NO_MARKET_VERIFICATION',
            'rotation_number':rotation_number,'created_for_date':today.isoformat(),
            'candidate_count':len(selected),'candidates':[], 'external_actions':0}
    for row in selected:
        try:
            kit=make_kit(row,root)
            state='new_draft'
        except SetupError as e:
            if 'already exists' not in str(e):raise
            state='existing_draft_preserved'
        result['candidates'].append({'id':row['id'],'niche':row.get('niche'),
                                     'model':row.get('revenue_mode'), 'state':state,
                                     'evidence':'Research hypothesis, not validated buyer demand'})
    create_tasks(selected,root)
    reports=root/'rotation_reports';reports.mkdir(parents=True,exist_ok=True)
    # Unique per rotation number with no overwrite (idempotent).
    path=reports/f'rotation_{rotation_number}.json'
    if not path.exists():path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result
