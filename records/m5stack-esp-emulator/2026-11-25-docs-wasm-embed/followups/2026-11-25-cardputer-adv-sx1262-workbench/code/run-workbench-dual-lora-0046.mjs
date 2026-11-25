import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname,extname,resolve,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

assert.equal(process.env.M5_SX1262_DUAL_RUN,'1','Enable the isolated two-guest acceptance explicitly');
const runner=fileURLToPath(import.meta.url),lab=dirname(runner),workspace=resolve(lab,'../..');
const repo=resolve(workspace,'.work/docs-wasm-cardputer-adv-sx1262-source');
const [variant,outputName]=process.argv.slice(2);
const variants={lora1262:'LoRa1262',lora868:'LoRa868'};
assert.ok(Object.hasOwn(variants,variant));
assert.match(outputName??'',/^browser-0046-workbench-lora[a-z0-9-]+$/);
const site=resolve(process.env.M5_PUBLIC_SITE),output=resolve(lab,outputName);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const wasmSha=process.env.M5_SX1262_EXPECTED_WASM,siteSha=process.env.M5_SX1262_EXPECTED_SITE;
for(const value of [wasmSha,siteSha])assert.match(value??'',/^[a-f0-9]{64}$/);
const script=path=>pathToFileURL(resolve(repo,'platform/tests',path));
const {observeWorkerTargets,closedQemuPthreadBroker}=await import(script('public_qemu_worker_targets.mjs'));
const {capturePublicQemuProvenance,QEMU_EXECUTED_WEB_PATHS}=await import(script('public_qemu_artifacts.mjs'));
const provenance=await capturePublicQemuProvenance({repo,site,webPaths:[
  ...QEMU_EXECUTED_WEB_PATHS,'platform/web/public-micropython.js','platform/web/public-uiflow-firmware.js',
  'platform/web/uiflow-workbench-profiles.json',
]});
assert.equal(provenance.site_manifest_sha256,siteSha);
assert.equal(provenance.runtime_assets['qemu-system-xtensa.wasm'].sha256,wasmSha);
assert.equal(provenance.runtime_build.kind,'source-build');
assert.equal(provenance.runtime_build.all_objects_rebuilt,true);

const manifestBytes=await readFile(resolve(site,'public-site-manifest.json'));
assert.equal(hash(manifestBytes),siteSha);
const manifest=JSON.parse(manifestBytes);
assert.equal(manifest.publication_eligible,true);
const assets=new Map(manifest.assets.map(row=>[row.path,row]));
async function verified(path){
  const bytes=await readFile(resolve(site,path));
  assert.equal(hash(bytes),assets.get(path)?.sha256,path);
  assert.equal(bytes.length,assets.get(path)?.bytes,path);
  return bytes;
}
const runtime=JSON.parse(await verified('platform/runtime/qemu/runtime.json'));
const sxPatch='patches/qemu-wasm-probe/0046-cardputer-adv-sx1262-cap-peer.patch';
const sxPatchSHA='0c7b037ed3e95102c8d588d042767a0d61591946323f21a9f87a8e02f0c90238';
assert.deepEqual(runtime.source.patches.filter(row=>row.path===sxPatch),[{path:sxPatch,sha256:sxPatchSHA}]);
const config=JSON.parse(await verified('platform/web/site-config.json'));
assert.equal(config.service_url,'');
const originalPins={
  lora1262:{sender:'08bb6c92c945c25354dde44133711ccf51fc47320a7e079653f84351ac936f51',
    receiver:'6c3765e32fd6d2b730f164fc1aea478d150738f918f25509216325d23678abe9'},
  lora868:{sender:'d5bb7f05ccab053c41e83dc6d85ea6ee9cf1e5036f91614975f07df474c3d626',
    receiver:'174c834489590531f2271229b5b5c0093ea12f1c941826b6d6873fd683778df0'},
};
const originalSourceRevision='a61a29409f09f1f4bebae05e15c4bd6dcc4956b6';
const roleId=(family,role)=>family+'-rf-'+(role==='sender'?'tx':'rx');
const allOriginals={},sources={};
for(const [family,pins] of Object.entries(originalPins)){
  for(const [role,sha256] of Object.entries(pins)){
    const id=roleId(family,role),name=`cardputer_adv_${family}_cap_${role}_example.py`;
    const path='platform/runtime/qemu-probe/fixture/'+name;
    const original=await readFile(resolve(repo,'tests/browser-qemu/uiflow_workbench',name));
    assert.equal(hash(original),sha256);
    assert.deepEqual(config.browser_sx1262_examples?.[id],{path,sha256,bytes:original.length});
    assert.deepEqual(await verified(path),original);
    allOriginals[id]={path,sha256,bytes:original.length};
    if(family===variant)sources[role]=original.toString('utf8').replace(/\r\n?/g,'\n');
  }
}
assert.deepEqual(Object.keys(config.browser_sx1262_examples).sort(),Object.keys(allOriginals).sort());

