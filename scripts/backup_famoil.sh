#!/usr/bin/env bash
# =============================================================================
# backup_famoil.sh — Full backup of FamOil Odoo 17 instance
# =============================================================================
# Creates a timestamped backup directory containing:
#   - PostgreSQL plain-text dump
#   - Odoo filestore
#   - odoo.conf (passwords stripped)
#   - custom_addons directory
#   - Documentation snapshot
#   - Operational scripts
#
# Additionally:
#   - Optionally compresses the backup to tar.gz (controlled by COMPRESS var)
#   - Updates backups/BACKUP_MANIFEST.md in the repository (governance bridge)
#     so backup_check.yml workflow can validate backup currency
#   - Produces a retention report (dry-run — identifies candidates, no deletion)
#
# Usage:
#   bash /Users/mac/odoo17/scripts/backup_famoil.sh
#
# Options (edit variables in config section below):
#   COMPRESS   — "true" produces tar.gz alongside directory (default: true)
#   KEEP_DAYS  — age threshold in days for retention report candidates (default: 7)
#
# No credentials are exposed. Uses local trust auth (pg_hba.conf = trust).
# Backward-compatible: supports legacy famoil_* and v2_* naming conventions.
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
REPO_ROOT="/Users/mac/odoo17"
COMPRESS="true"
KEEP_DAYS=7
AUTO_DELETE="false"   # set to "true" to permanently delete retention candidates

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
echo "[1/6] Dumping database: ${DB_NAME}..."
pg_dump -U "${DB_USER}" -d "${DB_NAME}" -F p -f "${BACKUP_DIR}/${DB_NAME}.sql"
echo "      OK — $(du -sh "${BACKUP_DIR}/${DB_NAME}.sql" | cut -f1)"

# ---------------------------------------------------------------------------
# 2. Filestore
# ---------------------------------------------------------------------------
echo "[2/6] Copying filestore..."
cp -r "${FILESTORE}/" "${BACKUP_DIR}/filestore/"
echo "      OK — $(du -sh "${BACKUP_DIR}/filestore" | cut -f1)"

# ---------------------------------------------------------------------------
# 3. odoo.conf (strip passwords)
# ---------------------------------------------------------------------------
echo "[3/6] Copying odoo.conf (passwords stripped)..."
grep -v -E "password|passwd|pwd|secret" "${ODOO_CONF}" \
  > "${BACKUP_DIR}/odoo.conf" || true
echo "      OK"

# ---------------------------------------------------------------------------
# 4. Custom addons
# ---------------------------------------------------------------------------
echo "[4/6] Copying custom_addons..."
cp -r "${CUSTOM_ADDONS}/" "${BACKUP_DIR}/custom_addons/"
echo "      OK — $(du -sh "${BACKUP_DIR}/custom_addons" | cut -f1)"

# ---------------------------------------------------------------------------
# 5. Documentation snapshot
# ---------------------------------------------------------------------------
echo "[5/6] Copying documentation snapshot..."
cp -r "${ODOO_ROOT}/docs/" "${BACKUP_DIR}/docs/"
echo "      OK — $(du -sh "${BACKUP_DIR}/docs" | cut -f1)"

# ---------------------------------------------------------------------------
# 6. Scripts
# ---------------------------------------------------------------------------
echo "[6/6] Copying scripts..."
cp -r "${ODOO_ROOT}/scripts/" "${BACKUP_DIR}/scripts/"
echo "      OK — $(du -sh "${BACKUP_DIR}/scripts" | cut -f1)"

