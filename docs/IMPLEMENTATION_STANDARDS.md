# Implementation Standards
# FamOil Software Factory — Core Engineering Rules
# Version: 1.2 | Created: 2026-05-27 | Updated: 2026-05-28

> These rules govern all implementation activity on this project.
> They are enforced at two layers: this document (Layer 1 — documentation)
> and `.claude/hooks/` + `.github/workflows/` (Layer 2 — technical enforcement).
> See `docs/architecture/GOVERNANCE_ENGINE.md` for the enforcement mapping.
> All implementation decisions must comply with `docs/architecture/ARCHITECTURAL_PRINCIPLES.md`.
> Implementation sequencing and priority order are defined in `docs/roadmap/PLATFORM_ROADMAP.md`.

---

## Architectural Doctrine Reference

Before making major implementation, module, deployment, workflow, or customization
decisions, consult:

`docs/architecture/ARCHITECTURAL_PRINCIPLES.md`

The principles document governs decision philosophy. This standards document governs
execution rules. If a proposed change conflicts with the architectural principles,
the exception must be approved by the operator and recorded in
`docs/famoil_erp_template/DECISION_LOG.md`.

---

## Rule 1 — Documentation First

Every major implementation activity MUST update:
- Implementation documentation
- Deployment documentation
- Testing documentation
- Architecture documentation
- SOP documentation

No undocumented architecture changes. If a change is not documented,
it did not happen as far as any future session or developer is concerned.

**Enforced by:** `post_tool_validator.sh` (Layer 1), `doc_lint.yml` (Layer 2)

---

## Rule 2 — Git Discipline

Every meaningful change must:
- Use a descriptive commit message (what changed and why)
- Preserve rollback capability (no force pushes to main)
- Avoid local-only critical assets (document everything in the repo)
- Maintain repository cleanliness (.gitignore covers generated files)

Branch strategy recommendation:
- `main` — stable, production-ready only
- `feature/<name>` — new features
- `fix/<name>` — bug fixes
- `phase/<n>` — phase-specific work

**Enforced by:** `pre_tool_guard.sh` (blocks force push, Layer 1), branch protection rules (Layer 2)

---

## Rule 3 — Modularity

Prefer:
- Reusable modules over monolithic implementations
- Reusable configuration over hardcoded values
- Reusable templates over one-off scripts
- Parameterised scripts over project-specific hard-coding

Avoid tightly coupled solutions. Every script must declare variables at the top.
Every module must have a clear single responsibility.

**Enforced by:** `ci_review.yml` code review (Layer 2)

---

## Rule 4 — Minimize Custom Code

Before suggesting or implementing custom code:
1. Perform deep research into native application capability
2. Investigate acceptable workflow/configuration workarounds
3. Present native alternatives first with trade-off analysis
4. Explain operational implications clearly

Only proceed with custom code if:
- Native solutions are operationally insufficient
- The operator explicitly approves custom development

Every customization must include in its code or manifest:
- Justification comment
- Operational purpose
- Maintenance impact
- Upgrade risk assessment

Periodically review existing custom modules. Research whether native improvements
now exist. Present replacement recommendations to the operator.

**Enforced by:** `ci_review.yml` code review (Layer 2)

---

## Rule 5 — Testing Discipline

All major changes must include:
- Implementation validation (does it work as configured?)
- Regression risk assessment (what else could break?)
- Operational scenario testing (what happens under real conditions?)
- Manufacturing flow testing (for manufacturing changes: trace full MO lifecycle)
- UAT considerations documented

Document testing assumptions explicitly. Never claim a change is validated
without stating what was tested and what was not.

**Enforced by:** `post_tool_validator.sh` flags (Layer 1), `ci_review.yml` (Layer 2)

---

## Rule 6 — Standardization

Standardize across all project assets:

**Naming conventions:**
- Documents: `SCREAMING_SNAKE_CASE.md`
- Scripts: `snake_case_projectname.sh` or `snake_case_projectname.py`
- CSV files: `snake_case_entity.csv`
- Hook scripts: `snake_case_purpose.sh`
- Workflow files: `kebab-case.yml`
- Custom addons: `snake_case_purpose` (Odoo convention)

**Structure standards:**
- All documentation under `docs/`
- All CSV templates under `csv_templates/`
- All hook scripts under `.claude/hooks/`
- All CI/CD workflows under `.github/workflows/`
- All operational scripts under `scripts/`

**Document standards:**
- Every `.md` file must have a `# Title` heading on line 1
- Every `.sh` script must have a shebang on line 1 and a comment block explaining purpose
- Every `.csv` file must have column headers on row 1

**Enforced by:** `post_tool_validator.sh` (Layer 1), `doc_lint.yml` (Layer 2)

---

## Rule 7 — Reusability

All outputs should be evaluated for cross-project applicability:
- Can this script be parameterised for a different client?
- Can this BOM structure be used as a template for a different industry?
- Can this hook or workflow be reused in the next software factory project?

