# Odoo 16 → 17 Breaking Changes Reference
# ERP-AGRO (FamOil) — Software Factory Governance
# Version: 1.0 | Created: 2026-11-25 | WP-GOV-01

This document catalogues known Odoo 16→17 breaking patterns that affect custom
module development in this repository. `scripts/pre_review_check.py` check 5
(check_version_compat) automatically detects patterns §1–§3 on branch-changed
XML files before every `gov review`.

---

## §1 — `portal_my_home_entry` → `portal_docs_entry` (FATAL)

**Pattern:** `portal_my_home_entry` in XML template inheritance
**Impact:** `KeyError` or silent template failure at portal `/my` page load.
**Fix:** Replace `portal_my_home_entry` with `portal_docs_entry`.
**Check:** pre_review_check.py check 5a — FATAL (exits 1).

```xml
<!-- WRONG (Odoo 16) -->
<template id="portal_my_home" inherit_id="portal.portal_my_home">
    <xpath expr="//div[@id='portal_my_home_entry']" ...>

<!-- CORRECT (Odoo 17) -->
<template id="portal_my_home" inherit_id="portal.portal_my_home">
    <xpath expr="//div[@id='portal_docs_entry']" ...>
```

---

## §2 — `<t t-field=...>` on a `<t>` element (FATAL)

**Pattern:** `<t t-field="..."/>` or `<t ... t-field="...">` where the tag is `<t>`
**Impact:** Odoo 17 raises `AssertionError` at render time — `t-field` requires
a concrete HTML element, not an abstract `<t>` wrapper.
**Fix:** Wrap in a concrete element: `<span t-field="record.field_name"/>` or
`<div t-field="..."/>`.
**Check:** pre_review_check.py check 5b — FATAL (exits 1).

```xml
<!-- WRONG (Odoo 16 — allowed; Odoo 17 — AssertionError) -->
<t t-field="o.partner_id.name"/>

<!-- CORRECT (Odoo 17) -->
<span t-field="o.partner_id.name"/>
```

**Known ERP-AGRO history:** No instances found in custom_addons/ as of 2026-11-25.
Third-party om_* modules may contain this pattern — do not modify them; re-install
from vendor source that is Odoo 17-compatible.

---

## §3 — `<tree>` view tag deprecated; use `<list>` (ADVISORY)

**Pattern:** `<tree ...>` as the root element of a list view definition
**Impact:** In Odoo 17, list views use `<list>` (not `<tree>`). `<tree>` still
works via a compatibility shim but is deprecated and may break in Odoo 18.
**Fix:** Replace `<tree>` with `<list>` in new list view definitions.
**Check:** pre_review_check.py check 5c — ADVISORY WARNING on `<tree\b` (exits 0, prints warning).

```xml
<!-- DEPRECATED (Odoo 16 / transitional Odoo 17) -->
<record id="view_famoil_list" model="ir.ui.view">
    <field name="arch" type="xml">
        <tree string="...">

<!-- PREFERRED (Odoo 17+) -->
<record id="view_famoil_list" model="ir.ui.view">
    <field name="arch" type="xml">
        <list string="...">
```

---

## §4 — `account.move` field renames (MANUAL CHECK)

Several `account.move` fields were renamed between Odoo 16 and 17:

| Odoo 16 field | Odoo 17 field | Notes |
|---|---|---|
| `type` | `move_type` | Use `move_type` for journal entry type |
| `journal_type` | removed | Filter via `journal_id.type` instead |
| `amount_total_signed` | renamed internally | Use `amount_total` with `currency_id` context |

**Check:** Manual — not covered by pre_review_check.py. Raise an OQ if a custom
module reads these fields directly.

---

## §5 — `website.route` and `http.route` controller signature (MANUAL CHECK)

**Pattern:** Portal controller methods decorated with `@http.route` that use
`auth='public'` without `website=True` may lose session context in Odoo 17.
**Fix:** Add `website=True` to `@http.route` for any controller that uses
`request.website` or renders website QWeb templates.
**Check:** Manual — not covered by pre_review_check.py.

---

## §6 — `mail.thread` → `_track_subtype` signature (MANUAL CHECK)

In Odoo 17, `_track_subtype(self, init_values)` was replaced with
`_track_get_action(self, field, tracking)` in some scenarios. If a custom module
overrides `_track_subtype`, verify the override signature matches Odoo 17.
**Check:** Manual — not covered by pre_review_check.py.

---

## Open Questions

| ID | Question | Status |
|---|---|---|
| OQ-GOV-01 | check 5b does not strip XML comments — a commented-out `<t t-field>` will fire a false-positive fatal error. Fix: `re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)` before the per-line loop. | **RESOLVED 2026-11-25** — fix applied in scripts/pre_review_check.py; test added |
| OQ-GOV-02 | §4–§6 are manual-check only. Consider adding automated detection in a future pre_review_check.py extension. | OPEN |
| OQ-GOV-04 | Moved to `DECISION_LOG.md DEC-017` and `MODULE_REGISTRY.md SCR-001` where it belongs. See those documents for status and resolution gate. | — |
