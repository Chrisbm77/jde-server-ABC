> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.

# JDE data architecture — Part 1. JDE Foundation — system codes, Address Book, shared building blocks

## Part 1. JDE Foundation — system codes, Address Book, shared building blocks

Sources: *Foundation Guide* (Tools), *Address Book Implementation Guide*.

### 1.1 What lives here

Everything else in JDE hangs off four shared ideas defined in this area:

1. **System (product) codes** – every table name starts with `F` + its system code, so the name tells you the owning module.
2. **Address Book** – one number (`AN8`) identifies every customer, supplier, employee, company, bank, tenant, carrier, bidder, partner.
3. **User-defined codes (UDCs) and category codes** – almost every coded column is validated against a UDC table.
4. **Batch-input (Z) tables** – every inbound interface uses the same EDI key pattern.

### 1.2 System codes → table names

A table is `F` + system code + sequence (`F0411` = system 04, `F03B11` = system 03B, `F43121` = system 43, `F15L109` = system 15L). The system-code list is Appendix A of the Foundation guide; the ones that matter for business data:

| Code | System | Code | System |
|---|---|---|---|
| 00 | Foundation environment (companies, business units, UDCs, next numbers, batches, AAIs, currency, tax) | 40 | Inventory/Order Processing base (shared distribution setup, line types, activity rules, pricing base) |
| 01 | Address Book | 41 / 41B | Inventory Management / Bulk Stock |
| 03 / 03B | Accounts Receivable (03B = "Enhanced A/R", the live ledger tables) | 42 / 42I / 42W / 42X | Sales Order Mgmt / Outbound Inventory / Fulfillment / In-Memory Sales Advisor |
| 04 | Accounts Payable | 43 / 43A / 43B / 43C / 43E / 43Q / 43S | Procurement / receipt routing / voucher match & landed cost / contracts / Requisition Self Service / sourcing / supplier self service |
| 05–08 | Time accounting, payroll, HR | 44 / 44H | Subcontract Management / Homebuilder |
| 09 / 09E / 09J | General Accounting / Expense reimbursement / Joint Venture | 45 | Advanced Pricing |
| 10 / 10C | Financial reporting / multisite consolidations | 46 / 46L | Warehouse Management / License plating |
| 11 / 11C | Multicurrency / cash basis | 47 | EDI |
| 12 | Fixed Assets | 48 / 48S | Work order processing / Service billing |
| 13 / 13C / 13E / 13R | Plant & Equipment (CAM) / condition-based maintenance / equipment cost analysis / resource assignments | 49 | Transportation |
| 14 | Modeling, planning & budgeting | 50 / 51 | Job cost |
| 15 / 15L | Real Estate Management / Advanced Real Estate Forecasting | 52 / 52G | Contract billing / Project & government contract accounting |
| 16 | Profit management (Advanced Cost Accounting) | 53 | Change management |
| 17 / 17C | Customer service management / call (case) management | 54R | Rental Management |
| 30 / 31 / 31A / 31P | Product data mgmt / shop floor / manufacturing accounting / engineer to order | 55–59 | Reserved for clients (custom tables `F55…`–`F59…`) |
| 32 | Configurator | 60–69 | Reserved for JDE custom |
| 33 / 34 / 34X | Capacity planning / requirements planning (MPS-MRP-DRP) / In-Memory Planning Advisor | 70–76 | Localizations (74 = EMEA, 74U = UK; 75 = Asia-Pacific; 76 = Latin America) |
| 36 / 37 / 38 / 39 | Forecasting / quality / agreements / advanced stock valuation | 90CA–90CG | CRM (foundation, sales force automation, marketing, service, solution advisor, scripting, case mgmt) |

The number is a strong hint, not a guarantee: `F4801` (work orders) is used by manufacturing, CAM, service and real estate; `F4008` (tax areas) sits in system 40 but is financial; `F3460` (forecast) is read by sales, planning and maintenance.

**Suffix conventions seen across the guides**

| Suffix | Meaning | Examples |
|---|---|---|
| `Z1`, `Z2`, `Z` | Unedited-transaction / batch-input / interoperability or generator work table | F0911Z1, F0411Z1, F03B11Z1, F0101Z2, F4311Z1, F4301Z |
| `T`, `T1`, `TX` | Tag (extension) table sharing the base table's key; `TX` = taxed-price tag | F4311T, F43121T, F4801T, F4801T1, F41021T, F03B11T, F4211TX |
| `W`, `WF`, `UI…` | Work file | F34X200W, F4333WF, F40UI74, F31PUI01, F1502WB |
| `A` | As-of or audit copy | F0411A, F0413A, F0414A, F0101A, F03012A |
| `P`, `S` | Purge/save copy | F0411P, F03B11P, F1201P, F3111S, F4801S, F3460S |
| `D` | Alternate-language description | F0006D, F0901D, F4101D, F0012D |
| trailing `9` / `H` | Ledger or history of the base table | F42119, F42019, F42199, F43199, F43099, F48019, F31119, F31129, F54R099, F54R199, F32019, F1511HB, F4812H |
| `B` (system 15) | Current-generation Real Estate table | F1501B, F1511B, F1502B |

