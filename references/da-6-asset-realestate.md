> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.

# JDE data architecture — Part 6. JDE Asset Lifecycle Management

## Part 6. JDE Asset Lifecycle Management

Sources: Capital Asset Management (CAM), Work Orders, Condition-Based Maintenance, Equipment Cost Analysis, Resource Assignments, Rental Management, Real Estate Management, Enhanced Real Estate Management for the United Kingdom and China, Advanced Real Estate Forecasting. (Fixed-asset accounting tables are in Part 2.7.)

### 6.1 Equipment and maintenance (systems 12, 13, 48)

```
F1201 Asset/Equipment Master ─┬─ F1217 Equipment Master Extension (service/CAM attributes, product model/family)
        │ (parent → child)    ├─ F1204 Location Tracking (current / planned / history)      ├─ F1307 Status History
        │                     ├─ F1207 Maintenance Schedule (PM by service type) ──> F4801 Work Order ──< F3111 parts, F3112 labor
        │                     └─ F1202 Asset Account Balances (cost, depreciation, meters by account/ledger/year)
        └── costs: any F0911 line with the asset ID or with subledger type W (work order) / E (equipment)
```

**Primary tables (as the CAM guide classifies them)**

| Table | Name | What it holds |
|---|---|---|
| F1201 | Asset Master File (prefix `FA`) | one row per piece of equipment: equipment (asset) number, description, account coding (company, responsible business unit, cost account), category codes, parent, status. Every asset has an asset number; unit number and serial number are alternate identifiers |
| F1217 | Equipment Master Extension | additional CAM/Service Management data per equipment (product model and family, customer/site, extra category codes, meter-schedule flags) |
| F1202 | Asset Account Balances File (prefix `FL`) | balance amount **or units** per equipment account, ledger type and fiscal year |
| F1204 | Location Tracking Table | key `FMNUMB, FMEFTB, FMAL, FMNNBR`: equipment number, location, start/end dates, status, transfer number, location code (planned, current, history) |
| F1207 | Maintenance Schedule File | one row per equipment × service type × occurrence, current and history: when due (date, meter, interval), last completed, maintenance status (UDC 12/MS; 98 cancelled, 99 complete), assigned work order. Service types UDC 12/ST. Model schedules in F12071 |
| F1731 | Equipment Master Location History | owner and site history |
| F4801 | Work Order Master File | maintenance work orders: description, equipment worked on, estimated hours and amounts, charge-to accounts, status, type, priority, category codes |
| F0911 | Account Ledger | audit trail for both F1202 and F0902; work-order costs carry the work order as subledger with type `W` |

**Secondary tables**

| Area | Tables |
|---|---|
| Equipment data | F1205 Equipment Messages · F1206 Equipment License Master (`FHNUMB, FHADDS, FHLNUM`) · F1210 Location History Text · F1212 Parent History · F1215/F1216 Specification Cross Reference / Specification Data · F13017 Equipment Parts List · F17311 Equipment Master Location Details · F1391 Equipment Category Code Mapping · F00090/F00091/F00092 supplemental data (databases `AM` assets, `WO` work orders) |
| Preventive maintenance | F1393 Maintenance Rules · F1306 Meter Reading Estimates · F1308 Equipment Routes · F13411 PM Projections · F3460 Forecast File (parts demand from PM for MRP) · F1310 Condition-Based Alerts (alerts create or update F1207 schedules or work orders) |
| Work orders | F4802 Work Order Instructions (text by record type; record types in F48002) · F4826 W.O. Status Action Table (activity rules: allowed status sequence) · F4827 Work Order Approval Routing · F48001 Work Order Default Coding (default manager/supervisor by category codes 01–03) · F3111 Work Order Parts List · F3112 Work Order Routing (labor steps; actual hours can be replaced from payroll history F0618) · standard parts/labor F3002 Bill of Material and F3003 Routing · ledger records F48019 header, F31119 parts list, F31129 routing (written at statuses flagged in the activity rules) · F4829 delivery information |
| Equipment billing | F1301 Equipment Rates (`FGRTTB, FGRTGR, FGNUMB, FGEFTB, FGERC`) · F1390 rate code definition · F1302 Rental Rules (`FKCO, FKMCU`) · F1304 Equipment Location Billing · F1305 Equipment Distribution Rules |
| Equipment cost analysis (13E) | F1380 groups/subgroups · F1381 filters · F1382 equipment listing per group · F1383 Equipment Analysis Costs (summary and detail by group, subgroup, equipment, account, subledger, ledger type) · F1385 rules (which accounts count and their cost classification) · F5192/F5193 inquiry columns/formats |
| Resource assignments (13R) | F48310 Resource Master (crews, people, equipment) · F48311 / F48331 Resource Assignments · F48301 constants · F48307 working hours · F48302 Maintenance Schedule Periods · F48315/F48316 schedule and reschedule metrics; timecard templates staged in F06116Z1 |
| Accounting defaults | F12002 Default Accounting Constants · F12003 Default Depreciation Constants · F0012 AAIs |

