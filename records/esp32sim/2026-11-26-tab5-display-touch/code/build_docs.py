"""Compile the fenced Arduino programs from a fixed docs checkout."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
docs = Path(sys.argv[1])
sdk = Path(sys.argv[2])
wanted = set(sys.argv[3:])
for page in sorted(docs.glob("*.md")):
    for index, source in enumerate(re.findall(r"```(?:cpp|c\+\+|arduino)[^\n]*\n(.*?)```", page.read_text(), re.S), 1):
        if "void setup" not in source:
            continue
        name = f"{page.stem}-{index}"
        if wanted and name not in wanted:
            continue
        out = root / "firmware" / name
        sketch = out / "sketch"
        sketch.mkdir(parents=True, exist_ok=True)
        (sketch / "sketch.ino").write_text(source)
        command = [str(sdk/"arduino-cli"), "--config-file", str(sdk/"arduino/arduino-cli.yaml"),
                   "compile", "--fqbn", "m5stack:esp32:m5stack_tab5", "-j", "4",
                   "--build-property", f"runtime.tools.esptool_py.path={sdk/'tools/esptool'}",
                   "--build-path", str(root/"arduino-build"), str(sketch)]
        with (out/"compile.log").open("w") as log:
            rc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
        result = {"case": name, "exit_code": rc, "sketch_sha256": hashlib.sha256(source.encode()).hexdigest()}
        if rc == 0:
            merged = out/"sketch.ino.merged.bin"
            shutil.copyfile(root/"arduino-build"/merged.name, merged)
            result["firmware_sha256"] = hashlib.file_digest(merged.open("rb"), "sha256").hexdigest()
        (out/"result.json").write_text(json.dumps(result, indent=2)+"\n")
        print(json.dumps(result), flush=True)
