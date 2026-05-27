# Governance Engine
# FamOil Software Factory — Two-Layer Enforcement Architecture
# Version: 1.0 | Created: 2026-05-27

---

## What This Document Is

Governance rules in this project exist at **two layers simultaneously**:

- **Layer 1 — Documentation** (`docs/IMPLEMENTATION_STANDARDS.md`, `CLAUDE.md`):
  Tells Claude what it *should* do. Guides reasoning and decisions during a session.
  Can be bypassed by an inattentive or context-lost AI session.

- **Layer 2 — Technical Enforcement** (`.claude/settings.json` + hook scripts, GitHub Actions):
  Defines what Claude *cannot bypass*. Fires deterministically regardless of Claude's
  reasoning. Survives AI context loss, developer replacement, and project pause.

A rule that exists only in documentation is a suggestion.
A rule that exists in both layers is a guarantee.

---

## Layer 1 — Session Hook System

Hooks fire during every Claude Code session via `.claude/settings.json`.
Hook scripts live in `.claude/hooks/` and are executed at specific lifecycle events.

### Hook-to-Rule Mapping

| Hook File                    | Lifecycle Event | Rule(s) Enforced    | Violation Action    |
|-----------------------------|-----------------|---------------------|---------------------|
| `pre_tool_guard.sh`          | PreToolUse      | Rule 1, 8, 9        | BLOCK (exit 2)      |
| `file_protection_guard.sh`   | PreToolUse      | Rule 1, 8           | BLOCK (exit 2)      |
| `post_tool_validator.sh`     | PostToolUse     | Rule 1, 6           | WARN (exit 0)       |
| `audit_logger.sh`            | PostToolUse     | Rule 8              | LOG (exit 0)        |
| `session_start_loader.sh`    | SessionStart    | Rule 10             | WARN (exit 0)       |
| `session_end_reporter.sh`    | Stop            | Rule 1              | LOG (exit 0)        |

### Exit Code Reference

| Exit Code | Meaning                                                        |
|-----------|----------------------------------------------------------------|
| 2         | BLOCK — action is physically prevented from executing          |
| 1         | WARN — action proceeds but warning is logged                   |
| 0         | ALLOW — action proceeds normally                               |

### Hook Script Summary

**`pre_tool_guard.sh`** — Intercepts every Bash tool call before execution.
Blocks: `rm -rf`, `DROP DATABASE`, `DELETE FROM` without WHERE, `TRUNCATE`,
config overwrites, force pushes, hard resets, and all `git push` until a remote is connected.
Logs every blocked command to `logs/blocked_commands.log`.

**`file_protection_guard.sh`** — Intercepts every Write/Edit call before execution.
Blocks: writes to `/etc/odoo/`, Odoo core source, `.env` files, credential files,
and any path outside the project repository root.
Logs every blocked write to `logs/blocked_writes.log`.

**`post_tool_validator.sh`** — Runs after every Write/Edit.
Checks: `.md` files have headings; `.sh` scripts are executable and have shebangs;
`.csv` files have headers; `.py` files flagged for manual review.
Appends results to `logs/validation_log.log`.

**`audit_logger.sh`** — Runs after every Bash execution.
Logs every command with timestamp, session ID, tool name, and action.
Rotates `logs/audit_trail.log` when it exceeds 10MB.

**`session_start_loader.sh`** — Fires at the start of every Claude Code session.
Checks CLAUDE.md and .claude/settings.json exist. Echoes ACTIVE PHASE,
CRITICAL RULES, and GOVERNANCE ENGINE STATUS from CLAUDE.md to the console.
Prints session start banner.

**`session_end_reporter.sh`** — Fires when Claude stops.
Generates session summary: commands run, blocked actions, files modified.
Appends to `logs/session_reports.log`. Checks `stop_hook_active` to prevent
infinite stop loops.

---

## Layer 2 — Repository CI/CD (GitHub Actions)

Workflows in `.github/workflows/` fire on every git push and pull request,
independent of any local development session. They enforce governance at the
repository boundary — nothing reaches `main` without passing all gates.

> **Status:** ACTIVE — remote connected 2026-05-27. All 4 workflows active.
> Branch protection on main enabled by operator 2026-05-27.

