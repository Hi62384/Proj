---
{
  "id": "GDM-004",
  "title": "Refactor Ledger — Godot Exported Property Recovery & Git Audit Toolkit",
  "schema_version": 1,
  "workflow_version": 2,
  "project_phase": "working_phase_2",
  "draft": false,
  "niche_id": "N-gdm-20261115",
  "niche_path": "digital-products/game-development-marketplaces",
  "record_type": "product_candidate",
  "origin": "owner_created",
  "priority": "P2",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "Independent Godot developer issue reports, open feature proposals, documented free migration workflows, direct paid competitor inspection, official technical documentation, marketplace payment documentation and a separate adversarial research pass. The historical recovery and CI advantage remains subject to implementation testing; actual customer conversion is unvalidated.",
  "source_ids": [],
  "parent_project": null,
  "related_projects": [],
  "next_action": "Review and independently recheck the Phase 1 evidence, then manually advance to Phase 2 if approved. Preserve the proof-first implementation gate.",
  "last_reviewed": "2026-11-27",
  "execution_authorized": false,
  "privacy": "public",
  "research_verification": {
    "phase_1": "unreviewed",
    "phase_2": "unreviewed",
    "phase_3": "unreviewed"
  },
  "research_verdict": "GO",
  "platforms_proposed": [
    "itch.io",
    "Godot 4.6 standard",
    "Godot 4.7 standard",
    "Windows desktop development environments",
    "Linux desktop development environments",
    "Git-based continuous integration environments"
  ],
  "delivery_window_days": {
    "minimum": 2,
    "maximum": 21
  },
  "phase_history": [
    {
      "from": "working_phase_1",
      "to": "working_phase_2",
      "actor": "user",
      "at": "2026-11-27T03:15:59+00:00",
      "evidence": "Owner advanced the research phase."
    }
  ]
}
---

# Refactor Ledger — Godot Exported Property Recovery & Git Audit Toolkit

## Project brief

Create a specialized offline developer utility for Godot 4 projects using Git version control.

The utility helps developers identify and recover serialized exported-property values that disappear, become outdated or require migration after GDScript refactoring.

The primary commercial differentiator is retrospective recovery using an existing Git commit, combined with deterministic, script-aware auditing that can be repeated locally or during continuous integration.

The product must not merely rename variables, perform unrestricted text replacement or provide a generic AI-generated project audit.

The product will be distributed as a small, documented, tested developer toolkit with no mandatory subscription, cloud service, AI API or runtime integration into the customer's game.

Research verdict: GO — TEST-FIRST.

Commercial validation: unvalidated.

This verdict approves a bounded experiment, not an unrestricted implementation commitment or a prediction of commercial success.

No code, marketplace listing, sales, paid advertising or execution receipts exist at this stage.

## Delivery window and constraints

- Total allowed window: 2–21 calendar days across all six phases.
- Target window: 12–16 calendar days.
- Maximum planning budget: CAD100.
- Planned external cash expenditure: CAD0.
- Currently authorized expenditure: CAD0.
- Execution authorization: false.
- Target price: USD9.99 one-time.
- Initial owner involvement estimate: 4–7 hours.
- Estimated implementation and verification effort: 30–45 hours of effective development work, with additional research, release and marketing effort.
- No mandatory external APIs or recurring hosting expenses.
- No purchases, account creation, uploads, publication or external promotional activity without appropriate authorization.
- Preserve the existing canonical project path and sibling work/ directory.

---

# Phase 1 — Product research and build specification

## 1.1 Product discovery and candidate screening

Research began with actual developer workflows and existing marketplace categories rather than assuming a generic Godot addon would be commercially viable.

The discovery scan considered the following directions:

| Candidate | Target buyer and job | Evidence and principal concern | Preliminary result |
|---|---|---|---|
| Exported-property migration plugin | Developers renaming serialized GDScript properties | Documented developer problems and direct $15 commercial competitor | Strong problem; generic implementation rejected |
| Git-baseline property recovery and auditing | Developers recovering lost settings or reviewing large refactors | Independent reports of values being lost and discovered later; historical recovery differentiation | Selected |
| 3D asset placement | Level designers repeatedly placing environment props | Established paid products and comprehensive free MIT competitor | Rejected as a generic product |
| Subtitle timing and export | Developers integrating voiced dialogue and accessibility subtitles | Real production workflow, but capable free editing and integration tools | Rejected as generic product |
| Localization layout QA | Developers testing translated interface layouts | Native Godot pseudolocalization and emerging dedicated paid tools | Lower priority |
| Animation track repair | Developers restructuring animated scenes | Direct $5.99 commercial alternative | Lower priority |
| Save and persistence toolkit | Developers implementing persistent game data | Numerous inexpensive marketplace listings and easy basic implementation | Lower priority |
| Inventory toolkit | RPG and survival-game developers | Numerous existing general-purpose products | Lower priority |
| Dialogue system | Narrative game developers | Mature free/open-source alternatives | Lower priority |
| General project audit | Developers preparing projects for release | Several inexpensive specialized audit tools already listed | Lower priority |
| Procedural audio generator | Indie developers needing inexpensive sound effects | Low-cost existing products and strong substitute risk | Lower priority |
| RPG statistics and progression toolkit | Developers designing XP and stat curves | Easily reproduced core mathematics and inexpensive alternatives | Lower priority |

The screening is not a claim that every candidate has been exhaustively evaluated. Lower-ranked ideas received preliminary checks rather than full finalist-level verification.

Marketplace discovery references:

- https://itch.io/tools/store/tag-godot/tag-godot-4
- https://itch.io/tools/top-sellers/store/tag-godot/tag-tool
- https://itch.io/tools/newest/store/tag-godot/tag-plugin
- https://itch.io/tools/newest/made-with-godot/store

All accessed 2026-11-26.

## 1.2 Comparison of serious candidate directions

### Candidate A: Exported-property refactoring and recovery

Independent developer reports demonstrate that renaming exported properties can invalidate previously configured values in scenes and resources.

A commercial tool already targets conventional rename migration.

An ordinary competing rename plugin would have insufficient differentiation. The selected variation changes the primary workflow to Git-history recovery and reviewable automated auditing.

The selected variation has credible technical and buyer-value evidence, subject to the proof-first implementation gate.

### Candidate B: 3D asset placement toolkit

Buyer job:

Reduce the repetitive work involved in placing, organizing, aligning and scattering level assets.

Paid alternative:

AssetPlacer by CookieBadger, USD26.99.

The product has an established marketplace presence and offers asset organization, placement and alignment capabilities.

https://cookiebadger.itch.io/assetplacer

Free alternative:

Godot Asset Placer by Roman Levinzon.

The official listing identifies the MIT license and a minimum Godot version of 4.4. Its version 1.7.0 release introduces additional capabilities including brush placement and MultiMesh instancing.

https://store.godotengine.org/asset/levinzonr/godot-asset-placer/

https://github.com/levinzonr/godot-asset-placer/releases

The creator's recent public discussion demonstrates active distribution and attention, although creator promotion is not equivalent to verified purchases.

https://www.reddit.com/r/godot/comments/1xz0o1e/godot_asset_placer_just_hit_170/

Assessment:

There is credible interest in this category, but the free alternative already solves much of the central buyer job. Building another broad placement toolkit would require substantial development and maintenance to create meaningful differentiation.

A specialized placement workflow might remain worthwhile in the future, but no specific unmet segment was established here.

Verdict: IDEA_NO_GO for a generic asset placement toolkit.

### Candidate C: Game subtitle production and integration

Buyer job:

Create, time, validate and integrate dialogue subtitles efficiently.

Independent workflow evidence:

A February 2024 game-development discussion includes developers describing manual timing, timing based on audio duration, editing tools and accessibility-related timing requirements.

https://www.reddit.com/r/gamedev/comments/1b30t2h/

Paid alternative:

Cue Sheet Pro, USD9.99, provides a timing editor, multiple export formats and Godot/Unity runtime integration according to its listing.

https://theluckyduck666.itch.io/cue-sheet-pro

Complete free workflow:

Subtitle Edit is MIT-licensed, free and supports detailed subtitle timing and conversion.

https://subtitleedit.github.io/subtitleedit/overview.html

https://subtitleedit.github.io/subtitleedit/faq.html

For Godot integration, the MIT-licensed Subtitles Importer supports Godot 4.2+ and imports subtitle formats into AnimationPlayer workflows.

https://github.com/Rubonnek/subtitles-importer

Assessment:

