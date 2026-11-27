# Browser-WASM board results

The static workbench loaded the pinned esp32sim WASM source build for every
passing device. The fixed UIFlow2 cases use the existing workbench example
composer and the same Flash SHA as the QEMU-WASM board profile. The board check
opens the reference example using the public controls, drives a browser input
and waits for application output. Chrome's CDP target list is sampled before
Stop and again before the browser context closes. The first Dial run failed the
color oracle despite placing the point. The corrected oracle compares the
expanded RGB565 value (132, 206, 239), and the repeat passed on the same export.

| Device | esp32sim qualification | Browser default in mixed export | Per-device observation or limit |
| --- | --- | --- | --- |
| CoreS3 | Existing | esp32sim | Prior published qualification |
| Cardputer-ADV | Existing | esp32sim | Prior published qualification |
| Cardputer K132 | Existing, rerun PASS | QEMU-WASM | F12 routed to GPIO0, guest count and 240 × 135 redraw. Full same-image keyboard comparison remains open |
| AtomS3 | PASS | esp32sim | A press and release, count=1, 128 × 128 redraw |
| AtomS3 Lite | PASS | esp32sim | A press and release, RGB 204060 → 40A020 → 204060 |
| AtomS3R | FAIL, withheld | QEMU-WASM | Guest button edges passed. Fixed frame did not redraw with either ST7735S or GC9107 |
| AtomS3U | PARTIAL, withheld | — | Arduino BtnA press, hold and release passed. Same-firmware RGB response remains unverified |
| Atom VoiceS3R | NOT RUN | — | No LCD in the board. Combined microphone/speaker or serial output gate pending |
| AtomS3R-CAM | NOT RUN | — | Camera output is not integrated in the public adapter |
| AtomS3R-M12 | NOT RUN | — | Same camera output gate as CAM, separate board and case required |
| StickS3 | PASS | QEMU-WASM | A press and release, count=1, 135 × 240 redraw. PM1 power path remains open |
| Dial | PASS | esp32sim | Touch example draws sampled cyan points on 240 × 240 panel. Rotary gesture equivalence remains open |
| StopWatch | PASS | QEMU-WASM | Touch, count=1 and 468 × 466 planar redraw. Different frame geometry from the existing QEMU 3D path |
| StamPLC | NOT RUN | QEMU-WASM | A/B/C live on the board IO expander. Current WASM receives GPIO button messages and does not expose the modeled PLC key operation |
| StackChan | PASS for display and touch | QEMU-WASM | One touch count and 320 × 240 redraw. Same fixture reports servo-error. Three body-touch zones are unqualified in this adapter |
| PaperColor | FAIL, withheld | QEMU-WASM | Fixed guest emitted begin and did not emit ready during the 35 s observation. Separate Arduino button run did not yield end-to-end display response |
| PaperDIY | PASS | QEMU-WASM | A press and release, one count and 540 × 960 e-paper redraw. Refresh-quality equivalence remains open |
| PaperMono | PASS | QEMU-WASM | Stock driver raw-point example, one touch count and 480 × 800 redraw. Refresh and greyscale equivalence remain open |
| PaperS3 | PASS | QEMU-WASM | GT911 touch, count=1 and 540 × 960 redraw. Refresh-quality equivalence remains open |
| Atom Lite | PASS | esp32sim | Classic ROM boot, A press and release, RGB 204060 → 40A020 → 204060 |
| Atom Matrix | NOT RUN | QEMU-WASM | 25-LED workbench output mapping and case still need verification |
| Atom Matrix v1.1 | NOT RUN | QEMU-WASM | 25-LED output mapping and independent v1.1 case pending |
| Atom Echo | NOT RUN | — | Prior stock M5Things import failure requires a different verified guest example |
| AtomU | NOT RUN | — | Prior stock M5Things import failure requires a different verified guest example |
| Basic v2.7 | NOT RUN | — | Separate flash variants and same-guest three-button/display acceptance pending |
| Core2 | NOT RUN | QEMU-WASM | Catalog models 8 MiB PSRAM. Pinned classic WASM only supports 0 or 4 MiB. Both PMIC variants require their own qualification |
| StickC | PASS | esp32sim | Classic ROM boot, A press and release, 80 × 160 redraw |
| StickC Plus | PASS | esp32sim | Classic ROM boot, A press and release, 135 × 240 redraw |
| StickC Plus SE | PASS | esp32sim | Classic ROM boot, A press and release, 135 × 240 redraw |
| StickC Plus2 | NOT RUN | QEMU-WASM | Catalog 2 MiB PSRAM is outside the pinned classic WASM 0/4 MiB options |
| M5Stick | NOT RUN | — | Factory image OLED and GPIO35 behavior have no browser receipt |
| M5StickT2 | NOT RUN | — | Factory image, its I2C encoder and board controls have no browser receipt |
| NanoC6 | PASS | esp32sim | Exact Arduino press and release markers. Stock control observed RGB 00007F → 0000FF and a REPL with one Worker, zero after Stop |
| Arduino Nesso N1 | FAIL, withheld | — | C6 ROM booted both images. Neither factory launcher nor touch example yielded a usable frame during the bounded test |
| Tab5 | NOT RUN | — | P4 revision selection and ESP-Hosted sidecar loader pending |

