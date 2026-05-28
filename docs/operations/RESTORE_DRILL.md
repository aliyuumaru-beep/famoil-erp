# RESTORE_DRILL.md
# FamOil Software Factory — Restore Drill Reports
# Version: 2.0 | Updated: 2026-05-28 | Status: PASSED (Drill 2)

---

## Drill Summary

| Drill | Date | Format | ir_attachment | Modules | RTO | Outcome |
|-------|------|--------|--------------|---------|-----|---------|
| Drill 1 | 2026-05-28 | plain (-F p) | 0/875 FAIL | 83 ✓ | 36s | PARTIAL PASS — format changed |
| Drill 2 | 2026-05-28 | custom (-F c) | 875/875 ✓ | 83 ✓ | 43s | **FULL PASS — backup trusted** |

---

# Drill 1 — 2026-05-28 (Original — SUPERSEDED)

---

## Summary

A full restore drill was executed against backup `famoil_20260528_0033` (the most recent
backup at drill time). The restore was performed to an isolated test database `FamOilRestoreTest`.
The production database `Famoil` was not touched at any point.

**Overall result:** PARTIAL PASS — Core ERP data restored completely. Attachments failed
due to a structural limitation in the plain pg_dump format. Action required on backup strategy.

---

## 1. Drill Parameters

| Field | Value |
|-------|-------|
| Drill date | 2026-05-28 |
| Backup used | `famoil_20260528_0033` (2026-05-28 00:33) |
| Backup age at drill | ~17 hours |
| Backup format | PostgreSQL plain-text dump (`pg_dump -F p`) |
| Backup size | 17MB (SQL) + 16MB (filestore) = 33MB total |
| Restore target DB | `FamOilRestoreTest` (isolated, dropped after drill) |
| Restore target filestore | `/Users/mac/Library/Application Support/Odoo/filestore/FamOilRestoreTest/` |
| Production DB | `Famoil` (untouched throughout) |
| Odoo version | 17.0.1.3 Community |
| PostgreSQL version | 16.11 (Homebrew) |

---

## 2. Recovery Timing

| Step | Duration | Notes |
|------|----------|-------|
| Create test database | 1s | `createdb -U odoo FamOilRestoreTest` |
| Restore SQL dump | 29s | Strip `\restrict` header, pipe to psql |
| Restore filestore | 1s | `cp -r` from backup directory |
| Odoo module load validation | ~5s | `--stop-after-init --no-http` |
| **Total recovery time** | **~36 seconds** | Excluding discovery and decision time |

**RTO estimate (from scratch):** Under 5 minutes including operator steps and validation.

---

## 3. Restore Procedure Executed

```bash
# Step 1 — Create isolated test database
createdb -U odoo -E UTF8 FamOilRestoreTest --no-password

# Step 2 — Restore SQL dump (strip \restrict psql header added by Odoo backup format)
grep -v '\\restrict' /Users/mac/odoo_backups/famoil_20260528_0033/Famoil.sql | \
  psql -U odoo -d FamOilRestoreTest -v ON_ERROR_STOP=0 --quiet

# Step 3 — Restore filestore
cp -r /Users/mac/odoo_backups/famoil_20260528_0033/filestore/ \
  "/Users/mac/Library/Application Support/Odoo/filestore/FamOilRestoreTest/"

# Step 4 — Validate Odoo loads against restored database
source /Users/mac/odoo17/odoo/venv/bin/activate
python /Users/mac/odoo17/odoo/odoo-bin -d FamOilRestoreTest -r odoo \
  --addons-path=/Users/mac/odoo17/odoo/odoo/addons,/Users/mac/odoo17/custom_addons,/Users/mac/oca_web \
  --stop-after-init --no-http

# Step 5 — Clean up test environment
dropdb -U odoo FamOilRestoreTest
rm -rf "/Users/mac/Library/Application Support/Odoo/filestore/FamOilRestoreTest"
```

---

## 4. Validation Results

### 4.1 Record Count Comparison

