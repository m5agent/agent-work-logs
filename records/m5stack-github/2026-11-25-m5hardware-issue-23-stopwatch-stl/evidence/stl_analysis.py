#!/usr/bin/env python3
"""Reproducible geometry checks for Products/C152_StopWatch/Structures/StopWatch.stl.

Binary STL only, no third-party dependencies.

  curl -sSLO https://raw.githubusercontent.com/m5stack/M5_Hardware/067ddd8fa3cf17506dba4769e50237daf21359db/Products/C152_StopWatch/Structures/StopWatch.stl
  python3 stl_analysis.py StopWatch.stl

Coordinate convention of this model: STL X is the height axis (0 at the back),
Y/Z are the radial plane (r = hypot(Y,Z)).
"""
import struct, math, sys
from collections import defaultdict

path = sys.argv[1] if len(sys.argv) > 1 else "StopWatch.stl"
d = open(path, "rb").read()
n = struct.unpack("<I", d[80:84])[0]
assert len(d) == 84 + 50 * n, "not a binary STL or truncated file"
tris = []
for i in range(n):
    v = struct.unpack_from("<9f", d, 84 + 50 * i + 12)
    tris.append(((v[0], v[1], v[2]), (v[3], v[4], v[5]), (v[6], v[7], v[8])))

def rad(p): return math.hypot(p[1], p[2])

def bbox(ts):
    xs = [p[0] for t in ts for p in t]
    ys = [p[1] for t in ts for p in t]
    zs = [p[2] for t in ts for p in t]
    return (round(min(xs), 3), round(max(xs), 3), round(min(ys), 3),
            round(max(ys), 3), round(min(zs), 3), round(max(zs), 3))

print("header:", d[:80].replace(b"\x00", b" ").decode("latin1").strip())
print("triangles:", n, "bytes:", len(d))
print("global bbox X %.3f..%.3f Y %.3f..%.3f Z %.3f..%.3f" % bbox(tris))

# device copy sits at the origin; the second copy is displaced far in -Z
main = [t for t in tris if min(p[2] for p in t) > -30]
dup  = [t for t in tris if max(p[2] for p in t) < -30]
print("device group  tris=%d bbox X %.3f..%.3f Y %.3f..%.3f Z %.3f..%.3f" % ((len(main),) + bbox(main)))
print("displaced group tris=%d bbox X %.3f..%.3f Y %.3f..%.3f Z %.3f..%.3f" % ((len(dup),) + bbox(dup)))

top = [p for t in main for p in t if p[0] > 14.99]
print("highest surface X>14.99: %d verts, r %.3f..%.3f (dia %.2f..%.2f)"
      % (len(top), min(map(rad, top)), max(map(rad, top)), 2 * min(map(rad, top)), 2 * max(map(rad, top))))

seat = [p for t in main for p in t if abs(p[0] - 14.30) < 0.005]
print("seat plane X=14.30: r %.3f..%.3f (aperture dia %.2f, seat dia %.2f)"
      % (min(map(rad, seat)), max(map(rad, seat)), 2 * min(map(rad, seat)), 2 * max(map(rad, seat))))

for R in (23.60, 23.65, 23.69, 23.70):
    sel = [p[0] for t in main for p in t if rad(p) <= R]
    print("max X inside r<=%.2f : %.4f" % (R, max(sel)))

print("proposed glass: dia %.2f, bottom 14.30, top 15.50, thickness 1.20, protrusion 0.50"
      % (2 * 24.541))

# --- per-part matching of the displaced copy (vertex-welded island clustering) ---
parent = {}
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra
key = {}
for t in tris:
    ids = []
    for p in t:
        k = (round(p[0] * 1000), round(p[1] * 1000), round(p[2] * 1000))
        if k not in key:
            key[k] = len(key); parent[key[k]] = key[k]
        ids.append(key[k])
    union(ids[0], ids[1]); union(ids[1], ids[2])
islands = defaultdict(list)
for t in tris:
    k = (round(t[0][0] * 1000), round(t[0][1] * 1000), round(t[0][2] * 1000))
    islands[find(key[k])].append(t)
parts = sorted(islands.values(), key=len, reverse=True)
print("islands:", len(parts))
src = [p for p in parts if min(pt[2] for t in p for pt in t) > -30]
mir = [p for p in parts if max(pt[2] for t in p for pt in t) < -30]
for p in src:
    b = bbox(p)
    m = [q for q in mir if len(q) == len(p)]
    if m:
        mb = bbox(m[0])
        print("  part tris=%4d  dX=%.3f dY=%.3f dZ=%.3f" % (len(p), mb[0]-b[0], mb[2]-b[2], mb[4]-b[4]))
