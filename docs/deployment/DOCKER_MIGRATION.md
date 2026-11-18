# FamOil — Docker Migration Guide

**Version:** 1.0.0
**Date:** 2026-11-18
**Spec:** DEC-014 / SPEC-DOCKER-01 — see `docs/famoil_erp_template/DECISION_LOG.md` § DEC-014

---

## Overview

This guide covers packaging the FamOil Odoo 17 ERP as a Docker image and migrating it to any Linux/cloud host. The image contains:

- Odoo 17.0 (official base image)
- 12 custom/third-party addons from `custom_addons/`
- 10 OCA web addons from `docker/oca_addons/`

The database and filestore are **not** inside the image — they live in Docker named volumes and are migrated separately via export/import scripts.

---

## Quick Reference

> All `docker compose` commands require `--env-file docker/.env` because compose runs from
> the project root but `.env` is in the `docker/` subdirectory.

| Task | Command |
|------|---------|
| Build image | `docker compose -f docker/docker-compose.yml --env-file docker/.env build` |
| Start stack | `docker compose -f docker/docker-compose.yml --env-file docker/.env up -d` |
| Stop stack | `docker compose -f docker/docker-compose.yml --env-file docker/.env down` |
| Export for migration | `./scripts/export_for_docker.sh` |
| Import on target host | `./scripts/import_to_docker.sh <export_dir>` |
| Smoke test (acceptance gate) | `./scripts/docker_smoke_test.sh` |
| View Odoo logs | `docker compose -f docker/docker-compose.yml --env-file docker/.env logs -f odoo` |
| DB shell | `docker compose -f docker/docker-compose.yml --env-file docker/.env exec db psql -U odoo Famoil` |

---

## Part 1 — First-Time Setup (Build & Run)

### 1.1 Prerequisites

Install Docker Desktop (macOS/Windows) or Docker Engine + Compose (Linux):

```bash
# Verify
docker --version        # Docker 24.x or later
docker compose version  # v2.x or later
```

### 1.2 Configure environment

```bash
cd /Users/aliyuumaru/OdooFolder/odoo17
cp docker/.env.example docker/.env
```

Edit `docker/.env` and set **all three** required values before starting the stack:

| Variable | Requirement |
|----------|-------------|
| `POSTGRES_PASSWORD` | Strong password for the PostgreSQL `odoo` user |
| `ODOO_ADMIN_PASSWD` | Odoo master password (protects `/web/database/` page) |
| `ODOO_PORT` | Host port (default 8069; change if already in use) |
| `POSTGRES_DB` | Database name (default `Famoil`). **If you change this, also update `db_name` in `docker/odoo.conf` and rebuild** (`docker compose build`). |

> **Security gate (mandatory before exposing to any network):** `POSTGRES_PASSWORD` and
> `ODOO_ADMIN_PASSWD` are required at startup — `docker compose up` will fail fast if either
> is missing. Do **not** commit `.env` to git.

### 1.3 Build the image

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build
```

This builds from `docker/Dockerfile` using the project root as build context. It copies:
- `custom_addons/` → `/mnt/extra-addons/`
- `docker/oca_addons/` → `/mnt/oca-addons/`

Expected build time: 2–5 minutes (downloads Odoo base image on first build).

### 1.4 Start the stack

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

This starts two containers:
- `odoo17-db-1` — PostgreSQL 16
- `odoo17-odoo-1` — Odoo 17

Verify they are running:
```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env ps
```

### 1.5 Initial database setup (fresh install only)

If starting from scratch (no migration), initialise the database:

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env exec odoo odoo \
  -d Famoil \
  -i base,stock,mrp,account,sale,purchase \
  --without-demo=all \
  --stop-after-init
```

Then restart:
```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env restart odoo
```

