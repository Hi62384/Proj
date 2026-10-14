"""Read/search the categorized research. No network calls or real-world actions."""
from __future__ import annotations
import argparse
import json
import sys
from .model import DATA, read_json, query


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('search');p.add_argument('text',nargs='?',default='');p.add_argument('--category',default='');p.add_argument('--mode',default='')
    p.add_argument('--limit',type=int,default=12);p.add_argument('--min-privacy',type=int,choices=range(6),default=0)
    p.add_argument('--min-passivity',type=int,choices=range(6),default=0);p.add_argument('--standard-only',action='store_true')
    p.add_argument('--include-capital',action='store_true');p.add_argument('--lens',choices=['low_touch','fast_cash'],default='low_touch')
    p=sub.add_parser('show');p.add_argument('id');sub.add_parser('categories');args=parser.parse_args(argv)
    try:
        lib=read_json(DATA/'catalog.json')
        if args.action=='show':
            row=next((r for r in lib['records'] if r['id']==args.id),None)
            if row is None:raise ValueError('Unknown opportunity ID')
            print(json.dumps(row,indent=2,ensure_ascii=False));return 0
        if args.action=='categories':
            for c in lib['categories']:print(c['id'],c['name'])
            return 0
        if args.category and args.category not in {c['id'] for c in lib['categories']}:raise ValueError('Unknown category ID')
        rows=query(lib,text=args.text,category=args.category,mode=args.mode,min_privacy=args.min_privacy,
                   min_passivity=args.min_passivity,include_review=not args.standard_only,
                   include_capital=args.include_capital,lens=args.lens,limit=args.limit)
        print('RESEARCH PRIORS ONLY — no verified sales, profit or anonymity\n')
        for r in rows:print(f"{r['id']:14} {r['category_id']} {r['mode']:7} {str(r['score_'+args.lens]):>4} {r['name']}")
        print(f'\n{len(rows)} records. Capital research is excluded unless explicitly requested.');return 0
    except (OSError,ValueError,KeyError) as e:
        print('ERROR:',e,file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
