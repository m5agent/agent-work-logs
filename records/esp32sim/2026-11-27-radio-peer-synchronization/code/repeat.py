"""Replay exact board binaries and verify ordered guest-visible radio payloads."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path
import re
import socket
import subprocess as sp
import sys
from time import monotonic

ROOT = Path(os.environ["RADIO_FIXTURES"]).resolve()
S3_ROM = ROOT / "roms/esp32s3_rev0_rom.elf"
C6_ROM = ROOT / "roms/esp32c6_rev0_rom.elf"
STOCK = ROOT / "uiflow253.bin"
SEED = ROOT / "mono-seed.img"
FIRMWARE = ROOT / "firmware"
CDC = Path(__file__).with_name("cdc-doc.py")
CC_BASE = ROOT / "cc1101"
EXPECTED_NESSO = ["Hello world from M5Stack!"] + [f"Hello Arduino Nesso N1 #{i}" for i in range(13)]
LOOPBACK = socket.inet_ntoa(socket.INADDR_LOOPBACK.to_bytes(4, "big"))


def sha(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def captures(path, pattern):
    return re.findall(pattern, path.read_text(errors="replace").replace("\r", ""))


def number(path, pattern):
    return int(captures(path, pattern)[-1])


def payload_receipt(payloads):
    return {"payloads": payloads, "count": len(payloads),
            "payload_sha256": sha256(json.dumps(payloads, separators=(",", ":")).encode()).hexdigest()}


def run(command, log):
    with log.open("wb") as dest:
        sp.run(command, stdout=dest, stderr=sp.STDOUT, timeout=200, check=True)


def nesso(args, out, isolated):
    paths = out / "captures"
    command = [sys.executable, args.repo / "tools/run-nesso-n1-lora.py", args.binary,
               C6_ROM, FIRMWARE / "nesso-n1", paths, "--commit", args.commit]
    run(command + (["--isolated"] if isolated else []), out / "runner.log")
    receipt = json.loads((paths / "run.json").read_text())
    assert all(row["exit"] == 0 for row in receipt["cases"].values()), receipt
    tx = number(paths / "lora-1.err", r"\blora_tx=(\d+)")
    rx = number(paths / "lora-2.err", r"\blora_rx=(\d+)")
    data = captures(paths / "lora-2.log", r"\[SX1262\] Data:[ \t]+([^\n]+)")
    assert tx == 14 and rx == len(data) and data == ([] if isolated else EXPECTED_NESSO), (tx, rx, data)
    return {"tx": tx, **payload_receipt(data)}


def paper(args, out):
    paths = out / "captures"
    run([args.repo / "tools/run-papermono-docs.sh", args.binary, FIRMWARE / "papermono", paths,
         "--rom-dir", ROOT / "roms", "--source", args.commit, "--sd", SEED,
         "--case", "lora-1", "--case", "lora-2"], out / "runner.log")
    run([sys.executable, args.repo / "tools/check-paper-docs.py", paths], out / "checker.log")
    data = captures(paths / "lora-2.log", r"\[LoRa RX\] Data: ([^\n]+)")
    tx = number(paths / "lora-1.log", r"\bLoRa tx=(\d+)")
    isolated = number(paths / "lora-2-control.log", r"\bLoRa tx=0 rx=(\d+)")
    assert data == [f"Hello PaperMono #{i}" for i in range(1, 5)] and tx == 4 and isolated == 0
    return {"tx": tx, "isolated": isolated, **payload_receipt(data)}


def cap_source(cap, role):
    if cap == "cc1101":
        return CC_BASE / f"cc1101_cap_rf_{role}_example.py"
    return ROOT / "adv-docs" / f"cardputer_adv_{cap}_cap_{role}_example/source.py"


def ports():
    with socket.socket() as a, socket.socket() as b:
        a.bind((LOOPBACK, 0))
        b.bind((LOOPBACK, 0))
        result = a.getsockname()[1], b.getsockname()[1]
        return result


def cap(args, out, variant, isolated=False):
    subghz = variant == "cc1101"
    proc = []
    port_pair = ports()
    notes = {}
    with ExitStack() as stack:
        for index, side in enumerate(("rx", "tx") if subghz else ("receiver", "sender")):
            dest = out / side
            dest.mkdir()
            original = cap_source(variant, side)
            source = original.read_bytes()
            if subghz and not index:
                # Observe successful reads at the existing CRC-checked branch.
                site = b"        if cc1101_data.crc_ok:\n"
                assert source.count(site) == 1
                source = source.replace(site, site + b"            print('PAIR_RX_HEX', bytes(cc1101_data.data).hex())\n")
            (dest / "source.py").write_bytes(source)
            source_hash = sha(dest / "source.py")
            host = sp.check_output([sys.executable, CDC, "source.py", source_hash], cwd=dest)
            if subghz and not index:
                host = host.replace(b"cdc 6500\n", b"cdc 11000\n")
            if subghz and index:
                # Give the receiver's longer setup a deterministic guest-time head start.
                host = host.replace(b"cdc 3000\n", b"cdc 4800\n", 1)
            if not subghz and not index:
                # Inspect the original example's receive callback variable after
                # the scripted send, via the same guest CDC REPL.
                host = host.removesuffix(b"cdc 6500\n") + (
                    b"cdc 8000\ncdc 200 \x03\n"
                    b"cdc 10 print('PAIR_RX_HEX', lora_data.hex() if lora_data else 'none')\x04\ncdc 400\n")
            (dest / "cdc.txt").write_bytes(host)
            command = [args.binary, "--chip", "s3", "--board", "m5stack-cardputer-adv",
                       "--boot", "rom", "--rom", S3_ROM, "--flash-image", STOCK,
                       "--console", "both", "--usb-host", "cdc.txt", "--cap", variant,
                       "--max-seconds", ("13.8" if subghz else "12") if index else "17", "--no-dump", "--tft-png", "frame.png"]
            if not isolated:
                local, remote = port_pair if index else port_pair[::-1]
                command += ["--cap-peer", f"{local}:{remote}"]
            if index and not subghz:
                (dest / "keys.txt").write_text("7.0 key w 150\n7.3 key a 150\n7.6 key s 150\n7.9 key m 150\n8.2 key enter 150\n")
                command += ["--script", "keys.txt"]
            stdout = stack.enter_context((dest / "serial.log").open("wb"))
            stderr = stack.enter_context((dest / "runtime.log").open("wb"))
            child = sp.Popen(command, cwd=dest, stdout=stdout, stderr=stderr)
            stack.callback(child.wait)
            stack.callback(lambda p=child: p.kill() if p.poll() is None else None)
            proc.append((dest, child))
            notes[side] = {"source_sha256": source_hash, "original_sha256": sha(original),
                           "cdc_sha256": sha(dest / "cdc.txt"), "command": list(map(str, command))}
        (out / "inputs.json").write_text(json.dumps(notes, indent=2))
        for dest, child in proc:
            assert child.wait(timeout=140) == 0, dest
    receiver, sender = [dest for dest, _ in proc]
    rx = number(receiver / "runtime.log", rf"CAP {variant}: .*? (\d+) RX,")
    tx = number(sender / "runtime.log", rf"CAP {variant}: .*? (\d+) TX ")
    hexes = captures(receiver / "serial.log", r"(?:^|\n|>OK)PAIR_RX_HEX ([0-9a-f]+)\b")
    decoded = [bytes.fromhex(frame).decode() for frame in hexes]
    assert rx == len(decoded) and tx > 0, (tx, rx, decoded)
    if isolated:
        assert rx == 0, decoded
    elif not subghz:
        assert tx == rx == 1 and decoded == ["wasm"], (tx, rx, decoded)
    else:
        assert rx == tx and decoded == [f"CC1101, SEQ={i}, Hello" for i in range(tx)], (tx, rx, decoded)
    return {"tx": tx, **payload_receipt(decoded)}


def trial(args, round_number, lane, fun):
    case = args.output / f"{round_number:02d}-{lane}"
    case.mkdir()
    start = monotonic()
    try:
        record = {"status": "PASS", **fun(args, case)}
    except Exception as e:
        record = {"status": "FAIL", "error": str(e)}
    record.update(round=round_number, lane=lane, wall_s=round(monotonic() - start, 3))
    (case / "result.json").write_text(json.dumps(record, indent=2))
    print(round_number, lane, record, flush=True)
    return record


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "binary", "output"):
        cli.add_argument(name, type=Path)
    cli.add_argument("--commit", required=True)
    cli.add_argument("--rounds", type=int, default=10)
    cli.add_argument("--only", nargs="+")
    cli.add_argument("--load", type=int, default=0, help="concurrent CPU stress workers")
    args = cli.parse_args()
    args.output.mkdir()
    lanes = {"nesso": lambda a, o: nesso(a, o, False), "paper": paper,
             "nesso-isolated": lambda a, o: nesso(a, o, True)}
    for variant in ("lora1262", "lora868", "cc1101"):
        lanes[variant] = lambda a, o, v=variant: cap(a, o, v)
        lanes[f"{variant}-isolated"] = lambda a, o, v=variant: cap(a, o, v, True)
    if args.only:
        lanes = {name: lanes[name] for name in args.only}
    assets = [args.binary, S3_ROM, C6_ROM, STOCK, SEED, CDC]
    assets.extend(FIRMWARE / board / role / "sketch.merged.bin"
                  for board in ("papermono", "nesso-n1") for role in ("lora-1", "lora-2"))
    assets.extend(cap_source(variant, role) for variant in ("lora1262", "lora868", "cc1101")
                  for role in (("rx", "tx") if variant == "cc1101" else ("receiver", "sender")))
    receipt = {"commit": args.commit, "load_workers": args.load, "cpu_count": os.cpu_count(),
               "runtime_sha256": sha(args.binary), "assets": {str(path): sha(path) for path in assets}}
    (args.output / "inputs.json").write_text(json.dumps(receipt, indent=2))
    results = []
    with ExitStack() as stack:
        for _ in range(args.load):
            load = sp.Popen(["yes"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            stack.callback(load.wait)
            stack.callback(load.terminate)
        pool = stack.enter_context(ThreadPoolExecutor(max_workers=min(5, len(lanes))))
        for i in range(1, args.rounds + 1):
            waiting = [pool.submit(trial, args, i, lane, fun) for lane, fun in lanes.items()]
            results.extend(job.result() for job in waiting)
    (args.output / "results.json").write_text(json.dumps(results, indent=2))
    assert all(row["status"] == "PASS" for row in results)
    for lane in lanes:
        matched = {(row["count"], row["payload_sha256"]) for row in results if row["lane"] == lane}
        assert len(matched) == 1, (lane, matched)


if __name__ == "__main__":
    main()
