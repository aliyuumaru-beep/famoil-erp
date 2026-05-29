# CHANGELOG

## v1.11.0 — 2026-05-29 — Warehouse Hygiene: Putaway Rule and Demo Warehouse Archival

- Added putaway rule: SoyaBean → `Famoil/Stock/RM Warehouse` (was missing; SoyaBean was landing at `Famoil/Stock` parent)
- All 7 putaway rules now cover full product routing (Crude Soya Oil, Refined Soya Oil, SoapStock, Soya Cake, RSO 5L, RSO 25L, SoyaBean)
- Archived Chicago 1 warehouse (FamOil FTZ company) + 2 associated picking types
- Archived YourCompany warehouse (My Company San Francisco) + 4 associated picking types
- Cancelled 26 open demo/test pickings and 3 demo MOs (furniture — Desk Combination, Table, Table Top) prior to archival
- Moved 1,960 kg SoyaBean from CHIC1/Stock → Famoil/Stock/RM Warehouse (stock correction for test POs that used wrong picking type)
- Zeroed 32 YourCompany demo stock quants (furniture demo data) via inventory adjustment
- Active warehouses now: FamOilWH (FamOil FTZ) and NG Company only
- Removed "Demo warehouses not yet archived" from CLAUDE.md known issues

## v1.10.0 — 2026-05-29 — Procurement Maturity: Landed Costs and Integrity Module

- Installed `stock_landed_costs` (native Odoo, LGPL-3) — 88 modules now loaded
- Created account `570000 — Freight & Haulage Expense` (type=expense, company=FamOil FTZ)
- Created landed cost service products (via UI):
  - `SoyaBean Freight & Haulage` — split method: By Quantity — account 570000
  - `Weighbridge Fee` — split method: Equal — account 570000
- Created custom module `stock_landed_cost_po_check` v17.0.1.0.0:
  - Constraint on `button_validate`: blocks landed costs on non-PO receipts and
    outgoing/internal transfers — prevents wrong-receipt assignment
  - Automated activity on receipt validation: schedules "todo" task reminding
    operator to enter landed costs for every validated SoyaBean PO receipt
  - Depends: stock_landed_costs, purchase_stock, base_automation, mail
  - 3-test suite: all pass (valid PO allowed, non-PO blocked, outgoing blocked)
- Workflow: haulage vendor bill (separate from goods vendor) → Create Landed Costs
  → link receipt → validate → SoyaBean unit cost absorbs freight automatically
- CLAUDE.md: procurement checklist and backup status updated

## v1.9.0 — 2026-05-29 — Procurement Maturity: RFQ Workflow and Vendor Pricelists

- Configured vendor pricelists (product.supplierinfo) for SoyaBean on 3 vendors:
  - Kaduna Soybean Traders Ltd: ₦710/kg, min 500 kg, 3-day lead
  - Niger State Farmers Cooperative: ₦705/kg, min 1,000 kg, 5-day lead
  - Benue Agro Aggregators Ltd: ₦718/kg, min 500 kg, 7-day lead
- Removed stale demo supplierinfo entry (Industrial Consumables Ltd at ₦660/kg)
- RFQ workflow validated end-to-end via Odoo Python shell (6 tests):
  - Vendor price auto-fills on RFQ creation from pricelist ✓
  - RFQ draft → sent (email dispatch) → to approve → purchase ✓
  - Niger State min_qty=1,000 enforced (no seller below threshold) ✓
  - Full approval gate integration confirmed ✓
- CLAUDE.md: backup status and procurement checklist updated

## v1.8.0 — 2026-05-29 — Procurement Maturity: PO Approval Workflow

- Configured PO approval workflow (two-step validation) on FamOil FTZ company:
  - `po_double_validation = 'two_step'` (was already set; confirmed active)
  - `po_double_validation_amount` updated from ₦500,000 → ₦200,000
  - Threshold rationale: captures all SoyaBean batch purchases (₦710k/batch) and
    most raw material orders for anti-fraud control
- Workflow validated end-to-end via Odoo Python shell:
  - PO above threshold (demo user) → state = `to approve` ✓
  - Admin approves → state = `purchase` ✓
  - PO below threshold (demo user) → state = `purchase` directly ✓
- User role assignments confirmed: admin = Purchase Administrator (approver),
  demo = Purchase User (requester)
- CLAUDE.md: backup status updated; procurement progress checklist added
- Backup: `famoil_20260529_0726` (post-configuration, custom format)

## v1.7.0 — 2026-05-28 — Post-Restore Governance Synchronization

- CLAUDE.md v1.2.0: updated active phase to "Procurement Maturity & Operational Workflow
  Expansion"; added RESTORE VALIDATION STATUS section; updated backup status (latest:
  famoil_20260528_1814, custom format); resolved stale known issue (restore drill removed);
  updated scripts count (4→5); fixed stale workflow status ("pending remote" → "active")
- PLATFORM_ROADMAP.md v1.2: marked RESTORE DRILL as COMPLETE with Drill 2 results;
  added milestones v1.4.0-roadmap-institutionalization and v1.5.0-restore-validated to
  Phase 4; renumbered priorities (Procurement is now Priority 1); updated risks (removed
  "restore drill not yet validated", added off-machine sync and operator-driven risks);
  updated Section 11 current focus (removed "restore validation")
