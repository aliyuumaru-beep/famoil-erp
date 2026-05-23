from odoo import models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        self._check_crude_oil_tank_restriction()
        return super().button_validate()

    def _get_crude_oil_tank_ids(self):
        tanks = self.env['stock.location'].search([
            ('name', 'ilike', 'Crude Oil Tank'),
            ('usage', '=', 'internal'),
            ('active', '=', True),
        ])
        return set(tanks.ids)

    def _get_crude_soya_oil_product_id(self):
        product = self.env['product.product'].search([
            ('name', '=', 'Crude Soya Oil'),
            ('active', '=', True),
        ], limit=1)
        return product.id if product else None

    def _check_crude_oil_tank_restriction(self):
        tank_ids = self._get_crude_oil_tank_ids()
        product_id = self._get_crude_soya_oil_product_id()
        if not tank_ids or product_id is None:
            return

        for picking in self:
            violations = picking.move_ids.filtered(
                lambda m: m.location_dest_id.id in tank_ids
                and m.product_id.id != product_id
                and m.state not in ('done', 'cancel')
            )
            if violations:
                products = ', '.join(violations.mapped('product_id.display_name'))
                tanks = ', '.join(violations.mapped('location_dest_id.name'))
                raise UserError(
                    _("Transfer blocked: only Crude Soya Oil is allowed into %s.\n"
                      "The following product(s) are not permitted: %s")
                    % (tanks, products)
                )
