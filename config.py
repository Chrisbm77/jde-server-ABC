"""
JDE AI Assistant — Client Configuration (ABC, Microsoft SQL Server)
=========================================================================

>>> BEFORE GO-LIVE: this file was ported from the reference deployment. The
>>> department catalog below is generic JDE and carries over unchanged, but
>>> every ABC-specific fact still has to be confirmed against ABC's own
>>> database — look for "TODO(ABC)". Nothing marked VERIFIED in the
>>> reference deployment is assumed true here.

CURRENT STATE: DISCOVERY MODE is on. Four departments are defined —
procurement, finance, sales, hr — and every key that has a department is
walled to that department's tables (plus the shared reference tables every
department gets: JDE metadata, UDCs, Address Book, business units, company
and currency setup). A key with NO department is an internal/admin key
with full access. The "department" string in clients.json must be exactly
one of: procurement, finance, sales, hr.

To lock this down before real users: set RESTRICT_TO_APPROVED_TABLES = True
and curate TABLES down to a reviewed, verified list.
"""

# ---------------------------------------------------------------------------
# Schema configuration
# ---------------------------------------------------------------------------

# TODO(ABC): confirm ABC's real data schema. The reference deployment used
# CRPDTA; JDE on SQL Server is commonly PRODDTA / CRPDTA / TESTDTA. Check:
#   SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
#   WHERE TABLE_NAME IN ('F4101','F4211','F0101','F0902')
SCHEMA_PREFIX_DEFAULT = "PRODDTA"

# TODO(ABC): confirm where ABC's JDE system tables live. On SQL Server they
# are often in separate schemas — and sometimes a separate DATABASE, in
# which case write the full prefix, e.g. "JDE_SYSTEM.OL920". Any text here
# is simply placed in front of the table name.
SCHEMA_OVERRIDES = {
    "F9860": "OL920",   # Object Librarian Master
    "F9202": "DD920",   # Data Dictionary Alias/Glossary
    "F98711": "PY920",  # Table Design
    # Confirmed by the user: ABC's UDC (code) tables live in the control schema PRODCTL.
    "F0005": "PRODCTL",  # UDC values
    "F0004": "PRODCTL",  # UDC types
}

# ---------------------------------------------------------------------------
# Table access mode
# ---------------------------------------------------------------------------
# True  = STRICT mode. Only tables explicitly listed in TABLES below can be
#         queried, regardless of what the underlying database account can
#         see. Recommended for any client-facing deployment.
#
# False = DISCOVERY mode (current setting). Any table can be queried
#         (still read-only, still row-capped, still timed-out) as long as
#         it's a real table the database account can see. Useful during
#         active exploration. Flip back to True before a client deployment.
RESTRICT_TO_APPROVED_TABLES = False

# ---------------------------------------------------------------------------
# Department-scoped table access
# ---------------------------------------------------------------------------
# Four departments: "procurement", "finance", "sales", "hr" — the exact
# strings to put in a client's "department" field in clients.json. A
# deployment with NO department gets full access (subject only to
# RESTRICT_TO_APPROVED_TABLES) — meant for an internal/admin key.
#
# Enforced ALWAYS when a department is set, even in discovery mode. A
# department string with no entry below FAILS CLOSED (denied entirely), so
# the old names "purchasing", "inventory", "manufacturing" and "support"
# no longer exist — keys still using them must be changed.
#
# Two layers, checked in order:
#   1. DEPARTMENT_TABLES — exact table membership.
#   2. DEPARTMENT_TABLE_PREFIXES — coarser fallback for a real table of the
#      department's module range that is not listed (keeps discovery useful).
#
# How the catalog was redistributed:
#   SHARED by all four: JDE metadata (F9860, F98711, F9202 — so any key can
#     look up table designs), UDC values/types (F0004, F0005), Address Book
#     and its satellites (F0101, F0111, F0115, F0116 ...), business units
#     (F0006), company/fiscal/currency setup (F0008-F0010, F0013, F0015).
#   SALES (+ F0901/F0902 account master and balances, added on request): sales orders + history (F4201, F4211, F42119, F42199, F42019),
#     pricing and agreements (F40xx, F407x), customer master and A/R
#     (F03012, F03B*), item master/stock/ledger (F41xx), shipping,
#     warehouse and transportation (F4215, F46*, F49*), forecast (F3460),
#     CRM/service (F17xx, F18xx, F90C*, F4801).
#   PROCUREMENT: requisitions, purchase orders, receipts, vouchers match
#     (F43*, F4311, F43121, F43199, F0401, F0411), item/stock (F41xx),
#     supply planning and manufacturing (F30*, F31*, F34*), work orders
#     (F48*), equipment (F13xx).
#   FINANCE: G/L (F0901, F0902, F0911, F0011, F0012, F0018), A/P and A/R
#     (F04xx, F03B*), fixed assets (F12xx), service billing (F4812),
#     company/fiscal setup (F0002, F0010).
#   HR: payroll and employee tables (F06xx, F07xx, F08xx), health and
#     safety (F54HS*). HR tables are NOT in the reference catalog — the
#     list is carried over and the real tables must be confirmed on ABC's
#     database (TODO(ABC)): SELECT SIOBNM, SIMD FROM OL920.F9860
#     WHERE SIFUNO = 'TBLE' AND SIOBNM LIKE 'F06%'

