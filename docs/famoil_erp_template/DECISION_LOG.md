# FamOil — Decision Log

_Records every major architectural decision, rationale, alternatives, trade-offs, and conditions for revisiting._

---

## DEC-001 — Odoo Community vs Enterprise Edition

**Decision:** Use Odoo 17 Community Edition.

**Rationale:**
- Zero licence cost — critical for a startup agro-processor in Nigeria.
- Community covers all core requirements: Inventory, Manufacturing, Accounting.
- Local technical capacity can support Community without vendor dependency.

**Alternatives Considered:**
- Odoo Enterprise: adds MRP II, maintenance scheduling, quality control, advanced costing. Licensing cost prohibitive at this stage.
- Other ERPs (SAP B1, ERPNext): higher implementation complexity or limited local support.

**Trade-offs:**
- No native Quality module — quality holds must be managed via manual location (QC area) workflows.
- No advanced MRP scheduling (no rough-cut capacity planning).
- No maintenance scheduling module (custom `maintenance_spareparts_v6` used instead).
- Reporting relies on OCA/community PDF report modules.

**Revisit Conditions:**
- When monthly revenue exceeds ₦50M and reporting/compliance needs outgrow Community.
- When a dedicated quality management process is required by a buyer or certification body.

---

## DEC-002 — Work Center Costing vs Advanced Accounting Allocation

**Decision:** Use Odoo work center hourly cost (`costs_hour`) for overhead allocation.

**Rationale:**
- Native Odoo mechanism — no custom development required.
- Cost per operation is automatically posted to WIP account when manufacturing orders are validated.
- Straightforward to configure and explain to plant operators.

**Alternatives Considered:**
- Manual journal entry overhead allocation (monthly overhead spread).
- Activity-based costing via analytic accounts.
- Odoo Enterprise manufacturing workcenter with detailed cost components.

**Trade-offs:**
- `costs_hour` is a flat rate — does not separate labour, electricity, depreciation.
- Rate must be manually updated when actual costs change (no automatic variance tracking).
- Over/under absorption of overhead is not automatically detected.

**Work Center Rates (current):**

| Section  | ₦/hr   | Basis (assumed)      |
|---------|-------|---------------------|
| Cleaning  | 15,000 | Labour + utilities  |
| Extrusion | 45,000 | Machine + electricity |
| Pressing  | 75,000 | High-power equipment |
| Filtration| 20,000 | Labour + filter costs |
| Packaging | 12,000 | Labour              |

**Revisit Conditions:**
- When actual plant cost data (payroll, utility bills, depreciation schedule) is available for proper rate validation.
- If variance between standard and actual cost exceeds 10% consistently.

---

## DEC-003 — FIFO vs Average Costing for Finished Goods

**Decision:** Finished Goods (Crude Soya Oil, Soya Cake, SoapStock) use FIFO. Raw Materials (SoyaBean) use Average Cost.

**Rationale:**
- FIFO for finished goods: accurately reflects the cost of oldest stock, important for food/agro products with perishability.
- Average for raw materials: SoyaBean is purchased in bulk at varying seasonal prices — average cost smooths volatility and is simpler to reconcile.

**Alternatives Considered:**
- Standard cost: requires setting and maintaining standard rates — too rigid for commodity inputs with price volatility.
- FIFO for raw materials: would create many small valuation layers with each purchase, complex to manage without dedicated purchasing team.

**Trade-offs:**
- FIFO finished goods requires accurate lot/serial tracking if individual batches need individual cost tracing.
- Average cost for SoyaBean means a sudden large purchase at a different price immediately changes the cost basis for all subsequent production.

**Revisit Conditions:**
- If auditors or investors require standard costing for budget variance analysis.
- When purchasing volume is large enough to justify per-lot cost tracking.

---

## DEC-004 — Internal Tank Locations vs Virtual Locations for Oil Storage

**Decision:** Crude oil tanks (Tank 1, Tank 2) and filtered oil tanks are modelled as **internal stock locations** under FamOilWH/Stock.

**Rationale:**
- Internal locations carry real inventory value and appear in stock reports.
- Physical tanks are real assets holding real product — not a virtual concept.
- Allows tank-level stock visibility (how many litres in Tank 1 vs Tank 2).
- Transfer between tanks is tracked as an internal transfer with full audit trail.

**Alternatives Considered:**
- Virtual locations: appropriate for theoretical quantities (e.g., in-transit), not for physical tanks.
- Single "Crude Oil" location: simpler but loses per-tank traceability.

**Trade-offs:**
- Requires internal transfers to move product between tanks — adds operational steps.
- Tank capacity enforcement is not native in Odoo Community — requires custom module (`stock_crude_oil_tank_restriction`).

