> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.

# JDE data architecture — Part 3. JDE Supply Management (Procurement)

## Part 3. JDE Supply Management (Procurement)

Sources: Procurement Management, Subcontract Management, Requisition Self Service, Operational Sourcing, Buyer Workspace and Supplier Self Service.

### 3.1 How purchasing data hangs together

```
F43E01/F43E11 requisition (self service) ─┐
F4301 PO header ──< F4311 PO detail line ──< F43121 receiver (receipt + voucher records) ──> F0411 voucher ──> F0413/F0414 payment
        │                 │   └──< F43199 PO detail ledger (every status/change, commitments)
        │                 └──< F4316 multiple account distribution      └──> F4111 item ledger, F41021 on-hand, F0911 journal
        └── supplier F0401/F0101 (AN8)        item F4101/F4102 (ITM, MCU)        business unit / account F0006 / F0901
```

- **One set of order tables serves every purchasing document**: requisitions, quotes, blanket orders, purchase orders, subcontracts, transfer and direct-ship orders are all rows in F4301/F4311 distinguished by **order type** (`DCTO`). Subcontract Management uses the same tables with its own order type and adds logs, progress payments and retainage.
- **The order key** used everywhere: order number (`DOCO`) + order type (`DCTO`) + order company (`KCOO`), plus order suffix (`SFXO`) and line number (`LNID`) at line level.
- **Line type** (F40205 Line Type Control Constants) decides what a line touches: inventory interface `Y` (stock: updates inventory on receipt), `N` (non-inventory), `A` (account number – purchasing only; charged directly to a G/L account), `B` (non-stock with item edits and price lookup, G/L interface on), `D` (inventory item that does not affect availability), plus tax, freight, A/P and G/L interface flags and whether a receipt is required.
- **Order activity rules** (F40203) define, per order type + line type, the status sequence (`last status` → `next status`), the allowed alternate next statuses, and whether a row is written to the ledger F43199 at that step. Status codes are UDC 40/AT. Typical purchasing steps shown in the guides: 220 enter order → 230 approval → 280 print → 400 record receipt → 999 complete (sites differ; read F40203).

### 3.2 Core tables

| Table | Name | Grain / key (composite-key appendix) | What to use it for |
|---|---|---|---|
| F4301 | Purchase Order Header | order: `DOCO, DCTO, KCOO, SFXO`† (prefix `PH`†; the appendix prints the detail-file columns for this table) | supplier, ship-to, dates, payment terms, hold code, currency, order total, supplier classification codes |
| F4311 | Purchase Order Detail File | line: `PDDOCO, PDDCTO, PDKCOO, PDSFXO, PDLNID` | item or account, branch/plant, quantity ordered/open/received, unit and extended cost, amounts received/open, last and next status, line type, requested and promised dates, G/L class, subledger, related order references, freeze code (`UNCD`), configurator flag (`GBCFG`). `F4311T` is its tag table |
| F43121 | Purchase Order Receiver File | `PRMATC, PRDOCO, PRDCTO, PRKCOO, PRMCU, PRLNID, PRNLIN, PRDOC` | one row per **receipt** and per **voucher match** against a line, with open quantity and open amount to voucher. `F43121T` tag |
| F43199 | P.O. Detail Ledger File – Flexible Version | `OLDOCO, OLDCTO, OLKCOO, OLSFXO, OLLNID, OLNLIN, OLCORD, OLUPMJ, OLTDAY` | history of each line at the statuses flagged in activity rules, change orders, and the commitment audit trail (`PA`/`PU` ledger rows) |
| F4316 / F4316T | Purchase Order Multiple Account File | line × account distribution | split of one line across several accounts; copied to F43126 at receipt/voucher |
| F43126 / F43126T | Purchase Order Receiver Multiple Account | receiver × account | account distribution of receipts |
| F4317 / F43127 | Purchase Order Detail / Receiver Non-Billable | | non-billable portions |
| F4209 | Held Orders | order × hold code | holds and approval history |
| F43008 / F4318 / F43080 | Approval Levels / Approval-Rejection Reasons / Approvals Fields Constants | | approval routes by amount |
| F43090 | Supplier/Item Relationships | `PCAN8, PCMCU, PCITM` | supplier-item status, receipt route, price, and delivery/quality/cost performance updated from receipts |
| F43100 | Supplier and Branch/Plant Relationship | | |
| F41061 | Supplier Price/Catalog File | supplier × item × branch × date | contract/catalog unit costs |
| F43091 / F43092 / F43099 | Receipt Routing Master / PO Receipt Routing File / Receipt Routing Ledger | | routing operations (inspection, dock, in transit) and quantities at each step |
| F43093 / F43094 | Inspection-Sample Size / Supplier Item Additional Routes | | |
| F4330 / F4331 / F4332 | Supplier Selection (quotes) / Quantity Breaks / Multiple Requisition File | | quote responses; requisition-to-order consolidation |
| F4321 / F43211 / F43213 | Supplier Schedule Master / split percentages / SRS ship dates | | supplier release scheduling on blanket orders |
| F4340 / F4341 / F4342 / F4343 | Purchase Rebate Master / Threshold / Inclusion Rules / History | | rebate agreements and accruals |
| F4322 / F43221 | Purchasing Tolerance / Rounding Tolerance Rules | | receipt and voucher tolerances |
| F4303 / F4303M / F4304 / F4305 | Log Master / Log Models / Log Hierarchy Constants / Logs | | subcontract logs (insurance, submittals, transmittals) at contract, company, subcontractor, project, job level |
| F4355 | Subcontractor Threshold | | |
| F4320 | Purchase Order Clauses | | |
| F4314 | Sales Order/Purchasing Text Detail Lines | | text lines |
| F4371 | Suggested Reorder Stock Items | | output of the reorder-point generator |
| F43147, F4314Z, F43800, F43146T | Freight distribution, voucher match selection, summary voucher match, voucher match multiple account tag | | voucher-match work/support tables |
| F0411Z1 / F0411Z1T | Voucher Transactions – Batch Upload / Voucher Match Automation tag | | supplier invoices staged for **voucher match automation** (process type 1 = invoice awaiting match, 2 = logged voucher exists, 4 = processed records eligible for purge) |
| F4301Z, F4311Z, F43121Z, F43092Z | work files | | order generation and receipt work files |
| F4301Z1, F4311Z1, F43121Z1, F43092Z1 | Unedited transaction tables | | outbound interoperability |

