# FamOil — Backup and Restore Procedures

## Backup Structure

```
/Users/mac/odoo_backups/famoil_YYYYMMDD_HHMM/
├── Famoil.sql          # Full PostgreSQL plain-text dump
├── filestore/          # Attachments and binary files
├── odoo.conf           # Config file (passwords stripped)
├── custom_addons/      # All custom/third-party addons
├── docs/               # Documentation snapshot
├── scripts/            # Utility scripts
└── BACKUP_MANIFEST.md  # Backup record
```

## Quick Backup (Automated)

```bash
bash /Users/mac/odoo17/scripts/backup_famoil.sh
```

The script creates a timestamped directory under `/Users/mac/odoo_backups/` with all components.

## Manual Backup Steps

### 1. PostgreSQL Dump
```bash
pg_dump -U odoo -d "Famoil" -F p -f "/path/to/backup/Famoil.sql"
```

Options:
- `-F p` — plain text SQL (human-readable, portable)
- `-F c` — custom compressed format (faster restore, smaller)

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

## Restore Procedure

> STOP the Odoo server before restoring.

### 1. Restore Database
```bash
# Drop existing (if needed — confirm first!)
# dropdb -U odoo "Famoil"

# Recreate
createdb -U odoo -E UTF8 "Famoil"

# Restore
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
# Run from /Users/mac/odoo17 — NOT from inside the odoo subdirectory
source /Users/mac/odoo17/odoo/venv/bin/activate
python /Users/mac/odoo17/odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=/Users/mac/odoo17/odoo/odoo/addons,/Users/mac/odoo17/custom_addons,/Users/mac/oca_web
```

## Backup Log

| Date-Time        | Type       | Path                                    | DB Size | Notes                     |
|-----------------|------------|-----------------------------------------|---------|---------------------------|
| 2026-05-22 11:33 | Full Manual | /Users/mac/odoo_backups/famoil_20260522_1133 | 16MB | Phase 1 pre-change backup |

## Retention Policy (Recommended — Not Yet Configured)

- Keep daily backups for 7 days
- Keep weekly backups for 4 weeks
- Keep monthly backups for 12 months
- Store off-machine (external drive or cloud) for at least weekly backups
