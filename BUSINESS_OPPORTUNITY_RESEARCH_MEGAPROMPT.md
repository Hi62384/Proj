# EDIT ONLY THESE TWO SETTINGS

**BUSINESS_NICHE:** Game Development Marketplaces  
**BUDGET_CEILING_CAD:** 100

---

# UNIVERSAL BUSINESS OPPORTUNITY RESEARCH → ONE EXECUTION-READY PROJECT

## 0. Your assignment and nonnegotiable output

Execute this prompt in full. The two lines above are the **only user-configurable settings**. Everything else—business model, research breadth, appropriate technologies, go-to-market strategy, timeline, pricing, number of candidates evaluated, and work breakdown—must be decided through evidence-based research. **Do not ask me to set a planning horizon, pick an idea, choose a business model, select a platform, conduct interviews, or answer a questionnaire.** Make reasonable, explicitly labeled assumptions and proceed.

Your task is to find **one** compelling, nonduplicative income opportunity **within BUSINESS_NICHE**, research it rigorously, then create **exactly one downloadable `.md` file** that is a detailed, self-contained, Codex-executable business and implementation plan. The file must follow the current repository's business-project record conventions as closely as the verifiable facts allow. Do **not** create extra spreadsheets, PDFs, slide decks, images, ZIPs, example project files, or multiple opportunity files. All useful research, citations, implementation detail, checklists, and artifacts-to-create instructions belong **inside that single Markdown file**.

**Crucial goal:** Maximize the number of genuinely worthwhile opportunities we can bring to market over successive runs—not the number of flimsy ideas, fake validations, or unfinished prototypes. Minimize delay between credible desk research and an independently verified, sale-ready offer or functioning business. One prompt run produces one new candidate at most; subsequent runs can discover more without repeating the existing portfolio.

This is a universal business-research prompt, **not** a digital-product-only prompt. It must adapt to software, original games, creative media, services, ecommerce, dropshipping, affiliate marketing, advertising, licensing, data, automation, lead generation, APIs, investments, financial research, and any other legal business model that actually belongs to the selected niche. Some businesses require developing something; others require sourcing, providing a service, building distribution, managing operations, or allocating capital. Do not add irrelevant engineering sections just to resemble a software project.

### Permanent operating assumptions (NOT additional user settings)

- Repository to inspect: **https://github.com/Hi62384/Proj**, current default branch and actual accessible content at execution time.
- First portfolio milestone: **CAD 150/month of combined net operating contribution** from the portfolio, *after ongoing cash operating costs, marketplace/payment fees, refunds/allowances, and directly attributable recurring expenses; before personal income taxes and the imputed cost of owner labor*. Each individual opportunity may contribute only part of this goal.
- For investments, keep dividends, interest, distributions, realized gains, unrealized gains, principal movements, and risk-adjusted returns separate. Do **not** reclassify speculative appreciation as reliable monthly business income.
- Canadian owner: validate Canada-specific seller eligibility, payouts, taxes and business/legal rules where material, instead of assuming a US account.
- Default spend authorization: **CAD 0**. The editable budget is a *maximum proposed cumulative startup cash commitment*, NOT permission to spend. The repository currently has its own stricter **CAD 100** commercial-schema ceiling; if the user-entered budget exceeds the latest enforced repository limit, comply with the repository limit and flag the policy conflict. If lower, comply with the lower ceiling. Never silently change the repository's spending policy.
- No forced planning duration: pursue the **fastest credible path** to a tested, operating or purchasable offering. Estimate the actual critical-path duration and show assumptions, but do not invent a deadline or optimize by skipping meaningful QA.
- Minimal human participation, not zero human accountability: do not require research interviews, surveys, customer calls or paid pilots before building. Human involvement is acceptable only when inherent to actual business operations (such as a paying service client), legally required, or necessary for authorization, identity verification, acquiring access, platform publication, payment, supplier contracts, financial decisions, or another unavoidable blocker.
- The final project remains **planned/unvalidated** unless independent evidence shows otherwise. A detailed plan, active storefront, publicly listed product, review count, or apparent search demand does not establish paid sales.

## 1. Read and obey the current repository before choosing an idea

Use available GitHub-connected tools first if the account has access; otherwise inspect the public GitHub repository and source files via normal web browsing. Read the live repository, not recollections or a cached summary. Record the checked branch/commit when obtainable and the date of inspection. Do not falsely imply access to uncommitted local changes, private accounts, sales dashboards, or files you could not inspect.

At minimum, seek and inspect:

1. Root `AGENTS.md`, `README.md`, and repository tree.
2. `business_portfolio/README.md`, `business_portfolio/SCHEMA.md`, `business_portfolio/PROJECT_TEMPLATE.md`.
3. Active niche tree `business_portfolio/niches/**/NICHE.json` and `**/projects/*.md`, including IDs, current statuses, related projects and next actions.
4. `business_portfolio/PROJECT_INDEX.json` where accessible, remembering it is a generated view, **not** the canonical source of truth.
5. Archived business records and the migration/crosswalk files under `business_portfolio/archive/`, including `2026-11-15-legacy` and `2026-11-15-taxonomy-view-v1` if still present.
6. `business_portfolio/research/SOURCE_REGISTER.json`, active source IDs, commercial assumptions and prior opportunity research.
7. Actual existing work in `products/`, `outputs/`, `apps/`, relevant `portfolio_autopilot/` paths, and other repositories/subdirectories that materially overlap the niche.
8. The broader research inventory under `opportunity_library/data/catalog.json`, taxonomy/classifications, archived ideas, current/abandoned offers and historical launch plans.
9. If relevant, `business_portfolio/tools/build_browser.py`, `commercial_checks.py`, and the portfolio tests to confirm current import requirements.

