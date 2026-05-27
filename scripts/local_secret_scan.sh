#!/usr/bin/env bash
# =============================================================================
# local_secret_scan.sh — Local secret and credential scan
# =============================================================================
# Mirrors the logic of .github/workflows/security_scan.yml so that
# developers can verify scan results locally before pushing.
#
# Usage:
#   bash /Users/mac/odoo17/scripts/local_secret_scan.sh
#
# Exit codes:
#   0 — scan passed, no real credentials found
#   1 — scan failed, at least one violation found
#
# Approved test-fixture values (not flagged):
#   'test_password'   — explicit placeholder in test scripts
#   'dummy_password'  — explicit placeholder in test scripts
# =============================================================================

set -euo pipefail

REPO_ROOT="/Users/mac/odoo17"
FAILED=0

# ---------------------------------------------------------------------------
# Credential patterns to scan for
# ---------------------------------------------------------------------------
PATTERNS=(
  "password\s*="
  "passwd\s*="
  "db_password"
  "ANTHROPIC_API_KEY\s*="
  "SECRET_KEY\s*="
  "-----BEGIN.*PRIVATE KEY-----"
)

# ---------------------------------------------------------------------------
# File types to scan
# ---------------------------------------------------------------------------
INCLUDE_FLAGS=(
  "--include=*.py"
  "--include=*.sh"
  "--include=*.conf"
  "--include=*.json"
  "--include=*.env"
)

# ---------------------------------------------------------------------------
# Directories to exclude
# odoo/   — core Odoo framework source; not committed to git so not scanned
#            by CI; contains legitimate framework use of 'password' in APIs
# backups — local ERP backup archives; never committed to git
# ---------------------------------------------------------------------------
EXCLUDE_FLAGS=(
  "--exclude-dir=.git"
  "--exclude-dir=backups"
  "--exclude-dir=odoo"
  "--exclude=local_secret_scan.sh"
)

echo "============================================================"
echo " Local Secret Scan — $(date '+%Y-%m-%d %H:%M:%S')"
echo " Repo: ${REPO_ROOT}"
echo "============================================================"
echo ""

cd "${REPO_ROOT}"

for pattern in "${PATTERNS[@]}"; do
  # Scan for the pattern, then exclude approved test-fixture literals.
  # test_password and dummy_password are explicit placeholders — not real credentials.
  # Any other value (admin, secret, 123456, etc.) still fails.
  HITS=$(
    grep -rn \
      "${INCLUDE_FLAGS[@]}" \
      "${EXCLUDE_FLAGS[@]}" \
      -i "${pattern}" \
      . \
      2>/dev/null \
    | grep -v "'test_password'\|'dummy_password'" \
    || true
  )

  if [ -n "${HITS}" ]; then
    echo "SECURITY VIOLATION — pattern '${pattern}' found:"
    echo "${HITS}"
    echo ""
    FAILED=1
  else
    echo "  OK — ${pattern}"
  fi
done

echo ""
echo "============================================================"
if [ "${FAILED}" -ne 0 ]; then
  echo " Scan FAILED — remove credentials before pushing."
  echo "============================================================"
  exit 1
fi

echo " Scan PASSED — no credential violations found."
echo "============================================================"
