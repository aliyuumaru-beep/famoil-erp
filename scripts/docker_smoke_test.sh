#!/usr/bin/env bash
# docker_smoke_test.sh — Verify the Docker stack starts and Odoo responds on /web/health
# Run this after docker compose build on the target host, before importing any real data.
#
# Usage: ./scripts/docker_smoke_test.sh [--no-cleanup]
#   --no-cleanup  Leave the stack running after the test (default: stop after pass)
#
# Prerequisites: docker/.env must exist with POSTGRES_PASSWORD and ODOO_ADMIN_PASSWD set.

set -euo pipefail

COMPOSE_FILE="$(dirname "$0")/../docker/docker-compose.yml"
COMPOSE_ENV="$(dirname "$0")/../docker/.env"
MAX_WAIT=120
CLEANUP=true

for arg in "$@"; do
    [[ "${arg}" == "--no-cleanup" ]] && CLEANUP=false
done

echo "=== FamOil Docker Smoke Test ==="
echo "Compose file: ${COMPOSE_FILE}"
echo ""

if [[ ! -f "${COMPOSE_ENV}" ]]; then
    echo "ERROR: docker/.env not found. Copy docker/.env.example and fill in real values."
    exit 1
fi

# Source .env to get ODOO_PORT
set -a; source "${COMPOSE_ENV}"; set +a
ODOO_PORT="${ODOO_PORT:-8069}"

echo "[1/4] Starting stack..."
docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" up -d

echo "[2/4] Waiting for Odoo healthcheck (up to ${MAX_WAIT}s)..."
ELAPSED=0
until curl -sf "http://localhost:${ODOO_PORT}/web/health" > /dev/null 2>&1; do
    if (( ELAPSED >= MAX_WAIT )); then
        echo "FAIL: Odoo did not respond within ${MAX_WAIT}s."
        docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" logs --tail=50 odoo
        docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" down
        exit 1
    fi
    sleep 5
    ELAPSED=$(( ELAPSED + 5 ))
    echo "      ... waited ${ELAPSED}s"
done

echo "[3/4] Checking /web/health response..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${ODOO_PORT}/web/health")
if [[ "${HTTP_STATUS}" != "200" ]]; then
    echo "FAIL: /web/health returned HTTP ${HTTP_STATUS} (expected 200)."
    docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" down
    exit 1
fi

echo "      HTTP ${HTTP_STATUS} — Odoo is healthy."

if [[ "${CLEANUP}" == "true" ]]; then
    echo "[4/4] Stopping stack (pass --no-cleanup to keep running)..."
    docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" down
else
    echo "[4/4] Stack left running (--no-cleanup)."
fi

echo ""
echo "=== SMOKE TEST PASSED ==="
echo "Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Host: $(hostname)"
echo "Port: ${ODOO_PORT}"
