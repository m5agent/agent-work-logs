import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname, extname, resolve, sep} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {observeWorkerTargets} from '../../platform/tests/public_qemu_worker_targets.mjs';

const lab=dirname(fileURLToPath(import.meta.url));
const [siteName,outputName,variant]=process.argv.slice(2);
assert.ok(/^lora-preview-site(?:-[a-z0-9-]+)?$/.test(siteName));
assert.ok(/^pair-output(?:-[a-z0-9-]+)?$/.test(outputName));
assert.ok(['lora1262','lora868'].includes(variant));
const site=resolve(lab,siteName),output=resolve(lab,outputName);
await mkdir(output);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const receipt=JSON.parse(await readFile(resolve(lab,siteName+'-receipt.json')));
const manifestBytes=await readFile(resolve(site,'public-site-manifest.json'));
assert.equal(hash(manifestBytes),receipt.site_manifest.sha256);
const manifest=JSON.parse(manifestBytes);
assert.equal(manifest.publication_eligible,false);
const assets=new Map(manifest.assets.map(row=>[row.path,row]));
async function checkedAsset(path){
  const bytes=await readFile(resolve(site,path));
  assert.equal(hash(bytes),assets.get(path)?.sha256,path);
  return bytes;
}
const runtimeBytes=await checkedAsset('platform/runtime/qemu/runtime.json');
assert.equal(hash(runtimeBytes),receipt.runtime_manifest.sha256);
const runtime=JSON.parse(runtimeBytes);
assert.equal(hash(await checkedAsset('platform/runtime/qemu/'+runtime.assets.wasm.path)),receipt.wasm.sha256);
assert.equal(hash(await checkedAsset('platform/web/public-qemu-engine.js')),receipt.engine.sha256);
const qemuRegistry=JSON.parse(await checkedAsset('platform/web/qemu-browser-profiles.json'));
const board=qemuRegistry.profiles.find(row=>row.deviceId==='cardputer-adv');
const originalRoot=resolve(lab,'../docs-uiflow-20261125/upstream/examples/cap',variant);
const originalFiles={
  lora1262:{sender:'08bb6c92c945c25354dde44133711ccf51fc47320a7e079653f84351ac936f51',
    receiver:'6c3765e32fd6d2b730f164fc1aea478d150738f918f25509216325d23678abe9'},
  lora868:{sender:'d5bb7f05ccab053c41e83dc6d85ea6ee9cf1e5036f91614975f07df474c3d626',
    receiver:'174c834489590531f2271229b5b5c0093ea12f1c941826b6d6873fd683778df0'},
};
const sources={};
for(const role of ['receiver','sender']){
  const name=`cardputer_adv_${variant}_cap_${role}_example.py`;
  const bytes=await readFile(resolve(originalRoot,name));
  assert.equal(hash(bytes),originalFiles[variant][role]);
  sources[role]={name,bytes,sha256:hash(bytes)};
}
const cached=[
  [board.reference,'../docs-wasm-cardputer-cc1101-lab/cardputer-adv-v2.5.3-base.bin'],
  [board.roms[0],'../docs-wasm-arduino-20261125/esp32s3_rev0_rom.bin'],
];
for(const item of cached){
  const bytes=await readFile(resolve(lab,item[1]));
  assert.equal(hash(bytes),item[0].sha256);
  item[1]=bytes;
}
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json',
  '.wasm':'application/wasm','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml'};
const server=createServer(async(req,res)=>{
  try {
    const page=new URL(req.url,'http://localhost');
    if(!page.pathname.startsWith(manifest.base_path))throw new Error('Unmapped');
    const asset=decodeURIComponent(page.pathname.slice(manifest.base_path.length))||'index.html';
    const file=resolve(site,asset);
    if(!file.startsWith(site+sep)||!assets.has(asset))throw new Error('Unmapped');
    res.writeHead(200,{'content-type':mime[extname(file)]||'application/octet-stream','cache-control':'no-store'}).end(await readFile(file));
  }catch{res.writeHead(404).end();}
});
const doc={status:'FAIL',variant,scope:'private virtual-device preview',receipt,guests:{},blocked_requests:[],page_errors:[],
  original_source_sha256:originalFiles[variant],harness_sha256:hash(await readFile(fileURLToPath(import.meta.url)))};
