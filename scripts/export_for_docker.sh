#!/usr/bin/env bash
# export_for_docker.sh — Export FamOil DB + filestore as a dated archive
# Output: odoo_backups/docker_export_YYYYMMDD_HHMM/
#   famoil_YYYYMMDD_HHMM.dump   — pg_dump custom format
#   filestore.tar.gz             — Odoo filestore
#   MANIFEST.txt                 — sizes and checksums

set -euo pipefail

DB_NAME="${1:-Famoil}"
DB_USER="${PGUSER:-odoo}"
FILESTORE_DIR="${HOME}/Library/Application Support/Odoo/filestore/${DB_NAME}"
BACKUP_ROOT="${HOME}/OdooFolder/odoo_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M)
EXPORT_DIR="${BACKUP_ROOT}/docker_export_${TIMESTAMP}"

echo "=== FamOil Docker Export ==="
echo "DB       : ${DB_NAME}"
echo "User     : ${DB_USER}"
echo "Filestore: ${FILESTORE_DIR}"
echo "Output   : ${EXPORT_DIR}"
echo ""

mkdir -p "${EXPORT_DIR}"

# 1. DB dump
echo "[1/3] Dumping database..."
DUMP_FILE="${EXPORT_DIR}/${DB_NAME,,}_${TIMESTAMP}.dump"
pg_dump -F c -U "${DB_USER}" "${DB_NAME}" -f "${DUMP_FILE}"
echo "      DB dump: $(du -sh "${DUMP_FILE}" | cut -f1)"

# 2. Filestore
echo "[2/3] Archiving filestore..."
if [[ -d "${FILESTORE_DIR}" ]]; then
    FILESTORE_ARCHIVE="${EXPORT_DIR}/filestore.tar.gz"
    tar -czf "${FILESTORE_ARCHIVE}" -C "$(dirname "${FILESTORE_DIR}")" "$(basename "${FILESTORE_DIR}")"
    echo "      Filestore: $(du -sh "${FILESTORE_ARCHIVE}" | cut -f1)"
else
    echo "      WARNING: Filestore directory not found at ${FILESTORE_DIR}"
    echo "      Skipping filestore archive."
fi

# 3. Manifest
echo "[3/3] Writing manifest..."
MANIFEST="${EXPORT_DIR}/MANIFEST.txt"
{
    echo "FamOil Docker Export"
    echo "Generated : $(date)"
    echo "DB        : ${DB_NAME}"
    echo "Odoo ver  : 17.0"
    echo ""
    ls -lh "${EXPORT_DIR}"
    echo ""
    echo "Checksums (SHA-256):"
    shasum -a 256 "${EXPORT_DIR}"/*.dump "${EXPORT_DIR}"/*.tar.gz 2>/dev/null || true
} > "${MANIFEST}"

echo ""
echo "=== Export complete ==="
echo "Directory: ${EXPORT_DIR}"
echo ""
echo "Next step: copy this directory to the target host, then run:"
echo "  scripts/import_to_docker.sh ${EXPORT_DIR}"
