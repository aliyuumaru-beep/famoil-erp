# Testing Guide
# FamOil Software Factory
# Version: 1.0 | Created: 2026-05-27

---

## 1. Testing Strategy by Phase

| Phase | Testing Focus                                         | Approach              |
|------|-------------------------------------------------------|-----------------------|
| 1    | Instance inspection — verify readings match DB state  | SQL queries           |
| 2    | Configuration validation — MO lifecycle, costing      | Manual MO + shell     |
| 3    | Framework — template applicability across industries  | Document review       |
| 4    | CI/CD — workflows fire and block correctly            | PR dry runs           |

---

## 2. Manufacturing Flow Test Scenarios

### Test A — Extraction MO (BOM 10)
**Objective:** Verify 1,000 kg SoyaBean → 140 kg Crude Oil + 840 kg Soya Cake

Steps:
1. Create MO: product=Crude Soya Oil, qty=140 kg, BOM=10
2. Confirm MO
3. Reserve components — verify SoyaBean reserves from `Famoil/Stock/RM Warehouse`
4. Complete work orders: Cleaning → Extrusion → Pressing → Filtration → Bottling
5. Validate MO
6. Verify: Crude Soya Oil arrives in `Famoil/Stock/Crude Oil Tank 1` (putaway)
7. Verify: Soya Cake arrives in `Famoil/Stock/FG Warehouse` (putaway)
8. Check cost layer: Crude Oil ~₦3,451/kg, Soya Cake ~₦383/kg

Expected failures that should be blocked:
- MO with insufficient SoyaBean → `mrp_component_availability_check` should block

### Test B — Refining MO (BOM 15)
**Objective:** Verify 140 kg Crude Oil → 135 kg Refined Oil + 5 kg SoapStock

Steps:
1. Create MO: product=Refined Soya Oil, qty=135 kg, BOM=15
2. Confirm + reserve — verify Crude Oil reserves from `Crude Oil Tank 1`
3. Complete work orders: Neutralization → Bleaching → Deodorization → Final Filtration
4. Validate MO
5. Verify: Refined Soya Oil in `Refined Oil Tank 1` (putaway)
6. Verify: SoapStock in `Soapstock Tank` (putaway)

### Test C — Tank Restriction Module
**Objective:** Verify Crude Oil Tanks reject non-crude-oil products

Steps:
1. Create internal transfer: any product (NOT Crude Soya Oil) → Crude Oil Tank 1
2. Validate the transfer
3. Expected: `UserError` raised with restriction message
4. Then create transfer: Crude Soya Oil → Crude Oil Tank 1
5. Expected: transfer validates successfully

---

## 3. Costing Validation Test Cases

| Test Case | Expected Result | Tolerance |
|-----------|-----------------|-----------|
| BOM 10 batch cost | ₦805,167 (₦710k RM + ₦95,167 overhead) | ±₦1,000 |
| Crude Soya Oil unit cost | ₦3,451/kg | ±₦50 |
| Soya Cake unit cost | ₦383/kg | ±₦10 |
| Production Waste unit cost | ₦0/kg | exact |

**Manual verification formula:**
```
Total batch = (1000 × SoyaBean standard_price) + sum(work_center_overhead)
Crude Oil cost = Total × 60% ÷ 140 kg
Soya Cake cost = Total × 40% ÷ 840 kg
```

---

## 4. UAT Checklist

- [ ] Store Keeper can create and receive a purchase order for SoyaBean
- [ ] Store Keeper can create an internal transfer from RM Warehouse
- [ ] Plant Operator can create and confirm a manufacturing order
- [ ] Plant Operator can complete work orders in sequence
- [ ] Plant Operator cannot validate MO with insufficient stock
- [ ] QC Officer can move stock to/from Quality Control location
- [ ] Accountant can view inventory valuation report
- [ ] Accountant can reconcile a vendor bill
- [ ] Manager can view manufacturing cost analysis

---

## 5. Regression Risk Assessment

When making configuration changes, assess these regression risks:

| Change Type                  | Risk Areas to Test                                     |
|-----------------------------|--------------------------------------------------------|
| BOM modification             | Cost allocation, component reservation, putaway routing |
| Work center rate change      | All MO cost calculations using that work center         |
| Location restructure         | All putaway rules, operation type source/destination    |
| Custom module update         | Module's override function, edge cases                  |
| Product category change      | Cost method, accounting entries, valuation reports      |

---

## 6. Shell-Based Test Scripts

```bash
# Run existing tests from repo root
python test_component_check.py
python test_soya.py
```

> These scripts test via the Odoo shell (not pytest). Run only against Famoil DB.

New test scripts should be created under `tests/` directory.
