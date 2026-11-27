# AtomU and Atom Echo candidate defaults

2026-11-27. Virtual-device validation. The reviewable candidate uses
esp32sim `1bde80f2472c4b4763a66fde63fad9fb4906a7ae` with the Device Service
control overlay. The source change for default selection is
`48da02cf59e44dc70e3a0199130373da26656f92`. The resident rollout is pending.

| Gate | AtomU | Atom Echo |
| --- | --- | --- |
| Arduino catalog cases | No board-specific cases in the pinned document inventory | 3 original examples fail compilation on the pinned library. All three remain DOCS-DEFECT |
| Uncomposed stock UART REPL, board, GPIO39 and RGB | 2/2 esp32sim and 2/2 QEMU, board 130, LED 0x204060 and 0→1→0 | 2/2 esp32sim and 2/2 QEMU, board 142, LED 0x204060 and 0→1→0 |
| Stock launcher | The separately hashed M5Burner catalog image includes M5Things | The GitHub v2.5.4 release omits M5Things on both runtimes, before the guest reaches REPL |
| Original-driver PDM samples | 6/6 per runtime for silence, 733 Hz and 1234 Hz | 6/6 per runtime for the same inputs |
| Speaker PCM | Board without speaker | Both trials per runtime observed 175 positive zero crossings and 440.042 Hz at 48 kHz |
| Checked-in console fixtures | 2/2 per runtime, including Grove scan and actual button input | 2/2 per runtime, including Grove TMP105, absence of ES8311 and captured PCM |
| Standard HTTP and evidence | 2/2 per runtime | 2/2 per runtime |
| Candidate ordinary default | Both omitted-runtime leases selected esp32sim | Both omitted-runtime leases selected esp32sim |

The timed path starts at the lease request and ends at a MicroPython startup
marker. AtomU took 1.640–1.746 s on esp32sim and 12.101–12.968 s on QEMU.
Atom Echo took 0.899–1.273 s on esp32sim and 7.427–7.672 s on QEMU. Both
comparisons use QEMU host-image Flash transport on the same macOS arm64 host.
The Echo timing measures time to REPL after the shared launcher defect.

Reproduction starts with the stock image SHA in the companion JSON. Create the
lease with `program_transport=uart-repl`, wait for MicroPython, and run the
stock `M5.begin()`, GPIO27 `hardware.RGB` and `M5.BtnA.isPressed()` APIs.
Use `POST /input` for GPIO39 down/up and check serial plus
`GET /device-state`. Provide 16 kHz PCM16 silence and the two tones as
session-local source media, check the guest's distinct microphone sample
statistics and recover the Echo tone from `GET /audio.pcm`. The checked-in
fixtures are in `tests/uiflow2/atomu_console_test` and
`tests/uiflow2/atom_echo_console_test`.

For watcher endpoint compatibility, both runtimes accepted the same firmware
upload, normalization and analysis. The eight leases verified readiness and
events, serial cursor, button state, QOM GPIO change and diff, two 4 MiB Flash
snapshots and diff, crash receipt and evidence ZIP member digests. Offline
network evidence is DISABLED on esp32sim. QEMU returns its existing typed
409 for the offline lease. Neither model is listed for a job-specific firmware
reviewer plan. Explicit QEMU and omitted-runtime legacy runtime environment,
persistent identity and NVS requests were each exercised twice per device on
the candidate. All 20 leases produced retained evidence and stopped.
Unit and filesystem fixture requests route to QEMU under the same condition.
Those two request variants were NOT RUN on these boards in this replay.

## PaperColor fixture readiness

An initial display can already show six colors while the guest is still
waiting for its last synchronous e-paper draw. On the same application with
an end-of-draw marker, both trials on both runtimes emitted
`PAPERCOLOR_PROBE_READY` before a 1.25 s key A hold and then
`PAPERCOLOR_BTN_A 1`. The pixel at (270, 160) changed from white to black.
The earlier misses are retained as fixture timing failures.

[Hashes, scoped observations and cleanup receipts](evidence/stock-classic-and-papercolor-summary.json)
· [Stock image and document-defect provenance](https://github.com/m5agent/agent-work-logs/tree/3b0ec43e686f08040ef7e39caddba854a1ca7a6b/records/esp32sim/2026-11-27-lx6a-stock-receivers).
