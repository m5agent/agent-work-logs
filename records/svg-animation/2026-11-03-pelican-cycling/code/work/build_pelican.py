from pathlib import Path
import math
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
OUT = ROOT / "outputs"
VIZ = OUT / "preview"
N = 96
T = 1.6
frames = [2 * math.pi * i / N for i in range(N + 1)]
def fmt(v):
    return f"{v:.2f}"
def point(p):
    return " ".join(map(fmt, p))
def anim(attribute, values):
    return f'<animate attributeName="{attribute}" values="{";".join(values)}" dur="{T}s" repeatCount="indefinite"/>'

def build_leg(far=False):
    paths, cranks, feet = [], [], []
    distances = []
    for th in frames:
        bob = -2.6 * math.sin(2 * th)
        hx, hy = (480, 376 + bob) if far else (490, 380 + bob)
        phase = th + (math.pi if far else 0)
        px, py = 540 + 34 * math.cos(phase), 537 + 34 * math.sin(phase)
        ax, ay = px - 5, py - 10
        dx, dy = ax - hx, ay - hy
        d = math.hypot(dx, dy)
        l1, l2 = 105, 108
        distances.append(d)
        assert abs(l1 - l2) < d < l1 + l2, (far, th, d)
        a = (l1*l1 - l2*l2 + d*d) / (2*d)
        h = math.sqrt(l1*l1 - a*a)
        kx = hx + a * dx/d + h * dy/d
        ky = hy + a * dy/d - h * dx/d
        paths.append(f"M{point((hx,hy))}L{point((kx,ky))}L{point((ax,ay))}")
        cranks.append(f"M540 537L{point((px,py))}")
        feet.append(f"{fmt(px)} {fmt(py)}")
    # Avoid tiny trigonometric differences at the seam.
    paths[-1], cranks[-1], feet[-1] = paths[0], cranks[0], feet[0]
    color = "#596b60" if far else "#3e5550"
    leg = f'<path id="{"far" if far else "near"}-leg" d="{paths[0]}" fill="none" stroke="{color}" stroke-width="11" stroke-linecap="round" stroke-linejoin="round">{anim("d", paths)}</path>'
    crank = f'<path d="{cranks[0]}" fill="none" stroke="#294947" stroke-width="7" stroke-linecap="round">{anim("d",cranks)}</path>'
    foot = f'''<g id="{"far" if far else "near"}-foot" transform="translate({feet[0]})">
      <animateTransform attributeName="transform" type="translate" values="{";".join(feet)}" dur="{T}s" repeatCount="indefinite"/>
      <path d="M-20 7H24" stroke="#294947" stroke-width="8" stroke-linecap="round"/>
      <path d="M-6-14Q0-15 5-7L24-3L30 3L10 2L3 5L-7 2L-17 4L-14-2Z" fill="{"#cf955f" if far else "#eab467"}" stroke="#294947" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="M5-5L11 0M12-3L19 0" stroke="#ab784e" stroke-width="1.5"/>
    </g>'''
    print(f'{"far" if far else "near"} leg: hip-to-ankle range {min(distances):.2f}–{max(distances):.2f}; IK reach 213; seam matched')
    return leg, crank, foot

far = build_leg(True)
near = build_leg(False)
bob_values = [f'0 {fmt(-2.6*math.sin(2*th))}' for th in frames]
bob_values[-1] = bob_values[0]
bob = f'<animateTransform attributeName="transform" type="translate" values="{";".join(bob_values)}" dur="{T}s" repeatCount="indefinite"/>'
svg = (WORK / "pelican-template.svg").read_text()
road_a = ' '.join(f'M{k*344+offset} 712h{length}' for k in range(-2, 6) for offset,length in [(0,48),(129,14),(250,38)])
road_b = ' '.join(f'M{k*510+offset} 746h{length}' for k in range(-2, 5) for offset,length in [(0,19),(97,58),(252,32),(406,18)])
for token, value in dict(FAR_LEG=far[0], FAR_CRANK=far[1], FAR_FOOT=far[2], NEAR_LEG=near[0], NEAR_CRANK=near[1], NEAR_FOOT=near[2], BODY_BOB=bob, ROAD_A=road_a, ROAD_B=road_b).items():
    svg = svg.replace(f'__{token}__', value)
assert '__' not in svg
ET.fromstring(svg)
OUT.mkdir(exist_ok=True)
VIZ.mkdir(parents=True, exist_ok=True)
(OUT / "pelican-cycling.svg").write_text(svg)
fragment = (WORK / "pelican-preview-template.html").read_text().replace('__SVG__', svg.replace('width="1120" height="800"', 'style="display:block;width:100%;height:auto"', 1))
(VIZ / "pelican-cycling.html").write_text(fragment)
(WORK / "preview.html").write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>html,body{margin:0;background:#f8f3e8}body{display:grid;place-items:center;min-height:100vh}</style></head><body>' + fragment + '</body></html>')
print('SVG XML valid; standalone SMIL; no scripts, dependencies or external requests.')
print(f'Output: {OUT / "pelican-cycling.svg"} ({len(svg.encode()):,} bytes)')