**Do not assume that the 36-category opportunity research taxonomy is the active portfolio niche hierarchy.** At the last verified revision, the active portfolio has 12 business categories and 13 business niches; these can change. Determine the existing niche path and stable `NICHE.json` ID from the *current* repository. `Lead Generation` and `Licensing & Royalties` may function as category/niche nodes without redundant children. Do not invent a new ID or rename a niche merely because this prompt names it differently.

### Mandatory duplication and reuse analysis

Search for duplicates using **the customer job-to-be-done, core functionality, source assets, distribution audience, revenue mechanism, and operating process**, not just the title. Compare each finalist to:

- Existing active project plans, whether built or only proposed.
- All preserved, archived, paused, deferred, failed and published projects, preserving their actual completion state.
- Existing files, reusable components, prototypes, storefront listings and completed source work.
- Previously rejected research directions and why they were rejected.

Assign each serious candidate one outcome: **new and distinct / complement to existing / extension of existing / duplicate / already built / previously rejected / insufficient visibility**. Do not select a duplicate or repackage an identical product with a new name. Prefer a genuinely novel opportunity; where existing work makes a complementary project much cheaper, explain why it is commercially distinct. Never overwrite an existing project or repeat an already completed release. Preserve original IDs and progress.

If the repository is temporarily inaccessible, attempt appropriate alternate access; record exactly what could and could not be inspected. **Do not claim a full duplicate check passed.** Without sufficient repository visibility, a project can be output as **import-blocked provisional research**, not as a duplicate-cleared, ready-to-index record. Include the specific Codex pre-import verification task.

## 2. Research the niche broadly before selecting one opportunity

Do not begin with a favorite idea. First identify plausible business models **within the specified niche** and the distinct buyers/beneficiaries, revenue routes and distribution methods applicable to each. Cover conventional and non-obvious opportunities, including underserved workflow bottlenecks, high-friction processes, creative gaps, underserved customer subgroups, and business opportunities created by platform or industry change.

Run a **two-pass funnel** to balance research depth with speed:

- **Pass A — broad discovery:** Build a working longlist, ordinarily roughly 15–30 materially different ideas when the niche supports it. Group and de-duplicate; quickly reject trivial, saturated, unaffordable, unsupported and excessively labor-intensive models. A narrower niche may support fewer. Do not pad the count with cosmetic variants.
- **Pass B — serious investigation:** Examine the strongest approximately 4–8 alternatives, then deeply compare about 2–4 finalists. Treat these numbers as efficient research heuristics, not mandatory quotas or user settings. Search for counter-evidence as hard as supporting evidence.
- If all finalists fail, research adjacent *within-niche* directions before declaring no-go. Do not drift into unrelated businesses to produce a winner.
- Stop once additional research is unlikely to change the top candidate's decision or the key rejection gates. Avoid endless exploratory loops, but do not cut short a material competitive or legal check.

Research publicly available evidence such as actual purchase requests, user complaints, forum/issue discussions, product reviews, support questions, current competitor listings, official marketplace policies, feature requests, documented failures, pricing, platform/search behavior, free substitutes, native capabilities, and documented customer outcomes. Look for *recent* data and verify dates, especially for changing tools, policies, AI capabilities, prices and access rules.

### Evidence discipline

For every important market claim, link to a named, dated, inspectable source where feasible. Prefer official documentation for rules/fees/technical capabilities and independent customer discussion for reported pain. Explicitly distinguish:

- **Verified fact:** official rule, documented feature, observed listing/price, published technical limit.
- **Direct market evidence:** documented buyer request, paid offer or reported transaction with clear limits.
- **Proxy evidence:** developer complaint, reviews, competing listings, search-interest proxy, forum demand.
- **Inference/hypothesis:** willingness to pay, volume, customer acquisition, future sales, implementation effort.
- **Unverified:** data not accessible, stale evidence, unpublished conversion figures or private seller metrics.

A competing listing and its review count are **not** proof of sales quantity. Prices are not evidence that customers will accept our price. A complaint is not necessarily a paying market. The absence of visible competitors may mean an undiscovered or nonexistent market. Do not invent TAM/SAM/SOM, sales ranks, paid conversions, refunds, customer interviews, financial returns or competitor flaws. Mark research dates, different jurisdictions and limitations.

Try several search phrasings and synonyms when an idea seems promising. Compare official alternatives, free/open-source alternatives, incumbent commercial products, templates/tutorials, and what a typical motivated buyer can achieve using AI assistants. Inspect relevant source licenses and distribution rules.

## 3. Mandatory hard rejection gates

**Hard gates outrank a high numeric score.** Reject a concept as a recommended project when one or more of these applies and cannot be resolved within the planned narrow scope:

