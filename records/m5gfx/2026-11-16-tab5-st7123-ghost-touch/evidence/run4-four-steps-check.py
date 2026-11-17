#!/usr/bin/env python3
"""Round-14 checks for m5stack/M5GFX#418 (author's four follow-up steps).

Inputs are the author's reported counts only (no hardware, no device):
  A: 226 forced gaps, 1 burst within 100 ms, 3 columns at 424/605/668 ms, 9 later
  step 2: 7 quiet fast-read cells (500 ms at 3 ms), 0 points, 0 ghosts after
  step 3: 42 episodes at the 24 ms poll: 40 x 2 reads, 1 x 3, 1 x 4, 0 x 1
  step 4: single-edge frames 0 at 24 ms (4 reads after one fast window),
          85 in fast windows; both-edge 21 at 24 ms, 142 in fast windows
  B (round 13): first frame byte-identical for 21-30 ms (8-11 reads at 3 ms)
"""

from math import comb, exp


def fisher_one_tailed(a, b, c, d):
    """P(table at least as extreme) for [[a,b],[c,d]] enrichment of a."""
    n = a + b + c + d
    r1 = a + b
    c1 = a + c
    return sum(
        comb(r1, k) * comb(n - r1, c1 - k)
        for k in range(a, min(r1, c1) + 1)
    ) / comb(n, c1)


def binom_cdf(k, n, p):
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def binom_upper(k, n, alpha):
    """One-sided (1-alpha) upper bound on p, exact (Clopper-Pearson tail)."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if binom_cdf(k, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


P = 24.6  # mean poll interval, ms (author: 78,365 reads / 30 min)


def p_single(T):
    """P(exactly one poll inside a state of length T), conditional on detection.

    Free phase, poll spacing P.  N=0 only when T<P.
    For P<T<2P: P(N=1)=(2P-T)/P, P(N=2)=(T-P)/P.
    """
    if T < P:
        return 1.0  # N=1 whenever detected
    if T < 2 * P:
        return (2 * P - T) / P
    return 0.0


print("== step 3: reads per episode vs a free-phase 24-33 ms report ==")
for T in (24, 27, 30, 33, 40, 47, 49):
    p1 = p_single(T)
    p_zero_single = (1 - p1) ** 42
    print(f"  T={T:>2} ms  P(1 read|seen)={p1:5.3f}  P(0 of 42 single)={p_zero_single:.2e}")
# T needed so that P(0 of 42 single) >= 0.05
print("  T where 0/42 stops being surprising (P>=0.05): %.1f ms (%.2f poll intervals)"
      % (P * (2 - (1 - 0.05 ** (1 / 42))), 2 - (1 - 0.05 ** (1 / 42))))
print("  observed histogram 40/1/1 vs expected if T=33 ms:",
      [round(42 * v, 2) for v in ((2 * P - 33) / P, (33 - P) / P, 0.0)])

print()
print("== step 2: quiet fast-read cell ==")
print("  cell protocol: 7*(0.5+10) = %.1f s = %.1f min of the 7.7 min session"
      % (7 * 10.5, 7 * 10.5 / 60))
lam = 7 * (7.7 / 50)  # 7 free-running columns in run A's 50 min
print("  expected column bursts in 7.7 min at 8.4/h = %.2f, P(0) = %.2f" % (lam, exp(-lam)))
print("  0/7 upper bound on a fast-read-only burst rate: %.0f%% per cell"
      % (100 * binom_upper(0, 7, 0.05)))
print("  Fisher 6/7 (fast after burst) vs 0/7 (fast, quiet cell) p = %.4f"
      % fisher_one_tailed(6, 1, 0, 7))
print("  Fisher 6/7 vs 0/3 (24 ms controls)                   p = %.4f"
      % fisher_one_tailed(6, 1, 0, 3))
print("  Fisher 6/7 vs 1/3 (if 'once in a control' was one)   p = %.4f"
      % fisher_one_tailed(6, 1, 1, 2))
print("  Fisher 6/7 vs 0/10 (all no-burst fast arms)          p = %.5f"
      % fisher_one_tailed(6, 1, 0, 10))

print()
print("== step 1 (A): latency re-score ==")
rate_col = 9.08  # /h, 7 free-running columns in 2774 s
rate_rail = 2.60  # /h, 2 free-running rails in 2774 s
win_h = 226 * 0.110 / 3600
print("  110 ms windows over 226 gaps: any-burst mu = %.3f, P(>=1) = %.3f"
      % ((rate_col + rate_rail) * win_h, 1 - exp(-(rate_col + rate_rail) * win_h)))
print("  rail only mu = %.3f, P(>=1) = %.3f (post-hoc on the event's type)"
      % (rate_rail * win_h, 1 - exp(-rate_rail * win_h)))
print("  1/226 = %.2f%%, one-sided 95%% upper = %.2f%% per gap"
      % (100 / 226, 100 * binom_upper(1, 226, 0.05)))

print()
print("== step 4: shape counts ==")
print("  both-edge at 24 ms: 21 frames; single-edge at 24 ms: 0 (+4 reads after one fast window)")
print("  fast windows: single-edge 85 frames in 4 episodes (intensity 10-22), both-edge 142")
print("  opening table: 61 of 97 ghosts carried a point at x=0, 2 points/frame usual,")
print("  only 2 logged frames held one point on each long edge -> point count != frame class")
