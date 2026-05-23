# Industry Variation Matrix
# FamOil ERP Framework — Agro-Processing Edition

_Version: 1.0 | Date: 2026-05-22 | Base: Odoo 17 Community_

---

## Purpose

This matrix guides an implementer in estimating configuration effort and identifying departure points when adapting the FamOil soybean oil template to other agro-processing verticals.

Assumptions are flagged with **[ASSUMPTION]**.

---

## Common Foundation — What Always Stays

The following elements are reusable across all industries without modification:

| Element | Reuse Level |
|---|---|
| Core modules (mrp, stock, account, purchase, sale) | Full |
| BOM structure (components → main output + byproducts) | Full |
| `cost_share` byproduct allocation mechanism | Full |
| Work center + routing concept | Full |
| Average / FIFO costing methods | Full |
| Stock location hierarchy (RM → WIP → FG) | Full |
| Lot/serial tracking framework | Full |
| Purchase → GRN → inventory flow | Full |
| Manufacturing Order lifecycle | Full |
| Tank restriction custom module (generalised to any product/location pair) | Adaptable |
| Nigerian compliance layer (VAT, WHT chart of accounts) | Full |
| Backup, inspection, and deployment scripts | Full |

---

## Industry 1 — Soybean Oil Mill (Baseline Template)

This is the documented FamOil implementation. All other entries are deltas from this baseline.

| Dimension | Detail |
|---|---|
| Main input | SoyaBean, 1,000 kg/batch |
| Main output | Crude Soya Oil (~14% yield) |
| Byproducts | Soya Cake (~84%), Production Waste (~1%) |
| Work centers | Cleaning → Extrusion → Pressing → Filtration → Packaging |
| Storage | Bulk tanks (oil), bag stock (cake) |
| Costing | Average (RM), FIFO (FG), byproduct cost_share |
| Reconfiguration effort | Baseline — 0 additional effort |

---

## Industry 2 — Palm Oil Mill

### What Stays the Same
- MRP module, BOM structure, work center concept
- Purchase and GRN workflow
- Cost allocation via `cost_share`
- Chart of accounts structure

### What Changes
| Element | Change |
|---|---|
| Raw material | Fresh Fruit Bunches (FFB) — perishable, 24–48 hr processing window |
| Process stages | Sterilisation → Threshing → Digestion → Pressing → Clarification → Drying → Kernel Recovery |
| Dual product streams | CPO (main stream) + Palm Kernel (secondary stream, goes to kernel press) |
| Two separate BOMs needed | BOM A: FFB → CPO + Fibre + Shell + Kernel Nuts; BOM B: Kernel Nuts → Palm Kernel Oil + Kernel Cake |
| Byproducts | Palm fibre (fuel), shell (fuel/sale), empty fruit bunches (EFB, compost) |
| Storage | Heated CPO tanks (maintain 40–50°C to prevent solidification) **[ASSUMPTION: electric or steam heating]** |

### Yield Logic
```
FFB input: 1,000 kg
CPO yield:        ~200 kg   (20%)   [ASSUMPTION: varies 18–22% by variety]
Palm Kernel Nuts: ~60 kg    (6%)
Palm Fibre:       ~140 kg   (14%)
Shell:            ~60 kg    (6%)
EFB:              ~230 kg   (23%)
Process water/loss: ~310 kg (31%)
```

### Work Center Differences
| FamOil (Soybean) | Palm Oil Mill |
|---|---|
| Cleaning Section | Steriliser Bay |
| Extrusion Section | Thresher |
| Pressing Section | Digester + Screw Press |
| Filtration Section | Clarifier + Vacuum Dryer |
| Packaging Section | Kernel Recovery + Packaging |

### Storage Differences
- CPO tanks require temperature control — add location attribute or note in warehouse config
- Kernel nuts need dry storage, separate location
- EFB/fibre often stored at mill yard — may not need Odoo tracking