Access: `http://localhost:8069` (or the host's IP).

---

## Part 2 — Migrating the Existing FamOil Instance

Use this path when moving the live `Famoil` database from the macOS local instance to Docker (on the same machine or a new host).

### 2.1 Export from macOS (source machine)

Make sure Odoo is **stopped** before exporting:

```bash
# Stop the local Odoo process first, then:
cd /Users/aliyuumaru/OdooFolder/odoo17
./scripts/export_for_docker.sh
```

Output directory: `~/OdooFolder/odoo_backups/docker_export_YYYYMMDD_HHMM/`

Contents:
```
famoil_YYYYMMDD_HHMM.dump   ← PostgreSQL custom-format dump
filestore.tar.gz             ← Odoo attachments and reports
MANIFEST.txt                 ← sizes and SHA-256 checksums
```

### 2.2 Transfer to target host (if different machine)

```bash
# Example using scp — replace <target> with IP/hostname
scp -r ~/OdooFolder/odoo_backups/docker_export_YYYYMMDD_HHMM/ user@<target>:/opt/famoil_export/
```

Or compress and copy via USB / Google Drive if network is unavailable.

### 2.3 Start Docker stack on target (without data)

On the target host, clone the repository and start the stack:

```bash
git clone https://github.com/aliyuumaru-beep/famoil-erp.git
cd famoil-erp
cp docker/.env.example docker/.env   # and set password
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d db
# Wait for DB to be healthy, then:
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d odoo
```

### 2.4 Import data

```bash
cd famoil-erp
./scripts/import_to_docker.sh /opt/famoil_export/docker_export_YYYYMMDD_HHMM
```

Type `CONFIRM` when prompted. The script:
1. Stops the Odoo container
2. Drops and recreates the `Famoil` database
3. Restores the pg_dump
4. Restores the filestore into the Docker volume
5. Restarts Odoo

### 2.5 Verify — Automated Smoke Test (Acceptance Gate)

Run the smoke test before doing anything else. It starts the stack, waits until Odoo accepts TCP connections on its port, confirms the werkzeug HTTP service started in the logs, then stops cleanly:

```bash
./scripts/docker_smoke_test.sh
```

> **Note:** `docker_smoke_test.sh` checks TCP connectivity + log confirmation (not `/web/health`).
> The `/web/health` endpoint returns 500 on a fresh stack because `db_name = Famoil` is set
> in `odoo.conf` and no database exists yet — that is expected before `import_to_docker.sh`
> has been run. After import, Odoo responds normally.

Expected output ends with:
```
=== SMOKE TEST PASSED ===
Date: YYYY-MM-DD HH:MM:SS UTC
```

**This is the acceptance criterion for a successful Docker deployment.** Record the pass date here:

> Smoke Test: ☐ PASS — Date: 2026-11-18 09:22:09 UTC — Host: Mac — Signed: Aliyu

Then verify data integrity:

```bash
# Check Odoo starts cleanly
docker compose -f docker/docker-compose.yml --env-file docker/.env logs -f odoo
```

Open `http://<host>:8069` and log in with `admin`.

Verify:
- [ ] Manufacturing → Bills of Materials — 3-stage BOMs present (BOM 10, 15, 208/209)
- [ ] Inventory → Products — Crude Soya Oil, Refined Soya Oil, RSO 25L, RSO 5L visible
- [ ] Accounting → Journal Entries — historical entries present
- [ ] Settings → Technical → Scheduled Actions — automations active

---

## Part 3 — Day-to-Day Operations

### Backup (from Docker)

The existing `scripts/backup_famoil.sh` script targets the macOS local PostgreSQL. For Docker, use `export_for_docker.sh` as the backup tool:

```bash
./scripts/export_for_docker.sh
```

Schedule via cron on the host:
```
0 2 * * * /path/to/famoil-erp/scripts/export_for_docker.sh >> /var/log/famoil_backup.log 2>&1
```

### Rebuilding the image after addon changes

Whenever `custom_addons/` or `docker/oca_addons/` are modified:

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env build --no-cache
docker compose -f docker/docker-compose.yml --env-file docker/.env up -d
```

### Updating Odoo (minor patch)

1. Update the `FROM odoo:17.0` pin in `docker/Dockerfile` to the new patch tag.
2. Rebuild the image.
3. Test on a copy of the data first.

### Accessing the database directly

```bash
docker compose -f docker/docker-compose.yml --env-file docker/.env exec db psql -U odoo Famoil
```

### Environment variables at runtime

Override any `odoo.conf` value via `ODOO_*` env vars passed to the container. The official Odoo image reads `HOST`, `USER`, `PASSWORD` for DB connection; all other config comes from `/etc/odoo/odoo.conf`.

---

## Part 4 — Production Hardening (before go-live)

> **⚠ WARNING — never `docker commit` a running stack container.** The `entrypoint-wrapper.sh`
> writes `admin_passwd` in plaintext to `/etc/odoo/odoo.conf` inside the container at start-up.
> A `docker commit` captures that layer; anyone who pulls the image can read the master password.
> **Always build from `Dockerfile` only — never from committed containers.**

Before exposing Docker Odoo to the internet:

1. **Reverse proxy (Nginx/Traefik) — required before changing `proxy_mode`:** Put Nginx in front; handle TLS (Let's Encrypt) there. The default `docker/odoo.conf` ships with `proxy_mode = False` (safe default). Once your reverse proxy is running and tested, change it to `proxy_mode = True` and rebuild. **Never set `proxy_mode = True` without a proxy** — it makes Odoo trust `X-Forwarded-For` unconditionally, enabling client IP spoofing.
2. **Change default passwords:** Update `POSTGRES_PASSWORD` and `ODOO_ADMIN_PASSWD` in `docker/.env` before go-live.
3. **Disable database list:** `list_db = False` is already set in `odoo.conf`.
4. **Workers:** Tune `workers` in `odoo.conf` based on available CPUs (formula: `(CPUs × 2) + 1`). Note: `workers > 0` requires a reverse proxy for long-polling/notifications; use `workers = 0` for local/development testing.
5. **Firewall:** Only expose port 80/443 (Nginx). Block port 8069 from the internet; leave it accessible from localhost/internal only.
6. **Volume backups:** Configure automated export and copy to off-site storage (S3, Backblaze B2, Google Drive via rclone).
7. **Pin base image digests:** Run `docker inspect --format='{{index .RepoDigests 0}}' odoo:17.0` and `postgres:16` after the first successful build, record the digests, and pin `Dockerfile:4` and `docker-compose.yml:5` to those values before production deployment.

---

## File Reference

```
docker/
├── Dockerfile               ← Image definition (Odoo 17 + addons)
├── docker-compose.yml       ← Full stack (Odoo + PostgreSQL 16)
├── odoo.conf                ← Odoo configuration for Docker
├── .env.example             ← Environment variable template
├── entrypoint-wrapper.sh   ← Injects ADMIN_PASSWD into odoo.conf at container start
└── oca_addons/              ← 10 OCA web addons (self-contained)
    ├── web_responsive/
    ├── web_environment_ribbon/
    ├── web_notify/
    ├── web_refresher/
    ├── web_theme_classic/
    ├── web_dialog_size/
    ├── web_m2x_options/
    ├── web_pivot_computed_measure/
    ├── web_search_with_and/
    └── web_remember_tree_column_width/

scripts/
├── export_for_docker.sh    ← Export DB + filestore from macOS
├── import_to_docker.sh     ← Import into Docker stack
└── docker_smoke_test.sh    ← Acceptance gate: start stack, check TCP port + werkzeug log entry
```

---

*See also: `docs/famoil_erp_template/DECISION_LOG.md` → DEC-014 for the architectural rationale.*
