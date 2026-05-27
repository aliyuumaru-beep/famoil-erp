#!/usr/bin/env bash
# pre_tool_guard.sh
# PURPOSE: Block dangerous bash commands before execution.
# ENFORCES: Rule 1 (no undocumented changes), Rule 8 (security),
#           Rule 9 (no destructive ops on live instance).
# LIFECYCLE: PreToolUse — Bash
# EXIT CODES: 2 = BLOCK action | 1 = warn only | 0 = allow

set -euo pipefail

# ── Setup ────────────────────────────────────────────────────────────────────
LOG_DIR="logs"
BLOCKED_LOG="$LOG_DIR/blocked_commands.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$LOG_DIR"

# Read JSON from stdin (Claude Code passes tool context as JSON)
INPUT=$(cat)

# Extract the bash command from the JSON input
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Tool input is in tool_input or input field
    tool_input = data.get('tool_input', data.get('input', {}))
    cmd = tool_input.get('command', '')
    print(cmd)
except Exception:
    print('')
" 2>/dev/null || echo "")

if [ -z "$COMMAND" ]; then
    exit 0
fi

# ── Destructive pattern definitions ──────────────────────────────────────────
# Each entry: "pattern|reason"
BLOCKED_PATTERNS=(
    "rm -rf|Recursive force delete is prohibited without operator approval"
    "DROP DATABASE|Database drop is prohibited — take a backup first and get operator approval"
    "DROP TABLE|Table drop is prohibited — use migrations, not raw drops"
    "DELETE FROM [a-zA-Z].*;?\s*$|DELETE without WHERE clause is prohibited — would wipe entire table"
    "TRUNCATE|TRUNCATE is prohibited — would wipe entire table"
    "> odoo\.conf|Overwriting odoo.conf is prohibited — credentials and config would be lost"
    "git push --force|Force push is prohibited — would overwrite remote history"
    "git push -f |Force push is prohibited — would overwrite remote history"
    "git reset --hard|Hard reset discards uncommitted work — get operator approval first"
    "git clean -f|Force clean deletes untracked files — get operator approval first"
    "dropdb|Database drop is prohibited — take a backup first and get operator approval"
    "pg_restore.*--clean|Restore with --clean drops existing objects — operator approval required"
)

# ── Phase 1 gate: block git push entirely during Phase 1 ─────────────────────
# Check CLAUDE.md for current phase — if Phase 4 or below is not approved, block push
if echo "$COMMAND" | grep -qE "^git push"; then
    REASON="git push is blocked: no remote repository has been connected yet. Connect a remote and get operator approval before pushing."
    echo "BLOCKED: $REASON" >&2
    echo "[$TIMESTAMP] BLOCKED | COMMAND: $COMMAND | REASON: $REASON" >> "$BLOCKED_LOG"
    exit 2
fi

# ── Check each destructive pattern ───────────────────────────────────────────
for ENTRY in "${BLOCKED_PATTERNS[@]}"; do
    PATTERN="${ENTRY%%|*}"
    REASON="${ENTRY##*|}"

    if echo "$COMMAND" | grep -qiE "$PATTERN"; then
        echo "" >&2
        echo "╔══════════════════════════════════════════════════════════════╗" >&2
        echo "║  GOVERNANCE BLOCK — pre_tool_guard.sh                       ║" >&2
        echo "╚══════════════════════════════════════════════════════════════╝" >&2
        echo "BLOCKED COMMAND: $COMMAND" >&2
        echo "REASON: $REASON" >&2
        echo "To proceed: get explicit operator approval and document the decision in DECISION_LOG.md" >&2
        echo "" >&2

        echo "[$TIMESTAMP] BLOCKED | COMMAND: $COMMAND | REASON: $REASON" >> "$BLOCKED_LOG"
        exit 2
    fi
done

# ── Log allowed command for auditability ─────────────────────────────────────
# (audit_logger.sh handles full PostToolUse logging; this just tracks guards passed)
exit 0
