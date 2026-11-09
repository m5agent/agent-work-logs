import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir } from 'node:fs/promises';
import { chromium } from 'playwright-core';

const [base, output, ...selectedModels] = process.argv.slice(2);
const modelIds = selectedModels.length ? selectedModels : ['paperdiy','papers3','cardputer','corematrix'];
const cases = {
  sticks3: { sku: 'K150', dimensions: [135, 240], display: 'lcd', key: 'btnA' },
  paperdiy: { sku: 'K159-B', dimensions: [540, 960], display: 'lcd', key: 'key1' },
  papers3: { sku: 'C139', dimensions: [540, 960], display: 'lcd', key: 'power', touch: true },
  cardputer: { sku: 'K132', dimensions: [240, 135], display: 'lcd', key: 'key-KeyA', keyboard: true },
  corematrix: { sku: 'C158', dimensions: [16, 16], display: 'display', key: 'btnA' },
};
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
await mkdir(output, {recursive:true});
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || undefined,
  args: ['--enable-webgl', '--enable-unsafe-swiftshader', '--use-angle=swiftshader'],
});
try {
  for (const id of modelIds) {
    const test = cases[id];
    const page = await browser.newPage({viewport:{width:1400,height:1040}, deviceScaleFactor:1});
    const failures = [];
    const staticFiles = new Map();
    page.on('pageerror', error => failures.push(error.message));
    page.on('response', response => {
      const url = new URL(response.url());
      if (url.origin !== new URL(base).origin) return;
      if (!response.ok() && response.status() !== 304) failures.push(`HTTP ${response.status()} ${url.pathname}`);
      if (url.pathname.includes('/assets/') || url.pathname.endsWith('/data/catalog.json')) {
        staticFiles.set(url.pathname, response);
      }
    });
    page.on('requestfailed', request => {
      if (new URL(request.url()).origin === new URL(base).origin) failures.push(request.failure().errorText);
    });
    const url = new URL(base);
    url.searchParams.set('model', id);
    const response = await page.goto(url.href, {waitUntil:'domcontentloaded', timeout:60000});
    assert.equal(response.status(), 200);
    const stage = page.locator('#stage');
    await stage.and(page.locator(`[data-state=ready][data-model=${id}]`)).waitFor({timeout:45000});
    assert.match(await page.locator('#model-tag').innerText(), new RegExp(test.sku + '$'));
    assert.match(await page.locator('#facts').innerText(), new RegExp(test.dimensions.join(' × ')));
    const canvas = stage.locator('canvas');
    assert.equal(await canvas.count(), 1);
    await page.waitForTimeout(1250);
    const iso = await stage.screenshot({path:`${output}/${id}-iso.png`});
    await page.locator('[data-view=back]').click();
    await page.waitForTimeout(1250);
    const back = await stage.screenshot({path:`${output}/${id}-back.png`});
    await page.locator('[data-view=front]').click();
    await page.waitForTimeout(1250);
    const blank = await stage.screenshot({path:`${output}/${id}-front-blank.png`});
    const calibration = page.locator('#calibration');
    assert.equal(await calibration.getAttribute('data-display'), test.display);
    await calibration.click();
    await page.waitForTimeout(300);
    assert.equal(await calibration.getAttribute('aria-pressed'), 'true');
    const frame = await stage.screenshot({path:`${output}/${id}-front-calibration.png`});
    assert.notEqual(hash(blank), hash(frame), `${id}: calibration frame should visibly update`);
    const directInput = {};
    if (test.touch) {
      const box = await canvas.boundingBox();
      const x = box.x + box.width * 0.5, y = box.y + box.height * 0.48;
      await page.mouse.move(x, y);
      await page.mouse.down();
      assert.match(await page.locator('#input-events').innerText(), /lcd · start/);
      await page.mouse.move(x + 15, y + 15, {steps:3});
      await page.mouse.up();
      directInput.touch = await page.locator('#input-events').innerText();
      for (const action of ['start','move','end']) assert.ok(directInput.touch.includes('lcd · ' + action));
    }
    if (test.keyboard) {
      await canvas.focus();
      await page.keyboard.down('KeyA');
      await page.waitForFunction(() => document.querySelector('#input-events').textContent.includes('key-KeyA · down · key:KeyA'));
      await page.keyboard.up('KeyA');
      await page.waitForFunction(() => document.querySelector('#input-events').textContent.includes('key-KeyA · up · key:KeyA'));
      directInput.keyboard = await page.locator('#input-events').innerText();
    }
    const control = page.locator(`[data-button=${test.key}]`);
    await control.scrollIntoViewIfNeeded();
    await control.focus();
    await page.keyboard.down('Space');
    await page.waitForFunction(key => document.querySelector(`[data-button=${key}]`).getAttribute('aria-pressed') === 'true', test.key);
    await page.keyboard.up('Space');
    await page.waitForFunction(key => document.querySelector(`[data-button=${key}]`).getAttribute('aria-pressed') === 'false', test.key);
    const input = await page.locator('#input-events').innerText();
    assert.match(input, new RegExp(test.key + ' · up'));
    await page.locator('#reference-toggle').click();
    const reference = page.locator('#reference-image');
    const referenceLoaded = await reference.evaluate(image => Promise.race([
      image.decode().then(() => image.naturalWidth > 0, () => false),
      new Promise(resolve => setTimeout(() => resolve(false), 10000)),
    ]));
    await page.locator('#reference-toggle').click();
    assert.deepEqual(failures, []);
    const assets = Object.fromEntries(await Promise.all([...staticFiles].map(async ([path, res]) => [path, hash(await res.body())])));
    console.log(JSON.stringify({
      id, sku:test.sku, display:test.display, browser:browser.version(), referenceLoaded, input, directInput,
      images:{iso:hash(iso),back:hash(back),blank:hash(blank),frame:hash(frame)}, assets,
    }));
    await page.close();
  }
} finally {
  await browser.close();
}
