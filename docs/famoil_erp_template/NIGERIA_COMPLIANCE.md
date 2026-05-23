# Nigerian Compliance Layer
# FamOil ERP Framework

_Version: 1.0 | Date: 2026-05-22_

---

## IMPORTANT DISCLAIMER

> This document records implementation **considerations and recommended Odoo configurations** based on the implementer's working knowledge of Nigerian regulatory requirements as of 2026.
>
> **This document is NOT legal or tax advice.**
> Rates, thresholds, and obligations change with Finance Acts and regulatory circulars. Before configuring any client's compliance setup, the following must be obtained from qualified professionals:
> - Tax position: from a CITN/ICAN-registered tax adviser or FIRS-accredited tax consultant
> - Pension: from PENCOM-licensed PFA/PFC
> - NAFDAC/SON: from the regulatory affairs officer or a registered consultant
>
> **Do not present this document to clients as authoritative compliance guidance.**

---

## 1. Value Added Tax (VAT)

### Regulatory Background
- Rate: **7.5%** (Finance Act 2020, effective February 2020; was 5% before)
- Administered by: Federal Inland Revenue Service (FIRS)
- Registration threshold: **₦25 million annual taxable turnover** — below this, registration is voluntary
- Relevant legislation: VATA Cap. V1 LFN 2004, Finance Acts 2019, 2020, 2021

### Exemptions Relevant to Agro-processing
The following are VAT-exempt under Schedule 1 of VATA (verify with tax adviser — exemption scope is contested):
- Locally-produced basic food items (e.g., unprocessed grains, raw agricultural produce)
- Agricultural equipment (tractors, planters) — exemption applies to the equipment, not necessarily services

**[Flag for professional validation]:** Whether processed vegetable oil (crude soya oil, groundnut oil) qualifies as a "basic food item" for VAT exemption is not settled and may depend on FIRS practice at the time of filing. Some processors charge VAT on oil sales; others do not.

### Odoo Configuration

**Tax Groups:**
```
VAT 7.5% (Sales)   — applied to taxable product sales
VAT 7.5% (Purchase) — applied to VATable supplier invoices (input VAT)
VAT Exempt (Sales)  — for exempt product lines (raw agricultural produce)
VAT Exempt (Purchase) — for purchases of exempt inputs
```

**Configuration steps in Odoo:**
1. Accounting → Configuration → Taxes
2. Create "VAT 7.5% (Sales)": Tax Type = Sales, Computation = Percentage of Price, Amount = 7.5
3. Create "VAT 7.5% (Purchase)": Tax Type = Purchase, same amount
4. Assign default taxes on product categories (Finished Goods → VAT 7.5% Sales; Raw Materials → as advised)
5. Set up fiscal positions if some customers are VAT-exempt (export customers, diplomats)

**VAT Returns:**
- Monthly VAT returns are filed with FIRS via TaxPro Max portal
- Odoo's "Tax Report" (Accounting → Reporting → Tax Report) produces a summary of output and input VAT
- **[Flag]:** Odoo's standard VAT report may require customisation to match FIRS return format — validate this before first filing

---

## 2. Withholding Tax (WHT)

### Regulatory Background
- Administered by: FIRS (federal) and State Boards of Internal Revenue (SBIR) for state-resident companies
- WHT is deducted at source by the paying party and remitted to FIRS
- Relevant legislation: CITA Cap. C21, PITA Cap. P8, Finance Acts

### Common WHT Rates for Agro-processors

| Payment Category | WHT Rate | Remit To |
|---|---|---|
| Supply of goods (between companies) | 2.5% | FIRS |
| Services (consultancy, management, etc.) | 5% | FIRS |
| Rent (commercial property) | 10% | FIRS |
| Construction and related works | 2.5% | FIRS |
| Technical/professional fees | 5% | FIRS |
| Dividends | 10% | FIRS |
| Interest on loans | 10% | FIRS |

**[Flag for professional validation]:** Finance Act 2023 proposed changes to WHT rates and categories. Confirm current applicable rates with a tax adviser before configuration.

### Odoo Configuration

**Approach:** Configure WHT as a negative tax on vendor bills.

1. Accounting → Configuration → Taxes → New
2. Name: "WHT 2.5% — Goods Supply"
3. Tax Type: Purchase
4. Tax Scope: leave blank (apply at line level)
5. Computation: Percentage of Price
6. Amount: **-2.5** (negative to reduce vendor payment)
7. Tax Account: link to a "WHT Payable" liability account (e.g., 2150 - WHT Payable)

Create one tax per category:
- WHT 2.5% — Goods
- WHT 5% — Services
- WHT 10% — Rent

Apply manually at the vendor bill line where applicable.

**WHT Remittance:** Odoo does not auto-generate FIRS WHT schedule forms. Export the WHT Payable account transactions and prepare the WHT credit note / remittance schedule manually or via a custom report.

