# FamOil — Validation Checklist

_Use before go-live and after any significant configuration change._

---

## 1. Environment Checklist

- [ ] Single company configured (no demo "My Company" or "San Francisco" company)
- [ ] Company name = client's legal name
- [ ] Country = Nigeria
- [ ] Currency = NGN (Nigerian Naira)
- [ ] Fiscal year start = correct month
- [ ] No demo data in database (`--without-demo=all` was used)

**Verify via SQL:**
```sql
SELECT name, currency_id FROM res_company;
SELECT count(*) FROM ir_module_module WHERE state='installed' AND demo='t';
```

---

## 2. Warehouse Validation

- [ ] Only project warehouses exist (no YourCompany, no Chicago 1)
- [ ] FamOilWH (CW) is the active production warehouse
- [ ] Inbound routing = 3 steps (Input + QC + Stock)
- [ ] Outbound routing = 3 steps (Pick + Pack + Ship)
- [ ] All 14 custom locations exist under CW/Stock
- [ ] No stock quants exist in WH/* or CHIC1/* locations

**Verify via SQL:**
```sql
-- Check warehouses
SELECT name, code FROM stock_warehouse;

-- Check for rogue stock
SELECT sl.complete_name, sum(sq.quantity) as qty
FROM stock_quant sq
JOIN stock_location sl ON sq.location_id=sl.id
WHERE sl.usage='internal'
  AND sl.complete_name NOT LIKE 'CW%'
  AND sl.complete_name NOT LIKE 'Virtual%'
  AND sl.complete_name NOT LIKE 'Partners%'
GROUP BY sl.complete_name
HAVING sum(sq.quantity) != 0;
```
Expected result: zero rows.

- [ ] Crude Oil Tank restriction module installed and active
- [ ] Tank restriction correctly identifies tanks by name (test with wrong product)

---

## 3. Product & Category Validation

- [ ] All FamOil products are in the correct category (not in root "All")
- [ ] SoyaBean → All / Raw Materials
- [ ] Crude Soya Oil, Soya Cake, SoapStock → All / Finished Goods
- [ ] Production Waste → All / Work In Progress
- [ ] Packaging materials → All / Packaging Materials
- [ ] Consumables → All / Consumables
- [ ] Spare Parts → All / Spare Parts
- [ ] No product has list_price = 1.00 (placeholder)
- [ ] SoyaBean standard_price = standard_price (not placeholder)
- [ ] All finished goods have realistic list_price (not ₦220 placeholder)

**Verify via SQL:**
```sql
SELECT pt.name->>'en_US', pc.complete_name, pt.list_price
FROM product_template pt
JOIN product_category pc ON pt.categ_id=pc.id
WHERE pt.active=true
  AND (pt.list_price = 1 OR pt.list_price = 0)
  AND pc.complete_name LIKE 'All / %'
  AND pc.id NOT IN (SELECT id FROM product_category WHERE name='All');
```

---

## 4. Manufacturing Validation

### BOM 10 — Crude Soya Oil (Extraction)
- [ ] BOM 10 is active; input: 1,000 kg SoyaBean; output: 140 kg Crude Soya Oil
- [ ] Byproducts: Soya Cake (840 kg, 40%), Production Waste (10 kg, 0%) — SoapStock must NOT be present
- [ ] All 5 operations linked to correct FamOil work centers (Cleaning/Extrusion/Pressing/Filtration/Packaging)
- [ ] No operation named "Clearning" (typo fixed to "Cleaning")
- [ ] Work center rates are non-zero and finance-approved
- [ ] Consumables (Hexane, Lubricant) added to BOM with correct quantities (OPEN — not yet done)

### BOM 15 — Refined Soya Oil (Refining)
- [ ] BOM 15 is active; input: 140 kg Crude Soya Oil; output: 135 kg Refined Soya Oil
- [ ] Byproduct: SoapStock (5 kg) — no cost share field
- [ ] 4 operations linked: Neutralization → Bleaching → Deodorization → Final Filtration
- [ ] Chemicals (Caustic Soda, Bleaching Earth, Citric Acid) are type=consu in BOM components

### Operation Types
- [ ] Extraction Manufacturing (id=79): source=Famoil/Stock/RM Warehouse, dest=Famoil/Stock
- [ ] Refining Manufacturing (id=127): source=Famoil/Stock, dest=Famoil/Stock
- [ ] Packaging Manufacturing (id=128): source=Famoil/Stock, dest=Famoil/Stock/FG Warehouse

### Putaway Rules (all trigger at Famoil/Stock)
- [ ] Crude Soya Oil → Crude Oil Tank 1
- [ ] Refined Soya Oil → Refined Oil Tank 1
- [ ] SoapStock → Soapstock Tank
- [ ] Soya Cake → FG Warehouse
- [ ] Refined Soya Oil 5L → FG Warehouse
- [ ] Refined Soya Oil 25L → FG Warehouse

**Verify via SQL:**
```sql
-- BOM 10 byproducts (SoapStock must NOT appear)
SELECT pt.name->>'en_US' AS product, mbp.product_qty, mbp.cost_share
FROM mrp_bom_byproduct mbp
JOIN product_product pp ON mbp.product_id=pp.id
JOIN product_template pt ON pp.product_tmpl_id=pt.id
WHERE mbp.bom_id=10;

-- Operations BOM 10
SELECT name, time_cycle_manual FROM mrp_routing_workcenter WHERE bom_id=10;

-- Work center rates
SELECT name, costs_hour FROM mrp_workcenter WHERE name LIKE 'FamOil%';

-- Putaway rules
SELECT pp.default_code, pt.name->>'en_US' AS product,
       li.complete_name AS loc_in, lo.complete_name AS loc_out
FROM stock_putaway_rule spr
JOIN product_product pp ON spr.product_id=pp.id
JOIN product_template pt ON pp.product_tmpl_id=pt.id
JOIN stock_location li ON spr.location_in_id=li.id
JOIN stock_location lo ON spr.location_out_id=lo.id
WHERE spr.company_id=2;
```

- [ ] Test MO (BOM 10): components reserve from Famoil/Stock/RM Warehouse; output routes to Crude Oil Tank 1 via putaway
- [ ] Test MO (BOM 15): Crude Soya Oil reserves from Crude Oil Tank 1; output routes to Refined Oil Tank 1; SoapStock routes to Soapstock Tank
- [ ] Confirm cost layers created correctly after MO completion

---

## 5. Costing Validation

- [ ] Raw Materials category → cost method = Average
- [ ] Finished Goods category → cost method = FIFO
- [ ] Packaging Materials category → cost method = FIFO
- [ ] Consumables category → cost method = Average
- [ ] All categories → valuation = Automated (Perpetual)
- [ ] SoyaBean standard_price > 0 and matches current market purchase price
- [ ] After a test MO: Crude Soya Oil unit cost ≈ ₦3,451/kg (at ₦710/kg SoyaBean + current work center rates)
- [ ] Byproduct cost allocation verified against manual calculation

**Manual calculation check:**
```
Batch cost = (SoyaBean qty × standard_price) + work_center_overhead
Expected crude oil cost per kg = (batch_cost × 0.60) / 140
```

---

## 6. Accounting Validation

- [ ] Chart of accounts installed (Nigerian GAAP)
- [ ] Stock input/output/valuation accounts mapped per category
- [ ] Test receipt creates correct debit/credit in stock valuation journal
- [ ] Test MO validates and posts WIP → Finished Goods journal entry
- [ ] VAT (7.5%) configured for purchases and sales
- [ ] Bank accounts configured in NGN
- [ ] Opening balances entered

---

## 7. Nigerian Configuration Checks

- [ ] Currency = NGN, symbol = ₦
- [ ] VAT = 7.5% (Federal Inland Revenue Service rate)
- [ ] Fiscal year aligned with Nigerian Companies and Allied Matters Act
- [ ] Company address includes Nigerian state and LGA
- [ ] All product prices entered in NGN (no USD placeholder prices)
- [ ] Supplier contacts configured with Nigerian addresses
- [ ] Report header shows company name, RC number, and address

---

## 8. Custom Module Validation

### stock_crude_oil_tank_restriction
- [ ] Module version = 17.0.1.1.0
- [ ] No hardcoded IDs in `stock_picking.py`
- [ ] Test: attempt to transfer a non-crude-oil product to Crude Oil Tank 1 → should raise UserError
- [ ] Test: transfer Crude Soya Oil to Crude Oil Tank 1 → should succeed

### mrp_component_availability_check
- [ ] Module is installed and active
- [ ] Test: attempt to validate MO with insufficient components → should raise UserError listing shortfalls
- [ ] Test: validate MO with fully reserved components → should succeed

---

## 9. Pre-Go-Live Final Gate

All of the above must be checked before going live. Additionally:

- [ ] Full database backup taken and verified (restore tested)
- [ ] Opening stock entered and matches physical count
- [ ] All users created with correct access rights
- [ ] Training completed for all user roles
- [ ] Backup script (`backup_famoil.sh`) scheduled or documented for daily use
