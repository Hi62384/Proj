"""Portfolio Autopilot phase zero: research selection and review-only workflows.

All commands are local. No network calls, credentials, public posts, API
payments or live customer actions exist in this package.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from html import escape
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "research_merge" / "opportunity_atlas_expanded.csv"
LOCAL = ROOT / "portfolio_autopilot" / ".local"
STATUSES = ("unreviewed", "researching", "buyer_signal", "offered", "funded", "fulfilling", "live", "paused", "retired")
EVIDENCE_REQUIRED = {"buyer_signal", "offered", "funded", "fulfilling", "live"}
LEDGER_TYPES = ("revenue", "refund", "fee", "expense", "owner_time")
WEIGHTED_OWNER_HOUR_CAD = Decimal("30")  # editable assumption, NOT a wage or tax rate
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


def load_catalog(path: Path = DEFAULT_CATALOG) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"Missing catalogue: {path}. Run this from the repository containing research_merge/.")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        needed = {"id", "name", "niche", "revenue_mode", "cross_niche_score", "legal_class"}
        if not reader.fieldnames or not needed.issubset(reader.fieldnames):
            raise ValueError("Catalogue missing expected columns: " + ", ".join(sorted(needed)))
        rows = [dict(row) for row in reader]
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Catalogue contains duplicate opportunity IDs")
    for ref in ids:
        if not SAFE_ID.fullmatch(ref):
            raise ValueError(f"Unsafe opportunity ID: {ref!r}")
    return rows


def rating(row: dict[str, str]) -> float:
    try:
        return float(row.get("cross_niche_score") or 0)
    except (ValueError, TypeError):
        return 0.0


def first_sale_days(row: dict[str, str]) -> int:
    try:
        return int(float(row.get("first_possible_sale_days_min") or 9999))
    except (ValueError, TypeError):
        return 9999


def shortlist(rows: list[dict[str, str]], limit: int = 12, max_per_mode: int = 3,
              include_regulated: bool = False, include_existing: bool = True,
              states: dict[str, dict[str, str]] | None = None) -> list[dict[str, str]]:
    """Rank hypotheses with industry/model diversity. Scores are NOT success odds."""
    if limit < 1 or max_per_mode < 1:
        raise ValueError("Limits must be positive")
    states = states or {}
    allowed = []
    for r in rows:
        if r.get("legal_class", "").strip().lower() != "standard" and not include_regulated:
            continue
        if not include_existing and r.get("parent_study", "").startswith("Repo 54"):
            continue
        if states.get(r["id"], {}).get("status") in ("paused", "retired", "live"):
            continue
        allowed.append(r)
    allowed.sort(key=lambda r: (-rating(r), first_sale_days(r), r["id"]))
    out: list[dict[str, str]] = []
    used_niches: set[str] = set()
    per_mode: dict[str, int] = {}
    for r in allowed:
        niche = r.get("niche", "").casefold()
        mode = r.get("revenue_mode", "")
        if niche in used_niches or per_mode.get(mode, 0) >= max_per_mode:
            continue
        out.append(r)
        used_niches.add(niche)
        per_mode[mode] = per_mode.get(mode, 0) + 1
        if len(out) >= limit:
            break
    return out


def read_statuses(local: Path = LOCAL) -> dict[str, dict[str, str]]:
    path = local / "statuses.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Local status file must contain an object")
    return data


def save_statuses(data: dict[str, dict[str, str]], local: Path = LOCAL) -> None:
    local.mkdir(parents=True, exist_ok=True)
    path = local / "statuses.json"
    tmp = local / "statuses.json.tmp"
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def find_id(rows: list[dict[str, str]], ref: str) -> dict[str, str]:
    matches = [r for r in rows if r["id"] == ref]
    if len(matches) != 1:
        raise ValueError(f"Unknown opportunity ID: {ref}")
    return matches[0]


def task_packet(row: dict[str, str]) -> str:
    def v(key: str) -> str:
        return (row.get(key) or "Not established").strip().replace("\r", " ").replace("\n", " ")
    return f"""# REVIEW-ONLY LAUNCH PACKET — {v('id')}

**Opportunity:** {v('name')}  
**Buyer:** {v('buyer')}  
**Industry:** {v('niche')}  
**Revenue model:** {v('business_model')} (`{v('revenue_mode')}`)  
**Demand status:** NOT VALIDATED FOR THIS OFFER. Rankings, prices and dates are hypotheses.  
**Risk classification:** {v('legal_class')} (must be independently verified)

## Proposed deliverable
{v('description')}

## Existing assumptions (not offers to publish without review)
- Indicative asking price: CAD {v('illustrative_price_cad')}; verify actual competing offers and buyer willingness to pay.
- Earliest possible first-sale window: {v('first_possible_sale_days_min')}–{v('first_possible_sale_days_max')} days; **no sale is also possible**.
- Proposed acquisition route: {v('acquisition_method')}
- Existing demand citation: {v('niche_source_url')} (may indicate only a category, NOT exact-offer demand).
- Source evidence grade: {v('evidence_grade')}.
- Main risks: {v('risk')}.

