> Historical v1 research. Revision 2 commercial/budget/marketing decisions take precedence; see [current findings](RESEARCH_V2.md), [economics](ECONOMICS_V2.md) and [marketing](MARKETING_PLAYBOOK.md). Old price/ranking assumptions are not new verification.

# First paid pilot: one form → CRM → internal notification

**Recommended record:** AWA-001. Alternative entry: AWA-005 field-mapping rescue or AWA-007 capped diagnosis. This guide is a plan, not a contract, a launched offer or authority to spend/contact anyone.

## Stage A — prove a small delivery capability locally

Use `fixtures/awa-001-cases.json` as a fictional test specification. It is not an importable n8n/Make/Zapier workflow and has not been run against a customer platform. Demonstrate stable event identity, field validation, destination conflict handling and recovery using already available tools. No paid account, API key or Connects purchase is required to read the plan. Do not pretend a mock destination proves a real connector works.

The operator should be able to explain a duplicate event, a malformed payload, a temporary error, a permanent validation failure and an uncertain remote side effect. Time the preparation. If even the bounded demo needs a large new infrastructure stack, simplify the offer before doing sales. A suggested reassessment checkpoint is 3–5 hours, not a guaranteed training duration.

## Stage B — qualify a real buyer before a custom build

For an owner-authorized buyer request, establish: one actual form, one CRM object, up to twelve mapped fields, one internal notification destination, current plans, expected volume, latency tolerance, identity rule, required/optional fields, exception owner, data rights and the account owner. Ask for one redacted example of the desired output and one failure case. Identify what native integration already does. Avoid regulated records or customer messaging in the initial pilot.

Agree the specific deliverable, acceptance cases, revision cap, support window, exclusions, payment process and ownership of configuration. Example proposed support boundary: one defect correction round within seven days of acceptance; new fields, apps or changed business rules require new scope. This is an offer-design hypothesis, not a policy already accepted by a customer.

A proposed US$200–350 price is suitable only if the whole job supports the owner’s selected economic threshold. Record actual fee/plan costs before a quote. Do not collect credentials through chat; request customer-managed scoped connections or the platform’s delegated access. No implementation depends on the owner’s laptop for production uptime.

## Stage C — receive authorization and funded scope

Draft an individualized proposal for owner review. Do not submit automatically or move pre-contract discussions off-platform contrary to rules. A funded milestone is a prerequisite to customer-specific paid implementation, not permission for unlimited account access. Customer production changes still require the agreed authority, window and rollback/reconciliation plan. [T03–T06]

No hard promise of “zero lost leads” or “100% uptime.” Specify how rejected, missed and uncertain events are detected and reconciled. An API returning success is not independent proof the desired record exists. Business-level reconciliation and explicit exceptions matter.

## Stage D — build, accept and measure

Create the smallest flow in the customer’s selected platform. Keep AI out of identity and validation rules unless a documented need warrants it. Test valid, duplicate, concurrent duplicate, malformed, unknown field, rate-limited, timeout, permission-loss and crash-after-remote-success cases within authorized staging. Log only necessary redacted identifiers. Verify the destination and the error disposition independently.

Handover should include: configuration/export where permitted; field map; account owner; triggers/volumes; test evidence; error/replay instructions; limits; cancellation/rollback notes; and temporary-access revocation. No secrets in exported workflows or public screenshots. A reviewer unfamiliar with the build should be able to identify a failed event and know when not to replay it.

Use the platform’s correct delivery/acceptance process. Track released/available/settled payment separately. Record all time, fees, defects and support after delivery. First acceptance does not validate repeat demand. Consider a second similar client only if the scope and actual economics are acceptable.

## Proposed gates and stop conditions

A real paid pilot is a useful milestone, not proof of scalable demand. Before productizing, seek several independent paid examples showing the same problem and why native alternatives did not suffice. Require actual repeat payments for a recurring offer. Keep an owner-time cap and stop when sales, permissions or exceptions erase the benefit.

A failed attempt should leave a useful checkpoint: buyer fit, reason lost/declined, actual hours, constraints, missing skills, source/date and next decision. Do not respond to weak demand by building sixty more features or another storefront.

Evidence IDs refer to [SOURCES.md](SOURCES.md) and the machine-readable [SOURCE_REGISTER.json](SOURCE_REGISTER.json). Planning choices and calculations are not observed customer results.
