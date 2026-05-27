#!/usr/bin/env bash
# file_protection_guard.sh
# PURPOSE: Block writes to protected files and directories.
# ENFORCES: Rule 1 (no undocumented changes), Rule 8 (security),
#           operational stability.
# LIFECYCLE: PreToolUse — Write | Edit | MultiEdit
# EXIT CODES: 2 = BLOCK action | 0 = allow

set -euo pipefail

# ── Setup ────────────────────────────────────────────────────────────────────
LOG_DIR="logs"
BLOCKED_LOG="$LOG_DIR/blocked_writes.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$LOG_DIR"

# Read JSON from stdin
INPUT=$(cat)

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tool_input = data.get('tool_input', data.get('input', {}))
    # Write uses file_path; Edit uses file_path; MultiEdit uses file_path
    path = tool_input.get('file_path', tool_input.get('path', ''))
    print(path)
except Exception:
    print('')
" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# ── Protected path patterns ───────────────────────────────────────────────────
PROTECTED_PATHS=(
    "/etc/odoo"
    "/etc/postgresql"
    "/usr/lib/python3"
    "/usr/local/lib/python"
    "/Users/mac/odoo17/odoo/odoo/"
)

# ── Credential file patterns ──────────────────────────────────────────────────
CREDENTIAL_PATTERNS=(
    "\.env$"
    "\.env\."
    "passwords"
    "secrets"
    "credentials"
    "id_rsa"
    "id_ed25519"
)

# ── Check protected paths ─────────────────────────────────────────────────────
for PROTECTED in "${PROTECTED_PATHS[@]}"; do
    if echo "$FILE_PATH" | grep -q "^$PROTECTED"; then
        REASON="Write to protected path '$PROTECTED' is prohibited — modifying core application files is not allowed"
        echo "" >&2
        echo "╔══════════════════════════════════════════════════════════════╗" >&2
        echo "║  GOVERNANCE BLOCK — file_protection_guard.sh                 ║" >&2
        echo "╚══════════════════════════════════════════════════════════════╝" >&2
        echo "BLOCKED FILE: $FILE_PATH" >&2
        echo "REASON: $REASON" >&2
        echo "" >&2
        echo "[$TIMESTAMP] BLOCKED | FILE: $FILE_PATH | REASON: $REASON" >> "$BLOCKED_LOG"
        exit 2
    fi
done

# ── Check credential file patterns ───────────────────────────────────────────
BASENAME=$(basename "$FILE_PATH")
for PATTERN in "${CREDENTIAL_PATTERNS[@]}"; do
    if echo "$BASENAME" | grep -qiE "$PATTERN"; then
        REASON="Write to credential/secret file '$FILE_PATH' is prohibited — never commit credentials"
        echo "" >&2
        echo "╔══════════════════════════════════════════════════════════════╗" >&2
        echo "║  GOVERNANCE BLOCK — file_protection_guard.sh                 ║" >&2
        echo "╚══════════════════════════════════════════════════════════════╝" >&2
        echo "BLOCKED FILE: $FILE_PATH" >&2
        echo "REASON: $REASON" >&2
        echo "" >&2
        echo "[$TIMESTAMP] BLOCKED | FILE: $FILE_PATH | REASON: $REASON" >> "$BLOCKED_LOG"
        exit 2
    fi
done

# ── Check file is within repo boundary ───────────────────────────────────────
# Resolve absolute path if possible
if command -v realpath &>/dev/null; then
    ABS_PATH=$(realpath -m "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")
else
    ABS_PATH="$FILE_PATH"
fi

if [[ "$ABS_PATH" == /* ]] && [[ "$ABS_PATH" != "$REPO_ROOT"* ]]; then
    REASON="Write outside repository boundary is prohibited. Repo root: $REPO_ROOT"
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  GOVERNANCE BLOCK — file_protection_guard.sh                 ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "BLOCKED FILE: $FILE_PATH" >&2
    echo "REASON: $REASON" >&2
    echo "" >&2
    echo "[$TIMESTAMP] BLOCKED | FILE: $FILE_PATH | REASON: $REASON" >> "$BLOCKED_LOG"
    exit 2
fi

exit 0