**Revisit Conditions:**
- If tanks are sold or decommissioned.
- If a third tank is added — simply add a new child location under CW/Stock.

---

## DEC-005 — Byproduct Cost Share Strategy

**Decision:** SoapStock assigned 5% cost share; Soya Cake assigned 35% cost share; Production Waste 0%.

**Rationale:**
- Soya Cake is the highest-volume co-product (840 kg per batch) and has commercial value (₦750/kg list price). Capturing 35% of cost reflects its economic significance.
- SoapStock (10 kg) has commercial value but lower volume — 5% cost share is appropriate.
- Production Waste has no economic value and is disposed — 0% prevents artificial cost inflation.
- The 60% residual to Crude Soya Oil reflects that it is the primary intended output.

**Alternatives Considered:**
- Net realisable value (NRV) method: allocate cost based on relative selling prices. More accurate but requires stable, reliable selling prices.
- All cost to main product (0% byproduct share): simpler but overstates Crude Soya Oil cost and understates byproduct profitability.
- Physical quantity method: allocate by kg weight. Would give Soya Cake 84% of cost — misrepresents economics.

**Trade-offs:**
- Current percentages are estimates — not derived from NRV analysis.
- If SoapStock selling price rises significantly, its 5% share may understate its cost basis.

**Revisit Conditions:**
- When stable selling price data is available → recalculate using NRV method.
- Annually, when cost and price data is reviewed.

---

## DEC-006 — 3-Step Inbound / 3-Step Outbound for FamOilWH

**Decision:** FamOilWH configured for 3-step inbound (Input → QC → Stock) and 3-step outbound (Pick → Pack → Ship).

**Rationale:**
- Inbound 3-step allows for quality inspection of incoming SoyaBean before it enters RM Warehouse.
- Outbound 3-step supports picking from storage, packing into final containers, then dispatching.
- Appropriate for a plant with dedicated QC and packaging stages.

**Alternatives Considered:**
- 1-step inbound: receive directly into stock. Simpler but no QC gate.
- 2-step inbound: receive then put away. No explicit QC.

**Trade-offs:**
- More transfer operations per shipment — requires disciplined scan/confirm workflow.
- Operators need training on the 3-step process to avoid skipping steps.

**Revisit Conditions:**
- If QC is handled entirely offline (paper-based) and the Odoo step adds no value.
- If throughput speed is more critical than traceability.

---

## DEC-007 — Custom Module for Tank Restriction vs Configuration-Only Approach

**Decision:** Build a custom module (`stock_crude_oil_tank_restriction`) to enforce product restrictions on tank locations.

**Rationale:**
- Odoo Community has no native "location-product restriction" feature.
- Without enforcement, operators could accidentally store wrong products in crude oil tanks, contaminating batch integrity.
- A light Python override on `button_validate` is low-risk and low-maintenance.

**Alternatives Considered:**
- Training-only: rely on operator discipline. Rejected — human error risk is too high.
- Putaway rules: Odoo putaway rules suggest destination but do not block wrong products.
- Odoo Enterprise: has more advanced quality/restriction features, not available in Community.

**Trade-offs:**
- Custom code adds a maintenance burden when Odoo upgrades.
- Lookup by name is slightly slower than hardcoded IDs (negligible in practice).

**Revisit Conditions:**
- On Odoo version upgrade — test that `button_validate` override is still compatible.
- If additional location restrictions are needed (e.g., Soapstock Tank) — extend the same module.

---

## DEC-008 — Per-Component Source Location: Rank 1 (Parent + child_of) vs Custom Module

**Decision:** Use **Rank 1 — parent location + child_of semantics** as the primary approach for component sourcing. A custom module overriding `_get_move_raw_values` is deferred.

**Context:**
Odoo 17 Community (and Enterprise) does not support per-BOM-line source locations natively. `mrp.bom.line` has no `location_id` field at either the ORM or DB level. The OCA module `mrp_bom_location` exists for 16.0 and 18.0 but not 17.0, and was informational-only (no `_get_move_raw_values` override) even where available.

**Rationale:**
- Setting the MO source location to the parent `Famoil/Stock` causes Odoo's `stock.quant._gather` to use `child_of` semantics — components are reserved from whichever child location they physically reside in.
- This achieves the functional outcome (each component reserved from its correct physical location) with zero custom code.
- Physical stock discipline + putaway rules enforce correct product placement, making the parent-location approach reliable in practice.

