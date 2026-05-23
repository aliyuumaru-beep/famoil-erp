# Template Versioning Strategy
# FamOil ERP Framework

_Version: 1.0 | Date: 2026-05-22_

---

## Purpose

This document defines how the FamOil ERP framework is versioned, how client forks are managed, and how upgrades are handled across both the template and deployed instances.

---

## 1. Naming Conventions

### 1.1 Framework Template Name

```
FAMOIL-TPL-{INDUSTRY}-v{MAJOR}.{MINOR}.{PATCH}
```

| Segment | Description | Example |
|---|---|---|
| `FAMOIL-TPL` | Fixed prefix — identifies this as a framework template | |
| `{INDUSTRY}` | Short industry code (see table below) | `SOYBEAN` |
| `v{MAJOR}` | Breaking changes — major Odoo version or architectural redesign | `v1` |
| `{MINOR}` | New features, new modules, significant config additions | `3` |
| `{PATCH}` | Bug fixes, documentation updates, minor corrections | `2` |

**Industry Codes:**

| Industry | Code |
|---|---|
| Soybean Oil Mill | `SOYBEAN` |
| Palm Oil Mill | `PALMOIL` |
| Groundnut Oil Mill | `GNUT` |
| Rice Mill | `RICEMILL` |
| Feed Mill | `FEEDMILL` |
| Shea Butter Oil Mill | `SHEA` |
| FMCG Food Processing | `FMCG` |
| Generic Agro-processing | `AGRO` |

**Examples:**
```
FAMOIL-TPL-SOYBEAN-v1.0.0   ← Initial release of soybean template
FAMOIL-TPL-SOYBEAN-v1.1.0   ← Added Nigeria compliance module
FAMOIL-TPL-SOYBEAN-v1.1.1   ← Fixed SoapStock BOM classification error
FAMOIL-TPL-PALMOIL-v1.0.0   ← First palm oil template derived from soybean v1.1.1
```

### 1.2 Client Fork Name

```
FAMOIL-{CLIENTCODE}-{INDUSTRY}-v{FORK_MAJOR}.{FORK_MINOR}
```

| Segment | Description | Example |
|---|---|---|
| `FAMOIL` | Fixed prefix | |
| `{CLIENTCODE}` | 3–5 letter client code (assigned at engagement start) | `FAM` |
| `{INDUSTRY}` | Industry code (same as template) | `SOYBEAN` |
| `v{FORK_MAJOR}` | Tracks which template major version the fork was based on | `v1` |
| `{FORK_MINOR}` | Client-specific changes incremented independently | `2` |

**Examples:**
```
FAMOIL-FAM-SOYBEAN-v1.0    ← FamOil initial deployment (based on TPL v1.0.0)
FAMOIL-FAM-SOYBEAN-v1.1    ← FamOil: added shea butter refining BOM post-go-live
FAMOIL-ABK-PALMOIL-v1.0    ← New client Abeke Foods, palm oil, based on TPL v1.0.0
```

---

## 2. Version Types

### Major Version (MAJOR++)

Increment when:
- Upgrading the underlying Odoo version (e.g., 17 → 18)
- Fundamental architectural change (e.g., switching costing method framework-wide)
- Custom module API breaks (existing client forks cannot upgrade without code changes)

**Rule:** A major version change always requires a fresh client migration plan. Do not assume client forks can absorb major version changes automatically.

### Minor Version (MINOR++)

Increment when:
- A new industry template is added
- A new custom module is added to the framework
- A new compliance layer is added (e.g., new tax type, new regulatory requirement)
- The discovery template or commercial guide has significant structural changes
- A new CSV migration template is added

**Rule:** Minor versions should be backwards-compatible. A client on v1.2.x should be able to absorb v1.3.0 changes with only configuration work, not code changes.

### Patch Version (PATCH++)

Increment when:
- A bug is fixed in a BOM, formula, or configuration
- A documentation error is corrected
- A cost share percentage is revised (e.g., the SoapStock removal)
- A typo in a work center or operation name is fixed

**Rule:** Patches never require client re-migration. Document the change in the CHANGELOG (see Section 5).

---

## 3. Client Fork Strategy

### 3.1 When to Fork