**Work orders are one table for everything.** F4801 holds maintenance, manufacturing, service, engineering-change and project task orders; work-order type classification is UDC 48/OT (04 = equipment work order, 05 = service) and status is UDC 00/SS with site-specific values. Type (00/TY) and priority (00/PR) are separate codes. Costs are not stored on the work order: actuals are F0911 lines with subledger = work order number, type `W` (also in F0902 by subledger); estimates sit on F4801/F3111/F3112.

### 6.2 Rental Management (54R)

| Table | Name | Notes |
|---|---|---|
| F54R10 | Rental Contract Header | customer, dates, billing frequency, requested billing day |
| F54R11 | Rental Contract Detail | one row per rented item/asset line with actions and statuses |
| F54R20 | Rental Contract Related Orders | links each contract line to the sales order, purchase order or work order generated for it |
| F54R099 / F54R199 | Rental Contract Header / Detail Ledger | change history (ledger action codes, e.g. 07 = close contract) |
| F54R01 | Rental Constants | statuses of related orders required before closing |
| F54R02 / F54R021 / F54R03 / F54R031 | Action Definitions / Details / Line Type and Action Association header and detail | which actions (deliver, return, bill…) a line type allows |
| F54R12 | Purchase Order Receiver Rentals File | re-rent receipts |
| F54R41T | Rental Item | rental attributes of items |

Rental billing runs through the service-billing workfile: generation writes **F4812** (with asset number, period and fiscal year) and F1794 Billing Control, then invoices in F03B11. The module is activated by record `SY54R` in F99410. Inventory commitments for rented items are in F41021.

### 6.3 Real Estate Management (system 15)

```
F0006 Building/Property (business unit) ──< F1506 Floor ──< F1507 Unit (MCU, UNIT) ──< F1514 Area (by area type and date)
F1501B Lease header (DOCO, LSVR) ──< F15017 Lease detail (lease × building × unit, dates, tenant)
        ├── F1502B Recurring billings      ├── F15012B Expense-participation class   ├── F15013B Sales overage    ├── F15016B Escalation
        └── billing generation ──> F1511B Lease Billings Master ──post──> F03B11 invoices (or F0411 vouchers) + F0911
```