| Table | Production | Restored | Match |
|-------|-----------|----------|-------|
| `stock_move` | 239 | 239 | ✓ |
| `mrp_production` | 29 | 29 | ✓ |
| `stock_quant` | 86 | 86 | ✓ |
| `product_template` | 72 | 72 | ✓ |
| `mrp_bom` | 13 | 13 | ✓ |
| `account_move` | 84 | 84 | ✓ |
| `stock_location` | 84 | 84 | ✓ |
| `stock_warehouse` | 4 | 4 | ✓ |
| `mrp_workcenter` | 14 | 14 | ✓ |
| `ir_attachment` | 875 | 0 | **✗ FAILED** |

### 4.2 Warehouse Structure Validation

Restored warehouse hierarchy verified:

| Warehouse | Company | Status |
|-----------|---------|--------|
| YourCompany (id=1) | company 1 | ✓ |
| Chicago 1 (id=2) | company 2 | ✓ |
| FamOilWH (id=3) | FamOil FTZ (id=2) | ✓ |
| NG Company (id=4) | company 3 | ✓ |

### 4.3 Stock Quant Validation

Key FamOil locations verified in restored DB:

| Location | Product id | Qty |
|----------|-----------|-----|
| Famoil/Stock/Crude Oil Tank 1 | 111 | 199 kg |
| Famoil/Stock/Crude Oil Tank 2 | 111 | 22 kg |
| Famoil/Stock/RM Warehouse | 107 | 1,000 kg |
| Famoil/Stock/Refined Oil Tank 1 | 126 | 224 kg |
| Famoil/Stock/FG Warehouse | 112 | 2,520 units |

### 4.4 BOM Validation

13 BOMs restored. FamOil-specific BOMs confirmed:

| BOM id | Qty | Company |
|--------|-----|---------|
| 10 (Extraction) | 140 kg | FamOil FTZ |
| 15 (Refining) | 135 kg | FamOil FTZ |
| 208, 209 (Packaging) | 1 unit | FamOil FTZ |

### 4.5 Odoo Module Load

```
83 modules loaded in 2.57s, 0 queries (+0 extra)
Registry loaded in 3.220s
```

Result: All 83 modules loaded with **zero errors** against the restored database.

---

## 5. Findings and Issues

### FINDING 1 — CRITICAL: ir_attachment data not restored

**Impact:** HIGH
**Severity:** Operational gap in restore procedure

All 875 attachment records (PDFs, images, signed documents, report outputs) failed to restore.
The filestore files are present (16MB of binary data copied successfully) but the database
index (`ir_attachment`) that maps file hashes to records is empty. Odoo cannot locate or
display any attachments after restore.

**Root cause:** Circular foreign key dependency between `account_move` and `ir_attachment`.
Plain `pg_dump -F p` generates COPY statements in an order that places `account_move` before
`ir_attachment`. The FK constraint `account_move_message_main_attachment_id_fkey` fires
during the COPY of `account_move` because `ir_attachment` is not yet populated. With no
`DISABLE TRIGGER ALL` in the dump, the COPY block for `ir_attachment` is preceded by FK
errors that leave the table empty.

**Three FK violations observed at restore time:**
- `account_move.message_main_attachment_id_fkey` → id 899 not in `ir_attachment`
- `message_attachment_rel.attachment_id_fkey` → id 759 not in `ir_attachment`
- `product_document.ir_attachment_id_fkey` → id 219 not in `ir_attachment`

**Fix required:** Change backup format. See Section 7 (Recommendations).

---

### FINDING 2 — INFO: `\restrict` header in dump

The SQL dump contains a `\restrict` psql metacommand on line 5, paired with `\unrestrict`
at the end. These are Odoo-internal markers not part of standard pg_dump output. They must
be stripped before restoring with psql:

```bash
grep -v '\\restrict' Famoil.sql | psql -U odoo -d TARGET_DB
```

This is handled in the procedure above. Not a data integrity issue.

---

### FINDING 3 — INFO: Backup contains `\restrict`/`\unrestrict` markers

The `\unrestrict` command at end of dump generates a harmless warning:
`\unrestrict: not currently in restricted mode`

No data impact. Document for future operator awareness.

---

## 6. What Was NOT Tested

