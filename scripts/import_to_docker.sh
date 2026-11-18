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
COMPOSE_ENV="$(dirname "$0")/../docker/.env"

# Load .env if present so POSTGRES_USER is available for psql calls
if [[ -f "${COMPOSE_ENV}" ]]; then
    # shellcheck source=/dev/null
    set -a; source "${COMPOSE_ENV}"; set +a
fi
POSTGRES_USER="${POSTGRES_USER:-odoo}"

if [[ -z "${EXPORT_DIR}" ]]; then
    echo "Usage: $0 <export_dir>"
    echo "  export_dir: path to the directory created by export_for_docker.sh"
    exit 1
fi

if [[ ! -d "${EXPORT_DIR}" ]]; then
    echo "ERROR: Export directory not found: ${EXPORT_DIR}"
    exit 1
fi

# Guard against command injection via DB_NAME before it reaches bash -c strings
if ! [[ "${DB_NAME}" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo "ERROR: DB_NAME '${DB_NAME}' contains invalid characters. Only [A-Za-z0-9_-] allowed."
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
echo ""
echo "  >>> IF YOU ARE REIMPORTING INTO AN EXISTING LIVE STACK <<<"
echo "  Run ./scripts/export_for_docker.sh FIRST to save the current state."
echo "  Dropped data cannot be recovered without an export archive."
echo ""
read -r -p "Type CONFIRM to proceed: " CONFIRM
if [[ "${CONFIRM}" != "CONFIRM" ]]; then
    echo "Aborted."
    exit 0
fi

# 1. Stop Odoo (keep DB running)
echo "[1/5] Stopping Odoo service..."
docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" stop odoo

# 2. Drop + recreate DB
echo "[2/5] Dropping and recreating database ${DB_NAME}..."
docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" exec -T db psql -U "${POSTGRES_USER}" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}';" || true
docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" exec -T db psql -U "${POSTGRES_USER}" -c "DROP DATABASE IF EXISTS \"${DB_NAME}\";"
docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" exec -T db psql -U "${POSTGRES_USER}" -c "CREATE DATABASE \"${DB_NAME}\" OWNER \"${POSTGRES_USER}\";"

# 3. Restore DB
echo "[3/5] Restoring database from dump..."
docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" exec -T db pg_restore \
    --disable-triggers \
    --no-owner \
    --no-privileges \
    -j 4 \
    -U "${POSTGRES_USER}" \
    -d "${DB_NAME}" < "${DUMP_FILE}"
echo "      DB restored."

# 4. Restore filestore
# NOTE: Odoo is STOPPED at this point, so `docker compose exec` will fail.
# We use `docker run --rm -v <volume>` with the already-built Odoo image (no external pull)
# to manipulate the odoo-data volume directly.
if [[ -n "${FILESTORE_ARCHIVE}" && -f "${FILESTORE_ARCHIVE}" ]]; then
    echo "[4/5] Restoring filestore..."

    # Get the stopped container ID and derive its image + volume
    CONTAINER_ID=$(docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" ps -q odoo)
    if [[ -z "${CONTAINER_ID}" ]]; then
        echo "      ERROR: could not locate odoo container. Is the stack up (even if stopped)?"
        exit 1
    fi
    ODOO_IMAGE=$(docker inspect "${CONTAINER_ID}" --format '{{.Config.Image}}')
    ODOO_DATA_VOLUME=$(docker inspect "${CONTAINER_ID}" \
        --format '{{range .Mounts}}{{if eq .Destination "/var/lib/odoo"}}{{.Name}}{{end}}{{end}}')

    if [[ -z "${ODOO_DATA_VOLUME}" ]]; then
        echo "      ERROR: could not determine odoo-data volume name from container inspect."
        exit 1
    fi

    echo "      Using image : ${ODOO_IMAGE}"
    echo "      Volume name : ${ODOO_DATA_VOLUME}"

    # Extract the archive to a temp directory
    IMPORT_TMPDIR=$(mktemp -d)
    trap 'rm -rf "${IMPORT_TMPDIR}"' EXIT
    tar -xzf "${FILESTORE_ARCHIVE}" -C "${IMPORT_TMPDIR}"

    EXTRACTED_FS=$(find "${IMPORT_TMPDIR}" -maxdepth 1 -mindepth 1 -type d | head -1)
    if [[ -z "${EXTRACTED_FS}" ]]; then
        echo "      ERROR: could not find extracted filestore directory in archive."
        exit 1
    fi

    # Remove old filestore from volume using the already-built Odoo image
    docker run --rm \
        -v "${ODOO_DATA_VOLUME}:/var/lib/odoo" \
        "${ODOO_IMAGE}" \
        bash -c "rm -rf '/var/lib/odoo/filestore/${DB_NAME}' && mkdir -p /var/lib/odoo/filestore"

    # Copy new filestore into the volume and fix ownership (odoo uid=101)
    docker run --rm \
        -v "${ODOO_DATA_VOLUME}:/var/lib/odoo" \
        -v "${EXTRACTED_FS}:/src:ro" \
        "${ODOO_IMAGE}" \
        bash -c "cp -a /src/. '/var/lib/odoo/filestore/${DB_NAME}' && \
                 chown -R odoo:odoo '/var/lib/odoo/filestore/${DB_NAME}'"

    rm -rf "${IMPORT_TMPDIR}"
    echo "      Filestore restored."
else
    echo "[4/5] No filestore archive found — skipping (OK for a fresh/data-only DB)."
fi

# 5. Start Odoo
echo "[5/5] Starting Odoo..."
docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" start odoo

echo ""
echo "=== Import complete ==="
echo "Odoo should be accessible at http://localhost:8069"
echo "Login: admin / (the admin password from your Odoo instance)"
