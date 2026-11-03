// Test-only Pages transport. No server, firmware, pixels or guest-state writes.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
import {isDeepStrictEqual} from 'node:util';
import {capturePublicQemuProvenance} from './public_qemu_artifacts.mjs';

export const PAGES_URL='https://m5agent.github.io/m5stack-esp-emulator/';
// This labels the reviewed producer artifact, not a successful regular-CI run.
export const REVIEWED_ARTIFACT=Object.freeze({
  kind:'reviewed-artifact-HTTPS-release-preflight',
  artifact_provenance:'prepared-preview-export',
  runtime_origin:'fresh-full-source-build-public-path-policy-v1',
  source_commit:'1b86ed6f7edcc36deafc4834b45a28c6a6017c79',
});
const SHA=/^[a-f0-9]{64}$/;
const REQUIRED_PATCH={path:'patches/qemu-wasm-probe/0027-gpio-bounded-transactions.patch',sha256:'43685da86d9b959b2e769cd9cda5785a5c4039b5076f73f3b9d6033d1d161bdf'};
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function expectedRelease(env,urlKey){
  assert.equal(env[urlKey],PAGES_URL,'Only the confirmed HTTPS Pages project root is allowed');
  const rows={manifest:'M5_PAGES_MANIFEST_SHA256',runtime:'M5_PAGES_RUNTIME_SHA256',wasm:'M5_PAGES_WASM_SHA256',lock:'M5_PAGES_SOURCE_LOCK_SHA256'};
  const expected={url:PAGES_URL};
  for(const [key,name] of Object.entries(rows)){assert.match(env[name]||'',SHA,'Explicit reviewed artifact pin is required: '+name);expected[key]=env[name];}
  return Object.freeze(expected);
}
function safe(path){
  assert.equal(typeof path,'string');
  assert.ok(path&&/^[A-Za-z0-9._/-]+$/.test(path)&&!path.startsWith('/')&&path.split('/').every(p=>p&&p!=='.'&&p!=='..'),'Unsafe remote asset path');
  return path;
}
export function validateRuntimeSource(runtime,lock,lockBytes,expected){
  assert.equal(sha(lockBytes),expected.lock,'Checked-out release source lock differs from explicit reviewed artifact pin');
  assert.equal(lock.qemu.commit,'40edccac415693c5130f91c01d84176ae6008566');
  assert.equal(lock.patches.length,72);assert.equal(lock.native_patch_count,47);
  assert.equal(Object.keys(lock.patched_files).length,160);
  assert.ok(isDeepStrictEqual(runtime.source,{...lock.qemu,native_patch_count:lock.native_patch_count,patches:lock.patches,patched_files_sha256:lock.patched_files}),'Actual remote source, ordered patches or postimages differ from the release lock');
  assert.ok(runtime.source.patches.some(p=>isDeepStrictEqual(p,REQUIRED_PATCH)),'Required GPIO patch is absent');
  assert.equal(runtime.build.kind,'source-build');assert.equal(runtime.build.all_objects_rebuilt,true);
  assert.equal(runtime.build.lock_sha256,expected.lock);assert.equal(runtime.build.emscripten,lock.emsdk.version);
  assert.equal(runtime.assets.wasm.sha256,expected.wasm,'Actual remote WASM differs from explicit reviewed artifact pin');
}
export async function readRemoteRelease({repo,expected,testScript,fetchImpl=globalThis.fetch}){
  assert.equal(expected.url,PAGES_URL);for(const key of ['manifest','runtime','wasm','lock'])assert.match(expected[key]||'',SHA);
  const root=new URL(PAGES_URL),cache=new Map(),fetches=[];
  const fetchCached=async(input,options={})=>{
    const url=new URL(input);assert.ok(url.href.startsWith(root.href)&&url.origin===root.origin,'Cross-origin/path remote metadata request rejected');
    const path=decodeURIComponent(url.pathname.slice(root.pathname.length));safe(path);
    if(!cache.has(url.href)){
      const response=await fetchImpl(url,{...options,redirect:'error',credentials:'omit',referrerPolicy:'no-referrer',cache:'no-store',signal:AbortSignal.timeout(60000)});
      assert.ok(response.ok,'Remote asset unavailable: '+path);
      if(response.url)assert.equal(response.url,url.href,'Remote redirect is not allowed');
      const bytes=Buffer.from(await response.arrayBuffer());cache.set(url.href,bytes);
      fetches.push({path,bytes:bytes.length,sha256:sha(bytes)});
    }
    return new Response(cache.get(url.href),{status:200});
  };
  const get=async path=>Buffer.from(await (await fetchCached(new URL(safe(path),root))).arrayBuffer());
  const manifestBytes=await get('public-site-manifest.json');assert.equal(sha(manifestBytes),expected.manifest,'Actual remote site manifest differs from explicit reviewed artifact pin');
  const manifest=JSON.parse(manifestBytes);assert.equal(manifest.schema_version,1);assert.equal(manifest.kind,'m5stack-public-site');
  assert.equal(manifest.publication_eligible,true);assert.deepEqual(manifest.candidate_profiles,[]);assert.equal(manifest.base_path,root.pathname);
  const declared=new Map();
  for(const row of manifest.assets){safe(row.path);assert.ok(!declared.has(row.path),'Duplicate manifest path');assert.match(row.sha256,SHA);assert.ok(Number.isSafeInteger(row.bytes)&&row.bytes>=0);declared.set(row.path,row);}
  const getAsset=async path=>{
    const row=declared.get(safe(path));assert.ok(row,'Asset absent from actual site manifest: '+path);
    const bytes=await get(path);assert.equal(bytes.length,row.bytes,'Actual remote bytes mismatch: '+path);assert.equal(sha(bytes),row.sha256,'Actual remote SHA mismatch: '+path);return bytes;
  };
  const runtimeBytes=await getAsset('platform/runtime/qemu/runtime.json');assert.equal(sha(runtimeBytes),expected.runtime,'Actual remote runtime manifest differs from explicit reviewed artifact pin');
  const runtime=JSON.parse(runtimeBytes),lockBytes=await readFile(resolve(repo,'scripts/qemu-wasm-build/sources.lock.json')),lock=JSON.parse(lockBytes);
  validateRuntimeSource(runtime,lock,lockBytes,expected);
  const config=JSON.parse(await getAsset('platform/web/site-config.json'));assert.equal(config.publication_eligible,true);assert.deepEqual(config.browser_candidate_profiles,[]);
  assert.equal(config.browser_runtime_engine,'qemu-wasm');
  const registry=JSON.parse(await getAsset('platform/web/qemu-browser-profiles.json'));
  assert.equal(registry.profiles.length,19);assert.ok(registry.profiles.every(p=>p.admission==='public'));
  assert.ok(registry.profiles.some(p=>p.deviceId==='core2'));assert.ok(!registry.profiles.some(p=>p.deviceId==='dial'));
  const provenance=await capturePublicQemuProvenance({repo,publicUrl:PAGES_URL,fetchImpl:fetchCached,testScript});
  assert.equal(provenance.site_manifest_sha256,expected.manifest);assert.equal(provenance.runtime_manifest_sha256,expected.runtime);
  for(const row of Object.values(runtime.assets))await getAsset('platform/runtime/qemu/'+safe(row.path));
  return {url:PAGES_URL,manifest,runtime,expected,provenance,getAsset,fetches,assets:Object.fromEntries(fetches.map(row=>[row.path,{bytes:row.bytes,sha256:row.sha256}]))};
}
export async function prepareRemoteRelease(options){
  const release=await readRemoteRelease(options),{out,repo}=options,dir=resolve(out,'remote-runtime-preflight');await mkdir(dir,{recursive:false});
  await writeFile(resolve(dir,'runtime.json'),await release.getAsset('platform/runtime/qemu/runtime.json'),{flag:'wx'});
  for(const row of Object.values(release.runtime.assets))await writeFile(resolve(dir,safe(row.path)),await release.getAsset('platform/runtime/qemu/'+row.path),{flag:'wx'});
  const verifier=fileURLToPath(new URL('./verify_runtime_archive.py',import.meta.url));
  const child=spawn(process.env.M5_PAGES_PYTHON||'python3',[verifier,repo,dir],{stdio:['ignore','pipe','pipe']});
  let stdout='',stderr='';child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
  const code=await new Promise((yes,no)=>{child.on('error',no);child.on('exit',yes);});
  assert.equal(code,0,'Actual downloaded runtime/archive validation failed: '+stderr);
  const sourceArchive=JSON.parse(stdout);assert.equal(sourceArchive.result,'PASS');
  const proof={...REVIEWED_ARTIFACT,location:'remote-static-host',url:PAGES_URL,expected:release.expected,
    site_manifest_sha256:release.provenance.site_manifest_sha256,runtime_manifest_sha256:release.provenance.runtime_manifest_sha256,
    source_archive:sourceArchive,fetches:release.fetches,source_provenance:release.provenance,
    verifier_sha256:sha(await readFile(verifier)),transport_sha256:sha(await readFile(fileURLToPath(import.meta.url))),
    test_script:options.testScript};
  await writeFile(resolve(out,'remote-release-preflight.json'),JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
  return {...release,proof};
}
export function assertReleaseReceipt(receipt,release){
  assert.equal(receipt.wasmSha256,release.expected.wasm,'Running guest used another WASM');
  assert.equal(receipt.javascriptSha256,release.runtime.assets.javascript.sha256);
  assert.equal(receipt.workerSha256,release.runtime.assets.worker.sha256);
  assert.equal(receipt.sourceCommit,release.runtime.source.commit);
  assert.equal(receipt.clockOverride,null,'Remote acceptance must use the ordinary public profile');
}
export async function adapterIdentity(){
  const identity=JSON.parse(await readFile(new URL('./adapter-identity.json',import.meta.url)));
  for(const row of Object.values(identity.actual_files)){
    safe(row.name);assert.equal(sha(await readFile(new URL(row.name,import.meta.url))),row.sha256,'Adapter/helper changed after the reviewed identity was generated: '+row.name);
  }
  return identity;
}