The combination solves much of the general subtitle-authoring and integration job without payment. A useful specialized multilingual dialogue production pipeline may be possible, but it was not established sufficiently to justify building another generic subtitle editor.

Verdict: IDEA_NO_GO for generic subtitle authoring and import.

## 1.3 Selected opportunity

Working product name:

Refactor Ledger.

Descriptive subtitle:

Godot Exported Property Recovery & Git Audit Toolkit.

The name is provisional. Check for conflicting products and trademarks before publication.

### Target customers

Primary:

- Solo Godot developers with medium-sized or large projects.
- Small development teams using Git.
- Developers undertaking substantial GDScript refactoring.
- Developers maintaining many configured scenes, resources or inherited scene instances.
- Teams using automated code generation or coding assistants that may rename properties without safely migrating serialized scene data.

Secondary:

- Technical designers maintaining game content through Godot's Inspector.
- Developers upgrading older Godot projects.
- Contractors auditing unfamiliar client projects.

### Poor-fit customers

- Developers without usable Git history.
- Small projects with only a few affected properties.
- Developers who rarely refactor serialized properties.
- Projects exclusively using C#.
- Developers primarily storing their data in unsupported binary resources.
- Customers expecting automatic project-wide code refactoring.

Do not market the product as suitable for every Godot developer.

### Buyer scenarios

Scenario 1: Historical recovery.

A developer renames an exported enemy-health property. Several enemy resources are subsequently saved, removing their old configured values. The loss is discovered days later.

The developer selects a known-good Git commit and provides the old/new property mapping.

Refactor Ledger identifies matching serialized objects, extracts previous saved values and produces a reviewable recovery report.

Scenario 2: Refactoring validation.

A team renames multiple exported settings in a feature branch.

Before merging, Refactor Ledger compares the base revision with the working project and reports old stored values that have not been appropriately migrated.

Scenario 3: Name collisions.

Two unrelated scripts both export a property named speed. Only one script has been refactored.

The tool must distinguish the relevant script and its instances instead of suggesting global replacement.

Scenario 4: Existing new values.

A renamed property already contains a deliberately changed value.

The tool must preserve that value, report the difference and never recommend an automatic overwrite.

Scenario 5: CI review.

A team commits an explicit property migration manifest. Its CI workflow runs the audit and produces a machine-readable report identifying potentially incomplete migrations.

## 1.4 Independent buyer and demand evidence

### Evidence A: Repeated developer problem reports

Godot issue #62643, opened July 2, 2022:

A developer describes configured scene-instance values resetting after exported-variable renaming. The report also describes the difficulty of discovering the cause after subsequent commits.

https://github.com/godotengine/godot/issues/62643

This issue is closed and concerns older engine versions, so it is historical evidence rather than proof of current engine behavior.

### Evidence B: Commercial project refactoring

Godot proposal #10644, opened September 3, 2024:

A developer working on commercial game projects requests a mechanism to preserve exported-property data during refactoring.

The inspected discussion includes multiple approaches and disagreements over their complexity.

https://github.com/godotengine/godot-proposals/issues/10644

The proposal remained open on the accessed page.

A participant described risks when several team members work on the same project and scripts are modified independently.

The discussion also includes significant counterevidence: developers can use compatibility properties, custom migration code or direct file replacement.

### Evidence C: Older maintained-project problem

Godot proposal #3152, opened August 16, 2021:

The author describes maintaining an older, medium-sized project and the difficulty of retaining serialized values during variable renames.

https://github.com/godotengine/godot-proposals/issues/3152

The proposal also contains discussion of team compatibility and automated refactoring behavior.

### Evidence D: Developer-created workaround

An independent developer published a workflow for migrating renamed exported properties by retaining the old property temporarily, adding migration code, processing resources and scenes, and removing temporary migration code afterward.

https://prvaak.cz/blog/safely-renaming-exported-variables-in-godot/

The article establishes that at least one developer considered the problem worth solving with a dedicated workflow.

It also demonstrates a meaningful free alternative and therefore weakens the case for charging for simple property renaming.

### Evidence E: Related serialized-property problem

Godot issue #98524, opened October 25, 2024:

A developer describes stored property values remaining active after a property's export annotation has been removed, despite the property no longer appearing in the Inspector.

https://github.com/godotengine/godot/issues/98524

This is related evidence that serialized scene state can behave unexpectedly during refactoring.

It does not establish that Refactor Ledger automatically solves every stale-property problem.

### Demand conclusion

Observed:

- Multiple developers have reported real problems involving exported-property refactoring.
- Some developers have implemented or requested dedicated migration workflows.
- The problem can affect maintained projects and teams.
- A direct commercial product exists.

Inferred:

- Some developers with complicated migrations may value a dedicated Git-based recovery and audit utility.
- Reviewing historical values without running project scripts may be useful for cautious teams.
- A USD9.99 price may be reasonable for users who would otherwise spend meaningful time investigating lost values.

Not observed:

- Purchases of Refactor Ledger.
- Confirmed willingness to pay USD9.99.
- Reliable sales figures for the direct competitor.
- Quantified market size.
- Verified demand specifically for a CI-integrated version.

Do not convert discussion activity or reactions into estimates of actual customers.

## 1.5 Complete competitive analysis

### Direct paid competitor: Propferry

Source:

https://sundryard.itch.io/propferry

Observed on 2026-11-26.

Advertised price:

USD15 minimum, one-time.

Advertised capabilities:

- Script-specific exported-property migration.
- Preview and application of changes.
- Parent and inherited scene override migration.
- Embedded-resource handling.
- Backup snapshots.
- Restoration of previous changes.
- Editor integration.

Advertised compatibility:

Godot 4.7.2 standard, tested by the seller on Linux.

Other versions are not claimed tested in its listing.

Advertised limits relevant to this proposal:

- Same-type renaming.
- GDScript only.
- Text-format scenes and resources.
- No headless CLI.
- No general type conversion.
- Guard-based recovery depends on available snapshots.

Its public licensing summary permits personal and commercial project use for an individual or studio and restricts standalone redistribution. The complete bundled license was not inspected because no purchase was made.

Propferry is a strong solution for prospective rename migration. Refactor Ledger must not pretend that Propferry lacks ordinary backups, scoped migration or inherited-scene handling.

The selected product instead concentrates on:

1. Existing Git history rather than requiring its own previous backup snapshots.
2. Read-only analysis of a chosen historical revision.
3. Reproducible local and CI reports.
4. Conservative recovery proposals after values have already disappeared.
5. No project addon installation or execution of the customer's game scripts.

Whether buyers prefer these differences remains commercially unvalidated.

### Free alternative 1: Git and manual recovery

A complete manual workflow is:

1. Locate a known-good commit.
2. Inspect historical TSCN and TRES files using Git.
3. Identify the affected script and each serialized instance.
4. Recover the previous value.
5. Edit the appropriate current property.
6. Inspect the resulting Git diff.
7. Reopen and test the project.

Software cost:

CAD0.

This is capable of achieving the buyer's desired outcome.

For a small number of known affected files, it is likely preferable to purchasing a specialized tool.

For many files, inherited instances, identical property names belonging to unrelated scripts and multiple commits, the manual process becomes more difficult to review consistently.

The product's advantage must be demonstrated through reduced work and improved reviewability, not by asserting that manual recovery is impossible.

### Free alternative 2: Compatibility setters and retained properties

A developer can retain an old property, use storage-only exports, introduce a compatibility setter or temporarily migrate values through editor scripts.

Evidence:

https://github.com/godotengine/godot-proposals/issues/10644

https://github.com/godotengine/godot-docs/pull/9900

https://prvaak.cz/blog/safely-renaming-exported-variables-in-godot/

This approach is particularly appropriate when the developer anticipates the rename and still has the old serialized values.

The workflow may require temporary compatibility code, deliberate resource re-saving or project-specific handling.

Refactor Ledger must not claim that compatibility setters are inherently unreliable. Their suitability depends on the project and implementation.

Historical values that have already been removed require a separate source of recovery data, such as Git history or an existing backup.

### Free alternative 3: Scope-aware GDScript refactoring plugin

Source:

https://store.godotengine.org/asset/quanty-bandit/gdscript-refactoring-plugin/

Observed:

- Free distribution.
- MIT license.
- Godot 4.6 and 4.7 compatibility described by the creator.
- Scope-aware script-symbol renaming.
- Reference searching.
- Multi-file preview and undo.
- GDScript language-server integration.
- AI-assisted development disclosed.