| Workflow File         | Trigger               | Purpose                                   |
|----------------------|-----------------------|-------------------------------------------|
| `ci_review.yml`       | Pull Request          | Claude Code reviews every PR for rule adherence |
| `doc_lint.yml`        | Push + PR to main     | Verifies all mandatory documents exist    |
| `backup_check.yml`    | Weekly schedule       | Alerts if backups are older than 7 days   |
| `security_scan.yml`   | Push + PR to main     | Scans for hardcoded credentials           |

### Branch Protection Rules (apply manually in GitHub repository settings)

These settings must be applied by the operator after the remote is connected:

- Require pull request before merging: **YES**
- Require 1 approval minimum
- Required status checks before merge:
  - `doc_lint` (Documentation Completeness Check)
  - `secret-scan` (Secret and Credential Scan)
  - `claude-review` (Claude Code PR Review)
- Require branches to be up to date: **YES**
- Allow bypassing: **NO** (including admins)
- Allow force pushes: **NO**
- Allow deletions: **NO**

---

## Audit Log Format

All logs are in `logs/` (git-ignored — local operational records only).

### `audit_trail.log`
```
[YYYY-MM-DD HH:MM:SS] | SESSION:<id> | TOOL:<name> | ACTION:<command>
```
Example:
```
[2026-05-27 09:15:33] | SESSION:abc123 | TOOL:Bash | ACTION:git status
[2026-05-27 09:15:41] | SESSION:abc123 | TOOL:SessionStart | ACTION:session_started
```

### `blocked_commands.log`
```
[YYYY-MM-DD HH:MM:SS] BLOCKED | COMMAND:<cmd> | REASON:<reason>
```

### `blocked_writes.log`
```
[YYYY-MM-DD HH:MM:SS] BLOCKED | FILE:<path> | REASON:<reason>
```

### `validation_log.log`
```
[YYYY-MM-DD HH:MM:SS] <STATUS> | FILE:<path> | <notes>
```
Status values: OK, WARN, REVIEW

### `session_reports.log`
Free-text session summary appended at each session end.

---

## How to Add a New Governance Rule

When a new rule is introduced, it must be enforced at both layers:

1. **Write it** in `docs/IMPLEMENTATION_STANDARDS.md` (Layer 1 documentation)
2. **Identify** which lifecycle event should enforce it (PreToolUse / PostToolUse / etc.)
3. **Add the pattern** to the appropriate hook script in `.claude/hooks/`
4. **Add or extend** a GitHub Actions workflow in `.github/workflows/` (Layer 2)
5. **Update this document** — add a row to the Hook-to-Rule Mapping table
6. **Record the decision** in `docs/famoil_erp_template/DECISION_LOG.md`
7. **Update CLAUDE.md** — GOVERNANCE ENGINE STATUS section

---

## How to Temporarily Disable a Hook

This is an operator-only procedure. Hooks must not be disabled without audit trail.

1. Open `docs/famoil_erp_template/DECISION_LOG.md`
2. Create a new DEC entry: state the hook being disabled, the reason, and the duration
3. Modify `.claude/settings.json` to comment out or remove the specific hook entry
4. Re-enable the hook after the stated condition is resolved
5. Add another DECISION_LOG entry confirming re-enablement

Never disable a BLOCK (exit 2) hook without explicit operator approval and a DEC entry.

---

## How to Test a Hook

Test hooks before relying on them by simulating their inputs:

```bash
# Test pre_tool_guard.sh with a blocked pattern
echo '{"tool_input": {"command": "rm -rf /tmp/test"}}' | .claude/hooks/pre_tool_guard.sh
# Expected: exit 2 and BLOCKED message

# Test file_protection_guard.sh
echo '{"tool_input": {"file_path": "/etc/odoo/odoo.conf"}}' | .claude/hooks/file_protection_guard.sh
# Expected: exit 2 and BLOCKED message

# Test audit_logger.sh
echo '{"tool_input": {"command": "git status"}, "session_id": "test123", "tool_name": "Bash"}' \
  | .claude/hooks/audit_logger.sh
# Expected: exit 0 and entry appended to logs/audit_trail.log
```
