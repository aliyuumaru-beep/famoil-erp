# CONFIDENTIAL — Commercial Implementation Guide
# FamOil ERP Framework

_Version: 1.0 | Date: 2026-05-22_

---

> **CONFIDENTIAL — INTERNAL USE ONLY**
> This document contains commercial pricing structures, effort estimates, and business strategy.
> Do not share with clients, third parties, or prospective clients without authorisation.
> All effort estimates are **PRELIMINARY** and subject to revision based on client scope.

---

## 1. Template Tiers

Three tiers are defined based on client size, complexity, and customisation depth.

---

### Tier 1 — Starter

**Target client:** Small agro-processor, single product line, ≤10 users, ≤₦200M annual revenue.

**What is included:**
- Standard FamOil framework deployment (matched to client's industry from the variation matrix)
- Single warehouse, single company
- Core modules: inventory, manufacturing, purchase, sales, accounting
- Standard BOM configuration (1–3 BOMs)
- Up to 5 work centers
- Chart of accounts configuration (standard Nigerian manufacturing CoA)
- VAT and WHT tax configuration
- Opening data entry: products, vendors, customers, opening stock, opening balances
- 2-day on-site training (production staff + accounts)
- 30-day hypercare support (email/WhatsApp, business hours)

**What is excluded:**
- Custom module development
- Integration with third-party software
- Multi-company or multi-warehouse
- Payroll module
- Advanced reporting / BI dashboards

**Deliverables:**
- Configured Odoo instance (cloud or on-premise)
- Completed discovery template
- BOM validation report
- Costing validation document (adapted from COSTING_VALIDATION.md template)
- Known issues log at handover
- Backup + restore runbook

**[PRELIMINARY] Effort Estimate:**

| Activity | Days |
|---|---|
| Discovery + planning | 1.5 |
| Server setup + base install | 0.5 |
| Configuration (BOM, products, CoA) | 3.0 |
| Data entry (opening data) | 1.5 |
| Testing + UAT | 1.5 |
| Training | 2.0 |
| Hypercare (30 days, distributed) | 2.0 |
| Documentation | 1.0 |
| **Total** | **~13 days** |

---

### Tier 2 — Standard

**Target client:** Mid-size agro-processor, 2–3 product lines, 10–30 users, ₦200M–₦2B annual revenue.

**What is included:**
Everything in Tier 1, plus:
- Multi-warehouse (up to 3 warehouses)
- Up to 10 BOMs
- Up to 2 custom modules (scoped separately — see Section 4)
- MRP replenishment rules and reorder points
- Quality control checkpoints (basic, using notes/checklist approach)
- Landed cost configuration for imported raw materials
- Financial reporting: P&L, Balance Sheet, aged payables/receivables
- 4-day on-site training across multiple departments
- 90-day standard support (SLA: 4 business hours response)

**What is excluded:**
- Enterprise modules (Odoo Enterprise licence required)
- Payroll (Odoo HR Payroll requires separate scoping)
- Complex integrations (bank feeds, weighbridge, lab LIMS)
- BI / analytics dashboards

**[PRELIMINARY] Effort Estimate:**

| Activity | Days |
|---|---|
| Discovery + planning | 3.0 |
| Server setup + base install | 0.5 |
| Configuration (BOM, products, CoA, multi-wh) | 6.0 |
| Custom module development (2 modules) | 5.0 |
| Data migration | 2.0 |
| Testing + UAT | 3.0 |
| Training | 4.0 |
| Support (90 days, distributed) | 5.0 |
| Documentation | 2.0 |
| **Total** | **~31 days** |

---

### Tier 3 — Enterprise

**Target client:** Large agro-processor or group, multiple plants, 30+ users, >₦2B annual revenue.

**What is included:**
Everything in Tier 2, plus:
- Multi-company, multi-currency configuration
- Unlimited BOMs and work centers
- Custom modules (scoped per engagement — see Section 4)
- Integration scoping (bank, weighbridge, POS, B2B portal)
- Advanced manufacturing: work order scheduling, capacity planning
- Lot traceability (upstream to RM batch, downstream to customer invoice)
- Custom financial reports (management accounts, cost centre P&L)
- Dedicated project manager
- 1-year standard support contract
- Quarterly review meetings

**What is excluded:**
- Odoo Enterprise licence costs (separate vendor contract)
- Infrastructure hosting costs
- Payroll integration with IPPIS/external system (separate project)
- ERP-to-ERP integration with parent group systems

**[PRELIMINARY] Effort Estimate:**
Scoped per engagement. Indicative range: **60–120 days** across a 4–6 month timeline.

---

## 2. Implementation Effort Estimates

> **ALL ESTIMATES ARE PRELIMINARY.**
> Actual effort depends on: client data readiness, staff availability, complexity of existing processes, number of products/vendors/customers, and scope changes during implementation.
> Estimates assume a single experienced Odoo implementer familiar with this framework. Add 30% for new-to-framework implementers.

| Scope Item | Typical Effort |
|---|---|
| Discovery (per session, 2-hour) | 0.5 day |
| Product master creation (per 50 products) | 0.5 day |
| BOM creation (per 5 BOMs) | 0.5 day |
| Chart of accounts setup | 0.5–1 day |
| Tax configuration (VAT + WHT) | 0.5 day |
| Opening inventory data entry (per 100 lines) | 0.5 day |
| Vendor/customer master (per 100 records) | 1 day |
| Opening balance journal entry | 0.5–1 day |
| Custom module (simple restriction/validation) | 1–2 days |
| Custom module (workflow or complex logic) | 3–5 days |
| Training session (per 2-hour session) | 0.5 day (prep) + 0.25 day (delivery) |
| User acceptance testing (per round) | 1–2 days |
| Go-live support (on-site day) | 1 day |

---

## 3. Billable Customisation Boundaries

### Included in Template (Non-Billable)

The following are part of the base framework and should not be separately billed:

- Standard Odoo module configuration (fields, views, menus)
- BOM setup within the framework pattern
- Standard Nigerian tax codes (VAT 7.5%, WHT standard rates)
- Chart of accounts using the standard manufacturing template
- Stock location hierarchy setup
- Reorder rules and replenishment configuration
- Training on standard Odoo workflows
- Bug fixes for implementer errors during the warranty period

### Billable Customisation

Bill separately for any work outside standard configuration:

| Customisation Type | Billing Basis |
|---|---|
| Custom Python module (new model or logic) | Per module, fixed price |
| Custom report (QWeb PDF or XLSX) | Per report |
| Integration development (API, webhook) | Per integration, T&M |
| Data migration scripting (complex transformations) | Per dataset, T&M |
| Training beyond agreed days | Per day |
| Support beyond SLA scope | Per incident or retainer |
| Re-scoped work (client-initiated changes) | Per change request |
| Server/infrastructure setup | Per engagement |

### Change Request Process

Any change to agreed scope must be:
1. Documented in writing (email is acceptable)
2. Estimated and approved before work begins
3. Billed at the agreed day rate

Do not absorb scope creep silently — it destroys margins on small engagements.

---

## 4. Support Models

### Model A — Hypercare (30 days post-go-live)

Included in all tiers. Covers:
- Bug fixes for configuration errors
- User questions on standard workflows
- Up to 2 minor configuration adjustments

Response: business hours, email or WhatsApp.
Not included: new features, new reports, additional training.

### Model B — Standard Annual Support

Tier 2 and above. Covers:
- 4 business hours response SLA
- Up to 20 support hours per month (rollover not permitted)
- Odoo minor version upgrades (patch releases)
- Quarterly health check call

Exclusions: new module development, Odoo major version upgrades, third-party issues.

**[PRELIMINARY] Monthly fee range:** Scoped per engagement based on system complexity and user count.

### Model C — Premium Annual Support

Tier 3. Covers:
- 2 business hours response SLA
- Unlimited support hours (fair use policy)
- Dedicated WhatsApp group with senior implementer
- Odoo minor version upgrades included
- Quarterly on-site review (up to 4/year)
- One annual major feature addition (scoped jointly)

**[PRELIMINARY] Monthly fee range:** Scoped per engagement.

### Model D — Ad Hoc / Pay-per-Incident

Available to any client. Billed at agreed day rate. No SLA guarantee.
Suitable for: clients with strong internal IT who only need occasional specialist help.

---

## 5. Strategic Notes

These are internal observations — not for client communication.

- **Groundnut and rice mills** are the fastest upsell path from a soybean deployment — 2 days of delta work, near-identical config.
- **Feed mills** have strong recurring revenue potential (formula updates, new SKUs, seasonal adjustments) — support contracts are stickier.
- **FMCG is high-effort but high-value** — only take if budget is confirmed and data is clean.
- **Palm oil mills** often have NGO/development finance involvement in Nigeria — procurement timelines can be long; factor into project scheduling.
- **Avoid multi-company + multi-currency on Tier 1 budget** — it rarely stays simple and will erode margin.
- **Data readiness is the #1 implementation risk.** A client with no clean product list will consume 3× the estimated data entry time.

---

_This document is reviewed and updated each time a new industry implementation is completed._
_Next review: after first non-soybean deployment._
