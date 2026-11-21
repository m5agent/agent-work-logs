#!/usr/bin/env python3
"""Upload a merged BIN to the local Device Service (dial profile) and capture serial."""
import argparse
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.request

BASE = os.environ["DEVICE_SERVICE_API"].rstrip("/")


def request(path, method="GET", payload=None, content_type="application/json", timeout=180):
    body = payload
    if isinstance(payload, (dict, list)):
        body = json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--device", default="dial")
    ap.add_argument("--owner", default="m5agent/pcf8563-446-follow")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    image = args.image.read_bytes()
    sha = hashlib.sha256(image).hexdigest()
    print("artifact sha256", sha, "size", len(image))

    st, body = request("/artifacts", "POST", image, "application/octet-stream")
    if st not in (200, 201):
        raise SystemExit(f"artifact upload failed {st}: {body[:300]}")
    art = json.loads(body)
    print("artifact_id", art.get("artifact_id"))

    st, body = request("/firmware", "POST", {
        "device_id": args.device, "kind": "merged", "artifact_id": art["artifact_id"]})
    if st not in (200, 201):
        raise SystemExit(f"firmware import failed {st}: {body[:300]}")
    fw = json.loads(body)
    print("firmware_id", fw.get("firmware_id"), "sha256", fw.get("sha256"))

    st, body = request("/sessions", "POST", {
        "device_id": args.device, "firmware_id": fw["firmware_id"], "runtime": "qemu",
        "owner": args.owner, "ttl_seconds": 240})
    if st not in (200, 201, 202):
        raise SystemExit(f"session create failed {st}: {body[:300]}")
    sess = json.loads(body)
    sid = sess["session_id"]
    print("session_id", sid)

    serial = ""
    deadline = time.time() + 240
    while time.time() < deadline:
        st, sb = request(f"/sessions/{sid}")
        state = json.loads(sb) if st == 200 else {}
        st, xb = request(f"/sessions/{sid}/serial?offset=0&limit=200000")
        serial = json.loads(xb).get("data", "") if st == 200 else ""
        if "PCF8563_446_FOLLOW_DONE" in serial or state.get("state") in ("failed", "stopped"):
            break
        time.sleep(1)

    (args.out / "serial.log").write_text(serial)
    (args.out / "session.json").write_text(json.dumps(sess, indent=1))
    st, ev = request(f"/sessions/{sid}/evidence?include=manifest,serial,logs")
    if st == 200:
        (args.out / "evidence.zip").write_bytes(ev)
    request(f"/sessions/{sid}?purge=0", "DELETE")
    print(serial)
    print("SESSION_ID", sid)


if __name__ == "__main__":
    main()
