# EDIT ONLY THESE TWO SETTINGS

**PROJECT_IDEA:**

```text
PASTE YOUR IDEA HERE.

It can be a sentence, a detailed story plot, a game concept, a software tool,
service idea, business process, ecommerce opportunity, content channel,
licensing concept, investment approach, or any other legal project.

Include any details you regard as essential. Anything you explicitly specify
is a constraint unless it conflicts with feasibility, law, rights, or safety.
```

**BUDGET_CEILING_CAD:** 100

---

# UNIVERSAL IDEA → FULL BUSINESS & EXECUTION PROJECT — ONE FILE

## 0. Mission, operating assumptions, and output contract

**Execute this entire prompt.** The two settings above are the **only fields the user edits**: `PROJECT_IDEA` and `BUDGET_CEILING_CAD`. The first may contain many paragraphs or a detailed plot. There is **no niche selector, time-horizon selector, project count, marketplace selector, preferred technology, or questionnaire**. Infer those from the actual idea and current evidence. Never ask for an optional setting already derivable from the idea or research. If a nonessential detail is absent, make the most defensible reversible design decision and label it as an assumption. For genuine unavoidable blockers (e.g. ownership of specific third-party IP, age/identity verification, required capital, an account login), document the precise action the owner must take **without blocking the planning work**.

**Crucial distinction from the companion `BUSINESS_OPPORTUNITY_RESEARCH_MEGAPROMPT.md`:** That prompt researches a niche to *discover a new idea*. **This prompt starts from the user's idea, respects it as the brief, strengthens it, and converts it into a complete execution-ready project.** Do not replace the idea with an unrelated “higher-scoring” business. Do not use a large idea-discovery funnel. Research ways to make *this specific idea* excellent and commercially viable; evaluate variants, scope, release formats and channels **within the user's concept**. If something fundamental makes the idea infeasible, explain that and give the closest feasible remedy without silently changing its identity.

**Required deliverable:** Create **exactly ONE downloadable UTF-8 `.md` file**. For a feasible idea, this is a detailed, self-contained business/project specification that Codex can use to **create/implement/operate, independently test, package, publish or launch, market and maintain the idea** with minimal additional planning. Write the real, specific plan—not a generic template with placeholder bullets. The single Markdown file must include the complete research evidence, exact implementation or production plan, marketing assets/copy, multi-channel distribution strategy, financial analysis, first tasks and operational checkpoints. Do not create an extra executive-summary file, PDF, spreadsheet, ZIP, slides, or separate chapter outline. The owner's original idea must be preserved in the one file.

**If inherently unworkable:** Deliver one `NO_GO_<idea-slug>.md` decision report instead of a fictitious active project, containing the precise blocker, what research actually established, and the nearest idea-faithful alternative that would resolve it. Do not dismiss an otherwise viable creative work merely because its commercial demand is unproven; a modest, differentiated, inexpensive release can be a legitimate marketplace experiment. A weak/uncertain business case should be openly labeled, not marketed as certainty.

**Fixed assumptions — not editable settings:**

- Portfolio repository: **https://github.com/Hi62384/Proj**. Inspect its **current** default branch, actual schema, niche tree, projects, archives, deliverables and current progress; prior conversations and examples are not a substitute for the live repository.
- First milestone: **CAD150/month of combined net operating contribution** across all businesses, after ongoing cash operating expenses, sales/platform/payment fees and returns allowances, but before personal taxes and imputed owner labor. This is a portfolio target: no requirement that this single project individually earn CAD150 monthly. Keep realized investing results and appreciation separate from operating-business income.
- Owner is based in Canada for eligibility/payout/relevant rule checks. Do not assume US-only creator, seller, publisher or broker programs are available.
- **Spending authorized by this prompt: CAD0**. `BUDGET_CEILING_CAD` is the maximum **proposed cumulative new owner cash exposure**, not permission to make commitments. Respect the stricter of this input and the repository's *currently enforced* commercial limit (previously CAD100). If the input exceeds the enforced limit, flag the conflict and use the stricter effective cap; never silently change the repo budget policy.
- **Speed:** Optimize for the fastest **credible, complete and quality-controlled** route to publication, customer availability, or lawful operations. Determine a realistic critical path from the work; do not ask for or impose a user-set planning horizon and do not replace a full release with an unusable “MVP.”
- **Human interaction:** No mandatory market interviews, customer discovery calls, surveys, focus groups, agency/team approval, beta users or paid pilots as prerequisites. Use public evidence, internally reproducible QA and marketplace results. Human interaction is permitted only when genuinely required by the operating model (e.g. actual client delivery), legal/contractual requirements, access/identity, financial decisions, platform/submission review, ownership of source materials, purchases or other necessary permissions.
- A generated plan **does not authorize** purchases, uploads, publication, client contact, account creation, financial transactions, investments, orders or third-party actions. Those are explicitly identified as future owner-approved steps. Do not claim any product is already built, tested, live, sold or commercially validated without independent evidence.
- Workflows are adaptable to any project type: original book, fiction/nonfiction series, game, mobile app, developer plugin, digital asset, artwork, video/content account, service, ecommerce/dropshipping, print-on-demand, automation, SaaS/API, physical product, research offering, licensing, investing or hybrid businesses. Do not force a software architecture on a book, or a book launch plan on a B2B service.

## 1. Extract and protect the exact idea

Before researching, parse `PROJECT_IDEA` into a **brief fidelity contract** and preserve it verbatim in a clearly labeled section of the resulting project file. Organize:

1. **Core concept:** what the user wants to create/do and for whom; the key customer, audience, experience or economic objective.
2. **Nonnegotiable elements:** characters, plot, setting, game mechanics, requirements, intended output, target customer, preferred technologies/platforms, explicit style, limitations and user-provided facts actually stated.
3. **Flexible elements:** sensible creative, technical, pricing, packaging and go-to-market decisions that the idea leaves open.
4. **Unknowns/assumptions:** matters the model must decide and later verify; keep ownership, production rights and financial account access uncertain until confirmed.
5. **Project identity:** one canonical parent project, with editions/formats/platform-specific deliverables as children/tasks **inside the same project**, unless the repository's existing structure requires a distinct ID for a genuinely distinct business.

