"""Isolated UART1 PN532 startup peer. Only answer recognized valid frames."""
from hashlib import sha256
from pathlib import Path
import json
import socket
import sys
from threading import Thread
import time

PREAMBLE = bytes.fromhex("0000ff")
ACK = bytes.fromhex("0000ff00ff00")
SAM_NORMAL = bytes.fromhex("d41401")
GET_FIRMWARE_VERSION = bytes.fromhex("d402")
KILLER_CHECK = bytes.fromhex("d4aa")


def frame(body):
    return PREAMBLE + bytes((len(body), -len(body) & 255)) + body + bytes((-sum(body) & 255, 0))


def parse(buffer):
    while True:
        start = buffer.find(PREAMBLE)
        if start == -1:
            del buffer[:max(0, len(buffer) - 2)]
            return
        del buffer[:start]
        if len(buffer) < 5:
            return
        length, length_check = buffer[3:5]
        if (length == 0 and length_check == 255) or (length == 255 and length_check == 0):
            if len(buffer) < 6:
                return
            yield bytes(buffer[:6]), None
            del buffer[:6]
            continue
        if (length + length_check) & 255:
            del buffer[0]
            continue
        if len(buffer) < 7 + length:
            return
        wire = bytes(buffer[:7 + length])
        del buffer[:7 + length]
        payload = wire[5:5 + length]
        if (sum(payload) + wire[-2]) & 255 or wire[-1] != 0:
            yield wire, None
            continue
        yield wire, payload


class Peer:
    def __init__(self, stage, out, qemu, mode):
        self.out = out
        self.mode = mode
        self.events = []
        self.received = bytearray()
        self.sent = bytearray()
        self.error = None
        self.socket_path = stage / "pn532.sock"
        self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.listener.bind(str(self.socket_path))
        self.listener.listen(1)
        self.listener.settimeout(30)
        self.connection = None
        self.wrapper = self.create_wrapper(stage, qemu)
        self.started = time.monotonic()
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    def create_wrapper(self, stage, qemu):
        wrapper = stage / "qemu-system-riscv32"
        wrapper.write_text(f"""#!{sys.executable}
import os
from pathlib import Path
import sys

qemu = {str(qemu)!r}
args = sys.argv[1:]
uart1 = [(i, arg) for i, arg in enumerate(args) if i > 0 and args[i - 1] == "-serial" and
         arg.startswith("file:") and Path(arg[5:]).name == "serial1.log"]
if uart1:
    (index, original), = uart1
    socket = "socket,id=isolated-uart1,path=" + {str(self.socket_path)!r} + ",server=off,logfile=" + original[5:]
    args[index - 1:index + 1] = ["-chardev", socket, "-serial", "chardev:isolated-uart1"]
os.execv(qemu, [qemu, *args])
""")
        wrapper.chmod(0o700)
        return wrapper

    def log(self, direction, wire, payload):
        self.events.append(
            {"elapsed_seconds": round(time.monotonic() - self.started, 6),
             "direction": direction, "wire_hex": wire.hex(),
             "payload_hex": payload.hex() if payload is not None else None}
        )

    def transmit(self, wire, payload=None):
        self.connection.sendall(wire)
        self.sent.extend(wire)
        self.log("peer_to_uart1", wire, payload)

    def run(self):
        buffer = bytearray()
        sam_seen = False
        try:
            self.connection, _ = self.listener.accept()
            self.connection.settimeout(20)
            while True:
                try:
                    chunk = self.connection.recv(256)
                except socket.timeout:
                    continue
                if not chunk:
                    break
                self.received.extend(chunk)
                buffer.extend(chunk)
                for wire, payload in parse(buffer):
                    self.log("uart1_to_peer", wire, payload)
                    if self.mode == "silent":
                        continue
                    response = None
                    if payload == KILLER_CHECK and self.mode in {"killer", "response-only", "bad-dcs"}:
                        response = bytes.fromhex("d5ab")
                    elif payload == SAM_NORMAL:
                        response = bytes.fromhex("d515")
                        sam_seen = True
                    elif payload == GET_FIRMWARE_VERSION and sam_seen:
                        response = bytes.fromhex("d50332010507")
                    if response is None:
                        continue
                    if self.mode != "response-only":
                        self.transmit(ACK)
                        time.sleep(.008)
                    reply = frame(response)
                    if self.mode == "bad-dcs":
                        reply = reply[:-2] + bytes((reply[-2] ^ 1, 0))
                    self.transmit(reply, response)
        except OSError as error:
            self.error = str(error)
        finally:
            if self.connection:
                self.connection.close()

    def close(self):
        self.thread.join(3)
        if self.thread.is_alive() and self.connection:
            self.connection.shutdown(socket.SHUT_RDWR)
            self.thread.join(2)
        self.listener.close()
        events = (json.dumps(self.events, indent=2) + "\n").encode()
        (self.out / "uart1-events.json").write_bytes(events)
        (self.out / "uart1-guest-tx.bin").write_bytes(self.received)
        (self.out / "uart1-peer-tx.bin").write_bytes(self.sent)
        return {
            "event_sha256": sha256(events).hexdigest(), "guest_tx_sha256": sha256(self.received).hexdigest(),
            "peer_tx_sha256": sha256(self.sent).hexdigest(), "guest_tx_bytes": len(self.received),
            "peer_tx_bytes": len(self.sent), "events": len(self.events), "error": self.error,
            "thread_exited": not self.thread.is_alive(),
        }
