# Project Management — Guide Index

Index page: https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/guides.html

| Guide | HTML | PDF |
|---|---|---|
| Job Cost Implementation Guide (cost code structures, job budgets, projected final values) | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoajc/index.html | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoajc/job-cost-implementation-guide.pdf |
| Contract and Service Billing Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoasb/index.html | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoasb/contract-and-service-billing-implementation-guide.pdf |
| Advanced Contract Billing Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoagc/index.html | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoagc/advanced-contract-billing-implementation-guide.pdf |
| Advanced Job Forecasting Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoapf/index.html | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoapf/advanced-job-forecasting-implementation-guide.pdf |
| Homebuilder Management Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoahm/index.html | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoahm/homebuilder-management-implementation-guide.pdf |
| In-Memory Project Portfolio Advisor Implementation Guide | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoaxc/index.html | https://docs.oracle.com/en/applications/jd-edwards/project-management/9.2/eoaxc/in-memory-project-portfolio-advisor-implementation-guide.pdf |
| Change Management Implementation Guide (shared w/ Supply Chain & Manufacturing) | https://docs.oracle.com/en/applications/jd-edwards/supply-chain-manufacturing/9.2/eoacm/index.html | https://docs.oracle.com/en/applications/jd-edwards/supply-chain-manufacturing/9.2/eoacm/change-management-implementation-guide.pdf |

Also frequently relevant: **General Accounting** (topic `ba-financials`) for job-cost-to-GL posting, **Payroll**/**Human Resources** (topic `ba-human-capital`) for labor cost capture against jobs, **Procurement Management** and **Subcontract Management** (topic `ba-supply-management`) for committed-cost tracking on jobs.

## What each guide covers (paraphrased summary — verify specifics against the live guide)

**Job Cost (eoajc).** Tracks cost and revenue for jobs/projects using a cost code structure (a chart-of-accounts-like breakdown of a job into cost codes/cost types) and job budgets set up per job. The system calculates projected final values throughout a job's life — an estimate of final cost/revenue based on costs, revenue, and percent-complete to date — recalculated as commitments, actuals, and budget changes occur. Reporting spans management-summary, job/account-setup, financial-detail, and supplemental-data reports. Feeds and is fed by: General Accounting (job-cost GL postings), Procurement/Subcontract Management (committed costs against a job), Payroll/Time and Labor (labor cost capture against a job), and Contract and Service Billing (billing for the job).

**Contract and Service Billing (eoasb).** The billing/revenue engine for both Project Management and Service Management. A contract defines billing lines (pay items) with billing-rate/markup rules, tax-derivation rules, and (for Service Billing specifically) G/L-offset and retainage rules; AAI tables (the 48xx series — Actual Revenue 4811, Tax Liability 4815, Accrued Revenue 4831, WIP 4841/COGS 4842, Revenue/Invoice Margin accounts, Not-to-Exceed offsets) drive where amounts post. Revenue can be recognized independently of invoicing, via flat-line, milestone, or percent-complete methods. Whether a given invoice actually flows into the AR revenue-recognition process (P03B116) depends on a chain of triggers: the Journal Generation Control billing constant (Invoice Only vs. Invoice/Revenue with or without reconciliation) plus a three-part trigger definition (hierarchy, dates, configuration records) set up on the AR side for contract billing, service billing, sales order, and real estate invoices respectively — all three trigger pieces must be defined before a contract billing line becomes eligible.

**Advanced Contract Billing (eoagc).** Extends the base Contract and Service Billing programs (Journal Generation R48132, Workfile Generation R48120, Invoice Generation R52121, Contract Billing Line Details P5202) to more complex government/commercial contract structures — the guide reuses rather than replaces the base billing engine, so most billing questions are really base Contract and Service Billing questions with contract-structure nuances layered on.

**Homebuilder Management (eoahm).** Manages the repetitive-building process — tract/community home construction where the same job structure repeats across many similar houses/lots — layered on top of Job Cost.

**Advanced Job Forecasting, In-Memory Project Portfolio Advisor, Change Management** — URL-indexed above but not deep-dived in this pass; `web_search` the guide title for specifics.
