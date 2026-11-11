---
{
  "id": "AWA-004",
  "title": "Approved calendar booking to CRM",
  "niche_path": "ai-workflow-automation/agency/white-label/builds",
  "record_type": "standalone_service",
  "origin": "revised_candidate",
  "priority": "P2",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "adjacent_buyer_request",
  "source_ids": [
    "J01",
    "J02",
    "J03",
    "J07",
    "J13",
    "P06",
    "P07",
    "P08",
    "P09",
    "T01",
    "T02",
    "T03",
    "T05",
    "T06",
    "T08",
    "V2-08",
    "V2-10",
    "V2-16",
    "V2-17",
    "V2-21"
  ],
  "parent_project": null,
  "related_projects": [],
  "legacy_ids": [
    "AWA-004"
  ],
  "next_action": "At $0 incremental cash, check one eligible request for 'calendar booking cancellation CRM integration', compare the native alternative and draft the proof/scope. Do not build a bespoke customer workflow or send a proposal without approval.",
  "delivery_hours_assumption": [
    3,
    8
  ],
  "total_first_order_hours_assumption": [
    5.5,
    20
  ],
  "verified_paid_pilots": 0,
  "actual_revenue": null,
  "actual_profit": null,
  "owner": "unassigned",
  "execution_authorized": false,
  "privacy": "public_planning_only",
  "schema_version": 1,
  "last_reviewed": "2026-11-05",
  "niche_id": "N-57d959e8d44b",
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
  "marketing_lane": "agency_implementation_requests",
  "launch_gate": "buyer_test_only",
  "offer_price_cad_hypothesis": [
    250,
    450
  ],
  "paid_delivery_cap_hours": 5,
  "pre_sale_work_cap_hours": 4,
  "acquisition_batch_max_qualified_requests": 8,
  "ad_test_cap_cad": 0,
  "economics_scenarios": [
    {
      "name": "low_price_favorable_direct_hypothesis",
      "price_cad": 250,
      "combined_fee_fraction": 0.05,
      "refund_reserve_fraction": 0,
      "allocated_cash_cost_cad": 0,
      "total_owner_hours": 7.5,
      "contribution_before_owner_labor_cad": 237.5,
      "effective_cad_per_owner_hour": 31.67
    },
    {
      "name": "low_price_marketplace_stress_hypothesis",
      "price_cad": 250,
      "combined_fee_fraction": 0.2,
      "refund_reserve_fraction": 0.05,
      "allocated_cash_cost_cad": 25,
      "total_owner_hours": 10.5,
      "contribution_before_owner_labor_cad": 162.5,
      "effective_cad_per_owner_hour": 15.48
    }
  ],
  "stress_quote_floor_cad_assumption": 453.33,
  "historical_price_usd_hypothesis": [
    200,
    450
  ],
  "offer_price_usd": null
}
---
# AWA-004 — Approved calendar booking to CRM

## Decision and evidence
**Classification:** standalone_service. **Priority:** P2. **Commercial state:** unvalidated. A separately commissioned deliverable is plausible, but it is one offer within a service business, not proof of an independent market.

The sources establish adjacent work or platform capabilities, not a verified exact-scope buyer for this entry. Validate the particular problem before offering or building it. Priority is editorial sequencing for fast, low-upfront-cost experimentation, not probability of success. No workflow implementation, client interview, proposal, contract, paid order or production test was performed for this candidate in this package.

## Buyer, trigger and reason to pay
**Buyer:** Appointment-setting agency supporting a client with an existing scheduler.

**Problem/outcome:** Calendar-confirmed bookings update CRM pipeline with correct contact matching.

**Buying trigger:** An agency with a signed client needs a small integration shipped correctly and documented under its delivery process.

A defensible fee is for resolving the buyer’s specific mapping/operating problem, measured acceptance, failure handling and usable handover—not for owning a template or merely using AI. Ask for one real failure example and the operational consequence. If native configuration or vendor support solves it adequately, use that cheaper route or decline the custom build.

**Native/free/AI alternatives:** Start with the CRM’s native connector, then a maintained platform template; keep the customer’s existing platform unless a concrete limitation justifies another.

## Bounded deliverable
Process booking and cancellation events; match contact via agreed keys; update booked/cancelled state; notify account owner.

**Pilot cap:** One calendar, one CRM pipeline, booking/cancellation only.

Include a versioned field/rule map, sanitized export where permitted, test results, known limitations, rollback/recovery instructions and customer-owned handover. Changes outside the cap need a new estimate. No external publication, unsolicited messaging, payments/refunds, destructive data changes or account-wide permissions are implied.

