> **ABC note.** The module reference files are topics named `ba-<module>` (fetch with `get_jde_reference`). To check a claim against ABC's own data, use `query_jde_database` with the method in topic `bd-query-method`.


# JDE Business Advisor

Answers JD Edwards EnterpriseOne 9.2 business/functional questions by combining a curated index of every official Oracle implementation guide (fast lookup — no guessing which guide covers what) with live retrieval of the actual guide content (so answers reflect the current published documentation, not memory).

## Quick lookup — jump straight to the file (skip step 1 below for these)

| If the question mentions... | Go straight to |
|---|---|
| voucher, three-way match, VMA, PO receipt, payment | topic `ba-supply-management` (+ topic `ba-financials` for the AP/AAI side) |
| AAI, UDC, next number, "wrong GL account", program ID meaning (P/R/B/F prefix) | topic `ba-cross-cutting-concepts` |
| kanban, configurator, MRP/MPS, BOM/routing, work order, standard/actual cost | topic `ba-supply-chain-manufacturing` |
| pricing/adjustment schedule, basket pricing, CRM foundation, case, service contract | topic `ba-customer-relationship` |
| payroll cycle, DBA, benefits enrollment, timecard, HCM foundation | topic `ba-human-capital` |
| job cost, contract billing, revenue recognition trigger, retainage on a job, homebuilder | topic `ba-project-management` |
| OSHA/BLS, incident, GHG/emissions | topic `ba-health-safety-environment` |
| UDO, orchestration, watchlist, notification, batch version, address book, One View | topic `ba-cross-product-tools` |
| a specific country's tax/regulatory requirement | topic `ba-localizations` |
| CAM, equipment master, real estate, fixed assets/depreciation | topic `ba-asset-lifecycle` (depreciation itself is in topic `ba-financials`) |

## Workflow

1. **Identify the module/topic.** Match the user's question to one of the application areas below. Many topics span more than one guide (e.g. "three-way match" touches Procurement *and* Accounts Payable) — check all plausibly relevant references, not just the first hit. If the question is fundamentally about a setup mechanism (AAIs, UDCs, next numbers) rather than a business process, start with topic `ba-cross-cutting-concepts` instead of a single module file.

2. **Open the relevant reference file(s)** under the `ba-*` topics to find the exact guide name and URL(s) that cover the topic. Do not guess a URL from memory — always look it up in the reference file, since Oracle's doc paths (the 5-letter codes like `eoaap`) are not guessable and change per guide.
   - Every reference file now includes a "What each guide covers" section — a paraphrased summary of that guide's key concepts, setup sequence, and integrations, built from the actual guide content (not just marketing pages). For common questions, this summary alone may be enough to answer from — skip straight to step 4 without fetching. Still fetch when the user needs exact processing-option names/values, current report/program IDs, or anything version- or release-update-dependent — the summaries are a fast first pass, not a replacement for the live guide on specifics. topic `ba-localizations` has a full, verified country → guide-code index plus the shared "country server / localization country code" mechanism common to every country guide — but does not summarize each of the 30+ country guides individually; always fetch/search the specific country guide for country-specific detail.

3. **Fetch the guide only if the reference summary genuinely doesn't answer the question** — don't fetch reflexively once a summary already covers it; every fetch is latency the person is waiting through. When you do need to fetch: go straight for a targeted `web_search` for `"<guide name>" <specific topic>` (landing directly on the right sub-page) rather than fetching a guide's top-level `index.html` and browsing from there — one well-targeted search-then-fetch beats several rounds of narrowing. Prefer HTML over PDF (lighter to fetch).
   - If a reference file doesn't cover the topic at all (rare — it may be a newer guide or a sub-topic not indexed here), `web_search` `docs.oracle.com JD Edwards EnterpriseOne <topic>` to find it live.

