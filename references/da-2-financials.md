> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.

# JDE data architecture — Part 2. JDE Financials

## Part 2. JDE Financials

Sources: Financial Management Fundamentals, General Accounting, Accounts Payable, Accounts Receivable, Fixed Assets, Multicurrency Processing, Base Currency Conversion (composite-key appendix), Tax Processing, Advanced Cost Accounting, Expense Management, Joint Venture Management, 1099 Year-End Processing.

### 2.1 Organisation and chart of accounts

```
F0010 Company ──< F0006 Business Unit (MCU) ──< F0901 Account (AID = MCU.OBJ.SUB) ──< F0902 balances
                                                              └──────────────────────< F0911 transactions
```

- **Company (F0010)** – number, name, fiscal date pattern, current period, base currency. Company 00000 is the default company used for constants, AAIs and next numbers. Closing a period updates the current period in F0010.
- **Business unit (F0006)** – "where": department, branch/plant, job, project, building. Carries company and category codes. Posting edit on the business unit: blank = posting allowed, `K` = budget locked, `N` = no posting, `P` = may be purged. `F0006S` holds date-effective snapshots of the structure; `F0050`/`F0050A` hold parent/child and category-code organisational structures; `F0006D` holds translations.
- **Account (F0901)** – one row per account. Three ways to name an account: the **short account ID** (`AID`, system-assigned, never changes, 8 characters), **business unit.object.subsidiary** (`MCU.OBJ.SUB`), and a free-form **third account number**. `AID` is the key shared by F0901, F0902, F0911 (and F03B117). If accounts are renumbered, R09806 pushes the new MCU/OBJ/SUB from F0901 onto F0902/F0911, so join on `AID`, not on object.
- **Level of detail** on the account (1–9; 1–2 company and business unit totals, 3 = assets/liabilities/revenue/expense, 8–9 job-cost posting accounts) drives roll-ups.
- **Posting edit code** on the account: blank = posts, subledger optional; `B` budget ledgers only; `I` inactive; `L` subledger and type required (detail); `S` subledger required, posted in summary; `M` machine-generated only; `N` non-posting (title); `U` units required; `X` subledger must be blank.
- **Subledger** (`SBL`) + **subledger type** (`SBLT`) add a second analysis dimension without new accounts. Hard-coded types and the master they validate against: `A` Address Book (F0101), `C` Business Unit (F0006), `E` Asset (F1201), `I` Item (F4101), `J` Change request (F5301), `L` Lease (F1501), `O` Sales order (F4201), `S` structured (F0907), `W` Work order (F4801); `X`, `Y`, `Z` are user-defined. Subledgers never add rows to F0901; they add rows to F0911 and, depending on the posting edit code, to F0902.
- **Fiscal calendar (F0008)** – period end dates per date pattern and fiscal year. G/L dates map to fiscal year (`FY`), period (`PN`) and century (`CTRY`) through the company's pattern; 52-period accounting uses F0008B and F0902B.

### 2.2 Core ledger tables

| Table | Name | Grain | Key from the guides' composite-key appendix | Notes |
|---|---|---|---|---|
| F0901 | Account Master | one per account | `AID`† | account definitions; `F0901D` translations |
| F0902 | Account Balances | account × fiscal year × ledger type × subledger/type (× currency when posting by currency) | `GBAID, GBCTRY, GBFY, GBFQ, GBLT, GBSBL, GBSBLT, GBCRCD` | net posting per period plus prior-year net (`APYN`) and prior-year-end cumulative (`APYC`); budget fields `BORG` (final), `BREQ` (requested), `BAPR` (approved) |
| F0911 | Account Ledger | one row per journal line per ledger type | `GLDCT, GLDOC, GLKCO, GLDGJ, GLJELN, GLLT, GLEXTL` | every posted and unposted G/L line from every module |
| F0011 | Batch Control Records | one per batch | batch number `ICU` + batch type `ICUT`† | status, totals; history in F00119 |
| F0012 | Automatic Accounting Instructions | AAI item × company | prefix `KG` (`KGMCU, KGOBJ, KGSUB`) | account lookup rules |
| F0025 | Ledger Type Master | ledger type | | balancing rules, attached units ledger |

