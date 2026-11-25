import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname,extname,resolve,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

assert.equal(process.env.M5_DUAL_KMETER_RUN,'1','Enable the isolated single-guest test explicitly');
const runner=fileURLToPath(import.meta.url),lab=dirname(runner),workspace=resolve(lab,'../..');
const repo=resolve(workspace,'.work/docs-wasm-cardputer-adv-sx1262-source');
const docs=resolve(workspace,'.work/docs-uiflow-20261125');
const [id,outputName]=process.argv.slice(2);
const cases={
  dualkmeter:{path:'dualkmeter.official.full-preview.py',sha:'6765c65ac5e3a6219d762fe2cbc4639301714719646a79b115cc794e2b44fb37',
    project:'examples/module/dualkmeter/dualkmeter_cores3.m5f2', assetSha:'f228aa58eebcb6879a7f1d0c4f527b615cf9f6552fb7286c184c36e9261a39ee'},
};
assert.equal(id,'dualkmeter');
assert.match(outputName??'',/^browser-dual-kmeter-[a-z0-9-]+$/);
const spec=cases[id],output=resolve(lab,outputName);
assert.ok(process.env.M5_PUBLIC_SITE);
const site=resolve(process.env.M5_PUBLIC_SITE);
const expected={wasm:process.env.M5_DUAL_KMETER_WASM,site:process.env.M5_DUAL_KMETER_SITE,
  firmware:'b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49',
  base:'1324f12d3ddd5392f47a9eff537f9ce0b01a8e6e36d829b6bd22cdf82d2c1264',
  rom:'b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913',
  profile:'cores3-wasm-uiflow-workbench-lvgl-wallclock-candidate',
  revision:'a61a29409f09f1f4bebae05e15c4bd6dcc4956b6'};
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const source=await readFile(resolve(lab,'../docs-wasm-cores3-blockly-lab',spec.path));
assert.equal(sha(await readFile(resolve(docs,'upstream',spec.project))),spec.assetSha);
const editorSource=source.toString('utf8').replace(/\r\n?/g,'\n');
assert.equal(sha(source),spec.sha);
assert.equal(sha(editorSource),spec.sha);
const srcUrl=name=>pathToFileURL(resolve(repo,'platform/tests',name));
const {observeWorkerTargets,closedQemuPthreadBroker}=await import(srcUrl('public_qemu_worker_targets.mjs'));
const siteBytes=await readFile(resolve(site,'public-site-manifest.json'));
assert.match(expected.site,/^[0-9a-f]{64}$/);assert.match(expected.wasm,/^[0-9a-f]{64}$/);
assert.equal(sha(siteBytes),expected.site);
const manifest=JSON.parse(siteBytes);
assert.equal(manifest.base_path,'/showcase/');
assert.equal(manifest.publication_eligible,false);
const assets=new Map(manifest.assets.map(row=>[row.path,row]));
async function verified(path){
  const bytes=await readFile(resolve(site,path));
  assert.equal(sha(bytes),assets.get(path)?.sha256,path);
  assert.equal(bytes.length,assets.get(path)?.bytes,path);
  return bytes;
}
const runtimePath='platform/runtime/qemu/runtime.json';
const runtimeBytes=await verified(runtimePath);
const runtime=JSON.parse(runtimeBytes);
const wasmPath='platform/runtime/qemu/'+runtime.assets.wasm.path;
assert.equal(sha(await verified(wasmPath)),expected.wasm);
const enginePath='platform/web/public-qemu-engine.js';
const provenance={site_manifest_sha256:expected.site,wasm_sha256:expected.wasm,runtime_manifest_sha256:sha(runtimeBytes),
  engine_sha256:sha(await verified(enginePath)),source_patches:runtime.source.patches.slice(-3),private:true};
const qemu=JSON.parse(await verified('platform/web/qemu-browser-profiles.json'));
const board=qemu.profiles.find(row=>row.deviceId==='cores3');
const registry=JSON.parse(await verified('platform/web/uiflow-workbench-profiles.json'));
const workbench=registry.profiles.find(row=>row.deviceId==='cores3');
assert.equal(workbench.firmwareSHA256,expected.firmware);
assert.equal(workbench.baseSHA256,expected.base);
assert.equal(board.roms[0].sha256,expected.rom);
const base=await readFile(resolve(docs,'source/.work/firmware-cache',expected.base+'.bin'));
const rom=await readFile(resolve(workspace,'.work/docs-wasm-arduino-20261125/esp32s3_rev0_rom.bin'));
assert.equal(sha(base),expected.base);
assert.equal(base.length,workbench.baseBytes);
assert.equal(sha(rom),expected.rom);
assert.equal(rom.length,board.roms[0].bytes);
const downloads=new Map([[board.reference.url,base],[board.roms[0].url,rom]]);
if(process.env.M5_DUAL_KMETER_PREFLIGHT==='1'){
  console.log(JSON.stringify({status:'PREFLIGHT_OK',case:id,site_sha256:expected.site,wasm_sha256:expected.wasm,
    runtime_sha256:provenance.runtime_manifest_sha256,source_sha256:spec.sha,firmware_sha256:expected.firmware,runner_sha256:sha(await readFile(runner))}));
  process.exit(0);
}
const modules=process.env.M5_WASM_NODE_MODULES??resolve(workspace,'platform/tests/node_modules');
const {chromium}=await import(pathToFileURL(resolve(modules,'playwright/index.mjs')));
await mkdir(output);