1. **No compelling customer/use value:** the proposed value is cosmetic, hypothetical, or readily satisfied by existing means with no meaningful advantage.
2. **Insufficient evidence of demand:** no credible usage/pain/purchase signal after an appropriately broad search; explain the research limit rather than inventing evidence.
3. **No reason to choose us:** free, native, existing commercial, or AI-created alternatives provide substantially the same value at lower total cost and we cannot demonstrate a meaningful difference.
4. **Crowded without an angle:** numerous capable competitors target the same buyer and the differentiated opening is vague, too small or unsubstantiated.
5. **Trivially replicable without creative distinction:** a common prompt, basic script, clone template, generic generated content or a short tutorial effectively recreates the offer.
6. **Unsuitable economics:** cannot credibly contribute positive net cash flow or a useful first-milestone increment after costs, expected acquisition effort, returns and ongoing support, given the capital available.
7. **Prohibitively slow or heavy:** launch path or manual support effort is disproportionate to plausible value; narrow it if a compelling useful subset remains.
8. **Inaccessible market:** no realistic legitimate way to list, deliver, reach buyers, open eligible accounts, obtain payments or provide the service from Canada.
9. **Regulatory, privacy, intellectual-property or platform-policy blocker:** cannot lawfully or safely implement/operate/sell the proposed business under realistic constraints.
10. **Third-party dependency fragility:** success depends on unapproved scraping, prohibited automation, unreliable unofficial APIs, uncontrolled external providers, or permissions we do not have.
11. **Existing portfolio duplication:** substantially the same project or deliverable already exists without a validated reason for a separate offer.
12. **Unacceptable financial downside:** the plan relies on speculative leverage, guarantees, capital loss outside the cash cap, or unrealistic monthly investment yield to meet the target.

Don't over-interpret these gates as requiring statistical proof or pre-sales. Small low-cost experiments can qualify with **credible public signals plus a distinctive, testable value proposition**. For creative products, artistic excellence and a specific audience may justify a small release even when exact demand is uncertain, but reject mass-produced indistinguishable content.

### Two legitimate ways to be differentiated

**A — Technical or operational:** substantial useful functionality, hard edge cases, real integrations, specialist knowledge, verified accuracy, robust testing, maintained compatibility, defensible data/rights, reliable delivery, or end-to-end execution that a buyer would prefer to purchasing/developing piecemeal. Quantify setup and maintenance friction relative to DIY and AI.

**B — Original creative value:** distinctive artistic vision, character/world design, storytelling, audio, visual polish, mechanics, curation, authorship, taste, production quality and cultural appeal. Explicitly describe what is original and appealing. Copyright/likeness/asset rights must be verified. A mass-generated pack, imitation, bland ebook, low-effort wallpaper, generic prompt collection or superficial reskin does **not** qualify merely because it is creative content.

For businesses that do not sell differentiated products (e.g. ordinary investing), substitute the relevant **risk-adjusted economics, capital efficiency, operational advantage and lawful accessibility** rather than inventing a customer moat. For commodity commerce, require an identifiable sourcing, bundling, fulfillment, positioning or distribution edge that survives competitor comparison. For services, require a reliable delivered outcome and a repeatable, appropriately automated process—not a claim that clients cannot use AI.

## 4. Compare the leading candidates with transparent reasoning

Prepare an internal candidate matrix and embed a concise version in the **one final file** (or no-go report). Include:

- Idea and type of business.
- Exact target customer and specific trigger for spending/use.
- Importance/frequency of problem or creative appeal.
- Evidence strength and important contradictory evidence.
- Direct/indirect competitors and free/AI alternatives.
- A measurable or clearly demonstrable reason to choose this offer.
- Startup/recurring costs and possible capital at risk.
- Fastest realistic operational or launch path.
- Ongoing human work, support, risk and automation fit.
- Distribution/acquisition channel accessibility.
- Monthly net contribution plausibility toward CAD150 portfolio goal.
- Duplicate check outcome and reason for selecting or rejecting.

Use a comparative 100-point screen **only as a decision aid**, never as measured success probability: evidence of genuine demand (20), competitive gap/advantage (20), customer value and creative/AI/DIY resistance (15), time to first credible market test (15), realistic distribution/acquisition (10), unit economics and milestone contribution (10), maintenance/automation (5), compliance/feasibility (5). Assign ranges or qualitative confidence if data are weak; an obvious hard-gate failure cannot be rescued by a high score. Explicitly state **why each close finalist lost**.

After selecting a tentative winner, run an **adversarial red-team review**: try to find three reasons it might fail, a compelling free substitute, an AI-generated substitute, a closer competitor, missing evidence, a hidden platform restriction, a grossly optimistic cost assumption, and a likely acquisition bottleneck. If these undermine the choice, switch to another finalist; do not write persuasive copy to defend a weak selection. Preserve the unresolved risks in the final plan.

## 5. Financial and $150/month milestone analysis

The CAD150 target is **portfolio-wide, not an artificial requirement that each project alone earn CAD150**. Determine the project's credible contribution and how many completed sales, subscribers, paying clients, qualified jobs, affiliate conversions, ad impressions, licenses, transactions or invested dollars it would need to create that contribution. If incremental contribution is implausible, reject it regardless of how interesting the project is.

Produce itemized **startup costs** (all-in Canadian dollars, taxes, FX, payment setup, inventory, samples, hosting/API, tools, permits, compliance, ads if considered, refund reserves, noncancelable commitments), **unit economics**, recurring costs, and operator/Codex workload. Distinguish:

- Gross billings/revenue, fees, refunds, cost of goods, variable delivery, fixed cash expenses and **net operating contribution before owner labor**.
- Owner labor hours, support effort, and optional effective contribution per owner hour (not included as an unreported cash expense).
- First-month cash investment and cash runway; capital tied up in inventory or investments separately from spent expenses.
- One-time sales versus monthly recurring revenue; **do not call irregular one-time sales recurring income**.
- Actual paid evidence versus optimistic/conservative scenarios; no made-up conversion rates dressed as facts.
- Where a product contributes e.g. CAD20/month under an assumption, show how that affects the **combined** CAD150 goal without double-counting revenues or related projects.

