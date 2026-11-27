# LX6-C Basic and Core2 integration

| Board | Arduino docs | Stock UIFlow2 |
| --- | --- | --- |
| Basic v2.7, 4 MiB | 8/8 applicable PASS, IMU DOCS-DEFECT | PASS |
| Core2 v1.1, AXP2101 | 14/14 PASS | PASS |
| Core2, AXP192 | 14/14 PASS | PASS |

The Basic IMU example targets Gray. The Basic fixture used 4 MiB for every run. Core2 AXP192 battery stimuli use the accepted 3,678 mV at −150 mA and 4,096 mV at 150 mA inputs. The original runner supplied AXP2101 inputs to both presets, so the two AXP192 battery captures were replayed with the correct inputs. Stock UIFlow2 reached home and returned scripted button states through UART0. The Core2 presets also reported the injected touch point. BLE was NOT RUN because the matching stock debug ELF was unavailable.

The merge was clean. It retained LX6-A's updated RMT receive and raw PDM paths and took LX6-C's continuous I2S-to-DAC implementation. The shared AXP192, IP5306, INA3221 and FT6336U models are used by the corresponding board presets. The cyclic guest fixture produced the expected waveform, amplitude and cadence.

Replay with `tools/run-lx6-cores.py` and `tools/check-lx6-cores.py`, with `--board m5stack-core2-axp192` for the older Core2 preset. Use the Basic 4 MiB setting throughout. Run the cyclic DAC case via `docs/fixtures/lx6-receivers/replay.py`.

## Common gate

CoreS3 15/15, Cardputer-ADV 11/11, Tab5 25 PASS with one DOCS-DEFECT and two NOT RUN, and all earlier batch verdicts reproduced. Both ADV CAP NFC variants selected the tag 33 times each. Native and WASM Clippy passed. The hello and Pocket Tank instruction sentinels retained the same counts and serial output. Release workspace tests passed 2020 with zero failures.

The native CLI used the repository release profile. The workspace used release with LTO off, eight codegen units and debug symbols off. The S3-B runner used a scratch Bash 3.2 compatibility adjustment. Full transcripts stayed outside the archive.

Physical hardware, browser guest execution and cloud sync were NOT RUN. The pre-merge tree is the first parent of `7abb6b775d3cb12b2f2320c2593baeb72f41d522`. Rollback in shared history would use a new revert of the merge with the first parent as mainline.