The listing describes a capable code-refactoring workflow.

Its advertised focus is not retrospective recovery of deleted serialized values from historical Git revisions.

It may complement the selected product rather than directly replace its historical recovery workflow.

### Free alternative 4: AI-assisted DIY

A developer could ask a coding assistant to:

- Find exported-property changes.
- Search old Git revisions.
- Parse affected scenes and resources.
- Generate a migration script.
- Suggest changes.
- Review resulting Git differences.

This is a serious substitute, especially for users who already have an AI coding subscription.

No claim is made that this product is impossible to reproduce with AI.

The value of the packaged utility must instead come from:

- Tested handling of documented scene structures.
- Repeatable deterministic behavior.
- Explicit handling of ambiguous object identity.
- A known supported-format contract.
- Reusable regression fixtures.
- Auditable reports.
- Conservative suggestions.
- A predictable workflow requiring less project-specific prompting.

If the proof demonstrates that a simple AI-generated script delivers an equally safe and convenient result, reject or substantially narrow the product.

### Cheapest capable paid alternative

The closest inspected direct commercial alternative is Propferry at USD15.

Other lower-priced Godot audit and animation products were discovered, but they were not established as complete substitutes for historical exported-property recovery.

No cheaper equivalent commercial historical-recovery product was identified during this research.

This is not proof that none exists.

The proposed USD9.99 price is below the closest verified comparable paid migration product, while recognizing that their feature sets are not identical.

## 1.6 Separate adversarial research pass

After identifying the original migration opportunity, additional searches targeted:

- Safe renaming without an addon.
- Git recovery of lost scene settings.
- GDScript scope-aware refactoring.
- Compatibility setters and old exported names.
- Resource migration scripts.
- Native serialization-name support.
- Scene/resource diff utilities.
- Godot project auditing.
- Historical recovery and CI workflows.

### Objection 1: The problem can be solved in seconds for free

Evidence:

A February 17, 2026 comment in proposal #10644 describes a simple property rename using direct file replacement, taking approximately 30 seconds.

https://github.com/godotengine/godot-proposals/issues/10644

The independent migration article provides a more comprehensive free workflow.

Assessment:

This objection is valid.

The original general-purpose rename plugin concept is rejected as insufficiently differentiated.

The selected product excludes simple renames from its main commercial promise and targets complicated historical recovery, scoped comparisons and repeated auditing.

Remaining uncertainty:

Developers may still prefer their existing tools for those larger cases.

Status: Survives only with the revised specialized workflow.

### Objection 2: A direct competitor already provides safe migration and recovery

Evidence:

Propferry offers scoped migration, backups and inherited-scene handling for USD15.

https://sundryard.itch.io/propferry

Assessment:

A clone priced slightly lower would be a weak product.

However, Propferry explicitly lists headless CLI support as absent from the advertised version. Its Guard workflow also relies on its own captured history.

Refactor Ledger proposes to inspect Git history that already exists, including revisions from before the customer installed any recovery tool.

The product must demonstrate this difference rather than simply claim it.

Status: Survives, with proof-first verification of retrospective recovery.

### Objection 3: The engine may introduce native migration features

Evidence:

Godot proposal #10644 discusses an engine-native previous-property-name annotation and alternative mechanisms.

https://github.com/godotengine/godot-proposals/issues/10644

The proposal was open during inspection. The version-specific exported-property documentation was also inspected.

https://docs.godotengine.org/en/4.7/tutorials/scripting/gdscript/gdscript_exports.html

Assessment:

A future engine feature could significantly reduce demand for ordinary renaming tools.

Historical auditing, review of incomplete migrations and recovery of values already lost could remain useful, but the market could shrink substantially.

Stop or reevaluate if native functionality provides equally convenient historical recovery and review.

Status: Survives with acknowledged maintenance and obsolescence risk.

### Objection 4: Incorrect recovery suggestions could damage projects

Evidence:

Godot scene files contain external resources, embedded resources, instance references, node paths and other structures. Properties equal to defaults may not be stored explicitly.

https://docs.godotengine.org/en/4.7/engine_details/file_formats/tscn.html

A missing stored value is therefore not automatically evidence of accidental loss.

Assessment:

A general automatic recovery guarantee would be unsafe and unrealistic.

The product will be read-only by default, report ambiguous cases, distinguish explicit values from defaults, and generate conservative optional patches only for supported cases.

No automatic overwrite or automatic Git-history modification is permitted.

Status: Survives through explicit scope restrictions.

### Objection 5: Marketplace acquisition may be too difficult

Evidence:

The independent Godot Marketplace closed on October 30, 2026.

https://godotmarketplace.com/faq-publisher/

The official Godot Asset Store does not currently accept paid assets.

https://docs.godotengine.org/en/stable/community/asset_store/faq.html

itch.io permits developer-tool sales, but it also enforces quality guidelines and discourages excessive automated content and duplicate products.

https://itch.io/docs/creators/quality-guidelines

Assessment:

The available paid acquisition channels are narrower than they might initially appear.

itch.io nevertheless provides an existing category for Godot developer tools and supports low-cost distribution.

A useful free demonstration, honest technical documentation and targeted permitted community promotion provide a feasible initial test.

Actual discoverability and conversion are unknown.

Status: Survives as a small zero-ad-spend experiment, not as a forecast of reliable recurring revenue.

## 1.7 Decision-critical evidence packet

Observation/access date for all entries: 2026-11-26.

INITIAL denotes evidence collected during initial discovery.

RECHECKED denotes evidence directly inspected during the subsequent verification or skeptical search.

| Claim | Direct source URL | Finding | Status |
|---|---|---|---|
| Developers have experienced lost instance values after renaming exports | https://github.com/godotengine/godot/issues/62643 | Historical developer report describes value resets and difficult debugging | INITIAL / RECHECKED |
| Commercial project developers encounter export-refactoring friction | https://github.com/godotengine/godot-proposals/issues/10644 | Open proposal includes commercial project context and developer discussion | INITIAL / RECHECKED |
| Maintained projects face property migration problems | https://github.com/godotengine/godot-proposals/issues/3152 | Developer reports problems retaining values during maintenance | INITIAL / RECHECKED |
| Free manual and scripted migration is viable | https://prvaak.cz/blog/safely-renaming-exported-variables-in-godot/ | Resource and scene migration workflow is publicly explained | RECHECKED |
| Compatibility properties offer another free workaround | https://github.com/godotengine/godot-docs/pull/9900 | Discussion describes alternatives using retained properties and accessors | RECHECKED |
| Direct paid alternative costs USD15 | https://sundryard.itch.io/propferry | Seller advertises scoped migration, backup and recovery functionality | INITIAL / RECHECKED |
| Direct competitor does not advertise headless CLI | https://sundryard.itch.io/propferry | Explicitly included in its current limitations | RECHECKED |
| Free scope-aware code refactoring exists | https://store.godotengine.org/asset/quanty-bandit/gdscript-refactoring-plugin/ | MIT addon provides script refactoring and reference finding | RECHECKED |
| Godot text scenes have documented serialization structure | https://docs.godotengine.org/en/4.7/engine_details/file_formats/tscn.html | Documented sections, resources, node paths and instance structures support static analysis | RECHECKED |
| Exported values are serialized with scenes and resources | https://docs.godotengine.org/en/4.7/tutorials/scripting/gdscript/gdscript_exports.html | Official version-specific documentation confirms underlying storage behavior | RECHECKED |
| Git supports inspecting historical objects without checking them out | https://git-scm.com/docs/git-show | Official Git documentation supports historical inspection approach | RECHECKED |
| Historical Git trees can be enumerated | https://git-scm.com/docs/git-ls-tree | Official Git documentation supports revision file enumeration | RECHECKED |
| Canadian sellers have an available payment route | https://itch.io/docs/creators/payments | Official documentation includes Canadian Stripe payment support | RECHECKED |
| itch.io transaction economics can be modeled | https://itch.io/docs/creators/payments | Default revenue share and typical processing fees documented | INITIAL / RECHECKED |
| Official Godot Asset Store is not currently a paid release route | https://docs.godotengine.org/en/stable/community/asset_store/faq.html | Paid assets are planned but not presently supported | RECHECKED |
| Former independent marketplace is closed | https://godotmarketplace.com/faq-publisher/ | Closure dated October 30, 2026 | RECHECKED |
| Original Godot-compatible utilities can be distributed commercially | https://godotengine.org/license/ | Godot's MIT licensing permits commercial usage subject to applicable notices | RECHECKED |
| Marketplace requires accurate presentation and AI disclosure | https://itch.io/docs/creators/quality-guidelines | Official publication quality and disclosure requirements | RECHECKED |
| Product achieves safe historical recovery on real fixtures | No implementation exists | Requires Phase 4 proof | UNKNOWN |
| Customers will purchase this particular tool | No listing or transactions exist | Future commercial experiment | UNKNOWN |
| Owner's personal seller account is fully eligible | No account inspected | Verify during authorized release preparation | UNKNOWN |

