# PLATFORM_ROADMAP.md

# Software Factory Platform Roadmap

Version: 1.1
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

Major outcome:
Governance now actively enforced by repository systems.

---

# 5. CURRENT ACTIVE PRIORITY

CURRENT PRIORITY:
Operational Maturity + Commercial MVP Completion

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

# PRIORITY 1 — RESTORE DRILL

STATUS: NOT YET COMPLETED

Objectives:

* restore PostgreSQL dump
* restore filestore
* validate attachments
* validate modules
* validate records
* measure recovery timing

Required output:
docs/operations/RESTORE_DRILL.md

Core principle:
A backup is only trusted after a successful restore.

---

# PRIORITY 2 — OPERATIONAL ERP MATURITY

Focus areas:

* procurement maturity
* QC maturity
* maintenance
* dispatch
* weighbridge
* fleet
* anti-fraud operational controls
* operational traceability

---

# PRIORITY 3 — KPI & OPERATIONAL ANALYTICS LAYER

Future operational visibility layer:

* yield variance tracking
* downtime tracking
* production KPI architecture
* operational reporting
* management dashboards
* cost variance monitoring

---

# PRIORITY 4 — REGULATORY & COMPLIANCE MATURITY

Future compliance architecture:

* NAFDAC
* SON
* PenCom
* NSITF
* tax workflows
* compliance documentation
* audit trails

---

# PRIORITY 5 — INDUSTRIAL INFRASTRUCTURE & UTILITIES

Future utilities architecture:

* generator monitoring
* fuel tracking
* power consumption monitoring
* utility cost analysis
* industrial sensor integration

---

# PRIORITY 6 — INDUSTRIAL INTELLIGENCE LAYER

Only after operational stability:

* IoT integration
* anomaly detection
* predictive maintenance
* industrial analytics

Operational truth must exist before intelligence.

---

# PRIORITY 7 — MULTI-INDUSTRY TEMPLATE EXPANSION

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

* restore drill not yet validated
* founder dependency still exists
* roadmap intelligence partially centralized
* premature expansion risk
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

* operational maturity
* governance survivability
* restore validation
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
