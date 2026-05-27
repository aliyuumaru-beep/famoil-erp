#!/usr/bin/env bash
# =============================================================================
# check_claude_review_log.sh — Fetch and filter a claude-review CI run log
# =============================================================================
# Retrieves the GitHub Actions run log for a claude-review job and extracts
# the lines most relevant to diagnosing authentication or review failures.
#
# Usage:
#   bash scripts/check_claude_review_log.sh <RUN_ID> <REPO>
#
# Example:
#   bash scripts/check_claude_review_log.sh 26538461795 aliyuumaru-beep/famoil-erp
#
# Exit codes:
#   0 — always (reporting only, no destructive actions)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
RUN_ID="${1:-}"
REPO="${2:-}"

if [ -z "${RUN_ID}" ] || [ -z "${REPO}" ]; then
  echo "Usage: bash scripts/check_claude_review_log.sh <RUN_ID> <REPO>"
  echo "Example: bash scripts/check_claude_review_log.sh 26538461795 aliyuumaru-beep/famoil-erp"
  exit 0
fi

echo "============================================================"
echo " claude-review Log Inspector"
echo " Run ID : ${RUN_ID}"
echo " Repo   : ${REPO}"
echo "============================================================"
echo ""

# ---------------------------------------------------------------------------
# Fetch the full log from GitHub Actions
# ---------------------------------------------------------------------------
FULL_LOG=$(gh run view "${RUN_ID}" --repo "${REPO}" --log 2>&1 || true)

# ---------------------------------------------------------------------------
# Filter 1: Error lines — surfaced failures and exit codes
# ---------------------------------------------------------------------------
echo "--- Errors and failures ---"
echo "${FULL_LOG}" \
  | grep -i "error\|fail\|exit code\|##\[error\]" \
  | grep -v "##\[group\]\|##\[endgroup\]\|Post job\|warning\|deprecated" \
  | head -20 \
  || echo "  (none found)"

echo ""

# ---------------------------------------------------------------------------
# Filter 2: Authentication / token lines — shows which auth path was taken
# ---------------------------------------------------------------------------
echo "--- Authentication and token flow ---"
echo "${FULL_LOG}" \
  | grep -i "oidc\|token\|credential\|unauthorized\|401\|install\|app token\|github_token\|anthropic" \
  | grep -v "##\[group\]\|##\[endgroup\]\|checkout\|safe.directory\|git config\|node_modules" \
  | head -20 \
  || echo "  (none found)"

echo ""

# ---------------------------------------------------------------------------
# Filter 3: Review outcome — what Claude actually decided
# ---------------------------------------------------------------------------
echo "--- Review result (if reached) ---"
echo "${FULL_LOG}" \
  | grep -i "REVIEW RESULT\|APPROVED\|CHANGES REQUIRED\|violation" \
  | grep -v "direct_prompt\|End your\|one of:" \
  | head -10 \
  || echo "  (review did not reach a result)"

echo ""
echo "============================================================"
echo " Report complete."
echo "============================================================"

exit 0
