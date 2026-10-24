# Querying a live JDE database — method (SQL Server / T-SQL)

How to discover real table, column and object facts instead of guessing. Use together with `da-0-rules`. All examples are T-SQL.
Use the schema names exactly as `get_jde_schema` shows them; if a metadata table is refused or "Invalid object name", check
`SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '<name>'`.

## The three metadata sources

| Metadata | Table | What it gives |
|---|---|---|
| Object Librarian | `F9860` | object name, description, type (`SIFUNO`: TBLE table, APPL application, BSFN business function, UBE report, BSVW business view) |
| Data Dictionary | `F9202` | the real business meaning of each data item/alias (`FRDTAI` alias, `FRDSCR` description; default-language row has blank `FRSYR`) |
| Table Design | `F98711` | table -> physical column mapping (`TDOBNM` table, `TDSQLC` real column name, `TDOBND` data item, `TDPSEQ` order) |

## Core discovery pattern — a table's real column names, order and meaning

```sql
SELECT d.TDSQLC, g.FRDSCR, d.TDPSEQ
FROM <F98711 as shown by get_jde_schema> d
JOIN <F9202 as shown by get_jde_schema> g ON LTRIM(RTRIM(g.FRDTAI)) = LTRIM(RTRIM(d.TDOBND))
WHERE d.TDOBNM = '<TABLE_NAME>' AND (g.FRSYR IS NULL OR LTRIM(RTRIM(g.FRSYR)) = '')
ORDER BY d.TDPSEQ
```
Blank is a space, not NULL, in SQL Server CHAR columns, hence both tests on `FRSYR`. Both sides of the join need `LTRIM(RTRIM())`.

Find an object's type/purpose: `SELECT SIOBNM, SIMD, SIFUNO FROM <F9860> WHERE SIOBNM = '<OBJECT>'`.
List tables of a module: `SELECT SIOBNM, SIMD FROM <F9860> WHERE SIFUNO = 'TBLE' AND SIOBNM LIKE 'F06%'`.
Search by words: `... WHERE SIFUNO = 'TBLE' AND UPPER(SIMD) LIKE '%PAYROLL%'`.

Real SQL data types (F98711 gives names and order only): query `INFORMATION_SCHEMA.COLUMNS` for the table. Amount columns will not reveal their
implied decimals there — scaling comes from the currency or the Data Dictionary (see `da-0-rules` section 0.10).

## Known gaps — say so, never fabricate around them

- `F980021` (Cross Reference field relationships) is commonly empty; `F980011` (object relationships) is often only partly filled. Silence is not proof of "no relationship".
- Event rule and form-layout blobs are compiled binary — not readable through SQL.
- `F98711` covers TBLE objects only; do not assume the same join works for business views or other object types without testing.
- If a table, column or relationship is in neither the reference documents nor the live metadata, say so explicitly.

## Mapping a new table or module on demand

1. Catalog what exists: `F9860` by module prefix (`F01%` address book, `F06%` payroll ...) or description keyword. Don't guess a table name.
2. Get real columns from `F98711`/`F9202` (TBLE only).
3. Find join keys: a data-dictionary alias that appears in two tables is a candidate key —
   `SELECT DISTINCT TDOBNM FROM <F98711> WHERE LTRIM(RTRIM(TDOBND)) = '<alias>' ORDER BY TDOBNM` — then check cardinality before assuming 1:1.
4. State, for every relationship claim, whether it is confirmed by query, inferred from naming, or unknown. If it is unknown, say what would settle it and stop; do not guess.
5. Sanity check amounts: compare a result against one independently known document or total before reporting figures from a new table.

## Result size and paging

The query tool returns a limited number of rows per call (200). For larger result sets page with `ROW_NUMBER()` inside a derived table:
```sql
SELECT * FROM (
  SELECT ROW_NUMBER() OVER (ORDER BY t.k1, t.k2) AS RN, t.*
  FROM ( <the aggregate select here> ) t
) p WHERE p.RN BETWEEN <start> AND <end>
```
Independent pages can be requested in one turn. Always cross-check the total of the pages against one direct aggregate before presenting figures.