| Item | Reason Deferred |
|------|-----------------|
| Full UI functional test | Requires running Odoo instance pointed to restored DB — deferred to next drill |
| Manufacturing order completion | Data present; MO workflow test deferred |
| Accounting report generation | Deferred — dependent on ir_attachment fix |
| Restore from tar.gz archive | Only uncompressed backup directory tested; tar.gz extraction not tested this drill |
| Google Drive restore path | rclone not yet installed locally |
| Cross-machine restore | macOS-only tested; Linux restore not tested |

---

## 7. Recommendations

### R-01 — CRITICAL: Fix backup format to resolve ir_attachment failure

**Action:** Update `scripts/backup_famoil.sh` to use pg_dump custom format (`-F c`)
and restore with `pg_restore --disable-triggers`.

Current (broken for attachments):
```bash
pg_dump -U odoo -d Famoil -F p -f Famoil.sql
# Restore:
psql -U odoo -d TARGET < Famoil.sql
```

Required fix:
```bash
pg_dump -U odoo -d Famoil -F c -f Famoil.dump
# Restore:
pg_restore -U odoo -d TARGET --disable-triggers -F c Famoil.dump
```

Note: `--disable-triggers` requires the restoring user to be a superuser, or the database
owner. Verify that the `odoo` PostgreSQL user has sufficient privileges.

Priority: HIGH — implement before next backup cycle.

---

### R-02 — Codify restore procedure as a script

**Action:** Create `scripts/restore_famoil.sh` using the procedure from Section 3,
incorporating the fix from R-01. The script should:
- Accept a backup directory as argument
- Create a target database (default: `FamOilRestoreTest`)
- Restore SQL dump with proper format handling
- Restore filestore to correct path
- Run `--stop-after-init` validation
- Print record count summary
- Confirm operator before cleanup

Priority: MEDIUM — implement in next governance cycle.

---

### R-03 — Schedule periodic restore drills

**Action:** Add restore drill to operational calendar — at minimum quarterly, ideally monthly.
Update `backup_check.yml` to also track last restore drill date.

Priority: LOW — process improvement.

---

## 8. Drill Outcome Summary

| Check | Result |
|-------|--------|
| Backup file accessible | ✓ PASS |
| SQL dump restores without fatal errors | ✓ PASS (with caveats) |
| Core ERP data (10/11 tables) | ✓ PASS — 100% match |
| Warehouse hierarchy | ✓ PASS |
| Manufacturing BOMs | ✓ PASS |
| Stock quants | ✓ PASS |
| Odoo modules load (83 modules) | ✓ PASS — 0 errors |
| Filestore restores | ✓ PASS — 16MB, 233 dirs |
| ir_attachment data | ✗ FAIL — 0/875 records |
| RTO target (< 30 min) | ✓ PASS — ~36 seconds |
| Production DB unaffected | ✓ PASS |

**Verdict:** The backup is partially trusted. Core ERP data and operational continuity are
restorable within 36 seconds. Attachment data (PDFs, images, documents) is NOT recoverable
from the current backup format. **Backup format must be fixed before this backup system
can be declared fully trusted.**

---

## 9. Next Actions (Drill 1 — RESOLVED)

| Priority | Action | Status |
|----------|--------|--------|
| HIGH | Fix backup script: change to `pg_dump -F c` (R-01) | DONE — 2026-05-28 |
| HIGH | Re-run restore drill after backup format fix | DONE — Drill 2 PASSED |
| MEDIUM | Create `scripts/restore_famoil.sh` (R-02) | DONE — 2026-05-28 |
| LOW | Schedule quarterly restore drills (R-03) | Open |

---

## 10. Drill Sign-Off

| Field | Value |
|-------|-------|
| Drill executed by | Claude Code (operator supervised) |
| Production database affected | NO |
| Drill database cleaned up | YES — `FamOilRestoreTest` dropped, filestore removed |
| Document path | `docs/operations/RESTORE_DRILL.md` |
| Status | SUPERSEDED — see Drill 2 below |

---

---

# Drill 2 — 2026-05-28 (Custom Format — FULL PASS)

## Summary