**F0902 facts**: one record per account/ledger type/subledger/subledger type/fiscal year; period buckets are net postings (period columns `AN01`–`AN14`†). Balance-sheet balance at period *n* = `APYC` + periods 1…*n*; income-statement accounts start each year at zero (the year-end close rolls them into retained earnings, AAI `GLG4`) so year-to-date = periods 1…*n*. When a journal entry carries units, the units are stored on the same F0911 row but posted to a **separate F0902 record in the units ledger** paired with the amount ledger (AA→AU, BA→BU).

**F0911 facts**: stores the detail for both F0902 and (for fixed assets) F1202. With multiple currencies each transaction has **two rows – ledger `AA` (domestic) and `CA` (foreign)** – so always filter on ledger type or amounts double. Posted code `P` = posted to F0902. The post sets line extension `EXTL = 'AE'` on automatic-entry rows it creates (trade account offsets, intercompany, tax). Other fields named in the guides: `GLRCND` reconciled code and `GLR3` reference 3 (bank reconciliation), `GLALT1` (intercompany multicurrency), `ALTW` = `W` on pay-when-paid vouchers, `PM01`–`PM10` managerial-accounting posted flags (one per cost analyzer view), cost object fields and types (`ABR1…`/`ABT1…`), asset ID, subledger and type, tax explanation code / tax rate area / tax item.

**Ledger types (UDC 09/LT)** referenced in the guides: `AA` actual amounts · `AU` actual units · `BA` budget amounts · `BU` budget units · `CA` foreign currency amounts · `XA` alternate currency (detailed currency restatement) · `AZ` cash basis · `PA`/`PU` purchasing commitment amounts/units · `JA` reserved for Job Cost budgets · `AC` consolidation / balance-restatement ledger · stock-valuation ledgers (for example `FI`, `LI`) and user-defined ledgers. Budget-only accounts (posting edit code `B`) accept ledger types beginning with B, J, K, L, M, N, O or U. Fixed-asset depreciation books are additional ledger types in F1202.

### 2.3 Batches, documents and posting

Every financial transaction belongs to a **batch** (F0011) and is identified by a **document**: number (`DOC`), type (`DCT`), document company (`KCO`), and for A/P and A/R a pay item (`SFX`). The first letter of a document type shows its origin: `P` accounts payable, `R` accounts receivable, `J` general accounting, `I` inventory, `O` purchasing, `S` sales, `T` payroll.

**Post (R09801) in order**: selects approved batches in F0011 → validates accounts, business units, G/L dates, intercompany setup and balance → creates automatic entries → updates F0018 taxes → sets posted code `D` on the subsystem ledger rows (F0411, F03B11, F0413/F0414, F03B13/F03B14), posts to F0902 and sets posted code `P` on F0911 → sets the batch to `D` (posted) or `E` (error) → optionally launches fixed-asset post (R12800 → F1202), 52-period post, detailed currency restatement (XA), cash-basis entries (AZ), burdening (F52G11/F52G02).

Batch status values: `P` pending, `A` approved, in use, `E` error, `D` posted. Only approved batches post. Integrity reports compare F0011 with F0911/F0411/F03B11 and F0911 with F0902 (work tables F007021W, F007032W, F097001W, F097021W, F097031W, F097041W, F09706W).

**Batch types (UDC 98/IT; post version by type in 09/PV)**

