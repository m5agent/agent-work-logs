import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname, extname, resolve, sep} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {closedQemuPthreadBroker, observeWorkerTargets} from '../../../platform/tests/public_qemu_worker_targets.mjs';

const lab=dirname(fileURLToPath(import.meta.url)), project=resolve(lab,'../../..');
const [siteDir,mode,outDir]=process.argv.slice(2);
assert.ok(siteDir&&outDir&&['on','preflight'].includes(mode),'Pass private exported site, on|preflight, and a new report directory');
const site=resolve(siteDir), out=resolve(outDir);
assert.ok(out.startsWith(lab+sep),'Reports belong in this ignored lab');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const issueOriginal='https://docs.m5stack.com/en/arduino/m5cardputer/button';
const fixtures=resolve(project,'.work/docs-examples-20261125.U1s7Lf');
const previous=resolve(project,'.work/docs-wasm-arduino-20261125');
const sketch=await readFile(resolve(fixtures,'sketches/cardputer-adv/button/button.ino'));
assert.equal(sha(sketch),'444450396503479b748d137758cab1a70f206b882fccf06bdaac786f81ad0d81');
const cases={
  on:{file:resolve(fixtures,'firmware/cardputer-adv/button/button.ino.merged.bin'),
    input:'07ebcecd82c9a64aad457f5e30eac140bfd24db8006506ea6f04489a860dc0e7',
    flash:'54ee755a50f4187e9ddfc96efb7ea996c896e46d4b99e2945ceb3183a1aa6f50',channel:'usb-serial-jtag'},
};
for(const item of Object.values(cases)){
  const original=await readFile(item.file);
  assert.equal(sha(original),item.input);
  assert.equal(original.length,4194304);
  assert.equal(sha(Buffer.concat([original,Buffer.alloc(4194304,255)])),item.flash);
}
const siteBytes=await readFile(resolve(site,'public-site-manifest.json')), manifest=JSON.parse(siteBytes);
assert.match(manifest.base_path,/^\/(?:[a-zA-Z0-9._~-]+\/)*$/);
const accelerator={kind:'tcg-icount',thread:'single',tbSizeMb:128,icountShift:5};
const minimumObserved=5;
assert.equal(sha(siteBytes),'f9cdc2a5da88a3de49655cb7b9561140f2e5c6f4afff9c00f0abdec3f2a91bd5');
assert.equal(manifest.base_path,'/showcase/');
assert.equal(manifest.publication_eligible,false);
assert.equal(manifest.firmware_bundled,false);
assert.deepEqual(manifest.private_diagnostic,{
  parent_site_manifest_sha256:'cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac',
  accelerator,c_wasm_changed:false,changed_assets:[
    'platform/web/qemu-browser-profiles.json','site-config.json','platform/web/site-config.json'
  ]
});
const assets=new Map(manifest.assets.map(row=>[row.path,row]));
async function asset(path){
  const data=await readFile(resolve(site,path));
  assert.equal(sha(data),assets.get(path)?.sha256,`Manifest identity for ${path}`);
  return data;
}
const runtimeBytes=await asset('platform/runtime/qemu/runtime.json'), runtime=JSON.parse(runtimeBytes);
assert.equal(sha(runtimeBytes),'a56410a8fb99a0e65ce7a7017c3a5ceb8ce0bd832451cbc71e12317cf614a0b9');
assert.equal(runtime.build.lock_sha256,'4ba15619e4613bc886e796d6f6c6cacce7e2f1b9225e424a48c2aaea1aaa36cd');
assert.equal(runtime.assets.wasm.sha256,'210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211');
const patch='patches/qemu-wasm-probe/0044-cardputer-adv-usb-serial-jtag-tx.patch';
assert.deepEqual(runtime.source.patches.filter(row=>row.path===patch),
  [{path:patch,sha256:'730b55228fe499c0b64ee26cfb0bd880d99cd8a7bdc3950a125480be9fb56590'}]);
assert.equal(sha(await asset(`platform/runtime/qemu/${runtime.assets.wasm.path}`)),runtime.assets.wasm.sha256);
const rom=await readFile(resolve(previous,'esp32s3_rev0_rom.bin'));
assert.equal(sha(rom),'b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913');
assert.equal(sha(rom),runtime.required_rom.sha256);
const files=['index.html','site-config.json','platform/web/public.js','platform/web/public-qemu-engine.js',
  'platform/web/public-qemu-runtime.js','platform/web/public-qemu-profiles.js','platform/web/qemu-browser-profiles.json'];
