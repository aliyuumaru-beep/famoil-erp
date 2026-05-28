# Backup and Recovery
# FamOil Software Factory
# Version: 2.0 | Created: 2026-05-27 | Updated: 2026-05-28

> Backup format upgraded to PostgreSQL custom format (`pg_dump -F c`) on 2026-05-28.
> This resolved the ir_attachment restore failure identified in Restore Drill 1.
> Use `scripts/restore_famoil.sh` for all restores. Do NOT use raw `psql` against
> the new `.dump` files.

---

## Backup Schedule (Recommended)

| Frequency | Retention | Location              |
|-----------|-----------|----------------------|
| Daily     | 7 days    | Local machine        |
| Weekly    | 4 weeks   | External drive       |
| Monthly   | 12 months | Cloud / offsite      |

**Current status:** Automated daily backup via launchd (02:00 AM). Google Drive offsite sync
pending (rclone — requires `brew install rclone` + `rclone config gdrive`).

---

## Backup Format

| Property | Value |
|----------|-------|
| Format | PostgreSQL custom (`pg_dump -F c`) |
| File extension | `.dump` |
| Compression | Built-in (pg_dump compresses internally) |
| Typical size | ~6MB (vs 17MB for plain format) |
| Restore tool | `pg_restore --disable-triggers` |
| Attachment support | Full — `ir_attachment` restores correctly |

**Why custom format?** The previous plain-text format (`-F p`) had a circular FK dependency
between `account_move` and `ir_attachment` that caused all 875 attachment records to fail
to restore. Identified in Restore Drill 1 (2026-05-28). Custom format with
`--disable-triggers` resolves this completely.

---

## Quick Backup

```bash
bash /Users/mac/odoo17/scripts/backup_famoil.sh
```

Creates a timestamped directory under `/Users/mac/odoo_backups/` containing:

| File/Dir | Description |
|----------|-------------|
| `Famoil.dump` | PostgreSQL custom-format dump — use `pg_restore` to restore |
| `filestore/` | Odoo binary attachments (hashed directory structure) |
| `odoo.conf` | Server config (passwords stripped) |
| `custom_addons/` | All custom and third-party modules |
| `docs/` | Documentation snapshot |
| `scripts/` | Utility scripts |
| `BACKUP_MANIFEST.md` | Backup record |

Also produces:
- `famoil_YYYYMMDD_HHMM.tar.gz` — compressed archive of the whole backup directory
- `backups/BACKUP_MANIFEST.md` — governance bridge (commit after each run)
- `logs/retention_report.log` — retention dry-run report (no deletions)

### Governance Bridge

After running the backup, commit the governance bridge manifest:

```bash
git add backups/BACKUP_MANIFEST.md
git commit -m "chore: update backup manifest $(date '+%Y-%m-%d')"
```

---

## Quick Restore

```bash
bash /Users/mac/odoo17/scripts/restore_famoil.sh /path/to/backup/dir
```

Default target: `FamOilRestoreTest` (isolated — never touches production).

For production recovery:
```bash
bash /Users/mac/odoo17/scripts/restore_famoil.sh /path/to/backup/dir --production
```

The script will prompt for `CONFIRM` before touching the production database.

---

## Backup Log

| Date-Time         | Format   | Path                                              | Notes                                     |
|------------------|----------|--------------------------------------------------|-------------------------------------------|
| 2026-05-22 11:33 | plain-F-p| `/Users/mac/odoo_backups/famoil_20260522_1133`   | Phase 1 baseline                          |
| 2026-05-27 21:03 | plain-F-p| `/Users/mac/odoo_backups/famoil_20260527_2103`   | Pre-governance backup                     |
| 2026-05-28 00:33 | plain-F-p| `/Users/mac/odoo_backups/famoil_20260528_0033`   | Restore Drill 1 source — LEGACY FORMAT    |
| 2026-05-28 18:14 | custom-Fc| `/Users/mac/odoo_backups/famoil_20260528_1814`   | First custom-format backup — CURRENT      |

> Backups marked `plain-F-p` cannot reliably restore `ir_attachment`. Use the
> 2026-05-28 18:14 backup or later for a complete restore.

---

## Manual Backup Steps

### 1. PostgreSQL Database Dump (custom format)

```bash
pg_dump -U odoo -d "Famoil" -F c -f "/path/to/backup/Famoil.dump"
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

## Recovery Procedure (Standard — Test Environment)

> For production recovery, use `scripts/restore_famoil.sh` with `--production`.

### 1. Create target database

```bash
createdb -U odoo -E UTF8 FamOilRestoreTest --no-password
```

### 2. Restore database (custom format)

```bash
pg_restore \
  -U odoo \
  -d FamOilRestoreTest \
  --disable-triggers \
  --no-owner \
  --no-privileges \
  -j 4 \
  -F c \
  /path/to/backup/Famoil.dump
```

`--disable-triggers` disables FK constraint triggers during load, resolving circular
dependency between `account_move` and `ir_attachment`. Requires the `odoo` user to
be a superuser (it is, per `\du odoo`).

### 3. Restore filestore

```bash
cp -r /path/to/backup/filestore/ \
      "/Users/mac/Library/Application Support/Odoo/filestore/FamOilRestoreTest/"
```

### 4. Validate

```bash
psql -U odoo -d FamOilRestoreTest -c "
SELECT 'ir_attachment', COUNT(*) FROM ir_attachment
UNION ALL SELECT 'mrp_production', COUNT(*) FROM mrp_production
UNION ALL SELECT 'stock_quant', COUNT(*) FROM stock_quant;"
```

Expected: `ir_attachment` = 875, other counts match production snapshot.

### 5. Validate Odoo starts

```bash
source /Users/mac/odoo17/odoo/venv/bin/activate
python /Users/mac/odoo17/odoo/odoo-bin -d FamOilRestoreTest -r odoo \
  --addons-path=/Users/mac/odoo17/odoo/odoo/addons,/Users/mac/odoo17/custom_addons,/Users/mac/oca_web \
  --stop-after-init --no-http
```

Expected: `83 modules loaded in ~2.5s, 0 queries`.

### 6. Clean up

```bash
dropdb -U odoo FamOilRestoreTest
rm -rf "/Users/mac/Library/Application Support/Odoo/filestore/FamOilRestoreTest"
```

---

## Post-Restore Verification Checklist

- [ ] `ir_attachment` count matches production (875 records)
- [ ] PDF attachments accessible via Odoo `/web/content/{id}` endpoint
- [ ] Odoo starts without errors (0 CRITICAL/ERROR in log)
- [ ] Manufacturing → Bills of Materials shows BOM 10 and BOM 15
- [ ] Inventory → Products shows Crude Soya Oil, Refined Soya Oil, SoyaBean
- [ ] Stock quants match expected values (RM Warehouse 1,000 kg, Crude Oil Tanks, etc.)
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

---

## Restore Drill History

| Drill | Date | Backup Source | ir_attachment | Outcome |
|-------|------|--------------|---------------|---------|
| Drill 1 | 2026-05-28 | famoil_20260528_0033 (plain) | 0/875 FAIL | Format changed to custom |
| Drill 2 | 2026-05-28 | famoil_20260528_1814 (custom) | 875/875 PASS | Full pass — PDF served OK |

See: `docs/operations/RESTORE_DRILL.md` for full drill reports.
