"""Restore frozen HTTPS test adapters in a new fixed-source checkout.
Only regenerates test source files; never fetches, opens Chrome or runs a guest.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
SOURCE='10788607feefb9e532c2dd1fe4679adcd6aa0fc2'
TREE='9158da43530d82d0eaf5472eff15f831e82666e8'
EXPECTED_IDENTITY='ecc887184178b99656bdada419502355940ee6cec7ec45a405c2259a822efa87'
SEEDS=('prepare.py','pages_remote_release.mjs','preflight.mjs','verify_runtime_archive.py',
       'test_remote_release.mjs','test_archive_controls.py','prepared-provenance-label-only.patch')
sha=lambda b:hashlib.sha256(b).hexdigest()
def main(repo):
    repo=Path(repo).resolve();bundle=Path(__file__).resolve().parent
    manifest=json.loads((bundle/'adapter-source-manifest.json').read_text())
    assert manifest['reproduction_source_commit']==SOURCE
    assert manifest['frozen_identity_sha256']==EXPECTED_IDENTITY
    for field,expected in [('HEAD',SOURCE),('HEAD^{tree}',TREE)]:
        assert subprocess.check_output(['git','rev-parse',field],cwd=repo,text=True).strip()==expected
    subprocess.run(['git','diff-index','--quiet','HEAD','--'],cwd=repo,check=True)
    identity_bytes=(bundle/'seeds/adapter-identity.json').read_bytes()
    assert sha(identity_bytes)==EXPECTED_IDENTITY
    identity=json.loads(identity_bytes)
    for row in identity['parents'].values():
        assert sha((repo/row['path']).read_bytes())==row['sha256'],'Fixed parent source mismatch'
    work=repo/'.work';out=work/'pages-remote-tools'
    assert not work.is_symlink(),'A new independent checkout is required'
    assert not out.exists(),'Never overwrite an existing adapter or execution directory'
    data={}
    for name in SEEDS:
        b=(bundle/'seeds'/name).read_bytes();row=manifest['seed_files'][name]
        assert len(b)==row['bytes']and sha(b)==row['sha256'],'Frozen seed changed'
        data[name]=b
    out.mkdir(parents=True,exist_ok=False)
    for name,b in data.items():(out/name).write_bytes(b)
    # Run only the original fixed generator; this does not execute the adapters.
    result=subprocess.run([sys.executable,str(out/'prepare.py')],cwd=repo,check=True,capture_output=True,text=True)
    restored=(out/'adapter-identity.json').read_bytes()
    assert sha(restored)==EXPECTED_IDENTITY,'Generated identity differs from frozen source'
    assert json.loads(result.stdout)==identity
    for name,row in identity['actual_files'].items():
        b=(out/name).read_bytes();assert len(b)==row['bytes']and sha(b)==row['sha256'],name
    return {'status':'PASS','scope':'host-only source restoration; guest/browser/network NOT RUN',
            'source_commit':SOURCE,'frozen_identity_sha256':EXPECTED_IDENTITY,'exact_identity_members':15,
            'existing_execution_copies_changed':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True)
    print(json.dumps(main(p.parse_args().repo),indent=2))
