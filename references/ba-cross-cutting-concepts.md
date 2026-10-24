# Cross-Cutting Concepts Glossary

These mechanisms aren't specific to any one module — they show up, with the same underlying logic, in Financials, Procurement, Manufacturing, HCM, CRM, and beyond. Read this file when a question is really about one of these mechanisms rather than about a specific business process, or when you need to recognize that a module-specific question ("why did this AP voucher post to the wrong account") is actually a cross-cutting setup question in disguise. Items marked as verified were checked on a reference system; confirm them on ABC's own data with `query_jde_database` (method in topic `bd-query-method`).

## AAIs (Automatic Accounting Instructions)

**What they are:** rules that map a transaction (voucher, invoice, receipt, depreciation run, payroll DBA, etc.) to the correct GL account, so the user never manually specifies an offset account. Defined per company (or company 00000 as a default) and, depending on the AAI, per business unit/object/subsidiary.

**Master table: F0012** (DTA schema). Key columns verified on a reference system: `KGITEM` (the AAI item code), `KGSY` (system code, e.g. "04"=AP), `KGCO` (company), `KGOBJ`/`KGSUB` (the GL object.subsidiary it resolves to), `KGDL01` (description).

**Naming convention — the item code's first letter tells you the system:**
- **P**xxx — Accounts Payable (financials.md). E.g. PC=payables trade/class account, PB=payables bank account. The actual object accounts these resolve to are company-specific: read them from F0012 for the company in question.
- **R**xxx — Accounts Receivable
- **G**Txxx / general GA items — General Accounting
- **PT**xxxx / **RT**xxxx / **GT**xxxx — VAT tax AAIs for AP/AR/GA respectively; **PTVATD** specifically for Procurement VAT
- 48xx series — Contract and Service Billing (4811 Actual Revenue, 4815 Tax Liability, 4831 Accrued Revenue, 4841 WIP / 4842 COGS, 4871-4874 Revenue/Invoice Margin, 4851-4852 Not-to-Exceed Offsets)
- Procurement AAI *tables* (not single items) cover PO entry, receipts/voucher match, variances, tax liabilities, receipt routing, landed costs, zero-balance adjustments