| Type | Content | Type | Content |
|---|---|---|---|
| `G` | General accounting journal entries | `IB` | A/R invoices |
| `D` | Allocations | `RB` | A/R receipts and adjustments (also unapplied cash, chargebacks, deductions) |
| `V` | A/P vouchers | `DB` | A/R drafts |
| `K` | A/P automatic payments | `N` | Inventory transactions |
| `M` | A/P manual payments with voucher match | `O` | Purchase order / contract entries |
| `W` | A/P manual payments without match | `NC` | Frozen cost update |
| `#` | Payroll vouchers | `ST` | Interbranch sales transfer |
| `E` | Asset transfer; `AR` asset revaluation | `0` | Manufacturing |
| `1`, `2B`, `/` | Real estate billing batch, tenant invoices, real estate vouchers | `JG`, `JI`, `JO` · `XX` · `X` | Joint venture journal entries, invoices, overhead entries · detailed currency restatement · depreciation (document type `DP`) |

**Document types**

| Area | Original documents | Matching documents (cannot exist alone) |
|---|---|---|
| G/L | `JE` journal entry · `JA` allocation · `JX` unrealised gain/loss · `AE` automatic entry (created by the post) · `PZ`/`MZ`/`TZ` cash-basis entries | |
| A/P | `PV` voucher · `PR` recurring voucher · `PL` logged voucher · `PD` debit memo · `PM` manual voucher created together with its payment · `P1` draft | `PK` automatic payment · `PN` manual payment · `PT` electronic funds transfer · `PO` void payment · `PE` change to voucher amount / void · `PG` payment gain/loss |
| A/R | `RI` invoice · `RM` credit memo · `RR` recurring invoice · `RB` chargeback · `RF` delinquency fee · `RU` unapplied receipt · `R1` draft · `R5` deduction · `NP` partial NSF · real estate `RD`, `RH`, `RJ`, `RL`, `RN`, `RT` | `RC` receipt · `RO` void receipt · `RS` spread (credit memo applied) · `RV` insufficient funds · `RL` logged receipt · `RR` rounding record · `RG` receipt gain/loss · `RK` journal entry per receipt batch |

**Payment status (UDC 00/PS)** – same field on vouchers and invoices: `A` approved for payment · `H` hold (sites add more hold codes) · `P` paid in full · `R` retainage · `%` withholding applies · `#` payment in process · `Z` selected for manual payment · `Y` workflow in progress · `F` workflow rejected · drafts: `D` accepted, `E` expired not collected, `G` deposited not due.

### 2.4 Accounts Payable

| Table | Name | Grain / key | Use |
|---|---|---|---|
| F0401 | Supplier Master | `AN8` | supplier defaults, YTD and prior-year vouchered amounts |
| F0411 | Accounts Payable Ledger | voucher pay item: `RPDOC, RPDCT, RPKCO, RPSFX` | gross (`AG`), open (`AAP`), foreign gross/open (`ACR`/`FAP`), pay status (`PST`), due date (`DDJ`), G/L date (`DGJ`), supplier invoice (`VINV`), purchase order reference (`PO`/`PDCT`/`PKCO`), G/L offset (`GLC`), business unit, approver, category code 07 (1099), `PYWP` pay-when-paid |
| F0413 | A/P Matching Document | payment: `RMDOCM, RMDCTM, RMPYE` | one row per payment (payment number, type, payee, bank account, amount, date) |
| F0414 | A/P Matching Document Detail | payment × voucher pay item: `RNDOC, RNDCT, RNDCTM, RNKCO, RNSFX` | amount of each voucher pay item paid; carries the historical exchange rate |
| F04571 / F04572 / F04573 | A/P Payment Processing header / summary / detail | payment control group | work tables while a payment group is being written; F0413/F0414 are created only at update |
| F04572OW | A/P Payment Tape | | EFT output |
| F0411Z1 (+F0911Z1) | Voucher Transactions – Batch Upload | EDI keys | inbound vouchers; `F0411Z1T` adds voucher-match-automation data |
| F0411A / F0413A / F0414A | "As of" copies | | date-effective snapshot for as-of reports |
| F0411P / F0413P / F0414P | Purge copies | | paid, zero-open items purged before a G/L date |
| F0450 | Payee Control | | audit of changes to payee/bank fields |
| F0417 | A/P Payments – Default Print and Update | payment instrument | print/update program per instrument |
| F0030 | Bank Transit Master | | G/L bank, supplier bank, next payment number |

