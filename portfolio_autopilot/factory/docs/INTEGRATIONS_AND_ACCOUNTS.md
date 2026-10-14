# Shared tools and accounts — connect only when a business needs them

The factory intentionally runs offline with **zero paid APIs and no pre-installed service dependencies**. The user requested fewer repetitive account setups; the highest-leverage approach is one approved seller identity, one suitable checkout account, and one business inbox shared by permitted products. Different regulated/marketplace models may require separate accounts.

| Capability | Built and usable now | Outside service when validated | What the owner must do |
|---|---|---|---|
| Idea filtering | Atlas CLI + draft dashboard; 1,296 hypotheses | Periodic verified evidence research | Approve research sources, budgets and data access |
| First reporting offer | Existing tested Python core; synthetic ZIP; templates | Upwork Project Catalog or direct selling | Verify freelancer identity, profile and authorized proposals |
| Digital downloads | Product kit and offline store mockups | Eligible hosted merchant/checkout + storefront | Choose provider, complete KYC/bank/tax and approve go-live |
| Payments | Manual event ledger only; no remote charges | Stripe or an eligible merchant-of-record provider | Connect account securely, verify webhooks/payouts/tax/fees |
| Customer communications | Draft proposals, no sending | Dedicated email/inbox with scoped connector | Provide mailbox, review consent and initial external messages |
| Job automation | Tested Python stdlib runner; repeatable ZIP | Approved scheduler/queue, n8n/Make if needed | Choose a hosted provider, approve usage and response time |
| Hosting/deployment | Local HTML preview only | Private/static host or managed service | Approve public release, domain and costs |
| Analytics | Pseudonymous manual SQLite ledger | Provider exports and reconciled transaction ingestion | Check that sales/fees/payouts actually reconcile |
| AI agent activity | No token-consuming API code | Work, dot, or Codex for approved one-off steps | Connect and authorize appropriate tools/usage |

**No account passwords, OAuth tokens, webhook secrets, bank details, identity documents or private client files belong in GitHub, ProjectBridge ZIPs, example templates or chat messages.** Use provider-hosted OAuth, managed secrets, least privilege and short-lived delegated authorization.

## When ready to enable an external service

1. Confirm a real buyer problem and the provider's current pricing/eligibility/licence terms.
2. Choose a single provider for the capability, not a new provider for every niche.
3. User signs up and completes ID/tax/payout onboarding directly with the provider.
4. Create a separate sandbox/testing environment and configure secrets ONLY through the provider's secret store; zero spend cap before approval.
5. Add a separately-reviewed adapter: signatures, replay safety, idempotency, data isolation, quotas, cancellations/refunds, failure alerts, retention, and audit trail.
6. Test success, rejection, duplicates, timeout, cancellation, reversal and rollback before approving the first live use.
7. Set limits (monthly CAD spend, per-job quotas, permissioned channels, maximum owner support time) and explicitly approve the first public launch.

Connecting a plugin or cloud browser does not by itself configure this software, grant permissions for purchases, or bypass site restrictions.

## Minimum account path for the reporting business

- The **report and packaging** already operate entirely offline, requiring no seller account to demonstrate.
- For the first buyer, one suitable freelancer platform (such as Upwork) may be sufficient; use platform-approved funded milestones and proposals. Buyer acquisition and KYC are still manual.
- Do **not** open Stripe, Mailchimp, n8n, Cloudflare, Shopify, Gmail and many marketplaces simultaneously. Add only what paid demand actually requires.

## Privacy and marketing

Commercial messages in Canada may fall under CASL. Do not automate unsolicited bulk outreach or ignore marketplace bot policies. Use existing explicit purchase requests and consented introductions. Avoid medical/legal/safety decisions and storing identifying customer data without suitable safeguards. For public deployments, consult current CRA, privacy, hosting and payment-provider rules rather than trusting a static template.
