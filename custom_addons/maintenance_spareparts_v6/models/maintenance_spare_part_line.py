from odoo import models, fields


class MaintenanceSparePartLine(models.Model):
    _name = 'maintenance.spare.part.line'
    _description = 'Maintenance Spare Part Line'

    request_id = fields.Many2one(
        'maintenance.request',
        ondelete='cascade',
        required=True
    )

    product_id = fields.Many2one(
        'product.product',
        required=True
    )

    quantity = fields.Float(
        required=True,
        default=1.0
    )

    uom_id = fields.Many2one(
        'uom.uom',
        related='product_id.uom_id',
        store=True,
        readonly=True
    )

    move_id = fields.Many2one(
        'stock.move',
        readonly=True,
        copy=False
    )
