# FamOil — Known Issues Library

_Each entry: issue → root cause → discovery → fix → prevention → Odoo version._

---

## ISSUE-001 — CHIC1/Stock Phantom Reservation Blocking Production

**Severity:** HIGH
**Odoo Version:** 17 Community (all versions with multi-warehouse)

### Issue
The Chicago 1 (CHIC1) demo warehouse has 200 units of Large Cabinet in CHIC1/Stock with 180 units reserved and 13 pending stock moves. Odoo's global reservation engine can pull available stock from CHIC1/Stock for any product that routes through any internal location — creating phantom reservations that cannot be fulfilled and silently consuming available-to-promise quantities.

### Root Cause
Odoo's default installation creates demo warehouses (YourCompany, Chicago 1) with demo stock. When a real warehouse (FamOilWH) is added, the reservation algorithm still considers all active internal locations globally unless restricted by routes. CHIC1/Stock remained active with demo stock and live reservations.

### Discovery Method
Queried `stock_quant` for all internal locations with non-zero quantity:
```sql
SELECT sl.complete_name, sq.quantity, sq.reserved_quantity, pt.name->>'en_US'
FROM stock_quant sq
JOIN stock_location sl ON sq.location_id=sl.id
JOIN product_product pp ON sq.product_id=pp.id
JOIN product_template pt ON pp.product_tmpl_id=pt.id
WHERE sl.usage='internal' AND sq.quantity != 0;
```
Found: CHIC1/Stock — 200 Large Cabinet, 180 reserved.

Also found 13 pending stock moves against CHIC1 locations:
```sql
SELECT count(*) FROM stock_move WHERE state NOT IN ('done','cancel')
AND (location_id IN (SELECT id FROM stock_location WHERE complete_name LIKE 'CHIC1%')
OR location_dest_id IN (SELECT id FROM stock_location WHERE complete_name LIKE 'CHIC1%'));
```

### Fix

**Step 1:** Cancel or process the 13 pending moves via UI (Inventory → Operations → Transfers, filter by CHIC1).

**Step 2:** Scrape or zero out the CHIC1 inventory via an inventory adjustment (set quantity to 0 for all CHIC1 products).

**Step 3:** Archive the Chicago 1 warehouse:
- Inventory → Configuration → Warehouses → Chicago 1 → Archive

**Step 4:** Verify CHIC1 locations are now inactive:
```sql
SELECT complete_name, active FROM stock_location
WHERE complete_name LIKE 'CHIC1%' ORDER BY complete_name;
```
All should show `active = false`.

### Prevention Rule
> Before going live on any Odoo instance that was configured from a demo/sample database, run the stock_quant query above and verify zero stock in all non-project warehouses. Archive all demo warehouses **before** any production data entry begins.

---

## ISSUE-002 — Demo Stock in WH/Stock Polluting Inventory Reports

**Severity:** MEDIUM
**Odoo Version:** 17 Community

### Issue
WH/Stock (YourCompany warehouse) contains large quantities of demo furniture products (Desk Combination, Customizable Desk, Cabinet with Doors, etc.) with active reservations. These appear in inventory valuation reports and available-stock calculations, making them misleading.

### Root Cause
Default Odoo demo data was not cleaned before real data entry began.

### Discovery Method
Same stock_quant query as ISSUE-001 — found 30+ rows of WH/Stock entries for furniture products, several with non-zero reserved_quantity.

### Fix
1. Cancel all pending moves on WH locations.
2. Run inventory adjustment to set all WH/Stock quantities to 0.
3. Archive the YourCompany (WH) warehouse.

### Prevention Rule
> Always start a production instance from a clean database (no demo data). Use `--without-demo=all` flag when initialising Odoo for a client: `odoo-bin -d NewDB --without-demo=all -i base`

---

## ISSUE-003 — Hardcoded Location/Product IDs in Custom Module

**Severity:** HIGH (resolved)
**Odoo Version:** 17 Community
**Status:** FIXED in v17.0.1.1.0 (2026-05-22)

