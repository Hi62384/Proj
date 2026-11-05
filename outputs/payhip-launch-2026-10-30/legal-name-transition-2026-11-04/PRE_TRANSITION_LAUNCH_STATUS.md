# Cedargrid Digital — current launch status

Updated **2026-11-04**, America/Vancouver. **Both products are published: Cleaning CAD15 and Inventory CAD9.** The storefront and approved support/refund page are published. Both zero-charge checkout tests passed, including download-page display and receipt-email delivery. The owner reconfirmed publication and requested lower prices. No real payment was charged.

## 1. Work completed

- Payhip now explicitly shows **PayPal Connected** after the owner privately completed authorization. Stripe is not connected.
- The approved Cleaning v1.0.1 ZIP is saved and its owner-download hash matched exactly.
- Inventory has been corrected, independently tested, uploaded and saved at CAD19 while Invisible. The original test package remains backed up.
- The owner approved the 14-day voluntary refund policy, two-business-day response target and Inventory single-business licence.
- Created and published **Support and Refunds**, added it to the footer beside Shop and Contact, and observed Payhip's explicit Published confirmation.
- Completed Cleaning's CA$0 checkout: download page observed, one-use coupon exhausted, and receipt-email arrival confirmed by the owner.
- Implemented, deployed and owner-enabled **Automatically allow routine work** in Computer Bridge. Live project Read, same-site tab refresh and existing Invisible-product saves completed without approval cards.

## 2. Tests passed

| Area | Verified result |
|---|---|
| Cleaning native Calc calculation/input matrix | 59/59 passed against independent Decimal calculations |
| Cleaning existing workbook regression checks | 9/9 passed |
| Inventory native Calc matrix | 11/11 passed: ordinary, zero, fractional, large, above-threshold, missing/text and each negative-input case |
| Inventory preservation/visual checks | Original styles, print settings and unrelated cells preserved; both changed sheets and native PDF printouts reviewed |
| Bridge tests | Routine policy/runtime 10; dashboard 9; controller 11; file/desktop 25; Chrome control 29; action classification 26 passed. Counts refer to separate suites, not repeated runs. |
| Browser widget regressions | Multiline non-submit input, bounded drag, image targets and Quill paragraph handling passed |
| Live automatic approvals | Enabled flag persisted through restart; project file Read and Invisible-product saves succeeded without local cards |
| Native Microsoft Excel | Unavailable and unverified; Calc checks do not certify Excel compatibility |
| Real charged transaction | Not performed; connection and free-order success are separate evidence |

Evidence: `verification-2026-11-01/qa/candidate/results.json`, `verification-2026-11-01/qa/additional-checks.json`, `inventory-release-2026-11-03/qa/results.json`, and the preserved release manifests. No unsupported Google Sheets/Numbers/mobile workbook compatibility claim was made.

## 3. Product changes

Cleaning: input guards reject invalid assumptions/currency and invalid logged costs; summary warnings prevent misleading ready/profit states; catalogue dropdowns follow a named range; CAD-only/manual-validity/printing instructions corrected. The reviewed one-page CLIENT QUOTE correction, styling and unrelated cells remain intact. Contribution is explicitly distinct from net profit. Its PDF and licence content remain unchanged.

Inventory: visible test branding removed; irrelevant contribution-margin instructions replaced; four required nonnegative inputs and CHECK INPUTS warnings added; fractional inputs remain supported and unrounded. Replaced the clipped previews and cover, supplied accurate plain-text instructions and the owner-approved licence, and saved corrected listing copy with compatibility limitations. The gap to threshold is not represented as an optimized order quantity. Original source/archive copies are preserved.

## 4. Final packages and hashes

| Product | Saved archive | Bytes | SHA-256 |
|---|---|---:|---|
| Cleaning | `verification-2026-11-01/final/Cleaning_Pricing_Toolkit_v1.0.1_CUSTOMER.zip` | 61,130 | `334518208388483457c8849cfdf9c73955c80e929d38c1afa6631e9459d990d5` |
| Inventory | `inventory-release-2026-11-03/Inventory_Reorder_Planner_v1.0.1_CUSTOMER.zip` | 205,675 | `55246987e3395e1cd225f7143022285b1f87cab6ca315f415057389994ce06aa` |

