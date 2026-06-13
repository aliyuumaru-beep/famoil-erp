# Phase 2 — Process 1: Reactive Maintenance (Contractor master data)
from odoo import models, fields, api


class FmContractor(models.Model):
    """Facilities Management contractor (TFF / local / specialised).

    Business purpose: master record for external contractors who execute
    reactive (Process 1) and preventive (Process 2) maintenance work.
    Tracks the contractor's held consumable inventory so the Branch Desk
    Officer has real-time visibility over stock issued to the field.

    Integration points: referenced by ``fm.job.order``,
    ``fm.maintenance.schedule`` and ``fm.consumable.request``.
    ``user_ids`` links portal/internal users to a contractor record so
    record rules (Phase 7) can restrict a contractor to their own records.
    """
    _name = 'fm.contractor'
    _description = 'Facilities Management Contractor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    contractor_type = fields.Selection([
        ('tff', 'TFF / Local Contractor'),
        ('mechanical', 'Mechanical Contractor'),
        ('electrical', 'Electrical Contractor'),
        ('general', 'General'),
    ], string='Contractor Type', required=True, default='tff', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    branch_id = fields.Many2one('hr.department', string='Assigned Branch', tracking=True)
    active = fields.Boolean(default=True)
    inventory_line_ids = fields.One2many(
        'fm.contractor.inventory.line', 'contractor_id', string='Inventory',
    )
    # DECISION: user_ids is not in the original spec table for fm.contractor,
    # but Phase 7 requires "TFF Contractor: can only see Job Orders and
    # Consumable Requests assigned to their contractor record" — this link
    # is the minimal addition needed to express that record rule.
    user_ids = fields.Many2many(
        'res.users', string='Contractor Users',
        help='Users (Facilities Management / TFF Contractor group) representing '
             'this contractor for record-rule access.',
    )


class FmContractorInventoryLine(models.Model):
    """Stock of consumables held by a contractor.

    Business purpose: gives the Branch Desk Officer real-time visibility
    over materials issued to a contractor versus consumed on jobs.
    Updated automatically when a ``fm.consumable.request`` is approved
    (issued quantity) and read by ``fm.inventory.report`` for quarterly
    reconciliation (Process 3).
    """
    _name = 'fm.contractor.inventory.line'
    _description = 'Facilities Management Contractor Inventory Line'
    _order = 'product_id'

    contractor_id = fields.Many2one(
        'fm.contractor', string='Contractor', required=True,
        ondelete='cascade', index=True,
    )
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity_issued = fields.Float(string='Quantity Issued', default=0.0)
    quantity_consumed = fields.Float(string='Quantity Consumed', default=0.0)
    quantity_balance = fields.Float(
        string='Balance', compute='_compute_quantity_balance', store=True,
    )
    last_updated = fields.Date(string='Last Updated', default=fields.Date.context_today)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    @api.depends('quantity_issued', 'quantity_consumed')
    def _compute_quantity_balance(self):
        for rec in self:
            rec.quantity_balance = rec.quantity_issued - rec.quantity_consumed
