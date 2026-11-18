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

# Ensure odoo user owns the addon directories
RUN chown -R odoo:odoo /mnt/extra-addons /mnt/oca-addons

USER odoo

EXPOSE 8069 8072
