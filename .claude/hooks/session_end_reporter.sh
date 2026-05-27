#!/usr/bin/env bash
# session_end_reporter.sh
# PURPOSE: Generate a session summary when Claude stops.
# ENFORCES: Rule 1 (documentation), continuity across sessions.
# LIFECYCLE: Stop
# EXIT CODES: 0 always

# ── Infinite loop prevention ──────────────────────────────────────────────────
# Read stdin JSON to check stop_hook_active flag
INPUT=$(cat 2>/dev/null || echo "{}")

STOP_HOOK_ACTIVE=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('true' if data.get('stop_hook_active', False) else 'false')
except Exception:
    print('false')
" 2>/dev/null || echo "false")

# If stop_hook_active is true, exit immediately to prevent infinite loop
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    exit 0
fi

# ── Setup ────────────────────────────────────────────────────────────────────
LOG_DIR="logs"
AUDIT_LOG="$LOG_DIR/audit_trail.log"
BLOCKED_LOG="$LOG_DIR/blocked_commands.log"
SESSION_REPORT="$LOG_DIR/session_reports.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$LOG_DIR"

# ── Count actions from audit log (since last session start) ──────────────────
COMMANDS_RUN=0
BLOCKED_COUNT=0

if [ -f "$AUDIT_LOG" ]; then
    # Count entries after the most recent session_started entry
    COMMANDS_RUN=$(tac "$AUDIT_LOG" 2>/dev/null | \
        awk '/session_started/{exit} {count++} END{print count}' || echo 0)
fi

if [ -f "$BLOCKED_LOG" ]; then
    # Count blocked entries today
    TODAY=$(date '+%Y-%m-%d')
    BLOCKED_COUNT=$(grep "^\[$TODAY" "$BLOCKED_LOG" 2>/dev/null | wc -l | tr -d ' ' || echo 0)
fi

# ── Write session report ──────────────────────────────────────────────────────
{
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  SESSION END REPORT — $TIMESTAMP"
    echo "════════════════════════════════════════════════════════════════"
    echo "  Commands executed this session : $COMMANDS_RUN"
    echo "  Blocked actions today          : $BLOCKED_COUNT"
    echo "  Audit log                      : $AUDIT_LOG"
    echo "  Blocked commands log           : $BLOCKED_LOG"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
} | tee -a "$SESSION_REPORT"

# Log session end to audit trail
echo "[$TIMESTAMP] | SESSION:end | TOOL:Stop | ACTION:session_ended | commands_run:$COMMANDS_RUN | blocked:$BLOCKED_COUNT" >> "$AUDIT_LOG" 2>/dev/null || true

exit 0
