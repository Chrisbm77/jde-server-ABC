> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.

# JDE data architecture — Part 4. JDE Supply Chain Management and Manufacturing

## Part 4. JDE Supply Chain Management and Manufacturing

Sources: Inventory Management, Sales Order Management, Advanced Pricing, Fulfillment Management, Outbound Inventory Management, Demand Scheduling Execution, Transportation Management, Warehouse Management, Bulk Stock Inventory, Advanced Stock Valuation, Agreement Management, Product Data Management, Shop Floor Management, Product Costing and Manufacturing Accounting, Requirements Planning, Forecast Management, Kanban Management, Demand Flow Manufacturing, Quality Management, Configurator, Engineer to Order, Project Manufacturing, In-Memory Planning Advisor.

### 4.1 The item and inventory backbone

```
F4101 Item Master (ITM) ──< F4102 Item Branch (ITM, MCU) ──< F41021 Item Location (ITM, MCU, LOCN, LOTN)   ← quantities
        │                          │                              └── F4108 Lot Master (lot status, dates, potency)
        │                          ├──< F4105 Item Cost (ITM, MCU, LOCN, LOTN, cost method)
        │                          └──< F4106 Item Base Price
        └── every stock movement ──> F4111 Item Ledger ("Cardex")  ──summarised──> F41112 Item As Of, F4115 Item History
```

| Table | Name | Grain / key | What it holds |
|---|---|---|---|
| F4101 | Item Master | item (short item number `ITM`†) | item numbers, description, search keys, category codes, default units of measure, stocking type, G/L class, line type, cost/price level, lot and warehouse process groups. `F4101D` translations, `F4101M` manufacturing data (lead times, issue type code) |
| F4102 | Item Branch File | item × branch/plant | branch-level category codes, planner/buyer/supplier, lead times, planning fences, order policy, ABC codes, MRP net-change flag, promising constraints flag, production-controlled flag |
| F41021 | Item Location File | item × branch × location × lot | **all quantity buckets**: on hand (`PQOH`), soft committed (`PCOM`), hard committed (`HCOM`), backordered (`PBCK`), on purchase order (`PREQ`), work-order commitments (`FUN1`…), in transit / inspection; G/L class; lot status; primary-location flag. `F41021T` tag = on-hand by production number |
| F4100 | Location Master | branch × location | location definitions, zones, level of detail |
| F41001 | Inventory Constants | branch/plant | location format, warehouse control, default UoM, supply/demand inclusion rule |
| F4105 | Item Cost File | `COITM, COMCU, COLOCN, COLOTN, COLEDG` | one row per **cost method**; flags say which method is used for sales/inventory and for purchasing |
| F4106 | Item Base Price File | item or item group × customer or customer group × branch × location/lot × currency × UoM × effective dates | base prices (currency and UoM are part of the key) |
| F4108 | Lot Master | lot × item × branch | lot status, expiration and other lot dates, potency, supplier lot |
| F4111 | Item Ledger File | one row per inventory transaction (appendix key `ILDOC, ILDCT, ILKCO`; physical unique key†) | history of every movement: item, branch, location, lot, document, transaction date, G/L date, quantity, unit cost, extended amount, order reference, production number |
| F41112 | Item As Of File | `INITM, INMCU, INLOCN, INGLPT, INCTRY, INFY` | period balances built from F4111 by R41542 (full or partial regeneration) for as-of valuation |
| F4115 | Item History | `IHITM, IHMCU, IHCTRY, IHFY` | usage/sales history by item, branch and fiscal year |
| F41002 / F41003 | Item UoM Conversion Factors / UoM Standard Conversion | item-specific / global | unit-of-measure conversions |
| F4104 | Item Cross Reference File | item × address × type (UDC 41/DT) | customer/supplier item numbers, substitutes, replacements |
| F4140 / F4141 | Cycle Count Header / Transaction | count × item/location/lot (`PJITM, PJMCU, PJLOCN, PJLOTN`) | physical inventory; `F4160` tag counts |
| F4118 / F41181 | Container Deposit / Container Transaction | | container management |

**Item identifiers**: three numbers per item – short (system-assigned numeric), 2nd (`LITM`, the "product number") and 3rd (`AITM`, catalogue number). Transaction tables store the short number and usually copies of the other two; join on the short number.

