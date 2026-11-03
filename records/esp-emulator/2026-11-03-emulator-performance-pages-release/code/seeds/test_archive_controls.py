"""Offline actual archive verifier positive/negative controls, no guest."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile

p = Path(__file__).with_name("verify_runtime_archive.py")
spec = importlib.util.spec_from_file_location("archive_verifier", p)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)
rows = []
with tempfile.TemporaryDirectory(prefix="m5-pages-source-host-control-") as task_dir:
    archive = Path(task_dir) / "source.tar.xz"
    def package(members):
        with tarfile.open(archive, "w:xz") as tar:
            for name, content in members:
                info = tarfile.TarInfo(name);info.size = len(content);tar.addfile(info, io.BytesIO(content))
    expected = {"qemu/example.c": hashlib.sha256(b"actual source\n").hexdigest()}
    package([("qemu/example.c", b"actual source\n")])
    assert verifier.verify_members(archive, expected) == 1
    rows.append({"name": "matching actual archived bytes", "status": "PASS"})
    for name, members in [
        ("changed postimage", [("qemu/example.c", b"changed\n")]),
        ("missing postimage", [("qemu/other.c", b"actual source\n")]),
        ("duplicate postimage", [("qemu/example.c", b"actual source\n"), ("qemu/example.c", b"actual source\n")]),
    ]:
        package(members)
        try: verifier.verify_members(archive, expected)
        except ValueError: rows.append({"name": name, "status": "PASS"})
        else: raise AssertionError(name + " must fail")
out = {"result": "PASS", "kind": "offline-source-archive-controls", "guest_execution": "NOT RUN", "checks": rows}
Path(__file__).with_name("offline-archive-controls.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out))