**At least three scenarios:** stress/conservative, plausible base hypothesis, and upside. Make every sales/conversion/cost assumption explicit. Show formulas and arithmetic clearly (prefer calculations verified with tools if available). Perform sensitivity analysis on price, attainable sales volume, refunds, marketplace fee, support time and customer acquisition. Include the exact break-even condition and a simple contribution-to-target table.

For advertising businesses, do not assume traffic or RPM; calculate threshold traffic using sourced ranges and label assumptions. For affiliate, validate program eligibility/terms, commission eligibility and traffic need; do not assume commissions are paid. For ecommerce/dropshipping, show landed cost, shipping/returns, chargebacks, delivery/quality risks, supplier access, platform subscriptions and demand-generation cost. For services, account for finding a client, qualification, scope, invoicing, communication and delivery—customer acquisition is not 'free' simply because it costs no cash. For SaaS/API, include uptime/support, compute/hosting, abuse and usage costs. For licensing, distinguish one-time fees, minimums, exclusivity and royalties. For financial/investment opportunities, **separate cash yield from price appreciation and capital at risk**, use realistic yield math and downside cases; if sufficient capital is not available, return an honest no-go rather than an implausible trading strategy.

### Budget governance

The **entered budget ceiling** is a ceiling on cumulative incremental owner cash commitments for this opportunity, **not** a marketing budget and **not** authorization to incur any cost. Research and plan under the smaller of the entered budget and the current repository's enforceable ceiling (at last inspection, CAD100). If the budget exceeds the current schema rule, say the conflict explicitly and never silently modify policy. Prefer CAD0 upfront. If the input is 0, all proposed immediate cash expenditures must be 0. Unknown costs are **unknown**, not zero. The owner must separately authorize any spending, publication, account changes or external financial action.

The latest repository's `commercial_revision: 2` validator currently requires `owner_budget.currency` to be `CAD`, `hard_ceiling <= 100`, `authorized_spend: 0` unless a real approval exists, and `owner_recurring_monthly: 0` absent an approved revised policy. Align the proposed metadata with the *current* code; do not mark ongoing fees as authorized. If necessary recurring costs make the opportunity unworkable under policy, reject/defer it rather than hiding them.

## 6. Research distribution, customer acquisition and launch **before** final selection

The strongest technical/business model can still fail because it has no reachable buyers. Investigate concrete channels for the selected niche (official stores, marketplaces, web/search, newsletters, communities, affiliates, direct discovery, approved freelancing platforms, legitimate suppliers, permitted app ecosystems, or other appropriate channels). For each candidate channel, check current:

- Eligibility for a Canadian seller/operator, verification requirements, payouts, taxes, jurisdiction, content/product restrictions, fees and current submission rules.
- Search/discovery mechanism, typical purchase context, relevant keywords, likely saturation and feasible exposure strategy.
- What it actually sells: don't pitch a desktop executable to a marketplace for 3D models or a general software plugin to a consumer-game store.
- Assets needed before opening a listing or customer-facing offer; what may be built locally first.
- Practical route to the **first exposure and first sale**, not just 'publish on social media'.
- Fair, permission-respecting alternatives if no paid ads are viable. Ads default to **CAD0** and require explicit separate approval and favorable economics before even proposing a paid test.

Provide a compelling, specific positioning statement and **ready-to-use drafts** where relevant: store headline, brief and detailed descriptions, buyer outcomes, feature bullets, comparison framing, FAQs, honest limitations, keywords/search copy, demo/storyboard, sample announcement, documentation outline, customer handoff, checkout/support/refund expectations, or a compliant service proposal. Describe exact screenshots/screens and proof demonstrations to capture *after* they exist; do not invent existing visuals or reviews.

Do not use fake testimonials, bots, mass unsolicited messaging, bought engagement, shady affiliate links, misleading scarcity, prohibited scraping or platform rule evasion. No actual outreach, publication, purchases, vendor accounts, trading or payment actions are authorized by this research prompt.

## 7. Pick the fastest honest version that can sell or operate

For the winner, define the **minimum genuinely worthwhile release**: the smallest scope that delivers the *core differentiator and a full end-to-end customer outcome*, NOT a hollow MVP or a set of unfinished stubs. Identify:

- **Must-have** features/operational processes for a useful release.
- Features to defer because they add time without near-term value.
- Quality, rights, privacy, reliability and accessibility requirements that cannot be skipped.
- Concrete 'done' tests and an independent buyer-facing demo or proof artifact.
- Genuine dependency risks and fallback methods.
- The shortest credible critical path, parallelizable tasks that do not write the same files, dependencies, and realistic estimates/ranges rather than promised launch dates.
- Exactly which actions Codex can carry out locally, which can be done using approved connected tools, and which require unavoidable user intervention.
- A stop/reconsideration condition that does **not** demand interviews or paid pilots; a working, properly packaged product may be launched and validated by real marketplace results.

When using multiple platforms/engines/storefronts, evaluate the economic value **per destination**. Share core specifications or code where practical, but do not assume one implementation works universally or that all marketplaces have demand. Start with the fastest credible first release, then prioritize ports based on competition, accessibility and maintenance costs.

## 8. Adapt the complete plan to the actual business model

Do not make all sections software-centric. Determine the selected opportunity's actual execution type and include ALL that apply; explain exclusions briefly when likely to be misunderstood.

### A. Software, SaaS, game-development tools, apps, APIs, automation

Provide a near-implementation-grade **technical specification**, including:

1. User personas, primary jobs-to-be-done, user journeys and prioritized feature acceptance criteria.
2. Architecture overview, component responsibilities and dependency diagram (text/Mermaid when useful).
3. Specific chosen language/runtime/framework/library/SDK versions **where verified**; compare alternatives, favor simple cheap reliable architecture.
4. Proposed repository directory tree and important source files/modules with individual responsibilities and data ownership.
5. Public/internal APIs, event shapes, data contracts, state machines, request/response examples, configuration formats, schemas and validation rules.
6. Core algorithms and pseudocode for technically difficult behaviors, complexity/performance tradeoffs, deterministic test vectors and correctness invariants.
7. Persistence, migrations, backwards compatibility, idempotency, transactions, partial failures, retries, race conditions and consistency guarantees where relevant.
8. Data flow, isolation, auth/authz, secrets handling, supply-chain security, abuse prevention and privacy protections.
9. UI screens, hierarchy, interactions, empty states, failures, keyboard/accessibility and responsive behavior where applicable.
10. Installation, setup, integration hooks, supported platforms/versions and interoperability boundaries.
11. Automated unit/integration/regression/end-to-end/negative/security/performance tests; concrete example fixtures and expected results, not only test names.
12. CI/build/package/distribution/release/versioning/dependency update processes, rollback and reproducible artifacts.
13. Compatibility test matrix, release-blocking acceptance criteria and support/troubleshooting paths.
14. Open-source/copyleft/license obligations, external code and art rights; do not fabricate implementation artifacts or claim unrun tests passed.
15. Cost-control, maintenance burden, telemetry and operational monitoring, if applicable and consented.

A precise architecture is valuable, but do **not** overdesign a universal engine, production infrastructure or unsupported integrations. Name key uncertainties as small technical proof tasks and alternative paths, not as unverifiable promises.

### B. Original games, books, creative assets, educational content, media

Provide an **original creative brief**: audience, unique hook, emotional/learning payoff, detailed concept, artistic direction, tone, content/feature outline, style references that do not copy protected work, characters/setting/story/loop where relevant, production workflow, deliverable inventory, quality benchmark, editing/QA rubric, source provenance, rights/consent, originality checks, packaging, publishing schedule based on actual critical path, previews, discoverability and maintenance. Specify what makes the work **distinctively better than generic AI-generated material**, and why somebody would choose it over free content. Do not rely on sheer volume.

### C. Freelancing, agencies, consulting, other services

Provide the exact **service promise** and exclusion list, defined outcomes, client eligibility, fixed scope, intake questions only when a real customer is engaged, reusable SOPs and templates, automation/delegation plan, access/security boundaries, discovery/contracting/delivery/handover, acceptance tests, dispute/refund policies, revision limits, actual labor including communications, pricing/quote formulas, client acquisition platform eligibility, permitted outreach and follow-up, lead qualification and one first-customer fulfillment example. **Do not require pre-build market interviews.** Real client contact during authorized service sale/delivery is part of the business and should be minimized, not hidden.

### D. Ecommerce, dropshipping, resale, print-on-demand, physical goods

Specify precise product/customer angle, **real suppliers and current access evidence**, sample/quality inspection, landed cost including taxes/FX/shipping, processing, shipping regions/times, inventory or supplier-stock risk, returns/refunds/chargebacks, damaged/lost parcels, customer support, storefront/marketplace restrictions, product/compliance obligations, variant and listing setup, catalog asset rights, ordering/fulfillment SOP, fallback supplier, fraud prevention and profitability after customer acquisition. Do not invent suppliers, availability or wholesale prices; do not propose counterfeit, unauthorized branded, or unlawful goods. If costs exceed the budget or product cannot be validated without purchasing essential samples, mark that blocker honestly.

### E. Affiliate, lead-generation, advertising, communities, content-led traffic

Specify audience/source of original value, verified monetization program access and fee/commission policy, permitted traffic acquisition, real differentiated content/tool/data strategy, owned vs rented distribution, analytics and conversion funnel, consent/privacy/CASL where applicable, affiliate disclosures, publisher policies, abuse prevention, low/zero-traffic scenario, RPM/EPC/lead qualification assumptions, recurring content and moderation labor, monetization thresholds, and measured go/no-go metrics. No synthetic clicks, fake leads, spam, engagement farming or guaranteed SEO rankings.

### F. Data, research, intelligence products, licensing, royalties

Specify source provenance, data acquisition rights and terms, freshness/update cadence, independent verification, methodology, precision/coverage limits, ethical access, redistribution rights, anonymization, buyer uses, license scope (territory/term/exclusivity/resale), pricing/royalties and reporting, delivery format, support, change detection and audit trail. Exclude datasets based on illicit scraping or unauthorized personal data. Do not assume a license has been granted merely because material is accessible online.

### G. Investing, stocks, ETFs, research tools, capital strategies

Clearly distinguish **capital allocation** from operating a business that sells something. Show capital needed for a target cash distribution at credible yields, all fees/taxes/FX, historical variance, drawdown, concentration, liquidity, risk tolerance assumptions, no guaranteed gains, diversification, inflation, and scenarios including capital loss. Never prescribe reckless leverage, day-trading gains or unrealistic yields as a substitute for reliable CAD150 monthly income. Do not trade, open accounts, move money, or represent general research as personal fiduciary advice. If the budget makes the requested earnings infeasible, issue an honest **no-go**; do not manufacture a different niche or secretly pivot into selling stock signals.

### H. Other or hybrid businesses

Define the **true value chain** (what is obtained/created, how users/customers receive benefit, how money is generated, what must operate continuously), correct domain-specific workflows, interfaces and quality checks. Combine applicable modules above; use no irrelevant boilerplate. Include regulated/legal dependencies where genuinely applicable. If this requires a fully new planning discipline, design it with the same evidence, risk, economics, launch and verification standards.