**Do not invent user intentions or rewrite the original concept into a different genre, target customer, product or storyline simply to be more marketable.** If the idea supplies a plot, protect the main characters, major events, ending and required tone; elaborate continuity, arcs and scene mechanics around them. If the idea describes an app behavior, preserve required workflows; architect a reliable implementation. If the idea describes an investment or financial strategy, preserve the question/goal while rigorously analyzing feasibility and risk, without promising returns or automatically executing trades.

**When the idea contains copyrighted or third-party material:** Identify whether it is the user's own original work, public-domain material in the relevant jurisdictions, or requires permission. Do not assume rights. Plan the safest legally supportable implementation and highlight the exact license/permission needed. The user's own submitted material may be used as input to elaborate the plan, but that alone is not proof of ownership of every referenced brand, character, image or song.

**Define the finished result** in a testable sentence: the complete customer-facing deliverable or functioning operation, including what a buyer/reader/player/client actually receives and how they can access it. List explicit exclusions to prevent scope creep.

## 2. Inspect the live repository and prevent duplicates or progress loss

Use the connected GitHub tool when available; otherwise inspect the public repository with web access. Prefer current canonical files over generated indexes. Record inspection timestamp, checked branch/commit when known, and any visibility limits. Inspect at minimum:

- `AGENTS.md`, root `README.md`, and the current repository tree.
- The root `BUSINESS_OPPORTUNITY_RESEARCH_MEGAPROMPT.md` for consistency, when available.
- `business_portfolio/SCHEMA.md`, `business_portfolio/PROJECT_TEMPLATE.md`, `business_portfolio/README.md`, `business_portfolio/research/SOURCE_REGISTER.json`.
- Every relevant `business_portfolio/niches/**/NICHE.json` and `**/projects/*.md` with IDs, statuses, plans, source IDs and last checkpoint; verify the **current** hierarchy, even if it has recently changed to five primary categories.
- `business_portfolio/PROJECT_INDEX.json` only as a derived navigation aid, not the primary source of truth.
- Archives and crosswalks under `business_portfolio/archive/`, including preserved 2026-11-15 revisions when present.
- Existing implementation/assets under `products/`, `apps/`, `outputs/`, `portfolio_autopilot/` and any other clearly relevant folders.
- `opportunity_library/data/catalog.json`, taxonomy/research histories and previous rejected, paused, published or duplicate concepts.
- Relevant Portfolio Manager workflow, source-registration/import rules, browser builder and commercial validators.

**Semantic duplicate test:** Compare the user's idea with existing work by actual job-to-be-done, plot/premise and unique creative elements, user journey, algorithm/features, target audience, output rights, distribution and business model. Check *active, archived, completed, published, deferred and partially implemented work*. Similar names alone do not imply duplicates; different names do not prove uniqueness. Identify exact reusable work and the risk of accidental duplicate publication.

If the same project is already in the repo, do **not** create a second competing canonical project or reset progress. Generate the **improved project plan for the existing stable ID**, preserving completed work, deliverables, real metrics, existing decision log and related projects. Mark all new proposed steps as remaining, not completed. Specify merge-by-ID and content-hash checks in the Codex handoff. If the idea genuinely extends existing work, explain exactly what is reused and what is distinct.

If repo access is incomplete, **do not claim the duplicate or ID check passed**. The output must be staged and marked as needing Codex pre-import verification, while still planning the idea in full. Never invent a niche ID, source ID, published work, actual income or completed implementation.

**Niche placement:** Determine the best *existing canonical* niche from the current `NICHE.json` tree. A game-development addon may belong in Digital Products → Game Development Marketplaces; a novel may belong in Books & eBooks; a service in the appropriate Services subniche. If the exact niche is missing, choose the nearest truthful parent and document an owner-approved niche-creation/migration task. Do not arbitrarily invent categories or silently restructure the portfolio. Preserve stable IDs across any moves. Respect the optional niche-level `working` state if it exists: generating a plan alone must not switch it on or claim a Codex worker is running.

## 3. Research THIS idea rather than search for unrelated opportunities

Investigate the intended customer/audience/user, actual value proposition, likely pain or appeal, competition, demand signals, substitutes, rights, technical feasibility and practical distribution. This is a **focused idea-development investigation**, not a 30-idea hunt.

### Evidence and competitors

- Verify current official documentation for all important technology, content formats, marketplaces, fees, eligibility, payouts, content/licensing rules and distribution terms.
- Examine direct competitors and adjacent products/works/offers, including free/open-source/native alternatives, marketplace listings, user reviews and public discussions. Cite exactly what supports each claim; never fabricate sales, review counts, ranking, downloads or weak points.
- For a creative project, compare positioning, genres/subgenres, tropes, format, audience expectations, quality and discoverability **without copying another creator's protected expression**.
- For technical projects, compare setup time, capabilities, version compatibility, reliability, maintenance, support, integration friction and what a competent customer could generate with AI.
- For commerce and services, examine pricing, fulfillment, platform commissions, sourcing/quality, customer acquisition, delivery time, refunds and complaints.
- For investments, analyze risk-adjusted objectives, opportunity cost, fees, diversification, drawdowns, taxes, available capital, liquidity and whether financial goals are mathematically plausible.
- For every significant source include title, exact URL, organization/author, publication/update date (if known), access date, concrete supported claim, confidence and limitations. Clearly label facts versus assumptions and unanswered questions.

**No invented viability:** A published listing proves a listing exists, not that it sells. Other creators' views/likes do not predict this project's audience. A complaint is not a confirmed purchase intent. An investment's historical return is not a forecast. If public evidence for an original creative idea is indirect, state that openly. A product can still be a sensible small release experiment if costs and downside are low and its creative premise is distinctive.