- FAMOIL_ROADMAP.md v1.1: updated current strategic priority; updated Phase 4 with
  restore drill outcome and milestone; updated Section 6 priority order (Procurement #1);
  updated Section 7 next phase (Procurement Maturity replaces Restore Drill); updated
  risks; removed stale "restore governance matures" condition
- AI_ONBOARDING_V2.txt v2.1: Rule 10 updated with current active phase and restore
  validation status
- DECISION_LOG.md: added DEC-011 — backup format architectural decision (pg_dump -F c,
  rationale, validation, alternatives, trade-offs, revisit conditions)
- Git tag v1.5.0-restore-validated created at f083a9a

## v1.6.0 — 2026-05-28 — Backup Architecture Upgrade and Restore Validation

- Upgraded backup format from `pg_dump -F p` (plain text) to `pg_dump -F c` (custom):
  - Resolves `ir_attachment` restore failure (875/875 attachments now restored)
  - Dump file: `Famoil.dump` (6MB, self-compressed) replaces `Famoil.sql` (17MB)
  - Restore: `pg_restore --disable-triggers -j 4` — requires `odoo` superuser role (confirmed)
- Created `scripts/restore_famoil.sh`:
  - Full restore procedure in one script (DB drop/create, pg_restore, filestore, validation)
  - Built-in validation: ir_attachment count, PDF count, image count, filestore integrity
  - `--production` flag with `CONFIRM` prompt for production restores
  - Backward-compatible: auto-detects `.dump` vs `.sql` and warns on legacy format
- Restore Drill 1 (plain format): PARTIAL PASS — ir_attachment 0/875, all else 100%
- Restore Drill 2 (custom format): FULL PASS — ir_attachment 875/875, PDF served HTTP 200
- Updated `docs/BACKUP_AND_RECOVERY.md` v2.0: new format docs, recovery procedure, drill log
- Updated `docs/operations/RESTORE_DRILL.md`: Drill 2 full report and summary table
- Updated `docs/famoil_erp_template/IMPLEMENTATION_HISTORY.md`: milestone recorded

## v1.5.0 — 2026-05-28 — Two-Level Roadmap Architecture Institutionalized

- Integrated `docs/famoil_erp_template/FAMOIL_ROADMAP.md` (FamOil operational execution roadmap)
  into full governance architecture alongside `docs/roadmap/PLATFORM_ROADMAP.md`
- Fixed `FAMOIL_ROADMAP.md`: removed duplicate plain-text header; replaced U+2028 LINE SEPARATOR
  characters with proper pipe delimiters throughout
- Updated `docs/roadmap/PLATFORM_ROADMAP.md` § 10: removed stale Risk 3
  ("roadmap intelligence partially centralized") — now resolved by two-level roadmap architecture
- Updated `CLAUDE.md`: ACTIVE PHASE section now references both PLATFORM_ROADMAP.md and
  FAMOIL_ROADMAP.md, with distinct roles documented
- Updated `PROJECT_FACTORY_MANUAL.md` v1.3: § 3 document map adds FAMOIL_ROADMAP.md;
  § 4 Roadmap Authority distinguishes platform-level vs template-level authority;
  § 7 onboarding sequence adds FAMOIL_ROADMAP.md at step 5
- Updated `docs/ONBOARDING_GUIDE.md` v1.2: developer checklist, Claude session checklist,
  and key documents table all include FAMOIL_ROADMAP.md with correct read-order position
- Updated `docs/INDUSTRY_TEMPLATE_GUIDE.md` v1.1: added roadmap reference block pointing
  to PLATFORM_ROADMAP.md § 7 (multi-industry expansion strategy) with expansion guard
- Updated `docs/famoil_erp_template/IMPLEMENTATION_HISTORY.md`: recorded two-level roadmap
  architecture milestone
- Duplication resolved: PLATFORM_ROADMAP.md is platform authority; FAMOIL_ROADMAP.md is
  template execution authority; CLAUDE.md is operational cockpit — roles are now distinct,
  documented, and cross-referenced consistently across all governance documents

## v1.4.0 — 2026-05-28 — Roadmap Institutionalization and Governance Maturity

- Created `docs/roadmap/PLATFORM_ROADMAP.md` — authoritative platform roadmap converted
  from `.docx` to governed markdown; establishes vision, sequencing, MVP definition,
  current priorities, and future repository evolution
- Clarified governance document architecture:
  `PLATFORM_ROADMAP.md` (roadmap authority) vs `CLAUDE.md` (operational cockpit) vs
  `IMPLEMENTATION_HISTORY.md` (historical timeline) vs `DECISION_LOG.md` (reasoning record)
- Updated `CLAUDE.md` v1.1.0: stripped roadmap data, added roadmap pointer, fixed stale
  backup status, resolved stale KNOWN ISSUE "no remote connected", updated repo structure
- Updated `PROJECT_FACTORY_MANUAL.md` v1.2.0: added Roadmap and Sequencing Authority section
  (§ 4), updated document relationship map, updated phase table to reflect all phases
  complete, renumbered sections, added PLATFORM_ROADMAP.md to onboarding sequence
- Updated `docs/ONBOARDING_GUIDE.md` v1.1: added PLATFORM_ROADMAP.md to developer and
  AI session reading lists, added to key documents table, updated stale "no remote" rule,
  updated repo structure diagram
- Updated `docs/IMPLEMENTATION_STANDARDS.md` v1.2: added PLATFORM_ROADMAP.md as
  implementation sequencing authority reference in preamble
- Created `docs/famoil_erp_template/IMPLEMENTATION_HISTORY.md`: historical implementation
  timeline covering Phases 1–4 and post-Phase 4 governance maturity
- Duplication removed: roadmap phase tables no longer stored in CLAUDE.md; priority list
  no longer scattered across multiple documents; single authoritative source established

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