## Steps an AI worker may take immediately (no credentials required)
1. Verify that relevant buyers currently encounter this specific problem. Capture source URLs, dates and limitations.
2. Document the three best alternatives (including free and incumbent tools). Do not invent usage or revenue statistics.
3. Write one honest, fixed-scope offer and objective acceptance test. Include what is excluded.
4. Produce a minimal synthetic or licensed example without using customer information.
5. Build a demonstrable prototype or sample. Check intellectual-property origin, security, determinism and quality.
6. Write a price/contribution worksheet with downside including zero sales and all owner hours.
7. Prepare up to five tailored responses to *actual, permissioned purchase requests*, but do not send them.
8. Create a QA report, deployment checklist, basic support instructions and a safe shutdown plan.
9. Request human approval for public posting, account access, paid tools, outreach, production actions and customer promises.

## Must-pass decision gates
- [ ] Exact buyer need observed; links or permitted interviews documented
- [ ] Free and paid alternatives compared honestly
- [ ] Scope, fulfillment competence, acceptance and support limits documented
- [ ] Regulatory and licensing requirements reviewed by responsible owner
- [ ] Price and expense/capacity budget approved
- [ ] Payment provider/seller profile verified by owner
- [ ] Outreach or public launch individually approved
- [ ] Payment evidence recorded before treating as validated
- [ ] Two independent paid orders or renewal evidence before describing repeatability

**Blocked by default:** charging customers, sending messages, publishing products, logging in, spending money, external file uploads, secrets, production writes, medical/legal/safety decisions, and using unlicensed source material.

