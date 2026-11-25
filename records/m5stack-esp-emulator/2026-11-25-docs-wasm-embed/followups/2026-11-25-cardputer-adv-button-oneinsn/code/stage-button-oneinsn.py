import hashlib
import json
from pathlib import Path
import shutil
import sys

BASE = 'cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac'
WASM = '210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211'
BUTTON_INPUT = '07ebcecd82c9a64aad457f5e30eac140bfd24db8006506ea6f04489a860dc0e7'
BUTTON_FLASH = '54ee755a50f4187e9ddfc96efb7ea996c896e46d4b99e2945ceb3183a1aa6f50'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)

base, output = map(lambda name: Path(name).resolve(), sys.argv[1:])
manifest_name = 'public-site-manifest.json'
profile_js = 'platform/web/public-qemu-profiles.js'
profile_json = 'platform/web/qemu-browser-profiles.json'
assert digest(base / manifest_name) == BASE
assert digest(base / 'platform/runtime/qemu/qemu-system-xtensa.wasm') == WASM
manifest = json.loads((base / manifest_name).read_bytes())
assert manifest['publication_eligible'] is True
shutil.copytree(base, output)
profile = json.loads((base / profile_json).read_bytes())
row = next(row for row in profile['profiles'] if row['deviceId'] == 'cardputer-adv')
row['firmwareProfiles'].append(dict(
    firmwareSHA256=BUTTON_FLASH, profile='cardputer-adv-private-arduino-button-oneinsn',
    clockDivisor=1, readyMarker=None, fixture='cardputer-adv-arduino-button-default-cdc',
    sourceSHA256=BUTTON_INPUT, schedulerCandidate='qemu-tci-mmio-blocks-v1',
    sourceKind='published-firmware-binary', oneInsnPerTb=True,
    requiredRuntimePatch=row['firmwareProfiles'][0]['requiredRuntimePatch'],
))
(output / profile_json).write_text(json.dumps(profile, indent=2)+'\n')
js = (base / profile_js).read_text()
entry = ('const publishedFirmwareVariants = Object.freeze([\n'
    "  {deviceId:'cardputer-adv',board:'m5cardputer-adv',fixture:'cardputer-adv-arduino-button-default-cdc',\n"
    f"    firmwareSHA256:'{BUTTON_FLASH}',sourceSHA256:'{BUTTON_INPUT}'}},\n")
entry = entry.replace("board:'m5cardputer-adv'", "board:'"+row['board']+"'")
js = replace_once(js, 'const publishedFirmwareVariants = Object.freeze([\n', entry)
js = replace_once(js, "&& profile.chip === 'esp32s3' && profile.flashMb === 16 && profile.psramMb === 8\n      && publishedFirmwareVariants", "&& profile.chip === 'esp32s3'\n      && (profile.flashMb === 16 && profile.psramMb === 8\n        || profile.deviceId === 'cardputer-adv' && profile.flashMb === 8 && profile.psramMb === 0)\n      && publishedFirmwareVariants")
(output / profile_js).write_text(js)
for asset in manifest['assets']:
    path = asset['path']
    assert digest(base / path) == asset['sha256']
    if path in (profile_js, profile_json):
        asset.update(sha256=digest(output / path), bytes=(output / path).stat().st_size)
    else:
        assert digest(output / path) == asset['sha256']
manifest['publication_eligible'] = False
(out := output / manifest_name).write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
print(json.dumps({'status':'PRIVATE_PREFLIGHT','base_manifest_sha256':BASE,'manifest_sha256':digest(out),'wasm_sha256':WASM,'changed_assets':[profile_js, profile_json]}))
