#!/usr/bin/env python3
"""Run one merged firmware on the local Device Service nesso-n1 esp32sim profile."""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("DEVICE_SERVICE_API", "http://<device-service>/api/v1")


def req(method, path, body=None, headers=None, raw=False):
    url = BASE + path
    data = None
    hdrs = dict(headers or {})
    if body is not None:
        if raw:
            data = body
        else:
            data = json.dumps(body).encode()
            hdrs.setdefault("Content-Type", "application/json")
    r = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            content = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            if "application/json" in ctype:
                return resp.status, json.loads(content)
            return resp.status, content
    except urllib.error.HTTPError as e:
        content = e.read()
        try:
            return e.code, json.loads(content)
        except Exception:
            return e.code, content


def main():
    bin_path, label = sys.argv[1], sys.argv[2]
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence", label)
    os.makedirs(outdir, exist_ok=True)
    blob = open(bin_path, "rb").read()
    sha = hashlib.sha256(blob).hexdigest()
    name = f"pr452-{label}-merged.bin"

    st, art = req("POST", "/artifacts", blob,
                  {"Content-Type": "application/octet-stream", "X-Artifact-Name": name}, raw=True)
    print("artifact", st, art, flush=True)
    assert st in (200, 201), art
    st, fw = req("POST", "/firmware", {"device_id": "nesso-n1", "kind": "merged",
                                       "artifact_id": art["artifact_id"]})
    print("firmware", st, fw, flush=True)
    assert st in (200, 201, 202), fw
    fw_id = fw.get("firmware_id") or fw.get("id")

    body = {
        "device_id": "nesso-n1",
        "firmware_id": fw_id,
        "runtime": "esp32sim",
        "ttl_seconds": 240,
        "ready_marker": "done",
        "ready_timeout_seconds": 120,
        "owner": "m5agent/pr452-review",
    }
    st, sess = req("POST", "/sessions", body)
    print("session", st, sess, flush=True)
    assert st in (200, 201, 202), sess
    sid = sess["session_id"] if "session_id" in sess else sess["id"]
    try:
        st, waited = req("POST", f"/sessions/{sid}/wait",
                         {"ready_marker": "done", "timeout_seconds": 120})
        print("wait", st, waited.get("state") if isinstance(waited, dict) else waited, flush=True)
        time.sleep(3)
        st, serial = req("GET", f"/sessions/{sid}/serial?offset=0&limit=200000")
        if isinstance(serial, dict):
            serial_text = serial.get("data") or serial.get("text") or json.dumps(serial)
        else:
            serial_text = serial.decode("utf-8", "replace")
        open(os.path.join(outdir, "serial.txt"), "w").write(serial_text)
        print(serial_text, flush=True)
        st, frame = req("GET", f"/sessions/{sid}/frame.png")
        if st == 200 and isinstance(frame, bytes):
            open(os.path.join(outdir, "frame.png"), "wb").write(frame)
        st, state = req("GET", f"/sessions/{sid}")
        json.dump({"artifact": art, "firmware": fw, "session": state},
                  open(os.path.join(outdir, "session.json"), "w"), indent=1)
        print("state", st, state.get("state"), flush=True)
    finally:
        st, stopped = req("DELETE", f"/sessions/{sid}")
        print("stop", st, stopped if isinstance(stopped, dict) else stopped, flush=True)


if __name__ == "__main__":
    main()