## Acceptance and implementation sequence
1. Confirm the current behavior, ownership, destination semantics and one named acceptance decision-maker. Use synthetic/redacted fixtures before requesting production access.
2. Specify the smallest deterministic implementation. Introduce AI only when text variability justifies it; keep a review/abstention path and budget approval.
3. Test cancellation, repeated events and unmatched person to review queue.
4. **Distinct failure test:** A cancellation arriving before the booking creates an exception rather than a phantom confirmed appointment.
5. Verify outputs independently of a tool’s “success” response. Test permission loss, retries and partial failures relevant to this scope. Record observed results, residual limitations and restore instructions.
6. Obtain customer acceptance and hand over/revoke temporary access. Do not mark a mock test as a production pass.

**Required access/environment:** An owner-approved staging form, scoped CRM connection and one internal notification destination. Production belongs in an appropriately authorized customer-owned account and reliable hosting, not a dependency on the owner’s laptop staying awake. For n8n use cases, check P02 before offering hosted/external configuration access.

## Economics and remaining human work
**New customer-price hypothesis:** CAD250–450 for the stated cap; this is not the owner's startup cost, an observed sale or a conversion of earlier USD ideas. The `historical_price_usd_hypothesis` field, where present, preserves the prior unvalidated USD idea; it is not the current quote. Customer willingness to pay this CAD quote is unverified.

**Efficiency change:** Reuse calendar event IDs; use the CRM's native booking integration first.

**Time boundaries:** stop unpaid preparation/qualification for this experiment at four owner-hours total, including the proof; do not build eight custom demos for eight requests. Aim for at most a 60–90 minute reusable fictional proof. The proposed paid delivery allowance is at most 5 hours, including testing and handover, followed by 30–60 minutes of defined defect triage. These are workload limits to validate, not promises that unfamiliar integration work fits them. Quote separately or decline before accepting work that does not fit. Do not omit necessary testing to stay inside the cap.

| Scenario, not forecast | Receipt | Fees / refund reserve assumptions | Allocated cash | All owner hours | Contribution before owner labor/tax | Effective hourly contribution |
|---|---:|---|---:|---:|---:|---:|
| Favorable direct at lower quote | CAD250 | 5% combined processing, 0% refund reserve | CAD0 | 7.5 | CAD237.50 | CAD31.67 |
| Marketplace stress at lower quote | CAD250 | 20% fee, 5% refund reserve | CAD25 | 10.5 | CAD162.50 | CAD15.48 |

The favorable scenario allocates one proof hour, one acquisition hour and half an hour of support on top of the delivery cap. The stress case allocates 1.5 proof hours, three acquisition hours and one support hour. Include previous failed pitches and shared business-development time in actual results; they can exceed both examples. The fee percentages are sensitivity assumptions, not assertions of any provider's exact rate. A 20% marketplace case is deliberately conservative; verify the actual provider and contract.

At an illustrative CAD30/hour owner-time target, the stress scenario needs about **CAD453.33** in customer price to break even economically. This is a rejection test, not permission to claim a buyer will pay that price. If that floor exceeds the credible quote, narrow the deliverable without weakening acceptance, use a less costly acquisition channel, or decline. Zero customers produces zero receipts and loses the time/cash spent.

**Unavoidable human work:** qualification, proof of skill, access decisions, scope agreement, ambiguous exceptions, independent acceptance, handover, support and payment reconciliation. Do not call the offer passive. Full methodology: [economics](../../../../../../research/ECONOMICS_V2.md).

## Customer acquisition and validation gate
### Buyer and buying trigger
An agency with an actual client, permitted test data and a named delivery owner. A request must actually match **keep confirmed bookings and cancellations consistent in one crm pipeline**; broad interest in AI is not enough.

### Positioning and proof
**Landing/profile headline draft:** Keep confirmed bookings and cancellations consistent in one CRM pipeline.

**Show, rather than claim:** Book, cancel and reschedule a fictional event across a timezone boundary. Label all examples fictional. Show actual observed test results only after running them. Keep one relevant annotated screenshot or a 45–90 second demo and a one-page scope; no new website, logo, CRM or subscription is required.

**One-call-to-action draft:** “Send a redacted example of the current problem and the result you need. I will confirm whether it fits this fixed scope before proposing paid work.” This is draft copy, not a message sent.

**Response draft for an invited, eligible buyer request:** “Your request mentions [their exact failure]. My proposed deliverable is: keep confirmed bookings and cancellations consistent in one crm pipeline. The check I would use is: book, cancel and reschedule a fictional event across a timezone boundary. I would first verify whether your existing tools can do this natively. The bounded scope excludes [the project exclusions below]. Are you able to share a redacted example and name the person who will accept the result? I would confirm scope, access and a fixed quote before starting.” Remove any implication of prior client results; do not claim unearned certification.

