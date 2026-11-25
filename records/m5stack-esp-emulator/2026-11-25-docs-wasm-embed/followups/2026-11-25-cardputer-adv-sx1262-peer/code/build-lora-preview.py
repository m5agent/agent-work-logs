"""Incrementally relink a private SX1262 browser preview from exact 0043 objects."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

lab=Path(__file__).resolve().parent
workspace=lab.parent.parent
control=workspace/'.work/docs-wasm-cores3-camera-lab/locked-0043-build'
sdk=workspace/'.work/docs-wasm-arduino-20261125/emsdk'
patch=lab/'0098-cardputer-adv-sx1262-preview.patch'
parser=ArgumentParser()
parser.add_argument('--name',default='lora-preview-build')
args=parser.parse_args()
assert re.fullmatch(r'lora-preview-build(?:-[a-zA-Z0-9_-]+)?',args.name)
candidate=lab/args.name
assert not candidate.exists(), candidate
qemu_patch_files={
    'hw/m5stopwatch/m5_sx1262.c',
    'hw/m5stopwatch/m5cardputeradv.c',
    'hw/m5stopwatch/m5stopwatch.h',
}
compiled_files={name for name in qemu_patch_files if name.endswith('.c')}


def identity(path):
    content=path.read_bytes()
    return {'sha256':sha256(content).hexdigest(),'bytes':len(content)}


def read_json(path):
    return json.loads(path.read_bytes())


def write_json(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def command_hash(command):
    portable=[value.replace(str(workspace), '/m5stack-preview/workspace').replace(args.name, 'lora-preview-build')
              for value in command]
    return sha256(json.dumps(portable,separators=(',',':')).encode()).hexdigest()


baseline_receipt=read_json(control/'build-receipt.json')
assert baseline_receipt['status']=='PASS' and baseline_receipt['all_objects_rebuilt']
assert baseline_receipt['artifacts']['wasm']['sha256']=='e350ed7b2f969139803befef12757178049427058a212136868d382dfe5a5f4b'
assert identity(patch)['sha256']=='ac6611b1dd181489fb59e97e956cd80230100c29ae18532dce78fea47a4ce736'
assert json.loads((sdk/'upstream/emscripten/emscripten-version.txt').read_text())=='3.1.50'
for name,row in baseline_receipt['artifacts'].items():
    assert identity(control/'qemu-build'/row['path'])=={k:row[k] for k in ('sha256','bytes')},name
locked=read_json(control/'source.json')['patched_files']
assert compiled_files.issubset(locked)
for name in qemu_patch_files:
    original=identity(control/'qemu'/name)
    assert identity(lab/'preimage'/name)==original
    if name in locked:
        assert original['sha256']==locked[name]
candidate.mkdir()
for name in ('qemu','qemu-build','em-cache'):
    subprocess.run(['cp','-cR',str(control/name),str(candidate/name)],check=True)
subprocess.run(['patch','-p1','-d',str(candidate/'qemu'),'-i',str(patch)],check=True)
for name in qemu_patch_files:
    assert identity(candidate/'qemu'/name)==identity(lab/'source'/name)
build_dir=candidate/'qemu-build'
commands=read_json(control/'qemu-build/compile_commands.json')
commands_by_source={row['file']:shlex.split(row['command']) for row in commands}
link_pin=read_json(control/'effective-link.json')
link=link_pin['argv']
assert link[2:4]==['-o','qemu-system-xtensa.js']
responses={arg[1:] for arg in link if arg.startswith('@')}
assert responses=={'block.syms','qemu.syms'}
response_identities={}
for name in responses:
    response_identities[name]=identity(control/'qemu-build'/name)
    assert identity(candidate/'qemu-build'/name)==response_identities[name]
steps=[]
for name in sorted(compiled_files):
    argv=commands_by_source['../qemu/'+name]
    object_path=argv[argv.index('-o')+1]
    assert object_path in link and not Path(object_path).is_absolute()
    argv=[arg.replace(str(control/'qemu'),str(candidate/'qemu')) for arg in argv]
    argv.insert(argv.index('-MD'),'-ffile-prefix-map='+str(candidate)+'=/m5stack-build/cache')
    steps.append((name,object_path,argv))
expected_rebuilt={object_path for _,object_path,_ in steps}

previous_objects={}
for item in link:
    if item.endswith(('.o','.a')):
        path=Path(item)
        baseline_path=path if path.is_absolute() else control/'qemu-build'/path
        alternate_path=path if path.is_absolute() else build_dir/path
        assert baseline_path.is_file() and alternate_path.is_file(),item
        assert not alternate_path.is_symlink(),item
        before=identity(baseline_path)
        assert identity(alternate_path)==before,item
        previous_objects[item]=before

env=dict(os.environ,EM_CONFIG=str(sdk/'.emscripten'),EM_CACHE=str(candidate/'em-cache'),EMCC_CORES='2',
         BINARYEN_CORES='2',EMSDK=str(sdk))
for key in ('CFLAGS','CXXFLAGS','CPPFLAGS','LDFLAGS','EMCC_CFLAGS','EMMAKEN_CFLAGS','CPATH','EMCC_DEBUG'):
    env.pop(key,None)
env['PATH']=os.pathsep.join([
    str(sdk/'upstream/emscripten'),str(sdk/'upstream/bin'),env['PATH']
])
run_commands={'compile':[{'source':name,'argv':argv} for name,_,argv in steps],'link':link}
write_json(candidate/'executed-commands.json',run_commands)


def compile_one(step):
    source, object_path, argv=step
    log=candidate/(Path(source).stem+'.log')
    with log.open('w') as stream:
        subprocess.run(argv,cwd=build_dir,env={**env,'EMCC_CORES':'1','BINARYEN_CORES':'1'},
                       stdout=stream,stderr=subprocess.STDOUT,check=True)
    print('compiled '+source,flush=True)
    return object_path


with ThreadPoolExecutor(max_workers=2) as pool:
    actual_rebuilt=set(pool.map(compile_one,steps))
assert actual_rebuilt==expected_rebuilt
for item,before in previous_objects.items():
    path=Path(item)
    current=identity(path if path.is_absolute() else build_dir/path)
    assert (item in actual_rebuilt)==(current!=before),item
    baseline_path=path if path.is_absolute() else control/'qemu-build'/path
    assert identity(baseline_path)==before,item
print('linking exact 0043 dependency/object list with two reviewed replacements',flush=True)
with (candidate/'link.log').open('w') as stream:
    subprocess.run(link,cwd=build_dir,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
assets={}
for kind,row in baseline_receipt['artifacts'].items():
    path=build_dir/row['path']
    assert identity(control/'qemu-build'/row['path'])=={k:row[k] for k in ('sha256','bytes')}
    assets[kind]={**identity(path),'path':row['path']}
assert assets['wasm']['sha256']!=baseline_receipt['artifacts']['wasm']['sha256']
assert (build_dir/assets['wasm']['path']).read_bytes().startswith(b'\0asm\x01\0\0\0')
for row in assets.values():
    content=(build_dir/row['path']).read_bytes()
    assert str(workspace).encode() not in content
receipt={
    'kind':'private-incremental-browser-qemu',
    'status':'PASS',
    'guest_validation':'NOT RUN',
    'all_objects_rebuilt':False,
    'max_compile_jobs':2,
    'emscripten':'3.1.50',
    'baseline_wasm_sha256':baseline_receipt['artifacts']['wasm']['sha256'],
    'baseline_build_receipt':identity(control/'build-receipt.json'),
    'baseline_source_lock_sha256':baseline_receipt['lock_sha256'],
    'preview_patch':{'name':patch.name,**identity(patch)},
    'rebuild':{name:{'input':identity(candidate/'qemu'/name),'object':identity(build_dir/obj),
                     'portable_command_sha256':command_hash(argv)}
               for name,obj,argv in steps},
    'changed_sources':{name:identity(candidate/'qemu'/name) for name in sorted(qemu_patch_files)},
    'reused_link_inputs':len(previous_objects)-len(actual_rebuilt),
    'link_command_sha256':command_hash(link),
    'link_response_files':response_identities,
    'baseline_link_audit':baseline_receipt['link_audit'],
    'assets':assets,
}
write_json(candidate/'preview-receipt.json',receipt)
print(json.dumps(receipt))
