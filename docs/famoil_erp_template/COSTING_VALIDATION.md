# FamOil — Costing Validation

_Validated: 2026-05-22. Updated: 2026-05-23 — SoapStock removed from BOM 10 (refining byproduct, not crude production); Soya Cake cost share raised 35% → 40%._

---

## 1. Input Configuration

| Parameter       | Value            | Source              |
|----------------|-----------------|---------------------|
| Raw material    | SoyaBean        | BOM component       |
| Input qty       | 1,000 kg        | BOM line            |
| Standard cost   | ₦710/kg         | ir_property (average) |
| Cost method     | Average         | All / Raw Materials |

**Raw material cost per batch:**
```
1,000 kg × ₦710 = ₦710,000
```

> Note: SoyaBean list_price = ₦720/kg, standard_price = ₦710/kg. Minor discrepancy — standard_price is what Odoo uses for costing. Recommend aligning both to the same value.

---

## 2. Work Center Overhead

| Operation               | Work Center               | Time (min) | Rate (₦/hr) | Cost (₦)   |
|------------------------|--------------------------|-----------|------------|------------|
| Cleaning                | FamOil Cleaning Section  | 15        | 15,000     | 3,750      |
| Extrusion               | FamOil Extrusion Section | 30        | 45,000     | 22,500     |
| Pressing/Oil Extraction | FamOil Pressing Section  | 45        | 75,000     | 56,250     |
| Filtration              | FamOil Filtration Section| 20        | 20,000     | 6,667      |
| Bottling                | FamOil Packaging Section | 30        | 12,000     | 6,000      |
| **TOTAL**               |                          | **140**   |            | **95,167** |

> Formula: Cost = (time_cycle_manual ÷ 60) × costs_hour
> These are per-batch times for one BOM run (140 kg Crude Soya Oil output).

---

## 3. Total Production Cost

```
Raw Material Cost :  ₦710,000
Work Center Overhead:  ₦95,167
──────────────────────────────
Total Batch Cost  :  ₦805,167
```

---

## 4. Output Cost Allocation (Odoo Byproduct Method)

Odoo distributes total batch cost using `cost_share` percentages assigned to byproducts. The remainder goes to the main output.

| Output           | Qty   | UoM | Cost Share | Allocated Cost  | Unit Cost    |
|-----------------|-------|-----|-----------|-----------------|-------------|
| Soya Cake        | 840   | kg  | 40%       | ₦322,067        | ₦383/kg     |
| Production Waste | 10    | kg  | 0%        | ₦0              | ₦0/kg       |
| **Crude Soya Oil** | **140** | **kg** | **60% (residual)** | **₦483,100** | **₦3,451/kg** |

**Calculation:**
```
Byproduct total share : 40% + 0% = 40%
Main product share    : 100% - 40% = 60%

Crude Soya Oil cost   : ₦805,167 × 60%  = ₦483,100 → ₦483,100 ÷ 140 kg = ₦3,451/kg
Soya Cake cost        : ₦805,167 × 40%  = ₦322,067 → ₦322,067 ÷ 840 kg = ₦383/kg
Production Waste      : ₦805,167 × 0%   = ₦0
```

---

## 5. Revenue vs Cost Check (at current list prices)

| Output          | Qty  | List Price | Revenue     |
|----------------|------|-----------|------------|
| Crude Soya Oil  | 140  | ₦220/kg   | ₦30,800    |
| Soya Cake       | 840  | ₦750/kg   | ₦630,000   |
| **Total**       |      |           | **₦660,800** |

```
Total Revenue   :  ₦660,800
Total Cost      :  ₦805,167
Gross Loss      : -₦144,367  (-17.9%)
```

> **CRITICAL WARNING:** At current list prices, each batch runs at a ₦144,367 loss.
> Crude Soya Oil at ₦220/kg is almost certainly a placeholder — market price is typically ₦1,500–₦3,000/litre.
> **List prices must be updated before any financial reporting is trusted.**

---

## 6. Comparison: Expected vs Actual Odoo Configuration

