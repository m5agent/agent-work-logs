# LX6-B Stick integration and complete device matrix

The LX6-B merge combined CLI help, device exports and board callbacks. It retained the S3 hooks and the classic serialized I2S piezo route. AXP192, IP5306, MPU6886 and RX8130 each remain a shared model. The classic I2C FIFO change was exercised by the Atom, Basic and both Core2 profiles.

The Arduino columns count the pinned example cases. A dash marks profiles without a pinned suite. The four FAIL counts are the accepted LoRa pairing exceptions from the initial cumulative gate. The table lists the separate stock and factory checks.

| Board or profile | PASS | FAIL | DOCS-DEFECT | LIBRARY-DEFECT | NOT RUN | Stock or factory | Reasons and limits |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| CoreS3 | 15 | 0 | 0 | 0 | 0 | UIFlow2 2.5.3 home, touch and USB CDC PASS | |
| Cardputer-ADV | 11 | 0 | 0 | 0 | 0 | UIFlow2 2.5.3 home, keyboard and USB CDC PASS | Both CAP NFC and both CAP LoRa variants passed. The LoRa advisory includes ADV CAP. |
| AtomS3 Lite | 2 | 0 | 1 | 0 | 0 | UIFlow2 PASS | |
| AtomS3, each LCD preset | 3 | 0 | 2 | 0 | 0 | UIFlow2 PASS on both | |
| AtomS3R, each LCD preset | 5 | 0 | 0 | 0 | 0 | UIFlow2 PASS on both | |
| AtomS3U | 5 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| Atom VoiceS3R | 5 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| AtomS3R-CAM | 1 | 0 | 0 | 0 | 0 | UIFlow2 PASS | HTTP JPEG at 320×240 |
| AtomS3R M12 | 1 | 0 | 0 | 0 | 0 | UIFlow2 PASS | HTTP JPEG at 1600×1200 |
| Cardputer | 10 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| Dial | 10 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| StickS3 | 10 | 0 | 5 | 0 | 0 | UIFlow2 PASS | |
| StopWatch | 17 | 0 | 1 | 0 | 0 | UIFlow2 PASS | |
| StamPLC | 12 | 0 | 1 | 0 | 0 | UIFlow2 2.5.3 PASS | |
| StackChan | 25 | 0 | 1 | 0 | 0 | UIFlow2 2.5.3 PASS | |
| PaperDIY | 6 | 0 | 0 | 0 | 0 | UIFlow2 home, USB CDC and input PASS | |
| PaperS3 | 9 | 0 | 0 | 0 | 0 | UIFlow2 home, USB CDC and input PASS | |
| PaperMono | 23 | 2 | 1 | 0 | 0 | UIFlow2 home, USB CDC and input PASS | Two LoRa cases known flaky. The 4-gray frame held during BUSY. |
| PaperColor | 14 | 0 | 2 | 0 | 0 | UIFlow2 home, USB CDC and input PASS | The six-color frame held during BUSY. |
| Tab5, GT911 and ST7123 | 13 | 0 | 1 | 0 | 1 | UIFlow2 2.5.3 and 2.5.4 home and REPL PASS on GT911 | Original sketches counted once. Corrected speaker and the second touch-panel replay add two passing checks. RS485 and a board-specific UIFlow2 example have no pinned sketches. ST7123 stock was outside the multi-touch run. Mixed gate 25 PASS, 1 DOCS-DEFECT, 2 NOT RUN. |
| Atom Lite | 5 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| Atom Matrix | 5 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| Atom Matrix v1.1 | 5 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| AtomU | — | — | — | — | — | M5Burner catalog PASS. GitHub 2.5.3–2.5.5 launcher FAIL with missing M5Things. | Arduino NOT RUN. No dedicated examples. |
| Atom Echo | 0 | 0 | 3 | 0 | 0 | GitHub 2.5.1–2.5.5 launcher FAIL with missing M5Things. Representative REPL, button, RGB, mic and speaker PASS. | The three published sketches fail compilation. |
| Basic v2.7, 4 MiB | 8 | 0 | 1 | 0 | 0 | UIFlow2 PASS | BLE NOT RUN. The matching debug ELF is unavailable. |
| Core2, each AXP2101 and AXP192 preset | 14 | 0 | 0 | 0 | 0 | UIFlow2 PASS on both | BLE NOT RUN. The matching debug ELF is unavailable. |
| NanoC6, base and ENV-III | 15 | 0 | 0 | 0 | 0 | UIFlow2 PASS | Zigbee reset and rejoin PASS. The sensor case uses ENV-III. BLE NOT RUN. No pinned runnable case. |
| Arduino Nesso N1 | 9 | 2 | 1 | 0 | 0 | UIFlow2 PASS | Two LoRa cases known flaky. |
| StickC | 37 | 0 | 6 | 1 | 0 | UIFlow2 PASS | |
| StickC Plus | 28 | 0 | 0 | 1 | 0 | UIFlow2 PASS | |
| StickC Plus SE | 8 | 0 | 0 | 0 | 0 | UIFlow2 PASS | |
| StickC Plus2 | 10 | 0 | 1 | 0 | 0 | UIFlow2 PASS | |
| M5Stick | — | — | — | — | — | Factory PASS, including SH1107 and MPU9250 ID 0x71 | Arduino NOT RUN. No dedicated examples. |
| StickT2 | — | — | — | — | — | Factory thermal UI PASS, including two scenes and palette switching | Arduino NOT RUN. No dedicated examples. Absolute temperature PARTIAL without physical calibration. |
| Atech14, Waveshare Cam, LCD4B and AMOLED1.8 v2 | — | — | — | — | — | NOT RUN | Third-party presets have no M5Stack docs or stock inputs in this gate. The AMOLED board ran the Pocket Tank sentinel. |
| TTGO T-Display, CYD, AI-Thinker Cam, Ulanzi TC001 and SPI loopback | — | — | — | — | — | NOT RUN | No M5Stack docs or stock inputs for these presets. |
| Waveshare C6 LCD147, XIAO ESP32C6 and Waveshare P4 LCD35 | — | — | — | — | — | NOT RUN | No M5Stack docs or stock inputs for these presets. |
| ESP-Mosaico v1.2 and bare-module presets | — | — | — | — | — | NOT RUN | Upstream workspace guests and hello sentinels ran. These presets have no M5Stack docs or stock inputs. |

