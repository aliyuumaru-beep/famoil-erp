# NOTE: odoo:17.0 and postgres:16 are floating tags. Pin to a digest in production:
#   docker inspect --format='{{index .RepoDigests 0}}' odoo:17.0
#   Then replace: FROM odoo@sha256:<digest>
FROM odoo:17.0

USER root

# System dependencies for custom modules (lxml, Pillow etc. are already in base image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Custom addons (in-house + third-party)
COPY custom_addons/ /mnt/extra-addons/

# OCA web addons (selected modules — self-contained, no external fetch at build time)
COPY docker/oca_addons/ /mnt/oca-addons/

# Odoo configuration
COPY docker/odoo.conf /etc/odoo/odoo.conf

# Custom entrypoint: injects ODOO_ADMIN_PASSWD before handing off to official entrypoint
COPY docker/entrypoint-wrapper.sh /entrypoint-wrapper.sh
RUN chmod +x /entrypoint-wrapper.sh

# Ensure odoo user owns the addon directories
RUN chown -R odoo:odoo /mnt/extra-addons /mnt/oca-addons

USER odoo

ENTRYPOINT ["/entrypoint-wrapper.sh"]
CMD ["odoo"]

EXPOSE 8069 8072
