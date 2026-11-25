import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname,extname,resolve,sep} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

assert.equal(process.env.M5_STOCK_M5UI_RUN,'1','Enable the isolated single-guest test explicitly');
const runner=fileURLToPath(import.meta.url),lab=dirname(runner),workspace=resolve(lab,'../..');
const repo=resolve(workspace,'.work/docs-wasm-cardputer-adv-sx1262-source');
const docs=resolve(workspace,'.work/docs-uiflow-20261125');
const [id,outputName]=process.argv.slice(2);
const cases={
  switch:{path:'examples/m5ui/switch/cores3_switch_event_example.py',sha:'ddca9d31feeee60478bacacb32d35275bc110c388924146a90b175eac7b5cc2a',
    control:[128,91,60,30],outside:[25,58],point:[158,106]},
  slider:{path:'examples/m5ui/slider/cores3_slider_basic_example.py',sha:'e3c7f359fd6dfba395bd16b78adefaabdabe3878f70966a8c6265afdd8261a71',
    control:[54,101,220,32],label:[140,135,90,32],outside:[25,58],drag:[[110,119],[225,119]]},
};
assert.ok(Object.hasOwn(cases,id));
assert.match(outputName??'',/^browser-0046-stock-m5ui-[a-z0-9-]+$/);
const spec=cases[id],output=resolve(lab,outputName);
const switchDiagnostic=process.env.M5_STOCK_M5UI_SWITCH_DIAGNOSTIC==='1'&&id==='switch';
const site=resolve(process.env.M5_PUBLIC_SITE??resolve(workspace,'.work/docs-wasm-cardputer-lora-lab/locked-0046-site'));
const expected={wasm:'210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211',
  site:'cec271aefa1a575d8b257ea899a8af91eb8209575202fef99fb919bab37f16ac',
  runtime:'a56410a8fb99a0e65ce7a7017c3a5ceb8ce0bd832451cbc71e12317cf614a0b9',
  firmware:'b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49',
  base:'1324f12d3ddd5392f47a9eff537f9ce0b01a8e6e36d829b6bd22cdf82d2c1264',
  rom:'b5c7090cc22efce51c1323cef31ca96fcd673a5b1d1b1017e219d393f2659913',
  profile:'cores3-wasm-uiflow-workbench-lvgl-wallclock-candidate',
  revision:'a61a29409f09f1f4bebae05e15c4bd6dcc4956b6'};
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const source=await readFile(resolve(docs,'upstream',spec.path));
const editorSource=source.toString('utf8').replace(/\r\n?/g,'\n');
assert.equal(sha(source),spec.sha);
assert.equal(sha(editorSource),spec.sha);
if(id==='switch'){
  const alias=await readFile(resolve(docs,'upstream/examples/m5ui/arc/cores3_arc_event_example.py'));
  assert.deepEqual(alias,source,'same source bytes for Arc inventory row and Switch');
}
const srcUrl=name=>pathToFileURL(resolve(repo,'platform/tests',name));
const {capturePublicQemuProvenance,QEMU_EXECUTED_WEB_PATHS}=await import(srcUrl('public_qemu_artifacts.mjs'));
const {observeWorkerTargets,closedQemuPthreadBroker}=await import(srcUrl('public_qemu_worker_targets.mjs'));
const provenance=await capturePublicQemuProvenance({repo,site,webPaths:[
  ...QEMU_EXECUTED_WEB_PATHS,'platform/web/public-micropython.js','platform/web/public-uiflow-firmware.js',
  'platform/web/uiflow-workbench-profiles.json',
]});
assert.equal(provenance.site_manifest_sha256,expected.site);
assert.equal(provenance.runtime_manifest_sha256,expected.runtime);
assert.equal(provenance.runtime_assets['qemu-system-xtensa.wasm'].sha256,expected.wasm);
assert.equal(provenance.runtime_build.all_objects_rebuilt,true);
const manifest=JSON.parse(await readFile(resolve(site,'public-site-manifest.json')));
assert.equal(manifest.base_path,'/showcase/');
assert.equal(manifest.publication_eligible,true);
const assets=new Map(manifest.assets.map(row=>[row.path,row]));
async function verified(path){
  const bytes=await readFile(resolve(site,path));
  assert.equal(sha(bytes),assets.get(path)?.sha256,path);
  assert.equal(bytes.length,assets.get(path)?.bytes,path);
  return bytes;
}
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
if(process.env.M5_STOCK_M5UI_PREFLIGHT==='1'){
  console.log(JSON.stringify({status:'PREFLIGHT_OK',case:id,site_sha256:expected.site,wasm_sha256:expected.wasm,
    runtime_sha256:expected.runtime,source_sha256:spec.sha,firmware_sha256:expected.firmware,runner_sha256:sha(await readFile(runner))}));
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
const report={kind:'stock-cores3-m5ui-workbench-0046',status:'FAIL',evidence_level:'virtual-device validation',
  case:id,source:{path:spec.path,sha256:spec.sha,revision:expected.revision},
  ...(id==='switch'?{deduplicated_same_source:'examples/m5ui/arc/cores3_arc_event_example.py'}:{}),
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
let browser,context,workers,page,address,canvas;
const text=()=>page.locator('#pythonOutput').textContent();
const markers=async()=>((await text())||'').match(/switch0 (?:un)?checked/g)??[];
const snapshot=()=>page.evaluate(async ({control,label})=>{
  const current=guest.lastFrame;
  if(!current)return null;
  const pixels=Uint8Array.from(current.pixels),w=current.width,h=current.height;
  if(w!==320||h!==240)return {width:w,height:h};
  const digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),
    value=>value.toString(16).padStart(2,'0')).join('');
  function pixelsIn([x,y,regionWidth,regionHeight]){
    const shape=new Uint8Array(regionWidth*regionHeight*2);
    let green=0,grey=0,blue=0,dark=0,white=0,blueXMin=w,blueXMax=-1,blueXSum=0;
    for(let a=0;a<regionHeight;a++){
      const index=2*((a+y)*w+x);
      shape.set(pixels.subarray(index,index+regionWidth*2),a*regionWidth*2);
      for(let b=0;b<regionWidth;b++){
        const i=index+2*b,p=pixels[i]|pixels[i+1]<<8;
        const r=(p>>11)&31,g=(p>>5)&63,c=p&31;
        if(r<10&&g>42&&c<12)green++;
        if(r>=11&&r<=13&&g>=23&&g<=27&&c>=11&&c<=13)grey++;
        if(r<15&&g>20&&g<54&&c>20){blue++;blueXSum+=b+x;blueXMin=Math.min(blueXMin,b+x);blueXMax=Math.max(blueXMax,b+x);}
        if(r<12&&g<24&&c<12)dark++;
        if(r>=29&&g>=59&&c>=29)white++;
      }
    }
    return {shape,green,grey,blue,dark,white,blueXMin,blueXMax,blueXMean:blue?blueXSum/blue:null};
  }
  async function region(rect){
    const {shape,...metrics}=pixelsIn(rect);
    return {rect,sha256:await digest(shape),...metrics};
  }
  const corner=pixelsIn([0,0,26,26]);
  return {width:w,height:h,sequence:guest.sequence,source:current.source,
    source_sequence:current.sourceSequence,frame_sha256:await digest(pixels),
    corner_white:corner.white,control:await region(control),...(label?{label:await region(label)}:{})};
},spec);
async function point(x,y){
  await canvas.scrollIntoViewIfNeeded();
  const target=await canvas.evaluate((node,[x,y])=>{
    const rect=node.getBoundingClientRect();
    const actual={x:rect.left+(x+0.5)*rect.width/node.width,y:rect.top+(y+0.5)*rect.height/node.height};
    return {...actual,width:node.width,height:node.height,has_front_canvas:document.elementFromPoint(actual.x,actual.y)===node};
  },[x,y]);
  assert.equal(target.has_front_canvas,true,'the real pointer target is the unobstructed flat guest framebuffer');
  assert.equal(target.width,320);assert.equal(target.height,240);
  return target;
}
async function tap(coordinate,hold=650){
  const at=await point(...coordinate);
  await page.mouse.move(at.x,at.y);
  await page.mouse.down();
  await delay(hold);
  await page.mouse.up();
  return at;
}
async function drag(start,end){
  const from=await point(...start),to=await point(...end);
  await page.mouse.move(from.x,from.y);
  await page.mouse.down();
  await delay(400);
  for(let i=1;i<=8;i++){
    await page.mouse.move(from.x+(to.x-from.x)*i/8,from.y+(to.y-from.y)*i/8);
    await delay(90);
  }
  await page.mouse.up();
  return {from,to};
}
const hits=()=>page.evaluate(()=>guest.evidence().inputs.filter(event=>event.type==='touch'));
const take=path=>canvas.screenshot({path:resolve(output,path)});
function containsEdge(rows,[x,y],down){
  return rows.some(row=>row.down===down&&Math.abs(row.x-x)<=2&&Math.abs(row.y-y)<=2);
}

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
    PublicQemuRuntime.prototype.start=function(opts){globalThis.guest=this;return start.call(this,opts);};
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
  await page.locator('#pythonFile').setInputFiles({name:spec.path.split('/').at(-1),mimeType:'text/x-python',buffer:source});
  const editor=await page.locator('#pythonSource').inputValue();
  assert.equal(editor,editorSource);
  report.editor_sha256=sha(editor);
  await page.locator('#pythonRunBtn').click();
  await page.waitForFunction(()=>globalThis.originalRun?.phase==='running');
  await page.locator('#nativeScreenBtn').click();
  canvas=page.locator('#rawFrameCanvas');
  await canvas.waitFor({state:'visible'});
  let roiIdentity, stableSince;
  report.initial=await until('original M5UI canvas and completed control before the first input',snapshot,row=>{
    if(!(row?.width===320&&row.height===240&&row.corner_white>=650&&
      (id==='switch'?row.control.green===0&&row.control.grey>750:row.control.blue>20&&row.label.dark>0)))return false;
    const current=row.control.sha256+(row.label?.sha256??'');
    if(current!==roiIdentity){roiIdentity=current;stableSince=performance.now();}
    return performance.now()-stableSince>=950;
  });
  assert.equal(report.initial.source,'qemu-display-surface-shared');
  await take('before.png');

  const beforeTouch=(await hits()).length;
  report.outside_point=await tap(spec.outside);
  await delay(800);
  report.outside_after=await snapshot();
  report.outside_events=(await hits()).slice(beforeTouch);
  assert.ok(containsEdge(report.outside_events,spec.outside,true)&&containsEdge(report.outside_events,spec.outside,false));
  assert.equal(report.outside_after.control.sha256,report.initial.control.sha256);
  if(id==='slider')assert.equal(report.outside_after.label.sha256,report.initial.label.sha256);
  else assert.deepEqual(await markers(),[]);

  const inputStart=(await hits()).length;
  let switchPoint=spec.point;
  if(id==='switch'){
    if(switchDiagnostic){
      report.switch_orientation_trials=[];
      const [x,y]=spec.point;
      for(const trial of [spec.point,[y,239-x],[319-y,x]]){
        const at=await tap(trial,200);
        await delay(1400);
        const trialResult={point:trial,at,frame:await snapshot(),markers:await markers()};
        report.switch_orientation_trials.push(trialResult);
        if(trialResult.markers.includes('switch0 checked')||trialResult.frame.control.green>100){
          switchPoint=trial;
          report.on_point=at;
          break;
        }
      }
    }else report.on_point=await tap(spec.point);
    await until('original switch checked UART marker',markers,events=>events.length===1&&events[0]==='switch0 checked',
      switchDiagnostic?4500:40000);
    report.checked=await until('green LVGL checked switch ROI',snapshot,
      row=>row?.control.green>100&&row.control.sha256!==report.initial.control.sha256);
    await take('checked.png');
    report.off_point=await tap(switchPoint,switchDiagnostic?200:650);
    await until('original switch unchecked UART marker',markers,
      events=>events.length===2&&events[0]==='switch0 checked'&&events[1]==='switch0 unchecked');
    report.unchecked=await until('checked color is removed and switch visual state restores',snapshot,
      row=>row?.control.green===0&&row.control.grey>100&&row.control.sha256!==report.checked.control.sha256);
    report.marker_order=await markers();
    await take('unchecked.png');
  }else{
    report.drag=await drag(...spec.drag);
    report.slider_changed=await until('thumb and separate numeric label after the original value-changed callback',snapshot,
      row=>row?.control.blue>20&&row.control.sha256!==report.initial.control.sha256&&
        row.label.dark>0&&row.label.sha256!==report.initial.label.sha256);
    assert.ok(report.slider_changed.source_sequence>report.initial.source_sequence);
    await take('dragged.png');
  }
  report.in_control_events=(await hits()).slice(inputStart);
  if(id==='switch'){
    assert.equal(report.in_control_events.filter(row=>row.down&&Math.abs(row.x-switchPoint[0])<=2&&Math.abs(row.y-switchPoint[1])<=2).length,2);
    assert.equal(report.in_control_events.filter(row=>!row.down&&Math.abs(row.x-switchPoint[0])<=2&&Math.abs(row.y-switchPoint[1])<=2).length,2);
  }else{
    assert.ok(containsEdge(report.in_control_events,spec.drag[0],true));
    assert.ok(containsEdge(report.in_control_events,spec.drag[1],false));
  }
  const running=await page.evaluate(()=>({phase:originalRun.phase,finished:originalRun.finished}));
  assert.equal(running.phase,'running');
  assert.equal(running.finished,undefined);
  await page.locator('#pythonInterruptBtn').click();
  const ended=await until('original program stopped normally from editor',()=>page.evaluate(()=>originalRun),row=>row?.finished);
  assert.equal(ended.result?.transfer,'raw-paste');
  assert.equal(ended.result?.interrupted,true);
  assert.equal(ended.result?.sessionId,report.session.sessionId);
  assert.equal(ended.result?.consoleEpoch,report.session.consoleEpoch);
  report.original_result={transfer:ended.result.transfer,interrupted:true,stdout:ended.result.stdout};
  assert.deepEqual(report.page_errors,[]);
  report.rotated_alternate_control=switchDiagnostic&&switchPoint!==spec.point;
  report.status='DATA_PASS';
}catch(error){
  report.error=error.stack??String(error);
  process.exitCode=1;
}finally{
  if(page&&await page.evaluate(()=>Boolean(globalThis.guest)).catch(()=>false)){
    report.observed_before_stop={
      frame:await snapshot().catch(()=>null),
      touch_events:await hits().catch(()=>[]),
      program_output:await text().catch(()=>null),
    };
    if(canvas&&(await canvas.isVisible().catch(()=>false))&&report.status==='FAIL')
      await take('last-visible.png').catch(()=>{});
    try{
      report.dom_stop=await page.locator('#stopBtn').isVisible();
      if(report.dom_stop)await page.locator('#stopBtn').click();
      else if(await page.evaluate(()=>guest.status!=='stopped'))await page.evaluate(()=>guest.stop());
      await page.waitForFunction(()=>guest.status==='stopped',null,{timeout:45000});
      report.final=await page.evaluate(()=>({status:guest.status,sessionId:guest.sessionId,consoleEpoch:guest.consoleEpoch,
        cleanup:guest.cleanupResult,console:guest.serial.slice(-12000)}));
    }catch(error){
      report.cleanup_error=error.message;
      await page.evaluate(()=>globalThis.guest?.stop()).catch(()=>{});
      process.exitCode=1;
    }
  }
  if(workers){
    const minimum=Math.max(1,(report.final?.cleanup?.workersCreated??0)+1);
    report.worker_cleanup=await workers.waitUntilClosed({minimumObserved:minimum,timeoutMs:30000}).catch(error=>({ok:false,error:error.message}));
    if(report.status==='DATA_PASS'){
      const value=report.final;
      const ok=Boolean(value&&report.dom_stop&&value.status==='stopped'&&value.sessionId===report.session.sessionId
        &&value.consoleEpoch===report.session.consoleEpoch&&value.cleanup.gracefulExit&&value.cleanup.exitCode===0
        &&value.cleanup.iframeRemoved&&closedQemuPthreadBroker(value.cleanup)
        &&report.worker_cleanup.ok&&report.worker_cleanup.observed.length===minimum);
      report.status=ok?(report.rotated_alternate_control?'PARTIAL':'PASS'):'FAIL';
      if(!ok)process.exitCode=1;
    }
  }
  await writeFile(resolve(output,'report.json'),JSON.stringify(report,null,2)+'\n');
  await workers?.detach();
  await context?.close();
  await browser?.close();
  await new Promise(done=>server.close(done));
  console.log(JSON.stringify({status:report.status,case:id,error:report.error??null,workers:report.worker_cleanup?.observed?.length??0}));
}
