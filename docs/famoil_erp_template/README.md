# FamOil ERP — Project Overview

## Identity

| Field          | Value                        |
|---------------|------------------------------|
| Project Name  | FamOil                       |
| Database      | Famoil (PostgreSQL)          |
| Odoo Version  | 17.0.1.3 Community Edition  |
| PostgreSQL    | 16.11 (Homebrew, macOS)      |
| Industry      | Soybean Oil Processing       |
| Country       | Nigeria                      |
| Currency      | NGN                          |
| Server        | localhost:8069               |
| Addons Path   | See ARCHITECTURE.md          |

## Phase Status

| Phase | Description                               | Status      | Date       |
|------|-------------------------------------------|-------------|------------|
| 1    | Inspection, Backup & Stabilization        | COMPLETE    | 2026-05-22 |
| 2    | Configuration Validation & Pipeline Setup | COMPLETE    | 2026-05-24 |
| 3    | Commercialisation Framework               | COMPLETE    | 2026-05-24 |
| 4    | Cleanup & Go-Live Preparation             | PENDING     |            |
| 5    | Reporting & Exports                       | PENDING     |            |

## Documents

### Phase 1–2 (Configuration)
- [ARCHITECTURE.md](ARCHITECTURE.md) — System layout, modules, addons
- [MANUFACTURING_FLOW.md](MANUFACTURING_FLOW.md) — 3-stage pipeline, BOMs, work centers, putaway rules
- [CONFIGURATION_EXPORTS.md](CONFIGURATION_EXPORTS.md) — Products, locations, categories
- [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md) — Backup procedures and backup log
- [COSTING_VALIDATION.md](COSTING_VALIDATION.md) — Batch cost model, unit cost calculations
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — Issues, root causes, fixes, prevention rules
- [DECISION_LOG.md](DECISION_LOG.md) — Architectural decisions and rationale
- [IMPLEMENTATION_PLAYBOOK.md](IMPLEMENTATION_PLAYBOOK.md) — Step-by-step deployment guide
- [VALIDATION_CHECKLIST.md](VALIDATION_CHECKLIST.md) — Pre-go-live checklist
- [STANDARDIZATION_NOTES.md](STANDARDIZATION_NOTES.md) — Reusable framework principles

### Phase 3 (Commercialisation)
- [INDUSTRY_VARIATION_MATRIX.md](INDUSTRY_VARIATION_MATRIX.md) — 7 industries scored vs FamOil template
- [CLIENT_DISCOVERY_TEMPLATE.md](CLIENT_DISCOVERY_TEMPLATE.md) — 8-section discovery questionnaire
- [COMMERCIAL_GUIDE.md](COMMERCIAL_GUIDE.md) — CONFIDENTIAL; pricing tiers and engagement model
- [TEMPLATE_VERSIONING.md](TEMPLATE_VERSIONING.md) — Naming convention, fork strategy, upgrade path
- [DATA_MIGRATION_SCAFFOLD.md](DATA_MIGRATION_SCAFFOLD.md) — 14-step migration sequence with CSV templates
- [NIGERIA_COMPLIANCE.md](NIGERIA_COMPLIANCE.md) — VAT, WHT, PENCOM, ITF, NSITF, NAFDAC, SON, CoA

## Key Findings & Status

| Finding | Status |
|---------|--------|
| Two databases: `FamOil` (empty) and `Famoil` (active) | RESOLVED — `FamOil` dropped 2026-05-22 |
| Demo warehouses (Chicago 1, YourCompany) with phantom stock | OPEN — not yet archived |
| `SoyaBean` category: confirmed correctly in Raw Materials (not root "All") | RESOLVED 2026-05-22 |
| SoapStock incorrectly in crude oil BOM (BOM 10) | RESOLVED 2026-05-23 — moved to refining BOM |
| Soya Cake cost share updated 35% → 40% | RESOLVED 2026-05-23 |
| `stock_crude_oil_tank_restriction` used hardcoded DB IDs | RESOLVED 2026-05-22 — v17.0.1.1.0 uses name lookup |
| Negative quant -81 kg in Crude Oil Tank 1 | RESOLVED 2026-05-24 |
| Misplaced crude/refined oil and SoapStock stock | RESOLVED 2026-05-24 |
| 3-stage pipeline (Extraction → Refining → Packaging) | COMPLETE 2026-05-24 |
| Putaway rules for all manufacturing outputs | COMPLETE 2026-05-24 |
| Cost method not set on `Raw Materials` category | OPEN |
| Consumables (Hexane, Lubricant) missing from BOM 10 | OPEN |
| Demo company "My Company (San Francisco)" not archived | OPEN |

## Scripts

| Script                                 | Purpose                                             |
|---------------------------------------|-----------------------------------------------------|
| `scripts/backup_famoil.sh`            | Full backup (DB + filestore + addons)               |
| `scripts/inspect_famoil_config.sh`    | Read-only config inspection                         |
| `scripts/process_refined_oil_mo.py`   | Creates and completes Refined Soya Oil MO (135 kg)  |
| `scripts/fix_locations_and_routing.py`| Stock corrections + putaway rule creation           |