## Next human decision
Review this packet and select `researching`, `offered`, or `paused`. Never move to funded/live without a traceable human-confirmed evidence reference.
"""


def write_packet(row: dict[str, str], outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / (row["id"] + ".md")
    path.write_text(task_packet(row), encoding="utf-8")
    return path


def snapshot_html(rows: list[dict[str, str]], all_count: int) -> str:
    trs = []
    for r in rows:
        vals = [r.get("id", ""), r.get("niche", ""), r.get("revenue_mode", ""),
                r.get("name", ""), f"{rating(r):.1f}",
                f"{r.get('first_possible_sale_days_min') or '?'}–{r.get('first_possible_sale_days_max') or '?'} days",
                r.get("evidence_grade", "")]
        trs.append("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in vals) + "</tr>")
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Portfolio Autopilot — Draft Opportunity Queue</title><style>body{font:16px system-ui,sans-serif;max-width:1400px;margin:30px auto;padding:0 20px;background:#111827;color:#e5e7eb}"
            "h1{font-size:28px}p{line-height:1.5}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:10px;border-bottom:1px solid #374151;vertical-align:top}"
            ".notice{background:#273449;border-left:3px solid #fbbf24;padding:12px;border-radius:4px}th{color:#93c5fd}a{color:#93c5fd}</style>"
            "<main><h1>Portfolio Autopilot — research queue</h1>"
            f"<p class='notice'>Draft only. {all_count:,} research records screened. Zero live research or confirmed buyers are implied by this page."
            " All sales windows, scores and product prices are unverified planning estimates."
            " No accounts, websites, messages or payments were created.</p>"
            "<p>Re-check current buyer evidence before launching. Rows are diversified across industry and revenue model.</p>"
            "<table><thead><tr><th>ID</th><th>Industry</th><th>Mode</th><th>Offer</th><th>Heuristic score</th><th>Possible sale window</th><th>Evidence</th></tr></thead><tbody>"
            + "".join(trs) + "</tbody></table></main></html>")


def parse_money(v: str) -> Decimal:
    try:
        n = Decimal(v)
    except (InvalidOperation, TypeError):
        raise ValueError("Amount must be a CAD decimal number")
    if not n.is_finite() or n < 0 or n.as_tuple().exponent < -2:
        raise ValueError("Amount must be non-negative CAD with at most two decimal places")
    return n


def record_event(event: dict[str, Any], local: Path = LOCAL) -> None:
    """Append locally and reject duplicate event IDs. Entries are USER-ASSERTED, not verified receipts."""
    local.mkdir(parents=True, exist_ok=True)
    p = local / "ledger.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if json.loads(line).get("event_id") == event["event_id"]:
                raise ValueError("Duplicate event_id (event not appended)")
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def summarize_ledger(local: Path = LOCAL) -> dict[str, Any]:
    money = {x: Decimal(0) for x in LEDGER_TYPES[:-1]}
    minutes = 0
    p = local / "ledger.jsonl"
    count = 0
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            r = json.loads(ln)
            typ = r["type"]
            if typ == "owner_time":
                minutes += int(r["minutes"])
            else:
                money[typ] += parse_money(r["amount_cad"])
            count += 1
    profit = money["revenue"] - money["refund"] - money["fee"] - money["expense"]
    imputed = (Decimal(minutes) / Decimal(60) * WEIGHTED_OWNER_HOUR_CAD).quantize(Decimal("0.01"))
    return {"status":"UNRECONCILED MANUAL ENTRIES — NOT A BANK STATEMENT",
            "events":count,"income_tax_excluded":True,
            "gross_revenue_cad":str(money["revenue"]),"refunds_cad":str(money["refund"]),
            "fees_cad":str(money["fee"]),"other_expenses_cad":str(money["expense"]),
            "operating_profit_cad":str(profit),"owner_hours":round(minutes/60,3),
            "owner_time_value_assumed_cad_per_hour":str(WEIGHTED_OWNER_HOUR_CAD),
            "profit_after_imputed_owner_time_cad":str(profit-imputed)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Approval-gated research autopilot; NO external actions.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG,
                        help="Path to current opportunity_atlas_expanded.csv")
    sub = parser.add_subparsers(dest="command", required=True)
    sc = sub.add_parser("scan", help="Rank cross-industry ideas without contacting anybody")
    sc.add_argument("--limit", type=int, default=12)
    sc.add_argument("--max-per-mode", type=int, default=3)
    sc.add_argument("--include-regulated", action="store_true", help="Display flagged ideas for research, NOT approval")
    sc.add_argument("--export", type=Path, help="Optional machine-readable JSON file")
    sc.add_argument("--html", type=Path, help="Optional offline report")
    packet = sub.add_parser("prepare", help="Generate review-only offer/task/QA packet")
    packet.add_argument("id")
    packet.add_argument("--output-dir", type=Path, default=LOCAL / "packets")
    review = sub.add_parser("review", help="Manually record a candidate stage; never triggers external action")
    review.add_argument("id")
    review.add_argument("--status", choices=STATUSES, required=True)
    review.add_argument("--evidence-ref", help="Human-entered proof ID/link, required for progressed states")
    review.add_argument("--note", default="")
    led = sub.add_parser("record", help="Manually append an unreconciled actual; local only")
    led.add_argument("--event-id", required=True)
    led.add_argument("--business-id", required=True)
    led.add_argument("--type", choices=LEDGER_TYPES, required=True)
    led.add_argument("--amount", default="0")
    led.add_argument("--minutes", type=int, default=0)
    led.add_argument("--date", default=None)
    sub.add_parser("summary", help="Aggregate manually asserted records; tax not calculated")
    args = parser.parse_args(argv)
    try:
        if args.command == "summary":
            print(json.dumps(summarize_ledger(), indent=2)); return 0
        if args.command == "record":
            if not SAFE_ID.fullmatch(args.event_id) or not SAFE_ID.fullmatch(args.business_id):
                raise ValueError("event-id and business-id must be simple safe identifiers")
            d = date.fromisoformat(args.date) if args.date else date.today()
            amt = parse_money(args.amount)
            if args.type == "owner_time":
                if args.minutes <= 0 or amt != 0: raise ValueError("owner_time needs positive --minutes and amount zero")
            elif args.minutes: raise ValueError("Money events cannot also contain owner minutes")
            event = {"event_id":args.event_id,"business_id":args.business_id,"type":args.type,
                     "amount_cad":str(amt),"minutes":args.minutes,"date":d.isoformat(),
                     "input_status":"user_entered_unreconciled"}
            record_event(event); print("Recorded LOCAL UNRECONCILED event",args.event_id);return 0
        rows = load_catalog(args.catalog)
        if args.command == "scan":
            selected = shortlist(rows, limit=args.limit, max_per_mode=args.max_per_mode,
                                 include_regulated=args.include_regulated, states=read_statuses())
            print("RESEARCH HYPOTHESES — NOT VERIFIED BUYERS OR EARNINGS\n")
            for r in selected:
                print(f"{r['id']} | {r['niche']} | {r['revenue_mode']} | {r['name']} | heuristic {rating(r):.1f}")
            if args.export:
                args.export.parent.mkdir(parents=True, exist_ok=True)
                safe = {"status":"unvalidated research queue", "total_catalog_records":len(rows),
                        "selection":selected, "note":"No outreach, payment, or launch occurred"}
                args.export.write_text(json.dumps(safe, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
                print("Exported",args.export)
            if args.html:
                args.html.parent.mkdir(parents=True, exist_ok=True)
                args.html.write_text(snapshot_html(selected,len(rows)),encoding="utf-8")
                print("HTML",args.html)
        elif args.command == "prepare":
            if not SAFE_ID.fullmatch(args.id): raise ValueError("Invalid opportunity ID")
            p = write_packet(find_id(rows,args.id),args.output_dir)
            print("Generated DRAFT ONLY:",p)
        elif args.command == "review":
            row=find_id(rows,args.id)
            if args.status in EVIDENCE_REQUIRED and not args.evidence_ref:
                raise ValueError("Status requires --evidence-ref (a human-verifiable reference)")
            if args.status == "live":
                raise ValueError("Phase zero cannot mark a business live; deploy through future approved integration")
            existing=read_statuses()
            existing[row["id"]] = {"status":args.status,"evidence_ref":args.evidence_ref or "",
                                   "note":args.note[:400],"reviewed_at_utc":datetime.now(timezone.utc).isoformat()}
            save_statuses(existing)
            print("Recorded manual review; no external action:",args.id,args.status)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print("ERROR:",str(e),file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
