import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import fs from 'node:fs';
import {chromium} from 'playwright';

const [site, firmware, output] = process.argv.slice(2);
const inputHash = createHash('sha256').update(fs.readFileSync(firmware)).digest('hex');
assert.equal(inputHash, 'd6733a0ca378f95335fa5fba4d4d992fb1dd97c17557b20e9aebfca08ba6d624');
const rows = {firmware_sha256:inputHash, inputs:[], status:'FAIL'};
const browser = await chromium.launch({
  executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
  args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'],
});
const page = await browser.newPage({viewport:{width:1380,height:1000}});
const cdp = await browser.newBrowserCDPSession();
const workers = async () => (await cdp.send('Target.getTargets')).targetInfos.filter(r=>r.type==='worker').length;
const sample = () => page.locator('#rawFrameCanvas').evaluate(canvas => {
  if (canvas.width!==540||canvas.height!==960) return null;
  const rgba=canvas.getContext('2d').getImageData(78,296,77,89).data;
  let black=0, hash=2166136261;
  for(let i=0;i<rgba.length;i+=4) {
    if (rgba[i]===0&&rgba[i+1]===0&&rgba[i+2]===0&&rgba[i+3]) black++;
    hash=Math.imul(hash^rgba[i],16777619);
  }
  return {black,hash};
});
try {
  const url = new URL(site);
  url.search=new URLSearchParams({device:'papers3',engine:'esp32sim',mode:'browser',autostart:'0'});
  await page.goto(url.href);
  await page.evaluate(async () => {
    const {PublicBrowserRuntime} = await import(new URL('platform/web/public-browser-runtime.js',document.baseURI));
    const start=PublicBrowserRuntime.prototype.start;
    PublicBrowserRuntime.prototype.start=function(...args){window.paperRuntime=this;return start.apply(this,args);};
  });
  await page.locator('[name=firmwareSource][value=local]').evaluate(input=>input.click());
  await page.locator('#firmwareFile').setInputFiles(firmware);
  await page.locator('#startBtn').click({timeout:15000});
  await page.waitForFunction(()=>document.querySelector('#serialOutput')?.textContent.includes('board_M5PaperS3'),{}, {timeout:18000});
  rows.initial_raster = await page.locator('#rawFrameCanvas').evaluate(canvas =>
    ({width:canvas.width,height:canvas.height}));
  for (let i=0;i<30;i++) {
    const initial = await sample();
    if (initial && initial.black>0 && initial.black<77*89) break;
    await page.waitForTimeout(400);
  }
  assert.equal(await page.locator('#firmwareInputSha256').textContent(),inputHash);
  rows.flash_sha256=await page.locator('#firmwareRuntimeSha256').textContent();
  rows.workers_before=await workers();
  for(const hold_ms of [150,300,500,500,300,150,300,500,150,500,300,500]) {
    const before=await sample();
    assert(before && before.black>0 && before.black<77*89, 'No matching initial PaperS3 icon raster in the observation window');
    await page.evaluate(()=>paperRuntime.input({type:'touch', x:113,y:347,down:true}));
    await page.waitForTimeout(hold_ms);
    await page.evaluate(()=>paperRuntime.input({type:'touch', x:113,y:347,down:false}));
    await page.waitForTimeout(1500);
    const after=await sample();
    rows.inputs.push({hold_ms,before,after,changed:after.hash!==before.hash});
  }
  rows.status='PARTIAL';
} catch(error) {
  rows.error=String(error).split('\n')[0];
} finally {
  if (await workers()) {
    await page.locator('#stopBtn').click({timeout:3000}).catch(()=>{});
    for(let i=0;i<80&&(await workers());i++)await page.waitForTimeout(50);
  }
  rows.workers_after=await workers();
  await browser.close();
  fs.writeFileSync(output,JSON.stringify(rows,null,2)+'\n');
}
