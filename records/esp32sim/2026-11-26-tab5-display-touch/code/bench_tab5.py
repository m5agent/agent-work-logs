"""Compare the same native CLI fixtures with three interleaved release runs."""
import json
import re
import statistics
import subprocess
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
base, candidate, assets, roms = (Path(arg).resolve() for arg in sys.argv[1:5])
binaries = {"hello": "esp32sim", "c3-hello": "esp32sim-c3",
            "c6-hello": "esp32sim-c6", "p4-hello": "esp32sim-p4", "pocket-tank": "esp32sim"}
results = {}
for demo, binary in binaries.items():
    if sys.argv[5:] and demo not in sys.argv[5:]:
        continue
    spec = json.loads((assets / f"{demo}.json").read_text())
    files = spec["files"]
    argv = ["--boot", "rom", "--rom", str(roms / files["rom"]), "--flash-mb", str(spec["flash_mb"]),
            "--console", "uart0", "--no-dump", "--max-seconds", "5" if demo == "pocket-tank" else "3"]
    if binary == "esp32sim":
        argv += ["--board", spec["board"], "--psram-mb", str(spec["psram_mb"])]
    for name in ("bootloader", "ptable", "app"):
        argv += ["--" + name, str(assets / files[name])]
    for address, path in spec.get("flash_at", {}).items():
        argv += ["--flash-at", f"{address}={assets / path}"]
    runs = {"baseline": [], "candidate": []}
    for i in range(3):
        for label, directory in [("baseline", base), ("candidate", candidate)]:
            result = subprocess.run(["/usr/bin/time", "-p", str(directory / binary), *argv],
                                    cwd=root, capture_output=True, text=True, timeout=140)
            (root / f"{demo}-{label}-{i}.log").write_text(result.stderr)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            counts = re.search(r"— (?:core0 )?(\d+)(?: \+ core1 (\d+))? insns", result.stderr)
            elapsed = re.search(r"^user ([0-9.]+)$", result.stderr, re.M)
            if not counts or not elapsed or "Halted" not in result.stderr:
                raise RuntimeError(result.stderr)
            runs[label].append((list(counts.groups()), float(elapsed[1]), result.stdout))
    first = runs["baseline"][0]
    assert all(run[0] == first[0] and run[2] == first[2] for samples in runs.values() for run in samples), demo
    results[demo] = {label: {"insns": [int(x) for x in runs[label][0][0] if x is not None],
                              "median_user_s": statistics.median(run[1] for run in runs[label])} for label in runs}
    print(json.dumps({demo: results[demo]}), flush=True)