### $0-first acquisition experiment
Manually inspect the official Make Hire Help and n8n Jobs hiring areas for an explicit, eligible request; do not treat For Hire posts as buyers. Use a warm introduction only where genuine.

**Specific discovery phrase:** `calendar booking cancellation CRM integration`. Check current date, location restrictions, budget, exact deliverable, reputation/credential requirements and whether hiring is still open. Search results and community categories are lead-discovery starting points, not a vetted live prospect list.

Prepare at most eight high-fit request records in two batches of four. Obtain owner approval before responses or public posts. Use one reusable proof and personalize the problem, not a generic AI pitch. Stop at four unpaid owner-hours, eight eligible attempts or fourteen elapsed calendar days—whichever comes first—and review what happened. A time-box is not a promised time to first revenue. Pause earlier when no eligible request exists; do not purchase exposure merely to fill a quota.

**Secondary channel:** one relevant, permitted public demonstration or a genuine opt-in referral. No unsolicited mass DMs, scraped email lists or automated applications. Upwork is optional only after eligibility and actual Connects costs are checked; its proposal expense is not assumed zero. Do not move marketplace-sourced pre-contract communication or payment off-platform contrary to its rules.

### Funnel, decision and sale
Record source, eligible request, authorized response, meaningful reply, scoped conversation, funded agreement, accepted delivery, collected receipt, refund and total owner time. Count unpaid likes, followers, waitlist entries and quotes separately from customers. With no meaningful replies after the first four qualified attempts, revise one of buyer/offer/proof before using the second batch; do not simply increase posting volume. With replies but no scoped agreement, record the objection. With no paid commitment at the cap, pause this offer instead of building more features. These are spending/workload gates, not statistical proof of market failure.

Do not begin client-specific production work until there is an agreed scope, lawful permissions, a funded milestone or approved payment arrangement and acceptance criteria. A small paid diagnosis can precede a repair; do not relabel free discovery as a paid deliverable. Ask for a case study or referral only after a real successful delivery and permission.

**Project-specific rejection:** Stop if recurring appointments, payments or multiple calendars become required.

### Advertising decision
**Current ad allocation: CAD0.** This narrow service needs proof and qualified conversations before broad paid traffic. Advertised job budgets do not establish conversion economics. Only reassess ads after actual profitable sales; any later test must have a measured conversion path, a conservative acquisition-cost ceiling and a separate approved total budget. No retargeting pixels, uploaded customer lists or campaign launch is authorized by this plan.

**Launch gate:** `buyer_test_only`. For skill-gated work, produce a convincing disposable-environment acceptance test before offering the service. For follow-ons, do not advertise before the earlier project actually has paying clients. [Marketing method](../../../../../../research/MARKETING_PLAYBOOK.md) · [Validation gates](../../../../../../research/VALIDATION_GATES.md).

## Progress checkpoint — resume here
- [x] Prior candidate ID retained and scope reviewed on 2026-11-05.
- [x] Current source links, alternatives, classification and scope-specific edge case recorded.
- [ ] Exact buyer/problem validated; no interview or paid test completed.
- [ ] Owner-approved acquisition action and funded scope recorded privately.
- [ ] Implementation built and tested in an authorized environment.
- [ ] Acceptance, actual receipts, costs, total hours and support burden reconciled.

**Current task:** planning only. **Next action:** Review one exact-scope buyer request and the native alternative; prepare a fictional-data test specification and an all-in quote calculation. Do not send or spend without authorization.

**Blockers:** no verified exact buyer, no customer-approved access and no spending/external-action authorization. **Existing deliverables:** this project plan; any related planning fixtures listed in the top-level pilot guide. **Implementation files:** none created for this candidate. **External effects:** none initiated; no upload/publication/payment to retry.

**Decision log:** 2026-11-05 — retain the identifier, reject automatic launch from ranking, and classify as `standalone_service`. 

**Resume protocol:** read this file, its source limitations, the relevant family research and the latest private checkpoint. Verify uncertain external state before retrying an effect. Update only this record and its owned work; preserve completed artifacts and other agents’ changes.

