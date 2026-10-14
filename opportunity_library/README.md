# Organized Opportunity Library

**Primary entry point:** open [`../Opportunity_Library.html`](../Opportunity_Library.html).

36 categories · 144 subcategories · 1,512 research records · 69 current primary references.

There are 1,296 preserved records plus 216 new hypotheses. Two are separate personal-capital research notes, not businesses. Every idea has one primary category plus industry and mechanism tags. None has independently verified paid demand in this dataset.

## Find things quickly

| Need | Location |
|---|---|
| Browse / filter / compare / save IDs / export a draft | [Offline browser](../Opportunity_Library.html) |
| Understand scores, missing data and limitations | [Methodology](docs/METHODOLOGY.md) |
| Identity, AI content and platform constraints | [Privacy and platform matrix](docs/PRIVACY_AND_PLATFORMS.md) |
| Facts and primary links | [69-source register](docs/SOURCES.md) |
| Go from research to a paid test | [Operating workflow](docs/OPERATING_WORKFLOW.md) |
| Programmatic catalogue | [JSON](data/catalog.json) / [CSV](data/catalog.csv) |
| Edit category and subcategory assignments | [Taxonomy](data/taxonomy.json) / [classifications](data/classifications.json) |
| Edit new hypotheses | [Curated additions](data/curated_additions.json) |
| Industry facet / coverage audit | [Industry index](data/industry_index.json) / [coverage](data/coverage.json) |

## Categories

| Category | Subcategories | Records |
|---|---:|---:|
| [C01 · AI Content Systems](categories/ai-content-systems/README.md) | 4 | 6 |
| [C02 · Video & Creator Media](categories/video-and-creator-media/README.md) | 4 | 22 |
| [C03 · Audio, Music & Voice](categories/audio-music-and-voice/README.md) | 4 | 25 |
| [C04 · Writing, Publishing & Newsletters](categories/writing-publishing-and-newsletters/README.md) | 4 | 19 |
| [C05 · SEO & Search-led Websites](categories/seo-and-search-led-websites/README.md) | 4 | 26 |
| [C06 · Advertising & Marketing Analytics](categories/advertising-and-marketing-analytics/README.md) | 4 | 24 |
| [C07 · Email, CRM & Sales Enablement](categories/email-crm-and-sales-enablement/README.md) | 4 | 24 |
| [C08 · Social, Community & Memberships](categories/social-community-and-memberships/README.md) | 4 | 10 |
| [C09 · Digital Templates & Printables](categories/digital-templates-and-printables/README.md) | 4 | 13 |
| [C10 · Graphic Design & Brand Assets](categories/graphic-design-and-brand-assets/README.md) | 4 | 52 |
| [C11 · 3D, CAD & Digital Fabrication](categories/3d-cad-and-digital-fabrication/README.md) | 4 | 23 |
| [C12 · Games & Interactive Entertainment](categories/games-and-interactive-entertainment/README.md) | 4 | 21 |
| [C13 · Education & Training](categories/education-and-training/README.md) | 4 | 57 |
| [C14 · Websites & Storefront Design](categories/websites-and-storefront-design/README.md) | 4 | 6 |
| [C15 · SaaS & Business Applications](categories/saas-and-business-applications/README.md) | 4 | 60 |
| [C16 · Desktop & Mobile Utilities](categories/desktop-and-mobile-utilities/README.md) | 4 | 13 |
| [C17 · Plugins, Extensions & Connectors](categories/plugins-extensions-and-connectors/README.md) | 4 | 54 |
| [C18 · Developer, DevOps & Testing](categories/developer-devops-and-testing/README.md) | 4 | 23 |
| [C19 · APIs & Data Infrastructure](categories/apis-and-data-infrastructure/README.md) | 4 | 18 |
| [C20 · Analytics, Reporting & Spreadsheets](categories/analytics-reporting-and-spreadsheets/README.md) | 4 | 152 |
| [C21 · Documents, Extraction & Workflow Automation](categories/documents-extraction-and-workflow-automation/README.md) | 4 | 37 |
| [C22 · Ecommerce Product Operations](categories/ecommerce-product-operations/README.md) | 4 | 51 |
| [C23 · Print-on-demand & Physical Fulfillment](categories/print-on-demand-and-physical-fulfillment/README.md) | 4 | 12 |
| [C24 · Directories, Jobs & Marketplaces](categories/directories-jobs-and-marketplaces/README.md) | 4 | 38 |
| [C25 · Research, Datasets & Information Products](categories/research-datasets-and-information-products/README.md) | 4 | 128 |
| [C26 · Finance & Bookkeeping Operations](categories/finance-and-bookkeeping-operations/README.md) | 4 | 60 |
| [C27 · Stocks, Investing & Market Tools](categories/stocks-investing-and-market-tools/README.md) | 4 | 6 |
| [C28 · Privacy, Security & Compliance Tools](categories/privacy-security-and-compliance-tools/README.md) | 4 | 29 |
| [C29 · Localization & Accessibility](categories/localization-and-accessibility/README.md) | 4 | 48 |
| [C30 · Property, Construction & Home Services](categories/property-construction-and-home-services/README.md) | 4 | 122 |
| [C31 · Logistics, Manufacturing & Supply Chains](categories/logistics-manufacturing-and-supply-chains/README.md) | 4 | 101 |
| [C32 · Food, Hospitality & Travel](categories/food-hospitality-and-travel/README.md) | 4 | 58 |
| [C33 · Health & Wellness Administration](categories/health-and-wellness-administration/README.md) | 4 | 62 |
| [C34 · People, HR & Recruitment](categories/people-hr-and-recruitment/README.md) | 4 | 25 |
| [C35 · Agriculture, Environment & Energy](categories/agriculture-environment-and-energy/README.md) | 4 | 29 |
| [C36 · Nonprofits, Events & Public Services](categories/nonprofits-events-and-public-services/README.md) | 4 | 58 |

## Existing tools remain intact

The original `research_merge/` files, the large master plan, legacy reports and financial models remain in place. The factory reads the optional expanded CSV while the original Phase-0 command can still use its old index. FAST-O01 remains the reporting offer; existing generated customer/first-sales packs are not overwritten. VaultDesk is unrelated and unchanged.

The browser stores only selected IDs in local browser storage. It does not encrypt customer data and must never be used as a credential vault. There are no network clients, live accounts, trades, payments or messages in this library.

## Rebuild and test

```powershell
python -m opportunity_library.build
python -m opportunity_library.build --check
python -m unittest discover -s opportunity_library/tests -v
python -m opportunity_library.cli search --category C01 --limit 6
python -m opportunity_library.cli show CUR-01-01
```

Generated category pages are views of source data, not files to hand-edit. New evidence requires a reviewed source entry; rebuilding never verifies current demand.
