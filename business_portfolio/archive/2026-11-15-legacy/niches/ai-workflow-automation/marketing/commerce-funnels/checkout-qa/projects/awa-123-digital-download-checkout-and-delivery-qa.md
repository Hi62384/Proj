---
{
  "id": "AWA-123",
  "title": "Digital-download checkout and delivery QA",
  "niche_path": "ai-workflow-automation/marketing/commerce-funnels/checkout-qa",
  "record_type": "standalone_service",
  "origin": "revised_candidate",
  "priority": "P2",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "adjacent_buyer_request_not_exact_offer",
  "source_ids": [
    "V2-34",
    "V2-01",
    "V2-04",
    "V2-05",
    "V2-08",
    "V2-15",
    "V2-16",
    "V2-17",
    "V2-21"
  ],
  "parent_project": null,
  "related_projects": [
    "EX-003",
    "AWA-010"
  ],
  "legacy_ids": [],
  "next_action": "At $0 incremental cash, check one eligible request for 'Payhip digital product delivery checkout testing', compare the native alternative and draft the proof/scope. Do not build a bespoke customer workflow or send a proposal without approval.",
  "delivery_hours_assumption": [
    1,
    3
  ],
  "total_first_order_hours_assumption": null,
  "verified_paid_pilots": 0,
  "actual_revenue": null,
  "actual_profit": null,
  "owner": "unassigned",
  "execution_authorized": false,
  "privacy": "public_planning_only",
  "schema_version": 1,
  "last_reviewed": "2026-11-05",
  "niche_id": "N-1c30e80744b2",
  "commercial_revision": 2,
  "owner_budget": {
    "currency": "CAD",
    "preferred_upfront": 0,
    "planned_upfront": 0,
    "authorized_spend": 0,
    "hard_ceiling": 100,
    "owner_recurring_monthly": 0,
    "budget_window": "Cumulative incremental owner launch cash/commitments; review at first sale or 30 days, whichever comes first. No automatic cap reset after a sale or new month.",
    "includes": [
      "tax",
      "currency_conversion_cost",
      "noncancelable_commitments",
      "proposal_credits",
      "demo_API_cost",
      "advertising",
      "hosting"
    ],
    "unknown_cost_action": "Pause; do not treat missing costs as zero.",
    "production_runtime": "Customer-owned and customer-paid only after explicit acceptance; limits and exact plan requirements remain a preflight gate.",
    "budget_fit": "conditional_on_existing_customer_stack",
    "optional_all_in_envelope": {
      "proposal_or_channel_test": 25,
      "demo_runtime": 10,
      "advertising": 0,
      "contingency": 15
    },
    "optional_total_ceiling": 50
  },
  "marketing_execution_authorized": false,
  "success_probability": "not_established",
  "production_budget_verified": false,
  "marketing_lane": "commerce_agency_requests",
  "launch_gate": "buyer_test_only",
  "offer_price_cad_hypothesis": [
    180,
    350
  ],
  "paid_delivery_cap_hours": 3,
  "pre_sale_work_cap_hours": 4,
  "acquisition_batch_max_qualified_requests": 8,
  "ad_test_cap_cad": 0,
  "economics_scenarios": [
    {
      "name": "low_price_favorable_direct_hypothesis",
      "price_cad": 180,
      "combined_fee_fraction": 0.05,
      "refund_reserve_fraction": 0,
      "allocated_cash_cost_cad": 0,
      "total_owner_hours": 5.5,
      "contribution_before_owner_labor_cad": 171.0,
      "effective_cad_per_owner_hour": 31.09
    },
    {
      "name": "low_price_marketplace_stress_hypothesis",
      "price_cad": 180,
      "combined_fee_fraction": 0.2,
      "refund_reserve_fraction": 0.05,
      "allocated_cash_cost_cad": 25,
      "total_owner_hours": 8.5,
      "contribution_before_owner_labor_cad": 110.0,
      "effective_cad_per_owner_hour": 12.94
    }
  ],
  "stress_quote_floor_cad_assumption": 373.33,
  "historical_price_usd_hypothesis": null,
  "offer_price_usd": null
}
---
# AWA-123 — Digital-download checkout and delivery QA

