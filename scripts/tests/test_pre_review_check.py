#!/usr/bin/env python3
"""
Unit tests for scripts/pre_review_check.py — covers check_version_compat().

Run with:
    python3 scripts/tests/test_pre_review_check.py
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

CHECK_SCRIPT = Path(__file__).resolve().parent.parent / 'pre_review_check.py'


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


class TestCheckVersionCompatListTag(unittest.TestCase):
    """check 5c — <list> advisory (exits 0, prints warning only)"""

    def _run(self, xml_content):
        issues = []
        with tempfile.TemporaryDirectory() as td:
            xml_file = Path(td) / 'test.xml'
            xml_file.write_text(xml_content)
            ns = _load_checker_functions(xml_file, issues)
            ns['check_version_compat']()
        return issues

    def test_list_tag_does_not_add_issue(self):
        """<list> is advisory only — must NOT add to ISSUES (no fatal exit)."""
        issues = self._run('        <list string="Items">')
        self.assertEqual(issues, [],
                         f'<list> must be advisory only (no ISSUES entry), got: {issues}')

    def test_listing_tag_clean(self):
        """<listing> must NOT trigger the advisory."""
        issues = self._run('<listing string="Items">')
        self.assertEqual(issues, [],
                         f'False positive on <listing>: {issues}')


if __name__ == '__main__':
    unittest.main()