## 9. Implementation tasks must minimize Codex's remaining planning

Produce an executable work breakdown, not a list such as 'build the system' or 'start marketing.' Every meaningful task should include:

- Stable task ID and concise outcome; priority and estimated effort range (uncertain estimates marked as such).
- Prerequisites and the stage in the critical path; opportunities for **conflict-free** parallelization.
- Exact inputs/source facts and source links required to perform it.
- Specific actions and algorithms/procedures, selected tools/engines/platforms and alternatives.
- Expected deliverables **including proposed paths and file/module names where appropriate** (never falsely claim they exist).
- Observable acceptance/negative tests and how to run/interpret them.
- Completion evidence and where it will be recorded, plus rollback/recovery when needed.
- Whether it can proceed unattended within existing permissions; if not, the **smallest unavoidable human action**.
- Costs, platform dependencies, policy gates and conditions to cancel/simplify the task.

Make the task plan **fully sequentially usable** even if only one Codex chat executes it; optionally mark genuinely independent workstreams so multiple chats can claim separate paths. Workstream ownership must respect the repo's existing coordination rules. Do not start alternative worker infrastructure or invent background execution capabilities.

Provide a **first-session Codex runbook**: exact files to read, paths to inspect, collision check, first commands, first five concrete tasks, tests to run, expected outputs and checkpoint writeback. Then provide development/operational stages through launch and first performance review. Include decision criteria for solving implementation surprises without returning for general planning.

Be explicit that after import the code agent should follow current `AGENTS.md`, regular Codex permissions, and actual system state. It may research refreshed facts, test a local proof, continue authorized work and note blockers; it must **not** silently spend, publish, contact people, trade, open accounts, or make unapproved external commitments.

## 10. Product/business quality and launch acceptance

Define a **sale-ready or operational acceptance checklist** suited to the model. As applicable test: correct essential functionality, independent end-to-end use, install/onboarding flow, incompatibility and error handling, rights, privacy/security, taxes/payout eligibility, fulfilled order delivery, refunds/support, performance, cross-version tests, user comprehension, accurate product descriptions, repeatable output, and a rollback plan. A passing build alone is not product-market fit; a polished landing page is not an operating business.

Use **synthetic and owned data** by default; no real customer/account access required during initial design. For performance include machine/platform, scale, method and target, not unmeasured claims. For services, stage a fictional acceptance case. For commerce, calculate a fully priced hypothetical order and clearly identify unverified supplier facts. For creative content, use an originality/quality rubric. For investing, verify arithmetic and warn about capital risk.

Prepare the listing/sales assets in the project plan **as specifications and draft text**. They are not existing deliverables until created and checked. Publication may be the commercial test after satisfactory internal QA; no prelaunch interviews or required pilot sales. Include a **first-sales measurement plan** with genuine data: impressions if observable, product-page visits, qualified inquiries, purchases, revenue, fees, refunds, support tickets, platform review outcomes and dated observations. Don't insist on private marketplace analytics that may be unavailable; identify the exact proxy and its limits.

## 11. Post-launch learning, product portfolio and kill rules

Prescribe brief, meaningful review checkpoints driven by accessible data and actual effort, not rigid arbitrary dates. Once launched, classify the outcome:

- **Continue:** worthwhile sales/traction with manageable service/support costs.
- **Improve:** identifiable conversion, UX, quality or listing bottleneck with a bounded, testable remedy.
- **Expand:** demonstrated success justifies ports, related products, bundles, additional channels or automation.
- **Pause:** weak evidence but very low maintenance and no urgent risk.
- **Discontinue:** repeated exposure with no meaningful demand, prohibitive support, policy/legal problems, negative economics or a clearly superior substitute.

Avoid sunk-cost reasoning. Actual market results replace desk assumptions over time. Updating a plan must preserve existing progress and reconcile any uncertain external side effects; never retry uploads, outreach, charges or publication because a chat lacks memory.

Identify reusable tools/templates/test harnesses/data **already present in the repo** or worth building as part of this project only when they materially accelerate future opportunities. No broad 'platform-building' detour before releasing the chosen offer.

## 12. Output document specification: ONE `.md` file

If a candidate passes the hard gates, create exactly **one** downloadable file, with an informative lowercase hyphenated filename such as `opp-<specific-opportunity-slug>.md`. The Markdown file must contain the **entire** work product. Do not create additional deliverables; a small final chat message linking the file and identifying the verdict is sufficient. Do not paste a giant duplicate of the file into chat.

### A. Repository-compatible strict JSON frontmatter

The current project format begins with `---`, then **a strict JSON object**, then `---`, followed by Markdown. **No YAML frontmatter, comments, trailing commas, duplicate keys, invalid JSON numbers, or invented validated state.** Verify and follow the **live** `business_portfolio/SCHEMA.md`, `PROJECT_TEMPLATE.md` and validators. At last inspection, relevant required fields included:

`id`, `title`, `schema_version` (1), `niche_id`, `niche_path`, `record_type`, `origin`, `priority`, `work_state`, `commercial_validation`, `evidence_basis`, `source_ids`, `parent_project`, `related_projects`, `next_action`, `last_reviewed`, `execution_authorized`, `privacy`.

Additional business metadata should include `commercial_revision`, `owner_budget`, `marketing_execution_authorized`, `production_budget_verified`, `success_probability`, `marketing_lane`, `launch_gate`, price hypotheses and truthful actual-money fields, **as allowed by the current code**.

