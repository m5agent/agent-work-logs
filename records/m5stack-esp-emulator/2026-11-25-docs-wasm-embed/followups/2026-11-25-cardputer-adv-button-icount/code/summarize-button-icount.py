"""Build a bounded comparison from three finished private reports and preserved control reports."""

from hashlib import sha256
import json
from pathlib import Path

lab = Path(__file__).resolve().parent


def read(path):
    blob = path.read_bytes()
    return json.loads(blob), {'sha256': sha256(blob).hexdigest(), 'bytes': len(blob)}


def markers(value):
    return [line.strip() for line in (value or '').splitlines() if line.strip() in ('Button A Pressed', 'Button A Released')]


def short_error(report):
    error = report.get('error')
    return error.splitlines()[0] if error else None


def cold_run(index):
    root = lab / f'browser-button-0046-icount-cold-{index}'
    report, raw = read(root / 'report.json')
    run, = report['runs']
    final = run.get('final') or report.get('failure') or {}
    held = run.get('press') or {}
    cleanup = run.get('cleanup') or report.get('failure_shutdown') or {}
    workers = run.get('dedicated_workers') or report.get('failure_cleanup') or {}
    before = run.get('counters_before') or {}
    after = run.get('counters_after') or {}
    top = run.get('active_topology') or {}
    filename = 'cdc-on-serial.png' if report['status'] == 'PASS' else 'failure.png'
    screenshot = (root / filename).read_bytes() if (root / filename).exists() else None
    receipt = run.get('ready', {}).get('receipt', {})
    assert receipt.get('firmwareInputSha256') == '07ebcecd82c9a64aad457f5e30eac140bfd24db8006506ea6f04489a860dc0e7'
    assert receipt['firmwareRuntimeSha256'] == '54ee755a50f4187e9ddfc96efb7ea996c896e46d4b99e2945ceb3183a1aa6f50'
    assert receipt['wasmSha256'] == report['wasm_sha256']
    assert receipt['accelerator'] == report['requested_accelerator']
    assert receipt['oneInsnPerTb'] is False and receipt['clockOverride'] is None
    span = lambda key: round(run[key], 2) if key in run else None
    return report, {
        'start': index, 'status': report['status'], 'failure': short_error(report), 'raw_report': raw,
        'screenshot': {'sha256': sha256(screenshot).hexdigest(), 'bytes': len(screenshot)} if screenshot else None,
        'ready_ms': span('ready_ms'), 'rom_handoff_ms': span('rom_handoff_ms'), 'f12_hold_ms': span('f12_hold_ms'),
        'observed_input': [{'down': event.get('down'), 'qmp_acknowledged': event.get('result') == {}}
                           for event in final.get('inputs', []) if event.get('id') == 'boot'],
        'held_serial_cdc': markers(held.get('usb')), 'final_serial_cdc': markers(final.get('usb')),
        'final_ui_cdc': markers(final.get('uiText')), 'final_uart_button': markers(final.get('uart')),
        'cdc_controller_before': before, 'cdc_controller_after': after or None,
        'final_cdc_bytes': final.get('usbBytes'), 'frame': final.get('frame'),
        'worker_errors': [{'name': entry['name'], 'kind': entry['kind']} for entry in final.get('workerErrors', [])],
        'reset_count': sum(event.get('event') == 'RESET' for event in final.get('events', [])),
        'cleanup': {'exit_code': cleanup.get('exitCode'), 'graceful': cleanup.get('gracefulExit'), 'iframe_removed': cleanup.get('iframeRemoved'),
                    'engine_workers': top.get('engine_count'), 'guest_pthreads': top.get('pthread_count'),
                    'workers_observed': len(workers.get('observed', [])), 'workers_live': len(workers.get('live', [])),
                    'workers_closed_observed': workers.get('ok')},
    }


def control(label, dirs):
    rows = []
    for d in dirs:
        report, raw = read(lab.parent / d / 'report.json')
        rows.append({'status': report['status'], 'failure': short_error(report), 'raw_report': raw})
    return {'label': label, 'passes': sum(row['status'] == 'PASS' for row in rows), 'cold_starts': rows}


reports, runs = zip(*(cold_run(i) for i in (1, 2, 3)))
first = reports[0]
assert first['status'] in ('PASS', 'FAIL')
identity_keys = ('kind', 'validation', 'doc', 'sketch_sha256', 'rom_sha256', 'site_manifest_sha256', 'runtime_manifest_sha256',
                 'source_lock_sha256', 'wasm_sha256', 'workbench_asset_sha256', 'harness_sha256', 'requested_accelerator', 'expected_worker_targets')
assert all(all(row[key] == first[key] for key in identity_keys) for row in reports)
assert all(not row['blocked_requests'] and not row['page_errors'] for row in reports)
passes = sum(run['status'] == 'PASS' for run in runs)
summary = {
    'issue': 268, 'status': 'PASS' if passes == len(runs) else 'FAIL', 'passes': passes, 'attempts': len(runs),
    **{key: first[key] for key in identity_keys},
    'canonical_site_manifest_sha256': 'cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac',
    'firmware_input_sha256': '07ebcecd82c9a64aad457f5e30eac140bfd24db8006506ea6f04489a860dc0e7',
    'firmware_runtime_sha256': '54ee755a50f4187e9ddfc96efb7ea996c896e46d4b99e2945ceb3183a1aa6f50',
    'only_staged_changes': ['platform/web/qemu-browser-profiles.json', 'site-config.json', 'platform/web/site-config.json'],
    'replay_method': 'Three sequential fresh headless Chrome processes and contexts. Standard workbench local upload, ROM wait, 2.5-second settle, actual F12 keydown until CDC press or same 20-second timeout, keyup, actual release output, and teardown.',
    'scope': 'Private fixed scheduler comparison. Executable WASM, original guest firmware, GPIO board wiring, default CDC controller, and standard workbench JavaScript are byte-identical to the corresponding canonical assets.',
    'cold_starts': runs,
    'prior_separate_controls': [
        control('prior standard default clock', [f'browser-button-0046-on-{i}' for i in range(1, 6)]),
        control('prior interleaved standard default clock', [f'browser-button-0046-ab-{i}-default' for i in range(1, 4)]),
        control('prior interleaved one-insn-per-TB', [f'browser-button-0046-ab-{i}-oneinsn' for i in range(1, 4)]),
    ],
}
result = lab / 'button-0046-icount.summary.json'
result.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
print(result.name, sha256(result.read_bytes()).hexdigest(), result.stat().st_size)