**Cost methods** (UDC 40/CM): `01` last in · `02` weighted average · `03` memo · `04` current · `05` future · `06` lot · `07` standard · `08` purchasing – base cost no additions · `09` manufacturing last cost. Standard-cost manufacturing uses `07`; actual costing uses `02` or `09`.

**Item-ledger document types** (defaults shown in the guides; UDC 00/DT): `IA` inventory adjustment · `II` inventory issue · `IT` inventory transfer · `IR` reclassification · `OV` purchase receipt · `IM` work-order material issue · `IC` work-order completion · `IS` work-order scrap · `RI` sales invoice · `ST`/`OT` transfer-order sales and purchase sides · `IB` item balance created by the frozen cost update · `PI` physical inventory†. Sales lines relieve on-hand either at shipment confirmation or at sales update (UDC 40/IU); at sales update the F4111 row is overwritten with the invoice number, type and G/L date.

**Availability** is calculated, not stored: on-hand minus the commitment buckets chosen in the branch's availability definition. Use the F41021 buckets and state which definition you applied.

### 4.2 Sales order to cash

```
F4201 SO header ──< F4211 SO detail ──(Sales Update R42800)──> F42119 SO history   + F03B11 invoice + F0911 + F4111
        │                │  └──< F42199 SO detail ledger (status/audit trail)        + F4229 sales summary, F42005 commissions
        │                ├──< F4074 price adjustment ledger     ├──< F49211 SO detail tag (shipment/freight)
        │                └──< F4209 held orders                 └──< F4211TX taxed prices
        └── sold-to / ship-to F0101 + F03012 billing instructions
```

| Table | Name | Key (composite-key appendix) | Notes |
|---|---|---|---|
| F4201 | Sales Order Header File | `SHDOCO, SHDCTO, SHKCOO, SHSFXO` | sold-to, ship-to, dates, terms, hold code, currency; purged to **F42019** header history |
| F4211 | Sales Order Detail File | `SDDOCO, SDDCTO, SDKCOO, SDLNID` | the working table for open lines: item, branch, quantities ordered (`UORG`) / shipped (`SOQS`) / backordered / cancelled, unit price and extended price (`AEXP`), unit cost (`UNCS`) and extended cost, line type (`LNTY`), last/next status (`LTTR`/`NXTR`), requested (`DRQJ`), promised and actual ship dates, invoice number/type/date, sold-to `SDAN8`, ship-to, shipment number, related purchase/work order |
| F42119 | Sales Order History File | same layout as F4211 | closed lines moved here by sales update or by the purge R42996; some sites keep closed lines in F4211 at status 999 |
| F42199 | S.O. Detail Ledger File | `SLDOCO, SLDCTO, SLKCOO, SLLNID` (+ status/time) | a copy of the line at each status flagged "ledger" in the activity rules; source for credit orders from history |
| F49211 | Sales Order Detail File – Tag File | `UDDOCO, UDDCTO, UDKCOO, UDLNID` | shipment confirmation, freight and intercompany invoice data |
| F4229 | Sales Summary History File | customer × branch × order type × item × line type × sales codes × fiscal year | summarised sales and COGS |
| F42005 | Sales Commission File | `SCDOCO, SCDCTO, SCKCOO, SCLNID` | commissions; constants F42004, assignments F42140/F42150/F42160 |
| F4209 | Held Orders | order × hold code | hold and release history (hold codes UDC 42/HC) |
| F40203 | Order Activity Rules | order type × line type × status | status flow for sales **and** purchasing |
| F40205 | Line Type Control Constants | line type | inventory/G/L/A/R interfaces of a line |
| F4074 | Price Adjustment Ledger File | `ALDOCO, ALDCTO, ALKCOO, ALLNID` + adjustment | price history per order line (sales and purchase) |
| F4211TX, F4201TX, F42199TX, F42119TX | Tax tag tables | | taxed prices |
| F40300R, F40711, F40721 | Preference Resolution Ledger / Preference Values | | advanced preferences applied |
| F42420 | Audit Log Transaction | | order change audit |
| F004201 | Prepayment Transaction | | credit-card prepayments (status UDC 00/SP) |
| F40051 | Return Material Authorization | | RMA links between credit and replacement orders |

