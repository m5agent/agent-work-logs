# Final fork pin paired documentation matrix

2026-11-27. Virtual-device validation.
The same service oracles were executed against 56 built Arduino examples, twice per runtime.
This table includes the whole Device Service catalog. Planned examples outside the service
oracle selection, and original docs or library defects, retain their source classification.
The standalone fork, stock UIFlow2, review jobs and integration fixtures have separate scope.

| Device | Planned Arduino cases | Cases with paired service evidence | esp32sim P/F/M | QEMU P/F/M | Candidate default |
| --- | ---: | ---: | --- | --- | --- |
| atom-echo | 3 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim |
| atom-echos3r | 5 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| atom-lite | 5 | 4 | 4 / 0 / 0 | 4 / 0 / 0 | esp32sim |
| atom-matrix | 5 | 4 | 4 / 0 / 0 | 4 / 0 / 0 | esp32sim |
| atom-matrix-v11 | 5 | 4 | 4 / 0 / 0 | 4 / 0 / 0 | esp32sim |
| atoms3 | 5 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU |
| atoms3-lite | 3 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| atoms3r | 5 | 2 | 2 / 0 / 0 | 0 / 2 / 0 | QEMU |
| atoms3r-cam | 1 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| atoms3r-m12 | 1 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| atoms3u | 5 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| atomu | 0 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim |
| basic-v27 | 9 | 2 | 2 / 0 / 0 | 0 / 2 / 0 | QEMU |
| cardputer | 10 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | esp32sim |
| cardputer-adv | 11 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim |
| cardputer-zero | — | 0 | 0 / 0 / 0 | 0 / 0 / 0 | external Linux |
| core2 | 14 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | esp32sim |
| cores3 | 15 | 6 | 6 / 0 / 0 | 5 / 1 / 0 | esp32sim |
| dial | 10 | 3 | 3 / 0 / 0 | 3 / 0 / 0 | esp32sim |
| m5stick | 0 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim |
| nanoc6 | 15 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| nesso-n1 | 12 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| papercolor | 16 | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU |
| paperdiy | 6 | 1 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU |
| papermono | 26 | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU |
| papers3 | 9 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU |
| stackchan | 26 | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU |
| stamplc | 13 | 1 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU |
| stickc | 44 | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU |
| stickc-plus | 29 | 11 | 11 / 0 / 0 | 11 / 0 / 0 | QEMU |
| stickc-plus-se | 8 | 2 | 2 / 0 / 0 | 0 / 2 / 0 | QEMU |
| stickc-plus2 | 11 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU |
| sticks3 | 15 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU |
| stickt2 | 0 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim |
| stopwatch | 18 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU |
| tab5 | — | 0 | 0 / 0 / 0 | 0 / 0 / 0 | conditional Tab5 |

Totals are esp32sim 56 PASS, QEMU 47 PASS and 9 FAIL. No case in this selected
matrix was mixed. The nine QEMU failures are CoreS3 IMU, Basic v2.7 display and
long text scroll, PaperDIY display-1, both selected StickC Plus SE cases, both
selected AtomS3R cases and StamPLC quickstart display. The Basic and AtomS3R
exceptions bind to display geometry inside the original sketch loops.
Further per-device consumer and stock limitations are recorded separately.

- [Trial receipts 1–40](evidence/final-pin-doc-trials-1.json)
- [Trial receipts 41–80](evidence/final-pin-doc-trials-2.json)
- [Trial receipts 81–120](evidence/final-pin-doc-trials-3.json)
- [Trial receipts 121–160](evidence/final-pin-doc-trials-4.json)
- [Trial receipts 161–200](evidence/final-pin-doc-trials-5.json)
- [Trial receipts 201–224](evidence/final-pin-doc-trials-6.json)