const checkpoint=()=>writeFile(resolve(output,'report.json'),JSON.stringify(doc,null,2)+'\n');
const {chromium}=await import(pathToFileURL(resolve(lab,'../../platform/tests/node_modules/playwright/index.mjs')));
let browser,context,workers;
const owned={};
const until=async(label,read,accept,timeout=23000)=>{
  const end=performance.now()+timeout;
  let value;
  while(performance.now()<end){
    value=await read();
    if(accept(value))return value;
    await new Promise(delay=>setTimeout(delay,125));
  }
  throw new Error(label+': '+JSON.stringify(value).slice(0,1000));
};
function model(page){return page.evaluate(()=>guest.ask('lora-lab-state'));}
async function frame(page,label){
  const frame=await page.evaluate(async()=>{
    const sample=guest.lastFrame;
    if(!sample)return null;
    const bytes=new Uint8Array(sample.pixels);
    const digest=await crypto.subtle.digest('SHA-256',bytes);
    return {bytes:[...bytes],sequence:sample.sourceSequence,width:sample.width,height:sample.height,
      sha256:[...new Uint8Array(digest)].map(byte=>byte.toString(16).padStart(2,'0')).join('')};
  });
  if(!frame)return null;
  const {bytes,...summary}=frame;
  if(label)await writeFile(resolve(output,label+'.rgb565'),Buffer.from(bytes));
  return summary;
}
async function run(role,address){
  const page=await context.newPage();
  owned[role]=page;
  page.on('pageerror',error=>doc.page_errors.push({role,error:error.message}));
  await page.goto(address,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>crossOriginIsolated&&document.querySelector('#deviceMount')?.dataset.deviceId==='cores3');
  await page.evaluate(async(root)=>{
    const {PublicQemuRuntime}=await import(new URL('platform/web/public-qemu-runtime.js',root));
    const start=PublicQemuRuntime.prototype.start;
    PublicQemuRuntime.prototype.start=function(options){globalThis.guest=this;return start.call(this,options);};
  },address);
  await page.locator('button[data-device-id="cardputer-adv"]').click();
  await page.waitForFunction(()=>document.querySelector('#deviceMount')?.dataset.deviceId==='cardputer-adv');
  await page.locator('.advanced-options > summary').click();
  await page.locator('#runtimeMode').selectOption('browser');
  await page.locator('input[name="firmwareSource"][value="reference"]').check();
  await page.locator('#startBtn').click();
  await page.waitForFunction(()=>globalThis.guest?.status==='running'&&guest.receipt&&guest.guestReady(),{},{timeout:100000});
  const info=await page.evaluate(()=>({receipt:guest.receipt,sessionId:guest.sessionId,epoch:guest.consoleEpoch}));
  assert.equal(info.receipt.firmwareRuntimeSha256,'b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd');
  assert.equal(info.receipt.wasmSha256,receipt.wasm.sha256);
  doc.guests[role]={info,before:await model(page),before_frame:await frame(page)};
  const file=sources[role];
  await page.locator('#pythonFile').setInputFiles({name:file.name,mimeType:'text/x-python',buffer:file.bytes});
  assert.equal(hash(await page.locator('#pythonSource').inputValue()),
    hash(file.bytes.toString().replaceAll('\r\n','\n').replaceAll('\r','\n')));
  await page.locator('#pythonRunBtn').click();
  return page;
}