On a new researched candidate with no verified sales or work, usually choose:

- A genuinely unused ID that matches the **live validator's pattern**, distinct from active **and archived** IDs; at last inspection the pattern was `[A-Z][A-Z0-9_-]*-[0-9]{3,}`. Do not pretend the ID is confirmed unique if you cannot read the full inventory.
- `origin: "revised_candidate"`, a meaningful `record_type` (including a truthful business-model type only if accepted by the current parser), `priority: "P1"` only if actually chosen as the next portfolio research/implementation candidate, and `work_state: "planned"`.
- `commercial_validation: "unvalidated"`; `execution_authorized: false`; `privacy: "public_planning_only"`; `marketing_execution_authorized: false`.
- `actual_revenue: null`, `actual_profit: null`, `verified_paid_pilots: 0` unless genuine evidence has been verified; `offer_price_usd: null` unless an actual approved offer exists.
- `related_projects: []` unless a verified **active** related project ID should be linked (the current builder rejects unknown related IDs); `parent_project: null` unless a real active parent exists.
- The real niche ID/path from its canonical `NICHE.json`, not the requested label transformed into a guess.
- Clear `next_action` to begin **authorized desk work, local feasibility/implementation, or launch preparation**, not a generic mandatory request to interview three teams.
- Date in `YYYY-MM-DD` and explicit research freshness/limitations.
- `owner_budget` metadata obeying actual schema limits: CAD currency, cap=min(entered ceiling, enforced repository ceiling), zero authorized spend, zero recurring owner allocation unless an approved policy change exists, no invented cost verification or approval reference.

#### The **one-file/source-register import problem**—do not ignore

The current `build_browser.py` requires `source_ids` to be a **nonempty list of IDs already in `business_portfolio/research/SOURCE_REGISTER.json`**. A newly researched public URL is **NOT** automatically a registered source. The prompt's single-file constraint means you cannot also output an updated source-register JSON file.

**Resolve this honestly:**

1. Inspect the current source register. Use an already-registered ID in `source_ids` **only when it genuinely supports a factual claim in this project**. Put all newly researched references in the Markdown **Source registration handoff** section with proposed unique IDs, titles, URLs, access/review dates, exact findings and limits. On import, Codex must register the new sources in the canonical register and update `source_ids` accordingly.
2. If there is **no relevant already registered source**, do not invent a valid-looking ID. Mark the document **STAGED — SOURCE REGISTRATION REQUIRED** prominently. Use an explicitly flagged non-registered sentinel in `source_ids` (e.g. `"SOURCE-REGISTRATION-REQUIRED"`) and state that this one file **MUST NOT** be placed directly under `niches/**/projects/` until Codex registers sources and replaces the sentinel. A staged file is not schema-valid/imported yet.
3. If the chosen niche has no canonical `NICHE.json`, do not invent a stable ID. Mark **STAGED — NICHE SETUP REQUIRED** and include the **proposed** path and a `NICHE.json` creation task for Codex; keep the project outside the indexed `projects/` tree until the niche ID is assigned, then update frontmatter. Use an explicit noncanonical sentinel `niche_id` if needed rather than inventing an existing ID.
4. If the repository could not be sufficiently inspected, mark **STAGED — DUPLICATE/ID CHECK REQUIRED**. Add a precise pre-import checklist for the missing checks. Never call such a file already validated by the portfolio browser.
5. These administrative import steps may modify the repository **later** when Codex actually imports the **single** generated project file. They do **not** authorize this research chat to change the repository or produce more output files.

Where everything is verified and the existing source IDs support the record, use a fully schema-compatible frontmatter immediately. **Never sacrifice correctness just to label a file 'ready to import.'**

### B. Required in-file body sections (adapt intelligently)

The final Markdown must contain the following material, with **concrete researched details instead of repeated generic advice**. Keep sections organized so Codex can act on them; merge irrelevant sections only when the information remains findable.

1. **Executive decision:** project title, exact niche, selected business model, intended buyer/user, outcome, why this business, explicit verdict/status and whether import is blocked.
2. **Repository baseline:** checked repo/commit/date, canonical proposed path and ID, existing-asset reuse, semantic duplicate comparison, archive and research references, uncovered visibility limits.
3. **Opportunity discovery and eliminated finalists:** enough of the longlist/shortlist to show what was actually considered and why the winner is preferable; evidence/confidence and kill-gate decisions.
4. **Buyer/audience and problem/value:** precise user persona, use moment, severity/frequency, buyer benefit and nonbuyers; for investments explain economic objective instead.
5. **Evidence ledger:** source table with URLs, dates, concrete claims, conflicting findings, reliability and limitations, plus source-register handoff.
6. **Competition, free and AI substitutes:** specific competitors, current feature/price/policy differences, weaknesses only when supported, DIY/AI feasibility and differentiation proof plan.
7. **Offer and release scope:** complete first salable/operable version, inclusions, exclusions, milestones, quality bar, packaging/delivery and unsupported requests.
8. **Business model and pricing:** how cash is earned, appropriate payment/contract terms, revenue vs expenses, refund/returns, price tests and comparison to alternatives.
9. **CAD150 portfolio milestone economics:** exact conservative/base/upside scenarios, unit economics, cash and capital at risk, break-even, owner time, assumptions and first-milestone contribution.
10. **Acquisition and distribution:** channel eligibility, buyer discovery, launch friction, organic marketing, search/keywords, comparison messaging, listings/service-page drafts, demos/visual requirements and tracking.
11. **Architecture or operating design:** as appropriate: detailed modules, file tree, data/API/contracts, algorithms and security/tests; or supplier sourcing/fulfillment; or service SOP; or creative production bible; or investment/capital/risk framework. Include decisions and alternatives.
12. **Detailed implementation plan:** dependency-ordered workstreams, tasks with file paths/tools/inputs/acceptance, realistic critical path and effort estimates, narrow human approvals and graceful fallback routes.
13. **Testing and independent verification:** concrete successful, unsuccessful and edge-case examples; QA fixtures, reproducible commands/procedures, what Codex can check and what can only be observed after launch.
14. **Rights/compliance/platform requirements:** licensing, Canada eligibility, legal/privacy/tax/identity/account needs, platform distribution restrictions and blocking uncertainties.
15. **Delivery and launch runbook:** packaging/release/service setup, step-by-step marketplace or customer delivery, listing material, checklists and formal human gates where necessary.
16. **Support/operations/maintenance:** likely issue types, remedies, updates, costs, incident/rollback processes and how to keep ongoing work low.
17. **Measurement and next-product loop:** evidence to capture after launch, thresholds to maintain/iterate/pivot/abandon, what to reuse for subsequent products or businesses.
18. **Risks and red-team findings:** top failure modes, contradictions, direct competitor threats, market weakness, capital risk and mitigations; realistic kill rules.
19. **First-session Codex execution handoff:** precise initial steps, paths, commands, source-register and niche-ID import checks, work ownership, actual next action and acceptance evidence.
20. **Resume checkpoint and work log:** *actually completed* research vs unstarted code/operations, remaining tasks, blockers, deliverables (only those that exist), external effects `not_started`, date, and a truthful next action.

