# FamOil — Standardization Notes

_What is reusable, what is industry-specific, and how to scale this framework._

---

## 1. Reusable Principles (Any Agro-Processor)

### 1.1 — Single BOM with Byproducts
Any processing industry that converts one raw input into multiple outputs should use a single BOM with byproducts rather than separate BOMs.
- Main output = highest-value primary product
- Byproducts = co-products and waste streams
- Cost shares = percentage of total batch cost absorbed by each byproduct

### 1.2 — Location Hierarchy for Processing Plants
```
Warehouse (view)
└── Stock (view)
    ├── RM Warehouse          ← raw material holding
    ├── Production            ← WIP staging
    ├── [Process tanks/areas] ← intermediate storage
    ├── FG Warehouse          ← finished goods
    ├── Packaging Store       ← packaging inputs
    ├── Packaging Dispatch    ← outbound staging
    ├── QC Area               ← quality hold
    ├── Spare Parts Store     ← maintenance
    └── Waste Area            ← inventory loss type
```
This pattern works for: oil processing, flour milling, sugar refining, dairy, fish processing.

### 1.3 — Work Center = Production Stage
Map each distinct physical operation to one work center. Set `costs_hour` from actual overhead rate for that area (not a blended plant rate). This gives per-stage cost visibility.

### 1.4 — Cost Method by Category

| Category type    | Cost Method | Rationale                            |
|-----------------|------------|--------------------------------------|
| Raw Materials    | Average    | Commodity prices fluctuate — average smooths |
| Finished Goods   | FIFO       | Perishability, traceability          |
| Packaging        | FIFO       | Lot-specific packaging costs         |
| Consumables      | Average    | Low unit value, high frequency       |
| Spare Parts      | Average    | Maintenance budget view              |

### 1.5 — Custom Module Pattern for Location Restrictions
Any location-specific product restriction should:
- Look up locations by name pattern (not hardcoded IDs)
- Override `button_validate` on `stock.picking`
- Return early gracefully if no locations match (avoid false blocks)
- Be versioned and documented in the manifest

### 1.6 — Demo Data Eradication Protocol
Before any data entry on a new instance:
1. Confirm `--without-demo=all` was used OR manually verify and clean demo data
2. Archive all non-project warehouses
3. Zero out all non-project stock quants
4. Archive demo products (office furniture, etc.)
5. Remove or archive demo company

---

## 2. Industry-Specific Elements (Soybean Oil Processing)

These elements are specific to FamOil and must be adapted for other industries:

| Element | FamOil Specific | Generic Equivalent |
|--------|----------------|--------------------|
| BOM ratio | 1000 kg → 140 kg + byproducts | Depends on crop/process |
| Yield | 14% oil extraction rate | Industry yield tables |
| Work centers | Cleaning, Extrusion, Pressing, Filtration, Packaging | Process-specific |
| Tank locations | Crude Oil Tank, Filtered Oil Tank, Soapstock Tank | Storage-specific |
| Byproducts | Soya Cake (feed), SoapStock (resell), Waste | Crop-specific |
| Cost shares | 60/40/0 (crude oil/cake/waste) | Derived from NRV of each output |
| Restriction module | Crude oil tank → Crude Soya Oil only | Product-location restriction pattern |

---

## 3. What Remains Generic (Portable to Other Clients)

| Component | Reusable As-Is |
|----------|---------------|
| `backup_famoil.sh` | Yes — parameterise DB_NAME and paths |
| `inspect_famoil_config.sh` | Yes — parameterise DB_NAME |
| IMPLEMENTATION_PLAYBOOK.md | Yes — phases are universal |
| VALIDATION_CHECKLIST.md | Mostly — update product/location names |
| KNOWN_ISSUES.md | Yes — ISSUE-001, 002, 003, 007 are universal |
| DECISION_LOG.md | Framework is universal — decisions change per client |
| Category structure | Yes — rename categories per industry |
| 3-step warehouse routing | Yes — universal for quality-controlled processing |
| `mrp_component_availability_check` | Yes — applies to any manufacturing client |
| `stock_crude_oil_tank_restriction` | Pattern reusable — names must be adapted |

---

## 4. Future Scaling Strategy

### Scale 1: Add Refining Stage — **COMPLETE (2026-05-24)**
- Refined Oil Tank 1 & 2 — in location hierarchy ✓
- BOM 15 (Refined Soya Oil): Crude Soya Oil → 135 kg Refined + 5 kg SoapStock ✓
- Refining work centers: Neutralization, Bleaching, Deodorization ✓
- Refining Manufacturing operation type (id=127) configured ✓
- Putaway rules route all outputs to correct child locations ✓

### Scale 2: Multiple Production Lines
- Duplicate work centers (Pressing Line 2, etc.)
- BOM routing can assign operations to alternative work centers
- Odoo handles parallel routing natively

### Scale 3: Multiple Plants
- Each plant = one Odoo warehouse (with its own location hierarchy)
- Inter-plant transfers = cross-warehouse internal moves
- Requires multi-warehouse route configuration
- Consider Odoo Enterprise for inter-company transactions if separate legal entities

### Scale 4: Sales & Distribution Module
- Add `sale` app (already installed in Famoil ✓)
- Link finished goods to customer price lists
- Add delivery routes for distributors
- NGN pricing with customer-specific discount structures

### Scale 5: Procurement Automation
- Add `purchase` app (already installed ✓)
- Link SoyaBean to supplier price lists and lead times
- Configure reorder rules on RM Warehouse (min qty → generate PO)
- Track supplier performance (on-time delivery, quality rejects)

### Scale 6: Maintenance Integration
- `maintenance_spareparts_v6` already in custom_addons
- Link spare parts consumption to maintenance orders
- Track MTBF per work center
- Schedule preventive maintenance around production calendar

---

## 5. Deployment Methodology Summary

```
Phase 0: Discovery         → 2–3 days
Phase 1: Environment       → 0.5 day
Phase 2: Master Data       → 1–2 days
Phase 3: Warehouse Setup   → 0.5 day
Phase 4: Manufacturing     → 1 day
Phase 5: Accounting        → 1–2 days
Phase 6: Training          → 2–3 days
Phase 7: Go-Live           → 0.5 day
Phase 8: Stabilization     → 2–4 weeks monitoring
─────────────────────────────────────────
TOTAL                      → 4–6 weeks
```

The FamOil instance represents approximately 3–4 weeks of configuration effort. With this playbook, a similar deployment should be achievable in 2–3 weeks by an experienced Odoo implementer.

---

## 6. Technology Choices That Should Not Change

| Choice | Reason |
|--------|--------|
| Python 3.12 (via venv) | Required for Odoo 17 — do not use system Python |
| PostgreSQL 14+ | Odoo 17 minimum requirement |
| Odoo 17 Community | Active LTS until 2027 |
| OCA web_responsive | Essential for tablet/mobile use on plant floor |
| Plain-text SQL dump | Human-readable, portable, no pg_restore dependency |
