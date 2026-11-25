import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname,extname,resolve,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

assert.equal(process.env.M5_NFC_131_RUN,'1','Enable the isolated guest explicitly');
const ref=fileURLToPath(import.meta.url),lab=dirname(ref),workspace=resolve(lab,'../..');
const repo=resolve(workspace,'.work/docs-wasm-cardputer-adv-sx1262-source');
const docs=resolve(workspace,'.work/docs-uiflow-20261125');
const [mode,outputName]=process.argv.slice(2);
assert.ok(['stock','candidate'].includes(mode));
assert.match(outputName??'',/^browser-0046-nfccap-131-[a-z0-9-]+$/);
const output=resolve(lab,outputName);
const site=resolve(workspace,'.work/docs-wasm-cardputer-lora-lab/locked-0046-site');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const patchReceipt=JSON.parse(await readFile(resolve(lab,'candidate-source.receipt.json')));
const capsule=await readFile(resolve(lab,'nfccap-131-capsule.py'),'utf8');
const original=await readFile(resolve(docs,'upstream',patchReceipt.original_example_path));
assert.equal(sha(capsule),patchReceipt.candidate_capsule_sha256);
assert.equal(sha(original),patchReceipt.original_example_sha256);
const editorOriginal=original.toString('utf8').replace(/\r\n?/g,'\n');
assert.equal(sha(editorOriginal),patchReceipt.original_example_sha256);

const manifestBytes=await readFile(resolve(site,'public-site-manifest.json'));
const manifest=JSON.parse(manifestBytes);
assert.equal(manifest.base_path,'/showcase/');
assert.equal(sha(manifestBytes),'cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac');
const assets=new Map(manifest.assets.map(row=>[row.path,row]));
async function verified(path){
  const bytes=await readFile(resolve(site,path));
  assert.equal(sha(bytes),assets.get(path)?.sha256,path);
  assert.equal(bytes.length,assets.get(path)?.bytes,path);
  return bytes;
}
const toolkit=path=>pathToFileURL(resolve(repo,'platform/tests',path));
const {capturePublicQemuProvenance,QEMU_EXECUTED_WEB_PATHS}=await import(toolkit('public_qemu_artifacts.mjs'));
const {observeWorkerTargets,closedQemuPthreadBroker}=await import(toolkit('public_qemu_worker_targets.mjs'));
const provenance=await capturePublicQemuProvenance({repo,site,webPaths:[
  ...QEMU_EXECUTED_WEB_PATHS,'platform/web/public-micropython.js','platform/web/public-uiflow-firmware.js',
  'platform/web/uiflow-workbench-profiles.json',
]});
const expectedWasm='210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211';
const firmwareSHA='b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd';
assert.equal(provenance.runtime_assets['qemu-system-xtensa.wasm'].sha256,expectedWasm);
assert.equal(provenance.runtime_build.all_objects_rebuilt,true);
const runtime=JSON.parse(await verified('platform/runtime/qemu/runtime.json'));
const nfcC='hw/m5stopwatch/m5_st25r3916_spi.c';
const c=await readFile(resolve(workspace,'.work/docs-wasm-cardputer-lora-lab/locked-0046-build/qemu',nfcC));
assert.equal(sha(c),runtime.source.patched_files_sha256[nfcC]);
const browserProfiles=JSON.parse(await verified('platform/web/qemu-browser-profiles.json'));
const workbenchProfiles=JSON.parse(await verified('platform/web/uiflow-workbench-profiles.json'));
const board=browserProfiles.profiles.find(row=>row.deviceId==='cardputer-adv');
const adv=workbenchProfiles.profiles.find(row=>row.deviceId==='cardputer-adv');
assert.equal(adv.firmwareSHA256,firmwareSHA);
const base=await readFile(resolve(workspace,'.work/docs-wasm-cardputer-cc1101-lab/cardputer-adv-v2.5.3-base.bin'));
const rom=await readFile(resolve(workspace,'.work/docs-wasm-arduino-20261125/esp32s3_rev0_rom.bin'));
assert.equal(sha(base),adv.baseSHA256);
assert.equal(base.length,adv.baseBytes);
assert.equal(sha(rom),board.roms[0].sha256);
assert.equal(rom.length,board.roms[0].bytes);
const dir=process.env.M5_WASM_NODE_MODULES??resolve(workspace,'platform/tests/node_modules');
const downloads=new Map([[board.reference.url,base],[board.roms[0].url,rom]]);
const generator_sha256=sha(await readFile(resolve(lab,'prepare-nfc-candidate.py')));
const runner_sha256=sha(await readFile(ref));
if(process.env.M5_NFC_131_PREFLIGHT==='1'){
  console.log(JSON.stringify({status:'PREFLIGHT_PASS',mode,wasm:expectedWasm,firmware:firmwareSHA,
    site:provenance.site_manifest_sha256,controller_sha256:sha(c),runner_sha256,generator_sha256,candidate:patchReceipt}));
  process.exit(0);
}
const {chromium}=await import(pathToFileURL(resolve(dir,'playwright/index.mjs')));
await mkdir(output);