### Issue
`stock_crude_oil_tank_restriction` module used hardcoded database IDs:
```python
CRUDE_OIL_TANK_IDS = {141, 142}
CRUDE_SOYA_OIL_ID = 111
```
If the Crude Oil Tank locations or the Crude Soya Oil product were deleted and recreated (e.g., during a data migration or restore), the restriction would silently stop working with no error.

### Root Cause
Developer convenience — IDs were copied from a query result and pasted directly into code.

### Discovery Method
Code review of `custom_addons/stock_crude_oil_tank_restriction/models/stock_picking.py`.

### Fix
Replaced hardcoded constants with runtime name-based lookups:
```python
def _get_crude_oil_tank_ids(self):
    tanks = self.env['stock.location'].search([
        ('name', 'ilike', 'Crude Oil Tank'),
        ('usage', '=', 'internal'),
        ('active', '=', True),
    ])
    return set(tanks.ids)

def _get_crude_soya_oil_product_id(self):
    product = self.env['product.product'].search([
        ('name', '=', 'Crude Soya Oil'),
        ('active', '=', True),
    ], limit=1)
    return product.id if product else None
```

### Prevention Rule
> Never use database IDs as constants in Odoo module code. Always look up by name, `ref()`, or `xml_id`. If IDs are truly required, store them in `ir.config_parameter` and provide a settings UI.

---

## ISSUE-004 — Operation Name Typo: "Clearning"

**Severity:** LOW (resolved)
**Status:** FIXED 2026-05-22

### Issue
BOM operation ID 6 was named "Clearning" instead of "Cleaning". Appears in manufacturing order work orders and printed documents.

### Root Cause
Manual data entry error during initial setup.

### Discovery Method
Query on `mrp_routing_workcenter` table.

### Fix
```sql
UPDATE mrp_routing_workcenter SET name = 'Cleaning'
WHERE id = 6 AND name = 'Clearning';
```

### Prevention Rule
> Always spell-check BOM operations, work center names, and product names before recording any transactions against them. After go-live, name changes require verifying historical reports are not broken.

---

## ISSUE-005 — SoyaBean Miscategorised (All vs Raw Materials)

**Severity:** MEDIUM (resolved)
**Status:** CONFIRMED CORRECT 2026-05-22

### Issue
SoyaBean appeared to be under category "All" in early inspection queries, which would have meant no specific cost method applied.

### Root Cause
The category name "FamOil / Raw Materials" (with complete_name "All / FamOil / Raw Materials") was displaying as "All" in certain queries due to the FamOil prefix rendering confusion. The product's categ_id was correctly pointing to category 17 (Raw Materials) all along.

### Discovery Method
Direct query on `categ_id` confirmed: `SoyaBean categ_id = 17` = Raw Materials.

### Fix
None required for the product. Category names were cleaned (FamOil prefix removed).

### Prevention Rule
> When inspecting category assignments, always join on `categ_id` and display both `id` and `complete_name`. Do not rely on display names alone.

---

## ISSUE-006 — Consumables Not in BOM (Hexane Chemical, Lubricant Oil)

**Severity:** MEDIUM
**Status:** OPEN

### Issue
Hexane Chemical (₦11,000 standard cost) and Lubricant Oil (₦3,000 standard cost) are defined as consumable products in the system but are not included as BOM components. Their costs are therefore invisible in manufacturing cost calculations — understating total batch cost by ~₦14,000.

### Root Cause
Products were created but not added to the BOM, likely deferred during initial setup.

### Discovery Method
Cross-referencing product list against BOM components for BOM 10. BOM has only one component: SoyaBean.

### Fix
Add to BOM 10 as components with appropriate per-batch quantities:
- Hexane Chemical: determine actual litres used per 1,000 kg soybean batch
- Lubricant Oil: determine actual litres used per maintenance cycle / batch allocation

### Prevention Rule
> Every input to the production process — including chemicals, packaging, and lubricants — should be in the BOM. If exact quantity varies, use a minimum/standard quantity and adjust during production.

---

## ISSUE-007 — Two Companies in Single Odoo Instance

**Severity:** LOW (awareness)
**Status:** OPEN

### Issue
Two companies exist in the Famoil database:
- "My Company (San Francisco)" — USD, demo data
- "FamOil FTZ" — NGN, active project