### 1.3 Address Book data model

| Table | Name | Grain / key | What it holds |
|---|---|---|---|
| F0101 | Address Book Master | one row per address number (`AN8`)† | Names, address numbers, search types, address book category codes for any individual or company |
| F0111 | Address Book – Who's Who | `AN8` + who's-who line (`IDLN`) | Contact names and who's-who category codes |
| F01112 | Related Person | under a who's-who line | People related to a who's-who entry |
| F0115 | Address Book – Phone Numbers | per address / who's-who line | Area codes, phone numbers, phone types |
| F01151 | Electronic Address | per who's-who line | E-mail and URL addresses |
| F0116 | Address by Date | `AN8` + effective date (`EFTB`) | Address lines, postal code, effective dates. R01840 writes the effective date of the current address back to F0101 |
| F01161 | Alternate Address | per who's-who/contact | Extra addresses with effective dates |
| F0150 | Address Organization Structure Master | structure type + parent + child | Parent/child relationships (structure types in UDC 01/TS; blank = default structure) |
| F01501 | Enhanced Parent Child | | Parent numbers and who's-who child numbers |
| F0117, F0118, F0017 | Postal codes / postal code address | | City, state, county, country per postal code |
| F0070 | Country Constants Master | country | Country-specific address formats |
| F01815 | AB Word Search Master | | Search words built from address book data |
| F01090, F01092, F01093 | Supplemental Database – core / code / narrative | | User-defined supplemental data |
| F0101A | Address Book Master Audit Log | | Changes to and additions of address book records |
| F01138 | Data Permission List Definition | | Data-privacy permission lists (personal fields in F0101/F0111/F0115/F0116 can be masked) |
| F0119 | Address Book Geo Code | | Latitude/longitude from the geocoding service |
| F01301, F01311, F01321, F01331 | Activity / Calendar / Recurrence / Recurrence Exclusion | | Foundation calendar events and tasks |
| F01401, F01411 | Action Plan / Action Plan Activity | | Activity templates |
| **F0401** | Supplier Master | `AN8` | Supplier-specific setup (payment terms, bank, YTD vouchered amounts, prenote status) |
| **F03012** | Customer Master by Line of Business | `AN8` + company | Customer-specific setup (credit, billing instructions, category codes). Without line-of-business processing there is one row per customer for company 00000 |
| F03012A | Customer Date-Effective Category Codes | | Future-dated customer category codes |

**How to read an address number**

- The role of an address is its **search type** (`AT1`, UDC 01/ST): `C` customers, `V` suppliers, `E` employees, `A` applicants, and any site-defined codes. A number is a customer or supplier for transactions when a row exists in F03012 or F0401.
- Address book category codes are `AC01`–`AC30`; customer master has its own set. The first 10 customer category codes are copied onto each invoice at entry, so the ledger keeps the classification as of the invoice date.
- A supplier or customer cannot be deleted while it has rows in F0411/F0413/F0414, F03B11/F03B13, F0911, or F0902 (when the address number is used as a subledger), nor while F4211, F4311, F4801, F5201, F1501B rows reference it. Those are therefore the tables to search when asking "where is this address number used?".
- Companies must exist as address numbers too: every company in F0010 needs an F0101 record or the G/L post fails.