**Status flow**: each line carries last and next status (UDC 40/AT). Examples used in the guides: 520 = enter sales order; a line at 540 advances to 560 when shipment is confirmed; 580 = cycle billing/invoicing; sales update moves lines at 600 to 999 (closed). Sites change steps per order type + line type, so read F40203 rather than assuming. Held orders do not advance until released.

**Order types** named in the guides: `SO` sales order · `ST` transfer order (sales side; paired purchase order `OT`) · blanket and quote orders (types listed in UDC 40/BT) · credit orders · direct ship (creates a linked purchase order; the receipt advances the sales line) · interbranch/intercompany orders. A transfer order writes F4201/F4211 **and** F4301/F4311.

**Sales update (R42800)** creates the invoice in F03B11, journal entries in F0911, the F42199 ledger row, updates on-hand in F41021/F4111/F4115 when not relieved at ship confirm, F4229 and F42005, sets the line to 999 and optionally moves it to F42119 and the header to F42019. All receivables post to the sold-to. Sales DMAAIs (F4095): 4220 COGS · 4230 revenue · 4240 inventory · 4245 A/R trade · 4250 tax liability · 4260 interbranch revenue · 4270 price adjustments · 4280 rebates payable · 4221/4231/4232 deferred and unbilled (cycle billing). Lookup order: order company + order type + G/L class → `****` wildcard class → company 00000.

**Pricing**: base price F4106; Advanced Pricing F4070 schedule → F4071 adjustment type → F4072 adjustment detail (prefix levels by item/customer group keys F4092, F40941, F40942, F40943) → applied adjustments logged per order line in F4074; F4075 price variables, F4076 formulas, F4073/F4573 free goods, rebates F4078 summary / F4079 detail, ship-and-debit F4575/F4576, price lists F45520–F45524, price matrix F4580.

### 4.3 Logistics

- **Warehouse Management (46)**: F4600 Warehouse Requests (putaway, pick, replenishment) → F4611 Warehouse Suggestions → F4601 Warehouse Task Header; F4602 Location Detail Information (item, quantity, UoM per location); item profile F46010, UoM definition F46011, fixed locations F46012; location characteristics/dimensions/capacity F46021/F46022/F46024; movement instructions F46095, process selection F46093, order groups F46092; cartons F46091 codes, F4615 recommendations, F4620 carton detail (labels, serial/EPC); license plates F46L10 master, F46L11 item detail, F46L12 commitments, F46L30 location capacity, F46L99 history. Supply/demand inclusion rules F34004 decide which order types and statuses create requests.
- **Transportation (49)**: F4215 Shipment Header, F4941 Shipment Routing Steps, F4942 Shipment Detail, F4943 Shipment Pieces, F4945 Shipment Charges, F4947 Shipment Status Codes, F4217 Shipment Reference (tracking) Numbers, F4216 SO Pack Confirm Detail, F4906 Carrier Master, F4950 Routing Entries, F4972 Rate Detail, F4981 Freight Audit History (payable and billable freight with tax and cost objects), loads in transit F4963/F49631/F49632, constants F49001. Shipment number is stamped on F4211/F49211.
- **Demand Scheduling (40R)**: EDI demand F47171/F47172/F47173 (+F471721–F471724) → F40R10 Demand Header, F40R11 Demand Detail, F40R12 cumulative quantities, F40R13 packaging, F40R14 addresses, F40R20 demand rules, F40R41 demand history, F40R42 cumulative history; advance ship notices F47036 header / F470371 detail.
- **Outbound Inventory / consignment (42I)**: F42I010 Agreement Master, F42I011 Agreement Detail, F42I02 Agreement Acknowledge (received at customer), F42I03 Consumption Report File, F42I015 transactions, F42I021 item balance, change history F42I06/F42I07; reuses agreement tables F38010/F38011.
- **Fulfillment (42W)**: F4277701 Service Level Rule, F4277711 Service Level Rule Detail, F4277710 Fulfillment Plan ID, F4277750 scoring setup.
- **Agreements (38)**: F38010 Agreement Master, F38011 Agreement Quantities, F38012 source/destination, F38013 quantity schedule, F38014 formulas, F38111 Agreements Transaction Ledger, F38112 committed quantities.
- **Bulk stock (41B)**: F41500 Tank Master, F41503 strapping tables, F41505 allowed products, F41506 Meter Master, F41508 default tank information, F41022 bulk depot/product information, F41011 bulk item master, F41511 Bulk Product Transaction File (ambient/standard volumes, temperature, density per movement), F41512 Gain/Loss Transactions, F41515 meter readings.
- **Advanced Stock Valuation (39)**: F3904 item pools, F39041 valuation categories, F3905 valuation methods, F39042 company G/L update method, F39061 Valuation Period Table, F39062 Valuation Layers (LIFO/FIFO layers), F39063 additional quantities, F39064 document summary, F3908 replacement costs, F3910 G/L adjustments. Built from F4111.