The evidence packet exceeds the normal finalist page-coverage guide because both competitive alternatives and platform restrictions materially affect the decision.

The competitor's downloaded binaries, source and full packaged license were not inspected.

## 1.8 Research gate ledger

| Gate | Result | Reason |
|---|---|---|
| Buyer value | PASS | Real data-loss and migration problems documented |
| Demand context | PASS | Independent reports, developer-created workflows and a relevant paid category |
| Complete free alternatives | PASS for specialized scope | Free workflows solve the task, but complex Git-history recovery and repeatable auditing provide a plausible material convenience advantage |
| Cheapest comparable paid product | PASS | Closest inspected direct alternative is USD15 |
| Proposed unit economics | PASS | Positive contribution under modeled USD9.99 pricing |
| Technical prerequisites | PASS | Git history and documented Godot text formats support bounded implementation |
| Actual implementation correctness | UNKNOWN | Must pass early fixture-based proof and release tests |
| Rights feasibility | PASS | Original code, original fixtures and no required commercial third-party content |
| Canadian distribution eligibility | PASS at platform level | Canadian payment support documented; actual account status unverified |
| Initial customer acquisition | PASS for experiment | Relevant marketplace category and public technical audiences exist |
| Owner effort | PASS subject to estimates | Small bounded product, no server operation |
| Cash downside | PASS | CAD0 planned external expenditure |
| Total time fit | PASS subject to proof | Proposed 12–16-day scope fits 21-day maximum |
| Commercial validation | UNKNOWN / FUTURE TESTABLE | No product, purchases or conversions exist |
| Portfolio duplication | UNKNOWN | Other repository projects were not inspected |

Overall verdict:

GO — TEST-FIRST.

The conclusion is not that Refactor Ledger has a proven moat or guaranteed sales.

It is that credible buyer pain, differentiated workflow scope, feasible implementation and limited financial downside justify attempting a small product.

The early proof is mandatory. Failure to demonstrate a material advantage must stop the current production plan.

## 1.9 Financial model

All selling-price and revenue calculations below are in USD.

The owner's planning budget remains CAD100, with CAD0 authorized spending.

Proposed one-time price:

USD9.99.

Illustrative itch.io transaction model:

- Gross sale: $9.99.
- Marketplace share at 10%: approximately $1.00.
- Processor fee at 2.9% plus $0.30: approximately $0.59.
- Estimated proceeds before reserves: approximately $8.40.
- Modeled refund and adjustment reserve: 10% of proceeds, approximately $0.84.
- Modeled support allowance: five minutes at USD15/hour, approximately $1.25.
- Estimated contribution: approximately $6.31 per sale.

The support allowance and refund reserve are planning assumptions, not measured operating results.

Actual fees can vary by payment method, international transaction, currency conversion, tax treatment and account configuration.

| Monthly sales scenario | Gross revenue | Modeled contribution |
|---:|---:|---:|
| 0 | $0.00 | $0.00 |
| 5 | $49.95 | $31.55 |
| 15 | $149.85 | $94.65 |
| 25 | $249.75 | $157.75 |
| 50 | $499.50 | $315.50 |

These are mathematical scenarios, not forecasts.

The model excludes initial development labor, income taxes, possible withholding, currency conversion and unusual payment disputes.

If itch.io's collected-payment system is used, additional payout-related charges and a documented tax-identity verification charge may apply.

A realistic zero-sales scenario results in:

- No product revenue.
- CAD0 planned external spending.
- Lost development and owner time.
- Potentially reusable technical knowledge and code, but no assumed monetary value.

Labor sensitivity:

If 40 hours of development were valued at USD15/hour, the initial labor cost would be USD600. Approximately 96 sales at USD6.31 contribution would be required to cover that illustrative labor cost.

This illustrates why the project must remain tightly bounded.

## 1.10 Product specification

### Core product architecture

A standalone, offline Python-based command-line utility accompanied by readable HTML reports.

Use:

- Python 3.11 or newer.
- An installed Git executable.
- Python standard-library modules where practical.
- Original code and test fixtures.
- No mandatory third-party Python packages.
- No runtime network connection.
- No external AI calls.
- No hosted backend.
- No Godot addon installation requirement.

Godot is required for development verification and customer project testing, but the static audit itself should not require launching the engine.

Initial proposed target engines:

- Godot 4.6.
- Godot 4.7.

Initial proposed operating systems:

- Windows.
- Linux.

Evaluate Godot 4.4, 4.5 and macOS during Phase 2. Do not claim support without actual tests.

### Main operating principle

The utility compares:

1. A user-selected Git revision containing previous property values.
2. The current saved project files.
3. An explicit manifest identifying relevant exported-property renames.

It determines which supported serialized objects have evidence requiring migration review.

The utility does not attempt to reconstruct arbitrary game behavior or infer every change in a codebase.

### Input requirements

Required:

- Path to the Godot project.
- A Git repository containing that project.
- An accessible historical commit or other resolvable Git revision.
- An explicit migration mapping.
- Supported text-format scene and resource files.

Example mapping:

```json
{
  "schema_version": 1,
  "migrations": [
    {
      "script": "res://actors/enemy_data.gd",
      "old_property": "hp",
      "new_property": "hitpoints"
    },
    {
      "script": "res://actors/player.gd",
      "old_property": "run_speed",
      "new_property": "movement_speed"
    }
  ]
}
```

Mappings are exact and case-sensitive.

Do not accept unrestricted regular-expression property mappings.

Reject:

- Empty property names.
- Duplicate conflicting mappings.
- Cyclic rename mappings.
- Invalid resource paths.
- Identical old and new property names.
- Multiple ambiguous mappings targeting the same property.
- Invalid or unsupported manifest versions.

### Command-line interface

Provide the following workflows.

1. init

Creates a documented example mapping manifest in a user-selected output location.

2. audit

Runs a read-only comparison.

Example:

```text
python refactor_ledger.py audit --project ./game --base HEAD~5 --map migrations.json --out ./ledger-report
```

3. explain

Displays detailed evidence for one selected finding.

4. patch

Generates an optional reviewable patch for explicitly supported recovery candidates.

This command does not apply the patch.

5. self-test

Runs bundled local verification examples and checks prerequisite availability.

6. version

Displays product version, manifest schema version and report schema version.

Commands and flags may be refined during implementation without removing the defined workflows.

### First-use experience

The customer should be able to:

1. Unzip the product.
2. Open a concise quick-start guide.
3. Verify Python and Git availability.
4. Identify a known-good commit.
5. Create or edit a migration manifest.
6. Run the audit.
7. Open the HTML report.
8. Inspect findings and recovery recommendations.

Target installation-to-first-report time:

Under five minutes for a developer who already has Git and a supported Python version installed.

This is an acceptance target, not a currently measured result.

### Historical snapshot reader

Use Git commands to:

- Resolve the supplied revision.
- Identify the repository root.
- Determine the Godot project's location relative to that root.
- Enumerate tracked relevant files at the selected revision.
- Retrieve historical file content.

Requirements:

- No checkout.
- No reset.
- No stash.
- No commit.
- No modifying branches.
- No modifying Git configuration.
- No invoking hooks.
- No network fetch.
- No execution of project scripts.

Use subprocess argument arrays rather than constructing shell commands from user input.

Treat Git revisions, filenames and manifest data as untrusted input.

Reject invalid or unavailable revisions with useful diagnostics.

Report shallow-history limitations rather than downloading data.

### Current project snapshot reader

Read supported files from the saved working tree.

Exclude by default:

- .git/
- .godot/
- Generated import caches.
- Binary resources.
- Product report output directories.
- Explicitly excluded folders.
- Symlinks and unsupported filesystem boundaries.

Support nested Godot projects inside Git repositories.

Do not assume the repository root is always the Godot project root.

Record missing or deleted files separately.

Do not infer that a renamed or moved file represents the same object unless a supported deterministic mapping establishes that relationship.

### Serialized resource parser

Support documented Godot format-3 text structures.

Required recognized sections:

- gd_scene.
- gd_resource.
- ext_resource.
- sub_resource.
- node.
- resource.
- connection sections as non-target content.

Preserve original source offsets and relevant property text.

The parser must correctly distinguish:

- Section headers.
- Quoted strings.
- Escaped quotes.
- Multiline property values.
- Nested parentheses and arrays.
- Dictionary values.
- Comments where applicable.
- External resource references.
- Embedded resource references.
- Node paths.

Unsupported syntax must result in an explicit diagnostic rather than a guessed interpretation.

Do not build a parser based only on a few unrestricted regular expressions.

### Script identity resolver

Associate supported serialized objects with their actual script identity.

Required supported cases:

- Scene nodes with direct external GDScript references.
- Standalone scripted TRES resources.
- Embedded scripted subresources.
- Instance-root overrides where the source scene can be resolved deterministically.
- Inherited root scenes with resolvable base-scene relationships.
- Nested instance relationships that can be resolved within the documented supported subset.

Resolve using explicit resource paths and local resource IDs.

Resource IDs alone are not stable global identities.

For embedded resources, compare the containing file, resource identity and available corroborating structural information.

Mark the object ambiguous if embedded identifiers have changed without a trustworthy way to establish correspondence.

Detect cycles in scene references and terminate safely.

Do not infer unrelated classes are identical merely because they expose matching property names.

Script inheritance beyond reliably resolvable cases is out of the initial guaranteed support contract.

### Object identity and matching

Compare historical and current objects conservatively.

Candidate identity components:

- Project-relative file path.
- Node path.
- Resource section identity.
- Resolved script path.
- Resolved source scene.
- Stable corroborating structural information.

Support unchanged object paths and explicitly resolvable instance relationships.

When an object is moved, replaced, renamed or structurally ambiguous, report that uncertainty instead of guessing.

Never match by property name alone.

### Migration analysis

For each mapping, identify supported historical objects containing the old explicit property.

Compare with the corresponding current object.

Possible classifications:

MIGRATED:

The current new property contains an equivalent supported serialized value.

OLD_PROPERTY_PRESENT:

The old property remains explicitly stored and the new property is not established.

RECOVERY_CANDIDATE:

A historical explicit value exists, the matching current object can be resolved, and the expected new explicit property is absent.

This classification indicates a candidate for review, not proof of accidental loss.

VALUE_CHANGED:

The new property exists but contains a different value.

This may be intentional and must not be overwritten.

CONFLICT:

The old and new properties are both present or another inconsistency prevents a safe suggestion.

AMBIGUOUS:

The relevant object's identity, script, value or serialization cannot be resolved reliably.

OBJECT_MISSING:

The historical object no longer has a corresponding supported current object.

UNSUPPORTED:

The file, property, resource type or structure is outside the supported contract.

The report must clearly distinguish an explicitly stored property from an implicit default.

A property absent from the current file may intentionally equal its script default.

Do not describe all missing explicit values as corruption.

### Value comparison

Initial confidently comparable values:

- Booleans.
- Integers.
- Finite floating-point values.
- Strings.
- StringName values where reliably parsed.
- Supported simple vector and color literals.

Additional report-only values:

- NodePath references.
- External resource references.
- Embedded resource references.
- Arrays.
- Dictionaries.
- More complicated serialized Variant structures.

For references, display the baseline reference and resolved path when possible.

Never transplant a historical ExtResource or SubResource identifier into a current file unless the current reference mapping has been independently verified.

Initial patch generation must exclude complicated reference-bearing values.

Do not attempt arbitrary property type conversions.

### Historical recovery report

The HTML report must contain:

- Product version.
- Audit timestamp.
- Resolved historical revision.
- Project path or privacy-safe project label.
- Supported-format information.
- Scan coverage.
- Total findings.
- Findings by classification.
- File-level breakdown.
- Mapping-level breakdown.
- Historical and current property evidence.
- Relevant source paths and line numbers.
- Reasons for ambiguous or unsupported findings.
- Suggested next actions.
- Clear warnings about review and backups.

Design requirements:

- Professional developer-tool appearance.
- Responsive layout.
- Legible typography.
- Compact summary cards.
- Filterable or easily navigable findings.
- Status indicators that include text.
- No reliance on color alone.
- Keyboard-accessible navigation.
- Copyable source paths.
- No external fonts or network assets.
- No misleading success message when coverage is incomplete.

Escape all user-controlled strings and paths.

A project file containing HTML or script-like text must not execute inside the report.

The report remains local and may contain confidential project values. Warn customers before sharing it.

### Machine-readable output

Generate a versioned JSON report.

Include:

- Tool version.
- Report schema version.
- Baseline revision.
- Scan configuration.
- Coverage counts.
- Findings.
- Classification.
- Historical/current identifiers.
- Relevant serialized values.
- Confidence or resolution status.
- Explanation.
- Unsupported-case diagnostics.

Output ordering must be deterministic except for explicitly documented timestamps and environment-specific metadata.

The same inputs should produce equivalent findings across repeated runs.

### CI support

Provide a documented generic CI integration and an example GitHub Actions workflow.

Proposed exit statuses:

- 0: Successful scan with no findings matching the configured failure policy.
- 1: Successful scan with review findings matching that policy.
- 2: Invalid input or unavailable prerequisites.
- 3: Incomplete scan, unresolved operational failure or strict coverage violation.

Default local mode should make it easy to inspect findings without blocking development.

An explicit CI flag can enforce selected review classifications.

Do not require sending source code to an external service.

Do not add a mandatory GitHub integration to the customer's project.

### Optional recovery patches

The paid toolkit may generate unified diff files for a conservative supported subset.

Requirements:

- Explicit user selection of findings.
- Exact historical/current object match.
- Current property conflict checks.
- Validation that the relevant target property is compatible with the selected mapping.
- Supported scalar or simple literal values only.
- File-content precondition checks.
- No automatic overwrite.
- No automatic patch application.
- No repository modifications by the tool.

Generate a readable patch preview and instructions for manually checking it.

Where practical, document Git's patch-validation workflow.

If file contents changed after the audit, refuse to generate a stale patch.

Never generate patches for ambiguous, unsupported or changed-value findings.

### Persistent settings

Store optional user preferences in a separate user-controlled configuration file.

Possible settings:

- Default output format.
- Explicit exclusion paths.
- Preferred strictness.
- Report privacy mode.

Do not collect telemetry.

Do not store customer source code remotely.

Do not store credentials or access tokens.

## 1.11 First falsification proof

This is the first Phase 4 task and must precede substantial production work.

Maximum initial effort:

One calendar day or approximately six effective development hours, whichever results in an appropriately bounded proof.

Create an original miniature Git-controlled Godot project containing:

- One scripted scene with an exported numeric property.
- Multiple scene instances with different configured values.
- An unrelated script using the same property name.
- A scripted external TRES resource.
- An embedded scripted resource.
- An inherited scene.
- A nested scene instance.
- One intentionally changed new value.

Record a known-good commit.

Rename the relevant property and produce saved states representing:

- Correctly migrated values.
- Values no longer present.
- Remaining old keys.
- Intentionally changed values.
- Ambiguous object identity.

Use real Godot runs or editor saves to establish the serialization behavior where relevant.

Compare three workflows:

A. Manual Git recovery and text editing.

B. A reasonable AI-assisted one-off migration approach.

C. The Refactor Ledger proof.

Record:

- Correct findings.
- Missed findings.
- False positive suggestions.
- Time required for setup and recovery review.
- Handling of unrelated scripts.
- Ability to work from historical Git data without prior product installation.
- Handling of inherited and nested scenes.
- Whether the result is meaningfully easier to repeat.

Minimum proof requirements:

- Detect all intentionally constructed recoverable cases in the explicitly supported subset.
- Produce no recovery suggestions for unrelated scripts.
- Never recommend overwriting deliberately changed new values.
- Identify ambiguous cases without guessing.
- Perform no writes to the customer project.
- Demonstrate historical recovery from a commit created before installing the tool.
- Produce a meaningful repeatability or review-effort advantage against the free workflows.

The quantitative usability target is at least a 50% reduction in measured review effort on a larger multi-file test case, or another clearly documented material advantage.

Do not manipulate the comparison by making the free workflow artificially inefficient.

If these conditions cannot be achieved:

- Stop full production.
- Record the actual failed technical or value gate.
- Evaluate a narrower report-only product only if it retains credible buyer value.
- Otherwise change the verdict to NO_GO or CONDITIONAL_PROOF_ONLY as appropriate.
- Do not expand implementation merely to justify sunk development time.

