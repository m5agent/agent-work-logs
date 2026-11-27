# Per-device documentation replay on the merged fork

2026-11-27. Virtual-device validation.
Each selected firmware ran twice on each runtime. The counts use the latest paired result
for each case and include the firmware and evidence SHA in the companion JSON.
Status order is PASS / FAIL / MIXED / PARTIAL / ERROR. PARTIAL means that the
visual or control predicate passed and the full fork oracle still has conditions to verify.
The unselected column covers the local input plan and the two external suites. Known
build and firmware defects retain their prior classification. Tab5 uses its separate archive.

| Device | Planned | Selected | Unselected | QEMU | esp32sim | Live default |
| --- | ---: | ---: | ---: | --- | --- | --- |
| atom-echo | 3 | 0 | 3 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atom-echos3r | 5 | 0 | 5 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atom-lite | 5 | 0 | 5 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atom-matrix | 5 | 0 | 5 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atom-matrix-v11 | 5 | 0 | 5 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atoms3 | 5 | 2 | 3 | 0 / 0 / 0 / 2 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| atoms3-lite | 3 | 0 | 3 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atoms3r | 5 | 2 | 3 | 0 / 2 / 0 / 0 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| atoms3r-cam | 1 | 0 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atoms3r-m12 | 1 | 0 | 1 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atoms3u | 5 | 0 | 5 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| atomu | 0 | 0 | 0 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| basic-v27 | 9 | 2 | 7 | 0 / 2 / 0 / 0 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| cardputer | 10 | 2 | 8 | 0 / 0 / 0 / 2 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| cardputer-adv | 11 | 0 | 11 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | esp32sim |
| cardputer-zero | Separate | 0 | — | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | Linux |
| core2 | 14 | 2 | 12 | 0 / 0 / 0 / 2 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| cores3 | 15 | 4 | 11 | 0 / 0 / 0 / 4 / 0 | 0 / 0 / 0 / 4 / 0 | esp32sim |
| dial | 10 | 3 | 7 | 0 / 0 / 1 / 2 / 0 | 0 / 0 / 0 / 3 / 0 | QEMU |
| m5stick | 0 | 0 | 0 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | esp32sim |
| nanoc6 | 15 | 0 | 15 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| nesso-n1 | 12 | 0 | 12 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| papercolor | 16 | 1 | 15 | 0 / 0 / 0 / 1 / 0 | 0 / 0 / 0 / 1 / 0 | QEMU |
| paperdiy | 6 | 1 | 5 | 0 / 1 / 0 / 0 / 0 | 0 / 0 / 0 / 1 / 0 | QEMU |
| papermono | 26 | 1 | 25 | 0 / 0 / 0 / 1 / 0 | 0 / 0 / 0 / 1 / 0 | QEMU |
| papers3 | 9 | 0 | 9 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | QEMU |
| stackchan | 26 | 1 | 25 | 0 / 0 / 0 / 1 / 0 | 0 / 0 / 0 / 1 / 0 | QEMU |
| stamplc | 13 | 1 | 12 | 0 / 1 / 0 / 0 / 0 | 0 / 0 / 0 / 1 / 0 | QEMU |
| stickc | 44 | 1 | 43 | 0 / 0 / 0 / 1 / 0 | 0 / 0 / 0 / 1 / 0 | QEMU |
| stickc-plus | 29 | 11 | 18 | 0 / 0 / 0 / 11 / 0 | 0 / 0 / 0 / 11 / 0 | QEMU |
| stickc-plus-se | 8 | 2 | 6 | 0 / 2 / 0 / 0 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| stickc-plus2 | 11 | 2 | 9 | 0 / 0 / 0 / 2 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| sticks3 | 15 | 2 | 13 | 0 / 0 / 0 / 2 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| stickt2 | 0 | 0 | 0 | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | esp32sim |
| stopwatch | 18 | 2 | 16 | 0 / 0 / 0 / 2 / 0 | 0 / 0 / 0 / 2 / 0 | QEMU |
| tab5 | Separate | 0 | — | 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 | Firmware/panel dependent |

Basic v2.7 and AtomS3R document display images reached the caller loop under QEMU and
raised IntegerDivideByZero. The exact ELF resolved the caller to the range calculation
that uses the display geometry. The candidate generated the documented visual output.
No full-catalog parity or deployment claim follows from this coverage.

- [Trial results esp32sim-1](evidence/merged-doc-oracle-trials-esp32sim-1.json)
- [Trial results esp32sim-2](evidence/merged-doc-oracle-trials-esp32sim-2.json)
- [Trial results esp32sim-3](evidence/merged-doc-oracle-trials-esp32sim-3.json)
- [Trial results qemu-1](evidence/merged-doc-oracle-trials-qemu-1.json)
- [Trial results qemu-2](evidence/merged-doc-oracle-trials-qemu-2.json)
- [Trial results qemu-3](evidence/merged-doc-oracle-trials-qemu-3.json)
