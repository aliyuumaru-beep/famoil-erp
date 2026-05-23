# Data Migration Scaffold
# FamOil ERP Framework

_Version: 1.0 | Date: 2026-05-22_

---

## Overview

This scaffold defines the data migration sequence, CSV templates, and validation steps for onboarding a new client onto the FamOil framework. Migration must happen in the exact sequence defined in Section 2 — many Odoo records have foreign key dependencies.

**Golden rule:** Never import data you have not validated in a test instance first.

---

## 1. Pre-Migration Checklist

Before any import begins:

- [ ] Odoo instance is installed and accessible
- [ ] Base company configuration is complete (name, currency, TIN, address)
- [ ] Chart of accounts is configured (do this manually, not via import)
- [ ] All Odoo modules are installed and tested
- [ ] A full backup of the empty/base instance exists before any data is loaded
- [ ] All CSV files have been validated for encoding (UTF-8, no BOM)
- [ ] All CSV files have been validated for required fields (no blanks in mandatory columns)
- [ ] Client has signed off on the data in the CSVs

---

## 2. Migration Sequence

Import in this exact order. Dependencies flow downward.

```
1.  Units of Measure (UoM)           ← usually already in Odoo; verify only
2.  Product Categories               ← must exist before products
3.  Products (templates)             ← must exist before variants, BOMs, partners
4.  Product Variants                 ← if applicable
5.  Vendor Pricelist (product.supplierinfo)
6.  Customers                        ← res.partner (type=customer)
7.  Vendors                          ← res.partner (type=supplier)
8.  Stock Locations                  ← must exist before opening inventory
9.  Opening Inventory                ← stock.quant via inventory adjustment
10. Chart of Accounts                ← manual (not CSV); do before opening balances
11. Opening Balances (Journal Entry) ← account.move
12. Open Purchase Orders             ← if migrating in-flight POs
13. Open Sales Orders                ← if migrating in-flight SOs
14. BOMs                             ← mrp.bom (products must exist first)
15. Work Centers                     ← mrp.workcenter
16. BOM Operations                   ← mrp.routing.workcenter
```

---

## 3. CSV Templates

### 3.1 Product Categories

**File:** `01_product_categories.csv`

```csv
name,parent_category,property_cost_method,property_valuation
FamOil,All,,
Raw Materials,FamOil / All,average,real_time
Finished Goods,FamOil / All,fifo,real_time
Byproducts,FamOil / All,fifo,real_time
Packaging Materials,FamOil / All,average,real_time
Consumables,FamOil / All,average,manual_periodic
```

> **Note:** `property_cost_method` and `property_valuation` may not be directly importable via CSV in Odoo 17 — verify via UI after import. The CSV serves as the specification.

---

### 3.2 Products

**File:** `02_products.csv`

| Column | Required | Description | Example |
|---|---|---|---|
| `name` | Yes | Product name | SoyaBean |
| `type` | Yes | `consu` / `product` / `service` | `product` |
| `uom_id` | Yes | Unit of measure (must exist) | `kg` |
| `uom_po_id` | Yes | Purchase UoM | `kg` |
| `categ_id` | Yes | Category path | `All / FamOil / Raw Materials` |
| `standard_price` | Yes | Standard / average cost | `710` |
| `list_price` | Yes | Sales price | `720` |
| `tracking` | No | `none` / `lot` / `serial` | `lot` |
| `description` | No | Internal notes | |

**Sample rows:**
```csv
name,type,uom_id,uom_po_id,categ_id,standard_price,list_price,tracking
SoyaBean,product,kg,kg,All / FamOil / Raw Materials,710,720,lot
Crude Soya Oil,product,kg,kg,All / FamOil / Finished Goods,0,3500,lot
Soya Cake,product,kg,kg,All / FamOil / Byproducts,0,750,lot
Production Waste,product,consu,kg,kg,All / FamOil / Byproducts,0,0,none
Hexane Chemical,product,litre,litre,All / FamOil / Consumables,0,0,none
Lubricant Oil,product,litre,litre,All / FamOil / Consumables,0,0,none
```

---

### 3.3 Vendors

**File:** `03_vendors.csv`

