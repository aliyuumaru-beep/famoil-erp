# Implementation History
# FamOil Software Factory — Historical Timeline
# Version: 1.0 | Created: 2026-05-28

> This document records the historical implementation timeline of the FamOil
> Software Factory. It is a record of what was done and when — not a roadmap
> for what comes next.
>
> For future priorities and implementation sequencing, see:
> `docs/roadmap/PLATFORM_ROADMAP.md`
>
> For the reasoning behind decisions, see:
> `docs/famoil_erp_template/DECISION_LOG.md`

---

## Phase 1 — Foundation Infrastructure

**Completed:** 2026-05-22 | **Tag:** v0.1-alpha

### What was implemented

- Initial Odoo 17.0.1.3 Community Edition deployment on macOS
- Database `Famoil` created for FamOil FTZ (company id=2)
- Warehouse hierarchy stabilised: FamOilWH with RM Warehouse, Crude Oil Tanks,
  Refined Oil Tanks, Soapstock Tank, FG Warehouse
- Product categories configured with automated valuation (FIFO/Average)
- Manufacturing costing validated: 3-stage pipeline architecture confirmed
- Byproduct architecture documented: Crude Soya Oil (60%), Soya Cake (40%), SoapStock (5%)
- Initial backup taken: `/Users/mac/odoo_backups/famoil_20260522_1133/`
- Git repository initialised with documentation framework
- Initial reusable CSV templates created (9 templates)

### Key decisions made

- DEC-001: Odoo Community over Enterprise (cost, local capacity)
- DEC-002: Work center hourly cost for overhead allocation
- DEC-003: FIFO for finished goods, Average for raw materials
- DEC-004: Internal tank locations (not virtual) for oil storage

---

## Phase 2 — Configuration Validation and Pipeline Setup

**Completed:** 2026-05-24 | **Tag:** v1.0.0 (Phase 2 section)

### What was implemented

- Removed SoapStock from BOM 10; reassigned cost shares (Soya Cake 40%, SoapStock 0%)
- Fixed operation name typo: "Clearning" → "Cleaning" (BOM 10, operation id=6)
- Upgraded `stock_crude_oil_tank_restriction` to v17.0.1.1.0 — runtime name lookups
  replacing hardcoded IDs
- Resolved negative quant (−81 kg) in Crude Oil Tank 1 via `_update_available_quantity`
- Corrected misplaced stock across all locations (Crude Soya Oil, Refined Soya Oil, SoapStock)
- Configured 3-stage manufacturing pipeline operation types (Extraction, Refining, Packaging)
  with correct source/destination locations
- Added 6 putaway rules routing all manufacturing outputs to correct child locations
- Created and validated full Refined Soya Oil MO (135 kg, BOM 15)
- Documented Odoo 17 limitation: no per-BOM-line source location → Rank 1 approach adopted
- Added custom module `mrp_component_availability_check`

### Key decisions made

- DEC-005: Byproduct cost share strategy (SoapStock 5%, Soya Cake 35%)
- DEC-006: 3-step inbound / 3-step outbound for FamOilWH
- DEC-007: Custom module for tank restriction (no native Odoo capability)
- DEC-008: Per-component source location via Rank 1 (parent + child_of)
- DEC-009: Putaway rules for manufacturing output routing
- DEC-010: Separate operation types per manufacturing stage

---

## Phase 3 — Commercialisation Framework

**Completed:** 2026-05-24 | **Tag:** v1.0.0 (Phase 3 section)

### What was implemented

- `INDUSTRY_VARIATION_MATRIX.md` — 7 industries scored vs FamOil template
- `CLIENT_DISCOVERY_TEMPLATE.md` — 8-section discovery questionnaire
- `COMMERCIAL_GUIDE.md` (CONFIDENTIAL) — 3-tier pricing (Starter ~13d, Standard ~31d,
  Enterprise 60–120d)
- `TEMPLATE_VERSIONING.md` — naming convention, fork strategy, upgrade path
- `DATA_MIGRATION_SCAFFOLD.md` — 14-step sequence, CSV templates, SQL validation queries
- `NIGERIA_COMPLIANCE.md` — VAT 7.5%, WHT, PENCOM 18%, ITF 1%, NSITF 1%, NAFDAC, SON,
  CoA skeleton
- Framework commercialisation readiness assessed at 8.5/10
- Next deployment target identified: groundnut oil mill

---

## Phase 4 — CI/CD Governance Engine

**Completed:** 2026-05-27 | **Tags:** v1.1.0, v1.2.0-governance-foundation,
v1.3.0-offsite-backup-operational

### What was implemented

**Repository governance:**
- GitHub remote connected: `aliyuumaru-beep/famoil-erp`
- Branch protection on `main` via ruleset `MAIN_BRANCH_PROTECTION_v1`
- PR workflow enforced: squash merge, no direct pushes to main