const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json',
  '.wasm':'application/wasm','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml','.webp':'image/webp'};
const server=createServer(async(req,res)=>{
  try{
    const url=new URL(req.url,'http://localhost');
    assert.ok(url.pathname.startsWith(manifest.base_path));
    const name=decodeURIComponent(url.pathname.slice(manifest.base_path.length))||'index.html';
    const file=resolve(site,name);
    assert.ok(file.startsWith(site+sep)&&assets.has(name));
    res.writeHead(200,{'content-type':mime[extname(file)]??'application/octet-stream','Cache-Control':'no-store',
      'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp',
      'Cross-Origin-Resource-Policy':'same-origin'}).end(await readFile(file));
  }catch{res.writeHead(404).end();}
});
const report={kind:'private-cores3-dual-kmeter-workbench',status:'FAIL',evidence_level:'virtual-device validation',
  case:id,source:{project:spec.project,projectSha256:spec.assetSha,pythonSha256:spec.sha,revision:expected.revision},
  provenance,runner_sha256:sha(await readFile(runner)),page_errors:[]};
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(label,read,match,timeout=40000){
  const end=performance.now()+timeout;
  let value;
  do{
    value=await read();
    if(match(value))return value;
    await delay(60);
  }while(performance.now()<end);
  throw new Error(label+': '+JSON.stringify(value)?.slice(0,700));
}
let browser,context,workers,page,address;
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
  await page.waitForFunction(()=>crossOriginIsolated&&document.querySelector('#deviceMount')?.dataset.deviceId==='cores3');
  await page.evaluate(async address=>{
    const {PublicQemuRuntime}=await import(new URL('platform/web/public-qemu-runtime.js',address));
    const {PublicMicroPythonRunner}=await import(new URL('platform/web/public-micropython.js',address));
    const start=PublicQemuRuntime.prototype.start;
    PublicQemuRuntime.prototype.start=function(opts){
      globalThis.guest=this;
      return start.call(this,{...opts,dualKmeterExample:'m127-celsius'});
    };
    const run=PublicMicroPythonRunner.prototype.run;
    PublicMicroPythonRunner.prototype.run=async function(source,opts={}){
      const entry=globalThis.originalRun={source,phase:null,sessionId:this.runtime.sessionId,consoleEpoch:this.runtime.consoleEpoch};
      try{
        entry.result=await run.call(this,source,{...opts,onPhase(phase){entry.phase=phase;opts.onPhase?.(phase);}});
        return entry.result;
      }catch(error){entry.error=error.message;throw error;}
      finally{entry.finished=true;}
    };
  },address);
  assert.equal(await page.locator('#referenceExample').inputValue(),'uiflow');
  await page.locator('#startBtn').click();
  await page.waitForFunction(()=>globalThis.guest?.status==='running'&&guest.guestReady(),null,{timeout:120000});
  report.session=await page.evaluate(()=>({receipt:guest.receipt,sessionId:guest.sessionId,consoleEpoch:guest.consoleEpoch}));
  const receipt=report.session.receipt;
  assert.equal(receipt.profile,expected.profile);
  assert.equal(receipt.firmwareInputSha256,expected.firmware);
  assert.equal(receipt.firmwareRuntimeSha256,expected.firmware);
  assert.equal(receipt.wasmSha256,expected.wasm);
  assert.equal(receipt.clockDivisor,1);
  assert.equal(receipt.oneInsnPerTb,true);
  assert.equal(receipt.dualKmeterExample,'m127-celsius');
  await page.locator('#pythonFile').setInputFiles({name:spec.path,mimeType:'text/x-python',buffer:source});
  const editor=await page.locator('#pythonSource').inputValue();
  assert.equal(editor,editorSource);
  report.editor_sha256=sha(editor);
  await page.locator('#pythonRunBtn').click();
  await page.waitForFunction(()=>originalRun?.phase==='running');
  await page.locator('#nativeScreenBtn').click();
  const canvas=page.locator('#rawFrameCanvas');
  await canvas.waitFor({state:'visible'});
  const readModel=()=>page.evaluate(()=>guest.ask('dual-kmeter-example-state'));
  const temperature=value=>page.evaluate(temperatureCentiC=>guest.ask('dual-kmeter-example-temperature',{temperatureCentiC}),value);
  const snapshot=()=>page.evaluate(async()=>{
    const f=guest.lastFrame;
    if(!f)return null;
    const bytes=await crypto.subtle.digest('SHA-256',f.pixels);
    return {width:f.width,height:f.height,sequence:f.sourceSequence,
      sha256:[...new Uint8Array(bytes)].map(b=>b.toString(16).padStart(2,'0')).join(''),
      epoch:guest.consoleEpoch,session:guest.sessionId,phase:originalRun?.phase,output:document.querySelector('#pythonOutput')?.textContent};
  });
  report.stimuli=[];
  async function expectTemperature(centiC,expectedText,previous){
    const deadline=performance.now()+15000;
    const filename=resolve(output,`temperature-${centiC}.png`);
    let frame,model,text;
    do{
      frame=await snapshot(); model=await readModel();
      assert.ok(!/OSError|Traceback/i.test(frame?.output||''));
      if(frame?.width===320&&frame.height===240&&(!previous||frame.sequence>previous.sequence)&&frame.sha256!==previous?.sha256){
        await canvas.screenshot({path:filename});
        text=JSON.parse(execFileSync(resolve(lab,'read-display-text'),[filename],{encoding:'utf8'}));
        if(text.some(line=>line.trim().replace(/[−–]/g,'-')===expectedText)) {
          assert.equal(frame.session,report.session.sessionId);assert.equal(frame.epoch,report.session.consoleEpoch);
          assert.equal(model.kind,'dual-kmeter');
          assert.equal(model.temperatureCentiC,centiC);
          return {centiC,expectedText,text,frame,model,canvasSha256:sha(await readFile(filename))};
        }
      }
      await delay(200);
    }while(performance.now()<deadline);
    throw new Error(`No matching original temperature display for ${expectedText}: ${JSON.stringify({text,model,frame})}`);
  }
  for(const [cents,label] of [[2350,'23.5'],[-1234,'-12.34'],[8765,'87.65']]){
    const previous=report.stimuli.at(-1);
    if(previous)assert.equal((await temperature(cents)).temperatureCentiC,cents);
    const actual=await expectTemperature(cents,label,previous?.frame);
    for(const counter of ['transactions','readBytes','writtenBytes'])
      assert.ok(Number.isSafeInteger(actual.model[counter])&&actual.model[counter]>(previous?.model[counter]??0));
    report.stimuli.push(actual);
  }
  assert.equal(await page.locator('#pythonSource').inputValue(),editorSource);
  await page.locator('#pythonInterruptBtn').click();
  await page.waitForFunction(()=>originalRun?.finished===true,null,{timeout:25000});
  report.program=await page.evaluate(()=>({source:originalRun?.source,phase:originalRun?.phase,result:originalRun?.result,error:originalRun?.error}));
  assert.equal(report.program.source,editorSource);delete report.program.source;
  assert.equal(report.program.result?.interrupted,true);
  report.status='DATA_PASS';
}catch(error){
  report.error=error.stack??String(error);
  process.exitCode=1;
}finally{
  if(page&&await page.evaluate(()=>Boolean(globalThis.guest)).catch(()=>false)){
    try{
      const stop=page.locator('#stopBtn');
      report.domStop=await stop.isVisible();
      assert.equal(report.domStop,true);
      await stop.click();
      await page.waitForFunction(()=>guest.status==='stopped',null,{timeout:45000});
      report.cleanup=await page.evaluate(()=>guest.cleanupResult);
      assert.equal(report.cleanup.exitCode,0);
      assert.equal(report.cleanup.iframeRemoved,true);
      assert.ok(closedQemuPthreadBroker(report.cleanup));
    }catch(error){
      report.cleanupError=error.message;
      await page.evaluate(()=>globalThis.guest?.stop()).catch(()=>{});
      report.status='FAIL';
      process.exitCode=1;
    }
  }
  if(workers){
    report.workerCleanup=await workers.waitUntilClosed({minimumObserved:6,timeoutMs:30000}).catch(error=>({ok:false,error:error.message}));
    if(!report.workerCleanup.ok){report.status='FAIL';process.exitCode=1;}
  }
  await writeFile(resolve(output,'report.json'),JSON.stringify(report,null,2)+'\n');
  await workers?.detach();
  await context?.close();
  await browser?.close();
  if (server.listening)await new Promise(done=>server.close(done));
  console.log(JSON.stringify({case:id,status:report.status,phase:report.observation?.phase,output:report.observation?.output,error:report.error}));
}
