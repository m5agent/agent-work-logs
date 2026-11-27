# esp32sim runtime follow-up

This run compares esp32sim fork base `4e257b6be8ee0ed706c2e509d8f31ef7472a424b` with the runtime ending at `69f769fe` plus two test and documentation commits. The baseline benchmark used the native Device Service and browser WASM lanes. This follow-up uses locally owned CLI instances and a Node.js WASM ABI harness. The QEMU benchmark published first nonblack Core2 frames at 1.853 and 2.573 wall seconds in two of three runs, with no stable home in that capture. [Benchmark document](https://github.com/m5agent/m5stack-esp-emulator/blob/main/docs/esp32sim-backend-benchmark-2026-11-27.md)

| Item | Before | After |
| --- | --- | --- |
| Core2 stock home | The benchmark captured zero frames in eight wall seconds. Our CLI ran five guest seconds in 44.4 wall seconds at 8.2 M instructions/s and eventually drew home. | Classic Core pin observers stay attached. The scheduler uses normal quanta when the board has no GPIO SD waveform. The final binary draws the same stock home by 2.7 guest seconds, measured at 10.3 wall seconds and 32.6 M instructions/s for this capture. Matching serial and framebuffer hashes are in the manifest. A same-service frozen-QEMU follow-up captured no complete home, leaving same-screen latency censored. |
| Native pacing and throughput | The benchmark CPU control measured 0.987 guest seconds per wall second with Device Service pacing. | Documented standalone unpaced execution and service socket pacing. A mostly idle S3 probe completed three guest seconds in 0.1–0.3 wall seconds unpaced and 3.0 paced at identical 4,294,726 instructions and console. A saturated workload reached 958,355,931 instructions in both modes on the same guest-time bound. |
| #188 DSI panel ID | Normal Tab5 with GT911 attached drew frames and did not exercise the fallback read. | Unmodified UIFlow2 v2.5.4 on the disconnected-GT911 variant returned 98, 81, 0c through three real RX FIFO pops and drew 98 DSI scanouts. Attached-touch control drew 135 scanouts and produced zero pops. |
| #226 USB host MSC | Original Maker Fighter 1.4 exercised USB HID. Attaching MSC to this firmware produced setup traffic without a bulk read. The simulator served a built-in disk image. | Arduino-ESP32 P4 SDK guest sent READ(10) for LBA 4 through USB host and received 512 bytes and success CSW. Hashes matched on two distinct read-only images. The bus-reset path had recreated a default MSC device and discarded the configured backing. It now clears transport buffers while preserving the image across bus and BOT reset. |
| RUNTIME-01 C6 reset | The original Meshtastic landscape image did not reach the target reset in the exercised boot window. | An ESP-IDF v5.4.2 guest exercises the documented alternative path. Both `esp_restart()` and `LP_AON_SYS_CFG.HPSYS_SW_RESET` reboot with SDK reason 3, ROM causes 12 and 3 respectively, and persistent flash verifies after each reset. Both lanes pass with JIT enabled and disabled. |
| RUNTIME-02 Zigbee | The original light associated and processed the reference On/Off traffic. Leave and rejoin were untested. | An SDK coordinator sent Management Leave with rejoin set. The original light acknowledged, rebooted, rejoined and processed Off after On. This firmware run did not exercise simultaneous Wi-Fi. |
| RUNTIME-07/08/09 | QEMU workbench failure conditions include PIF on Core 1 SYSTIMER loads and a pthread WASM OOB after reset. | Each corresponding esp32sim board profile passed six alternating soft/power-on reset rounds with the JIT enabled and disabled. Both guest instruction encodings read the actual SYSTIMER registers at `0x60023008` and `0x6002306c` and an overdue compare raised INT_RAW before resetting. Node ABI re-instantiation covers stock boot separately. The QEMU workbench paths remain open. |

## Core2 Device Service reproduction

Both runtime variants were admitted by scoped local manifests on Device Service source `4462bf8f095bb051a00863f59321ee3052f36f0b`. Both used the same Core2 ROM and normalized flash SHA-256 `2a91964f4ef1b4823adc4b7b13fa08ddb2166ead3b96c74fe2088a71c4e3ea2a`. The HTTP request sequence used artifact intake, firmware creation, native esp32sim session, serial and framebuffer polling, ZIP acquisition and DELETE with `purge=0&retain_flash=0`.

| Runtime | First nonblack frame (wall s) | Exact home (wall s) | Stop |
| --- | ---: | ---: | --- |
| Baseline | 20.49 | 30.24 | stopped |
| Candidate | 3.70 | 5.40 | stopped |

Three separate sessions with the standard fat-LTO release build drew complete matching home frames at 5.53, 5.32 and 6.79 wall seconds. Their first nonblack timings were 3.62, 3.75 and 5.29 seconds. Each session archived evidence and reached the stopped state. The first nonblack hashes matched in the paired replay. The complete home image matched between arms and matched the stock CLI home image after pixel normalization. Timings are from session creation. Archive hashes and executable identities are in the performance summary. This is one HTTP pair. It closes the eight-second home window in that replay. A separate same-source QEMU comparison used the frozen executable with SHA-256 `04abc3ba8cb115919e7faebd55425c802f4f6e40b10bc3cc422c51700add728e` and the same normalized Flash. All three 24-second sessions reached the stock UIFlow2 banner. One returned an all-white frame at 6.62 s and two returned no nonblack frame. All three archived evidence and stopped. These samples establish the observed full-home outcome in the bounded window. They leave QEMU complete-home latency unmeasured. The QEMU first-frame timings in the historical benchmark remain separate.

## Profiling

The three stock 4.5 guest-second profiles sampled one native host process on macOS with the JIT enabled and disabled. CoreS3 spent time in Xtensa execution, SHA and bus/IRQ tick-budget handling. The Classic Core baseline sampled frequently in round processing, GPIO pad reads and `SocBus::tick`. With normal quanta, Xtensa execution and GPIO and MMIO operations remained visible. Tab5 interpreter time included instruction decode and flash fetch through the MMU window. The Tab5 JIT profile frequently sampled peripheral IRQ refresh, timer ticking, and translated MMIO helpers. The JIT comparisons ran the same guest instruction counts on each tested board.

| Profile | JIT M instructions/s | Interpreter M instructions/s | Guest instructions per run |
| --- | ---: | ---: | ---: |
| CoreS3 baseline | 24.0 | 19.0 | 383,894,435 |
| Core2 scheduling pilot | 29.9 | 22.6 | 359,375,217 |
| Tab5 baseline | 140.2 | 125.0 | 3,178,761,728 |

The existing WAITI/WFI idle path bounds advancement by pending core timers, peripheral deadlines and host inputs. Increasing the global idle cap reached the same Core2 home with the same instruction count as the scheduling fix alone. The classic ESP32 SoftAP golden then gained 20 exceptions. The cap was restored and the same golden passed. Default block chaining was left in place. Pacing affects host delay and does not guarantee that host-dependent input or network arrival timing reproduces.

At the same 2.7 guest-second limit, Classic Core changed Core 0/1 instruction counts from 132,477,754 + 204,367,072 to 132,290,321 + 204,272,039. The scheduler interleaves firmware polling and timed device events at its normal quanta. Repeated JIT/interpreter captures gave the same candidate counts and exact published output hashes. Five-guest-second pilot counts were also repeatable. This Core2 workload should not be compared as equal-work throughput.

## Stock time to home and REPL

| Board | Home baseline → candidate (wall s) | REPL baseline → candidate (wall s) |
| --- | ---: | ---: |
| CoreS3 | 12.68 → 10.05 | 14.35 → 14.30 |
| Cardputer-ADV | 6.94 → 5.77 | 10.89 → 11.17 |
| Core2 | 71.33 → 14.95 | 80.92 → 18.38 |
| Tab5 with stock C6 adapter | 34.81 → 41.04 | 23.13 → 21.46 |
| AtomS3 | 2.27 → 3.22 | 5.13 → 5.88 |
| Dial | 4.92 → 5.47 | 10.89 → 11.48 |

Home uses the first complete captured UI with its expected layout, excluding an all-white or splash frame. Core2 first nonblack was 52.80 → 10.03 wall seconds. REPL measures the first return of a scripted arithmetic command with a fixed guest-time injection schedule. Core2 and Tab5 use the native inherited service socket console. The remaining boards use a separate CLI USB-OTG CDC host capture. Tab5 home uses a separate boot without prompt injection. These are single pairs under varying concurrent regression load. Treat changes other than the repeated Classic Core scheduling effect as descriptive. Firmware and runtime SHA-256s, sample guest time and framebuffer identities are in the performance summary.

## Reproduction

Build the two pinned revisions with Rust 1.100.0 and the same release profile. The original stock timing pair used the default fat-LTO release build as its baseline and an LTO-disabled release build as its candidate. This corrects the initial claim that both binaries used the same profile. The historical wall timings describe those exact binaries under differing host load. The [service-parity merge follow-up](followups/2026-11-27-service-parity-merge/report.md) rebuilds both sides with matching compiler flags for the Tab5 comparison.

- Core2 CLI — `esp32sim --chip esp32 --board m5stack-core2 --boot rom --flash-image "$FW" --max-seconds 2.7 --no-dump --tft-png "$PNG"`. Use five guest seconds for the historical standalone baseline/pilot comparison.
- Tab5 DSI — `esp32sim --chip p4 --board m5stack-tab5-dsi-only --boot rom --flash-image "$FW" --debug dsi --max-seconds 2.7 --no-dump`. Use `m5stack-tab5` for the attached-touch control.
- [P4 USB host sector probe](https://github.com/m5agent/esp32sim/tree/2fba23b0305cc96a3bd9b9ccb78d0f3ed50523d8/tools/tab5-msc-probe). Hash the guest’s entire 512-byte reply on the host so both comparisons use the same SHA-256 implementation.
- [C6 flash and software reset probe](https://github.com/m5agent/esp32sim/tree/2fba23b0305cc96a3bd9b9ccb78d0f3ed50523d8/tools/c6-reset-probe). Repeat with `--no-jit`.
- [C6 original Zigbee light probe](https://github.com/m5agent/esp32sim/tree/2fba23b0305cc96a3bd9b9ccb78d0f3ed50523d8/tools/c6-zigbee-leave).
- `cargo test --release -p esp32s3 --test machine core1_systimer_mmio_survives_repeated_resets`.
- `cargo test --release --workspace --no-fail-fast --locked -- --include-ignored --skip external_`.
- `cargo clippy --workspace --all-targets -- -D warnings`.
- `cargo clippy --release --target wasm32-unknown-unknown -p esp32sim-wasm --features jit-tests -- -D warnings`.

Each change can be reverted independently. Revert the Classic Core change to restore the former instruction scheduling, and revert the USB change to restore the built-in-only media path.

## Regression

Workspace tests passed 2,041, with 34 `external_` cases excluded by the local matrix command. Native and WASM Clippy both passed with `-D warnings`. The alternating-reset test also passed in a separate invocation against the final test source.

All four three-run sentinels matched the baseline instruction counts and serial bytes on every repeat. CPU seconds varied under concurrent host load. Core2's changed scheduling count is separately listed above.

CoreS3 reached 15/15 and Cardputer-ADV reached 11/11 on the final native binary. Tab5 reported 25 PASS, one docs defect and two cases with no matching docs sketch. The first run captured an SDK enumeration stall on rebuilt firmware `3a742af6`. The matching reference SDK fixture `1d404ac8` passed on the same candidate with the same full-speed attachment script. The two-image LBA oracle used an independent guest. The companion record retains the initial suite failure and the final verdicts.

All nine radio pair checks passed with the synchronized peer runner, including isolated controls. The superseded asynchronous ADV relay could not establish a peer with this runtime. The C6 peer run verified Thread join, isolation and scan plus Zigbee join, reset recovery and scan. The stock-light leave probe is a separate case.

The first Node WASM run missed a requested console banner. In the repeat, each of the three stock images ran eight guest seconds twice in freshly constructed WASM instances without a trap and reached the ROM entry marker. StamPLC and ADV generated display frames. AtomS3 Lite has no framebuffer. The original QEMU workbench lifecycle and pthread trap remain outside this replay.

| Batch | Result | Evidence boundary |
| --- | --- | --- |
| S3-A Atom family | PARTIAL | Six board variants passed. AtomS3 Lite, AtomS3 and AtomS3 GC9107 failed the button fixture on both the pinned parent and candidate. The two AtomS3 variants also failed the IMU fixture on both. The stock CDC REPL checks passed on those three boards. |
| S3-B handhelds | PASS with docs defects | Cardputer and Dial passed. StickS3 and StopWatch passed runnable cases with the documented PM1 example defects. |
| S3-C StamPLC and StackChan | PASS with docs defects | Runnable Arduino cases and stock USB REPLs passed. The StamPLC display and StackChan NFC snippet defects remain recorded. |
| S3-D Paper boards | PASS with docs defects | PaperDIY, PaperS3, PaperMono and PaperColor completed their example and stock replays. PaperMono NFC power order and PaperColor IR pin sharing and SHT40 routing were classified as docs defects. |
| Classic Atom and Stick | PASS | Classic Atom stock versions, LittleFS and receiver fixtures ran. All six Stick profiles and routed receiver replays completed. |
| Classic Basic and Core2 | PASS with docs defect | Both Core2 power-chip profiles passed 15/15. Basic passed its supported cases, with a docs inventory mapping to a Gray-only IMU example. |
| C6-A NanoC6 and Nesso N1 | PASS with docs defect | NanoC6 passed 16/16. Nesso N1 passed 12 cases with one power example defect. Thread, Zigbee and LoRa pairs passed, including their exercised negative controls. |
| Cardputer-ADV CAP | PASS | NFC tag inputs and synchronized LoRa and CC1101 pair checks passed. The superseded asynchronous host relay failed before peer formation. |

The public summary binds these checks to the candidate binaries. The retained local runs contain the full fixture input and output logs.