const registry=JSON.parse(await verified('platform/web/qemu-browser-profiles.json'));
const workbench=JSON.parse(await verified('platform/web/uiflow-workbench-profiles.json'));
const board=registry.profiles.find(row=>row.deviceId==='cardputer-adv');
const adv=workbench.profiles.find(row=>row.deviceId==='cardputer-adv');
const firmwareSHA='b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd';
assert.equal(adv.firmwareSHA256,firmwareSHA);
const base=await readFile(resolve(process.env.M5_SX1262_BASE??resolve(lab,'../docs-wasm-cardputer-cc1101-lab/cardputer-adv-v2.5.3-base.bin')));
const rom=await readFile(resolve(process.env.M5_SX1262_ROM??resolve(lab,'../docs-wasm-arduino-20261125/esp32s3_rev0_rom.bin')));
assert.equal(hash(base),adv.baseSHA256);
assert.equal(base.length,adv.baseBytes);
assert.equal(hash(rom),board.roms[0].sha256);
assert.equal(rom.length,board.roms[0].bytes);
const downloads=new Map([[board.reference.url,base],[board.roms[0].url,rom]]);
const modules=process.env.M5_WASM_NODE_MODULES??resolve(workspace,'platform/tests/node_modules');
const {chromium}=await import(pathToFileURL(resolve(modules,'playwright/index.mjs')));
await mkdir(output);

const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json',
  '.wasm':'application/wasm','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};
const server=createServer(async(request,response)=>{
  try{
    const pathname=new URL(request.url,'http://localhost').pathname;
    assert.ok(pathname.startsWith(manifest.base_path));
    const name=decodeURIComponent(pathname.slice(manifest.base_path.length))||'index.html';
    const path=resolve(site,name);
    assert.ok(path.startsWith(site+sep)&&assets.has(name));
    const bytes=await readFile(path);
    response.writeHead(200,{'content-type':mime[extname(path)]??'application/octet-stream',
      'Cache-Control':'no-store','Cross-Origin-Opener-Policy':'same-origin',
      'Cross-Origin-Embedder-Policy':'require-corp','Cross-Origin-Resource-Policy':'same-origin'}).end(bytes);
  }catch{response.writeHead(404).end();}
});
const doc={status:'FAIL',level:'virtual-device validation',variant,provenance,originalSourceRevision,
  original_assets:allOriginals,runner_sha256:hash(await readFile(runner)),guests:{},page_errors:[]};
const checkpoint=()=>writeFile(resolve(output,'report.json'),JSON.stringify(doc,null,2)+'\n');
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let browser,context,workers,address;
const pages={};
async function until(label,read,matches,timeout=45000){
  const deadline=performance.now()+timeout;
  let current;
  do{
    current=await read();
    if(matches(current))return current;
    await delay(40);
  }while(performance.now()<deadline);
  throw new Error(label+': '+JSON.stringify(current)?.slice(0,700));
}
const model=page=>page.evaluate(()=>guest.readSx1262PeerState());
const armed=row=>row.receiving&&!row.busy&&!row.dio1&&(row.irq_status&2)===0;
const frame=page=>page.evaluate(()=>{
  const value=guest.evidence().last_frame;
  if(!value)return null;
  const {pixels,...identity}=value;
  return identity;
});
const execution=(page,index)=>page.evaluate(index=>guestExecutions[index],index);

