// Offline host controls only: fake HTTP fixtures never become guest evidence.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {PAGES_URL,REVIEWED_ARTIFACT,expectedRelease,readRemoteRelease,assertReleaseReceipt} from './pages_remote_release.mjs';
import {QEMU_EXECUTED_WEB_PATHS} from './public_qemu_artifacts.mjs';
const repo=resolve(fileURLToPath(new URL('../..',import.meta.url))),results=[];
const sha=b=>createHash('sha256').update(b).digest('hex'),json=v=>Buffer.from(JSON.stringify(v)+'\n');
const lockBytes=await readFile(resolve(repo,'scripts/qemu-wasm-build/sources.lock.json'));
const runtimeBase=JSON.parse(await readFile(resolve(repo,'.work/perf-final-r6-site/platform/runtime/qemu/runtime.json')));
const canonicalRegistry=JSON.parse(await readFile(resolve(repo,'platform/web/qemu-browser-profiles.json')));
async function fixture(mutator=()=>{}){
  const runtime=structuredClone(runtimeBase),files=new Map();
  for(const path of QEMU_EXECUTED_WEB_PATHS){
    const source=await readFile(resolve(repo,path));
    files.set(path,path.endsWith('qemu-browser-profiles.json')
      ?json({...canonicalRegistry,profiles:canonicalRegistry.profiles.filter(p=>p.admission==='public'&&runtime.compiled_profiles.includes(p.deviceId))})
      :Buffer.from(source.toString('utf8').replace(/(?<=["'\u0060(])\/(platform|devices|data)\//g,(_,g)=>'/m5stack-esp-emulator/'+g+'/')));
  }
  files.set('index.html',files.get('platform/web/index.html'));files.set('coi-serviceworker.js',files.get('platform/web/public-coi-serviceworker.js'));
  files.set('platform/web/site-config.json',json({publication_eligible:true,browser_candidate_profiles:[],browser_runtime_engine:'qemu-wasm'}));
  for(const [key,row] of Object.entries(runtime.assets)){
    const bytes=key==='wasm'?Buffer.from([0,97,115,109,1,0,0,0]):Buffer.from('offline transport-only fixture '+key);
    runtime.assets[key]={...row,bytes:bytes.length,sha256:sha(bytes)};files.set('platform/runtime/qemu/'+row.path,bytes);
  }
  mutator({runtime,files});files.set('platform/runtime/qemu/runtime.json',json(runtime));
  const manifest={schema_version:1,kind:'m5stack-public-site',base_path:'/m5stack-esp-emulator/',publication_eligible:true,candidate_profiles:[],assets:[...files].map(([path,b])=>({path,bytes:b.length,sha256:sha(b)}))};
  const expected={url:PAGES_URL,manifest:'',runtime:sha(files.get('platform/runtime/qemu/runtime.json')),wasm:runtime.assets.wasm.sha256,lock:sha(lockBytes)};
  const refresh=()=>{files.set('public-site-manifest.json',json(manifest));expected.manifest=sha(files.get('public-site-manifest.json'));};
  refresh();const calls=[];
  const fetchImpl=async input=>{calls.push(String(input));const path=new URL(input).pathname.slice('/m5stack-esp-emulator/'.length);return files.has(path)?new Response(files.get(path),{status:200}):new Response('',{status:404});};
  return {files,runtime,manifest,expected,refresh,calls,fetchImpl};
}
async function check(name,fn){await fn();results.push({name,status:'PASS'});}
await check('mandatory explicit reviewed artifact pins and exact HTTPS project root',async()=>{
  assert.throws(()=>expectedRelease({M5_BENCH_URL:PAGES_URL},'M5_BENCH_URL'),/Explicit reviewed artifact pin/);
  for(const url of [PAGES_URL+'?x=1',PAGES_URL+'other/',PAGES_URL.replace('https:','http:'),'https://example.com/'])
    assert.throws(()=>expectedRelease({M5_BENCH_URL:url},'M5_BENCH_URL'),/confirmed HTTPS/);
});
await check('actual offline fetch closure and canonical source provenance',async()=>{
  const f=await fixture(),r=await readRemoteRelease({repo,expected:f.expected,testScript:'.work/pages-remote-tools/benchmark.mjs',fetchImpl:f.fetchImpl});
  assert.deepEqual(REVIEWED_ARTIFACT,{kind:'reviewed-artifact-HTTPS-release-preflight',artifact_provenance:'prepared-preview-export',runtime_origin:'fresh-full-source-build-public-path-policy-v1',source_commit:'1b86ed6f7edcc36deafc4834b45a28c6a6017c79'});
  assert.equal(Object.isFrozen(REVIEWED_ARTIFACT),true);
  assert.equal(r.provenance.location,'remote-static-host');assert.equal(r.provenance.site_manifest_sha256,f.expected.manifest);
  assert.equal(new Set(f.calls).size,f.calls.length);assert.ok(f.calls.every(u=>u.startsWith(PAGES_URL)));
  for(const asset of Object.values(f.runtime.assets))assert.ok(f.calls.includes(PAGES_URL+'platform/runtime/qemu/'+asset.path));
  assertReleaseReceipt({wasmSha256:f.expected.wasm,javascriptSha256:f.runtime.assets.javascript.sha256,workerSha256:f.runtime.assets.worker.sha256,sourceCommit:f.runtime.source.commit,clockOverride:null},r);
  assert.throws(()=>assertReleaseReceipt({wasmSha256:'0'.repeat(64)},r),/another WASM/);
});
for(const [name,mutate] of [
  ['ordered patch removed',({runtime})=>runtime.source.patches.pop()],
  ['actual postimage metadata changed',({runtime})=>runtime.source.patched_files_sha256['hw/gpio/esp32_gpio.c']='0'.repeat(64)],
  ['required GPIO patch changed',({runtime})=>runtime.source.patches.find(p=>p.path.endsWith('0027-gpio-bounded-transactions.patch')).sha256='0'.repeat(64)],
  ['incremental build rejected',({runtime})=>runtime.build.all_objects_rebuilt=false],
  ['runtime source lock changed',({runtime})=>runtime.build.lock_sha256='0'.repeat(64)],
]){
 await check(name,async()=>{const f=await fixture(mutate);await assert.rejects(()=>readRemoteRelease({repo,expected:f.expected,testScript:'.work/pages-remote-tools/benchmark.mjs',fetchImpl:f.fetchImpl}));});
}
await check('wrong reviewed site/runtime/WASM/lock pins rejected',async()=>{
 for(const key of ['manifest','runtime','wasm','lock']){const f=await fixture();f.expected[key]='0'.repeat(64);await assert.rejects(()=>readRemoteRelease({repo,expected:f.expected,testScript:'.work/pages-remote-tools/benchmark.mjs',fetchImpl:f.fetchImpl}));}
});
await check('tampered actual runtime bytes rejected',async()=>{
 const f=await fixture();f.files.set('platform/runtime/qemu/qemu-system-xtensa.wasm',Buffer.from('tampered'));
 await assert.rejects(()=>readRemoteRelease({repo,expected:f.expected,testScript:'.work/pages-remote-tools/benchmark.mjs',fetchImpl:f.fetchImpl}),/mismatch/);
});
await check('source bytes changed even with repinned site metadata rejected',async()=>{
 const f=await fixture();const path='platform/web/public.js',b=Buffer.concat([f.files.get(path),Buffer.from('\n// mutated')]);f.files.set(path,b);
 Object.assign(f.manifest.assets.find(r=>r.path===path),{bytes:b.length,sha256:sha(b)});f.refresh();
 await assert.rejects(()=>readRemoteRelease({repo,expected:f.expected,testScript:'.work/pages-remote-tools/benchmark.mjs',fetchImpl:f.fetchImpl}),/current source/);
});
await check('candidate/private manifest and unsafe/duplicate paths rejected',async()=>{
 for(const mode of ['private','candidate','unsafe','duplicate']){
  const f=await fixture();if(mode==='private')f.manifest.publication_eligible=false;
  if(mode==='candidate')f.manifest.candidate_profiles=['dial'];
  if(mode==='unsafe')f.manifest.assets.push({path:'../escape',sha256:'a'.repeat(64),bytes:1});
  if(mode==='duplicate')f.manifest.assets.push(f.manifest.assets[0]);f.refresh();
  await assert.rejects(()=>readRemoteRelease({repo,expected:f.expected,testScript:'.work/pages-remote-tools/benchmark.mjs',fetchImpl:f.fetchImpl}));
 }
});
await check('redirected responses rejected',async()=>{
 const f=await fixture();await assert.rejects(()=>readRemoteRelease({repo,expected:f.expected,testScript:'.work/pages-remote-tools/benchmark.mjs',
 fetchImpl:async input=>({ok:true,url:'https://example.com/',arrayBuffer:async()=>new ArrayBuffer(0)})}),/redirect/);
});
await check('no createServer and unchanged original runtime/UI/metrics/input/cleanup body',async()=>{
 for(const name of ['benchmark.mjs','board_guest.mjs']){const s=await readFile(new URL(name,import.meta.url),'utf8');assert.doesNotMatch(s,/\bcreateServer\b|\.listen\s*\(/);}
 for(const name of ['emulator_performance_summary.mjs','public_qemu_worker_targets.mjs','public_qemu_performance.mjs','public_qemu_artifacts.mjs'])
  assert.deepEqual(await readFile(new URL(name,import.meta.url)),await readFile(resolve(repo,'platform/tests',name)));
 const parent=await readFile(resolve(repo,'platform/tests/benchmark_emulator_firmware.mjs'),'utf8'),actual=(await readFile(new URL('benchmark.mjs',import.meta.url),'utf8')).replace('assertReleaseReceipt(row.receipt,remoteRelease);','');
 assert.equal(actual.slice(actual.indexOf('function guestFailureObservations'),actual.indexOf('try{\n  const remoteRelease=')),parent.slice(parent.indexOf('function guestFailureObservations'),parent.indexOf('try{\n  let url;')));
 assert.equal(actual.slice(actual.indexOf('  for(let i=0;i<runs;i++){')),parent.slice(parent.indexOf('  for(let i=0;i<runs;i++){')));
 const boardParent=await readFile(resolve(repo,'platform/tests/test_public_qemu_board_guest.mjs'),'utf8'),board=(await readFile(new URL('board_guest.mjs',import.meta.url),'utf8')).replace('assertReleaseReceipt(first.receipt,remoteRelease);','');
 assert.equal(board.slice(board.indexOf('  const textureReadback =')),boardParent.slice(boardParent.indexOf('  const textureReadback =')));
});
const result={kind:'offline-host-transport-controls',result:'PASS',guest_execution:'NOT RUN',server_started:false,network_fetches:'fake fixtures only',checks:results};
await writeFile(new URL('./offline-controls.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
