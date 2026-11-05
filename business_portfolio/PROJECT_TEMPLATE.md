# Project template — copy only when selecting a genuine new project

Create a unique ID, preserve it across moves, choose an existing niche ID/path, replace every placeholder, and save under that niche’s `projects/` folder. Do not put this template itself into the indexed tree unchanged. Price/hours are assumptions until measured. External work remains subject to actual permissions.

```json
{
  "schema_version": 1,
  "id": "NEW-001",
  "title": "Replace with a distinct actionable result",
  "niche_id": "N-existing-id",
  "niche_path": "existing-niche/child",
  "record_type": "standalone_service",
  "origin": "revised_candidate",
  "priority": "P3",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "capability_and_competitor_only",
  "source_ids": [
    "P06"
  ],
  "parent_project": null,
  "related_projects": [],
  "legacy_ids": [],
  "next_action": "Replace with a concrete bounded next action",
  "last_reviewed": "2026-11-05",
  "offer_price_usd": null,
  "delivery_hours_assumption": null,
  "total_first_order_hours_assumption": null,
  "verified_paid_pilots": 0,
  "actual_revenue": null,
  "actual_profit": null,
  "owner": "unassigned",
  "execution_authorized": false,
  "privacy": "public_planning_only",
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
    "budget_fit": "unassessed_costs_block_launch",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  },
  "marketing_execution_authorized": false,
  "production_budget_verified": false,
  "success_probability": "not_established",
  "marketing_lane": "not_selected",
  "launch_gate": "cost_and_buyer_preflight",
  "pre_sale_work_cap_hours": 2,
  "ad_test_cap_cad": 0,
  "offer_price_cad_hypothesis": null,
  "historical_price_usd_hypothesis": null
}
```

In the actual project, put that JSON between two `---` delimiters, without the code fence. Use these body sections:

## Buyer, problem, buying trigger
Who can approve payment? What observed problem prompts a purchase? Why would native tools, vendor support, free templates or AI not already solve it?

## Evidence and limits
List dated source IDs and exactly what each supports. Distinguish buyer requests, competitor features/prices, opinions and actual private paid evidence. Record unsuccessful validation too.

## Deliverable and scope cap
Define the number of sources/objects/records/fields, output, integration boundaries, revisions and support window. State exclusions and access/cost prerequisites.

## Acceptance and failure cases
Define expected outputs, malformed/duplicate/partial-failure behavior and independent verification. Separate mocks, staging and production results. Document uncertain side effects and recovery.

## Economics and remaining human work
Include search/failed proposals, communication, discovery, access, build, QA, handover, support and admin. Distinguish gross revenue, cash contribution, owner time and illustrative economic surplus. Keep currencies separate.

## Validation gate and stop condition
What evidence permits the next stage? What would make the offer too risky, redundant or uneconomic? A management threshold is not a statistical guarantee.

## Resume checkpoint
- Completed with evidence:
- Current task:
- Remaining checklist:
- Blockers/decisions needed:
- Next concrete action:
- Owned deliverables and hashes/versions:
- External effect state: not_started / confirmed / uncertain; never retry uncertain effects automatically.
- Private checkpoint reference, if appropriate and non-sensitive:

## Decisions and work log
Append date, what actually changed, result/evidence, unresolved issue and next action. Preserve historical decisions when superseded; do not silently erase them.


## V2 commercial planning additions for a newly created record
Before using this template for a new launch, add the revision-2 metadata as illustrated in an actual revised record: CAD0 preferred/authorized; CAD100 cumulative ceiling; itemized optional costs; unknown production costs; launch gate; marketing lane; all-in time cap; current price-currency hypothesis and separate historical prices. Do not clone paid evidence or completed checkmarks from another record.

Add a buyer-specific headline, proof, draft response/CTA, primary permission-appropriate acquisition route, native alternative, qualified-attempt limit, all-in time/economics model, ad decision and measurable stop rule. Bundles/internal projects must say why they do not need independent customer acquisition. Link relevant sources and mark exact versus adjacent demand; no unsupported probability of success.


## Customer acquisition and advertising
- Exact buyer/request and current channel eligibility:
- Outcome headline, proof, limitations and single call to action:
- Native/free substitute and reason to pay:
- Permission-appropriate primary acquisition route and tailored draft:
- Qualified-attempt and all-owner-hour caps:
- Conversion stages, private evidence and stop/change rule:
- Advertising decision (default CAD0), future economics gate and verified total billing cap:
- All-in quote sensitivity, production-cost payer and required account features:
- Separate actual authorization before any send, publication, spend or account change:
