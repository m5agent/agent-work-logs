"""Seal private exact CoreS3 DualKmeter fixture interfaces on the 0049 site."""
from hashlib import sha256, file_digest
import json
from pathlib import Path
import subprocess

lab=Path(__file__).resolve().parent
base=lab.parent/'docs-wasm-cardputer-adv-ir-ledc-lab/0049-locked-final-site'
site=lab/'dualkmeter-private-0049-site'
rel_build=lab/'incremental-0049-build'
runtime_path='platform/runtime/qemu/runtime.json'
patch_path='patches/qemu-wasm-probe/private-cores3-dual-kmeter.patch'
engine_path='platform/web/public-qemu-engine.js'
adapter_path='platform/web/public-qemu-runtime.js'
helper_path='platform/web/private-dual-kmeter-example.js'
expected_site='5c53116f28894a0b6210167b3aecf52abaf77e9cb385da048901ceac85211495'
expected_firmware='b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49'
exact_python=lab.parent/'docs-wasm-cores3-blockly-lab/dualkmeter.official.full-preview.py'

def read(path):
    return json.loads(path.read_bytes())

def identity(path):
    with path.open('rb') as data:
        return {'bytes':path.stat().st_size,'sha256':file_digest(data,'sha256').hexdigest()}

def write(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def replace(path,changes):
    content=path.read_text()
    for before,after in changes:
        assert content.count(before)==1,(path.name,before)
        content=content.replace(before,after)
    path.write_text(content)

assert not site.exists()
assert identity(base/'public-site-manifest.json')['sha256']==expected_site
before=read(base/'public-site-manifest.json')
index={row['path']:row for row in before['assets']}
compiled=read(rel_build/'preview-receipt.json')
assert compiled['status']=='PASS' and not compiled['all_objects_rebuilt']
base_manifest=read(base/runtime_path)
assert base_manifest['assets']['wasm']['sha256']==compiled['base_wasm_sha256']
assert base_manifest['build']['lock_sha256']==compiled['base_lock_sha256']
assert identity(base/runtime_path)['sha256']==compiled['base_manifest_sha256']
assert base_manifest['assets']['source']['sha256']==compiled['base_source_archive_sha256']
for rel in (runtime_path,engine_path,adapter_path):
    assert identity(base/rel)=={k:index[rel][k] for k in ('bytes','sha256')}

subprocess.run(['cp','-cR',str(base),str(site)],check=True)
for name in ('javascript','wasm','worker'):
    row=compiled['assets'][name]
    binary=rel_build/'qemu-build'/row['path']
    exact={k:row[k] for k in ('bytes','sha256')}
    assert identity(binary)==exact
    rel='platform/runtime/qemu/'+row['path']
    (site/rel).write_bytes(binary.read_bytes())
    index[rel].update(exact)
    base_manifest['assets'][name].update(exact)
patch_row={'path':patch_path,'sha256':compiled['patch_sha256']}
fixture={'id':'m127-celsius','board':'cores3','firmware_sha256':expected_firmware,
         'original_python_sha256':identity(exact_python)['sha256']}
capability={'distribution':'private incremental, original source archive describes baseline 0049 only',
            'base_site_sha256':expected_site,'base_wasm_sha256':compiled['base_wasm_sha256'],
            'base_source_archive_sha256':compiled['base_source_archive_sha256'],'fixture':fixture,
            'patch':patch_row,'build_receipt_sha256':identity(rel_build/'preview-receipt.json')['sha256']}
base_manifest['build']['all_objects_rebuilt']=False
base_manifest['source']['patches'].append(patch_row)
base_manifest['source']['patched_files_sha256'].update(compiled['patched_files'])
base_manifest['private_dual_kmeter_preview']=capability
write(site/runtime_path,base_manifest)

(site/helper_path).write_text(f'''export const DUAL_KMETER_EXAMPLE = {json.dumps(fixture['id'])};
export const DUAL_KMETER_FIRMWARE = {json.dumps(expected_firmware)};
const PATCH = {json.dumps(patch_row)};

export function validDualKmeterExample(example, profile, patches) {{
  if (!Array.isArray(patches)) return false;
  const matches = patches.filter(row => row?.path === PATCH.path);
  return example === DUAL_KMETER_EXAMPLE && profile?.deviceId === 'cores3' && profile.board === 'm5cores3'
    && profile.profile === 'cores3-wasm-uiflow-workbench-lvgl-wallclock-candidate' && profile.clockDivisor === 1
    && profile.readyFirmwareSHA256 === DUAL_KMETER_FIRMWARE
    && matches.length === 1 && matches[0].sha256 === PATCH.sha256;
}}

export function validDualKmeterTemperature(value) {{
  return Number.isSafeInteger(value) && value >= -20000 && value <= 135000;
}}
''')
helper="./private-dual-kmeter-example.js"
replace(site/adapter_path,[
    ("import {admitQemuEnginePort,createQemuEngineOwner} from './public-qemu-engine-owner.js';",
     "import {admitQemuEnginePort,createQemuEngineOwner} from './public-qemu-engine-owner.js';\n"
     f"import {{DUAL_KMETER_FIRMWARE,validDualKmeterExample}} from '{helper}';"),
    ("capExample,capPeer,sx1262Example,audio}=options;", "capExample,capPeer,sx1262Example,audio,dualKmeterExample}=options;"),
    ("'capPeer','sx1262Example','audio'].includes", "'capPeer','sx1262Example','audio','dualKmeterExample'].includes"),
    ("      validateQemuRuntimeRequirements(profile,manifest);",
     """      validateQemuRuntimeRequirements(profile,manifest);
      if (dualKmeterExample !== undefined) {
        check(inputSHA256 === DUAL_KMETER_FIRMWARE && firmwareSHA256 === DUAL_KMETER_FIRMWARE
          && clockDivisor === undefined && validDualKmeterExample(dualKmeterExample,profile,manifest.source.patches),
          'DualKmeter preview requires the pinned CoreS3 workbench firmware and fixture patch.');
      }"""),
    ("        ...(profile.unitExample ? {unitExample:profile.unitExample} : {}),",
     """        ...(profile.unitExample ? {unitExample:profile.unitExample} : {}),
        ...(dualKmeterExample ? {dualKmeterExample} : {}),"""),
    ("...(audioExample ? {audio:{kind:audioExample,ring:this.audioPlayer.ring}} : {}),runtimePatches:manifest.source.patches}",
     """...(audioExample ? {audio:{kind:audioExample,ring:this.audioPlayer.ring}} : {}),
        ...(dualKmeterExample ? {dualKmeterExample} : {}),runtimePatches:manifest.source.patches}"""),
])
replace(site/engine_path,[
    ("import {readQemuServoOutputs} from './public-qemu-servo.js';",
     "import {readQemuServoOutputs} from './public-qemu-servo.js';\n"
     f"import {{validDualKmeterExample,validDualKmeterTemperature}} from '{helper}';"),
    ("let audioMode, micArmed = false;","let audioMode, micArmed = false;\nlet dualKmeterEnabled = false;"),
    ("  validateQemuRuntimeRequirements(boardProfile,{source:{patches:config.runtimePatches}});",
     """  validateQemuRuntimeRequirements(boardProfile,{source:{patches:config.runtimePatches}});
  if (config.dualKmeterExample !== undefined) {
    if (!validDualKmeterExample(config.dualKmeterExample,boardProfile,config.runtimePatches)) {
      throw new Error('DualKmeter preview firmware or fixture mismatch');
    }
    dualKmeterEnabled = true;
  }"""),
    ("      if(sdCard) {",
     """      if (dualKmeterEnabled) m.ENV.M5_WASM_CORES3_DUAL_KMETER_EXAMPLE = '1';
      if(sdCard) {"""),
    ("async function request(op, value) {",
     """const DUAL_KMETER_PATH = '/machine/dual-kmeter';
async function readDualKmeterState() {
  const [temperatureCentiC, transactions, readBytes, writtenBytes] = await Promise.all(
    ['temperature-centi-c','transactions','read-bytes','written-bytes'].map(property =>
      qmp('qom-get',{path:DUAL_KMETER_PATH,property})));
  if (!validDualKmeterTemperature(temperatureCentiC) || ![transactions,readBytes,writtenBytes].every(
    count => Number.isSafeInteger(count) && count >= 0)) throw new Error('Invalid DualKmeter state');
  return {kind:'dual-kmeter',temperatureCentiC,transactions,readBytes,writtenBytes};
}

async function request(op, value) {
  if (op === 'dual-kmeter-example-state' || op === 'dual-kmeter-example-temperature') {
    if (!dualKmeterEnabled || !value || typeof value !== 'object' || Array.isArray(value)) {
      throw new Error('DualKmeter fixture unavailable');
    }
    if (op === 'dual-kmeter-example-temperature') {
      if (Object.keys(value).length !== 1 || !validDualKmeterTemperature(value.temperatureCentiC)) {
        throw new Error('DualKmeter temperature must be a bounded integer in centi-degrees Celsius');
      }
      await qmp('qom-set',{path:DUAL_KMETER_PATH,property:'temperature-centi-c',value:value.temperatureCentiC});
    } else if (Object.keys(value).length) {
      throw new Error('DualKmeter state does not accept arguments');
    }
    return readDualKmeterState();
  }"""),
])
for rel in ('site-config.json','platform/web/site-config.json'):
    config=read(site/rel)
    config['publication_eligible']=False
    write(site/rel,config)
    index[rel].update(identity(site/rel))
for rel in (engine_path,adapter_path,helper_path):
    subprocess.run(['node','--check',str(site/rel)],check=True)
    index[rel]={'path':rel,**identity(site/rel)}
index[runtime_path].update(identity(site/runtime_path))
before['publication_eligible']=False
before['private_dual_kmeter_preview']=capability
before['assets']=sorted(index.values(),key=lambda row:row['path'])
write(site/'public-site-manifest.json',before)
for rel,row in index.items():
    assert identity(site/rel)=={key:row[key] for key in ('bytes','sha256')},rel
summary={'status':'PREFLIGHT_PASS','guest_execution':'NOT RUN','publication_eligible':False,
         'site_manifest_sha256':identity(site/'public-site-manifest.json')['sha256'],
         'runtime_manifest_sha256':identity(site/runtime_path)['sha256'],
         'wasm_sha256':compiled['assets']['wasm']['sha256'],
         'source':capability,'asset_count':len(index),
         'adapter':identity(site/adapter_path),'engine':identity(site/engine_path)}
write(lab/'dualkmeter-private-0049-site-identities.json',summary)
print(json.dumps(summary))
