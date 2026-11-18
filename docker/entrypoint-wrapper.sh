#!/bin/bash
# Injects ODOO_ADMIN_PASSWD into odoo.conf before handing off to the official entrypoint.
# The official odoo:17.0 entrypoint only sets db_host/port/user/password from env —
# it does not handle admin_passwd, so we patch the conf file here.
set -e

ODOO_CONF="${ODOO_RC:-/etc/odoo/odoo.conf}"

if [ -n "${ADMIN_PASSWD:-}" ]; then
    # Guard against newline injection — a multi-line value would corrupt odoo.conf
    if printf '%s' "${ADMIN_PASSWD}" | grep -q $'\n'; then
        echo "ERROR: ADMIN_PASSWD must not contain newline characters." >&2
        exit 1
    fi
    # Remove existing admin_passwd line (commented or not), then append the real value
    sed -i '/^\s*;*\s*admin_passwd\s*=/d' "${ODOO_CONF}"
    printf 'admin_passwd = %s\n' "${ADMIN_PASSWD}" >> "${ODOO_CONF}"
fi

exec /entrypoint.sh "$@"