async function openRole(role){
  const page=await context.newPage();
  pages[role]=page;
  page.on('pageerror',error=>doc.page_errors.push({role,error:error.message}));
  await page.goto(address,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>crossOriginIsolated&&document.querySelector('#deviceMount')?.dataset.deviceId);
  await page.evaluate(async address=>{
    const {PublicQemuRuntime}=await import(new URL('platform/web/public-qemu-runtime.js',address));
    const {PublicMicroPythonRunner}=await import(new URL('platform/web/public-micropython.js',address));
    const start=PublicQemuRuntime.prototype.start;
    PublicQemuRuntime.prototype.start=function(options){globalThis.guest=this;return start.call(this,options);};
    globalThis.guestExecutions=[];
    const run=PublicMicroPythonRunner.prototype.run;
    PublicMicroPythonRunner.prototype.run=async function(source,options={}){
      const entry={source,consoleEpoch:this.runtime.consoleEpoch,sessionId:this.runtime.sessionId};
      guestExecutions.push(entry);
      try{
        entry.result=await run.call(this,source,{...options,onPhase(phase){
          entry.phase=phase;
          options.onPhase?.(phase);
        }});
        return entry.result;
      }catch(error){entry.error=error.message;throw error;}
      finally{entry.finished=true;}
    };
  },address);
  await page.locator('button[data-device-id="cardputer-adv"]').click();
  await page.waitForFunction(()=>document.querySelector('#deviceMount')?.dataset.deviceId==='cardputer-adv');
  assert.equal(await page.locator('#referenceExample').inputValue(),'uiflow');
  assert.equal(await page.locator('#browserCc1101Panel').isVisible(),false);
  await page.locator('#referenceExample').selectOption(roleId(variant,role));
  await page.locator('#startBtn').click();
  await page.waitForFunction(()=>globalThis.guest?.status==='running'&&guest.guestReady(),null,{timeout:120000});
  assert.equal(await page.locator('#browserRadioCapName').textContent(),variants[variant]+' Cap');
  assert.equal(await page.locator('#browserCc1101Role').textContent(),role==='sender'?'发送端':'接收端');
  const info=await page.evaluate(()=>({receipt:guest.receipt,sessionId:guest.sessionId,consoleEpoch:guest.consoleEpoch}));
  assert.equal(info.receipt.sx1262Example,roleId(variant,role));
  assert.equal(info.receipt.capExample,undefined);
  assert.equal(info.receipt.gnssExample,undefined);
  assert.equal(info.receipt.usbSerialJtag?.controller,'esp32s3-usb-serial-jtag');
  assert.equal(info.receipt.firmwareInputSha256,firmwareSHA);
  assert.equal(info.receipt.firmwareRuntimeSha256,firmwareSHA);
  assert.equal(info.receipt.wasmSha256,wasmSha);
  assert.equal(info.receipt.clockDivisor,1);
  assert.equal(info.receipt.oneInsnPerTb,true);
  doc.guests[role]={info};
  return page;
}
async function runEditor(page,source){
  const index=await page.evaluate(()=>guestExecutions.length);
  await page.locator('#pythonRunBtn').click();
  const result=await until('raw-paste of exact editor source',()=>execution(page,index),
    row=>row?.phase==='running'||row?.finished);
  assert.equal(result.source,source);
  return index;
}
async function runOriginal(page,role){
  const button=page.locator('#loadWorkbenchExampleBtn');
  assert.equal(await button.textContent(),`载入 ${variants[variant]} Cap 官方例程`);
  await button.click();
  const loaded=await until('load the original via standard workbench',()=>page.locator('#pythonSource').inputValue(),
    value=>value===sources[role]);
  doc.guests[role].editor_source_sha256=hash(loaded);
  assert.equal(hash(loaded),originalPins[variant][role]);
  return runEditor(page,loaded);
}
async function stopOriginal(page,role,index){
  const current=await execution(page,index);
  assert.equal(current.finished,undefined,'the original loop ran through the controller observation');
  await page.locator('#pythonInterruptBtn').click();
  const ended=await until('interrupt the original program',()=>execution(page,index),row=>row?.finished);
  assert.equal(ended.result?.interrupted,true);
  assert.equal(ended.result?.transfer,'raw-paste');
  assert.equal(ended.result?.sessionId,doc.guests[role].info.sessionId);
  assert.equal(ended.result?.consoleEpoch,doc.guests[role].info.consoleEpoch);
  doc.guests[role].original_result=ended.result;
}
async function stopGuest(page){
  const present=await page.evaluate(()=>Boolean(globalThis.guest));
  if(!present)return null;
  const button=page.locator('#stopBtn');
  const domStop=await button.isVisible();
  if(domStop){
    await button.click();
    await page.waitForFunction(()=>guest.status==='stopped'&&!document.querySelector('#stopBtn').offsetParent,null,{timeout:45000});
  }else if(await page.evaluate(()=>guest.status!=='stopped')){
    await page.evaluate(()=>guest.stop());
  }
  return page.evaluate(domStop=>({domStop,status:guest.status,sessionId:guest.sessionId,consoleEpoch:guest.consoleEpoch,
    cleanup:guest.cleanupResult,serial:guest.serial.slice(-16000)}),domStop);
}

