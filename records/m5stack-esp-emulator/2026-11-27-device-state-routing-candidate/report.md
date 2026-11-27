# Device Service routing qualification

## Scope and identities

The [control parity rollout](https://github.com/m5agent/agent-work-logs/blob/db8eb5e4db558185831650214d001b364fe9e1b7/records/m5stack-esp-emulator/2026-11-27-device-service-control-parity/synchronized-rollout.md) recorded lease and reviewer gaps with the `9c0447e8` fork runtime. This candidate reads the existing QEMU component schema from each board's modeled registers, retains it after stop, and maps supported QOM fixture writes onto the modeled peripheral bus. The C6 SoftAP path uses a virtual station and retains Ethernet capture without host NAT.

The Device Service candidate is `c6cd576f1a5dfd40a193acb75dbd908cbe9613a4` on base `3ec64361ca9094fff773f32614e5ed13e8fe54a2`. The [fork candidate](https://github.com/m5agent/esp32sim/commit/e929d5b2ca7a1f2475d60ee0626b30ab6ed986d7) is `e929d5b2ca7a1f2475d60ee0626b30ab6ed986d7`. The reviewer opt-in local replay used `d0d51f84d2933807ffbac35f1a0060e60e9b6be8`. The summaries bind firmware SHA-256, runtime identities where exposed, paired trial and retained evidence digest. Validation was on an isolated macOS arm64 stack and used virtual devices.

## Results

Each count includes two trials per case. A dash means the shared 56-case oracle does not exercise that device. For each trial esp32sim passed 56/56 and QEMU passed 46/56. Both runtimes completed cleanup in all 224 shared-oracle trials. Some QEMU failures were fixture or endpoint admission failures. The figures describe outcomes of the shared predicates on the configured runtime lanes. The public summaries omit endpoint, session, device identity and unbounded logging fields.

| Board | Native device state | Network work | QEMU oracle | esp32sim oracle | Ordinary route | Open gate |
| --- | --- | --- | ---: | ---: | --- | --- |
| `atom-echos3r` | 2/2 reads, onboard-io, es8311 | — | — | — | QEMU | QEMU fixture returned an empty map. Native export has onboard I/O and codec counters. A matched consumer-state replay remains open. |
| `atoms3` | 2/2 reads, imu | — | 4/4 | 4/4 | QEMU | The original batch button and IMU guest assertions failed on the ST7735S fixture. UIFlow live admission uses QEMU. |
| `atoms3-lite` | 2/2 reads, onboard-io | — | — | — | QEMU | No shared oracle case. Onboard I/O reads passed. The watcher and reviewer case expansion remains open. |
| `atoms3r` | 2/2 reads, imu, magnetometer, led | — | 0/4 | 4/4 | QEMU | The checked-in guest fixture did not emit its button, acceleration, gyroscope or magnetometer markers on the native service replay. |
| `atoms3r-cam` | 2/2 reads, onboard-io, gc0308 | — | — | — | QEMU | The sampled state includes onboard I/O beyond the legacy camera component. Matched camera write and watcher replay remains open. |
| `atoms3r-m12` | 2/2 reads, onboard-io, ov3660, m5-lcd-cam | — | — | — | QEMU | The sampled state includes onboard I/O beyond the legacy camera components. Matched camera sequence and watcher replay remains open. |
| `atoms3u` | 2/2 reads, onboard-io, rmt0 | — | — | — | QEMU | No shared oracle case. The onboard I/O and RMT reads passed. Per-channel guest and watcher replay is still required. |
| `basic-v27` | 2/2 reads, ip5306 | — | 0/4 | 4/4 | QEMU | The shared screen oracle passed on esp32sim. An equivalent checked-in IP5306 write and reviewer replay remains open. |
| `nanoc6` | No registered components | STA + SoftAP 4/4. HCI-UART QEMU. | — | — | QEMU | The legacy stock HCI-UART diagnostic needs a complete flash image. Its omitted-runtime request resolves to qemu-ble. |
| `nesso-n1` | No registered components | STA + SoftAP 4/4. Unified QEMU. | — | — | QEMU | The legacy unified HCI-UART diagnostic needs a complete flash image. Its omitted-runtime request resolves to qemu-unified. |
| `papercolor` | 2/2 reads, power, sensor | — | 2/2 | 2/2 | QEMU | The paired PM1 power and button fixture did not complete. Its original preboot QOM setup is required to judge it. |
| `paperdiy` | 2/2 reads, panel | — | 0/2 | 2/2 | QEMU | The shared display oracle passed on esp32sim. Matched panel plus SD and reviewer endpoint qualification remains open. |
| `papermono` | 2/2 reads, power, charger, imu, rtc | — | 2/2 | 2/2 | QEMU | The paired PM1 and charger fixture did not complete. A same-input replay requires the original SD and preboot charger state. |
| `papers3` | 2/2 reads, panel | — | — | — | QEMU | No shared oracle case. The panel state read passed. The same-input visual plus reviewer endpoint expansion remains open. |
| `stackchan` | 2/2 reads, power, imu, magnetometer, power-monitor, light-proximity, rtc, body-touch, io-expander, servo-yaw, servo-pitch | — | 2/2 | 2/2 | QEMU | The `key:a` request in the body-touch fixture returned not_supported_on_runtime. Native typed servo and board-state reads passed. |
| `stamplc` | 2/2 reads, temperature, power-monitor, rtc, io-expander, front-panel | — | 0/2 | 2/2 | QEMU | The paired guest fixture did not emit the relay press or INA226 value marker. The LM75 preboot ordering remained outside the leased replay. |
| `stickc` | 2/2 reads, imu | — | 2/2 | 2/2 | QEMU | Shared oracle passed on both. Full guest-side legacy IMU write and consumer qualification remains open. |
| `stickc-plus` | 2/2 reads, imu | — | 22/22 | 22/22 | QEMU | Shared oracle passed on both. Full guest-side legacy IMU write and consumer qualification remains open. |
| `stickc-plus2` | 2/2 reads, imu, rtc | — | 4/4 | 4/4 | QEMU | Shared oracle passed on both. UIFlow live admission still uses QEMU and the reviewed IMU and RTC write cases remain open. |
| `sticks3` | 2/2 reads, power, imu | — | 4/4 | 4/4 | QEMU | The paired firmware did not emit the expected battery value. Its IMU predicate also needs the firmware-specific axis substitutions in the direct runner. |
| `stopwatch` | 2/2 reads, power, expander, imu | — | 4/4 | 4/4 | QEMU | The PM1 full guest fixture failed to emit STOPWATCH_M5PM1_DONE PASS while QEMU passed the direct fixture twice. |
| `tab5` | No registered components | — | — | — | Qualified firmware/panel pairs use esp32sim | The forced native frame reviewer returned SIM_PARTIAL, and the legacy stereo recording cursor and retained windows remain unavailable on native. |

QEMU passed all 13 checked-in direct state fixtures twice. The separate leased replay attempted 13 fixtures twice per runtime. It did not qualify guest parity. Some leases failed during admission or cleanup, and the replay could not apply the original preboot setup. The [state fixture summary](evidence/state-fixture-summary.json) retains outcomes, missing guest markers and setup limits. Successful state reads alone are a narrower result than guest execution.

## Tab5

The same v2.5.3 and v2.5.4 binaries, GT911/ILI9881C and ST7123 panels, and touch location were exercised twice on both runtimes. All eight esp32sim runs exposed TOOLS and ADC after touch. QEMU exposed both on all four ST7123 runs and produced no complete GT911 DSI frame in four trials. The v2.5.4 file is the raw #188 input. The #226 Maker Fighter firmware reached its HID-driven menu in the native CLI suite. A retry with a fresh-frame wait delivered HID input on both native runs. Frames updated, and the post-input menu markers were absent. The QEMU comparison had no usable frame and logged DWC assertions.

The standalone suite emitted 22 PASS cases across 28 labels. Four inputs or build receipts were missing, and two labels have no pinned independent docs sketch. Those six labels are recorded as NOT RUN. The suite does not constitute the full paired 25-case gate.

## Firmware reviewer with runtime map enabled

The saved-snapshot replay covered both job types eligible for the flag and two Tab5 comparisons. Only the forced comparisons overrode the pinned runtime decision. Submission was disabled. The resident flag was left off.

| Job | QEMU/esp-emu | esp32sim |
| --- | --- | --- |
| `sd_read` | `SIM_VERIFIED` | `SIM_VERIFIED` |
| `dial_encoder` | `SIM_PARTIAL` (`E_INTERACTION_CLAIM_PARTIAL`) | `SIM_PARTIAL` (`E_INTERACTION_CLAIM_PARTIAL`) |
| `tab5_frame_review` | `SIM_VERIFIED` | `SIM_PARTIAL` (`E_SIM_OBSERVATION_INCOMPLETE`) |
| `tab5_speaker_review` | `SIM_PARTIAL` (`E_TAB5_SPEAKER_PARTIAL`) | `SIM_PARTIAL` (`E_SIM_OBSERVATION_INCOMPLETE`) |

The speaker run did not recover a usable window on esp-emu. An independent legacy UserDemo run returned a live cursor with 62,784 bytes and retrieved a 4,096-byte quiet stereo window after stop using the same recording ID. The native cursor returned `invalid_audio_range`. The retained-window check does not establish guest playback. Other reviewer job families did not receive paired executable coverage on the candidate. The pinned reviewer unit suite passed 369 tests.

## Regression and release

The fork workspace passed 2,047 Rust tests after restoring the pinned test assets. Native and WASM clippy passed. Four sentinel workloads preserved counters and serial outputs across three pairs. Under concurrent host load, Pocket Tank median user time rose from 7.44 s to 7.98 s. CoreS3 passed 15/15 and Cardputer-ADV passed 11/11. Some standalone batch cases and two Cardputer-ADV LoRa peer runs remained unresolved. Restricting to the radio evidence collected here, Nesso N1 received 14 peer packets, the isolation control received zero and PaperMono received four. The PaperMono replay used the archived standard SD seed. Virtual results cover emulated guest behavior.

Use the repository's `scripts/bootstrap-esp32sim-runtime.py` with the candidate's runtime lock. Start an isolated Device Service with the same assets. Run `tests/firmware/arduino_docs/run_service.py` on both runtimes for both trials. The direct state fixtures use `tests/uiflow2/run_profile_ui_test.py` and the profiles' checked-in QOM sequence and serial predicates. For the C6 path, compose the fork's C6 station or SoftAP unit firmware at ESP-IDF flash offsets 0, 0x8000 and 0x10000. Use restricted leases, record the guest association and DHCP lines, retrieve evidence with `include=serial,logs,network`, and stop with `purge=0`. A fresh Tab5 frame followed by the tools and ADC menu after a held touch is the stock acceptance signal.

The exact Device Service head completed the Python 3.12 platform suite with 2,596 tests and nine skips. Runtime coverage, peripheral catalog, QEMU profile and snapshot validators, PR scope and the source diff check all passed.

The release gate is PARTIAL. The default expansion, PR, production cutover and rollout pruning were not executed. No production rollback was needed. The preceding synchronized rollout remains the known deployed baseline for this task. The branch contains opt-in candidate changes so qualification can continue against the exact source above.