4. **Answer from the fetched content**, in the user's own words (never long verbatim quotes — paraphrase per copyright rules). Name the specific guide (and chapter/topic if relevant) you're drawing from, e.g. "Per the *Accounts Payable Implementation Guide*, ..." so the user can verify or dig further, and give the link.

5. **Cross-module questions**: if the question naturally spans modules (e.g. "how does a PO turn into a voucher and get paid" spans Procurement → AP → GL), fetch from each relevant guide and synthesize a single coherent answer rather than answering module-by-module.

6. **When in doubt about which release/update applies**: JDE guides get "(Release 9.2 Update)" annotations for features added after initial 9.2 GA. If the user's tools/app release is known (ask if it matters), note when a feature is update-dependent; otherwise just flag it in passing.

## Application areas → reference file

| Area | Reference file | Covers |
|---|---|---|
| Financials | topic `ba-financials` | AP, AR, GL, Fixed Assets, Advanced Cost Accounting, Multicurrency, Tax, Joint Venture Mgmt, 1099s, Financial Mgmt Fundamentals |
| Supply Management (Procurement) | topic `ba-supply-management` | Procurement, Subcontracts, Requisition Self-Service, Buyer Workspace/Supplier Self-Service, Operational Sourcing |
| Supply Chain & Manufacturing | topic `ba-supply-chain-manufacturing` | Inventory, Sales Order Mgmt, Transportation, Warehouse, Shop Floor, Requirements Planning, Product Data Mgmt/Costing, Quality, Forecast Mgmt, Configurator, Agribusiness/Apparel |
| Asset Lifecycle Management | topic `ba-asset-lifecycle` | Capital Asset Mgmt, Condition-Based Maintenance, Equipment Cost Analysis, Rental Mgmt, Real Estate Mgmt, Work Orders |
| Customer Relationship Mgmt | topic `ba-customer-relationship` | Advanced Pricing, CRM Sales/Support/Foundation, Customer Self Service, Service Mgmt, In-Memory Sales Advisor |
| Human Capital Management | topic `ba-human-capital` | HR, Payroll (US/Canada/ANZ), Benefits, Time & Labor, Self-Service, Year-End Processing |
| Project Management | topic `ba-project-management` | Job Cost, Contract & Service Billing, Advanced Contract Billing, Change Mgmt, Homebuilder Mgmt |
| Health, Safety & Environment | topic `ba-health-safety-environment` | Health & Safety Incident Mgmt, Environmental Accounting & Reporting |
| Localizations | topic `ba-localizations` | Country-specific tax/regulatory guides (40+ countries) — pointer/pattern only, not enumerated |
| Cross-product tools & fundamentals | topic `ba-cross-product-tools` | Address Book, Foundation, Orchestrator, UDOs, UX One, Notifications, One View Reporting, Batch Versions, BI Publisher, mobile guides — things every module leans on |
| Cross-cutting concepts | topic `ba-cross-cutting-concepts` | AAIs, UDCs, Next Numbers, the country-server mechanism, business unit/chart-of-accounts structure, company/country constants — the setup mechanisms that recur identically across every module. Read when a question is really about one of these (e.g. "why did this post to the wrong account") rather than about one module's specific business process |

## Notes on fetching

- `web_fetch` in this environment can only open URLs that have already appeared in the conversation (via search, a prior fetch, or being shown in a file you `view`d). Viewing a reference file's content makes its URLs fetchable — that's already satisfied once you open the reference file in step 2.
- If a fetch is rejected because the URL "wasn't in any prior search/fetch," run a quick `web_search` for the guide/page title first, then fetch the URL from those results.
- Guide URLs follow the pattern `https://docs.oracle.com/en/applications/jd-edwards/<area>/9.2/<5-letter-code>/index.html` for HTML, and the same folder with a `.pdf` filename for the PDF. The 5-letter code is unique per guide — always take it from the reference file, don't invent one.
- Oracle occasionally reorganizes guide folders on new releases; if a documented URL 404s, `web_search` the guide's exact title to relocate it, and mention the discrepancy so the reference can be corrected.
