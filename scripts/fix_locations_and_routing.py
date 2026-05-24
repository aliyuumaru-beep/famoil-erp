"""
Complete location and routing corrections for FamOil.

Stock fixes:
  1. Crude Oil Tank 1: zero out -81 kg negative quant
  2. Crude Soya Oil 20 kg (floating in Famoil/Stock) → Crude Oil Tank 1
  3. Crude Soya Oil 179 kg (wrongly in FG Warehouse) → Crude Oil Tank 1
  4. Refined Soya Oil 135 kg (floating in Famoil/Stock) → Refined Oil Tank 1
  5. SoapStock 5 kg (wrongly in Refined Oil Tank 1) → Soapstock Tank

Putaway rules (so future MO outputs route automatically):
  6. Crude Soya Oil arriving at Famoil/Stock → Crude Oil Tank 1
  7. Refined Soya Oil arriving at Famoil/Stock → Refined Oil Tank 1
  8. SoapStock arriving at Famoil/Stock → Soapstock Tank
  9. Soya Cake arriving at Famoil/Stock → FG Warehouse
 10. Refined Soya Oil 5L arriving at Famoil/Stock → FG Warehouse
 11. Refined Soya Oil 25L arriving at Famoil/Stock → FG Warehouse

Operation type sources/destinations are updated via SQL after this script.
"""

env = env(context=dict(env.context, allowed_company_ids=[2], company_id=2))

# ── Locations ────────────────────────────────────────────────────────────────
famoil_stock  = env['stock.location'].browse(152)  # Famoil/Stock (parent)
tank1         = env['stock.location'].browse(141)  # Famoil/Stock/Crude Oil Tank 1
tank2         = env['stock.location'].browse(142)  # Famoil/Stock/Crude Oil Tank 2
refined_tank1 = env['stock.location'].browse(143)  # Famoil/Stock/Refined Oil Tank 1
soapstock_tank= env['stock.location'].browse(149)  # Famoil/Stock/Soapstock Tank
fg_wh         = env['stock.location'].search(
    [('complete_name', '=', 'Famoil/Stock/FG Warehouse')], limit=1)

assert all([famoil_stock, tank1, tank2, refined_tank1, soapstock_tank, fg_wh]), \
    "One or more locations not found"
print(f"Locations verified. FG Warehouse id={fg_wh.id}")

# ── Products ─────────────────────────────────────────────────────────────────
crude_oil    = env['product.product'].search([('name', '=', 'Crude Soya Oil')],   limit=1)
refined_oil  = env['product.product'].search([('name', '=', 'Refined Soya Oil')], limit=1)
soapstock    = env['product.product'].search([('name', '=', 'SoapStock')],         limit=1)
soya_cake    = env['product.product'].search([('name', '=', 'Soya Cake')],         limit=1)
refined_5l   = env['product.product'].search([('name', 'ilike', 'Refined Soya Oil 5L')],  limit=1)
refined_25l  = env['product.product'].search([('name', 'ilike', 'Refined Soya Oil 25L')], limit=1)

assert crude_oil and refined_oil and soapstock and soya_cake, "Core products not found"
print("Products verified.")

SQ = env['stock.quant']

# ── Fix 1: Zero out Crude Oil Tank 1 negative quant ─────────────────────────
SQ._update_available_quantity(crude_oil, tank1, 81.0)
env.cr.commit()
print("Fix 1 ✓ — Crude Oil Tank 1: -81 → 0 kg")

# ── Fix 2: Move 20 kg Crude Soya Oil from Famoil/Stock → Tank 1 ─────────────
SQ._update_available_quantity(crude_oil, famoil_stock, -20.0)
SQ._update_available_quantity(crude_oil, tank1, 20.0)
env.cr.commit()
print("Fix 2 ✓ — 20 kg Crude Soya Oil: Famoil/Stock → Crude Oil Tank 1")

# ── Fix 3: Move 179 kg Crude Soya Oil from FG Warehouse → Tank 1 ────────────
SQ._update_available_quantity(crude_oil, fg_wh, -179.0)
SQ._update_available_quantity(crude_oil, tank1, 179.0)
env.cr.commit()
print("Fix 3 ✓ — 179 kg Crude Soya Oil: FG Warehouse → Crude Oil Tank 1")

# ── Fix 4: Move 135 kg Refined Soya Oil from Famoil/Stock → Refined Tank 1 ──
SQ._update_available_quantity(refined_oil, famoil_stock, -135.0)
SQ._update_available_quantity(refined_oil, refined_tank1, 135.0)
env.cr.commit()
print("Fix 4 ✓ — 135 kg Refined Soya Oil: Famoil/Stock → Refined Oil Tank 1")

# ── Fix 5: Move 5 kg SoapStock from Refined Tank 1 → Soapstock Tank ─────────
SQ._update_available_quantity(soapstock, refined_tank1, -5.0)
SQ._update_available_quantity(soapstock, soapstock_tank, 5.0)
env.cr.commit()
print("Fix 5 ✓ — 5 kg SoapStock: Refined Oil Tank 1 → Soapstock Tank")

# ── Fixes 6–11: Putaway rules ────────────────────────────────────────────────
putaway_rules = [
    (crude_oil,   famoil_stock, tank1,          "Crude Soya Oil → Crude Oil Tank 1"),
    (refined_oil, famoil_stock, refined_tank1,  "Refined Soya Oil → Refined Oil Tank 1"),
    (soapstock,   famoil_stock, soapstock_tank, "SoapStock → Soapstock Tank"),
    (soya_cake,   famoil_stock, fg_wh,          "Soya Cake → FG Warehouse"),
]
if refined_5l:
    putaway_rules.append((refined_5l,  famoil_stock, fg_wh, "Refined Soya Oil 5L → FG Warehouse"))
if refined_25l:
    putaway_rules.append((refined_25l, famoil_stock, fg_wh, "Refined Soya Oil 25L → FG Warehouse"))

PR = env['stock.putaway.rule']
for product, loc_in, loc_out, label in putaway_rules:
    existing = PR.search([
        ('product_id', '=', product.id),
        ('location_in_id', '=', loc_in.id),
        ('company_id', '=', 2),
    ], limit=1)
    if not existing:
        PR.create({
            'product_id': product.id,
            'location_in_id': loc_in.id,
            'location_out_id': loc_out.id,
            'company_id': 2,
        })
        print(f"Putaway ✓ — {label}")
    else:
        existing.write({'location_out_id': loc_out.id})
        print(f"Putaway updated — {label}")

env.cr.commit()
print("\nAll stock fixes and putaway rules complete.")

# ── Final stock snapshot ─────────────────────────────────────────────────────
print("\n── Final stock snapshot ──────────────────────────────────────")
key_products = crude_oil | refined_oil | soapstock | soya_cake
quants = SQ.search([
    ('product_id', 'in', key_products.ids),
    ('location_id.usage', '=', 'internal'),
    ('location_id.company_id', '=', 2),
    ('quantity', '!=', 0),
])
for q in quants.sorted(lambda r: (r.product_id.name, r.location_id.complete_name)):
    print(f"  {q.product_id.name:<25} {q.location_id.complete_name:<40} {q.quantity:>8.2f} kg")