### 4.4 Manufacturing

```
F3002 Bill of Material ─┐                         ┌─< F3111 WO parts list ──issues (IM)──> F4111
F3003 Routing ──────────┼─(order processing)──> F4801 Work Order ──< F3112 WO routing ──< F31122 time transactions
F30006 Work Center ─────┘        ▲                 └─ completions (IC) ─> F4111, F41021      └─> F3102 Production Cost ─> F0911
F3460 Forecast, F4211, F4311 ─(MRP R3482/R3483)─> F3411 messages, F3412 pegging, F3413 time series
```

| Table | Name | Grain | Notes |
|---|---|---|---|
| F3002 | Bill of Material Master File | parent item × branch × BOM type × component (× effectivity) | quantity per, issue type, features/options, revision level; changes logged in F3011; ECO parts in F3013 |
| F3003 | Routing Master File | item × branch × routing type × operation sequence | work center, run/setup/machine time, yield, outside operations |
| F30006 / F30008 / F3007 | Work Center Master / Rates / Resource Units | work center (a business unit) | efficiency, queue/move hours; simulated and frozen rates; capacity by day/month/shift |
| F3009 | Manufacturing Constants | branch/plant | BOM/routing validation, commitment control, hours per day, costing options |
| F4801 | Work Order Master File | one row per work order or rate schedule (order number `DOCO`†; appendix lists `WADCTO, WATYPS, WASRST, WADPL, WAAN8, WADOCO`) | item, branch, quantities ordered/completed/scrapped, dates, status (`SRST`, UDC 00/SS), type, parent order, related sales order. The **same table** holds manufacturing, equipment, service, engineering-change and project task orders (document-type classification in UDC 48/OT: 02 manufacturing, 03 rework, 04 equipment, 05 service, 08/09 engineering change, 12 rate schedule) |
| F4801T / F4801T1 | Work Order Master Tag / ETO tag | work order | cost method (standard vs actual), unaccounted amounts, production number, project data |
| F3111 | Work Order Parts List | work order × component line (`CMCU, CPIT, COBY, DOCO, OPSQ`) | required, issued, unaccounted quantities |
| F3112 | Work Order Routing | work order × operation sequence × work center | standard vs actual hours, operation status, unaccounted labor |
| F31122 | Work Order Time Transactions | `WTYST, WTAN8, WTDGL, WTDOCO, WTOPSQ, WTTYR` | labor and machine time and quantities by employee/date/operation; R31422 rolls them into F3112 |
| F3102 | Production Cost | work order × cost component | standard, planned, actual and completed costs and variances |
| F4802 | Work Order Instructions File | work order × record type | text |
| F3105 / F3106 / F3108 | WO lot-serial numbers / WO cross-reference | | |
| F3109 / F31091 | Line/Item Relationship Master / Schedule Quantity Detail | | repetitive (rate schedule) production |
| F3118 | Shortage Maintenance Master | | component shortages |
| F30026 / F300261 | Item Cost Component Add-Ons / Detail | item × branch × cost method × cost component | simulated and frozen standard cost by component |
| F00191 | Generic Message/Rates | | costing factors and rates, employee labor rates |

**Cost components** (UDC 30/CA): `A1` purchased material · `B1` direct labor · `B2` setup labor · `B3` machine run · `B4` labor efficiency · `C1`/`C2` machine variable/fixed overhead · `C3`/`C4` labor variable/fixed overhead · `D`x outside operations and extras†. Simulated roll-up (R30812) fills F30026; the frozen update (R30835) writes standard cost to F4105 method 07, revalues on-hand (batch type `NC`, item-ledger type `IB`) and WIP.

