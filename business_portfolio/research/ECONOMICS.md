> Historical v1 research. Revision 2 commercial/budget/marketing decisions take precedence; see [current findings](RESEARCH_V2.md), [economics](ECONOMICS_V2.md) and [marketing](MARKETING_PLAYBOOK.md). Old price/ranking assumptions are not new verification.

# Economics: actual cash, all owner time, and no invented forecasts

All examples below are **USD planning scenarios**, not actual financial results. Existing Payhip prices are CAD and must not be mixed with these examples. Taxes, exchange rates, indirect overhead and future sales are not forecast. Upwork fees vary by contract; the model uses 15% as one conservative scenario within the published range, not a universal rate. Connects cost money when purchased; none are authorized here. [T01, T02]

## Minimal model

```
contribution_before_owner_labor = receipts - refunds - platform_payment_fees
                                  - allocated_tools_hosting_AI - acquisition_cash_costs
all_owner_hours = research + lost_and_won_proposals + scoping + access_setup
                  + implementation + QA + communication + handover + support + admin
contribution_per_owner_hour = contribution_before_owner_labor / all_owner_hours
illustrative_economic_surplus = contribution_before_owner_labor
                               - all_owner_hours * chosen_hour_value
quote_floor = (target_hour_value * estimated_all_hours + allocated_cash_costs)
              / (1 - applicable_fee_fraction)
```

The simplified quote floor assumes the only revenue-proportional deduction is the fee and no refunds. Add a refund/rework reserve explicitly when justified; do not hide it. Client-paid hosting is excluded from seller expense only when the arrangement genuinely makes the client responsible. A payout/settlement is a transfer of existing revenue, not another sale.

| Gross fee | Platform fee scenario | Other allocated cash costs | Contribution before labor | Total owner hours | Contribution / owner hour |
|---:|---:|---:|---:|---:|---:|
| $150 | 15% | $15 | $112.50 | 8 | $14.06 |
| $250 | 15% | $15 | $197.50 | 4 | $49.38 |
| $250 | 15% | $15 | $197.50 | 8 | $24.69 |
| $250 | 15% | $15 | $197.50 | 20 | $9.88 |
| $350 | 15% | $15 | $282.50 | 8 | $35.31 |

Four total hours is an optimistic repeat/straightforward-job scenario, not an assumption that a new seller can find, scope and finish a client in four hours. Twenty hours illustrates acquisition/learning overruns. None of these numbers is a profit guarantee.

With an **illustrative**, user-changeable target of $30/hour, $15 allocated cash costs and a 15% fee, an eight-hour scope needs a $300 gross quote; twelve hours needs $441.18. If buyers will pay only $195 for a scope that reliably consumes twelve hours, that mismatch calls for a smaller scope, a different buyer or a stop—not a fabricated automation-efficiency assumption.

## Price the result, cap the risk

For AWA-001, test a $200–350 bounded offer only after identifying the systems and showing the synthetic fixture path. For an unknown failure, offer a capped diagnosis, not unlimited repair. A “simple” connector can still be unavailable on the customer’s plan or unable to preserve required semantics. Expensive plan upgrades can eliminate the business case. [P01–P05]

An initial agent listing’s $35/$50 maintenance proposal is not proof of profitable recurring service. At 15% fees, a $50 monthly charge leaves $42.50 before other expenses: one support hour, an incident and administration can consume it. Offer a follow-on review/support allowance only after measuring incidents and defining service hours, scope and overages. [J03, T01]

## Skill and time gates

Before accepting client work, the operator must be able to trace one failed event, explain identity/idempotency, distinguish transient errors from permanent input problems, verify the resulting record and recover without exposing a secret. A model-generated workflow is not evidence those abilities exist. Use a fictional demo to measure the learning burden. A suggested initial preparation cap is 3–5 owner hours before reassessing the scope; this is a management limit, not an estimate of how quickly anyone will become qualified.

Before sending an authorized proposal, log time already spent finding and assessing requests, including unsuccessful ones. At the end of a deliberately bounded acquisition trial—such as ten well-matched approved proposals or ten hours of real sales effort—review response quality and economics. That trial size is an owner decision aid, not statistical proof of no demand. No proposal is submitted by this package.

## Record actuals privately

Use an access-controlled private ledger for event ID, project ID, customer pseudonym, invoice/milestone status, currency, gross amount, refund, fee, cash expense, time category, minutes, acceptance evidence and settlement reference. Store no passwords, client documents or account identifiers in public Markdown. Public project status can say “paid pilot verified privately on DATE” with a non-sensitive evidence reference when true.

Keep `unknown`, `zero observed` and `not applicable` distinct. The current package has zero verified paid pilots for new candidates, but it does not inspect account-wide sales. Existing product revenue and balances remain unknown. Use the existing factory ledger only within its stated limitations; its human-entered totals are not bank reconciliation. [R06]

## Time to usable cash

A first sale, accepted delivery, released milestone and available payout are separate events. The fixed-price platform process may include a fourteen-day review and five-day security hold, with other delays possible. Never interpret “deliver a workflow this week” as “cash will arrive this week.” [T05, T06]

Evidence IDs refer to [SOURCES.md](SOURCES.md) and the machine-readable [SOURCE_REGISTER.json](SOURCE_REGISTER.json). Planning choices and calculations are not observed customer results.