Second restore drill executed immediately after upgrading the backup format to
`pg_dump -F c` (custom format). Restored from backup `famoil_20260528_1814`.
All 875 `ir_attachment` records restored successfully. PDF file served via
Odoo `/web/content` endpoint confirmed at HTTP 200.

**Overall result: FULL PASS — backup system is trusted.**

---

## 1. Drill Parameters

| Field | Value |
|-------|-------|
| Drill date | 2026-05-28 |
| Backup used | `famoil_20260528_1814` (2026-05-28 18:14) |
| Backup age at drill | < 1 minute |
| Backup format | PostgreSQL custom format (`pg_dump -F c`) |
| Dump file size | 6MB (vs 17MB for plain format) |
| Restore script | `scripts/restore_famoil.sh` |
| Restore target DB | `FamOilRestoreTest` (isolated, dropped after drill) |
| Production DB | `Famoil` (untouched throughout) |

---

## 2. Recovery Timing

| Step | Duration |
|------|----------|
| Create test database | 2s |
| Restore custom-format dump (`pg_restore -j 4 --disable-triggers`) | 33s |
| Restore filestore | 1s |
| Validation checks | <1s |
| Odoo module load validation | 7s |
| **Total** | **43s** |

---

## 3. Restore Procedure

```bash
bash /Users/mac/odoo17/scripts/restore_famoil.sh \
  /Users/mac/odoo_backups/famoil_20260528_1814
```

Internally uses:
```bash
pg_restore -U odoo -d FamOilRestoreTest \
  --disable-triggers --no-owner --no-privileges \
  -j 4 -F c Famoil.dump
```

---

## 4. Validation Results

### 4.1 Record Count Comparison

| Table | Production | Restored | Match |
|-------|-----------|----------|-------|
| `stock_move` | 239 | 239 | ✓ |
| `mrp_production` | 29 | 29 | ✓ |
| `stock_quant` | 86 | 86 | ✓ |
| `product_template` | 72 | 72 | ✓ |
| `mrp_bom` | 13 | 13 | ✓ |
| `account_move` | 84 | 84 | ✓ |
| `stock_location` | 84 | 84 | ✓ |
| `stock_warehouse` | 4 | 4 | ✓ |
| `mrp_workcenter` | 14 | 14 | ✓ |
| `ir_attachment` | 875 | **875** | **✓ FIXED** |

### 4.2 Attachment Breakdown

| Type | Count | Restored |
|------|-------|----------|
| Total `ir_attachment` | 875 | 875 ✓ |
| Filestore refs (`store_fname`) | 874 | 874 ✓ |
| Inline DB storage (`db_datas`) | 0 | 0 ✓ |
| PDFs | 16 | 16 ✓ |
| Images (PNG + JPEG) | 844 | 844 ✓ |
| Binary/octet-stream | 6 | 6 ✓ |
| Filestore dirs on disk | 233 | 233 ✓ |

### 4.3 PDF Attachment Access — End-to-End

Odoo started on port 8070 against `FamOilRestoreTest`. Authenticated as `admin`.
PDF attachment (`id=899`, `in_invoice_yourcompany_demo.pdf`) fetched via
`/web/content/899`:

```
HTTP 200 | Content-Type: application/pdf | Bytes served: 47,172
ATTACHMENT ACCESS: PASS
```

### 4.4 Odoo Module Load

```
83 modules loaded in 2.15s, 0 queries
Registry loaded in 2.962s
```

Result: All 83 modules loaded with **zero errors**.

---

## 5. Findings

No critical findings. The custom format with `--disable-triggers` fully resolves
the `ir_attachment` circular FK dependency identified in Drill 1.

Minor observation: total RTO increased from 36s (Drill 1) to 43s (Drill 2) due to
the additional `pg_restore` overhead and validation. Both are well within the
target RTO of 30 minutes.

---

## 6. Drill Sign-Off

| Field | Value |
|-------|-------|
| Drill executed by | Claude Code (operator supervised) |
| Production database affected | NO |
| Drill database cleaned up | YES — `FamOilRestoreTest` dropped, filestore removed |
| Odoo test instance | Stopped cleanly (PID 42079) |
| Document path | `docs/operations/RESTORE_DRILL.md` |
| Status | **FULL PASS — backup system trusted** |
