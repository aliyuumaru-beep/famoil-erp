# Architectural Principles
# FamOil Software Factory — Architecture Doctrine
# Version: 1.0 | Created: 2026-05-27

> This document defines the architectural doctrine for the FamOil Software Factory.
> It governs how implementation decisions should be made across Odoo configuration,
> custom addons, scripts, documentation, CI/CD, and future industry templates.
>
> This is not a technical how-to document. It is the decision philosophy that
> future developers, ERP analysts, Claude Code sessions, and implementation teams
> must follow.

---

## 1. Purpose

The purpose of this document is to ensure that the FamOil ERP framework grows into
repeatable software factory infrastructure rather than a collection of one-off
implementation decisions.

All major implementation decisions must align with these principles unless a
specific exception is documented in the Decision Log.

Reference documents:

- `CLAUDE.md` — session state and AI operating anchor
- `PROJECT_FACTORY_MANUAL.md` — repository and factory navigation
- `docs/IMPLEMENTATION_STANDARDS.md` — execution rules
- `docs/famoil_erp_template/DECISION_LOG.md` — recorded deviations and rationale

---

## 2. Core Architectural Principles

### Principle 1 — Configuration Before Customization

Native Odoo capability, configuration, workflow redesign, and acceptable operational
workarounds must be explored before custom code is proposed.

Custom code is allowed only when native capability cannot meet the operational
requirement safely, clearly, or sustainably.

---

### Principle 2 — Operational Simplicity Over Technical Sophistication

A solution that operators can understand, maintain, and audit is preferred over a
technically elegant solution that increases fragility or dependency on scarce
engineering talent.

The best architecture is not the most complex architecture. It is the one that
survives real operational use.

---

### Principle 3 — Documentation Is Infrastructure

Documentation is not administrative support. It is part of the system.

Any configuration, workflow, script, custom module, deployment process, or governance
rule that is not documented should be treated as incomplete.

---

### Principle 4 — Every System Must Be Reproducible

A new developer or AI session must be able to rebuild, inspect, operate, and improve
the system using only the repository, documented credentials process, backups, and
approved operating instructions.

No hidden local knowledge should be required.

---

### Principle 5 — ERP Must Reflect Operational Reality

The ERP system must model real factory operations, not imaginary textbook processes.

Warehouse structures, tanks, work centers, costing logic, quality checks, fraud
controls, and approvals must reflect how the business actually operates and how it
should be controlled.

---

### Principle 6 — AI Assists, But Does Not Govern Production Autonomously

Claude Code and other AI agents may inspect, propose, generate, refactor, document,
and validate.

They must not independently perform destructive actions, production-critical changes,
remote pushes, or architectural reversals without operator approval.

---

### Principle 7 — Standardization Before Expansion

Do not rush into new industry templates before the base implementation patterns are
stable, documented, tested, and reusable.

New industries should inherit proven structures instead of creating fresh chaos.

---

### Principle 8 — Minimize Founder Dependency

The software factory must reduce dependence on any single person, including the
project director.

Every document, script, workflow, and template should help future developers,
ERP analysts, QA staff, and AI sessions continue without private context.

---

### Principle 9 — Rollback Capability Is Mandatory

Every major change must preserve a practical path back to a known good state.

This includes database backups, Git history, documentation updates, release notes,
and tested recovery procedures.

---

### Principle 10 — Prevent Complexity Accumulation

Avoid unnecessary abstractions, premature frameworks, excessive custom modules, and
architecture that exists only because it feels advanced.

Complexity must be justified by operational value.

---

### Principle 11 — Governance Must Be Useful, Not Theatrical

Rules, checks, branch protections, hooks, and workflows must reduce real risk.

Do not add governance that blocks useful work without improving safety,
reproducibility, quality, or auditability.

---

### Principle 12 — Data Integrity Is Business Integrity

Master data, inventory records, costs, approvals, and production movements must be
protected as business-critical assets.

Bad data in an ERP system creates bad decisions, financial leakage, and operational
fraud risk.

---

## 3. Decision Hierarchy

When choosing between alternatives, apply this hierarchy:

1. Operational correctness
2. Data integrity and auditability
3. Safety and rollback capability
4. Native Odoo capability
5. Maintainability
6. Reusability across future templates
7. Speed of implementation
8. Technical elegance

Speed is valuable, but it must not defeat survivability.

---

## 4. Custom Code Doctrine

Before custom code is approved, the responsible developer or Claude Code session must
document:

- the operational problem
- native Odoo options investigated
- workflow or configuration workarounds considered
- why native options were rejected
- expected maintenance burden
- upgrade risk
- test approach
- rollback approach

Existing custom code must be reviewed periodically to determine whether it can be
replaced by native functionality or simpler configuration.

No custom code should become permanent merely because it already exists.

---

## 5. Factory Expansion Doctrine

A new industry template should only be created when the base template has:

- documented architecture
- validated workflows
- stable CSV standards
- tested backup and restore process
- known issues register
- decision log
- onboarding guide
- branch governance
- minimum CI/CD checks

Expansion without stabilization creates multiplied disorder.

---

## 6. Exception Handling

Exceptions are allowed, but they must be deliberate.

Any deviation from these principles must be recorded in:

`docs/famoil_erp_template/DECISION_LOG.md`

Each exception must state:

- what principle was overridden
- why it was overridden
- who approved it
- risk accepted
- future revisit condition

---

## 7. Final Doctrine

The goal is not merely to build an ERP implementation.

The goal is to build a repeatable industrial implementation system that improves
over time, survives personnel change, supports AI-assisted execution, and can be
reused across industries without losing operational discipline.