| Column | Required | Description | Example |
|---|---|---|---|
| `name` | Yes | Vendor legal name | Kano Agro Supplies Ltd |
| `ref` | No | Internal vendor code | VND-001 |
| `vat` | No | TIN / FIRS tax ID | 12345678-0001 |
| `street` | No | Address line 1 | 14 Kano Road |
| `city` | No | City | Kano |
| `state_id` | No | State (must match Odoo state list) | Kano |
| `country_id` | No | Country | Nigeria |
| `phone` | No | Phone | +234 803 000 0000 |
| `email` | No | Email | |
| `property_payment_term_id` | No | Payment terms | 30 days |
| `is_company` | Yes | True / False | True |
| `supplier_rank` | Yes | Set to 1 to mark as vendor | 1 |
| `customer_rank` | No | Set to 1 if also a customer | 0 |
| `l10n_ng_tax_id` | No | WHT category (if applicable) | |

**Sample rows:**
```csv
name,ref,vat,street,city,state_id,country_id,phone,is_company,supplier_rank,customer_rank
Kano Agro Supplies Ltd,VND-001,12345678-0001,14 Kano Road,Kano,Kano,Nigeria,+2348030000001,True,1,0
Northern Inputs Co.,VND-002,,Plot 5 Industrial Estate,Kaduna,Kaduna,Nigeria,,True,1,0
```

---

### 3.4 Customers

**File:** `04_customers.csv`

| Column | Required | Description | Example |
|---|---|---|---|
| `name` | Yes | Customer legal name | Lagos Oil Distributors Ltd |
| `ref` | No | Internal customer code | CUS-001 |
| `vat` | No | TIN | |
| `street` | No | Address | |
| `city` | No | City | Lagos |
| `state_id` | No | State | Lagos |
| `country_id` | No | Country | Nigeria |
| `phone` | No | Phone | |
| `email` | No | Email | |
| `property_payment_term_id` | No | Payment terms | Immediate |
| `credit_limit` | No | Credit limit (₦) | 5000000 |
| `is_company` | Yes | True / False | True |
| `supplier_rank` | No | 0 unless also a supplier | 0 |
| `customer_rank` | Yes | Set to 1 | 1 |

**Sample rows:**
```csv
name,ref,street,city,state_id,country_id,phone,is_company,supplier_rank,customer_rank
Lagos Oil Distributors Ltd,CUS-001,15 Marina St,Lagos,Lagos,Nigeria,+2348031111111,True,0,1
Abuja Feeds Wholesale,CUS-002,,Abuja,FCT,Nigeria,,True,0,1
```

---

### 3.5 Opening Inventory

**File:** `05_opening_inventory.csv`

> Opening inventory is entered as an inventory adjustment in Odoo (Inventory → Operations → Physical Inventory). This CSV is the input to that process.

| Column | Required | Description | Example |
|---|---|---|---|
| `product_id` | Yes | Product name (must exist) | SoyaBean |
| `location_id` | Yes | Full location path | WH/Stock/RM Warehouse |
| `inventory_quantity` | Yes | Quantity on hand | 1000 |
| `lot_id` | If tracked | Lot / batch reference | LOT-2026-001 |
| `unit_cost` | No | Cost per unit at migration date (₦) | 710 |
| `expiration_date` | If applicable | ISO format YYYY-MM-DD | 2026-12-31 |

**Sample rows:**
```csv
product_id,location_id,inventory_quantity,lot_id,unit_cost
SoyaBean,WH/Stock/RM Warehouse,1000,LOT-2026-001,710
Crude Soya Oil,WH/Stock/FG Warehouse,319,,3451
Soya Cake,WH/Stock/FG Warehouse,2520,,383
```

> **Important:** Enter opening inventory at actual cost, not list price. For FIFO products, each lot will carry its own cost layer — ensure lots reflect actual purchase batches if historical accuracy matters.

---

### 3.6 Opening Balances (Journal Entry)

**File:** `06_opening_balances.csv`

Opening balances are entered as a single journal entry dated the day before go-live (e.g., if go-live is 2026-06-01, date the entry 2026-05-31).

