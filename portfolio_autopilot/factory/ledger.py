"""Local unreconciled business metrics, review queue and stage evidence.

Not a payment gateway, bank sync, tax system or CRM with personal data.
Only pseudonymous opportunity IDs and owner-asserted evidence are stored.
"""
from __future__ import annotations
import csv
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from .config import PRIVATE, SetupError, init_private, money, safe_id

KINDS={'revenue','refund','fee','expense','owner_minutes','settlement'}
STAGES={'researching','buyer_signal','offered','funded','delivering','paused','retired'}
HIGH_STAGES={'buyer_signal','offered','funded','delivering'}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(root: Path = PRIVATE) -> sqlite3.Connection:
    init_private(root)
    conn=sqlite3.connect(root/'operations.sqlite3',timeout=10)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS activity (
        event_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, event_date TEXT NOT NULL,
        kind TEXT NOT NULL, amount_cad TEXT NOT NULL, minutes INTEGER NOT NULL,
        source_ref TEXT NOT NULL, source_status TEXT NOT NULL, created_utc TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS candidate (
        business_id TEXT PRIMARY KEY, stage TEXT NOT NULL, evidence_ref TEXT NOT NULL,
        note TEXT NOT NULL, reviewed_utc TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS task (
        task_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, category TEXT NOT NULL,
        headline TEXT NOT NULL, status TEXT NOT NULL, created_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS approval_request (
        request_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, action_name TEXT NOT NULL,
        details TEXT NOT NULL, status TEXT NOT NULL, created_utc TEXT NOT NULL,
        decision_note TEXT NOT NULL DEFAULT ''
    );''')
    conn.commit()
    return conn


def _validate_activity(event: dict) -> dict:
    if set(event)!={'event_id','business_id','date','kind','amount_cad','minutes','source_ref'}:
        raise SetupError('Ledger event must have exactly event_id, business_id, date, kind, amount_cad, minutes, source_ref.')
    event_id=safe_id(event['event_id']);bid=safe_id(event['business_id'])
    kind=event['kind']
    if kind not in KINDS:
        raise SetupError('Unknown ledger event kind.')
    try:
        d=date.fromisoformat(event['date'])
    except (ValueError,TypeError) as e:
        raise SetupError('Date must be YYYY-MM-DD.') from e
    if d.isoformat()!=event['date']:
        raise SetupError('Date must be exact YYYY-MM-DD.')
    amount=money(event['amount_cad'])
    try:
        minutes=int(event['minutes'])
        if str(minutes)!=str(event['minutes']).strip() or minutes<0 or minutes>525600:
            raise ValueError('minutes')
    except (ValueError,TypeError) as e:
        raise SetupError('Minutes must be a reasonable non-negative integer.') from e
    if (kind=='owner_minutes') != (minutes>0) or (kind=='owner_minutes' and amount!=0) or (kind!='owner_minutes' and minutes!=0):
        raise SetupError('Only owner_minutes records nonzero minutes; other events record nonnegative CAD.')
    ref=event['source_ref']
    if not isinstance(ref,str) or len(ref)>180:
        raise SetupError('Source reference must be <=180 characters and must not be a secret or person name.')
    return {'event_id':event_id,'business_id':bid,'event_date':d.isoformat(), 'kind':kind,
            'amount_cad':str(amount),'minutes':minutes,'source_ref':ref,
            'source_status':'HUMAN_ENTERED_UNRECONCILED','created_utc':_now()}


def record(event: dict, root: Path = PRIVATE) -> bool:
    clean=_validate_activity(event)
    conn=connect(root)
    try:
        with conn:
            exists=conn.execute('SELECT * FROM activity WHERE event_id=?',(clean['event_id'],)).fetchone()
            if exists:
                keys=('event_id','business_id','event_date','kind','amount_cad','minutes','source_ref')
                if all(str(exists[k])==str(clean[k]) for k in keys):
                    return False  # idempotent exact duplicate
                raise SetupError('Event ID is already used by different data. Nothing changed.')
            conn.execute('''INSERT INTO activity(event_id,business_id,event_date,kind,amount_cad,minutes,source_ref,source_status,created_utc)
                            VALUES (:event_id,:business_id,:event_date,:kind,:amount_cad,:minutes,:source_ref,:source_status,:created_utc)''',clean)
        return True
    finally:
        conn.close()


def import_csv(path: Path, root: Path = PRIVATE) -> dict:
    """All-or-nothing input validation and commit, conflict-safe exact repeats."""
    if not path.is_file() or path.stat().st_size>2*1024*1024:
        raise SetupError('Import must be an existing local CSV smaller than 2 MB.')
    try:
        with path.open('r',encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            expected={'event_id','business_id','date','kind','amount_cad','minutes','source_ref'}
            if not reader.fieldnames or set(reader.fieldnames)!=expected or len(reader.fieldnames)!=len(expected):
                raise SetupError('Ledger CSV must have exactly: '+', '.join(sorted(expected)))
            validated=[]
            for row in reader:
                if len(validated)>=10000 or None in row or any(v is None for v in row.values()):
                    raise SetupError('CSV row is malformed or import exceeds 10,000 rows.')
                validated.append(_validate_activity(row))
    except (UnicodeError,csv.Error) as e:
        raise SetupError('Ledger CSV must be valid UTF-8.') from e
    seen={}
    for record_row in validated:
        eid=record_row['event_id']
        if eid in seen:
            raise SetupError('Repeated event_id in the imported file; resolve before retrying.')
        seen[eid]=record_row
    conn=connect(root)
    added=0
    try:
        with conn:
            for clean in validated:
                exists=conn.execute('SELECT * FROM activity WHERE event_id=?',(clean['event_id'],)).fetchone()
                if exists:
                    keys=('event_id','business_id','event_date','kind','amount_cad','minutes','source_ref')
                    if not all(str(exists[k])==str(clean[k]) for k in keys):
                        raise SetupError('Existing event ID has different data; entire import cancelled.')
                    continue
                conn.execute('''INSERT INTO activity(event_id,business_id,event_date,kind,amount_cad,minutes,source_ref,source_status,created_utc)
                                VALUES (:event_id,:business_id,:event_date,:kind,:amount_cad,:minutes,:source_ref,:source_status,:created_utc)''',clean)
                added+=1
    finally:
        conn.close()
    return {'imported':added,'exact_duplicates_skipped':len(validated)-added,
            'source_status':'HUMAN_ENTERED_UNRECONCILED'}


def summary(root: Path = PRIVATE) -> dict:
    conn=connect(root)
    try:
        lines=[dict(r) for r in conn.execute('SELECT business_id,kind,amount_cad,minutes FROM activity')]
        pending=conn.execute("SELECT COUNT(*) FROM task WHERE status='pending'").fetchone()[0]
        reviews=conn.execute("SELECT COUNT(*) FROM approval_request WHERE status='pending'").fetchone()[0]
        active=conn.execute("SELECT COUNT(*) FROM candidate WHERE stage IN ('researching','buyer_signal','offered','funded','delivering')").fetchone()[0]
    finally:
        conn.close()
    totals={k:Decimal('0') for k in KINDS if k!='owner_minutes'}
    mins=0
    by_business={}
    for l in lines:
        bid=l['business_id']
        b=by_business.setdefault(bid,{'revenue':Decimal(0),'refund':Decimal(0),'fee':Decimal(0),'expense':Decimal(0),'owner_minutes':0,'settlement':Decimal(0)})
        if l['kind']=='owner_minutes':
            mins+=int(l['minutes']);b['owner_minutes']+=int(l['minutes'])
        else:
            amount=Decimal(l['amount_cad']);totals[l['kind']]+=amount;b[l['kind']]+=amount
    profit=totals['revenue']-totals['refund']-totals['fee']-totals['expense']
    wage=Decimal(mins)/Decimal(60)*Decimal(30)
    return {'source_status':'UNRECONCILED_HUMAN_ENTRIES_NOT_BANK_DATA',
            'revenue_cad':str(totals['revenue']), 'refund_cad':str(totals['refund']),
            'fee_cad':str(totals['fee']),'expenses_cad':str(totals['expense']),
            'operating_profit_cad':str(profit),
            'owner_hours':round(mins/60,2),
            'illustrative_owner_hour_value_cad':30,
            'economic_profit_cad':str((profit-wage).quantize(Decimal('0.01'))),
            'payouts_recorded_cad':str(totals['settlement']),
            'payouts_are_not_new_revenue':True,
            'pending_tasks':pending,'pending_approvals':reviews,'active_candidates':active,
            'by_business':{bid:{**{k:str(v) for k,v in d.items() if k!='owner_minutes'},
                                'owner_hours':round(d['owner_minutes']/60,2)} for bid,d in by_business.items()},
            'note':'Manual values are not independently reconciled, do not calculate GST/HST, tax or available bank cash.'}


def set_candidate(business_id: str, stage: str, evidence_ref: str='', note: str='',root: Path=PRIVATE) -> None:
    safe_id(business_id)
    if stage not in STAGES: raise SetupError('Invalid candidate stage; live deployment is intentionally unavailable.')
    if stage in HIGH_STAGES and not evidence_ref:
        raise SetupError('Record a human-checkable evidence reference before progressing.')
    if len(evidence_ref)>200 or len(note)>500:
        raise SetupError('Evidence and notes must be short, non-sensitive references.')
    conn=connect(root)
    try:
        with conn:
            conn.execute('''INSERT INTO candidate(business_id,stage,evidence_ref,note,reviewed_utc)
                            VALUES(?,?,?,?,?) ON CONFLICT(business_id) DO UPDATE SET
                            stage=excluded.stage,evidence_ref=excluded.evidence_ref,
                            note=excluded.note,reviewed_utc=excluded.reviewed_utc''',
                         (business_id,stage,evidence_ref,note,_now()))
    finally:conn.close()


def create_tasks(candidates: list[dict],root: Path=PRIVATE) -> int:
    """Refresh safe local research/draft tasks; no background workers or external actions."""
    conn=connect(root);added=0
    try:
        with conn:
            for row in candidates:
                bid=safe_id(row['id'])
                for kind,title in [('research','Check actual buyer demand, alternatives and permitted source URLs'),
                                   ('draft','Review scope, pricing, prototype and buyer-proof checklist')]:
                    tid=bid+'-'+kind
                    if conn.execute('SELECT 1 FROM task WHERE task_id=?',(tid,)).fetchone():
                        continue
                    conn.execute('INSERT INTO task VALUES (?,?,?,?,?,?,?)',
                                 (tid,bid,kind,title,'pending',_now(),_now()))
                    added+=1
    finally:conn.close()
    return added


def get_tasks(root: Path=PRIVATE) -> list[dict]:
    conn=connect(root)
    try:return [dict(r) for r in conn.execute('SELECT * FROM task ORDER BY status,created_utc,task_id LIMIT 500')]
    finally:conn.close()


def finish_task(task_id: str,root: Path=PRIVATE) -> bool:
    safe_id(task_id)
    conn=connect(root)
    try:
        with conn:
            count=conn.execute("UPDATE task SET status='reviewed', updated_utc=? WHERE task_id=? AND status='pending'",(_now(),task_id)).rowcount
        return count>0
    finally:conn.close()


def request_approval(business_id: str, action_name: str, details: str,root: Path=PRIVATE) -> str:
    safe_id(business_id)
    if action_name not in ('public_launch','spending','customer_outreach','provider_connection','billing_changes','production_release'):
        raise SetupError('Unknown approval request category.')
    if not isinstance(details,str) or not details.strip() or len(details)>600:
        raise SetupError('A short plain-language request description is required.')
    req='request_'+uuid4().hex
    conn=connect(root)
    try:
        with conn:
            conn.execute('INSERT INTO approval_request(request_id,business_id,action_name,details,status,created_utc) VALUES (?,?,?,?,?,?)',
                         (req,business_id,action_name,details,'pending',_now()))
    finally:conn.close()
    return req


def get_approvals(root: Path=PRIVATE) -> list[dict]:
    conn=connect(root)
    try:return [dict(r) for r in conn.execute('SELECT * FROM approval_request ORDER BY created_utc DESC LIMIT 200')]
    finally:conn.close()


def resolve_approval(request_id: str,decision: str,note: str='',root: Path=PRIVATE) -> None:
    safe_id(request_id)
    if decision not in ('reviewed','declined'):
        raise SetupError('Only local reviewed/declined decisions are allowed; no external action is authorized.')
    conn=connect(root)
    try:
        with conn:
            if conn.execute('UPDATE approval_request SET status=?,decision_note=? WHERE request_id=? AND status=\'pending\'',
                            (decision,note[:400],request_id)).rowcount!=1:
                raise SetupError('Unknown or already resolved request.')
    finally:conn.close()
