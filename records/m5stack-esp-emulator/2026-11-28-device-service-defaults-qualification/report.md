# Device Service default migration qualification

## Source and scope

The service candidate `872c92e18408696c1a12f4c5a9ed5db119f18adf` extends the published `c6cd576f1a5dfd40a193acb75dbd908cbe9613a4` candidate. The latest qualification fork is `4245d96b1cf3fae5c2360a87cd6b716bc1c94c9d`. Reviewer tests used the local patch `a7730f8` on `d0d51f84d2933807ffbac35f1a0060e60e9b6be8` with the runtime-map flag enabled and submission disabled. The resident rollout remains the preceding production basis. These are virtual-device results.
[Service source](https://github.com/m5agent/m5stack-esp-emulator/commit/872c92e18408696c1a12f4c5a9ed5db119f18adf) · [Fork source](https://github.com/m5agent/esp32sim/commit/4245d96b1cf3fae5c2360a87cd6b716bc1c94c9d) · [Prior qualification](../2026-11-27-device-state-routing-candidate/)

The shared oracle, the new board-state reads, the Tab5 stock and playback receipts, and early reviewer comparisons used fork `cf628d4ce275a46c9bee61531df02dc40283ad72`. Its native binary SHA-256 was `bf90df19d795ceea61e551e59baa51d00efd12ca36c6730d7162eba69e7eb6a6`. Its P4 binary SHA-256 was `2f124a3ab6ef427a7ebeb338b72cf710f9e18fe1e789e25ee5f1cbb486c81281`. The latest fork adds the PaperColor and PaperMono PM1 power-key register path. Its staged native and P4 binaries are `28a15181e5434c5de68157b83d9428ff64ae68637ed4b3ad5d31da7a9795980f` and `a5cd05d6d9a6babfb8b019e45ece991e2b0a21a530372546c256258954358c20`. The first exact 4,096-byte stereo window proof used fork `b0589c01`. Each claim is tied to the corresponding evidence rather than carried forward to every source revision. [Oracle receipts](evidence/shared-oracle-summary.json) · [Tab5 receipts](evidence/tab5-summary.json)

## Per-device results

The oracle columns count passing cases **per trial**, with identical totals in trials 1 and 2. A dash means the 56-case suite has no case for that board or no new network result. Existing board-state rows derive from the previous candidate's recorded read proofs unless the row says new. The QEMU route is the existing ordinary Device Service path. Tab5 retains its firmware and panel routing. [Prior state receipts](../2026-11-27-device-state-routing-candidate/) · [Shared oracle](evidence/shared-oracle-summary.json) · [Paired fixture receipts](evidence/paired-fixture-summary.json)

| Board | Native device state | Network | QEMU | esp32sim | Default | Open gate |
| --- | --- | --- | ---: | ---: | --- | --- |
| atom-echos3r | Onboard I/O and ES8311 | — | — | — | QEMU | Matched oracle and consumer state replay missing |
| atoms3 | IMU | — | 2/2 | 2/2 | QEMU | Existing ST7735S button and IMU parity and REPL consumer coverage |
| atoms3-lite | Onboard I/O | — | — | — | QEMU | Matched oracle and watcher/reviewer endpoint coverage missing |
| atoms3r | IMU, BMM150 and LED | — | 0/2 | 2/2 | QEMU | Native paired magnetometer output differs from the legacy fixture |
| atoms3r-cam | Onboard I/O and GC0308 | — | — | — | QEMU | Same-camera write and watcher replay missing |
| atoms3r-m12 | Onboard I/O, OV3660 and LCD_CAM | — | — | — | QEMU | Same-camera sequence and watcher replay missing |
| atoms3u | Onboard I/O and RMT | — | — | — | QEMU | Matched oracle and per-channel RMT watcher replay missing |
| basic-v27 | IP5306 | — | 0/2 | 2/2 | QEMU | Matched IP5306 write and reviewer replay missing |
| nanoc6 | New RGB, IR and button reads 2/2 | STA/SoftAP 4/4. HCI diagnostic uses qemu-ble | — | — | QEMU | Matched oracle and full watcher/reviewer replay missing |
| nesso-n1 | New PI4IOE, BQ27220, AW32001 and BMI270 reads 2/2. BQ27220 guest bus read 2/2 | STA/SoftAP 4/4. HCI diagnostic uses qemu-unified | — | — | QEMU | Matched oracle and full watcher/reviewer replay missing |
| papercolor | PM1 and sensor. Original power fixture 2/2 on each lane | — | 1/1 | 1/1 | QEMU | Shared watcher and saved review pass. Named legacy network compatibility unresolved |
| paperdiy | Panel | — | 0/1 | 1/1 | QEMU | Saved SD-write reviewer remains partial on both lanes |
| papermono | PM1, charger, IMU and RTC. Original board and SDMMC fixture 2/2 on each lane | LoRa 4/4 loopback | 1/1 | 1/1 | QEMU | Shared watcher and saved review pass. Pinned standalone SD seed missing |
| papers3 | Panel | — | — | — | QEMU | Same-input oracle and reviewer endpoint replay missing |
| stackchan | Power, IMU, magnetometer, INA226, light/proximity, RTC, body touch, expander and servos | — | 1/1 | 1/1 | QEMU | Legacy body touch 2/2. Full paired fixture still differs on magnetometer, power telemetry and IR receive |
| stamplc | LM75, INA226, RTC, expander and front panel | — | 0/1 | 1/1 | QEMU | Onboard I/O 2/2. Native LM75 paired fixture 0/2 versus QEMU 2/2 |
| stickc | IMU | — | 1/1 | 1/1 | QEMU | Same-firmware legacy IMU write and watcher/reviewer replay missing |
| stickc-plus | IMU | — | 11/11 | 11/11 | QEMU | Same-firmware legacy IMU write and watcher/reviewer replay missing |
| stickc-plus2 | IMU and RTC | — | 2/2 | 2/2 | QEMU | Legacy IMU/RTC write and REPL consumer coverage missing |
| sticks3 | PM1 and IMU. Paired peripherals 2/2 on each lane | Original provisioning reviewer remains partial | 2/2 | 2/2 | QEMU | Paired audio capture and provisioning criteria incomplete |
| stopwatch | PM1, M5IOE1 and IMU. Paired PM1/M5IOE1 2/2 | STA managed-review replay incomplete | 2/2 | 2/2 | QEMU | Managed STA reviewer endpoint parity missing |
| tab5 | New PI4IOE, INA226, RX8130, BMI270 and panel reads 2/2 | — | — | — | Qualified firmware/panel pairs use esp32sim | Original frame plan remains partial on esp32sim. Standalone 25-case replay incomplete |

The paired runner waits for the runtime lease to enter `running`. It applies boot settings to QEMU before `cont` and to esp32sim as cycle-zero register writes. After boot it applies each original fixture's QOM, synchronization markers and inputs in order. It requests the evidence bundle before stop and confirms the lease is stopped. StopWatch's PM1 GPIO initialization is required before boot. The StickS3 initial battery sample must also be in place before the application reads it. The restored `p` route reaches the model's M5PM1 button registers. PaperMono's SDMMC admission reaches the original block-read/write guest marker `PAPERMONO_SD rw ok`. Both Paper board fixture pairs passed on each runtime twice after the preboot supply and guest-marker ordering were restored. The original power-key input reaches each board's PM1 bus registers. [Paired receipts](evidence/paired-fixture-summary.json)

The Nesso N1 BQ27220 probe reads commands `0x08`, `0x14` and `0x2c` through I²C0 on SDA10 and SCL8. The guest serial and service state both tracked `3900 mV / 123 mA / 77%` to `3750 mV / 123 mA / 65%` twice. The separate native device-state evidence shows the NanoC6 button transitions and Tab5 INA226 fixture readback. [Probe source](code/main/probe.c) · [Board-state receipts](evidence/board-state-summary.json) · [C6 network receipts](evidence/c6-network-summary.json)

The watcher probe covered live frame, serial, events, device state, QOM and Flash snapshots and diffs, ZIP member hashes and retained Flash readback. It passed across 16 leases with two trials per runtime for PaperColor, PaperMono, StickS3 and StopWatch. These endpoint results cover the sampled firmware and the shared watcher calls. The board-specific reviewer endpoints have independent results below. [Watcher receipts](evidence/watcher-summary.json)

## Tab5 behavior

Stock UIFlow2 v2.5.3 and v2.5.4 opened TOOLS/ADC 8/8 on esp32sim. esp-emu opened it 4/4 with ST7123 and did not produce a usable GT911 frame in 4/4 trials. UserDemo's peripheral bus uses P4 I²C0 and its ES8388 output uses I²S1. The stereo path emits complete interleaved 16-bit frames with a live offset, a recording identifier and the existing range checks. Both backends returned the exact retained 4,096-byte quiet window. On the native runtime, two same-firmware Music Test and Play Music runs each retained 400,384 bytes of stereo PCM at 48 kHz. The quiet RMS was zero. Playback L/R RMS values were 1406.832/1886.855 and 2634.679/3470.759. [Tab5 evidence](evidence/tab5-summary.json)

The original frame plan passes on esp-emu and dispatches its first tap on esp32sim. The native Music Test region digest is stable across the direct trials and differs from the expected legacy digest. The review stops at that assertion and cannot count the original action as verified. In the direct playback runs the native controller reported both reads for Music Test and one of two reads for Play Music. Playback and frames therefore provide a narrower functional result than the saved reviewer contract. The existing review criteria remain in force. [Reviewer evidence](evidence/reviewer-summary.json)

## Saved-snapshot reviewer with runtime flag enabled

| Job | Configured or legacy run | Forced native comparison |
| --- | --- | --- |
| SD read | SIM_VERIFIED | SIM_VERIFIED |
| Dial encoder | SIM_PARTIAL, E_INTERACTION_CLAIM_PARTIAL | SIM_PARTIAL, E_INTERACTION_CLAIM_PARTIAL |
| Crash | SIM_PARTIAL, E_SIM_APP_CRASH | SIM_PARTIAL, E_NO_FRAME. Native crash receipt showed no panic |
| Network/STA | SIM_PARTIAL, E_SIM_MODEL_GAP on the same-guest review-sta run | NOT RUN on an admitted managed STA lane |
| Fixed SoftAP | Native Wi-Fi network assertion PASS. Headless job SIM_PARTIAL, E_NO_FRAME | NOT RUN on a compatible esp32sim reviewer profile |
| StickS3 provisioning | Original application and matching boot context admitted to qemu-wifi. SIM_PARTIAL, E_NETWORK_PARTIAL | NOT RUN on an admitted native reviewer profile |
| Unit | SIM_VERIFIED with joystick fixture | SIM_VERIFIED with joystick fixture |
| Audio | Cardputer ADV speaker SIM_PARTIAL. The firmware starts playback on its own and the action baseline was unstable | NOT RUN for the generic audio job |
| Filesystem output | Exact guest-created SPIFFS file verified. Headless job SIM_PARTIAL, E_NO_FRAME | Native admission for this filesystem fixture remains open |
| SD write | SIM_PARTIAL, E_SIM_SD_WRITE_PARTIAL | SIM_PARTIAL, E_SIM_SD_WRITE_PARTIAL |
| Core2 2048 | NOT RUN. Public 2048 Game 1.0 metadata was found. The exact archived application and its matched boot context were unavailable for this replay | NOT RUN. The reviewer check binds the original identity to QEMU |
| CardputerDict | Original firmware stopped at E_CARDPUTER_PRONUNCIATION_ENVIRONMENT | NOT RUN. Managed trusted network prerequisites were unavailable |
| PaperColor display review | SIM_VERIFIED | SIM_VERIFIED |
| PaperMono display review | SIM_VERIFIED | SIM_VERIFIED |
| Tab5 frame assertion | SIM_VERIFIED | SIM_PARTIAL, E_INTERACTION_CLAIM_PARTIAL |
| Tab5 speaker assertion | SIM_PARTIAL, E_TAB5_SPEAKER_PARTIAL on this run | SIM_PARTIAL, E_INTERACTION_CLAIM_PARTIAL |

The three rebuilt review fixtures used ESP-IDF `fff9895c82d744c7237be8847347bdd1b07c6643`. Their hashes are distinct from the earlier archive inputs. External review submission was disabled. The archived verdicts preserve a prior unsuccessful admission attempt as well as the retried outcome. [Job receipts](evidence/reviewer-summary.json)

## Reproduction and remaining gates

Use `scripts/bootstrap-esp32sim-runtime.py` with the matching fork commit and [qualification runtime lock](code/qualification-runtime.lock.json) in a separate output directory. Enable the candidate's declared register-state, touch-receipt and stereo capabilities on the exact staged binary. Run `tests/firmware/arduino_docs/run_service.py` with the same firmware for each backend and two trials. The per-case digests and lease cleanup are in the oracle summary. Apply the original cases and boot inputs from `tests/uiflow2/run_peripheral_matrix.py`. The relevant expected markers and prior failures remain in the paired evidence. For Nesso, build the [probe](code/) with ESP-IDF 6.1, then merge the bootloader, partition table and app into 16 MiB flash at offsets 0, 0x8000 and 0x10000. Inject each battery value through the normal Device Service input endpoint and compare the I²C-driven serial result with the service state.

The latest fork passed 2,047 workspace tests with 34 explicit filtered cases, native and WASM Clippy, CoreS3 15/15 and Cardputer-ADV 11/11. The four sentinel workloads preserved instruction counts and serial output across three comparisons. Timings varied under concurrent host load. Both ADV LoRa peer cases received the original payload, and the same-build isolated controls showed zero receptions. Nesso N1 received 14 packets, and the PaperMono pair delivered all four exact packet identifiers while its isolated control received zero. [Gate receipts](evidence/gate-summary.json) · [Radio receipts](evidence/radio-summary.json)

The exact service source passed the Python 3.12 platform suite with 2,596 tests and nine skips. The runtime coverage, peripheral catalog, QEMU profiles, generated snapshot and PR scope checks passed. The previous source attempt failed the snapshot check after two test lines changed. The generated snapshot was refreshed before the passing run.

The migration gate is PARTIAL. The standalone Tab5 harness references archived inputs that have expired or whose available replacements have other digests. The full PaperMono docs batch requires its original FAT seed with SHA-256 `30e8fcb56ada9282944d404fd6929a2f8a2cd112a7b795b8cecd68747507fcea`. The narrower radio, board and reviewer results have their own verdicts. No service PR, merge SHA, production cutover time or new rollback record exists for this qualification. The prior rollback remains applicable to the prior rollout. [Gate evidence](evidence/gate-summary.json)
