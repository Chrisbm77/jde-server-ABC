> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.

# JDE data architecture — Part 7. Health and Safety, and Apparel Management

## Part 7. Health and Safety, and Apparel Management

Source: the Oracle public-documentation table compendium (see 0.11 and Appendix A) — **not** one of the 57 implementation guides behind Parts 1–6, and correspondingly thinner: table-level purpose only, no keys, column lists, status flows or process maps beyond what's stated here. Treat anything beyond this as a question for the live database connector (0.9), not for inference from the patterns in Parts 1–6.

### 7.1 Health and Safety Incident Management (system 54HS)

| Table | Name | What it holds |
|---|---|---|
| F54HS01 | Incident Master | One row per incident: company, business unit, establishment, project, contractor or other responsible party, incident description, dates, location and causal details. |
| F54HS02 | Incident People | People involved in an incident, plus the primary injury/illness case information for the incident. |
| F54HS021 | Incident Injury/Illness Details | Additional injuries or illnesses associated with one injured/ill person on one incident — i.e. the detail rows under F54HS02 when a person has more than one recorded injury. |

Likely relationship, by naming and description (not confirmed against a live schema — verify via 0.9 before relying on it): F54HS01 (incident) ← F54HS02 (people on that incident) ← F54HS021 (that person's individual injury/illness entries). Business unit (`MCU`) and company (`CO`) follow the same Foundation conventions as every other module (Part 1).

### 7.2 Apparel Management (system CW)

| Table | Name | What it holds |
|---|---|---|
| FCW44 | Proposal Order Details | Proposal details for a sales order, including allocation and delivery proposals — i.e. how a style/size order is proposed to be allocated and delivered before it is committed. |
| FCW46 | Size Weights for Proposals | Size-weight information used by the allocation and delivery proposal processes (how a total quantity is split across sizes). |
| FCW48 | Bill of Material Association Header | Bill-of-material association information for a **parent** style item. |
| FCW49 | Bill of Material Association Detail | Bill-of-material association information for the **child** style items and components under a parent (the counterpart to FCW48). |

This is apparel's size/style analogue of the standard BOM pattern in Part 4.4 (F3002 parent↔component), applied to proposal/allocation data rather than manufacturing structure; sales orders for apparel still live in the standard F4201/F4211 (Part 4.2).

### 7.3 Using Part 7

Both areas are narrow and this skill has no verified keys for them. Before writing SQL against any F54HS or FCW table:
1. Confirm real column names and the join key between the tables above via the connector pattern in 0.9 — do not assume `MCU`/`CO`/`AN8` naming carries over without checking.
2. State explicitly that the table purposes come from public documentation only, not from a verified schema, so the reader knows the confidence level is lower than for Parts 1–6.
3. Apply the same decimal-interpretation discipline (0.10) to any amount or quantity field encountered here — nothing about these two modules exempts them from implied-decimal storage.


## Appendix A. Public Oracle documentation sources

The compendium behind Part 7 (and cross-checked against Parts 1–6 for the tables they share) cites these Oracle documentation pages. Consult them directly for anything Part 7 doesn't cover, before falling back to general JDE knowledge:

- Inventory Management Tables
- Procurement Management Tables
- Shop Floor Management Tables
- Health and Safety Tables
- Sales Order Management Implementation Guide
- General Accounting Implementation Guide
- Warehouse Management Implementation Guide
- Job Cost Implementation Guide
- Capital Asset Management Implementation Guide
- JDE Tables and Object Owner IDs

The compendium's own scope note applies here too: it is sourced only from what these public pages state, marks anything not stated as "not specified," and does not infer unstated physical attributes. Where Parts 1–6 of this skill already cover a table in more depth (keys, columns, codes, process flow — true for nearly all of F0006, F0101, F0111, F0115, F0116, F0150, F03012, F03B11, F0901, F0902, F0911/F0911Z1, F41xx, F42xx/F43xx and their Z1 variants, F46xx, F4801/F4802/F4812, F30006/F3002/F3003/F3106/F3111/F3112, F3400/F34006/F3460), treat Parts 1–6 as authoritative and this appendix as a cross-check only. The two genuinely new areas this compendium added are Part 7 (F54HS01/02/021, FCW44/46/48/49) — use 0.9's live-connector fallback for anything about them beyond what Part 7 states.
