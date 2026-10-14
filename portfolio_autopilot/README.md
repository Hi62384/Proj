## Organized research library — new primary research view

Open `Opportunity_Library.html` in the project root, or use **Open the organized Opportunity Library** in the local workbench. The installed factory now prefers `opportunity_library/data/factory_catalog.csv`: 1,512 research records (1,296 preserved + 216 new hypotheses), 36 categories and 144 subcategories. Two personal-capital research notes are excluded from normal launch selection. None represents verified paid demand.

The existing sales pack, original IDs, research files and runtime data remain intact. Category, public-privacy and whole-business workload lenses help discovery; they do not create accounts or remove legal obligations. An explicit custom catalogue path still works, and without the optional library the factory falls back to the old atlas. The original Phase-0 CLI continues to use its original atlas by default.

Read `opportunity_library/README.md` and its methodology before treating score differences as evidence. Rebuilding this library is offline and is not fresh market research.

---

# Portfolio Autopilot — Phase 0 (safe, local-first)

This code turns the repository's 1,296-record research index into a **review-only shortlist and AI task-packet generator**. It is not a live business, customer acquisition bot, autonomous executor, SaaS, merchant account or payment integration.

## Start in 2 minutes

Use Python 3.11+ from the repository root; no third-party packages:

```bash
python -m unittest discover -s portfolio_autopilot/tests -v
python -m portfolio_autopilot.cli scan --limit 12 --max-per-mode 3 --html portfolio_autopilot/.local/shortlist.html
python -m portfolio_autopilot.cli prepare EXP-001-01
```

Open `portfolio_autopilot/.local/shortlist.html` locally. Run `prepare` with **any actual atlas ID**, not only the example.

```bash
# Human review only; this never publishes or contacts anyone
python -m portfolio_autopilot.cli review EXP-001-01 --status researching --note "Verify actual buyer requests"

# Mark genuine buyer evidence (human-entered reference, not automatically verified)
python -m portfolio_autopilot.cli review EXP-001-01 --status buyer_signal --evidence-ref "interview_001"

# Manually enter ACTUAL financials only after verified activity. Local unreconciled ledger.
python -m portfolio_autopilot.cli record --event-id invoice_001 --business-id EXP-001-01 --type revenue --amount 299.00
python -m portfolio_autopilot.cli record --event-id owner_001 --business-id EXP-001-01 --type owner_time --minutes 75
python -m portfolio_autopilot.cli summary
```

Generated data is under `.local/` and ignored by Git. **It is not encrypted.** Do not use this local store for passwords, personal data, customer documents, tax IDs or private financial statements. It is for opportunity IDs and non-sensitive planning metadata only. Use a private, access-controlled accounting system for real records later.

## Scheduled review queue

The optional GitHub Action `Portfolio Autopilot — draft-only weekly queue` runs tests and generates a ranked *static* queue from the existing CSV every Monday. This is **not live market research**. It uploads the report as a GitHub Actions artifact; it never sends messages, pays for anything, opens public stores, or writes to `main`. Schedule may be delayed or skipped on GitHub's infrastructure. For current demand, use your ChatGPT dot/Work with explicit instructions and date/source checks.

## Automation boundaries

- Safe today: explore all niches, rank hypotheses without skill-based bias, create packets, generate reports, test software, recommend go/no-go.
- Not implemented or authorized: scrape sites, send messages, access seller accounts, publish products, take payment, install software, charge APIs, buy ads, issue refunds, change customer data, or create a deployed business.
- A `live` status is intentionally blocked in phase 0. Real integration requires independent approval and tests.
- Financial entries are user-entered and **unreconciled**. Operating profit excludes owner remuneration and personal income taxes; economic profit charges an illustrative CAD 30/hour to owner time.
- `--include-regulated` changes *display only*. It does not approve any regulated activity.

Read `USER_SETUP_CHECKLIST.md` for your minimal-intervention setup, and `AUTOMATION_POLICIES.md` before connecting accounts.

---

## NEW: Working business launch factory (offline automation)

The original Phase 0 shortlist CLI remains available and unchanged. For a more automated, one-click workflow, use the **local-first launch factory** now located in `portfolio_autopilot/factory/`.

**On Windows:** double-click `portfolio_autopilot/Start_Autopilot.cmd`. It launches a private local browser dashboard with buttons for generating cross-industry launch kits, creating a standardized first reporting-business sales pack and packaging tested reports. It has no paid dependencies or live account integrations.

**From repository root:**

```powershell
python -m portfolio_autopilot.factory.cli doctor
python -m portfolio_autopilot.factory.cli init
python -m portfolio_autopilot.factory.cli first-business
python -m portfolio_autopilot.factory.cli serve
```

Full instructions and integration boundaries: **[`factory/README.md`](factory/README.md)**. Weekly GitHub Actions now also generates *rotated draft opportunity packets* from existing research; that is **not fresh market research or actual business operation**. The toolkit cannot create seller accounts, send messages, process payments, publish listings or access private customer information. Required account setup, approvals and live integrations remain separate until specifically authorized.
