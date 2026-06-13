# Phase 3 — Process 2: Preventive Maintenance (Plan & Spare Parts)
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FmMaintenancePlan(models.Model):
    """Quarterly or annual preventive maintenance plan for a branch
    (Process 2, step 1).

    State machine: draft -> submitted -> approved/rejected -> active
    -> closed. Approval is restricted to the Branch Facilities Manager
    group, enforced both at the Python level (this model) and via the
    `groups` attribute on the form button (Phase 5).

    Integration points:
    - ``schedule_ids``: individual equipment maintenance entries
      (``fm.maintenance.schedule``) generated/managed under this plan.
    - ``spare_part_line_ids``: planned spares, used as a reference list
      for ``fm.inventory.report`` reconciliation (Process 3).
    - ``inventory_report_ids`` / ``last_inventory_report_id``: added in
      Phase 4 to surface the branch's last inventory position.
    """
    _name = 'fm.maintenance.plan'
    _description = 'Preventive Maintenance Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, quarter, id desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'),
    )
    plan_type = fields.Selection([
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ], string='Plan Type', required=True, default='quarterly')
    year = fields.Integer(string='Year', required=True, default=lambda self: fields.Date.today().year)
    quarter = fields.Selection([
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    ], string='Quarter')
    branch_id = fields.Many2one('hr.department', string='Branch', required=True, tracking=True)
    desk_officer_id = fields.Many2one(
        'res.users', string='Desk Officer', required=True,
        default=lambda self: self.env.user,
    )
    facilities_manager_id = fields.Many2one('res.users', string='Head of Facilities')
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', tracking=True, copy=False)
    schedule_ids = fields.One2many('fm.maintenance.schedule', 'plan_id', string='Schedule Entries')
    spare_part_line_ids = fields.One2many(
        'fm.plan.spare.part.line', 'plan_id', string='Planned Spare Parts',
    )
    approval_date = fields.Datetime(string='Approval Date', readonly=True, copy=False)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, copy=False)
    rejection_reason = fields.Text(string='Rejection Reason')

    # Phase 4 — linkage to Process 3 inventory reports
    inventory_report_ids = fields.Many2many(
        'fm.inventory.report', string='Related Inventory Reports',
        compute='_compute_inventory_report_ids',
    )
    last_inventory_report_id = fields.Many2one(
        'fm.inventory.report', string='Last Inventory Report',
        compute='_compute_last_inventory_report_id',
    )

    @api.depends('branch_id', 'year', 'quarter', 'plan_type')
    def _compute_inventory_report_ids(self):
        report_model = self.env['fm.inventory.report']
        for rec in self:
            domain = [('branch_id', '=', rec.branch_id.id), ('report_year', '=', rec.year)]
            if rec.plan_type == 'quarterly' and rec.quarter:
                domain.append(('report_period', '=', rec.quarter))
            rec.inventory_report_ids = report_model.search(domain)

    @api.depends('branch_id')
    def _compute_last_inventory_report_id(self):
        report_model = self.env['fm.inventory.report']
        for rec in self:
            rec.last_inventory_report_id = report_model.search([
                ('branch_id', '=', rec.branch_id.id),
                ('state', '=', 'archived'),
            ], order='report_year desc, report_period desc', limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fm.maintenance.plan') or _('New')
        return super().create(vals_list)

    # ── State transitions ──────────────────────────────────────────────

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft maintenance plans can be submitted.'))
            rec.write({'state': 'submitted'})
            if rec.facilities_manager_id:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Approve Preventive Maintenance Plan'),
                    user_id=rec.facilities_manager_id.id,
                )
            rec.message_post(body=_('Maintenance plan submitted for approval.'))
        return True

    def action_approve(self):
        if not self.env.user.has_group('nadf_facilities_management.group_fm_branch_facilities_manager'):
            raise UserError(_('Only the Branch Facilities Manager can approve a maintenance plan.'))
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted maintenance plans can be approved.'))
            rec.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approval_date': fields.Datetime.now(),
            })
            rec.message_post(body=_('Maintenance plan approved.'))
        return True

    def action_reject(self):
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted maintenance plans can be rejected.'))
            rec.write({'state': 'rejected'})
            rec.message_post(body=_('Maintenance plan rejected.'))
        return True

    def action_activate(self):
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_('Only approved maintenance plans can be activated.'))
            rec.write({'state': 'active'})
            rec.message_post(body=_('Maintenance plan activated.'))
        return True

    # DECISION: 'closed' is part of the state selection per spec but no
    # transition method was specified. action_close() is added so the
    # state is reachable once a plan's period has elapsed.
    def action_close(self):
        for rec in self:
            if rec.state != 'active':
                raise UserError(_('Only active maintenance plans can be closed.'))
            rec.write({'state': 'closed'})
            rec.message_post(body=_('Maintenance plan closed.'))
        return True


class FmPlanSparePartLine(models.Model):
    """Planned spare part line on a Preventive Maintenance Plan, used to
    budget materials ahead of scheduled work."""
    _name = 'fm.plan.spare.part.line'
    _description = 'Preventive Maintenance Plan Spare Part Line'

    plan_id = fields.Many2one(
        'fm.maintenance.plan', string='Plan', required=True, ondelete='cascade', index=True,
    )
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description')
    quantity_planned = fields.Float(string='Quantity Planned')
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', related='product_id.uom_id', store=True, readonly=True,
    )
    unit_cost = fields.Float(string='Unit Cost')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    # Phase 7 — 7.2.5: reference figure pulled from the branch's last
    # archived inventory report, to help the planner judge how much of this
    # product is likely already on hand / typically consumed.
    suggested_quantity = fields.Float(
        string='Suggested Qty (Last Inventory)', compute='_compute_suggested_quantity',
    )

    @api.depends('quantity_planned', 'unit_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity_planned * rec.unit_cost

    @api.depends('product_id', 'plan_id.last_inventory_report_id')
    def _compute_suggested_quantity(self):
        for rec in self:
            suggestion = 0.0
            report = rec.plan_id.last_inventory_report_id
            if report and rec.product_id:
                lines = report.line_ids.filtered(lambda l: l.product_id == rec.product_id)
                suggestion = sum(lines.mapped('closing_stock_calculated'))
            rec.suggested_quantity = suggestion

    @api.onchange('product_id')
    def _onchange_product_id_suggest_quantity(self):
        if self.product_id and not self.quantity_planned:
            report = self.plan_id.last_inventory_report_id
            if report:
                lines = report.line_ids.filtered(lambda l: l.product_id == self.product_id)
                if lines:
                    self.quantity_planned = sum(lines.mapped('closing_stock_calculated'))