**Work-order lifecycle**: created (planning message, sales order, manual) → order processing (R31410) attaches F3111/F3112 → material issues (`IM`) → hours and quantities (F31122 → F3112) → completions (`IC`) and scrap (`IS`) → manufacturing accounting journal entries (R31802A; WIP, completions) → variances (R31804) → close. Unaccounted units sit on F3111, F3112, F3102, F4801/F4801T until journal entries are created. Lean/demand-flow transactions use their own `FF` tables (FF31010 Production Master, FF31011 Lean Transaction Master, FF31111 parts list, FF31112 routing, FF31113 labor detail, FF31200 production costs, FF31201 G/L cross-reference; DFM design tables FF30L… and kanban FF31K…).

**Planning (34/36/33)**
- F3460 Forecast File – key `MFITM, MFMCU, MFDRQJ, MFTYPF, MFDCTO`; detail forecasts and, with forecast type `AA`, actual sales history copied from F42119 by R3465. F3400 Forecast Summary File, F34007 forecast prices, F4091 summary hierarchy constants, F3405 forecast consumption periods.
- F3411 MPS/MRP/DRP Message File – action messages (UDC 34/MT: `A` warning · `B` order and expedite · `C` cancel · `D` defer · `E` expedite · `F` frozen order · `G` increase quantity · `L` decrease quantity · `M` manual reminder · `N` create rate · `O` order · `T` past due). `WP` planned work orders have no F4801 header until the message is processed.
- F3412 Lower Level Requirements (pegging: source of gross requirements from parent items) · F3413 Summary File (time series by quantity type, UDC 34/QT and related tables) · F3403 Branch Relationships (DRP supply/demand between branches) · F34004 Supply/Demand Inclusion Rules (which order types and statuses count).
- Capacity: F3303 resource profiles, F3311 capacity messages, F3313 capacity load.
- Supplier scheduling: F4321/F43211 schedule master and splits, F3430 Vendor Schedule Quantity, F3435 commitments, F3440 history, F3450 ad hoc schedules.
- In-Memory Planning Advisor: configuration F34X001, F34X010; everything else (F34X100W, F34X101W, F34X110W, F34X200W, F34X310W) is a refreshable work table.

**Other manufacturing sub-systems**
- **Kanban**: F3016 Kanban Master (one row per kanban ID), F3016T tag, F30161 Kanban Card Detail (status, quantity, date), F3017/F3018 size calculation, F3019 replenishment capacity.
- **Quality**: F3701 test definitions, F37011 test equipment, F3702/F37021 specifications, F3711 Test Results (by item/lot on inventory, work order, purchase or sales order; F3711Z1 inbound from LIMS), F3703 nonconforming material, F37900 certificate-of-analysis extract, F40318 quality preference.
- **Configurator (32)**: F3201 Configurator Master (configuration ID per order line), F3211 segment detail (answers), F3215 components, F3212 routings, F3216 price/cost; rules F3291 segments, F3292/F32921/F32922 cross-segment editing rules, F3293 assembly inclusion rules, F3281–F3283 rules tables, F3209 constants.
- **Engineer to Order (31P)**: projects and WBS tasks are F4801 rows (project number not blank) with F4801T1; F31P01 Project Attributes, F31P10/F31P11 quotes, F31P12 task dependencies, F31P21 cost classification, F4080 Related Order Cross Reference, F410211 Project Commitment Detail, F5108 Extended Job Master.
- **Project manufacturing (production numbers)**: F34401 Production Number Master (key company + production number short), F34401T tag, F34402 structure; the production number is carried on F4211, F4311, F43121, F4801T, F3411, F3460, F4111 and on-hand by production number in F41021T.

### 4.5 Distribution accounting

Distribution/manufacturing AAIs are in **F4095** (values by AAI table number, company, document type, G/L class, cost type); F4090 lists the AAI record types. The G/L class (`GLPT`, UDC 41/9) on the item location/order line plus company and document type select the account; `****` is the wildcard class and 00000 the default company. Tables you will meet: 3110/3120/3130… manufacturing†, 4122/4124 inventory†, 4220–4280 sales, 4310–4390 purchasing. Flexible sales accounting (F4096) can derive business unit/subsidiary/subledger from order fields. Inventory batches are type `N`, purchasing `O`, sales invoices `IB`, interbranch transfers `ST`.

### 4.6 Analysis recipes

