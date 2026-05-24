# FamOil — System Architecture

## Directory Layout

```
/Users/mac/odoo17/
├── odoo/                       # Odoo 17 core (git branch: 17.0)
│   ├── odoo-bin                # Server entry point
│   ├── odoo/addons/            # Core addons
│   ├── odoo.conf               # Config (dbfilter=OdooClean — NOT for FamOil)
│   └── odoo_farm.conf          # Alt config
├── custom_addons/              # Project custom modules
│   ├── accounting_pdf_reports/
│   ├── maintenance_spareparts_v6/
│   ├── mrp_component_availability_check/   # FamOil custom
│   ├── om_account_accountant/
│   ├── om_account_asset/
│   ├── om_account_budget/
│   ├── om_account_daily_reports/
│   ├── om_account_followup/
│   ├── om_fiscal_year/
│   ├── om_recurring_payments/
│   └── stock_crude_oil_tank_restriction/   # FamOil custom
├── custom_addons_farm/         # Unused farm project addons
├── docs/famoil_erp_template/   # This documentation
├── scripts/                    # Utility scripts
├── test_component_check.py     # Test: component availability
└── test_soya.py                # Test: soya oil flow
```

## Addons Path (as launched)

```
odoo/odoo/addons
custom_addons
/Users/mac/oca_web
```

The `odoo.conf` file targets `OdooClean` database. FamOil is started via CLI override (run from `/Users/mac/odoo17`):
```bash
source odoo/venv/bin/activate
python odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web
```
> `-i <module>` flag is for first-time installation only — do not include on normal start.

## OCA Web Addons (/Users/mac/oca_web)

| Module                        | Purpose                          |
|------------------------------|----------------------------------|
| web_responsive               | Mobile-friendly UI               |
| web_environment_ribbon       | Environment label banner         |
| web_notify                   | Push notifications               |
| web_refresher                | Auto-refresh list views          |
| web_theme_classic            | Classic Odoo theme               |
| web_dialog_size              | Resizable dialogs                |
| web_m2x_options              | Many2x field options             |
| web_pivot_computed_measure   | Pivot table custom measures      |
| web_search_with_and          | AND logic in search              |
| web_remember_tree_column_width | Persistent column widths       |
| (+ others)                   |                                  |

## Custom FamOil Modules

### stock_crude_oil_tank_restriction
- **Purpose**: Prevents any product except Crude Soya Oil from being transferred into Crude Oil Tank 1 or Tank 2.
- **Mechanism**: Overrides `button_validate` on `stock.picking`. Raises `UserError` on violation.
- **Lookup**: Searches for locations by name (`ilike 'Crude Oil Tank'`, usage=internal) and product by name (`= 'Crude Soya Oil'`) at runtime. No hardcoded IDs — works correctly if locations or products are recreated.

### mrp_component_availability_check
- **Purpose**: Blocks manufacturing order completion if component quantities are insufficient.
- **Mechanism**: Overrides `_button_mark_done_sanity_checks`. Compares reserved vs required quantity for each raw move.

## Installed Modules (80 total)

Core ERP:
- `stock`, `stock_account`, `mrp`, `mrp_account`
- `account`, `account_payment`, `account_check_printing`
- `sale`, `sale_management`, `sale_stock`, `sale_mrp`
- `purchase`, `purchase_stock`, `purchase_mrp`

Custom/OCA:
- `accounting_pdf_reports`, `om_account_accountant`, `om_account_asset`
- `om_account_budget`, `om_account_daily_reports`, `om_account_followup`
- `om_fiscal_year`, `om_recurring_payments`
- `web_responsive` (via oca_web)
- `stock_crude_oil_tank_restriction`, `mrp_component_availability_check`

## Databases on This Instance

| Database  | Owner | Collation   | Notes                        |
|-----------|-------|-------------|------------------------------|
| Famoil    | odoo  | C           | **Active running instance**  |
| OdooClean | odoo  | en_US.UTF-8 | Default conf target          |
| OdooTest  | odoo  | C           | Test database                |
| aedc_demo | odoo  | C           | Demo/other project           |
| odoo_farm | odoo  | C           | Farm project DB              |
| odoo      | odoo  | C           | Blank/system DB              |

## Filestore Location

```
/Users/mac/Library/Application Support/Odoo/filestore/Famoil/
```
