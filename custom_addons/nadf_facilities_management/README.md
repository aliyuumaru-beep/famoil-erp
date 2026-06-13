# NADF Facilities Management

Odoo 17 Community module implementing the NADF Facilities Management
Department's three core workflows: Reactive Maintenance, Preventive
Maintenance, and Quarterly Inventory Reporting.

## 1. Module Purpose & Scope

This module digitises the end-to-end lifecycle of facilities maintenance
across NADF branches, from the moment a staff member raises a fault report
through to Finance payment of the contractor, and gives HQ ongoing
visibility of contractor-held consumable stock via quarterly reconciliation.

It covers three integrated business processes:

- **Process 1 — Reactive Maintenance**: Job Complaint → Job Order → Repair
  (contractor execution + consumable usage) → end-user sign-off → Monthly
  Batch → HQ / Cost Control / Director / Finance approval chain → Payment.
- **Process 2 — Preventive Maintenance**: Quarterly/Annual Maintenance Plan
  → Branch Facilities Manager approval → Maintenance Schedule entries →
  contractor execution → Desk Officer sign-off → Monthly Batch (shared with
  Process 1) → Payment.
- **Process 3 — Inventory Visibility & Quarterly Reporting**: reconciles
  contractor-held consumable stock (issued via Process 1/2 consumable
  requests) against contractor-declared closing stock, flags discrepancies,
  and feeds a "suggested quantity" back into the next Maintenance Plan's
  spare-parts budget.

Out of scope: payroll, asset register / fixed-asset accounting (handled
elsewhere in the NADF ERP), and any Enterprise-only features (this module is
Odoo 17 **Community** only).

## 2. Actors & Roles

| Role (security group) | Responsibilities |
|---|---|
| **End User** (`group_fm_end_user`) | Raises Job Complaints for their own branch; gives satisfaction feedback on completed Job Orders. |
| **Branch Desk Officer** (`group_fm_branch_desk_officer`) | Triages complaints into Job Orders; assigns contractors; reviews/approves consumable requests; signs off completed preventive schedules; compiles and submits Monthly Batches; prepares Inventory Reports. Implies End User. |
| **Branch Facilities Manager** (`group_fm_branch_facilities_manager`) | Approves/rejects Maintenance Plans; branch-level oversight of Job Orders, Consumable Requests, Monthly Batches, and Inventory Reports. Implies Branch Desk Officer. |
| **TFF / Local Contractor** (`group_fm_tff_contractor`) | Acknowledges and executes Job Orders / Maintenance Schedules; raises Consumable Requests; submits completion and inventory data. Scoped to their own `fm.contractor` record. |
| **HQ Procurement Officer** (`group_fm_hq_procurement_officer`) | First HQ-tier reviewer of Monthly Batches submitted by branches; can return batches for correction. |
| **Cost Control Officer** (`group_fm_cost_control`) | Reviews/queries Monthly Batches forwarded by HQ Procurement; reviews/archives Inventory Reports forwarded by HQ. |
| **Facilities Director** (`group_fm_director`) | Final approval of Monthly Batches before Finance. |
| **Finance Officer** (`group_fm_finance`) | Processes payment on fully-approved Monthly Batches. |

Group hierarchy: `group_fm_branch_facilities_manager` implies
`group_fm_branch_desk_officer`, which implies `group_fm_end_user`. The
HQ-tier groups (Procurement, Cost Control, Director, Finance) and the TFF
Contractor group are independent of this branch hierarchy.

## 3. Process Walkthroughs

### Process 1 — Reactive Maintenance

1. **End User** creates a `fm.job.complaint` (auto-numbered `FM/COMP/<year>/####`)
   for their branch. The Branch Desk Officer is notified via activity.
2. **Branch Desk Officer** creates a `fm.job.order` (`FM/JO/<year>/####`)
   referencing the complaint (complaint moves to *Assigned*), assigns a
   `fm.contractor`, and progresses it through `assigned` → `in_progress`.
3. **Contractor** raises `fm.consumable.request` lines (`FM/CR/<year>/####`)
   against the Job Order; **Desk Officer** approves with `quantity_approved`,
   which updates the contractor's inventory (`fm.contractor.inventory.line`).
