# FamOil — Manufacturing Flow

_Last updated: 2026-05-24_

## 3-Stage Pipeline Overview

```
RM Warehouse
│
│  1,000 kg SoyaBean
▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 1 — EXTRACTION  (BOM 10, Operation Type id=79)   │
│  Extraction Manufacturing: source=RM Warehouse           │
│  destination=Famoil/Stock (putaway routes outputs)       │
│                                                          │
│  Cleaning (15 min) → Extrusion (30 min)                  │
│  → Pressing (45 min) → Filtration (20 min)               │
│  → Bottling (30 min)                                     │
└──────────────────────────┬──────────────────────────────┘
                           │
            ┌──────────────┴────────────────┐
            │                               │
            ▼                               ▼
   140 kg Crude Soya Oil          840 kg Soya Cake
   → Crude Oil Tank 1             → FG Warehouse
   (putaway rule)                 (putaway rule)
                                  10 kg Production Waste
                                  → (consumed/disposed)

│
│  140 kg Crude Soya Oil (from Crude Oil Tank 1)
▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 2 — REFINING  (BOM 15, Operation Type id=127)    │
│  Refining Manufacturing: source=Famoil/Stock             │
│  destination=Famoil/Stock (putaway routes outputs)       │
│                                                          │
│  Neutralization (30 min) → Bleaching (45 min)            │
│  → Deodorization (60 min) → Final Filtration (20 min)    │
└──────────────────────────┬──────────────────────────────┘
                           │
            ┌──────────────┴────────────────┐
            │                               │
            ▼                               ▼
   135 kg Refined Soya Oil          5 kg SoapStock
   → Refined Oil Tank 1             → Soapstock Tank
   (putaway rule)                   (putaway rule)

│
│  Refined Soya Oil (from Refined Oil Tank 1)
▼
┌─────────────────────────────────────────────────────────┐
│  STAGE 3 — PACKAGING  (BOMs 208/209, Op Type id=128)    │
│  Packaging Manufacturing: source=Famoil/Stock            │
│  destination=Famoil/Stock/FG Warehouse                   │
│                                                          │
│  BOMs: 25L pack (BOM 208), 5L pack (BOM 209)             │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
             Refined Soya Oil 25L / 5L → FG Warehouse
```

---

## Stage 1 — Extraction: BOM 10

| Field        | Value                    |
|-------------|--------------------------|
| BOM ID      | 10                       |
| BOM Type    | Manufacturing (Normal)    |
| Main Output | Crude Soya Oil — 140 kg  |
| Operation Type | Extraction Manufacturing (id=79) |

### Components

| Component | Qty    | UoM |
|-----------|--------|-----|
| SoyaBean  | 1,000  | kg  |

### Byproducts

| Byproduct        | Qty  | UoM | Cost Share | Destination (via putaway) |
|-----------------|------|-----|------------|--------------------------|
| Soya Cake        | 840  | kg  | 40%        | FG Warehouse             |
| Production Waste | 10   | kg  | 0%         | disposed                 |

> SoapStock removed from BOM 10 on 2026-05-23 — it is produced during refining (Stage 2), not extraction.

### Operations / Routing (BOM 10)

| Seq | Operation Name          | Work Center               | Duration (min) | Cost/hr (₦) |
|-----|-------------------------|--------------------------|---------------|-------------|
| 1   | Cleaning                | FamOil Cleaning Section   | 15            | 15,000      |
| 2   | Extrusion               | FamOil Extrusion Section  | 30            | 45,000      |
| 3   | Pressing/Oil Extraction | FamOil Pressing Section   | 45            | 75,000      |
| 4   | Filtration              | FamOil Filtration Section | 20            | 20,000      |
| 5   | Bottling                | FamOil Packaging Section  | 30            | 12,000      |

### Stage 1 Operation Cost Per Batch

| Work Center    | Time (min) | Cost/hr  | Cost per Batch |
|---------------|-----------|----------|----------------|
| Cleaning       | 15        | ₦15,000  | ₦3,750         |
| Extrusion      | 30        | ₦45,000  | ₦22,500        |
| Pressing       | 45        | ₦75,000  | ₦56,250        |
| Filtration     | 20        | ₦20,000  | ₦6,667         |
| Bottling       | 30        | ₦12,000  | ₦6,000         |
| **TOTAL**      | **140**   |          | **₦95,167**    |

---

## Stage 2 — Refining: BOM 15

| Field        | Value                     |
|-------------|---------------------------|
| BOM ID      | 15                        |
| BOM Type    | Manufacturing (Normal)     |
| Main Output | Refined Soya Oil — 135 kg |
| Operation Type | Refining Manufacturing (id=127) |

### Components

| Component      | Qty   | UoM | Type       |
|---------------|-------|-----|------------|
| Crude Soya Oil | 140   | kg  | Storable   |
| Caustic Soda   | [qty] | kg  | Consumable |
| Bleaching Earth| [qty] | kg  | Consumable |
| Citric Acid    | [qty] | kg  | Consumable |

> Consumables (Caustic Soda, Bleaching Earth, Citric Acid) are type=consu — no quant tracking needed.

### Byproducts