### Differentiation required

- **Creative:** identify the actual original appeal (characters, world, dramatic engine, voice, imagery, art direction, mechanics, emotional payoff, craft quality, distinctive audience promise). A generic AI-written or mass-generated work is insufficient merely because it can be published quickly. Include a concrete originality and anti-derivative quality review.
- **Technical:** specify a buyer-relevant capability not trivially created with a one-shot AI prompt, simple script, template or existing free tool. Prefer complex real integration, reliability, hard edge cases, maintained compatibility, useful data/rights or verified results.
- **Services:** define specialized reliable client outcome, scope, consistent delivery and quality controls; client acquisition can remain a real operational step when unavoidable.
- **Commerce:** define a defensible sourcing, quality, positioning, brand, bundling or delivery advantage; generic resale of easily discovered supplier items is not enough.
- **Investing:** competitive differentiation may not apply. Instead evaluate available capital, plausible risk-adjusted returns and safe, lawful mechanics; never create an artificial buyer/value proposition.

### Idea-faithful viability decision

Deliver a concise verdict: **PROCEED TO BUILD / PROCEED WITH A NARROWED SCOPE / CONDITIONAL BLOCKER / NO-GO**. Give evidence and the strongest counterarguments. Do not add nonessential interviews or pilot programs as gates. Define no more than the necessary pre-build technical/rights feasibility checks. If a small local proof can establish the uncertain mechanism quickly, make that Codex's first technical task, not a months-long interview process.

## 4. Turn the idea into the best complete release, not a vague MVP

Specify the actual deliverable, its core advantages, its audience and the smallest **fully satisfying** release. This should be fast to produce **because scope is sharply chosen**, not because quality, story coherence, reliability, legal compliance or testing are skipped.

For each proposed feature/content component/workflow specify:

- **Must have at first publication:** essential to fulfill the user's idea and the buyer/audience promise.
- **Should have if cheap:** improves presentation or utility without threatening the first release.
- **Defer:** expansion, optional editions, translations, plugins, advanced modules, sequel, extra platforms that do not yet make economic sense.
- **Never included:** prohibited dependencies, copyright misuse, unreliable promises and costly optional complexity.

Decide meaningful length, scope, editions and technical choices *from the idea*: e.g., for a novel choose genre-informed target word-count range and chapter structure; for a game choose platform, core loop and minimum complete content; for a SaaS choose paid promise and production guardrails; for a freelance service choose turnaround/SOP and exact handoff; for a commerce offer choose SKU set, supplier/quality and fulfillment; for financial research choose analysis and risk limits rather than claiming an asset exists.

Provide a **definition of done** using objective checks and observed artifacts, plus qualitative craft checks where necessary. State what cannot be verified by tests alone (reader satisfaction, sustained sales, platform acceptance, buyer demand).

## 5. Full design/production package — select ALL applicable branches

**Use the appropriate sections below, with idea-specific details, not boilerplate.** An idea combining multiple models must have coherent interface and ownership between them. Architecture here means the *structure of how the project is built and operated*, not necessarily computer code.

### A. Books, novels, nonfiction, comics, scripts and other written works

Provide a substantial **writing and publishing production bible**, not merely “write the book.” Include where relevant:

1. Core premise, genre/subgenre, intended readers, emotional promise, original hooks, themes, tone, point of view, tense, content boundaries and comparable-reader expectations.
2. Protect **all explicitly supplied plot events and ending**. Create a continuity map linking the user's source details to planned scenes and character changes; do not lose or silently contradict them.
3. Logline, synopsis, back-cover pitch, detailed beginning/middle/end narrative architecture, inciting event, escalating conflict, midpoint, reversals, climax, resolution and any intended series hooks.
4. Character bible: goals, needs, contradictions, flaws, arcs, relationships, voice signatures, motivations, secrets, timeline, physical/setting continuity and explicit don't-change rules.
5. World/location/research bible: chronology, rules, geography, institutions, technology/magic if applicable, era detail, credible motivations, recurring symbolism and consistency checks.
6. **Chapter-by-chapter and scene-by-scene outline** with scene goal, POV, location, time, inciting complication, key action/dialogue, turn, emotional beat, continuity inputs/outputs, chapter-end momentum and approximate word budget. Make it detailed enough that a writing agent does not improvise an incompatible plot.
7. A style guide with positive and negative examples of **original, non-copyright-infringing prose qualities**, dialogue, rhythm, imagery, humor and vocabulary. If owner supplies samples, anchor to those, not an invented preference; do not imitate living authors' distinctive expression.
8. Drafting workflow: chapter order, context packets, how to carry forward continuity, how to mark research gaps, revision passes (structural, character, prose, line/copyedit), fact-checking, sensitivity/context review where relevant and human judgment at quality gates.
9. Editorial QA: contradictions, chronological impossibilities, unresolved subplots, accidental repetition, name/age changes, inconsistent POV/tense, plagiarism/derivative resemblance, bad pacing, formatting and accessibility. Include concrete review checklists and stop/go criteria.
10. Production files and formats: canonical manuscript source, style sheet, chapter metadata, front/back matter, table of contents, ebook EPUB accessibility, print-ready PDF, cover artwork briefing, dimensions/bleed dependent on exact platform requirements, proof copies if needed, typography, ISBN/imprint decisions and metadata. Do not invent ISBNs or asset licenses.
11. Original cover concept, typography/composition, spine/back-cover rules, author bio (placeholder until true), description, keywords, categories, sample excerpt, series information, price hypotheses and edition-specific packaging.
12. Platform-by-platform plan for **all meaningfully suitable** channels: direct sales, Amazon KDP, Kobo Writing Life, Apple Books, Google Play Books, Barnes & Noble Press, Draft2Digital and/or other relevant ebook, print, audiobook and library distribution options *after fresh eligibility/format/rights/fee checks*. Evaluate overlapping aggregators, duplicate distribution, print-on-demand integration and region rights.
13. Specifically check **exclusivity conflicts** (e.g. KDP Select ebook exclusivity if relevant), country-specific distribution, ISBN ownership, revenue-sharing, AI-generated content disclosure, audiobook narration rights and retailer content policies. Never promise simultaneous wide publication when exclusivity/rights prevent it.
14. For a series, plan continuity, catalog metadata and reuse **without falsely claiming other books already exist**. For nonfiction, replace fictional character/plot systems with research provenance, argument outline, source permissions and practical verification.
15. Release checklist, proofing, store-preview QA, metadata QA, staged launch, reader discovery, ongoing promotion and post-release iteration. Do not write a complete novel in this one planning run unless the idea is explicitly a very short deliverable; the project file must tell Codex how to write and publish it.

