# Module Registry
# FamOil Software Factory — Installed Modules Inventory
# Version: 1.3 | Created: 2026-05-27 | Updated: 2026-11-25

---

## Custom FamOil Modules (in custom_addons/)

### stock_crude_oil_tank_restriction
| Field | Value |
|-------|-------|
| Version | 17.0.1.1.0 |
| Purpose | Prevents non-Crude-Soya-Oil products from being transferred into Crude Oil Tank 1 or Tank 2 |
| Mechanism | Overrides `button_validate` on `stock.picking`; raises `UserError` on violation |
| Lookup strategy | Runtime name search — no hardcoded IDs |
| Override point | `stock.picking.button_validate()` |
| Upgrade risk | LOW — override is at validation level; test after any Odoo upgrade |
| Known conflicts | None |

### mrp_component_availability_check
| Field | Value |
|-------|-------|
| Version | current |
| Purpose | Blocks manufacturing order completion if component quantities are insufficient |
| Mechanism | Overrides `_button_mark_done_sanity_checks` on `mrp.production` |
| Override point | `mrp.production._button_mark_done_sanity_checks()` |
| Upgrade risk | MEDIUM — sanity check method may change across Odoo versions |
| Known conflicts | None |

### stock_landed_cost_po_check
| Field | Value |
|-------|-------|
| Version | 17.0.1.0.0 |
| Purpose | Blocks landed cost validation if any linked receipt was not created from a Purchase Order; schedules automated activity reminder on every validated SoyaBean receipt |
| Mechanism | Overrides `button_validate` on `stock.landed.cost`; raises `UserError` if `picking_type_code != 'incoming'` or `move_ids.filtered('purchase_line_id')` is empty. Automated action fires on `stock.picking` state → done to schedule a todo activity |
| Override point | `stock.landed.cost.button_validate()` |
| Depends | `stock_landed_costs`, `purchase_stock`, `base_automation`, `mail` |
| Decision | DEC-016 |
| Upgrade risk | LOW — constraint logic is simple; re-run 3-test suite after any Odoo upgrade |
| Known conflicts | None |

---

## Third-Party Modules (in custom_addons/)

| Module | Version | Purpose | Upgrade Risk |
|--------|---------|---------|-------------|
| `accounting_pdf_reports` | 17.0 | PDF accounting reports (trial balance, P&L, etc.) | LOW |
| `maintenance_spareparts_v6` | 17.0 | Spare parts tracking linked to maintenance | LOW |
| `om_account_accountant` | 17.0 | Extended accounting features | LOW |
| `om_account_asset` | 17.0 | Fixed asset management and depreciation | LOW |
| `om_account_budget` | 17.0 | Budget management and variance tracking | LOW |
| `om_account_daily_reports` | 17.0 | Daily accounting reports | LOW |
| `om_account_followup` | 17.0 | Customer payment follow-up automation | LOW |
| `om_fiscal_year` | 17.0 | Fiscal year configuration | LOW |
| `om_recurring_payments` | 17.0 | Recurring payment scheduling | LOW |

---

## OCA Web Addons (embedded in `docker/oca_addons/` — DEC-014 / v1.17.0)

> **Path change:** These modules are now committed to the repository at `docker/oca_addons/`
> and are baked into the Docker image at build time. The original source was `/Users/mac/oca_web`
> (local macOS path, non-portable). `docker/oca_addons/` is the canonical, portable location.
> On non-Docker deployments, add `docker/oca_addons/` to `--addons-path`.

| Module | Version (copied 2026-11-18) | Repo Path | Purpose |
|--------|-----------------------------|-----------|---------|
| `web_responsive` | 17.0.1.1.11 | `docker/oca_addons/web_responsive/` | Mobile-friendly UI (essential for plant floor tablet use) |
| `web_environment_ribbon` | 17.0.1.0.3 | `docker/oca_addons/web_environment_ribbon/` | Environment label banner (shows DEV/PROD) |
| `web_notify` | 17.0.1.1.0 | `docker/oca_addons/web_notify/` | Browser push notifications |
| `web_refresher` | 17.0.1.1.3 | `docker/oca_addons/web_refresher/` | Auto-refresh list views |
| `web_theme_classic` | 17.0.1.0.0 | `docker/oca_addons/web_theme_classic/` | Classic Odoo 16/17 theme |
| `web_dialog_size` | 17.0.1.0.2 | `docker/oca_addons/web_dialog_size/` | Resizable dialog boxes |
| `web_m2x_options` | 17.0.1.0.8 | `docker/oca_addons/web_m2x_options/` | Many2x field creation options |
| `web_pivot_computed_measure` | 17.0.1.0.0 | `docker/oca_addons/web_pivot_computed_measure/` | Custom computed measures in pivot tables |
| `web_search_with_and` | 17.0.1.0.0 | `docker/oca_addons/web_search_with_and/` | AND logic in search bar |
| `web_remember_tree_column_width` | 17.0.1.0.0 | `docker/oca_addons/web_remember_tree_column_width/` | Persistent column widths |