**Flow**: voucher entry writes F0411 (unposted) + F0911 distribution → post marks F0411 `D`, creates the `AE` trade-account offset through AAI `PC` + G/L offset, updates F0902 → payment (automatic: create payment control group → write → update; or manual) creates F0413 + F0414 and reduces `AAP` on F0411 → payment post writes cash/discount entries. The **payment ID** is the internal key joining F0413 to F0414. Voiding creates `PO` (payment) or `PE` (voucher) records rather than deleting.

### 2.5 Accounts Receivable

| Table | Name | Grain / key | Use |
|---|---|---|---|
| F03012 | Customer Master by Line of Business | `AN8` + company | credit limit, collection/statement settings, billing instructions, category codes |
| F03B11 | Customer Ledger | invoice pay item: `RPDOC, RPDCT, RPKCO, RPSFX` | every invoice, credit memo, chargeback, deduction, unapplied receipt, draft; gross/open amounts, pay status, due date, discount; `F03B11T` tag table |
| F03B112 | Invoice Revisions | | audit trail of gross-amount changes |
| F03B13 | Receipts Header | one per receipt/draft (payment ID) | receipt number, date, G/L date, bank account, payor, amount, draft status |
| F03B14 | Receipts Detail | receipt × invoice pay item | amount applied, discount, write-off, chargeback, deduction; receipt document type in the matching document type field; type code `D` on draft-stage rows; `PDLT` paid-late code |
| F03B13Z1 | Electronic Receipts Input | bank file rows | automatic receipts staging (R03B551 creates F03B13/F03B14) |
| F03B11Z1 (+F0911Z1) | Batch Invoices | EDI keys | inbound invoices |
| F03B15 | Credit and Cash Management | customer × company (parent and child) | open-activity summary refreshed by Credit Analysis Refresh |
| F03B16 / F03B16S | A/R Statistical History / Summary | customer × period | sales, payments, days late, write-offs (`MWO`), bad debt (`BDBT`) from Statistics History Update |
| F03B20 / F03B21 | A/R Notification History / Detail | statement or notice / invoice on it | statements and delinquency notices |
| F03B22 / F03B23 | A/R Fee Journal History / Detail | | delinquency fees |
| F03B40 / F03B41 / F03B42 | Deduction Management / deduction activity / activity master | | deduction (`R5`) resolution |
| F03B31 | Customer Activity Log | | collection activities |
| F03B08 | Credit/Collection Fiscal Date Patterns | | periods for statistics |
| F03B115–F03B119 | Revenue Recognition schedule, invoice, G/L info, audits | | deferred revenue/COGS by invoice pay item and G/L line |
| F03B571, F03B575, F03B57OW | Auto Debit batch control, invoice select, formatted tape | | automatic debits |
| F47111–F47114 | EDI Lockbox header / detail tables | | inbound lockbox |
| F03B11P / F03B13P / F03B14P | Purge copies | | |

**Flow**: invoice entry (or Sales Update, contract/service billing, real estate billing) writes F03B11 + F0911 → post sets `D`, creates the A/R trade offset (AAI `RC` + G/L offset) → receipt entry writes F03B13 (one header) and F03B14 (one row per invoice pay item paid, or a row that *generates* an `RU`, `RB` or `R5` invoice record in F03B11) and reduces the open amount → receipt post writes cash, discount (`RKD`), write-off (`RA`xx) entries. Receipt records stay unposted until the receipt batch (`RB`) is posted, while generated `RU`/`RB`/`R5` invoice rows are created already posted (`D`). All receivables from sales are posted to the **sold-to** address number.

