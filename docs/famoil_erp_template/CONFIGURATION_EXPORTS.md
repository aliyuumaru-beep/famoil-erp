# FamOil — Configuration State (Phase 1 Snapshot)

_Captured: 2026-05-22. This is a read-only snapshot of current state — not a target configuration._

## Product Categories

| ID | Category                        | Cost Method | Valuation  |
|----|---------------------------------|-------------|------------|
| 1  | All                             | (default)   | (default)  |
| 17 | All / FamOil / Raw Materials    | NOT SET     | NOT SET    |
| 18 | All / FamOil / Work In Progress | NOT SET     | NOT SET    |
| 19 | All / FamOil / Finished Goods   | FIFO        |            |
| 20 | All / FamOil / Packaging Materials | FIFO     |            |
| 21 | All / FamOil / Consumables      | Average     |            |
| 22 | All / FamOil / Spare Parts      | NOT SET     | NOT SET    |

> **Issue:** Raw Materials category has no cost method set. Should be FIFO or Average. Confirm in Phase 2.

## Products — FamOil

### Raw Materials
| Product  | Category | UoM | List Price | Cost | Note                           |
|---------|----------|-----|-----------|------|--------------------------------|
| SoyaBean | All (!) | kg  | 720.00    | N/A  | WRONG CATEGORY — should be Raw Materials |

### Finished Goods
| Product         | Category                   | UoM | List Price |
|----------------|---------------------------|-----|-----------|
| Crude Soya Oil  | All / FamOil / Finished Goods | kg | 220.00  |
| Soya Cake       | All / FamOil / Finished Goods | kg | 750.00  |
| SoapStock       | All / FamOil / Finished Goods | kg | 150.00  |

### Consumables / WIP
| Product          | Category                       | UoM | List Price |
|-----------------|-------------------------------|-----|-----------|
| Production Waste | All / FamOil / Work In Progress | kg | 1.00    |
| Hexane Chemical  | All / FamOil / Consumables     | —   | 1.00    |
| Lubricant Oil    | All / FamOil / Consumables     | —   | 1.00    |

### Packaging Materials
| Product    | Category                          | UoM | List Price |
|-----------|----------------------------------|-----|-----------|
| 1L Bottle  | All / FamOil / Packaging Materials | — | 1.00     |
| 5L Jerrycan| All / FamOil / Packaging Materials | — | 1.00     |
| Caps       | All / FamOil / Packaging Materials | — | 1.00     |
| Labels     | All / FamOil / Packaging Materials | — | 1.00     |

### Spare Parts
| Product     | Category                  | UoM | List Price |
|------------|--------------------------|-----|-----------|
| Bearing 6205| All / FamOil / Spare Parts | — | 1.00     |
| Oil Filter  | All / FamOil / Spare Parts | — | 1.00     |
| Press Belt A52 | All / FamOil / Spare Parts | — | 1.00  |

> **Issue:** All spare parts, packaging, and consumables have list_price = 1.00. Real costs not yet configured.

## Units of Measure

| Category        | UoMs in Use              |
|----------------|--------------------------|
| Weight         | kg (ref), g, t, lb, oz  |
| Volume         | L (ref), m³, gal, fl oz |
| Unit           | Units (ref), Dozens      |
| Working Time   | Hours, Days              |
| Length         | m (ref), cm, mm, ft, in  |

## Warehouses

| Name        | Code  | Status | Notes                            |
|-------------|-------|--------|----------------------------------|
| YourCompany | WH    | Active | Demo warehouse — not cleaned yet |
| Chicago 1   | CHIC1 | Active | Demo warehouse — not cleaned yet |
| FamOilWH    | CW    | Active | **Project warehouse**            |

## Operation Types (Active)

| Name              | Code       | Warehouse  |
|------------------|-----------|-----------|
| Receipts          | incoming   | WH         |
| Delivery Orders   | outgoing   | WH         |
| Internal Transfers| internal   | WH         |
| Manufacturing     | mrp_op     | WH         |
| Receipts          | incoming   | CHIC1      |
| Delivery Orders   | outgoing   | CHIC1      |
| Manufacturing     | mrp_op     | CHIC1      |
| Receipts          | incoming   | CW (FamOilWH) |
| Delivery Orders   | outgoing   | CW         |
| Pick              | internal   | CW         |
| Pack              | internal   | CW         |
| Internal Transfers| internal   | CW         |
| Manufacturing     | mrp_op     | CW         |

## Routes (Active)

| Route                                              | Status |
|---------------------------------------------------|--------|
| Buy                                                | Active |
| Manufacture                                        | Active |
| YourCompany: Receive in 1 step                     | Active |
| YourCompany: Deliver in 1 step                     | Active |
| Chicago 1: Receive in 1 step                       | Active |
| Chicago 1: Deliver in 1 step                       | Active |
| FamOilWH: Receive in 3 steps (input+quality+stock) | Active |
| FamOilWH: Deliver in 3 steps (pick+pack+ship)      | Active |
| FamOilWH: Cross-Dock                               | Active |
| Replenish on Order (MTO)                           | INACTIVE |

## Demo Data Still Present

These items exist from initial Odoo setup and have not been cleaned:
- Warehouses: YourCompany (WH), Chicago 1 (CHIC1)
- Products: Office furniture, Desk Combination, Table, Drawer, Plastic Laminate, etc.
- BOMs: IDs 1–8 and 12 (Desk Combination, Table, Drawers, etc.)
- Work Centers: Assembly Line 1, Drill Station 1, Assembly Line 2
- Locations: WH/* and CHIC1/* hierarchy
