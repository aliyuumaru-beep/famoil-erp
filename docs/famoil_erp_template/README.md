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

| Phase | Description                        | Status      |
|------|------------------------------------|-------------|
| 1    | Inspection, Backup & Stabilization | COMPLETE    |
| 2    | Architecture Extraction & ERP Standardization | COMPLETE |
| 3    | Cleanup & Go-Live Preparation      | PENDING     |
| 4    | Reporting & Exports                | PENDING     |

## Documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — System layout, modules, addons
- [MANUFACTURING_FLOW.md](MANUFACTURING_FLOW.md) — BOM, work centers, routing
- [CONFIGURATION_EXPORTS.md](CONFIGURATION_EXPORTS.md) — Products, locations, categories
- [BACKUP_AND_RESTORE.md](BACKUP_AND_RESTORE.md) — Backup procedures
- [COSTING_VALIDATION.md](COSTING_VALIDATION.md) — Batch cost model, unit cost calculations
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — Issues, root causes, fixes, prevention rules
- [DECISION_LOG.md](DECISION_LOG.md) — Architectural decisions and rationale
- [IMPLEMENTATION_PLAYBOOK.md](IMPLEMENTATION_PLAYBOOK.md) — Step-by-step deployment guide
- [VALIDATION_CHECKLIST.md](VALIDATION_CHECKLIST.md) — Pre-go-live checklist
- [STANDARDIZATION_NOTES.md](STANDARDIZATION_NOTES.md) — Reusable framework principles

## Key Findings (Phase 1)

- Two databases exist: `FamOil` and `Famoil` (different capitalisation). Running instance uses `Famoil`.
- Demo data still present: `Chicago 1` warehouse, office furniture products, demo BOMs.
- `SoyaBean` (raw material) is miscategorised under `All` instead of `All / FamOil / Raw Materials`.
- Byproducts confirmed: 10 kg SoapStock (5% cost share, sellable) + 10 kg Production Waste (0% cost share). BOM is correct.
- Cost method not set on `Raw Materials` category.
- `stock_crude_oil_tank_restriction` uses hardcoded DB IDs — will break if locations are recreated.

## Scripts

| Script                       | Purpose                          |
|-----------------------------|----------------------------------|
| `scripts/backup_famoil.sh`  | Full backup (DB + filestore + addons) |
| `scripts/inspect_famoil_config.sh` | Read-only config inspection |
