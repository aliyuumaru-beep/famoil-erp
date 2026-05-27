#!/usr/bin/env bash
# =============================================================================
# sync_backup_to_gdrive.sh — Sync FamOil compressed backups to Google Drive
# =============================================================================
# Uploads compressed backup archives (famoil_*.tar.gz) to Google Drive using
# rclone. Only archives are synced — PostgreSQL dumps, filestore, and raw
# backup directories are never committed to the repository or uploaded to Drive.
#
# Usage:
#   bash /Users/mac/odoo17/scripts/sync_backup_to_gdrive.sh [--dry-run]
#
# Prerequisites:
#   1. rclone installed: brew install rclone
#   2. Google Drive remote configured: rclone config (name the remote "gdrive")
#   3. See docs/deployment/MACOS_BACKUP_AUTOMATION.md for setup instructions
#
# Options:
#   --dry-run    Show what would be uploaded without transferring any files
#
# Target structure on Google Drive:
#   FamOil_Backups/ERP/famoil_YYYYMMDD_HHMM.tar.gz
#
# No credentials are stored in this script.
# Google Drive authentication is managed by rclone's token store.
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BACKUP_BASE="/Users/mac/odoo_backups"
GDRIVE_REMOTE="gdrive"
GDRIVE_TARGET="FamOil_Backups/ERP"
LOG_FILE="/Users/mac/odoo17/logs/gdrive_sync.log"
DRY_RUN="false"

# Parse arguments
for ARG in "$@"; do
  case "${ARG}" in
    --dry-run) DRY_RUN="true" ;;
    *) echo "Unknown argument: ${ARG}"; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
echo "============================================================"
echo " FamOil → Google Drive Sync — $(date '+%Y-%m-%d %H:%M:%S')"
[ "${DRY_RUN}" = "true" ] && echo " Mode: DRY-RUN (no files transferred)"
echo "============================================================"

# Check rclone is installed
if ! command -v rclone &>/dev/null; then
  echo ""
  echo "ERROR: rclone is not installed."
  echo ""
  echo "Install it with:"
  echo "  brew install rclone"
  echo ""
  echo "Then configure the Google Drive remote:"
  echo "  rclone config"
  echo "  (Follow prompts — name the remote 'gdrive', choose Google Drive)"
  echo ""
  echo "See docs/deployment/MACOS_BACKUP_AUTOMATION.md for full setup guide."
  exit 1
fi

# Check gdrive remote is configured
if ! rclone listremotes 2>/dev/null | grep -q "^${GDRIVE_REMOTE}:"; then
  echo ""
  echo "ERROR: rclone remote '${GDRIVE_REMOTE}' is not configured."
  echo ""
  echo "Configure it with:"
  echo "  rclone config"
  echo "  (Choose 'n' for new remote, name it '${GDRIVE_REMOTE}', type 'drive')"
  echo ""
  echo "See docs/deployment/MACOS_BACKUP_AUTOMATION.md for full setup guide."
  exit 1
fi

# ---------------------------------------------------------------------------
# Find archives to sync
# ---------------------------------------------------------------------------
ARCHIVES=$(find "${BACKUP_BASE}" -maxdepth 1 -name "famoil_*.tar.gz" | sort)
ARCHIVE_COUNT=$(echo "${ARCHIVES}" | grep -c . 2>/dev/null || echo 0)

if [ -z "${ARCHIVES}" ]; then
  echo "No famoil_*.tar.gz archives found in ${BACKUP_BASE}"
  echo "Run scripts/backup_famoil.sh first (COMPRESS=true)."
  exit 0
fi

echo ""
echo "Archives to sync (${ARCHIVE_COUNT} found):"
echo "${ARCHIVES}" | while read -r F; do
  echo "  $(basename "${F}") — $(du -sh "${F}" | cut -f1)"
done
echo ""

# ---------------------------------------------------------------------------
# Sync to Google Drive
# ---------------------------------------------------------------------------
RCLONE_FLAGS="--progress --stats-one-line"
[ "${DRY_RUN}" = "true" ] && RCLONE_FLAGS="${RCLONE_FLAGS} --dry-run"

{
  echo "# Sync Log — $(date '+%Y-%m-%d %H:%M:%S')"
  [ "${DRY_RUN}" = "true" ] && echo "# Mode: DRY-RUN"
  echo "# Archives found: ${ARCHIVE_COUNT}"
  echo ""
} >> "${LOG_FILE}"

echo "Syncing to ${GDRIVE_REMOTE}:${GDRIVE_TARGET}/ ..."
# shellcheck disable=SC2086
rclone copy "${BACKUP_BASE}" "${GDRIVE_REMOTE}:${GDRIVE_TARGET}" \
  --include "famoil_*.tar.gz" \
  ${RCLONE_FLAGS} \
  2>&1 | tee -a "${LOG_FILE}"

# ---------------------------------------------------------------------------
# Verify transfer
# ---------------------------------------------------------------------------
echo ""
echo "Verifying remote contents..."
rclone ls "${GDRIVE_REMOTE}:${GDRIVE_TARGET}" 2>/dev/null \
  | grep "famoil_" \
  | tee -a "${LOG_FILE}"

echo "" >> "${LOG_FILE}"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================================"
if [ "${DRY_RUN}" = "true" ]; then
  echo " DRY-RUN complete — no files transferred."
else
  echo " Sync complete."
fi
echo " Target : ${GDRIVE_REMOTE}:${GDRIVE_TARGET}"
echo " Log    : ${LOG_FILE}"
echo "============================================================"
