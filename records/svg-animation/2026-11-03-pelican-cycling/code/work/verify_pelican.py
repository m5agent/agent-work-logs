from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
result = {"browser_errors": [], "network_requests": [], "poses": [], "viewports": []}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get("PELICAN_BROWSER_EXECUTABLE"), headless=True)
    page = browser.new_page(viewport={"width":1120,"height":800}, device_scale_factor=1)
    page.on("pageerror", lambda e: result["browser_errors"].append(str(e)))
    page.on("request", lambda r: result["network_requests"].append(r.url) if r.url.startswith(("http:","https:")) else None)
    page.goto((ROOT / "work/preview.html").as_uri())
    page.wait_for_timeout(150)
    page.evaluate('document.querySelector("svg").pauseAnimations()')
    for i, t in enumerate([0,.2,.4,.6,.8,1.,1.2,1.4,1.6]):
        page.evaluate('(t) => document.querySelector("svg").setCurrentTime(t)', t)
        page.wait_for_timeout(25)
        pose = page.evaluate('''() => {
          const errors = {};
          for (const side of ['near', 'far']) {
            const leg = document.getElementById(side + '-leg');
            const end = leg.getPointAtLength(leg.getTotalLength());
            const foot = document.getElementById(side + '-foot').transform.animVal.getItem(0).matrix;
            errors[side] = Math.hypot(end.x - (foot.e - 5), end.y - (foot.f - 10));
          }
          const r = document.getElementById('rider').transform.animVal.getItem(0).matrix;
          const hip = document.getElementById('near-leg').getPointAtLength(0);
          return {foot_attachment_errors:errors, hip_attachment_error: Math.abs(hip.y-380-r.f), body_y:r.f};
        }''')
        pose['time'] = t
        assert max(pose['foot_attachment_errors'].values()) < .04, pose
        assert pose['hip_attachment_error'] < .02, pose
        result['poses'].append(pose)
        if i in [0, 2, 4, 6]:
            page.screenshot(path=str(ROOT / f'work/pose-{i//2}.png'))
    for width in [1120,736,320]:
        page.set_viewport_size({"width":width,"height":max(240,round(width*800/1120))})
        page.wait_for_timeout(40)
        dims = page.evaluate('''() => { const s=document.querySelector('svg').getBoundingClientRect(); const c=document.querySelector('#scene rect'); return {width:innerWidth,svg_width:s.width,svg_height:s.height,scroll_width:document.documentElement.scrollWidth,clip_width:c.width.baseVal.value,clip_height:c.height.baseVal.value,animations:document.querySelectorAll('animate,animateTransform').length}; }''')
        assert dims['svg_width'] == width, dims
        assert dims['scroll_width'] == width, dims
        assert dims['clip_height'] == 800, dims
        result['viewports'].append(dims)
        page.screenshot(path=str(ROOT / f'work/viewport-{width}.png'))
    # Verify the SVG itself also runs when opened directly, without the wrapper.
    page.goto((ROOT / 'outputs/pelican-cycling.svg').as_uri())
    page.wait_for_timeout(120)
    assert page.locator('parsererror').count() == 0
    result['standalone_svg'] = page.evaluate('({animations:document.querySelectorAll("animate,animateTransform").length,time:document.documentElement.getCurrentTime()})')
    result['browser'] = browser.version
    browser.close()
assert not result['browser_errors'], result['browser_errors']
assert not result['network_requests'], result['network_requests']
(ROOT / 'work/verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
