# Industry Template Guide
# FamOil Software Factory — How to Fork for a New Industry
# Version: 1.1 | Created: 2026-05-27 | Updated: 2026-05-28

> Multi-industry expansion strategy and priority sequencing:
> `docs/roadmap/PLATFORM_ROADMAP.md` § 7 (Priority 7 — Multi-Industry Template Expansion)
>
> FamOil remains the primary reference implementation until commercial MVP stabilizes.
> Do not begin new industry templates before the FamOil template reaches operational maturity.

---

## 1. What Stays the Same Across All Forks

These elements are reusable without modification for any agro-processing industry:

| Component | Reusable As-Is |
|----------|---------------|
| Backup scripts (`backup_famoil.sh`) | Parameterise DB_NAME and paths |
| Inspection scripts | Parameterise DB_NAME |
| Governance hook system (`.claude/`) | No changes needed |
| GitHub Actions workflows | No changes needed |
| IMPLEMENTATION_STANDARDS.md | No changes needed |
| ONBOARDING_GUIDE.md | Update project name only |
| CSV template structure | Update data rows only |
| 3-step warehouse routing | Universal for quality-controlled processing |
| `mrp_component_availability_check` module | No changes needed |
| `stock_crude_oil_tank_restriction` pattern | Adapt location and product names |
| Category structure (RM / FG / WIP / etc.) | Rename categories per industry |
| Nigerian compliance layer | No changes for Nigerian clients |

---

## 2. What Changes Per Industry

| Element | What to Change | Notes |
|---------|---------------|-------|
| BOM ratios | Input qty → output qty | Verify against plant yield data |
| Work centers | Names, rates | Get actual overhead per stage |
| Tank/storage locations | Names and hierarchy | Match physical plant layout |
| Byproducts | Products, quantities, cost shares | Use NRV method when prices stable |
| Product names | Raw materials, finished goods | Industry-specific naming |
| Manufacturing stages | Number of BOMs | 1-stage vs 3-stage pipelines |
| Regulatory requirements | NAFDAC registration per SKU | Industry-specific |

---

## 3. Industry Variation Summary

See full matrix: `docs/famoil_erp_template/INDUSTRY_VARIATION_MATRIX.md`

| Industry | Effort vs FamOil | Key Difference |
|----------|-----------------|---------------|
| Groundnut Oil Mill | LOW | Similar extraction; fewer stages |
| Rice Mill | LOW | Hulling + milling; different byproduct |
| Palm Oil Mill | MEDIUM | Multi-stage pressing; FFB input |
| Shea Butter | MEDIUM | Different extraction chemistry |
| Feed Mill | MEDIUM | Blending BOM; formulation logic |
| FMCG Food Processing | HIGH | Multi-product; lots + expiry tracking |

---

## 4. Fork Procedure

1. **Review** `docs/famoil_erp_template/CLIENT_DISCOVERY_TEMPLATE.md` and complete for the new client
2. **Determine** industry variation level (LOW / MEDIUM / HIGH) from INDUSTRY_VARIATION_MATRIX.md
3. **Name** the new template using the convention in `docs/famoil_erp_template/TEMPLATE_VERSIONING.md`
4. **Create** a new Odoo database: `createdb -U odoo -E UTF8 "ClientDB" --without-demo=all`
5. **Copy** CSV templates from `csv_templates/` to a working directory; update prefix and data
6. **Import** in the sequence defined in `docs/CSV_STANDARDS.md`
7. **Create** BOMs specific to the new industry
8. **Configure** operation types and putaway rules (do this BEFORE first MO)
9. **Deploy** tank/location restriction module adapted for new industry
10. **Test** using the manufacturing flow scenarios in `docs/TESTING_GUIDE.md`
11. **Document** all decisions in a new `DECISION_LOG.md` for the client fork

---

## 5. Template Versioning

Naming convention: `FAMOIL-TPL-{INDUSTRY}-v{MAJOR}.{MINOR}.{PATCH}`

Client fork: `FAMOIL-{CLIENTCODE}-{INDUSTRY}-v{MAJOR}.{MINOR}`

Example:
- Base template: `FAMOIL-TPL-SOYA-v1.0.0`
- Client fork: `FAMOIL-ABC-PALM-v1.0`

Never modify the base template when implementing for a client. Always fork.
