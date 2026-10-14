# Using the organized library without creating another setup burden

## Start with the browser, not 36 new accounts

Open `Opportunity_Library.html` in the repository root. No internet, installation, API keys or paid plan is needed for the local browser. It embeds the catalogue and provides category/subcategory/industry/model/privacy/workload filters. Source links need internet. All records are research; no action in this browser publishes, pays, sends messages, places trades or authorizes contracts.

Use the **Low-touch & public privacy** lens for products that might run with less ongoing work after validation. Use **Fast cash** to compare practical first-sale tests. Neither lens is a forecast. The main categories are not industry silos: secondary tags, buyer text and 197 inherited industry tags connect shared mechanisms across niches.

For one shortlist, compare three offers with different distribution paths. Read their exact output, free/paid alternatives, current source evidence, human workload, privacy review and stop rule. Prefer an inexpensive demonstration and a buyer conversation over another storefront.

## A practical first-week cycle

Day 1: select a few research candidates across different sectors. Inspect at least one current primary competitor/policy source for each. Record the unresolved customer and disclosure questions.

Day 2: produce one bounded honest sample and a price/acceptance draft for the best supported candidate. Keep synthetic examples clearly marked. Reuse an existing engine only when its input/output contract actually fits.

Days 3–4: use permitted channels to find real buying intent; review and send tailored proposals yourself where the platform requires it. Keep the existing CSV reporting offer as an optional first revenue experiment, not a permanent niche preference. Do not upload private customer data to this library.

Days 5–7: complete a paid pilot if obtained, otherwise record objections and revise the offer/channel. Track **all** time, fees and refund/support obligations. A score, generated sales pack or free download never changes a record to validated.

## Automation after validation

Share schemas, tests, versioned releases, intake adapters, approved billing/fulfillment, support knowledge and a reconciled actual ledger. Isolate customer data, credentials, terms and failure switches per business. Use deterministic code for financial arithmetic. AI can draft, classify and assist development; it cannot verify its own assumptions by writing them confidently.

One email/provider/storefront can support several eligible offers. Open another account only when an actual product needs that channel and its fee/identity/automation rules have been reviewed. A hypothetical 1,512-record library is not a task list to operate 1,512 companies.

## Keep research separate from live operations

Canonical research inputs: `opportunity_library/data/` JSON files and the preserved `research_merge/` source atlas. Generated files: catalogue JSON/CSV, category Markdown, and root HTML. Runtime factory files: existing `portfolio_autopilot/.local/` (ignored by Git, not encrypted). Original financial scenarios: preserved and separate. Real customer material belongs in suitable private storage, not any of these research folders.

The factory automatically prefers the expanded compatibility CSV when installed and falls back to the old atlas otherwise. Existing IDs and the reporting sales pack still work. Review flags remain blocked where appropriate. The old Phase-0 shortlist command still reads its original atlas by default; the new library CLI and factory use the new index. This separation prevents breaking earlier scripts.

## Updating and testing

From repository root:

```powershell
python -m opportunity_library.build
python -m opportunity_library.build --check
python -m unittest discover -s opportunity_library/tests -v
python -m opportunity_library.cli search --category C01 --limit 8
python -m opportunity_library.cli show CUR-01-01
```

Add new opportunities to `data/curated_additions.json` with a new immutable ID, actual source references, scope, buyer, price hypothesis, barrier and paid test. Add a source only after inspecting it and recording exactly what it proves and does not prove. Edit taxonomy and assignments deliberately. Run the builder and tests, then review the diff.

The builder is offline and only writes known generated paths. It does not conduct live searches, validate paid demand or claim current prices after the research date. `--check` never changes files. Avoid manually editing generated category pages: edit their source data instead.

## Stop, preserve, learn

Pause a candidate when scope, customer acquisition, legal/identity exposure, source rights, quality, capital requirements or support defeat the original thesis. Keep the evidence and lessons. Never delete client obligations simply because the next idea looks more attractive. Only expand when measured economics, capacity and paid repeat behavior justify it.
