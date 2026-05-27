# Backup and Recovery
# FamOil Software Factory
# Version: 1.1 | Created: 2026-05-27 | Updated: 2026-05-27

> This document supersedes `docs/famoil_erp_template/BACKUP_AND_RESTORE.md`
> for the purposes of the mandatory document checklist.
> Full operational backup procedures are in BACKUP_AND_RESTORE.md.

---

## Backup Schedule (Recommended)

| Frequency | Retention | Location              |
|-----------|-----------|----------------------|
| Daily     | 7 days    | Local machine        |
| Weekly    | 4 weeks   | External drive       |
| Monthly   | 12 months | Cloud / offsite      |

**Current status:** Manual backups only. Automated scheduling pending (launchd — Phase 3 of backup governance).
Google Drive offsite sync pending (rclone — Phase 3 of backup governance).

---

## Quick Backup (Automated Script)

```bash
bash /Users/mac/odoo17/scripts/backup_famoil.sh
```

Creates a timestamped directory under `/Users/mac/odoo_backups/` containing:
- `Famoil.sql` — full PostgreSQL plain-text dump
- `filestore/` — attachments and binary files
- `odoo.conf` — config file (passwords stripped)
- `custom_addons/` — all custom modules
- `docs/` — documentation snapshot
- `scripts/` — utility scripts
- `BACKUP_MANIFEST.md` — backup record

Also produces:
- `famoil_YYYYMMDD_HHMM.tar.gz` — compressed archive (controlled by `COMPRESS` variable)
- `backups/BACKUP_MANIFEST.md` — governance bridge in the repository (commit after each run)
- `logs/retention_report.log` — retention dry-run report (no deletions)

### Governance Bridge

After running the backup, commit the governance bridge manifest so `backup_check.yml` can validate:

```bash
git add backups/BACKUP_MANIFEST.md
git commit -m "chore: update backup manifest $(date '+%Y-%m-%d')"
```

---

## Backup Log

| Date-Time         | Type         | Path                                            | Notes                                       |
|------------------|--------------|------------------------------------------------|---------------------------------------------|
| 2026-05-22 11:33 | Full Manual  | `/Users/mac/odoo_backups/famoil_20260522_1133` | Phase 1 pre-change baseline                 |
| 2026-05-27 —     | **REQUIRED** | —                                              | Fresh backup needed — 5 days of work since last |

---

## Manual Backup Steps

### 1. PostgreSQL Database Dump
```bash
pg_dump -U odoo -d "Famoil" -F p -f "/path/to/backup/Famoil.sql"
```

### 2. Filestore
```bash
cp -r "/Users/mac/Library/Application Support/Odoo/filestore/Famoil/" \
      "/path/to/backup/filestore/"
```

### 3. Config (strip passwords)
```bash
grep -v "password\|passwd\|pwd\|secret" \
  /Users/mac/odoo17/odoo/odoo.conf \
  > /path/to/backup/odoo.conf
```

### 4. Custom Addons
```bash
cp -r /Users/mac/odoo17/custom_addons/ /path/to/backup/custom_addons/
```

---

## Recovery Procedure

> STOP the Odoo server before restoring.

### 1. Restore Database
```bash
# Confirm first — this will overwrite the existing database
createdb -U odoo -E UTF8 "Famoil"
psql -U odoo -d "Famoil" -f "/path/to/backup/Famoil.sql"
```

### 2. Restore Filestore
```bash
cp -r "/path/to/backup/filestore/" \
      "/Users/mac/Library/Application Support/Odoo/filestore/Famoil/"
```

### 3. Restore Custom Addons
```bash
cp -r /path/to/backup/custom_addons/ /Users/mac/odoo17/custom_addons/
```

### 4. Restart Odoo
```bash
# Run from /Users/mac/odoo17
source odoo/venv/bin/activate
python odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web
```

### 5. Verify After Restore
- [ ] Odoo starts without errors
- [ ] Can log in as admin
- [ ] Manufacturing → Bills of Materials shows BOM 10 and BOM 15
- [ ] Inventory → Products shows Crude Soya Oil, Refined Soya Oil, SoyaBean
- [ ] Stock quants match backup snapshot (check COSTING_VALIDATION.md Section 8)
- [ ] Custom modules installed: `stock_crude_oil_tank_restriction`, `mrp_component_availability_check`

---

## Pre-Action Backup Requirement

A backup MUST be taken before any of the following:
- Phase progression (before starting any new phase)
- Database structure changes
- Custom module installation or upgrade
- Bulk stock adjustments
- Chart of accounts changes

Do not skip this. The backup is the rollback. Without it, recovery may be impossible.
