# CLAUDE.md — Software Factory Session Anchor
# FamOil Industrial ERP Framework
# Version: 1.0.1 | Last updated: 2026-05-27

> This file is read automatically by Claude Code at the start of every session.
> It is the single source of truth for project state. Keep it current.
> Update this file at the end of every phase before stopping.

---

## PROJECT IDENTITY

| Field                | Value                                      |
|---------------------|--------------------------------------------|
| Project Name        | FamOil                                     |
| Industry / Sector   | Soybean Oil Processing (Agro-processing)   |
| Application         | Odoo 17.0.1.3 Community Edition            |
| Database Name       | Famoil (PostgreSQL 16.11)                  |
| Country             | Nigeria                                    |
| Currency            | NGN (Nigerian Naira, ₦)                    |
| Deployment          | Local — macOS (MacBook Air)                |
| Project Directory   | /Users/mac/odoo17                          |
| Company (active)    | FamOil FTZ (id=2)                          |
| Server              | localhost:8069                             |

**Start command** (run from /Users/mac/odoo17):
```bash
source odoo/venv/bin/activate
python odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web
```

---

## ACTIVE PHASE

| Phase | Description                               | Status   | Date       | Approved By |
|------|-------------------------------------------|----------|------------|-------------|
| 1    | Inspection, Backup & Repository Foundation | COMPLETE | 2026-05-22 | Operator    |
| 2    | Configuration Validation & Pipeline Setup  | COMPLETE | 2026-05-24 | Operator    |
| 3    | Commercialisation Framework                | COMPLETE | 2026-05-24 | Operator    |
| 4    | CI/CD Governance Engine                    | COMPLETE | 2026-05-27 | Operator    |

**Current phase:** Phase 4 — COMPLETE. GitHub remote connected, Actions active, branch protection on main enabled.

**Governance engine:** Phase 1 hooks created 2026-05-27. See GOVERNANCE ENGINE STATUS below.

---

## INSTALLED MODULES

**Core ERP (Odoo native):**
`stock`, `stock_account`, `mrp`, `mrp_account`, `account`, `account_payment`,
`account_check_printing`, `sale`, `sale_management`, `sale_stock`, `sale_mrp`,
`purchase`, `purchase_stock`, `purchase_mrp`

**Custom / Third-party addons (in custom_addons/):**

| Module                            | Purpose                                        | Version      |
|----------------------------------|------------------------------------------------|--------------|
| `stock_crude_oil_tank_restriction`| Blocks non-Crude-Oil into Crude Oil Tanks      | 17.0.1.1.0   |
| `mrp_component_availability_check`| Blocks MO completion if components short      | current      |
| `accounting_pdf_reports`          | PDF accounting reports                        | third-party  |
| `maintenance_spareparts_v6`       | Spare parts tracking                          | third-party  |
| `om_account_accountant`           | Extended accounting                           | third-party  |
| `om_account_asset`                | Asset management                              | third-party  |
| `om_account_budget`               | Budget management                             | third-party  |
| `om_account_daily_reports`        | Daily accounting reports                      | third-party  |
| `om_account_followup`             | Customer follow-up                            | third-party  |
| `om_fiscal_year`                  | Fiscal year management                        | third-party  |
| `om_recurring_payments`           | Recurring payment automation                  | third-party  |

**OCA Web addons (in /Users/mac/oca_web):**
`web_responsive`, `web_environment_ribbon`, `web_notify`, `web_refresher`,
`web_theme_classic`, `web_dialog_size`, `web_m2x_options`,
`web_pivot_computed_measure`, `web_search_with_and`,
`web_remember_tree_column_width`

---

## MANUFACTURING CONTEXT

**3-Stage Production Pipeline:**

```
1,000 kg SoyaBean (RM Warehouse)
        │
        ▼  STAGE 1 — EXTRACTION (BOM 10, Op Type id=79)
        │  Cleaning → Extrusion → Pressing → Filtration → Bottling
        ├──► 140 kg Crude Soya Oil → Crude Oil Tank 1 (putaway)
        └──► 840 kg Soya Cake → FG Warehouse (putaway)

140 kg Crude Soya Oil (Crude Oil Tank 1)
        │
        ▼  STAGE 2 — REFINING (BOM 15, Op Type id=127)
        │  Neutralization → Bleaching → Deodorization → Final Filtration
        ├──► 135 kg Refined Soya Oil → Refined Oil Tank 1 (putaway)
        └──► 5 kg SoapStock → Soapstock Tank (putaway)

Refined Soya Oil
        │
        ▼  STAGE 3 — PACKAGING (BOMs 208/209, Op Type id=128)
        └──► Refined Soya Oil 25L / 5L → FG Warehouse
```

**Work Centers (Extraction):** Cleaning (₦15k/hr), Extrusion (₦45k/hr),
Pressing (₦75k/hr), Filtration (₦20k/hr), Packaging (₦12k/hr)

**Work Centers (Refining):** Neutralization (id=20), Bleaching (id=21),
Deodorization (id=23)

**Key BOM costing (BOM 10, per batch):**
- Raw material: ₦710,000 (1,000 kg × ₦710/kg SoyaBean)
- Overhead: ₦95,167
- Total: ₦805,167
- Crude Soya Oil unit cost: ₦3,451/kg (60% share)
- Soya Cake unit cost: ₦383/kg (40% share)

---

## CRITICAL RULES FOR THIS SESSION

> Full rules: see docs/IMPLEMENTATION_STANDARDS.md
> Architectural doctrine: see docs/architecture/ARCHITECTURAL_PRINCIPLES.md

