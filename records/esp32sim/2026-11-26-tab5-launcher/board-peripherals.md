# Tab5 milestone 2 virtual-device validation

The source branch is [m5/tab5-2 at 9e9694a7](https://github.com/m5agent/esp32sim/tree/9e9694a71e486779a636a14890917f1d83944fca), seven commits after base `3e079c0b`. The original Tab5 profile uses the ILI9881C panel and GT911 touch. The secondary profile uses ST7123. All results are guest execution or host-side regression checks as indicated.

| Stage | Commits | Guest evidence |
| --- | --- | --- |
| DMA2D and PPA | `566989f0`, `cf6c3712`, `3cc79d76` | The baseline stock v2.5.4 frame was white while the guest polled DMA2D reset state. The working SRM descriptor path draws the launcher. Unit checks cover fill, blend, conversion and completion interrupts. |
| UIFlow2 launcher | `0d987ebd` | Cold boots of stock v2.5.3 and v2.5.4 show the launcher. A GT911 press at native (83, 755) at 7.00 s with lift at 7.45 s opens the ADC controls. Both tests passed again at the final head. |
| P4 HS USB host | `b760490f` | Maker Fighter 1.4 enumerates a HID gamepad, receives four three-byte IN reports and opens its menu. The separate MSC controller probe enumerates and reads a 512-byte sector through bulk transfer. Both passed again at the final head. |
| Audio | `b74c3e1f` | P4 I2S0 routes the ES8388 speaker and ES7210 microphone. The final corrected speaker run produced 528,117 samples at 48 kHz and all five ordered tones from 10 kHz to 2 kHz. The microphone example showed different tone and silence waveforms and replayed the 733 Hz input after a touch, with a measured active-window median of 730 Hz at 10 Hz frequency resolution. |
| Board peripherals | `9e9694a7` | Original Arduino examples exercised two simultaneous points, injected motion and battery state, the running RTC, and SPI SD. A second guest read the SPI-written file through native SDMMC. |

The accelerator model services synchronously armed channels by priority, then channel number. RGB565, RGB888, ARGB8888 and the tested YUV420 SRM conversions are implemented. Token-weight timing, the remaining YUV subsampling combinations, and cycle timing remain open. The USB host evidence covers descriptor DMA, control, interrupt and bulk traffic. SDK MSC, keyboard interaction in Maker Fighter, and other transfer modes remain outside the passing results.

## Case results

| Case | Result | Observation |
| --- | --- | --- |
| Arduino GT911 button | PASS | Released, pressed, released frames after touch down and up. |
| Arduino GT911 multi-touch | PASS | Two simultaneous contacts at (160, 400) and (540, 880). |
| Arduino ST7123 multi-touch | PASS | The same two contacts on the alternate board. |
| Arduino BMI270 | PASS | The display reports injected acceleration X=0.50, Y=-0.25 and gyro X=125.00. |
| Arduino speaker, original | FAIL | The public sketch starts with `##include`, which the compiler rejects. |
| Arduino speaker, corrected copy | PASS | Replacing the leading `##include` with `#include` builds the example. The guest shows Speaker Test and plays the five expected tones in order. |
| Arduino microphone | PASS | Tone and silence yield distinct frames. Touch starts replay of the injected tone. |
| Arduino battery and charging | PASS | The injected 7,980 mV and charging=yes appear on-screen with 86% battery computed by the sketch. |
| Power output fragment | PASS | Guest extension calls and expander reads observe PA and USB both enabled, USB only, then both disabled. |
| Arduino RTC, local | PASS | RX8130 date and time are written and read, and seconds advance. |
| Arduino RTC, SNTP | FAIL | The setup remained at station mode and produced no RTC sync marker. |
| Arduino wake after five seconds | FAIL | Touch put the panel to sleep. Ten virtual seconds elapsed without a guest reboot. |
| Arduino wake at the next minute | FAIL | The guest reached panel sleep. The traced run timed out at 25.129 virtual seconds and the retry reached 65 seconds without rebooting. |
| Arduino microSD, SPI | PASS | Mounted and wrote the exact 39-byte file. The sketch found both test PNGs and RGB scanout verified both rendered fixtures. |
| Arduino microSD, SDMMC probe | PASS | A second guest mounted the same image with the SDMMC API, used CMD17 and read 6,864 controller bytes. Its serial success marker confirms the exact SPI-written file contents. |
| Arduino Wi-Fi station | FAIL | The P4 application remained in station setup with the matched C6 and virtual AP. |
| Arduino Wi-Fi scan | FAIL | C6 serial recorded scan completion. The P4 screen stayed at Scan start. |
| Arduino antenna selection | PASS | The guest programmed expander P0 for the internal antenna. |
| Arduino Wi-Fi AP | NOT RUN | AP code in the published station sketch is commented out. |
| UIFlow2 v2.5.3, stock | PASS | ILI9881C displays the home screen and GT911 input opens ADC. |
| UIFlow2 v2.5.4, stock | PASS | ILI9881C displays the home screen and GT911 input opens ADC. |
| UIFlow2 v2.5.3, REPL | PASS | Exact 720×1280 fill, GT911 down/up, and DSI RX ID `98 81 0c`. |
| UIFlow2 v2.5.4, REPL | PASS | Exact 720×1280 fill and GT911 down/up. |
| Maker Fighter HID | PASS | Idle control remains before the menu. Four injected HID reports change the screen to ARCADE, TAG BATTLE, TRAINING and SETTING. |
| MSC register probe | PASS | The guest reads descriptors, sends READ(10), verifies the sector and command status, and draws a green result frame. |
| MSC Arduino USB Host SDK probe | FAIL | The call to `usb_host_install` did not return before the 6 s capture, with no enumeration activity. |
| RS485/UART | NOT RUN | The English Tab5 Arduino examples examined for this run contain no RS485 sketch. |

The RTC alarm register path has unit coverage. End-to-end board wake still needs P4 PMU sleep and power sequencing. Network tests used a local virtual AP with the example's placeholder values. The camera, RF behavior, electrical rails and physical audio remain unmeasured.

## Reproduction and regressions

The [runner and checker](code/board-validation/README.md) describe the staged captures. The [run manifest](run-board.json) binds the guest checks to firmware, ROM, runtime and framebuffer hashes. The [case verdicts](evidence/tab5-board-check-summary.ndjson) are the automatic acceptance results. The runner exits with a failure status if any case fails.

M5Stack Arduino 3.2.5, Arduino CLI 1.3.1, and M5Unified/M5GFX 0.3.0 were used with FQBN `m5stack:esp32:m5stack_tab5`. The sketches came from English docs commit `7219cc9286c39b463da84053deee40bc234625db`. The stock UIFlow2 and network experiments used C6 adapter v2.12.6. The original Arduino speaker compile error is retained independently of the corrected binary.

At the final source head, 623 library tests, the P4 and S3 ROM suites, native and WASM Clippy with warnings denied, and both P4 device-mode MSC goldens passed. CoreS3 passed 15/15 cases and Cardputer ADV passed 11/11. The final candidate and base executed the same instruction counts for the dual-core hello, C3 hello, C6 hello, P4 hello and pocket-tank comparison. CPU time was measured on a shared host. The [benchmark summary](evidence/tab5-board-benchmark-summary.ndjson) contains the individual measurements.

The earlier [launcher report](report.md) records the failed baseline and exact working launcher stage. The [USB report](usb-host.md) records the first-report assertion and the successful retest. Source rollback is available by reverting the affected commits in reverse order.