**Field aliases named in the Address Book mapping appendix** (data-dictionary aliases; physical columns add the table's two-character prefix†):
`AN8` address number · `ALKY` long address number · `ALPH` alpha name · `MLNM` mailing name · `AT1` search type · `TAX`/`TX2` tax IDs · `MCU` business unit · `SIC` industry code · `LNGP` language · `CM` credit message · `AC01…AC30` category codes · `AN81…AN86` related address numbers · `EFTB` effective date · `ADD1…ADD4` address lines · `ADDZ` postal code · `CTY1` city · `COUN` county · `ADDS` state · `CTR` country · `AR1`/`PH1`/`PHT1` phone prefix/number/type · `IDLN` who's-who line.

### 1.4 User-defined codes and category codes

- A UDC is a (product code, code type) pair such as `01/ST` (search types), `00/DT` (document types), `00/PS` (payment status), `09/LT` (ledger types), `40/AT` (order status codes). Values are stored in **F0005** (User Defined Codes) with Description 01, Description 02, Special Handling and Hard Coded attributes; code types are defined in F0004†.
- "Special Handling" often carries logic (for example which write-off reason codes accumulate as minor write-offs, or the format of a custom subledger type), so read it before interpreting a code.
- **Category codes** are UDC types reserved for the customer's own classification (Category Code 01, 02…). They exist on address book, customer, supplier, business unit, account, item, item branch, asset, work order, lease and more. Their meaning is site-specific: always read the UDC descriptions instead of assuming.
- **F40039** (Document Type Master) is a single repository of document-type attributes that also live in several UDC tables (40/DC, 40/CT, 40/BT, 40/IU, 39/TT, 40/NT, 40/OC, 40/OQ, 40/IB, 17/CM, 48/OT, 46/RS). Adding a value directly in the UDC updates F0005 but not F40039.
- † To decode a value: join `F0005` on product code (`DRSY`), code type (`DRRT`) and code (`DRKY`). `DRKY` is a 10-character field stored right-justified with leading blanks, so compare with `LTRIM`/`TRIM`.

### 1.5 Shared tables every module uses

| Table | Name | Notes |
|---|---|---|
| F0002 / F00021 | Next Numbers – Automatic / by Company and Fiscal Year | Source of document, batch, order, address numbers |
| F0005 | User Defined Codes | Decode table for coded columns |
| F0006 | Business Unit Master | Business units, and equally branch/plants, warehouses, jobs, projects, buildings/properties, depots |
| F0007 | Workday Calendar | Work-day types by branch/plant, month, year, shift |
| F0008 | Date Fiscal Patterns | Period end dates per fiscal year and pattern |
| F0009 | General Constants | System-wide rules (account coding, batch control and approval, intercompany, multicurrency) |
| F0010 | Company Constants | Company number, name, fiscal date pattern, current period, base currency |
| F0011 | Batch Control Records | One header per batch of financial/distribution transactions |
| F0012 | Automatic Accounting Instructions Master | Financial AAIs |
| F0013 / F0015 | Currency Codes / Currency Exchange Rates | |
| F0014 (+F00141–F00147) | Payment Terms (advanced, due date rules, multitiered, installment) | |
| F0018 / F0018R | Taxes / Tax Reconciliation Repository | |
| F0025 | Ledger Type Master | |
| F0030 | Bank Transit Master | G/L, customer and supplier bank accounts (record type distinguishes them) |
| F00090 / F00091 / F00092 | Supplemental Database setup / data types / data | Generic user-defined data by database code (business units, assets `AM`, work orders `WO`, items…) |
| F00095 | Business Object Reservation | Record locks; not business data |
| F00165 | Media Objects Storage | Attachments and generic text for any record |
| F00191 | Generic Message/Rates | Text messages, and rate tables (costing factors 30/CF, costing rates 30/CR, employee labor rates 31/ER) |
| F007101 / F007111 | Text Processor Header / Detail | Staging for text files exported to or imported from outside (bank files, positive pay) |
| F99410 | System Control File | Module activation switches (for example `SY90CA` CRM, `SY54R` Rental) |

### 1.6 Batch-input (Z-table) pattern

Inbound data never goes straight into master or ledger tables. A custom program loads a `Z` table and a JDE batch program edits and creates the real records (address book: F0101Z2, F03012Z1, F0401Z1, F0111Z1, F01112Z1, F0115Z1, F01151Z1, F01161Z1; the same pattern exists for journal entries, vouchers, invoices, receipts, budgets, orders, work orders).

Common key and control aliases: `EDUS` EDI user · `EDBT` EDI batch · `EDTN` EDI transaction number · `EDLN` EDI line · `EDSP` successfully-processed flag · `TNAC` transaction action · `DRIN` direction indicator · `EDCT` EDI document type · `EDDT` transmission date. Child records attach to their parent by EDI user + batch + transaction number. Processed rows stay in the Z table until purged, so **never report from Z tables as if they were the ledger**; filter on `EDSP` if you must read them.

Audit aliases on almost every table: `USER` user ID · `PID` program ID · `JOBN` workstation · `UPMJ` date updated · `UPMT` or `TDAY` time updated. `PID` tells you which program wrote the row, which is often the quickest way to know where data came from.

### 1.7 Analysis recipes

- **Name for any address number**: join F0101 on `AN8`, read `ALPH`.
- **Current mailing address**: F0116 row with the latest effective date not after today for the `AN8`.
- **Customer or supplier attributes**: F03012 (remember the company dimension; 00000 is the default row) or F0401.
- **Roll-ups (national accounts, buying groups, reporting hierarchies)**: F0150 filtered on the structure type; blank is the default hierarchy.
- **Decode any code**: find its UDC (product code/type) in the relevant guide section, then join F0005.

### 1.8 Address Book and foundation tables named in the guides

Address book: F0101, F0101A, F0101Z2, F0111, F0111Z1, F01112, F01112Z1, F0115, F0115Z1, F01151, F01151Z1, F0116, F01161, F01161Z1, F0117, F0118, F0017, F0119, F0070, F0150, F01501, F01815, F01090, F01092, F01093, F01138, F011901 Contacts Subscription, F01301 Activity Master, F01301W, F01302, F01311 Calendar Master, F01315 Calendar Association, F01321, F01331, F01401, F01411, F0401, F0401Z1, F03012, F03012Z1, F76011 / F76011P Address Book Brazilian Tag and its archive.