A client fork is created at the moment a discovery document is signed off and configuration begins. The fork:
- Is based on the most current stable template version at that time
- Lives in its own directory or repository
- Is never merged back into the template (changes flow template → fork only, not fork → template)

### 3.2 What Goes in a Client Fork

| Item | In Template | In Client Fork |
|---|---|---|
| Generic BOM patterns | Yes | Client-specific BOMs |
| Standard CoA structure | Yes | Client-specific account codes |
| Nigerian compliance config | Yes | Client's actual TIN, VAT number |
| Discovery template | Yes | Completed discovery document |
| Generic CSV templates | Yes | Populated client data CSVs |
| Custom modules | Framework modules only | Client-specific modules |
| Backup scripts | Template scripts | Client-specific paths and DB name |

### 3.3 Fork Directory Structure

```
clients/
  {CLIENTCODE}/
    discovery/
      CLIENT_DISCOVERY_{CLIENTCODE}.md     ← completed discovery
    config/
      bom/                                  ← client BOM export CSVs
      products/
      partners/
      accounts/
    modules/
      {client_specific_module}/            ← client-only custom modules
    docs/
      COSTING_VALIDATION_{CLIENTCODE}.md
      KNOWN_ISSUES_{CLIENTCODE}.md
      DECISION_LOG_{CLIENTCODE}.md
    scripts/
      backup_{clientcode}.sh
    VERSION                                 ← single line: FAMOIL-{CODE}-{IND}-v{X}.{Y}
```

### 3.4 What Must Never Enter a Client Fork

- Credentials (passwords, API keys, database connection strings)
- Another client's data or configuration
- Experimental or untested modules

---

## 4. Upgrade Strategy

### 4.1 Template Upgrades

When the template is updated (minor or patch):

1. Update the template files in `docs/famoil_erp_template/`
2. Update the `VERSION` file in the template root
3. Write a CHANGELOG entry (see Section 5)
4. Notify active client engagements if the change is relevant to them

### 4.2 Client Upgrade from Template Patch

Patches (bug fixes, documentation corrections):
- Implementer reviews the patch and decides if it applies to the client
- If it applies: apply the configuration change directly to the client's Odoo instance
- Update the client's fork `VERSION` minor number
- Document in the client's KNOWN_ISSUES log

### 4.3 Client Upgrade from Template Minor Version

Minor upgrades (new modules, new compliance requirements):
- Assess applicability per client
- Create a change request if the client wants the new feature
- Apply in a maintenance window; test before cutover
- Bump the client fork's minor version

### 4.4 Odoo Major Version Upgrade (e.g., 17 → 18)

This is a full re-implementation project, not a configuration change:

1. Stand up a new Odoo 18 instance
2. Migrate template to Odoo 18 (update custom modules, test standard flows)
3. Release `FAMOIL-TPL-{IND}-v2.0.0`
4. For each active client: scope a migration project separately
5. Run old and new instances in parallel until client signs off
6. Do not force clients to upgrade on a schedule — support the old major version for at least 24 months

---

## 5. Changelog Format

Maintain a `CHANGELOG.md` at the template root. Each entry:

```markdown
## FAMOIL-TPL-SOYBEAN-v1.1.1 — 2026-05-22

### Fixed
- Removed SoapStock from crude oil production BOM (was incorrectly classified;
  SoapStock is a refining byproduct). Soya Cake cost share updated 35% → 40%.
  Affects: COSTING_VALIDATION.md, KNOWN_ISSUES.md (ISSUE-008 added).

---

## FAMOIL-TPL-SOYBEAN-v1.0.0 — 2026-05-22

### Initial Release
- Soybean oil mill template based on FamOil (FAM) Phase 1 and Phase 2 implementation.
- Includes: BOM ID 10, 5 work centers, Nigerian compliance layer, 8-phase playbook.
```

---

## 6. Version Registry

Maintain a simple registry of all deployed client forks.

| Client Code | Client Name | Industry | Template Base | Current Fork Version | Go-Live Date | Support Tier |
|---|---|---|---|---|---|---|
| FAM | FamOil FTZ | SOYBEAN | v1.1.1 | v1.0 | TBD | Active |

_Update this table at the start of each new engagement and after each client version bump._
