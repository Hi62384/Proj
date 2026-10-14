# Portfolio Autopilot Business Factory — working local-first toolkit

**What it actually does today:** turns the repository's **1,296 unvalidated opportunity records** into cross-industry draft launch packages; gives you a local control panel; creates the first reporting business's synthetic sales pack; maps and validates approved CSV exports; packages a reusable report runner and delivery ZIP; stores pseudonymous review tasks and manually-entered financial events; produces one offline multi-product storefront preview; and adds two GitHub Actions workflows for tests and synthetic drafts.

**What it does NOT do:** set up Stripe, Upwork or other seller accounts; run paid AI; publish anything publicly; send proposals; scrape job sites; process live payments; verify buyer demand; upload customer data; or automatically manage taxes and refunds. **The factory has no external API/network client code.** GitHub Actions may consume platform compute quota but not ChatGPT Work or OpenAI API allowance.

## Windows: one-click launch

Double-click `portfolio_autopilot/Start_Autopilot.cmd` from Windows File Explorer. Requires Python 3.10+ (`py -3` or `python`) installed. A terminal stays open to host a **loopback-only** browser control panel. The script doesn't install dependencies or start any paid service. Close it or press Ctrl+C to stop.

The workbench will open at `http://127.0.0.1:<random port>/`. It has buttons for **Prepare first sales pack**, **Prepare kit**, **Create research queue**, and **Create offline catalogue preview**. The initial user profile is a placeholder file in `.local/factory/seller_profile.json`; change only non-sensitive information, and keep the spending limit at zero until you explicitly decide otherwise. The app refuses non-localhost binding and cross-origin write requests.

## Windows/macOS/Linux CLI — from repository root

```powershell
python -m portfolio_autopilot.factory.cli doctor
python -m portfolio_autopilot.factory.cli init
python -m portfolio_autopilot.factory.cli first-business
python -m portfolio_autopilot.factory.cli scan --limit 15
python -m portfolio_autopilot.factory.cli kit EXP-001-01
python -m portfolio_autopilot.factory.cli batch --limit 6
python -m portfolio_autopilot.factory.cli storefront-preview
python -m portfolio_autopilot.factory.cli status
python -m portfolio_autopilot.factory.cli serve
```

Use `py -3 -m` instead of `python -m` if your Windows launcher is named `py`. All generated files are under `portfolio_autopilot/.local/factory/` and are ignored by Git. **Ignored does not mean encrypted:** do not process confidential or regulated customer data unless you separately establish compliant private storage and consent.

## First business: complete synthetic reporting delivery

The already-tested original is `research_merge/reporting_demo/report_builder.py`. This factory supports an **explicit mapping from arbitrary header names to its five required fields**; this does not turn it into a universal two-file importer or an accounting system.

```powershell
python -m portfolio_autopilot.factory.cli report-preflight --input research_merge/reporting_demo/synthetic_sample.csv --mapping portfolio_autopilot/factory/templates/report_mapping.sample.json
python -m portfolio_autopilot.factory.cli report-package --input research_merge/reporting_demo/synthetic_sample.csv --mapping portfolio_autopilot/factory/templates/report_mapping.sample.json --customer-ref DEMO001
```

Open `.local/factory/deliveries/DEMO001/customer_delivery.zip` after running the second command. The ZIP contains HTML/CSV/JSON summaries, a mapping file and portable runnable Python scripts. No original input CSV is included, and nothing is sent to a customer. It must be reviewed before real delivery.

To package a real job: make an approved mapping JSON with the *actual authorized* source headers; use a pseudonymous customer-ref; preflight, generate and review in a private workspace. Reject any job requiring unsupported data, complex accounting, unauthorized content, or live system access. Get a funded milestone and written acceptance spec before paid work. See `../research_merge/INTAKE_AND_ACCEPTANCE.md`.

## Manual actuals ledger (not financial-account integration)

Prepare a CSV with exact columns `event_id,business_id,date,kind,amount_cad,minutes,source_ref` using the synthetic template. Kind is one of `revenue`, `refund`, `fee`, `expense`, `owner_minutes`, `settlement`. Each event must have a unique ID. `settlement` represents a payout, **not a new sale**. The import rejects conflicts and is idempotent.

```powershell
python -m portfolio_autopilot.factory.cli finance-import --file PATH_TO_LOCAL_CSV.csv
python -m portfolio_autopilot.factory.cli status
```

Amounts are human-entered and **unreconciled**. The dashboard calculates an illustrative economic profit by valuing owner time at CAD 30/hour, not a tax or accounting result. Do not put personal or financial-identifying data into CSVs or the public repository.

## Automation infrastructure and reuse

- One seller profile placeholder, one standard launch kit template, one private state store, one internal review system.
- A self-contained deliverable builder and automated test suite for the first reporting offer.
- One static, offline multi-business product preview; it is not a public checkout store.
- GitHub CI tests on pull requests/pushes; `portfolio-factory-drafts.yml` can generate downloadable synthetic packets on manual workflow dispatch. Nothing commits, deploys or sends messages.
- Existing weekly draft research workflow remains unchanged; its results are based on existing data, not live market monitoring.

## Recommended order (do not set up ten services first)

1. Generate first-business pack and open synthetic report (minutes).
2. Verify one freelancer account only when ready to propose; edit Upwork profile using honest samples.
3. Search for current buyer requests; approve individual tailored proposals and funded milestones.
4. Customize the existing reporting pipeline for accepted tasks; measure delivery hours.
5. Once paid repetition exists, connect checkout, automation scheduler and email/fulfillment under an explicit budget and tested approval boundary.
6. Only then reuse the factory for unrelated product/industry pilots; acquiring customers remains separate from generating products.

See `docs/INTEGRATIONS_AND_ACCOUNTS.md`, `docs/DEVELOPMENT_AND_SECURITY.md` and `docs/LAUNCH_CHECKLIST.md`.

## Automatic weekly cross-sector rotation

The original weekly read-only GitHub workflow now also produces a **different rotating six-sector draft batch** and a static mock storefront. It does NOT query current job boards or verify demand. When the patch is committed/pushed to GitHub and Actions enabled, check the workflow artifact every week; review real buyer signals before treating a drafted idea as a business. You can run the rotation locally:

```powershell
python -m portfolio_autopilot.factory.cli rotate --count 6
```

This process consumes no ChatGPT Work usage or OpenAI API calls. GitHub Actions compute/storage quotas still apply. Use the manual `Portfolio factory - generate offline launch drafts` workflow to create synthetic packets on demand.