try{
  await new Promise(done=>server.listen(0,'127.0.0.1',done));
  address=`http://127.0.0.1:${server.address().port}${manifest.base_path}`;
  browser=await chromium.launch({headless:true,
    ...(process.env.M5_WASM_CHROME?{executablePath:process.env.M5_WASM_CHROME}:{}),
    args:['--enable-webgl','--use-gl=angle','--use-angle=metal','--ignore-gpu-blocklist']});
  doc.browser=browser.version();
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
  const rx=await openRole('receiver');
  const rxIndex=await runOriginal(rx,'receiver');
  doc.rx_armed=await until('original receiver reaches SX1262 RX',()=>model(rx),row=>armed(row)&&row.commands>8);
  await delay(1800);
  doc.no_peer={window_ms:1800,state:await model(rx),frame:await frame(rx)};
  assert.ok(armed(doc.no_peer.state)&&doc.no_peer.frame?.sha256);
  assert.equal(doc.no_peer.state.rx_sequence,0);
  assert.equal(doc.no_peer.state.rx_bytes_read,0);
  await rx.screenshot({path:resolve(output,'rx-no-peer.png')});
  await checkpoint();

  const tx=await openRole('sender');
  assert.notEqual(doc.guests.receiver.info.sessionId,doc.guests.sender.info.sessionId);
  const txIndex=await runOriginal(tx,'sender');
  doc.tx_ready=await until('original sender programs matching radio',()=>model(tx),
    row=>row.frequency_word===doc.rx_armed.frequency_word&&row.commands>8&&!row.busy);
  assert.equal(doc.tx_ready.tx_sequence,0);
  doc.tx_before=await frame(tx);
  await rx.locator('#browserCc1101NewCode').click();
  const code=await rx.locator('#browserCc1101Code').inputValue();
  assert.match(code,/^[a-f0-9]{32}$/);
  await tx.locator('#browserCc1101Code').fill(code);
  await rx.locator('#browserCc1101Connect').click();
  await tx.locator('#browserCc1101Connect').click();
  for(const page of [rx,tx])
    await page.waitForFunction(()=>document.querySelector('#browserCc1101State').textContent.includes('已配对'));
  await delay(600);
  doc.paired_before_input=await model(rx);
  assert.ok(armed(doc.paired_before_input));
  assert.equal(doc.paired_before_input.rx_sequence,0);
  assert.equal(doc.paired_before_input.rx_bytes_read,0);

  await tx.locator('#deviceMount').click({position:{x:3,y:3}});
  const keys=['w','a','s','m','Enter'];
  for(const key of keys.slice(0,-1)){
    await tx.keyboard.press(key,{delay:160});
    await delay(250);
  }
  await rx.evaluate(()=>{
    const probe=globalThis.receiverReadback={running:true,samples:[]};
    void (async()=>{
      while(probe.running){
        try{
          const state=await guest.readSx1262PeerState();
          const previous=probe.samples.at(-1);
          if(probe.samples.length<32&&(!previous||['rx_sequence','rx_bytes_read','irq_status','dio1'].some(key=>previous[key]!==state[key])))
            probe.samples.push(state);
        }catch(error){probe.error=error.message;break;}
        await new Promise(done=>setTimeout(done,15));
      }
    })();
  });
  await tx.keyboard.press('Enter',{delay:160});
  doc.sender_keys=keys;
  doc.tx_packet=await until('original sender completed actual FIFO packet',()=>model(tx),
    row=>row.tx_sequence===1&&row.tx_hex==='7761736d');
  doc.rx_readout=await until('original receiver consumed one actual SPI FIFO packet',()=>model(rx),
    row=>row.rx_sequence===1&&row.rx_bytes_read===4&&!row.dio1&&(row.irq_status&2)===0);
  doc.rx_controller_trace=await rx.evaluate(()=>{
    receiverReadback.running=false;
    return {samples:receiverReadback.samples,error:receiverReadback.error};
  });
  assert.equal(doc.rx_controller_trace.error,undefined);
  const raised=doc.rx_controller_trace.samples.find(row=>row.rx_sequence===1&&row.dio1&&(row.irq_status&2)!==0);
  doc.rx_dio1_high_directly_sampled=Boolean(raised);
  doc.rx_after=await until('receiver guest redraws after original IRQ callback',()=>frame(rx),
    row=>row?.sha256&&row.sha256!==doc.no_peer.frame.sha256&&row.width===240&&row.height===135);
  doc.tx_after=await frame(tx);
  assert.ok(doc.tx_after?.sha256&&doc.tx_after.width===240&&doc.tx_after.height===135);
  doc.pair_labels={receiver:await rx.locator('#browserCc1101State').textContent(),
    sender:await tx.locator('#browserCc1101State').textContent()};
  for(const label of Object.values(doc.pair_labels))assert.match(label,/已转交 1 帧/);
  const ingress=await rx.evaluate(()=>guest.evidence().inputs.filter(row=>row.type==='sx1262-peer-packet'));
  assert.equal(ingress.length,1);
  assert.equal(ingress[0].packetHex,doc.tx_packet.tx_hex);
  doc.ingress=ingress[0];
  await rx.screenshot({path:resolve(output,'rx-packet.png')});
  await tx.screenshot({path:resolve(output,'tx-packet.png')});
  await tx.locator('#browserCc1101Disconnect').click();
  await rx.waitForFunction(()=>document.querySelector('#browserCc1101State').textContent.includes('配对已断开'));
  doc.ui_disconnected=true;

  await stopOriginal(rx,'receiver',rxIndex);
  await stopOriginal(tx,'sender',txIndex);
  const witnessSource='print("RX_WITNESS",lora_data.hex(),rx_text)\n';
  await rx.locator('#pythonSource').fill(witnessSource);
  const witnessIndex=await runEditor(rx,witnessSource);
  const witness=await until('read-only check of original IRQ callback variables',()=>execution(rx,witnessIndex),
    row=>row?.finished);
  assert.equal(witness.result?.sessionId,doc.guests.receiver.info.sessionId);
  assert.equal(witness.result?.consoleEpoch,doc.guests.receiver.info.consoleEpoch);
  doc.rx_callback_witness=witness.result.stdout.trim();
  assert.equal(doc.rx_callback_witness,'RX_WITNESS 7761736d wasm');
  assert.deepEqual(doc.page_errors,[]);
  doc.status='DATA_PASS';
}catch(error){
  doc.error=error.stack??String(error);
  process.exitCode=1;
}finally{
  for(const [role,page] of Object.entries(pages)){
    await page.evaluate(()=>{if(globalThis.receiverReadback)receiverReadback.running=false;}).catch(()=>{});
    doc.guests[role]??={};
    try{doc.guests[role].final=await stopGuest(page);}
    catch(error){
      doc.guests[role].cleanup_error=error.message;
      await page.evaluate(()=>globalThis.guest?.stop()).catch(()=>{});
      process.exitCode=1;
    }
  }
  if(workers){
    const stopped=Object.values(doc.guests).filter(row=>row.final?.cleanup);
    const count=stopped.reduce((total,row)=>total+row.final.cleanup.workersCreated+1,0);
    doc.worker_cleanup=await workers.waitUntilClosed({minimumObserved:Math.max(1,count),timeoutMs:30000})
      .catch(error=>({ok:false,error:error.message}));
    if(doc.status==='DATA_PASS'){
      const closed=doc.worker_cleanup.ok&&doc.worker_cleanup.observed.length===12&&stopped.length===2
        &&stopped.every(({info,final})=>final.domStop&&final.status==='stopped'&&final.sessionId===info.sessionId
          &&final.consoleEpoch===info.consoleEpoch&&final.cleanup.gracefulExit&&final.cleanup.exitCode===0
          &&final.cleanup.iframeRemoved&&closedQemuPthreadBroker(final.cleanup));
      doc.status=closed?'PASS':'FAIL';
      if(!closed)process.exitCode=1;
    }
  }
  await checkpoint();
  await workers?.detach();
  await context?.close();
  await browser?.close();
  await new Promise(done=>server.close(done));
  console.log(JSON.stringify({status:doc.status,variant,error:doc.error??null,
    dio1_direct:doc.rx_dio1_high_directly_sampled??null,workers:doc.worker_cleanup?.observed?.length??0}));
}