## Decision and evidence
**Classification:** standalone_service. **Priority:** P2. **Commercial state:** unvalidated.
The author-store request is broader than QA and includes fulfillment. Exact willingness to pay for this bounded check still needs validation; prior internal Payhip work is not a client testimonial. This is a scoped offer within the existing service business, not proof of an independent market. No customer was contacted, charged or served by preparing this plan.

## Buyer, trigger and reason to pay
**Buyer:** An existing digital-product seller or agency with a finished download and a configured storefront.

**Problem/outcome:** The owner needs evidence that the approved listing, checkout path and permitted test delivery are consistent.

**Buying trigger:** A current owner requests a solution to this specific existing problem and can define an accepted result.

**Native/free/AI alternatives:** The provider’s launch checklist and the seller’s own free test flow; sell only where independent documented checking is valuable.

## Bounded deliverable
**Pilot cap:** One existing listing, one release file, agreed desktop/mobile viewports and one provider-permitted test mode or zero-price flow. Verify file hash and disclosed compatibility. No charged purchase, payment-setting change, new store or sales guarantee.

Include a versioned scope, test result, known limitations and handover. Production changes require separately approved scoped access, customer-owned running costs and acceptance criteria. No new owner-funded infrastructure.

## Acceptance and implementation sequence
1. Confirm a permitted example of the failure and the buyer's authority. Reject missing consent or data rights.
2. Prefer native configuration, deterministic rules and existing approved tools.
3. A fictional listing checklist and a hash-checked disposable download demonstrate the test method without copying a paid product.
4. **Distinct failure test:** A stale release, broken link or receipt-to-file mismatch remains a failed check; a free checkout is never described as paid-payment verification.
5. Record expected and observed results; false confidence is a failed acceptance test.
6. Obtain customer acceptance of a funded scoped job and revoke temporary access. Synthetic tests are not production acceptance.

## Economics and remaining human work
**New customer-price hypothesis:** CAD180–350 for the stated cap; this is not the owner's startup cost, an observed sale or a conversion of earlier USD ideas. The `historical_price_usd_hypothesis` field, where present, preserves the prior unvalidated USD idea; it is not the current quote. Customer willingness to pay this CAD quote is unverified.

**Efficiency change:** Reuse the existing store and approved assets; no redesign, pixel installation or funnel subscription.

**Time boundaries:** stop unpaid preparation/qualification for this experiment at four owner-hours total, including the proof; do not build eight custom demos for eight requests. Aim for at most a 60–90 minute reusable fictional proof. The proposed paid delivery allowance is at most 3 hours, including testing and handover, followed by 30–60 minutes of defined defect triage. These are workload limits to validate, not promises that unfamiliar integration work fits them. Quote separately or decline before accepting work that does not fit. Do not omit necessary testing to stay inside the cap.

| Scenario, not forecast | Receipt | Fees / refund reserve assumptions | Allocated cash | All owner hours | Contribution before owner labor/tax | Effective hourly contribution |
|---|---:|---|---:|---:|---:|---:|
| Favorable direct at lower quote | CAD180 | 5% combined processing, 0% refund reserve | CAD0 | 5.5 | CAD171.00 | CAD31.09 |
| Marketplace stress at lower quote | CAD180 | 20% fee, 5% refund reserve | CAD25 | 8.5 | CAD110.00 | CAD12.94 |

The favorable scenario allocates one proof hour, one acquisition hour and half an hour of support on top of the delivery cap. The stress case allocates 1.5 proof hours, three acquisition hours and one support hour. Include previous failed pitches and shared business-development time in actual results; they can exceed both examples. The fee percentages are sensitivity assumptions, not assertions of any provider's exact rate. A 20% marketplace case is deliberately conservative; verify the actual provider and contract.

