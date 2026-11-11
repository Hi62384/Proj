#!/usr/bin/env python3
"""Validate canonical Markdown records and rebuild a self-contained read-only browser.
Python 3.10+. Standard library only. No network, account, scheduler or queue writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

# Load the adjacent local checker, never a network/transaction client.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from commercial_checks import validate_record, CommercialError

ROOT = Path(__file__).resolve().parents[1]
WORK_STATES = {'planned','deferred','published_reported','operational_reported','paused',
 'prototype_reported','legacy_preserved','needs_reconciliation','package_ready',
 'active','blocked','ready_for_test','completed','cancelled','archived'}
VALIDATIONS = {'unvalidated','published_unvalidated','not_applicable','unknown',
 'unvalidated_catalogue','buyer_signal','paid_pilot','repeat_paid','commercially_validated'}
PRIORITIES = {'P1','P2','P3','BUNDLE','DEFER','PRESERVE','INTEGRATE'}
REQUIRED = {'id','title','schema_version','niche_path','record_type','origin','priority',
 'work_state','commercial_validation','evidence_basis','source_ids','next_action',
 'last_reviewed','niche_id','parent_project','related_projects','execution_authorized','privacy'}

class ValidationError(ValueError):
    pass

def reject_duplicates(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValidationError(f'Duplicate JSON key: {key}')
        value[key] = item
    return value

def loads(text: str):
    return json.loads(text, object_pairs_hook=reject_duplicates,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValidationError(f'Invalid JSON constant: {v}')))

def parse_project(text: str, label: str = '<record>') -> tuple[dict, str]:
    normalized = text.replace('\r\n','\n')
    if not normalized.startswith('---\n'):
        raise ValidationError(f'{label}: missing JSON frontmatter')
    pieces = normalized.split('\n---\n', 1)
    if len(pieces) != 2:
        raise ValidationError(f'{label}: missing frontmatter terminator')
    try:
        meta = loads(pieces[0][4:])
    except (ValueError, TypeError) as exc:
        raise ValidationError(f'{label}: invalid JSON metadata: {exc}') from exc
    if not isinstance(meta, dict):
        raise ValidationError(f'{label}: metadata must be an object')
    return meta, pieces[1].strip()

def safe_niche(path: str) -> bool:
    reserved = {'con', 'prn', 'aux', 'nul'} | {f'{prefix}{i}' for prefix in ('com', 'lpt') for i in range(1, 10)}
    return isinstance(path,str) and bool(path) and all(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',p)
        and p not in {'projects','private','local'} | reserved for p in path.split('/'))

def linked_input(path: Path) -> bool:
    info = path.stat(follow_symlinks=False)
    return path.is_symlink() or bool(getattr(info,'st_file_attributes',0) & 0x400) or (path.is_file() and info.st_nlink > 1)

def walk_files(root: Path):
    # Iterative filesystem walk: no artificial niche-depth limit; do not follow links.
    if linked_input(root):
        raise ValidationError('Linked index root refused')
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in list(dirs):
            p = Path(directory)/name
            if linked_input(p):
                raise ValidationError(f'Symlink directory refused: {p}')
            if name.startswith('.') or name in {'__pycache__','private'}:
                dirs.remove(name)
        for name in sorted(files):
            p = Path(directory)/name
            if linked_input(p):
                raise ValidationError(f'Symlink file refused: {p}')
            yield p

def ensure_acyclic(mapping: dict[str, str | None], label: str):
    done: set[str] = set()
    for start in mapping:
        seen: set[str] = set()
        current = start
        while current is not None and current not in done:
            if current in seen:
                raise ValidationError(f'{label}: cycle at {current}')
            if current not in mapping:
                raise ValidationError(f'{label}: unknown parent {current}')
            seen.add(current)
            current = mapping[current]
        done.update(seen)

def load_portfolio(root: Path) -> dict:
    root = root.resolve()
    for name in ('niches','research','tools','results'):
        directory=root/name
        if directory.exists() and linked_input(directory):
            raise ValidationError('Linked input root refused')
    source_path = root/'research/SOURCE_REGISTER.json'
    if linked_input(source_path):
        raise ValidationError('Linked source register refused')
    source_rows = loads(source_path.read_text(encoding='utf-8'))
    sources = {}
    for s in source_rows:
        if not isinstance(s,dict) or not s.get('id') or s['id'] in sources:
            raise ValidationError('Missing or duplicate source ID')
        if not s.get('title') or not s.get('url'):
            raise ValidationError(f"Invalid source: {s.get('id')}")
        if not s['url'].startswith(('https://','http://','attachment:')):
            raise ValidationError(f"Unsafe source URL: {s['id']}")
        sources[s['id']] = s
    files = list(walk_files(root/'niches'))
    nodes = {}
    for p in files:
        if p.name != 'NICHE.json':
            continue
        m = loads(p.read_text(encoding='utf-8'))
        actual = p.parent.relative_to(root/'niches').as_posix()
        if not safe_niche(actual) or m.get('path') != actual or not re.fullmatch(r'N-[a-zA-Z0-9_-]+', str(m.get('id',''))):
            raise ValidationError(f'Niche path/id mismatch: {p}')
        if not isinstance(m.get('title'),str):
            raise ValidationError(f'Niche parent/title mismatch: {p}')
        if m['id'] in nodes:
            raise ValidationError('Duplicate niche ID')
        nodes[m['id']] = m
    ensure_acyclic({k:v['parent'] for k,v in nodes.items()},'niches')
    node_paths = {v['path']:v['id'] for v in nodes.values()}
    for node in nodes.values():
        path = node['path']
        expected_parent = node_paths.get(path.rsplit('/',1)[0]) if '/' in path else None
        if ('/' in path and expected_parent is None) or node['parent'] != expected_parent:
            raise ValidationError(f"Niche directory/parent mismatch: {path}")
    records = []
    ids = set()
    for p in files:
        if p.suffix.lower() != '.md' or p.parent.name != 'projects':
            continue
        m, body = parse_project(p.read_text(encoding='utf-8'),str(p))
        missing = REQUIRED-set(m)
        if missing:
            raise ValidationError(f'{p}: missing fields {sorted(missing)}')
        if m['schema_version'] != 1 or not re.fullmatch(r'[A-Z][A-Z0-9_-]*-[0-9]{3,}',m['id']):
            raise ValidationError(f'{p}: invalid schema version or project ID')
        if m['id'] in ids:
            raise ValidationError(f"Duplicate project ID: {m['id']}")
        ids.add(m['id'])
        actual = p.parent.parent.relative_to(root/'niches').as_posix()
        if m['niche_path'] != actual or m['niche_id'] != node_paths.get(actual):
            raise ValidationError(f'{p}: record niche mismatch/missing NICHE.json')
        if m['work_state'] not in WORK_STATES or m['commercial_validation'] not in VALIDATIONS or m['priority'] not in PRIORITIES:
            raise ValidationError(f'{p}: unknown state/validation/priority')
        if not isinstance(m['source_ids'],list) or not m['source_ids'] or any(x not in sources for x in m['source_ids']):
            raise ValidationError(f'{p}: missing/unknown sources')
        if not isinstance(m['related_projects'],list):
            raise ValidationError(f'{p}: related_projects must be a list')
        if not isinstance(m['execution_authorized'],bool):
            raise ValidationError(f'{p}: execution_authorized must be boolean')
        if not isinstance(m['next_action'],str) or not m['next_action'].strip() or not body:
            raise ValidationError(f'{p}: missing next action/body')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',m['last_reviewed']):
            raise ValidationError(f'{p}: invalid review date')
        if m['commercial_validation'] in {'paid_pilot','repeat_paid','commercially_validated'} and not m.get('validation_evidence_ref'):
            raise ValidationError(f'{p}: paid validation requires a non-sensitive evidence reference')
        if not isinstance(m['title'],str) or not m['title'].strip():
            raise ValidationError(f'{p}: missing title')
        results=m.get('public_results',[])
        if not isinstance(results,list) or len(results)>20:
            raise ValidationError(f'{p}: invalid public results')
        for result in results:
            if not isinstance(result,dict) or not isinstance(result.get('path'),str) or not isinstance(result.get('label'),str) or not result['label'].strip():
                raise ValidationError(f'{p}: invalid public result entry')
            target=PurePosixPath(result['path'])
            if target.is_absolute() or '..' in target.parts or '\\' in result['path'] or target.parts[:2]!=('results',m['id']):
                raise ValidationError(f'{p}: public result must stay inside results/{m["id"]}')
        try:
            validate_record(m)
        except CommercialError as exc:
            raise ValidationError(str(exc)) from exc
        records.append(dict(m,path=p.relative_to(root).as_posix(),body=body,
                            content_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    ensure_acyclic({r['id']:r['parent_project'] for r in records},'project parents')
    for r in records:
        if any(i not in ids for i in r['related_projects']):
            raise ValidationError(f"Unknown related project in {r['id']}")
    records.sort(key=lambda r:r['id'])
    documents=[]
    for rel in ['README.md','research/RESEARCH_V2.md','research/PRIORITIES_V2.md',
                'research/MARKETING_PLAYBOOK.md','research/BUDGET_POLICY.md','research/ECONOMICS_V2.md',
                'research/VALIDATION_GATES.md','research/SOURCES_V2.md','marketing/LAUNCH_CHECKLIST.md',
                'marketing/AD_TEST_BRIEF_TEMPLATE.md','research/V2_CHANGELOG.md','research/MARKET_RESEARCH.md','research/TOP_OPPORTUNITIES.md',
                'research/ECONOMICS.md','research/COMPETITIVE_MATRIX.md','research/FIRST_PAID_PILOT.md',
                'research/EXISTING_PROJECTS.md','research/REPOSITORY_RECONCILIATION.md',
                'research/SAFE_EXECUTION.md','research/SOURCES.md','REPO_PLACEMENT.md',
                'CODEX_IMPLEMENTATION_PROMPT.md','SCHEMA.md','QA_REPORT.md','INTEGRATION_STATUS.md']:
        p = root/rel
        if p.exists():
            if linked_input(p):
                raise ValidationError('Linked document refused')
            content=p.read_text(encoding='utf-8')
            documents.append(dict(path=rel,title=content.splitlines()[0].lstrip('# ').strip(),body=content))
    return dict(schema_version=1,generated_from='Canonical Markdown; offline build is not fresh research',
                latest_record_review=max((r['last_reviewed'] for r in records),default='unknown'),
                records=records,niches=sorted(nodes.values(),key=lambda n:n['path']),
                sources=source_rows,documents=documents)

def embedded_json(data: dict) -> str:
    return json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')

def render_browser(data: dict, template: str) -> str:
    if template.count('/*__PORTFOLIO_DATA__*/') != 1:
        raise ValidationError('Browser template must contain one data placeholder')
    return template.replace('/*__PORTFOLIO_DATA__*/',embedded_json(data))

def atomic_text(path: Path, text: str):
    path.parent.mkdir(parents=True,exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',newline='\n',dir=path.parent,delete=False) as f:
            name=f.name; f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if name and os.path.exists(name): os.unlink(name)

def build(root: Path, check: bool=False):
    data=load_portfolio(root)
    template=(root/'tools/browser_template.html').read_text(encoding='utf-8')
    outputs={root/'PROJECT_BROWSER.html':render_browser(data,template),
             root/'PROJECT_INDEX.json':json.dumps(data,ensure_ascii=False,indent=2)+'\n'}
    if check:
        stale=[p.name for p,t in outputs.items() if not p.exists() or p.read_text(encoding='utf-8')!=t]
        if stale: raise ValidationError('Generated files stale/missing: '+', '.join(stale))
    else:
        for path,text in outputs.items(): atomic_text(path,text)
    return data

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=ROOT)
    ap.add_argument('--check',action='store_true',help='Validate and check generated files without writing')
    args=ap.parse_args()
    try:
        data=build(args.root,args.check)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print('Portfolio validation failed: '+str(exc),file=sys.stderr);return 1
    print(f"{'Checked' if args.check else 'Built'} {len(data['records'])} projects, {len(data['niches'])} niche nodes, {len(data['sources'])} source records. No external action executed.")
    return 0
if __name__=='__main__':raise SystemExit(main())
