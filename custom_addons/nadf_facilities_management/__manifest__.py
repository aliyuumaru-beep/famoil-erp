# Phase 1 — Module Scaffold & Security Foundation
{
    'name': 'NADF Facilities Management',
    'version': '17.0.1.0.0',
    'category': 'Operations/Maintenance',
    'summary': 'NADF Facilities Management: Reactive Maintenance, Preventive Maintenance, and Inventory Reporting',
    'description': """
        Implements the NADF Facilities Management Department workflows:
        - Process 1: Reactive Maintenance (Job Complaints, Job Orders, TFF Contractor assignment)
        - Process 2: Preventive Maintenance (Quarterly/Annual plans, schedule execution)
        - Process 3: Inventory Visibility and Quarterly Reporting
        Integrates with HQ Procurement approval, Cost Control, Director approval, and Finance payment workflows.
    """,
    'author': 'NADF / Tasemmen Engineering',
    'depends': [
        'base',
        'mail',
        'hr',
        'purchase',
        'stock',
        'account',
    ],
    'data': [
        'security/fm_security.xml',
        'security/ir.model.access.csv',
        'data/fm_sequence_data.xml',
        'data/fm_cron_data.xml',
        'data/fm_mail_template_data.xml',
        'report/report_fm_job_order.xml',
        'report/report_fm_monthly_batch.xml',
        'report/report_fm_inventory_report.xml',
        'views/fm_contractor_views.xml',
        'views/fm_job_complaint_views.xml',
        'views/fm_job_order_views.xml',
        'views/fm_consumable_request_views.xml',
        'views/fm_maintenance_plan_views.xml',
        'views/fm_maintenance_schedule_views.xml',
        'views/fm_inventory_report_views.xml',
        'views/fm_satisfaction_feedback_wizard_views.xml',
        'views/fm_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
