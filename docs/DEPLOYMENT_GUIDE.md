# Deployment Guide
# FamOil Software Factory — Odoo 17 Community
# Version: 1.0 | Created: 2026-05-27

---

## 1. Prerequisites

| Requirement    | Version  | Notes                                        |
|---------------|----------|----------------------------------------------|
| macOS          | 12+      | Tested on macOS 23.6.0                       |
| Python         | 3.10+    | Managed via venv at `odoo/venv/`             |
| PostgreSQL     | 14+      | Running on 16.11 (Homebrew)                  |
| Odoo Community | 17.0.1.3 | Source at `odoo/`                            |
| OCA web addons | 17.0     | Installed at `/Users/mac/oca_web`            |

---

## 2. Environment Variables and Configuration

**odoo.conf location:** `/Users/mac/odoo17/odoo/odoo.conf`
> WARNING: `odoo.conf` is git-ignored and contains credentials. Never commit it.
> The config targets database `OdooClean` — always override with `-d Famoil` CLI flag.

**Key paths:**
```
Odoo core:       /Users/mac/odoo17/odoo/
Python venv:     /Users/mac/odoo17/odoo/venv/
Custom addons:   /Users/mac/odoo17/custom_addons/
OCA web addons:  /Users/mac/oca_web/
Filestore:       /Users/mac/Library/Application Support/Odoo/filestore/Famoil/
Backups:         /Users/mac/odoo_backups/
```

---

## 3. Start Command

Run from `/Users/mac/odoo17` — NOT from inside the `odoo/` subdirectory:

```bash
source odoo/venv/bin/activate
python odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web
```

Access: http://localhost:8069  
Default port: 8069

---

## 4. Installing a New Custom Addon (First Time Only)

```bash
source odoo/venv/bin/activate
python odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web \
  -i <module_name>
```

> The `-i` flag is for first-time installation only. Do not include it on normal start.

---

## 5. Upgrading a Custom Addon

```bash
source odoo/venv/bin/activate
python odoo/odoo-bin -d Famoil -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web \
  -u <module_name>
```

---

## 6. Fresh Deployment (New Client Instance)

```bash
# 1. Create fresh database — no demo data
createdb -U odoo -E UTF8 "ClientDB"
python odoo/odoo-bin -d ClientDB --without-demo=all -i base \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web

# 2. Access Odoo and configure:
#    - Company name, country (Nigeria), currency (NGN), fiscal year
#    - Archive the default "My Company" if present
#    - Install required apps: Inventory, Manufacturing, Accounting

# 3. Install FamOil custom modules
python odoo/odoo-bin -d ClientDB -r odoo \
  --addons-path=odoo/odoo/addons,custom_addons,/Users/mac/oca_web \
  -i stock_crude_oil_tank_restriction,mrp_component_availability_check

# 4. Import CSV templates in order — see csv_templates/README.md
```

---

## 7. Post-Deployment Verification

- [ ] Odoo starts with no errors in server log
- [ ] http://localhost:8069 is accessible
- [ ] FamOil FTZ company is selected (id=2)
- [ ] Currency = NGN
- [ ] Inventory → Warehouses shows FamOilWH (code: CW)
- [ ] Manufacturing → Bills of Materials shows BOM 10 and BOM 15
- [ ] Stock quants match expected state (see `docs/famoil_erp_template/COSTING_VALIDATION.md`)
- [ ] Custom modules installed and active (Settings → Apps → Installed)
- [ ] Governance hooks active: `.claude/settings.json` present
