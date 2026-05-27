import os
import xmlrpc.client

url = os.environ.get('ODOO_URL', 'http://localhost:8069')
db = os.environ.get('ODOO_DB', 'Famoil')
username = os.environ.get('ODOO_USER', 'admin')
password = os.environ.get('ODOO_PASSWORD', '')

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

COMPANY_ID = 2  # FamOil FTZ
CTX = {'allowed_company_ids': [COMPANY_ID], 'company_id': COMPANY_ID}

def call(model, method, *args, **kwargs):
    kwargs.setdefault('context', CTX)
    return models.execute_kw(db, uid, password, model, method, list(args), kwargs)

# ── Find Crude Soya Oil ────────────────────────────────────────────────────────
soya = call('product.product', 'read', [111],
    fields=['id', 'name', 'qty_available', 'uom_id'])[0]
on_hand = soya['qty_available']
print(f"Crude Soya Oil: {on_hand} {soya['uom_id'][1]} on hand")

# ── Find a finished product accessible to FamOil FTZ ──────────────────────────
fin_products = call('product.product', 'search_read',
    [('type', '=', 'product'), ('id', '!=', 111)],
    fields=['id', 'name', 'product_tmpl_id'], limit=1)

if not fin_products:
    print("No finished product found.")
    exit(1)

fin = fin_products[0]
print(f"Finished product: {fin['name']} (id={fin['id']})")

# ── Find manufacturing operation type for FamOil FTZ ─────────────────────────
pick_types = call('stock.picking.type', 'search_read',
    [('code', '=', 'mrp_operation'), ('company_id', '=', COMPANY_ID)],
    fields=['id', 'name', 'company_id'], limit=1)

if not pick_types:
    print("No manufacturing operation type found for FamOil FTZ.")
    exit(1)

pick_type = pick_types[0]
print(f"Operation type: {pick_type['name']} (id={pick_type['id']})")

# ── Create BOM requiring MORE crude soya oil than on hand ─────────────────────
required_qty = on_hand + 500  # guarantee a shortage
bom_id = call('mrp.bom', 'create', {
    'product_id': fin['id'],
    'product_tmpl_id': fin['product_tmpl_id'][0],
    'product_qty': 1.0,
    'company_id': COMPANY_ID,
    'picking_type_id': pick_type['id'],
    'bom_line_ids': [(0, 0, {
        'product_id': 111,  # Crude Soya Oil
        'product_qty': required_qty,
    })]
})
print(f"Created BOM id={bom_id} requiring {required_qty} kg Crude Soya Oil (only {on_hand} kg on hand)")

# ── Create and confirm MO ──────────────────────────────────────────────────────
mo_id = call('mrp.production', 'create', {
    'product_id': fin['id'],
    'product_qty': 1.0,
    'bom_id': bom_id,
    'company_id': COMPANY_ID,
    'picking_type_id': pick_type['id'],
})
call('mrp.production', 'action_confirm', [mo_id])
mo = call('mrp.production', 'read', [mo_id],
    fields=['name', 'state', 'reservation_state'])[0]
print(f"\nCreated MO: {mo['name']} | state={mo['state']} | reservation={mo['reservation_state']}")

# ── Show component moves ───────────────────────────────────────────────────────
raw_moves = call('stock.move', 'search_read',
    [('raw_material_production_id', '=', mo_id), ('state', 'not in', ['done', 'cancel'])],
    fields=['product_id', 'product_uom_qty', 'quantity', 'product_uom'])

print("\nComponents:")
for m in raw_moves:
    status = "OK" if m['quantity'] >= m['product_uom_qty'] else "SHORT"
    uom = m['product_uom'][1]
    print(f"  [{status}] {m['product_id'][1]}: required={m['product_uom_qty']} {uom}, reserved={m['quantity']} {uom}")

# ── TEST 1: Mark as done — should be blocked ───────────────────────────────────
print("\n--- TEST 1: Attempt mark as done (components insufficient) ---")
try:
    call('mrp.production', 'button_mark_done', [mo_id])
    print("[FAIL] No error raised!")
except xmlrpc.client.Fault as e:
    msg = e.faultString
    if 'Cannot process' in msg or 'sufficient stock' in msg:
        print("[PASS] Correctly blocked:")
        for line in msg.strip().split('\n'):
            if line.strip() and 'Traceback' not in line and 'File "/' not in line:
                print(f"  {line.strip()}")
    else:
        print(f"[OTHER ERROR]: {msg[:400]}")

# ── TEST 2: Reserve whatever is available, still short ────────────────────────
print("\n--- TEST 2: Reserve available stock, still attempt mark as done ---")
call('mrp.production', 'action_assign', [mo_id])
raw_after = call('stock.move', 'search_read',
    [('raw_material_production_id', '=', mo_id), ('state', 'not in', ['done', 'cancel'])],
    fields=['product_id', 'product_uom_qty', 'quantity', 'product_uom'])
for m in raw_after:
    uom = m['product_uom'][1]
    print(f"  After reserve: {m['product_id'][1]} reserved={m['quantity']} / required={m['product_uom_qty']} {uom}")

try:
    call('mrp.production', 'button_mark_done', [mo_id])
    print("[FAIL] No error raised — still should be blocked!")
except xmlrpc.client.Fault as e:
    msg = e.faultString
    if 'Cannot process' in msg or 'sufficient stock' in msg:
        print("[PASS] Still blocked — partial reservation is not enough:")
        for line in msg.strip().split('\n'):
            if line.strip() and 'Traceback' not in line and 'File "/' not in line:
                print(f"  {line.strip()}")
    else:
        print(f"[OTHER ERROR]: {msg[:400]}")

print("\nTest complete. MO", mo['name'], "left in confirmed state (not modified).")