### B. Games, interactive experiences, simulations and virtual economies

Provide: original game design document; precise platforms, engine choice and version checks; player fantasy, target player and core loop; progression, economy/balance, win/fail, accessibility and pacing; complete level/quest/scene/content graph; narrative, characters and dialogue rules where relevant; art/audio/UI standards; animation and control specs; data, save/load and migrations; offline/network authority/anti-cheat if applicable; performance targets and benchmarks; modular repo tree, scenes/scripts/classes, API/events and algorithms; deterministic fixtures; difficult negative tests and softlock prevention; packaging, platform certification, age/content ratings where applicable, pricing and monetization ethics; store media, demos, patches and multi-store or multi-engine feasibility. Preserve the requested original mechanic/story and avoid replacing the game with a generic prototype.

### C. Software, developer tools, applications, SaaS, APIs, digital utilities, automations

Provide an implementation-grade specification:

1. Specific target workflows, buyer-facing outcomes, hard competitive differentiation and non-goals.
2. Stack, runtime/SDK/API versions only when verified, and rationale vs cheaper simpler alternatives.
3. A proposed **repository/project directory tree** with each important file/module's responsibilities and owner.
4. Component architecture, integration boundaries, state machines and data flow.
5. APIs/interfaces/events, request/response and error examples, persisted schemas, migration/versioning and configuration.
6. Hard algorithms with pseudocode, invariants, complexity and deterministic input→output test cases.
7. Security/auth, secrets, data retention, privacy, rate limits/abuse, dependency licenses and supply-chain risks.
8. User interface screens/states, keyboard/accessibility, failure recovery and installation.
9. Automated unit/integration/E2E/negative/regression/security/performance tests, real fixture strategy and credible benchmark environment.
10. Cross-platform builds, versioned adapters, compatibility matrix, packaging/CI, reproducible release steps, rollback, updates and user-facing docs.
11. Infrastructure/hosting, operational telemetry (with privacy controls), incident procedures, recurring cloud/API costs, fallback modes and support scope.
12. Commercial versus free differentiation and genuine support burden. Never claim a port works merely because the conceptual core is portable.

### D. Digital art, 3D assets, photos, video, audio, design templates and other creative deliverables

Provide: distinctive creative direction/mood boards described in text, audience/use case, exact assets and variants, style/quality bar, production pipeline, naming and folder rules, resolutions/poly/format or compression specs, licensed-source inventory, color/lighting/render/animation requirements, cross-app compatibility, sample scenes/previews/thumbnails, export and QA checks, accessibility/metadata, watermark/preview strategy without compromising purchases, licensing/redistribution rules and appropriate asset/media marketplaces. Distinguish meaningful creative work from trivial mass generation. Specify source/editable deliverables and packaged customer files.

### E. Content channels, social accounts, video/image publishing, newsletters and advertising

Provide: channel premise and distinct identity, audience segment and promise, original content pillars, realistic production cadence chosen by workload (not an extra setting), script/storyboard/story idea backlog with concrete examples, sourcing and copyright rights, audio/visual pipeline, title/thumbnail/hook metadata, distribution to relevant platforms and aspect ratios, formatting/adaptation rules, transparent disclosures, editorial/reputational checks, monetization eligibility and cash-flow reality (ads/sponsorships/affiliates/direct offers), follower/traffic and conversion assumptions, analytics/feedback loop, platform anti-spam and reuse policies, scheduling and fallback when algorithms change. Do not assume YouTube/TikTok creator payouts are available from Canada without verifying official current rules. No fake engagement, misleading automation or reuploads of others' work.

### F. Services, freelance offers, consulting, AI-assisted client deliverables and lead generation

Provide: concrete paid outcome, ideal buyer and purchase trigger, fixed or bounded scope, service packages and quote rules, customer acquisition through permission-compliant channels, listing/proposal/page copy, discovery/requirements intake **only when required to deliver the work**, contract/consent/scope/access checklist, client data security, repeatable standard operating procedure with step-by-step prompts/tools, automated draft production, independent QA/human review for high-stakes outputs, acceptance tests, handoff/aftercare, revisions/refunds, operational hours, client communications and limits. Do not require arbitrary prelaunch interviews or paid pilots. Do not fabricate client references, perform unauthorized outreach or expose confidential data.

### G. Dropshipping, ecommerce, print-on-demand, marketplaces and physical commerce

Provide: actual buyer and differentiated offer; product/SKU and supplier-search criteria; **legitimate sourcing** (not fake supplier relationships); supplier quality, shipping region, landed-cost/FX/taxes/duties, fulfillment times, inventory/samples if essential, return/warranty obligations, customer safety/regulatory review, brand and intellectual property rights, storefront/platform selection with Canadian eligibility, catalog listings/photos/variants, orders/returns/chargeback SOP, customer support, fraud/privacy, paid/organic marketing economics and cash exposure. Do not assume an inexpensive store subscription covers inventory, refunds, ads, shipping or customer support. Reject commodity products without a credible edge and pause where supplier access/pricing is unverified.

### H. Licensing, affiliate, digital information/data products and other intermediated models