Both saved owner-download hashes matched their local package. Member hashes are in `verification-2026-11-01/final/FINAL_RELEASE_MANIFEST.json` and `inventory-release-2026-11-03/RELEASE_MANIFEST.json`.

Original Cleaning ZIP retained: `9835184cb1e37a4ca7f4d379d0a234fee3b769fa22a0af0a3ca356a500c0d215`. Original Inventory ZIP retained: `411bef96fc93f85738cbfa440b25ccd4e3a3bffa22159a47a00b0413d008ac91`.

## 5. Actual Payhip changes

- Cleaning's approved ZIP replacement is saved; CAD29, title and four images were preserved during replacement.
- Inventory's new ZIP, three images, corrected title/description and CAD19 price are saved. Old ZIP/image references were removed after replacement receipts were verified. No uncertain upload was repeated.
- Added Support and Refunds and its footer link; storefront changes were published with Payhip confirmation.
- Created Cleaning-only 100% coupon CGVERIFY1103, limit one, now **1/1 used**.
- Created Inventory-only 100% coupon CGINV1103, limit one. November 4 CA$0 order/download page and both receipt notifications are confirmed by owner screenshots; no second test order was created.
- Initial Cleaning publication approval was not granted; owner reconfirmed publication November 4. Both fresh publication cards were granted locally and both product saves succeeded at the newly reduced prices.

## 6. Storefront state

Store: https://payhip.com/CedargridDigital

Published policy: https://payhip.com/CedargridDigital/support-and-refunds

Header, navy hero, collection, About and footer remain in the prepared store. Policy content matches the approved text, is left-aligned and has a footer link. November 4 catalogue inspection shows both products at CAD15 and CAD9. No fictional testimonials, staff, sales or company history were introduced.

Desktop DOM layout has no horizontal overflow. A real 375 × 667 homepage preview and working collapsed navigation were measured November 1. The current policy preview was measured at desktop width; its background Mobile-mode flag did not produce a new narrow render. Current pixel-level desktop/mobile acceptance remains incomplete. Do not infer a mobile visual pass from a mode flag. Public URLs could not be independently fetched by the web tool; verification used authenticated Chrome and Payhip's publication confirmation.

## 7. Product visibility — latest saved state

| Product | Price | Saved state |
|---|---:|---|
| Cleaning Business Pricing & Profit Calculator | CAD15 | Published / Visible |
| Inventory Reorder Planner | CAD9 | Published / Visible |

November 4 verification: both protected publication saves were locally approved and Payhip confirmed changes saved. Products page shows CAD15 Cleaning and CAD9 Inventory, neither marked HIDDEN, each with one CA$0 order. The storefront catalogue independently displays both at the new prices. The owner requested lower pricing before launch; no discount/sales-demand claims were fabricated.

## 8. Payment and business readiness

PayPal is connected in Payhip. No real charge, payout, purchase, refund, banking change or additional provider agreement was automated. The owner's PayPal identity-verification report is separate from the observed successful Payhip connection.

Owner confirmed Ontario, Canada. Refund/support commitments are approved in `store-policy-approved-2026-11-03.txt`. Receipt-email arrival is owner-confirmed; the separate Contact form has not been submitted/tested. Seller identity, applicable business registration and tax requirements remain the owner's review responsibility; no determination or registration was fabricated or performed.

## 9. Checkout verification

**Cleaning free flow passed through order creation, download-page display and owner-confirmed receipt delivery.** The correct v1.0.1 archive name appeared. The saved owner-download bytes matched the package; the buyer-downloaded archive has not been separately rehashed. This does not prove an actual paid transaction.

**Inventory free flow passed on November 4.** Owner-supplied screenshots show CAD0.00 total, the 201 KB ZIP on the download page, buyer receipt and seller notification delivered. Independent Products-page inspection confirms one order and CAD0.00 sales. Buyer-downloaded archive bytes have not been separately rehashed.

