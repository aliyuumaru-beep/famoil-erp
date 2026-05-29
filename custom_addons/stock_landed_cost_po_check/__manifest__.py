{
    'name': 'Landed Cost PO Receipt Check',
    'version': '17.0.1.0.0',
    'summary': 'Blocks landed costs on non-PO receipts; reminds operator after receipt validation',
    'category': 'Inventory',
    'depends': ['stock_landed_costs', 'purchase_stock', 'base_automation', 'mail'],
    'data': ['data/automation.xml'],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