---

## 3. NAFDAC (National Agency for Food and Drug Administration and Control)

### Applicability
NAFDAC regulates:
- Processed food and beverages
- Edible oils (crude and refined)
- Animal feed
- Packaging materials in contact with food

Any agro-processor selling a food product must have **NAFDAC product registration** for each SKU.

### Key Requirements
| Requirement | Description |
|---|---|
| Facility registration | The production facility must be registered with NAFDAC |
| Product registration | Each finished product (each SKU) needs a NAFDAC registration number |
| Labelling compliance | Product labels must carry NAFDAC number, batch number, expiry date, and country of origin |
| Renewal | Product registration is typically valid for 5 years; renewal required |
| Import/export | Additional NAFDAC certificates required for imported inputs or exported products |

### Odoo Configuration Recommendations
- Store NAFDAC registration number per product as an **Internal Reference** or a **custom product field**
- Use **Lot tracking** on finished goods so NAFDAC-required batch/lot traceability is maintained
- Expiry date tracking (`use_expiration_date = True`) on finished goods lots
- If exporting: the delivery order and picking can carry NAFDAC certificate reference in the note field

**[Flag for regulatory validation]:** NAFDAC registration is a legal prerequisite before selling. ERP configuration does not substitute for obtaining the registration — it only helps maintain the required records.

---

## 4. SON (Standards Organisation of Nigeria)

### Applicability
SON sets and enforces quality standards for manufactured goods. Relevant to agro-processors for:
- Edible oils (NIS 301 for groundnut oil, NIS 87 for palm oil, NIS for soya oil)
- Animal feeds (NIS standards for feed quality)
- Weighing and measuring equipment used in production

### Key Requirements
| Requirement | Description |
|---|---|
| Product certification | Some products require SON certification (MANCAP) before sale |
| Standards compliance | Products must meet relevant Nigerian Industrial Standards (NIS) |
| Weighing instruments | Calibrated and SON-verified scales required in production |
| Imported standards | Import Duty Exemption and SONCAP certificate for imported equipment |

### Odoo Configuration Recommendations
- Store SON/MANCAP certificate number as a product attribute or document attachment
- Use the Odoo Documents module (or file attachments) to store certificates per product
- Lot records can carry quality check notes (pass/fail against NIS specification)

---

## 5. PENCOM (National Pension Commission)

### Regulatory Background
- Pension Reform Act 2014 (as amended)
- Mandatory for organisations with **3 or more employees**
- Contribution rates: **Employer 10% + Employee 8% = 18% of monthly emoluments**
- Emoluments = basic salary + housing allowance + transport allowance (as defined in the PRA)
- Contributions must be remitted to employee's Retirement Savings Account (RSA) with a licensed PFA

### Odoo Configuration Recommendations

> **[Flag]:** Odoo Community does not include a Nigerian payroll module. Standard HR Payroll (Enterprise) requires localisation for Nigerian pension calculation. Options:

1. **If using Odoo Payroll:** Create a salary rule "Pension — Employee (8%)" and "Pension — Employer (10%)" linked to the appropriate accounts
2. **If payroll is external:** Track pension payable via a manual journal entry each month to "Pension Payable" liability account
3. **Accounts needed:**
   - 5500 - Pension Expense (employer contribution — P&L)
   - 2160 - Pension Payable (liability — remittance pending)

---

## 6. ITF (Industrial Training Fund)