Payhip's documented testing method: https://help.payhip.com/article/107-testing-checkout-flow . Checkout screens require manual control under the current bridge security boundary. Neither test authorizes a real payment using the seller's own payment account.

## 10. Remaining owner actions

1. Publication intent resolved November 4: owner explicitly requested continuing with both products.
2. Both free checkout tests are complete; buyer receipts were delivered.
3. Both protected publication cards were granted and saved November 4. Routine mode continues to preserve sensitive-action review.
4. Support Contact delivery and owner business/tax details still need review. No password or verification code is needed in chat.

The routine checkbox is already enabled; no further enable/resume step is currently needed.

## 11. Remaining technical/verification work

- Publication is complete; both catalogue prices and product-page visibility were independently checked. No package uploads were repeated.
- Inventory buyer receipt/download-page test passed November 4; buyer-archive byte verification and current visual screenshots remain limited as described above.
- Both one-use test coupons were reserved for their completed tests, not public promotion. No further test order is needed.
- The improved publication explanation is deployed: visible/unlisted product saves are identified as public listing changes. Routine mode remains enabled, and explicit file rules, Stop, manual control and sensitive-screen/frame checks remain enforced.
- No commit/push, authentication reset, conversation deletion or new automation framework was performed.

## 12. Ready for public sale?

**Both products are publicly listed as of November 4.** Packages, PayPal connection, approved policy and storefront are prepared, and both zero-charge delivery/receipt tests passed. This does not certify a real charged payment/payout, native Excel compatibility, Contact-form delivery or current mobile pixel acceptance. Buyer archive bytes were not separately rehashed; saved owner-download package hashes matched.

## First-sales experiment — proposal only

Target independent residential cleaners and small cleaning teams already comfortable with spreadsheets. The specific problem is repeatable cost-based quoting, comparison of up to 25 proposed jobs and review of recorded actual costs. The reason to pay is a ready-to-use offline workflow, fictional example and customer quote sheet; generic formulas, ChatGPT and free sheets are credible alternatives. Do not imply unique AI capabilities or guaranteed profit.

Current primary seller asking-price examples reviewed November 1 (not evidence of sales):

| Alternative | Observed asking price | Comparison limit |
|---|---|---|
| [Vars Digital cleaning pricing/job costing](https://varsdigital.app/p/cleaning-business-pricing-and-job-costing/) | C$19 | Claims Excel/Sheets support; not independently tested |
| [BooksheetPro](https://www.booksheetpro.com/) | $19.99 calculator; $39.99 bundle | Currency not established from the reviewed page |
| [JobCostLabs](https://jobcostlabs.com/house-cleaning-price-calculator/) | Free web tool; $11.39 spreadsheet | Currency not established; genuine free competition |
| [Kernovia cleaning calculator](https://getkernovia.com/products/calculators/cleaning/) | $29 | Currency not established; desktop Excel focus |

Keep CAD29 as the existing price hypothesis; no price change is authorized. Once sale readiness and publication are approved, run a 14-day small pilot. Prepare one honest demonstration using fictional inputs and one clear limitations/compatibility explanation. Seek permission to share in relevant cleaning-operator communities; use the owner's existing legitimate network or permitted educational posts. No scraping, unsolicited bulk messages, fabricated reviews or paid ads. Distribution/public posts still require approval.

Track channel-tagged qualified product visits, checkout starts when available, paid orders, conversion (orders / qualified visits), actual gross CAD receipts, platform/processor deductions, refunds, chargebacks and time spent on support. Net proceeds = receipts minus actual deductions/refunds/chargebacks; operating profit also subtracts labor and other business costs. No assumed fee schedule or earnings forecast is used.

Decision gates are experimental thresholds, not sales forecasts: fewer than 30 qualified visits means distribution evidence is insufficient; improve the approved channel before interpreting conversion. At 100 qualified visits with no purchases, review price/value/compatibility with willing target users before more promotion. Three or more genuine paid users who can complete their first quote with manageable support is a reason for a limited continuation, not proof of a scalable business. Any calculation defect, failed delivery or misleading claim pauses promotion immediately. After one focused revision and another measured pilot without paid demand or useful adoption, stop expanding this product and evaluate alternatives separately.

