from odoo import models, _
from odoo.exceptions import UserError


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def button_validate(self):
        self._check_po_receipt()
        return super().button_validate()

    def _check_po_receipt(self):
        for cost in self:
            for picking in cost.picking_ids:
                if picking.picking_type_code != 'incoming':
                    raise UserError(_(
                        "Landed cost blocked: '%s' is not an incoming receipt.\n"
                        "Only purchase order receipts can receive landed costs."
                    ) % picking.name)

                if not picking.move_ids.filtered('purchase_line_id'):
                    raise UserError(_(
                        "Landed cost blocked: receipt '%s' was not created from a "
                        "Purchase Order.\n"
                        "Only purchase order receipts can receive landed costs."
                    ) % picking.name)