### Root Cause
Demo company was not removed when the real company was created.

### Discovery Method
```sql
SELECT name, currency_id FROM res_company;
```

### Fix
If multi-company is not needed: archive "My Company (San Francisco)" via Settings → Companies.
Ensure all products, warehouses, and BOMs belong to the correct company.

### Prevention Rule
> On a fresh Odoo instance, configure the real company name and currency first before installing any apps or entering any data. Archive the demo company before go-live.

---

## ISSUE-008 — SoapStock Incorrectly Listed as Crude Oil Production Byproduct

**Severity:** MEDIUM (resolved)
**Status:** FIXED 2026-05-22

### Issue
SoapStock (10 kg, 5% cost share) was listed as a byproduct on BOM 10 (crude oil production). This caused 5% of batch cost to be allocated to SoapStock and for it to appear as a physical output of the pressing/extraction stage — which is incorrect.

### Root Cause
SoapStock is produced during oil **refining** (the degumming/neutralisation step), not during crude oil **production** (cleaning → extrusion → pressing → filtration). Including it in the crude oil BOM overstated the outputs of that stage and misallocated costs.

### Discovery Method
Process review — crude oil pressing produces Crude Soya Oil, Soya Cake (solid residue), and inert waste. SoapStock only appears when crude oil is subsequently refined with an alkali wash.

### Fix
```sql
BEGIN;
DELETE FROM mrp_bom_byproduct WHERE id = 1;  -- removes SoapStock (10 kg, 5%)
UPDATE mrp_bom_byproduct SET cost_share = 40 WHERE id = 2;  -- Soya Cake 35% → 40%
COMMIT;
```
Cost impact: Soya Cake unit cost rises ₦335/kg → ₦383/kg. Crude Soya Oil unit cost unchanged (₦3,451/kg) — residual share remains 60%.

### Prevention Rule
> Map each byproduct to the specific process stage that physically produces it before entering it in any BOM. If a downstream stage produces additional outputs, create a separate BOM for that stage rather than bundling all outputs into the upstream BOM.

---

## ISSUE-009 — Negative Quant in Crude Oil Tank 1 (-81 kg)

**Severity:** HIGH (resolved)
**Status:** FIXED 2026-05-24

### Issue
`stock.quant` showed -81 kg for Crude Soya Oil in Crude Oil Tank 1 (id=141), causing inventory valuation errors and preventing correct stock reporting.

### Root Cause
One or more manufacturing orders were partially validated (stock moves committed) and then cancelled without reversing the outbound stock moves. Odoo created the outbound quant decrements but the inbound production quants were never fully committed, leaving a net negative position.

### Discovery Method
```sql
SELECT sq.quantity, sl.complete_name
FROM stock_quant sq JOIN stock_location sl ON sq.location_id=sl.id
JOIN product_product pp ON sq.product_id=pp.id
JOIN product_template pt ON pp.product_tmpl_id=pt.id
WHERE pt.name->>'en_US' = 'Crude Soya Oil' AND sl.usage='internal';
```

### Fix
```python
env['stock.quant']._update_available_quantity(crude_oil, tank1, 81.0)
```
Applied via `/Users/mac/odoo17/scripts/fix_locations_and_routing.py`.

### Prevention Rule
> Always cancel an MO before any stock moves are validated. If a partially-processed MO must be cancelled, run a stock reconciliation (inventory adjustment) on affected locations immediately to restore correct quantities.

---

## ISSUE-010 — Crude Soya Oil Misplaced: 20 kg in Parent Location, 179 kg in FG Warehouse

**Severity:** HIGH (resolved)
**Status:** FIXED 2026-05-24

### Issue
- 20 kg Crude Soya Oil sitting in `Famoil/Stock` (parent, id=152) — should be in Crude Oil Tank 1
- 179 kg Crude Soya Oil sitting in `Famoil/Stock/FG Warehouse` (id=140) — should be in Crude Oil Tank 1

### Root Cause
Manufacturing orders were completed before putaway rules were configured. Odoo placed finished goods at the MO destination location rather than routing them to the correct child tank.