Cash-basis accounting (ledger `AZ`) is derived after the fact: the system marks F0414 and F03B14 rows (`ALT6 = P`) once cash-basis entries exist.

### 2.6 Multicurrency and tax

- **F0013** Currency Codes (decimals per currency) · **F0015** Currency Exchange Rates (rates and conversion method per currency pair and effective date) · **F0015Z1** external rates · **F1113** restatement rates · **F1114** company conversion parameters · **F11151** cross rates.
- Transaction rows carry currency code (`CRCD`), exchange rate (`CRR`), mode (`CRRM`: domestic or foreign entry), domestic amounts (`AG`/`AAP`) and foreign amounts (`ACR`/`FAP`). F0911 keeps domestic in the `AA` row and foreign in the `CA` row. Posting balances by currency adds the currency code to the F0902 key. Amounts are stored **without a decimal point**; the decimals come from the currency (F0013) or the data dictionary display decimals.
- Realised gains/losses are written when payments/receipts are posted (`PG`/`RG`); unrealised gains/losses are journal entries of type `JX`.
- **F4008** Tax Areas (rates by tax rate/area and effective date) · **F40081** alternate tax rate/area · **F0018** Taxes – one row per taxed pay item/G/L line, written by the post according to the "update tax file" processing option (so it can be incomplete by design) · **F0018R** Tax Reconciliation Repository – tax by G/L account and pay item, built by R0018R after posting. Tax explanation code and tax rate/area sit on F0411/F03B11 pay items and are copied to F0911.

### 2.7 Fixed Assets

| Table | Name | Notes |
|---|---|---|
| F1201 | Asset Master File (prefix `FA`) | asset number, description, account coding (cost and accumulated-depreciation accounts), category codes, location, parent; purge copy F1201P |
| F1202 | Asset Account Balances File (prefix `FL`) | balance per asset × account × ledger type × fiscal year (`FLCTRY`, `FLFY`, `FLLT`, `FLAPYC`, `FLAPYN`…); also depreciation method and life per ledger |
| F1204 | Location Tracking Table | key `FMNUMB, FMEFTB, FMAL, FMNNBR`; current, planned and historical locations |
| F12002 / F12003 | Default Accounting / Depreciation Constants | defaults by company and asset cost account |
| F12851 / F12852 / F12853 / F12854 | Depreciation rules / annual rules / formulas / period spread rules | user-defined depreciation |
| F1208 | Units of Production Schedule Master | |
| F12141 | Disposal Account Rules | |
| F1206, F1205, F1212, F1216, F1215 | Licenses, messages, parent history, specification data and cross-reference | shared with CAM |

F0911 is the audit trail for **both** F0902 and F1202: journal lines whose account falls in the `FX` AAI range are posted to F1202 by R12800 (post code tracked separately), so an asset's cost history = F0911 rows carrying the asset ID. If the account master is renumbered, a global update realigns F1202 by short account ID.

### 2.8 Other financial subsystems