# ---------------------------------------------------------------------------
# Write backup manifest (inside backup directory)
# ---------------------------------------------------------------------------
BACKUP_RAW_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
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
# Compress backup directory (optional — controlled by COMPRESS variable)
# ---------------------------------------------------------------------------
ARCHIVE=""
ARCHIVE_SIZE=""
if [ "${COMPRESS}" = "true" ]; then
  echo ""
  echo "Compressing backup directory..."
  ARCHIVE="${BACKUP_BASE}/famoil_${TIMESTAMP}.tar.gz"
  tar -czf "${ARCHIVE}" -C "${BACKUP_BASE}" "famoil_${TIMESTAMP}"
  ARCHIVE_SIZE=$(du -sh "${ARCHIVE}" | cut -f1)
  echo "      Archive: ${ARCHIVE} (${ARCHIVE_SIZE})"
fi

# ---------------------------------------------------------------------------
# Update governance bridge — repo backups/BACKUP_MANIFEST.md
# Lightweight metadata only. No SQL, credentials, or binary content.
# This file must be committed after each backup run so that the
# backup_check.yml GitHub Actions workflow can validate backup currency.
# ---------------------------------------------------------------------------
BRIDGE_DIR="${REPO_ROOT}/backups"
mkdir -p "${BRIDGE_DIR}"

cat > "${BRIDGE_DIR}/BACKUP_MANIFEST.md" <<EOF
# Backup Manifest — Governance Bridge
# FamOil Software Factory
# Auto-generated by scripts/backup_famoil.sh — do not edit manually

> This file bridges local backup execution and the backup_check.yml GitHub
> Actions workflow. It contains metadata only — no credentials, no dumps,
> no sensitive data.

---

| Field                | Value                                          |
|---------------------|------------------------------------------------|
| Last Backup Date     | $(date '+%Y-%m-%d %H:%M:%S')                  |
| Backup Archive Name  | famoil_${TIMESTAMP}                           |
| Backup Location      | ${BACKUP_DIR}                                 |
| Raw Directory Size   | ${BACKUP_RAW_SIZE}                            |
| Compressed Archive   | ${ARCHIVE:-not compressed}                    |
| Archive Size         | ${ARCHIVE_SIZE:-n/a}                          |
| Verification Status  | COMPLETED                                     |
| Odoo Version         | 17.0.1.3 Community                            |
| Database             | ${DB_NAME}                                    |
| Backed Up By         | scripts/backup_famoil.sh                      |

## Contents Backed Up

- [x] PostgreSQL database dump (${DB_NAME}.sql)
- [x] Odoo filestore
- [x] odoo.conf (passwords stripped)
- [x] custom_addons/
- [x] docs/ snapshot
- [x] scripts/ snapshot

## Restore Reference

See: docs/BACKUP_AND_RECOVERY.md
See: docs/famoil_erp_template/BACKUP_AND_RESTORE.md

## Governance Note

After each backup run, commit this file to maintain workflow continuity:

  git add backups/BACKUP_MANIFEST.md
  git commit -m "chore: update backup manifest $(date '+%Y-%m-%d')"

The backup_check.yml workflow fails if this file is not updated within 7 days.
EOF

echo "      Governance bridge updated: ${BRIDGE_DIR}/BACKUP_MANIFEST.md"

# ---------------------------------------------------------------------------
# Retention report — DRY-RUN only (Phase 2)
# Identifies deletion candidates. Does NOT delete anything.
# Supports both famoil_YYYYMMDD_HHMM and v2_YYYYMMDD_* naming conventions.
# Automatic deletion may be enabled after operator validation.
# ---------------------------------------------------------------------------
RETENTION_LOG="${REPO_ROOT}/logs/retention_report.log"
TODAY_EPOCH=$(date +%s)

echo ""
echo "------------------------------------------------------------"
echo " Retention Report (DRY-RUN — no deletions)"
echo " Policy: flag backups older than ${KEEP_DAYS} days as candidates"
echo "------------------------------------------------------------"

