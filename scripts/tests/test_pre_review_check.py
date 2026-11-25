#!/usr/bin/env python3
"""
Unit tests for scripts/pre_review_check.py.

Covers: check_version_compat, check_no_hardcoded_ids, check_inline_imports,
check_create_decorator, check_acl_xml_ids, check_no_secrets.

Run with:
    python3 scripts/tests/test_pre_review_check.py
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

CHECK_SCRIPT = Path(__file__).resolve().parent.parent / 'pre_review_check.py'


def _load_module_ns(mod_dir: Path, issues_list: list):
    """
    Exec the checker up to the '# ── Run all checks' sentinel. Patches CUSTOM_ADDONS
    and CUSTOM_MODULE_NAMES so only mod_dir's parent / mod_dir.name is scanned.
    """
    source = CHECK_SCRIPT.read_text()
    cut = source.find('# ── Run all checks')
    assert cut > 0, 'Sentinel not found in pre_review_check.py'
    fn_source = source[:cut]
    ns = {
        '__file__': str(CHECK_SCRIPT),
        'ISSUES': issues_list,
        're': re,
        'sys': sys,
    }
    exec(compile(fn_source, str(CHECK_SCRIPT), 'exec'), ns)  # noqa: S102
    ns['ROOT'] = mod_dir.parent
    ns['CUSTOM_ADDONS'] = mod_dir.parent
    ns['CUSTOM_MODULE_NAMES'] = {mod_dir.name}
    def _issue(filepath, line_no, msg):
        issues_list.append(f'  [{filepath.name}:{line_no}] {msg}')
    ns['issue'] = _issue
    return ns


def _load_checker_functions(xml_file: Path, issues_list: list):
    """
    Exec the checker up to the '# ── Run all checks' sentinel so sys.exit()
    is never called. Overrides ROOT, MODULE path, _branch_changed_xml_files,
    and issue() so tests capture findings from a single temp XML file.
    """
    source = CHECK_SCRIPT.read_text()
    cut = source.find('# ── Run all checks')
    assert cut > 0, 'Sentinel not found in pre_review_check.py'
    fn_source = source[:cut]
    ns = {
        '__file__': str(CHECK_SCRIPT),
        'ISSUES': issues_list,
        're': re,
        'sys': sys,
    }
    exec(compile(fn_source, str(CHECK_SCRIPT), 'exec'), ns)  # noqa: S102
    # Override ROOT AFTER exec — script re-assigns ROOT from __file__
    ns['ROOT'] = xml_file.parent
    # Patch _branch_changed_xml_files to return exactly this one file
    ns['_branch_changed_xml_files'] = lambda: [xml_file]
    # Override issue() to capture to our list
    def _issue(filepath, line_no, msg):
        issues_list.append(f'  [{filepath.name}:{line_no}] {msg}')
    ns['issue'] = _issue
    return ns


class TestCheckVersionCompatPortalEntry(unittest.TestCase):
    """check 5a — portal_my_home_entry"""

    def _run(self, xml_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            xml_file = Path(td) / 'test.xml'
            xml_file.write_text(xml_content)
            ns = _load_checker_functions(xml_file, issues)
            ns['check_version_compat']()
        return issues

    def test_portal_my_home_entry_detected(self):
        issues = self._run('<xpath expr="//div[@id=\'portal_my_home_entry\']"/>')
        self.assertTrue(any('portal_my_home_entry' in i for i in issues),
                        f'Expected portal_my_home_entry finding, got: {issues}')

    def test_portal_docs_entry_clean(self):
        issues = self._run('<xpath expr="//div[@id=\'portal_docs_entry\']"/>')
        self.assertFalse(any('portal_my_home_entry' in i for i in issues),
                         f'False positive on portal_docs_entry: {issues}')


class TestCheckVersionCompatTField(unittest.TestCase):
    """check 5b — <t t-field=...> on a <t> element"""

    def _run(self, xml_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            xml_file = Path(td) / 'test.xml'
            xml_file.write_text(xml_content)
            ns = _load_checker_functions(xml_file, issues)
            ns['check_version_compat']()
        return issues

    def test_t_tfield_detected(self):
        issues = self._run('<t t-field="o.partner_id.name"/>')
        self.assertTrue(any('t-field' in i for i in issues),
                        f'Expected t-field finding, got: {issues}')

    def test_span_tfield_clean(self):
        issues = self._run('<span t-field="o.partner_id.name"/>')
        self.assertFalse(any('t-field' in i for i in issues),
                         f'False positive on span t-field: {issues}')

    def test_td_tfield_clean(self):
        """<td t-field=...> must NOT fire (only <t ...> fires)."""
        issues = self._run('<td t-field="o.amount_total"/>')
        self.assertFalse(any('t-field' in i for i in issues),
                         f'False positive on td t-field: {issues}')

    def test_template_tfield_clean(self):
        """<template ...> tag must NOT fire."""
        issues = self._run('<template id="x" t-field="something"/>')
        self.assertFalse(any('t-field' in i for i in issues),
                         f'False positive on template t-field: {issues}')

    def test_commented_out_tfield_no_false_positive(self):
        """Commented-out <t t-field> must NOT fire after OQ-GOV-01 fix."""
        issues = self._run('<!-- <t t-field="o.partner_id.name"/> -->')
        self.assertFalse(any('t-field' in i for i in issues),
                         f'False positive on commented-out t-field: {issues}')


class TestCheckVersionCompatTreeTag(unittest.TestCase):
    """check 5c — <tree> advisory (exits 0, prints warning only)"""

    def _run(self, xml_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            xml_file = Path(td) / 'test.xml'
            xml_file.write_text(xml_content)
            ns = _load_checker_functions(xml_file, issues)
            ns['check_version_compat']()
        return issues

    def test_tree_tag_does_not_add_issue(self):
        """<tree> is advisory only — must NOT add to ISSUES (no fatal exit)."""
        issues = self._run('        <tree string="Items">')
        self.assertEqual(issues, [],
                         f'<tree> must be advisory only (no ISSUES entry), got: {issues}')

    def test_list_tag_clean(self):
        """<list> (the preferred Odoo 17 form) must NOT trigger the advisory."""
        issues = self._run('        <list string="Items">')
        self.assertEqual(issues, [],
                         f'False positive on <list>: {issues}')


class TestCheckNoHardcodedIds(unittest.TestCase):
    """check 4 — hardcoded database ID constants (ISSUE-003 recurrence prevention)"""

    def _load_and_run(self, py_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            mod_dir = Path(td) / 'my_module' / 'models'
            mod_dir.mkdir(parents=True)
            (mod_dir / 'stock_picking.py').write_text(py_content)
            ns = _load_module_ns(Path(td) / 'my_module', issues)
            ns['check_no_hardcoded_ids']()
        return issues

    def test_hardcoded_id_constant_detected(self):
        """CRUDE_OIL_TANK_IDS = {141, 142} must fire."""
        issues = self._load_and_run('CRUDE_OIL_TANK_IDS = {141, 142}\n')
        self.assertTrue(any('hardcoded database ID' in i for i in issues),
                        f'Expected hardcoded-ID finding, got: {issues}')

    def test_name_based_lookup_clean(self):
        """Runtime name lookup must NOT fire."""
        issues = self._load_and_run(
            "tanks = self.env['stock.location'].search([('name', 'ilike', 'Crude Oil Tank')])\n"
        )
        self.assertFalse(any('hardcoded database ID' in i for i in issues),
                         f'False positive on name-based lookup: {issues}')


class TestCheckInlineImports(unittest.TestCase):
    """check 1 — inline imports inside method bodies"""

    def _run(self, py_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            mod = Path(td) / 'my_mod' / 'models'
            mod.mkdir(parents=True)
            (mod / 'test.py').write_text(py_content)
            ns = _load_module_ns(Path(td) / 'my_mod', issues)
            ns['check_inline_imports']()
        return issues

    def test_inline_import_detected(self):
        code = 'def my_method(self):\n    import os\n    return os.getcwd()\n'
        issues = self._run(code)
        self.assertTrue(any('Inline import' in i for i in issues),
                        f'Expected inline import finding, got: {issues}')

    def test_module_level_import_clean(self):
        code = 'import os\n\ndef my_method(self):\n    return os.getcwd()\n'
        issues = self._run(code)
        self.assertFalse(any('Inline import' in i for i in issues),
                         f'False positive on module-level import: {issues}')


class TestCheckCreateDecorator(unittest.TestCase):
    """check 2 — create() overrides must have @api.model_create_multi"""

    def _run(self, py_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            mod = Path(td) / 'my_mod' / 'models'
            mod.mkdir(parents=True)
            (mod / 'test.py').write_text(py_content)
            ns = _load_module_ns(Path(td) / 'my_mod', issues)
            ns['check_create_decorator']()
        return issues

    def test_missing_decorator_detected(self):
        code = 'class MyModel:\n    def create(self, vals):\n        return super().create(vals)\n'
        issues = self._run(code)
        self.assertTrue(any('missing @api.model_create_multi' in i for i in issues),
                        f'Expected missing decorator finding, got: {issues}')

    def test_with_decorator_clean(self):
        code = 'class MyModel:\n    @api.model_create_multi\n    def create(self, vals_list):\n        return super().create(vals_list)\n'
        issues = self._run(code)
        self.assertFalse(any('missing @api.model_create_multi' in i for i in issues),
                         f'False positive with decorator present: {issues}')


class TestCheckAclXmlIds(unittest.TestCase):
    """check 3 — ACL group refs must exist in groups.xml"""

    def _run(self, csv_content, groups_xml_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            mod = Path(td) / 'my_mod'
            sec = mod / 'security'
            sec.mkdir(parents=True)
            (sec / 'ir.model.access.csv').write_text(csv_content)
            if groups_xml_content is not None:
                (sec / 'groups.xml').write_text(groups_xml_content)
            ns = _load_module_ns(mod, issues)
            ns['check_acl_xml_ids']()
        return issues

    def test_missing_group_ref_detected(self):
        csv = 'id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n'
        csv += 'access_test,test,model_my_model,group_nonexistent,1,0,0,0\n'
        groups = '<odoo><data><record id="group_other" model="res.groups"/></data></odoo>'
        issues = self._run(csv, groups)
        self.assertTrue(any('ACL group ref not found' in i for i in issues),
                        f'Expected ACL finding, got: {issues}')

    def test_known_group_ref_clean(self):
        csv = 'id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n'
        csv += 'access_test,test,model_my_model,group_manager,1,0,0,0\n'
        groups = '<odoo><data><record id="group_manager" model="res.groups"/></data></odoo>'
        issues = self._run(csv, groups)
        self.assertFalse(any('ACL group ref not found' in i for i in issues),
                         f'False positive on known group ref: {issues}')


class TestCheckNoSecrets(unittest.TestCase):
    """check 6 — no hardcoded passwords/secrets"""

    def _run_with_root(self, root: Path, issues_list: list):
        source = CHECK_SCRIPT.read_text()
        cut = source.find('# ── Run all checks')
        assert cut > 0
        fn_source = source[:cut]
        ns = {
            '__file__': str(CHECK_SCRIPT),
            'ISSUES': issues_list,
            're': re,
            'sys': sys,
        }
        exec(compile(fn_source, str(CHECK_SCRIPT), 'exec'), ns)  # noqa: S102
        ns['ROOT'] = root
        def _issue(filepath, line_no, msg):
            issues_list.append(f'  [{filepath.name}:{line_no}] {msg}')
        ns['issue'] = _issue
        return ns

    def test_hardcoded_password_in_py_detected(self):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / 'config.py').write_text("password = 'mysecretpass'\n")
            ns = self._run_with_root(Path(td), issues)
            ns['check_no_secrets']()
        self.assertTrue(any('hardcoded secret' in i for i in issues),
                        f'Expected secret finding, got: {issues}')

    def test_example_file_excluded(self):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / '.env.example').write_text("password = 'changeme'\n")
            ns = self._run_with_root(Path(td), issues)
            ns['check_no_secrets']()
        self.assertFalse(any('hardcoded secret' in i for i in issues),
                         f'False positive on .example file: {issues}')


if __name__ == '__main__':
    unittest.main()
