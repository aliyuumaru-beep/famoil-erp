# Onboarding Guide
# FamOil Software Factory — New Developer / New AI Session
# Version: 1.1 | Created: 2026-05-27 | Updated: 2026-05-28

> Goal: A new developer or AI session should be productive within 30 minutes
> using only this repository. No prior context required.

---

## 1. What Is This Repository?

This repository is the **FamOil Software Factory** — an industrial ERP implementation
and reusable framework built on Odoo 17 Community Edition for a Nigerian soybean oil
processor (FamOil FTZ).

It contains:
- A fully configured Odoo 17 instance (database: `Famoil`)
- A 3-stage manufacturing pipeline (Extraction → Refining → Packaging)
- Reusable framework documentation for other agro-processing clients
- A governance engine that enforces quality standards automatically

---

## 2. First Actions Checklist

### If you are a new developer:
- [ ] Read `CLAUDE.md` — this is the session memory anchor; read it first, always
- [ ] Read `docs/IMPLEMENTATION_STANDARDS.md` — understand the 12 rules before touching anything
- [ ] Read `docs/roadmap/PLATFORM_ROADMAP.md` — understand where the platform is going and what the current priorities are
- [ ] Read `docs/famoil_erp_template/KNOWN_ISSUES.md` — know what is already broken and fixed
- [ ] Read `docs/famoil_erp_template/DECISION_LOG.md` — understand why things are configured as they are
- [ ] Run the backup script before making any changes: `bash scripts/backup_famoil.sh`
- [ ] Check `CLAUDE.md → ACTIVE PHASE` to understand where the project is

### If you are a new Claude Code session:
1. `CLAUDE.md` is read automatically at session start (SessionStart hook)
2. Read `CLAUDE.md` carefully — it contains the current phase, known issues, and DO NOT rules
3. Read `docs/roadmap/PLATFORM_ROADMAP.md` — it defines current priorities, sequencing, and next steps
4. Do not proceed without understanding the ACTIVE PHASE and CRITICAL RULES sections
5. Check `logs/audit_trail.log` to understand what was done in previous sessions

---

## 3. Starting the Odoo Instance

```bash
# From /Users/mac/odoo17 — NOT from inside the odoo/ subdirectory
source odoo/venv/bin/activate
python odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web
```

Access at: http://localhost:8069  
Database: `Famoil`  
Company: FamOil FTZ (company id=2)

> The `odoo.conf` file targets `OdooClean` — always use the `-d Famoil` CLI override.

---

## 4. Key Documents — Reading Order

| Document | What it tells you | Read when |
|----------|-------------------|-----------|
| `CLAUDE.md` | Current project state, active phase, known issues | Every session, first |
| `docs/roadmap/PLATFORM_ROADMAP.md` | Platform vision, priorities, MVP definition, sequencing | After CLAUDE.md, before deciding what to work on |
| `docs/IMPLEMENTATION_STANDARDS.md` | The 12 rules you must follow | Before any work |
| `docs/famoil_erp_template/MANUFACTURING_FLOW.md` | The 3-stage production pipeline | Before touching manufacturing |
| `docs/famoil_erp_template/DECISION_LOG.md` | Why things are configured as they are | Before changing any configuration |
| `docs/famoil_erp_template/KNOWN_ISSUES.md` | Active bugs and resolved issues | Before troubleshooting |
| `docs/famoil_erp_template/COSTING_VALIDATION.md` | Cost model and unit costs | Before touching costing |
| `docs/DEPLOYMENT_GUIDE.md` | How to deploy from scratch | Before any new deployment |
| `docs/architecture/GOVERNANCE_ENGINE.md` | How the hook system works | Before modifying hooks |

---

## 5. Repository Structure at a Glance

```
/Users/mac/odoo17/
├── CLAUDE.md                    ← READ FIRST every session
├── PROJECT_FACTORY_MANUAL.md    ← software factory overview
├── .claude/settings.json        ← governance hook configuration
├── .claude/hooks/               ← 6 enforcement scripts
├── .github/workflows/           ← CI/CD workflows (pending remote)
├── docs/
│   ├── IMPLEMENTATION_STANDARDS.md  ← 12 rules
│   ├── DEPLOYMENT_GUIDE.md
│   ├── ONBOARDING_GUIDE.md      ← this document
│   ├── roadmap/PLATFORM_ROADMAP.md  ← authoritative roadmap
│   ├── architecture/GOVERNANCE_ENGINE.md
│   ├── sops/CI_CD_RUNBOOK.md
│   └── famoil_erp_template/     ← FamOil-specific docs
├── csv_templates/               ← 9 import templates
├── custom_addons/               ← installed modules
├── scripts/                     ← operational scripts
└── logs/                        ← local audit logs (git-ignored)
```

---

## 6. Governance Engine — What to Know

This repository has an active governance engine. As you work:

- **Dangerous bash commands are blocked** — `rm -rf`, `DROP DATABASE`, `git push --force`
  and others will be intercepted and blocked before execution.
- **Writes to protected paths are blocked** — core application files, `.env` files,
  and paths outside the repo root cannot be written.
- **Every action is logged** — `logs/audit_trail.log` records every bash command.
- **Every session is summarised** — `logs/session_reports.log` captures what happened.

If a hook blocks an action you believe is legitimate:
1. Check `logs/blocked_commands.log` for the reason
2. Get operator approval
3. Add a DECISION_LOG entry explaining the exception
4. Then proceed

---

## 7. What NOT to Do

- Do NOT push directly to `main` — all changes go through a PR and CI checks
- Do NOT modify files under `odoo/` (Odoo core application)
- Do NOT expose passwords or credentials in any output
- Do NOT delete committed files without operator approval
- Do NOT progress to the next priority without operator approval
- Do NOT run `git commit --amend` on already-shared commits

---

## 8. Getting Help

- Check `CLAUDE.md → KNOWN ISSUES` for active blockers
- Check `docs/famoil_erp_template/KNOWN_ISSUES.md` for detailed issue history
- If unsure about any action: **STOP and ask the operator**
- Contact: aliyuumaru@gmail.com