| Column | Required | Description | Example |
|---|---|---|---|
| `date` | Yes | Entry date (YYYY-MM-DD) | 2026-05-31 |
| `journal_id` | Yes | Journal name | Miscellaneous |
| `ref` | Yes | Reference | Opening Balances — Migration |
| `account_id` | Yes | Account code or name | 1100 - Accounts Receivable |
| `name` | Yes | Line description | Opening AR balance |
| `debit` | Yes | Debit amount (₦) | 500000 |
| `credit` | Yes | Credit amount (₦) | 0 |
| `partner_id` | If applicable | Partner name | Lagos Oil Distributors Ltd |

**Sample rows:**
```csv
date,journal_id,ref,account_id,name,debit,credit,partner_id
2026-05-31,Miscellaneous,Opening Balances,1100 - Accounts Receivable,Opening AR,500000,0,Lagos Oil Distributors Ltd
2026-05-31,Miscellaneous,Opening Balances,2100 - Accounts Payable,Opening AP,0,300000,Kano Agro Supplies Ltd
2026-05-31,Miscellaneous,Opening Balances,3000 - Retained Earnings,Opening Equity,0,200000,
```

> **Rule:** The opening balance entry must net to zero (total debits = total credits). Have the client's accountant validate this entry before posting. Do not post until the trial balance matches the client's last closing balance from their old system.

---

## 4. Validation Steps

Run these checks after each import before proceeding to the next stage.

### After Product Import
```sql
-- Check for products with missing category
SELECT name, categ_id FROM product_template WHERE categ_id IS NULL;

-- Check for products with list_price = 0 or 1 (likely placeholders)
SELECT name, list_price, standard_price FROM product_template
WHERE type = 'product' AND (list_price <= 1 OR standard_price = 0)
ORDER BY name;
```

### After Vendor/Customer Import
```sql
-- Vendors with no TIN (flag for WHT compliance)
SELECT name, ref FROM res_partner
WHERE supplier_rank > 0 AND (vat IS NULL OR vat = '') AND is_company = True;

-- Customers with no payment terms
SELECT name FROM res_partner
WHERE customer_rank > 0 AND property_payment_term_id IS NULL;
```

### After Opening Inventory
```sql
-- Confirm quantities match expected
SELECT sl.complete_name AS location, pt.name->>'en_US' AS product,
       sq.quantity, sq.reserved_quantity
FROM stock_quant sq
JOIN stock_location sl ON sq.location_id = sl.id
JOIN product_product pp ON sq.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
WHERE sl.usage = 'internal'
ORDER BY sl.complete_name, pt.name->>'en_US';

-- Total inventory value
SELECT SUM(sq.quantity * sq.value / NULLIF(sq.quantity, 0)) AS total_value
FROM stock_quant sq
JOIN stock_location sl ON sq.location_id = sl.id
WHERE sl.usage = 'internal';
```

### After Opening Balances
```sql
-- Confirm opening entry is balanced
SELECT ref, SUM(debit) AS total_debit, SUM(credit) AS total_credit,
       SUM(debit) - SUM(credit) AS difference
FROM account_move_line aml
JOIN account_move am ON am.id = aml.move_id
WHERE am.ref ILIKE '%Opening Balances%'
GROUP BY ref;
-- difference must be 0
```

---

## 5. Rollback Procedure

If a migration stage goes wrong:

1. **Do not attempt to manually reverse imports** — Odoo's ORM has cascading logic that makes manual reversal dangerous.
2. **Restore from the pre-import backup** taken in the pre-migration checklist.
3. Fix the source CSV (correct the error that caused the problem).
4. Re-run the import from that stage.

This is why backups before each major import stage are non-negotiable.

**Backup command before each stage:**
```bash
pg_dump -U odoo -F c -f ~/odoo_backups/migration_stage_{N}_{YYYYMMDD}.dump Famoil
```

---

## 6. Go-Live Cutover Checklist

- [ ] All CSVs imported and validated
- [ ] Opening balances posted and trial balance confirmed
- [ ] Opening inventory confirmed by physical count
- [ ] At least one full purchase → GRN → invoice cycle tested
- [ ] At least one full sales order → delivery → invoice cycle tested
- [ ] At least one manufacturing order from raw material to finished good tested
- [ ] All user accounts created and passwords distributed
- [ ] Backup scripts deployed and tested
- [ ] Client sign-off on data accuracy obtained in writing
