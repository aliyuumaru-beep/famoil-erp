# FamOil — Implementation Playbook

_A step-by-step guide for deploying this ERP framework for an agro-processing plant on Odoo 17 Community._

---

## Phase 0 — Discovery & Scoping

### Prerequisites
- Access to plant floor for process observation
- Sample invoices and purchase orders (last 3 months)
- List of all raw materials, consumables, finished products
- Org chart and user list

### Steps
1. Map the physical production flow (inputs → process stages → outputs).
2. Identify all storage locations (tanks, warehouses, areas).
3. List all products with current purchase prices and selling prices.
4. Identify byproducts and waste streams.
5. Determine costing preference (FIFO, average, standard).
6. Confirm currency, country, fiscal year start.
7. Count expected users and roles.

### Validation Checks
- [ ] Production flow diagram signed off by plant manager
- [ ] Product list confirmed with finance team
- [ ] Costing method approved by accountant

### Failure Points
- Incomplete product list → BOM gaps discovered after go-live
- Incorrect yield percentages → wrong cost allocation from day one
- No accountant involvement → wrong chart of accounts

### Estimated Effort
2–3 days

---

## Phase 1 — Environment Setup

### Prerequisites
- macOS or Linux server with Python 3.10+
- PostgreSQL 14+
- Odoo 17 Community source

### Steps
1. Create fresh database with no demo data:
   ```bash
   createdb -U odoo -E UTF8 "ClientDB"
   python odoo-bin -d ClientDB --without-demo=all -i base
   ```
2. Configure `odoo.conf`:
   ```ini
   db_user = odoo
   db_name = ClientDB
   addons_path = odoo/addons,custom_addons,oca_web
   http_port = 8069
   log_level = info
   ```
3. Set company name, country (Nigeria), currency (NGN), fiscal year.
4. Archive the default "My Company" if it still exists.
5. Install core apps: Inventory, Manufacturing, Accounting.
6. Install OCA web addons (web_responsive, web_environment_ribbon).
7. Install custom FamOil modules.

### Validation Checks
- [ ] `--without-demo=all` confirmed — no demo products, no demo warehouses
- [ ] Company = real client name, currency = NGN
- [ ] Only one company in Settings → Companies
- [ ] All required apps installed and no errors in server log

### Failure Points
- Starting from a demo database → ISSUE-001 (CHIC1 phantom reservations), ISSUE-002 (WH/Stock pollution)
- Installing apps before setting company/currency → chart of accounts uses wrong defaults

### CSV Templates
See `templates/` directory.

### Estimated Effort
0.5 day

---

## Phase 2 — Master Data

### Prerequisites
- Phase 1 complete
- Product list from discovery

### Steps

#### 2a — Units of Measure
Verify kg is the reference UoM for Weight. Add litres (L) if oil is sold by volume.

#### 2b — Product Categories
Create categories in this order (parent before child):
```
All / Raw Materials       → Average cost, Automated valuation
All / Finished Goods      → FIFO, Automated valuation
All / Work In Progress    → Average cost
All / Consumables         → Average cost
All / Packaging Materials → FIFO
All / Spare Parts         → Average cost
```

> Use CSV import: `templates/product_categories.csv`

#### 2c — Products
Create all products with correct:
- Category
- UoM (kg for solids, L for liquids)
- Internal reference / barcode
- Standard cost (for raw materials)
- Sales price (for finished goods)
- Product type: Storable for anything physically tracked

> Use CSV import: `templates/products.csv`

#### 2d — Set Standard Costs
After creating products, set standard cost for each raw material:
- Go to product → Cost tab → Update cost

### Validation Checks
- [ ] All products in correct category
- [ ] All raw materials have non-zero standard cost
- [ ] All finished goods have realistic list price
- [ ] No products left in category "All" (root)

### Failure Points
- Products in wrong category → wrong cost method applied silently
- Zero standard cost on raw materials → zero-cost manufacturing orders
- list_price = 1.00 (placeholder) → wrong margin reports

### Estimated Effort
1–2 days depending on product count

---

## Phase 3 — Warehouse & Inventory Setup

### Prerequisites
- Phase 2 complete
- Physical layout confirmed

### Steps

#### 3a — Configure Warehouse
1. Inventory → Configuration → Warehouses
2. Create: Name = "FamOilWH", Short Code = "CW"
3. Set inbound: 3 steps (Input + QC + Stock)
4. Set outbound: 3 steps (Pick + Pack + Ship)

#### 3b — Create Storage Locations
Under CW/Stock, create child locations:
```
RM Warehouse              (internal)
Production                (internal)
Crude Oil Tank 1          (internal)
Crude Oil Tank 2          (internal)
Filtered Oil Tank 1       (internal)
Filtered Oil Tank 2       (internal)
Cake Storage Area         (internal)
Soapstock Tank            (internal)
FG Warehouse              (internal)
Packaging Store           (internal)
Packaging Dispatch Area   (internal)
Spare Parts Store         (internal)
Quality Control           (internal)
Waste Area                (inventory loss)
```