- **Stock on hand and value**: F41021 on-hand by item/branch/location/lot × F4105 cost of the sales/inventory method; join F4101 for description and stocking type, F4102 for branch classifications. For a past date use F41112 (or roll F4111 back from today).
- **Stock movements / consumption**: F4111 filtered by document type and transaction or G/L date; receipts `OV`, issues `II`/`IM`, completions `IC`, sales `RI`.
- **Open sales orders / backlog**: F4211 with next status < 999 (and not cancelled), by requested or promised date; join F4201, F0101 (sold-to/ship-to), F4101.
- **Sales history / revenue by customer and item**: F42119 **union** F4211 lines already invoiced (check where closed lines live at this site), using invoice date and extended price/cost; or the pre-summarised F4229; reconcile to F03B11/F0911.
- **Order cycle times**: F42199 status timestamps per line.
- **Fill rate / on-time shipment**: F4211/F42119 shipped vs ordered quantity, actual ship vs promised date; shipment-level data in F4215/F4941/F49211.
- **Margin**: extended price minus extended cost on the sales line; price adjustments in F4074.
- **Where-used / BOM explosion**: F3002 recursive on parent → component within branch and BOM type, respecting effectivity dates.
- **Work-in-process and work-order variance**: F4801 open orders by status; F3111 issued vs required; F3112 actual vs standard hours; F3102 cost and variance by component.
- **MRP exceptions**: F3411 by message type, planner (F4102) and item; pegging through F3412; supply/demand time series in F3413.
- **Forecast accuracy**: F3460 forecast types vs type `AA` actuals for the same item/branch/period.
- **Quality**: F3711 results joined to F3701 tests and F4108 lots; failures in F3703.

### 4.7 Tables named in the guides, by guide

- **Inventory Management**: F4009, F40095, F40096, F4016, F4017, F40039, F4095, F4100, F41001, F41002, F41003, F41006, F4101, F4101D, F41013, F4102, F41021, F41021T, F41023, F4104, F4105, F41051, F4106, F41061, F4108, F41081 Allowed Lot Status, F4111, F41112, F41113 Lot Ledger, F4115, F4118, F41181, F4140, F4141, F4160, F4170 Lot Status Activity Rules, F41829 Item Word Search, F41291 Item Cost Components, F46010.
- **Sales Order Management**: F4201, F42019, F4201TX, F4211, F42119, F4211TX, F42199, F42199TX, F4229, F42004, F42005, F42140, F42150, F42160, F4209, F40203, F40205, F4074, F4106, F4573 Free Goods, F40300R, F40344, F40711, F42420, F42440 Customer Segment Items, F4314, F40051, F004201, F41021WF Transaction Workfile, F49211, F34A10/F34A11/F34A30/F34A110/F34A210 APS integration and ATP rules, F4001Z/F4011Z batch order headers/details, F470462 EDI invoice.
- **Advanced Pricing**: F4070, F4071, F4072, F4073, F4074, F4075, F4076, F4078, F4079, F4092, F4093, F40941, F40942, F40943, F40UI74, F4510, F4511W, F4550, F45520, F45521, F45522, F45523, F45524, F45715, F4575, F4576, F4576Z1, F4580.
- **Warehouse / Transportation / Demand / Outbound / Fulfillment / Agreements / Bulk / Stock valuation**: listed in section 4.3.
- **Product Data Management**: F3002, F3003, F30006, F30008, F3007, F3009, F3011, F3013, F3015 Component Locator, F4101M, F4808 Order Routing Approval Master, F4818 Order Approval Audit, F48092 WO supplemental data.
- **Shop Floor Management**: F4801, F4801T, F4802, F3111, F3112, F31122, F3102, F3105, F3108, F3109, F31091, F3118, F300210/F300211/F300311 lean multi-level BOM and routing, FF31010–FF31201, FF30L912 Line Master; purge copies F3111S, F3112S, F31122S, F3102S, F4801S.
- **Product Costing and Manufacturing Accounting**: F30026, F300261, F30008, F3102, F3106, F4105, F4095, F4096, F00191, F1301 equipment rates.
- **Requirements Planning / Forecast / Planning Advisor**: F3411, F3412, F3413, F3403, F3405, F3406, F3425 safety stock messages, F3430, F3435, F3440, F3450, F3460, F3400, F34006, F34007, F4091, F3303, F3311, F3313, F4321, F43211, F34004, F34X001, F34X010, F34X100W, F34X101W, F34X110W, F34X200W, F34X310W.
- **Kanban / Quality / Configurator / ETO / Project Manufacturing**: listed in section 4.4.
