import argparse
import hashlib
import io
import json
from pathlib import Path
import statistics
import re
import subprocess
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("origin")
parser.add_argument("token_file", type=Path)
parser.add_argument("cases", type=Path)
parser.add_argument("out", type=Path)
parser.add_argument("--runs", type=int, default=3)
parser.add_argument("--window", type=float, default=15)
parser.add_argument("--runtimes", nargs="+", default=["qemu", "esp32sim"])
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=True)
token = args.token_file.read_text().strip()

def api(path, payload=None, *, method=None):
    headers = {"Authorization": f"Bearer {token}"}
    if isinstance(payload, Path):
        headers.update({"Content-Type":"application/octet-stream", "X-Artifact-Name":payload.name})
        body = payload.read_bytes()
    elif payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode()
    else:
        body = None
    request = Request(args.origin + "/api/v1/" + path, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=75) as response:
            data = response.read()
            if response.headers.get_content_type() == "application/json":
                return json.loads(data)
            return data, dict(response.headers)
    except HTTPError as error:
        data = json.loads(error.read())
        raise RuntimeError(f"HTTP {error.code} {data.get('error', data.get('code', '?'))}") from None

def sha(body):
    return hashlib.sha256(body).hexdigest()

def frame(root):
    body, headers = api(root + "/frame.png")
    with Image.open(io.BytesIO(body)) as image:
        rgb = image.convert("RGB")
        if all(channel[1] == 0 for channel in rgb.getextrema()):
            return None
        digest = sha(rgb.tobytes())
    return digest, body, {k: v for k, v in headers.items() if k.lower().startswith("x-frame-")}

def measure(case, firmware_id, runtime, run):
    device, label, file, action = case
    row = dict(device=device, case=label, runtime=runtime, run=run, firmware_sha256=sha(file.read_bytes()))
    working = args.out / f"{device}-{label}-{runtime}-{run}"
    def artifact(extension):
        return working.parent / (working.name + extension)

    root = None
    try:
        t0 = time.monotonic()
        created = api("sessions", {"device_id":device, "firmware_id":firmware_id,
                                  "runtime":runtime, "ttl_seconds":240})
        root = "sessions/" + created.get("session_id", created.get("id"))
        samples = []
        frames = set()
        recent = None
        stable = 0
        offset = 0
        parts = []
        guest_ticks = {}
        while time.monotonic() - t0 < args.window:
            now = time.monotonic() - t0
            active = api(root)
            if active.get("state") == "failed":
                row["session_failure"] = active.get("error_code") or active.get("reason") or active.get("error")
                break
            if active.get("state") != "running":
                time.sleep(0.10)
                continue
            row.setdefault("running_s", now)
            serial = api(root + f"/serial?offset={offset}")
            offset = serial["next_offset"]
            parts.append(serial["data"])
            observed = time.monotonic() - t0
            for second in re.findall(r"BENCH sec=(\d+) iters=", "".join(parts)):
                guest_ticks.setdefault(int(second), observed)
            if ">>>" in "".join(parts):
                row.setdefault("repl_s", time.monotonic() - t0)
            if "MicroPython" in "".join(parts):
                row.setdefault("micropython_banner_s", time.monotonic() - t0)
            pid = active.get("pid")
            if pid and len(samples) < int(now * 2):
                stat = subprocess.run(["ps","-o","%cpu=,rss=","-p",str(pid)], text=True,capture_output=True).stdout.split()
                if len(stat) == 2:
                    samples.append([float(stat[0]), int(stat[1])])
            try:
                captured = frame(root)
            except RuntimeError as error:
                row.setdefault("frame_error", str(error))
                captured = None
            sampled = time.monotonic() - t0
            if captured:
                digest, body, headers = captured
                frames.add(digest)
                if "first_visible_s" not in row:
                    row.update(first_visible_s=sampled, first_rgb_sha256=digest, frame_headers=headers)
                    artifact(".first.png").write_bytes(body)
                if digest != recent:
                    recent = digest
                    span_start = sampled
                    stable = 1
                else:
                    stable += 1
                    if stable >= 3 and sampled - span_start >= 0.20:
                        row.setdefault("first_stable_s", span_start)
                last = body
            time.sleep(0.13)
        if len(guest_ticks) > 1:
            first, last_tick = min(guest_ticks), max(guest_ticks)
            interval = guest_ticks[last_tick] - guest_ticks[first]
            if interval > 0:
                row["guest_real_time_ratio"] = (last_tick - first) / interval
                row["guest_clock_samples"] = guest_ticks
        row["serial_sha256"] = sha("".join(parts).encode())
        artifact(".serial.log").write_text("".join(parts))
        row["unique_nonblack_frames"] = len(frames)
        if recent:
            row["last_rgb_sha256"] = recent
            artifact(".last.png").write_bytes(last)
        if samples:
            row["cpu_pct_median"] = statistics.median(v[0] for v in samples)
            row["rss_mib_median"] = statistics.median(v[1] for v in samples) / 1024
        if action and recent:
            row["input"] = action
            ti = time.monotonic()
            try:
                sequence = action if isinstance(action, list) else [[0, action]]
                for delay, payload in sequence:
                    time.sleep(delay)
                    api(root + "/input", payload)
                while time.monotonic() - ti < 5:
                    captured = frame(root)
                    if captured and captured[0] != recent:
                        row["input_to_changed_frame_s"] = time.monotonic() - ti
                        row["input_rgb_sha256"] = captured[0]
                        artifact(".input.png").write_bytes(captured[1])
                        if isinstance(action, list):
                            time.sleep(1)
                            settled = frame(root)
                            if settled:
                                row["settled_rgb_sha256"] = settled[0]
                                artifact(".settled.png").write_bytes(settled[1])
                        break
                    time.sleep(0.05)
            except RuntimeError as error:
                row["input_error"] = str(error)
        return row
    except (RuntimeError, KeyError, TypeError, TimeoutError) as error:
        row["run_error"] = str(error)
        return row
    finally:
        if root:
            try:
                archive, _ = api(root + "/evidence?include=manifest,serial,frames,logs")
                artifact(".zip").write_bytes(archive)
                row["evidence_sha256"] = sha(archive)
            except (RuntimeError, TimeoutError) as error:
                row["evidence_error"] = str(error)
            try:
                stopped = api(root + "?purge=0&retain_flash=0", method="DELETE")
                row["stop_state"] = stopped.get("state") or stopped.get("session", {}).get("state")
            except (RuntimeError, TimeoutError) as error:
                row["stop_error"] = str(error)

with (args.out / "rows.jsonl").open("a") as results:
    for entry in json.loads(args.cases.read_text()):
        device, label, raw_path, action = entry
        file = Path(raw_path)
        try:
            asset = api("artifacts", file)
            built = api("firmware", {"device_id":device,"kind":"merged",
                                     "artifact_id":asset.get("artifact_id", asset.get("id"))})
            firmware_id = built.get("firmware_id",built.get("id"))
        except (RuntimeError, OSError) as error:
            print(device, label, "intake", error, flush=True)
            continue
        for run in range(1, args.runs + 1):
            engines = args.runtimes.copy()
            if run % 2 == 0:
                engines.reverse()
            for runtime in engines:
                row = measure((device, label, file, action), firmware_id, runtime, run)
                line = json.dumps(row, sort_keys=True)
                results.write(line + "\n")
                results.flush()
                print(line, flush=True)
