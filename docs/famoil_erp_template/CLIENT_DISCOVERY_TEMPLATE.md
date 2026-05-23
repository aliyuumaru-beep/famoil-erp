# Client Discovery Template
# FamOil ERP Framework — Pre-Implementation Discovery

_Version: 1.0 | Date: 2026-05-22_
_Complete this document in the first client meeting. Aim to finish within 2–3 sessions._

---

## How to Use This Template

- Fill one section per meeting. Do not rush.
- Leave blanks rather than guessing — blanks are safer than wrong answers.
- Answers here directly drive BOM configuration, chart of accounts structure, and module selection.
- Flag contradictions immediately — clients often describe the same process differently across sessions.

---

## Section 1 — Business Profile

| Field | Response |
|---|---|
| Legal entity name | |
| Trading name (if different) | |
| RC number (CAC) | |
| TIN | |
| NAFDAC registration number(s) | |
| SON certification(s) | |
| Primary industry / sector | |
| Location(s) of operation | |
| Number of production sites | |
| Number of employees | |
| Annual throughput (approx.) | kg/year |
| Annual revenue (approx.) | ₦ |
| Reporting currency | ₦ (default) / other: |
| Financial year end | |
| Current ERP / accounting software | |
| Go-live target date | |

### Key Stakeholders

| Role | Name | Email | Phone | Decision Authority |
|---|---|---|---|---|
| Project sponsor | | | | Final approval |
| Operations lead | | | | Production config |
| Accounts lead | | | | Chart of accounts |
| IT / systems lead | | | | Technical |
| Warehouse / store lead | | | | Inventory |

---

## Section 2 — Raw Materials

Complete one row per raw material.

| # | Material Name | UoM | Typical Batch Qty | Source (local/import) | Supplier Count | Price Range (₦) | Shelf Life | Storage Condition | Lot Tracking? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| 3 | | | | | | | | | |
| 4 | | | | | | | | | |
| 5 | | | | | | | | | |

### Raw Material Notes

- Are any inputs sourced seasonally (e.g., harvest windows)? If yes, which and when?
- Are any inputs imported? If yes, what is the typical lead time?
- How is incoming quality checked today? (Visual / lab test / weight / moisture)
- Is there a rejection / return process for substandard RM?

---

## Section 3 — Production Process

### 3.1 Production Stages

List every stage in order. Add rows as needed.

| # | Stage Name | Equipment / Machine | Typical Duration (min) | Labour Required | Consumables Used | Waste / Loss at this Stage |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |

### 3.2 Outputs and Yield

| # | Output Name | Type | Typical Yield (%) | Commercial Value? | UoM | Destination (sale / reprocess / dispose) |
|---|---|---|---|---|---|---|
| 1 | (main output) | Main | | Yes | | |
| 2 | | Byproduct | | | | |
| 3 | | Byproduct | | | | |
| 4 | | Waste | | No | | |

> **[Flag]:** Yield percentages must sum to ~100% across all outputs + losses. If they do not, the BOM will not balance.

### 3.3 Batch Size

| Question | Answer |
|---|---|
| Standard batch size (kg or units) | |
| Minimum batch size | |
| Maximum batch size | |
| Can batch size vary mid-production? | |
| How many batches per day (typical) | |
| How many batches per day (maximum) | |

### 3.4 Quality Control

| QC Point | What is checked | Pass/Fail criteria | Who checks | Documented today? |
|---|---|---|---|---|
| Incoming RM | | | | |
| In-process | | | | |
| Finished goods | | | | |

---

## Section 4 — Costing Requirements

| Question | Answer |
|---|---|
| How do you currently cost your products? | |
| Do you track actual vs standard cost? | |
| Do you need real-time cost per batch? | |
| Do you need cost broken down by work center? | |
| Are byproduct costs tracked separately? | |
| How are overhead costs currently allocated? | |
| Do you need cost centre reporting? | |
| How many cost centres? | |
| Preferred inventory costing method | Average / FIFO / LIFO / Standard |

### Labour Cost

| Question | Answer |
|---|---|
| Number of direct production workers | |
| Labour cost per worker per hour (₦) | |
| Shift structure | |
| Is overtime tracked? | |
| Do you need labour cost in BOM? | |

### Utility Cost

| Utility | Monthly Cost (₦) | Allocation Method |
|---|---|---|
| Electricity | | Per machine-hour / per batch / % |
| Diesel / generator | | |
| Water | | |
| Gas | | |

---

## Section 5 — Regulatory Requirements

Answer Yes / No / Unknown for each. Flag all "Yes" answers for deeper discussion.

| Requirement | Applicable? | Current Status | Notes |
|---|---|---|---|
| NAFDAC product registration | | | |
| SON product certification | | | |
| FIRS VAT registration (≥₦25M turnover) | | | |
| WHT deductions from vendors | | | |
| PENCOM registration + remittances | | | |
| ITF remittance (1% payroll) | | | |
| NSITF remittance (1% payroll) | | | |
| State-level business permit | | | |
| Environmental permit (FMEnv / NESREA) | | | |
| Export documentation (NXP, NAFDAC export cert) | | | |
| Halal / organic certification | | | |

### Tax Profile

| Tax Area | Details |
|---|---|
| VAT-registered? | Yes / No |
| VAT number (if registered) | |
| What do you sell that is VAT-exempt? | |
| What do you purchase with VAT? | |
| Are your customers mostly VAT-registered? | |
| Do you currently deduct WHT from suppliers? | |
| Which payment categories attract WHT? | |

---

## Section 6 — Existing Systems

| System | Software / Tool | Version | In Use Since | Will it be replaced? |
|---|---|---|---|---|
| Accounting | | | | |
| Inventory | | | | |
| Production tracking | | | | |
| Sales / CRM | | | | |
| Payroll | | | | |
| HR | | | | |
| Banking | | | | |

### Data Migration

| Question | Answer |
|---|---|
| Is there historical data to migrate? | |
| How many years of history needed? | |
| Is current data in digital format? | |
| Who owns data extraction from old system? | |
| What is the agreed opening balance date? | |
| Are there open purchase orders at go-live? | |
| Are there open sales orders at go-live? | |
| Are there open manufacturing orders at go-live? | |

---

## Section 7 — Implementation Constraints

### Technical

| Constraint | Detail |
|---|---|
| Internet reliability at site | Stable / Intermittent / None |
| Power reliability | Stable / Generator-dependent |
| Number of users | |
| Device types (PC / tablet / mobile) | |
| Server preference | Cloud / On-premise / Either |
| IT support available on-site | Yes / No |

### Organisational

| Constraint | Detail |
|---|---|
| Key staff availability for training | |
| Blackout periods (no go-live) | e.g., harvest peak, audit window |
| Change management concerns | |
| Language requirements | English / Hausa / Yoruba / Igbo / other |
| Literacy / tech comfort level of staff | High / Medium / Low |

### Budget and Commercial

| Item | Answer |
|---|---|
| Implementation budget (approx.) | |
| Annual support budget | |
| Preferred payment terms | |
| Decision-making timeline | |
| Has client evaluated other ERP options? | |
| Why Odoo / why this framework? | |

---

## Section 8 — Discovery Sign-off

To be signed after all sections are complete and reviewed with the client.

| Party | Name | Role | Signature | Date |
|---|---|---|---|---|
| Client | | | | |
| Client | | | | |
| Implementer | | | | |

### Open Items at Sign-off

List any unresolved questions that must be answered before configuration begins.

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

_This document is confidential between the implementation partner and the client. Do not share with third parties without written consent from both parties._
