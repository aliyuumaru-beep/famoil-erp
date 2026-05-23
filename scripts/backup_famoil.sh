#!/usr/bin/env bash
# =============================================================================
# backup_famoil.sh — Full backup of FamOil Odoo 17 instance
# =============================================================================
# Creates a timestamped backup directory containing:
#   - PostgreSQL plain-text dump
#   - Odoo filestore
#   - odoo.conf (passwords stripped)
#   - custom_addons directory
#
# Usage:
#   bash /Users/mac/odoo17/scripts/backup_famoil.sh
#
# No credentials are exposed. Uses local trust auth (pg_hba.conf = trust).
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — edit these if paths change
# ---------------------------------------------------------------------------
DB_USER="odoo"
DB_NAME="Famoil"
ODOO_ROOT="/Users/mac/odoo17"
FILESTORE="/Users/mac/Library/Application Support/Odoo/filestore/${DB_NAME}"
ODOO_CONF="${ODOO_ROOT}/odoo/odoo.conf"
CUSTOM_ADDONS="${ODOO_ROOT}/custom_addons"
BACKUP_BASE="/Users/mac/odoo_backups"

# ---------------------------------------------------------------------------
# Timestamp and target directory
# ---------------------------------------------------------------------------
TIMESTAMP=$(date +%Y%m%d_%H%M)
BACKUP_DIR="${BACKUP_BASE}/famoil_${TIMESTAMP}"

echo "============================================================"
echo " FamOil Backup — $(date '+%Y-%m-%d %H:%M:%S')"
echo " Target: ${BACKUP_DIR}"
echo "============================================================"

# ---------------------------------------------------------------------------
# Create directory structure
# ---------------------------------------------------------------------------
mkdir -p "${BACKUP_DIR}"/{filestore,custom_addons,docs,scripts}

# ---------------------------------------------------------------------------
# 1. PostgreSQL dump (plain text)
# ---------------------------------------------------------------------------
echo "[1/4] Dumping database: ${DB_NAME}..."
pg_dump -U "${DB_USER}" -d "${DB_NAME}" -F p -f "${BACKUP_DIR}/${DB_NAME}.sql"
echo "      OK — $(du -sh "${BACKUP_DIR}/${DB_NAME}.sql" | cut -f1)"

# ---------------------------------------------------------------------------
# 2. Filestore
# ---------------------------------------------------------------------------
echo "[2/4] Copying filestore..."
cp -r "${FILESTORE}/" "${BACKUP_DIR}/filestore/"
echo "      OK — $(du -sh "${BACKUP_DIR}/filestore" | cut -f1)"

# ---------------------------------------------------------------------------
# 3. odoo.conf (strip passwords)
# ---------------------------------------------------------------------------
echo "[3/4] Copying odoo.conf (passwords stripped)..."
grep -v -E "password|passwd|pwd|secret" "${ODOO_CONF}" \
  > "${BACKUP_DIR}/odoo.conf" || true
echo "      OK"

# ---------------------------------------------------------------------------
# 4. Custom addons
# ---------------------------------------------------------------------------
echo "[4/4] Copying custom_addons..."
cp -r "${CUSTOM_ADDONS}/" "${BACKUP_DIR}/custom_addons/"
echo "      OK — $(du -sh "${BACKUP_DIR}/custom_addons" | cut -f1)"

# ---------------------------------------------------------------------------
# Write backup manifest
# ---------------------------------------------------------------------------
cat > "${BACKUP_DIR}/BACKUP_MANIFEST.md" <<EOF
# Backup Manifest

| Field         | Value                              |
|---------------|------------------------------------|
| Database      | ${DB_NAME}                         |
| Odoo Version  | 17.0.1.3 Community                 |
| Backup Date   | $(date '+%Y-%m-%d %H:%M:%S')       |
| Backup Path   | ${BACKUP_DIR}                      |
| DB User       | ${DB_USER}                         |
| Filestore     | ${FILESTORE}                       |

## Contents

| File/Dir       | Description                        |
|----------------|------------------------------------|
| ${DB_NAME}.sql | PostgreSQL plain-text dump         |
| filestore/     | Odoo binary attachments            |
| odoo.conf      | Server config (passwords stripped) |
| custom_addons/ | All custom and third-party modules |
| docs/          | Documentation snapshot             |
| scripts/       | Utility scripts                    |

## Restore

See docs/famoil_erp_template/BACKUP_AND_RESTORE.md
EOF

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo " Backup complete."
echo " Location : ${BACKUP_DIR}"
echo " Total    : $(du -sh "${BACKUP_DIR}" | cut -f1)"
echo "============================================================"
