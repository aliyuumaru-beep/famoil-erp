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
