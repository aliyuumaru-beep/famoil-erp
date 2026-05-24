"""
Process MO: 135 kg Refined Soya Oil (BOM 15)
Steps:
  1. Inventory adjustment — add chemicals to RM Warehouse
  2. Create MO from BOM 15
  3. Confirm + reserve
  4. Mark as done (immediate production)
"""

import sys

# ── 0. Switch to FamOil FTZ company context ──────────────────────────────────
env = env(context=dict(env.context, allowed_company_ids=[2], company_id=2))
print(f"Company context: {env.company.name}")

# ── 1. Locations & products ──────────────────────────────────────────────────

rm_location = env['stock.location'].browse(138)  # Famoil/Stock/RM Warehouse
assert rm_location.exists(), "RM Warehouse location 138 not found"

bleaching_earth = env['product.product'].browse(128)
caustic_soda    = env['product.product'].browse(129)
citric_acid     = env['product.product'].browse(130)
refined_oil     = env['product.product'].search(
    [('product_tmpl_id.name', '=', 'Refined Soya Oil')], limit=1)
bom             = env['mrp.bom'].browse(15)
picking_type    = env['stock.picking.type'].browse(24)  # Manufacturing — FamOilWH

assert bleaching_earth.exists(), "Bleaching Earth (128) not found"
assert caustic_soda.exists(),    "Caustic Soda (129) not found"
assert citric_acid.exists(),     "Citric Acid (130) not found"
assert refined_oil.exists(),     "Refined Soya Oil product not found"
assert bom.exists(),             "BOM 15 not found"

print("Products and location verified.")

# ── 2. Skip chemical stock adjustment ───────────────────────────────────────
# Bleaching Earth, Caustic Soda, Citric Acid are type=consu (consumables).
# Odoo does not track quants for consumables — they are always considered
# available and consumed directly in production without stock moves.
print("Chemicals are consumables — no inventory adjustment needed.")

# ── 3. Create MO ─────────────────────────────────────────────────────────────

uom_kg = env['uom.uom'].search([('name', '=', 'kg'), ('category_id.name', '=', 'Weight')], limit=1)

mo = env['mrp.production'].create({
    'product_id':       refined_oil.id,
    'bom_id':           bom.id,
    'product_qty':      135.0,
    'product_uom_id':   uom_kg.id,
    'company_id':       2,
    'picking_type_id':  picking_type.id,
})
print(f"MO created: {mo.name}  (id={mo.id})")

# ── 4. Confirm ───────────────────────────────────────────────────────────────

mo.action_confirm()
print(f"MO confirmed. State: {mo.state}")

# ── 5. Reserve components ────────────────────────────────────────────────────

mo.action_assign()
print(f"Components reserved. Availability: {mo.reservation_state}")

# Check reservation
for move in mo.move_raw_ids:
    avail = move.quantity
    needed = move.product_uom_qty
    status = "OK" if avail >= needed else f"SHORT ({avail}/{needed})"
    print(f"  {move.product_id.name}: {needed} kg — {status}")

# ── 6. Set qty_producing and mark done ───────────────────────────────────────

# ── 6a. Complete work orders ─────────────────────────────────────────────────

for wo in mo.workorder_ids.sorted('id'):
    if wo.state == 'done':
        continue
    if wo.state == 'pending':
        # pending WOs unlock once previous is done; force to ready
        wo.state = 'ready'
    wo.button_start()
    wo.qty_producing = mo.qty_producing or mo.product_qty
    wo.button_finish()
    print(f"  Work order '{wo.name}' — done")

env.cr.commit()

# ── 6b. Set producing qty and component done quantities ──────────────────────

mo.qty_producing = 135.0

for move in mo.move_raw_ids:
    move.quantity = move.product_uom_qty

for move in mo.move_byproduct_ids:
    move.quantity = move.product_uom_qty

env.cr.commit()

# Mark as done
result = mo.button_mark_done()
env.cr.commit()

# Handle wizard chain until MO is done
def handle_wizard(res):
    if not isinstance(res, dict) or not res.get('res_model'):
        return
    model = res['res_model']
    print(f"Wizard triggered: {model}")
    wizard = env[model].browse(res['res_id'])
    if model == 'mrp.consumption.warning':
        # action_confirm internally calls button_mark_done(skip_consumption=True)
        next_res = wizard.action_confirm()
        handle_wizard(next_res)
    elif model == 'mrp.immediate.production':
        handle_wizard(wizard.action_immediate_production())
    elif model == 'mrp.production.backorder':
        wizard.action_close_mo()
    else:
        print(f"Unhandled wizard: {model}")

handle_wizard(result)
env.cr.commit()

print(f"\nDone. MO state: {mo.state}")
print(f"MO name: {mo.name}")

# ── 7. Summary ───────────────────────────────────────────────────────────────

print("\n── Component consumption ─────────────────────")
for move in mo.move_raw_ids:
    print(f"  {move.product_id.name}: {move.quantity} kg consumed")

print("\n── Outputs ───────────────────────────────────")
for move in mo.move_finished_ids:
    print(f"  {move.product_id.name}: {move.quantity} kg produced")