const mime={'.html':'text/html','.css':'text/css','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json',
  '.wasm':'application/wasm','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml'};
const server=createServer(async(request,response)=>{
  try{
    const pathname=new URL(request.url,'http://localhost').pathname;
    assert.ok(pathname.startsWith(manifest.base_path));
    const name=decodeURIComponent(pathname.slice(manifest.base_path.length))||'index.html';
    const file=resolve(site,name);
    assert.ok(file.startsWith(site+sep)&&assets.has(name));
    response.writeHead(200,{'content-type':mime[extname(file)]??'application/octet-stream','Cache-Control':'no-store',
      'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp',
      'Cross-Origin-Resource-Policy':'same-origin'}).end(await readFile(file));
  }catch{response.writeHead(404).end();}
});
const report={kind:'nfccap-131-private-sdk-comparison',status:'FAIL',mode,evidence_level:'virtual-device validation',provenance,
  touched_release_sdk:patchReceipt,controller_file:nfcC,controller_sha256:sha(c),runner_sha256,generator_sha256,programs:[],page_errors:[]};
const checkpoint=()=>writeFile(resolve(output,'report.json'),JSON.stringify(report,null,2)+'\n');
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let browser,context,workers,page,address;
async function until(label,read,match,timeout=22000){
  const stop=performance.now()+timeout;
  let value;
  do{
    value=await read();
    if(match(value))return value;
    await delay(65);
  }while(performance.now()<stop);
  throw new Error(label+': '+JSON.stringify(value)?.slice(-650));
}
const readRun=index=>page.evaluate(index=>guestRuns[index],index);
const frame=()=>page.evaluate(()=>{
  const value=guest.evidence().last_frame;
  if(!value)return null;
  const {pixels,...identity}=value;
  return identity;
});
function witnessSame(row){
  assert.equal(row.result?.transfer,'raw-paste');
  assert.equal(row.result?.sessionId,report.session.sessionId);
  assert.equal(row.result?.consoleEpoch,report.session.consoleEpoch);
}
async function runProgram(name,source,{file=false,running=false}={}){
  const index=await page.evaluate(()=>guestRuns.length);
  if(file)await page.locator('#pythonFile').setInputFiles({name:'cc1101_cap_nfc_read_id_example.py',mimeType:'text/x-python',buffer:original});
  else await page.locator('#pythonSource').fill(source);
  assert.equal(await page.locator('#pythonSource').inputValue(),source);
  await page.locator('#pythonRunBtn').click();
  const observed=await until(name,()=>readRun(index),entry=>running?entry?.phase==='running'||entry?.finished:entry?.finished);
  assert.equal(observed.source,source);
  const row={name,index,source_sha256:sha(source),phase:observed.phase};
  if(observed.finished){
    row.result=observed.result;row.error=observed.error;
    witnessSame(observed);
  }
  report.programs.push(row);
  return {index,row,observed};
}
const stockProbe=`import M5
from cap import NFCCap
from unit.nfc import NFCUnit
M5.begin()
assert issubclass(NFCCap, NFCUnit)
try:
    NFCCap()
except TypeError as exc:
    print("NFC_STOCK_TYPEERROR", str(exc))
else:
    raise RuntimeError("Stock constructor did not reproduce")
`;
const installProbe=`import os, sys, hashlib, binascii
import cap.cc1101 as cap_impl
from cap import NFCCap
from unit.nfc import NFCUnit
assert cap_impl.NFCCap is NFCCap and issubclass(NFCCap, NFCUnit)
name = "_m5_nfccap_131_candidate"
assert name not in sys.modules
cwd = os.getcwd()
assert cwd in ("/", "/flash")
filename = cwd.rstrip("/") + "/" + name + ".py"
assert name + ".py" not in os.listdir(cwd)
payload = ${JSON.stringify(capsule)}.encode()
digest = binascii.hexlify(hashlib.sha256(payload).digest()).decode()
assert digest == "${patchReceipt.candidate_capsule_sha256}"
with open(filename, "wb") as dst:
    dst.write(payload)
try:
    sys.path.insert(0, cwd)
    try:
        candidate = __import__(name)
    finally:
        sys.path.pop(0)
finally:
    os.remove(filename)
previous = NFCCap.__init__
NFCCap.__init__ = candidate.__init__
assert NFCCap.__init__ is candidate.__init__ and previous is not candidate.__init__
reader = NFCCap()
assert reader.chip is reader._chip
print("NFC_CAPSULE", digest)
print("NFC_INIT_OK", reader.chip.read_reg8(0x3f))
`;
const appReadback=`import binascii
from cap import NFCCap
assert isinstance(cap_nfc, NFCCap) and cap_nfc.chip is cap_nfc._chip
assert card_0
print("NFC_APP_READBACK", binascii.hexlify(card_0.uid).decode(), card_uid, card_0.type_name, card_0.user_memory)
print("NFC_APP_VENDOR", cap_nfc.chip.read_reg8(0x3f))
`;

