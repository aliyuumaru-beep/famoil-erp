#!/usr/bin/env bash
# post_tool_validator.sh
# PURPOSE: Validate file changes after every write or edit.
# ENFORCES: Rule 1 (documentation completeness), Rule 6 (standardization).
# LIFECYCLE: PostToolUse — Write | Edit | MultiEdit
# EXIT CODES: 0 always (validators warn, they do not block)

set -euo pipefail

# ── Setup ────────────────────────────────────────────────────────────────────
LOG_DIR="logs"
VALIDATION_LOG="$LOG_DIR/validation_log.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$LOG_DIR"

# Read JSON from stdin
INPUT=$(cat)

# Extract file path from tool result
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tool_input = data.get('tool_input', data.get('input', {}))
    path = tool_input.get('file_path', tool_input.get('path', ''))
    print(path)
except Exception:
    print('')
" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

EXT="${FILE_PATH##*.}"
BASENAME=$(basename "$FILE_PATH")
STATUS="OK"
NOTES=""

# ── Validate Markdown files ───────────────────────────────────────────────────
if [[ "$EXT" == "md" ]]; then
    if [ ! -s "$FILE_PATH" ]; then
        STATUS="WARN"
        NOTES="Markdown file is empty — every .md file must have content"
        echo "VALIDATION WARN: $FILE_PATH — $NOTES" >&2
    elif ! head -5 "$FILE_PATH" | grep -qE "^#"; then
        STATUS="WARN"
        NOTES="Markdown file has no heading in first 5 lines — add a # heading"
        echo "VALIDATION WARN: $FILE_PATH — $NOTES" >&2
    fi
fi

# ── Validate shell scripts ────────────────────────────────────────────────────
if [[ "$EXT" == "sh" ]]; then
    if [ ! -x "$FILE_PATH" ]; then
        STATUS="WARN"
        NOTES="Shell script is not executable — run chmod +x $FILE_PATH"
        echo "VALIDATION WARN: $FILE_PATH — $NOTES" >&2
    fi
    if ! head -1 "$FILE_PATH" | grep -qE "^#!"; then
        STATUS="WARN"
        NOTES="Shell script missing shebang on line 1 (e.g. #!/usr/bin/env bash)"
        echo "VALIDATION WARN: $FILE_PATH — $NOTES" >&2
    fi
fi

# ── Validate CSV files ────────────────────────────────────────────────────────
if [[ "$EXT" == "csv" ]]; then
    if [ ! -s "$FILE_PATH" ]; then
        STATUS="WARN"
        NOTES="CSV file is empty — must have headers on row 1"
        echo "VALIDATION WARN: $FILE_PATH — $NOTES" >&2
    elif ! head -1 "$FILE_PATH" | grep -qE "[a-zA-Z]"; then
        STATUS="WARN"
        NOTES="CSV first row does not look like headers"
        echo "VALIDATION WARN: $FILE_PATH — $NOTES" >&2
    fi
fi

# ── Flag Python and addon files for manual review ────────────────────────────
if [[ "$EXT" == "py" ]] || [[ "$BASENAME" == "__manifest__.py" ]]; then
    STATUS="REVIEW"
    NOTES="Python/addon file written — flag for manual review before commit"
    echo "VALIDATION FLAG: $FILE_PATH — $NOTES" >&2
fi

# ── Append to validation log ──────────────────────────────────────────────────
echo "[$TIMESTAMP] $STATUS | FILE: $FILE_PATH | $NOTES" >> "$VALIDATION_LOG"

exit 0