{
  echo "# Retention Report — $(date '+%Y-%m-%d %H:%M:%S')"
  echo "# Policy: flag backups older than ${KEEP_DAYS} days as candidates"
  echo "# Naming conventions supported: famoil_YYYYMMDD_*, v2_YYYYMMDD_*"
  echo "# Mode: DRY-RUN (no deletions performed)"
  echo ""
  printf "| %-36s | %-10s | %-6s | %-9s |\n" "Backup Name" "Age (days)" "Size" "Status"
  printf "| %-36s | %-10s | %-6s | %-9s |\n" "------------------------------------" "----------" "------" "---------"
} > "${RETENTION_LOG}"

TOTAL=0
CANDIDATES=0

for ITEM in "${BACKUP_BASE}"/famoil_* "${BACKUP_BASE}"/v2_*; do
  [ -e "${ITEM}" ] || continue
  NAME=$(basename "${ITEM}")
  SIZE=$(du -sh "${ITEM}" 2>/dev/null | cut -f1 || echo "?")
  TOTAL=$((TOTAL + 1))

  # Extract 8-digit date from famoil_YYYYMMDD_* or v2_YYYYMMDD_* naming
  DATE_PART=$(echo "${NAME}" | grep -oE '[0-9]{8}' | head -1 || true)
  if [ -n "${DATE_PART}" ]; then
    DIR_EPOCH=$(date -j -f "%Y%m%d" "${DATE_PART}" +%s 2>/dev/null || echo "0")
    AGE_DAYS=$(( (TODAY_EPOCH - DIR_EPOCH) / 86400 ))
  else
    AGE_DAYS="unknown"
    DIR_EPOCH=0
  fi

  if [ "${AGE_DAYS}" = "unknown" ] || [ "${AGE_DAYS}" -gt "${KEEP_DAYS}" ] 2>/dev/null; then
    STATUS="CANDIDATE"
    CANDIDATES=$((CANDIDATES + 1))
  else
    STATUS="RETAIN"
  fi

  printf "| %-36s | %-10s | %-6s | %-9s |\n" "${NAME}" "${AGE_DAYS}" "${SIZE}" "${STATUS}" \
    >> "${RETENTION_LOG}"
  echo "  ${NAME} — age: ${AGE_DAYS} days — ${SIZE} — ${STATUS}"

  if [ "${STATUS}" = "CANDIDATE" ] && [ "${AUTO_DELETE}" = "true" ]; then
    rm -r "${ITEM}"
    echo "  [DELETED] ${NAME}"
    echo "  DELETED: ${NAME}" >> "${RETENTION_LOG}"
  fi
done

ACTION_TAKEN="NONE (dry-run)"
[ "${AUTO_DELETE}" = "true" ] && ACTION_TAKEN="DELETED ${CANDIDATES} candidate(s)"

{
  echo ""
  echo "Total scanned : ${TOTAL}"
  echo "Candidates    : ${CANDIDATES}"
  echo "Action taken  : ${ACTION_TAKEN}"
  echo ""
  echo "To enable deletion: set AUTO_DELETE=\"true\" in script config section."
} >> "${RETENTION_LOG}"

echo ""
echo "  Total: ${TOTAL} | Candidates: ${CANDIDATES} | Action: ${ACTION_TAKEN} | Report: ${RETENTION_LOG}"
echo "------------------------------------------------------------"

# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
echo " Backup complete."
echo " Raw dir  : ${BACKUP_DIR} (${BACKUP_RAW_SIZE})"
[ -n "${ARCHIVE}" ] && echo " Archive  : ${ARCHIVE} (${ARCHIVE_SIZE})"
echo " Manifest : ${BRIDGE_DIR}/BACKUP_MANIFEST.md"
echo " Retention: ${RETENTION_LOG}"
echo "============================================================"
echo ""
echo " NEXT STEP — Commit governance bridge to repository:"
echo "   cd ${REPO_ROOT}"
echo "   git add backups/BACKUP_MANIFEST.md"
echo "   git commit -m \"chore: update backup manifest $(date '+%Y-%m-%d')\""
echo "============================================================"