**GitHub Actions workflows:**
- `ci_review.yml` — Claude Code AI governance review on every PR
- `doc_lint.yml` — documentation completeness check (doc-lint)
- `security_scan.yml` — secret and credential scan (secret-scan)
- `backup_check.yml` — weekly backup currency validation (Mondays 06:00 UTC)

**Backup governance:**
- `scripts/backup_famoil.sh` extended: tar.gz compression, governance bridge,
  retention dry-run reporter
- `backups/BACKUP_MANIFEST.md` created as governance bridge for `backup_check.yml`
- `.gitignore` updated: `backups/*` + `!backups/BACKUP_MANIFEST.md`
- `scripts/sync_backup_to_gdrive.sh` — rclone-based Google Drive sync
- `scripts/com.famoil.backup.daily.plist` — launchd daily backup at 02:00 AM
- `scripts/com.famoil.gdrive.sync.plist` — launchd daily sync at 03:00 AM
- `docs/deployment/MACOS_BACKUP_AUTOMATION.md` — full launchd setup guide

**Architectural foundation:**
- `docs/architecture/ARCHITECTURAL_PRINCIPLES.md` — 12-principle factory doctrine
- Rule 12 added to `docs/IMPLEMENTATION_STANDARDS.md` (Architectural Principles Compliance)
- Architectural Governance section added to `PROJECT_FACTORY_MANUAL.md`

**Governance utilities:**
- `scripts/local_secret_scan.sh` — mirrors CI security_scan.yml for local verification
- `scripts/check_claude_review_log.sh` — CI log inspector (read-only diagnostic)

---

## Post-Phase 4 — Governance Maturity

**Completed:** 2026-05-28

### What was implemented

- `docs/roadmap/PLATFORM_ROADMAP.md` — authoritative platform roadmap institutionalised
- Governance document architecture clarified:
  - `PLATFORM_ROADMAP.md` → authoritative roadmap and sequencing
  - `CLAUDE.md` → operational cockpit only (not roadmap storage)
  - `IMPLEMENTATION_HISTORY.md` → historical timeline (this document)
  - `DECISION_LOG.md` → reasoning record
- References updated in: `CLAUDE.md`, `PROJECT_FACTORY_MANUAL.md`,
  `docs/ONBOARDING_GUIDE.md`, `docs/IMPLEMENTATION_STANDARDS.md`
- Stale content resolved: remote connection status, backup currency, phase statuses

---

## Post-Phase 4 — Two-Level Roadmap Architecture

**Completed:** 2026-05-28

### What was implemented

- `docs/famoil_erp_template/FAMOIL_ROADMAP.md` integrated into full governance architecture:
  - Duplicate plain-text header removed; U+2028 LINE SEPARATOR characters replaced
  - Added to all governance document reading sequences (ONBOARDING_GUIDE, PROJECT_FACTORY_MANUAL,
    AI_ONBOARDING_V2, CLAUDE.md)
- Two-level roadmap authority established:
  - `PLATFORM_ROADMAP.md` → platform-level vision, sequencing, and commercial MVP definition
  - `FAMOIL_ROADMAP.md` → FamOil template operational state, ERP module status, phase priorities
- Stale risk resolved: `PLATFORM_ROADMAP.md` Risk 3 ("roadmap intelligence partially centralized")
  removed — now resolved by two-level roadmap architecture
- `docs/INDUSTRY_TEMPLATE_GUIDE.md` updated with expansion guard referencing PLATFORM_ROADMAP.md § 7
- All governance documents now cross-reference the correct roadmap authority for their scope

---

## Post-Phase 4 — Backup Architecture Upgrade and Restore Validation

**Completed:** 2026-05-28

### What was implemented

- Restore Drill 1 executed from `famoil_20260528_0033` (plain format):
  - Core ERP data 100% restored; critical finding: `ir_attachment` 0/875 failed
  - Root cause: circular FK between `account_move` and `ir_attachment` in plain `pg_dump -F p`
- Backup format upgraded to PostgreSQL custom format (`pg_dump -F c`):
  - `scripts/backup_famoil.sh`: dump now outputs `Famoil.dump` (6MB compressed)
  - `pg_restore --disable-triggers -j 4` resolves circular FK dependency
- `scripts/restore_famoil.sh` created: full restore + validation in one script
- Restore Drill 2 from `famoil_20260528_1814` (custom format): FULL PASS
  - `ir_attachment`: 875/875 ✓ | PDFs: 16/16 ✓ | Images: 844/844 ✓
  - PDF served via Odoo `/web/content` endpoint: HTTP 200, 47,172 bytes ✓
  - 83 modules loaded, 0 errors | RTO: 43 seconds
