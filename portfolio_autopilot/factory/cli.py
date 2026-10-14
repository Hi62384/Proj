"""One-entry CLI for a safe, reusable local business launch factory."""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path
import sys

from .catalog import catalog, find, select, summary as atlas_summary
from .config import PRIVATE, ROOT, SetupError, bootstrap, load_profile, safe_id
from .kits import make_kit
from .ledger import (connect, record, import_csv, summary as ledger_summary,
                     set_candidate, create_tasks, request_approval, get_tasks, get_approvals)
from .reporting import create_delivery, preflight
from .first_business import first_business
from .storefront import create_preview
from .rotation import create_rotation
from .portal import serve


def doctor(rows: list[dict]) -> dict:
    import platform
    return {'phase':'local-first factory; not a live business',
            'python':platform.python_version(),
            'research':atlas_summary(rows),
            'report_core_exists':(ROOT/'research_merge'/'reporting_demo'/'report_builder.py').is_file(),
            'report_tests_exist':(ROOT/'research_merge'/'reporting_demo'/'tests'/'test_report_builder.py').is_file(),
            'github_draft_workflow_exists':(ROOT/'.github'/'workflows'/'portfolio-autopilot-draft.yml').is_file(),
            'external_actions_enabled':False,
            'extra_packages_required':0,
            'required_user_actions':['Review real opportunities, create/verify permitted seller account when needed',
                                     'Approve pricing/publication/spending/communications',
                                     'Verify paid orders and data permission before fulfillment']}


