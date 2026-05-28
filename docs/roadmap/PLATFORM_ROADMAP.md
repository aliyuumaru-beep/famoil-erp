# PLATFORM_ROADMAP.md

# Software Factory Platform Roadmap

Version: 1.2
Last Updated: 2026-05-28

---

# PURPOSE

This document defines:

* software factory strategic direction,
* platform maturity roadmap,
* governance evolution,
* implementation sequencing,
* survivability architecture,
* commercial MVP direction,
* operational maturity targets,
* industrial intelligence direction,
* and long-term platform architecture.

This is NOT:

* a detailed ERP execution checklist,
* a department-level implementation matrix,
* or a client deployment plan.

Detailed template execution belongs inside template-specific roadmaps.

---

# 1. STRATEGIC VISION

The objective is to build:

* a governed industrial ERP software factory,
* reusable implementation systems,
* reusable industry templates,
* reusable deployment methodology,
* institutional memory architecture,
* operational survivability,
* and reduced dependency on:

  * individual developers,
  * individual AI agents,
  * and deployment environments.

---

# 2. SOFTWARE FACTORY STRUCTURE

Conceptual hierarchy:

Software Factory
└── Platform Layers
└── Industry Templates
└── Client Deployments

---

# LEVEL 1 — SOFTWARE FACTORY CORE

Purpose:

* governance
* onboarding
* standards
* survivability
* CI/CD
* implementation doctrine
* backup architecture
* AI operational discipline
* institutional memory

Examples:

* CLAUDE.md
* AI_ONBOARDING_V2.txt
* IMPLEMENTATION_STANDARDS.md
* ARCHITECTURAL_PRINCIPLES.md
* workflows
* governance hooks

---

# LEVEL 2 — PLATFORM LAYERS

Current platform:

* Odoo ERP platform

Future platforms:

* IoT platform
* analytics platform
* integration platform

Purpose:

* reusable technical architecture
* reusable deployment tooling
* reusable module governance
* reusable operational architecture

---

# LEVEL 3 — INDUSTRY TEMPLATES

Current primary template:

* FamOil

Future templates:

* RiceMill
* FeedMill
* PalmOil
* HospitalityERP
* OfficeERP
* PowerSectorERP

Purpose:

* reusable industry operational architecture
* reusable costing structures
* reusable warehouse flows
* reusable BOM structures
* reusable deployment patterns

---

# LEVEL 4 — CLIENT DEPLOYMENTS

Examples:

* NADF
* future commercial deployments

Client deployments are NOT framework definitions.

---

# 3. CURRENT STATE

Current maturity:
Governed industrial ERP implementation framework.

Major maturity transition achieved:
The project evolved from:

* generic ERP implementation,
  into:
* governed implementation systems engineering.

Governance is now operationally enforced.

---

# 4. COMPLETED IMPLEMENTATION PHASES

---

# PHASE 1 — FOUNDATION

STATUS: COMPLETE / STABLE

Implemented:

* Odoo deployment
* inventory foundation
* manufacturing foundation
* accounting foundation
* warehouse hierarchy
* costing architecture
* git repository
* governance structure
* documentation architecture

---

# PHASE 2 — EXTRACTION MANUFACTURING

STATUS: COMPLETE / STABLE

Implemented:

* soybean extraction flow
* BOM architecture
* byproducts
* WIP logic
* routing
* operation types
* warehouse movement architecture
* costing flow

Major outcome:
Industrial extraction manufacturing stabilized.

---

# PHASE 3 — REFINING & PACKAGING

STATUS: COMPLETE / STABLE

Implemented:

* refining flow
* packaging flow
* consumables
* tank architecture
* putaway rules
* packaging BOMs
* refining architecture

Major outcome:
Industrial process manufacturing operational.

---

# PHASE 4 — GOVERNANCE & SURVIVABILITY

STATUS: COMPLETE / OPERATIONAL

Implemented:

* branch protection
* CI/CD
* GitHub Actions
* secret scanning
* documentation linting
* PR governance
* backup governance
* backup manifest bridge
* offsite backups
* launchd automation
* Google Drive sync
* onboarding architecture
* implementation history
* decision logging
* architectural doctrine

Milestones:

* v1.2.0-governance-foundation
* v1.3.0-offsite-backup-operational
* v1.4.0-roadmap-institutionalization
* v1.5.0-restore-validated

Major outcome:
Governance now actively enforced by repository systems.
Production-grade restore survivability validated (Drill 2: full pass, RTO ≈ 43s).

---

# 5. CURRENT ACTIVE PRIORITY

CURRENT PRIORITY:
Procurement Maturity & Operational Workflow Expansion

Restore validation is complete (v1.5.0-restore-validated).
Backup system is production-grade trusted.

Current operational template:
FamOil ERP

Current execution roadmap source:
docs/famoil_erp_template/FAMOIL_ROADMAP.md

---

# 6. COMMERCIAL MVP TARGET

Commercial MVP includes:

## Manufacturing

* stable manufacturing
* stable warehouse operations
* stable costing

## Procurement

* RFQ workflows
* approvals
* vendor management
* landed costs

