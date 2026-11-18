# 65 s grid arithmetic over huntson's two unattended censuses in m5stack/M5GFX#418.
# Input: his episode start times (run 6, 2026-11-18T01:38Z; run 5, 2026-11-17T23:17Z).
# No runtime data; checks period, phase, tick indices and poll-phase clustering.
eps6 = [464.354, 659.356, 789.357, 984.363, 1374.354, 2349.353, 2999.356, 3129.355]
eps5 = [724.354, 1374.350, 1699.348, 1894.349, 1439.349, 2479.355, 2544.351]
gaps6 = [21.822, 22.505, 22.216, 22.431, 22.604, 21.931, 22.213, 22.690]  # ms, call end -> first read
calls6 = [148.220, 148.534, 148.826, 149.612, 148.438, 147.112, 148.830, 148.352]  # ms
off5 = 676.420

print("run6 mod65 ms:", [round((t % 65 - 9.35) * 1000, 1) for t in eps6])
print("run5 mod65 ms:", [round((t % 65 - 9.35) * 1000, 1) for t in eps5])
print("run6 ticks:", [round((t - 9.35) / 65) for t in eps6])
print("run5 ticks:", [round((t - 9.35) / 65) for t in eps5])
print("ticks available run6/run5:", int((3616 - 9.35) // 65) + 1, int((3771 - 9.35) // 65) + 1)
print("run6 rate: 8/%d = %.1f%%" % (int((3616 - 9.35) // 65) + 1, 800.0 / (int((3616 - 9.35) // 65) + 1)))
print("run5 rate: 7/%d = %.1f%%" % (int((3771 - 9.35) // 65) + 1, 700.0 / (int((3771 - 9.35) // 65) + 1)))
print("off-grid run5: %.3f mod65" % (off5 % 65))
print("call dur min/max/spread%%: %.3f %.3f %.1f" % (min(calls6), max(calls6), (max(calls6) - min(calls6)) / min(calls6) * 100))
print("call end mod 23ms:", [round(((t - g / 1000.0) % 0.023) * 1000, 2) for t, g in zip(eps6, gaps6)])
print("65536ms drift over 3616s: %.1f s" % (3616 / 65.536 * 0.536))
print("65000 mod 23 =", 65000 % 23, "ms")
print("keepalive spacing: %.1f s" % (3616 / 256.0))