Provide: exact licensed asset/data/traffic or referral source, provenance and legal rights; buyer or partner eligibility; contract and exclusivity, royalty/commission, payout delays/thresholds, account policies, ongoing tracking and recordkeeping, quality verification, delivery/update obligations, permitted marketing, compliance/disclosures and realistic volume thresholds. Affiliate systems need permission and truthful disclosure; data systems need lawful data sourcing, update mechanisms and privacy protection. No unapproved data scraping or invented partner deals.

### I. Investments, assets and capital-based opportunities

Provide: objective and strategy, actual capital needed at plausible yields, CAD denomination/FX assumptions, custody/broker platform eligibility and current fees, risk exposures, diversification/liquidity, taxes and reporting, drawdown scenarios, fees/slippage and legal constraints; distinguish dividends/interest/distributions, realized gains, unrealized price appreciation and principal. Compare with lower-risk alternatives and inflation/opportunity costs. No assumed profit, leverage-based shortcut, automated trades or promises of fixed monthly income. If adequate capital or authority does not exist, describe a research/monitoring project or return a no-go rather than invent an operational investment business. **The project plan is not an authorization to place orders or provide individualized investment guarantees.**

### J. Unlisted or hybrid project types

Identify its actual components and supply an equally rigorous end-to-end architecture/production/SOP/operating plan. Do not force it into a listed template. If the idea requires hardware, manufacturing, licensing, research and a hosted application together, define the interface and dependencies between all relevant components.

## 6. Publication/distribution: reach every genuinely suitable channel

**Goal:** Prepare the idea for distribution on **as many appropriate, lawful, economically viable platforms as possible**, not just the easiest single platform. Research the exact platform fit; a channel is appropriate only if its buyers, formats, content/product type, eligibility, payout model, rights and support burden fit the actual idea.

Produce a **destination-by-destination channel matrix** covering every relevant direct store, specialist marketplace, publisher, content network, app store, service platform, aggregator/distributor, print/audio channel, website/API route, licensee channel, or financial operating venue as appropriate. For every considered destination include:

- Official current platform name and policy/guide URL, verified access date; geographic eligibility including Canadian seller/account/payout access.
- Which exact **edition/SKU/format/service offer** qualifies for listing; required files, media, API integration or account type.
- Current fees/commission, likely payout currency, minimums/holds, refunds/taxes and cost implications; label unknown until verified.
- Rights, exclusivity, AI-content or automation disclosure, restrictions, quality standards, review/approval, prohibited categories and any relevant contract conflict.
- Product listing/search/discovery mechanics, audience fit, competitive density and realistic acquisition route.
- **Direct versus aggregator overlap** to prevent duplicate uploads, duplicate ISBN/listings, channel conflicts, competing prices and accidental exclusivity violations.
- Actual onboarding/submission steps, screenshots/metadata/cover/demo and other assets to prepare, owner steps for verification and expected review dependencies.
- Support/update/version and fulfillment overhead after publishing.
- Classification: **Launch wave 1 / Launch wave 2 / Conditional / Unsuitable**, with a specific reason; do not include a platform merely to increase the count.

**Launch order:** First prepare and launch the lowest-friction, best-fit, legitimate channels; then reuse the same validated core asset or compatible editions on additional suitable platforms, adapting metadata/packages. Do not assume a single upload fulfills every platform's rules. Provide a **release manifest** for all formats and channels, with canonical source, per-platform build/metadata, version, rights, price hypothesis and current publication status. Include cross-channel consistency and rollback/withdrawal instructions. Actual account logins, publisher terms, external submissions, fees, offers, or financial actions require separate approval and the necessary trusted tools.

For channels with exclusivity or rights conflicts, select a coherent **wide vs exclusive** strategy based on the actual idea and documented economics. Never promise “all platforms” where doing so would breach exclusivity or create duplicate/conflicting distribution.

**If the idea doesn't involve publishing** (e.g. a client service or investing), translate this requirement into **every suitable acquisition/distribution/operating channel**, and explain exactly why ordinary retail publishing does not apply.

## 7. Commercial plan and $150/month portfolio contribution

Create an actual business model for the idea where a saleable/monetizable model is appropriate. If the idea is fundamentally personal/artistic with uncertain economic value, keep the project honest about its role and propose only reasonable monetization options. Analyze:

1. Who pays (or how the operation earns), the precise value exchange, buyer triggers and free/AI/DIY alternatives.
2. Pricing strategy (one-time sale, subscription, service fee, usage, licensing, royalties, advertising, affiliate, investment cash flows or hybrid); regional/format/platform price harmonization, supported by transparent hypotheses rather than invented acceptance.
3. Full incremental cash envelope: tools, hosting, assets, licenses, marketplace/payments, samples, fulfillment, refunds, subscription commitments, tax/FX and support; **unknown costs are unknown** and block the relevant commitment.
4. Ongoing contribution: price – marketplace/payment commission – refund allowance – variable fulfillment – attributable recurring cash costs – acquisition costs; allocate shared fixed costs honestly, avoid double-counting revenue across parent and edition.
5. Owner labor and Codex work: research/creation, production, QA, marketing, support, updates, client communication and ongoing oversight; effective contribution per owner hour separately from cash contribution.
6. **Conservative, base-hypothesis and upside scenarios** with every assumed sale/customer/view/commission/conversion rate explicit. Reconcile mathematics with calculator tools if available; no fake forecasts or success percentages. Include zero-sales case and realistic downside.
7. Exact additional sales/units/clients/royalty streams/traffic needed for CAD20, CAD50 and/or the remaining **portfolio-wide CAD150/month** milestone, using genuine net contribution not gross. A one-time book or asset sale creates *nonrecurring transaction revenue*, even if new monthly sales later produce regular cash flow.
8. Break-even, cash-at-risk and post-launch stop/continue/iterate criteria; where capital is invested, classify assets and mark-to-market separately from operating expenses and do not confuse appreciation with predictable monthly income.
9. Canadian seller/publisher rules and tax/payout questions that need proper verification; do not invent legal conclusions or imply business registration/tax filing already done.
10. Optional advertising **defaults CAD0**. Include a paid strategy only as a future conditional proposal with verified cost economics and separate owner approval; prioritize free and owned-audience channels.