At an illustrative CAD30/hour owner-time target, the stress scenario needs about **CAD373.33** in customer price to break even economically. This is a rejection test, not permission to claim a buyer will pay that price. If that floor exceeds the credible quote, narrow the deliverable without weakening acceptance, use a less costly acquisition channel, or decline. Zero customers produces zero receipts and loses the time/cash spent.

**Unavoidable human work:** qualification, proof of skill, access decisions, scope agreement, ambiguous exceptions, independent acceptance, handover, support and payment reconciliation. Do not call the offer passive. Full methodology: [economics](../../../../../../research/ECONOMICS_V2.md).

## Customer acquisition and validation gate
### Buyer and buying trigger
An existing store owner or authorized agency already paying for the necessary commerce stack. A request must actually match **check that one digital product delivers what its listing promises**; broad interest in AI is not enough.

### Positioning and proof
**Landing/profile headline draft:** Check that one digital product delivers what its listing promises.

**Show, rather than claim:** A specific issue report and expected-versus-observed delivery record, not a generic conversion audit. Label all examples fictional. Show actual observed test results only after running them. Keep one relevant annotated screenshot or a 45–90 second demo and a one-page scope; no new website, logo, CRM or subscription is required.

**One-call-to-action draft:** “Send a redacted example of the current problem and the result you need. I will confirm whether it fits this fixed scope before proposing paid work.” This is draft copy, not a message sent.

**Response draft for an invited, eligible buyer request:** “Your request mentions [their exact failure]. My proposed deliverable is: check that one digital product delivers what its listing promises. The check I would use is: a specific issue report and expected-versus-observed delivery record, not a generic conversion audit. I would first verify whether your existing tools can do this natively. The bounded scope excludes [the project exclusions below]. Are you able to share a redacted example and name the person who will accept the result? I would confirm scope, access and a fixed quote before starting.” Remove any implication of prior client results; do not claim unearned certification.

### $0-first acquisition experiment
Start with explicit merchant/commerce-agency requests in permitted hiring areas. A platform community is not permission to pitch in support threads.

**Specific discovery phrase:** `Payhip digital product delivery checkout testing`. Check current date, location restrictions, budget, exact deliverable, reputation/credential requirements and whether hiring is still open. Search results and community categories are lead-discovery starting points, not a vetted live prospect list.

Prepare at most eight high-fit request records in two batches of four. Obtain owner approval before responses or public posts. Use one reusable proof and personalize the problem, not a generic AI pitch. Stop at four unpaid owner-hours, eight eligible attempts or fourteen elapsed calendar days—whichever comes first—and review what happened. A time-box is not a promised time to first revenue. Pause earlier when no eligible request exists; do not purchase exposure merely to fill a quota.

**Secondary channel:** one relevant, permitted public demonstration or a genuine opt-in referral. No unsolicited mass DMs, scraped email lists or automated applications. Upwork is optional only after eligibility and actual Connects costs are checked; its proposal expense is not assumed zero. Do not move marketplace-sourced pre-contract communication or payment off-platform contrary to its rules.

### Funnel, decision and sale
Record source, eligible request, authorized response, meaningful reply, scoped conversation, funded agreement, accepted delivery, collected receipt, refund and total owner time. Count unpaid likes, followers, waitlist entries and quotes separately from customers. With no meaningful replies after the first four qualified attempts, revise one of buyer/offer/proof before using the second batch; do not simply increase posting volume. With replies but no scoped agreement, record the objection. With no paid commitment at the cap, pause this offer instead of building more features. These are spending/workload gates, not statistical proof of market failure.

Do not begin client-specific production work until there is an agreed scope, lawful permissions, a funded milestone or approved payment arrangement and acceptance criteria. A small paid diagnosis can precede a repair; do not relabel free discovery as a paid deliverable. Ask for a case study or referral only after a real successful delivery and permission.