| Byproduct | Qty | UoM | Cost Share | Destination (via putaway) |
|-----------|-----|-----|------------|--------------------------|
| SoapStock | 5   | kg  | —          | Soapstock Tank           |

### Operations / Routing (BOM 15)

| Seq | Operation Name    | Work Center    | Duration (min) |
|-----|------------------|----------------|---------------|
| 1   | Neutralization   | Neutralization (id=20) | 30   |
| 2   | Bleaching        | Bleaching (id=21)      | 45   |
| 3   | Deodorization    | Deodorization (id=23)  | 60   |
| 4   | Final Filtration | Filtration (id=9)      | 20   |

---

## Stage 3 — Packaging: BOMs 208 / 209

| Field        | Value                               |
|-------------|-------------------------------------|
| BOM IDs     | 208 (25L pack), 209 (5L pack)       |
| BOM Type    | Manufacturing (Normal)               |
| Operation Type | Packaging Manufacturing (id=128) |

---

## Work Centers

### Extraction Work Centers

| ID | Name                     | Cost/hr (₦) | Capacity |
|----|--------------------------|------------|---------|
| 9  | FamOil Filtration Section| 20,000     | 140 kg  |
| 10 | FamOil Extrusion Section | 45,000     | 140 kg  |
| 11 | FamOil Pressing Section  | 75,000     | 140 kg  |
| 12 | FamOil Cleaning Section  | 15,000     | 140 kg  |
| 13 | FamOil Packaging Section | 12,000     | 140 kg  |

### Refining Work Centers

| ID | Name           | Cost/hr (₦) |
|----|----------------|------------|
| 20 | Neutralization | set        |
| 21 | Bleaching      | set        |
| 23 | Deodorization  | set        |

> Legacy demo work centers (Assembly Line 1, Drill Station 1) still present — not yet archived.

---

## Operation Types (Manufacturing Pipeline)

| Stage      | Operation Type               | ID  | Source              | Destination      |
|-----------|------------------------------|-----|---------------------|------------------|
| Extraction | Extraction Manufacturing     | 79  | Famoil/Stock/RM Warehouse | Famoil/Stock |
| Refining   | Refining Manufacturing       | 127 | Famoil/Stock        | Famoil/Stock     |
| Packaging  | Packaging Manufacturing      | 128 | Famoil/Stock        | Famoil/Stock/FG Warehouse |

---

## Putaway Rules

All rules trigger on arrival at `Famoil/Stock` (id=152):

| Product              | Destination              |
|---------------------|--------------------------|
| Crude Soya Oil       | Crude Oil Tank 1         |
| Refined Soya Oil     | Refined Oil Tank 1       |
| SoapStock            | Soapstock Tank           |
| Soya Cake            | FG Warehouse             |
| Refined Soya Oil 5L  | FG Warehouse             |
| Refined Soya Oil 25L | FG Warehouse             |

---

## Warehouse & Storage Locations

**Active Warehouse:** FamOilWH (code: CW) — Famoil/Stock parent id=152

| Location                          | ID  | Type      | Purpose                         |
|----------------------------------|-----|-----------|---------------------------------|
| Famoil/Stock/RM Warehouse         | 138 | Internal  | Raw material input storage      |
| Famoil/Stock/Crude Oil Tank 1     | 141 | Internal  | Crude oil output (Stage 1)      |
| Famoil/Stock/Crude Oil Tank 2     | 142 | Internal  | Crude oil overflow/alt tank     |
| Famoil/Stock/Refined Oil Tank 1   | 143 | Internal  | Refined oil output (Stage 2)    |
| Famoil/Stock/Refined Oil Tank 2   | 144 | Internal  | Refined oil alt tank            |
| Famoil/Stock/Soapstock Tank       | 149 | Internal  | SoapStock byproduct storage     |
| Famoil/Stock/FG Warehouse         | 140 | Internal  | Finished goods                  |
| Famoil/Stock/Production           | —   | Internal  | WIP staging                     |
| Famoil/Stock/Packaging Store      | —   | Internal  | Packaging materials             |
| Famoil/Stock/Packaging Dispatch   | —   | Internal  | Outbound staging                |
| Famoil/Stock/Spare Parts Store    | —   | Internal  | Maintenance spares              |
| Famoil/Stock/Quality Control      | —   | Internal  | QC hold area                    |
| Famoil/Stock/Waste Area           | —   | Inv. Loss | Production waste disposal       |
| CW/Input                          | —   | Internal  | 3-step inbound receiving        |
| CW/Output                         | —   | Internal  | 3-step outbound shipping        |

**Routing:** 3-step inbound (Input + QC + Stock) and 3-step outbound (Pick + Pack + Ship).

---

## Crude Oil Tank Restriction (Custom Logic)

`stock_crude_oil_tank_restriction` v17.0.1.1.0 — overrides `button_validate` on `stock.picking`. Any transfer attempting to move a non-Crude-Soya-Oil product into a Crude Oil Tank raises a `UserError`.

Tank locations and product are identified at runtime by name search (no hardcoded IDs):
- Tanks: `location.name ilike 'Crude Oil Tank'`, usage=internal
- Product: `product.name = 'Crude Soya Oil'`