## Evidence references
- [J01](https://www.upwork.com/freelance-jobs/apply/n8n-Workflow-Automation-Specialist_~022116896013798430323/) — n8n Workflow Automation Specialist. Access: `indexed_primary`; evidence type: `buyer_request`.
- [J02](https://www.upwork.com/freelance-jobs/apply/n8n-Integration-Specialist-for-CRM-Sync_~022109970881946103061/) — n8n Integration Specialist for CRM Sync. Access: `indexed_primary`; evidence type: `buyer_request`.
- [J03](https://www.upwork.com/freelance-jobs/apply/n8n-Agent-Automation-Builder-Long-Term-Partner-Per-Project-Pay_~022115893133876904343/) — n8n Agent / Automation Builder — agency per-project partner. Access: `indexed_primary`; evidence type: `buyer_request`.
- [J07](https://www.upwork.com/freelance-jobs/apply/HubSpot-Zapier-Instant-Email-SMS-for-Facebook-Lead-Ads_~022109930742933687604/) — HubSpot / Zapier Facebook lead mapping and follow-up. Access: `indexed_primary`; evidence type: `buyer_request`.
- [J13](https://www.upwork.com/freelance-jobs/apply/Automation-Engineer-n8n-Make-APIs-integrations_~022113363247233397148/) — Agency automation engineer — n8n, Make and APIs. Access: `indexed_primary`; evidence type: `buyer_request`.
- [P06](https://n8n.io/workflows/) — n8n workflow library. Access: `full_page`; evidence type: `competitor`.
- [P07](https://help.make.com/scenario-templates) — Make scenario templates. Access: `full_page`; evidence type: `competitor`.
- [P08](https://help.zapier.com/hc/en-us/articles/15703650952077-Use-the-power-of-AI-to-generate-Zap-workflows) — Zapier Copilot workflow generation. Access: `full_page`; evidence type: `competitor`.
- [P09](https://help.gohighlevel.com/support/solutions/articles/155000006100) — HighLevel AI workflow builder. Access: `indexed_primary`; evidence type: `competitor`.
- [T01](https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee) — Upwork freelancer service fee. Access: `indexed_primary`; evidence type: `policy`.
- [T02](https://support.upwork.com/hc/en-us/articles/211062898-Understanding-and-using-Connects) — Upwork Connects. Access: `indexed_primary`; evidence type: `policy`.
- [T03](https://support.upwork.com/hc/en-us/articles/43342677368467-Use-bots-and-other-automation-properly) — Upwork bots and automation policy. Access: `indexed_primary`; evidence type: `policy`.
- [T05](https://support.upwork.com/hc/en-us/articles/211063748-How-Fixed-Price-Payment-Protection-works-for-freelancers-on-Upwork) — Upwork fixed-price payment protection. Access: `indexed_primary`; evidence type: `policy`.
- [T06](https://support.upwork.com/hc/en-us/articles/211063718-How-payments-for-milestones-and-fixed-price-contracts-work) — Upwork milestone payment timing. Access: `indexed_primary`; evidence type: `policy`.
- [T08](https://www.priv.gc.ca/en/privacy-topics/employers-and-employees/outsourcing/02_05_d_57_os_01/) — OPC outsourcing guidance. Access: `indexed_primary`; evidence type: `policy`.

The shared register records access limitations and dates. A source about a tool’s features is not a paying customer; an advertised budget is not revenue. Historical supplier/repository reports are not freshly rerun tests.

## V2 budget and execution boundary
**Preferred incremental owner cash: CAD0. Current authorized spend: CAD0. Absolute project ceiling: CAD100, not a target.** The ceiling includes tax, FX cost, committed renewals, proposal credits, demonstrations and advertising through the first-sale/first-30-day experiment. Optional envelope for this record: **CAD50**, available only after separate itemized approval. No automatic replenishment, account creation or paid trial. Unknown required costs block execution instead of being entered as zero.

**Budget fit:** `conditional_on_existing_customer_stack`. Existing equipment/software are reused; electricity, past development and sunk subscriptions are not asserted to be free. Owner recurring subscription allocation is CAD0. Customer production accounts/plans/usage are a separate disclosed preflight cost, never silently subsidized from the owner's budget or described as universally free. If safe completion requires an unaffordable owner commitment, simplify or keep the work deferred.

No customer acquisition, publication, payment or account access has occurred in this revision. A marketing plan cannot ensure sales; exact-offer success probability and paid validation remain unestablished. Project execution must also respect the portfolio-wide **CAD0 current authorization**, so starting many projects cannot multiply spending rights. [Budget rules](../../../../../../research/BUDGET_POLICY.md) · [Current research](../../../../../../research/SOURCES_V2.md).

## V2 revision note
2026-11-05: added the applicable marketing, effort and cash gates; preserved recorded completed work and commercial validation. Frontmatter next_action is the current proposed planning step. Older checkpoint instructions remain historical where superseded by this revision; do not repeat completed external actions.