**Alternatives Considered:**
- Custom module overriding `_get_move_raw_values` to inject `location_id` per BOM line: correct and explicit, but requires ~80 lines of Python + upgrade maintenance.
- Setting source directly at MO level (override per MO): manual, does not scale, defeats BOM automation.
- OCA `mrp_bom_location` for 17.0: does not exist as of 2026-05.

**Trade-offs:**
- Rank 1 relies on physical stock discipline — if wrong products are placed in wrong locations, Odoo will still reserve them.
- No hard BOM-level enforcement: an operator who manually adjusts source on the MO can break routing.
- Does not support a scenario where two storable components of the same product reside in different child locations and must each be taken from specific ones.

**Revisit Conditions:**
- If a future BOM requires two components of the same product sourced from different specific child locations.
- If regulatory audit requires a traceable BOM-to-location linkage on every transaction.
- When implementing for a client with low stock discipline — the custom `_get_move_raw_values` module becomes justified.

---

## DEC-009 — Putaway Rules for Manufacturing Output Routing

**Decision:** Configure `stock.putaway.rule` (product × parent location → specific child location) for all manufacturing outputs, rather than setting child location directly on operation type destination.

**Rationale:**
- `mrp.bom.byproduct` has no `location_id` field — byproducts always go to the same destination as the main product.
- Setting operation type destination to a product-specific child location (e.g., Crude Oil Tank 1) would also route byproducts (e.g., Soya Cake, SoapStock) there — incorrect.
- Setting destination to parent `Famoil/Stock` and using putaway rules gives each output (main product and all byproducts) its own correct child destination independently.

**Putaway rules configured (all trigger on arrival at Famoil/Stock, id=152):**

| Product | Destination |
|---|---|
| Crude Soya Oil | Crude Oil Tank 1 |
| Refined Soya Oil | Refined Oil Tank 1 |
| SoapStock | Soapstock Tank |
| Soya Cake | FG Warehouse |
| Refined Soya Oil 5L | FG Warehouse |
| Refined Soya Oil 25L | FG Warehouse |

**Alternatives Considered:**
- Destination = child location on operation type: works for single-output BOMs; breaks for multi-output BOMs with byproducts.
- Custom override of byproduct destination via Python: possible but higher complexity than putaway rules.

**Trade-offs:**
- Putaway rules are a soft routing mechanism — they apply when a product *arrives* at a location, but do not prevent manual overrides.
- If a new product is added to a BOM without creating its putaway rule, it will land in the parent `Famoil/Stock` without further routing — silent failure.

**Revisit Conditions:**
- When adding a new BOM or byproduct: **always** check if a putaway rule exists for the new product.
- If a product needs to route to different destinations depending on production context (e.g., grade A vs grade B output) — putaway rules cannot handle this; a custom override or split BOM is required.

---

## DEC-011 — Backup Format: PostgreSQL Custom Format (-F c) over Plain Text (-F p)

**Decision:** Migrate backup from `pg_dump -F p` (plain text, `Famoil.sql`) to
`pg_dump -F c` (custom format, `Famoil.dump`). Restore via `pg_restore --disable-triggers`.

**Rationale:**
- Plain format restore produced circular FK violations between `account_move` and
  `ir_attachment`, leaving all 875 attachment records unrestored (Drill 1 — 2026-05-28).
- Custom format with `pg_restore --disable-triggers` disables FK constraint triggers
  during data load, fully resolving the circular dependency.
- Custom format is also self-compressed (~6MB vs ~17MB plain), restores in parallel
  (`-j 4`), and supports selective table restoration.

**Trigger:**
Restore Drill 1 failure — `ir_attachment` 0/875 recovered. Root cause: plain pg_dump
COPY ordering conflict. Decision made immediately after root cause was confirmed.

**Validation:**
Restore Drill 2 — FULL PASS: `ir_attachment` 875/875, PDFs 16/16, images 844/844,
PDF served via Odoo `/web/content` HTTP 200. RTO ≈ 43 seconds.

**Alternatives Considered:**
- Keep plain format, strip `\restrict` and use `ON_ERROR_STOP=0`: produces FK errors,
  ir_attachment remains empty, attachments inaccessible. Rejected.
- Use Odoo web backup ZIP (dump.sql + filestore): same FK ordering issue, and ties
  restore to Odoo web interface. Rejected.
- Restore with `SET session_replication_role = 'replica'`: equivalent to
  `--disable-triggers` but more obscure and harder to document. Deferred.

**Trade-offs:**
- `.dump` files require `pg_restore` (not `psql`) — operators must use
  `scripts/restore_famoil.sh` rather than raw psql commands.
