#!/usr/bin/env python3
"""Repeat selected syntax observations without executing document examples.
Usage: python3 check_document_examples.py --checkout PATH
The checkout must contain documentation commit 47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac.
"""
import argparse, ast, json, re, subprocess
BASE = "47ab6d5115713ffc71ea6ae5ef4dba572fe2c5ac"
CASES = [
    ("static/zh_CN/uiflow/blockly/advanced/modbus_master.md", "timeout=)"),
    ("static/zh_CN/uiflow/blockly/hat/8servo_v1.1.md", ".write_servo_angle"),
    ("static/en/uiflow/blockly/module/commu.md", ">>|"),
    ("static/zh_CN/guide/stickv/maixpy.md", "fimport lcd"),
    ("static/ja/guide/stickv/maixpy.md", "fimport lcd"),
]
p = argparse.ArgumentParser()
p.add_argument("--checkout", required=True)
a = p.parse_args()
rows = []
for file, needle in CASES:
    text = subprocess.check_output(["git", "-C", a.checkout, "show", BASE + ":" + file], text=True)
    block = next(m for m in re.finditer(r"^```python[^\n]*\n(.*?)^```", text, re.M | re.S) if needle in m.group(1))
    try:
        ast.parse(block.group(1))
        rows.append({"file": file, "syntax": "PASS"})
    except SyntaxError as e:
        rows.append({"file": file, "syntax": "FAIL", "line": text[:block.start(1)].count("\n") + e.lineno, "reason": e.msg})
print(json.dumps({"commit": BASE, "validation": "host syntax only; no device execution", "observations": rows}, ensure_ascii=False, indent=2))