4. **Contractor** submits completion (`action_submit_completion`).
5. **End User** completes the `fm.satisfaction.feedback.wizard`:
   - *Satisfied* → Job Order and source complaint both close.
   - *Not satisfied* → Job Order reopens, contractor is notified via chatter.
6. **Desk Officer** adds the closed Job Order to a `fm.monthly.batch`
   (`action_add_to_batch`, idempotent).
7. The batch progresses through the HQ approval chain (shared with Process 2,
   see §3.3).

### Process 2 — Preventive Maintenance

1. **Branch Desk Officer** drafts a `fm.maintenance.plan`
   (`FM/MP/<year>/####`, quarterly or annual) with planned spare-part lines
   (`fm.plan.spare.part.line`), then `action_submit`.
2. **Branch Facilities Manager** `action_approve`s (or rejects) the plan;
   approval activates it.
3. **Desk Officer** creates `fm.maintenance.schedule` entries
   (`FM/MS/<year>/####`) under the plan and assigns a contractor
   (`action_assign`). A daily cron
   (`ir_cron_fm_auto_assign_schedule`) auto-assigns schedules whose due date
   has arrived.
4. **Contractor** `action_acknowledge` → `action_start` →
   `action_submit_completion` (state becomes *Completed — Pending Sign-off*).
   Consumable requests can be raised against the schedule (`schedule_id`),
   with `contractor_id`/`branch_id` derived automatically.
5. **Desk Officer** `action_sign_off`s the completed schedule.
6. **Desk Officer** adds the signed-off schedule to a `fm.monthly.batch`
   (`action_add_to_batch`, idempotent — shared batch model with Process 1).
7. Once all schedules under a plan are closed, **Desk Officer** can
   `action_close` the plan.

### Process 3 — Inventory Visibility & Quarterly Reporting

1. **Desk Officer** creates a `fm.inventory.report` (`FM/IR/<year>/####`) for
   a branch/period and runs `action_populate_lines`, which pulls:
   - opening stock from the prior archived report for the same branch,
   - issues from approved Process 1/2 consumable requests in the period,
   - current contractor-held balances (`fm.contractor.inventory.line`).
   Each `fm.inventory.report.line` computes `closing_stock_calculated`
   (opening + issued − consumed) vs. `closing_stock_declared`.
2. **Desk Officer** `action_submit`s; **Branch Facilities Manager**
   `action_approve`s.
3. **HQ Procurement Officer** `action_hq_acknowledge`s, then
   `action_forward_cost_control`.
4. **Cost Control Officer** `action_archive_report`s — the report becomes the
   branch's new `last_inventory_report_id`.
5. Each `fm.plan.spare.part.line` on the **next** Maintenance Plan exposes a
   computed `suggested_quantity`, sourced from
   `last_inventory_report_id`'s `closing_stock_calculated` for the matching
   product.

### 3.3 Shared Monthly Batch Approval Chain (Process 1 + 2)

`fm.monthly.batch` (`job_order_ids` + `schedule_ids`) moves through:

```
draft -> submitted_hq -> cost_control -> director_approval -> finance -> paid
```

with two correction loops back to the branch:

- `hq_review` / `returned_branch` — HQ Procurement can return the batch to
  the branch for correction (`action_hq_return`).
- Cost Control can query the batch back (`action_cost_control_query`).
- Finance can also return a batch (`action_finance_return`).

| Step | Action | Actor (group) |
|---|---|---|
| `draft` → `submitted_hq` | `action_submit_to_hq` | Branch Desk Officer |
| `submitted_hq` → `cost_control` | `action_hq_approve` | HQ Procurement Officer |
| `submitted_hq`/`hq_review` → `returned_branch` | `action_hq_return` | HQ Procurement Officer |
| `cost_control` → `director_approval` | `action_cost_control_approve` | Cost Control Officer |
| `cost_control` → `hq_review` | `action_cost_control_query` | Cost Control Officer |
| `director_approval` → `finance` | `action_director_approve` | Facilities Director |
| `finance` → `paid` | `action_finance_pay` | Finance Officer |
| `finance` → `returned_branch` | `action_finance_return` | Finance Officer |

## 4. Installation

