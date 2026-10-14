# Online Business Opportunity Library

**Start here: [Opportunity_Library.html](Opportunity_Library.html)** — download/open the file locally, or use the link in the existing Portfolio Autopilot dashboard.

**36 categories · 144 subcategories · 197 inherited industry slices · 1,512 research records · 69 current primary references.**

The inventory contains 1,296 preserved records and 216 additional individually specified hypotheses. Two additions are personal-capital research notes, not businesses. These totals are not counts of independently validated markets: offers can overlap and reuse business mechanisms. No exact offer has verified paid demand in this research dataset. Scores and prices are hypotheses, not promised income. Public privacy does not mean guaranteed anonymity.

## Find the right part of the project

| Area | Use | Start |
|---|---|---|
| Organized research | Categories, subcategories, buyer/industry tags, filters, comparison, privacy and passive-workload analysis | [Opportunity Library](Opportunity_Library.html) / [category index](opportunity_library/README.md) |
| Primary evidence | Dated source claims and their limits, AI-content/platform rules, identity and Canadian considerations | [Sources](opportunity_library/docs/SOURCES.md), [privacy/platform matrix](opportunity_library/docs/PRIVACY_AND_PLATFORMS.md) |
| Method and decisions | Hypotheses vs. evidence, ranking weights, profit vs. capital returns, paid-validation gates | [Methodology](opportunity_library/docs/METHODOLOGY.md), [workflow](opportunity_library/docs/OPERATING_WORKFLOW.md) |
| Existing local factory | Draft sales packages, review queues, CSV report packaging and manually entered operations | [Factory guide](portfolio_autopilot/factory/README.md) / `portfolio_autopilot/Start_Autopilot.cmd` |
| Existing execution manual | Long-form per-opportunity plans; retained as historical planning context | [Master plan](MASTER_EXECUTION_PLAN.md) |
| Preserved original studies | Original 54/60/1,296-source research, scenarios, older dashboards and overlap notes | [Source archive](research_merge/README.md), `opportunities.json`, `sources.json`, `README.txt` |
| Financial models | Separate original what-if calculations; not live accounts or a combined forecast | `financial_model.mjs`, `assumptions.json`, `research_merge/fast_cash_assumptions.json` |
| Unrelated applications | Preserved, outside this research update | `VaultDesk/` |

### Broad coverage without a permanent niche preference

Content and media; marketing and commerce; design, games, education and software; data, reporting, finance and market tools; privacy, accessibility and people operations; trades, property, logistics, manufacturing, hospitality, health administration, agriculture and nonprofit/public services. Each category contains four subcategories and six new concrete hypotheses, plus relevant preserved records.

One record has one primary category, with cross-category and industry tags rather than duplicate copies. This structure can grow when genuine new opportunities or research justify it; adding names to a spreadsheet does not create revenue.

## Use it now

Open the HTML file directly: no installation, payment account or API key required. Use filters to compare an honest low-touch path with a faster service-sale path. Read the supporting evidence and missing questions. Select one bounded test with a real acquisition route before building or opening another platform account.

On Windows, the existing `portfolio_autopilot/Start_Autopilot.cmd` still launches the local workbench. Its research link opens the new library, and its category selector searches the expanded data. Existing first-business sales packs are not overwritten.

## Maintain it

```powershell
python -m opportunity_library.build
python -m opportunity_library.build --check
python -m unittest discover -s opportunity_library/tests -v
python -m opportunity_library.cli search --category C01 --limit 6
```

Edit source JSON in `opportunity_library/data/` and regenerate views; do not hand-edit generated category notes. The builder makes no network requests. Research updates require actually reviewed primary sources, dates and limits. Original studies and source IDs remain in place for traceability, not as a claim that their fees or recommendations remain current.

**Privacy:** Never commit credentials, identity documents, actual bank statements, customer datasets or private operations to this public repository. Runtime `.local` folders are ignored, not encrypted. Genuine identity may be required by providers, authorities and contracting clients. The library does not set up accounts, send proposals, charge customers, trade, deploy websites or guarantee income.
