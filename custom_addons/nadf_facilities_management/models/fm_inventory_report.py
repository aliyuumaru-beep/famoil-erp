# Phase 4 — Process 3: Inventory Visibility & Quarterly Reporting
import calendar
from datetime import date, datetime, time

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_QUARTER_MONTHS = {
    'Q1': (1, 3),
    'Q2': (4, 6),
    'Q3': (7, 9),
    'Q4': (10, 12),
}


class FmInventoryReport(models.Model):
    """Quarterly reconciliation of contractor-held consumable inventory
    (Process 3).

    Business purpose: lets the Branch Desk Officer reconcile what each
    contractor reports as closing stock against what the system
    calculates from opening stock + issues - consumption, flagging
    discrepancies for HQ/Cost Control review.

    State machine: draft -> submitted -> approved -> hq_acknowledged
    -> cost_control -> archived.

    Integration points:
    - ``action_populate_lines``: pulls contractor inventory
      (``fm.contractor.inventory.line``) and approved consumable requests
      (``fm.consumable.request``, Process 1) for the report period.
    - ``fm.maintenance.plan.last_inventory_report_id``: the Desk Officer
      can reference the most recent archived report when planning spares.
    """
    _name = 'fm.inventory.report'
    _description = 'Facilities Management Quarterly Inventory Report'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'fm.notification.mixin']
    _order = 'report_year desc, report_period desc, id desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'),
    )
    branch_id = fields.Many2one('hr.department', string='Branch', required=True, tracking=True)
    desk_officer_id = fields.Many2one(
        'res.users', string='Desk Officer', required=True,
        default=lambda self: self.env.user,
    )
    report_period = fields.Selection([
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    ], string='Report Period', required=True)
    report_year = fields.Integer(
        string='Report Year', required=True, default=lambda self: fields.Date.today().year,
    )
    report_date = fields.Date(string='Report Date', default=fields.Date.context_today)
    contractor_ids = fields.Many2many('fm.contractor', string='Contractors Covered')
    line_ids = fields.One2many('fm.inventory.report.line', 'report_id', string='Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted to Head of Facilities'),
        ('approved', 'Approved — Forwarded to HQ'),
        ('hq_acknowledged', 'HQ Acknowledged'),
        ('cost_control', 'With Cost Control'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', tracking=True, copy=False)
    facilities_manager_notes = fields.Text(string='Facilities Manager Notes')
    hq_notes = fields.Text(string='HQ Notes')
    discrepancy_flag = fields.Boolean(
        string='Has Discrepancies', compute='_compute_discrepancy_flag', store=True,
    )
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, copy=False)

    @api.depends('line_ids.discrepancy')
    def _compute_discrepancy_flag(self):
        for rec in self:
            rec.discrepancy_flag = any(rec.line_ids.mapped('discrepancy'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fm.inventory.report') or _('New')
        return super().create(vals_list)

    # ── Period helpers ───────────────────────────────────────────────────

    def _get_period_bounds(self):
        """Return (datetime_start, datetime_end) covering the report's quarter."""
        self.ensure_one()
        start_month, end_month = _QUARTER_MONTHS[self.report_period]
        period_start = date(self.report_year, start_month, 1)
        last_day = calendar.monthrange(self.report_year, end_month)[1]
        period_end = date(self.report_year, end_month, last_day)
        return (
            datetime.combine(period_start, time.min),
            datetime.combine(period_end, time.max),
        )

    def _get_previous_report(self):
        """Most recent archived report for this branch, prior to this period."""
        self.ensure_one()
        quarter_num = int(self.report_period[1])
        candidates = self.env['fm.inventory.report'].search([
            ('branch_id', '=', self.branch_id.id),
            ('state', '=', 'archived'),
            ('id', '!=', self.id),
        ])
        candidates = candidates.filtered(
            lambda r: (r.report_year, int(r.report_period[1])) < (self.report_year, quarter_num)
        )
        candidates = candidates.sorted(
            key=lambda r: (r.report_year, int(r.report_period[1])), reverse=True,
        )
        return candidates[:1]

    # ── Auto-population ──────────────────────────────────────────────────

    def action_populate_lines(self):
        """Pre-fill report lines from contractor inventory and Process 1
        approved consumable requests for the report period.

        DECISION: there is no period-segmented consumption ledger in the
        data model — ``fm.contractor.inventory.line.quantity_consumed`` is
        a running total, not a per-quarter figure. It is used here as the
        ``consumed_this_period`` value, and ``closing_stock_reported``
        defaults to the contractor's current balance. Both are editable
        before submission, as required by the spec.
        """
        period_start, period_end = self._get_period_bounds()[0], self._get_period_bounds()[1]
        request_line_model = self.env['fm.consumable.request.line']
        for rec in self:
            rec.line_ids.unlink()
            previous_report = rec._get_previous_report()
            line_vals = []
            for contractor in rec.contractor_ids:
                for inv_line in contractor.inventory_line_ids:
                    product = inv_line.product_id
                    opening_stock = 0.0
                    if previous_report:
                        prev_line = previous_report.line_ids.filtered(
                            lambda l: l.contractor_id == contractor and l.product_id == product
                        )
                        if prev_line:
                            opening_stock = prev_line[0].closing_stock_calculated

                    approved_lines = request_line_model.search([
                        ('request_id.contractor_id', '=', contractor.id),
                        ('request_id.state', '=', 'approved'),
                        ('product_id', '=', product.id),
                        ('request_id.approval_date', '>=', period_start),
                        ('request_id.approval_date', '<=', period_end),
                    ])
                    issued_this_period = sum(approved_lines.mapped('quantity_approved'))

                    line_vals.append((0, 0, {
                        'contractor_id': contractor.id,
                        'product_id': product.id,
                        'uom_id': inv_line.uom_id.id,
                        'opening_stock': opening_stock,
                        'issued_this_period': issued_this_period,
                        'consumed_this_period': inv_line.quantity_consumed,
                        'closing_stock_reported': inv_line.quantity_balance,
                    }))
            rec.line_ids = line_vals
        return True

    # ── State transitions ──────────────────────────────────────────────

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft inventory reports can be submitted.'))
            rec.write({'state': 'submitted'})
            rec.message_post(body=_('Inventory report submitted to Head of Facilities.'))
            # Phase 6 — flag discrepancies to the Head of Facilities.
            if rec.discrepancy_flag:
                facilities_managers = rec._fm_branch_users(
                    rec.branch_id, 'nadf_facilities_management.group_fm_branch_facilities_manager',
                )
                for user in facilities_managers:
                    rec.activity_schedule(
                        'mail.mail_activity_data_todo',
                        summary=_('Inventory Discrepancy Detected'),
                        note=_('Quarterly inventory report %s for branch %s has one or more '
                               'discrepancies between reported and calculated stock.') % (
                            rec.name, rec.branch_id.name,
                        ),
                        user_id=user.id,
                    )
        return True

    def action_approve(self):
        if not self.env.user.has_group('nadf_facilities_management.group_fm_branch_facilities_manager'):
            raise UserError(_('Only the Head of Facilities can approve an inventory report.'))
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted inventory reports can be approved.'))
            rec.write({'state': 'approved', 'approved_by': self.env.user.id})
            rec.message_post(body=_('Inventory report approved — forwarded to HQ.'))
        return True

    def action_hq_acknowledge(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_('Only approved inventory reports can be acknowledged by HQ.'))
            rec.write({'state': 'hq_acknowledged'})
            rec.message_post(body=_('Inventory report acknowledged by HQ.'))
        return True

    def action_forward_cost_control(self):
        for rec in self:
            if rec.state != 'hq_acknowledged':
                raise UserError(_('Only HQ-acknowledged inventory reports can be forwarded to Cost Control.'))
            rec.write({'state': 'cost_control'})
            rec.message_post(body=_('Inventory report forwarded to Cost Control.'))
        return True

    def action_archive_report(self):
        for rec in self:
            if rec.state != 'cost_control':
                raise UserError(_('Only inventory reports with Cost Control can be archived.'))
            rec.write({'state': 'archived'})
            rec.message_post(body=_('Inventory report archived.'))
        return True


class FmInventoryReportLine(models.Model):
    """Per-contractor, per-product reconciliation line on a Quarterly
    Inventory Report."""
    _name = 'fm.inventory.report.line'
    _description = 'Facilities Management Inventory Report Line'

    report_id = fields.Many2one(
        'fm.inventory.report', string='Report', required=True, ondelete='cascade', index=True,
    )
    contractor_id = fields.Many2one('fm.contractor', string='Contractor', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', related='product_id.uom_id', store=True, readonly=True,
    )
    opening_stock = fields.Float(string='Opening Stock')
    issued_this_period = fields.Float(string='Issued This Period')
    consumed_this_period = fields.Float(string='Consumed This Period')
    closing_stock_reported = fields.Float(string='Closing Stock (Reported)')
    closing_stock_calculated = fields.Float(
        string='Closing Stock (Calculated)', compute='_compute_closing_stock_calculated', store=True,
    )
    discrepancy = fields.Float(string='Discrepancy', compute='_compute_discrepancy', store=True)
    discrepancy_notes = fields.Text(string='Discrepancy Notes')

    @api.depends('opening_stock', 'issued_this_period', 'consumed_this_period')
    def _compute_closing_stock_calculated(self):
        for rec in self:
            rec.closing_stock_calculated = (
                rec.opening_stock + rec.issued_this_period - rec.consumed_this_period
            )

    @api.depends('closing_stock_reported', 'closing_stock_calculated')
    def _compute_discrepancy(self):
        for rec in self:
            rec.discrepancy = rec.closing_stock_reported - rec.closing_stock_calculated
