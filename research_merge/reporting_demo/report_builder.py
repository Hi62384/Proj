#!/usr/bin/env python3
"""Local CSV-to-HTML reporting proof of concept. No network calls or AI dependency.

This is a demonstration, not a hosted service or a general accounting tool.
Supported input: one currency; date, order_id (unique record ID), channel, revenue,
cost. Dates ISO YYYY-MM-DD. Money: signed plain decimals with <=2 decimal places.
A client adaptation needs agreed KPI definitions, tests, consent, and acceptance.
"""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from html import escape
import io
import json
from pathlib import Path
import re
import sys
from typing import Any

MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 10_000
REQUIRED = ("date", "order_id", "channel", "revenue", "cost")
MONEY = re.compile(r"^[+-]?\d+(?:\.\d{1,2})?$")

class ValidationError(ValueError):
    """Input does not satisfy the agreed demonstration schema."""

@dataclass(frozen=True)
class Record:
    day: date
    record_id: str
    channel: str
    revenue: Decimal
    cost: Decimal

def parse_money(value: str, row: int, field: str) -> Decimal:
    value = value.strip()
    if not MONEY.fullmatch(value):
        raise ValidationError(f"Row {row}: {field} must be a plain decimal with at most two decimal places.")
    number = Decimal(value)
    if abs(number) > Decimal("1000000000"):
        raise ValidationError(f"Row {row}: {field} exceeds this demo's amount limit.")
    return number

def read_records(path: Path, max_rows: int = MAX_ROWS) -> list[Record]:
    if not path.is_file():
        raise ValidationError("Input CSV file does not exist.")
    if path.stat().st_size > MAX_BYTES:
        raise ValidationError("Input exceeds the 10 MB demonstration limit.")
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            if not fields:
                raise ValidationError("Input is empty or missing its header.")
            if len(fields) != len(set(fields)):
                raise ValidationError("Duplicate column names are not allowed.")
            missing = set(REQUIRED) - set(fields)
            if missing:
                raise ValidationError("Missing required columns: " + ", ".join(sorted(missing)))
            if len(fields) > 50:
                raise ValidationError("Too many columns for this demonstration.")
            records: list[Record] = []
            seen: set[str] = set()
            for rownum, raw in enumerate(reader, start=2):
                if len(records) >= max_rows:
                    raise ValidationError("Input exceeds the row limit.")
                if None in raw or any(raw.get(k) is None for k in REQUIRED):
                    raise ValidationError(f"Row {rownum}: inconsistent number of fields.")
                if any(len(raw[k] or "") > 500 for k in REQUIRED):
                    raise ValidationError(f"Row {rownum}: a required field is too long.")
                rid = raw["order_id"].strip()
                channel = raw["channel"].strip()
                if not rid or not channel:
                    raise ValidationError(f"Row {rownum}: order_id and channel are required.")
                if rid in seen:
                    raise ValidationError(f"Row {rownum}: duplicate unique record ID. Review source data; nothing was silently removed.")
                try:
                    d = date.fromisoformat(raw["date"].strip())
                except ValueError as exc:
                    raise ValidationError(f"Row {rownum}: date must be YYYY-MM-DD.") from exc
                if raw["date"].strip() != d.isoformat():
                    raise ValidationError(f"Row {rownum}: use exact YYYY-MM-DD dates.")
                records.append(Record(d, rid, channel,
                                      parse_money(raw["revenue"], rownum, "revenue"),
                                      parse_money(raw["cost"], rownum, "cost")))
                seen.add(rid)
    except (UnicodeError, csv.Error) as exc:
        raise ValidationError("Input must be a valid UTF-8 CSV.") from exc
    if not records:
        raise ValidationError("No data records found.")
    return records

def summarize(records: list[Record]) -> dict[str, Any]:
    if not records:
        raise ValidationError("Cannot summarize an empty dataset.")
    revenue = sum((r.revenue for r in records), Decimal("0"))
    cost = sum((r.cost for r in records), Decimal("0"))
    groups: dict[str, dict[str, Any]] = {}
    for rec in records:
        item = groups.setdefault(rec.channel, {"records": 0, "revenue": Decimal("0"), "cost": Decimal("0")})
        item["records"] += 1
        item["revenue"] += rec.revenue
        item["cost"] += rec.cost
    channels=[]
    for channel,item in sorted(groups.items()):
        channels.append({"channel":channel,"records":item["records"],
                         "revenue":str(item["revenue"].quantize(Decimal(".01"))),
                         "cost":str(item["cost"].quantize(Decimal(".01"))),
                         "revenue_minus_input_cost":str((item["revenue"]-item["cost"]).quantize(Decimal(".01")))})
    return {"record_count":len(records),"from":min(r.day for r in records).isoformat(),
            "to":max(r.day for r in records).isoformat(),
            "revenue":str(revenue.quantize(Decimal(".01"))),
            "input_cost":str(cost.quantize(Decimal(".01"))),
            "revenue_minus_input_cost":str((revenue-cost).quantize(Decimal(".01"))),
            "channels":channels,
            "note":"Input revenue minus input cost is NOT net business profit; other expenses/taxes may be absent."}

