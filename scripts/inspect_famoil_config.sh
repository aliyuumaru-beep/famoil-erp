#!/usr/bin/env bash
# =============================================================================
# inspect_famoil_config.sh — Read-only inspection of FamOil Odoo instance
# =============================================================================
# Prints a structured report of:
#   - Process state (Odoo running?)
#   - Database list
#   - Installed modules (count)
#   - Warehouses
#   - Active locations (FamOilWH)
#   - Products (FamOil categories)
#   - BOMs and byproducts
#   - Work centers
#   - Custom addons
#   - Filestore size
#
# READ-ONLY. Makes no changes to any file or database.
#
# Usage:
#   bash /Users/mac/odoo17/scripts/inspect_famoil_config.sh
#   bash /Users/mac/odoo17/scripts/inspect_famoil_config.sh > report.txt
# =============================================================================

set -uo pipefail

DB_USER="odoo"
DB_NAME="Famoil"
ODOO_ROOT="/Users/mac/odoo17"
FILESTORE="/Users/mac/Library/Application Support/Odoo/filestore/${DB_NAME}"

SEP="------------------------------------------------------------"

echo "============================================================"
echo " FamOil Instance Inspection — $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# ---------------------------------------------------------------------------
# 1. Odoo process
# ---------------------------------------------------------------------------
echo ""
echo "=== ODOO PROCESS ==="
ps aux | grep "odoo-bin\|odoo/odoo-bin" | grep -v grep || echo "(not running)"

# ---------------------------------------------------------------------------
# 2. Databases
# ---------------------------------------------------------------------------
echo ""
echo "=== DATABASES ==="
psql -U "${DB_USER}" -l 2>/dev/null | grep -E "Name|---|\bFam|\bOdoo|\bodoo|\baedc" || echo "Cannot connect to PostgreSQL"

# ---------------------------------------------------------------------------
# 3. Installed modules count
# ---------------------------------------------------------------------------
echo ""
echo "=== INSTALLED MODULES (count) ==="
psql -U "${DB_USER}" -d "${DB_NAME}" -t -c \
  "SELECT count(*) || ' modules installed' FROM ir_module_module WHERE state='installed';" 2>/dev/null || echo "Query failed"

# ---------------------------------------------------------------------------
# 4. Warehouses
# ---------------------------------------------------------------------------
echo ""
echo "=== WAREHOUSES ==="
psql -U "${DB_USER}" -d "${DB_NAME}" -c \
  "SELECT id, name, code FROM stock_warehouse ORDER BY id;" 2>/dev/null

# ---------------------------------------------------------------------------
# 5. Active locations — FamOilWH (CW)
# ---------------------------------------------------------------------------
echo ""
echo "=== LOCATIONS (FamOilWH / CW) ==="
psql -U "${DB_USER}" -d "${DB_NAME}" -c \
  "SELECT id, complete_name, usage FROM stock_location WHERE complete_name LIKE 'CW%' AND active=true ORDER BY complete_name;" 2>/dev/null

# ---------------------------------------------------------------------------
# 6. FamOil products
# ---------------------------------------------------------------------------
echo ""
echo "=== PRODUCTS (FamOil categories) ==="
psql -U "${DB_USER}" -d "${DB_NAME}" -c \
  "SELECT pt.name->>'en_US' AS product, pc.complete_name AS category, pt.detailed_type
   FROM product_template pt
   JOIN product_category pc ON pt.categ_id=pc.id
   WHERE pt.active=true AND pc.complete_name LIKE '%FamOil%'
   ORDER BY pc.complete_name, pt.name->>'en_US';" 2>/dev/null

# ---------------------------------------------------------------------------
# 7. BOMs
# ---------------------------------------------------------------------------
echo ""
echo "=== BILLS OF MATERIALS ==="
psql -U "${DB_USER}" -d "${DB_NAME}" -c \
  "SELECT mb.id, pt.name->>'en_US' AS product, mb.product_qty, u.name->>'en_US' AS uom, mb.type
   FROM mrp_bom mb
   JOIN product_template pt ON mb.product_tmpl_id=pt.id
   JOIN uom_uom u ON mb.product_uom_id=u.id
   WHERE mb.active=true ORDER BY mb.id;" 2>/dev/null

echo ""
echo "--- BOM 10 Components ---"
psql -U "${DB_USER}" -d "${DB_NAME}" -c \
  "SELECT pt.name->>'en_US' AS component, mbl.product_qty, u.name->>'en_US' AS uom
   FROM mrp_bom_line mbl
   JOIN product_product pp ON mbl.product_id=pp.id
   JOIN product_template pt ON pp.product_tmpl_id=pt.id
   JOIN uom_uom u ON mbl.product_uom_id=u.id
   WHERE mbl.bom_id=10;" 2>/dev/null

echo ""
echo "--- BOM 10 Byproducts ---"
psql -U "${DB_USER}" -d "${DB_NAME}" -c \
  "SELECT pt.name->>'en_US' AS byproduct, mbp.product_qty, u.name->>'en_US' AS uom, mbp.cost_share
   FROM mrp_bom_byproduct mbp
   JOIN product_product pp ON mbp.product_id=pp.id
   JOIN product_template pt ON pp.product_tmpl_id=pt.id
   JOIN uom_uom u ON mbp.product_uom_id=u.id
   WHERE mbp.bom_id=10;" 2>/dev/null

# ---------------------------------------------------------------------------
# 8. Work centers
# ---------------------------------------------------------------------------
echo ""
echo "=== WORK CENTERS ==="
psql -U "${DB_USER}" -d "${DB_NAME}" -c \
  "SELECT id, name, active, costs_hour, default_capacity FROM mrp_workcenter ORDER BY id;" 2>/dev/null

# ---------------------------------------------------------------------------
# 9. Custom addons
# ---------------------------------------------------------------------------
echo ""
echo "=== CUSTOM ADDONS ==="
for d in "${ODOO_ROOT}/custom_addons"/*/; do
  addon=$(basename "$d")
  version=$(python3 -c "import ast; m=ast.literal_eval(open('${d}__manifest__.py').read()); print(m.get('version','?'))" 2>/dev/null || echo "?")
  echo "  ${addon} (v${version})"
done

# ---------------------------------------------------------------------------
# 10. Filestore size
# ---------------------------------------------------------------------------
echo ""
echo "=== FILESTORE ==="
if [ -d "${FILESTORE}" ]; then
  du -sh "${FILESTORE}"
else
  echo "Filestore not found at: ${FILESTORE}"
fi

# ---------------------------------------------------------------------------
# 11. odoo.conf (no passwords)
# ---------------------------------------------------------------------------
echo ""
echo "=== ODOO.CONF (passwords hidden) ==="
grep -v -E "password|passwd|pwd|secret" "${ODOO_ROOT}/odoo/odoo.conf" 2>/dev/null || echo "Not found"

echo ""
echo "============================================================"
echo " Inspection complete — no changes made."
echo "============================================================"
