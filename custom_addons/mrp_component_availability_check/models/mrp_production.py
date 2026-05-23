from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _button_mark_done_sanity_checks(self):
        super()._button_mark_done_sanity_checks()
        for order in self:
            unavailable = []
            for move in order.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                reserved = move.quantity
                required = move.product_uom_qty
                rounding = move.product_uom.rounding
                if float_compare(reserved, required, precision_rounding=rounding) < 0:
                    unavailable.append(
                        f"  - {move.product_id.display_name}: "
                        f"required {required:.2f} {move.product_uom.name}, "
                        f"available {reserved:.2f} {move.product_uom.name}"
                    )
            if unavailable:
                raise UserError(
                    _("Cannot process manufacturing order '%s'.\n"
                      "The following components do not have sufficient stock:\n%s\n\n"
                      "Please reserve the required quantities before proceeding.")
                    % (order.name, "\n".join(unavailable))
                )
