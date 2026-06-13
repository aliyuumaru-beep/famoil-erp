# Phase 2 — Process 1: Reactive Maintenance (Job Order & Monthly Batch)
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FmJobOrder(models.Model):
    """Work order issued to a contractor to resolve a job complaint
    (Process 1, step 2) or to record ad-hoc reactive work.

    State machine: draft -> assigned -> in_progress -> pending_feedback
    -> closed, with reopen (-> in_progress) on negative feedback and
    escalated as a side branch from assigned/in_progress.

    Integration points:
    - ``complaint_id``: on creation, marks the source complaint 'assigned'.
    - ``action_close``: marks the source complaint 'closed'.
    - ``consumable_request_ids``: materials drawn from the contractor.
    - ``batch_id``: groups closed job orders for the monthly HQ payment cycle.
    """
    _name = 'fm.job.order'
    _description = 'Facilities Management Job Order'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'fm.notification.mixin']
    _order = 'order_date desc, id desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'),
    )
    order_date = fields.Datetime(string='Order Date', default=fields.Datetime.now)
    branch_id = fields.Many2one('hr.department', string='Branch', required=True, tracking=True)
    desk_officer_id = fields.Many2one(
        'res.users', string='Desk Officer', required=True,
        default=lambda self: self.env.user,
    )
    complaint_id = fields.Many2one(
        'fm.job.complaint', string='Source Complaint', copy=False,
    )
    contractor_id = fields.Many2one('fm.contractor', string='Contractor', required=True, tracking=True)
    job_description = fields.Text(string='Job Description', required=True)
    assessment_notes = fields.Text(string='Contractor Assessment Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned to Contractor'),
        ('in_progress', 'In Progress'),
        ('pending_feedback', 'Pending User Feedback'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated to HQ'),
    ], string='Status', default='draft', tracking=True, copy=False)
    consumable_request_ids = fields.One2many(
        'fm.consumable.request', 'job_order_id', string='Consumable Requests',
    )
    completion_report = fields.Text(string='Job Completion Report')
    completion_date = fields.Datetime(string='Completion Date')
    satisfaction_state = fields.Selection([
        ('pending', 'Pending'),
        ('satisfied', 'Satisfied'),
        ('unsatisfied', 'Not Satisfied'),
    ], string='Satisfaction', default='pending', tracking=True, copy=False)
    satisfaction_notes = fields.Text(string='Satisfaction Notes')
    batch_id = fields.Many2one(
        'fm.monthly.batch', string='Monthly Submission Batch', copy=False,
    )
    # DECISION: total_cost is not in the original field list, but
    # fm.monthly.batch.total_amount is specified as "compute from job
    # orders" with no other cost source defined — it is derived here from
    # approved consumable request lines (the only costed records on a
    # job order) and rolled up on the batch.
    total_cost = fields.Float(
        string='Total Consumables Cost', compute='_compute_total_cost', store=True,
    )
    # DECISION: not in the original field list — added to back the
    # "Consumable Requests" smart button required on the Job Order form
    # (Phase 5 UI spec).
    consumable_request_count = fields.Integer(
        string='Consumable Request Count', compute='_compute_consumable_request_count',
    )

    @api.depends('consumable_request_ids.line_ids.total_cost', 'consumable_request_ids.state')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = sum(
                line.total_cost
                for request in rec.consumable_request_ids.filtered(lambda r: r.state == 'approved')
                for line in request.line_ids
            )

    @api.depends('consumable_request_ids')
    def _compute_consumable_request_count(self):
        for rec in self:
            rec.consumable_request_count = len(rec.consumable_request_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fm.job.order') or _('New')
        records = super().create(vals_list)
        for rec in records:
            if rec.complaint_id and rec.complaint_id.state == 'draft':
                rec.complaint_id.write({'job_order_id': rec.id})
                rec.complaint_id.action_set_assigned()
        return records

    # ── State transitions ──────────────────────────────────────────────

    def action_assign(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft job orders can be assigned to a contractor.'))
            rec.write({'state': 'assigned'})
            rec.message_post(
                body=_('Job order assigned to contractor: %s') % rec.contractor_id.name,
            )
            # Phase 6 — notify the contractor by email of the new assignment.
            rec._fm_send_template(
                'nadf_facilities_management.mail_template_fm_job_order_assigned', rec.id,
            )
        return True

    def action_start(self):
        for rec in self:
            if rec.state != 'assigned':
                raise UserError(_('Only job orders assigned to a contractor can be started.'))
            rec.write({'state': 'in_progress'})
        return True

    def action_submit_completion(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_('Only job orders in progress can have a completion report submitted.'))
            rec.write({
                'state': 'pending_feedback',
                'completion_date': fields.Datetime.now(),
            })
            rec.message_post(body=_('Completion report submitted — awaiting end-user feedback.'))
            # Phase 6 — notify the Branch Desk Officer that a completion
            # report is awaiting end-user feedback / review.
            desk_officers = rec._fm_branch_users(
                rec.branch_id, 'nadf_facilities_management.group_fm_branch_desk_officer',
            )
            for user in desk_officers:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Job Order Completion Report Submitted'),
                    note=_('Job order %s has a completion report awaiting review.') % rec.name,
                    user_id=user.id,
                )
        return True

    def action_open_feedback_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Satisfaction Feedback'),
            'res_model': 'fm.satisfaction.feedback.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_job_order_id': self.id},
        }

    def action_view_consumable_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Consumable Requests'),
            'res_model': 'fm.consumable.request',
            'view_mode': 'tree,form',
            'domain': [('job_order_id', '=', self.id)],
            'context': {'default_job_order_id': self.id},
        }

    def action_view_batch(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Monthly Batch'),
            'res_model': 'fm.monthly.batch',
            'view_mode': 'form',
            'res_id': self.batch_id.id,
        }

    # Phase 7 — 7.2.3: optional "add to monthly batch" once closed.
    def action_add_to_batch(self):
        for rec in self:
            if rec.state != 'closed':
                raise UserError(_('Only closed job orders can be added to a monthly batch.'))
            if rec.batch_id:
                raise UserError(_('This job order is already part of a monthly batch.'))
            rec.batch_id = self.env['fm.monthly.batch']._find_or_create_for_branch(rec.branch_id)
        return True

    def action_close(self):
        for rec in self:
            if rec.state == 'closed':
                continue
            rec.write({'state': 'closed'})
            if rec.complaint_id:
                rec.complaint_id.action_set_closed()
            rec.message_post(body=_('Job order closed.'))
        return True

    def action_reopen(self):
        for rec in self:
            rec.write({'state': 'in_progress', 'satisfaction_state': 'pending'})
            rec.message_post(body=_('Job order reopened — end user reported dissatisfaction.'))
        return True

    # DECISION: 'escalated' is part of the state selection per spec but no
    # transition method was specified. action_escalate() is added so the
    # state is reachable, restricted to non-terminal states.
    def action_escalate(self):
        for rec in self:
            if rec.state in ('closed', 'escalated'):
                raise UserError(_('Closed or already-escalated job orders cannot be escalated.'))
            rec.write({'state': 'escalated'})
            rec.message_post(body=_('Job order escalated to HQ.'))
        return True


