# Security Guidelines
# FamOil Software Factory
# Version: 1.0 | Created: 2026-05-27

---

## 1. Password Policy

- All Odoo user passwords must be at least 12 characters
- Passwords must not be reused from previous instances or demo databases
- Admin password must be changed on every new deployment before go-live
- Database password (`db_password` in `odoo.conf`) must be unique per instance

**Storage:**
- Passwords stored only in `odoo.conf` (git-ignored)
- Never in scripts, documentation, commits, or any tracked file
- Use environment variables or a secrets manager for automation

---

## 2. User Access Levels

| Role             | Odoo Group                    | What They Can Do                           |
|-----------------|-------------------------------|--------------------------------------------|
| Admin            | Technical / Administrator     | Full access — restrict to 1–2 trusted users|
| Manager          | All apps — Manager level      | Approve MOs, view reports, configure       |
| Store Keeper     | Inventory / User              | Receipts, transfers, inventory adjustments |
| Plant Operator   | Manufacturing / User          | Create and complete manufacturing orders   |
| QC Officer       | Inventory / User              | Move stock to/from QC location             |
| Accountant       | Accounting / Accountant       | Journals, reconciliation, reports          |
| View Only        | All apps — Portal/Read-only   | Reports only, no modifications             |

**Principle of least privilege:** Grant the minimum access required for each role.

---

## 3. Audit Trail Requirements

Every significant action must be traceable:

- Manufacturing orders: Odoo logs MO creation, confirmation, and validation with user and timestamp
- Stock moves: all inventory moves create `stock.move` records with user attribution
- Accounting entries: every journal entry records the user who created it
- Claude Code sessions: all bash commands logged to `logs/audit_trail.log`
- Blocked governance actions: logged to `logs/blocked_commands.log` and `logs/blocked_writes.log`

Audit logs must be retained for a minimum of 1 year.
`logs/*.log` files are git-ignored (local operational records) — export to external storage for retention.

---

## 4. Sensitive Data Handling

**Never commit to the repository:**
- `odoo.conf` (contains `db_password`, `admin_passwd`)
- `.env` files of any kind
- API keys (ANTHROPIC_API_KEY, any cloud API)
- PostgreSQL connection strings with passwords
- SSH private keys
- Any file matching patterns in `.gitignore`

**What Claude Code must never output:**
- The contents of `odoo.conf`
- Any database password
- Any API key
- Any connection string containing credentials

If asked to show `odoo.conf`: show only the non-sensitive fields (addons_path, db_name, http_port, log_level).

---

## 5. Database Security

- PostgreSQL user `odoo` should have access only to Odoo databases (not system databases)
- PostgreSQL should not be exposed on a public network interface
- Use `pg_hba.conf` to restrict connections to localhost only for a single-machine deployment
- Database backups (`.sql` files) are git-ignored — store separately with access controls

---

## 6. File Permission Requirements

| Path                  | Required Permission | Reason                               |
|----------------------|---------------------|--------------------------------------|
| `.claude/hooks/*.sh`  | `chmod +x`          | Hook scripts must be executable      |
| `scripts/*.sh`        | `chmod +x`          | Operational scripts must be executable|
| `odoo.conf`           | `chmod 600`         | Contains credentials — owner only    |
| `logs/`               | `chmod 700`         | Audit logs — owner only              |

---

## 7. Security Scan — What the CI/CD Workflow Checks

The `security_scan.yml` workflow scans for these patterns on every push:
- `password\s*=` in `.py`, `.sh`, `.conf`, `.json`, `.env` files
- `passwd\s*=`
- `db_password`
- `ANTHROPIC_API_KEY\s*=`
- `SECRET_KEY\s*=`
- `-----BEGIN.*PRIVATE KEY-----`

If any of these are found in a push, the workflow will block the merge.
Remediate by removing the credential and rotating it immediately (the old credential
is now compromised even if removed from the file — it was in git history).
