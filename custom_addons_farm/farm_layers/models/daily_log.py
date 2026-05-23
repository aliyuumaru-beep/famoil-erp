from odoo import models, fields, api


class FarmLayerDailyLog(models.Model):
    _name = "farm.layer.daily.log"
    _description = "Layer Daily Log"
    _order = "log_date desc"

    log_date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )

    batch_id = fields.Many2one(
        "farm.layer.batch",
        string="Layer Batch",
        required=True,
        ondelete="cascade",
    )

    eggs_collected = fields.Integer(
        string="Eggs Collected",
        default=0,
    )

    mortality = fields.Integer(
        string="Mortality",
        default=0,
    )

    lay_rate = fields.Float(
        string="Lay Rate (%)",
        help="Eggs laid as a percentage of birds alive",
    )

    notes = fields.Text(
        string="Notes",
    )
