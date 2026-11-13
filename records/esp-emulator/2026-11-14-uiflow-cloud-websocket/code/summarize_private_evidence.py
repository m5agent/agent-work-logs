#!/usr/bin/env python3
"""Produce a bounded public summary from private Device Service evidence.

Python 3.12+ and the pinned esp-emulator checkout are required. This program is
strictly offline. Input/output paths and arbitrary captured strings are never
included in the output. Original ZIP, serial, frames and identities stay private.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import struct
import sys
import zipfile

MAX_ZIP = 64 * 1024 * 1024
MAX_SERIAL = 8 * 1024 * 1024
MAX_METADATA = 1024 * 1024
NO_PONG = b"Error, no PONG received for more than 120 seconds after PING"
LABELS = ("default-baseline", "authorized-identity", "candidate-default",
          "candidate-authorized", "follow-up")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value, length=64):
    return value if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % length, value) else None


def load_json(path):
    with Path(path).open("rb") as source:
        data = source.read(MAX_METADATA + 1)
    if len(data) > MAX_METADATA:
        raise ValueError("metadata_limit")
    return json.loads(data)


def member(archive, name, limit):
    if archive.getinfo(name).file_size > limit:
        raise ValueError("member_limit")
    with archive.open(name) as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("member_limit")
    return data


def load_observer(tools_dir):
    path = Path(tools_dir) / "uiflow_cloud_status.py"
    spec = importlib.util.spec_from_file_location("_record_cloud_observer", path)
    if spec is None or spec.loader is None:
        raise ValueError("observer_unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, sha(path.read_bytes())


def relative_packets(data, observer):
    # The observer has already validated the PCAP format and bounded packet count.
    endian = observer._MAGIC[data[:4]]
    first, offset, rows = None, 24, {}
    scale = 1_000_000_000 if data[:4] in (b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d") else 1_000_000
    while offset + 16 <= len(data):
        seconds, fraction, size, _ = struct.unpack_from(endian + "IIII", data, offset)
        offset += 16
        if size > len(data) - offset:
            break
        time = seconds + fraction / scale
        first = time if first is None else first
        frame = data[offset:offset + size]
        offset += size
        rows[len(rows) + 1] = (round(time - first, 6), frame)
    return rows


_STATES = {"not_observed", "identity_rejected", "server_error", "heartbeat_observed", "handshake_observed", "disconnected"}
_REASONS = {None, "mac_not_bound", "mac_not_found", "server_error"}
_OBSERVATION_REASONS = {None, "stream_bytes_limit", "stream_gap", "stream_conflict", "malformed_packet", "fragmented_ip", "malformed_pcap", "unsupported_pcap", "packet_limit", "stream_limit", "capture_partial_tail", "http_bytes_limit", "malformed_http", "malformed_websocket", "message_bytes_limit", "protocol_partial", "unsupported_websocket", "unrecognized_message", "malformed_mqtt", "capture_bytes_limit", "malformed_protocol", "capture_unavailable"}

def count(value):
    return value if type(value) is int and 0 <= value <= 64 * 1024 * 1024 else 0

def safe_status(value):
    # A whitelist protects future reuse even if the observer gains extra fields.
    pairing, webrepl, observation = value.get("pairing", {}), value.get("webrepl", {}), value.get("observation", {})
    return {
        "source": "guest-pcap",
        "state": value.get("state") if value.get("state") in ("observed", "not_observed", "unavailable") else "unavailable",
        "pairing": {"state": "code_received" if pairing.get("state") == "code_received" else "not_observed"},
        "webrepl": {
            "state": webrepl.get("state") if webrepl.get("state") in _STATES else "not_observed",
            "reason": webrepl.get("reason") if webrepl.get("reason") in _REASONS else None,
            "device_registered": webrepl.get("device_registered") is True,
            **{key: count(webrepl.get(key)) for key in ("handshakes", "disconnects", "heartbeat_roundtrips", "protocol_ping_sent", "protocol_pong_received", "protocol_ping_without_pong_count")},
        },
        "observation": {
            "status": observation.get("status") if observation.get("status") in ("complete", "partial", "unavailable") else "unavailable",
            "reason": observation.get("reason") if observation.get("reason") in _OBSERVATION_REASONS else "malformed_protocol",
            **{key: count(observation.get(key)) for key in ("capture_bytes", "packets", "tcp_streams", "unsupported_packets")},
            **{key: observation.get(key) is True for key in ("partial_tail", "partial_stream", "protocol_unknown")},
        },
    }

def protocol_details(data, observer, status):
    if status["state"] == "unavailable":
        return {"state": "unavailable", "connections": []}
    observation = observer._blank(len(data))["observation"]
    packets = relative_packets(data, observer)
    connections = observer._connections(data, observation)
    rows, errors = [], Counter()
    for connection in connections:
        if connection.port != 80:
            continue
        result = observer._websocket(connection, observation)
        if result is None:
            continue
        client, client_orders = connection.client.assemble()
        server, server_orders = connection.server.assemble()
        request_end = observer._http(client)[2]
        response_end = observer._http(server)[2]
        outgoing = observer._ws_messages(client[request_end:], client_orders[request_end:], True, observation)
        incoming = observer._ws_messages(server[response_end:], server_orders[response_end:], False, observation)
        if result["reason"]:
            errors[result["reason"]] += 1
        first_close = None
        if connection.close_order is not None:
            time, frame = packets[connection.close_order]
            packet = observer._packet(frame, observation)
            first_close = {
                "kind": "fin" if packet[5] & 1 else "rst",
                "initiator": "server" if packet[2] == 80 else "guest",
                "capture_seconds": time,
                "seconds_from_connection_start": round(time - packets[connection.order][0], 6),
            }
        ping_times = [packets[order][0] for op, _, order in outgoing if op == 9]
        text_pings = [order for op, payload, order in outgoing if op == 1 and payload == b"PING"]
        text_pongs = [order for op, payload, order in incoming if op == 1 and payload == b"PONG"]
        close = connection.close_order
        waiting, text_roundtrips = 0, 0
        for order, is_ping in sorted([(order, True) for order in text_pings] + [(order, False) for order in text_pongs]):
            if close is not None and order >= close:
                continue
            if is_ping:
                waiting += 1
            elif waiting:
                waiting -= 1
                text_roundtrips += 1
        rows.append({
            "ordinal": len(rows) + 1,
            "handshake_valid": True,
            "state": result["state"],
            "reason": result["reason"],
            "device_registered_observed": result["device_registered"],
            "first_close": first_close,
            "guest_text_ping_count": len(text_pings),
            "server_text_pong_count": len(text_pongs),
            "text_roundtrips_before_close": text_roundtrips,
            "protocol_ping_sent": result["protocol_ping_sent"],
            "protocol_pong_received": result["protocol_pong_received"],
            "protocol_ping_without_pong_count": result["protocol_ping_without_pong_count"],
            "first_protocol_ping_seconds": ping_times[0] if ping_times else None,
            "first_close_after_first_protocol_ping_seconds": round(first_close["capture_seconds"] - ping_times[0], 6)
            if first_close is not None and ping_times else None,
        })
    closes = [row["first_close"] for row in rows if row["first_close"] is not None]
    return {
        "state": "observed" if rows else "not_observed",
        "capture_duration_seconds": packets[len(packets)][0] if packets else None,
        "valid_handshakes": len(rows),
        "error_counts": dict(errors),
        "server_first_fin_count": sum(close["kind"] == "fin" and close["initiator"] == "server" for close in closes),
        "guest_first_fin_count": sum(close["kind"] == "fin" and close["initiator"] == "guest" for close in closes),
        "text_roundtrips_before_close": sum(row["text_roundtrips_before_close"] for row in rows),
        "protocol_ping_sent": sum(row["protocol_ping_sent"] for row in rows),
        "protocol_pong_received": sum(row["protocol_pong_received"] for row in rows),
        "connections": rows,
    }


def summarize(args):
    observer, observer_hash = load_observer(args.tools_dir)
    path = Path(args.zip)
    if path.stat().st_size > MAX_ZIP:
        raise ValueError("zip_limit")
    with path.open("rb") as stream:
        raw = stream.read(MAX_ZIP + 1)
    if len(raw) > MAX_ZIP:
        raise ValueError("zip_limit")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        data = member(archive, "network/capture.pcap", observer.MAX_CAPTURE_BYTES)
        serial = member(archive, "serial.log", MAX_SERIAL)
        manifest = json.loads(member(archive, "manifest.json", MAX_METADATA))
    session = manifest.get("session", {})
    startup = session.get("uiflow_startup") or {}
    status = observer.observe_uiflow_cloud_pcap(data)
    runtime = load_json(args.runtime_identity) if args.runtime_identity else {}
    terminal = load_json(args.terminal_state) if args.terminal_state else {}
    return {
        "schema_version": 1,
        "kind": "redacted-uiflow-websocket-evidence-summary",
        "case": args.case,
        "validation": "virtual-device validation",
        "guest_source_commit": digest(args.source_commit, 40),
        "source_commit_provenance": "operator-supplied",
        "observer_source_commit": digest(args.observer_source_commit, 40),
        "observer_module_sha256": observer_hash,
        "firmware_sha256": digest(startup.get("reference_sha256")),
        "normalized_firmware_sha256": digest(session.get("firmware_sha256")),
        "runtime_sha256": digest(runtime.get("binary_sha256", runtime.get("sha256"))),
        "evidence_zip": {"sha256": sha(raw), "bytes": len(raw)},
        "pcap": {"sha256": sha(data), "bytes": len(data)},
        "serial": {
            "sha256": sha(serial), "bytes": len(serial),
            "receive_error_count": serial.count(b"websocket_client: Error receive data"),
            "control_pong_timeout_120s_marker_count": serial.count(NO_PONG),
            "marker_definition": "control_pong_timeout_120s",
        },
        "observer_status": safe_status(status),
        "protocol": protocol_details(data, observer, status),
        "cleanup": {"state": "stopped" if terminal.get("state") == "stopped" else "not_verified",
                    "flash_released": terminal.get("flash_retained") is False if terminal else None},
        "limits": {"zip_bytes": MAX_ZIP, "capture_bytes": observer.MAX_CAPTURE_BYTES,
                   "serial_bytes": MAX_SERIAL, "directional_tcp_streams": observer.MAX_TCP_STREAMS,
                   "tcp_stream_bytes": observer.MAX_STREAM_BYTES},
        "not_claimed": ["account_binding_from_pairing_code", "remote_repl_execution", "physical_hardware", "long_term_stability"],
        "redaction": "No MAC, IP, endpoint, session, task, host path, pairing code, credential, device identifier, raw header or raw peer body is included.",
    }


class _SafeParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"state":"unavailable","reason":"invalid_arguments"}\n')

def main():
    parser = _SafeParser(description=__doc__)
    parser.add_argument("--tools-dir", required=True)
    parser.add_argument("--zip", required=True)
    parser.add_argument("--case", required=True, choices=LABELS)
    parser.add_argument("--source-commit")
    parser.add_argument("--observer-source-commit")
    parser.add_argument("--runtime-identity")
    parser.add_argument("--terminal-state")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = summarize(args)
        encoded = json.dumps(result, indent=2) + "\n"
        if len(encoded.encode()) > 64 * 1024:
            raise ValueError("output_limit")
        Path(args.output).write_text(encoded, encoding="utf-8")
    except Exception:
        # A private input path, exception detail, or captured string must not leak.
        print('{"state":"unavailable","reason":"summary_generation_failed"}', file=sys.stderr)
        return 2
    print(json.dumps({"state": "written", "summary_sha256": sha(encoded.encode()), "summary_bytes": len(encoded.encode())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
