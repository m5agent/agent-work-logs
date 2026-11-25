// Private two-guest reproduction using unchanged official RF examples.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname,extname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {capturePublicQemuProvenance,QEMU_EXECUTED_WEB_PATHS} from '../platform/tests/public_qemu_artifacts.mjs';
import {observeWorkerTargets,closedQemuPthreadBroker} from '../platform/tests/public_qemu_worker_targets.mjs';

assert.equal(process.env.M5_CC1101_DUAL_RUN,'1','Explicit private two-guest browser authorization required');
const repo=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const workspace=resolve(repo,'../..');
const lab=resolve(workspace,'.work/docs-wasm-cardputer-cc1101-lab');
const site=resolve(process.env.M5_PUBLIC_SITE);
const out=resolve(process.env.M5_PUBLIC_QEMU_OUT);
assert.ok(out.startsWith(lab+'/'),'raw guest evidence belongs in the private lab');
const firmware=resolve(lab,'cardputer-adv-workbench-b6255f6a.bin');
const chipBinSha='b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd';
const wasmSha=process.env.M5_CC1101_EXPECTED_WASM;
assert.match(wasmSha,/^[a-f0-9]{64}$/);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(hash(await readFile(firmware)),chipBinSha);
const firmwareBase=await readFile(resolve(lab,'cardputer-adv-v2.5.3-base.bin'));
const localRom=await readFile(resolve(process.env.M5_CC1101_ROM));
const registry=JSON.parse(await readFile(resolve(repo,'platform/web/qemu-browser-profiles.json'),'utf8'));
const workbench=JSON.parse(await readFile(resolve(repo,'platform/web/uiflow-workbench-profiles.json'),'utf8'));
const adv=registry.profiles.find(row=>row.deviceId==='cardputer-adv');
const advWorkbench=workbench.profiles.find(row=>row.deviceId==='cardputer-adv');
assert.equal(firmwareBase.length,advWorkbench.baseBytes);
assert.equal(hash(firmwareBase),advWorkbench.baseSHA256);
assert.deepEqual(adv.roms.map(row=>row.sha256),[hash(localRom)]);
assert.equal(adv.roms[0].bytes,localRom.length);
const sourceRoot=resolve(workspace,'.work/docs-uiflow-20261125/upstream/examples/cap/cc1101');
const sourcePins={tx:'12d62591b8400f84dce2560601b4fe7939785ef6be1f9b574c1b419a58b2ce40',
  rx:'725c082f699a054b1b5983cdac62981b3287d24675ee3002efbd5b8058512744'};
const sources={};
for(const [role,sha] of Object.entries(sourcePins)){
  const bytes=await readFile(resolve(sourceRoot,'cc1101_cap_rf_'+role+'_example.py'));
  assert.equal(hash(bytes),sha);
  sources[role]=bytes.toString('utf8').replaceAll('\r\n','\n').replaceAll('\r','\n');
}
await mkdir(out);
const provenance=await capturePublicQemuProvenance({repo,site,testScript:'.work/cc1101-workbench-pair.mjs',
  webPaths:[...QEMU_EXECUTED_WEB_PATHS,'platform/web/public-micropython.js','platform/web/public-uiflow-firmware.js','platform/web/uiflow-workbench-profiles.json']});
assert.equal(provenance.runtime_assets['qemu-system-xtensa.wasm'].sha256,wasmSha);
for(const [role,pin] of Object.entries(sourcePins))assert.equal(provenance.cc1101_example_sources?.[role]?.sha256,pin);
const modules=process.env.M5_WASM_NODE_MODULES||resolve(workspace,'platform/tests/node_modules');
const {chromium}=await import(pathToFileURL(resolve(modules,'playwright/index.mjs')));
const mime={'.html':'text/html','.css':'text/css','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json',
  '.wasm':'application/wasm','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml'};
