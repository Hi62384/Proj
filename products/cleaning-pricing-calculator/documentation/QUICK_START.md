# Cleaning Business Pricing & Profit Calculator

**Excel workbook • CAD example currency • Version 1.0 • Completely offline • No macros**

> **Before quoting anyone:** All prefilled assumptions are fictional illustrations. They are not market rates, tax advice, certified accounting, or guaranteed profits. Enter your actual business costs, verify applicable taxes and review each quote. The blank template begins with `SETTINGS → REVIEW BEFORE USE`.

## 5-minute startup

1. Save a working copy of `Cleaning_Pricing_Calculator.xlsx`. Keep the original unchanged as your reusable template. Open it in a modern desktop version of Microsoft Excel; other spreadsheet software has not been verified.
2. Go to **SETTINGS**. Enter *your* loaded hourly cost per worker, vehicle cost per kilometer, typical per-job overhead, contingency, target contribution margin, card/payment processing estimate, minimum price, quote rounding increment, and any sales tax rate applicable to your sales. The initial tax rate is **0% as an UNCONFIGURED PLACEHOLDER**.
3. Change the last blue setting, **Assumptions reviewed?**, from `REVIEW BEFORE USE` to `READY` only after you've checked everything, including your status under applicable tax rules.
4. Go to **SERVICES**. The seven services are examples. Adjust default on-site hours **per employee** and per-job consumable costs. Use the exact service names in the dropdowns.
5. Go to **QUICK QUOTE**. Pick a service and enter the crew count, on-site hours if you want to override the default, *paid* travel hours per person, round-trip kilometers, extra supply/overhead expenses and any discount. Make sure the status says **READY TO REVIEW**. Check the quote against actual scope and capacity.
6. Open **CLIENT QUOTE** to see a separate draft intended for customer review. It does not display your internal cost calculations. You can use Excel's normal print/export-to-PDF functionality once you've confirmed business identity and legal terms. Never send it while the status is not ready.

## What is in the workbook?

| Tab | Purpose | Editable fields |
|---|---|---|
| READ ME | Orientation, risk warnings, color legend | None |
| OVERVIEW | Dynamic KPI summaries from scenario quotes and actual-job log | None |
| QUICK QUOTE | One job quote with transparent costing and fees | Blue cells B10:B21 |
| CLIENT QUOTE | Draft customer-facing quote | Reads other tabs; not independently edited |
| JOB SCENARIOS | Up to 25 alternative job estimates | Blue columns A:I, rows 10–34 |
| JOB LOG | Enter actual job expenses after completion | Blue columns A:I and N, rows 10–34 |
| SERVICES | Seven sample service definitions | Blue columns A:C, rows 9–15 |
| SETTINGS | All major pricing assumptions and display details | Blue cells B10:B23 |

**Blue = inputs.** Dark text = calculations. Teal = key quote totals or linked presentation values. Orange warning = review required. Formula cells are not intended for editing.

## How the price is calculated

1. **Loaded labor cost** = number of employees × (on-site hours per employee + paid travel hours per employee) × fully loaded hourly cost.
2. **Operating subtotal** = loaded labor + service consumables + extra supplies + (round-trip km × mileage allowance) + base job overhead + extra overhead.
3. **Modeled job cost** = subtotal + rounded contingency.
4. **Minimum pre-tax amount after discount** = the larger of your minimum price and `[modeled cost ÷ (1 − target contribution margin − estimated payment-processing rate)]`, rounded upwards to your preferred price increment.
5. **List price** additionally compensates for any discount; the discount is deducted to find the customer **pre-tax** quote. Sales tax is calculated afterward, where applicable.
6. **Estimated contribution** = customer pre-tax quote − modeled job cost − estimated percentage payment fee. **Contribution margin** = contribution ÷ customer pre-tax quote.

This is *contribution*, not final net business profit. Not all business costs can be inferred from the spreadsheet: marketing, refunds, subscription software, some management labor, income taxes, and unexpected incidents may be missing. A credit-card processor can also charge fixed and foreign-exchange fees. Add those costs to your assumptions or account for them separately.

### Fictional worked example, using the included demonstration workbook

| Element | Amount |
|---|---:|
| Standard home cleaning, two staff × (3 h onsite + 0.25 h travel) × $25/h | CAD $162.50 |
| Base and additional consumables | CAD $13.00 |
| 12 km round trip × CAD $0.55/km | CAD $6.60 |
| Overhead allocation | CAD $14.00 |
| Operating subtotal | **CAD $196.10** |
| 8% contingency | CAD $15.69 |
| Total modeled job cost | **CAD $211.79** |
| Proposed list price, after rounding | CAD $330.00 |
| Discount | CAD $10.00 |
| Customer price excluding sales tax | **CAD $320.00** |
| Estimated payment fee (3%) | CAD $9.60 |
| Estimated contribution before income taxes and omitted business costs | **CAD $98.61** |
| Estimated contribution margin | **30.8%** |

**The demo's 0% tax is a placeholder; it must not be copied blindly.** All companies, customers, values and records in the demonstration are fictional. These figures do not represent actual customer results or typical market rates.

## Multi-quote planning

In **JOB SCENARIOS**, type a nonempty job ID and choose a service. Enter crew and adjustments in the blue cells. Up to 25 rows calculate independently, and OVERVIEW summarizes their pre-tax sales and modeled contribution. The dashboard is not a live revenue tracker: planned jobs are not actual revenue.

In **JOB LOG**, enter *observed* actual paid worker-hours, actual supplies, mileage, other costs and pre-tax money collected. The workbook computes an observed contribution estimate and quote variance. It will **not** automatically synchronize with the planner or any payment system. The illustrated sample rows in the demonstration are fictional.

## Troubleshooting

- **SELECT SERVICE / CHECK SERVICE:** Choose a service from the list instead of typing a different name.
- **REVIEW SETTINGS:** Open SETTINGS and change the last cell to READY only after verifying all assumptions.
- **CHECK INPUTS:** Ensure crew is a positive whole number, on-site hours are positive if provided, travel/expenses/discount are nonnegative, target margin + fee rate is below 100%, and rounding increment is positive.
- **No tax on the quote:** The default is 0%; that is not a tax determination. Verify the tax rate and how your business should collect it before issuing invoices or quotes.
- **Actual earnings differ:** The workbook uses assumptions and does not automatically calculate your full bookkeeping net profit. Review data and factor in omitted costs.
- **Excel asks to enable macros:** Reject the prompt. The included `.xlsx` files contain no macros.

## Safety, compatibility and privacy

Only enter information you are permitted to process. Do not put passwords, banking data, full residential addresses or unnecessary personal data into files. You may keep client names generic in exported demonstration images. The workbook has no external data connections or macros; it does not automatically upload data. Access to the files on your own device is controlled by your device and storage system.

Use a compatible Excel version with `IF`, `IFERROR`, `VLOOKUP`, `SUM`, `ROUND`, `ROUNDUP`, `COUNTIF`, `COUNTA` and `OR`. Microsoft Excel desktop compatibility should be reviewed before production use. Other apps may interpret formulas, dropdowns or formatting differently; Google Sheets support is not guaranteed.

For support, refer to the seller's actual monitored support address shown on your order confirmation. No human support response times or business outcomes are guaranteed by this template.
