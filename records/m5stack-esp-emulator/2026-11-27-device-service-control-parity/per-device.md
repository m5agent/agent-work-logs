# Per-device results

Virtual-device validation across the tested milestones. Counts are paired Arduino cases
in PASS / FAIL / MIXED / PARTIAL order. Unexecuted cases are outside the counts.
The planned column covers the archived input plan and the separate CoreS3 and
Cardputer-ADV suites. NO PLAN means this inventory did not bind a docs suite.
HTTP controls apply only to the board and operation tested.

| Device | Planned | esp32sim | QEMU | Existing default | Observed result or gate |
| --- | ---: | --- | --- | --- | --- |
| atom-echo | 3 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Three planned example builds have pinned source/library defects. |
| atom-echos3r | 5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atom-lite | 5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atom-matrix | 5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atom-matrix-v11 | 5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atoms3 | 5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atoms3-lite | 3 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atoms3r | 5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atoms3r-cam | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | QEMU passed the camera fixture twice. esp32sim cannot enable timed distinct frames through the existing camera control. |
| atoms3r-m12 | 1 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | QEMU passed the camera fixture twice. esp32sim cannot enable timed distinct frames through the existing camera control. |
| atoms3u | 5 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| atomu | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| basic-v27 | 9 | 0 / 0 / 0 / 2 | 0 / 2 / 0 / 0 | QEMU | QEMU missed the tested Arduino display/scroll predicates. |
| cardputer | 10 | 0 / 0 / 0 / 2 | 0 / 0 / 0 / 2 | QEMU | SPI read delivery counters passed on the candidate. Reviewer jobs pending. |
| cardputer-adv | 11 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | esp32sim | SPI read delivery counters passed on the candidate. Reviewer jobs pending. |
| cardputer-zero | NO PLAN | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | External Linux | Separate Linux ARM64 target with no esp32sim board. |
| core2 | 14 | 0 / 0 / 0 / 2 | 0 / 0 / 0 / 2 | QEMU | Arduino frames met predicates on both. Stock observations are separate. |
| cores3 | 15 | 0 / 0 / 0 / 3 | 0 / 0 / 0 / 3 | esp32sim | Stock and REPL fixture passed on both. VFS autostart negative preserved. |
| dial | 10 | 0 / 0 / 0 / 2 | 0 / 0 / 0 / 2 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| m5stick | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | esp32sim | Native-only Device Service path, with no QEMU lease. |
| nanoc6 | 15 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| nesso-n1 | 12 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| papercolor | 16 | 0 / 0 / 0 / 1 | 0 / 0 / 0 / 1 | QEMU | Both palettes matched. QEMU was faster in the observed refresh window. |
| paperdiy | 6 | 0 / 0 / 0 / 1 | 0 / 1 / 0 / 0 | QEMU | Preboot eject and write stamps passed. Arduino swatch oracle favored esp32sim. |
| papermono | 26 | 0 / 0 / 0 / 1 | 0 / 0 / 0 / 1 | QEMU | Touch fixture passed twice on both after waiting for the initial UI. |
| papers3 | 9 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| stackchan | 26 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| stamplc | 13 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| stickc | 44 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| stickc-plus | 29 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| stickc-plus-se | 8 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| stickc-plus2 | 11 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| sticks3 | 15 | 0 / 0 / 0 / 2 | 0 / 0 / 0 / 2 | QEMU | Full suite and reviewer endpoint coverage remain unverified. |
| stickt2 | 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | esp32sim | Native-only Device Service path, with no QEMU lease. |
| stopwatch | 18 | 0 / 0 / 0 / 2 | 0 / 0 / 0 / 2 | QEMU | Corrected 466×466 geometry and touch passed on both. |
| tab5 | NO PLAN | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | esp-emu / qualified esp32sim | Existing firmware/panel routing. P4 and reviewer jobs need exact qualification. |
