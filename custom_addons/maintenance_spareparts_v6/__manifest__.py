{
    "name": "Maintenance Spare Parts (v6)",
    "version": "17.0.1.0.0",
    "category": "Maintenance",
    "summary": "Stage-driven automation for maintenance spare parts",
    "author": "Aliyu Umar",
    "license": "LGPL-3",
    "depends": [
        "maintenance",
        "maintenance_hr",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/maintenance_request_views.xml",
    ],
    "installable": True,
    "application": False,
}
