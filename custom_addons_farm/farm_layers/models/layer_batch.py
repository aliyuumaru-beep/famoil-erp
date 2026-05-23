from odoo import models, fields, api


class FarmLayerBatch(models.Model):
    _name = "farm.layer.batch"
    _description = "Layer Batch / Flock"
    _order = "start_date desc"

    name = fields.Char(string="Batch Reference", required=True)
    start_date = fields.Date(string="Placement Date", required=True)
    breed = fields.Char(string="Breed")

    birds_started = fields.Integer(
        string="Birds Started",
        required=True,
        help="Number of birds placed at the start of the batch",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("closed", "Closed"),
        ],
        default="draft",
    )

    # RELATIONSHIPS
    daily_log_ids = fields.One2many(
        "farm.layer.daily.log",
        "batch_id",
        string="Daily Logs",
    )

    # KPI FIELDS
    birds_alive = fields.Integer(
        compute="_compute_birds_alive",
        store=True,
    )

    total_eggs = fields.Integer(
        compute="_compute_totals",
        store=True,
    )

    cumulative_mortality = fields.Integer(
        compute="_compute_totals",
        store=True,
    )

    avg_lay_rate = fields.Float(
        compute="_compute_totals",
        store=True,
    )

    # COMPUTES
    @api.depends("birds_started", "daily_log_ids.mortality")
    def _compute_birds_alive(self):
        for batch in self:
            batch.birds_alive = (
                batch.birds_started
                - sum(batch.daily_log_ids.mapped("mortality"))
            )

    @api.depends(
        "daily_log_ids.eggs_collected",
        "daily_log_ids.mortality",
        "daily_log_ids.lay_rate",
    )
    def _compute_totals(self):
        for batch in self:
            logs = batch.daily_log_ids
            batch.total_eggs = sum(logs.mapped("eggs_collected"))
            batch.cumulative_mortality = sum(logs.mapped("mortality"))
            batch.avg_lay_rate = (
                sum(logs.mapped("lay_rate")) / len(logs)
                if logs else 0.0
            )
