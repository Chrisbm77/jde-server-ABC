# JDE knowledge topics served by this API

Fetch any topic with `get_jde_reference(topic=...)`. Fetch only what the question needs; each topic is a focused document.

## How to choose

- **Any data/SQL question:** `da-0-rules` first, then the module part (`da-2-financials`, `da-3-procurement`, `da-4-supply-chain`, ...), and `bd-query-method` when you must discover columns.
- **Sales / revenue / account balance / trial balance questions:** `da-2-financials` and `bd-gl-balances`.
- **How a JDE process works or how to configure it:** `ba-guide`, then the matching `ba-<module>` topic.
- **JDE object development (tables, business views, data structures, event rules, PAR files):** `core-rules` first, then the development topics.


## Data architecture (tables, keys, joins, codes)

- `da-0-rules` - READ FIRST for any data question: naming of tables/columns, Julian dates, implied decimals, UDCs, keys, process map (order-to-cash, procure-to-pay), query checklist
- `da-1-foundation` - Foundation: system codes, Address Book (F0101 etc.), UDCs, shared tables
- `da-2-financials` - Financials: chart of accounts, F0911/F0902, A/P (F0411), A/R (F03B11), fixed assets, AAIs, recipes
- `da-3-procurement` - Procurement: requisitions, purchase orders (F4311), receipts (F43121), vouchers, recipes
- `da-4-supply-chain` - Supply chain: item master/stock (F4101/F41021), sales order to cash (F4211/F42119), logistics, manufacturing, recipes
- `da-5-crm` - CRM and service: cases, contracts, sales pipeline tables
- `da-6-asset-realestate` - Asset lifecycle: equipment, maintenance work orders, rental, REAL ESTATE (system 15 lease/billing tables)
- `da-7-health-apparel` - Health and safety incident tables, apparel, and the list of public documentation sources

## Querying and general ledger

- `bd-query-method` - How to discover real columns/tables with F9860/F98711/F9202 in T-SQL, mapping a new module, known gaps, paging results
- `bd-gl-balances` - General ledger balances and trial balance: F0902/F0901 columns, scaling, grain, T-SQL templates, mandatory verification

## Business advisor (how JDE modules work)

- `ba-financials` - Financials: A/P, A/R, G/L, fixed assets, cost accounting, multicurrency, tax — Oracle guide index and summaries
- `ba-supply-management` - Procurement: purchase orders, receipts, vouchers/three-way match, subcontracts, requisitions, sourcing
- `ba-supply-chain-manufacturing` - Inventory, sales orders, transportation, warehouse, shop floor, MRP, product data/costing, quality, forecasting
- `ba-asset-lifecycle` - Equipment, maintenance, rental, real estate management, work orders
- `ba-customer-relationship` - Pricing, CRM sales/support, service management, customer self service
- `ba-human-capital` - HR, payroll, benefits, time and labor, year-end
- `ba-project-management` - Job cost, contract and service billing, change management, homebuilder
- `ba-health-safety-environment` - Health and safety incident management, environmental accounting
- `ba-localizations` - Country-specific tax/regulatory guides (pattern only)
- `ba-cross-product-tools` - Address Book, Foundation, Orchestrator, UDOs, notifications, One View, batch versions, BI Publisher
- `ba-cross-cutting-concepts` - AAIs, UDCs, next numbers, country-server mechanism, business unit and chart-of-accounts structure
- `ba-guide` - Business advisor workflow and quick lookup: which module reference answers a functional JDE question

## JDE development

- `core-rules` (fetch first), `master-reference`, `par-file-structure`, `table-design`, `business-view-design`, `data-dictionary`, `data-structure-design`, `event-rules`, `form-design-aid`, `report-design-aid`, `application-design`, `business-function-programming`, `development-tools-overview`
