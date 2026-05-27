# Changelog
# FamOil Software Factory
# Format: version | date | phase | description

> This document mirrors the root `CHANGELOG.md` and serves as the mandatory
> document for the CI/CD governance doc-lint check.
> Authoritative version: root `CHANGELOG.md`

---

## v1.3.0 — 2026-05-27 — Phase 3 Backup Automation

- Created `scripts/sync_backup_to_gdrive.sh`: rclone Google Drive sync
- Created launchd plists: com.famoil.backup.daily.plist (02:00 AM),
  com.famoil.gdrive.sync.plist (03:00 AM)
- Created `docs/deployment/MACOS_BACKUP_AUTOMATION.md`: full setup guide
- Requires: `brew install rclone` + `rclone config` to activate offsite sync

## v1.2.0 — 2026-05-27 — Phase 2 Backup Governance

- Extended `scripts/backup_famoil.sh`: docs/scripts population, compression,
  governance bridge manifest update, retention dry-run reporter
- Fixed R-01 governance gap: `backups/BACKUP_MANIFEST.md` created as bridge
  for `backup_check.yml` workflow validation
- Fixed `.gitignore` to allow `backups/BACKUP_MANIFEST.md` to be tracked
- Committed `docs/architecture/ARCHITECTURAL_PRINCIPLES.md` (12-principle doctrine)
- Updated `docs/BACKUP_AND_RECOVERY.md` to v1.1
- Remaining: automated scheduling, cloud sync, retention deletion (later phases)

## v1.1.0 — 2026-05-27 — Phase 4 CI/CD Governance Complete

- GitHub remote connected: https://github.com/aliyuumaru-beep/famoil-erp
- All 4 GitHub Actions workflows active (ci_review, doc_lint, backup_check, security_scan)
- Branch protection rules applied on main by operator
- CLAUDE.md updated: all phases COMPLETE, governance engine FULLY ACTIVE
- GOVERNANCE_ENGINE.md updated: Layer 2 status ACTIVE

## v1.0.0 — 2026-05-27 — Phase 1 Governance

- Created `CLAUDE.md` session memory anchor
- Created `.claude/settings.json` governance hook configuration
- Created 6 hook enforcement scripts in `.claude/hooks/`
- Created `logs/` directory with 5 audit log files
- Created `docs/architecture/GOVERNANCE_ENGINE.md`
- Created `docs/IMPLEMENTATION_STANDARDS.md` (11 rules)
- Created `docs/ONBOARDING_GUIDE.md`
- Created `docs/BACKUP_AND_RECOVERY.md`
- Created `docs/CHANGELOG.md`
- Created `docs/DEPLOYMENT_GUIDE.md`
- Created `docs/TESTING_GUIDE.md`
- Created `docs/CSV_STANDARDS.md`
- Created `docs/MODULE_REGISTRY.md`
- Created `docs/INDUSTRY_TEMPLATE_GUIDE.md`
- Created `docs/SECURITY_GUIDELINES.md`
- Created `docs/sops/CI_CD_RUNBOOK.md`
- Created `PROJECT_FACTORY_MANUAL.md`
- Migrated CSV templates from `templates/` to `csv_templates/`
- Created new CSV templates: `warehouses.csv`, `operation_types.csv`
- Created `.github/workflows/` with 4 workflow files (pending remote)
- Updated `.gitignore` with `logs/*.log` and governance entries

## v1.0.0 — 2026-05-24 — Phase 2 & 3

### Phase 2: Configuration Validation
- Removed SoapStock from BOM 10; Soya Cake cost share 35% → 40%
- Fixed "Clearning" typo → "Cleaning" (operation id=6)
- Upgraded `stock_crude_oil_tank_restriction` to v17.0.1.1.0 (name-based lookup)
- Resolved negative quant (-81 kg) in Crude Oil Tank 1
- Corrected misplaced stock across all tanks and parent locations
- Configured 3-stage pipeline operation types (Extraction, Refining, Packaging)
- Implemented 6 putaway rules for all manufacturing outputs
- Created and validated Refined Soya Oil MO (135 kg, BOM 15)
- Documented Odoo 17 limitation: no per-BOM-line source location
- Added DEC-008, DEC-009, DEC-010; ISSUE-009 to ISSUE-013

### Phase 3: Commercialisation Framework
- Created INDUSTRY_VARIATION_MATRIX.md (7 industries)
- Created CLIENT_DISCOVERY_TEMPLATE.md (8-section questionnaire)
- Created COMMERCIAL_GUIDE.md (CONFIDENTIAL, 3 pricing tiers)
- Created TEMPLATE_VERSIONING.md (naming convention, fork strategy)
- Created DATA_MIGRATION_SCAFFOLD.md (14-step sequence)
- Created NIGERIA_COMPLIANCE.md (VAT, WHT, PENCOM, ITF, NSITF, NAFDAC, SON)
- Framework readiness: 8.5/10

## v0.1-alpha — 2026-05-22 — Phase 1

- Initial agro-processing ERP framework extraction
- Warehouse hierarchy stabilised
- Manufacturing costing validated (BOM 10: 1,000 kg SoyaBean → 140 kg Crude Oil)
- Byproduct architecture documented
- Backup/documentation framework created
- Initial reusable CSV templates created
- Backup taken: `/Users/mac/odoo_backups/famoil_20260522_1133/`
