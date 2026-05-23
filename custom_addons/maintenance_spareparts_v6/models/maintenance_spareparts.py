from odoo import models, fields


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    spare_part_line_ids = fields.One2many(
        'maintenance.spare.part.line',
        'request_id',
        string='Spare Parts'
    )

    def action_request_spare_parts(self):
        StockMove = self.env['stock.move']

        for request in self:
            for line in request.spare_part_line_ids:
                if line.move_id:
                    continue  # already requested

                move = StockMove.create({
                    'name': f'{request.name} - Spare Part',
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': request.company_id.internal_stock_location_id.id,
                    'location_dest_id': request.company_id.maintenance_location_id.id,
                })

                move._action_confirm()   # 🔻 forecast
                move._action_assign()    # reserve stock

                line.move_id = move.id

    def action_done(self):
        res = super().action_done()

        for request in self:
            for line in request.spare_part_line_ids:
                move = line.move_id
                if move and move.state not in ('done', 'cancel'):
                    move._action_done()  # 🔻 on-hand

        return res
