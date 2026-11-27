import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import fs from 'node:fs';
import {resolve} from 'node:path';
import {chromium} from 'playwright';

const [site, images, out] = process.argv.slice(2);
const config = await fetch(new URL('site-config.json', site)).then(response => response.json());
const browser = await chromium.launch({
  executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
  args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']
});
const cdp = await browser.newBrowserCDPSession();
const workers = async () => (await cdp.send('Target.getTargets')).targetInfos
  .filter(t => t.type === 'worker' && t.url.includes('/vendor/esp32sim/')).map(row => row.targetId);
const hash = data => createHash('sha256').update(data).digest('hex');
const ready = 'M5_UIFLOW_WORKBENCH_READY';

try {
  for (const device of ['stamplc','cardputer-adv','atoms3-lite']) {
    const file = resolve(images,device+'.bin');
    const row = {device, firmware_sha256:hash(fs.readFileSync(file)), checks:{}};
    if (!config.browser_esp32sim_profiles.includes(`m5stack-${device}`)) {
      row.status='NOT RUN';
      row.reason='This static export does not admit the esp32sim board.';
      fs.appendFileSync(out,JSON.stringify(row)+'\n');
      continue;
    }
    const page = await browser.newPage({viewport:{width:1380,height:1000}});
    const timings = {};
    const segment = async (label, from = 0) => {
      const t0 = performance.now();
      await page.waitForFunction(({ready, from}) => {
        const r = window.benchRuntime;
        const serial = document.querySelector('#serialOutput')?.textContent.slice(from) || '';
        const marker = serial.indexOf(ready);
        return r?.status === 'running' && marker >= 0 && serial.slice(marker).includes('>>>');
      }, {ready, from}, {timeout:20000});
      timings[label] = Math.round(performance.now()-t0);
      row.checks[label+'_ready'] = true;
      const marker = 'M5_BENCH_'+label.toUpperCase()+'_OK';
      await page.evaluate(async marker => {
        const r=window.benchRuntime;
        const command = 'print('+JSON.stringify(marker.slice(0,9))+'+'+JSON.stringify(marker.slice(9))+')\r';
        await r.input({type:'uart',channel:'uart0',text:command});
      }, marker);
      await page.waitForFunction(marker => document.querySelector('#serialOutput')?.textContent.includes(marker),
                                 marker,{timeout:5000});
      row.checks[label+'_executed_uart_source'] = true;
    };
    try {
      const url = new URL(site);
      url.search = new URLSearchParams({device,mode:'browser',engine:'esp32sim',autostart:'0'});
      await page.goto(url.href,{waitUntil:'domcontentloaded'});
      await page.evaluate(async () => {
        const {PublicBrowserRuntime}=await import(new URL('platform/web/public-browser-runtime.js', document.baseURI));
        const start=PublicBrowserRuntime.prototype.start;
        PublicBrowserRuntime.prototype.start=function (...args) { window.benchRuntime=this; return start.apply(this,args); };
      });
      await page.locator('[name=firmwareSource][value=local]').evaluate(input=>input.click());
      await page.locator('#firmwareFile').setInputFiles(file);
      await page.locator('#startBtn').click({timeout:25000});
      await segment('cold');
      const before = await workers();
      assert.equal(before.length,1);
      const offset = (await page.locator('#serialOutput').textContent()).length;
      await page.evaluate(()=>window.benchRuntime.input({type:'reset'}));
      await segment('reset', offset);
      const after = await workers();
      row.checks.old_worker_replaced=before.length===1&&after.length===1&&before[0]!==after[0];
      assert(row.checks.old_worker_replaced);
      const serial = await page.locator('#serialOutput').textContent();
      row.reset_serial_sha256=hash(serial.slice(offset));
      row.pif_oob=serial.match(/LoadStorePIFAddrError|memory access out of bounds/g)?.length ?? 0;
      assert.equal(row.pif_oob,0);
      row.status='PASS';
    } catch(error) {
      row.status='FAIL';
      row.error=String(error).split('\n')[0];
      row.serial_tail=await page.locator('#serialOutput').textContent({timeout:2000})
        .then(value=>value.slice(-2000)).catch(()=>null);
    } finally {
      if ((await workers()).length) {
        await page.locator('#stopBtn').click({timeout:3000}).catch(()=>{});
        for(let i=0;i<80 && (await workers()).length;i++)await page.waitForTimeout(50);
      }
      row.timings=timings;
      row.workers_after_stop=(await workers()).length;
      await page.close();
      const line=JSON.stringify(row);
      fs.appendFileSync(out,line+'\n');
      console.log(line);
    }
  }
} finally {
  await browser.close();
}
