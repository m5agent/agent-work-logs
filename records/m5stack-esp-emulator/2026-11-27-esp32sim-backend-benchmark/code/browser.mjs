import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, appendFile, mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {chromium} from 'playwright';

const [site, caseFile, out] = process.argv.slice(2);
const cases = JSON.parse(await readFile(caseFile, 'utf8'));
const browser = await chromium.launch({
  executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
  args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']
});
const cdp = await browser.newBrowserCDPSession();
const workers = async () => (await cdp.send('Target.getTargets')).targetInfos
  .filter(t => t.type === 'worker').length;
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
await mkdir(out, {recursive:true});
try {
  for (const [device, example, path] of cases) {
    const firmware = resolve(path);
    const firmwareSha256 = sha(await readFile(firmware));
    for (let i = 0; i < 3; i++) {
      const engines = i % 2 ? ['esp32sim', 'qemu-wasm'] : ['qemu-wasm', 'esp32sim'];
      for (const engine of engines) {
        const context = await browser.newContext({viewport:{width:1380,height:1000}});
        const page = await context.newPage();
        const result = {device, example, firmwareSha256, engine, run:i+1, browser:browser.version()};
        const before = await workers();
        try {
          await page.addInitScript(() => {
            document.addEventListener('click', event => {
              if (event.target.id === 'startBtn') window.benchBegin = performance.now();
            }, {capture:true});
          });
          const url = new URL(site);
          url.search = new URLSearchParams({device, mode:'browser', autostart:'0', engine});
          await page.goto(url.href, {waitUntil:'domcontentloaded'});
          if (engine === 'qemu-wasm') await page.waitForFunction(() => crossOriginIsolated, {}, {timeout:45000});
          await page.locator('[name=firmwareSource][value=local]').evaluate(input=>input.click());
          await page.locator('#firmwareFile').setInputFiles(firmware);
          await page.locator('#startBtn').click({timeout:45000});
          const shown = await page.waitForFunction(() => {
            const ready = document.querySelector('#runtimeStatus')?.dataset.status === 'running';
            const canvas = document.querySelector('#rawFrameCanvas');
            if (!ready || !canvas?.width || !canvas.height || !window.benchBegin) return false;
            const pixels = canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
            for (let i=0;i<pixels.length;i+=4) if (pixels[i] || pixels[i+1] || pixels[i+2]) {
              return {ms:performance.now()-window.benchBegin,width:canvas.width,height:canvas.height};
            }
            return false;
          }, {}, {polling:50,timeout:45000});
          result.first_rendered_frame = await shown.jsonValue();
          result.frame_sha256 = sha(await page.locator('#rawFrameCanvas').evaluate(canvas => canvas.toDataURL()));
          result.runtime_flash_sha256 = await page.locator('#firmwareRuntimeSha256').textContent();
          assert.equal(await page.locator('#firmwareInputSha256').textContent(), firmwareSha256);
          result.workers_running = (await workers()) - before;
          await page.locator('#stopBtn').click();
          for(let i = 0;i<150 && (await workers()) !== before;i++) await page.waitForTimeout(50);
          result.workers_after_stop = (await workers()) - before;
          assert.equal(result.workers_after_stop, 0);
          result.status = 'PASS';
        } catch(error) {
          result.status = 'FAIL';
          result.error = String(error).split('\n')[0];
          result.ui = await page.evaluate(() => ({
            state:document.querySelector('#runtimeStatus')?.textContent,
            error:document.querySelector('#errorBanner')?.textContent,
            isolated:crossOriginIsolated
          })).catch(()=>null);
        } finally {
          await context.close();
          console.log(JSON.stringify(result));
          await appendFile(resolve(out,'browser.jsonl'), JSON.stringify(result) + '\n');
        }
      }
    }
  }
} finally {
  await browser.close();
}