| Table | Name | Key / notes |
|---|---|---|
| F1510B | Real Estate Management Constants | company-level rules |
| F0006, F1506, F1507, F1514 | Building (business unit), Floor, Unit (`MCU, UNIT`), Area Master | property structure; areas by area type and effective date; F15142 area definitions; F15141 Gross Lease Occupied Areas; F1522/F15221 unit attribute templates |
| F159071 | Market/Potential/Renewal Rent Master | `MCU, UNIT, RNTY, SEQ` |
| F1501B / F15017 | Lease Master Header / Lease Master Detail | lease number + lease version (`DOCO, LSVR`); detail links lease to buildings and units with move-in/out dates |
| F1502B | Recurring Billings Master | `DOCO, LNID`; bill code, amount, frequency (F15019 Billing Frequency Master), dates |
| F1512 | Billing Code Extension | bill codes → G/L offset and revenue accounts |
| F1511B | Lease Billings Master | `GENT, ICU, DOC, SFX, KCO`; every billing transaction (manual or generated) before and after posting; history in F1511HB; batch summary F1511B1 |
| F15011B | Billings Generation Control | which period was generated for each lease/bill code/generation type (a `G` flag per period) |
| F1530, F15301, F15012B, F1531, F1533B, F150120–F150123 | Expense participation (EP) classes, account overrides, tenant EP class, adjustments, tenant exclusions, share-factor denominators | common-area cost recovery rules |
| F1538B, F1538B1, F1538B2, F1532B, F1539A/C/E/FC/FL, F15151–F15153, F15303 | EP billing register and audit tables, caps and cap history | how each EP bill was calculated |
| F1502WB / F1502WC | Estimated EP / lessee recurring billings worktables | become F1502B rows through R15113 |
| F15013B, F15014B, F15015B | Sales Overage Master, Product Scales, Min/Max Rents and Recoveries | percentage rent |
| F1540B, F1541B, F15410, F1542, F1543B, F1544B, F1547 | Sales Report Control, Tenant Sales History, weekly sales, projected sales, sales analysis, seasonality | tenant-reported sales |
| F15016B, F1548B, F1550 | Tenant Escalation Master, Escalation Billing Register, Escalation Index | index-based rent increases |
| F1525B | Fees and Interest | late fees on tenant A/R |
| F1565 | Security Deposit Master | `DOCO, LNID` |
| F1513B | Straight-line Rent (FASB 13) Lease Control | `DOCO, MCU, UNIT, CTRY, YR, ICU`; straight-line accruals |
| F1517 | Lease Amortization Schedules | lessee accounting for leased assets |
| F1570, F15701–F15703, F157011 | Legal clauses, options, space detail, amounts | critical dates and options |
| F1521 / F1523 | Log Detail Master / Log Standard Master | lease, unit, floor, building logs |
| F1505B / F1505HB | Management Fee Master / Revenue Fee Generation History | |
| F03B11T, F03B116, F03B117 | Customer Ledger tag and revenue-recognition tables | real estate invoices in A/R |

**Codes**
- **Generation type** on F1511B/F15011B: 1 recurring billing · 2 expense participation (actual) · 3 sales overage · 4 escalation · 6 expense participation (estimated) · 7 manual billing (fees and interest and straight-line rent have their own generation programs).
- **Document types** written when billings post – invoices: `RD` recurring, `RH` expense participation, `RJ` sales overage, `RL` escalation, `RN` manual, `RT` fees and interest; vouchers (lessee or payable leases): `PF` recurring, `PJ` sales overage, `PQ` manual/EP/escalation; accruals `AC`.
- **Batch types**: `1` real estate billing batch (F1511B), `2B` tenant invoices, `/` real estate vouchers; receipts `RB`.
- Tenant receivables are ordinary F03B11 rows (customer = tenant address number), paid through F03B13/F03B14. Deleting posted F1511B rows does not remove F03B11/F0911.

**UK and China enhancements (74U)**: tag tables extend the base ones – F74U01BT Lease Master Tag, F74U02BT Recurring Billing Tag, F74U03BT lease alternative UoM, F74U006T Business Unit Tag, F74U071T Property Unit Tag, F74U012T Tenant EP Class Tag, F74U25BT Interest Tag; F74U0201 Property Company Constants, F74U0202 Bank Base Rates, F74U0205 Payment Profile (billing is generated into the profile rather than straight to F1511B), F74U0212/F74U0213 periodic and weekly Accounting Billing Profile, F74U203A/F74U203B billing patterns, F74U0208 bill pattern mapping, F74U0209 EPM Status Code, F74U207A/B/C profile status histories.