## 1.12 Component-level work breakdown

| Component | Effort estimate | Dependency | Observable acceptance |
|---|---:|---|---|
| Falsification proof | 4–6 hours | None | Documented side-by-side result |
| CLI and manifest validation | 2–3 hours | Proof | Valid commands and negative-input tests |
| Git snapshot handling | 3–4 hours | CLI | Historical and current snapshots without repository mutation |
| Text resource parser | 5–7 hours | Snapshot handling | Representative fixtures parse deterministically |
| Script and object resolution | 5–8 hours | Parser | Correct supported instance identities |
| Migration classification | 3–4 hours | Resolver | Expected classification for all fixture cases |
| JSON and HTML reports | 3–4 hours | Classification | Readable and schema-valid outputs |
| Conservative patch generation | 2–3 hours | Classification | Valid reviewable patches for supported cases only |
| CI integration and packaging | 2–3 hours | Stable CLI | Clean-install and automation examples |
| Final QA and documentation | 4–5 hours | All components | Release checklist passes |

Estimates are planning ranges and may overlap where tasks are implemented efficiently.

Scope must be reduced if measured development effort threatens the total delivery window.

Do not reduce the correctness or safety requirements.

## 1.13 Acceptance tests

### Positive tests

- Single exported numeric property rename.
- Multiple instances of the same scripted scene.
- Multiple simultaneous mappings.
- Standalone scripted resources.
- Embedded scripted resources.
- Resolvable inherited root scenes.
- Resolvable nested scene-instance overrides.
- Previously deleted explicit values recoverable from Git.
- Current correctly migrated values.
- Windows-style filesystem usage.
- Linux filesystem usage.
- Non-ASCII paths.
- Project nested inside a larger Git repository.
- Repeated deterministic audits.

### Negative and safety tests

- Unrelated scripts using identical property names.
- Existing new property with intentionally changed value.
- Deleted scene.
- Moved node without reliable correspondence.
- Changed embedded resource ID.
- Invalid Git revision.
- Missing Git executable.
- Missing historical file.
- Shallow Git history.
- Invalid JSON manifest.
- Duplicate or cyclic mapping.
- Malformed Godot resource.
- Unsupported binary resource.
- Invalid UTF-8.
- Resource-reference cycle.
- Symlink escaping the project root.
- Very large resource file.
- Shell metacharacters in user-controlled paths.
- HTML and JavaScript-like text in serialized strings.
- Output directory containing existing user files.
- Current file changed between audit and patch generation.
- Interrupted scan.
- Unsupported engine-version declaration.
- Missing current explicit value that may intentionally use a default.

### Patch verification

For supported recovery suggestions:

- Confirm the generated patch is structurally valid.
- Apply it only within a disposable test project.
- Reopen or load the affected resources with the appropriate Godot version.
- Verify intended values are recovered.
- Verify unrelated values are unchanged.
- Verify no scene import errors are introduced.

A patch must never be advertised as safe for an untested format.

### Performance targets

On a documented reference development machine:

- Target audit completion within 15 seconds for a representative 1,000-file fixture project.
- Avoid quadratic traversal where practical.
- Cache resolved resource and scene relationships.
- Place reasonable limits on recursion and input size.
- Avoid retaining unnecessary file copies in memory.
- Provide meaningful progress for larger scans.

These targets must be measured before making performance claims.

### Usability verification

A first-use reviewer should be able to complete the documented workflow without reading implementation code.

Record:

- Installation difficulty.
- Time to first useful report.
- Confusing terminology.
- Error recovery.
- Ability to understand the difference between recovery candidates and definite failures.

If an independent reviewer is unavailable, record that limitation and distinguish a clean-environment self-test from independent feedback.

## 1.14 Product exclusions

Initial release does not include:

- C# property migration.
- Godot 3 support.
- Arbitrary binary-resource parsing.
- Arbitrary script execution.
- Automatic whole-project code refactoring.
- Automatic Git history changes.
- Automatic recovery from inaccessible commits.
- Automatic identification of every renamed property.
- Automatic type conversion.
- Guaranteed recovery of every historical value.
- Cloud synchronization.
- AI integration.
- Subscription features.
- Full project bug auditing.
- Arbitrary save-file migration for shipped games.
- Guaranteed support for all Godot versions.
- Automatic overwriting of customer files.

These exclusions protect the project from becoming a broad refactoring platform.

## 1.15 Deliverables and file locations

All implementation artifacts remain under the existing sibling work/ directory.

Proposed structure:

```text
work/
  source/
    refactor_ledger/
    refactor_ledger.py
  tests/
    unit/
    integration/
    regression/
    fixtures/
  proof/
    baseline-project/
    comparison.md
    measurements.json
  examples/
    example-project/
    migrations.json
    github-actions/
  docs/
    README.md
    QUICKSTART.md
    USER_GUIDE.md
    SUPPORTED_FORMATS.md
    TROUBLESHOOTING.md
    CHANGELOG.md
    LICENSE.txt
    THIRD_PARTY_NOTICES.md
  marketing/
    screenshots/
    demo/
    listing-copy.md
  qa/
    test-results/
    compatibility-matrix.md
    release-checklist.md
  dist/
    refactor-ledger-1.0.0.zip
    refactor-ledger-demo-1.0.0.zip
    SHA256SUMS.txt
```

These are planned paths only.

No files are claimed created.

### Paid package

- Complete utility.
- Historical recovery workflow.
- Multiple property mappings.
- JSON and HTML output.
- CI examples.
- Conservative patch generation.
- Documentation.
- Example project.
- License.
- Changelog.

### Free demonstration

Provide a useful read-only demonstration using the original fixture project.

The demo should demonstrate:

- Actual historical value recovery analysis.
- An unrelated-script collision.
- A deliberately changed current value.
- Clear classifications.
- A real HTML report.

The free demo may omit unrestricted customer-project auditing or optional patch generation, provided its limitations are clearly stated.

Do not create misleading artificial functionality or multiple near-identical marketplace pages.

## 1.16 Licensing and intellectual property

Proposed commercial license:

A one-time license for one individual or studio, permitting use in an unlimited number of that purchaser's own projects and client projects.

Permit normal internal collaboration.

Prohibit redistribution or resale of the standalone commercial toolkit.

Do not prohibit distribution of ordinary games developed using the tool.

The actual license text must be reviewed before publication.

Implementation rules:

- Write original product code.
- Create original fixture projects.
- Do not copy competitor source, artwork, documentation or proprietary behavior implementations.
- Do not incorporate third-party code without verifying its license.
- Preserve required notices for any included dependencies.
- Prefer standard-library-only implementation.
- Do not redistribute Python, Git or Godot executables in the initial package.
- Document external prerequisites.
- Disclose AI-assisted development where applicable.
- Do not claim exclusive ownership of general ideas or functionality.
- Avoid implying endorsement by the Godot Foundation.

Godot licensing reference:

https://godotengine.org/license/

## 1.17 Risks and stop criteria

| Risk | Mitigation |
|---|---|
| Free workflows are sufficient for most developers | Target difficult historical recovery; compare against them in the proof |
| Narrow market | Keep cost and development scope low |
| Direct competitor adds Git recovery or CI | Recheck product before release; stop if differentiation disappears |
| Native Godot features improve | Recheck current engine capabilities |
| False recovery suggestions | Conservative classifications and no automatic edits |
| Serialization changes between versions | Version-specific fixtures and explicit compatibility matrix |
| Excessive support requests | Document strict supported-format boundaries |
| Customer projects contain sensitive data | Fully offline operation and local privacy warnings |
| AI-generated products reduce marketplace visibility | Release one substantive product with accurate disclosure and genuine validation |
| Product name conflicts | Search names before publication |
| Project duplication within owner's portfolio | Check existing portfolio records during authorized implementation preparation |

Post-release commercial criteria:

Measure during the initial campaign and a later optional 30-day evaluation.

Track:

- Relevant listing visits.
- Free demo downloads.
- Paid purchases.
- Refund requests.
- Support time.
- Actual transaction costs.
- Credible user feedback.

Illustrative initial decision thresholds:

- Fewer than 100 relevant listing visits: acquisition remains inadequately tested; do not conclude demand failure from this alone.
- At least 200 relevant visits and zero purchases: investigate positioning, demo value and buyer fit before further investment.
- Five genuine paid purchases with acceptable support burden: evidence sufficient to consider continued maintenance.
- Repeated reports of unsafe suggestions: suspend promotion and correct the underlying issues.
- Support averaging substantially more than 15 minutes per sale: reassess economics and scope.
- No credible traction after two bounded positioning experiments: stop further investment unless new evidence justifies it.