**ACTIVE DO NOT rules:**
- DO NOT run git push without explicit operator instruction
- DO NOT modify core Odoo application files in odoo/
- DO NOT delete any existing committed file without operator approval
- DO NOT expose passwords, API keys, or database credentials in any output
- DO NOT make architectural decisions that conflict with docs/architecture/ARCHITECTURAL_PRINCIPLES.md unless the exception is approved and recorded in the Decision Log
- DO NOT commit ERP backup archives (SQL, filestore, tar.gz) to the repository — only `backups/BACKUP_MANIFEST.md` metadata is tracked

**Backup status:**
- Last backup: 2026-05-22 11:33 — `/Users/mac/odoo_backups/famoil_20260522_1133/`
- Backup script: `scripts/backup_famoil.sh` (Phase 2 enhanced — compression + governance bridge)
- Governance bridge: `backups/BACKUP_MANIFEST.md` (must be committed after each run)
- **A fresh backup is overdue** — 5 days of changes since last backup; run before next change
- Automated scheduling: launchd plists created — install per MACOS_BACKUP_AUTOMATION.md
- Cloud offsite sync: sync script created — requires `brew install rclone` + `rclone config gdrive`

---

## GOVERNANCE ENGINE STATUS

| Component                        | Status                  | Notes                              |
|---------------------------------|-------------------------|------------------------------------|
| Hook system (.claude/settings.json) | ACTIVE              | Created 2026-05-27                 |
| PreToolUse — pre_tool_guard.sh  | ACTIVE (BLOCK exit 2)   | Blocks dangerous bash commands     |
| PreToolUse — file_protection_guard.sh | ACTIVE (BLOCK exit 2) | Blocks writes outside repo       |
| PostToolUse — post_tool_validator.sh | ACTIVE (WARN exit 0) | Validates written files           |
| PostToolUse — audit_logger.sh   | ACTIVE (LOG exit 0)     | Logs all bash commands             |
| SessionStart — session_start_loader.sh | ACTIVE (WARN exit 0) | Loads context at session start  |
| Stop — session_end_reporter.sh  | ACTIVE (LOG exit 0)     | Reports session summary            |
| GitHub Actions — ci_review.yml  | ACTIVE                  | Fires on every PR                  |
| GitHub Actions — doc_lint.yml   | ACTIVE                  | Fires on push + PR to main         |
| GitHub Actions — backup_check.yml | ACTIVE               | Fires every Monday 06:00 UTC       |
| GitHub Actions — security_scan.yml | ACTIVE              | Fires on push + PR to main         |
| Branch protection (main)        | ENABLED                 | Applied by operator 2026-05-27     |
| Last audit log entry            | 2026-05-27 session start|                                    |
| Last backup verification        | 2026-05-22              |                                    |

---

## KNOWN ISSUES

> Full log: see docs/famoil_erp_template/KNOWN_ISSUES.md (13 issues documented)

**Active open issues:**
- Demo warehouses (Chicago 1, YourCompany) not yet archived
- Demo company "My Company (San Francisco)" not archived
- Cost method not set on Raw Materials category
- Consumables (Hexane, Lubricant Oil) missing from BOM 10
- Spare parts/consumables list_price = ₦1 (placeholder)
- No remote git repository connected (Phase 4 blocked)

---

## REPOSITORY STRUCTURE

```
/Users/mac/odoo17/
├── CLAUDE.md                        ← this file
├── CHANGELOG.md                     ← version history
├── VERSION                          ← FamOil-Template-v1.0.0
├── PROJECT_FACTORY_MANUAL.md        ← software factory overview
├── .claude/
│   ├── settings.json                ← hook engine config
│   └── hooks/                       ← 6 enforcement scripts
├── .github/
│   └── workflows/                   ← CI/CD workflows (pending remote)
├── docs/
│   ├── IMPLEMENTATION_STANDARDS.md  ← 11 core engineering rules
│   ├── DEPLOYMENT_GUIDE.md
│   ├── TESTING_GUIDE.md
│   ├── CSV_STANDARDS.md
│   ├── MODULE_REGISTRY.md
│   ├── INDUSTRY_TEMPLATE_GUIDE.md
│   ├── BACKUP_AND_RECOVERY.md
│   ├── SECURITY_GUIDELINES.md
│   ├── ONBOARDING_GUIDE.md
│   ├── CHANGELOG.md
│   ├── architecture/
│   │   ├── ARCHITECTURAL_PRINCIPLES.md
│   │   └── GOVERNANCE_ENGINE.md
│   ├── sops/
│   │   └── CI_CD_RUNBOOK.md
│   └── famoil_erp_template/         ← FamOil-specific docs (14 files)
├── csv_templates/                   ← 9 reusable import templates
├── custom_addons/                   ← 11 installed modules
├── scripts/                         ← 4 operational scripts
├── prompts/                         ← prompt library
├── tests/                           ← test scripts
└── logs/                            ← local audit logs (git-ignored)
```

**Deviations from spec:**
- `notes/` directory exists (legacy) — not in spec, will be retained
- `templates/` directory exists (legacy CSV location) — content migrated to `csv_templates/`
- `custom_addons_farm/` exists (farm project) — unrelated to FamOil, retained

---

## CONTACTS & ESCALATION

| Role             | Contact                  |
|-----------------|--------------------------|
| Project Owner   | FamOil FTZ               |
| Technical Lead  | aliyuumaru@gmail.com     |
| Escalation      | Stop and report to operator if unsure |

**If Claude is unsure:** STOP. Do not proceed. Report the uncertainty clearly
and wait for operator instruction. Never take a destructive action to resolve ambiguity.
