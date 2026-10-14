"""Preflight, build and package a customer-specific reporting delivery locally.

ZIPs are local private outputs containing potentially sensitive report results.
Never commit or upload these deliveries to the public GitHub repository.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from .config import PRIVATE, ROOT, SetupError, init_private, safe_id
from .portable_runner import read_mapping, inspect_input, transform_to_validated_report

HERE=Path(__file__).parent
REPORT_ENGINE=ROOT/'research_merge'/'reporting_demo'/'report_builder.py'


def ensure_local_output(out: Path) -> Path:
    """Allow output outside the repository or under .local/, never a tracked repo path."""
    out=out.expanduser().resolve()
    repo=ROOT.resolve()
    local=(ROOT/'portfolio_autopilot'/'.local').resolve()
    if out.is_relative_to(repo) and not out.is_relative_to(local):
        raise SetupError('Customer output may not be inside the tracked/public repository; use portfolio_autopilot/.local/.')
    if out.exists():
        raise SetupError('Destination exists. Use a fresh delivery ID to avoid overwriting customer work.')
    return out


def preflight(source: Path, mapping_config: Path) -> dict:
    return inspect_input(source, read_mapping(mapping_config))


def create_delivery(source: Path, mapping_config: Path, *,
                    customer_ref: str, destination: Path | None = None) -> Path:
    """Build verified report and portable ZIP; does not deliver/send anything."""
    ref=safe_id(customer_ref)
    cfg=read_mapping(mapping_config)
    init_private()
    final=ensure_local_output(destination or PRIVATE/'deliveries'/ref)
    final.parent.mkdir(parents=True,exist_ok=True)
    # Stage beside destination so rename is atomic on the same volume.
    staging=Path(tempfile.mkdtemp(prefix='delivery-stage-',dir=final.parent))
    try:
        report_dir=staging/'results'
        summary=transform_to_validated_report(source,report_dir,cfg)
        (staging/'run_report.py').write_bytes((HERE/'portable_runner.py').read_bytes())
        (staging/'report_builder.py').write_bytes(REPORT_ENGINE.read_bytes())
        (staging/'mapping.json').write_text(json.dumps(cfg,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        (staging/'README.txt').write_text(
            'CSV REPORT AUTOMATION — PRIVATE DELIVERY\n\n'
            'This package has not been published or sent to a customer. Review the output first.\n'
            'The report is computed from the customer-approved input; no input file is included.\n'
            'Requires Python 3.10+. In this folder run:\n'
            '  python run_report.py --input YOUR_CSV.csv --config mapping.json --out NEW_REPORT_FOLDER\n\n'
            'Do not run on unapproved customer data. The source file is never modified.\n'
            'Amounts use the selected currency as a LABEL only (no conversion).\n'
            'Revenue minus input cost is not accounting or tax net profit.\n'
            'This report does not connect to databases, email, payment systems, or external APIs.\n'
            'For sensitive/regulated data, stop and establish approved privacy safeguards first.\n'
            'Before customer handoff: verify totals, acceptance, source authority and retention terms.\n',
            encoding='utf-8')
        paths=['results/report.html','results/summary.json','results/channel_summary.csv',
               'run_report.py','report_builder.py','mapping.json','README.txt']
        manifest={'schema_version':1,'status':'LOCAL_QA_REVIEW_NOT_DELIVERED',
                  'customer_ref':ref,'record_count':summary['record_count'],
                  'from':summary['from'],'to':summary['to'],
                  'currency_label':cfg['currency'],
                  'output_files':[{'name':name,'sha256':hashlib.sha256((staging/name).read_bytes()).hexdigest()} for name in paths],
                  'review_required':['confirm correct metric definitions','inspect representative outputs',
                                     'confirm data rights and retention','confirm contracted delivery channel']}
        (staging/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        paths.append('manifest.json')
        archive=staging/'customer_delivery.zip'
        with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=8) as z:
            for name in paths:
                z.write(staging/name,arcname=name)
        # Check archive members match expected approved paths and hashes.
        with ZipFile(archive) as z:
            if set(z.namelist())!=set(paths) or z.testzip() is not None:
                raise SetupError('ZIP contents or CRC validation failed.')
            for item in manifest['output_files']:
                if hashlib.sha256(z.read(item['name'])).hexdigest()!=item['sha256']:
                    raise SetupError('ZIP manifest hash verification failed.')
        staging.rename(final)
        return final
    except BaseException:
        shutil.rmtree(staging,ignore_errors=True)
        raise
