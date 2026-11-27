# Per-device behavioral comparison

Virtual-device validation through Device Service. Counts cover the adapted Arduino display-frame oracles and checked-in UIFlow2 device-matrix fixtures. Each paired result represents two leases on each runtime. A case passes only when both verdicts pass. A changed verdict is counted as mixed. Stock observations are retained separately as PARTIAL. Stable case verdicts do not establish byte-identical dynamic frames or timing.

| Device | esp32sim pass / fail / mixed | QEMU pass / fail / mixed | Default | Decision or remaining work |
| --- | --- | --- | --- | --- |
| atom-echo | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | GitHub stock M5Things launcher defect excluded. Paired fixture still needs matching microphone and Grove stimuli. |
| atom-echos3r | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atom-lite | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atom-matrix | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atom-matrix-v11 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atoms3 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atoms3-lite | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atoms3r | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atoms3r-cam | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atoms3r-m12 | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atoms3u | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| atomu | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | GitHub stock M5Things launcher defect excluded. esp32sim passed the composed device matrix twice. Stock REPL inputs and microphone oracle are pending. |
| basic-v27 | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| cardputer | 2 / 0 / 0 | 2 / 0 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| cardputer-adv | 1 / 0 / 0 | 0 / 1 / 0 | esp32sim | Full docs, stock and peripheral fixture oracle coverage is pending. |
| cardputer-zero | — | — | External Linux | External Linux runtime. |
| core2 | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| cores3 | 0 / 1 / 0 | 0 / 1 / 0 | esp32sim | Full docs, stock and peripheral fixture oracle coverage is pending. |
| dial | 3 / 0 / 0 | 2 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| m5stick | — | — | esp32sim | No QEMU Service lease. Two omitted-runtime factory runs read MPU9250 ID 0x71. Factory UI remains partial. |
| nanoc6 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| nesso-n1 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| papercolor | 0 / 2 / 0 | 1 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| paperdiy | 1 / 1 / 0 | 0 / 2 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| papermono | 1 / 1 / 0 | 2 / 0 / 0 | QEMU | UIFlow2 device matrix. Hold (240,650) for 1 s. QEMU changed the frame and produced black at (440,30). esp32sim stayed white at that pixel. |
| papers3 | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| stackchan | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| stamplc | 0 / 1 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| stickc | 12 / 0 / 0 | 11 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| stickc-plus | 12 / 0 / 0 | 11 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| stickc-plus-se | 1 / 0 / 0 | 1 / 0 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| stickc-plus2 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| sticks3 | 2 / 1 / 0 | 2 / 1 / 0 | QEMU | Full docs, stock and peripheral fixture oracle coverage is pending. |
| stickt2 | — | — | esp32sim | No QEMU Service lease. Two omitted-runtime factory runs printed M5StickC initializing...OK. Full thermal UI remains partial. |
| stopwatch | 2 / 1 / 0 | 3 / 0 / 0 | QEMU | UIFlow2 device matrix. Both reached green at (233,233). QEMU exported 466×466 and esp32sim exported 468×466. |
| tab5 | — | — | esp-emu / qualified esp32sim | Previously qualified firmware/panel selection. Stock QEMU sample on the original isolated service lacked the legacy C6 co-processor file. |

The case-level checks, exact firmware hashes, frame outcomes and evidence ZIP hashes are in [virtual-device summary](evidence/virtual-device-summary.json). The two power-off cases and radio pair outcomes are recorded separately in the same file.

Candidate cases bound from app start through teardown cover the tested route only. Additional controller telemetry and guest-time checkpoints required by several fork checkers were unavailable through the same typed API. The test used comparable behavior predicates for the sampled displays, such as color count, drawing bounds, changed pixels or palette and swatch order.
