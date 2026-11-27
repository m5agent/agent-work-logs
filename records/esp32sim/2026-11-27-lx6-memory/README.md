# Classic ESP32 exact memory capacities

- Date 2026-11-27
- Result PASS for native virtual-device validation
- Work type code change
- Source [esp32sim memory milestone](https://github.com/m5agent/esp32sim/commit/bd2dcb7e14d25baede0946a5205ced6b2c123be3)
- Environment classic ECO3 ROM with a bare ESP32 model and an ESP-IDF v6.1 dual-core fixture

Both native guests booted through the ROM and read back the last word of 16 MiB Flash. The 2 MiB build measured 2,097,152 physical bytes and checked both ends of a 2,064,384-byte allocation. The 8 MiB build remapped one HIMEM slot to three physical pages and read distinct patterns back from all three.

[Report](report.md) · [Artifact identity](run.json) · [Serial markers](evidence/markers-summary.txt)

Board-specific stock firmware, browser admission and physical memory timing are outside this run.