const workbench_asset_sha256=Object.fromEntries(await Promise.all(files.map(async path=>[path,sha(await asset(path))])));
const report={status:'FAIL',kind:'cardputer-adv-private-tcg-icount-button',validation:'virtual-device validation (browser WASM)',mode,
  doc:issueOriginal,sketch_sha256:sha(sketch),rom_sha256:sha(rom),site_manifest_sha256:sha(siteBytes),
  runtime_manifest_sha256:sha(runtimeBytes),source_lock_sha256:runtime.build.lock_sha256,
  wasm_sha256:runtime.assets.wasm.sha256,workbench_asset_sha256,harness_sha256:sha(await readFile(fileURLToPath(import.meta.url))),
  requested_accelerator:accelerator,expected_worker_targets:minimumObserved,blocked_requests:[],page_errors:[],runs:[]};
if(mode==='preflight'){
  console.log(JSON.stringify({...report,status:'PREFLIGHT_OK',validation:'artifact identity only'}));
  process.exit(0);
}

const type={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json',
  '.wasm':'application/wasm','.css':'text/css','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml','.woff2':'font/woff2'};
const server=createServer(async(request,response)=>{
  try{
    const url=new URL(request.url,'http://localhost');
    assert.ok(url.pathname.startsWith(manifest.base_path));
    const key=decodeURIComponent(url.pathname.slice(manifest.base_path.length))||'index.html';
    const path=resolve(site,key);
    assert.ok(path.startsWith(site+sep)&&assets.has(key));
    response.writeHead(200,{'content-type':type[extname(path)]||'application/octet-stream','cache-control':'no-store'}).end(await readFile(path));
  }catch{response.writeHead(404).end();}
});
await mkdir(out);
const save=()=>writeFile(resolve(out,'report.json'),JSON.stringify(report,null,2)+'\n');
let browser,context,page,workers;
const output=channel=>channel==='usb-serial-jtag'?'usb':'uart';
const pressed='Button A Pressed', released='Button A Released';
const read=()=>page.evaluate(()=>{
  const r=globalThis.cdcStudy?.runtime;
  const lastFrame=r?.lastFrame;
  const frame=lastFrame?{width:lastFrame.width,height:lastFrame.height,sequence:lastFrame.sequence,sourceSequence:lastFrame.sourceSequence}:null;
  if(!r)return null;
  const banner=document.querySelector('#errorBanner');
  const chosen=document.querySelector('#serialChannel');
  return {session:r.sessionId,epoch:r.consoleEpoch,generation:r.generation,status:r.status,receipt:r.receipt,
    uart:r.serial,usb:r.usbSerial,usbBytes:r.usbSerialBytes,events:r.machineEvents,
    inputs:r.inputs,diagnostics:r.diagnostics,frame,workerErrors:[...globalThis.cdcWorkerErrors],selectedChannel:chosen?.value,
    uiOptions:Array.from(chosen?.options||[],option=>({value:option.value,label:option.label})),
    uiText:document.querySelector('#serialOutput')?.textContent,sendDisabled:document.querySelector('#serialSendBtn')?.disabled,
    banner:banner&&!banner.hidden?banner.textContent:''};
});
async function waitFor(test,label,timeout=20000){
  const end=performance.now()+timeout;
  let row;
  while(performance.now()<end){
    row=await read();
    if(row?.banner)throw new Error(row.banner);
    if(row&&test(row))return row;
    await page.waitForTimeout(100);
  }
  throw new Error(`Timed out waiting for ${label} (${row?.status})`);
}
async function execute(caseId){
  const expected=cases[caseId], run={case:caseId,firmware_input_sha256:expected.input,expected_channel:expected.channel};
  report.runs.push(run);
  await page.locator('#firmwareFile').setInputFiles(expected.file);
  await page.locator('#firmwareSha').fill(expected.input);
  workers=await observeWorkerTargets(browser);
  const startAt=performance.now();
  await page.locator('#startBtn').click();
  const ready=run.ready=await waitFor(row=>row.status==='running'&&row.receipt?.firmwareInputSha256===expected.input,'exact firmware start',135000);
  assert.ok(ready.session&&!report.runs.slice(0,-1).some(row=>row.ready.session===ready.session));
  run.ready_ms=performance.now()-startAt;
  assert.equal(ready.receipt.profile,'cardputer-adv-wasm-private-button-icount');
  assert.equal(ready.receipt.oneInsnPerTb,false);
  assert.equal(ready.receipt.clockOverride,null);
  assert.deepEqual(ready.receipt.accelerator,accelerator);
  const args=ready.receipt.actualArguments;
  assert.equal(args[args.indexOf('-accel')+1],'tcg,thread=single,tb-size=128');
  assert.equal(args[args.indexOf('-icount')+1],'shift=5,align=off,sleep=off');
  assert.equal(ready.receipt.clockDivisor,1);
  assert.equal(ready.receipt.deviceId,'cardputer-adv');
  assert.equal(ready.receipt.firmwareRuntimeSha256,expected.flash);
  assert.equal(ready.receipt.wasmSha256,report.wasm_sha256);
  assert.deepEqual(ready.receipt.usbSerialJtag,{direction:'guest-to-host',controller:'esp32s3-usb-serial-jtag'});
  run.rom_handoff=await waitFor(row=>/entry 0x[\da-f]+/i.test(row.uart),'ROM handoff');
  run.rom_handoff_ms=performance.now()-startAt;
  await page.waitForTimeout(2500);
  run.settled=await read();
  assert.doesNotMatch(run.settled.uart+run.settled.usb,/Guru Meditation Error|Stack canary watchpoint triggered/);
  const drawer=page.locator('#serialDrawer');
  if(!await drawer.evaluate(element=>element.open))await drawer.locator('summary').click();
  await page.locator('#serialChannel').selectOption(expected.channel);
  const selected=await waitFor(row=>row.selectedChannel===expected.channel&&row.uiOptions.length===2,'distinct console channels');
  assert.equal(selected.uiOptions[1].label,'USB Serial/JTAG');
  if(caseId==='on')assert.equal(selected.sendDisabled,true);
  run.counters_before=await page.evaluate(()=>cdcStudy.runtime.readUsbSerialJtag());
  run.active_topology=await workers.snapshotQemuTopology();
  assert.ok(run.active_topology.ok);
  assert.equal(run.active_topology.engine_count+run.active_topology.pthread_count,minimumObserved);
  await page.locator('#deviceMount .three-device-stage canvas').focus();
  const channel=output(expected.channel);
  const timer=performance.now();
  await page.keyboard.down('F12');
  try{
    run.press=await waitFor(row=>row[channel].includes(pressed)&&row.uiText.includes(pressed)&&!row[channel].includes(released)
      &&row.inputs.some(input=>input.type==='button'&&input.id==='boot'&&input.down),'pressed while G0/F12 is held');
  }finally{
    run.f12_hold_ms=performance.now()-timer;
    await page.keyboard.up('F12');
  }
  const final=run.final=await waitFor(row=>row[channel].includes(released)&&row.uiText.includes(released)
    &&row.inputs.some(input=>input.type==='button'&&input.id==='boot'&&!input.down),'released through same guest and UI channel');
  assert.equal(ready.session,final.session);
  assert.equal(ready.epoch,final.epoch);
  assert.equal(ready.generation,final.generation);
  assert.ok(!final.events.some(event=>event.event==='RESET'));
  assert.deepEqual(final.inputs.filter(input=>input.id==='boot').map(input=>[input.type,input.down]),[['button',true],['button',false]]);
  const inactive=caseId==='on'?'uart':'usb';
  assert.doesNotMatch(final[inactive],/Button A (Pressed|Released)/);
  assert.match(final.uart,/ESP-ROM:esp32s3/);
  assert.deepEqual(final.workerErrors,[]);
  assert.doesNotMatch(final.uart+final.usb,/Guru Meditation Error|Stack canary watchpoint triggered/);
  run.counters_after=await page.evaluate(()=>cdcStudy.runtime.readUsbSerialJtag());
  assert.equal(run.counters_after.consoleEpoch,ready.epoch);
  const deltaBytes=run.counters_after.txBytes-run.counters_before.txBytes;
  const deltaPackets=run.counters_after.txPackets-run.counters_before.txPackets;
  if(caseId==='on')assert.ok(deltaBytes>=pressed.length+released.length&&deltaPackets>=2);
  else assert.equal(deltaBytes,0);
  assert.equal(run.counters_after.txBytes,final.usbBytes);
  await drawer.screenshot({path:resolve(out,`cdc-${caseId}-serial.png`)});
  run.topology=await workers.snapshotQemuTopology();
  assert.ok(run.topology.ok);
  await page.locator('#stopBtn').click();
  await page.waitForFunction(()=>cdcStudy.runtime.status==='stopped'&&cdcStudy.runtime.cleanupResult?.iframeRemoved,{}, {timeout:60000});
  const cleanup=run.cleanup=await page.evaluate(()=>cdcStudy.runtime.cleanupResult);
  assert.ok(cleanup.exitCode===0&&cleanup.gracefulExit&&cleanup.workersAtExit===0
    &&cleanup.engineOwnership.engineFinalizationAcknowledged&&cleanup.engineOwnership.engineFallbackTerminations===0
    &&closedQemuPthreadBroker(cleanup));
  const closed=run.dedicated_workers=await workers.waitUntilClosed({minimumObserved});
  assert.equal(cleanup.workersCreated,minimumObserved-1);
  assert.ok(closed.ok&&closed.observed.length===minimumObserved&&!closed.live.length);
  await workers.detach();workers=null;
  console.log(JSON.stringify({case:caseId,channel:expected.channel,deltaBytes,deltaPackets,workers:closed.observed.length}));
  await save();
}

