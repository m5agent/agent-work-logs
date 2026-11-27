# Device Service parity in esp32sim

The fork implements a 466×466 StopWatch export, Flash snapshots, model-state sampling, runtime SD media presence, and Wi-Fi fault controls. The native service socket preserves its existing startup handshake and adds named operations. Coverage below is virtual-device validation.

## Board parity

- **StopWatch** — Controller columns 6 through 471 form the visible aperture. Firmware can continue sending a 468-column window. The first two nonempty baseline frames, cropped to that aperture, match the candidate bytes exactly. The composed UIFlow2 frame is 466×466 and the center turns green on touch. The Arduino replay passed 17 cases. The documented M5PM1/IOE1 example discrepancy remains. Stock home, touch response and USB REPL passed.
- **PaperMono** — The one-second hold during startup drove GPIO4 low and high, while the same guest was still in synchronous drawing. No touch report was sampled during that interval. A hold at guest 15 seconds produced two reads of controller register 0x02, with coordinates (240,650), and black at (440,30) by guest 24.36 seconds. The trace follows the FT5x06 report through I2C and the SSD1677 refresh count. A caller must wait for the complete application frame and allow the redraw to finish.
- **PaperColor** — The six-color Arduino frame arrived at guest 15.84 seconds and wall 15.87 seconds. GPIO11 remained low during refresh, and the prior frame remained visible until the first refresh completed. The nominal 15-second model interval fits the published 15–30 second display specification. The model interval remains 15 seconds. [M5Stack PaperColor specification](https://docs.m5stack.com/en/core/PaperColor)

## Socket operations

- `flash-snapshot` exported 16 MiB from a running PaperMono guest. The guest wrote and read a new NVS key through USB CDC. The Flash snapshot changed, the key appeared in the new bytes, and `flash-stop` exited successfully with the same final bytes.
- `state-snapshot`, `state-get`, `state-set`, `checkpoint` and `controller-report` expose state at a scheduler boundary. The PaperMono trace sampled the panel controller, FT5x06 status reads and cycle clock through this interface.
- `sd-media` and `--sd-ejected` let a prepared card start absent and be reinserted. The PaperDIY guest reported initialization failure with GPIO48 high. After insertion and guest reset, GPIO48 was low and the guest received completed SPI response blocks. Ejection cleared the read observation counts and advanced the generation. The SPI unit test additionally covers CMD18, an out-of-range read, early CS deassertion and the final CRC byte.
- Restricted and diagnostic STA joined the virtual WPA2 AP and acquired a DHCP lease. Restricted startup refused host port forwarding. Link and radio faults returned distinct states. Receive delivery stopped while radio was down. The SoftAP guest reported a joined virtual station and its DHCP lease.

The [control protocol](https://github.com/m5agent/esp32sim/blob/9eeb9a61e64cd3d3de6e4262fac13b8a3dc2f34d/docs/control-protocol.md) details the command and path contracts. Wi-Fi fault operations apply to SoCs with a direct modeled Wi-Fi link. Tab5's ESP-Hosted coprocessor has the spawn-time CLI networking modes and lacks direct fault controls on the P4 socket.

## Regression

Runtime suites ran on `a6216b68abda3af76f6f491f940fbf0e4e8a42f7`. The two subsequent commits scope a Flash output file lifetime for the WASM lint and update StopWatch integration assertions. The Flash read/write/stop replay and 2,041-test Rust suite ran on 441330fb. The focused camera and classic I2C replays below cover the later follow-up.

| Suite | Result |
| --- | --- |
| Release workspace and Clippy | 2,044 PASS, 0 FAIL and 34 external fixtures filtered at `9eeb9a61`. Native and WASM Clippy passed with warnings denied. |
| CoreS3 and Cardputer ADV | PASS 15/15 and 11/11. |
| Tab5 | PASS 25, DOCS-DEFECT 1 and NOT RUN 2, using the pinned stock binaries and documented probe substitutions below. |
| S3-A Atom | Six of nine variants completed all assertions. Lite's Arduino button and both AtomS3 configurations' Arduino button and IMU checks also failed on the pinned baseline. Stock USB CDC tests passed. |
| S3-B | Cardputer 11 PASS, Dial 11 PASS, StickS3 11 PASS plus five published example defects, StopWatch 18 PASS plus one published example defect, including the stock UIFlow2 case for each board. |
| S3-C | StampPLC 13 PASS and one DOCS-DEFECT. StackChan 26 PASS and one DOCS-DEFECT. Totals include stock. |
| Paper | PaperDIY 6, PaperS3 9, PaperMono 25 and PaperColor 14 runnable Arduino cases passed. PaperMono had one DOCS-DEFECT and PaperColor had two. All four stock UIFlow2 checks passed. Mono and Color held the same frame during BUSY. |
| C6-A | NanoC6 16 PASS and Nesso N1 12 PASS plus one DOCS-DEFECT, including stock. Thread, Zigbee and Nesso LoRa peer and isolation checks passed. |
| LX6 Atom | Lite and both Matrix profiles passed. M5Burner AtomU passed. The earlier M5Things launcher failures reproduced for GitHub AtomU and Echo images. The RMT and PDM receiver fixtures passed. |
| LX6 Stick | All six profiles passed their runnable cases. Five Stick receiver fixtures passed. The M5Stick factory and IP5306 probes also passed on `9eeb9a61`. |
| LX6 Core | Basic v2.7 and both Core2 profiles passed their runnable cases plus the cyclic DAC probe. The applicable Basic IMU documentation defect remains. |
| Four timing and instruction sentinels | Matched serial and instruction counts for the S3 hello, C3 hello, C6 hello and Pocket Tank fixtures. The follow-up build also matched all instruction counts and serial bytes. Wall-time performance figures reflect concurrent jobs and the separate build profiles. |
| Radio pairs | Nine PASS across connected and isolated ADV, Paper and Nesso lanes. |

The Tab5 fixture directory was incomplete. The replay recovered the exact stock UIFlow2 2.5.3/2.5.4, ESP-Hosted v2.12.6 and Maker Fighter 1.4 binaries and used archived Arduino builds of the pinned examples. The SDMMC and rail probes used the same sketch source built with Arduino ESP32 3.3.13, P4 preview rev3. The full-speed SDK MSC test used the preserved M5Stack Arduino 3.2.5 build of the same guest probe with normal SDK PHY setup. The generic ESP32 3.3.13 SDK probe variant reached host installation but did not finish enumeration in the original four-guest-second window. The M5Stack build enumerated, read sector 4 and completed all three BOT transfers in that window. The Maker Fighter rerun allowed more wall time while preserving its 7.5-second guest schedule. The original run reached its wall-time limit before the fourth interrupt report.

### AtomS3R-CAM and M12

The native socket accepts `state-set /machine/m5-lcd-cam auto-increment true` after `CAM_BASE_DONE` or `M12_BASE_DONE`. Both original guest images captured five distinct 153,600-byte frames through modeled DVP and DMA. Their seed-zero frame hashes matched the checked-in QEMU predicates at all tested geometries. The canonical property is `/board/camera auto-increment` and the full node includes seed, frames and power. [Marker-gated camera fixtures](https://github.com/m5agent/m5stack-esp-emulator/blob/48f14c7a74aed055b474b5424aec7a3c9f04cd4f/tests/uiflow2/device_matrix.json)

The original fixtures read SCCB before driving the active-low camera enable. Both sensors answered once the guest set GPIO18 low and waited 500 ms. Those two extra lines are the only source change in the separately composed powered images. CAM reported `0x21` and PID `9b00`. M12 reported `0x3c` and PID `3660`. Both still captured five distinct frames. The M12 legacy QEMU scan also includes devices that the fork places on other pin routes. [M5Stack camera power instructions](https://docs.m5stack.com/en/core/AtomS3R-CAM)

### Atom Echo and Basic v2.7

The classic QEMU machine supplies a TMP105 at 0x48. The fork makes it an explicit launch fixture using `--grove tmp105` and routes it over the boards' documented SDA/SCL pins. The original Atom Echo guest changed from an empty scan to `[0x48]`. Basic changed from `[0x75]` to `[0x48, 0x75]`. [QEMU Atom Echo board profile](https://github.com/m5agent/m5stack-esp-emulator/blob/5f3c4bd35fdc6f7fec4eddfcdb98420b95024d94/platform/qemu/profiles.json)

Basic's exact guest reads advanced from `SYS_CTL0=0x31` to `0xb9` and from `CHG_DIG_CTL0=0xc1` to `0x01` after preserving the documented reserved bits. The absence of a cell continues to show a clear charge-in-progress bit in `READ0=0x00`. The legacy QEMU fixture sets `0x08` with the charger-present fixture enabled and its battery-absent sentinel. Both report `READ4=0xff`. The guest also cleared and restored the boost bit and requested the 4.35 V charge target through M5Unified. [IP5306 register reference](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/core/IIC_IP5306_REG_V1.4_cn.pdf)

## Reproduction

Build the candidate with `cargo build --release --locked -p esp32sim --bin esp32sim --bin esp32sim-p4`. Supply the mask ROMs through `ESP32SIM_ROM_DIR`. Firmware, ROM, backend and frame hashes live in the [evidence summary](evidence/summary.json). Use the socket operations and timing listed above with the [original service parity fixtures](https://github.com/m5agent/agent-work-logs/blob/c85b8f0e84a51be65f1ab8273373bd472902fd74/records/m5stack-esp-emulator/2026-11-27-esp32sim-runtime-parity/per-device.md), the [pinned Arduino docs examples](https://github.com/m5agent/m5stack-firmware-archive) and the [Tab5 validation scripts](https://github.com/m5agent/agent-work-logs/tree/b50268351888f4ac0c1f061038188dee6092107a/records/esp32sim/2026-11-26-tab5-launcher/code/board-validation).

The StopWatch geometry also requires the service catalog's frame size to be updated to 466×466 on integration. Adapter deployment and physical panel, RF and electrical validation are outside this fork record.
