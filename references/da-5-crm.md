> **ABC note.** ABC's database is Microsoft SQL Server, so queries are T-SQL. Where an example below is written for Oracle,
> translate it: `TRIM(x)` -> `LTRIM(RTRIM(x))`; `a || b` -> `a + b`; `ROWNUM` / `FETCH FIRST n` -> `SELECT TOP n`;
> `TO_DATE`/`TO_CHAR` date conversion -> the SQL Server form shown in section 0.3 of topic `da-0-rules`.
> No CTEs (`WITH`), no temp tables, one SELECT per call. Use the table names exactly as `get_jde_schema` shows them (with their schema prefix).
> "The live database connector" in this text means the `query_jde_database` tool. Blank values are spaces, not NULL.

# JDE data architecture — Part 5. JDE Customer Relationship Management

## Part 5. JDE Customer Relationship Management

Sources: CRM Fundamentals, CRM for Sales, CRM for Support, Customer Self Service, In-Memory Sales Advisor, Service Management, plus Sales Order Management and Advanced Pricing (the same two PDFs also sit in the Supply Chain folder; their tables are documented in Part 4.2).

### 5.1 How CRM data hangs together

CRM in EnterpriseOne is a layer on top of the Address Book and the sales and service transaction tables, not a separate customer database.

```
F0101 Address Book (AN8) ── customer F03012 ── contacts F0111 (+ F0115 phones, F01151 e-mail, F01161 alternate address)
        │
        ├── Sales force automation: lead → opportunity (F90CB020) → quote / sales order (F4201/F4211) → forecast (F90CB060)
        ├── Support: case (F1755) → tasks (F1757) / time (F1760) → billing workfile F4812 → invoice F03B11
        └── Service: installed base (equipment F1201/F1217) → contract (F1721) → service work order (F4801/F4817) → billing F4812
```

