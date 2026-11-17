#!/usr/bin/env python3
"""Run an ESPHome host build against a simulated M5Stack Chain bus (pty).

Usage: ESPHOME_BIN=/path/to/esphome python3 emulate.py host.yaml [noevents]

The pty port is substituted into the YAML `uart.port` before compiling, so the
run needs a rebuild whenever the pty number changes.

The fake chain nodes answer the frames the three chain components send and
inject 0xE0 event reports at scripted times, so the component parsing and the
binary-sensor mapping can be observed from the ESPHome log output.
"""
import os
import pty
import re
import select
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))

HEAD = b"\xaa\x55"
TAIL = b"\x55\xaa"


def crc(index, cmd, data):
    return (index + cmd + sum(data)) & 0xFF


def frame(index, cmd, data=b""):
    length = 3 + len(data)
    body = bytes([length & 0xFF, length >> 8, index, cmd]) + bytes(data)
    return HEAD + body + bytes([crc(index, cmd, data)]) + TAIL


def parse(buf, requests):
    """Extract complete frames from buf; append (index, cmd, data) to requests.

    Returns the unconsumed remainder.
    """
    while True:
        start = buf.find(HEAD)
        if start < 0:
            return b""
        buf = buf[start:]
        if len(buf) < 6:
            return buf
        length = buf[2] | (buf[3] << 8)
        if length < 3 or length > 0x100:
            buf = buf[1:]
            continue
        total = length + 6
        if len(buf) < total:
            return buf
        packet = buf[:total]
        if packet[-2:] != TAIL:
            buf = buf[1:]
            continue
        index, cmd = packet[4], packet[5]
        data = packet[6:-3]
        if packet[-3] == crc(index, cmd, data):
            requests.append((index, cmd, bytes(data)))
            buf = buf[total:]
        else:
            buf = buf[1:]


READS = {
    (1, 0x30): bytes([0x2E, 0x09, 45]),                                  # AHT20: 2350 = 23.50 C, 45 %
    (1, 0x31): bytes([0x60, 0x09, 0x94, 0x27, 0xD2, 0x04, 0, 0]),        # SPA06: 24.00 C, 1013.2 hPa, 12.34 m
    (2, 0x30): bytes([0xD2, 0x04, 0, 0]),                                # DLight: 1234 lx
    (3, 0x30): bytes([0, 0, 0, 0, 0xE8, 0x03]),                          # accel mg: 0, 0, 1000
    (3, 0x31): bytes([10, 0, 0xF6, 0xFF, 30, 0]),                        # gyro dps: 10, -20, 30
    (3, 0x34): bytes([0xBE, 0x0A]),                                      # temperature 2750 = 27.50 C
}

SETTINGS = {0x36, 0xE1, 0xE3, 0xE5, 0xE7, 0xE9, 0x35, 0x37, 0x39, 0x3B, 0x20, 0x22, 0x31, 0x33}

# (seconds after start, index, payload of the 0xE0 report)
EVENTS = [
    (3.0, 1, b"\x01\x0f"),  # ENV temperature high active
    (3.6, 1, b"\x00\x0f"),  # ENV temperature high release
    (4.0, 3, b"\x03\x10"),  # IMU motion + rotation active
    (4.6, 3, b"\x04\x10"),  # IMU motion/rotation release, temperature high active
    (5.0, 3, b"\x00\x10"),  # IMU temperature release
    (5.4, 2, b"\x00"),      # DLight low active
    (5.8, 2, b"\x02"),      # DLight low release
    (6.2, 2, b"\x01"),      # DLight high active
    (6.6, 2, b"\x03"),      # DLight high release
]


def run(config_name, duration=8.0):
    master, slave = pty.openpty()
    port = os.ttyname(slave)
    out_master, out_slave = pty.openpty()

    yaml_path = os.path.join(BASE, config_name)
    with open(yaml_path) as f:
        text = f.read()
    text = re.sub(r"(?m)^(\s*port:\s*).*$", r"\1" + port, text, count=1)
    run_yaml = os.path.join(BASE, "run-" + config_name)
    with open(run_yaml, "w") as f:
        f.write(text)

    esphome_bin = os.environ.get("ESPHOME_BIN", "esphome")
    build = subprocess.run(
        [esphome_bin, "compile", run_yaml],
        capture_output=True,
        text=True,
    )
    if build.returncode != 0:
        print("BUILD FAILED")
        print(build.stdout[-4000:])
        return None

    program = os.path.join(BASE, ".esphome/build/chain-host/.pioenvs/chain-host/program")
    proc = subprocess.Popen(
        [program],
        stdin=subprocess.DEVNULL,
        stdout=out_slave,
        stderr=out_slave,
        close_fds=True,
    )
    os.close(out_slave)

    requests = []
    log_lines = []
    buf = b""
    logbuf = b""
    start = time.time()
    pending = list(EVENTS)
    while time.time() - start < duration:
        elapsed = time.time() - start
        while pending and elapsed >= pending[0][0]:
            _, index, payload = pending.pop(0)
            os.write(master, frame(index, 0xE0, payload))
            log_lines.append("### injected 0xE0 index=%d payload=%s" % (index, payload.hex()))
        r, _, _ = select.select([master, out_master], [], [], 0.02)
        for fd in r:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                continue
            if fd == master:
                buf += chunk
                new = []
                buf = parse(buf, new)
                for index, cmd, data in new:
                    if (index, cmd) in READS:
                        os.write(master, frame(index, cmd, READS[(index, cmd)]))
                        log_lines.append("REQ idx=%d cmd=0x%02X %s -> reading" % (index, cmd, data.hex()))
                    elif cmd in SETTINGS:
                        os.write(master, frame(index, cmd, b"\x01"))
                        log_lines.append("REQ idx=%d cmd=0x%02X %s -> ok" % (index, cmd, data.hex()))
                    else:
                        log_lines.append("REQ idx=%d cmd=0x%02X %s -> (no answer)" % (index, cmd, data.hex()))
            else:
                logbuf += chunk
                while b"\n" in logbuf:
                    line, logbuf = logbuf.split(b"\n", 1)
                    log_lines.append("LOG " + line.decode("utf-8", "replace"))

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    os.close(master)
    os.close(slave)
    os.close(out_master)
    return log_lines


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "noevents":
        EVENTS.clear()
    lines = run(sys.argv[1] if len(sys.argv) > 1 else "host.yaml")
    if lines is not None:
        print("\n".join(lines))
