# Phase 3 — Process 2: Preventive Maintenance (Schedule Execution)
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FmMaintenanceSchedule(models.Model):
    """Single piece-of-equipment maintenance entry under a Preventive
    Maintenance Plan (Process 2, step 2).

    State machine: scheduled -> assigned -> acknowledged -> in_progress
    -> completed -> signed_off, with remediation as a side branch from
    completed (rework requested before sign-off).

    Integration points:
    - ``plan_id``: parent ``fm.maintenance.plan``.
    - ``contractor_id``: contractor performing the work.
    - ``batch_id``: optional link to ``fm.monthly.batch`` once signed off,
      for inclusion in the monthly payment cycle.
    - A daily cron (``_cron_auto_assign_due_schedules``) automatically
      transitions 'scheduled' entries whose ``scheduled_date`` has arrived
      to 'assigned' and notifies the contractor via chatter.
    """
    _name = 'fm.maintenance.schedule'
    _description = 'Preventive Maintenance Schedule Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'fm.notification.mixin']
    _order = 'scheduled_date, id'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'),
    )
    plan_id = fields.Many2one(
        'fm.maintenance.plan', string='Maintenance Plan', required=True, ondelete='cascade', index=True,
    )
    equipment_name = fields.Char(string='Equipment', required=True)
    equipment_type = fields.Selection([
        ('generator', 'Generator Set'),
        ('hvac', 'HVAC Unit'),
        ('elevator', 'Elevator'),
        ('ups', 'UPS System'),
        ('other', 'Other'),
    ], string='Equipment Type')
    scheduled_date = fields.Date(string='Scheduled Date', required=True)
    contractor_id = fields.Many2one('fm.contractor', string='Contractor', required=True, tracking=True)
    assigned_date = fields.Datetime(string='Assigned Date', readonly=True, copy=False)
    acknowledgement_date = fields.Datetime(string='Acknowledgement Date', readonly=True, copy=False)
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('assigned', 'Assigned'),
        ('acknowledged', 'Acknowledged by Contractor'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed — Pending Sign-off'),
        ('signed_off', 'Signed Off'),
        ('remediation', 'Remediation Required'),
    ], string='Status', default='scheduled', tracking=True, copy=False)
    completion_report = fields.Text(string='Completion Report')
    completion_date = fields.Datetime(string='Completion Date', readonly=True, copy=False)
    sign_off_by = fields.Many2one('res.users', string='Signed Off By', readonly=True, copy=False)
    sign_off_date = fields.Datetime(string='Sign-off Date', readonly=True, copy=False)
    desk_officer_notes = fields.Text(string='Desk Officer Notes')
    batch_id = fields.Many2one('fm.monthly.batch', string='Payment Batch', copy=False)
    # Phase 7 — 7.2.4: materials drawn against this preventive maintenance
    # entry, mirroring the Job Order / Consumable Request link of Process 1.
    consumable_request_ids = fields.One2many(
        'fm.consumable.request', 'schedule_id', string='Consumable Requests',
    )
    consumable_request_count = fields.Integer(
        string='Consumable Request Count', compute='_compute_consumable_request_count',
    )

    @api.depends('consumable_request_ids')
    def _compute_consumable_request_count(self):
        for rec in self:
            rec.consumable_request_count = len(rec.consumable_request_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fm.maintenance.schedule') or _('New')
        return super().create(vals_list)

    # ── State transitions ──────────────────────────────────────────────

    def action_assign(self):
        for rec in self:
            if rec.state != 'scheduled':
                raise UserError(_('Only scheduled entries can be assigned to a contractor.'))
            rec.write({'state': 'assigned', 'assigned_date': fields.Datetime.now()})
            rec.message_post(
                body=_('Preventive maintenance assigned to contractor: %s') % rec.contractor_id.name,
            )
        return True

    def action_acknowledge(self):
        for rec in self:
            if rec.state != 'assigned':
                raise UserError(_('Only assigned entries can be acknowledged.'))
            rec.write({'state': 'acknowledged', 'acknowledgement_date': fields.Datetime.now()})
            rec.message_post(body=_('Assignment acknowledged by contractor.'))
        return True

    def action_start(self):
        for rec in self:
            if rec.state != 'acknowledged':
                raise UserError(_('Only acknowledged entries can be started.'))
            rec.write({'state': 'in_progress'})
        return True

    # DECISION: 'remediation' is a side branch back to rework. Allowing
    # action_submit_completion() from 'remediation' (in addition to
    # 'in_progress') lets the contractor resubmit after addressing
    # feedback, since no separate "resume" transition was specified.
    def action_submit_completion(self):
        for rec in self:
            if rec.state not in ('in_progress', 'remediation'):
                raise UserError(_('Only entries in progress or under remediation can have a completion report submitted.'))
            rec.write({'state': 'completed', 'completion_date': fields.Datetime.now()})
            rec.message_post(body=_('Completion report submitted — pending sign-off.'))
        return True

    def action_sign_off(self):
        for rec in self:
            if rec.state != 'completed':
                raise UserError(_('Only entries pending sign-off can be signed off.'))
            rec.write({
                'state': 'signed_off',
                'sign_off_by': self.env.user.id,
                'sign_off_date': fields.Datetime.now(),
            })
            rec.message_post(body=_('Maintenance schedule signed off.'))
        return True

    def action_request_remediation(self):
        for rec in self:
            if rec.state != 'completed':
                raise UserError(_('Remediation can only be requested for entries pending sign-off.'))
            rec.write({'state': 'remediation'})
            rec.message_post(body=_('Remediation requested — work does not meet sign-off standard.'))
        return True

    # Phase 7 — 7.2.3: optional "add to monthly batch" once signed off.
    def action_add_to_batch(self):
        for rec in self:
            if rec.state != 'signed_off':
                raise UserError(_('Only signed-off maintenance entries can be added to a monthly batch.'))
            if rec.batch_id:
                raise UserError(_('This maintenance entry is already part of a monthly batch.'))
            rec.batch_id = self.env['fm.monthly.batch']._find_or_create_for_branch(rec.plan_id.branch_id)
        return True

    def action_view_consumable_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Consumable Requests'),
            'res_model': 'fm.consumable.request',
            'view_mode': 'tree,form',
            'domain': [('schedule_id', '=', self.id)],
            'context': {'default_schedule_id': self.id},
        }

    # ── Cron ─────────────────────────────────────────────────────────────

    @api.model
    def _cron_auto_assign_due_schedules(self):
        """Daily cron: auto-assign 'scheduled' entries whose scheduled_date
        has arrived, and notify the assigned contractor and desk officer
        by email (Phase 6)."""
        today = fields.Date.context_today(self)
        due = self.search([
            ('state', '=', 'scheduled'),
            ('scheduled_date', '<=', today),
        ])
        due.action_assign()
        template = self.env.ref(
            'nadf_facilities_management.mail_template_fm_schedule_due', raise_if_not_found=False,
        )
        if not template:
            return
        for rec in due:
            template.send_mail(rec.id, force_send=False)
            desk_officers = rec._fm_branch_users(
                rec.plan_id.branch_id, 'nadf_facilities_management.group_fm_branch_desk_officer',
            )
            for user in desk_officers:
                if user.email:
                    template.send_mail(rec.id, force_send=False, email_values={'email_to': user.email})