**Advanced Real Estate Forecasting (15L)**: a budgeting sandbox keyed by building + revision number (`MCU, RVNB`): F15L100 building constants (+F15L1001 models), F15L101 AREF Unit Master (snapshot of units and leases), F15L102/F15L112 unit assumptions, F15L103/F15L113 sales overage rules, F15L104/F15L114 EP rules, F15L105 growth patterns, F15L106/F15L116 recurring bill code rules, F15L107 recycle rules, F15L120 account associations, F15L108/F15L118 base account definitions, F15L110/F15L111 account status (actuals pulled from F0902), **F15L109 AREF Budget Results** (`MCU, RVNB, AID, CTRY, FY, SBL, SBLT`), F15L141 gross lease occupied area, F15L301 projected sales, F15L302 prior gross billings, F15L38 EP billing register, F15L403 gross-up audit. Approved results are written to F0902 budget ledgers.

### 6.4 Analysis recipes

- **Equipment register**: F1201 ⨝ F1217, current location from F1204 (location code = current), status history F1307, parent/child from F1201 parent number and F1212.
- **Maintenance cost per equipment**: F0911 (ledger `AA`, posted) where the asset ID is the equipment or the subledger is a work order (type `W`) whose F4801 row points to the equipment; split labor/material by object account or by F1385 cost classifications; pre-summarised in F1383 if equipment cost analysis is used.
- **PM compliance**: F1207 by maintenance status and due date vs completion; projections in F13411.
- **Work-order backlog and ageing**: F4801 by status, type, priority, planned dates; estimates vs actuals (F0911/F0902 by subledger).
- **Rent roll**: F1501B ⨝ F15017 (active on the report date) ⨝ F1507/F1514 (unit area) ⨝ F1502B (current recurring billings by bill code) ⨝ F0101 tenant.
- **Occupancy / vacancy**: units F1507 against F15017 lease detail date ranges; areas from F1514 or F15141.
- **Lease expiries and options**: F1501B/F15017 dates, F1570/F15701 clauses.
- **Billed vs collected by tenant**: F1511B (billed, by bill code and generation type) → F03B11 open amounts.
- **Rental utilisation**: F54R11 lines by item/asset and dates; revenue from F4812/F03B11.

### 6.5 Tables named in these guides, by guide

- **Capital Asset Management**: F1201, F1202, F1204, F1205, F1206, F1207, F12071, F1210, F1212, F1215, F1216, F1217, F12002, F12003, F1301, F1302, F1304, F1305, F1306, F1307, F1308, F13017, F13411, F1380–F1385, F1390, F1391, F1393, F1731, F17311, F3002, F3003, F3111, F3112, F3460, F4801, F4801Z, F4802, F48001, F48002, F4826, F4827, F4829, F48301, F48302, F48307, F48310, F48311, F48315, F48316.
- **Work Orders**: F4801, F4802, F48001, F48002, F4826, F4827, F48019, F31119, F31129, F0911, F0902, F00191.
- **Condition-Based Maintenance**: F1310, F1207. **Equipment Cost Analysis**: F1380, F1381, F1382, F1383, F1385, F5192. **Resource Assignments**: F48301, F48307, F48310, F48311, F48315, F48331.
- **Rental Management**: F54R01, F54R02, F54R021, F54R03, F54R031, F54R099, F54R10, F54R11, F54R12, F54R199, F54R20, F54R41T, F4812, F1794.
- **Real Estate Management**: tables in section 6.3 plus F15011 Billings Generation Control Master, F15302 Ledger Type Groups, F15019, F00192 General Message Detail.
- **Enhanced REM UK/China** and **Advanced Real Estate Forecasting**: listed in section 6.3.
