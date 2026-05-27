# macOS Backup Automation
# FamOil Software Factory — Deployment Guide
# Version: 1.0 | Created: 2026-05-27

> This document covers automated backup scheduling (launchd) and offsite sync
> (rclone → Google Drive) for the FamOil Odoo 17 instance running on macOS.
>
> No credentials are stored in any script or this document.
> All authentication is handled via rclone's token store (local to the machine).

---

## Overview

Two scheduled jobs protect the FamOil ERP instance:

| Job | Script | Schedule | What it does |
|-----|--------|----------|--------------|
| Daily backup | `scripts/backup_famoil.sh` | 02:00 AM daily | pg_dump + filestore + compress |
| Google Drive sync | `scripts/sync_backup_to_gdrive.sh` | 03:00 AM daily | Upload archives to Drive |

The backup runs first. The sync runs one hour later to ensure the backup is complete.

---

## Part 1 — launchd Scheduling

macOS uses `launchd` instead of cron for persistent scheduled jobs. Two plist
agents are provided in `scripts/`:

- `scripts/com.famoil.backup.daily.plist` — backup at 02:00 AM
- `scripts/com.famoil.gdrive.sync.plist` — Google Drive sync at 03:00 AM

### 1.1 Install the backup agent

```bash
# Copy plist to launchd agents directory
cp /Users/mac/odoo17/scripts/com.famoil.backup.daily.plist \
   ~/Library/LaunchAgents/com.famoil.backup.daily.plist

# Load the agent (starts scheduling immediately)
launchctl load ~/Library/LaunchAgents/com.famoil.backup.daily.plist

# Verify it is loaded
launchctl list | grep famoil
```

### 1.2 Install the Google Drive sync agent

Install rclone and configure `gdrive` remote first (Part 2 below), then:

```bash
cp /Users/mac/odoo17/scripts/com.famoil.gdrive.sync.plist \
   ~/Library/LaunchAgents/com.famoil.gdrive.sync.plist

launchctl load ~/Library/LaunchAgents/com.famoil.gdrive.sync.plist

launchctl list | grep famoil
```

### 1.3 Test a manual run

```bash
# Trigger the backup job now (does not wait for scheduled time)
launchctl start com.famoil.backup.daily

# Watch the log
tail -f /Users/mac/odoo17/logs/launchd_backup.log
```

### 1.4 Uninstall agents

```bash
launchctl unload ~/Library/LaunchAgents/com.famoil.backup.daily.plist
launchctl unload ~/Library/LaunchAgents/com.famoil.gdrive.sync.plist

rm ~/Library/LaunchAgents/com.famoil.backup.daily.plist
rm ~/Library/LaunchAgents/com.famoil.gdrive.sync.plist
```

### 1.5 Change the schedule

Edit the plist file before loading. The `StartCalendarInterval` key controls timing.

Examples:

```xml
<!-- Every day at 02:00 AM (current) -->
<key>StartCalendarInterval</key>
<dict>
  <key>Hour</key><integer>2</integer>
  <key>Minute</key><integer>0</integer>
</dict>

<!-- Every Sunday at midnight -->
<key>StartCalendarInterval</key>
<dict>
  <key>Weekday</key><integer>0</integer>
  <key>Hour</key><integer>0</integer>
  <key>Minute</key><integer>0</integer>
</dict>
```

---

## Part 2 — Google Drive Sync (rclone)

### 2.1 Install rclone

```bash
brew install rclone
rclone version   # verify installation
```

### 2.2 Configure Google Drive remote

```bash
rclone config
```

Follow the interactive prompts:
1. Select `n` — new remote
2. Name: `gdrive` (must match exactly — this is what the script expects)
3. Type: `drive` (Google Drive)
4. Client ID / Secret: leave blank (use rclone defaults)
5. Scope: `1` — full access
6. Root folder ID: leave blank
7. Service account file: leave blank
8. Advanced config: `n`
9. Auto config: `y` — opens browser for Google sign-in
10. Team drive: `n`
11. Confirm and `q` to quit

### 2.3 Verify the remote

```bash
rclone lsd gdrive:
```

You should see your Google Drive root. If it errors, re-run `rclone config`.

### 2.4 Create the target folder

The sync script uses `FamOil_Backups/ERP/` as the target. rclone creates it
automatically on first sync. To verify manually:

```bash
# Dry-run to see what would be synced
bash /Users/mac/odoo17/scripts/sync_backup_to_gdrive.sh --dry-run

# Live sync
bash /Users/mac/odoo17/scripts/sync_backup_to_gdrive.sh
```

### 2.5 What is synced to Google Drive

Only compressed archives are synced:

```
Google Drive: FamOil_Backups/ERP/
├── famoil_20260527_2103.tar.gz
├── famoil_20260528_0200.tar.gz
└── ...
```

PostgreSQL dump files (`.sql`), raw backup directories, filestore contents, and
`odoo.conf` are **never** synced to Google Drive. The `.tar.gz` archive contains
the full backup but is treated as opaque binary — Google Drive holds it for
offsite disaster recovery only.

### 2.6 rclone token maintenance

Google Drive tokens expire periodically. If sync begins failing with auth errors:

```bash
rclone config reconnect gdrive:
```

This refreshes the token without reconfiguring the remote.

---

## Part 3 — Log Files

| Log file | Written by | Contents |
|---|---|---|
| `logs/launchd_backup.log` | launchd (backup agent) | Full backup run output |
| `logs/launchd_gdrive.log` | launchd (sync agent) | Full sync run output |
| `logs/retention_report.log` | backup_famoil.sh | Retention dry-run report |
| `logs/gdrive_sync.log` | sync_backup_to_gdrive.sh | Transfer log |

All log files are git-ignored (`logs/*.log`). They are local operational records.

To watch a live run:
```bash
tail -f /Users/mac/odoo17/logs/launchd_backup.log
```

---

## Part 4 — Governance Note

After each automated backup run, the governance bridge is updated automatically:

```
/Users/mac/odoo17/backups/BACKUP_MANIFEST.md
```

This file must be committed manually after each run so `backup_check.yml` can
validate backup currency:

```bash
cd /Users/mac/odoo17
git add backups/BACKUP_MANIFEST.md
git commit -m "chore: update backup manifest $(date '+%Y-%m-%d')"
git push origin feature/<current-branch>  # or via PR
```

The `backup_check.yml` GitHub Actions workflow fails if this file is not updated
within 7 days. This is the governance bridge between local backup execution and
repository-level backup validation.

---

## Part 5 — Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `launchctl list` shows no famoil entries | Agent not loaded | Re-run `launchctl load <plist>` |
| Backup runs but no archive produced | `COMPRESS=false` in script | Set `COMPRESS="true"` |
| Sync fails with "No such remote" | gdrive not configured | Re-run `rclone config` |
| Sync fails with auth error | Token expired | `rclone config reconnect gdrive:` |
| `backup_check.yml` still failing | Manifest not committed | Commit `backups/BACKUP_MANIFEST.md` |
| launchd agent fires but backup errors | pg_hba or Postgres not running | Ensure PostgreSQL is running |

---

## Reference

- Backup script: `scripts/backup_famoil.sh`
- Sync script: `scripts/sync_backup_to_gdrive.sh`
- Backup plist: `scripts/com.famoil.backup.daily.plist`
- Sync plist: `scripts/com.famoil.gdrive.sync.plist`
- Backup docs: `docs/BACKUP_AND_RECOVERY.md`
- Restore docs: `docs/famoil_erp_template/BACKUP_AND_RESTORE.md`
