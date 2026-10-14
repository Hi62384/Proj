# Minimal-work business automation — step-by-step setup

## Stage 1 — Give an ongoing AI coordinator the project

1. In ChatGPT, open your existing **dot**, or go to <https://chatgpt.com/dots> if eligible. In its conversation, provide the exact GitHub repository link `https://github.com/Hi62384/Proj`. Share `MASTER_EXECUTION_PLAN.md` and `portfolio_autopilot/README.md` if it cannot read them itself.
2. In your dot profile, connect GitHub when available. Use an appropriate scoped account connection; when asked for browser sign-in complete it personally. Permissions depend on account and app. Do not grant unrelated repository access.
3. If you want the dot to operate your Windows computer, use the ChatGPT desktop app: open the dot's profile → Computers → Your computer → **Allow access**; confirm. Keep the app running when local work is needed. Local access is optional; the cloud computer works without it.
4. In Codex cloud, create/publish a coding environment connected to this repository, then permit the dot to create Codex tasks there where supported. Review pull requests before merging to live branches. The local Windows command bridge is optional, and was unavailable during the October 2026 inspection.
5. Give the dot the `COORDINATOR_PROMPT.md` below; ask it to create recurring research and approval digests, not marketing spam or autonomous purchases.

## Stage 2 — Set up accounts once (your personal work)

6. Decide your legal seller identity and any necessary provincial registration. Use official Canada/CRA information for tax and sales-tax status. Seek professional advice when needed. Do not put identifiers in this repository.
7. Connect a business email inbox in ChatGPT Plugins or dot settings, with minimum needed permissions. Use it for support and permitted messages; never allow uncontrolled mass outreach.
8. Create a Stripe account using <https://dashboard.stripe.com/register> if appropriate for your products. Complete identity, banking, and tax onboarding **directly with Stripe**. If you sell digital goods internationally, compare merchant-of-record alternatives and tax responsibilities before choosing.
9. Connect the Stripe plugin to ChatGPT if available. Begin in test mode, create one draft product and a test payment link, verify payouts/fee estimates, and review the actual checkout. Do not paste card or bank information into the AI conversation.
10. Choose a domain/hosting platform **only when** a paid offer needs one. For the first fixed-scope sale, a marketplace-funded milestone or verified hosted checkout may be faster than building a complete website.
11. Create provider accounts for any chosen marketplace (e.g. digital downloads) only after verifying seller eligibility, fees, and commercial rights. You complete CAPTCHA, legal acceptance and tax forms.

## Stage 3 — First launch, review-based

12. Use `python -m portfolio_autopilot.cli scan --limit 12 --html portfolio_autopilot/.local/shortlist.html` to create a cross-industry queue. Ask the dot to verify current buyer requests and compare free/paid incumbents. Select no more than three distinct, small paid tests from unrelated niches.
13. Run `python -m portfolio_autopilot.cli prepare <OPPORTUNITY-ID>` for each selected offer. Ask Codex to produce a runnable MVP and tested synthetic fixtures. Require a human-readable scope and refund/repair terms.
14. Review actual customer intent and approve one offer. Ask Work/dot to draft marketplace responses to *explicit* job requests or prepare permitted partners' proposals. **Approve outgoing messages** and respond to actual buyers. Never count automatic email volume as traction.
15. Use a provider-hosted invoice/payment link or marketplace milestone. Verify payment yourself or via a connected, appropriately permissioned Stripe account before granting access. Fulfill with tested scripts or approved download delivery.
16. After accepted delivery, record actual paid invoices, fees, refunds, operating costs, and owner minutes. Never mix sales waiting for payout with settled money. Automate repetitive fulfillment only after the task repeats.

## Stage 4 — Turn a validated business into a mostly automated product

17. After independent paid proof and repeat-use signals, ask Codex to extract reusable adapters behind a fixed input/output contract and tests. Use managed payment/fulfillment where reasonable; avoid implementing your own card storage.
18. Deploy through a restricted production environment with separate secrets, webhooks, customer isolation, backups, spending caps and a kill switch. First launches and major account changes still require your approval.
19. Add n8n/Make or a managed scheduler only when the workflow needs it. Set failure notifications, retry limits, quotas, refund routing, and a weekly reconciliation report. GitHub Actions is best for code CI and noncritical research summaries, not guaranteed-time payment or job delivery.
20. Maintain a weekly decision review: acquisition funnel, *actual* profit, owner hours, support load and failed runs. Ask the dot to recommend doubling down, changing the offer, or stopping. Expand across new niches on evidence, not a requirement to launch hundreds simultaneously.

## Monthly cost control

Default automation budget: **CAD $0 external API/ads until you approve a cap**. At each rollout approve: one-time cost, recurring maximum, worst-case API usage, refund reserve, legal/data sensitivity and off switch. ChatGPT subscription and API usage are separately billed.

## Account actions AI cannot replace

Provider KYC/identity checks, bank linking, local business/tax registration decisions, service agreement acceptance, some verification/captchas, copyrighted content-rights attestations, first public launch approval, customer dispute resolution, and regulated/financial/legal professional judgments.

See official references for current features and rules: OpenAI dot help <https://help.openai.com/en/articles/20001530-getting-started-with-your-dot>; ChatGPT Work <https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt>; Stripe Canada fees <https://stripe.com/en-ca/pricing>; GitHub Actions schedule <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows>; CRA sole proprietorship <https://www.canada.ca/en/revenue-agency/services/tax/businesses/small-businesses-self-employed-income/setting-your-business/sole-proprietorship.html>; CASL <https://crtc.gc.ca/eng/com500/faq500.htm>.