Think beyond the current project. Every document, script, and configuration
that is made reusable reduces future implementation time.

**Enforced by:** `ci_review.yml` code review (Layer 2)

---

## Rule 8 — Security & Auditability

Always consider:
- Permissions — least privilege principle
- Traceability — every action logged in `logs/audit_trail.log`
- Fraud prevention — financial transactions require proper approval flow
- Financial integrity — no manual journal entries without documented rationale
- Operational accountability — every configuration change documented

**Never expose in any output:**
- Database passwords
- API keys (including ANTHROPIC_API_KEY)
- Database connection strings with credentials
- SSH private keys
- Any content from `.env` files

**Enforced by:** `pre_tool_guard.sh` and `file_protection_guard.sh` (Layer 1),
`security_scan.yml` (Layer 2)

---

## Rule 9 — Infrastructure Reproducibility

Every environment dependency must be documented so the system can be rebuilt
from scratch by a new operator with only the repository:

Document:
- All dependencies with versions (Python, PostgreSQL, Odoo, OCA modules)
- Environment variables required
- Exact start command
- Port mappings and addons paths
- Backup procedures
- Recovery procedures

No hidden environment assumptions. If it is not in the repository, it does not exist.

**Enforced by:** `pre_tool_guard.sh` (blocks destructive ops, Layer 1),
`backup_check.yml` (Layer 2)

---

## Rule 10 — Team Scalability

All outputs must support onboarding a new developer or AI session with
no prior context, using only what is in the repository:

- `CLAUDE.md` must always reflect current project state
- `docs/ONBOARDING_GUIDE.md` must guide a new person to productive work within 30 minutes
- Every phase must be completable by a replacement developer using only repo documentation
- No founder-dependent or single-person-dependent architecture

**Enforced by:** `session_start_loader.sh` (Layer 1), `doc_lint.yml` (Layer 2)

---

## Rule 11 — Automated Enforcement

Documentation rules are necessary but insufficient.
Every governance rule must exist at two layers simultaneously.

**Layer 1 — Documentation:**
Written in this document and `CLAUDE.md`.
Guides Claude's reasoning and decisions during a session.

**Layer 2 — Technical Enforcement:**
Implemented as Claude Code hooks in `.claude/settings.json`.
Implemented as GitHub Actions workflows in `.github/workflows/`.
Fires deterministically regardless of Claude's reasoning.
Survives AI context loss, developer replacement, and project pause.

When adding a new governance rule:
1. Write it in this document (Layer 1)
2. Implement or extend a hook to enforce it (Layer 2 — session)
3. Implement or extend a workflow to enforce it (Layer 2 — CI/CD)
4. Document the mapping in `docs/architecture/GOVERNANCE_ENGINE.md`
5. Record the decision in `docs/famoil_erp_template/DECISION_LOG.md`

A rule that exists only in documentation is a suggestion.
A rule that exists in both layers is a guarantee.

**Enforced by:** `.claude/settings.json` (Layer 1), all workflows (Layer 2)

---

## Rule 12 — Architectural Principles Compliance

All implementation decisions must comply with:

`docs/architecture/ARCHITECTURAL_PRINCIPLES.md`

This includes decisions relating to:
- Custom code
- Workflow design
- ERP configuration
- Repository structure
- CI/CD governance
- Data migration
- Security
- Industry template expansion
- AI agent permissions

If an exception is necessary, it must be:
1. Approved by the operator
2. Recorded in `docs/famoil_erp_template/DECISION_LOG.md`
3. Linked to the relevant principle being overridden
4. Given a future revisit condition

The architectural principles are the factory doctrine. These implementation standards
are the execution rules. Both must be kept aligned.

**Enforced by:** `ci_review.yml` code review (Layer 2), `doc_lint.yml` references check (Layer 2), operator approval gate

---

## Naming Conventions Reference

| Asset Type        | Convention             | Example                          |
|------------------|------------------------|----------------------------------|
| Documentation     | SCREAMING_SNAKE_CASE   | `IMPLEMENTATION_STANDARDS.md`    |
| Scripts           | snake_case             | `backup_famoil.sh`               |
| CSV templates     | snake_case             | `product_categories.csv`         |
| Hook scripts      | snake_case             | `pre_tool_guard.sh`              |
| CI/CD workflows   | kebab-case             | `ci_review.yml`                  |
| Custom addons     | snake_case             | `stock_crude_oil_tank_restriction`|
| Git branches      | kebab-case with prefix | `feature/bom-refining-stage`     |
| Git commits       | imperative mood        | `add BOM 15 refining operations` |
| Log files         | snake_case             | `audit_trail.log`                |

---

## Approval Workflow

| Change Type                    | Approval Required         |
|-------------------------------|---------------------------|
| New custom addon               | Operator written approval |
| Deleting a committed file      | Operator written approval |
| Disabling a governance hook    | Operator + DECISION_LOG entry |
| git push to remote             | Operator instruction      |
| Database destructive operation | Operator + backup first   |
| Phase progression              | Operator approval gate    |