class FmMonthlyBatch(models.Model):
    """Monthly compilation of closed Job Orders submitted for HQ approval
    and Finance payment (Process 1, step 3).

    State machine: draft -> submitted_hq -> cost_control ->
    director_approval -> finance -> paid, with hq_review (returned by Cost
    Control) and returned_branch (returned by HQ) as correction loops.

    Integration points:
    - ``job_order_ids``: closed Process 1 Job Orders added via
      ``fm.job.order.action_add_to_batch``.
    - ``schedule_ids``: signed-off Process 2 Maintenance Schedule entries
      added via ``fm.maintenance.schedule.action_add_to_batch``.
    - HQ/Cost Control/Director/Finance record-rule scoping (Phase 7) is
      keyed off this model's ``branch_id`` and ``state``.
    """
    _name = 'fm.monthly.batch'
    _description = 'Monthly Job Order Compilation Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'fm.notification.mixin']
    _order = 'period_year desc, period_month desc, id desc'

    name = fields.Char(string='Batch Reference', required=True, tracking=True)
    branch_id = fields.Many2one('hr.department', string='Branch', required=True)
    period_month = fields.Integer(string='Period Month', required=True)
    period_year = fields.Integer(string='Period Year', required=True)
    job_order_ids = fields.One2many('fm.job.order', 'batch_id', string='Job Orders')
    # Phase 7 — 7.2.3: signed-off preventive maintenance entries can also be
    # added to a monthly batch via fm.maintenance.schedule.action_add_to_batch.
    schedule_ids = fields.One2many(
        'fm.maintenance.schedule', 'batch_id', string='Maintenance Schedule Entries',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted_hq', 'Submitted to HQ'),
        ('hq_review', 'Under HQ Review'),
        ('returned_branch', 'Returned for Correction'),
        ('cost_control', 'With Cost Control'),
        ('director_approval', 'Awaiting Director Approval'),
        ('finance', 'With Finance'),
        ('paid', 'Payment Processed'),
    ], string='Status', default='draft', tracking=True, copy=False)
    hq_officer_id = fields.Many2one('res.users', string='HQ Procurement Officer')
    hq_notes = fields.Text(string='HQ Notes')
    cost_control_notes = fields.Text(string='Cost Control Notes')
    director_notes = fields.Text(string='Director Notes')
    finance_notes = fields.Text(string='Finance Notes')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)

    @api.depends('job_order_ids.total_cost')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.job_order_ids.mapped('total_cost'))

    # Phase 7 — 7.2.3: shared helper used by Job Order / Maintenance
    # Schedule "add to batch" actions to find (or open) the current draft
    # monthly batch for a branch, keyed on today's period.
    def _find_or_create_for_branch(self, branch):
        today = fields.Date.context_today(self)
        batch = self.search([
            ('branch_id', '=', branch.id),
            ('period_month', '=', today.month),
            ('period_year', '=', today.year),
            ('state', '=', 'draft'),
        ], limit=1)
        if not batch:
            batch = self.create({
                'name': _('%(branch)s - %(month)s/%(year)s') % {
                    'branch': branch.name, 'month': today.month, 'year': today.year,
                },
                'branch_id': branch.id,
                'period_month': today.month,
                'period_year': today.year,
            })
        return batch

    # ── Reporting helpers (Phase 6) ─────────────────────────────────────

    # DECISION: fm.job.order has no "job type" field. The Monthly Batch
    # Summary Report's "totals by job type" requirement is met using the
    # source complaint's complaint_type (Electrical/Plumbing/etc.), with
    # job orders that have no source complaint grouped as "Ad-hoc".
    def _get_contractor_totals(self):
        self.ensure_one()
        totals = {}
        for jo in self.job_order_ids:
            totals.setdefault(jo.contractor_id, 0.0)
            totals[jo.contractor_id] += jo.total_cost
        return [{'name': contractor.name, 'total': total} for contractor, total in totals.items()]

    def _get_job_type_totals(self):
        self.ensure_one()
        type_labels = dict(self.env['fm.job.complaint']._fields['complaint_type'].selection)
        totals = {}
        for jo in self.job_order_ids:
            if jo.complaint_id:
                label = type_labels.get(jo.complaint_id.complaint_type, jo.complaint_id.complaint_type)
            else:
                label = _('Ad-hoc')
            totals.setdefault(label, 0.0)
            totals[label] += jo.total_cost
        return [{'name': name, 'total': total} for name, total in totals.items()]

    # ── Notification helpers (Phase 6) ──────────────────────────────────

    def _get_hq_officer_emails(self):
        self.ensure_one()
        users = self.hq_officer_id
        group = self.env.ref(
            'nadf_facilities_management.group_fm_hq_procurement_officer', raise_if_not_found=False,
        )
        if group:
            users |= group.users
        return ','.join(filter(None, users.mapped('email')))

    def _get_desk_officer_emails(self):
        self.ensure_one()
        users = self._fm_branch_users(
            self.branch_id, 'nadf_facilities_management.group_fm_branch_desk_officer',
        )
        return ','.join(filter(None, users.mapped('email')))

    # ── State transitions ──────────────────────────────────────────────

    def action_submit_to_hq(self):
        for rec in self:
            rec.write({'state': 'submitted_hq'})
            rec.message_post(body=_('Monthly batch submitted to HQ Procurement.'))
            # Phase 6 — notify HQ Procurement (email + activity).
            rec._fm_send_template(
                'nadf_facilities_management.mail_template_fm_monthly_batch_submitted', rec.id,
            )
            group = rec.env.ref(
                'nadf_facilities_management.group_fm_hq_procurement_officer', raise_if_not_found=False,
            )
            hq_users = rec.hq_officer_id | (group.users if group else rec.env['res.users'])
            for user in hq_users:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Review Monthly Batch'),
                    note=_('Monthly batch %s from branch %s is awaiting HQ review.') % (
                        rec.name, rec.branch_id.name,
                    ),
                    user_id=user.id,
                )
        return True

    def action_hq_approve(self):
        for rec in self:
            rec.write({'state': 'cost_control'})
            rec.message_post(body=_('Monthly batch approved by HQ — forwarded to Cost Control.'))
        return True

    def action_hq_return(self):
        for rec in self:
            rec.write({'state': 'returned_branch'})
            rec.message_post(body=_('Monthly batch returned to branch for correction.'))
            # Phase 6 — notify the Branch Desk Officer by email.
            rec._fm_send_template(
                'nadf_facilities_management.mail_template_fm_monthly_batch_returned', rec.id,
            )
        return True

    def action_cost_control_approve(self):
        for rec in self:
            rec.write({'state': 'director_approval'})
            rec.message_post(body=_('Monthly batch approved by Cost Control — awaiting Director approval.'))
        return True

    def action_cost_control_query(self):
        for rec in self:
            rec.write({'state': 'hq_review'})
            rec.message_post(body=_('Monthly batch queried by Cost Control — returned to HQ for resolution.'))
        return True

    def action_director_approve(self):
        for rec in self:
            rec.write({'state': 'finance'})
            rec.message_post(body=_('Monthly batch approved by the Director — forwarded to Finance.'))
        return True

    def action_finance_pay(self):
        for rec in self:
            rec.write({'state': 'paid'})
            rec.message_post(body=_('Monthly batch payment processed by Finance.'))
        return True

    def action_finance_return(self):
        for rec in self:
            rec.write({'state': 'director_approval'})
            rec.message_post(body=_('Monthly batch returned by Finance to the Director.'))
        return True