**Budget rule:** Use `min(BUDGET_CEILING_CAD, current enforceable repository limit)` for a new proposed project where such a limit exists. As of the last known code, `commercial_revision: 2` limits the `owner_budget.hard_ceiling` to CAD100, requires `owner_budget.currency: "CAD"`, rejects any positive unapproved spend, and assumes zero recurring owner cash commitments until a revised policy/approval. Never quietly exceed it. If this makes the business model infeasible, say so and offer an idea-faithful lower-cost implementation or no-go. `BUDGET_CEILING_CAD` is NOT spend authorization.

## 8. Detailed marketing and buyer/audience discovery package

Create **ready-to-use, idea-specific** materials sufficient to prepare a launch, while marking prospective material as drafts:

- Positioning: one-sentence outcome promise, differentiator, buyer/reader/player/audience segment and exact reason to purchase, read, play, watch or hire.
- Competition-aware title, subtitle, product/series name or service offer; distinguish brand ideas from checked trademark availability.
- For each relevant channel: optimized listing title and description, honest features/benefits, category and keyword shortlist, price hypothesis, language/format, relevant tags and screenshots/cover/demo requirements.
- Creative: cover and thumbnail art direction, original taglines, back-cover/blurb, trailer/demo storyboard, excerpt/sample plan, author/about copy requiring true owner facts, launch posts and platform-appropriate adaptations.
- Technical/service: demonstration scenario, before/after proof, reproducible tests and logs, docs/FAQ/support notes, service scope/specimen, compatibility matrix and comparison without disparagement.
- Discovery strategy: who searches for this, where they search, channel SEO/metadata, comparable communities, permission-respecting outreach only when authorized, owned-website alternatives, short-form/social cross-promotion and organic demonstration content.
- Practical **week-1 launch actions chosen by dependencies**, not a fictional calendar deadline; follow-up exposure tasks, measurable funnels and the data that would justify changes.
- Review requests must comply with platform policies; no fake testimonials, purchased followers/reviews, spam, misleading scarcity, copyrighted review/marketing assets or automated impersonation.

The final plan must identify how customers/audiences can **discover** the idea after publication; having a listing alone does not guarantee exposure or sales. Estimate marketing effort honestly; do not assume 'AI will make it viral'.

## 9. Implementation plan so Codex does minimal extra planning

Produce a **dependency-ordered, execution-ready plan** with clear units of work. Each substantial task should contain:

- **Task ID, concise goal, priority and dependency IDs**; flag critical path versus parallelizable work.
- Concrete **inputs** (idea section, legal/rights preflight, fixture/manuscript scenes, source requirements, verified assets) and tool/runtime assumptions.
- Proposed **files/folders/modules/artifacts**, using actual existing repo paths where known and clearly labeled proposed paths where not.
- Exact work instructions, algorithms/scene beats/SOP steps, required content, edge cases, design decisions and permitted reusable components.
- **Observable outputs** (source file, manuscript chapter, image asset, test report, build, listing draft, release manifest, supplier comparison, contract draft, etc.) and file/format standards.
- **Pass/fail acceptance criteria and tests**, including positive, negative and boundary cases; where creative quality is subjective, give concrete craft/revision rubrics and a human editorial check if truly necessary, without insisting on interviewing readers.
- Expected risks, alternative solution, failure recovery and whether any action can affect external systems or customer data.
- **Owner interaction level:** `automatic local`, `permitted connected tool`, `owner approval/access required`, or `unavailable/blocked`; no covert spending/publishing/trading.
- Bounded effort **estimate/range** as a planning hypothesis, plus expected maintenance. Do not invent actual elapsed times or tests.
- Definition of done and exact evidence to record in the canonical project checkpoint.

Define shared contracts and task ownership for parallel Codex workers; **avoid assigning multiple chats to edit the same file simultaneously**. Provide a critical path and recommended first parallel workstreams. Prefer reusable code/assets and reproducible pipelines without building unnecessary infrastructure.

Include a practical **creation-to-launch runbook**: repository setup → research/rights preflight → work generation/implementation → revision/testing → packaging/conversion → independent verification → marketing assets/listings → platform eligibility/owner approvals → staged submission/publication → post-launch tracking → maintenance or future editions. If the idea already includes completed materials, specify what to reuse rather than starting over.

Provide a **first-session Codex handoff** that tells a newly connected chat exactly which canonical project file to open, which files to inspect, which task to claim, which local tests or checks to run, which reports to update, and which external actions are *not* authorized. If full source/asset creation is a later stage, no files should be falsely marked as already existing in the research plan.

## 10. Quality gates, test evidence and stop conditions

Quality is business-model specific. Define **pre-release gates** that Codex can verify with synthetic fixtures, local builds, editorial reviews, permissions or legitimate production checks without requiring interviews:

- **Creative:** coherence, original expression, completeness, plot/character/time continuity, craft/style consistency, accessible formatting, factual checking where appropriate, rights-clear assets, accurate book/file metadata and actual preview rendering. A polished manuscript/asset is not guaranteed to become popular.
- **Software/games:** deterministic functionality, correct state transitions, no dead-ends/softlocks, failing tests for bad inputs, platform/version compatibility, security, installability, uninstall/rollback, no regressions, reproducible package and useful documentation.
- **Services:** repeatable and accurate delivery, scoped intake/handover, confidentiality, nontrivial outcome, quality controls and a real route to clients without fake credentials.
- **Commerce:** supplier and goods legality, shipping/returns, product quality, cost bounds, legal store policies, actual seller eligibility and accurate customer claims.
- **Investing:** auditable calculations, risk limits, compliance and no automatic speculative action.
- **Distribution:** each chosen channel's policy and file-format checklist, correct pricing/rights, metadata, accounts, payout setup, independent sample/preview and disclosure requirements.