try{
  await new Promise(done=>server.listen(0,'127.0.0.1',done));
  address=`http://127.0.0.1:${server.address().port}${manifest.base_path}`;
  browser=await chromium.launch({headless:true,
    ...(process.env.M5_WASM_CHROME?{executablePath:process.env.M5_WASM_CHROME}:{}),
    args:['--enable-webgl','--use-gl=angle','--use-angle=metal','--ignore-gpu-blocklist']});
  report.browser=browser.version();
  workers=await observeWorkerTargets(browser);
  context=await browser.newContext({viewport:{width:1440,height:1100}});
  await context.route('**/*',route=>{
    const url=route.request().url();
    if(url.startsWith(address)&&!/\/api\/v1(?:\/|$)/.test(url))return route.continue();
    const body=downloads.get(url);
    if(!body)return route.abort('blockedbyclient');
    return route.fulfill({status:200,body,contentType:'application/octet-stream',
      headers:{'Access-Control-Allow-Origin':'*','Cross-Origin-Resource-Policy':'cross-origin'}});
  });
  page=await context.newPage();
  page.on('pageerror',error=>report.page_errors.push(error.message));
  await page.goto(address,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>crossOriginIsolated&&document.querySelector('#deviceMount')?.dataset.deviceId);
  await page.evaluate(async address=>{
    const {PublicQemuRuntime}=await import(new URL('platform/web/public-qemu-runtime.js',address));
    const {PublicMicroPythonRunner}=await import(new URL('platform/web/public-micropython.js',address));
    const start=PublicQemuRuntime.prototype.start;
    PublicQemuRuntime.prototype.start=function(opts){globalThis.guest=this;return start.call(this,opts);};
    globalThis.guestRuns=[];
    const run=PublicMicroPythonRunner.prototype.run;
    PublicMicroPythonRunner.prototype.run=async function(source,opts={}){
      const entry={source};guestRuns.push(entry);
      try{
        entry.result=await run.call(this,source,{...opts,onPhase(phase){entry.phase=phase;opts.onPhase?.(phase);}});
        return entry.result;
      }catch(error){entry.error=error.message;throw error;}
      finally{entry.finished=true;}
    };
  },address);
  await page.locator('button[data-device-id="cardputer-adv"]').click();
  await page.waitForFunction(()=>document.querySelector('#deviceMount')?.dataset.deviceId==='cardputer-adv');
  assert.equal(await page.locator('#referenceExample').inputValue(),'uiflow');
  // The standard Cap profile attaches both real SPI models. Pair tools remain untouched.
  await page.locator('#referenceExample').selectOption('cc1101-rf-rx');
  await page.locator('#startBtn').click();
  await page.waitForFunction(()=>globalThis.guest?.status==='running'&&guest.guestReady(),null,{timeout:120000});
  report.session=await page.evaluate(()=>({receipt:guest.receipt,sessionId:guest.sessionId,consoleEpoch:guest.consoleEpoch}));
  const receipt=report.session.receipt;
  assert.equal(receipt.capExample,'cc1101-rf-rx');
  assert.equal(receipt.capPeer,true);
  assert.equal(receipt.firmwareInputSha256,firmwareSHA);
  assert.equal(receipt.firmwareRuntimeSha256,firmwareSHA);
  assert.equal(receipt.wasmSha256,expectedWasm);
  assert.equal(receipt.clockDivisor,1);
  assert.equal(receipt.oneInsnPerTb,true);
  assert.equal(receipt.sx1262Example,undefined);
  const stock=await runProgram('stock-constructor-no-candidate',stockProbe);
  assert.match(stock.row.result.stdout,/NFC_STOCK_TYPEERROR unexpected keyword argument.*chip/);
  const stockApp=await runProgram('unchanged-stock-app',editorOriginal,{file:true});
  report.stock_frame=await frame();
  assert.ok(report.stock_frame?.sha256&&report.stock_frame.width===240&&report.stock_frame.height===135);
  await page.screenshot({path:resolve(output,'stock.png')});
  await checkpoint();

  if(mode==='candidate'){
    const init=await runProgram('capsule-import-bind-and-read-real-chip',installProbe);
    assert.match(init.row.result.stdout,new RegExp('NFC_CAPSULE '+patchReceipt.candidate_capsule_sha256+'\\b'));
    assert.match(init.row.result.stdout,/NFC_INIT_OK 42\b/);
    assert.equal(init.row.result.stderr,'');
    const app=await runProgram('unchanged-candidate-app',editorOriginal,{file:true,running:true});
    assert.equal(app.observed.finished,undefined);
    await delay(4500);
    const active=await readRun(app.index);
    assert.equal(active.finished,undefined,'original loop continued after construction');
    report.candidate_frame=await until('candidate original app produces its own frame',frame,
      row=>row?.sha256&&row.sha256!==report.stock_frame.sha256&&row.width===240&&row.height===135);
    await page.screenshot({path:resolve(output,'candidate.png')});
    await page.locator('#pythonInterruptBtn').click();
    const ended=await until('interrupt original candidate app',()=>readRun(app.index),r=>r?.finished);
    witnessSame(ended);
    assert.equal(ended.result.interrupted,true);
    app.row.result=ended.result;
    const observed=await runProgram('read-only-original-app-witness',appReadback);
    assert.match(observed.row.result.stdout,/NFC_APP_READBACK deadbeef\b/i);
    assert.match(observed.row.result.stdout,/NFC_APP_VENDOR 42\b/);
    assert.equal(observed.row.result.stderr,'');
    const inputs=await page.evaluate(()=>guest.evidence().inputs);
    assert.equal(inputs.some(row=>row.type==='cc1101-peer-frame'||row.type==='sx1262-peer-packet'),false,
      'virtual card comes entirely from model state');
    report.virtual_tag_only=true;
  }
  assert.deepEqual(report.page_errors,[]);
  report.status='DATA_PASS';
}catch(error){
  report.error=error.stack??String(error);
  process.exitCode=1;
}finally{
  if(page&&await page.evaluate(()=>Boolean(globalThis.guest)).catch(()=>false)){
    report.failure_output=await page.locator('#pythonOutput').textContent().catch(()=>null);
    report.failure_frame=await frame().catch(()=>null);
    if(report.status==='FAIL')await page.screenshot({path:resolve(output,'last-visible.png')}).catch(()=>{});
    try{
      report.dom_stop=await page.locator('#stopBtn').isVisible();
      if(report.dom_stop)await page.locator('#stopBtn').click();
      else if(await page.evaluate(()=>guest.status!=='stopped'))await page.evaluate(()=>guest.stop());
      await page.waitForFunction(()=>guest.status==='stopped',null,{timeout:45000});
      report.final=await page.evaluate(()=>({status:guest.status,sessionId:guest.sessionId,consoleEpoch:guest.consoleEpoch,
        cleanup:guest.cleanupResult,serial:guest.serial.slice(-12000)}));
    }catch(error){
      report.cleanup_error=error.message;
      await page.evaluate(()=>globalThis.guest?.stop()).catch(()=>{});
      process.exitCode=1;
    }
  }
  if(workers){
    const expected=Math.max(1,(report.final?.cleanup?.workersCreated??0)+1);
    report.worker_cleanup=await workers.waitUntilClosed({minimumObserved:expected,timeoutMs:30000})
      .catch(error=>({ok:false,error:error.message}));
    if(report.status==='DATA_PASS'){
      const f=report.final;
      const good=f?.cleanup?.gracefulExit&&f.cleanup.exitCode===0&&report.dom_stop&&f.cleanup.iframeRemoved
        &&f.sessionId===report.session.sessionId&&f.consoleEpoch===report.session.consoleEpoch&&closedQemuPthreadBroker(f.cleanup)
        &&report.worker_cleanup.ok&&report.worker_cleanup.observed.length===expected;
      report.status=good?'PASS':'FAIL';
      if(!good)process.exitCode=1;
    }
  }
  await checkpoint();
  await workers?.detach();await context?.close();await browser?.close();
  await new Promise(done=>server.close(done));
  console.log(JSON.stringify({status:report.status,mode,error:report.error??null,workers:report.worker_cleanup?.observed?.length??0}));
}