> Use CSV import: `templates/stock_locations.csv`

#### 3c — Install Tank Restriction Module
```bash
python odoo-bin -d ClientDB -u stock_crude_oil_tank_restriction
```
Verify the module looks up tanks by name `ilike 'Crude Oil Tank'` — no hardcoded IDs.

#### 3d — Archive Demo Warehouses
Archive YourCompany and any other demo warehouses before any stock entry.

### Validation Checks
- [ ] FamOilWH visible in Inventory → Warehouses
- [ ] All 14 custom locations visible under CW/Stock
- [ ] Tank restriction module installed
- [ ] Demo warehouses archived
- [ ] No stock quants in any non-project location

### Failure Points
- Creating locations before archiving demo warehouses → reservation pollution
- Wrong location type (e.g., inventory instead of internal) → breaks stock moves

### Estimated Effort
0.5 day

---

## Phase 4 — Manufacturing Configuration

### Prerequisites
- Phase 3 complete
- Work center cost rates confirmed with finance

### Steps

#### 4a — Work Centers
Create 5 work centers with accurate hourly rates:

| Name                     | Code | Capacity | Rate (₦/hr) |
|--------------------------|------|---------|------------|
| FamOil Cleaning Section  | CLN  | 140 kg  | [actual]   |
| FamOil Extrusion Section | EXT  | 140 kg  | [actual]   |
| FamOil Pressing Section  | PRS  | 140 kg  | [actual]   |
| FamOil Filtration Section| FLT  | 140 kg  | [actual]   |
| FamOil Packaging Section | PKG  | 140 kg  | [actual]   |

#### 4b — Operation Types
Create three dedicated operation types (Manufacturing → Configuration → Operations):

| Operation Type           | Source Location         | Destination Location       |
|--------------------------|-------------------------|----------------------------|
| Extraction Manufacturing | [WH]/Stock/RM Warehouse | [WH]/Stock (parent)        |
| Refining Manufacturing   | [WH]/Stock (parent)     | [WH]/Stock (parent)        |
| Packaging Manufacturing  | [WH]/Stock (parent)     | [WH]/Stock/FG Warehouse    |

> Setting destination to the parent location allows putaway rules to route each product to its correct child location. Never set destination to a product-specific tank when a BOM produces multiple outputs.

#### 4c — Putaway Rules
Configure via Inventory → Configuration → Putaway Rules. All rules use the parent Stock location as "From":

| Product               | From (arrives at) | To (routed to)      |
|----------------------|-------------------|---------------------|
| Crude Soya Oil        | [WH]/Stock        | Crude Oil Tank 1    |
| Refined Soya Oil      | [WH]/Stock        | Refined Oil Tank 1  |
| SoapStock             | [WH]/Stock        | Soapstock Tank      |
| Soya Cake             | [WH]/Stock        | FG Warehouse        |
| Refined Soya Oil 5L   | [WH]/Stock        | FG Warehouse        |
| Refined Soya Oil 25L  | [WH]/Stock        | FG Warehouse        |

> **Configure putaway rules BEFORE processing the first MO.** Outputs from MOs completed before rules are set will land in the parent location without routing.

#### 4d — BOM 10: Crude Soya Oil (Extraction Stage)

| Field          | Value                              |
|---------------|------------------------------------|
| Product        | Crude Soya Oil                     |
| Quantity       | 140 kg                             |
| BOM Type       | Manufacturing                      |
| Routing        | Extraction Manufacturing           |

**Components:**

| Product          | Qty   | UoM | Type       |
|-----------------|-------|-----|------------|
| SoyaBean         | 1,000 | kg  | Storable   |
| Hexane Chemical  | [qty] | L   | Consumable |
| Lubricant Oil    | [qty] | L   | Consumable |

**Byproducts:**

| Product          | Qty | UoM | Cost Share |
|-----------------|-----|-----|------------|
| Soya Cake        | 840 | kg  | 40%        |
| Production Waste | 10  | kg  | 0%         |

> Do NOT add SoapStock here — it is a refining byproduct (Stage 2), not an extraction output.

**Operations:**

| Seq | Name                    | Work Center | Duration (min) |
|-----|------------------------|------------|---------------|
| 1   | Cleaning                | Cleaning   | 15            |
| 2   | Extrusion               | Extrusion  | 30            |
| 3   | Pressing/Oil Extraction | Pressing   | 45            |
| 4   | Filtration              | Filtration | 20            |
| 5   | Bottling                | Packaging  | 30            |

#### 4e — BOM 15: Refined Soya Oil (Refining Stage)

| Field          | Value                              |
|---------------|------------------------------------|
| Product        | Refined Soya Oil                   |
| Quantity       | 135 kg                             |
| BOM Type       | Manufacturing                      |
| Routing        | Refining Manufacturing             |

**Components:**