For a pure service, do not force a source-code tree; supply an equally specific SOP, deliverable specifications, role/workflow and acceptance protocol. For an original creative work, provide substantial original design and production plans. For an investment, include rigorous risk and capital math, not fictitious source code. A very long project should still be navigable, unambiguous and nonrepetitive.

### C. One-file output and integrity checks

- Actually create the Markdown file using an available file-creation tool and verify its exact path before providing a download link. If no file tool exists, provide the **entire raw Markdown** in one fenced block for manual save, disclose that no downloadable file was created, and do not invent a link.
- Ensure the file is UTF-8, clearly named, JSON frontmatter parses, mandatory fields are present, no unescaped fence accidentally destroys the metadata, all tables/links render, and internal economics reconcile.
- Check current project-ID uniqueness and niche ID/path against the repo when accessible; check source IDs against the source register. Explicitly state which import validations ran versus which are assigned to Codex.
- Do not bundle private data, paid assets, copyrighted material without rights, credentials or fabricated source transcripts into the public project record.
- Do not generate multiple project files or other artifacts under any circumstances for this one run.
- After creating the file, the final chat response should be short: verdict, opportunity name, reason selected, major unresolved blocker (if any) and **one download link**.

## 13. If nothing qualifies: still ONE file, but **not** a fake project

If the evidence honestly supports no worthwhile business **within BUSINESS_NICHE** under the budget and repository restrictions:

- Produce exactly **one** downloadable file named `NO_GO_<niche-slug>_research.md`.
- Clearly mark **NO GO — NO ACTIVE PROJECT CREATED**. This file is a research decision, **not** a canonical project record and must not be dropped under the indexed `business_portfolio/niches/**/projects/` tree.
- Include candidate comparisons, source URLs, most serious rejected opportunities, blockers, and the single most useful future condition that would justify re-examining the niche.
- Do not pivot to a wholly unrelated niche, invent a buyer, assume external funding, or generate a dummy project to comply with an output quota.
- Provide exactly one downloadable Markdown file as requested. The absence of a qualified product/business is a successful and useful research outcome.

## 14. Finish with a final self-audit

Before output, explicitly verify internally that:

1. Only the two top settings were treated as editable; no extra questions or planning-horizon input were required.
2. The candidate is **inside the requested niche**, with the real business model adapted appropriately.
3. The live repository was checked as far as access allowed; active, archive, existing deliverables and historical research were compared for **semantic duplicates**.
4. There is credible public demand/use/creative value; no unwarranted presumption of paid sales.
5. Free/AI/DIY/incumbent alternatives were seriously examined and a **specific purchase/usage advantage** survives.
6. Competition is reasonably manageable for the chosen subsegment, or the unique advantage is strong and demonstrable.
7. The concept is within the budget and support limits; Canadian seller/regulatory/marketplace restrictions were checked where material.
8. The cash-flow model is internally consistent and evaluates a genuine incremental contribution to the **portfolio-wide CAD150/month** milestone.
9. The first offering is *actually useful* and has a short credible end-to-end launch path, not a vague backlog of interesting features.
10. Codex receives detailed architecture or SOP, implementation tasks, acceptance criteria, release checklist, acquisition strategy, economics, first-session plan, and stop rules.
11. Human interviews or paid pilots were **not** imposed as prelaunch blockers; human dependencies are kept to those actually necessary for the business or permission model.
12. No financial transaction, paid account, outreach, store publication, client commitment, user-data access or other consequential external action was performed or implicitly authorized.
13. The result is **one file** and the declared import readiness reflects real source-register, niche, ID and schema facts.
14. All claims of completion, test results, approval, deployment, sales and asset existence are grounded in actual observation; prospective actions are clearly prospective.

**Begin the research immediately using BUSINESS_NICHE and BUDGET_CEILING_CAD from the first two lines. Find the strongest truly worthwhile opportunity, deliver its one exhaustive execution-ready Markdown project file, or deliver one honest no-go Markdown report if the niche fails.**
