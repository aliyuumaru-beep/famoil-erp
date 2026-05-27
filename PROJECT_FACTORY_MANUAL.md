# Project Factory Manual
# FamOil Software Factory
# Version: 1.0 | Created: 2026-05-27

---

## 1. What Is the Software Factory?

The FamOil Software Factory is a structured approach to building, documenting,
and replicating industrial ERP implementations. It is not just a configured
Odoo instance — it is a repeatable system designed to survive:

- Developer replacement
- AI context loss
- Project pause
- Infrastructure migration
- Scaling across industries and clients

Every session must leave the repository more complete than it found it.
Every phase must be survivable by a replacement developer or AI with no
prior context, using only what is in this repository.

---

## 2. How to Use This Repository

This repository serves three simultaneous purposes:

**Purpose 1 — Active ERP Instance Documentation**
Documents the live FamOil FTZ Odoo 17 instance: configuration, manufacturing
pipeline, costing model, known issues, and decisions.

**Purpose 2 — Reusable Implementation Framework**
Extracts from the FamOil instance a template applicable to other agro-processing
clients: industry variation matrix, discovery templates, CSV templates,
implementation playbook.

**Purpose 3 — Software Factory Infrastructure**
Enforces quality governance through automated hooks and CI/CD pipelines so
that future sessions maintain the same standards without relying on memory.

---

## 3. Relationship Between Documents

```
CLAUDE.md                        ← Session anchor: always read first
│
├── docs/IMPLEMENTATION_STANDARDS.md   ← The 11 rules
│
├── docs/ONBOARDING_GUIDE.md           ← How to get started
│
├── docs/architecture/
│   └── GOVERNANCE_ENGINE.md           ← Hook and CI/CD enforcement map
│
├── docs/famoil_erp_template/          ← FamOil-specific knowledge
│   ├── MANUFACTURING_FLOW.md          ← 3-stage pipeline
│   ├── DECISION_LOG.md                ← Why things are as they are
│   ├── KNOWN_ISSUES.md                ← Issues and fixes
│   ├── COSTING_VALIDATION.md          ← Cost model
│   ├── IMPLEMENTATION_PLAYBOOK.md     ← Deployment guide (replicate)
│   └── [Phase 3 commercial docs]      ← Framework for new clients
│
├── csv_templates/                     ← Import templates
│
├── scripts/                           ← Operational scripts
│
├── .claude/                           ← Governance engine (Layer 1)
│   ├── settings.json
│   └── hooks/
│
└── .github/workflows/                 ← Governance engine (Layer 2)
```

---

## 4. Phase Structure

| Phase | Name                                    | Gate Protocol                          |
|------|-----------------------------------------|----------------------------------------|
| 1    | Inspection, Backup & Repo Foundation    | Complete → present to operator → approve Phase 2 |
| 2    | Configuration Validation & Pipeline     | Complete → present to operator → approve Phase 3 |
| 3    | Commercialisation Framework             | Complete → present to operator → approve Phase 4 |
| 4    | CI/CD Governance Engine                 | Requires GitHub remote — confirm before starting |

**Current status:** Phases 1–3 complete. Phase 4 pending GitHub remote connection.

---

## 5. How to Onboard a New Developer or AI Session

1. Read `CLAUDE.md` (read automatically at session start via hooks)
2. Read `docs/ONBOARDING_GUIDE.md`
3. Read `docs/IMPLEMENTATION_STANDARDS.md`
4. Check `CLAUDE.md → ACTIVE PHASE`
5. Check `CLAUDE.md → KNOWN ISSUES`
6. Take a backup before any changes: `bash scripts/backup_famoil.sh`
7. Proceed only within the current approved phase

A new session must never make assumptions about the current state.
Read the documents. Trust the documents. Update the documents after every change.

---

## 6. Governance Architecture Summary

Two layers of governance are active:

**Layer 1 — Session Hooks (`.claude/settings.json`)**
Fires during every Claude Code session. Blocks dangerous commands before
execution. Logs every action. Survives AI context loss because hooks run
independently of Claude's reasoning.

**Layer 2 — Repository CI/CD (`.github/workflows/`)**
Fires on every git push and pull request. Blocks merges that violate governance
rules. Provides team-wide enforcement independent of local sessions.
(Pending: requires GitHub remote connection.)

---

## 7. Adding a New Client or Industry Fork

1. Read `docs/famoil_erp_template/TEMPLATE_VERSIONING.md` for naming convention
2. Read `docs/famoil_erp_template/INDUSTRY_VARIATION_MATRIX.md` for adaptation scope
3. Use `docs/famoil_erp_template/CLIENT_DISCOVERY_TEMPLATE.md` for scoping
4. Fork the template following the versioning strategy
5. Do not modify the base FamOil template when implementing for a new client — always fork
