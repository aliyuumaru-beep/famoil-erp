#!/usr/bin/env bash
# audit_logger.sh
# PURPOSE: Log every bash command executed for full auditability.
# ENFORCES: Rule 8 (auditability), Rule 2 (git discipline traceability).
# LIFECYCLE: PostToolUse — Bash
# EXIT CODES: 0 always (never blocks)

set -euo pipefail

# ── Setup ────────────────────────────────────────────────────────────────────
LOG_DIR="logs"
AUDIT_LOG="$LOG_DIR/audit_trail.log"
MAX_SIZE_BYTES=10485760   # 10MB rotation threshold
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$LOG_DIR"
touch "$AUDIT_LOG"

# Read JSON from stdin
INPUT=$(cat)

# Extract fields from tool context
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tool_input = data.get('tool_input', data.get('input', {}))
    print(tool_input.get('command', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")

SESSION_ID=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('session_id', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo "unknown")

TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_name', 'Bash'))
except Exception:
    print('Bash')
" 2>/dev/null || echo "Bash")

# ── Log rotation: if log exceeds 10MB, archive it ───────────────────────────
if [ -f "$AUDIT_LOG" ]; then
    FILE_SIZE=$(stat -f%z "$AUDIT_LOG" 2>/dev/null || stat -c%s "$AUDIT_LOG" 2>/dev/null || echo 0)
    if [ "$FILE_SIZE" -gt "$MAX_SIZE_BYTES" ]; then
        ARCHIVE_NAME="$LOG_DIR/audit_trail_$(date '+%Y%m%d_%H%M%S').log"
        mv "$AUDIT_LOG" "$ARCHIVE_NAME"
        touch "$AUDIT_LOG"
        echo "[$TIMESTAMP] LOG_ROTATED | Previous log archived to $ARCHIVE_NAME" >> "$AUDIT_LOG"
    fi
fi

# ── Append audit entry ───────────────────────────────────────────────────────
# Format: [YYYY-MM-DD HH:MM:SS] | SESSION:<id> | TOOL:<name> | ACTION:<command>
if [ -n "$COMMAND" ]; then
    echo "[$TIMESTAMP] | SESSION:$SESSION_ID | TOOL:$TOOL_NAME | ACTION:$COMMAND" >> "$AUDIT_LOG"
fi

exit 0
