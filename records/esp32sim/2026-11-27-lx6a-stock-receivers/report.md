# LX6-A alternate firmware and shared classic controllers

## Stock UIFlow2

| Board and official distribution | Launcher and module availability | Follow-on behavior |
| --- | --- | --- |
| AtomU GitHub v2.5.3, v2.5.4 and v2.5.5 | FAIL, missing `M5Things` | v2.5.4 UART0 REPL, button, RGB and PDM capture PASS |
| AtomU M5Burner catalog v0.1, guest banner v2.5.4 | PASS, direct `M5Things` import and offline Wi-Fi setup path | UART0 REPL, ID 130, button 0/1/0, RGB and both mic inputs PASS |
| Atom Echo GitHub v2.5.1 through v2.5.5 | FAIL, missing `M5Things` in all five exact-board images | v2.5.4 UART0 REPL, button, RGB, PDM and I2S speaker PASS |
| Atom Echo M5Burner UIFlow2 | NOT RUN. Exact and Atom Series catalog searches found no UIFlow2 image for Echo on 2026-11-27. | Alternate matrix NOT RUN |

The catalog AtomU image came from the public M5Stack entry `2099000000000000001`. Its SHA-256 is `59e1236f6c47140270fa485ece305a7a8c36a4fbda96d59f2359c75219ab5497`. It printed the offline setup message, drove the launcher RGB blue and exposed the stock REPL. The microphone replay separated silence from the 733 Hz and 1,234 Hz inputs. Account binding and cloud sync were NOT RUN. [M5Burner](https://burner.m5stack.com) · [Latest GitHub release tested](https://github.com/m5stack/uiflow-micropython/releases/tag/2.5.5)

### Candidate text for the main repository

> **AtomU and Atom Echo stock UIFlow2 v2.5.4.** The SHA-256-pinned 4 MiB GitHub release images reach the UART0 REPL after the factory launcher aborts. In boot option `1`, `startup/headless.py` imports `M5Things` unconditionally. The module is absent from these release images. The M5Burner AtomU catalog entry `UIFlow2.0 AtomU` v0.1 also reports v2.5.4 in the guest. That separately hashed image includes `M5Things` and passed offline launcher, REPL, button, RGB and microphone checks in native virtual-device validation. Atom Echo's v2.5.4 GitHub image passed REPL, input, RGB, microphone and speaker checks after the launcher abort. [Upstream startup source](https://github.com/m5stack/uiflow-micropython/blob/e437118892520ba987c2d930a2428db1cab65ab1/m5stack/modules/startup/headless.py#L11) · [Official v2.5.4 release](https://github.com/m5stack/uiflow-micropython/releases/tag/2.5.4)

## Shared classic controllers

- **RMT RX PASS.** A GPIO32 waveform reached an enabled RX channel through the GPIO matrix. The ESP-IDF v6.1 callback and guest decoder recovered `aa55ff00` and `a956fe01`. The idle control returned no frame. Controller tests check the filter, idle IRQ, write pointer, ownership and RAM bound.
- **Raw PDM PASS.** The AtomU guest captured 20,480 raw 16-bit words through I2S0 DMA. GPIO5 carried the configured sampling-clock route, and GPIO19 supplied the data. The capture contained 7,865 zero words, 12,612 all-one words and three transition words. The idle control returned 20,480 zero words. Controller tests check split-interval packing, slot order, routing and DMA EOF. Physical PDM clock edges and microphone acoustics were NOT RUN.
- **Continuous I2S0 DAC PASS on LX6-C.** The controller contracts passed against `cc89f1adea1ee1922b4ecd99608382cacd4fbb9b`. The Basic v2.7 guest requested 500 Hz with cyclic DMA at 32 kHz and yielded 110 rising edges at 500.0 Hz on the modeled GPIO25 DAC path. The pinned Arduino Basic speaker sketch also produced 214,961 output samples. LX6-C owns the DAC implementation. LX6-A carries the reusable controller and guest checks.

The local branches showed LX6-B's converted PDM and speaker work and LX6-C's DAC path before their remote refs became available. A later fetch and merge-tree check passed against the published LX6-B and LX6-C tips. Earlier attempts are retained in raw evidence. The first DAC fixture requested 16 kHz from the default clock, below the driver minimum. The first raw PDM guest timed out until the input route recognized peripheral clock output enable. The corrected guest suite completed every case. [Fixture and reproduction commands](https://github.com/m5agent/esp32sim/tree/082938f4333f0fcbb1f16dca0cf3146f3e226ba3/docs/fixtures/lx6-receivers) · [ESP-IDF I2S reference](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/i2s.html)

## Release checks

CoreS3 passed 15/15. Cardputer-ADV passed 11/11. The nine AtomS3 profiles reproduced 39 passes and five inherited docs failures. Classic Atom reproduced the previous exact GitHub results. Native and wasm32 Clippy passed with Rust warnings denied. Cargo recorded 1,982 passes and the same seven P4 failures. Classic and S3 hello runs matched their previous per-core instruction counts. The native release build disabled LTO.

The evidence files retain hashes and bounded observations. Full serial logs, firmware, waveforms and audio remain in local evidence. Use the prior branch tip to roll back the receive changes. The main emulator repository's candidate note is provided above for review.
