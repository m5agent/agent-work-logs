"""Clone the existing sealed export with the previously approved IR diagnostic scheduler."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess

lab = Path(__file__).resolve().parent
base = lab.parent.parent / 'docs-wasm-cardputer-lora-lab' / 'locked-0046-site'
site = lab / 'private-button-icount-0046-site'
manifest_name = 'public-site-manifest.json'
profiles_name = 'platform/web/qemu-browser-profiles.json'
configs = ('site-config.json', 'platform/web/site-config.json')
old_manifest_hash = 'cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac'
wasm_hash = '210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211'
accelerator = dict(kind='tcg-icount', thread='single', tbSizeMb=128, icountShift=5)


def digest(data):
    return sha256(data).hexdigest()


old_manifest = (base / manifest_name).read_bytes()
assert digest(old_manifest) == old_manifest_hash
manifest = json.loads(old_manifest)
assert manifest['publication_eligible'] is True and manifest['firmware_bundled'] is False
assert not site.exists()
assert not any(path.is_symlink() for path in base.rglob('*'))
subprocess.run(['cp', '-cR', str(base), str(site)], check=True)
assets = {row['path']: row for row in manifest['assets']}
assert len(assets) == len(manifest['assets'])
for name, row in assets.items():
    data = (site / name).read_bytes()
    assert len(data) == row['bytes'] and digest(data) == row['sha256'], name
assert assets['platform/runtime/qemu/qemu-system-xtensa.wasm']['sha256'] == wasm_hash
assert assets['platform/runtime/qemu/runtime.json']['sha256'] == 'a56410a8fb99a0e65ce7a7017c3a5ceb8ce0bd832451cbc71e12317cf614a0b9'


def update_json(name, edit):
    path = site / name
    value = json.loads(path.read_bytes())
    edit(value)
    data = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()
    path.write_bytes(data)
    assets[name].update(sha256=digest(data), bytes=len(data))


def select_icount(registry):
    row, = (row for row in registry['profiles'] if row['deviceId'] == 'cardputer-adv')
    assert row['profile'] == 'cardputer-adv-wasm-wallclock' and row['clockDivisor'] == 1
    variant, = row.pop('firmwareProfiles')
    assert variant['oneInsnPerTb'] is True
    assert variant['firmwareSHA256'] == 'b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd'
    row.update(profile='cardputer-adv-wasm-private-button-icount', admission='candidate', accelerator=accelerator)


update_json(profiles_name, select_icount)
for name in configs:
    assert json.loads((site / name).read_bytes())['publication_eligible'] is True
    update_json(name, lambda config: config.update(publication_eligible=False))
manifest.update(publication_eligible=False, private_diagnostic={
    'parent_site_manifest_sha256': old_manifest_hash,
    'accelerator': accelerator,
    'c_wasm_changed': False,
    'changed_assets': [profiles_name, *configs],
})
(site / manifest_name).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
assert digest((base / manifest_name).read_bytes()) == old_manifest_hash
print(digest((site / manifest_name).read_bytes()))