### 3.3 Codes that drive analysis

- **Order types (UDC 00/DT)** named in the guides: `OP` purchase order · `OR` requisition · `OB` blanket order · `OQ` quote† · `OT` transfer order (purchase side; sales side is `ST`) · `OD` direct ship† · `OS` subcontract†. Blanket/quote types are also flagged in UDC 40/BT; commitment-eligible types in UDC 40/CT.
- **Status**: `LTTR` last status and `NXTR` next status on each F4311 line; `999` = closed/complete. A line is open while next status < 999 and open quantity/amount remain.
- **Receiver match type** (`MATC`) in F43121: `1` = receipt record (not yet vouchered / open to voucher), `2` = record created by voucher match, `3` = reversed by voucher match, `4` = another reversal-type record†. Filter on match type before summing, or receipts and vouchers double count.
- **Voucher match method**: *three-way* (order – receipt – invoice; formal receiving, voucher created from F43121 receipt rows) or *two-way* (order – invoice; no receipt rows, voucher created from F4311 lines; used for services, progress payments, subcontracts). Whether a line needs a receipt comes from its line type.
- **Hold codes** UDC 42/HC; landed cost components 40/CA and rules 41/P5; receipt routing codes 43/RC, movement 43/MC; rebate status/type 43/RS, 43/RT; log types 43/OL, 43/ML.

### 3.4 Process → tables

| Step | Program | Writes |
|---|---|---|
| Requisition (self service) | P43E10 and workflow | F43E01 header, F43E11 detail, F43E16 accounts; approval authority F43E091–F43E095; shopping cart F43E20; on generation creates F4301/F4311 |
| Order entry / blanket release / generation | P4310, P43060, R437002, MRP messages | F4301, F4311 (+F4316 accounts), F43199 where flagged; **commitment** in F0902 `PA`/`PU` ledgers for document types in 40/CT and line types with inventory interface A, B or C |
| Approval | P43081 | F4209, status advance |
| Receipt | P4312 | F43121 receipt row (match type 1); F41021 on-hand and commitments; F4111 item ledger (document type `OV`); F0911 inventory / received-not-vouchered entries (DMAAI 4310/4320); F4105 for average cost; landed cost rows (DMAAI 4385/4390); F43090 supplier performance |
| Receipt routing | P43250 | F43092 current step, F43099 history; quantities in transit / inspection in F41021 |
| Voucher match | P4314 / P0411, VMA batch | F0411 voucher (`PV`), F0911, F43121 voucher row (match type 2), F4311 open amounts; variances by DMAAI 4330/4340; relieves commitment if not relieved at receipt |
| Payment | A/P | F0413/F0414 |
| Progress payments (subcontract) | P4314 | two-way match with retainage held on the voucher pay item (pay status `R`) and later released |
| Encumbrance rollover / change orders | | F43199 rows by change order number, F0902 `PA`/`PU` |

All `PA`/`PU` ledger entries are based on F4311 and audited in F43199; they can be rebuilt from F4311 and reposted (R00932) if F0902 commitments drift.

### 3.5 Related sub-systems

