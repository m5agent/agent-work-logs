#!/usr/bin/env python3
"""Check huntson's 16-press real-touch table against the ghost distribution
and the proposed start rules. Pure arithmetic on the numbers posted in
m5stack/M5GFX#418; no device access.

Real table: raw x, raw y, first area, first intensity, peak area, peak intensity, held ms
Rows 1-16 exactly as posted (comment 2026-11-16T20:27:33Z).
"""

REAL = [
    # id, where, x, y, a_first, i_first, a_peak, i_peak, held_ms
    (1,  "mid",       394,  636, 11, 56, 14, 57,  481),
    (2,  "mid",       407,  661, 13, 43, 13, 48,  337),
    (3,  "mid",       422,  632,  9, 42, 13, 43,  411),
    (4,  "mid",       437,  611, 13, 43, 13, 43,  313),
    (5,  "mid",       437,  611, 11, 47, 11, 47,  265),
    (6,  "edge x~0",   40,  652,  4, 40,  4, 41,  169),
    (7,  "edge x~0",   35, 1066,  6, 36,  6, 36,  145),
    (8,  "mid firm",  395,  604, 20, 42, 31, 53, 1983),
    (9,  "mid firm",  423,  604, 17, 42, 26, 55, 2283),
    (10, "mid firm",  399,  598,  9, 43, 42, 61, 2185),
    (11, "edge x~0",   49, 1183,  5, 33,  6, 38,  169),
    (12, "edge x~0",   42, 1253,  3, 34,  8, 47, 2243),
    (13, "edge x~719", 683, 1211,  5, 37,  9, 60, 1993),
    (14, "edge x~719", 693,   52,  5, 37,  8, 66, 2041),
    (15, "edge x~0",   48,   44,  4, 43,  6, 60, 1873),
    (16, "edge x~0",   39, 1174,  5, 34,  8, 37,  169),
]

# Press 16's first *frame* was dropped by the area-only rule; the row above is
# the frame that survived. Posted as (x44, y1144, area35, intensity50).
REAL16_TRUE_FIRST = (44, 1144, 35, 50)

# Ghost population gathered in the thread: valid=1, x in {0,719}, 1-2 scans.
GHOST_AREA = [1, 32, 32, 32, 32, 28, 8, 16, 1, 1, 6, 6, 5, 4, 6]  # 1..32, incl. 28
GHOST_I = [10, 13, 13, 13, 14, 11, 11, 12, 13, 15, 12, 14, 11, 10, 13]  # 10..22 observed
GHOST_IMAX = 22   # reported max over all ghost frames
GHOST_AMAX = 32
REAL_IMIN_ALL = 26  # earlier 20-tap run, first-scan intensity 26-47 (gate >=25 active)

def main():
    print("== real table ==")
    print("first intensity: %d..%d   first area: %d..%d" % (
        min(r[5] for r in REAL), max(r[5] for r in REAL),
        min(r[4] for r in REAL), max(r[4] for r in REAL)))
    print("peak  intensity: %d..%d   peak  area: %d..%d" % (
        min(r[7] for r in REAL), max(r[7] for r in REAL),
        min(r[6] for r in REAL), max(r[6] for r in REAL)))
    print("held ms: %d..%d" % (min(r[8] for r in REAL), max(r[8] for r in REAL)))

    print("\n== gate margins (reject <= T-1, admit >= T) ==")
    print("   T | ghost max 22 | real min (all data) 26 | real min (this table) 33")
    for T in (23, 24, 25):
        print("  %2d |      %+2d     |            %+2d           |          %+2d" % (
            T, T - GHOST_IMAX, REAL_IMIN_ALL - T, min(r[5] for r in REAL) - T))

    print("\n== area-only start rule (area >= 30 drops) ==")
    dropped = [r[0] for r in REAL if r[4] >= 30]
    print("logged first frames dropped:", dropped or "none")
    print("press 16 true first frame area=%d -> dropped; table logs the next frame (area %d)" %
          (REAL16_TRUE_FIRST[2], 16 if False else 5))
    print("peak frames area>=30:", [r[0] for r in REAL if r[6] >= 30],
          "all with intensity", [r[7] for r in REAL if r[6] >= 30])

    print("\n== proposed rule: gate>=25 then (area>=30 and intensity<25) ==")
    unreachable = [(r[0], r[5], r[4]) for r in REAL if r[5] >= 25 and r[4] >= 30 and r[5] < 25]
    print("start frames where both clauses can fire:", unreachable or "none (dead clause)")
    print("ghost points with area>=30 and intensity<25: all of them" )
    print("ghost points with intensity>=25:", [i for i in GHOST_I if i >= 25] or "none observed")

    print("\n== rails ==")
    print("real min x: %d  real min 719-x: %d" % (
        min(r[2] for r in REAL), min(719 - r[2] for r in REAL)))
    print("real points at x in {0,719}:", [r[0] for r in REAL if r[2] in (0, 719)] or "none")
    print("ghost x values: 0 and 719 only (thread)")

    print("\n== survivor sample ==")
    print("floor of this table's first-intensity column is the gate, not the panel:")
    print("  press 16 true first intensity = %d, logged first = %d" %
          (REAL16_TRUE_FIRST[3], REAL[15][5]))
    print("  earlier run: 20 taps admitted at >=25, min 26 -> nothing below 25 can appear")

    print("\n== duration (not a safe rule) ==")
    print("real held ms min %d; ghost 1-2 scans (8.7 ms/frame) = 9-17 ms" %
          min(r[8] for r in REAL))
    print("but a 23 ms real tap was recorded earlier, so the classes overlap in principle")

if __name__ == "__main__":
    main()
