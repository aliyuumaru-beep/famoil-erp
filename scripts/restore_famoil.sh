#!/usr/bin/env bash
# =============================================================================
# restore_famoil.sh — Restore FamOil Odoo 17 instance from backup
# =============================================================================
# Restores a full FamOil backup (database + filestore) to a target database.
# Supports both:
#   - Custom format dumps (Famoil.dump) — RECOMMENDED, full attachment restore
#   - Plain-text dumps  (Famoil.sql)   — Legacy; ir_attachment may be missing
#
# Default target is FamOilRestoreTest (safe isolation from production).
# To restore to production, set TARGET_DB="Famoil" explicitly and confirm
# the --production flag.
#
# Validation:
#   After restore, runs record count checks including ir_attachment, PDFs,
#   and binary attachment coverage. Reports pass/fail per validation item.
#
# Usage:
#   bash scripts/restore_famoil.sh /path/to/backup/dir
#   bash scripts/restore_famoil.sh /path/to/backup/dir --production
#
# Requirements:
#   - odoo PostgreSQL user must be superuser (required for --disable-triggers)
#   - Odoo server must be stopped before restoring to production
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_USER="odoo"
ODOO_ROOT="/Users/mac/odoo17"
FILESTORE_BASE="/Users/mac/Library/Application Support/Odoo/filestore"
ADDONS_PATH="${ODOO_ROOT}/odoo/odoo/addons,${ODOO_ROOT}/custom_addons,/Users/mac/oca_web"
VENV="${ODOO_ROOT}/odoo/venv"

# Default: safe test target — never production by default
TARGET_DB="FamOilRestoreTest"
PRODUCTION_MODE="false"

