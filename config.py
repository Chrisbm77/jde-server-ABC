"""
JDE AI Assistant — Client Configuration (ABC, Microsoft SQL Server)
=========================================================================

>>> BEFORE GO-LIVE: this file was ported from the reference deployment. The
>>> department catalog below is generic JDE and carries over unchanged, but
>>> every ABC-specific fact still has to be confirmed against ABC's own
>>> database — look for "TODO(ABC)". Nothing marked VERIFIED in the
>>> reference deployment is assumed true here.

CURRENT STATE: JDE metadata tables (Object Librarian, Table Design, Data
Dictionary) plus two business tables (F4101, F4211, carried over, to re-verify), with
DISCOVERY MODE on — the assistant can query any table the database
account can see, not just the ones listed below, using F9860/F98711/F9202
to self-discover real structure first.

To adapt this for a new client, or to lock this down before a client
deployment: set RESTRICT_TO_APPROVED_TABLES = True and curate TABLES
down to a reviewed, verified list.
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
# Optional per-department table boundaries, keyed by whatever string you
# put in a client's "department" field in clients.json. A deployment with
# NO department set gets full access (subject only to
# RESTRICT_TO_APPROVED_TABLES above) — this is meant for an internal/admin
# key, not a department-scoped client deployment.
#
# IMPORTANT: this boundary is enforced ALWAYS when a department is set,
# even in discovery mode.
#
# Two layers, checked in order:
#   1. DEPARTMENT_TABLES (below) — EXACT table membership, derived directly
#      from the jde-understanding skill's 382-table catalog (itself sourced
#      from Oracle's official module documentation). This is the precise,
#      real answer to "does Sales actually use this table" — not a prefix
#      guess. Regenerate this by re-running the same catalog-parsing
#      process if the skill's catalog grows.
#   2. DEPARTMENT_TABLE_PREFIXES (further below) — a coarser prefix-based
#      FALLBACK, used only for a table that's real and matches a
#      department's module range but isn't (yet) one of the 382 catalogued
#      tables. This is what lets discovery mode keep working for tables
#      outside the catalog, without losing the department boundary.
#
# A department string with NO matching entry in EITHER dict fails CLOSED —
# denied entirely, not silently given full access. Double-check spelling
# against these dicts when adding a new client's department in
# clients.json.
#
# Four modules from the catalog were deliberately left OUT of every
# department below: Homebuilder Management/WIP and Real Estate Management
# (only relevant if a client is literally in those industries — add a
# department for them if that ever applies), and everything under
# Country-Specific Localizations (a documented pattern, not a fixed table
# list, in the catalog itself). A new "support" department was added to
# cover CRM/Case Management and Service Management (CSMS), which didn't
# fit any of the original six.
DEPARTMENT_TABLES = {
    "sales": {
        "F00090", "F00090D", "F00091", "F00092", "F0070", "F0101", "F0101A", "F01090",
        "F01092", "F01093", "F0111", "F01112", "F01138", "F0115", "F01151", "F0116",
        "F01161", "F0117", "F0118", "F011901", "F01301", "F01301W", "F01302", "F01311",
        "F01321", "F01331", "F01401", "F01411", "F0150", "F01501", "F01815", "F03012",
        "F03B11", "F03B112", "F03B13", "F03B14", "F03B16", "F03B20", "F03B21", "F03B22",
        "F03B23", "F03B41", "F0401", "F34004", "F4001Z", "F40039", "F4009", "F40095",
        "F4016", "F4017", "F4072", "F4074", "F4075", "F4078", "F4095", "F4096",
        "F4100", "F41001", "F41002", "F41003", "F41006", "F4101", "F41013", "F4102",
        "F41021", "F41023", "F4104", "F4105", "F4106", "F4108", "F41081", "F4111",
        "F41112", "F41113", "F4115", "F4140", "F4141", "F4160", "F4170", "F41829",
        "F4201", "F4209", "F4211", "F42119", "F42199", "F42420", "F4314", "F4550",
    },
    "purchasing": {
        "F00090", "F00090D", "F00091", "F00092", "F0070", "F0101", "F0101A", "F01090",
        "F01092", "F01093", "F0111", "F01112", "F01138", "F0115", "F01151", "F0116",
        "F01161", "F0117", "F0118", "F011901", "F01301", "F01301W", "F01302", "F01311",
        "F01321", "F01331", "F01401", "F01411", "F0150", "F01501", "F01815", "F03012",
        "F0401", "F0902", "F34004", "F40039", "F4009", "F40095", "F4015", "F4016",
        "F4017", "F40203", "F4090", "F4095", "F4100", "F41001", "F41002", "F41003",
        "F41006", "F4101", "F41013", "F4102", "F41021", "F41023", "F4104", "F4105",
        "F4106", "F41061", "F4108", "F41081", "F4111", "F41112", "F41113", "F4115",
        "F4140", "F4141", "F4160", "F4170", "F41829", "F4209", "F43001", "F43008",
        "F4301", "F4301Z", "F4301Z1", "F4303", "F4303M", "F4304", "F4305", "F43080",
        "F43090", "F43091", "F43092", "F43092Z", "F43092Z1", "F43093", "F43094", "F43099",
        "F43100", "F4311", "F4311T", "F4311Z", "F4311Z1", "F43121", "F43121T", "F43121Z",
        "F43121Z1", "F43126", "F43126T", "F43127", "F4314", "F43146T", "F43147", "F4314Z",
        "F4316", "F4316M", "F4316T", "F4317", "F4318", "F43199", "F4321", "F43211",
        "F43213", "F4322", "F4330", "F4331", "F4332", "F4333WF", "F4340", "F4341",
        "F4342", "F4343", "F4350", "F4351", "F4355", "F43632Z", "F4371", "F43800",
        "F43E01", "F52034",
    },
    "finance": {
        "F0002", "F0005", "F0006", "F0006S", "F0008", "F0009", "F0010", "F0011",
        "F0012", "F0018", "F0025", "F0070", "F0101", "F0101A", "F01090", "F01092",
        "F01093", "F0111", "F01112", "F01138", "F0115", "F01151", "F0116", "F01161",
        "F0117", "F0118", "F011901", "F01301", "F01301W", "F01302", "F01311", "F01321",
        "F01331", "F01401", "F01411", "F0150", "F01501", "F01815", "F03012", "F03B11",
        "F03B112", "F03B13", "F03B14", "F03B16", "F03B20", "F03B21", "F03B22", "F03B23",
        "F03B41", "F0401", "F0401M", "F0411", "F0411Z1", "F0413", "F0414", "F0901",
        "F0902", "F0911", "F1201", "F1202", "F4812", "F4812H", "F4822", "F48520",
        "F5202", "F5204", "F5212", "F5213", "F5216",
    },
    "inventory": {
        "F00090", "F00090D", "F00091", "F00092", "F34004", "F40039", "F4009", "F40095",
        "F4016", "F4017", "F4095", "F4100", "F41001", "F41002", "F41003", "F41006",
        "F4101", "F41013", "F4102", "F41021", "F41023", "F4104", "F4105", "F4106",
        "F4108", "F41081", "F4111", "F41112", "F41113", "F4115", "F4140", "F4141",
        "F4160", "F4170", "F41829", "F4215", "F4600", "F4601", "F46010", "F46011",
        "F46012", "F46013", "F4602", "F46021", "F46022", "F46024", "F46025", "F46026",
        "F46027", "F46051", "F46091", "F46092", "F46093", "F46095", "F46096", "F4611",
        "F46130", "F46821", "F46822", "F49211", "F49301", "F4941", "F4945", "F4950",
        "F4960", "F4961", "F49611", "F4972", "F49721", "F4973", "F4977", "F4981",
        "F49T90",
    },
    "hr": {
        "F00091", "F00092", "F060116", "F060117", "F06017", "F0607", "F0609", "F06106",
        "F06107", "F061071", "F06116", "F06116Z1", "F06136", "F06145", "F06146", "F06147",
        "F06210", "F062101", "F062102", "F065016", "F08042", "F08045", "F08102", "F08105",
    },
    "manufacturing": {
        "F0006", "F0007", "F00090", "F00090D", "F00091", "F00092", "F00191", "F0101",
        "F0901", "F0911", "F12002", "F12003", "F1201", "F1202", "F1204", "F1205",
        "F1206", "F1207", "F12071", "F1210", "F1212", "F1215", "F1216", "F1217",
        "F1301", "F1305", "F1307", "F1390", "F1391", "F1731", "F30006", "F30008",
        "F3002", "F300210", "F300211", "F30026", "F3003", "F300311", "F3007", "F3009",
        "F3011", "F3013", "F3015", "F3016", "F30161", "F30L912", "F3102", "F3105",
        "F3108", "F3109", "F31091", "F3111", "F3112", "F31122", "F3118", "F31B03",
        "F31B04", "F31B13", "F31B31", "F31B31C", "F31B37", "F31B65", "F31B66", "F31B70",
        "F31B73", "F3293", "F3400", "F34004", "F3411", "F3412", "F3413", "F3430",
        "F3435", "F3450", "F3460", "F34X001", "F34X010", "F34X100W", "F34X101W", "F34X110W",
        "F34X200W", "F3712", "F40039", "F4009", "F40095", "F4016", "F4017", "F40205",
        "F4091", "F4095", "F40G002", "F4100", "F41001", "F41002", "F41003", "F41006",
        "F4101", "F41013", "F4101M", "F4102", "F41021", "F41023", "F4104", "F4105",
        "F4106", "F4108", "F41081", "F4111", "F41112", "F41113", "F4115", "F4140",
        "F4141", "F4160", "F4170", "F41829", "F4600", "F4602", "F4611", "F4801",
        "F4802", "F4808", "F48092", "F4818", "FF31010", "FF31011",
    },
    "support": {
        "F0070", "F0101", "F0101A", "F01090", "F01092", "F01093", "F0111", "F01112",
        "F01138", "F0115", "F01151", "F0116", "F01161", "F0117", "F0118", "F011901",
        "F01301", "F01301W", "F01302", "F01311", "F01321", "F01331", "F01401", "F01411",
        "F0150", "F01501", "F01815", "F03012", "F0401", "F0911", "F12002", "F12003",
        "F1201", "F1202", "F1204", "F1205", "F1206", "F1207", "F12071", "F1210",
        "F1212", "F1215", "F1216", "F1217", "F1301", "F1305", "F1307", "F1390",
        "F1391", "F1720", "F1721", "F1724", "F1725", "F1726", "F1729", "F1731",
        "F17311", "F1750", "F1751", "F1752", "F1753", "F1754", "F1755", "F1757",
        "F1758", "F1759", "F1760", "F1761", "F1790", "F1791", "F1792", "F1793",
        "F1794", "F1797", "F18001", "F1810", "F1811", "F18111", "F1812", "F18121",
        "F18122", "F1820", "F1830", "F4801", "F90CA060", "F90CB020", "F90CG503",
    },
}

# Fallback prefix matching — only reached for a table NOT in DEPARTMENT_TABLES
# above (i.e. real but not yet catalogued). Keeps discovery mode useful for
# uncatalogued tables without losing the department wall.
DEPARTMENT_TABLE_PREFIXES = {
    "sales": ["F42", "F03B", "F40", "F41"],
    "purchasing": ["F43", "F40", "F41"],
    "finance": ["F09", "F00", "F03B", "F04", "F52"],
    "inventory": ["F41", "F46"],
    "hr": ["F06", "F08"],
    "manufacturing": ["F30", "F31", "F34", "F41"],
    "support": ["F17", "F90C"],
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
        "name": "F4101",
        "description": "Item Master",
        "columns": [
            ("IMITM", "TEXT", "Item Number (Short) — JDE's internal short item number, primary key. Carried over from the reference deployment; not yet verified on ABC's database."),
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
        "description": "Sales Order Detail",
        "columns": [
            ("SDDOCO", "INTEGER", "sales order number. Carried over, not yet verified on ABC."),
            ("SDAN8", "INTEGER", "customer number. Carried over, not yet verified on ABC."),
            ("SDITM", "TEXT", "item number, references F4101.IMITM. Carried over, not yet verified on ABC."),
            ("SDSOQS", "REAL", "quantity ordered. Carried over, not yet verified on ABC."),
            ("SDUPRC", "REAL", "unit price. Carried over, not yet verified on ABC."),
            ("SDDRQJ", "TEXT", "requested date, JDE Julian CYYDDD (see the Julian date rule below). Carried over, not yet verified on ABC."),
            ("SDLTTR", "TEXT", "line status code (UDC 40/AT). Status meanings are set per environment — do NOT assume them. In the reference deployment '545' = Pick Confirmation (in-process), '620' = Sales Update (closed), '980' = Canceled, but ABC's codes must be read from UDC 40/AT (F0005) before stating what any code means."),
        ],
        "notes": [
            "Physical columns on this table are prefixed with 'SD' in standard JDE (confirm via F98711.TDSQLC on ABC). "
            "F4211 has 268 columns total, including 20 user-defined status fields (SDSO01-SDSO20) "
            "for custom order-status tracking beyond the standard SDLTTR field.",
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
        "What is item 10001?",
        "SELECT IMITM, IMDSC1, IMUOM1 FROM {F4101} WHERE IMITM = '10001';",
    ),
    (
        "Show open sales orders for customer 12345.",
        "SELECT SDDOCO, SDITM, SDSOQS, SDUPRC, SDDRQJ FROM {F4211} WHERE SDAN8 = 12345 AND SDLTTR = '545';",
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
    "Only write single SELECT statements. Never INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/MERGE.",
    'Do not invent results. If query_jde_database returns "No matching records were found", say so plainly.',
    "PATTERN: physical columns are prefixed per table — in standard JDE F4101 uses 'IM' (e.g. "
    "IMITM) and F4211 uses 'SD' (e.g. SDAN8, SDLTTR). Confirm this against F98711.TDSQLC on this "
    "database before trusting it, and verify any table's columns the same way before use — query "
    "F98711 for the real TDSQLC values, don't assume a bare data item alias is the physical "
    "column name.",
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
    "DISCOVERY MODE IS ON: you are not limited to only the tables described above. If asked about "
    "a table not listed here, you can and should look it up yourself: (1) query F9860 (filter "
    "SIFUNO = 'TBLE') to confirm the table exists and get its real title, (2) query F98711 for that "
    "table's real physical column names (TDSQLC), (3) join to F9202 (with LTRIM(RTRIM()) on both "
    "sides) for what each column means, (4) then query the actual table using those real, verified "
    "column names. Never guess a bare data item alias as a column name — always confirm via F98711 "
    "first.",
    "For a table not listed in this config, you don't know its schema by default — always "
    "schema-qualify it. If a query on a newly-discovered table fails with 'Invalid object name', "
    "it may live in a different schema — you can check with: SELECT TABLE_SCHEMA, TABLE_NAME FROM "
    "INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '<name>'.",
    "JDE date columns (suffix J, e.g. SDDRQJ) are stored in Julian format CYYDDD: C = century digit "
    "(0 = 1900s, 1 = 2000s), YY = two-digit year within century, DDD = day of year (1-366). Example: "
    "119144 = century 1 (2000s) + year 19 (2019) + day 144 of that year = May 24, 2019. Decode these "
    "before presenting dates to the user rather than showing the raw Julian number, and say so if "
    "you're not confident about a specific value's conversion.",
    "STATUS CODES ARE NOT SAFE TO ASSUME: they differ per environment (in the reference deployment "
    "F4211.SDLTTR = '620' turned out to mean Sales Update / closed, not 'open'). Always check the "
    "relevant UDC table (F0005, filtered by the right DRSY/DRRT system+type code) before stating "
    "what a status code means, rather than relying on general JDE convention.",
]

# Derived — don't edit these directly, they're built from TABLES above.
ALLOWED_TABLES = {t["name"] for t in TABLES}
TABLE_SCHEMAS = {
    t["name"]: SCHEMA_OVERRIDES.get(t["name"], SCHEMA_PREFIX_DEFAULT) for t in TABLES
}