const server=createServer(async(request,response)=>{
  try{
    const pathname=new URL(request.url,'http://localhost').pathname;
    if(!pathname.startsWith(provenance.base_path)){response.writeHead(404).end();return;}
    const target=resolve(site,decodeURIComponent(pathname.slice(provenance.base_path.length))||'index.html');
    if(!target.startsWith(site+'/')){response.writeHead(403).end();return;}
    const bytes=await readFile(target);
    response.writeHead(200,{'content-type':mime[extname(target)]||'application/octet-stream','cache-control':'no-cache',
      'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp',
      'Cross-Origin-Resource-Policy':'same-origin'});
    response.end(bytes);
  }catch{response.writeHead(404).end();}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const origin='http://127.0.0.1:'+server.address().port+provenance.base_path;
const report={kind:'browser-cc1101-standard-workbench-pair',evidence_level:'virtual-device validation',status:'FAIL',
  provenance,sourcePins,sourceRevision:'a61a29409f09f1f4bebae05e15c4bd6dcc4956b6',roles:{},pageErrors:[]};
let browser,context,workers;
const pages={};
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(read, matches, detail, timeout=45000){
  const deadline=performance.now()+timeout;
  while(performance.now()<deadline){
    const value=await read();
    if(matches(value))return value;
    await delay(40);
  }
  throw new Error('Timed out waiting for '+detail);
}
async function openRole(role){
  const page=await context.newPage();
  pages[role]=page;
  await page.route('**/*',route=>{
    const url=route.request().url();
    if(url.startsWith(origin))return route.continue();
    const fixture=url===adv.reference.url?firmwareBase:url===adv.roms[0].url?localRom:null;
    if(!fixture)return route.abort('blockedbyclient');
    return route.fulfill({body:fixture,contentType:'application/octet-stream',
      headers:{'Access-Control-Allow-Origin':'*','Cross-Origin-Resource-Policy':'cross-origin'}});
  });
  page.on('pageerror',error=>report.pageErrors.push({role,message:error.message}));
  await page.goto(origin,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>crossOriginIsolated&&document.querySelector('#deviceMount')?.dataset.deviceId,
    {},{timeout:45000});
  await page.evaluate(async origin=>{
    const {PublicQemuRuntime}=await import(new URL('platform/web/public-qemu-runtime.js',origin));
    const {PublicMicroPythonRunner}=await import(new URL('platform/web/public-micropython.js',origin));
    const start=PublicQemuRuntime.prototype.start;
    PublicQemuRuntime.prototype.start=function(opts){
      globalThis.cc1101Runtime=this;
      return start.call(this,opts);
    };
    globalThis.cc1101Executions=[];
    const run=PublicMicroPythonRunner.prototype.run;
    PublicMicroPythonRunner.prototype.run=async function(source,opts={}){
      const record={source,sessionId:this.runtime.sessionId,consoleEpoch:this.runtime.consoleEpoch};
      globalThis.cc1101Executions.push(record);
      try{
        record.result=await run.call(this,source,{...opts,onPhase(phase){
          record.phase=phase;
          opts.onPhase?.(phase);
        }});
        return record.result;
      }catch(error){record.error=error.message;throw error;}
      finally{record.finished=true;}
    };
  },origin);
  await page.locator('button[data-device-id="cardputer-adv"]').click();
  await page.waitForFunction(()=>document.querySelector('#deviceMount')?.dataset.deviceId==='cardputer-adv');
  assert.equal(await page.locator('#referenceExample').inputValue(),'uiflow');
  assert.equal(await page.locator('#browserCc1101Panel').isVisible(),false);
  await page.locator('#referenceExample').selectOption('cc1101-rf-'+role);
  await page.locator('#startBtn').click();
  await page.waitForFunction(()=>globalThis.cc1101Runtime?.status==='running'
    &&cc1101Runtime.serial.includes('M5_UIFLOW_WORKBENCH_READY'),{},{timeout:120000});
  const runtime=await page.evaluate(()=>cc1101Runtime.evidence());
  const receipt=runtime.receipt;
  assert.equal(receipt.firmwareInputSha256,chipBinSha);
  assert.equal(receipt.firmwareRuntimeSha256,chipBinSha);
  assert.equal(receipt.wasmSha256,wasmSha);
  assert.equal(receipt.capExample,'cc1101-rf-'+role);
  assert.equal(receipt.usbSerialJtag.controller,'esp32s3-usb-serial-jtag');
  assert.equal(receipt.capPeer,true);
  assert.equal(receipt.clockDivisor,1);
  assert.equal(receipt.oneInsnPerTb,true);
  report.roles[role]={receipt,sessionId:runtime.session_id,consoleEpoch:runtime.console_epoch,
    original_source_sha256:sourcePins[role],editor_source_sha256:hash(sources[role])};
  return page;
}
async function execution(page,index){
  return page.evaluate(index=>globalThis.cc1101Executions[index],index);
}
async function startSource(page,source){
  const index=await page.evaluate(()=>cc1101Executions.length);
  await page.locator('#pythonSource').fill(source);
  return runEditor(page,source,index);
}
async function runOfficial(page,role){
  const index=await page.evaluate(()=>cc1101Executions.length);
  await page.locator('#loadWorkbenchExampleBtn').click();
  await until(()=>page.locator('#pythonSource').inputValue(),source=>source===sources[role],'the exact original source button');
  return runEditor(page,sources[role],index);
}
async function runEditor(page,source,index){
  await page.locator('#pythonRunBtn').click();
  const result=await until(()=>execution(page,index),run=>run?.phase==='running'||run?.finished,'raw-paste transfer');
  assert.equal(result.source,source);
  return index;
}
const state=page=>page.evaluate(()=>cc1101Runtime.readCc1101PeerState());
const frame=page=>page.evaluate(()=>{
  const {last_frame:frame}=cc1101Runtime.evidence();
  if(!frame)return null;
  const {pixels,...digest}=frame;
  return digest;
});
async function stopExample(page,index,role){
  assert.equal((await execution(page,index)).finished,undefined,'example must reach the real run loop');
  await page.locator('#pythonInterruptBtn').click();
  const result=await until(()=>execution(page,index),value=>value?.finished,'original script interrupt');
  assert.equal(result.source,sources[role]);
  assert.equal(result.result?.transfer,'raw-paste');
  assert.equal(result.result?.sessionId,report.roles[role].sessionId);
  assert.equal(result.result?.consoleEpoch,report.roles[role].consoleEpoch);
  assert.equal(result.result?.interrupted,true);
  report.roles[role].original_result=result.result;
}
async function finishRole(role){
  const page=pages[role];
  if(!page)return;
  const hasRuntime=await page.evaluate(()=>Boolean(globalThis.cc1101Runtime));
  if(hasRuntime&&await page.locator('#stopBtn').isVisible())await page.locator('#stopBtn').click();
  if(hasRuntime)await page.waitForFunction(()=>cc1101Runtime.status==='stopped',null,{timeout:45000});
  const stopped=await page.evaluate(()=>{
    const runtime=globalThis.cc1101Runtime;
    if(!runtime)return null;
    const evidence=runtime.evidence();
    const {last_frame:frame,...rest}=evidence;
    if(frame)delete frame.pixels;
    return {status:runtime.status,last_frame:frame,...rest};
  });
  if(stopped)report.roles[role]={...report.roles[role],stopped};
}

try{
  browser=await chromium.launch({headless:true,...(process.env.M5_WASM_CHROME?{executablePath:process.env.M5_WASM_CHROME}:{}),
    args:['--enable-webgl','--use-gl=angle','--use-angle=metal','--ignore-gpu-blocklist']});
  workers=await observeWorkerTargets(browser);
  context=await browser.newContext({viewport:{width:1440,height:1100}});
  const rx=await openRole('rx'),tx=await openRole('tx');
  assert.notEqual(report.roles.rx.sessionId,report.roles.tx.sessionId);
  const receiveIndex=await runOfficial(rx,'rx');
  const rxInitially=await until(()=>state(rx),value=>value.rx_armed,'receiver SRX');
  await delay(1250);
  report.no_peer=await state(rx);
  assert.equal(report.no_peer.rx_accepted,0);
  assert.equal(report.no_peer.rx_interrupts,0);
  assert.equal(report.no_peer.rx_fifo_bytes_read,0);
  assert.equal(report.no_peer.rx_completed,0);
  assert.equal(report.no_peer.tx_sequence,0);
  report.roles.rx.initialState=rxInitially;
  report.roles.rx.initialFrame=await frame(rx);
  await rx.screenshot({path:resolve(out,'rx-negative.png')});

  await rx.locator('#browserCc1101NewCode').click();
  const code=await rx.locator('#browserCc1101Code').inputValue();
  assert.match(code,/^[0-9a-f]{32}$/);
  await tx.locator('#browserCc1101Code').fill(code);
  await rx.locator('#browserCc1101Connect').click();
  await tx.locator('#browserCc1101Connect').click();
  for(const page of [rx,tx])
    await page.waitForFunction(()=>document.querySelector('#browserCc1101State').textContent.includes('已配对'));
  await delay(600);
  const before=await state(rx);
  assert.equal(before.rx_accepted,0);
  assert.equal(before.rx_armed,true);
  const txIndex=await runOfficial(tx,'tx');
  const sent=await until(()=>state(tx),value=>value.tx_sequence>0,'completed sender TX FIFO');
  assert.equal(sent.tx_sequence,1);
  const rawFrame=Buffer.from(sent.tx_fifo_hex,'hex');
  assert.equal(rawFrame[0],rawFrame.length-1);
  assert.equal(rawFrame.subarray(1).toString('ascii'),'CC1101, SEQ=0, Hello');
  const received=await until(()=>state(rx),value=>value.rx_completed>=1,'linked user action transfers actual FIFO bytes');
  report.pair_labels={rx:await rx.locator('#browserCc1101State').textContent(),
    tx:await tx.locator('#browserCc1101State').textContent()};
  await tx.locator('#browserCc1101Disconnect').click();
  await rx.waitForFunction(()=>document.querySelector('#browserCc1101State').textContent.includes('配对已断开'));
  const frames=await rx.evaluate(()=>cc1101Runtime.evidence().inputs.filter(row=>row.type==='cc1101-peer-frame'));
  assert.equal(frames.length,1);
  assert.equal(frames[0].frameHex,sent.tx_fifo_hex);
  assert.equal(received.rx_fifo_bytes_read,rawFrame.length+2);
  assert.equal(received.rx_accepted,1);assert.equal(received.rx_interrupts,1);
  assert.equal(received.tx_sequence,0);assert.equal(received.reset_epoch,before.reset_epoch);
  report.forwarded={captured_tx:sent,target_before:before,target_after:received,frameSha256:hash(rawFrame),
    byteLength:rawFrame.length,ui_pair_input:frames[0],ui_disconnect:true};
  report.roles.rx.receivedFrame=await until(()=>frame(rx),value=>value?.sha256&&value.sha256!==report.roles.rx.initialFrame?.sha256,'receiver UI redraw');
  report.roles.tx.sentFrame=await frame(tx);
  await rx.screenshot({path:resolve(out,'rx-packet.png')});
  await tx.screenshot({path:resolve(out,'tx-packet.png')});
  await stopExample(rx,receiveIndex,'rx');
  await stopExample(tx,txIndex,'tx');

  const readRx='print("RX_WITNESS",rx_count,crc_count,cc1101_data.data.hex() if cc1101_data else "")\n';
  const readTx='print("TX_WITNESS",seq,ok_count,fail_count)\n';
  for (const [role,source] of [['rx',readRx],['tx',readTx]]){
    const index=await startSource(pages[role],source);
    const witness=await until(()=>execution(pages[role],index),row=>row?.finished,'same-guest read-only witness');
    assert.equal(witness.result.sessionId,report.roles[role].sessionId);
    assert.equal(witness.result.consoleEpoch,report.roles[role].consoleEpoch);
    report.roles[role].witness_stdout=witness.result.stdout.trim();
  }
  const rxPayload=rawFrame.subarray(1).toString('hex');
  assert.match(report.roles.rx.witness_stdout,new RegExp('RX_WITNESS 1 0 '+rxPayload+'\\b'));
  const txCounts=report.roles.tx.witness_stdout.match(/TX_WITNESS (\d+) (\d+) (\d+)/);
  assert.ok(txCounts&&Number(txCounts[1])>0&&Number(txCounts[2])>0&&Number(txCounts[3])===0);
  assert.deepEqual(report.pageErrors,[]);
  report.status='DATA_PASS';
}catch(error){report.error=error.stack||error.message;process.exitCode=1;}
finally{
  for(const role of Object.keys(pages)){
    try{await finishRole(role);}catch(error){report.cleanup_error=error.message;process.exitCode=1;}
  }
  if(workers){
    const observed=Object.values(report.roles).map(row=>row.stopped?.cleanup).filter(Boolean);
    const expected=observed.reduce((count,row)=>count+(row.workersCreated??0)+1,0);
    report.worker_cleanup=await workers.waitUntilClosed({minimumObserved:Math.max(1,expected),timeoutMs:30000}).catch(error=>({ok:false,error:error.message}));
    if(report.status==='DATA_PASS'&&observed.length===2&&report.worker_cleanup.ok
      &&report.worker_cleanup.observed.length===expected
      &&observed.every(row=>row.gracefulExit&&row.exitCode===0&&row.iframeRemoved&&closedQemuPthreadBroker(row)))report.status='PASS';
    else if(report.status==='DATA_PASS'){report.status='FAIL';process.exitCode=1;}
  }
  await writeFile(resolve(out,'report.json'),JSON.stringify(report,null,2)+'\n');
  await workers?.detach();await context?.close();await browser?.close();
  await new Promise(done=>server.close(done));
  console.log(JSON.stringify({status:report.status,error:report.error||null,output:out}));
}