**When a question is really about AAIs:** any "why did this post to the wrong account" or "how do I redirect where X posts" question, across any module, is an AAI question — go to F0012 (or the relevant guide's AAI section) rather than the transaction-entry program.

## UDCs (User Defined Codes)

**What they are:** the validated-value lists behind nearly every code field in JDE (document types, statuses, category codes, reason codes, etc.) — org-customizable within a system/type pairing.

**Master table: F0005** (CTL schema). Key columns verified on a reference system: `DRSY` (system code, e.g. "00"=shared/cross-application), `DRRT` (the "record type" — the second half of the UDC's system/type identifier, e.g. "LC"), `DRKY` (the actual code value), `DRDL01`/`DRDL02` (description lines).

**Notable UDC tables that recur across guides:**
- **00/LC** — Localization country codes (verified on a reference system: AR, AT, AU, BE, BG, BR, BU, CA, CH... matches the country-server mechanism in topic `ba-localizations`)
- **00/EX** — Tax explanation codes (S=sales, U=use, V=VAT, C=VAT+sales, B=VAT+use, E=exempt — user-extendable)
- **01/WO** or **01/WT** — Who's Who category codes (Address Book contacts)
- **31/RS** — Kanban replenishment source type
- **34/QT** — MPS/MRP quantity types (explicitly warned against modifying — planning calculations depend on it)
- **79A/OT**, **79A/FS** — Environmental organization type/size (EAR, health-safety-environment.md)

**Category codes vs. UDCs:** category codes (e.g. Address Book category code 23, or item category codes on F4101) are themselves validated against a UDC table you define — "category code" is the field, "UDC" is the value list behind it. Category code 07 on Address Book is reserved for AP 1099 reporting unless 1099 isn't used.

## Next Numbers

**What they are:** the auto-numbering sequences JDE assigns to new documents/records (vouchers, invoices, work orders, address book numbers, etc.), configured per system, and sometimes per company/fiscal year.

**Master table: F0002** (CTL schema). Key columns verified on a reference system: `NNSY` (system code), `NNUD01` through `NNUDnn` (the actual next-number sequences maintained for that system — a system can have several parallel sequences for different document types).

## Country Server / Localization Mechanism

Fully covered in topic `ba-localizations` — the short version: localized behavior is isolated into separate country-specific programs, switched on via a localization country code (UDC 00/LC) set in user display preferences, and always layered *on top of* base-module setup rather than replacing it.

## Business Unit / Chart of Accounts Structure

**Master tables:** F0006 (Business Unit Master, DTA, column prefix `MC` — verified on a reference system) for the business unit itself; the chart of accounts sits in F0901 (not yet queried in this pass). Account structure is Business Unit.Object.Subsidiary — covered in depth by Financial Management Fundamentals (topic `ba-financials`).

## Company Constants / Country Constants

- **F0010** (Company Constants, DTA, column prefix `CC`) — verified on a reference system (`CCCO`, `CCNAME`, `CCALTC`...).
- **F0070** (Country Constants, DTA, column prefix `CK`) — verified on a reference system (`CKCTR` country code, `CKADID` address format template, `CKDSEP` decimal separator). This is the table the Localizations guides' address-format/country-constants setup steps actually populate.

## Program/Object ID naming convention (fast disambiguation — no fetch needed)

Verified on a reference system (P4310, R4304010, B4300310, and F4311 all exist together under system code 43 — Procurement): every JDE object's ID starts with a letter indicating its type, which usually tells you what a program *is* without needing to look it up:

- **P**xxxx — interactive application/program (a form/screen a user works in, e.g. P4310 = Purchase Order Entry)
- **R**xxxxx — report or batch process (a "UBE," Universal Batch Engine — runs without user interaction once submitted, e.g. R4304010 = Voucher Match Automation Driver)
- **B**xxxxxxx — business function (reusable business logic called by programs/reports, not run directly by a user, e.g. B4300310)
- **F**xxxx — table (the database table itself, e.g. F4311 = Purchase Order Detail)
- **T**xxxx — table conversion (a one-time or repeatable data-migration/conversion program)
- **N**xxxxx — named event rule / business function library object

The digits after the letter are usually the system code (2-digit, e.g. "43"=Procurement, "04"=AP, "03B"=AR, "42"/"41"=Sales/Inventory) followed by a sequence — so a program ID alone often tells you both *what kind of object it is* and *which system owns it*, which is enough to answer "what does R4304010 do" at a useful level (a Procurement/AP batch report) even before fetching anything. Still fetch/search for the specific behavior — the prefix tells you the shape, not the content.

**System codes (verified on a reference system)** (query any program's owning system via `SELECT SIOBNM, SISY FROM OL920.F9860 WHERE SIOBNM = '<program>'` if one below isn't listed):

| Code | System | Example |
|---|---|---|
| 00 | Foundation / General Accounting (chart of accounts) | P0901 |
| 03B | Accounts Receivable | P03B11 |
| 04 | Accounts Payable | P0411 |
| 07 | Payroll | P07350 |
| 12 | Fixed Assets | P1201 |
| 15 | Real Estate Management | P1502 |
| 17C | Capital Asset Management / Plant & Equipment | P1701 |
| 31 | Shop Floor Management / Manufacturing | P3111 |
| 42 | Sales Order Management | P4210 |
| 43 | Procurement | P4310, R4304010 |
| 43B | Voucher Match (straddles AP/Procurement) | P4314 |



Module reference files (e.g. topic `ba-financials`'s AP section) explain AAIs/UDCs/next-numbers *as they apply to that module's specific setup steps*. This file is for when the question crosses modules, or when you need the general mechanism (e.g. "how do AAI lookups actually resolve" rather than "what AAI item does AP use for the trade account"). When in doubt, check both.
