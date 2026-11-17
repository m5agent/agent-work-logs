#!/usr/bin/env python3
"""Issue #418 round 12: arithmetic over the reporter's gap-free idle run.

Inputs are the numbers in huntson's 2026-11-17T05:02:30Z comment
(issuecomment-6938977582). Nothing here is a measurement; this only re-derives
the rates, the significance figures, the register decode and the geometry of
the two pasted frames.
"""
import math

# ---------------------------------------------------------------- rates
print("== rates ==")
print("A: 15 bursts / 30 min      -> %.1f /h" % (15 * 2))
print("B:  2 bursts / 15 min      -> %.1f /h" % (2 * 4))
print("A+B pooled: 17 / 45 min    -> %.1f /h" % (17 * 60 / 45))
print("previous run: 164 / 329 min-> %.2f /h" % (164 * 60 / 329))

# ---------------------------------------------------------------- significance
print("\n== significance ==")
lam = 0.19
print("P(>=2 bursts | lam=0.19)          = %.4f"
      % (1 - math.exp(-lam) * (1 + lam)))
lam_b = 7.5  # A's 30/h re-scaled to 15 min
p_le2 = math.exp(-lam_b) * (1 + lam_b + lam_b ** 2 / 2)
print("P(<=2 bursts | lam=7.5, 15 min)   = %.4f   (B vs A rate)" % p_le2)

# 2x2: shape (rail|column) x gap (after|free).  rail 2/0, column 0/15
p_one = 1 / math.comb(17, 2)
print("Fisher exact, 2x2 (rail 2/0, col 0/15): one-tailed %.5f, two-tailed %.4f"
      % (p_one, 2 * p_one))
print("rail bursts per gap: 2/34 = %.3f (%.1f%%)" % (2 / 34, 100 * 2 / 34))

# ---------------------------------------------------------------- register decode
print("\n== chip registers 0x0005-0x0009 = 02 d0 05 00 0a ==")
max_x = 0x02D0
max_y = 0x0500
print("max x = %d, max y = %d, max touches = %d" % (max_x, max_y, 0x0A))
print("720/2 = %.1f   (0+719)/2 = %.1f   360-358 = %d   359.5-358 = %.1f"
      % (max_x / 2, (0 + 719) / 2, 360 - 358, 359.5 - 358))

# ---------------------------------------------------------------- geometry
print("\n== ghost x: 20 px lattice, x = 20k-1 ==")
xs = [0, 140, 179, 357, 358, 359, 538, 578, 719]
for x in xs:
    k = round((x + 1) / 20)
    print("  x=%3d  k=%2d  node=%3d  residual=%+d" % (x, k, 20 * k - 1, x - (20 * k - 1)))

print("\n== mirror pairs (k <-> 36-k), axis = sum/2 ==")
for a, b in [(0, 719), (140, 578), (179, 538)]:   # 357-359 is the self-mirrored seam
    print("  %3d + %3d = %3d   axis %.1f   vs 718: %+d" % (a, b, a + b, (a + b) / 2, a + b - 718))

print("\n== y against the same lattice (residual should be small if y is electrode-derived) ==")
y_c = [29, 179, 339, 797, 996, 1136, 1246, 418, 658]
y_r = [137, 359, 498, 638, 898, 1176, 533, 1136, 1246]
for name, ys in (("centre column", y_c), ("both rails", y_r)):
    res = [y - round(y / 20) * 20 for y in ys]
    print("  %-14s residuals %s  min %+d max %+d" % (name, res, min(res), max(res)))

print("\n== do real presses sit on the lattice by chance? ==")
real_x = [394, 407, 422, 437, 437, 40, 35, 395, 423, 399, 49, 42, 683, 693,
          48, 39, 384, 365, 399, 378, 367, 360, 360, 373, 373, 373, 319, 343, 49]
hits = [x for x in real_x if abs((x + 1) - 20 * round((x + 1) / 20)) <= 1]
print("  %d/%d real x within +-1 of 20k-1 (chance ~3/20 = %.0f%%, expected %.2f)"
      % (len(hits), len(real_x), 100 * 3 / 20, len(real_x) * 3 / 20))
print("  nearest real x to a rail: %d from x=0, %d from x=719"
      % (min(real_x), 719 - max(real_x)))

print("\n== burst persistence ==")
print("  17/17 bursts are two consecutive reads 24 ms apart -> state lasts >= 1 poll interval")