1. Place this module under your Odoo `addons_path`, e.g.
   `/Users/mac/odoo17/custom_addons/nadf_facilities_management/`.
2. Dependencies (all standard Odoo 17 Community apps, auto-installed if
   missing): `base`, `mail`, `hr`, `purchase`, `stock`, `account`.
3. Install/update:
   ```bash
   odoo-bin -c <config> -d <database> -u nadf_facilities_management --stop-after-init
   ```

## 5. Post-Install Configuration Checklist

- [ ] **Branches**: ensure each branch exists as an `hr.department` record.
      Branch-scoping record rules (§6) key off
      `user.employee_id.department_id`, so every Desk Officer / Facilities
      Manager / End User must have an `hr.employee` record linked to the
      correct department.
- [ ] **Users & Groups**: assign each user to the appropriate group(s) from
      §2. Remember the implied-group hierarchy (Facilities Manager ⊇ Desk
      Officer ⊇ End User).
- [ ] **Contractors**: create `fm.contractor` records per Process 1/2
      contractor; set `branch_id` (optional — leave blank for
      branch-agnostic contractors) and link contractor-side users via
      `user_ids` so the TFF Contractor record rules (§6) resolve correctly.
- [ ] **Products**: ensure consumable products used in
      `fm.consumable.request.line` / `fm.contractor.inventory.line` exist in
      `product.product`.
- [ ] **Mail templates**: review the 5 notification templates (§7) under
      *Settings → Technical → Email Templates* and adjust wording/branding
      as needed.
- [ ] **Cron**: confirm `FM: Auto-assign due preventive maintenance
      schedules` (`ir_cron_fm_auto_assign_schedule`) is active if
      auto-assignment of due preventive schedules is desired.
- [ ] **PDF reports**: install `wkhtmltopdf` on the server (see §9, Known
      Limitations) to enable PDF printing of the three QWeb reports.

## 6. Security Model

### 6.1 Groups

See §2. All groups belong to the **Facilities Management** module category.

### 6.2 Access Rights (ACL) Matrix

