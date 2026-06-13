# Phase 2 — Process 1: Reactive Maintenance (Job Complaint)
from odoo import models, fields, api, _


class FmJobComplaint(models.Model):
    """End-user maintenance complaint (Process 1, step 1).

    Business purpose: entry point for the reactive maintenance workflow.
    An End User (any internal staff member) logs a fault; the Branch Desk
    Officer triages it into a ``fm.job.order``.

    State machine: draft (Submitted) -> assigned (Assigned to Job Order)
    -> closed (Closed). The transition draft -> assigned happens when a
    Job Order is created referencing this complaint; assigned -> closed
    happens when that Job Order is closed.

    Integration points: ``job_order_id`` is set by ``fm.job.order.create``.
    """
    _name = 'fm.job.complaint'
    _description = 'Facilities Management Job Complaint'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'fm.notification.mixin']
    _order = 'complaint_date desc, id desc'
    # Phase 7 — 7.3: End Users only have read+create ACL on this model (no
    # write), but create() schedules a "new complaint" activity for the
    # Branch Desk Officer. mail.activity creation for operation 'create'
    # falls back to a 'write' check on the related document unless
    # _mail_post_access is relaxed to 'read', which End Users do have.
    _mail_post_access = 'read'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'),
    )
    complaint_date = fields.Datetime(
        string='Complaint Date', default=fields.Datetime.now, required=True,
    )
    end_user_id = fields.Many2one(
        'res.users', string='End User', required=True,
        default=lambda self: self.env.user,
    )
    branch_id = fields.Many2one('hr.department', string='Branch', required=True, tracking=True)
    location_detail = fields.Char(string='Location / Room')
    complaint_type = fields.Selection([
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('mechanical', 'Mechanical'),
        ('hvac', 'HVAC'),
        ('civil', 'Civil Works'),
        ('other', 'Other'),
    ], string='Complaint Type', required=True)
    description = fields.Text(string='Description', required=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Critical'),
    ], string='Priority', default='0')
    state = fields.Selection([
        ('draft', 'Submitted'),
        ('assigned', 'Assigned to Job Order'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', tracking=True, copy=False)
    job_order_id = fields.Many2one(
        'fm.job.order', string='Job Order', readonly=True, copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fm.job.complaint') or _('New')
        records = super().create(vals_list)
        # Phase 6 — notify the Branch Desk Officer of new complaints.
        for rec in records:
            desk_officers = rec._fm_branch_users(
                rec.branch_id, 'nadf_facilities_management.group_fm_branch_desk_officer',
            )
            for user in desk_officers:
                # Phase 7 — 7.3: an End User (create+read only, no write ACL
                # on this model) raises this complaint, but activity
                # creation also subscribes the assignee via
                # message_subscribe(), which requires write access. sudo()
                # this system-triggered notification since it is not a
                # permission the End User needs to exercise themselves.
                rec.sudo().activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('New Job Complaint Logged'),
                    note=_('A new job complaint %(ref)s has been submitted for branch %(branch)s.') % {
                        'ref': rec.name, 'branch': rec.branch_id.name,
                    },
                    user_id=user.id,
                )
        return records

    def action_set_assigned(self):
        """Called by fm.job.order when a Job Order is created for this complaint."""
        self.write({'state': 'assigned'})

    def action_set_closed(self):
        """Called by fm.job.order when the linked Job Order is closed."""
        self.write({'state': 'closed'})