DEPARTMENT_TABLES = {
    "procurement": {
        "F0004", "F0005", "F0006", "F0007", "F0008", "F0009",
        "F00090", "F00090D", "F00091", "F00092", "F0010", "F0013",
        "F0015", "F00191", "F0070", "F0101", "F0101A", "F01090",
        "F01092", "F01093", "F0111", "F01112", "F01138", "F0115",
        "F01151", "F0116", "F01161", "F0117", "F0118", "F011901",
        "F01301", "F01301W", "F01302", "F01311", "F01321", "F01331",
        "F01401", "F01411", "F0150", "F01501", "F01815", "F03012",
        "F0401", "F0411", "F0902", "F1301", "F1305", "F1307",
        "F1390", "F1391", "F1731", "F30006", "F30008", "F3002",
        "F300210", "F300211", "F30026", "F3003", "F300311", "F3007",
        "F3009", "F3011", "F3013", "F3015", "F3016", "F30161",
        "F30L912", "F3102", "F3105", "F3106", "F3108", "F3109",
        "F31091", "F3111", "F3112", "F31122", "F3118", "F31B03",
        "F31B04", "F31B13", "F31B31", "F31B31C", "F31B37", "F31B65",
        "F31B66", "F31B70", "F31B73", "F3293", "F3400", "F34004",
        "F34006", "F3411", "F3412", "F3413", "F3430", "F3435",
        "F3450", "F3460", "F34X001", "F34X010", "F34X100W", "F34X101W",
        "F34X110W", "F34X200W", "F3712", "F40039", "F4009", "F40095",
        "F4015", "F4016", "F4017", "F40203", "F40205", "F4090",
        "F4091", "F4095", "F40G002", "F4100", "F41001", "F41002",
        "F41003", "F41006", "F4101", "F41013", "F4101M", "F4102",
        "F41021", "F41023", "F4104", "F4105", "F4106", "F41061",
        "F4108", "F41081", "F4111", "F41112", "F41113", "F4115",
        "F4140", "F4141", "F4160", "F4170", "F41829", "F4209",
        "F43001", "F43008", "F4301", "F4301Z", "F4301Z1", "F4303",
        "F4303M", "F4304", "F4305", "F43080", "F43090", "F43091",
        "F43092", "F43092Z", "F43092Z1", "F43093", "F43094", "F43099",
        "F43100", "F4311", "F4311T", "F4311Z", "F4311Z1", "F43121",
        "F43121T", "F43121Z", "F43121Z1", "F43126", "F43126T", "F43127",
        "F4314", "F43146T", "F43147", "F4314Z", "F4316", "F4316M",
        "F4316T", "F4317", "F4318", "F43199", "F4321", "F43211",
        "F43213", "F4322", "F4330", "F4331", "F4332", "F4333WF",
        "F4340", "F4341", "F4342", "F4343", "F4350", "F4351",
        "F4355", "F43632Z", "F4371", "F43800", "F43E01", "F4600",
        "F4602", "F4611", "F4801", "F4802", "F4808", "F48092",
        "F4818", "F52034", "F9202", "F9860", "F98711", "FF31010",
        "FF31011",
    },
    "finance": {
        "F0002", "F0004", "F0005", "F0006", "F0006S", "F0008",
        "F0009", "F00090", "F00090D", "F00091", "F00092", "F0010",
        "F0011", "F0012", "F0013", "F0015", "F0018", "F0025",
        "F0070", "F0101", "F0101A", "F01090", "F01092", "F01093",
        "F0111", "F01112", "F01138", "F0115", "F01151", "F0116",
        "F01161", "F0117", "F0118", "F011901", "F01301", "F01301W",
        "F01302", "F01311", "F01321", "F01331", "F01401", "F01411",
        "F0150", "F01501", "F01815", "F03012", "F03B11", "F03B112",
        "F03B13", "F03B14", "F03B16", "F03B20", "F03B21", "F03B22",
        "F03B23", "F03B41", "F0401", "F0401M", "F0411", "F0411Z1",
        "F0413", "F0414", "F0901", "F0902", "F0911", "F0911Z1",
        "F12002", "F12003", "F1201", "F1202", "F1204", "F1205",
        "F1206", "F1207", "F12071", "F1210", "F1212", "F1215",
        "F1216", "F1217", "F4812", "F4812H", "F4822", "F48520",
        "F5202", "F5204", "F5212", "F5213", "F5216", "F9202",
        "F9860", "F98711",
    },
    "sales": {
        # Added on request: account balances + chart of accounts, so sales can report revenue by account.
        "F0901", "F0902",
        "F0004", "F0005", "F0006", "F0008", "F0009", "F00090",
        "F00090D", "F00091", "F00092", "F0010", "F0013", "F0015",
        "F0070", "F0101", "F0101A", "F01090", "F01092", "F01093",
        "F0111", "F01112", "F01138", "F0115", "F01151", "F0116",
        "F01161", "F0117", "F0118", "F011901", "F01301", "F01301W",
        "F01302", "F01311", "F01321", "F01331", "F01401", "F01411",
        "F0150", "F01501", "F01815", "F03012", "F03B11", "F03B112",
        "F03B13", "F03B14", "F03B16", "F03B20", "F03B21", "F03B22",
        "F03B23", "F03B41", "F0401", "F1720", "F1721", "F1724",
        "F1725", "F1726", "F1729", "F1731", "F17311", "F1750",
        "F1751", "F1752", "F1753", "F1754", "F1755", "F1757",
        "F1758", "F1759", "F1760", "F1761", "F1790", "F1791",
        "F1792", "F1793", "F1794", "F1797", "F18001", "F1810",
        "F1811", "F18111", "F1812", "F18121", "F18122", "F1820",
        "F1830", "F34004", "F3460", "F4001Z", "F40039", "F4009",
        "F40095", "F4016", "F4017", "F4072", "F4074", "F4075",
        "F4078", "F4095", "F4096", "F4100", "F41001", "F41002",
        "F41003", "F41006", "F4101", "F41013", "F4102", "F41021",
        "F41023", "F4104", "F4105", "F4106", "F4108", "F41081",
        "F4111", "F41112", "F41113", "F4115", "F4140", "F4141",
        "F4160", "F4170", "F41829", "F4201", "F42019", "F4201Z1",
        "F4209", "F4211", "F42119", "F4211Z1", "F4215", "F42199",
        "F4229", "F42420", "F4314", "F4550", "F4600", "F4601",
        "F46010", "F46011", "F46012", "F46013", "F4602", "F46021",
        "F46022", "F46024", "F46025", "F46026", "F46027", "F46051",
        "F46091", "F46092", "F46093", "F46095", "F46096", "F4611",
        "F46130", "F46821", "F46822", "F46L10", "F46L11", "F46L12",
        "F46L30", "F46L99", "F4801", "F49211", "F49301", "F4941",
        "F4945", "F4950", "F4960", "F4961", "F49611", "F4972",
        "F49721", "F4973", "F4977", "F4981", "F49T90", "F90CA060",
        "F90CB020", "F90CG503", "F9202", "F9860", "F98711",
    },
    "hr": {
        "F0004", "F0005", "F0006", "F0008", "F0009", "F00090",
        "F00090D", "F00091", "F00092", "F0010", "F0013", "F0015",
        "F0070", "F0101", "F0101A", "F01090", "F01092", "F01093",
        "F0111", "F01112", "F01138", "F0115", "F01151", "F0116",
        "F01161", "F0117", "F0118", "F011901", "F01301", "F01301W",
        "F01302", "F01311", "F01321", "F01331", "F01401", "F01411",
        "F0150", "F01501", "F01815", "F060116", "F060117", "F06017",
        "F0607", "F0609", "F06106", "F06107", "F061071", "F06116",
        "F06116Z1", "F06136", "F06145", "F06146", "F06147", "F06210",
        "F062101", "F062102", "F065016", "F08042", "F08045", "F08102",
        "F08105", "F54HS01", "F54HS02", "F54HS021", "F9202", "F9860",
        "F98711",
    },
}

