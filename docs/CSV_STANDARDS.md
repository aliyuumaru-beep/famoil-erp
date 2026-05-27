# CSV Standards
# FamOil Software Factory — Import Template Specification
# Version: 1.0 | Created: 2026-05-27

---

## 1. Column Naming Conventions

- Column headers must match Odoo import field names exactly (case-sensitive)
- Use `id` for external ID columns (used for cross-referencing)
- Use `/id` suffix for relational fields that reference external IDs
- Use `name` for human-readable name fields
- Separate words with underscores where Odoo requires it

---

## 2. Mandatory vs Optional Fields

Each CSV template defines fields as:
- **REQUIRED** — must be present and non-empty for Odoo to accept the row
- **RECOMMENDED** — strongly advised for operational completeness
- **OPTIONAL** — can be left blank; Odoo applies defaults

The `id` (external ID) column is REQUIRED in all templates to enable
cross-referencing between files and safe re-importing.

---

## 3. Data Type Requirements

| Field Type   | Format                                     | Example                    |
|-------------|-------------------------------------------|----------------------------|
| Text         | Plain string                               | `Crude Soya Oil`           |
| Number       | Decimal with period separator              | `140.00`                   |
| Boolean      | `True` or `False` (capitalised)           | `True`                     |
| Date         | `YYYY-MM-DD`                               | `2026-05-22`               |
| Many2one     | External ID of related record              | `famoil_product_category_fg`|
| Many2many    | Comma-separated external IDs               | `id1,id2`                  |
| Selection    | Exact key value as stored in Odoo          | `product` (for type)       |

---

## 4. Example Row Format

Every CSV template must include:
- **Row 1:** Column headers
- **Row 2:** Comment row explaining each column (prefixed with `#` — remove before import)
- **Row 3+:** Data rows (clearly marked as EXAMPLE — replace with real data)

Example:
```csv
id,name,categ_id/id,type,standard_price
# id=external ID | name=product name | categ_id/id=category ext ID | type=product type | standard_price=cost
famoil_product_soyabean_example,SoyaBean [EXAMPLE],famoil_categ_raw_materials,product,710.00
```

---

## 5. Import Sequence

Import in this order (dependencies must exist before dependents):

1. `product_categories.csv` — categories before products
2. `warehouses.csv` — warehouse before locations
3. `locations.csv` — locations before operation types and BOMs
4. `work_centers.csv` — work centers before BOM operations
5. `operation_types.csv` — operation types before BOMs
6. `products.csv` — products before BOMs
7. `bom_headers.csv` — BOM header before components and operations
8. `bom_lines.csv` — BOM components (requires BOM header to exist)
9. `byproducts.csv` — BOM byproducts (requires BOM header to exist)

---

## 6. External ID Prefix Convention

Use a consistent project prefix on all external IDs to avoid conflicts:

| Prefix                | Used for                        |
|----------------------|---------------------------------|
| `famoil_`            | FamOil production instance      |
| `<clientcode>_`      | Client-specific fork             |
| `tpl_`               | Template rows (example/generic) |

Example: `famoil_product_crude_soya_oil`, `famoil_categ_finished_goods`

---

## 7. Adapting for a New Client

1. Replace `famoil_` prefix with `<clientcode>_` in all `id` fields
2. Update product names, quantities, and costs to match client data
3. Update work center names and rates from client's actual overhead costs
4. Adjust BOM ratios based on client's actual yield data
5. Do not import example rows — delete or overwrite all EXAMPLE marker rows