Caps and external electrical, RF, audio or optical behavior were outside this
validation. Browser evidence does not assert Device Service behavior.

## ROM and Tab5 assets

The SHA-256 of the Espressif ELF archive was
`caa463d3cbef2430a5a35847c1d9f2f152403b17a802050927ff60c8da54fe46`.
The S3 rev 0, classic rev 300, C6 rev 0 and both P4 ELFs are in release 20260528.
Espressif applies Apache-2.0 to these object files. The workbench release stages
only the exact admitted S3, classic and C6 ELFs and retains source and license
records. The merge layouts preserve the 0x8000 partition table and accept
bootloaders at 0x1000 for classic ESP32 and 0x0 for S3 and C6.
[Release](https://github.com/espressif/esp-rom-elfs/releases/tag/20260528) ·
[Espressif object-license explanation](https://github.com/espressif/esp-rom-elfs#copyrights-and-license)

Tab5's board factory is bound to P4 rev < 3 in the pinned WASM. The generic
rev 3 factory lacks the Tab5 board and panel configuration. WASM has C6
co-processor load kinds. The approved native C6 sidecar archive contains four
ESP-Hosted MCU 2.0.13 SDIO build outputs and includes its notices and license
files. A browser loader needs hash-verified segment and ROM routes plus an
equivalent board revision selection and browser guest acceptance. The native
archive is identified by its lock and is outside this Pages export.
[WASM factory](https://github.com/m5agent/esp32sim/blob/4e257b6be8ee0ed706c2e509d8f31ef7472a424b/wasm/src/lib.rs#L139) ·
[ESP-Hosted source](https://components.espressif.com/components/espressif/esp_hosted/versions/2.0.13) ·
[ESP-IDF licenses](https://docs.espressif.com/projects/esp-idf/en/v5.4.2/esp32c6/COPYRIGHT.html)

## Hosted UI-04

In the retained hosted ADV run, 30 trials completed before Q failed. Both
trusted DOM edges reached QMP and were accepted, one callback reported press,
and public API heartbeat state continued to hold Q. The run used the QEMU
runtime with the TCA8418 CFG0 W1C patch. Normal guest/Worker exit passed. The
report distinguishes the stalled guest input from looser timeouts and lacks
controller traces to locate the remaining interrupt loss. No hosted timing
workaround or QEMU runtime alteration is credited as a fix.
[Hosted run](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45942728417)

## Reproduction

1. Bootstrap the pinned esp32sim browser runtime with
   `python3 platform/tools/bootstrap_browser_runtime.py --fetch-rom`.
2. Export with `build_public_site.py --browser-runtime` and the reviewed
   Xtensa, C61 and LittleFS directories. Use the project base path for a Pages
   mirror.
3. Serve the export on a dedicated local port. Set `M5_BROWSER_SITE` to its
   workbench URL. Run
   `node platform/tests/test_public_esp32sim_board_guest.mjs` for the fixed
   UIFlow2 cases. Use explicit device arguments and the matching locked BINs
   for Dial and NanoC6.
4. Run the existing QEMU-WASM gate independently. A browser build or a
   QEMU-WASM pass alone does not qualify an esp32sim board.

Arduino fixtures came from documentation revision
`7219cc9286c39b463da84053deee40bc234625db`, Arduino CLI 1.3.1,
`m5stack:esp32@3.2.5`, M5GFX
`28d47949bdc84f30881623476f555398e2194313`, M5Unified
`96576a14247ddc935149145aa6b51943464120f1`, and the core's esptool
5.0.dev1. Dial is `m5stack:esp32:m5stack_dial` (touch source SHA-256
`598ebd53f6b129fec13def9b5229513bde95cd5266f19477d5f847b1f7bb194c`).
NanoC6 is `m5stack:esp32:m5stack_nano_c6` (button source SHA-256
`0a41537bcae3700b14e28cca8a8b73f9fe5ac2cd3e852e43a2d4138d0203e74d`).
The local merged images and their normalized Flash hashes are in the summary.
[Dial Touch](https://docs.m5stack.com/en/arduino/m5dial/touch) ·
[NanoC6 Button](https://docs.m5stack.com/en/arduino/m5nanoc6/button)

## Local QEMU-WASM gate

The serial full gate stopped at the StopWatch editor after nine passes. Its
Core 1 raised LoadStorePIFAddrError before application readiness. There were
62 remaining cases. The isolated retry passed 65 checks on the same export,
including reset, guest framebuffer and normal Worker cleanup. The original
failure and the isolated retry have separate identities in run.json.
