#!/bin/bash
# Injects ODOO_ADMIN_PASSWD into odoo.conf before handing off to the official entrypoint.
# The official odoo:17.0 entrypoint only sets db_host/port/user/password from env —
# it does not handle admin_passwd, so we patch the conf file here.
set -e

ODOO_CONF="${ODOO_RC:-/etc/odoo/odoo.conf}"

if [ -n "${ADMIN_PASSWD:-}" ]; then
    # Strip any embedded newlines/CRs (prevents config-file injection via multi-line env vars)
    ADMIN_PASSWD_CLEAN="${ADMIN_PASSWD//[$'\n'$'\r']/}"
    # Fail-fast if stripping newlines left an empty value (all-whitespace ADMIN_PASSWD would
    # write a blank master password, leaving the database manager unprotected)
    if [ -z "${ADMIN_PASSWD_CLEAN}" ]; then
        echo "ERROR: ADMIN_PASSWD resolved to an empty string after stripping whitespace. Aborting." >&2
        exit 1
    fi
    # Remove existing admin_passwd line (commented or not), then append the real value
    sed -i '/^\s*;*\s*admin_passwd\s*=/d' "${ODOO_CONF}"
    printf 'admin_passwd = %s\n' "${ADMIN_PASSWD_CLEAN}" >> "${ODOO_CONF}"
fi

exec /entrypoint.sh "$@"
