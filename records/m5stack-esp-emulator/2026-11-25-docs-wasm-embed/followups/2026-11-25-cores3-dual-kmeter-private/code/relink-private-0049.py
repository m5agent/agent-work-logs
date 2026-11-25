"""Recompile only changed DualKmeter translation units in a private 0049 clone."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256, file_digest
import json
import os
from pathlib import Path
import shlex
import subprocess

lab=Path(__file__).resolve().parent
baseline=lab.parent/'docs-wasm-cardputer-adv-ir-ledc-lab/0049-locked-source-prepare'
published=baseline.parent/'0049-locked-runtime'
sdk=lab.parent/'docs-wasm-arduino-20261125/emsdk'
candidate=lab/'incremental-0049-build'
source=lab/'qemu'
build=candidate/'qemu-build'
patch=lab/'private-cores3-dual-kmeter.patch'
sources={'hw/m5stopwatch/m5cores3.c','hw/m5stopwatch/m5sw_i2c_devs.c'}
expected_base='3110d2859c0eb8648a94c52200c6456f387379859f865c0d3f46058d50bd798f'
expected_patch='e412ebb45fb7fc171f5059d57a04b443f3d014e6441297c3583cb621001dfdd1'

def read(path):
    return json.loads(path.read_bytes())

def identity(path):
    with path.open('rb') as data:
        return {'bytes':path.stat().st_size,'sha256':file_digest(data,'sha256').hexdigest()}

def argument_hash(args):
    return sha256(json.dumps(args,separators=(',',':')).encode()).hexdigest()

receipt=read(baseline/'build-receipt.json')
manifest=read(published/'runtime.json')
stamp=read(baseline/'source.json')
assert receipt['status']=='PASS' and receipt['all_objects_rebuilt'] and manifest['build']['all_objects_rebuilt']
assert receipt['artifacts']['wasm']['sha256']==manifest['assets']['wasm']['sha256']==expected_base
assert receipt['lock_sha256']==stamp['lock_sha256']==manifest['build']['lock_sha256']
assert identity(patch)['sha256']==expected_patch
assert manifest['source']['patched_files_sha256']==stamp['patched_files']
assert all(identity(baseline/'qemu'/name)['sha256']==stamp['patched_files'][name] for name in sources)
subprocess.run(['git','apply','--check',str(patch)],cwd=baseline/'qemu',check=True)
subprocess.run(['git','apply','--reverse','--check',str(patch)],cwd=source,check=True)
assert subprocess.check_output(['git','diff','--full-index','--no-ext-diff','--',*sorted(sources)], cwd=source)==patch.read_bytes()
assert all(identity(source/name)['sha256']==digest for name,digest in stamp['patched_files'].items()
           if name not in sources)
for kind,row in receipt['artifacts'].items():
    expected={key:row[key] for key in ('bytes','sha256')}
    assert identity(baseline/'qemu-build'/row['path'])==expected==identity(published/row['path']),kind

link_receipt=read(baseline/'effective-link.json')
link=link_receipt['argv']
assert link_receipt['verified'] and manifest['build']['link_audit']['verified']
assert argument_hash(link)==link_receipt['argv_sha256']==manifest['build']['link_audit']['argv_sha256']
assert link[link.index('-o')+1]=='qemu-system-xtensa.js'

database=read(baseline/'qemu-build/compile_commands.json')
records={row['output']:row for row in database if 'output' in row}
closure={}
for argument in link:
    if argument not in records:
        continue
    record=records[argument]
    name=record['file'].removeprefix('../qemu/')
    if name in sources:
        closure[argument]=record
assert len(closure)==len(sources)==2
# Only source leaves changed. Verify no other linked object names their paths
# through an unusual #include dependency before reusing every other input.
ninja=baseline/'tools/bin/ninja'
dep_text=subprocess.check_output([str(ninja),'-t','deps'],cwd=baseline/'qemu-build',text=True)
for block in dep_text.split('\n\n'):
    lines=block.splitlines()
    if not lines:
        continue
    name=lines[0].split(': #deps ',1)[0]
    for line in lines[1:]:
        normalized=line.strip().removeprefix('../qemu/').removeprefix(str(baseline/'qemu')+'/')
        if normalized in sources and name in link:
            assert name in closure, (name, normalized)

candidate.mkdir()
for name in ('qemu-build','em-cache'):
    subprocess.run(['cp','-cR',str(baseline/name),str(candidate/name)],check=True)
inputs={item.removeprefix('@'):identity(baseline/'qemu-build'/item.removeprefix('@')) for item in link
        if item.endswith(('.o','.a')) or item.startswith('@')}
assert set(closure)<=set(inputs)
assert all(identity(build/item)==ident for item,ident in inputs.items())
opts=os.environ.copy()
for option in ('CC','CXX','CPATH','CFLAGS','CXXFLAGS','CPPFLAGS','LDFLAGS','EMCC_CFLAGS','EMMAKEN_CFLAGS','C_INCLUDE_PATH'):
    opts.pop(option,None)
opts.update(EM_CONFIG=str(sdk/'.emscripten'),EM_CACHE=str(candidate/'em-cache'),
    EMCC_CORES='1',BINARYEN_CORES='1',
    PATH=os.pathsep.join(str(path) for path in [sdk/'upstream/emscripten',sdk/'upstream/bin',baseline/'tools/bin'])+
    os.pathsep+opts.get('PATH',''))

def compile_one(item):
    obj,row=item
    filename=row['file'].removeprefix('../qemu/')
    argv=[arg.replace(str(baseline/'qemu-build'),str(build)).replace(str(baseline/'qemu'),str(source)).
          replace('../qemu',str(source)) for arg in shlex.split(row['command'])]
    argv.insert(1,f'-ffile-prefix-map={lab}=/m5stack-build/private-dual-kmeter')
    assert argv[-1]==str(source/filename)
    with (candidate/(Path(filename).name+'.log')).open('wb') as log:
        subprocess.run(argv,cwd=build,env=opts,stdout=log,stderr=subprocess.STDOUT,check=True)
    print('rebuilt '+filename,flush=True)
    return obj, {'source':filename,'object':identity(build/obj)}

with ThreadPoolExecutor(max_workers=2) as executor:
    rebuilt=dict(executor.map(compile_one,closure.items()))
assert all(identity(build/item)==ident for item,ident in inputs.items() if item not in rebuilt)
print('relinking with the pinned 0049 link command',flush=True)
with (candidate/'link.log').open('wb') as log:
    subprocess.run(link,cwd=build,env=opts,stdout=log,stderr=subprocess.STDOUT,check=True)
assert all(identity(baseline/'qemu-build'/item)==ident for item,ident in inputs.items())
assets={kind:{'path':row['path'],**identity(build/row['path'])} for kind,row in receipt['artifacts'].items()}
assert assets['wasm']['sha256']!=expected_base
assert assets['worker']['sha256']==receipt['artifacts']['worker']['sha256']
for kind,row in receipt['artifacts'].items():
    assert identity(baseline/'qemu-build'/row['path'])=={key:row[key] for key in ('bytes','sha256')},kind
for row in assets.values():
    assert str(lab.parent.parent).encode() not in (build/row['path']).read_bytes(),row['path']
summary={
    'status':'PASS','distribution':'private incremental DualKmeter only','all_objects_rebuilt':False,
    'base_wasm_sha256':expected_base,'base_lock_sha256':receipt['lock_sha256'],
    'base_manifest_sha256':identity(published/'runtime.json')['sha256'],
    'base_source_archive_sha256':manifest['assets']['source']['sha256'],'patch_sha256':expected_patch,
    'patched_files':{name:identity(source/name)['sha256'] for name in sorted(sources)},
    'pinned_link_sha256':link_receipt['argv_sha256'],'rebuilt_objects':rebuilt,
    'identical_reused_link_input_count':len(inputs)-len(rebuilt),'assets':assets,
    'guest_execution':'NOT RUN',
}
(candidate/'preview-receipt.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary))