- **General accounting extras**: allocations F0912 (recurring), F0912A (indexed), F0912B (variable), F09123/F09123A (advanced variable numerator) · bank statements entered manually F0916 header / F0917 detail · automatic bank statements: staging F09610/F09611 → F09616/F09617, cross-references F09621/F09622 · reconciliation work table F0911R (rebuilt each refresh) · budget upload F0902Z1 · budget forecasting F1403 basis, F1404/F14041 results, F1406 growth patterns · cash forecasting F09521 rules, F09522 data, F09525 bank accounts · statement of cash flow F10520 · multisite consolidations F1001/F1002/F1003 (+F1001Z1/F1002Z1 inbound), F10430/F10470/F10471 structures and elimination rules · burdening F52G11 detail, F52G02 summary, F48S80–F48S85 segments, computation methods, base rules, pools, rates · intercompany hub F09190 · data relationships F00421/F00422 · pay-when-paid groups F03B470.
- **Advanced Cost Accounting (16)**: F1602 Cost Analyzer Balances (F0911 summarised per view 1–10 with cost objects), F1602Z1 external balances, F1632 Driver Balances (+F1632Z1), F1611 Cost Calculation Transactions (assignment audit trail), F1620 Cost Object Types, F1609 constants, F1642/F16421 rate master. Cost objects are entered on vouchers, invoices, journal entries, purchase and sales orders, work orders and freight (F4981 Freight Audit History).
- **Expense Management (09E)**: F20111 Expense Report Header, F20112 Expense Report Detail (key `EXRPTTP, EXRPTNUM, EMPLOYID, WRKSTNID, DTECRT` + line), F09E150 Credit Card Transaction Interface (status 0 available, 1 applied), F0075 Credit Card Information, F20103 Employee Profile, F20104 Group Profiles, F20106 Account Mapping, F20107 Business Purpose History, F09E105 Tax Mapping, F09E108 Policy Edit Rules, F09E109 Expense Category Setup, F09E110 Audit Selection Rules, F09E114 Exchange Rate Identifiers, F09E118 Type Mapping, F09E119 Routing Rules, F09E120 Routing History Log. Manager/designee hierarchy is in F0150 structure type `ERS`.
- **Joint Venture Management (09J)**: F09J30 Joint Venture Master, F09J0006 JV business unit attributes, F09J10 Legal Entities, F09J20/F09J21/F09J22 Division of Interest header, detail, assignment rules, F09J01 Distributable Accounts, F09J11 Joint Venture Account Ledger (loaded from F0911), F09J12 Joint Venture Distribution Detail (partner shares, with links to the resulting journal entry, A/R invoice and A/P voucher), F09J40 Cash Call Definition (status 30 invoiced, 99 closed) and F09J41 Cash Call Ledger, overhead F09J50–F09J57, F09J100 overhead calculation, F09J60 escalation index, F09J70/F09J71 operational status history.
- **1099 / T5018 year-end**: F045143 1099 A/P Worktable, F045141 1099 G/L Worktable, F04514 merged worktable, F04515OW electronic media, F045145 securities identification, F0451401 1099 supplier information; Canada T5018: F046141 workfile, F04614 tax file. These are rebuilt each year from F0411/F0413/F0414 or F0911.

### 2.9 AAIs you will meet in the data

Financial AAIs (F0012) are looked up by item + company, falling back to company 00000. Items named in the guides: `GLG`x general ledger account ranges (GLG4 retained earnings; GLG6/GLG11–GLG13 revenue/expense ranges†), `PC`xxxx A/P trade (xxxx = G/L offset), `PB` A/P bank, `RC`xxxx A/R trade, `RB` A/R bank, `RKD` discounts taken, `RA`xx write-offs, `RN` deduction suspense, `PT`/`RT`xxxx tax accounts, `ICCC`/`ICH` intercompany, `FX` fixed-asset account range, `PBC`xx accounts posted by currency. The G/L offset code on a voucher or invoice pay item is what selects the trade account, which is why trade balances can be analysed by offset.

### 2.10 Analysis recipes

