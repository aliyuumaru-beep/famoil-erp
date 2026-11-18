#!/usr/bin/env bash
# import_to_docker.sh — Import a docker export archive into the running Docker stack
# Usage: ./scripts/import_to_docker.sh <export_dir>
#
# Prerequisites:
#   - Docker and docker compose are installed and running
#   - The Docker stack has been started (docker compose up -d)
#   - The export was created by export_for_docker.sh
#
# This script:
#   1. Drops and recreates the DB inside the Docker postgres container
#   2. Restores the pg_dump archive
#   3. Copies the filestore into the odoo-data volume
#   4. Restarts the Odoo container

set -euo pipefail

EXPORT_DIR="${1:-}"
DB_NAME="${DB_NAME:-Famoil}"
COMPOSE_FILE="$(dirname "$0")/../docker/docker-compose.yml"

if [[ -z "${EXPORT_DIR}" ]]; then
    echo "Usage: $0 <export_dir>"
    echo "  export_dir: path to the directory created by export_for_docker.sh"
    exit 1
fi

if [[ ! -d "${EXPORT_DIR}" ]]; then
    echo "ERROR: Export directory not found: ${EXPORT_DIR}"
    exit 1
fi

DUMP_FILE=$(find "${EXPORT_DIR}" -name "*.dump" | head -1)
FILESTORE_ARCHIVE=$(find "${EXPORT_DIR}" -name "filestore.tar.gz" | head -1)

if [[ -z "${DUMP_FILE}" ]]; then
    echo "ERROR: No .dump file found in ${EXPORT_DIR}"
    exit 1
fi

echo "=== FamOil Docker Import ==="
echo "Export dir  : ${EXPORT_DIR}"
echo "DB dump     : ${DUMP_FILE}"
echo "Filestore   : ${FILESTORE_ARCHIVE:-NOT FOUND}"
echo "Compose file: ${COMPOSE_FILE}"
echo ""
echo "WARNING: This will DROP and recreate the '${DB_NAME}' database inside Docker."
read -r -p "Type CONFIRM to proceed: " CONFIRM
if [[ "${CONFIRM}" != "CONFIRM" ]]; then
    echo "Aborted."
    exit 0
fi

# 1. Stop Odoo (keep DB running)
echo "[1/5] Stopping Odoo service..."
docker compose -f "${COMPOSE_FILE}" stop odoo

# 2. Drop + recreate DB
echo "[2/5] Dropping and recreating database ${DB_NAME}..."
docker compose -f "${COMPOSE_FILE}" exec -T db psql -U odoo -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}';" || true
docker compose -f "${COMPOSE_FILE}" exec -T db psql -U odoo -c "DROP DATABASE IF EXISTS \"${DB_NAME}\";"
docker compose -f "${COMPOSE_FILE}" exec -T db psql -U odoo -c "CREATE DATABASE \"${DB_NAME}\" OWNER odoo;"

# 3. Restore DB
echo "[3/5] Restoring database from dump..."
docker compose -f "${COMPOSE_FILE}" exec -T db pg_restore \
    --disable-triggers \
    -j 4 \
    -U odoo \
    -d "${DB_NAME}" < "${DUMP_FILE}"
echo "      DB restored."

# 4. Restore filestore
if [[ -n "${FILESTORE_ARCHIVE}" && -f "${FILESTORE_ARCHIVE}" ]]; then
    echo "[4/5] Restoring filestore..."
    # The Docker odoo-data volume mounts at /var/lib/odoo inside the container.
    # Filestore lives at /var/lib/odoo/filestore/<DB_NAME>/ inside the container.
    ODOO_CONTAINER=$(docker compose -f "${COMPOSE_FILE}" ps -q odoo)
    docker run --rm \
        --volumes-from "${ODOO_CONTAINER}" \
        -v "${FILESTORE_ARCHIVE}:/tmp/filestore.tar.gz:ro" \
        ubuntu:22.04 \
        bash -c "rm -rf /var/lib/odoo/filestore/${DB_NAME} && \
                 mkdir -p /var/lib/odoo/filestore && \
                 tar -xzf /tmp/filestore.tar.gz -C /var/lib/odoo/filestore && \
                 chown -R 101:101 /var/lib/odoo/filestore/${DB_NAME}"
    echo "      Filestore restored."
else
    echo "[4/5] No filestore archive found — skipping (OK for a fresh/data-only DB)."
fi

# 5. Start Odoo
echo "[5/5] Starting Odoo..."
docker compose -f "${COMPOSE_FILE}" start odoo

echo ""
echo "=== Import complete ==="
echo "Odoo should be accessible at http://localhost:8069"
echo "Login: admin / (the admin password from your Odoo instance)"