---

## Core Odoo Modules (native)

| Module | Purpose |
|--------|---------|
| `stock`, `stock_account` | Inventory and inventory valuation |
| `mrp`, `mrp_account` | Manufacturing and manufacturing costing |
| `account`, `account_payment`, `account_check_printing` | Accounting |
| `sale`, `sale_management`, `sale_stock`, `sale_mrp` | Sales |
| `purchase`, `purchase_stock`, `purchase_mrp` | Purchasing |

---

## Development Scripts (in scripts/)

### SCR-001 — pre_review_check.py

| Field | Value |
|-------|-------|
| Type | Script (Python 3 CLI — no Odoo runtime dependency) |
| Status | ACTIVE |
| Introduced In | `feat/gov-uplift-erp-agro` (WP-GOV-01) |
| Owner | Technical Lead |
| Path | `scripts/pre_review_check.py` |
| Purpose | Static checks before `gov review`: inline imports, create() decorator, ACL XML ID references, hardcoded database ID constants, Odoo 16→17 breaking patterns in branch-changed XML files, hardcoded secrets (excluding odoo/ and venv/) |
| Scope | `custom_addons/stock_crude_oil_tank_restriction`, `mrp_component_availability_check`, `stock_landed_cost_po_check`; secrets scan covers full repo minus skip_dirs |
| Usage | `python3 scripts/pre_review_check.py` — exits 0 (clean) or 1 (issues found) |
| Tests | `scripts/tests/test_pre_review_check.py` — 19 unittest cases; all pass. Coverage: all 6 checks — check_inline_imports (1), check_create_decorator (2), check_acl_xml_ids (3), check_no_hardcoded_ids (4), check_version_compat 5a/5b/commented-out/5c, check_no_secrets (6). |
| Limitations | `check_acl_xml_ids` resolves local `groups.xml` refs only — cross-module group refs fire false positives (OQ-GOV-04). **OQ-GOV-04 MUST be fixed before any WP that adds an `ir.model.access.csv` row referencing a cross-module group.** `check_no_secrets` covers `password`/`admin_passwd` only; not `api_key`/`token`/`secret` (OQ-GOV-05; test gaps in OQ-GOV-07). `check_create_decorator` lookback covers only 2 lines above `def create(` — decorator more than 2 lines above is missed (OQ-GOV-03b). Line numbers after XML comment strip may be off by N (OQ-GOV-06). `check_version_compat` check 5c advisory print is not unit-tested (OQ-GOV-08). `HARDCODED_ID_PATTERN` only detects SCREAMING_SNAKE_CASE constants — mixed-case or snake_case names evade detection (OQ-GOV-09). |
| Decision | DEC-017 / WP-GOV-01 |
| Added | 2026-11-25 |

---

## Known Conflicts

None currently identified. Monitor after every Odoo version upgrade.

---

## Upgrade Procedure

When upgrading Odoo version:
1. Test `stock_crude_oil_tank_restriction` — `button_validate` override must still work
2. Test `mrp_component_availability_check` — `_button_mark_done_sanity_checks` must still exist
3. Test `stock_landed_cost_po_check` — run 3-test suite; verify `purchase_line_id` still exists on `stock.move`
4. Check all OCA module compatibility with new Odoo version on https://github.com/OCA — note: `web_responsive` adds stored columns to `res.users` (`apps_menu_search_type`, `apps_menu_theme`, `is_redirect_home`); confirm those columns are present after any `web_responsive` version change before restarting Odoo (`web_notify` fields are computed-only — no DB columns)
5. Check `om_*` modules for version compatibility
6. Run full manufacturing test (Test A and B from `docs/TESTING_GUIDE.md`) before go-live