### Estimated Reconfiguration Effort
| Area | Effort |
|---|---|
| Two new BOMs (FFB and Kernel) | 1 day |
| 5 new work centers | 0.5 day |
| Heated tank location notes/restrictions | 0.5 day |
| New product master (FFB, EFB, Fibre, Shell, Kernel Cake) | 0.5 day |
| Testing + validation | 1 day |
| **Total** | **~3.5 days** |

**Reconfiguration Effort: MEDIUM**

---

## Industry 3 — Feed Mill

### What Stays the Same
- MRP, BOM, work center framework
- Purchase and stock flows
- Chart of accounts

### What Changes
| Element | Change |
|---|---|
| Raw materials | 5–10 ingredients per formula (maize, soya meal, wheat bran, premix, fishmeal, salt, limestone, etc.) |
| No significant byproducts | Feed milling is a blending operation — near-zero byproduct cost allocation needed |
| Multiple finished SKUs | Broiler Starter, Grower, Finisher, Layer Mash, Pig Feed, Catfish Feed — each needs its own BOM |
| Formulation is recipe-driven | BOM % ratios must be maintained precisely; any ingredient substitution changes cost significantly |
| Micro-ingredient handling | Premix quantities are tiny (e.g., 2.5 kg per tonne) — UoM precision important |
| Packaging variants | Same product in 25 kg vs 50 kg bags = different finished goods SKUs |

### Yield Logic
```
Feed milling is near 100% conversion — almost no output loss.
Input: 1,000 kg multi-ingredient mix
Output: ~980–995 kg finished feed (loss = moisture + dust)
No byproducts with commercial value in typical feed mill.
```
**[ASSUMPTION: No pelleting moisture loss tracked — add if client has pellet mill]**

### Work Center Differences
| FamOil (Soybean) | Feed Mill |
|---|---|
| Cleaning Section | Intake & Pre-cleaning |
| Extrusion Section | Hammer Mill / Grinding |
| Pressing Section | Mixer (horizontal ribbon or paddle) |
| Filtration Section | Pellet Mill (if applicable) |
| Packaging Section | Bagging & Sealing |

### Storage Differences
- Multiple raw material silos (maize, soya, wheat) — each needs a dedicated location
- Premix stored separately (temperature-sensitive, short shelf life)
- Finished goods by SKU — separate bins per feed type

### Estimated Reconfiguration Effort
| Area | Effort |
|---|---|
| 6–10 product BOMs (one per feed type) | 1.5 days |
| Ingredient product masters (~15 items) | 0.5 day |
| UoM precision review (micro-ingredients) | 0.5 day |
| Location structure (multiple silos) | 0.5 day |
| Testing + validation | 1 day |
| **Total** | **~4 days** |

**Reconfiguration Effort: MEDIUM**

---

## Industry 4 — Rice Mill

### What Stays the Same
- MRP, BOM, work center, stock flows
- Byproduct cost_share mechanism (multiple valuable byproducts)
- Chart of accounts

### What Changes
| Element | Change |
|---|---|
| Raw material | Paddy rice (seasonal, bulk procurement) |
| Multiple output grades | Whole milled rice (Grade A), broken rice, rice bran, rice husk |
| Grade management | Same BOM but needs quality control routing or multi-step BOM |
| Bran is high-value | Rice bran (for bran oil extraction) — needs separate storage and pricing |
| Husk management | Rice husk = boiler fuel or sold in bulk — low unit value, high volume |
| Moisture content | Paddy moisture affects yield — tracking lot-level moisture is ideal **[ASSUMPTION: manual entry]** |

### Yield Logic
```
Paddy input: 1,000 kg  (12–14% moisture)
Whole milled rice:  ~650 kg   (65%)   [ASSUMPTION: varies 60–72% by variety]
Broken rice:        ~50 kg    (5%)
Rice bran:          ~100 kg   (10%)
Rice husk:          ~200 kg   (20%)
```

### Work Center Differences
| FamOil (Soybean) | Rice Mill |
|---|---|
| Cleaning Section | Pre-cleaner + De-stoner |
| Extrusion Section | Husker / Huller |
| Pressing Section | Paddy Separator + Whitener |
| Filtration Section | Polisher + Color Sorter |
| Packaging Section | Grader + Bagging |