Thresholds are decision aids, not statistical guarantees.

## 1.18 Total project schedule

| Phase | Proposed duration | Observable outcome |
|---|---|---|
| Phase 1 — Product research | 1 day | Evidence-backed candidate specification |
| Phase 2 — Release research | 1 day | Accepted compatibility and distribution matrix |
| Phase 3 — Marketing research | 1 day | Approved channel and measurement plan |
| Phase 4 — Build and verify | 6–9 days | Verified product and packages |
| Phase 5 — Release | 1–2 days | Authorized marketplace release and recorded URLs |
| Phase 6 — Initial marketing | 2 days | Executed placements and recorded initial results |

Target total:

12–16 calendar days.

Reserve up to the remaining five days within the 21-day ceiling for necessary QA or bounded corrections.

External account review, payout review or marketplace indexing delays must be recorded separately. Do not claim publication or payouts that have not occurred.

## Phase 1 checklist

- [x] Screen multiple distinct product opportunities.
- [x] Inspect independent buyer-side problem reports.
- [x] Inspect free migration and refactoring workflows.
- [x] Inspect closest direct paid competitor.
- [x] Research technical prerequisites.
- [x] Research initial Canadian distribution feasibility.
- [x] Conduct a separate adversarial search.
- [x] Document major counterfindings.
- [x] Model pricing and downside.
- [x] Define bounded product specification.
- [x] Define proof-first acceptance criteria.
- [ ] Complete the separate Phase 1 verification prompt.
- [ ] Resolve any newly discovered material weaknesses.
- [ ] Obtain owner review and manual phase advancement.

---

# Phase 2 — Release platforms and compatibility

Status: pending dedicated research and verification.

## Preliminary route assessment

| Route | Current assessment |
|---|---|
| itch.io | Primary proposed paid release route |
| Official Godot Asset Store | Potential free demonstration or genuinely useful free component; paid assets unavailable |
| Former independent Godot Marketplace | Rejected: closed October 30, 2026 |
| Gumroad | Conditional secondary distribution route requiring fee, seller eligibility and acquisition research |
| Other direct digital-product storefronts | Conditional; compare incremental benefits and effort |
| GitHub | Potential documentation, examples and free demo distribution; not assumed to be the paid storefront |
| Unity Asset Store | Not suitable for current Godot-specific product |
| Fab | Not established as suitable for this product |
| Unreal Engine port | Deferred; distinct implementation and market research required |

Do not create unnecessary additional listings merely to increase the number of platforms.

Where compatible marketplaces genuinely improve reach and fit the project window, include them after Phase 2 research.

## Preliminary compatibility matrix

| Target | Status |
|---|---|
| Godot 4.6 standard | Proposed; testing required |
| Godot 4.7 standard | Proposed; testing required |
| Godot 4.5 | Conditional; evaluate fixtures and demand |
| Godot 4.4 | Conditional; evaluate fixtures and demand |
| Windows | Proposed; native testing required |
| Linux | Proposed; native testing required |
| macOS | Conditional; require actual compatible test environment |
| GitHub Actions Linux runners | Proposed; workflow testing required |
| Other CI services | Document generic compatibility only when supported |
| Godot .NET/C# properties | Excluded |
| Godot 3 | Excluded |

## Phase 2 research checklist

- [ ] Verify current itch.io seller onboarding requirements.
- [ ] Verify Canadian payment eligibility and actual account prerequisites.
- [ ] Compare collected payments with direct payments.
- [ ] Confirm actual fee and refund implications.
- [ ] Determine appropriate currency configuration.
- [ ] Verify AI-content disclosure requirements.
- [ ] Verify official Godot Asset Store free-asset rules.
- [ ] Determine whether a free companion listing is permitted and worthwhile.
- [ ] Evaluate Gumroad and other genuinely relevant storefronts.
- [ ] Check product naming conflicts.
- [ ] Define final engine-version matrix.
- [ ] Define final operating-system matrix.
- [ ] Confirm availability of real compatibility test environments.
- [ ] Define accepted package formats.
- [ ] Record each accepted and rejected route with reasons.
- [ ] Update Phase 1 specification where compatibility changes.
- [ ] Independently verify Phase 2 research.
- [ ] Obtain manual owner advancement.

No release route is recorded as operationally verified yet.

---

# Phase 3 — Marketing strategy

Status: pending dedicated research and verification.

## Provisional positioning

Lead with the actual buyer problem:

Recover previously configured Godot property values from Git history and review incomplete migrations without automatically modifying the project.

Secondary selling points:

- Offline operation.
- Script-aware matching.
- Reviewable historical evidence.
- CI-compatible reporting.
- No mandatory subscription.
- Conservative recovery suggestions.

Avoid statements such as:

- Never lose Godot data again.
- Recover every property.
- Automatically fix every refactor.
- Guaranteed safe on all projects.
- Official Godot refactoring tool.
- Proven to save hours before measurements exist.

## Preliminary audience access

Potential channels:

- itch.io Godot tool discovery.
- Godot developer forums.
- Relevant Godot Reddit communities.
- Relevant developer Discord communities with permitted promotion.
- GitHub documentation and public example fixtures.
- Search-oriented technical articles.
- Short demonstration videos.

Community rules must be researched before posting.

Do not insert sales advertisements into unrelated bug reports, technical support threads or other developers' project repositories.

Do not create fabricated testimonials, ratings or endorsements.

## Marketing assets

Prepare:

- One professional product cover.
- Actual screenshots of the working report.
- One short demonstration of historical value recovery.
- A free example project.
- A technical explanation of supported and unsupported cases.
- A concise comparison with manual Git recovery.
- Installation and compatibility information.

Use actual product outputs rather than fabricated interface mockups in release materials.

## Proposed initial campaign

Day 1:

- Publish the approved listing.
- Publish the approved demonstration.
- Publish documentation and example material where permitted.

Day 2:

- Share the genuine demonstration in approved relevant channels.
- Record links and measurable initial results.
- Record feedback.
- Correct factual listing errors.

No paid advertisements are planned.

## Phase 3 checklist

- [ ] Research current promotion rules for each proposed community.
- [ ] Identify relevant permitted announcement channels.
- [ ] Research appropriate listing keywords and tags.
- [ ] Inspect marketing approaches of relevant developer tools.
- [ ] Define final positioning.
- [ ] Define exact promotional assets.
- [ ] Define initial release announcement.
- [ ] Define measurable traffic and conversion metrics.
- [ ] Set promotional spending to CAD0 unless separately authorized.
- [ ] Establish a bounded follow-up evaluation.
- [ ] Independently verify the marketing plan.
- [ ] Update earlier phases if research exposes significant weaknesses.
- [ ] Obtain manual owner advancement.

---

# Phase 4 — Build and verify

Status: not started.

Estimated implementation completion: 0%.

The following checklist is provisional until Phase 2 and Phase 3 are complete.

## Proof gate

- [ ] Create original Git-controlled Godot fixtures.
- [ ] Reproduce relevant property-refactoring behavior.
- [ ] Establish expected historical/current outcomes.
- [ ] Implement the minimal retrospective audit proof.
- [ ] Compare against manual Git recovery.
- [ ] Compare against reasonable AI-assisted DIY.
- [ ] Measure correctness and review effort.
- [ ] Record all limitations.
- [ ] Confirm the differentiated workflow remains worthwhile.

Do not continue to full production if the proof fails.

## Production

- [ ] Implement validated CLI.
- [ ] Implement versioned manifest parser.
- [ ] Implement historical Git snapshot reader.
- [ ] Implement current snapshot reader.
- [ ] Implement supported Godot text parser.
- [ ] Implement script identity resolver.
- [ ] Implement supported instance and inheritance resolution.
- [ ] Implement conservative object matching.
- [ ] Implement migration classifications.
- [ ] Implement JSON reports.
- [ ] Implement self-contained HTML reports.
- [ ] Implement report privacy controls.
- [ ] Implement optional conservative patch generation.
- [ ] Implement CI exit policies.
- [ ] Implement example CI workflow.

## QA

