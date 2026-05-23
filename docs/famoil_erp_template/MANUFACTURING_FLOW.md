# FamOil — Manufacturing Flow

## Process Overview

Soybean oil processing converts raw soybeans into crude oil and co-products through five sequential work center stages.

```
INPUT: 1000 kg SoyaBean
        │
        ▼
 ┌─────────────────┐
 │  1. Cleaning    │  15 min  @ ₦15,000/hr  (FamOil Cleaning Section)
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │  2. Extrusion   │  30 min  @ ₦45,000/hr  (FamOil Extrusion Section)
 └────────┬────────┘
          │
          ▼
 ┌─────────────────────────┐
 │  3. Pressing/Extraction │  45 min  @ ₦75,000/hr  (FamOil Pressing Section)
 └────────┬────────────────┘
          │
          ▼
 ┌─────────────────┐
 │  4. Filtration  │  20 min  @ ₦20,000/hr  (FamOil Filtration Section)
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │  5. Bottling    │  30 min  @ ₦12,000/hr  (FamOil Packaging Section)
 └────────┬────────┘
          │
          ├──► 140 kg  Crude Soya Oil   (MAIN OUTPUT — BOM product)
          ├──► 840 kg  Soya Cake        (Byproduct, 35% cost share)
          ├──►  10 kg  SoapStock        (Byproduct,  5% cost share)
          └──►  10 kg  Production Waste (Byproduct,  0% cost share)
```

## Bill of Materials (BOM ID: 10)

| Field        | Value                    |
|-------------|--------------------------|
| BOM Type    | Manufacturing (Normal)    |
| Main Output | Crude Soya Oil — 140 kg  |
| BOM Active  | Yes                      |

### Components

| Component | Qty    | UoM |
|-----------|--------|-----|
| SoyaBean  | 1000   | kg  |

### Byproducts

| Byproduct        | Qty  | UoM | Cost Share |
|-----------------|------|-----|------------|
| Soya Cake        | 840  | kg  | 35%        |
| SoapStock        | 10   | kg  | 5%         |
| Production Waste | 10   | kg  | 0%         |

> Confirmed 2026-05-22: 10 kg SoapStock (sellable byproduct, 5% cost share) + 10 kg Production Waste (disposal, 0% cost share). BOM is correct as-is.

## Operations / Routing (BOM 10)

| Seq | Operation Name      | Work Center               | Duration (min) | Cost/hr (₦) |
|-----|---------------------|--------------------------|---------------|-------------|
| 1   | Cleaning            | FamOil Cleaning Section   | 15            | 15,000      |
| 2   | Extrusion           | FamOil Extrusion Section  | 30            | 45,000      |
| 3   | Pressing/Oil Extraction | FamOil Pressing Section | 45           | 75,000      |
| 4   | Filtration          | FamOil Filtration Section | 20            | 20,000      |
| 5   | Bottling            | FamOil Packaging Section  | 30            | 12,000      |


## Work Centers

| ID | Name                     | Cost/hr (₦) | Capacity | Efficiency |
|----|--------------------------|------------|---------|------------|
| 9  | FamOil Cleaning Section  | 15,000     | 140 kg  | 100%       |
| 10 | FamOil Extrusion Section | 45,000     | 140 kg  | 100%       |
| 11 | FamOil Pressing Section  | 75,000     | 140 kg  | 100%       |
| 12 | FamOil Filtration Section| 20,000     | 140 kg  | 100%       |
| 13 | FamOil Packaging Section | 12,000     | 140 kg  | 100%       |

> Legacy work centers (Assembly Line 1, Drill Station 1, Assembly Line 2) are still present as demo data.

## Estimated Operation Cost Per Run

Total time: 140 min = 2.33 hours

| Work Center    | Time (min) | Cost/hr  | Cost per Run |
|---------------|-----------|----------|-------------|
| Cleaning       | 15        | ₦15,000  | ₦3,750      |
| Extrusion      | 30        | ₦45,000  | ₦22,500     |
| Pressing       | 45        | ₦75,000  | ₦56,250     |
| Filtration     | 20        | ₦20,000  | ₦6,667      |
| Bottling       | 30        | ₦12,000  | ₦6,000      |
| **TOTAL**      | **140**   |          | **₦95,167** |

> This is labour/machine cost only. Does not include material cost.

## Warehouse & Storage Locations

**Active Warehouse:** FamOilWH (code: CW)

| Location                   | Type     | Purpose                         |
|---------------------------|----------|---------------------------------|
| CW/Stock/RM Warehouse      | Internal | Raw material input storage      |
| CW/Stock/Production        | Internal | WIP staging                     |
| CW/Stock/Crude Oil Tank 1  | Internal | Crude oil output storage        |
| CW/Stock/Crude Oil Tank 2  | Internal | Crude oil output storage (alt)  |
| CW/Stock/Filtered Oil Tank 1 | Internal | Post-filtration storage       |
| CW/Stock/Filtered Oil Tank 2 | Internal | Post-filtration storage (alt) |
| CW/Stock/Cake Storage Area | Internal | Soya Cake storage               |
| CW/Stock/Soapstock Tank    | Internal | Soapstock byproduct storage     |
| CW/Stock/Waste Area        | Inventory | Production waste disposal      |
| CW/Stock/FG Warehouse      | Internal | Finished goods                  |
| CW/Stock/Packaging Store   | Internal | Packaging materials             |
| CW/Stock/Packaging Dispatch Area | Internal | Outbound staging          |
| CW/Stock/Spare Parts Store | Internal | Maintenance spares              |
| CW/Stock/Quality Control   | Internal | QC hold area                    |
| CW/Input                   | Internal | 3-step inbound receiving        |
| CW/Output                  | Internal | 3-step outbound shipping        |

**Routing:** FamOilWH configured for 3-step inbound (input + quality + stock) and 3-step outbound (pick + pack + ship).

## Crude Oil Tank Restriction (Custom Logic)

Location IDs 141 and 142 (Crude Oil Tank 1 & 2) are restricted to accept only product ID 111 (Crude Soya Oil). Any transfer validation attempt with a different product raises an error.

> **Risk:** These IDs are hardcoded in `stock_crude_oil_tank_restriction/models/stock_picking.py`. They must match the actual database IDs or the restriction will silently stop working.
