"""Start the Nesso sender first and delay the receiver by one host second."""
from contextlib import ExitStack
from pathlib import Path
from time import sleep
import json
import subprocess
import sys
from repeat import C6_ROM, FIRMWARE, EXPECTED_NESSO, captures, number, payload_receipt, ports, sha

binary, out = map(Path, sys.argv[1:3])
out.mkdir()
local, remote = ports()
commands = {}
with ExitStack() as stack:
    procs = []
    for role, listen, dial in ((1, local, remote), (2, remote, local)):
        image = FIRMWARE / "nesso-n1" / f"lora-{role}/sketch.merged.bin"
        argv = [str(binary), "--chip", "c6", "--board", "arduino-nesso-n1",
                "--boot", "rom", "--rom", str(C6_ROM), "--flash-image", str(image),
                "--max-seconds", "16", "--console", "usb", "--no-dump",
                "--cap-peer", f"{listen}:{dial}"]
        commands[str(role)] = {"command": argv, "firmware_sha256": sha(image)}
        f = stack.enter_context((out / f"{role}.log").open("wb"))
        e = stack.enter_context((out / f"{role}.err").open("wb"))
        p = subprocess.Popen(argv, stdout=f, stderr=e)
        stack.callback(p.wait)
        stack.callback(lambda child=p: child.kill() if child.poll() is None else None)
        procs.append(p)
        if role == 1:
            sleep(1)
            assert p.poll() is None and (out / "1.log").stat().st_size == 0
    for process in procs:
        assert process.wait(timeout=100) == 0
data = captures(out / "2.log", r"\[SX1262\] Data:[ \t]+([^\n]+)")
assert number(out / "2.err", r"\blora_rx=(\d+)") == 14 and data == EXPECTED_NESSO
(out / "result.json").write_text(json.dumps({
    "status": "PASS", "receiver_host_delay_seconds": 1, "commit": sys.argv[3],
    "binary_sha256": sha(binary), "rom_sha256": sha(C6_ROM), "inputs": commands,
    **payload_receipt(data),
}, indent=2))