def safe_csv_text(value: Any) -> str:
    """Prevent text fields being interpreted as spreadsheet formulas."""
    text = str(value)
    stripped = text.lstrip(" \t\r\n")
    return "'" + text if stripped.startswith(("=", "+", "-", "@")) or text.startswith(("\t","\r","\n")) else text

def render_html(data: dict[str, Any], label: str, currency: str) -> str:
    e=escape
    def amount(v: str)->str:
        return f"{e(currency)} {Decimal(v):,.2f}"
    body="".join("<tr><td>"+e(row["channel"])+"</td><td>"+str(row["records"])+"</td><td>"+
                 amount(row["revenue"])+"</td><td>"+amount(row["cost"])+"</td><td>"+
                 amount(row["revenue_minus_input_cost"])+"</td></tr>" for row in data["channels"])
    return """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>CSV report demonstration</title><style>
body{font:16px/1.6 system-ui,sans-serif;margin:0;background:#f4f7fa;color:#182b3c}
main{max-width:1050px;margin:auto;padding:36px 24px}header{border-bottom:3px solid #147f89;padding-bottom:20px}
h1{font-size:34px;line-height:1.2;margin:8px 0}.eyebrow{letter-spacing:.13em;font-size:12px;font-weight:700}
.cards{display:flex;gap:16px;flex-wrap:wrap;margin:28px 0}.card{background:white;padding:22px;flex:1;min-width:180px;border:1px solid #dbe4eb;border-radius:10px}
.value{font-size:27px;font-weight:700;margin-top:8px}.note{background:#fff3cc;padding:16px;border-radius:8px}
table{border-collapse:collapse;width:100%;background:white}td,th{text-align:right;padding:13px;border-bottom:1px solid #e1e7ed}
td:first-child,th:first-child{text-align:left}th{background:#173047;color:white}.table{overflow:auto}footer{font-size:13px;color:#496075;margin-top:24px}
</style><main><header><div class="eyebrow">LOCAL REPORTING PROOF OF CONCEPT</div><h1>"""+e(label)+"""</h1>
<div>"""+e(data["from"])+""" to """+e(data["to"])+""" · """+str(data["record_count"])+""" unique records</div></header>
<div class="cards"><div class="card">Input revenue<div class="value">"""+amount(data["revenue"])+"""</div></div>
<div class="card">Input cost<div class="value">"""+amount(data["input_cost"])+"""</div></div>
<div class="card">Revenue minus input cost<div class="value">"""+amount(data["revenue_minus_input_cost"])+"""</div></div></div>
<p class="note">This demonstration is not an accounting statement. Revenue minus the supplied cost field is not net business profit.
Fees, owner labour, taxes, marketing and other costs may be absent. A synthetic sample is not client evidence.</p>
<h2>Reconciled channel summary</h2><div class="table"><table><thead><tr><th>Channel</th><th>Records</th><th>Revenue</th><th>Input cost</th><th>Difference</th></tr></thead>
<tbody>"""+body+"""</tbody></table></div><footer>Strict schema, unique-ID checks and deterministic decimal arithmetic.
No network requests, tracking pixels, external scripts, credential collection or AI-generated financial claims.</footer></main></html>"""

def write_report(data: dict[str, Any], output: Path, label: str, currency: str, overwrite: bool=False) -> None:
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise ValidationError("Currency must be a three-letter uppercase label. No conversion is performed.")
    targets=[output/"report.html",output/"summary.json",output/"channel_summary.csv"]
    if not overwrite and any(p.exists() for p in targets):
        raise ValidationError("Output already exists; choose a new folder or explicitly use --overwrite.")
    output.mkdir(parents=True, exist_ok=True)
    html=render_html(data,label,currency)
    rows=io.StringIO(newline="")
    writer=csv.writer(rows)
    writer.writerow(["channel","records","revenue","input_cost","revenue_minus_input_cost"])
    for row in data["channels"]:
        writer.writerow([safe_csv_text(row["channel"]),row["records"],row["revenue"],row["cost"],row["revenue_minus_input_cost"]])
    for path,text in zip(targets,[html,json.dumps(data,indent=2),rows.getvalue()]):
        # Only known output filenames are touched; source file is never modified.
        temporary=path.with_suffix(path.suffix+".tmp")
        temporary.write_text(text,encoding="utf-8")
        temporary.replace(path)

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path)
    parser.add_argument("--out",type=Path,default=Path("report_output"))
    parser.add_argument("--label",default="Synthetic demonstration — not real customer results")
    parser.add_argument("--currency",default="CAD")
    parser.add_argument("--overwrite",action="store_true")
    args=parser.parse_args()
    try:
        source=args.input.resolve()
        if source in {(args.out/p).resolve() for p in ("report.html","summary.json","channel_summary.csv")}:
            raise ValidationError("An output path would overwrite the source file.")
        data=summarize(read_records(source))
        write_report(data,args.out,args.label,args.currency,args.overwrite)
        print(f"Validated {data['record_count']} records. Report: {args.out/'report.html'}")
        return 0
    except (ValidationError,OSError) as exc:
        print(f"Report not delivered: {exc}",file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