| Product          | Qty   | UoM | Type       |
|-----------------|-------|-----|------------|
| Crude Soya Oil   | 140   | kg  | Storable   |
| Caustic Soda     | [qty] | kg  | Consumable |
| Bleaching Earth  | [qty] | kg  | Consumable |
| Citric Acid      | [qty] | kg  | Consumable |

**Byproducts:**

| Product   | Qty | UoM | Cost Share |
|-----------|-----|-----|------------|
| SoapStock | 5   | kg  | —          |

**Operations:**

| Seq | Name              | Work Center    | Duration (min) |
|-----|------------------|----------------|---------------|
| 1   | Neutralization   | Neutralization | 30            |
| 2   | Bleaching        | Bleaching      | 45            |
| 3   | Deodorization    | Deodorization  | 60            |
| 4   | Final Filtration | Filtration     | 20            |

#### 4f — Packaging BOMs
Create one BOM per packaging SKU (e.g., 25L, 5L), routing to Packaging Manufacturing operation type.

### Validation Checks
- [ ] BOM 10 cost simulation shows expected unit cost (~₦3,451/kg at ₦710 SoyaBean + current work center rates)
- [ ] BOM 10 byproduct cost shares sum to ≤ 100% (Soya Cake 40% + Waste 0% = 40%)
- [ ] All 5 BOM 10 operations linked to correct work centers
- [ ] BOM 15 confirmed active with correct Crude Soya Oil input quantity
- [ ] All 3 operation types have correct source and destination locations
- [ ] All 6 putaway rules created before first MO
- [ ] Test MO (BOM 10): components reserve from RM Warehouse; Crude Soya Oil routes to Crude Oil Tank 1; Soya Cake routes to FG Warehouse
- [ ] Test MO (BOM 15): Crude Soya Oil reserves from Crude Oil Tank 1; Refined Soya Oil routes to Refined Oil Tank 1; SoapStock routes to Soapstock Tank

### Failure Points
- Operations missing → no overhead posted to manufacturing cost
- SoapStock added to BOM 10 → wrong cost allocation and wrong physical output stage
- Byproduct cost shares wrong → main product cost over/understated
- Operation type destination set to child location → byproducts land in wrong location
- Putaway rules created after first MO → outputs land in parent location, require manual correction

### Estimated Effort
1–2 days

---

## Phase 5 — Accounting Setup

### Prerequisites
- Chart of accounts installed (Nigerian GAAP preferred)
- Phase 2–4 complete

### Steps
1. Set fiscal year: January–December (or Nigerian financial year).
2. Configure journals: Sales, Purchase, Inventory Valuation, Stock Journal.
3. Map product categories to accounts:
   - Raw Materials → Stock Valuation Account, COGS Account
   - Finished Goods → Stock Valuation Account, Revenue Account
4. Set valuation method to "Automated (Perpetual)" for all FamOil categories.
5. Configure Nigerian tax rates (VAT 7.5%).
6. Set up bank journals in NGN.

### Validation Checks
- [ ] Trial balance opens with zero (fresh start)
- [ ] Test inventory receipt creates correct journal entry
- [ ] Manufacturing order posts WIP and finished goods correctly
- [ ] NGN currency rates configured

### Failure Points
- "Manual Periodic" valuation left by default → no real-time costing journals
- Wrong stock accounts mapped → valuation goes to wrong P&L line
- Currency not set → transactions default to USD

### Estimated Effort
1–2 days (with accountant involvement)

---

## Phase 6 — Training

### Prerequisites
- All configuration complete
- Test data entered and validated

### User Roles & Training Topics

| Role            | Modules          | Training Focus                          |
|----------------|------------------|-----------------------------------------|
| Store Keeper    | Inventory        | Receipts, internal transfers, locations |
| Plant Operator  | Manufacturing    | MO creation, work orders, production    |
| QC Officer      | Inventory        | QC location moves, quality holds        |
| Accountant      | Accounting       | Journals, valuation, reconciliation     |
| Manager         | All              | Reporting, dashboards, approval flows   |

### Estimated Effort
2–3 days (half day per role)

---

## Phase 7 — Go-Live

### Prerequisites
- All validation checklists passed (see VALIDATION_CHECKLIST.md)
- Backup taken
- Opening stock balances entered

### Steps
1. Enter opening stock quantities (inventory adjustment).
2. Enter opening stock values (manual journal if needed).
3. Create first real manufacturing order.
4. Validate first real receipt.
5. Monitor for 1 week before declaring stable.

### Failure Points
- Opening stock entered without correct valuation → wrong COGS from day one
- No backup before go-live → no rollback if something goes wrong

---

## Phase 8 — Stabilization

### Steps
1. Run daily: review open MOs, pending transfers, unreconciled payments.
2. Run weekly: stock valuation report, cost variance check.
3. Run monthly: close accounting period, backup database.
4. Review work center rates quarterly against actual costs.

### Scripts
```bash
# Daily backup
bash /Users/mac/odoo17/scripts/backup_famoil.sh

# Config inspection
bash /Users/mac/odoo17/scripts/inspect_famoil_config.sh
```
