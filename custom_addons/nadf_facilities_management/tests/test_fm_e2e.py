# Phase 7 — 7.3: End-to-end tests covering Process 1 (Reactive Maintenance),
# Process 2 (Preventive Maintenance) and Process 3 (Inventory Visibility &
# Quarterly Reporting), exercised through the actual role-based users via
# `.with_user(...)` so that ACLs and record rules are genuinely enforced.
import datetime

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestFmEndToEnd(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Department = cls.env['hr.department']
        Product = cls.env['product.product']
        Users = cls.env['res.users']
        Employee = cls.env['hr.employee']
        Contractor = cls.env['fm.contractor']

        cls.branch_a = Department.create({'name': 'E2E Branch A'})
        cls.branch_b = Department.create({'name': 'E2E Branch B'})

        cls.product = Product.search([('type', 'in', ('consu', 'product'))], limit=1)

        cls.group_end_user = cls.env.ref('nadf_facilities_management.group_fm_end_user')
        cls.group_desk_officer = cls.env.ref('nadf_facilities_management.group_fm_branch_desk_officer')
        cls.group_facilities_manager = cls.env.ref('nadf_facilities_management.group_fm_branch_facilities_manager')
        cls.group_contractor = cls.env.ref('nadf_facilities_management.group_fm_tff_contractor')
        cls.group_hq_procurement = cls.env.ref('nadf_facilities_management.group_fm_hq_procurement_officer')
        cls.group_cost_control = cls.env.ref('nadf_facilities_management.group_fm_cost_control')
        cls.group_director = cls.env.ref('nadf_facilities_management.group_fm_director')
        cls.group_finance = cls.env.ref('nadf_facilities_management.group_fm_finance')
        cls.group_base_user = cls.env.ref('base.group_user')

        counter = {'n': 0}

        def _make_user(name, login, groups):
            counter['n'] += 1
            return Users.create({
                'name': name,
                'login': '%s.%s' % (login, counter['n']),
                'email': '%s.%s@example.com' % (login, counter['n']),
                'groups_id': [(6, 0, [g.id for g in groups] + [cls.group_base_user.id])],
            })

        cls.end_user = _make_user('E2E End User', 'e2e_end_user', [cls.group_end_user])
        cls.desk_officer_a = _make_user('E2E Desk Officer A', 'e2e_desk_a', [cls.group_desk_officer])
        cls.fm_manager_a = _make_user('E2E Facilities Manager A', 'e2e_fm_a', [cls.group_facilities_manager])
        cls.desk_officer_b = _make_user('E2E Desk Officer B', 'e2e_desk_b', [cls.group_desk_officer])
        cls.hq_officer = _make_user('E2E HQ Officer', 'e2e_hq', [cls.group_hq_procurement])
        cls.cost_control_officer = _make_user('E2E Cost Control', 'e2e_cc', [cls.group_cost_control])
        cls.director = _make_user('E2E Director', 'e2e_director', [cls.group_director])
        cls.finance_officer = _make_user('E2E Finance', 'e2e_finance', [cls.group_finance])
        cls.contractor_user = _make_user('E2E Contractor User', 'e2e_contractor', [cls.group_contractor])

        Employee.create({
            'name': 'E2E End User', 'department_id': cls.branch_a.id, 'user_id': cls.end_user.id,
        })
        Employee.create({
            'name': 'E2E Desk Officer A', 'department_id': cls.branch_a.id, 'user_id': cls.desk_officer_a.id,
        })
        Employee.create({
            'name': 'E2E Facilities Manager A', 'department_id': cls.branch_a.id, 'user_id': cls.fm_manager_a.id,
        })
        Employee.create({
            'name': 'E2E Desk Officer B', 'department_id': cls.branch_b.id, 'user_id': cls.desk_officer_b.id,
        })

        partner = cls.env['res.partner'].create({'name': 'E2E Contractor Partner'})
        cls.contractor = Contractor.create({
            'name': 'E2E Contractor',
            'contractor_type': 'tff',
            'partner_id': partner.id,
            'branch_id': cls.branch_a.id,
            'user_ids': [(4, cls.contractor_user.id)],
        })

    def test_01_process1_reactive_maintenance_cycle(self):
        Complaint = self.env['fm.job.complaint']
        JobOrder = self.env['fm.job.order']
        ConsumableRequest = self.env['fm.consumable.request']
        Batch = self.env['fm.monthly.batch']

        # 1. End user raises a complaint.
        complaint = Complaint.with_user(self.end_user).create({
            'branch_id': self.branch_a.id,
            'complaint_type': 'electrical',
            'description': 'E2E: socket not working',
            'end_user_id': self.end_user.id,
        })
        self.assertEqual(complaint.state, 'draft')

        # 2. Desk officer A assigns the complaint -> creates a job order.
        complaint.with_user(self.desk_officer_a).action_set_assigned()
        self.assertEqual(complaint.state, 'assigned')

        job_order = JobOrder.with_user(self.desk_officer_a).create({
            'branch_id': self.branch_a.id,
            'complaint_id': complaint.id,
            'contractor_id': self.contractor.id,
            'job_description': 'E2E: replace faulty socket',
        })

        # Record-rule isolation: desk officer B (branch B) cannot see this complaint/order.
        self.assertFalse(
            Complaint.with_user(self.desk_officer_b).search([('id', '=', complaint.id)]),
        )
        self.assertFalse(
            JobOrder.with_user(self.desk_officer_b).search([('id', '=', job_order.id)]),
        )

        # 3. Desk officer assigns and starts the job order.
        job_order.with_user(self.desk_officer_a).action_assign()
        job_order.with_user(self.desk_officer_a).action_start()
        self.assertEqual(job_order.state, 'in_progress')

        # 4. Contractor raises a consumable request against the job order.
        consumable_request = ConsumableRequest.with_user(self.contractor_user).create({
            'job_order_id': job_order.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'description': 'E2E: replacement socket',
                'quantity_requested': 2,
                'unit_cost': 500,
            })],
        })
        consumable_request.with_user(self.contractor_user).action_submit()
        self.assertEqual(consumable_request.state, 'submitted')

        # 5. Desk officer approves the consumable request, sets approved qty.
        consumable_request.with_user(self.desk_officer_a).line_ids.write({'quantity_approved': 2})
        consumable_request.with_user(self.desk_officer_a).action_approve()
        self.assertEqual(consumable_request.state, 'approved')

        # 6. Contractor submits the completion report.
        job_order.with_user(self.contractor_user).write({'completion_report': 'E2E: socket replaced and tested.'})
        job_order.with_user(self.contractor_user).action_submit_completion()
        self.assertEqual(job_order.state, 'pending_feedback')

        # 7. End user gives satisfaction feedback -> job order closes.
        feedback_wizard = self.env['fm.satisfaction.feedback.wizard'].with_user(self.end_user).create({
            'job_order_id': job_order.id,
            'satisfaction': 'satisfied',
        })
        feedback_wizard.with_user(self.end_user).action_submit_feedback()
        self.assertEqual(job_order.state, 'closed')

        # 8. Desk officer adds the closed job order to a monthly batch.
        job_order.with_user(self.desk_officer_a).action_add_to_batch()
        self.assertTrue(job_order.batch_id)
        batch = job_order.batch_id

        # Re-running add_to_batch must raise (already batched).
        with self.assertRaises(Exception):
            job_order.with_user(self.desk_officer_a).action_add_to_batch()

        # HQ tier only sees job orders once batch-linked.
        visible_hq = JobOrder.with_user(self.hq_officer).search([('id', '=', job_order.id)])
        self.assertEqual(visible_hq.ids, [job_order.id])

        # 9. Monthly batch progresses through its full approval chain to 'paid'.
        batch.with_user(self.desk_officer_a).action_submit_to_hq()
        self.assertEqual(batch.state, 'submitted_hq')

        batch.with_user(self.hq_officer).action_hq_approve()
        self.assertEqual(batch.state, 'cost_control')

        batch.with_user(self.cost_control_officer).action_cost_control_approve()
        self.assertEqual(batch.state, 'director_approval')

        batch.with_user(self.director).action_director_approve()
        self.assertEqual(batch.state, 'finance')

        batch.with_user(self.finance_officer).action_finance_pay()
        self.assertEqual(batch.state, 'paid')

    def test_02_process2_preventive_maintenance_cycle(self):
        Plan = self.env['fm.maintenance.plan']
        Schedule = self.env['fm.maintenance.schedule']
        ConsumableRequest = self.env['fm.consumable.request']

        # 1. Desk officer drafts a maintenance plan for branch A.
        plan = Plan.with_user(self.desk_officer_a).create({
            'plan_type': 'quarterly',
            'year': 2026,
            'quarter': 'Q2',
            'branch_id': self.branch_a.id,
            'desk_officer_id': self.desk_officer_a.id,
            'facilities_manager_id': self.fm_manager_a.id,
        })
        self.assertEqual(plan.state, 'draft')

        # 2. Submit for approval, facilities manager approves, desk officer activates.
        plan.with_user(self.desk_officer_a).action_submit()
        self.assertEqual(plan.state, 'submitted')

        plan.with_user(self.fm_manager_a).action_approve()
        self.assertEqual(plan.state, 'approved')

        plan.with_user(self.desk_officer_a).action_activate()
        self.assertEqual(plan.state, 'active')

        # 3. Desk officer creates a schedule entry, assigns the contractor.
        schedule = Schedule.with_user(self.desk_officer_a).create({
            'plan_id': plan.id,
            'equipment_name': 'E2E Generator',
            'equipment_type': 'generator',
            'scheduled_date': datetime.date.today(),
            'contractor_id': self.contractor.id,
        })
        schedule.with_user(self.desk_officer_a).action_assign()
        self.assertEqual(schedule.state, 'assigned')

        # 4. Contractor acknowledges, starts, and submits completion.
        schedule.with_user(self.contractor_user).action_acknowledge()
        self.assertEqual(schedule.state, 'acknowledged')

        schedule.with_user(self.contractor_user).action_start()
        self.assertEqual(schedule.state, 'in_progress')

        schedule.with_user(self.contractor_user).write({'completion_report': 'E2E: generator serviced.'})
        schedule.with_user(self.contractor_user).action_submit_completion()
        self.assertEqual(schedule.state, 'completed')

        # 5. Desk officer signs off the work.
        schedule.with_user(self.desk_officer_a).action_sign_off()
        self.assertEqual(schedule.state, 'signed_off')

        # 6. Contractor raises a consumable request against the schedule (not a job order).
        consumable_request = ConsumableRequest.with_user(self.contractor_user).create({
            'schedule_id': schedule.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'description': 'E2E: oil filter',
                'quantity_requested': 1,
                'unit_cost': 1000,
            })],
        })
        self.assertEqual(consumable_request.contractor_id, self.contractor)
        self.assertEqual(consumable_request.branch_id, self.branch_a)

        # 7. Desk officer adds the signed-off schedule entry to a monthly batch.
        schedule.with_user(self.desk_officer_a).action_add_to_batch()
        self.assertTrue(schedule.batch_id)

        # Idempotency: already-batched schedule entry raises on retry.
        with self.assertRaises(Exception):
            schedule.with_user(self.desk_officer_a).action_add_to_batch()

        # 8. Desk officer closes the plan.
        plan.with_user(self.desk_officer_a).action_close()
        self.assertEqual(plan.state, 'closed')

    def test_03_process3_inventory_reporting_and_suggested_quantity(self):
        JobOrder = self.env['fm.job.order']
        ConsumableRequest = self.env['fm.consumable.request']
        InvReport = self.env['fm.inventory.report']
        Plan = self.env['fm.maintenance.plan']
        Complaint = self.env['fm.job.complaint']

        # Build up some contractor inventory via an approved consumable
        # request on an ad-hoc job order (so fm.contractor.inventory.line
        # has a row to report against).
        complaint = Complaint.with_user(self.desk_officer_a).create({
            'branch_id': self.branch_a.id,
            'complaint_type': 'plumbing',
            'description': 'E2E: leaking pipe for inventory setup',
        })
        job_order = JobOrder.with_user(self.desk_officer_a).create({
            'branch_id': self.branch_a.id,
            'complaint_id': complaint.id,
            'contractor_id': self.contractor.id,
            'job_description': 'E2E: fix leaking pipe',
        })
        consumable_request = ConsumableRequest.with_user(self.contractor_user).create({
            'job_order_id': job_order.id,
            'line_ids': [(0, 0, {
                'product_id': self.product.id,
                'description': 'E2E: pipe fitting',
                'quantity_requested': 10,
                'unit_cost': 200,
            })],
        })
        consumable_request.with_user(self.contractor_user).action_submit()
        consumable_request.with_user(self.desk_officer_a).line_ids.write({'quantity_approved': 10})
        consumable_request.with_user(self.desk_officer_a).action_approve()
        self.assertEqual(consumable_request.state, 'approved')

        # 1. Desk officer creates a quarterly inventory report and populates lines.
        inv_report = InvReport.with_user(self.desk_officer_a).create({
            'branch_id': self.branch_a.id,
            'report_period': 'Q1',
            'report_year': 2026,
            'contractor_ids': [(4, self.contractor.id)],
        })
        inv_report.with_user(self.desk_officer_a).action_populate_lines()
        self.assertTrue(inv_report.line_ids)

        # Introduce a discrepancy on the first line so the workflow's
        # discrepancy-handling activity gets exercised.
        line = inv_report.line_ids[0]
        line.with_user(self.desk_officer_a).write({
            'closing_stock_reported': line.closing_stock_calculated + 5,
        })
        self.assertTrue(line.discrepancy)

        # 2. Drive the inventory report through its full state machine.
        inv_report.with_user(self.desk_officer_a).action_submit()
        self.assertEqual(inv_report.state, 'submitted')

        inv_report.with_user(self.fm_manager_a).action_approve()
        self.assertEqual(inv_report.state, 'approved')

        inv_report.with_user(self.hq_officer).action_hq_acknowledge()
        self.assertEqual(inv_report.state, 'hq_acknowledged')

        inv_report.with_user(self.hq_officer).action_forward_cost_control()
        self.assertEqual(inv_report.state, 'cost_control')

        inv_report.with_user(self.cost_control_officer).action_archive_report()
        self.assertEqual(inv_report.state, 'archived')

        # 3. A new maintenance plan for the same branch should pick up this
        # archived report as its "last inventory report", and a spare part
        # line's suggested quantity should match the reported closing stock.
        plan2 = Plan.with_user(self.desk_officer_a).create({
            'plan_type': 'quarterly',
            'year': 2026,
            'quarter': 'Q2',
            'branch_id': self.branch_a.id,
            'desk_officer_id': self.desk_officer_a.id,
            'facilities_manager_id': self.fm_manager_a.id,
        })
        self.assertEqual(plan2.last_inventory_report_id, inv_report)

        spare_line = self.env['fm.plan.spare.part.line'].with_user(self.desk_officer_a).create({
            'plan_id': plan2.id,
            'product_id': self.product.id,
            'description': 'E2E: spare for suggested qty check',
        })
        self.assertEqual(spare_line.suggested_quantity, line.closing_stock_calculated)

        # 4. Record-rule scoping: contractor sees the inventory report that
        # covers their own contractor record.
        visible_to_contractor = InvReport.with_user(self.contractor_user).search([('id', '=', inv_report.id)])
        self.assertEqual(visible_to_contractor.ids, [inv_report.id])

        # HQ tier has no inventory-report-specific rule -> unrestricted access.
        visible_to_hq = InvReport.with_user(self.hq_officer).search([('id', '=', inv_report.id)])
        self.assertEqual(visible_to_hq.ids, [inv_report.id])