`R` = read, `W` = write, `C` = create, `U` = unlink. Blank = no access.
(Implied groups inherit the access of the groups they imply — e.g. a Branch
Facilities Manager also has the Branch Desk Officer row's access.)

| Model | End User | Desk Officer | Facilities Mgr | TFF Contractor | HQ Procurement | Cost Control | Director | Finance |
|---|---|---|---|---|---|---|---|---|
| `fm.job.complaint` | R,C | R,W,C | R | – | R | – | – | – |
| `fm.job.order` | R | R,W,C | R,W | R,W | R | R | R | R |
| `fm.consumable.request` | – | R,W,C | R | R,W,C | R | R | R | R |
| `fm.consumable.request.line` | – | R,W,C | R | R,W,C | – | – | – | – |
| `fm.monthly.batch` | – | R,W,C | R | – | R,W | R,W | R,W | R,W |
| `fm.maintenance.plan` | – | R,W,C | R,W | – | R | R | R | – |
| `fm.plan.spare.part.line` | – | R,W,C | R,W | – | – | – | – | – |
| `fm.maintenance.schedule` | – | R,W,C | R | R,W | R | R | R | – |
| `fm.inventory.report` | – | R,W,C | R,W | R | R,W | R,W | R | – |
| `fm.inventory.report.line` | – | R,W,C | R,W | R | R,W | R,W | R | – |
| `fm.contractor` | – | R | R,W | – | R | R | R | R |
| `fm.contractor.inventory.line` | – | R,W,C | R,W | R | – | – | – | – |
| `fm.satisfaction.feedback.wizard` (any internal user) | R,W,C,U | R,W,C,U | R,W,C,U | R,W,C,U | R,W,C,U | R,W,C,U | R,W,C,U | R,W,C,U |

The authoritative source for this matrix is
`security/ir.model.access.csv` (65 rows).

### 6.3 Record Rules (`security/fm_security.xml`)

Beyond the ACL matrix, 16 `ir.rule` record rules further restrict *which
records* a user can see/act on:

- **Branch scoping** (Branch Desk Officer, inherited by Facilities Manager):
  `fm.job.complaint`, `fm.job.order`, `fm.monthly.batch`,
  `fm.maintenance.plan`, `fm.maintenance.schedule` (via `plan_id.branch_id`),
  `fm.inventory.report`, `fm.consumable.request`, and `fm.contractor`
  (own branch **or** branch-agnostic contractors) are restricted to
  `branch_id = user.employee_id.department_id.id`.
- **Own-complaint scoping** (End User): a non-Desk-Officer End User sees only
  the `fm.job.complaint` records where `end_user_id = user.id`.
- **Contractor scoping** (TFF Contractor): `fm.job.order`,
  `fm.consumable.request`, `fm.maintenance.schedule`, and
  `fm.inventory.report` (via `contractor_ids`) are restricted to records
  linked to the contractor's own `fm.contractor` record via
  `fm.contractor.user_ids`.
- **HQ-tier batch-linkage scoping** (HQ Procurement, Cost Control, Director,
  Finance): `fm.job.order`, `fm.consumable.request`, and
  `fm.maintenance.schedule` are visible to these groups **only once attached
  to a Monthly Batch** (`batch_id != False`, or via `job_order_id.batch_id` /
  `schedule_id.batch_id` for consumable requests). `fm.monthly.batch` itself
  is **not** record-rule restricted for HQ-tier users — they need
  cross-branch visibility to action the approval chain.

A user with no `hr.employee` record resolves branch-scoping rules to
`branch_id = False`, so they will see no records on branch-required models.

## 7. Notifications

| Trigger | Mechanism | Recipient |
|---|---|---|
| New Job Complaint logged | `mail.activity` (To-Do) | Branch Desk Officer(s) |
| Job Order assigned to contractor | `mail_template_fm_job_order_assigned` | Contractor |
| Consumable Request approved | `mail_template_fm_consumable_request_approved` | Contractor |
| Monthly Batch submitted to HQ | `mail_template_fm_monthly_batch_submitted` | HQ Procurement |
| Monthly Batch returned to branch | `mail_template_fm_monthly_batch_returned` | Branch Desk Officer |
| Preventive schedule due | `mail_template_fm_schedule_due` | Contractor / Desk Officer |
| Maintenance Plan submitted for approval | `mail.activity` (To-Do) | Branch Facilities Manager |

Branch-level recipients are resolved via `fm.notification.mixin`, which
matches group membership against the user's `hr.employee.department_id`,
falling back to all group members if no branch match exists.

## 8. Reports

Three QWeb PDF reports (`report/`):

- **Job Order** (`report_fm_job_order.xml`)
- **Monthly Batch** (`report_fm_monthly_batch.xml`)
- **Quarterly Inventory Report** (`report_fm_inventory_report.xml`)

## 9. Known Limitations / Future Enhancements

- **wkhtmltopdf required for PDF printing**: this module's QWeb reports
  render correctly as HTML, but PDF generation requires `wkhtmltopdf` to be
  installed on the server (`brew install wkhtmltopdf` on macOS, or the
  appropriate package for your OS). Without it, PDF actions raise "Unable to
  find Wkhtmltopdf on this system".
- **Branch scoping depends on `hr.employee`**: every user subject to a
  branch-scoped record rule must have an `hr.employee` record with
  `department_id` set; there is no dedicated "branch manager" field on
  `hr.department` itself — group membership + employee department is used as
  the proxy for "which branch does this user belong to".
- **Contractor portal access**: this MVP assumes contractor users are
  internal Odoo users (`group_fm_tff_contractor`); a true external portal
  experience (e.g. via the `portal` module) is a possible future
  enhancement.
- **Multi-currency / budget integration**: Monthly Batch payment amounts are
  not currently integrated with `account.move` / vendor bills; Finance's
  `action_finance_pay` marks the batch as paid for tracking purposes only.

## 10. Automated Tests

`tests/test_fm_e2e.py` provides three `TransactionCase` end-to-end tests
(tagged `post_install`) exercising Process 1, Process 2, and Process 3 in
full, with `.with_user()` to verify ACL and record-rule enforcement for each
role. Run with:

```bash
odoo-bin -c <config> -d <database> -u nadf_facilities_management \
  --test-enable --stop-after-init --log-level=info
```
