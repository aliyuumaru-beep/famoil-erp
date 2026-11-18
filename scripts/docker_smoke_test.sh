#!/usr/bin/env bash
# docker_smoke_test.sh — Verify the Docker stack starts: TCP port open + werkzeug log entry
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

echo "[2/4] Waiting for Odoo to accept TCP connections on port ${ODOO_PORT} (up to ${MAX_WAIT}s)..."
# /web/health returns 500 when db_name is set but not yet initialized — that is expected
# on a fresh stack before import. We check TCP + the werkzeug startup log line instead.
ELAPSED=0
until nc -z localhost "${ODOO_PORT}" 2>/dev/null; do
    if (( ELAPSED >= MAX_WAIT )); then
        echo "FAIL: Odoo did not open port ${ODOO_PORT} within ${MAX_WAIT}s."
        CONTAINER_ID=$(docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" ps -q odoo)
        docker exec "${CONTAINER_ID}" tail -30 /var/log/odoo/odoo.log 2>/dev/null || true
        docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" down
        exit 1
    fi
    sleep 5
    ELAPSED=$(( ELAPSED + 5 ))
    echo "      ... waited ${ELAPSED}s"
done

echo "[3/4] Confirming werkzeug HTTP service log entry (10s grace)..."
sleep 10
CONTAINER_ID=$(docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" ps -q odoo)
# Check logfile first; fall back to container stdout if logfile not found
LOG_OK=false
if docker exec "${CONTAINER_ID}" test -f /var/log/odoo/odoo.log 2>/dev/null; then
    docker exec "${CONTAINER_ID}" grep -q "HTTP service (werkzeug)" /var/log/odoo/odoo.log 2>/dev/null && LOG_OK=true
fi
# Also check container stdout (some configurations log there)
docker logs "${CONTAINER_ID}" 2>&1 | grep -q "HTTP service (werkzeug)" && LOG_OK=true

if ! $LOG_OK; then
    echo "FAIL: werkzeug startup line not found in Odoo logs."
    docker exec "${CONTAINER_ID}" tail -30 /var/log/odoo/odoo.log 2>/dev/null || \
        docker logs "${CONTAINER_ID}" 2>&1 | tail -30
    docker compose -f "${COMPOSE_FILE}" --env-file "${COMPOSE_ENV}" down
    exit 1
fi
echo "      Odoo HTTP service confirmed running on port ${ODOO_PORT}."

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
