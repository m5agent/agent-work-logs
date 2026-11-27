# Per-device browser results

Browser-WASM virtual-device validation. Admission covers the named fixed or stock paths. Each passing browser guest check confirms actual Worker disappearance after workbench Stop.

## Browser catalog

| Device | esp32sim browser admission | Browser default | Guest evidence or remaining limit | Live retest |
| --- | --- | --- | --- | --- |
| CoreS3 | PASS | esp32sim | Official display and touch examples and UIFlow2 factory boot. | — |
| Cardputer-ADV | PASS | esp32sim | 11 TCA8418 KeyboardI2C press and release pairs and 8 × 8 pixel checks. QEMU-WASM IRQ keyboard remains diagnostic. | — |
| Cardputer K132 | PASS | esp32sim | F12 count and matching RGB565 input frames. Same-fixture boot 1.12 vs 15.46 s. | — |
| AtomS3 | PASS | esp32sim | A key and 128 × 128 frame change. | — |
| AtomS3 Lite | PASS | esp32sim | Onboard RGB and key down/up. | — |
| Dial | PASS | esp32sim | Arduino touch and 3 encoder detents change the corresponding guest frame. | — |
| StickS3 | PASS | esp32sim | Matching A-key output frames and faster response. PM1 timing remains outside this comparison. | — |
| StopWatch | PASS | QEMU-WASM | 466 × 466 round frame and touch. Paired frame bytes differ. | — |
| StackChan | PARTIAL, admitted | QEMU-WASM | Display, three body-touch zones and joint positions pass. Later Y servo writes sometimes fail. | — |
| PaperDIY | PASS | QEMU-WASM | A key and e-paper refresh. Paired frame bytes differ. | — |
| PaperMono | PASS | QEMU-WASM | Touch and e-paper refresh. Paired frame bytes differ and QEMU-WASM input was faster. | — |
| PaperS3 | PASS | QEMU-WASM | GT911 touch and e-paper refresh. Paired frame bytes differ. | — |
| Atom Lite | PASS | esp32sim | Key down/up and onboard RGB sequence. | — |
| StickC | PASS | esp32sim | A-key count and 80 × 160 display. | — |
| StickC Plus | PASS | esp32sim | A-key count and 135 × 240 display. | — |
| StickC Plus SE | PASS | esp32sim | A-key count and 135 × 240 display. | — |
| NanoC6 | PASS | esp32sim | Official Arduino Button serial edges and stationary UIFlow2 RGB/REPL check. | — |
| AtomS3R | PASS | QEMU-WASM | ST7735S 128 × 128 and real button response with corrected PICO LGA56 eFuse. Paired frame bytes differ. | — |
| PaperColor | PASS | QEMU-WASM | Spectra6 paints and changes after input. Same frames on both engines. QEMU-WASM was faster. | — |
| Core2 | PASS | esp32sim | Matching display and touch frames, 8 MiB PSRAM including HIMEM page readbacks, and nonzero PCM microphone input. | — |
| StickC Plus2 | PASS | QEMU-WASM | 2 MiB PSRAM including allocation boundaries, A key and display. Paired frame bytes differ. | — |
| Atom Matrix | PASS | esp32sim | 25 matching LED values and key response. Asymmetric spatial order unverified. | — |
| Atom Matrix v1.1 | PASS | esp32sim | 25 matching LED values and key response. Asymmetric spatial order unverified. | — |
| StamPLC | PASS | esp32sim | Expander A-key test and matching 240 × 135 output. Browser exposes plc-key mappings for three keys. | — |
| Arduino Nesso N1 | PASS | esp32sim | External Flash eFuse, 135 × 240 SPI frame and real GT911 guest touch. | — |
| AtomS3R-CAM | PASS | esp32sim | Five distinct hashes from guest camera capture and matching pattern preview. | — |
| AtomS3R-M12 | PASS | esp32sim | Five distinct hashes from guest camera capture and matching pattern preview. | — |
| Atom VoiceS3R | PASS | esp32sim | Guest emits nonzero speaker PCM and reads 3158 nonzero microphone bytes after WAV injection. | — |
| AtomS3U | PASS | esp32sim | Real USER input changes onboard RGB. | — |
| Basic v2.7 | PASS | esp32sim | A, B and C edges at 4 and 16 MiB Flash. | — |
| Tab5 | PASS rev 0 | esp32sim | Stock UIFlow2 v2.5.3 reaches the GT911 launcher and opens ADC with the hash-verified C6 sidecar. Rev 3 stock unqualified. | — |
| M5Stick | PASS diagnostic | esp32sim | SH1107 OLED over SPI and GPIO button down/up. Stock cold start unqualified. | — |
| StickT2 | PASS diagnostic | esp32sim | ST7789 frame, A/B, encoder press and I²C rotary count. Stock cold start unqualified. | — |
| AtomU | FAIL, excluded | Unavailable | Separate Arduino and UIFlow2 guests identify the board and stop emitting the heartbeat. | — |
| Atom Echo | FAIL, excluded | Unavailable | Separate Arduino and UIFlow2 guests stop emitting the heartbeat. Classic Echo audio remains unqualified. | — |

## Reproduction

Build the source-pinned runtime and export the mixed workbench. Run `node platform/tests/test_public_esp32sim_board_guest.mjs` using `M5_BROWSER_SITE` and the exact fixture files. The Bash workflow `public-site.yml` emits the approved export and guest acceptance artifacts. The previous release remains an immutable rollback point.

## Live publication

Live publication remains pending. See the local browser receipts below.

Tab5 stock v2.5.3, v2.5.4 and v2.5.5 examined bootloaders declare a maximum P4 revision of 199. The GT911 launcher acceptance used v2.5.3 and P4 rev 0. Rev 3 stock remains unqualified.
