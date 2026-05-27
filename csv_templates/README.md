# CSV Template Library

Reusable import templates for deploying the FamOil agro-processing ERP framework.

## Import Order

Always import in this sequence (dependencies must exist before dependents):

1. `product_categories.csv` — Inventory > Configuration > Product Categories > Import
2. `products.csv` — Inventory > Products > Import
3. `stock_locations.csv` — Inventory > Configuration > Locations > Import (after warehouse created)
4. `work_centers.csv` — Manufacturing > Configuration > Work Centers > Import
5. `bom_header.csv` — Manufacturing > Bills of Materials > Import
6. `bom_components.csv` — Manufacturing > Bills of Materials > [open BOM] > Components > Import
7. `bom_byproducts.csv` — Manufacturing > Bills of Materials > [open BOM] > Byproducts > Import
8. `bom_operations.csv` — Manufacturing > Bills of Materials > [open BOM] > Operations > Import

## Notes

- Lines starting with `#` are comments — remove before importing.
- Fields marked `PLACEHOLDER` must be filled with real values before import.
- `id` fields are external IDs — used for cross-referencing between templates.
- `standard_price` on products with cost method = average must be set post-import via the product cost update form (not CSV — Odoo handles this through `ir_property`).

## Adapting for a New Client

1. Replace `famoil_` prefix in `id` fields with `clientname_`.
2. Update work center names and rates with client-specific values.
3. Update product names and quantities to match client's production process.
4. Adjust byproduct quantities and cost shares based on actual yield data.