def main(argv: list[str]|None=None)->int:
    p=argparse.ArgumentParser(description='Offline business launch kits, reporting deliveries, and review dashboard.')
    p.add_argument('--workspace',type=Path,default=PRIVATE,
                   help='Ignored local folder. Do not use a Git-tracked folder for private data.')
    p.add_argument('--atlas',type=Path,default=None)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor',help='Check local prerequisites without changing external accounts')
    sub.add_parser('init',help='Create local profile placeholder (no secrets)')
    sc=sub.add_parser('scan',help='View diversified research candidates without sending anything')
    sc.add_argument('--limit',type=int,default=15)
    sc.add_argument('--per-mode',type=int,default=3)
    sc.add_argument('--modes',type=str,default='',help='Optional comma-separated F,R,D,I,M,P,A,L,C,X,ORIGINAL')
    sc.add_argument('--include-regulated',action='store_true',help='Display only; not authorized')
    kt=sub.add_parser('kit',help='Generate one complete local draft launch kit')
    kt.add_argument('id')
    batch=sub.add_parser('batch',help='Generate diversified draft kits, nothing published')
    batch.add_argument('--limit',type=int,default=6)
    batch.add_argument('--per-mode',type=int,default=2)
    batch.add_argument('--modes',type=str,default='',help='Optional comma-separated income model codes')
    qr=sub.add_parser('queue',help='Create local research/review tasks, no external workers')
    qr.add_argument('--limit',type=int,default=15)
    stage=sub.add_parser('stage',help='Record a human-entered opportunity status')
    stage.add_argument('id');stage.add_argument('status')
    stage.add_argument('--evidence-ref',default='');stage.add_argument('--note',default='')
    rq=sub.add_parser('request-approval',help='Create a review note; cannot enable external action')
    rq.add_argument('id');rq.add_argument('category');rq.add_argument('--details',required=True)
    sub.add_parser('status',help='Local-only financial/review summary')
    sub.add_parser('first-business',help='Package the synthetic reporting demo plus ready-to-edit sales drafts')
    sub.add_parser('storefront-preview',help='Combine drafted launch kits into one OFFLINE catalog mockup')
    rot=sub.add_parser('rotate',help='Draft diverse weekly industries; no live demand research')
    rot.add_argument('--count',type=int,default=6)
    rot.add_argument('--rotation-number',type=int,default=None)
    rep=sub.add_parser('report-preflight',help='Check CSV headers against a mapping; do not read rows')
    rep.add_argument('--input',type=Path,required=True);rep.add_argument('--mapping',type=Path,required=True)
    build=sub.add_parser('report-package',help='Generate tested local report ZIP and reusable runner')
    build.add_argument('--input',type=Path,required=True);build.add_argument('--mapping',type=Path,required=True)
    build.add_argument('--customer-ref',required=True);build.add_argument('--output',type=Path)
    imp=sub.add_parser('finance-import',help='Import owner-entered pseudonymous CSV, transactional')
    imp.add_argument('--file',type=Path,required=True)
    rec=sub.add_parser('finance-record',help='Record one manual event, not a bank transaction sync')
    rec.add_argument('--event-id',required=True);rec.add_argument('--business-id',required=True)
    rec.add_argument('--kind',required=True)
    rec.add_argument('--amount',default='0.00');rec.add_argument('--minutes',default='0');rec.add_argument('--source-ref',default='manual')
    svr=sub.add_parser('serve',help='Start local-only workbench at 127.0.0.1 (Ctrl+C stops it)')
    svr.add_argument('--port',type=int,default=0);svr.add_argument('--no-browser',action='store_true')
    args=p.parse_args(argv)
    try:
        args.workspace=args.workspace.expanduser().resolve()
        if args.workspace.is_relative_to(ROOT.resolve()) and not args.workspace.is_relative_to((ROOT/'portfolio_autopilot'/'.local').resolve()):
            raise SetupError('Workspace inside Git repository must be under portfolio_autopilot/.local.')
        if args.command=='init':
            loc=bootstrap(args.workspace)
            print('Local profile created/preserved:',loc)
            print('Edit only non-sensitive seller placeholders. Zero external spending and no accounts connected.')
            return 0
        if args.command=='serve':
            serve(args.port,no_browser=args.no_browser,root=args.workspace)
            return 0
        if args.command=='status':
            print(json.dumps(ledger_summary(args.workspace),indent=2));return 0
        if args.command=='first-business':
            path=first_business(args.workspace)
            print('FIRST SALES PACK — SYNTHETIC ONLY:',path)
            print('No listing, email, customer or payment account was created.');return 0
        if args.command=='storefront-preview':
            print('UNPUBLISHED CATALOGUE MOCKUP:',create_preview(args.workspace));return 0
        if args.command=='rotate':
            print(json.dumps(create_rotation(args.workspace,rotation_number=args.rotation_number,limit=args.count),indent=2));return 0
        if args.command=='report-preflight':
            print(json.dumps(preflight(args.input,args.mapping),indent=2));return 0
        if args.command=='report-package':
            dest=create_delivery(args.input,args.mapping,customer_ref=args.customer_ref,
                                 destination=args.output or args.workspace/'deliveries'/args.customer_ref)
            print('PRIVATE QA DELIVERY (NOT SENT):',dest/'customer_delivery.zip')
            print('Review report, original source rights, correctness, and customer acceptance before handoff.')
            return 0
        if args.command=='finance-import':
            print(json.dumps(import_csv(args.file,args.workspace),indent=2));return 0
        if args.command=='finance-record':
            added=record({'event_id':args.event_id,'business_id':args.business_id,'date':date.today().isoformat(),
                          'kind':args.kind,'amount_cad':args.amount,'minutes':args.minutes,
                          'source_ref':args.source_ref},args.workspace)
            print('Manual ledger record:', 'ADDED' if added else 'EXACT DUPLICATE SKIPPED');return 0
        rows=catalog(args.atlas) if args.atlas else catalog()
        if args.command=='doctor':
            print(json.dumps(doctor(rows),indent=2));return 0
        if args.command=='scan':
            modes={x.strip() for x in args.modes.split(',') if x.strip()} or None
            chosen=select(rows,limit=args.limit,per_mode=args.per_mode,modes=modes,
                          include_regulated=args.include_regulated)
            print('DRAFT OPPORTUNITY SHORTLIST — NOT VERIFIED SALES')
            for row in chosen:
                print(f"{row['id']:13s} {row.get('niche','')[:29]:29s} {row.get('revenue_mode','')[:8]:8s} {row.get('name','')} ")
            return 0
        if args.command=='kit':
            row=find(rows,safe_id(args.id))
            if row.get('legal_class','').lower().strip() not in ('standard','refer to original'):
                raise SetupError('Regulated risk: review compliance and prepare manually before generating a kit.')
            dest=make_kit(row,args.workspace,load_profile(args.workspace/'seller_profile.json'))
            print('DRAFT ONLY:',dest);return 0
        if args.command=='batch':
            if not 1<=args.limit<=50:raise SetupError('Batch limit must be 1–50.')
            modes={x.strip() for x in args.modes.split(',') if x.strip()} or None
            chosen=select(rows,limit=args.limit,per_mode=args.per_mode,modes=modes)
            created=[]
            for row in chosen:
                try:
                    dest=make_kit(row,args.workspace,load_profile(args.workspace/'seller_profile.json'))
                    created.append(str(dest))
                except SetupError as e:
                    if 'already exists' not in str(e):raise
            print(json.dumps({'new_review_only_kits':created,'generated':len(created),
                              'no_external_accounts_touched':True},indent=2));return 0
        if args.command=='queue':
            selected=select(rows,limit=args.limit,per_mode=3)
            print('Created local review tasks:',create_tasks(selected,args.workspace));return 0
        if args.command=='stage':
            find(rows,args.id)
            set_candidate(args.id,args.status,args.evidence_ref,args.note,args.workspace)
            print('Local human-asserted stage noted; no customer/payment verification or external action.');return 0
        if args.command=='request-approval':
            find(rows,args.id)
            ident=request_approval(args.id,args.category,args.details,args.workspace)
            print('Local review request:',ident,'(cannot authorize any live action)');return 0
        raise SetupError('Unknown action.')
    except (OSError,ValueError,LookupError,json.JSONDecodeError) as e:
        print('ERROR:',e,file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