Include **release-blocking failures**, nonblocking improvements, diagnostics and recovery. Never mark a task/test complete because its steps are written down. Do not mark platforms accepted or listings published until an actual result is observed.

Define **kill/pivot/iterate conditions** that respect the user's idea: abort a platform edition or a technical approach if costs/rights/compatibility fail; avoid dumping the whole creative concept because one store rejects it. After launch, measure actual sales/returns, qualified leads, download-to-purchase conversion where observable, support time and spend. Switch channels or improve presentation/quality when warranted; discontinue a loss-making process with real evidence, not made-up probabilities.

## 11. Repository record format and one-file import safeguards

The resulting **project Markdown** must follow the repository's **current** canonical schema as verified during execution, not a stale example. At the most recently examined revision:

- Canonical records reside under `business_portfolio/niches/**/projects/*.md`.
- Frontmatter starts with `---` on its own line, then a strict **JSON object** (not YAML), then `---` on its own line. Do not use comments, duplicate keys, trailing commas, NaN or Infinity in JSON.
- Required keys: `schema_version` (1), `id`, `title`, `niche_id`, `niche_path`, `record_type`, `origin`, `priority`, `work_state`, `commercial_validation`, `evidence_basis`, `source_ids`, `parent_project`, `related_projects`, `next_action`, `last_reviewed`, `execution_authorized`, `privacy`. Confirm whether the live repository has added requirements.
- Keep new plans `work_state: "planned"` (or a valid appropriate state) and `commercial_validation: "unvalidated"` unless there is independently verified contrary evidence. Use `execution_authorized: false`, `marketing_execution_authorized: false`, `actual_revenue: null`, `actual_profit: null`, `success_probability: "not_established"` and zero authorized spending absent real authority/evidence.
- `owner_budget` uses CAD, a hard ceiling no higher than the actual enforced policy, zero current spending, itemized optional estimated costs and **unknown costs clearly marked**. Add only numeric cost fields that are genuinely known/hypothesized and pass the current validator. New project IDs must match current regex and **not collide with active or archived IDs**.
- `source_ids` MUST reference IDs already present in `business_portfolio/research/SOURCE_REGISTER.json`. The browser builder rejects unknown/empty sources. Research new sources in the body, with full URLs, but do **not** fabricate source IDs. If no existing registered sources legitimately support the specific plan, deliver a **staged Markdown project** with a clearly labeled **IMPORT BLOCKED — SOURCE REGISTRATION REQUIRED** note and precise Codex pre-import instructions to register them under unique valid IDs. It is better to stage with incomplete source references than to fake compatibility. One-file output is unchanged; Codex can update the register later during the authorized import.
- Resolve current `NICHE.json` ID and path from actual files. If missing or unverified, stage the file and include the exact import decision and metadata changes required, rather than inventing IDs. Do not create duplicate niches for the same activity.
- A project already in the repo must preserve its stable ID and previous observed progress; the new document should be **merge-ready**, not a reset. Link related project IDs only if they exist as active records and the validator permits them. Retain the actual original concept in a source-of-truth section.
- Do not put sensitive customer data, private receipts, credentials, private financial or health details, actual client contacts, copyright-protected files lacking redistribution rights or unreviewed binaries in the public canonical Markdown/index. Do not declare `public_results` until such text files actually exist in the right location and have passed review.

### Suggested metadata fields (adapt to verified current schema)

Prepare the actual output using real values, not these illustrative placeholders:

```json
{
  "schema_version": 1,
  "id": "IDEA-001",
  "title": "Specific project title",
  "niche_id": "N-verified-niche-id",
  "niche_path": "verified/niche/path",
  "record_type": "product_family",
  "origin": "current_package",
  "priority": "P2",
  "work_state": "planned",
  "commercial_validation": "unvalidated",
  "evidence_basis": "idea_and_public_research_only",
  "source_ids": ["EXISTING-REGISTERED-SOURCE-ID"],
  "parent_project": null,
  "related_projects": [],
  "next_action": "Concrete, locally executable next action",
  "last_reviewed": "YYYY-MM-DD",
  "execution_authorized": false,
  "privacy": "public_planning_only",
  "actual_revenue": null,
  "actual_profit": null,
  "commercial_revision": 2,
  "marketing_execution_authorized": false,
  "production_budget_verified": false,
  "success_probability": "not_established",
  "marketing_lane": "organic_launch_preparation_only",
  "launch_gate": "independent_qa_and_platform_rights_preflight",
  "offer_price_cad_hypothesis": null,
  "owner_budget": {
    "currency": "CAD",
    "preferred_upfront": 0,
    "planned_upfront": 0,
    "authorized_spend": 0,
    "hard_ceiling": 100,
    "owner_recurring_monthly": 0,
    "budget_window": "Cumulative incremental owner cash exposure; no automatic reset",
    "includes": ["tax", "currency_conversion_cost", "noncancelable_commitments", "advertising", "hosting", "marketplace_fees"],
    "unknown_cost_action": "Pause and verify cost before any commitment",
    "production_runtime": "Not established; pending preflight",
    "budget_fit": "preflight_required",
    "optional_all_in_envelope": {},
    "optional_total_ceiling": 0
  }
}
```

**Important:** This is an illustration of the required shape, **not** a source of factual IDs, exact priorities, real dates, confirmed prices or status. Fill all fields with verified/current values for the real output, adjusting the `record_type` to the actual model. If any mandatory references remain unverified, explicitly make it a **staged/noncanonical** file and list the smallest repair tasks for Codex; do not claim `build_browser.py --check` passed when it was never executed.

### Required in-file sections

The single generated project file must contain, in this order unless the idea clearly warrants a better organization:

1. **Project decision and fidelity contract:** title, type, expected finished result, verdict, original `PROJECT_IDEA` preserved, must-keep vs adjustable elements, scope and assumptions.
2. **Repository baseline and duplicate/reuse findings:** inspected commit/path/date, niche, project ID and exact canonical candidate path, related work, existing assets, progress and limits.
3. **Audience/buyer/economic purpose:** exact user and outcome, original creative appeal or buyer job, constraints, ethical/legal boundaries.
4. **Focused research and sources:** competition/substitutes/AI/DIY, evidence ledger, current platform rules, truth-vs-assumption markers and red-team objections.
5. **Finished-project specification and design/production bible:** full architecture/creative bible/SOP/supply chain/investing framework or hybrid, with file tree and detailed contracts where applicable.
6. **Content and feature breakdown:** chapters/scenes/assets/modules/SKUs/services/dependencies, clear scope and complete first release.
7. **Distribution and platform matrix:** all appropriate destinations with edition/format, eligibility, fees, rights/exclusivity, reviews, metadata, relative priority and concrete publication/operation instructions.
8. **Revenue model, budget and milestone economics:** three scenarios plus zero-sales/downside, fee math, real recurring cash costs, owner effort, break-even and portfolio-target contribution.
9. **Marketing launch kit:** complete tailored copy, packaging/promotional asset briefs, organic discovery channels, platform keyword/tag/categorization research and measurement.
10. **Step-by-step implementation task table:** task IDs/dependencies, inputs, tools, exact artifacts/paths, detailed instructions, acceptance, tests, evidence, work ownership and owner permission checkpoints.
11. **Independent QA/verification matrix:** pass/fail and failure/boundary cases, technical or editorial test fixtures, release blockers and what remains uncertain until marketplace results.
12. **Release and multi-platform runbook:** staged execution per channel, cross-platform rights/conflict controls, versioned formats, submission checklist, rollout/withdrawal/update procedure.
13. **Post-launch operating playbook:** support, customer feedback, analytics, budget controls, maintenance, revision, follow-on editions and stop/change conditions.
14. **Risk, adversarial review and open questions:** real threats and alternative paths preserving the concept, constraints requiring user authorization.
15. **First-session Codex handoff:** exact next locally authorized steps, import source ID/register checks, duplicate/ID/path reconciliation, work ownership and release gates.
16. **Checkpoint and decision log:** only genuinely completed research, all unfinished work, external actions not_started/uncertain/confirmed, deliverables that actually exist, dated next action.

Make every section **concrete enough to act on**, not a restatement of generic best practices. For a large creative project, include a sufficiently detailed chapter/scene or asset/episode plan. For a multi-platform business, include per-platform packaging and submission requirements rather than “publish everywhere.” For technical work, include file/module API/algorithm/test details, not just features. A thorough project can be long; coherence, accuracy and low Codex decision burden are more important than arbitrary word counts.

## 12. Final independent red-team review

Before producing the final file, actively try to falsify your plan:

1. Did it change the owner's idea without permission or leave major given plot/feature requirements unplanned?
2. Is there a free/AI/DIY/incumbent alternative that makes the planned value trivial or redundant? For original creative work, is the result generic, derivative or lacking a distinct audience promise?
3. Is the chosen niche compatible with the *current* repo hierarchy and are project IDs/sources trustworthy?
4. Do rights, exclusivity, platform rules, AI-content disclosures, seller eligibility or payout restrictions make the proposed multi-platform launch impossible?
5. Are all formats/editions actually producible from the proposed source without fake cross-platform promises? Are additional platforms economically worthwhile?
6. Does the plan require interviews, surveys, paid pilots, unnecessary user questions or manually recruited teams that delay launch without necessity?
7. Could important safety, security, editorial, reliability, accessibility or QA defects reach buyers because the plan is overoptimized for speed?
8. Are time, labor, support, publishing approval, marketing/discoverability and costs understated? Is the CAD150 contribution based on transparent hypothetical math rather than invented sales?
9. Have any external or financial actions been mistaken for permission, or pre-existing accomplishments/receipts been invented?
10. Could a Codex chat execute the first meaningful task and follow the critical path **without rediscovering the product design, chapter plot, technical architecture, platform requirements or quality bar**?

Fix substantive gaps before delivering. If a blocker is unsolvable within the user's exact idea and available means, make an honest conditional/no-go report rather than fabricating a successful plan.

## 13. Output instructions — EXACTLY ONE Markdown file

1. Use available file-creation tools to write exactly **one new `.md` file** containing the complete planned project. Name it `<PROJECT-ID>-<concise-project-slug>.md` for a ready/staged plan, or `NO_GO_<idea-slug>.md` for a rejected concept. **Do not overwrite existing project IDs or files** without explicit owner-authorized merge logic; generating a project document in this chat is not direct repository mutation.
2. Use **strict JSON frontmatter** when producing a project plan, with the body sections above. For a no-go report, do not pretend it is an indexed project or populate invented frontmatter.
3. Validate UTF-8, frontmatter parser, required keys, duplicate-free unique ID where accessible, current niche ID/path where verified, source IDs where registered, markdown rendering, arithmetic and cited links. Mark unresolved import steps clearly.
4. Do not create other files even if the plan describes dozens of future manuscripts, code files, covers, distributions or tests. Those are **Codex's later implementation deliverables**, specified within the one project Markdown file.
5. Only link a sandbox download after confirming that **the exact file path exists** in the active execution environment. If no file-creation tool is available, provide the complete raw Markdown for manual saving and disclose that no downloadable file was created.
6. Final reply should be brief: project title, idea-faithfulness verdict, proposed first release and distribution strategy, important unresolved blockers and **one download link**.

**Begin using the `PROJECT_IDEA` and `BUDGET_CEILING_CAD` at the very top. Transform the supplied idea—not a newly invented substitute—into the most complete, high-quality, commercially sensible, platform-aware, implementation-ready single project file possible, without unnecessary human-interview delays or any unapproved external action.**