### Storage Differences
- Paddy silos (bulk, large capacity) — separate location from milled rice
- Milled rice bins by grade
- Bran stored separately (goes rancid quickly — track lot + date)
- Husk yard — may not need precise Odoo location tracking

### Estimated Reconfiguration Effort
| Area | Effort |
|---|---|
| New BOM with 4 outputs | 0.5 day |
| 6 new product masters (paddy, whole rice, broken, bran, husk, flour) | 0.5 day |
| Location structure (silos, grade bins, bran store) | 0.5 day |
| Lot tracking setup for paddy (seasonal batches) | 0.5 day |
| Testing + validation | 1 day |
| **Total** | **~3 days** |

**Reconfiguration Effort: LOW–MEDIUM**

---

## Industry 5 — Groundnut Oil Mill

### What Stays the Same
- Entire soybean oil template — this is the closest industry match
- BOM structure, work centers, storage, costing all transfer directly

### What Changes
| Element | Change |
|---|---|
| Raw material | Groundnuts (shelled or unshelled) |
| Shelling stage | If purchasing unshelled, add a shelling work center and shell as byproduct |
| Higher oil yield | Groundnut oil yield ~38–45% vs soybean ~14% — update BOM quantities |
| Roasting stage | Some mills roast before pressing (cold press mills skip this) |
| Output quality tiers | Cold-pressed vs hot-pressed = different product masters and price points |
| Cake value | Groundnut cake is a premium animal feed ingredient (higher protein than soya cake) |

### Yield Logic
```
Shelled groundnut input: 1,000 kg
Groundnut oil:  ~380–450 kg   (38–45%)   [ASSUMPTION: expeller press, not solvent]
Groundnut cake: ~540–600 kg   (54–60%)
Waste/moisture: ~10–20 kg     (1–2%)
```

### Work Center Differences
| FamOil (Soybean) | Groundnut Oil Mill |
|---|---|
| Cleaning Section | Cleaning + Shelling (if unshelled) |
| Extrusion Section | Roaster (optional) |
| Pressing Section | Expeller Press |
| Filtration Section | Filter Press |
| Packaging Section | Packaging |

### Storage Differences
- Nearly identical to soybean — bulk tanks for oil, bagged cake
- Unshelled groundnuts need larger RM storage footprint

### Estimated Reconfiguration Effort
| Area | Effort |
|---|---|
| Update BOM quantities (yield change) | 0.5 day |
| New product masters (groundnut, G/nut oil, G/nut cake) | 0.5 day |
| Optional: shelling work center + BOM stage | 0.5 day |
| Testing + validation | 0.5 day |
| **Total** | **~2 days** |

**Reconfiguration Effort: LOW** (nearest to baseline)

---

## Industry 6 — Shea Butter Oil Mill

### What Stays the Same
- BOM, work center, byproduct, and costing framework
- Purchase flow, stock locations concept
- Chart of accounts

### What Changes
| Element | Change |
|---|---|
| Raw material | Shea nuts (kernels, after cracking and drying) |
| Process type | Traditional wet extraction OR industrial cold/hot press — very different BOMs |
| Temperature-sensitive output | Shea butter melts at ~36°C — storage location must note temperature requirement |
| Export quality grades | Grade A (refined/deodorised), Grade B (semi-refined), Grade C (crude) — each is a separate product master |
| Long processing time | Traditional method: multi-day batch — `time_cycle_manual` values will be large |
| Low-value byproduct | Shea cake/meal (low protein, limited market) |
| Water usage | Wet extraction uses large volumes of water — not tracked in Odoo but relevant for utility cost |

