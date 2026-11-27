from collections import Counter
from hashlib import sha256
from pathlib import Path
from runpy import run_path
import json
import re
import sys

repo, out, prior = map(Path, sys.argv[1:])
checks = run_path(str(repo / "tools/check-c6-docs.py"))
summary = {}
for name in ("thread-peer", "thread-isolated", "zigbee-peer", "zigbee-recovery"):
    paths = [root / "nanoc6-peers" / name for root in (prior, out / "c6-a", out / "c6-b")]
    inputs = [json.loads((p / "inputs.json").read_text()) for p in paths]
    for key in ("rom_sha256", "firmware_sha256", "seconds", "isolated", "resets", "scripts", "traces"):
        assert len({json.dumps(record[key], sort_keys=True) for record in inputs}) == 1, (name, key)
    files = {}
    for file in ("radio.ndjson", "node0.log", "node1.log"):
        digest = [sha256((p / file).read_bytes()).hexdigest() for p in paths]
        assert len(set(digest)) == 1, (name, file, digest)
        files[file] = digest[0]
    first, second, wire = [(paths[1] / entry).read_text() for entry in ("node0.log", "node1.log", "radio.ndjson")]
    if name == "thread-peer":
        assert "Thread Node State: Leader" in first
        assert re.search(r"Thread Node State: (Child|Router)", second)
        assert "Hello,M5Stack" in second
    if name == "thread-isolated":
        assert "Hello,M5Stack" not in second
        assert re.search(r"Thread Node State: (Child|Router)", second) is None
    if name.startswith("zigbee"):
        assert "LED device bound successfully!" in first
        assert "Connected to Zigbee network!" in second
        assert "Sending ON command" in first and "Sending OFF command" in first
        assert checks["zigbee_light_transitions"](paths[1], first)
    if name == "zigbee-recovery":
        assert "RTC_SW_CPU_RESET" in second
        assert second.count("Connected to Zigbee network!") == 2
    summary[name] = {"status": "PASS", "inputs": {k: inputs[1][k] for k in
                     ("rom_sha256", "firmware_sha256", "seconds", "scripts")},
                     "identical_output_sha256": files,
                     "radio_events": Counter(json.loads(line)["type"] for line in wire.splitlines()),
                     "payload_receipts": second.count('Hello,M5Stack') if name.startswith("thread") else None,
                     "trials": {"base": 1, "candidate": 2}}
print(json.dumps(summary, indent=2))