try{
  await save();
  await new Promise(done=>server.listen(0,'127.0.0.1',done));
  const url=new URL(`http://127.0.0.1:${server.address().port}${manifest.base_path}`);
  url.searchParams.set('device','cardputer-adv');url.searchParams.set('mode','browser');
  const modules=process.env.M5_WASM_NODE_MODULES||resolve(project,'platform/tests/node_modules');
  const {chromium}=await import(pathToFileURL(resolve(modules,'playwright/index.mjs')));
  browser=await chromium.launch({headless:true,executablePath:process.env.M5_WASM_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args:['--enable-webgl','--use-gl=angle','--use-angle=metal','--ignore-gpu-blocklist']});
  report.browser=browser.version();
  context=await browser.newContext({viewport:{width:1440,height:1000}});
  await context.addInitScript(()=>{
    globalThis.cdcWorkerErrors=[];
    globalThis.Worker=new Proxy(globalThis.Worker,{construct(NativeWorker,args,newTarget){
      const worker=Reflect.construct(NativeWorker,args,newTarget);
      const observe=event=>globalThis.cdcWorkerErrors.push({name:args[1]?.name||'',kind:event.type,
        message:event.message||null,file:event.filename||null,line:event.lineno||null,column:event.colno||null});
      worker.addEventListener('error',observe);
      worker.addEventListener('messageerror',observe);
      return worker;
    }});
  });
  await context.route(target=>['http:','https:'].includes(target.protocol)
    &&(target.origin!==url.origin||/\/api\/v1(?:\/|$)/.test(target.pathname)),route=>{
    const request=route.request().url();
    if(request===runtime.required_rom.url)return route.fulfill({status:200,body:rom,contentType:'application/octet-stream',
      headers:{'access-control-allow-origin':'*','cross-origin-resource-policy':'cross-origin'}});
    report.blocked_requests.push(new URL(request).hostname+new URL(request).pathname);
    return route.abort('blockedbyclient');
  });
  page=await context.newPage();page.on('pageerror',error=>report.page_errors.push(error.message));
  await page.goto(url.href,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>crossOriginIsolated&&typeof SharedArrayBuffer==='function'
    &&document.querySelector('#deviceMount')?.dataset.deviceId==='cardputer-adv'
    &&document.querySelector('#runtimeMode')?.value==='browser',{}, {timeout:60000});
  await page.evaluate(async prefix=>{
    const {PublicQemuRuntime}=await import(new URL('platform/web/public-qemu-runtime.js',prefix));
    const start=PublicQemuRuntime.prototype.start;
    globalThis.cdcStudy={runtime:null};
    PublicQemuRuntime.prototype.start=function(...args){
      if(args[0].device==='cardputer-adv')cdcStudy.runtime=this;
      return start.apply(this,args);
    };
  },new URL(manifest.base_path,url).href);
  const advanced=page.locator('.advanced-options');
  if(!await advanced.evaluate(details=>details.open))await advanced.locator('summary').click();
  await page.locator('input[name="firmwareSource"][value="local"]').check();
  await execute(mode);
  assert.deepEqual(report.page_errors,[]);assert.deepEqual(report.blocked_requests,[]);
  report.status='PASS';
}catch(error){
  report.error=String(error.stack||error);
  if(page&&!page.isClosed()){
    await page.waitForTimeout(300);
    report.failure=await read().catch(()=>null);
    await page.screenshot({path:resolve(out,'failure.png'),fullPage:true}).catch(()=>{});
    await page.evaluate(()=>globalThis.cdcStudy?.runtime?.stop()).catch(()=>{});
    report.failure_shutdown=await page.evaluate(()=>globalThis.cdcStudy?.runtime?.cleanupResult).catch(()=>null);
    if(workers)report.failure_cleanup=await workers.waitUntilClosed({minimumObserved:0}).catch(()=>null);
  }
  process.exitCode=1;
}finally{
  await workers?.detach();await context?.close();await browser?.close();
  if(server.listening)await new Promise(done=>server.close(done));
  await save();
  console.log(JSON.stringify({mode,status:report.status,error:report.error}));
}