- `--disable-triggers` requires `odoo` PostgreSQL user to be superuser (confirmed).
- Parallel restore (`-j 4`) opens multiple connections — fine for local Mac, review
  if moving to resource-constrained server.

**Revisit Conditions:**
- If `odoo` PostgreSQL role is ever downgraded from superuser — use
  `SET session_replication_role = 'replica'` as an alternative.
- If backup storage cost becomes significant — custom format is already compressed;
  consider archiving older backups.
- On Odoo major version upgrade — re-run restore drill to confirm format compatibility.

---

## DEC-012 — Custom Module for Landed Cost Receipt Integrity

**Decision:** Build `stock_landed_cost_po_check` to enforce that landed costs can
only be applied to receipts that originated from a Purchase Order.

**Context:**
Odoo 17 Community places no restriction on which receipts an operator can link to a
landed cost. The only native filters are company isolation and the presence of stock
valuation layers — neither prevents an operator from accidentally selecting the wrong
receipt (e.g., linking Kaduna haulage costs to a Niger State SoyaBean receipt).
Native options were fully researched before this decision was taken.

**Rationale:**
- Costing errors from wrong-receipt assignment are silent and cumulative — the
  numbers appear plausible but unit costs are distorted in every downstream MO.
- The haulage vendor (ABC Logistics) and the goods vendor (Kaduna Soybean Traders)
  are separate entities; a vendor-match constraint is therefore inappropriate. The
  correct constraint is purchase order origin, not vendor identity.
- The implementation follows the existing `stock_crude_oil_tank_restriction` pattern
  already proven stable in this codebase — low risk, low maintenance.
- Partner consent obtained before implementation.

**Alternatives Considered:**
- Native Odoo domain (`picking_ids` field): only filters by company and valuation
  layer — no PO-origin check available. Rejected — insufficient.
- Operator training + SOP alone: costing errors are silent; training cannot prevent
  accidental selection. Rejected for production use.
- Vendor-match constraint (landed cost bill vendor = receipt vendor): incorrect for
  FamOil because goods vendor ≠ haulage vendor. Researched and ruled out.
- Automated activity only (soft reminder): leaves the error path open. Implemented
  as a companion to the hard constraint, not a replacement.

**What the module enforces (on `button_validate`):**
1. Every selected receipt must be of type `incoming` (not internal or outgoing).
2. Every selected receipt must have at least one move linked to a Purchase Order
   (`purchase_line_id` is set).

**Validation:**
3-test automated suite — all pass:
- Valid PO receipt: allowed ✓
- Incoming receipt with no PO origin: blocked ✓
- Internal transfer / outgoing delivery: blocked ✓

**Trade-offs:**
- Adds upgrade maintenance — `button_validate` on `stock.landed.cost` must be
  verified compatible after each Odoo major version upgrade.
- Module footprint is minimal (~25 lines Python + XML automation) — low burden.
- Does not prevent an operator from selecting the wrong PO receipt if multiple
  receipts from the same vendor exist on the same day. Process discipline and
  the automated activity reminder address this residual risk.

**Revisit Conditions:**
- On Odoo major version upgrade — re-run 3-test suite to confirm constraint fires.
- If a second constraint is needed (e.g., date-range validation) — extend
  `_check_po_receipt()` in the same module rather than creating a new one.
- If `purchase_line_id` field is renamed or moved in a future Odoo version —
  update the filtered lambda accordingly.

---

## DEC-010 — Separate Operation Types per Manufacturing Stage

**Decision:** Create three distinct operation types (Extraction Manufacturing, Refining Manufacturing, Packaging Manufacturing) rather than using a single shared "Manufacturing" operation type for all stages.

**Rationale:**
- Each stage has different source and destination locations — a single operation type cannot carry three different source/destination pairs.
- Separate operation types allow stage-specific sequence numbering (MO references), role-based access (different operators can be granted access to different operation types), and independent scheduling.
- Stage-level visibility in the Manufacturing menu (filter by operation type) is more useful than filtering by product.

**Alternatives Considered:**
- Single Manufacturing operation type: simpler, but source/destination must be set manually on every MO — error-prone.
- Two operation types (Extraction vs Refining+Packaging): slightly fewer operations to manage, but loses Packaging-specific visibility and FG Warehouse destination separation.

**Trade-offs:**
- Three operation types means three places to check/update if warehouse topology changes.
- Sequence number pools are separate — MO references (e.g., WH/MO/00001) are not contiguous across stages.

**Revisit Conditions:**
- If a fourth manufacturing stage is added (e.g., blending, flavouring) — create a fourth operation type.
- If the business wants unified MO numbering across all stages — merge operation types and manage source/destination at MO level.