NEC RX and raw PDM passed on StickC, Plus, Plus SE, Plus2 and StickT2 with the `LX6_RECEIVER_STICK=ON` guest. The first receiver attempt used the Atom build and entered DAC mode. Its capture was retained.

The known flaky LoRa pairing item covers Nesso, PaperMono and ADV CAP. Both ADV CAP variants passed ten of ten on each build. Preserved failures are `r01-ef799a13-papermono`, `r09-ef799a13-papermono`, `full-gate-9ac09fb7-papermono-initial` and `full-gate-9ac09fb7-nesso-initial`. The controlled repeats and launch timing observations are recorded in the linked LoRa comparison.


## Common gate

CoreS3 passed 15/15, Cardputer-ADV 11/11, and Tab5 recorded 25 PASS with one DOCS-DEFECT and two NOT RUN. The cumulative board checks completed with the LoRa exceptions above. Both ADV CAP NFC variants selected the tag 33 times each. Native and WASM Clippy passed. The hello and Pocket Tank instruction sentinels retained the same counts and serial output. Release workspace tests passed 2039 with zero failures.

The native CLI used the repository release profile. The workspace used release with LTO off, eight codegen units and debug symbols off. The S3-B runner used a scratch Bash 3.2 compatibility adjustment. Full transcripts stayed outside the archive.

Physical hardware, browser guest execution and cloud sync were NOT RUN. The pre-merge tree is the first parent of `9ac09fb79cefe4a2cb6f911172ffa6cbdfbd784a`. Rollback in shared history would use a new revert of the merge with the first parent as mainline.
