#!/usr/bin/env python3
"""Upload the merged BIN to a Device Service instance and capture the serial log.

Required environment:
  DEVICE_SERVICE_API   API base ending in /api/v1 (e.g. http://host:port/api/v1)
Optional arguments:
  --image   merged flash image (default: build/merged-binary.bin)
  --out     directory for serial.log, manifest.json and evidence.zip
  --device  device profile id (default: dial)
"""
import argparse
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.request


def request(base, path, method="GET", payload=None, content_type="application/json", timeout=120):
    body = payload
    if isinstance(payload, (dict, list)):
        body = json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=pathlib.Path, default=pathlib.Path("build/merged-binary.bin"))
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("run"))
    parser.add_argument("--device", default="dial")
    args = parser.parse_args()

    base = os.environ["DEVICE_SERVICE_API"].rstrip("/")
    args.out.mkdir(parents=True, exist_ok=True)
    image = args.image.read_bytes()
    print("image", len(image), hashlib.sha256(image).hexdigest())

    status, body = request(base, "/artifacts", "POST", image, "application/octet-stream")
    if status not in (200, 201):
        raise SystemExit(f"artifact upload failed: {status} {body[:300]}")
    artifact = json.loads(body)

    status, body = request(base, "/firmware", "POST", {
        "device_id": args.device,
        "kind": "merged",
        "artifact_id": artifact["artifact_id"],
    })
    if status not in (200, 201):
        raise SystemExit(f"firmware import failed: {status} {body[:300]}")
    firmware = json.loads(body)

    status, body = request(base, "/sessions", "POST", {
        "device_id": args.device,
        "firmware_id": firmware["firmware_id"],
        "runtime": "qemu",
        "owner": "pcf8563-issue-446",
        "ttl_seconds": 240,
    })
    if status not in (200, 201, 202):
        raise SystemExit(f"session create failed: {status} {body[:300]}")
    session = json.loads(body)
    session_id = session["session_id"]
    print("SESSION", session_id)

    serial = ""
    deadline = time.time() + 180
    while time.time() < deadline:
        _, state_body = request(base, f"/sessions/{session_id}")
        state = json.loads(state_body)
        _, serial_body = request(base, f"/sessions/{session_id}/serial?offset=0&limit=200000")
        serial = json.loads(serial_body).get("data", "")
        if "PCF8563_446_DONE" in serial or state.get("state") in ("failed", "stopped"):
            break
        time.sleep(1)

    print(serial)
    (args.out / "serial.log").write_text(serial)
    (args.out / "session.json").write_text(json.dumps(session, indent=1))
    status, evidence = request(base, f"/sessions/{session_id}/evidence?include=manifest,serial,logs")
    if status == 200:
        (args.out / "evidence.zip").write_bytes(evidence)
    print("SESSION_ID", session_id)


if __name__ == "__main__":
    main()
