"""Build a public summary of measured values without copying raw device data."""
import collections
import hashlib
import json
from pathlib import Path
import statistics
import sys
import zipfile

base = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

def decode_rows(name):
    receipt = base / name / 'rows.jsonl'
    if receipt.exists():
        for line in receipt.read_text().splitlines():
            row = json.loads(line)
            fields = (
                'device', 'case', 'runtime', 'run', 'firmware_sha256', 'running_s',
                'first_visible_s', 'first_stable_s', 'repl_s', 'micropython_banner_s',
                'input_to_changed_frame_s', 'guest_real_time_ratio', 'guest_clock_samples',
                'cpu_pct_median', 'rss_mib_median', 'first_rgb_sha256', 'last_rgb_sha256',
                'serial_sha256', 'input_rgb_sha256', 'settled_rgb_sha256', 'input',
                'stop_state', 'evidence_sha256', 'unique_nonblack_frames',
            )
            public = {key: row[key] for key in fields if key in row}
            for field in ('run_error','frame_error','input_error','session_failure','stop_error'):
                if field in row:
                    public[field] = True
            path = receipt.parent / f"{row['device']}-{row['case']}-{row['runtime']}-{row['run']}.zip"
            try:
                with zipfile.ZipFile(path) as archive:
                    manifest = json.loads(archive.read('manifest.json'))
                    public['normalized_firmware_sha256'] = manifest['session'].get('firmware_sha256')
                    if 'runtime/identity.json' in archive.namelist():
                        identity = json.loads(archive.read('runtime/identity.json'))
                        public['runtime_identity'] = {k: identity[k] for k in (
                            'runtime', 'commit', 'binary_sha256', 'rom_sha256', 'board',
                            'service_patch_sha256', 'flash_bytes', 'psram_bytes', 'coprocessor'
                        ) if k in identity}
                    serial_names = [n for n in archive.namelist() if n == 'serial.log']
                    if len(serial_names) == 1:
                        raw = archive.read(serial_names[0])
                        public['evidence_serial_sha256'] = hashlib.sha256(raw).hexdigest()
                        public['evidence_serial_bytes'] = len(raw)
            except (FileNotFoundError, KeyError, zipfile.BadZipFile):
                pass
            yield public

def write_summary(filename, rows):
    (out / filename).write_text(json.dumps(rows, indent=2) + '\n')

def median(rows, key, digits=2):
    values = [r[key] for r in rows if key in r and r.get('stop_state') == 'stopped']
    if len(values) >= 3:
        return f'{statistics.median(values):.{digits}f}'
    return f'— ({len(values)}/{len(rows)})'

def hashes(rows, field):
    values = {r[field] for r in rows if field in r}
    return f'{len(values)}/{sum(field in r for r in rows)}'

native = list(decode_rows('paired'))
tab5 = list(decode_rows('tab5-baseline'))
tab5_repeat = list(decode_rows('tab5-v254-repeat'))
keyboard = list(decode_rows('keyboard-retry'))
cpu = list(decode_rows('cpu-probe'))
gaps = list(decode_rows('gaps'))
tab5_followups = list(decode_rows('tab5-followups'))
write_summary('native-summary.json', {
    'paired':native, 'tab5_dsi_baseline':tab5, 'tab5_v254_repeat':tab5_repeat, 'adv_input_retry':keyboard,
    'cpu_control':cpu, 'original_gaps':gaps, 'tab5_input_followups':tab5_followups,
})
groups = collections.defaultdict(list)
for sample in [*native, *cpu]:
    groups[sample['device'], sample['case'], sample['runtime']].append(sample)
for sample in [*tab5, *tab5_repeat]:
    key = sample['device'], sample['case'], sample['runtime']
    prior = groups[key]
    if sample['run'] == 1:
        prior.clear()
    prior.append(sample)

print('| 设备 / 固件 | runtime | 停止 / 运行数 | 首非黑 s | 首稳定 s | CPU % | RSS MiB | 首帧 / 串口不同 SHA 数 |')
print('| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |')
for device, case, runtime in groups:
    rows = groups[device, case, runtime]
    print(f'| {device} / {case} | {runtime} | {sum(r.get("stop_state") == "stopped" for r in rows)}/{len(rows)} | '
          f'{median(rows, "first_visible_s")} | {median(rows, "first_stable_s")} | '
          f'{median(rows, "cpu_pct_median", 1)} | {median(rows, "rss_mib_median", 1)} | '
          f'{hashes(rows, "first_rgb_sha256")} / {hashes(rows, "serial_sha256")} |')

print('\nCPU control virtual/wall and input latency:')
for key, rows in groups.items():
    if len(rows) and ('guest_real_time_ratio' in rows[0] or rows[0]['case'] == 'touch'):
        print(key, median(rows, 'guest_real_time_ratio'), median(rows, 'input_to_changed_frame_s'))
for runtime in ('qemu','esp32sim'):
    rows = [r for r in keyboard if r['runtime'] == runtime]
    if rows:
        print('keyboard-retry', runtime, median(rows, 'input_to_changed_frame_s'))
