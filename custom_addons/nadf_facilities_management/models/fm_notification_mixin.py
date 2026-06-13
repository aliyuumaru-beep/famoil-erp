# Phase 6 — Shared notification helpers for Process 1-3 models
from odoo import models


class FmNotificationMixin(models.AbstractModel):
    """Helper methods shared by Facilities Management models for routing
    activities and emails to the right branch-level role.

    DECISION: there is no direct "desk officer of branch X" or "facilities
    manager of branch X" field anywhere in the data model — group
    membership (``res.groups.users``) combined with the user's
    ``hr.employee`` department is used as the best available proxy. If no
    user in the group belongs to the branch (e.g. minimal demo data), the
    notification falls back to every user in the group so nothing is
    silently dropped.
    """
    _name = 'fm.notification.mixin'
    _description = 'Facilities Management Notification Helpers'

    def _fm_branch_users(self, branch, group_xmlid):
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group or not branch:
            return self.env['res.users']
        users = group.users.filtered(
            lambda u: branch in u.employee_ids.department_id
        )
        return users or group.users

    def _fm_send_template(self, template_xmlid, res_id):
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if template:
            template.send_mail(res_id, force_send=False)
