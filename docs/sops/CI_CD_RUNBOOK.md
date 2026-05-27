# CI/CD Runbook
# FamOil Software Factory — Governance Engine Operations Reference
# Version: 1.0 | Created: 2026-05-27

---

## 1. Two-Layer Governance Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1 — SESSION HOOKS (.claude/settings.json)                │
│                                                                   │
│  Fires during every Claude Code session                          │
│  Runs independently of Claude's reasoning                        │
│  Blocks dangerous actions BEFORE they execute                    │
│  Logs every action to audit_trail.log                            │
│  Survives AI context loss                                        │
│                                                                   │
│  pre_tool_guard.sh     → blocks dangerous bash (exit 2)         │
│  file_protection.sh    → blocks protected writes (exit 2)       │
│  post_tool_validator   → validates written files (exit 0 warn)  │
│  audit_logger.sh       → logs every bash command (exit 0)       │
│  session_start_loader  → loads context at start (exit 0)        │
│  session_end_reporter  → summarises session (exit 0)            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2 — REPOSITORY CI/CD (.github/workflows/)                │
│                                                                   │
│  Fires on every git push and pull request                        │
│  Independent of any local session                                │
│  Provides team-wide enforcement                                  │
│  Blocks merges that violate governance rules                     │
│  Status: ACTIVE — remote connected, branch protection enabled   │
│                                                                   │
│  ci_review.yml       → Claude Code PR review on every PR        │
│  doc_lint.yml        → mandatory documents check on push        │
│  backup_check.yml    → weekly backup staleness alert            │
│  security_scan.yml   → credential scan on push                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Governance Rule Enforcement Matrix

| Rule | Description             | Layer 1 Hook                 | Layer 2 Workflow          |
|------|-------------------------|------------------------------|---------------------------|
| 1    | Documentation First     | `post_tool_validator.sh`     | `doc_lint.yml`            |
| 2    | Git Discipline          | `pre_tool_guard.sh` (push)   | Branch protection rules   |
| 3    | Modularity              | (documentation layer)        | `ci_review.yml`           |
| 4    | Minimize Custom Code    | (documentation layer)        | `ci_review.yml`           |
| 5    | Testing Discipline      | `post_tool_validator.sh`     | `ci_review.yml`           |
| 6    | Standardization         | `post_tool_validator.sh`     | `doc_lint.yml`            |
| 7    | Reusability             | (documentation layer)        | `ci_review.yml`           |
| 8    | Security                | `pre_tool_guard.sh` + `file_protection_guard.sh` | `security_scan.yml` |
| 9    | Reproducibility         | `audit_logger.sh`            | `backup_check.yml`        |
| 10   | Team Scalability        | `session_start_loader.sh`    | `doc_lint.yml`            |
| 11   | Automated Enforcement   | `.claude/settings.json`      | All workflows             |

---

## 3. How to Respond to a Failed CI Check

### doc_lint failure (missing mandatory document)
1. Identify the missing document from the workflow output
2. Create the document following the specification in `docs/IMPLEMENTATION_STANDARDS.md`
3. Ensure the document has a `# Title` heading (Rule 6)
4. Commit the document and push again

### security_scan failure (credential detected)
1. **Rotate the credential immediately** — it is now compromised
2. Remove the credential from the file
3. Verify it is not in git history: `git log -p --all | grep -i password`
4. If in history: use `git filter-branch` or BFG Repo-Cleaner (operator approval required)
5. Push the clean version and verify the workflow passes

### ci_review failure (governance rule violation)
1. Read the Claude Code review comment on the PR
2. Identify the rule violated and the file/line number
3. Correct the violation as specified
4. Push the fix to the same branch — the review reruns automatically

### backup_check failure (stale backup)
1. Run `bash scripts/backup_famoil.sh` to create a fresh backup
2. Commit the updated `BACKUP_MANIFEST.md` to the backups/ directory
3. The workflow checks for a manifest modified within 7 days

---

## 4. How to Add a New Governance Rule

1. Write the rule in `docs/IMPLEMENTATION_STANDARDS.md` (Layer 1 documentation)
2. Determine the lifecycle event (PreToolUse / PostToolUse / SessionStart / Stop)
3. Add the enforcement pattern to the appropriate hook script in `.claude/hooks/`
4. Create or extend a GitHub Actions workflow in `.github/workflows/` (Layer 2)
5. Update `docs/architecture/GOVERNANCE_ENGINE.md` — add row to Hook-to-Rule table
6. Update the enforcement matrix in this runbook (Section 2)
7. Record the decision in `docs/famoil_erp_template/DECISION_LOG.md`
8. Update `CLAUDE.md → GOVERNANCE ENGINE STATUS`

---

## 5. Secrets Management

**ANTHROPIC_API_KEY** — required for `ci_review.yml` (Claude Code PR review)
- Must be set in GitHub repository settings → Secrets and variables → Actions
- Name the secret exactly: `ANTHROPIC_API_KEY`
- Never commit this key to the repository
- Rotate every 90 days or immediately if exposed

**Database credentials** — stored only in `odoo.conf` (git-ignored)
- Never pass database passwords as command-line arguments in scripts
- Use environment variables in automated contexts

**Rotation procedure:**
1. Generate new credential
2. Update in all locations (odoo.conf, any environment variables)
3. Test connection with new credential
4. Revoke old credential
5. Record rotation in `logs/audit_trail.log` (manual entry)

---

## 6. Workflow Maintenance

### Updating workflow action versions
Periodically update pinned action versions (e.g. `actions/checkout@v4`):
1. Check for new versions on github.com/actions/checkout
2. Test in a feature branch before merging to main
3. Record the update in `docs/CHANGELOG.md`

### Testing workflows locally
Use `act` (https://github.com/nektos/act) to test GitHub Actions locally:
```bash
act push              # simulate a push event
act pull_request      # simulate a PR
act schedule          # simulate a scheduled trigger
```

### Disabling a workflow temporarily
1. Create a DECISION_LOG entry with reason and duration
2. Add `if: false` to the workflow's job or steps
3. Or rename the workflow file to `<name>.yml.disabled`
4. Re-enable within the stated timeframe
5. Add another DECISION_LOG entry confirming re-enablement