### Yield Logic — Industrial Cold Press
```
Shea kernel input: 1,000 kg
Shea butter:  ~200–500 kg   (20–50%)   [ASSUMPTION: varies widely by extraction method]
Shea cake:    ~450–700 kg
Moisture/loss: ~50–100 kg
```
**[ASSUMPTION: Wide yield range — implementer must get client's actual figures before entering BOM]**

### Work Center Differences
| FamOil (Soybean) | Shea Butter Mill (Industrial) |
|---|---|
| Cleaning Section | Sorting + Cracking + Winnowing |
| Extrusion Section | Roaster / Cooker |
| Pressing Section | Cold Press / Expeller |
| Filtration Section | Centrifuge / Filter |
| Packaging Section | Filling + Drumming |

### Storage Differences
- Shea butter stored in drums or totes (not open tanks) at ambient or slightly cool temperature
- Grade separation is critical — A, B, C must never mix; dedicated locations per grade
- Export units: 200L drums — packaging BOM may be needed

### Estimated Reconfiguration Effort
| Area | Effort |
|---|---|
| New BOMs (1 per extraction method) | 1 day |
| Product masters (nuts, grades A/B/C, cake) | 0.5 day |
| Location structure (grade-separated storage) | 0.5 day |
| Export packaging BOM (drums, labels) | 0.5 day |
| Testing + validation | 1 day |
| **Total** | **~3.5 days** |

**Reconfiguration Effort: MEDIUM**

---

## Industry 7 — FMCG Food Processing

### What Stays the Same
- Core Odoo modules
- Purchase, GRN, invoice flows
- Chart of accounts skeleton

### What Changes
| Element | Change |
|---|---|
| SKU proliferation | Dozens to hundreds of finished goods (flavours, sizes, formats) — each needs a BOM |
| Packaging complexity | Primary + secondary + tertiary packaging all in BOM |
| Shelf life / expiry | Lot tracking with removal dates mandatory — configure `product.tracking = lot` and `use_expiration_date = True` |
| Quality control | Incoming QC on ingredients + outgoing QC on finished goods — may require `quality` module |
| Regulatory labelling | NAFDAC number per SKU — store as product attribute or internal reference |
| Demand variability | Sales orders drive MRP scheduling; replenishment rules needed |
| Multiple production lines | Work center capacity planning becomes critical |
| Recipe scaling | BOMs likely at 100 kg or 1,000 unit scale — choose consistent UoM base |

### Yield Logic
```
[ASSUMPTION: Highly variable — no universal formula]
Typical range: 85–98% output/input ratio depending on product type.
Moisture loss, rejects, and rework must be measured per product line.
```

### Work Center Differences
Highly variable. Common pattern:
- Intake + QC
- Mixing / Blending / Cooking
- Forming / Filling / Extruding
- Cooling / Drying / Baking
- Packaging Line 1, 2, N

### Storage Differences
- Controlled-temperature storage for perishable ingredients
- FEFO (First Expiry First Out) mandatory — requires lot tracking
- Finished goods warehouse with expiry date management

### Estimated Reconfiguration Effort
| Area | Effort |
|---|---|
| Product master setup (high volume) | 3–5 days |
| BOM creation (per SKU) | 2–4 days |
| Lot + expiry date configuration | 1 day |
| Quality module setup | 1–2 days |
| Reorder rules and replenishment | 1 day |
| Testing + validation | 2–3 days |
| **Total** | **~10–16 days** |

**Reconfiguration Effort: HIGH**

---

## Summary Reconfiguration Matrix

| Industry | Effort | BOM Complexity | Byproduct Complexity | Storage Complexity | Closest Template Match |
|---|---|---|---|---|---|
| Soybean Oil Mill | Baseline | Low | Medium | Medium | — |
| Groundnut Oil Mill | LOW (~2d) | Low | Low | Medium | Soybean (direct) |
| Rice Mill | LOW–MED (~3d) | Medium | Medium | Medium | Soybean |
| Palm Oil Mill | MEDIUM (~3.5d) | High | High | High | Soybean (adapted) |
| Shea Butter Oil Mill | MEDIUM (~3.5d) | Medium | Low | Medium | Soybean (adapted) |
| Feed Mill | MEDIUM (~4d) | High (multi-ingredient) | None | Medium | New BOM set |
| FMCG Food Processing | HIGH (~10–16d) | Very High | Low | High | Partial reuse only |

---

_All effort estimates are per experienced Odoo implementer familiar with this framework. Add 50–100% for first-time implementers or novel industry variants._