# Fallback prefix matching — only reached for a table NOT in the exact lists.
_SHARED_PREFIXES = ["F01"]  # Address Book family
DEPARTMENT_TABLE_PREFIXES = {
    "procurement": ["F43", "F40", "F41", "F30", "F31", "F34", "F48", "F0401", "F0411"] + _SHARED_PREFIXES,
    "finance": ["F09", "F03B", "F04", "F12", "F15", "F52", "F55", "F58", "F59"] + _SHARED_PREFIXES,
    "sales": ["F42", "F03B", "F40", "F41", "F46", "F49", "F17", "F15", "F55", "F58", "F59", "F90C"] + _SHARED_PREFIXES,
    "hr": ["F06", "F07", "F08"] + _SHARED_PREFIXES,
}

# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

TABLES = [
    {
        "name": "F9860",
        "description": (
            "Object Librarian Master — catalog of every object in the JDE system "
            "(tables, applications, business functions, batch programs). Use this "
            "to look up the real title of a table, e.g. 'what does F4101 mean?'"
        ),
        "columns": [
            ("SIOBNM", "TEXT", "object name, e.g. 'F4101'"),
            ("SIMD", "TEXT", "description/title, e.g. 'Item Master'"),
            ("SIFUNO", "TEXT", "object type code — 'TBLE' = table, 'APPL' = application, 'BSFN' = business function, 'UBE' = batch program"),
        ],
        "notes": [
            "To list only tables, filter WHERE SIFUNO = 'TBLE'.",
        ],
    },
    {
        "name": "F98711",
        "description": (
            "Table Design — links a table to its real PHYSICAL columns and to the "
            "Data Dictionary item that defines each column's business meaning. "
            "IMPORTANT: TDSQLC is the actual physical column name to use in SQL "
            "against the real table — JDE prefixes physical columns with a "
            "2-3 letter table code (e.g. F4101's item number column is IMITM, "
            "not bare ITM; F4211's are prefixed SD). Never assume a bare data "
            "item alias is the real column name — always confirm via TDSQLC first."
        ),
        "columns": [
            ("TDOBNM", "TEXT", "table name, e.g. 'F4101'"),
            ("TDOBND", "TEXT", "Data Dictionary item ID for this column — join key to F9202.FRDTAI"),
            ("TDSQLC", "TEXT", "the REAL physical SQL column name (prefixed), e.g. 'IMITM' — this is what belongs in a SELECT statement, not the bare alias"),
            ("TDPSEQ", "INTEGER", "sequence number — column order within the table"),
        ],
    },
    {
        "name": "F9202",
        "description": (
            "Data Dictionary Alias/Glossary — the real business meaning of each "
            "Data Dictionary item (the alias, e.g. ITM), reused consistently "
            "across every table that uses it. Join F98711.TDOBND to "
            "F9202.FRDTAI to explain what a given physical column actually means."
        ),
        "columns": [
            ("FRDTAI", "TEXT", "Data Dictionary item ID — join key from F98711.TDOBND"),
            ("FRDSCR", "TEXT", "the real description text, e.g. 'Item Number'"),
            ("FRSYR", "TEXT", "language/system code — typically filter to blank for the default language"),
        ],
    },
    {
        "name": "F0005",
        "description": "User Defined Code values — decodes every coded field (status codes, document types, units, categories). Available to every department.",
        "columns": [
            ("DRSY", "TEXT", "system code, e.g. '40' (distribution), '00' (foundation). Standard JDE, not yet verified on ABC."),
            ("DRRT", "TEXT", "UDC type within the system, e.g. 'AT' (sales order status), 'DT' (document type). Standard JDE, not yet verified on ABC."),
            ("DRKY", "TEXT", "the code value itself (space-padded; use LTRIM(RTRIM())). Standard JDE, not yet verified on ABC."),
            ("DRDL01", "TEXT", "description of the code. Standard JDE, not yet verified on ABC."),
        ],
        "notes": ["Example: statuses of sales order lines = DRSY = '40' AND DRRT = 'AT'.", "This table lives in the control schema PRODCTL (not PRODDTA) — always write PRODCTL.F0005."],
    },
    {
        "name": "F0004",
        "description": "User Defined Code types — the list of code categories (system + type) and their titles. Available to every department. Lives in the control schema PRODCTL.",
        "columns": [
            ("DTSY", "TEXT", "system code. Standard JDE, not yet verified on ABC."),
            ("DTRT", "TEXT", "UDC type code. Standard JDE, not yet verified on ABC."),
            ("DTDL01", "TEXT", "title/description of the code type. Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F0101",
        "description": "Address Book Master — one row per customer, supplier, employee, company, carrier. Available to every department.",
        "columns": [
            ("ABAN8", "INTEGER", "address number — the key used as customer/supplier/employee number everywhere. Standard JDE, not yet verified on ABC."),
            ("ABALPH", "TEXT", "name (alpha name). Standard JDE, not yet verified on ABC."),
            ("ABAT1", "TEXT", "search type: C = customer, V = supplier, E = employee, etc. Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F0006",
        "description": "Business Unit Master — branch/plants, cost centers, jobs. Available to every department.",
        "columns": [
            ("MCMCU", "TEXT", "business unit code, right-justified with leading blanks (use LTRIM(RTRIM())). Standard JDE, not yet verified on ABC."),
            ("MCDC", "TEXT", "business unit description. Standard JDE, not yet verified on ABC."),
            ("MCCO", "TEXT", "company the business unit belongs to. Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F03B11",
        "description": "Customer Ledger — A/R invoices, credit memos and receipts per customer (ABC's main sales/billing record; sales, finance)",
        "columns": [
            ("RPDOC", "INTEGER", "document number. Standard JDE, not yet verified on ABC."),
            ("RPDCT", "TEXT", "document type: RI invoice, RD recurring, RN manual, RJ sales overage, RT fees, RM credit memo, RX reimbursement ... Standard JDE codes; ABC treatment in the rules."),
            ("RPAN8", "INTEGER", "customer number (F0101.ABAN8). Standard JDE, not yet verified on ABC."),
            ("RPDGJ", "TEXT", "G/L date, Julian CYYDDD — use for period filtering. Standard JDE, not yet verified on ABC."),
            ("RPDIVJ", "TEXT", "invoice date, Julian CYYDDD. Standard JDE, not yet verified on ABC."),
            ("RPAG", "REAL", "gross amount, implied decimals (2 for USF). Standard JDE, not yet verified on ABC."),
            ("RPAAP", "REAL", "open amount still owed, implied decimals. Standard JDE, not yet verified on ABC."),
            ("RPCRCD", "TEXT", "currency code (USF main). Standard JDE, not yet verified on ABC."),
            ("RPMCU", "TEXT", "business unit (building/property). Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F4101",
        "description": "Item Master (sales, procurement)",
        "columns": [
            ("IMITM", "TEXT", "Item Number (Short) — JDE's internal short item number, primary key. Carried over from the reference deployment; not yet verified on ABC's database."),
            ("IMLITM", "TEXT", "2nd item number — the item code people actually use. Standard JDE, not yet verified on ABC."),
            ("IMDSC1", "TEXT", "item description (line 1). Carried over, not yet verified on ABC."),
            ("IMUOM1", "TEXT", "primary/default unit of measure (e.g. EA, CS, LB). Carried over, not yet verified on ABC."),
            ("IMSTKT", "TEXT", "stocking type — classifies how the item is stocked/handled. Carried over, not yet verified on ABC."),
        ],
        "notes": [
            "Physical columns on this table are prefixed with 'IM' in standard JDE (confirm via F98711.TDSQLC on ABC). "
            "F4101 has 209 columns total; only the ones needed for common questions are listed here. "
            "Ask the assistant to query F98711 for the full list if a question needs a column not here.",
        ],
    },
    {
        "name": "F4211",
        "description": "Sales Order Detail — OPEN order lines only (sales)",
        "columns": [
            ("SDDOCO", "INTEGER", "sales order number. Carried over, not yet verified on ABC."),
            ("SDDCTO", "TEXT", "order type (SO etc.). Standard JDE, not yet verified on ABC."),
            ("SDAN8", "INTEGER", "sold-to customer number (F0101.ABAN8). Carried over, not yet verified on ABC."),
            ("SDITM", "TEXT", "item number, references F4101.IMITM. Carried over, not yet verified on ABC."),
            ("SDUORG", "REAL", "quantity ORDERED (implied decimals). Standard JDE, not yet verified on ABC."),
            ("SDSOQS", "REAL", "quantity SHIPPED (implied decimals) — this is what was actually sold/delivered, not the ordered quantity. Not yet verified on ABC."),
            ("SDUPRC", "REAL", "unit price (implied decimals). Carried over, not yet verified on ABC."),
            ("SDAEXP", "REAL", "extended price = line amount (implied decimals). Standard JDE, not yet verified on ABC."),
            ("SDDRQJ", "TEXT", "requested date, JDE Julian CYYDDD (see the Julian date rule below). Carried over, not yet verified on ABC."),
            ("SDIVD", "TEXT", "invoice date, Julian CYYDDD — the date a line was sold/invoiced. Standard JDE, not yet verified on ABC."),
            ("SDLTTR", "TEXT", "line status code (UDC 40/AT). Status meanings are set per environment — do NOT assume them. In the reference deployment '545' = Pick Confirmation (in-process), '620' = Sales Update (closed), '980' = Canceled, but ABC's codes must be read from UDC 40/AT (F0005) before stating what any code means."),
        ],
        "notes": [
            "Physical columns on this table are prefixed with 'SD' in standard JDE (confirm via F98711.TDSQLC on ABC). "
            "F4211 has 268 columns total, including 20 user-defined status fields (SDSO01-SDSO20).",
            "F4211 holds only OPEN lines. Once a line is invoiced/closed it moves to F42119 (same SD columns). "
            "Questions about what was SOLD in a past period must use F42119 (and F4211 too if open lines count).",
        ],
    },
    {
        "name": "F42119",
        "description": "Sales Order History — closed/invoiced order lines, same columns as F4211 (sales)",
        "columns": [
            ("SDDOCO", "INTEGER", "sales order number. Same layout as F4211; not yet verified on ABC."),
            ("SDAN8", "INTEGER", "sold-to customer number. Not yet verified on ABC."),
            ("SDITM", "TEXT", "item number, references F4101.IMITM. Not yet verified on ABC."),
            ("SDSOQS", "REAL", "quantity shipped (implied decimals). Not yet verified on ABC."),
            ("SDAEXP", "REAL", "extended price = line amount (implied decimals). Not yet verified on ABC."),
            ("SDIVD", "TEXT", "invoice date, Julian CYYDDD. Not yet verified on ABC."),
            ("SDLTTR", "TEXT", "last status (UDC 40/AT) — exclude canceled lines; check the cancel code in F0005 first. Not yet verified on ABC."),
        ],
        "notes": ["Same 'SD' column names as F4211 — confirm via F98711 for table F42119."],
    },
    {
        "name": "F4311",
        "description": "Purchase Order Detail — open PO lines (procurement)",
        "columns": [
            ("PDDOCO", "INTEGER", "purchase order number. Standard JDE, not yet verified on ABC."),
            ("PDDCTO", "TEXT", "order type (OP etc.). Standard JDE, not yet verified on ABC."),
            ("PDAN8", "INTEGER", "supplier number (F0101.ABAN8). Standard JDE, not yet verified on ABC."),
            ("PDITM", "TEXT", "item number (F4101.IMITM). Standard JDE, not yet verified on ABC."),
            ("PDUORG", "REAL", "quantity ordered (implied decimals). Standard JDE, not yet verified on ABC."),
            ("PDUOPN", "REAL", "quantity still open (implied decimals). Standard JDE, not yet verified on ABC."),
            ("PDPRRC", "REAL", "unit cost (implied decimals). Standard JDE, not yet verified on ABC."),
            ("PDAEXP", "REAL", "extended cost (implied decimals). Standard JDE, not yet verified on ABC."),
            ("PDDRQJ", "TEXT", "requested date, Julian CYYDDD. Standard JDE, not yet verified on ABC."),
            ("PDLTTR", "TEXT", "last status code (UDC 40/AT) — environment specific, read F0005 before interpreting. Not yet verified on ABC."),
        ],
        "notes": ["Closed/received lines move to F43199 (PO ledger) — use it for past-period purchase questions."],
    },
    {
        "name": "F43121",
        "description": "Purchase Order Receiver — goods receipts (procurement)",
        "columns": [
            ("PRDOCO", "INTEGER", "purchase order number. Standard JDE, not yet verified on ABC."),
            ("PRAN8", "INTEGER", "supplier number. Standard JDE, not yet verified on ABC."),
            ("PRITM", "TEXT", "item number. Standard JDE, not yet verified on ABC."),
            ("PRUREC", "REAL", "quantity received (implied decimals). Standard JDE, not yet verified on ABC."),
            ("PRAREC", "REAL", "amount received (implied decimals). Standard JDE, not yet verified on ABC."),
            ("PRRCDJ", "TEXT", "receipt date, Julian CYYDDD. Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F0411",
        "description": "Accounts Payable Ledger — supplier vouchers (procurement, finance)",
        "columns": [
            ("RPDOC", "INTEGER", "voucher document number. Standard JDE, not yet verified on ABC."),
            ("RPDCT", "TEXT", "document type (PV = voucher). Standard JDE, not yet verified on ABC."),
            ("RPAN8", "INTEGER", "supplier number. Standard JDE, not yet verified on ABC."),
            ("RPDIVJ", "TEXT", "invoice date, Julian CYYDDD. Standard JDE, not yet verified on ABC."),
            ("RPDDJ", "TEXT", "due date, Julian CYYDDD. Standard JDE, not yet verified on ABC."),
            ("RPAG", "REAL", "gross amount (implied decimals). Standard JDE, not yet verified on ABC."),
            ("RPAAP", "REAL", "open amount still to pay (implied decimals). Standard JDE, not yet verified on ABC."),
            ("RPPST", "TEXT", "pay status — P = paid. Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F0911",
        "description": "Account Ledger — every general-ledger journal line (finance)",
        "columns": [
            ("GLDOC", "INTEGER", "journal document number. Standard JDE, not yet verified on ABC."),
            ("GLDCT", "TEXT", "document type. Standard JDE, not yet verified on ABC."),
            ("GLCO", "TEXT", "company. Standard JDE, not yet verified on ABC."),
            ("GLDGJ", "TEXT", "G/L date, Julian CYYDDD. Standard JDE, not yet verified on ABC."),
            ("GLAID", "TEXT", "short account ID (F0901.GMAID). Standard JDE, not yet verified on ABC."),
            ("GLMCU", "TEXT", "business unit. Standard JDE, not yet verified on ABC."),
            ("GLOBJ", "TEXT", "object account. Standard JDE, not yet verified on ABC."),
            ("GLLT", "TEXT", "ledger type — AA = actuals. Never mix ledger types. Standard JDE, not yet verified on ABC."),
            ("GLAA", "REAL", "amount (implied decimals — usually 2). Standard JDE, not yet verified on ABC."),
            ("GLPOST", "TEXT", "posted code — P = posted. Standard JDE, not yet verified on ABC."),
            ("GLEXA", "TEXT", "explanation/description. Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F0901",
        "description": "Account Master — chart of accounts (finance)",
        "columns": [
            ("GMAID", "TEXT", "short account ID. Standard JDE, not yet verified on ABC."),
            ("GMMCU", "TEXT", "business unit. Standard JDE, not yet verified on ABC."),
            ("GMOBJ", "TEXT", "object account. Standard JDE, not yet verified on ABC."),
            ("GMSUB", "TEXT", "subsidiary. Standard JDE, not yet verified on ABC."),
            ("GMDL01", "TEXT", "account description. Standard JDE, not yet verified on ABC."),
        ],
    },
    {
        "name": "F0902",
        "description": "Account Balances — period balances per account (finance)",
        "columns": [
            ("GBAID", "TEXT", "short account ID. Standard JDE, not yet verified on ABC."),
            ("GBCO", "TEXT", "company. Standard JDE, not yet verified on ABC."),
            ("GBFY", "INTEGER", "fiscal year (2-digit). Standard JDE, not yet verified on ABC."),
            ("GBLT", "TEXT", "ledger type (AA actuals, BA budget). Standard JDE, not yet verified on ABC."),
            ("GBAPYC", "REAL", "balance brought forward from prior year (implied decimals). Standard JDE, not yet verified on ABC."),
            ("GBAN01", "REAL", "net posting period 1 (GBAN02 ... GBAN12 follow; implied decimals). Standard JDE, not yet verified on ABC."),
        ],
    },
]

# ---------------------------------------------------------------------------
# Example question/SQL pairs
# ---------------------------------------------------------------------------

EXAMPLES = [
    (
        "What is the real title of table F4101?",
        "SELECT SIMD FROM {F9860} WHERE SIOBNM = 'F4101' AND SIFUNO = 'TBLE';",
    ),
    (
        "List every real physical column on table F4101, in order.",
        "SELECT TDSQLC, TDPSEQ FROM {F98711} WHERE TDOBNM = 'F4101' ORDER BY TDPSEQ;",
    ),
    (
        "What does the column IMITM on table F4101 actually mean?",
        "SELECT g.FRDSCR FROM {F98711} d JOIN {F9202} g ON LTRIM(RTRIM(g.FRDTAI)) = LTRIM(RTRIM(d.TDOBND)) WHERE d.TDOBNM = 'F4101' AND d.TDSQLC = 'IMITM';",
    ),
    (
        "List every column on table F4211 with its real description.",
        "SELECT d.TDSQLC, g.FRDSCR FROM {F98711} d JOIN {F9202} g ON LTRIM(RTRIM(g.FRDTAI)) = LTRIM(RTRIM(d.TDOBND)) WHERE d.TDOBNM = 'F4211' ORDER BY d.TDPSEQ;",
    ),
    (
        "What do the sales order line status codes mean?",
        "SELECT LTRIM(RTRIM(DRKY)) AS code, DRDL01 FROM {F0005} WHERE LTRIM(RTRIM(DRSY)) = '40' AND LTRIM(RTRIM(DRRT)) = 'AT';",
    ),
    (
        "What is item 10001?",
        "SELECT IMITM, IMLITM, IMDSC1, IMUOM1 FROM {F4101} WHERE IMITM = 10001;",
    ),
    (
        "Show open sales orders for customer 12345.",
        "SELECT SDDOCO, SDITM, SDUORG, SDUPRC, SDDRQJ FROM {F4211} WHERE SDAN8 = 12345 AND SDLTTR = '545';",
    ),
    (
        "Who are the top 10 customers by amount billed in 2025?",
        "SELECT TOP 10 r.RPAN8, MAX(LTRIM(RTRIM(a.ABALPH))) AS customer, SUM(r.RPAG) / 100.0 AS net_billed_usf "
        "FROM {F03B11} r JOIN {F0101} a ON a.ABAN8 = r.RPAN8 "
        "WHERE r.RPDGJ BETWEEN 125001 AND 125365 AND LTRIM(RTRIM(r.RPCRCD)) = 'USF' "
        "AND LTRIM(RTRIM(r.RPDCT)) IN ('RI','RD','RN','RJ','RT','RM') "
        "GROUP BY r.RPAN8 ORDER BY SUM(r.RPAG) DESC;",
    ),
    (
        "Top 10 sold items in 2025 by quantity (only when item-level sales exist; on ABC F42119 is empty, so answer with top customers / revenue accounts instead).",
        "SELECT TOP 10 h.SDITM, MAX(LTRIM(RTRIM(i.IMDSC1))) AS item_description, SUM(h.SDSOQS) AS qty_shipped_raw "
        "FROM {F42119} h JOIN {F4101} i ON i.IMITM = h.SDITM "
        "WHERE h.SDIVD BETWEEN 125001 AND 125365 "
        "GROUP BY h.SDITM ORDER BY SUM(h.SDSOQS) DESC;",
    ),
    (
        "Who are our top 10 suppliers by open purchase order value?",
        "SELECT TOP 10 p.PDAN8, MAX(LTRIM(RTRIM(a.ABALPH))) AS supplier, SUM(p.PDAEXP) AS open_value_raw "
        "FROM {F4311} p JOIN {F0101} a ON a.ABAN8 = p.PDAN8 "
        "GROUP BY p.PDAN8 ORDER BY SUM(p.PDAEXP) DESC;",
    ),
    (
        "Which supplier vouchers are still unpaid?",
        "SELECT TOP 100 RPDOC, RPAN8, RPDDJ, RPAAP FROM {F0411} WHERE RPPST <> 'P' AND RPAAP <> 0 ORDER BY RPDDJ;",
    ),
    (
        "What was posted to the general ledger in 2025 by object account (actuals)?",
        "SELECT TOP 50 GLOBJ, SUM(GLAA) AS amount_raw FROM {F0911} "
        "WHERE GLLT = 'AA' AND GLPOST = 'P' AND GLDGJ BETWEEN 125001 AND 125365 "
        "GROUP BY GLOBJ ORDER BY GLOBJ;",
    ),
    (
        "Which tables exist for payroll and employees?",
        "SELECT SIOBNM, SIMD FROM {F9860} WHERE SIFUNO = 'TBLE' AND (SIOBNM LIKE 'F06%' OR SIOBNM LIKE 'F08%');",
    ),
]

# ---------------------------------------------------------------------------
# General rules given to the model alongside the schema.
# ---------------------------------------------------------------------------

RULES = [
    "SKILLS FIRST: every time you are about to extract data from the database, first load and follow "
    "the JDE skills available in this session (jde-data-architecture for tables, keys, joins, status "
    "and document codes; jde-business-data for querying and financial/GL data) and use "
    "get_jde_reference for JDE specifics. Do not write SQL from memory when a skill covers the topic. "
    "If no such skill is available, say nothing about it and rely on this schema and the reference "
    "documents.",
    "ANSWER DIRECTLY, DO NOT STOP AT 'NO DATA': the user wants an answer, not a report of what is "
    "missing. If the obvious table for a question is empty or does not fit, do NOT reply that you "
    "cannot answer and do NOT ask the user where the data is. Instead, in the same turn: (1) work out "
    "what business this database actually records by checking which candidate tables hold rows and "
    "reading their real columns and codes (F98711, F9202, F0005); (2) choose the closest meaningful "
    "measure of what the user asked (e.g. 'top sold items' -> top revenue accounts and top customers by "
    "invoiced amount when there is no item-level sales data); (3) run it and give the result table "
    "first; (4) then state in a few lines what you counted and what you excluded (document types, "
    "currencies, accounts, date range, decimals applied) and that you substituted a measure, and only "
    "then offer one alternative definition. Ask a question before answering only when two readings "
    "would give completely different results and nothing in the data can settle it.",
    "ABC BUSINESS CONTEXT (learned from live data, re-verify if a result looks off): ABC's database "
    "records REAL-ESTATE / MALL billing, not product sales. Item-level sales tables F4201, F4211, "
    "F42119 and the item ledger F4111 are EMPTY (0 rows) — never lead with them. The item master F4101 "
    "has items but no sales. Revenue lives in the A/R invoice ledger F03B11 (about 2.4 million rows, "
    "customer = RPAN8 joined to F0101.ABAN8 for the name, G/L date RPDGJ, amount RPAG, document type "
    "RPDCT, currency RPCRCD) and in the general ledger F0911 revenue accounts (object accounts "
    "5000-5999, with descriptions in F0901 such as 'Stands Revenue', 'Tenants Revenue', 'Common "
    "Charges Revenue'); real-estate lease/billing masters are in the F15xx tables. For any question "
    "about 'sales', 'revenue', 'top customers/tenants' or 'best sellers', use these.",
    "ABC REVENUE CONVENTIONS (from the first validated answer): count document types RI invoices, RD "
    "recurring billing, RN manual billing, RJ sales overage, RT fees/interest and RM credit memos "
    "(netted off); EXCLUDE RX reimbursements (very large, ~94.7M in 2025 — mention them, offer to "
    "include), RL advances, RH account transfers, RZ cash collected in advance, RU unapplied cash. "
    "The main currency is USF (2 decimals, so divide stored amounts by 100) — report other currencies "
    "(EUF, LBF) separately or note them as excluded, never add currencies together silently. For "
    "revenue by account use only object accounts 5000-5999 and drop the automatic trade-account offset "
    "lines so VAT, suspense and accrual accounts are not counted. Rank by invoice G/L date (RPDGJ) "
    "using Julian ranges (2025 = 125001 to 125365). Customers with two address numbers (e.g. the same "
    "company under two numbers) appear twice — mention it and offer to combine by name.",
    "CUSTOM TABLES: ABC has many custom tables (F55xx, F58xx, F59xx). If a standard table does not "
    "answer a question, look for the custom table in F9860 (SIOBNM LIKE 'F55%' etc.) and its columns "
    "in F98711 before concluding the data is unavailable.",
    "Only write single SELECT statements. Never INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/MERGE.",
    'Do not invent results. If query_jde_database returns "No matching records were found", say so plainly.',
    "DEPARTMENTS: each key belongs to one department — procurement, finance, sales or hr — and can only "
    "read that department's tables plus the shared reference tables (JDE metadata F9860/F98711/F9202, "
    "UDCs F0004/F0005, Address Book F0101 family, business units F0006, company/currency setup). "
    "If a question needs a table outside the key's department, the server answers 'you don't have "
    "access to that data' — tell the user that plainly and which department would hold the data; do "
    "not try workarounds. Typical homes: sales = F4201/F4211/F42119 orders, F4101 items, F03B* customer "
    "invoices; procurement = F4301/F4311/F43121/F43199 purchasing, F0401 suppliers, F4101 items, "
    "planning/work orders; finance = F0911/F0902/F0901 ledger, F0411/F0413 payables, F03B* receivables, "
    "F12xx assets; hr = F06xx payroll/employees, F08xx.",
    "PATTERN: physical columns are prefixed per table — in standard JDE F4101 uses 'IM' (e.g. "
    "IMITM) and F4211 uses 'SD' (e.g. SDAN8, SDLTTR). Confirm this against F98711.TDSQLC on this "
    "database before trusting it, and verify any table's columns the same way before use — query "
    "F98711 for the real TDSQLC values, don't assume a bare data item alias is the physical "
    "column name.",
    "HR / PAYROLL TABLES are not described here (F06xx, F07xx, F08xx — employee master, payroll "
    "history, benefits). Discover them first: SELECT SIOBNM, SIMD FROM F9860 WHERE SIFUNO = 'TBLE' AND "
    "SIOBNM LIKE 'F06%', then get the real columns from F98711. Qualify them with the data schema "
    f"({SCHEMA_PREFIX_DEFAULT}.).",
    "OPEN vs HISTORY: open order lines live in F4211 (sales) and F4311 (purchasing); closed lines move "
    "to F42119 and F43199. For any question about a PAST period (sold in 2025, bought last year) query the "
    "history table — and add the open table only if open lines should count. Say which you used.",
    "AMOUNTS AND QUANTITIES are stored as integers with implied decimals (no decimal point). Currency "
    "amounts scale by the currency's decimals (F0013; 2 for most currencies), quantities and unit "
    "prices by the Data Dictionary decimals (commonly quantity 0-4, unit price 4). Never present a raw "
    "number as final: scale it, and cross-check against one known document, stating the convention you "
    "applied.",
    "F98711/F9202 joins need LTRIM(RTRIM()) on both sides of the join condition — JDE Data "
    "Dictionary fields are space-padded, which breaks exact-match joins. (T-SQL: use "
    "LTRIM(RTRIM(x)); do not use TRIM(), it only exists from SQL Server 2017.)",
    "BLANK VALUES: JDE stores 'blank' as a space in CHAR columns, not NULL, and SQL Server does not "
    "treat an empty string as NULL. To get the default-language Data Dictionary row, filter "
    "LTRIM(RTRIM(FRSYR)) = '' (and consider FRSYR IS NULL as well). Don't use Oracle's 'IS NULL' "
    "trick for blanks.",
    "T-SQL ONLY: write SELECT TOP n (not LIMIT / FETCH FIRST / ROWNUM), no FROM DUAL, no || "
    "concatenation, no CTEs (WITH), temp tables, variables or multiple statements, and use explicit "
    "JOIN ... ON rather than comma-separated tables.",
    "If a query fails with an unexpected column/table error on a table NOT yet listed here with a "
    "'VERIFIED' note, say so plainly rather than guessing alternate names — query F98711 for that "
    "table's real columns instead of retrying variations blindly.",
    "DISCOVERY MODE IS ON: you are not limited to only the tables described above (within your "
    "department). If asked about a table not listed here, you can and should look it up yourself: "
    "(1) query F9860 (filter SIFUNO = 'TBLE') to confirm the table exists and get its real title, "
    "(2) query F98711 for that table's real physical column names (TDSQLC), (3) join to F9202 (with "
    "LTRIM(RTRIM()) on both sides) for what each column means, (4) then query the actual table using "
    "those real, verified column names. Never guess a bare data item alias as a column name — always "
    "confirm via F98711 first.",
    "For a table not listed in this config, you don't know its schema by default — always "
    "schema-qualify it. If a query on a newly-discovered table fails with 'Invalid object name', "
    "it may live in a different schema — you can check with: SELECT TABLE_SCHEMA, TABLE_NAME FROM "
    "INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '<name>'.",
    "JDE date columns (suffix J, e.g. SDDRQJ; also SDIVD, GLDGJ) are stored in Julian format CYYDDD: "
    "C = century digit (0 = 1900s, 1 = 2000s), YY = two-digit year within century, DDD = day of year "
    "(1-366). Example: 119144 = May 24, 2019. A whole calendar year 2025 = BETWEEN 125001 AND 125365 "
    "(125366 in leap years). Filter on the raw Julian number (it uses indexes), then decode dates "
    "before presenting them rather than showing the raw number.",
    "STATUS CODES ARE NOT SAFE TO ASSUME: they differ per environment (in the reference deployment "
    "F4211.SDLTTR = '620' turned out to mean Sales Update / closed, not 'open'). Always check the "
    "relevant UDC table (F0005, filtered by the right DRSY/DRRT system+type code) before stating "
    "what a status code means, rather than relying on general JDE convention.",
    "GENERAL LEDGER: always filter ledger type (GLLT = 'AA' for actuals) and say whether you included "
    "unposted lines (GLPOST); never mix ledger types.",
]

# Derived — don't edit these directly, they're built from TABLES above.
ALLOWED_TABLES = {t["name"] for t in TABLES}
TABLE_SCHEMAS = {
    t["name"]: SCHEMA_OVERRIDES.get(t["name"], SCHEMA_PREFIX_DEFAULT) for t in TABLES
}
