> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.


# JD Edwards EnterpriseOne data architecture

How JDE EnterpriseOne 9.2 business data is organised, so that the right tables can be found, joined, filtered and interpreted for extraction and analysis. Built from 57 Oracle implementation guides (Foundation, Financials, Supply Management, Supply Chain Management and Manufacturing, Customer Relationship Management, Asset Lifecycle Management).

## How to use this skill

1. **Find the module.** Read the table name (Part 0.1) or the business question, then go to the matching part: 1 Foundation · 2 Financials · 3 Supply Management · 4 Supply Chain and Manufacturing · 5 CRM and Service · 6 Asset Lifecycle · 7 Health and Safety / Apparel. Each part gives the data model, core tables with keys, the codes that drive filtering, the process-to-table flow, analysis recipes and the tables named in each guide.
2. **Confirm columns before writing SQL.** The guides describe tables, keys and data items, not full column lists. When a JDE schema or query tool is connected, look up the table's columns and its two-character prefix first (query pattern in 0.9); otherwise ask for the table layout. Never invent a column name. If a table or relationship isn't in this skill at all, that's also what the connector is for (0.9) — don't fill the gap from general JDE knowledge presented as fact.
3. **Apply the storage conventions** (Part 0.3), and scale amounts/quantities correctly (Part 0.10 — currency display decimals for amounts, Data Dictionary display decimals for everything else; never trust the SQL column's own precision/scale for this). Also apply Julian dates, padded strings, UDC decoding, ledger-type and status filters.
4. **State the assumptions** in the answer: environment/schema, ledger type, posted vs unposted, which statuses count as open, where closed lines live, which decimal convention was applied to any amount/quantity and where it came from.
5. For how a process works functionally (setup, programs, processing options) use the JDE functional guidance; this skill is about where the data lands.

**†** marks standard JDE conventions that these guides do not spell out. Treat them as likely and confirm in the data dictionary or with the schema tool.

## Part 0. Rules that apply to every module

### 0.1 Reading a table name

`F` + system code + sequence, optional suffix. System 00 foundation, 01 address book, 03B A/R, 04 A/P, 09 G/L, 12 fixed assets, 13 equipment, 15 real estate, 17 service, 30/31 manufacturing, 34 planning, 40–42 distribution and sales, 43 procurement, 45 pricing, 46 warehouse, 47 EDI, 48 work orders, 49 transportation, 55–59 customer custom tables. Suffix `Z1` = inbound/outbound staging, `T` = tag (extension, same key), `W`/`WF`/`UI` = work file, `A` = as-of/audit, `P`/`S` = purge copy, `D` = translation, trailing `9`/`H` = ledger/history. Full list in Part 1.

Kinds of table, and how to treat them:

| Kind | Examples | Use in analysis |
|---|---|---|
| Master | F0101, F0006, F0901, F4101, F4102, F1201, F1501B | dimensions; join for descriptions and category codes |
| Setup / rules | F0010, F0012, F4095, F40203, F40205, F0005 | decode behaviour; rarely reported on |
| Transaction (open/working) | F4211, F4311, F4801, F0411, F03B11 | facts; apply status and open-amount filters |
| Ledger / history | F0911, F4111, F42119, F42199, F43199, F0018 | facts over time; apply date, ledger type, document type filters |
| Balance / summary | F0902, F1202, F41021, F41112, F4229, F03B16, F1602 | already aggregated; do not re-aggregate from detail unless reconciling |
| Staging, work, purge | …Z1, …W, …P | exclude unless the question is about interfaces or archives |

### 0.2 Columns = table prefix + data-item alias

Every column is a two-character table prefix followed by a data dictionary alias: `GLDOC` = F0911 + `DOC`, `SDDOCO` = F4211 + `DOCO`. The same alias means the same thing in every table, which is what makes joins predictable. Prefixes confirmed by the guides (composite-key appendix and field references): F0911 `GL` · F0902 `GB` · F0012 `KG` · F0411 `RP` · F0413 `RM` · F0414 `RN` · F03B11 `RP` · F0018 `TD` · F1201 `FA` · F1202 `FL` · F1204 `FM` · F4105 `CO` · F4106 `BP` · F4111 `IL` · F41112 `IN` · F4115 `IH` · F4074 `AL` · F4201 `SH` · F4211 `SD` · F42199 `SL` · F49211 `UD` · F4311 `PD` · F43121 `PR` · F43199 `OL` · F4801 `WA` · F31122 `WT` · F3460 `MF` · F4812 `WD` · F0911Z1 `VN` · F0411Z1 `VL` · F03B11Z1 `VJ` · F0101Z2 `SZ`. Others in common use†: F0101 `AB` · F0111 `WW` · F0006 `MC` · F0901 `GM` · F0010 `CC` · F0401 `A6` · F03012 `AI` · F03B13 `RY` · F03B14 `RZ` · F4101 `IM` · F4102 `IB` · F41021 `LI` · F4301 `PH` · F3111 `WM` · F3112 `WL` · F3002 `IX` · F3003 `IR` · F0005 `DR`.

**Aliases worth knowing** (all appear in the guides)

| Theme | Aliases |
|---|---|
| Who / where | `AN8` address number · `CO` company · `MCU` business unit or branch/plant · `AID` short account ID · `OBJ`/`SUB` object/subsidiary · `SBL`/`SBLT` subledger/type · `ITM`/`LITM`/`AITM` short/2nd/3rd item number · `LOCN` location · `LOTN` lot · `NUMB` asset number · `PA8` parent address |
| Financial document | `DOC` document number · `DCT` document type · `KCO` document company · `SFX` pay item · `ICU`/`ICUT` batch number/type · `DOCM`/`DCTM` matching (payment or receipt) document number/type · `PYID` payment ID · `VINV` supplier invoice · `PO`/`PDCT`/`PKCO` purchase order reference · `ODOC`/`ODCT`/`OKCO` original document · `JELN` journal line · `EXTL` line extension |
| Order | `DOCO` order number · `DCTO` order type · `KCOO` order company · `SFXO` order suffix · `LNID` line number · `LNTY` line type · `LTTR`/`NXTR` last/next status · `SRST` work-order status · `OPSQ` operation sequence · `KIT`/`TBM` parent item/BOM type |
| Dates | `DGJ` G/L date · `DIVJ` invoice date · `DDJ` due date · `DSVJ` service/tax date · `TRDJ` order or transaction date · `DRQJ` requested · `PDDJ` promised delivery · `PPDJ` promised ship · `ADDJ` actual ship · `IVD` invoice date on orders · `DGL` G/L date on distribution tables · `EFTB`/`EFFF`/`EFFT` effective dates · `FY`/`PN`/`CTRY`/`FQ` fiscal year, period, century, quarter · `UPMJ` date updated |
| Amounts and quantities | `AA` ledger amount · `AG`/`AAP` gross/open (domestic) · `ACR`/`FAP` gross/open (foreign) · `ATXA`/`STAM` taxable/tax · `ADSC` discount available · `UORG` quantity ordered · `UOPN` open · `SOQS` shipped · `SOBK` backordered · `SOCN` cancelled · `AREC` amount received · `UPRC`/`AEXP` unit/extended price · `UNCS`/`ECST` unit/extended cost · `PQOH`/`HCOM`/`PCOM` on hand/hard/soft committed · `TRQT` transaction quantity · `UOM`/`UOM1` unit of measure |
| Codes | `LT` ledger type · `POST` posted code · `PST` pay status · `GLC` G/L offset · `GLPT` G/L class · `CRCD`/`CRR`/`CRRM` currency, rate, mode · `EXR1`/`TXA1` tax explanation, tax rate area · `AT1` search type · `MATC` receiver match type · `GENT` real-estate generation type |
| Audit | `USER` · `PID` program · `JOBN` workstation · `UPMJ` date · `UPMT`/`TDAY` time |

### 0.3 Storage conventions

- **Dates are Julian numbers in the form CYYDDD** (C = 0 for 19xx, 1 for 20xx; DDD = day of year). June 1, 2000 = 100153; June 1, 1999 = 099152. Zero means no date. Convert with† Oracle `TO_DATE(TO_CHAR(col + 1900000), 'YYYYDDD')` or SQL Server `DATEADD(day, CAST(col AS int) % 1000 - 1, DATEFROMPARTS(1900 + CAST(col AS int) / 1000, 1, 1))`, guarding `col > 0`. Filter on the raw Julian value so indexes are used. Times (`UPMT`/`TDAY`) are HHMMSS numbers†.
- **Amounts, quantities, costs and rates are stored without a decimal point.** Decimal places are implied: by the currency for amounts (F0013 display decimals: 2 for USD, 0 for JPY) and by the data dictionary display decimals for quantities, unit costs and unit prices (unit cost/price commonly 4). Divide by the right power of ten and confirm against one known document.
- **Fiscal period** comes from the company's date pattern (F0010 → F0008), not from the calendar month. Use `FY`/`PN`/`CTRY` on the row when present.
- **Strings are blank-padded**; blank (spaces), not NULL, means "no value". Business unit (`MCU`, 12 characters) is stored right-justified with leading blanks† and UDC keys likewise†, so trim before comparing or displaying. Company is 5 characters (`00001`), default company `00000`.
- **Coded values are UDCs.** Decode through F0005 (Part 1.4). Category codes are site-defined: read their descriptions.
- **Environments**: the same table exists once per environment data source (for example production, CRP/prototype, test)†. Confirm which schema to query; control tables (UDCs, next numbers) may sit in a different schema from business data†.
- **Nothing is physically deleted in the ledgers**: voids and reversals are extra rows (void payment `PO`, void receipt `RO`, reversing entries, receipt reversals with their own match type), so filter by document type/status instead of expecting rows to disappear.

### 0.4 The keys that connect everything

| Concept | Key | Where it appears |
|---|---|---|
| Address number | `AN8` | F0101 and every customer, supplier, employee, tenant, carrier reference (sold-to `AN8`, ship-to `SHAN`, payee `PYE`, parent `PA8`) |
| Business unit / branch-plant | `MCU` (company via F0006) | accounts, orders, item branch, work centers, buildings, jobs |
| Account | `AID` (or `MCU`+`OBJ`+`SUB`) | F0901, F0902, F0911, F1202, order lines charged to accounts |
| Item | `ITM` (+`MCU` for branch, +`LOCN`+`LOTN` for stock) | F4101/F4102/F41021 and every order, ledger, BOM, forecast row |
| Financial document | `DOC`+`DCT`+`KCO` (+`SFX` pay item) | F0411, F03B11, F0911, F0018, F4111 |
| Order | `DOCO`+`DCTO`+`KCOO` (+`SFXO`, `LNID`) | F4201/F4211, F4301/F4311, F43121, F43199, F42199, F4074, requisitions; work orders use `DOCO` alone |
| Batch | `ICU`+`ICUT` | F0011 and every posted transaction table |
| Asset / equipment | asset number | F1201, F1202, F1204, F1207, F1217, F4801, F0911 |
| Lease | `DOCO`+`LSVR` | F1501B and real-estate tables |
| EDI staging | `EDUS`+`EDBT`+`EDTN`(+`EDLN`) | all Z tables |

Order lines point to each other through related-order fields (sales ↔ purchase for transfer and direct ship, sales ↔ work order, purchase ↔ work order), and vouchers/invoices point back to the order through purchase-order or sales-order reference fields; F4080 and F54R20 are explicit cross-reference tables.

### 0.5 From operational transaction to general ledger

All modules post the same way: an operational table holds the business view (F4211, F43121, F4111, F3102, F1511B, F4812 …) → a subledger document is created in A/P (F0411) or A/R (F03B11) when money is owed → journal lines are written to **F0911** inside a batch (F0011) using automatic accounting instructions (financial AAIs in F0012; distribution/manufacturing AAIs in F4095 keyed by company, document type and G/L class) → the post updates **F0902** balances (and F1202 for assets, F0018 for tax). To reconcile, walk the chain by document number/type/company and by batch number/type.

### 0.6 Process map

| Process | Tables in order |
|---|---|
| Order to cash | F4201/F4211 → F41021 commitments → (F4600/F4611 pick) → ship confirm (F4111, F4215, F49211) → invoice / sales update → F42119 + F42199 + **F03B11** + F0911 → receipt F03B13/F03B14 |
| Procure to pay | (F43E01/F43E11 requisition) → F4301/F4311 (+F43199, commitments in F0902 `PA`/`PU`) → receipt **F43121** + F4111 + F41021 + F0911 → voucher match **F0411** → payment F0413/F0414 |
| Plan to produce | F3460 forecast + F4211 demand → MRP F3411/F3412/F3413 → F4801 work order (+F3111, F3112) or F4311 purchase order → issues/completions F4111 → F31122 labor → F3102 cost → F0911 |
| Record to report | F0911 (all sources) → post → F0902 → consolidations/allocations → statements |
| Acquire to retire | F4311/F0411 → F0911 with asset ID → F1201/F1202 → depreciation journals → disposal |
| Maintain | F1201/F1217 equipment → F1207 PM schedule → F4801 work order (+F3111, F3112) → costs in F0911 by subledger `W` |
| Lease to cash | F1501B/F15017 lease → F1502B and other billing masters → F1511B → F03B11 → receipts |
| Service to cash | F1721 contract / F1755 case / F4801 service order → F4812 billing workfile → F03B11 |

### 0.7 Query checklist

- Ledger type chosen (`AA` unless told otherwise); never mix `AA` and `CA` rows.
- Posted vs unposted decided and stated.
- Open vs closed defined by the module's own status (next status 999, pay status `P`, open amount zero, work-order status, match type).
- History tables included when lines are purged from the working table (F42119 with F4211; F42019 with F4201).
- Voids, reversals and matching documents handled, not double counted.
- Company/business-unit security scope and the default company 00000 rows understood.
- Dates converted, decimals scaled, strings trimmed, codes decoded.
- Result reconciled to a balance table (F0902, F41021, F03B15, F4229) when one exists.

### 0.8 Scope and limits

Covered: the modules in the seven parts below (Parts 1–6 from the 57 Oracle implementation guides; Part 7, Health and Safety and Apparel, from the supplementary Oracle table-documentation compendium — see 0.11). Not covered by either source: Human Capital Management and payroll, Job Cost, Contract and Service Billing internals, Homebuilder, localizations, and Tools tables (security, object librarian, data dictionary). Column-level layouts and site-specific customisations (`F55`–`F59` tables, custom UDC values, activity-rule status numbers) must be read from the live system.

### 0.9 When this reference doesn't cover what you need — use the live database connector

This skill documents table purposes, keys, codes and process flow from published Oracle guides. It does **not** give a full column list for most tables, and it cannot know a specific environment's customisations, custom UDC values, or activity-rule statuses. Whenever you need something this skill doesn't state — a table's actual column names, a table not mentioned here at all, or confirmation that a convention marked **†** actually holds in this environment — fall back to the live database connector (tool names vary by install, typically `get_jde_schema` / `query_jde_database`, or equivalent read-only SQL access) rather than guessing or inventing a column name. Never present a reconstructed or inferred column name as if it were confirmed.

The core discovery pattern (also used by the `jde-business-data` skill, repeated here so this skill is self-sufficient):

```sql
-- Real column names, order and business meaning for a table
SELECT d.TDSQLC, g.FRDSCR, d.TDPSEQ
FROM PY920.F98711 d
JOIN DD920.F9202 g ON TRIM(g.FRDTAI) = TRIM(d.TDOBND)
WHERE d.TDOBNM = '<TABLE_NAME>' AND TRIM(g.FRSYR) IS NULL
ORDER BY d.TDPSEQ
```

```sql
-- What an object actually is (table, view, business function...) and its description
SELECT SIOBNM, SIMD, SIFUNO FROM OL920.F9860 WHERE SIOBNM = '<OBJECT>'
```

Notes:
- `F98711` only reliably covers `TBLE`-type objects — don't assume it extends to business views or other object types without testing.
- Physical SQL data types/precision are not reliable from `F98711`; if the table exists physically, read `all_tab_columns` directly — but expect `data_precision`/`data_scale` to come back NULL for JDE amount columns even though the application stores implied decimals (see 0.10).
- If a question needs a table, column or relationship that is in neither this skill nor what the connector returns, say so explicitly rather than filling the gap from general JDE knowledge presented as fact.

### 0.10 Interpreting amount and quantity fields correctly (display decimals)

Every amount, cost, price, rate and quantity column in JDE is stored as a plain integer with the decimal point implied, never stored in the column itself. Getting the scaling wrong silently produces numbers that are off by a power of ten — always resolve this explicitly before reporting a number, not just when a result "looks wrong":

1. **Identify what kind of field it is.** A currency amount (ledger amounts like `AA`/`AG`/`AAP`, invoice/voucher amounts, prices in a given currency) scales by the **currency's** display decimals. A quantity, unit cost, unit price, or rate that is *not* a currency amount scales by the **data item's own** display-decimals attribute in the Data Dictionary.
2. **For a currency amount**: look up the row's currency code (`CRCD`, or the company's base currency from F0010 when the row has no explicit currency) in **F0013** (Currency Codes) and read its display-decimals value — 2 for most currencies (USD, EUR), 0 for currencies like JPY that have no minor unit, some currencies use 3. Divide the raw stored value by `10^decimals`.
3. **For a non-currency numeric field** (quantities, unit costs/prices, rates, percentages): find the data item's alias (table prefix + alias, Part 0.2), then look it up in the Data Dictionary (`DD920.F9202`, joined as in 0.9's query, filtering the language-neutral row) and read its display-decimals attribute — confirm the exact column name for that attribute via the schema tool rather than assuming one, since it is not spelled out in these Oracle guides. Unit cost/price is commonly 4 decimals; this is a convention, not a guarantee — always confirm per field rather than hard-coding 4.
4. **Never trust the database's own column precision/scale** for this — as noted in 0.9, JDE amount columns typically show NULL precision/scale at the SQL level regardless of the real implied decimals.
5. **Always sanity-check** the scaled result against one independently known value (an invoice total, a quoted unit price, a quantity you can cross-check) before reporting figures from a new table or field, and state in the answer which decimal convention was applied and where it came from (currency table vs data dictionary vs a documented default) so the assumption is visible and can be corrected.

### 0.11 Source note for Part 7 and Appendix A

Parts 1–6 are built from 57 Oracle EnterpriseOne implementation guides, as stated in the introduction. Part 7 (Health and Safety; Apparel) and Appendix A are built from a second, narrower public-documentation source — a compendium of table descriptions drawn strictly from Oracle's publicly available documentation pages (Appendix A lists the exact source URLs). That compendium deliberately does not infer any physical attribute (column list, data type, index) beyond what its cited page states, and explicitly recommends supplementing it with real environment/Data Dictionary data once available — which is exactly what 0.9's live-connector fallback does for any table in this skill, not only the Part 7 ones.