- **Trial balance / financial statements**: F0902 ⨝ F0901 on `AID` (⨝ F0006 on `MCU`), filter fiscal year and ledger type `AA`; balance sheet = `APYC` + periods; P&L = periods only. Use level of detail and object ranges (or business unit category codes) for grouping.
- **G/L detail**: F0911 with ledger type `AA`, posted code `P`, G/L date range; join F0901 on `AID`. Exclude nothing by document type unless asked; identify system-generated lines with `EXTL = 'AE'`.
- **Budget vs actual**: F0902 ledger `BA` vs `AA` for the same `AID`/fiscal year; annual budgets in `BORG`/`BREQ`/`BAPR`.
- **Open payables / ageing**: F0411 where open amount ≠ 0, grouped by supplier (`AN8` → F0101), aged on due date; split by pay status (`H` holds). Payment history: F0413 ⨝ F0414 on payment ID, then F0414 → F0411 on `DOC, DCT, KCO, SFX`.
- **Open receivables / ageing**: F03B11 where open amount ≠ 0; `RU` rows are unapplied cash (negative), `RB` chargebacks, `R5` deductions. Cash application: F03B13 ⨝ F03B14 on payment ID, F03B14 → F03B11 on the invoice key. DSO and late-payment statistics are already summarised in F03B16/F03B16S; credit exposure in F03B15.
- **Subledger to G/L reconciliation**: sum F0411 or F03B11 by G/L offset and compare with the F0902 balance of the trade account from AAI `PC`/`RC`; trace by batch number/type through F0011.
- **Spend or revenue by dimension**: F0911 by subledger/type (`A` address number, `W` work order, `E` asset, `C` business unit, `O` sales order), by business unit category codes, or by cost objects.
- **Unposted or stuck transactions**: F0011 batches not `D`; F0911 rows with blank posted code.

### 2.11 Financial tables named in the guides, by guide

- **Financial Management Fundamentals**: F0006, F0006D, F0006S, F0006Z2, F0007, F0008, F0009, F0010, F0010Z, F0011, F00119 G/L Batch Status History, F0012, F0012D, F0014, F00141, F00142, F00143, F00144, F00147, F00090–F00092, F00421 Column Relationships, F00422 Value Relationships, F0030, F0050, F0050A, F007101, F007111, F03B470, F0901, F0901D, F0901WS, F0907 Chart of Accounts Format, F0909 Chart of Accounts – Reference File, F09190, F5201 Contract Master (data relationships).
- **General Accounting**: F0902, F0902B, F0902Z1, F0911, F0911R, F0911Z1, F0912, F0912A, F0912B, F09123, F0916, F0917, F09218 Online Consolidations Set-up, F09505/F095051 bank tape work files, F09521, F09522, F09525, F09610, F09611, F09616, F09617, F09621, F09622, F1001, F1001Z1, F1002, F1002Z1, F1003, F10430, F10470, F10471, F10520, F1403, F1404, F14041, F1406, F48S80–F48S85, F52G02, F52G11, F52G60 Actual Rate Calculation.
- **Accounts Payable**: F0401, F0401M Multiple Vendor Bank Account Status, F0411 (+A, P, Z1, Z1T), F0413 (+A, P), F0414 (+A, P), F0417, F0450, F04571, F04572, F04572OW, F04573, F04614, F046141, F47041/F47042/F47044 EDI invoice inbound, F47056/F470561/F470562/F470563/F47057 EDI payment order outbound.
- **Accounts Receivable**: F03012, F03012A, F03B08, F03B11 (+T, Z1, P), F03B112, F03B115–F03B119, F03B13 (+Z1, P), F03B14 (+P), F03B15, F03B16, F03B16S, F03B20–F03B23, F03B25 Delinquency Policy (+F03B26, F03B27), F03B28 Letter Text, F03B29 Credit Insurance, F03B31, F03B40–F03B42, F03B465 A/R Netting Workfile, F03B50 Receipt Application Algorithm Execution Lists, F03B571, F03B575, F03B57OW, F03B672 Draft Remittance Work File, F03B920/F03B920C credit reporting, F47111–F47114, F74412 Customer/Supplier Balance Worktable.
- **Fixed Assets**: F1201, F1201P, F1201Z1, F1202, F1204, F1205, F1206, F1208, F12002, F12003, F12090 supplemental types, F12141, F1212, F1215, F1216, F12851–F12854 (+D demo copies).
- **Multicurrency / Tax**: F0013, F0015, F0015Z1, F1113, F1114, F11151, F0018, F0018R, F0018T Intrastat, F4008, F40081, F0010T Company Constants Tag, F74101 additional address book VAT data.
- **Composite keys for hundreds of further tables** are listed in the Base Currency Conversion guide, Appendix C; the keys quoted in these reference files come from it.