try {
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const address=`http://127.0.0.1:${server.address().port}${manifest.base_path}`;
  browser=await chromium.launch({headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=metal','--ignore-gpu-blocklist']});
  workers=await observeWorkerTargets(browser);
  context=await browser.newContext({viewport:{width:1440,height:1100}});
  for(const [row,body] of cached)
    await context.route(url=>url.href===row.url,route=>route.fulfill({status:200,headers:{'access-control-allow-origin':'*'},body}));
  await context.route(url=>[8787,8830].includes(Number(url.port))||/\/api\/v1(?:\/|$)/.test(url.pathname),route=>{
    doc.blocked_requests.push(route.request().url());return route.abort('blockedbyclient');
  });
  doc.browser=browser.version();
  const rx=await run('receiver',address);
  doc.rx_armed=await until('original receiver enters SX1262 RX',()=>model(rx),value=>value.receiving&&value.commands>8);
  await rx.waitForTimeout(1800);
  doc.rx_without_peer={state:await model(rx),frame:await frame(rx,'rx-before')};
  assert.equal(doc.rx_without_peer.state.rx_sequence,0);
  assert.equal(doc.rx_without_peer.state.rx_bytes_read,0);
  await checkpoint();
  const tx=await run('sender',address);
  doc.tx_ready=await until('original sender config registers',()=>model(tx),value=>value.frequency_word===doc.rx_armed.frequency_word&&value.commands>8);
  await tx.waitForTimeout(1200);
  doc.tx_before=await frame(tx,'tx-before');
  await tx.locator('#deviceMount').click({position:{x:3,y:3}});
  for(const key of ['w','a','s','m','Enter']){
    await tx.keyboard.press(key,{delay:160});
    await tx.waitForTimeout(250);
  }
  doc.tx_frame=await frame(tx,'tx-after');
  doc.tx_packet=await until('original sender commits actual SX1262 FIFO',()=>model(tx),
    value=>value.tx_sequence>0&&value.tx_hex==='7761736d');
  doc.rx_injected=await rx.evaluate(hex=>guest.ask('lora-lab-receive',{hex}),doc.tx_packet.tx_hex);
  doc.rx_read=await until('original receiver reads actual SX1262 FIFO',()=>model(rx),
    value=>value.rx_sequence===1&&value.rx_bytes_read===4);
  doc.rx_after=await until('original receiver renders received text',()=>frame(rx),
    value=>value&&value.sha256!==doc.rx_without_peer.frame.sha256);
  await frame(rx,'rx-after');
  assert.notEqual(doc.guests.sender.info.sessionId,doc.guests.receiver.info.sessionId);
  doc.status='PASS';
}catch(error){
  doc.error=error.stack||String(error);
  process.exitCode=1;
}finally{
  for(const [role,page] of Object.entries(owned)){
    doc.guests[role]??={};
    doc.guests[role].final=await page.evaluate(async()=>{
      const r=globalThis.guest;
      if(!r)return null;
      if(r.status!=='stopped')await r.stop();
      return {cleanup:r.cleanupResult,status:r.status,sessionId:r.sessionId,epoch:r.consoleEpoch,
        console:r.serial.slice(-16000),python:document.querySelector('#pythonOutput')?.textContent};
    }).catch(error=>({error:error.message}));
  }
  if(workers)doc.workers=await workers.waitUntilClosed({minimumObserved:Object.keys(owned).length>1?12:6,timeoutMs:30000});
  if(doc.status==='PASS'){
    try{
      assert.ok(doc.workers?.ok&&doc.workers.observed.length===12);
      for(const row of Object.values(doc.guests))
        assert.ok(row.final.cleanup.gracefulExit&&row.final.epoch===row.info.epoch&&row.final.sessionId===row.info.sessionId);
    }catch(error){doc.status='FAIL';doc.error=String(error);process.exitCode=1;}
  }
  await checkpoint();
  await workers?.detach();
  await browser?.close();
  await new Promise(resolve=>server.close(resolve));
  console.log(JSON.stringify({status:doc.status,variant,error:doc.error,receipt:receipt.wasm.sha256}));
}