### Discovery Method
Stock snapshot query across all internal locations.

### Fix
```python
env['stock.quant']._update_available_quantity(crude_oil, famoil_stock, -20.0)
env['stock.quant']._update_available_quantity(crude_oil, tank1, 20.0)
env['stock.quant']._update_available_quantity(crude_oil, fg_wh, -179.0)
env['stock.quant']._update_available_quantity(crude_oil, tank1, 179.0)
```
Applied via `/Users/mac/odoo17/scripts/fix_locations_and_routing.py`.

### Prevention Rule
> Configure putaway rules before processing the first manufacturing order. Always set destination on operation types to the parent location and let putaway route each product to its correct child location automatically.

---

## ISSUE-011 — Refined Soya Oil Floating in Parent Location (135 kg)

**Severity:** HIGH (resolved)
**Status:** FIXED 2026-05-24

### Issue
135 kg Refined Soya Oil sitting in `Famoil/Stock` (parent) instead of `Famoil/Stock/Refined Oil Tank 1`.

### Root Cause
Same as ISSUE-010 — MO for refined oil completed before putaway rules were in place. The Refining Manufacturing operation type destination was set to `Famoil/Stock`, so output landed at the parent location without being routed onward.

### Fix
```python
env['stock.quant']._update_available_quantity(refined_oil, famoil_stock, -135.0)
env['stock.quant']._update_available_quantity(refined_oil, refined_tank1, 135.0)
```

### Prevention Rule
> Same as ISSUE-010. Putaway rules must precede any MO processing.

---

## ISSUE-012 — SoapStock Misplaced in Refined Oil Tank 1 (5 kg)

**Severity:** MEDIUM (resolved)
**Status:** FIXED 2026-05-24

### Issue
5 kg SoapStock sitting in `Famoil/Stock/Refined Oil Tank 1` (id=143). This contaminates the refined oil tank location with a different product and misrepresents stock position.

### Root Cause
`mrp.bom.byproduct` has no `location_id` field in Odoo 17 — byproducts are delivered to the same destination as the main finished product. The Refining MO destination at the time was `Refined Oil Tank 1`, so SoapStock was also deposited there.

### Fix
```python
env['stock.quant']._update_available_quantity(soapstock, refined_tank1, -5.0)
env['stock.quant']._update_available_quantity(soapstock, soapstock_tank, 5.0)
```
Long-term fix: set Refining Manufacturing destination to parent `Famoil/Stock` + putaway rule for SoapStock → Soapstock Tank (applied as part of ISSUE-013 resolution).

### Prevention Rule
> When a BOM has byproducts, always set the operation type destination to the parent location and configure putaway rules for every output product (main product and all byproducts). Never set destination to a product-specific child location when a BOM produces more than one output.

---

## ISSUE-013 — Operation Type Source/Destination Not Aligned with 3-Stage Pipeline

**Severity:** HIGH (resolved)
**Status:** FIXED 2026-05-24

### Issue
Manufacturing operation types (Extraction, Refining, Packaging) had incorrect or absent source/destination locations, causing components to be reserved from wrong locations and finished goods to land in wrong locations.

### Root Cause
Operation types were created without configuring source and destination locations. Default Odoo behaviour leaves these blank, falling back to the warehouse's default locations rather than the stage-specific locations required by the 3-stage pipeline.

### Fix
Configured via UI + SQL:

| Stage | Operation Type | Source | Destination |
|---|---|---|---|
| Extraction | Extraction Manufacturing (id=79) | Famoil/Stock/RM Warehouse | Famoil/Stock |
| Refining | Refining Manufacturing (id=127) | Famoil/Stock | Famoil/Stock |
| Packaging | Packaging Manufacturing (id=128) | Famoil/Stock | Famoil/Stock/FG Warehouse |

Putaway rules then route each product from `Famoil/Stock` to the correct child location automatically.

### Prevention Rule
> When configuring a multi-stage manufacturing pipeline, define operation type source and destination locations before creating any BOMs or MOs. Use the parent location as source and destination where putaway rules handle child routing — never hardcode a product-specific child location as an operation type destination when multiple product types pass through that stage.