## Quality

* QC checkpoints
* batch traceability
* lab operations

## Operations

* maintenance basics
* weighbridge basics
* dispatch validation
* fleet basics

## Sales

* quotations
* sales orders
* invoicing
* receivables
* customer structures

## Governance

* backup governance
* restore governance
* onboarding continuity
* CI/CD governance

---

# 7. CURRENT HIGH-PRIORITY NEXT STEPS

---

# RESTORE DRILL — COMPLETE

STATUS: COMPLETE / VALIDATED (2026-05-28)

Milestone: v1.5.0-restore-validated

Results:

* Drill 1 — PARTIAL PASS (plain format, ir_attachment 0/875)
* R-01 — backup architecture hardened (pg_dump -F c, pg_restore --disable-triggers)
* Drill 2 — FULL PASS (ir_attachment 875/875, PDFs 16/16, images 844/844)
* PDF served via Odoo UI: HTTP 200, 47,172 bytes
* Measured RTO: ≈ 43 seconds
* 83 Odoo modules loaded, 0 errors

See: docs/operations/RESTORE_DRILL.md

---

# PRIORITY 1 — PROCUREMENT MATURITY

Focus areas:

* RFQ workflows
* purchase approvals
* vendor management
* vendor pricing
* landed costs
* procurement traceability

---

# PRIORITY 2 — SALES WORKFLOW MATURITY

Focus areas:

* quotations
* sales orders
* invoicing
* receivables
* customer pricing
* dispatch validation

---

# PRIORITY 3 — DISPATCH & LOGISTICS MATURITY

Focus areas:

* fleet tracking
* weighbridge integration
* dispatch validation
* trip monitoring

---

# PRIORITY 4 — MAINTENANCE MATURITY

Focus areas:

* preventive maintenance
* breakdown maintenance
* spare parts management
* maintenance scheduling

---

# PRIORITY 5 — BARCODE & WAREHOUSE OPERATIONS

Focus areas:

* barcode workflows
* warehouse scanning
* operational validation

---

# PRIORITY 6 — OFF-MACHINE SURVIVABILITY ACTIVATION

Focus areas:

* rclone installation
* Google Drive sync activation
* off-machine restore validation
* cross-machine recovery test

---

# PRIORITY 7 — KPI & OPERATIONAL ANALYTICS LAYER

Future operational visibility layer:

* yield variance tracking
* downtime tracking
* production KPI architecture
* operational reporting
* management dashboards
* cost variance monitoring

---

# PRIORITY 8 — REGULATORY & COMPLIANCE MATURITY

Future compliance architecture:

* NAFDAC
* SON
* PenCom
* NSITF
* tax workflows
* compliance documentation
* audit trails

---

# PRIORITY 9 — INDUSTRIAL INFRASTRUCTURE & UTILITIES

Future utilities architecture:

* generator monitoring
* fuel tracking
* power consumption monitoring
* utility cost analysis
* industrial sensor integration

---

# PRIORITY 10 — INDUSTRIAL INTELLIGENCE LAYER

Only after operational stability:

* IoT integration
* anomaly detection
* predictive maintenance
* industrial analytics

Operational truth must exist before intelligence.

---

# PRIORITY 11 — QUARTERLY RESTORE GOVERNANCE

Schedule quarterly restore drills.
Document recovery SOP improvements after each drill.
Track RTO progression over time.

---

# PRIORITY 12 — MULTI-INDUSTRY TEMPLATE EXPANSION

Future reusable templates:

* rice mills
* feed mills
* palm oil mills
* FMCG processing

Later:

* hospitality
* office ERP
* power sector

FamOil remains the primary reference framework until MVP stabilization.

---

# 8. GOVERNANCE PRINCIPLES

Priority order:

1. Operational realism
2. Inventory integrity
3. Manufacturing correctness
4. Traceability
5. Costing accuracy
6. Upgradeability
7. Reusability
8. Automation
9. UI convenience

---

# 9. IMPLEMENTATION PRINCIPLES

Mandatory:

* native Odoo first
* custom code last
* preserve upgradeability
* preserve repeatability
* preserve governance continuity
* avoid overengineering
* avoid framework/client coupling

---

# 10. CURRENT MAJOR RISKS

Current risks:

* off-machine backup sync not yet operationally activated (rclone not installed)
* restore process still partially operator-driven (manual invocation of restore_famoil.sh)
* founder dependency still exists
* premature multi-template expansion risk
* operational complexity growth
* overengineering risk

---

# 11. FUTURE REPOSITORY EVOLUTION

Current repository remains partially FamOil-centric intentionally.

Future likely architecture:

Repository A:
software-factory-core

Repository B:
platform-odoo

Repository C+:
industry templates

* famoil-template
* ricemill-template
* hospitality-template

Current focus remains:

* procurement maturity
* operational workflow expansion
* governance survivability
* ERP quality

---

# 12. SUCCESS DEFINITION

Success is NOT:

* merely configuring Odoo.

Success is:

* building a repeatable governed industrial ERP implementation system that survives replacement of:

  * developers,
  * AI agents,
  * operators,
  * deployment environments.

---

# END
