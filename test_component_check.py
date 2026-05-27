import os
import xmlrpc.client

url = os.environ.get('ODOO_URL', 'http://localhost:8069')
db = os.environ.get('ODOO_DB', 'Famoil')
username = os.environ.get('ODOO_USER', 'admin')
password = os.environ.get('ODOO_PASSWORD', 'test_password')

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def call(model, method, *args, **kwargs):
    return models.execute_kw(db, uid, password, model, method, list(args), kwargs)

mo_id = 1  # WH/MO/00001 from previous run

# Show current component state
raw_moves = call('stock.move', 'search_read',
    [('raw_material_production_id', '=', mo_id), ('state', 'not in', ['done', 'cancel'])],
    fields=['product_id', 'product_uom_qty', 'quantity', 'product_uom'])

print("Components:")
for m in raw_moves:
    status = "OK" if m['quantity'] >= m['product_uom_qty'] else "SHORT"
    uom = m['product_uom'][1]
    print(f"  [{status}] {m['product_id'][1]}: required={m['product_uom_qty']} {uom}, reserved={m['quantity']} {uom}")

# TEST 1: Try to mark done — should be blocked
print("\n--- TEST 1: Mark as done with insufficient components ---")
try:
    call('mrp.production', 'button_mark_done', [mo_id])
    print("[FAIL] No error raised — module not blocking!")
except xmlrpc.client.Fault as e:
    msg = e.faultString
    print("Full fault message:")
    print(msg)
    print()
    if 'Cannot process' in msg or 'sufficient stock' in msg or 'components do not have' in msg:
        print("[PASS] Correctly blocked by mrp_component_availability_check")
    elif 'UserError' in msg:
        print("[PASS] UserError raised (check message above for our custom text)")
    else:
        print("[INFO] Different error — see message above")