- **Requisition Self Service (43E)**: F43E01 Requisition Order Header (`DOCO, DCTO, KCOO`), F43E11 Requisition Detail (`+SFXO, LNID`), F43E16 multiple accounts, F43E20 Shopping Cart Detail (`USER, LNID`), F43E20WF work file, F43E15 shopping cart cross reference, F43E22/F43E25 Direct Connect setup, F43E091–F43E095 approval authority (employee, group/BU, BU, constants, commodity/BU), F43E280 Delegation Master; commodity structure F40241 UNSPSC codes, F40242, F40243, F40500, F40510, F40520, F40530, F40540, F40551.
- **Operational Sourcing (43Q)**: F43Q10 Event Header (`EVNU, DCTO, KCOO`), F43Q11 Event Detail (`+EVLN`), F43Q15 currencies, F43Q20/F43Q201/F43Q21/F43Q211 bid questions, F43Q213 price breaks, F43Q30 Event Invited Bidders, F43Q40 Response Header (`+BIDNUM, AN8`), F43Q41 Response Line, F43Q401–F43Q413 response question detail, F43Q51 Analyze Event Detail (awards), F43Q60–F43Q62 bid question templates, F43Q90 constants, F43Q91 Bidder Registration, F43Q911 bidder VAT, F43Q92 ad hoc items.
- **Supplier Self Service / Buyer Workspace (43S, 43BW)**: read mostly F4301/F4311/F43121/F43092/F0411; own tables F43S001 Alerts Master, F43S002 Alerts Configuration, F43S003W work file; KPI formats in F5193.
- **Subcontract Management (44)**: F4301/F4311/F43121/F43199 with subcontract order type; logs F4303/F4305; F52034 contract header log text; thresholds F4355; commitments in F0902 `PA`/`PU`.

### 3.6 Analysis recipes

- **Open purchase orders**: F4311 with next status < 999 and open quantity (`UOPN`) or open amount ≠ 0; join F4301 for supplier/buyer/dates, F0101 for names, F4101 for item descriptions. Exclude requisitions, quotes and blankets by order type unless wanted.
- **Received not vouchered (accrual)**: F43121 match type 1 rows with open quantity/amount ≠ 0; reconcile to the G/L account from DMAAI 4320.
- **Spend analysis**: for invoiced spend use F0411 (vouchers) joined back by purchase order reference; for committed spend use F4311 extended amounts; for account-level view use F4316/F43126 or F0911.
- **Supplier delivery performance**: compare F43121 receipt date with F4311 promised date; or read the pre-computed F43090.
- **Order history / who changed what**: F43199 ordered by update date/time for the order line; change orders by change-order number.
- **Budget vs commitment vs actual** for a job or account: F0902 ledgers `BA`/`JA` (budget), `PA` (commitments), `AA` (actual).
- **Three-way match exceptions**: F0411Z1/F0411Z1T rows left at process type 1.

### 3.7 Supply Management tables named in the guides, by guide

- **Procurement Management**: F4009 Distribution/Manufacturing Constants, F4015 Order Templates, F4016 Print Messages, F40203, F40205, F4090/F4095 Distribution/Manufacturing AAI record types and values, F41061, F4209, F43001 Procurement Self-Service Transaction Log, F43008, F4301 (+Z, Z1), F4303, F4303M, F4304, F4305, F43080, F43090, F43091, F43092 (+Z, Z1), F43093, F43094, F43099, F43100, F4311 (+T, Z, Z1), F43121 (+T, Z, Z1), F43126 (+T), F43127, F4314, F43146T, F43147, F4314Z, F4316 (+M model, T), F4317, F4318, F43199, F4320, F4321, F43211, F43213, F4322, F43221, F4330, F4331, F4332, F4333WF, F4340–F4343, F4350/F4351 Supplier Page Hyperlinks, F4355, F43632Z, F4371, F43800, F43061W Supplier Catalog Work File, F0411Z1, F0411Z1T, F43C01 Contract Header (grower contracts).
- **Subcontract Management**: F4301, F4311, F43121, F43199, F4303, F4304, F4305, F4355, F52034.
- **Requisition Self Service**: F43E01, F43E11, F43E121, F43E15, F43E16, F43E20, F43E20WF, F43E22, F43E25, F43E091–F43E095, F43E280, F40241–F40243, F40500, F40510, F40520, F40530, F40540, F40551.
- **Operational Sourcing**: F43Q10, F43Q11, F43Q15, F43Q20, F43Q201, F43Q21, F43Q211, F43Q212, F43Q213, F43Q30, F43Q35, F43Q40, F43Q401–F43Q405, F43Q41, F43Q411–F43Q413, F43Q50, F43Q51, F43Q60–F43Q62, F43Q90, F43Q91, F43Q911, F43Q92.
- **Buyer Workspace / Supplier Self Service**: F43S001, F43S002, F43S003W, F5193.