| Parameter              | Expected                  | Actual (DB)         | Status  |
|-----------------------|--------------------------|---------------------|---------|
| BOM input             | 1,000 kg SoyaBean        | ✓ 1,000 kg          | OK      |
| BOM main output       | 140 kg Crude Soya Oil    | ✓ 140 kg            | OK      |
| Byproduct: Soya Cake  | 840 kg, 40% cost share   | ✓ 840 kg, 40%       | OK      |
| Byproduct: Waste      | 10 kg, 0% cost share     | ✓ 10 kg, 0%         | OK      |
| SoyaBean cost method  | Average                  | ✓ Average           | OK      |
| Finished goods method | FIFO                     | ✓ FIFO              | OK      |
| SoyaBean standard cost| Set                      | ✓ ₦710/kg           | OK      |
| Finished goods cost   | Computed from MO         | ✓ No manual cost set| OK      |
| Hexane Chemical in BOM| Yes (consumable)         | ✗ NOT in BOM        | GAP     |
| Lubricant Oil in BOM  | Yes (consumable)         | ✗ NOT in BOM        | GAP     |
| Crude Soya Oil price  | Market rate              | ✗ ₦220 (placeholder)| FIX     |
| SoyaBean list_price   | = standard_price         | ✗ ₦720 vs ₦710      | MINOR   |
| Valuation method      | Automated perpetual      | Not explicitly set   | REVIEW  |

---

## 7. Gaps & Recommendations

### GAP 1 — Hexane Chemical and Lubricant Oil not in BOM
- **Impact:** Their costs (₦11,000 and ₦3,000 per batch) are invisible to manufacturing cost.
- **Fix:** Add to BOM with realistic quantities per 1,000 kg batch.
- **Estimated impact:** +₦14,000 to batch cost → Crude Soya Oil unit cost rises to ~₦3,551/kg.

### GAP 2 — List prices are placeholders
- **Impact:** All margin/profitability reports are misleading.
- **Fix:** Update list prices to reflect actual market selling prices (NGN).

### GAP 3 — Inventory valuation method not explicitly set
- **Impact:** Odoo defaults to "Manual Periodic" if not set — no automatic journal entries.
- **Fix:** For each FamOil category, explicitly set valuation to "Automated (Perpetual)" if real-time costing is required.

### GAP 4 — Work center rates not verified against actual payroll/energy costs
- **Impact:** Overhead may be overstated or understated.
- **Fix:** Validate rates against actual utility bills and labour costs for the plant.

---

## 8. Current Stock Snapshot (corrected 2026-05-24)

Stock corrections applied 2026-05-24 via `scripts/fix_locations_and_routing.py`:
- Negative quant (-81 kg) in Crude Oil Tank 1 zeroed out
- Misplaced Crude Soya Oil (20 kg parent + 179 kg FG Warehouse) moved to Crude Oil Tank 1
- Misplaced Refined Soya Oil (135 kg parent) moved to Refined Oil Tank 1
- Misplaced SoapStock (5 kg in Refined Oil Tank 1) moved to Soapstock Tank

| Product           | Location                            | Qty      |
|------------------|-------------------------------------|----------|
| SoyaBean          | Famoil/Stock/RM Warehouse           | 1,000 kg |
| Crude Soya Oil    | Famoil/Stock/Crude Oil Tank 1       | 199 kg   |
| Crude Soya Oil    | Famoil/Stock/Crude Oil Tank 2       | 22 kg    |
| Refined Soya Oil  | Famoil/Stock/Refined Oil Tank 1     | 224 kg   |
| SoapStock         | Famoil/Stock/Soapstock Tank         | 5 kg     |
| SoapStock         | Famoil/Stock/FG Warehouse           | 30 kg    |
| Soya Cake         | Famoil/Stock/FG Warehouse           | 2,520 kg |

> Soya Cake quantity (2,520 kg) = exactly 3 extraction runs × 840 kg. Confirms 3 Stage 1 batches completed.
> Refined Soya Oil (224 kg) includes one validated Stage 2 MO (135 kg) plus earlier stock.
