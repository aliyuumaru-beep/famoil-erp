#!/usr/bin/env python3
"""
Pre-review static checker for ERP-AGRO (FamOil) custom modules.

Run this before `gov review` to catch common Odoo 17 issues that would
otherwise consume expensive G1/G2/G3 review cycles. Exit code 0 = clean;
1 = issues found.

Usage:
    python3 scripts/pre_review_check.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUSTOM_ADDONS = ROOT / 'custom_addons'
ISSUES = []

# Custom FamOil modules (third-party om_* and OCA modules are excluded from checks)
CUSTOM_MODULE_NAMES = {
    'stock_crude_oil_tank_restriction',
    'mrp_component_availability_check',
    'stock_landed_cost_po_check',
}


def issue(filepath, line_no, msg):
    ISSUES.append(f'  [{filepath.relative_to(ROOT)}:{line_no}] {msg}')


def _custom_module_dirs():
    for d in CUSTOM_ADDONS.iterdir():
        if d.is_dir() and d.name in CUSTOM_MODULE_NAMES:
            yield d


# ── 1. No inline imports inside method bodies ───────────────────────────────
# OQ-GOV-03: in_method resets on any def/class boundary (indent heuristic).
# A nested def inside a method resets the flag prematurely — accepted limitation.
def check_inline_imports():
    for mod in _custom_module_dirs():
        for py in mod.rglob('*.py'):
            lines = py.read_text().splitlines()
            in_method = False
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Reset on any top-level def/class (indent 0 or 4-space class method)
                if re.match(r'^(def |async def |class )', stripped):
                    in_method = stripped.startswith('def ') or stripped.startswith('async def ')
                if in_method and re.match(r'^\s+(import |from \S+ import )', line):
                    issue(py, i, f'Inline import inside method body: {stripped!r}')


# ── 2. create() overrides must have @api.model_create_multi ─────────────────
def check_create_decorator():
    for mod in _custom_module_dirs():
        for py in mod.rglob('*.py'):
            lines = py.read_text().splitlines()
            for i, line in enumerate(lines, 1):
                if re.match(r'\s+def create\(self,', line):
                    prev = '\n'.join(lines[max(0, i - 3):i])
                    if '@api.model_create_multi' not in prev and '@api.model' not in prev:
                        issue(py, i, 'create() override missing @api.model_create_multi or @api.model')


# ── 3. XML ID references in ir.model.access.csv must exist in groups.xml ────
def check_acl_xml_ids():
    for mod in _custom_module_dirs():
        csv_path = mod / 'security/ir.model.access.csv'
        groups_path = mod / 'security/groups.xml'
        if not csv_path.exists():
            continue
        groups_text = groups_path.read_text() if groups_path.exists() else ''
        known_ids = set(re.findall(r'id="([^"]+)"', groups_text))
        for i, line in enumerate(csv_path.read_text().splitlines()[1:], 2):
            parts = line.split(',')
            if len(parts) >= 4 and parts[3].strip():
                group_ref = parts[3].strip()
                local_id = group_ref.split('.')[-1]
                if local_id not in known_ids and group_ref not in known_ids:
                    issue(csv_path, i, f'ACL group ref not found in groups.xml: {group_ref!r}')


# ── 4. No hardcoded database IDs as constants (ISSUE-003 prevention) ────────
HARDCODED_ID_PATTERN = re.compile(
    r'^[A-Z_]+_ID[S]?\s*=\s*\{?\d',
    re.MULTILINE,
)


def check_no_hardcoded_ids():
    for mod in _custom_module_dirs():
        for py in mod.rglob('*.py'):
            text = py.read_text()
            for m in HARDCODED_ID_PATTERN.finditer(text):
                lineno = text[:m.start()].count('\n') + 1
                issue(py, lineno,
                      f'Possible hardcoded database ID constant: {m.group().strip()!r} — use name-based lookup instead')


# ── 5. Odoo 16→17 breaking patterns in XML files ────────────────────────────
def _branch_changed_xml_files():
    """Return XML files changed on this branch vs merge-base. Falls back to all custom module XML."""
    try:
        base = subprocess.check_output(
            ['git', 'merge-base', 'HEAD', 'origin/main'],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).strip()
        changed = subprocess.check_output(
            ['git', 'diff', '--name-only', base, 'HEAD'],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
        ).splitlines()
        xml_files = [
            ROOT / f for f in changed
            if f.endswith('.xml') and (ROOT / f).exists()
        ]
        if xml_files:
            return xml_files
    except Exception:
        pass
    # Fallback: all XML in custom modules
    return [
        xml
        for mod in _custom_module_dirs()
        for xml in mod.rglob('*.xml')
    ]


def check_version_compat():
    for xml in _branch_changed_xml_files():
        try:
            text = xml.read_text(errors='ignore')
        except (OSError, IsADirectoryError):
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            # 5a — portal_my_home_entry rename
            if 'portal_my_home_entry' in line:
                issue(xml, i,
                      'Odoo 16→17: portal_my_home_entry was renamed to portal_docs_entry '
                      '(see docs/ODOO17_BREAKING_CHANGES.md §1)')
            # 5b — <t t-field=...> on a <t> element (raises AssertionError in Odoo 17)
            if re.search(r'<t\b[^>]*\bt-field=', line):
                issue(xml, i,
                      'Odoo 16→17: <t t-field="..."> raises AssertionError — '
                      'use a concrete element: <span t-field="..."/> '
                      '(see docs/ODOO17_BREAKING_CHANGES.md §2)')
            # 5c — <tree> tag advisory (deprecated in Odoo 17; prefer <list>)
            if re.search(r'^\s*<tree\b', line):
                print(f'  WARNING [{xml.relative_to(ROOT)}:{i}]: '
                      'Odoo 17 deprecated <tree> for list views — prefer <list>. '
                      '(see docs/ODOO17_BREAKING_CHANGES.md §3)')


# ── 6. No hardcoded passwords / secrets ─────────────────────────────────────
SECRET_PATTERN = re.compile(
    r'(password\s*=\s*["\'][^"\']{6,}["\']'
    r'|admin_passwd\s*=\s*(?!CHANGE_ME)[^\s#]{6,})',
    re.IGNORECASE,
)


def check_no_secrets():
    try:
        ignored = set(subprocess.check_output(
            ['git', 'ls-files', '--ignored', '--exclude-standard', '-o'],
            cwd=ROOT, text=True,
        ).splitlines())
    except Exception:
        ignored = set()
    skip_dirs = {'.git', '__pycache__', 'specs', 'backups', 'notes', 'odoo', 'venv'}
    for path in ROOT.rglob('*'):
        if any(d in path.parts for d in skip_dirs):
            continue
        if str(path.relative_to(ROOT)) in ignored:
            continue
        if path.suffix not in ('.py', '.xml', '.json', '.conf', '.cfg', '.env'):
            continue
        if path.name.endswith('.example'):
            continue
        try:
            text = path.read_text(errors='ignore')
        except (OSError, IsADirectoryError):
            continue
        for m in SECRET_PATTERN.finditer(text):
            lineno = text[:m.start()].count('\n') + 1
            issue(path, lineno, f'Possible hardcoded secret: {m.group()[:60]!r}')


# ── Run all checks ───────────────────────────────────────────────────────────
check_inline_imports()
check_create_decorator()
check_acl_xml_ids()
check_no_hardcoded_ids()
check_version_compat()
check_no_secrets()

if ISSUES:
    print(f'Pre-review: {len(ISSUES)} issue(s) found — fix before gov review:\n')
    for msg in ISSUES:
        print(msg)
    sys.exit(1)
else:
    print('Pre-review: clean. Safe to run gov review.')
    sys.exit(0)
