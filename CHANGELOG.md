# CHANGELOG

## v1.3.0 — 2026-05-27 — Phase 3 Backup Automation

- Created `scripts/sync_backup_to_gdrive.sh`: rclone-based Google Drive sync;
  uploads famoil_*.tar.gz to gdrive:FamOil_Backups/ERP/; dry-run flag;
  preflight checks for rclone and gdrive remote; logs to gdrive_sync.log
- Created `scripts/com.famoil.backup.daily.plist`: launchd agent running
  backup_famoil.sh daily at 02:00 AM
- Created `scripts/com.famoil.gdrive.sync.plist`: launchd agent running
  sync_backup_to_gdrive.sh daily at 03:00 AM
- Created `docs/deployment/MACOS_BACKUP_AUTOMATION.md`: full launchd setup,
  rclone installation and configuration, log reference, troubleshooting guide
- rclone not yet installed locally — setup required (see MACOS_BACKUP_AUTOMATION.md)

## v1.2.0 — 2026-05-27 — Phase 2 Backup Governance

- Extended `scripts/backup_famoil.sh`: added docs/scripts population, tar.gz
  compression (COMPRESS flag), governance bridge manifest update, retention
  dry-run reporter (no deletions)
- Fixed R-01 (critical gap): created `backups/BACKUP_MANIFEST.md` as governance
  bridge so `backup_check.yml` workflow can validate backup currency
- Fixed `.gitignore`: changed `backups/` → `backups/*` + `!backups/BACKUP_MANIFEST.md`
  so only the manifest (metadata, no sensitive data) is tracked
- Committed pending governance docs: `docs/architecture/ARCHITECTURAL_PRINCIPLES.md`
  (12-principle factory doctrine), Rule 12 in IMPLEMENTATION_STANDARDS.md,
  Architectural Governance section in PROJECT_FACTORY_MANUAL.md
- Updated `docs/BACKUP_AND_RECOVERY.md` v1.1: governance bridge, compression,
  retention report documentation, fresh backup warning
- Remaining risks: no automated scheduling (launchd), no cloud offsite (rclone),
  retention deletion not yet enabled, fresh backup still required

## v1.1.0 — 2026-05-27 — Phase 4 CI/CD Governance Complete

- GitHub remote connected: https://github.com/aliyuumaru-beep/famoil-erp
- All 4 GitHub Actions workflows active (ci_review, doc_lint, backup_check, security_scan)
- Branch protection rules applied on main by operator
- CLAUDE.md updated: all phases COMPLETE, governance engine FULLY ACTIVE
- GOVERNANCE_ENGINE.md updated: Layer 2 status ACTIVE

## v1.0.0 — 2026-05-24

### Phase 2: Configuration Validation
- Removed SoapStock from BOM 10 (crude oil extraction); reassigned 5% cost share to Soya Cake (now 40%)
- Updated COSTING_VALIDATION.md: Soya Cake unit cost ₦335 → ₦383/kg; batch gross loss recalculated
- Fixed operation name typo "Clearning" → "Cleaning" (BOM 10, operation id=6)
- Upgraded `stock_crude_oil_tank_restriction` to v17.0.1.1.0 — replaced hardcoded IDs with runtime name lookups
- Resolved negative quant (-81 kg) in Crude Oil Tank 1 via `_update_available_quantity`
- Corrected misplaced stock: Crude Soya Oil (20 kg parent + 179 kg FG Warehouse → Crude Oil Tank 1), Refined Soya Oil (135 kg parent → Refined Oil Tank 1), SoapStock (5 kg Refined Tank 1 → Soapstock Tank)
- Configured 3-stage manufacturing pipeline operation types (Extraction, Refining, Packaging) with correct source/destination locations
- Added 6 putaway rules routing all manufacturing outputs to correct child locations
- Created and validated full Refined Soya Oil MO (135 kg, BOM 15) via shell script
- Documented native Odoo 17 limitation: no per-BOM-line source location; adopted Rank 1 (parent + child_of) approach
- Added custom module `mrp_component_availability_check`
- Added decisions DEC-008, DEC-009, DEC-010 to DECISION_LOG.md
- Added ISSUE-009 through ISSUE-013 to KNOWN_ISSUES.md (all resolved)
- Backup: `/Users/mac/odoo_backups/famoil_20260522_1133/`

### Phase 3: Commercialisation Framework
- Created INDUSTRY_VARIATION_MATRIX.md — 7 industries scored LOW/MEDIUM/HIGH vs FamOil template
- Created CLIENT_DISCOVERY_TEMPLATE.md — 8-section discovery questionnaire
- Created COMMERCIAL_GUIDE.md (CONFIDENTIAL) — 3-tier pricing (Starter ~13d, Standard ~31d, Enterprise 60-120d)
- Created TEMPLATE_VERSIONING.md — naming convention, fork strategy, upgrade path
- Created DATA_MIGRATION_SCAFFOLD.md — 14-step sequence, CSV templates, SQL validation queries
- Created NIGERIA_COMPLIANCE.md — VAT 7.5%, WHT, PENCOM 18%, ITF 1%, NSITF 1%, NAFDAC, SON, CoA skeleton
- Framework commercialisation readiness: 8.5/10
- Next deployment target: Groundnut oil mill

### Scripts
- `scripts/backup_famoil.sh`
- `scripts/inspect_famoil_config.sh`
- `scripts/process_refined_oil_mo.py` — creates and completes Refined Soya Oil MO (135 kg) via shell
- `scripts/fix_locations_and_routing.py` — stock corrections + putaway rule creation

---

## v0.1-alpha — 2026-05-22

### Phase 1: Inspection & Backup
- Initial agro-processing ERP framework extraction
- Warehouse hierarchy stabilised
- Manufacturing costing validated
- Byproduct architecture documented
- Backup/documentation framework created
- Initial reusable CSV templates created
