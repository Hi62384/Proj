#!/usr/bin/env python3
"""Self-contained configured CSV runner (bundled next to report_builder.py).

Requires Python 3.10+ and stdlib only. No network, uploads or credentials.
The selected mapping is explicit; ambiguous columns are never guessed.
Do not use this for regulated, identifiable or confidential customer data until
an approved data-handling process exists.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import tempfile

try:
    from research_merge.reporting_demo import report_builder as core
except ModuleNotFoundError:
    import report_builder as core

CANONICAL = tuple(core.REQUIRED)

class MappingError(ValueError):
    pass


def read_mapping(path: Path) -> dict:
    try:
        config=json.loads(path.read_text(encoding='utf-8'))
    except (UnicodeError, OSError, json.JSONDecodeError) as e:
        raise MappingError('Mapping configuration is missing or invalid JSON.') from e
    if not isinstance(config,dict) or config.get('version')!=1:
        raise MappingError('Mapping must be a version 1 JSON object.')
    mapping=config.get('mapping')
    if not isinstance(mapping,dict) or set(mapping)!=set(CANONICAL):
        raise MappingError('Mapping must define exactly: '+', '.join(CANONICAL))
    if any(not isinstance(v,str) or not v or len(v)>160 for v in mapping.values()):
        raise MappingError('Source field names must be 1–160 character strings.')
    if len(set(mapping.values()))!=len(CANONICAL):
        raise MappingError('Every required field must come from a different source column.')
    label=config.get('label', 'Business report')
    currency=config.get('currency', 'CAD')
    if not isinstance(label,str) or not (1<=len(label)<=100) or any(ord(x)<32 for x in label):
        raise MappingError('Label must be 1–100 printable characters.')
    if currency not in ('CAD','USD','EUR','GBP','AUD','NZD'):
        raise MappingError('Currency is a label, not a conversion; use a supported code.')
    # Keep only allowlisted, reviewed fields in customer bundle.
    return {'version':1,'label':label,'currency':currency,'mapping':mapping}


def inspect_input(input_path: Path, config: dict) -> dict:
    if not input_path.is_file() or input_path.stat().st_size>core.MAX_BYTES:
        raise MappingError('Input missing or exceeds the 10 MB limit.')
    try:
        with input_path.open('r',encoding='utf-8-sig',newline='') as f:
            reader=csv.reader(f)
            headers=next(reader,None)
    except (UnicodeError,csv.Error) as e:
        raise MappingError('Expected UTF-8 CSV with valid header.') from e
    if not headers or len(headers)>50 or len(headers)!=len(set(headers)):
        raise MappingError('Missing, duplicate, or excessive input headers.')
    missing=sorted(set(config['mapping'].values())-set(headers))
    if missing:
        raise MappingError('Missing configured input columns: '+', '.join(missing))
    return {'supported':True, 'fields_mapped':len(config['mapping']),
            'extra_columns_ignored':len(headers)-len(config['mapping']),
            'currency':config['currency'], 'data_scanned':False}


def transform_to_validated_report(input_path: Path, output_dir: Path, config: dict) -> dict:
    """Write normalized data temporarily; validate with the original 14-test core."""
    inspect_input(input_path,config)
    with tempfile.TemporaryDirectory(prefix='report-validated-') as d:
        tmp=Path(d)/'normalized.csv'
        if os.name!='nt':
            os.chmod(d,0o700)
        try:
            with input_path.open('r',encoding='utf-8-sig',newline='') as source,\
                 tmp.open('w',encoding='utf-8',newline='') as dest:
                reader=csv.DictReader(source)
                if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):
                    raise MappingError('Duplicate or missing source header.')
                writer=csv.DictWriter(dest,fieldnames=CANONICAL)
                writer.writeheader()
                count=0
                for raw in reader:
                    count+=1
                    if count>core.MAX_ROWS:
                        raise MappingError('Input exceeds 10,000 rows.')
                    if None in raw or any(v is None for v in raw.values()):
                        raise MappingError('Input contains malformed rows; no data was silently dropped.')
                    writer.writerow({c:raw[config['mapping'][c]] for c in CANONICAL})
        except (UnicodeError,csv.Error) as e:
            raise MappingError('Input CSV encoding/format invalid.') from e
        records=core.read_records(tmp)
        summary=core.summarize(records)
        core.write_report(summary,output_dir,config['label'],config['currency'])
    return summary


def main(argv: list[str]|None=None) -> int:
    ap=argparse.ArgumentParser(description='Offline configured CSV reporting. Does NOT upload data.')
    ap.add_argument('--input',required=True,type=Path,help='Authorized CSV export')
    ap.add_argument('--config',type=Path,default=Path(__file__).parent/'mapping.json')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--check-only',action='store_true',help='Inspect CSV headers, not data')
    args=ap.parse_args(argv)
    try:
        config=read_mapping(args.config)
        if args.check_only:
            print(json.dumps(inspect_input(args.input,config),indent=2));return 0
        summary=transform_to_validated_report(args.input,args.out,config)
        print(f"Validated {summary['record_count']} records. Local output: {args.out}")
        print('Source files were not modified. Revenue minus input cost is not business net profit.')
        return 0
    except (MappingError,core.ValidationError,OSError,ValueError,KeyError) as e:
        print('ERROR: '+str(e),file=__import__('sys').stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
