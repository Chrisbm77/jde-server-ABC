# Human Capital Management — Guide Index

Index page: https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/guides.html

| Guide | Notes |
|---|---|
| Human Capital Management Fundamentals Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/eoahf/index.html |
| Human Resources Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/eoahr/index.html |
| Payroll Implementation Guide (base/global) | https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/eoapy/index.html |
| Canadian Payroll Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/eoapc/index.html |
| Benefits Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/eoacc/index.html |
| Time and Labor Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/eoatl/index.html |
| HCM Self-Service Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/human-capital/9.2/eoahs/index.html |
| US Payroll Implementation Guide | see guides.html for exact folder code |
| Australia/New Zealand Payroll Implementation Guide | see guides.html for exact folder code |
| US Payroll Year-End Processing Guide | see guides.html for exact folder code |
| Canadian Payroll Year-End Processing Guide | see guides.html for exact folder code |
| US Affordable Care Act Year-End Processing Guide | see guides.html for exact folder code |

For rows marked "see guides.html for exact code," fetch the master index above first to pick up the current 5-letter folder code and exact PDF filename.

Also frequently relevant: **Address Book** and **Foundation Guide** (topic `ba-cross-product-tools`), **General Accounting** (topic `ba-financials`) for payroll GL integration, **Job Cost** (topic `ba-project-management`) for labor-to-job costing.

## What each guide covers (paraphrased summary — verify specifics against the live guide)

**HCM Fundamentals (eoahf).** The shared foundation ("HCM Foundation") that HR, Payroll, and Time and Labor all read from — a single central database for employee info, job info, pay type/deduction/benefit/accrual (PDBA) info, and time/labor info, so that (for example) an HR clerk's update to an employee record is immediately visible to Payroll without re-entry. Usable standalone as a time-and-labor tracking system even without licensing Payroll. Field- and form-level security can restrict which parts of an employee's record different user types can see — important since HR and Payroll often need different visibility into the same records.

**Human Resources (eoahr).** Builds on HCM Foundation to manage the employee lifecycle: applicant tracking (Applicant Master F08401, compared against Employee Master F060116 to determine "hired" status for EEO/adverse-impact reporting), compensation management, position budget management (defining and tracking budgeted positions, with example budget-processing walkthroughs in the guide), and standard US government reporting (EEO-1). Integrates with Address Book, HCM Foundation, Payroll, General Accounting, Accounts Payable, and Asset Lifecycle Management (e.g. for equipment assigned to an employee).

**Payroll (eoapy, plus country-specific US/Canadian/ANZ guides layered on the same base).** The payroll cycle is a fixed five-step sequence run every pay period: **pre-payroll** (select employees into a "payroll ID," generate timecards for autopay employees, process manually entered timecards, calculate gross-to-net, and produce review reports for PDBAs/taxes/overrides) → **print payments** → **journal entries** (creates pro-forma entries in F063951 first for review via the Payroll Journal Proof/Edit report R05229, before actual entries are posted) → **payroll reports** → **final update** (posts actual journal entries to F0911, and optionally F0902, if a company option enables auto-post; otherwise entries must be posted manually). A payroll ID is created once per employee group (salaried, hourly, interim-only, bonus run, etc.) and reused across pay periods rather than recreated each cycle. Interim payments handle off-cycle needs — terminations, advances, bonuses, gross-ups, advance vacation pay. Supports up to 9,000 employee/employer DBAs, master pay cycles, and multi-company processing with journals kept in balance across companies. Country-specific guides (Canadian, US, ANZ) layer statutory tax/reporting requirements on top of the same five-step cycle — the steps themselves don't change per country.

**Benefits (eoacc).** Plan administration and employee enrollment. Plans carry eligibility criteria (age, length of service, employment status) and enrollment/open-enrollment periods; a benefit group (e.g. "EXEC") categorizes plans and enrollment rules for a class of employees. Two ways to model tiered coverage (e.g. employee-only vs. employee+family): separate plans per tier, or one plan with multiple "options" — the guide gives trade-offs for each (separate plans support mandatory/default rules and prerequisite-plan dependencies; a single plan with options avoids having to end/recreate a whole plan just to add or remove a tier). Every plan is linked to one or more DBAs — a deduction-type DBA withholds the employee-paid cost from pay, a benefit-type DBA tracks the employer-paid cost — resolved through a category/benefit-group/plan-master hierarchy when the system calculates what to actually withhold.

**Time and Labor (eoatl).** Captures the timecard — a one-line time-entry record — that both Payroll and job-cost accounting depend on. Mandatory if Payroll is used (payroll processing can't run without timecards) but usable standalone to post labor/equipment expense to the GL if Payroll isn't licensed. Timecards can be entered manually, uploaded in batch from a third-party time-collection system, or auto-generated (e.g. for autopay employees during the payroll cycle, or for a whole group during a company holiday/bonus run). Supports automatic overtime-rate calculation, retroactive pay, and a rules engine keyed off batch source type codes (which overtime rule set, retro-pay rule, or timecard template applies to a batch) and employee group codes (which employees a given time-management run covers). Journal entries follow the same pro-forma → actual pattern as Payroll (F063951 preliminary, then F0911/F0902 on posting) and can run daily for organizations that need to monitor labor cost in near-real-time rather than waiting for a full payroll cycle.

**HCM Self-Service (eoahs).** Web self-service layer for employees and managers — which features are available depends on which base modules (HR, Payroll, Time and Labor) are licensed. Employee self-service typically covers benefits enrollment (open enrollment or life-event-triggered), personal profile/dependent/beneficiary maintenance, pay-stub review, leave requests, and self-appraisal; manager self-service adds approval workflows on top.

**Year-End Processing guides (US Payroll, Canadian Payroll, US ACA)** — statutory annual-close guides, not deep-dived here; `web_search` the guide title for the current tax-year specifics since these tend to update yearly.