- [ ] Complete unit tests.
- [ ] Complete integration tests.
- [ ] Complete actual Godot fixture verification.
- [ ] Complete negative and malformed-input tests.
- [ ] Verify no repository or project mutation during audits.
- [ ] Verify patch correctness on disposable fixtures.
- [ ] Verify cross-version behavior for every accepted engine version.
- [ ] Verify every accepted operating system.
- [ ] Verify supported CI workflow.
- [ ] Verify input sanitization.
- [ ] Verify HTML escaping.
- [ ] Verify performance.
- [ ] Verify clean installation.
- [ ] Complete first-use evaluation.
- [ ] Correct every confirmed release-blocking issue.
- [ ] Record remaining non-blocking limitations accurately.

## Packaging

- [ ] Complete quick-start guide.
- [ ] Complete user guide.
- [ ] Complete troubleshooting documentation.
- [ ] Complete supported-format documentation.
- [ ] Complete compatibility matrix.
- [ ] Complete commercial license.
- [ ] Complete third-party notices.
- [ ] Complete changelog.
- [ ] Generate paid package.
- [ ] Generate free demo package.
- [ ] Generate package checksums.
- [ ] Verify package contents.
- [ ] Verify installation from the actual final ZIP.
- [ ] Save screenshots from the actual release candidate.
- [ ] Save actual demonstration recordings.
- [ ] Record final artifact paths.
- [ ] Record final test results.
- [ ] Record implementation completion percentage.
- [ ] Obtain approval for release.

---

# Phase 5 — Release execution

Status: not started.

Estimated release completion: 0%.

- [ ] Confirm execution authorization.
- [ ] Confirm final accepted release platforms.
- [ ] Verify seller account prerequisites.
- [ ] Complete authorized payment setup.
- [ ] Verify listing name.
- [ ] Upload the verified paid package.
- [ ] Upload the verified demonstration package.
- [ ] Configure approved pricing.
- [ ] Add actual compatibility information.
- [ ] Add license information.
- [ ] Add AI-assisted development disclosure.
- [ ] Add genuine screenshots.
- [ ] Add demonstration material.
- [ ] Add support information.
- [ ] Review listing for factual accuracy.
- [ ] Publish only after appropriate authorization.
- [ ] Verify public listing accessibility.
- [ ] Verify the free download workflow.
- [ ] Verify paid checkout accessibility without fabricating a purchase.
- [ ] Record actual listing URL.
- [ ] Record actual edit URL.
- [ ] Record actual download URL where applicable.
- [ ] Record platform acceptance or publication receipts.
- [ ] Record unresolved indexing, account or payout issues.
- [ ] Record actual completion percentage.

No purchase, payment, publication or listing URL currently exists.

---

# Phase 6 — Marketing execution

Status: not started.

Estimated marketing completion: 0%.

- [ ] Confirm approved marketing plan.
- [ ] Confirm relevant channel permissions.
- [ ] Publish approved technical demonstration.
- [ ] Publish approved announcements.
- [ ] Publish approved documentation or article.
- [ ] Record actual placement URLs.
- [ ] Record publication dates.
- [ ] Record observed traffic.
- [ ] Record observed demonstration downloads.
- [ ] Record actual sales if any.
- [ ] Record actual revenue and fees if any.
- [ ] Record actual refunds if any.
- [ ] Record support requests and time if any.
- [ ] Record genuine feedback.
- [ ] Compare results with the predefined decision criteria.
- [ ] Identify remaining corrective actions.
- [ ] Verify that all accepted release and marketing tasks have supporting evidence.
- [ ] Record actual marketing completion percentage.
- [ ] Conduct final project verification.

Do not mark the project commercially validated without appropriate real evidence.

Completion of the initial marketing phase does not require inventing sales.

Do not keep expanding marketing activity indefinitely when the bounded project is complete.

---

# Important data and URLs

## Project identity

- ID: GDM-004.
- Niche: Game Development Marketplaces.
- Canonical path: business_portfolio/niches/digital-products/game-development-marketplaces/gdm-004-empty-project/project.md
- Current phase: working_phase_1.
- Commercial validation: unvalidated.
- Maximum planning budget: CAD100.
- Authorized expenditure: CAD0.
- Proposed price: USD9.99.
- Proposed project duration: 12–16 calendar days.
- Maximum project duration: 21 calendar days.

## Independent problem evidence

https://github.com/godotengine/godot/issues/62643

https://github.com/godotengine/godot-proposals/issues/3152

https://github.com/godotengine/godot-proposals/issues/10644

https://github.com/godotengine/godot/issues/98524

https://github.com/godotengine/godot-docs/pull/9900

https://prvaak.cz/blog/safely-renaming-exported-variables-in-godot/

## Competitive products and discovery

https://sundryard.itch.io/propferry

https://store.godotengine.org/asset/quanty-bandit/gdscript-refactoring-plugin/

https://cookiebadger.itch.io/assetplacer

https://store.godotengine.org/asset/levinzonr/godot-asset-placer/

https://github.com/levinzonr/godot-asset-placer/releases

https://theluckyduck666.itch.io/cue-sheet-pro

https://subtitleedit.github.io/subtitleedit/overview.html

https://subtitleedit.github.io/subtitleedit/faq.html

https://github.com/Rubonnek/subtitles-importer

https://www.reddit.com/r/gamedev/comments/1b30t2h/

https://www.reddit.com/r/godot/comments/1xz0o1e/godot_asset_placer_just_hit_170/

https://itch.io/tools/store/tag-godot/tag-godot-4

https://itch.io/tools/top-sellers/store/tag-godot/tag-tool

https://itch.io/tools/newest/store/tag-godot/tag-plugin

https://awasan26.itch.io/animation-retarget-godot

## Technical documentation

https://docs.godotengine.org/en/4.7/engine_details/file_formats/tscn.html

https://docs.godotengine.org/en/4.7/tutorials/scripting/gdscript/gdscript_exports.html

https://docs.godotengine.org/en/4.6/tutorials/i18n/pseudolocalization.html

https://git-scm.com/docs/git-show

https://git-scm.com/docs/git-ls-tree

https://godotengine.org/license/

## Release and financial documentation

https://itch.io/docs/creators/payments

https://itch.io/docs/creators/faq

https://itch.io/docs/creators/quality-guidelines

https://stripe.com/global

https://docs.godotengine.org/en/stable/community/asset_store/faq.html

https://docs.godotengine.org/en/stable/community/asset_store/submitting_to_asset_store.html

https://godotmarketplace.com/faq-publisher/

## Operational data

Actual product listing URL: none.

Actual product edit URL: none.

Actual downloadable product package: none.

Actual marketing placement URLs: none.

Actual sales evidence: none.

Actual completion receipts: none.

No sensitive account or payment data should be stored here.

---

# Decisions and work log

## Original project state

An empty planning record was created.

No product, research, implementation, release or marketing work was previously claimed complete.

The supplied original last_reviewed date was 2026-11-27. This research pass uses the actual observation date, 2026-11-26, without treating the supplied future date as evidence of additional work.

## 2026-11-26 — Phase 1 research pass

Completed:

- Preliminary marketplace opportunity screening.
- Comparison of several distinct product directions.
- Independent investigation of exported-property refactoring problems.
- Direct inspection of the closest paid migration competitor.
- Investigation of complete free and AI-assisted alternatives.
- Separate disconfirming searches.
- Initial technical feasibility assessment.
- Preliminary Canadian marketplace eligibility assessment.
- Financial scenario modeling.
- Detailed bounded product specification.
- Definition of mandatory falsification proof.
- Provisional release, build and marketing checklists.

Decisions:

- Reject a generic exported-property renaming clone.
- Select retrospective Git-based recovery and audit functionality.
- Avoid direct project writes in the initial release.
- Restrict patch generation to confidently supported cases.
- Use a zero-hosting-cost architecture.
- Propose USD9.99 one-time pricing.
- Propose itch.io as the initial paid storefront.
- Retain the 21-day maximum total delivery window.
- Require the technical and workflow proof before full production.

Limitations:

- No implementation tests have been executed.
- No paid competitor was purchased or tested.
- Competitor capability comparisons rely on inspected public documentation.
- The complete commercial competitor license was not obtained.
- No actual customer conversions are known.
- No owner seller account was inspected.
- Other portfolio projects were not inspected for duplication.
- Full Phase 2 and Phase 3 research remains pending.
- Research does not establish that the entire possible competitor market has been exhausted.

Verdict:

GO — TEST-FIRST, commercially unvalidated.

Current next action:

Run the separate Phase 1 verification prompt against this record.

If the verification confirms the recommendation, manually advance to Phase 2.

Do not change execution authorization, commercial validation or current project phase automatically.
