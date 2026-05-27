#!/usr/bin/env bash
# session_start_loader.sh
# PURPOSE: Load project context at the start of every session.
# ENFORCES: Rule 10 (team scalability), AI context loss survival.
# LIFECYCLE: SessionStart
# EXIT CODES: 0 always (warns on issues, never blocks session start)

# Note: Do not use set -e here — we want to continue even if checks fail

# ── Setup ────────────────────────────────────────────────────────────────────
LOG_DIR="logs"
CLAUDE_MD="CLAUDE.md"
SETTINGS_JSON=".claude/settings.json"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$LOG_DIR"

# ── Session start banner ──────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  SOFTWARE FACTORY SESSION STARTED"
echo "  Project: FamOil Industrial ERP Framework"
echo "  Timestamp: $TIMESTAMP"
echo "  Governance hooks: ACTIVE"
echo "  Audit log: $LOG_DIR/audit_trail.log"
echo "============================================================"
echo ""

# ── Check CLAUDE.md exists ────────────────────────────────────────────────────
if [ ! -f "$CLAUDE_MD" ]; then
    echo "⚠️  WARNING: CLAUDE.md not found at repo root."
    echo "   Create CLAUDE.md before proceeding — it is the session memory anchor."
    echo ""
else
    echo "✓ CLAUDE.md found"

    # Extract and display ACTIVE PHASE section
    echo ""
    echo "── ACTIVE PHASE ─────────────────────────────────────────────"
    awk '/^## ACTIVE PHASE/,/^## [A-Z]/' "$CLAUDE_MD" | head -20 | grep -v "^## [A-Z][A-Z]" || true
    echo ""

    # Extract and display CRITICAL RULES section
    echo "── CRITICAL RULES ────────────────────────────────────────────"
    awk '/^## CRITICAL RULES/,/^## [A-Z]/' "$CLAUDE_MD" | head -20 | grep -v "^## [A-Z][A-Z]" || true
    echo ""

    # Extract and display GOVERNANCE ENGINE STATUS
    echo "── GOVERNANCE ENGINE STATUS ──────────────────────────────────"
    awk '/^## GOVERNANCE ENGINE STATUS/,/^## [A-Z]/' "$CLAUDE_MD" | head -20 | grep -v "^## [A-Z][A-Z]" || true
    echo ""
fi

# ── Check .claude/settings.json exists ───────────────────────────────────────
if [ ! -f "$SETTINGS_JSON" ]; then
    echo "⚠️  WARNING: .claude/settings.json not found."
    echo "   Hook system is not configured. Governance enforcement is inactive."
    echo ""
else
    echo "✓ .claude/settings.json found — hook system active"
fi

# ── Ensure logs/ directory exists ────────────────────────────────────────────
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    echo "✓ logs/ directory created"
else
    echo "✓ logs/ directory exists"
fi

echo ""
echo "============================================================"
echo "  Session ready. Governance engine active. Proceed carefully."
echo "============================================================"
echo ""

# Log session start to audit trail
echo "[$TIMESTAMP] | SESSION:new | TOOL:SessionStart | ACTION:session_started" >> "$LOG_DIR/audit_trail.log" 2>/dev/null || true

exit 0