**Project-specific rejection:** Decline sellers seeking guaranteed sales, payment certification or an unauthorized real-money self-test.

### Advertising decision
**Current ad allocation: CAD0.** This narrow service needs proof and qualified conversations before broad paid traffic. Advertised job budgets do not establish conversion economics. Only reassess ads after actual profitable sales; any later test must have a measured conversion path, a conservative acquisition-cost ceiling and a separate approved total budget. No retargeting pixels, uploaded customer lists or campaign launch is authorized by this plan.

**Launch gate:** `buyer_test_only`. For skill-gated work, produce a convincing disposable-environment acceptance test before offering the service. For follow-ons, do not advertise before the earlier project actually has paying clients. [Marketing method](../../../../../../research/MARKETING_PLAYBOOK.md) · [Validation gates](../../../../../../research/VALIDATION_GATES.md).

## Progress checkpoint — resume here
- [x] Prepared this project-specific research and scope record in the v2 package.
- [ ] Demonstrate the relevant skill using fictional data.
- [ ] Find an eligible, current buyer request for the exact scope.
- [ ] Obtain owner approval before any proposal, spend, account access or publication.
- [ ] Agree a funded milestone and acceptance specification before client-specific delivery.
- [ ] Record actual acquisition, delivery, support, fees and collected receipts in a private ledger.

No paid order, finished implementation, live test or recurring revenue is recorded. Next action is the current frontmatter next_action; append observed actions without resetting this checkpoint.

## Evidence references
- [V2-34](https://www.upwork.com/freelance-jobs/apply/Author-Website-Book-Sales-Email-Marketing-Setup_~022116953351921727940/) — Author website, Payhip and email setup request. indexed_primary; Includes broader website/fulfillment scope. It supports adjacent technical-funnel demand, not an exact checkout-QA purchase or guaranteed sales.
- [V2-01](https://payhip.com/pricing) — Payhip Free Forever pricing. full_page; A zero monthly subscription is not zero selling cost; provider terms are not evidence of customer demand.
- [V2-04](https://help.payhip.com/article/108-conversion-rate) — Payhip conversion-rate analytics. indexed_primary; Analytics requires actual traffic; instrumenting a funnel does not improve demand by itself.
- [V2-05](https://help.payhip.com/article/110-visitor-sources) — Payhip visitor-source analytics. indexed_primary; Attribution is incomplete when privacy settings, cross-device activity or referrer loss intervene.

## V2 budget and execution boundary
**Preferred incremental owner cash: CAD0. Current authorized spend: CAD0. Absolute project ceiling: CAD100, not a target.** The ceiling includes tax, FX cost, committed renewals, proposal credits, demonstrations and advertising through the first-sale/first-30-day experiment. Optional envelope for this record: **CAD50**, available only after separate itemized approval. No automatic replenishment, account creation or paid trial. Unknown required costs block execution instead of being entered as zero.

**Budget fit:** `conditional_on_existing_customer_stack`. Existing equipment/software are reused; electricity, past development and sunk subscriptions are not asserted to be free. Owner recurring subscription allocation is CAD0. Customer production accounts/plans/usage are a separate disclosed preflight cost, never silently subsidized from the owner's budget or described as universally free. If safe completion requires an unaffordable owner commitment, simplify or keep the work deferred.

No customer acquisition, publication, payment or account access has occurred in this revision. A marketing plan cannot ensure sales; exact-offer success probability and paid validation remain unestablished. Project execution must also respect the portfolio-wide **CAD0 current authorization**, so starting many projects cannot multiply spending rights. [Budget rules](../../../../../../research/BUDGET_POLICY.md) · [Current research](../../../../../../research/SOURCES_V2.md).

## V2 revision note
2026-11-05: added the applicable marketing, effort and cash gates; preserved recorded completed work and commercial validation. Frontmatter next_action is the current proposed planning step. Older checkpoint instructions remain historical where superseded by this revision; do not repeat completed external actions.