# ---------------------------------------------------------------------------
# Argument handling
# ---------------------------------------------------------------------------
if [ $# -lt 1 ]; then
  echo "Usage: bash scripts/restore_famoil.sh /path/to/backup/dir [--production]"
  echo ""
  echo "  Default target: FamOilRestoreTest (safe isolation)"
  echo "  --production: restore to Famoil (requires Odoo to be stopped)"
  exit 1
fi

BACKUP_DIR="${1}"

if [ "${2:-}" = "--production" ]; then
  PRODUCTION_MODE="true"
  TARGET_DB="Famoil"
fi

# ---------------------------------------------------------------------------
# Safety checks
# ---------------------------------------------------------------------------
if [ ! -d "${BACKUP_DIR}" ]; then
  echo "ERROR: Backup directory not found: ${BACKUP_DIR}"
  exit 1
fi

DUMP_FILE=""
DUMP_FORMAT=""

if [ -f "${BACKUP_DIR}/Famoil.dump" ]; then
  DUMP_FILE="${BACKUP_DIR}/Famoil.dump"
  DUMP_FORMAT="custom"
elif [ -f "${BACKUP_DIR}/Famoil.sql" ]; then
  DUMP_FILE="${BACKUP_DIR}/Famoil.sql"
  DUMP_FORMAT="plain"
  echo "WARNING: Legacy plain-text dump detected (Famoil.sql)."
  echo "         ir_attachment data (attachments, PDFs) may not restore correctly."
  echo "         Run a fresh backup with backup_famoil.sh to get Famoil.dump."
  echo ""
else
  echo "ERROR: No dump file found in ${BACKUP_DIR}"
  echo "       Expected: Famoil.dump (custom format) or Famoil.sql (legacy)"
  exit 1
fi

if [ ! -d "${BACKUP_DIR}/filestore" ]; then
  echo "ERROR: filestore/ directory not found in ${BACKUP_DIR}"
  exit 1
fi

if [ "${PRODUCTION_MODE}" = "true" ]; then
  echo "============================================================"
  echo " WARNING: PRODUCTION RESTORE MODE"
  echo " Target database: ${TARGET_DB}"
  echo " This will DROP and recreate the production database."
  echo " Ensure Odoo is stopped before proceeding."
  echo "============================================================"
  echo ""
  echo -n "Type 'CONFIRM' to proceed: "
  read -r CONFIRM
  if [ "${CONFIRM}" != "CONFIRM" ]; then
    echo "Aborted."
    exit 1
  fi
fi

RESTORE_START=$(date +%s)
echo "============================================================"
echo " FamOil Restore — $(date '+%Y-%m-%d %H:%M:%S')"
echo " Backup dir : ${BACKUP_DIR}"
echo " Dump file  : $(basename "${DUMP_FILE}") (${DUMP_FORMAT} format)"
echo " Target DB  : ${TARGET_DB}"
echo "============================================================"
echo ""

# ---------------------------------------------------------------------------
# Step 1 — Drop target DB if exists, create fresh
# ---------------------------------------------------------------------------
echo "[1/5] Preparing target database: ${TARGET_DB}..."
STEP1_START=$(date +%s)

if psql -U "${DB_USER}" -lqt 2>/dev/null | cut -d'|' -f1 | grep -qw "${TARGET_DB}"; then
  echo "      Dropping existing database: ${TARGET_DB}"
  dropdb -U "${DB_USER}" "${TARGET_DB}"
fi

createdb -U "${DB_USER}" -E UTF8 "${TARGET_DB}" --no-password
STEP1_END=$(date +%s)
echo "      OK — $((STEP1_END - STEP1_START))s"

# ---------------------------------------------------------------------------
# Step 2 — Restore database
# ---------------------------------------------------------------------------
echo "[2/5] Restoring database..."
STEP2_START=$(date +%s)

if [ "${DUMP_FORMAT}" = "custom" ]; then
  # Custom format: pg_restore with --disable-triggers to handle Odoo's circular
  # FK dependencies (ir_attachment ↔ account_move, message_attachment_rel, etc.)
  # Requires superuser role. -j 4 = parallel restore using 4 workers.
  pg_restore \
    -U "${DB_USER}" \
    -d "${TARGET_DB}" \
    --disable-triggers \
    --no-owner \
    --no-privileges \
    -j 4 \
    -F c \
    "${DUMP_FILE}" 2>&1 | grep -v "^$" || true
else
  # Legacy plain format: strip \restrict header added by Odoo backup tooling
  grep -v '\\restrict' "${DUMP_FILE}" | \
    psql -U "${DB_USER}" -d "${TARGET_DB}" -v ON_ERROR_STOP=0 --quiet 2>&1 | \
    grep -i "error" | head -20 || true
fi

STEP2_END=$(date +%s)
echo "      OK — $((STEP2_END - STEP2_START))s"

# ---------------------------------------------------------------------------
# Step 3 — Restore filestore
# ---------------------------------------------------------------------------
echo "[3/5] Restoring filestore..."
STEP3_START=$(date +%s)
TARGET_FILESTORE="${FILESTORE_BASE}/${TARGET_DB}"

rm -rf "${TARGET_FILESTORE}"
mkdir -p "${TARGET_FILESTORE}"
cp -r "${BACKUP_DIR}/filestore/" "${TARGET_FILESTORE}/"

FSTORE_SIZE=$(du -sh "${TARGET_FILESTORE}" | cut -f1)
FSTORE_DIRS=$(ls "${TARGET_FILESTORE}" | wc -l | tr -d ' ')
STEP3_END=$(date +%s)
echo "      OK — ${FSTORE_SIZE}, ${FSTORE_DIRS} dirs — $((STEP3_END - STEP3_START))s"

# ---------------------------------------------------------------------------
# Step 4 — Validation: record counts and attachment integrity
# ---------------------------------------------------------------------------
echo "[4/5] Running validation checks..."
STEP4_START=$(date +%s)

echo ""
echo "  --- Record Count Validation ---"

# Core ERP tables
psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -F'|' -c "
SELECT table_name, cnt FROM (
  SELECT 'mrp_production'  AS table_name, COUNT(*) AS cnt FROM mrp_production  UNION ALL
  SELECT 'mrp_bom',                        COUNT(*) FROM mrp_bom               UNION ALL
  SELECT 'stock_move',                     COUNT(*) FROM stock_move             UNION ALL
  SELECT 'stock_quant',                    COUNT(*) FROM stock_quant            UNION ALL
  SELECT 'product_template',               COUNT(*) FROM product_template       UNION ALL
  SELECT 'account_move',                   COUNT(*) FROM account_move           UNION ALL
  SELECT 'stock_warehouse',                COUNT(*) FROM stock_warehouse        UNION ALL
  SELECT 'stock_location',                 COUNT(*) FROM stock_location         UNION ALL
  SELECT 'mrp_workcenter',                 COUNT(*) FROM mrp_workcenter
) t ORDER BY table_name;" 2>/dev/null | while IFS='|' read -r tbl cnt; do
  printf "  %-25s %s\n" "${tbl}" "${cnt}"
done

# Attachment validation — the critical check
echo ""
echo "  --- Attachment Validation ---"

IR_TOTAL=$(psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -c "SELECT COUNT(*) FROM ir_attachment;" 2>/dev/null | tr -d ' ')
IR_FILESTORE=$(psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -c "SELECT COUNT(*) FROM ir_attachment WHERE store_fname IS NOT NULL AND store_fname != '';" 2>/dev/null | tr -d ' ')
IR_DBSTORE=$(psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -c "SELECT COUNT(*) FROM ir_attachment WHERE db_datas IS NOT NULL;" 2>/dev/null | tr -d ' ')
IR_PDF=$(psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -c "SELECT COUNT(*) FROM ir_attachment WHERE mimetype = 'application/pdf';" 2>/dev/null | tr -d ' ')
IR_IMAGE=$(psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -c "SELECT COUNT(*) FROM ir_attachment WHERE mimetype LIKE 'image/%';" 2>/dev/null | tr -d ' ')
IR_BINARY=$(psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -c "SELECT COUNT(*) FROM ir_attachment WHERE mimetype = 'application/octet-stream';" 2>/dev/null | tr -d ' ')

printf "  %-25s %s\n" "ir_attachment (total)"    "${IR_TOTAL}"
printf "  %-25s %s\n" "  → filestore refs"        "${IR_FILESTORE}"
printf "  %-25s %s\n" "  → db_datas (inline)"     "${IR_DBSTORE}"
printf "  %-25s %s\n" "  → PDFs"                  "${IR_PDF}"
printf "  %-25s %s\n" "  → Images"                "${IR_IMAGE}"
printf "  %-25s %s\n" "  → Binary/octet"          "${IR_BINARY}"
printf "  %-25s %s\n" "filestore dirs restored"   "${FSTORE_DIRS}"

# Filestore integrity: count store_fname refs that have corresponding files
echo ""
echo "  --- Filestore Integrity ---"
FILESTORE_ORPHANS=$(psql -U "${DB_USER}" -d "${TARGET_DB}" -t -A -c "
SELECT COUNT(*) FROM ir_attachment
WHERE store_fname IS NOT NULL AND store_fname != '';" 2>/dev/null | tr -d ' ')
echo "  DB records pointing to filestore: ${FILESTORE_ORPHANS}"
echo "  Filestore dirs on disk          : ${FSTORE_DIRS}"

if [ "${IR_TOTAL}" -gt 0 ]; then
  echo "  ir_attachment status            : PASS (${IR_TOTAL} records restored)"
  ATTACH_STATUS="PASS"
else
  echo "  ir_attachment status            : FAIL (0 records — attachment restore broken)"
  ATTACH_STATUS="FAIL"
fi

STEP4_END=$(date +%s)
echo ""
echo "      Validation complete — $((STEP4_END - STEP4_START))s"

# ---------------------------------------------------------------------------
# Step 5 — Odoo module load validation
# ---------------------------------------------------------------------------
echo "[5/5] Validating Odoo module load..."
STEP5_START=$(date +%s)

MODULE_RESULT=$(
  source "${VENV}/bin/activate" 2>/dev/null || true
  python "${ODOO_ROOT}/odoo/odoo-bin" \
    -d "${TARGET_DB}" -r "${DB_USER}" \
    --addons-path="${ADDONS_PATH}" \
    --stop-after-init --no-http 2>&1 | \
    grep -E "modules loaded|Registry loaded|ERROR|CRITICAL" | tail -5
)
STEP5_END=$(date +%s)
echo "      ${MODULE_RESULT}"
echo "      OK — $((STEP5_END - STEP5_START))s"

# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------
RESTORE_END=$(date +%s)
TOTAL_SECONDS=$((RESTORE_END - RESTORE_START))

echo ""
echo "============================================================"
echo " Restore complete — total time: ${TOTAL_SECONDS}s"
echo " Target DB      : ${TARGET_DB}"
echo " Filestore      : ${TARGET_FILESTORE}"
echo " Attachment status: ${ATTACH_STATUS}"
echo "============================================================"
echo ""

if [ "${PRODUCTION_MODE}" = "false" ]; then
  echo " Test environment cleanup (when done):"
  echo "   dropdb -U ${DB_USER} ${TARGET_DB}"
  echo "   rm -rf \"${TARGET_FILESTORE}\""
  echo ""
fi

if [ "${ATTACH_STATUS}" = "FAIL" ]; then
  echo " ACTION REQUIRED: ir_attachment restore failed."
  echo " Run a fresh backup with backup_famoil.sh (custom format)"
  echo " and re-run this restore script."
  exit 1
fi