### Regulatory Background
- ITF Act Cap. I9 LFN 2004
- Applies to: organisations with **5 or more employees** OR annual turnover of **₦50 million or more**
- Rate: **1% of annual payroll cost** (including employer's pension, PAYE, etc.)
- Remitted annually to ITF by 1 April of the following year
- ITF registration and annual levy payment required; ITAS (ITF Training Account Statement) issued on payment

### Odoo Configuration Recommendations
- Record ITF levy as an annual accrual:
  - DR: 5510 - ITF Levy Expense
  - CR: 2170 - ITF Levy Payable
- Post as a recurring journal entry (monthly accrual = 1% × monthly payroll ÷ 12)
- Reverse and repost when actual annual payroll is confirmed

---

## 7. NSITF (Nigeria Social Insurance Trust Fund)

### Regulatory Background
- NSITF Act 2010
- Applies to: all employers in the formal sector
- Rate: **1% of total monthly payroll** paid by the employer
- Provides work-related injury insurance for employees
- Remitted monthly to NSITF

### Odoo Configuration Recommendations
- Similar to ITF — monthly accrual:
  - DR: 5520 - NSITF Contribution Expense
  - CR: 2180 - NSITF Payable
- Remittance generates an NSITF compliance certificate (needed for some government contracts)

---

## 8. PAYE (Pay As You Earn)

### Regulatory Background
- Personal Income Tax Act (PITA) Cap. P8
- Deducted from employees' salaries by the employer and remitted to the relevant State Internal Revenue Service (SIRS) — the state where the employee resides
- Graduated rates: 7% to 24% depending on income band (as of last Finance Act — verify current bands)
- Annual returns (Form H1) due by 31 January of the following year

### Odoo Configuration Recommendations
- Configure PAYE as a deduction salary rule if using Odoo Payroll
- PAYE is remitted to state (not FIRS) — ensure correct payee is used
- Accounts needed:
  - 2140 - PAYE Payable (liability)

---

## 9. Manufacturing Chart of Accounts (Recommended Structure)

This is a recommended starting structure for a Nigerian agro-processor. All account codes are examples — adapt to client's existing numbering convention.

**[Flag for professional validation]:** A chartered accountant should review and approve the CoA before go-live.

### Assets (1xxx)

| Code | Account | Notes |
|---|---|---|
| 1000 | Cash and Cash Equivalents | |
| 1010 | Petty Cash | |
| 1020 | Bank — Main Account | One per bank account |
| 1100 | Accounts Receivable | |
| 1110 | Allowance for Doubtful Debts | Credit balance |
| 1200 | Inventory — Raw Materials | |
| 1210 | Inventory — Work In Progress | |
| 1220 | Inventory — Finished Goods | |
| 1230 | Inventory — Byproducts | |
| 1240 | Inventory — Packaging Materials | |
| 1300 | Prepayments | |
| 1400 | VAT Receivable (Input VAT) | |
| 1500 | Property, Plant & Equipment | |
| 1510 | Accumulated Depreciation | Credit balance |
| 1600 | Right-of-Use Assets | If leasing |

### Liabilities (2xxx)

| Code | Account | Notes |
|---|---|---|
| 2100 | Accounts Payable | |
| 2110 | Accrued Expenses | |
| 2140 | PAYE Payable | |
| 2150 | WHT Payable | |
| 2160 | Pension Payable | |
| 2170 | ITF Levy Payable | |
| 2180 | NSITF Payable | |
| 2200 | VAT Payable (Output VAT) | |
| 2210 | VAT Net Payable | Output minus Input |
| 2300 | Loans Payable | |
| 2400 | Deferred Revenue | |

### Equity (3xxx)

| Code | Account | Notes |
|---|---|---|
| 3000 | Share Capital | |
| 3100 | Retained Earnings | |
| 3200 | Current Year Profit | Auto-calculated |

### Revenue (4xxx)

| Code | Account | Notes |
|---|---|---|
| 4000 | Sales — Crude Soya Oil | One per product line |
| 4010 | Sales — Soya Cake | |
| 4020 | Sales — Other Byproducts | |
| 4100 | Other Operating Income | |

### Cost of Goods Sold (5xxx)

| Code | Account | Notes |
|---|---|---|
| 5000 | COGS — Raw Materials Consumed | |
| 5010 | COGS — Direct Labour | |
| 5020 | COGS — Work Center Overhead | |
| 5030 | COGS — Consumables (Hexane, Lubricant) | |
| 5040 | COGS — Packaging | |
| 5100 | Manufacturing Variance | |

### Operating Expenses (6xxx)

| Code | Account | Notes |
|---|---|---|
| 6000 | Salaries and Wages | |
| 6010 | Pension — Employer Contribution | |
| 6020 | NSITF Contribution | |
| 6030 | ITF Levy | |
| 6100 | Rent | |
| 6110 | Utilities — Electricity | |
| 6120 | Utilities — Generator / Diesel | |
| 6130 | Utilities — Water | |
| 6200 | Repairs and Maintenance | |
| 6300 | Depreciation | |
| 6400 | Transportation and Logistics | |
| 6500 | Marketing and Sales | |
| 6600 | Professional Fees | |
| 6700 | Bank Charges | |
| 6800 | Miscellaneous | |

---

## 10. Professional Validation Checklist

Before any client's compliance configuration is finalised, obtain written confirmation from qualified professionals on:

| Item | Professional Required | Status |
|---|---|---|
| VAT registration obligation and applicable rate | CITN/ICAN tax adviser | Pending |
| WHT applicability by payment category | Tax adviser | Pending |
| Whether crude oil / processed food qualifies for VAT exemption | Tax adviser | Pending |
| NAFDAC product registration status per SKU | NAFDAC consultant or regulatory affairs officer | Pending |
| SON certification requirements per product | SON consultant | Pending |
| PENCOM — correct emolument definition for contribution base | Licensed PFA | Pending |
| ITF — applicability threshold and levy base | ITF registered consultant | Pending |
| NSITF — remittance process and rate confirmation | NSITF registered consultant | Pending |
| Chart of accounts — COGS structure | ICAN-registered accountant | Pending |
| FIRS WHT current rates (post-Finance Act 2023) | Tax adviser | Pending |
