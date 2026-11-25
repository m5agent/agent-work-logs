from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys

lab = Path(__file__).resolve().parent
baseline = lab.parent / 'docs-wasm-adv-gnss-lab' / 'sealed-site'
compiled = lab / sys.argv[1]
site = lab / sys.argv[2]
assert compiled.name.startswith('lora-preview-build') and site.name.startswith('lora-preview-site')
assert not site.exists()
runtime_path = Path('platform/runtime/qemu/runtime.json')
manifest_path = Path('public-site-manifest.json')
engine_path = Path('platform/web/public-qemu-engine.js')


def identity(path):
    data = path.read_bytes()
    return {'sha256': sha256(data).hexdigest(), 'bytes': len(data)}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


build = json.loads((compiled / 'preview-receipt.json').read_bytes())
assert build['status'] == 'PASS' and build['all_objects_rebuilt'] is False
assert build['preview_patch']['sha256'] == 'ac6611b1dd181489fb59e97e956cd80230100c29ae18532dce78fea47a4ce736'
assert identity(baseline / manifest_path)['sha256'] == 'decd60adf628e1defb9d4ae27f0e64ffe75336f451c2e2ddd192cf2feacf594f'
subprocess.run(['cp', '-cR', str(baseline), str(site)], check=True)
runtime = json.loads((site / runtime_path).read_bytes())
assert runtime['assets']['wasm']['sha256'] == build['baseline_wasm_sha256']
manifest = json.loads((site / manifest_path).read_bytes())
declared = {row['path']: row for row in manifest['assets']}
for key, asset in build['assets'].items():
    artifact = compiled / 'qemu-build' / asset['path']
    destination = runtime_path.parent / asset['path']
    assert identity(artifact) == {k: asset[k] for k in ('sha256', 'bytes')}
    shutil.copyfile(artifact, site / destination)
    runtime['assets'][key].update(identity(site / destination))
    declared[destination.as_posix()].update(identity(site / destination))
patch = {'path': 'patches/qemu-wasm-probe/' + build['preview_patch']['name'],
         'sha256': build['preview_patch']['sha256']}
runtime['source']['patches'].append(patch)
runtime['source']['patched_files_sha256'].update({name: row['sha256'] for name, row in build['changed_sources'].items()})
runtime['build'].update(all_objects_rebuilt=False, guest_execution='NOT RUN by builder')
runtime['private_diagnostic'] = {'preview_patch': patch, 'source_archive_scope': 'Baseline 0043 archive only'}
write_json(site / runtime_path, runtime)
declared[runtime_path.as_posix()].update(identity(site / runtime_path))

engine = site / engine_path
js = engine.read_text()
before = "      if(sdCard) {"
after = """      if (boardProfile.deviceId==='cardputer-adv' && boardProfile.firmwareVariant?.firmwareSHA256==='b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd')
        m.ENV.M5SW_CARDPUTER_ADV_CAP_LORA='1';
""" + before
assert js.count(before) == 1
js = js.replace(before, after, 1)
before = "async function request(op, value) {"
after = before + """
  if (op === 'lora-lab-state' || op === 'lora-lab-receive') {
    if (boardProfile?.deviceId !== 'cardputer-adv') throw new Error('LoRa preview is not bound');
    const path = '/machine/cardputer-adv-lora';
    if (op === 'lora-lab-state') return qmp('qom-get',{path,property:'state'});
    if (typeof value?.hex !== 'string' || !/^(?:[0-9a-f]{2}){1,255}$/.test(value.hex))
      throw new Error('Preview receiver requires an exact packet');
    await qmp('qom-set',{path,property:'rx-packet',value:value.hex});
    return qmp('qom-get',{path,property:'state'});
  }"""
assert js.count(before) == 1
engine.write_text(js.replace(before, after, 1))
declared[engine_path.as_posix()].update(identity(engine))
manifest['publication_eligible'] = False
manifest['private_diagnostic'] = runtime['private_diagnostic']
write_json(site / manifest_path, manifest)
receipt = {
    'status': 'PASS', 'guest_execution': 'NOT RUN', 'distribution': 'private only',
    'build_receipt': identity(compiled / 'preview-receipt.json'),
    'site_manifest': identity(site / manifest_path),
    'runtime_manifest': identity(site / runtime_path),
    'engine': identity(engine), 'final_patch': patch, 'wasm': build['assets']['wasm'],
}
write_json(lab / (site.name + '-receipt.json'), receipt)
print(json.dumps(receipt))
