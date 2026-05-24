# CHANGELOG

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
