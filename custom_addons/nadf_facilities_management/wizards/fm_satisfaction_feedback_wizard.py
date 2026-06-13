# Phase 2 — Process 1: Reactive Maintenance (End-User Satisfaction Feedback)
from odoo import models, fields, _


class FmSatisfactionFeedbackWizard(models.TransientModel):
    """Lightweight wizard used by the End User to close the loop on a
    Job Order: confirm satisfaction (closes the job order and the source
    complaint) or report dissatisfaction (reopens the job order)."""
    _name = 'fm.satisfaction.feedback.wizard'
    _description = 'End User Satisfaction Feedback'

    job_order_id = fields.Many2one('fm.job.order', string='Job Order', required=True)
    end_user_id = fields.Many2one(
        'res.users', string='End User', required=True,
        default=lambda self: self.env.user,
    )
    satisfaction = fields.Selection([
        ('satisfied', 'Satisfied'),
        ('unsatisfied', 'Not Satisfied'),
    ], string='Satisfaction', required=True)
    feedback_notes = fields.Text(string='Feedback Notes')

    def action_submit_feedback(self):
        self.ensure_one()
        # DECISION: End Users have read-only access to fm.job.order (per the
        # Phase 1 access matrix), but this wizard is the sanctioned way for
        # them to close the loop on their own job order. The state/feedback
        # write below is performed via sudo() since the wizard itself
        # already restricts what can change and to which job order.
        job_order = self.job_order_id.sudo()
        job_order.write({
            'satisfaction_state': self.satisfaction,
            'satisfaction_notes': self.feedback_notes,
        })
        if self.satisfaction == 'satisfied':
            job_order.action_close()
        else:
            if self.feedback_notes:
                job_order.message_post(
                    body=_('End user reported dissatisfaction: %s') % self.feedback_notes,
                )
            # Phase 6 — notify the contractor via a chatter note on their
            # own record (in addition to the note on the job order above).
            if job_order.contractor_id:
                job_order.contractor_id.sudo().message_post(
                    body=_('End user reported dissatisfaction with job order %(ref)s: %(notes)s') % {
                        'ref': job_order.name,
                        'notes': self.feedback_notes or _('(no notes provided)'),
                    },
                )
            job_order.action_reopen()
        return {'type': 'ir.actions.act_window_close'}
