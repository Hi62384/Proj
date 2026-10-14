# Intake and acceptance checklist

This is an operational checklist, not legal advice or a substitute for a suitable written agreement.

## Before accepting the job
- Confirm the buyer has authority to share/use the data and purchase the work.
- What report is needed, by whom, how often, and what exact manual task does it replace?
- Record current workload using the buyer's observation; do not invent ROI.
- Obtain 10 redacted example rows and representative edge cases, not credentials.
- Define source columns, unique row ID, duplicate treatment, date/time zone, currency, rounding,
  null/negative values, metric definitions, expected totals and export format.
- Check that this pilot's format/volume limit is sufficient. A demo supporting one CSV does not yet join two arbitrary files.
- Agree delivery start conditions, acceptance test, revision limit, price, cancellation and data retention.
- Verify required registration, privacy obligations and payment-provider eligibility.
- No external AI/cloud upload without an appropriate processing agreement and client authorization.

## Acceptance test
- Agreed input fixtures parse; bad fixtures fail explicitly.
- Input record counts and totals reconcile to output; no silent dropped rows or guessed values.
- Required fields and duplicate IDs are checked under agreed business rules.
- Buyer confirms that the report answers the agreed operational question.
- Re-running the same input gives the same result.
- Re-running fulfillment does not charge again or duplicate downstream actions.
- Instructions work on the supported environment.
- Source files remain intact; data is deleted on the agreed schedule, subject to lawful retention.
- Record written acceptance and any exclusions; never invent customer approval.

## Human approval stays required
Business definitions, rights/permissions, privacy decisions, production writes, refunds, destructive changes,
ambiguous document extraction, and materially changed client-facing calculations.
