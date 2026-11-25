"""Produce the exact release-source NFCCap constructor delta and guest capsule."""
from ast import ClassDef, FunctionDef, parse
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
from textwrap import dedent
import json

lab = Path(__file__).resolve().parent
workspace = lab.parent.parent
docs = workspace / ".work/docs-uiflow-20261125"
versions = {"2.5.3": "50e440780492aa847378c7d3477ab912f7063bac",
            "2.5.5": "a61a29409f09f1f4bebae05e15c4bd6dcc4956b6"}
pins = {
    "cap-cc1101.py": "b5fb40b02ac0cd9d0ecb1de7bf8b6022294ccd1a1bea78d8ce568ca3bc8a6930",
    "unit-nfc.py": "fb45a7172ffb2bf1dbf0b884fcc6968ef11f520b0b9eaf61826342b08c00eeca",
    "driver-nfc.py": "7d5dca54658dd3fccda23fa1ef1198a347b5e4165b5263de95a8e2af9b6bcb6e",
    "driver-st25r3916.py": "54b54ced701530b315e7afb9e9e277327cad48de211b2275f254f9df33ce0926",
    "cap-init.py": "3ea4a3041fde22c0ad7ca8fb1a423b1a07b24b62585893e67c3b2f82faff14a9",
}
sha = lambda b: sha256(b).hexdigest()
for name, expected in pins.items():
    content = (lab / "release-v253" / name).read_bytes()
    assert sha(content) == expected
    assert (lab / "release-v255" / name).read_bytes() == content
    if name != "cap-init.py":
        assert (docs / "nfc-source" / name).read_bytes() == content

source_file = docs / "nfc-source/cap-cc1101.py"
upstream = source_file.read_text()
bad_call = "        super().__init__(chip=self._chip)\n"
new_call = (
    "        self.chip = self._chip\n"
    "        if not self.chip.begin():\n"
    '            raise RuntimeError("ST25R3916 initialization failed")\n'
)
assert upstream.count(bad_call) == 1
candidate = upstream.replace(bad_call, new_call)
assert candidate.replace(new_call, bad_call) == upstream

def constructor(source):
    cap = next(node for node in parse(source).body
               if isinstance(node, ClassDef) and node.name == "NFCCap")
    assert [base.id for base in cap.bases] == ["NFCUnit"]
    method = next(node for node in cap.body if isinstance(node, FunctionDef) and node.name == "__init__")
    assert [arg.arg for arg in method.args.args] == ["self"]
    return "\n".join(source.splitlines()[method.lineno - 1:method.end_lineno]) + "\n"

assert constructor(candidate).replace(new_call, bad_call) == constructor(upstream)
unit = parse((docs / "nfc-source/unit-nfc.py").read_text())
unit_type = next(node for node in unit.body if isinstance(node, ClassDef) and node.name == "NFCUnit")
unit_init = next(node for node in unit_type.body if isinstance(node, FunctionDef) and node.name == "__init__")
assert [arg.arg for arg in unit_init.args.args] == ["self", "i2c"]

# Only the constructor is copied. Every bound dependency comes from the frozen guest driver module.
capsule = "from cap.cc1101 import M5, ST25R3916, _port_table, machine\n\n" + dedent(constructor(candidate))
compile(capsule, "<nfc-candidate>", "exec")
diff = "".join(unified_diff(upstream.splitlines(keepends=True), candidate.splitlines(keepends=True),
                            fromfile="a/m5stack/libs/cap/cc1101.py", tofile="b/m5stack/libs/cap/cc1101.py",
                            n=3))
assert len([line for line in diff.splitlines() if line.startswith("@@")]) == 1
assert diff.count("+        self.chip = self._chip") == 1
(lab / "nfccap-131-candidate.patch").write_text(diff)
(lab / "nfccap-131-capsule.py").write_text(capsule)
(lab / "cap-cc1101-candidate.py").write_text(candidate)
example_src = docs / "upstream/examples/cap/cc1101/cc1101_cap_nfc_read_id_example.py"
example = example_src.read_bytes()
assert sha(example) == "e0df69f68471a717ba4ec23e67945fe7ed312c4c1bd34e6651c18d147bac1c5b"
result = {
    "schema_version": 1,
    "upstream_releases": versions,
    "shared_sdk_source_sha256": pins,
    "candidate_file_sha256": sha(candidate.encode()),
    "candidate_patch_sha256": sha(diff.encode()),
    "candidate_capsule_sha256": sha(capsule.encode()),
    "candidate_capsule_bytes": len(capsule.encode()),
    "original_example_sha256": sha(example),
    "original_example_path": "examples/cap/cc1101/cc1101_cap_nfc_read_id_example.py",
    "host_preflight": "PASS",
    "guest_test": "NOT RUN by source generator",
}
(lab / "candidate-source.receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result))