- CRM is switched on through the system control file F99410 (record `SY90CA`; `CRMMSL` for mobile sales). If the record is missing, CRM logic does not run and CRM tables stay empty.
- Customer and contact data are the standard address book tables. When a lead is converted, the system creates the customer (address book + F03012), the contact (who's who) and the opportunity.
- Sales-order extension tables F4201UR / F4211UR / F4210UR hold CRM user-reserved columns for orders created from opportunities.

### 5.2 CRM Sales (systems 90CA, 90CB)

| Table | Name | Notes |
|---|---|---|
| F90CA080 | Customer table | CRM customer record created from a lead's company name |
| F90CA070 | Contact table | CRM contact created from a lead |
| F90CA060 / F90CA06A | Competitor / Competitor_Product | key `CMAN8`; competitor items |
| F90CA12B / F90CA14A | Industry Grouping Employee / Territory Employee | sales team assignment by industry and territory |
| F90CA61E | Activity–Opportunity associative table | links calendar activities (F01301) to opportunities |
| F90CB010 / F90CB01A | Lead / Lead Address | |
| F90CB020 | Opportunity | key `OPPID` |
| F90CB02I | Opportunity_Item | key `OPPID, LNID`; products on the opportunity |
| F90CB02C / F90CB02D / F90CB02E | Opportunity_Competitor / _Contact / _Employee | |
| F90CB02J | Opportunity_Sales_Cycle | stage history |
| F90CB02M | Opportunity_Cost | key `COSTID` |
| F90CB030 | CRM Address | |
| F90CB040–F90CB043 | Qualification, _Answer, _Question, _Object | qualification scripts and scores |
| F90CB050 / F90CB05A / F90CB05B | Sales Methodology / Sales Cycle / Opportunity Sale Driver | pipeline stages and probabilities |
| F90CB060 | Forecast | key `FCID` |
| F90CB06A | Forecast Opportunity | live link; deleted when the forecast is frozen |
| F90CB06B / F90CB06C | Opportunity_For_Forecast / Opportunity_Item_For_Forecast | frozen snapshot (`FCID, OPPID` …) |
| F42140 | Customer Master Commission Information | sales team members assigned to a customer |
| F011901 | Contacts Subscription | contacts synchronised to a personal information manager |

Pipeline analysis: F90CB020 (amount, close date, probability, sales cycle step) joined to F90CB02I items and F90CB02E team; conversion to orders through the sales-order tables; frozen forecasts from F90CB06B/F90CB06C so history does not move when opportunities change.

### 5.3 CRM Support — cases (system 17 / 90CG)

| Table | Name | Notes |
|---|---|---|
| F1755 | Case Master | key in the composite-key appendix: `STAW, DOCO, UPMJ, UPMT`; one row per case (case number is an order number) with customer, product/equipment, priority, status, provider group, assignee, dates |
| F1757 | Task Master | tasks under a case |
| F1760 | Case time entry | time records; with F1755 the source for case billing |
| F1753 | Priority / escalation definitions | escalation percentages by priority |
| F90CG506 | Provider-group assignees and skill levels | routing of cases |
| F90CG503 | Case associations | links between a case and work orders or other cases |
| F1791 | Entitlement Dates | entitlement checking against contracts |
| F1725 | Service Contract Services | service types, response times and non-covered G/L codes |
| F4117 / F41171 | Item Master / Item Branch – Service/Warranty Extension | service attributes of items |
| F1790 | Product Family/Model Master | |
| F1797 | S/WM Address Book Information | service extension of F0101 |
| F90CF030, F90CF03A, F90CF040, F90CF060–F90CF180 | Branch scripting tables | scripts, questions, answers and their translations |

Case billing: Case Workfile Generation (R17675) reads billable F1755/F1760 rows and writes **F4812 Billing Detail Workfile**; invoicing then follows the service-billing path (F4822 invoice summary → F03B11/F0911). Case time can also create payroll time entry (F06116Z1) or journal entries (F0911Z1).

### 5.4 Service Management (system 17)

| Table | Name | Notes |
|---|---|---|
| F1201 + F1217 | Asset Master File + Equipment Master Extension | the installed base: every serviced product is an equipment record; F1217 holds product model/family, customer and site, warranty data |
| F1731 / F17311 | Equipment Master Location History / Location Details | owner and site history; mailing data and geocode |
| F1721 | Contract Detail | service contract and base-warranty lines (customer, equipment or product model, service package, coverage dates, billing data) |
| F1725 / F1729 | Service Contract Services / Service Package | what a package covers |
| F1794 | Billing/Amortization Control Master | billed and amortised periods per contract line |
| F15019 | Billing Frequency Master | shared with Real Estate |
| F1793 | S/WM Line Type Constants | responsible business unit and accounting behaviour by line type |
| F17111 / F17113 | Base Warranty Defaults / Assessor Defaults | |
| F4801 + F4817 | Work Order Master + Service Order Extension | service work orders (same F4801 as manufacturing and maintenance; F4801T tag) |
| F3111 + F31171 | Work Order Parts List + Parts Extension | parts used, with billable/payable amounts |
| F3112 + F31172 | Work Order Routing + Routing Instructions Extension | labor steps, with billed/paid dates and billable/payable units and amounts |
| F4812 / F4812H | Billing Detail Workfile / history | billable transactions from contracts, service orders and cases (key `BCI, DGL, SBSQ, PRSQ, SCSQ, SLNK, CLNK, CCOD`) |
| F4822 / F4823 | Invoice Summary Work File / Voucher Summary | invoice and voucher pay items generated from the workfile |
| F1307 | Status History File | equipment and work-order status changes |
| F4220 | Basic Serial Numbers | serial numbers captured at shipment |

Flow: shipment confirmation of a serialised item can create the equipment record → base warranty contract in F1721 → service order in F4801/F4817 with parts and labor → Workfile Generation writes F4812 → invoice (F4822 → F03B11 + F0911) and, for supplier recovery or payable service providers, voucher (F4823 → F0411). Contract revenue is amortised through F1794 with journal entries in F0911.

### 5.5 In-Memory Sales Advisor (42X) and Customer Self Service (42S)

- Sales Advisor reads F4211 and F42119 to suggest cross-sell, up-sell and frequently bought items: F42X000 Sales Advisor Constants, F42X001 included document types, F42X010 Buying Frequency by Customer (maintained as orders are entered); F42X010W, F42X020W, F42X040W, F42X041W, F42X050W, F42X060W are purgeable work files; profitability simulator F42X201 scenarios, F42X201B charts, F42X201C data.
- Customer Self Service has no data of its own: it reads and writes F4201/F4211/F42119, items F4101/F4102 and cross-references F4104, restricted to the signed-on customer's address number.

### 5.6 Analysis recipes

- **Pipeline by stage, owner, expected close**: F90CB020 with F90CB02J (stage) and F90CB02E (team); weight by probability; compare with frozen forecast rows F90CB06B/F90CB06C.
- **Win/loss and competitor analysis**: F90CB020 status with F90CB02C and F90CA060/F90CA06A.
- **Lead conversion**: F90CB010 leads vs created F0101/F03012 customers and F90CB020 opportunities.
- **Case volume, backlog and resolution time**: F1755 by status, priority, provider group, product; durations from the case dates; effort from F1760.
- **Contract coverage and renewals**: F1721 by customer and equipment with coverage dates; billing status in F1794; entitlement dates in F1791.
- **Service cost and revenue per equipment or customer**: service work orders in F4801 (subledger type `W` in F0911), parts F3111/F31171, labor F3112/F31172, billed amounts in F4812/F4812H and F03B11.
- **Customer 360**: F0101 + F03012 + F0111 contacts → open orders F4211 → history F42119/F4229 → open A/R F03B11 → cases F1755 → contracts F1721 → equipment F1217.

### 5.7 Tables named in these guides

F0101, F0111, F01112, F0115, F01151, F0116, F01161, F0117, F0118, F0150, F011901, F01301, F03012, F42140, F4201UR, F4210UR, F4211UR, F99410, F90CA060, F90CA06A, F90CA070, F90CA080, F90CA12B, F90CA14A, F90CA61E, F90CB010, F90CB01A, F90CB020, F90CB02C, F90CB02D, F90CB02E, F90CB02I, F90CB02J, F90CB02M, F90CB030, F90CB040–F90CB043, F90CB050, F90CB05A, F90CB05B, F90CB060, F90CB060Z, F90CB06A, F90CB06B, F90CB06C, F1753, F1755, F1757, F1760, F1791, F1725, F1729, F1790, F1793, F1794, F1797, F17111, F17113, F1721, F1731, F17311, F4117, F41171, F4220, F4801, F4801T, F4817, F3111, F31171, F3112, F31172, F4812, F4822, F4823, F90CG503, F90CG506, F90CF030–F90CF180, F42X000, F42X001, F42X010, F42X010W, F42X020W, F42X040W, F42X041W, F42X050W, F42X060W, F42X201, F42X201B, F42X201C.
