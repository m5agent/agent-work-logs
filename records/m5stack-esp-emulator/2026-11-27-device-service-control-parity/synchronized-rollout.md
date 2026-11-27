# Device Service default migration and synchronized rollout

2026-11-27. Virtual-device validation.

[PR #291](https://github.com/m5agent/m5stack-esp-emulator/pull/291) merged
`0fadb21401135ef0d14dc05a5b317768d0edb304` as
`6f138dc9c49e61ac6e6e6af72f4fd3047a2d1005`. Both GitHub checks passed and no
review threads remained open. Python 3.12 ran 2,592 tests with 11 skips. The
four validators, PR scope check and whitespace check passed.

Rollout `6f138dc9c49e61ac6e6e6af72f4fd3047a2d1005-esp32sim-service-defaults-20261127`
uses fork pin `9c0447e8e38d0bafc2f124e6e8b8cc5994d30eee`. Its exact native
binary SHA-256 is `f87e8de04a6a631e8ea551b3512ae719ccc8fffcf9f76b18ba020220c149bf91`.
The P4 binary is `5c8b6fb77cb9c2edebb9e76610263e74c553e212c31f96ac9d43ca808e9bf499`.

| Operation | Time UTC | Readback |
| --- | --- | --- |
| Primary Device Service and gateway | 2026-11-27 14:19:25.910806 | Ready on the merged source, with the same configured browser manifest and state. |
| Firmware-review Device Service | 2026-11-27 14:19:26.863737 | Ready on the same source. Original launcher and reviewer configuration backed up. |
| Cardputer SD dry-run and all-surface check | 2026-11-27 14:21:07.276932 | `SIM_VERIFIED`, `runtime=qemu`, `submit_requested=0`. All surfaces reported 36 rows and 35 ready esp32sim models. |

The nine new ordinary defaults are Atom Lite, Atom Matrix, Atom Matrix v1.1,
AtomU, Atom Echo, Cardputer K132, Core2, Dial and StickC Plus SE. Thirteen
ordinary devices now select esp32sim. The qualified Tab5 firmware and panel
pairs use their existing conditional selection. The other 21 ESP32 devices
default to QEMU for the concrete gaps below. CardputerZero uses the Linux path.

The isolated assembled rollout passed ten omitted-runtime probes and both
saved review job types in each flag state. The resident reviewer flag is
off. The established QEMU and specialized reviewer lanes remain explicit.
The gateway keeps its existing browser assets.

### Rollback

The rollout holds both verified launch inputs, the original gateway
configuration, the prior review worker launcher and the reviewer
configuration backup. With `ROLLOUT_DIR` set to the active rollout directory,
wait for the review queue and Device Service leases to drain and run:

```sh
python3.12 "$ROLLOUT_DIR/review_worker_cutover.py" rollback "$ROLLOUT_DIR"
python3.12 "$ROLLOUT_DIR/cutover.py" rollback "$ROLLOUT_DIR"
```

The two exact interpreter commands are in the release directory. The
second operation restores the gateway as well as the primary Device Service.
[Qualification and cutover receipts](evidence/synchronized-rollout.json).

## Per-device results

PASS, FAIL and MIXED count the same selected Arduino service oracles, twice per runtime.
A zero case count indicates no selected service oracle for that row. Stock UIFlow2,
checked-in fixtures, consumer probes and standalone fork oracles are separate evidence.

| Device | Paired docs cases | esp32sim PASS / FAIL / MIXED | QEMU PASS / FAIL / MIXED | Ordinary default | Endpoint compatibility or retained gap |
| --- | ---: | --- | --- | --- | --- |
| atom-echo | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim | Omitted runtime, original REPL, digital audio and watcher HTTP passed. |
| atom-echos3r | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `GET /device-state` returns 409. The legacy route registers `onboard-io` and `es8311`; its fixture returned an empty map. |
| atom-lite | 4 | 4 / 0 / 0 | 4 / 0 / 0 | esp32sim | Omitted runtime, original REPL and watcher HTTP passed. |
| atom-matrix | 4 | 4 / 0 / 0 | 4 / 0 / 0 | esp32sim | Omitted runtime, original REPL and watcher HTTP passed. |
| atom-matrix-v11 | 4 | 4 / 0 / 0 | 4 / 0 / 0 | esp32sim | Omitted runtime, original REPL and watcher HTTP passed. |
| atoms3 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU | `GET /device-state` lacks `imu`; native `uiflow-live` is unavailable. |
| atoms3-lite | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `GET /device-state` lacks `onboard-io`. |
| atoms3r | 2 | 2 / 0 / 0 | 0 / 2 / 0 | QEMU | `GET /device-state` lacks `imu`, `led` and `magnetometer`; native `uiflow-live` is unavailable. |
| atoms3r-cam | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `GET /device-state` lacks `gc0308`. |
| atoms3r-m12 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `GET /device-state` lacks `ov3660` and `m5-lcd-cam`. |
| atoms3u | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `GET /device-state` lacks `onboard-io` and `rmt0`. |
| atomu | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim | Omitted runtime, original REPL, digital audio and watcher HTTP passed. |
| basic-v27 | 2 | 2 / 0 / 0 | 0 / 2 / 0 | QEMU | `GET /device-state` lacks `ip5306`. |
| cardputer | 2 | 2 / 0 / 0 | 2 / 0 / 0 | esp32sim | Omitted runtime, original GPIO0 menu, watcher HTTP and both reviewer SD routes passed. |
| cardputer-adv | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim | Previously migrated ordinary path; legacy reviewer programming and network profiles are explicit. |
| cardputer-zero | 0 | 0 / 0 / 0 | 0 / 0 / 0 | External Linux | The catalog row is BCM2837/ARM64 and uses its separate Linux service. |
| core2 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | esp32sim | Omitted runtime, exact stock Home, touch, FT6336 A/B/C, REPL and watcher HTTP passed. |
| cores3 | 6 | 6 / 0 / 0 | 5 / 1 / 0 | esp32sim | Previously migrated ordinary path; stock fixture, Flash, QOM and restricted STA exercised. |
| dial | 3 | 3 / 0 / 0 | 3 / 0 / 0 | esp32sim | Omitted runtime, stock encoder, watcher HTTP and both reviewer encoder routes passed. |
| m5stick | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim | Previously migrated native-only Device Service path. |
| nanoc6 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `POST /sessions` rejects `network.profile=nanoc6-hci-ble` on esp32sim. |
| nesso-n1 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `POST /sessions` rejects `network.profile=nesso-unified` on esp32sim. |
| papercolor | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU | `GET /device-state` lacks `power` and `sensor`. |
| paperdiy | 1 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | `GET /device-state` lacks `panel`. |
| papermono | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU | `GET /device-state` lacks `charger`, `imu`, `power` and `rtc`. |
| papers3 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | QEMU | `GET /device-state` lacks `panel`. |
| stackchan | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU | `GET /device-state` only returns servos. Eight legacy components are missing. |
| stamplc | 1 | 1 / 0 / 0 | 0 / 1 / 0 | QEMU | `GET /device-state` lacks `front-panel`, `io-expander`, `power-monitor`, `rtc` and `temperature`. |
| stickc | 1 | 1 / 0 / 0 | 1 / 0 / 0 | QEMU | `GET /device-state` lacks `imu`. |
| stickc-plus | 11 | 11 / 0 / 0 | 11 / 0 / 0 | QEMU | `GET /device-state` lacks `imu`. |
| stickc-plus-se | 2 | 2 / 0 / 0 | 0 / 2 / 0 | esp32sim | Omitted runtime, two paired UIFlow2 fixtures and watcher HTTP passed. |
| stickc-plus2 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU | `GET /device-state` lacks `imu` and `rtc`; native `uiflow-live` is unavailable. |
| sticks3 | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU | `GET /device-state` lacks `imu` and `power`; native `uiflow-live` is unavailable. |
| stickt2 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | esp32sim | Previously migrated native-only Device Service path. |
| stopwatch | 2 | 2 / 0 / 0 | 2 / 0 / 0 | QEMU | `GET /device-state` lacks `expander`, `imu` and `power`; native `uiflow-live` is unavailable. |
| tab5 | 0 | 0 / 0 / 0 | 0 / 0 / 0 | Firmware/panel dependent | Qualified omitted-runtime lease passed. The legacy UserDemo stereo `GET /audio.pcm?format=cursor` and retained recording ID keep esp-emu. |

The selected matrix totals 56 esp32sim passes and 47 QEMU passes, with nine
QEMU failures and zero mixed cases. [Paired case identities](final-pin-doc-matrix.md).

[Consumer route follow-up](default-routing-follow-up.md) · [Stock and timing](expanded-paired-qualifications.md).

### Retention

The active release and its two immediate rollback releases are verified.
Two additional directories are referenced by other running services. A third
supplies QEMU and Python assets to the older retained rollback configuration.
These references prevent removal of those three resident directories.

Cleanup removed 32 task-owned, archived candidate directories with 9.55 GiB
of measured allocation. The data volume reported 67% used afterward. All
three live surfaces passed another source and health readback at
2026-11-27 14:24:55.403420 UTC.
