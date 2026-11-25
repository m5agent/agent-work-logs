"""Stage a private 0097 diagnostic site without changing the locked export."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess

lab=Path(__file__).resolve().parent
workspace=lab.parent.parent
repo=workspace/'.work/docs-wasm-cardputer-cc1101-source'
control=workspace/'.work/docs-wasm-cores3-camera-lab/locked-0043-site'
parser=ArgumentParser()
parser.add_argument('--build', default='peer-preview-build-clean')
parser.add_argument('--site', default='peer-preview-site')
args=parser.parse_args()
assert re.fullmatch(r'peer-preview-build(?:-[a-zA-Z0-9_-]+)?', args.build)
assert re.fullmatch(r'peer-preview-site(?:-[a-zA-Z0-9_-]+)?', args.site)
compiled=lab/args.build
site=lab/args.site
assert site.exists() is False
runner=repo/'.work/cc1101-peer-pair.mjs'
patch_path='patches/qemu-wasm-probe/0097-cardputer-adv-cc1101-peer-preview.patch'
patch_sha='feeae444d6f29dce4780b366759d66a727a850f22daf12012e37c31ba80381a2'
branch_base='915faa6bf9882579e10668c315a5f8e74b2491af'
paths=[f'platform/web/public-qemu-{component}.js' for component in ('engine','profiles','runtime')]
runtime_path='platform/runtime/qemu/runtime.json'
manifest_path='public-site-manifest.json'


def identity(path):
    content=path.read_bytes()
    return {'sha256':sha256(content).hexdigest(),'bytes':len(content)}


def read_json(path):
    return json.loads(path.read_bytes())


def write_json(path,data):
    path.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def git(*args):
    return subprocess.check_output(['git','-C',str(repo),*args])


build=read_json(compiled/'preview-receipt.json')
assert build['status']=='PASS' and build['all_objects_rebuilt'] is False and build['guest_validation']=='NOT RUN'
assert build['preview_patch']=={'name':Path(patch_path).name,**identity(lab/Path(patch_path).name)}
assert build['preview_patch']['sha256']==patch_sha
assert git('rev-parse','HEAD').decode().strip()==branch_base
manifest=read_json(control/manifest_path)
runtime=read_json(control/runtime_path)
assert runtime['assets']['wasm']['sha256']==build['baseline_wasm_sha256']
assert runtime['build']['lock_sha256']==build['baseline_source_lock_sha256']
assert identity(control/manifest_path)['sha256']=='14460d70c9b834627663e8f25c69730ae26693b1e1c2498a08232a20de9d071a'
declared={row['path']:row for row in manifest['assets']}
assert len(declared)==len(manifest['assets'])
root_prefix=re.compile(r"""(?<=["'`(])/(platform|devices|data)/""")


def rewrite(content):
    return root_prefix.sub(lambda match:manifest['base_path']+match.group(1)+'/',content.decode()).encode()


for path in paths:
    assert (control/path).read_bytes()==rewrite(git('show',f'{branch_base}:{path}'))
assert patch_sha in (repo/'platform/web/public-qemu-profiles.js').read_text()
archive=runtime['assets']['source']
archive_path=Path(runtime_path).parent / archive['path']
assert identity(control/archive_path)=={key:archive[key] for key in ('sha256','bytes')}
subprocess.run(['cp','-cR',str(control),str(site)],check=True)
for path in paths:
    destination=site/path
    destination.write_bytes(rewrite((repo/path).read_bytes()))
    declared[path].update(identity(destination))
for kind,row in build['assets'].items():
    origin=compiled/'qemu-build'/row['path']
    staged=Path(runtime_path).parent/row['path']
    assert identity(origin)=={key:row[key] for key in ('sha256','bytes')}
    shutil.copyfile(origin,site/staged)
    runtime['assets'][kind].update(identity(site/staged))
    declared[staged.as_posix()].update(identity(site/staged))

runtime['source']['patches'].append({'path':patch_path,'sha256':patch_sha})
runtime['source']['patched_files_sha256'].update({name:row['sha256'] for name,row in build['changed_sources'].items()})
portable_commands={
    'compile':{name:row['portable_command_sha256'] for name,row in build['rebuild'].items()},
    'link':build['link_command_sha256'],
}
commands_sha256=sha256(json.dumps(portable_commands,sort_keys=True,separators=(',',':')).encode()).hexdigest()
runtime['build'].update(all_objects_rebuilt=False,guest_execution='NOT RUN by builder',commands_sha256=commands_sha256)
diagnostic={
    'distribution':'private diagnostic only',
    'guest_execution':'NOT RUN',
    'required_peer_preview_patch':{'path':patch_path,'sha256':patch_sha},
    'baseline_wasm_sha256':build['baseline_wasm_sha256'],
    'source_archive_scope':'Retained corresponding-source archive covers the locked 0043 control only. The private peer experiment uses the pinned preview diff.',
    'baseline_source_archive_sha256':archive['sha256'],
    'reused_link_inputs':build['reused_link_inputs'],
    'rebuilt_c_translation_units':sorted(build['rebuild']),
}
runtime['private_diagnostic']=diagnostic
write_json(site/runtime_path,runtime)
declared[runtime_path].update(identity(site/runtime_path))
manifest['private_diagnostic']=diagnostic
write_json(site/manifest_path,manifest)
receipt={
    **diagnostic,
    'build_receipt':identity(compiled/'preview-receipt.json'),
    'control_site_manifest':identity(control/manifest_path),
    'preview_site_manifest':identity(site/manifest_path),
    'preview_runtime_manifest':identity(site/runtime_path),
    'runtime_assets':build['assets'],
    'browser_web_sources':{path:identity(repo/path) for path in paths},
    'dual_original_browser_runner':identity(runner),
}
write_json(lab/(args.site+'-receipt.json'),receipt)
print(json.dumps(receipt))