- `docs/BACKUP_AND_RECOVERY.md` updated to v2.0
- `docs/operations/RESTORE_DRILL.md` updated with Drill 2 full report

### Outcome

Backup system is now fully trusted. End-to-end recovery including attachment
access through the Odoo UI validated.

---

## Post-Phase 4 — Governance Synchronization and Roadmap Refresh

**Completed:** 2026-05-28 | **Tag:** v1.5.0-restore-validated (at f083a9a)

### What was implemented

- `CLAUDE.md` updated to v1.2.0:
  - Active phase updated to "Procurement Maturity & Operational Workflow Expansion"
  - RESTORE VALIDATION STATUS governance table added (Drill 2 results, RTO, PDF access)
  - Backup status updated to `famoil_20260528_1814` (custom format)
  - Stale known issue removed; off-machine sync risk added
  - Scripts count updated (4→5); workflow status corrected (pending→active)
- `docs/roadmap/PLATFORM_ROADMAP.md` updated to v1.2:
  - Phase 4 milestones: `v1.4.0-roadmap-institutionalization`, `v1.5.0-restore-validated` added
  - Restore drill marked COMPLETE in Section 7; priorities renumbered (Procurement is Priority 1)
  - Risks updated: removed stale "restore drill not yet validated"; added off-machine sync risk
  - Section 11 current focus: "restore validation" removed; procurement and workflow expansion added
- `docs/famoil_erp_template/FAMOIL_ROADMAP.md` updated to v1.1:
  - Current strategic priority updated to Procurement Maturity & Operational Workflow Expansion
  - Phase 4 block updated with restore drill outcome and milestone
  - Section 6 priority order: Procurement #1 (restore drill replaced)
  - Section 7 next phase: Procurement Maturity replaces Restore Drill
  - Risks updated: stale restore risk replaced with off-machine sync risk
- `AI_ONBOARDING_V2.txt` updated to v2.1:
  - Rule 10 updated with current active phase and restore validation status
- `docs/famoil_erp_template/DECISION_LOG.md`: DEC-011 added — backup format
  architectural decision (pg_dump -F c rationale, validation, alternatives, trade-offs,
  revisit conditions)
- `CHANGELOG.md`: v1.7.0 entry added documenting all governance sync changes

### Key decisions made

- DEC-011: Backup format upgrade from pg_dump -F p to pg_dump -F c

### Outcome

All governance documents synchronized to post-restore operational reality.
Stale "restore drill pending" references removed across all documents.
Procurement Maturity established as current Priority 1 across all authorities.

---

## Procurement Maturity — Phase 1 Implementation

**Completed:** 2026-05-29

### What was implemented

**PO Approval Workflow:**
- Two-step validation confirmed active on FamOil FTZ company
- Approval threshold set to ₦200,000 — captures all SoyaBean batch purchases
- Role assignments: admin = Purchase Administrator (approver), demo = Purchase User
- Workflow validated end-to-end: non-manager PO above threshold → `to approve` →
  manager approves → `purchase`

**RFQ Workflow and Vendor Pricelists:**
- Vendor pricelists configured on SoyaBean for 3 suppliers:
  - Kaduna Soybean Traders Ltd: ₦710/kg, min 500 kg, 3-day lead
  - Niger State Farmers Cooperative: ₦705/kg, min 1,000 kg, 5-day lead
  - Benue Agro Aggregators Ltd: ₦718/kg, min 500 kg, 7-day lead
- Stale demo pricelist (Industrial Consumables Ltd) removed
- RFQ state machine validated: draft → sent → to approve → purchase

**Landed Cost Infrastructure:**
- `stock_landed_costs` (native Odoo, LGPL-3) installed — 88 modules total
- Account `570000 — Freight & Haulage Expense` created (FamOil FTZ)
- Service products created: `SoyaBean Freight & Haulage` (By Quantity),
  `Weighbridge Fee` (Equal)
- Workflow established: haulage vendor bill (separate from goods vendor) →
  Create Landed Costs → link PO receipt → validate → SoyaBean FIFO layer
  absorbs freight, increasing true unit cost

**Custom Module — `stock_landed_cost_po_check` v17.0.1.0.0:**
- Constraint on `button_validate`: blocks landed costs on non-PO receipts and
  non-incoming transfers — prevents wrong-receipt cost assignment
- Automated activity: schedules "Enter landed costs" todo on every validated
  SoyaBean PO receipt
- 3-test suite: all pass
- Decision: DEC-012

### Key decisions made

- DEC-012: Custom module for landed cost receipt integrity (native options
  researched and confirmed insufficient; partner consent obtained)

### Outcome

Procurement Maturity Phase 1 complete. Core procurement workflow operational:
RFQ → approval → receipt → landed cost absorption. Cost integrity enforced by
custom module. Remaining: procurement traceability validation.
