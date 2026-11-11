# AWA-005 — fictional mapping proof and handover

**Complete locally:** one deterministic 15-field transformation with a parity report. **Not complete:** live connector integration, a verified eligible buyer, account permissions, paid scope or customer acceptance. CAD0 incremental purchases/commitments; no external sends or account changes.

The single pair is a fictional form `questions[]` array → fictional contact-property proposal. The `demo_*` destination names are placeholders, not certified HubSpot internal property names. IDs are stable fictional keys. It reuses the synthetic contact ID/email from `fixtures/awa-001-cases.json`; that earlier fixture's broader connector tests remain `not_run`.

Run from the repository root with installed Python (standard library only):

```
python business_portfolio/tools/awa005_mapping_demo.py
python -m unittest discover -s business_portfolio/tests -p test_awa005_mapping.py -v
```

The first command prints JSON only and exits nonzero on a failed fixture case. It has no network client, destination writer, credentials, web server or automatic alert sender. JSON stdout escapes Unicode for Windows legacy consoles; decoding restores exact text. The saved UTF-8 parity report is observed output, not a prospective test plan. Source: `tools/awa005_mapping_demo.py`; fixture/rule map: `fixtures/awa005-field-mapping.json`; independent boundary tests: `tests/test_awa005_mapping.py`.

## Rules and reviewed scope

All 15 fields appear in each parity result: external ID, full name, email, service, seats, approved flag, notes, phone, company, website, city, language, interests, requested date and rating. String fields receive type/nonblank checks, not full email, phone or URL validation. Dates use strict ISO calendar validation. Integer fields reject booleans and negatives. Picklists use explicit fictional allowlists; duplicate multi-select values are held.

Optional missing/null values omit writes; required missing/null values hold the event. Blank strings and empty multi-select collections hold instead of silently clearing. Numeric zero and boolean false survive with exact JSON types. Unknown IDs, duplicated IDs or invalid values hold the **entire** proposal, so no valid subset escapes. Display-label changes retain stable-ID mapping; a changed ID requires review and an explicit map version. The v1.1 demonstration changes only that one rule. Restoring v1 holds the renamed input again, which is configuration selection, not a real CRM rollback.

No live account or destination database exists in this proof. Output proposals are not applied. Deterministic replay is not durable idempotency, and emitting `drift_alerts` is not operational monitoring. Existing customer values and historical records were never accessed. The unit suite checks independent expected values/types, no input mutation, malformed payload rejection, map ambiguity, instruction-like text as inert data and Windows stdout compatibility. It does not prove production robustness.

See [market check](MARKET_CHECK.md), [scope/quote draft](SCOPE_AND_QUOTE_DRAFT.md), [observed parity](parity-report.json) and [acceptance checkpoint](ACCEPTANCE.md). All drafts remain local and unsent. Do not paste real customer payloads into this public-results namespace.

The [versioned fictional field map](field-map.json) is a reviewed copy for Files & Results; edit the source fixture and regenerate evidence rather than creating a second mapping database.
