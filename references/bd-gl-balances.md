# General ledger balances and trial balance — F0902 / F0901 (T-SQL)

Standard JDE column meanings for account balances. Column names below are standard JDE; confirm them on ABC's database with the discovery
pattern in `bd-query-method` before relying on them, and say which you confirmed. Use table names exactly as `get_jde_schema` shows them.

## F0902 Account Balances — one row per account x fiscal year x ledger type x subledger
- `GBAID` account ID (joins to `F0901.GMAID`); `GBCO` company (text, zero-padded, e.g. '00001')
- `GBCTRY` century of the fiscal year (20 = 2000s) and `GBFY` fiscal year, **2 digits** (25 = 2025) — filter both together
- `GBLT` ledger type: 'AA' = actual amounts (the ledger for a normal trial balance). Do not mix other ledger types (BA budget, CA foreign currency ...) unless asked
- `GBMCU` business unit, `GBOBJ` object account, `GBSUB` subsidiary (the natural account code is object.subsidiary)
- `GBAPYC` beginning balance brought forward into the year
- `GBAN01` ... `GBAN14` net posting per period (1-12 normal, 13-14 adjusting); signed: debit positive, credit negative
- `GBAND01` ... `GBAND14` debit-only posting per period (always >= 0)
- Derived: YTD net = sum of AN01..AN14; YTD debit = sum of AND01..AND14; YTD credit = YTD debit - YTD net; ending balance = GBAPYC + YTD net

## F0901 Account Master (chart of accounts)
`GMCO` company, `GMAID` account ID, `GMMCU` business unit, `GMOBJ` object, `GMSUB` subsidiary, `GMDL01` description.

## Amount scaling
Ledger amounts are stored without a decimal point. Find the company's ledger currency (`F0010` company constants) and that currency's decimals
(`F0013`), then divide by 10^decimals (2 for most currencies, so divide by 100). State the convention and cross-check against one known total.

## Which company, which year
If the user names no company, ask or list the companies from `F0010` and choose the one that holds the data; state your choice. Remember that the
fiscal year can differ from the calendar year — take it from the company's date pattern (`F0010` -> `F0008`).

## Aggregation grain
Grouping by `GBAID`, or by `GBMCU, GBOBJ, GBSUB`, returns department/subledger-level detail (thousands of rows). A company-wide trial balance should
`GROUP BY GBOBJ, GBSUB` only. Count first, then page with `ROW_NUMBER()` (see `bd-query-method`).

```sql
SELECT f.GBOBJ AS OBJ, f.GBSUB AS SUB,
       SUM(f.GBAPYC) AS BEG_BAL,
       SUM(f.GBAN01+f.GBAN02+f.GBAN03+f.GBAN04+f.GBAN05+f.GBAN06+f.GBAN07+f.GBAN08+f.GBAN09+f.GBAN10+f.GBAN11+f.GBAN12+f.GBAN13+f.GBAN14) AS YTD_NET,
       SUM(f.GBAND01+f.GBAND02+f.GBAND03+f.GBAND04+f.GBAND05+f.GBAND06+f.GBAND07+f.GBAND08+f.GBAND09+f.GBAND10+f.GBAND11+f.GBAND12+f.GBAND13+f.GBAND14) AS YTD_DEBIT
FROM <F0902> f
WHERE f.GBCO = '<company>' AND f.GBFY = <YY> AND f.GBCTRY = 20 AND f.GBLT = 'AA'
GROUP BY f.GBOBJ, f.GBSUB
```

## Mandatory verification step
Before presenting a trial balance, compare its totals with one direct aggregate over the same filter:
```sql
SELECT SUM(GBAPYC) AS TOT_BEG,
       SUM(GBAN01+GBAN02+GBAN03+GBAN04+GBAN05+GBAN06+GBAN07+GBAN08+GBAN09+GBAN10+GBAN11+GBAN12+GBAN13+GBAN14) AS TOT_NET,
       SUM(GBAND01+GBAND02+GBAND03+GBAND04+GBAND05+GBAND06+GBAND07+GBAND08+GBAND09+GBAND10+GBAND11+GBAND12+GBAND13+GBAND14) AS TOT_DEBIT
FROM <F0902>
WHERE GBCO = '<company>' AND GBFY = <YY> AND GBCTRY = 20 AND GBLT = 'AA'
```
Within one company a year's net postings normally sum to 0. Beginning balances may not (inter-company postings). If totals disagree with the pages you
pulled, a row was dropped or mis-copied: fix it before presenting. Report any oddity you see (very large turnover on a petty-cash account, a suspense account
with a balance) instead of silently adjusting it.

## Account-level detail
Journal lines are in `F0911` (`GLDGJ` G/L date Julian, `GLLT` ledger type, `GLPOST` posted code P, `GLAID`, `GLOBJ`, `GLSUB`, `GLAA` amount, `GLEXA` explanation).
Balances (F0902) should reconcile to the sum of posted F0911 lines per account and period.
