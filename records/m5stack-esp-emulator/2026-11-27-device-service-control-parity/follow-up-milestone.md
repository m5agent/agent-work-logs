# Device Service parity control follow-up

2026-11-27. PARTIAL. Virtual-device validation with same-firmware QEMU and
esp32sim sessions. The complete catalog migration remains open.

The [merged fork milestone](https://github.com/m5agent/esp32sim/commit/1bde80f2472c4b4763a66fde63fad9fb4906a7ae)
has the same Git tree as the tested
[9eeb9a61 milestone](https://github.com/m5agent/esp32sim/commit/9eeb9a61e64cd3d3de6e4262fac13b8a3dc2f34d).
The Device Service control overlay additionally records Dial encoder delivery
at the GPIO boundary. The exact fork, overlay, binary and P4 identities
are recorded in the [trial summary](evidence/follow-up-milestone-summary.json).

| Fixture or check | QEMU | esp32sim |
| --- | --- | --- |
| AtomS3R-CAM checked-in UIFlow2 camera | 2/2 | 2/2 |
| AtomS3R-M12 checked-in UIFlow2 camera | 2/2 | 2/2 |
| Atom Echo checked-in console, PCM, buttons and RGB | 2/2 | 2/2 |
| Basic v2.7 checked-in console, buttons and PMIC no-cell fixture | 2/2 | 2/2 |
| Core2 pinned v2.5.3 stock Home and Settings navigation | 2/2 | 2/2 |
| Core2 same-base UART-REPL program and separate A/B/C press and release | 2/2 | 2/2 |

The camera probes drove active-low GPIO18 before SCCB lookup. M12 checks
its sensor address independently of other I²C device placement. A write to
the existing camera sequencing property followed the guest baseline marker.
Both graphs delivered five distinct guest frames and matched the baseline
RGB565 geometry checks. The earlier unsupported sequencing trials are
retained separately.

The Atom Echo trials provided the same deterministic 16-bit mono microphone
samples. Both runtimes reported a non-silent guest recording and controller
RGB [32, 64, 96] with five updates. Basic v2.7 observed SYS 0xb9 and charge
current 0x01 on both runtimes. Both reported no battery cell. QEMU reported
READ0 0x08 and esp32sim reported 0x00 under that condition. The two device
leases used the legacy Grove TMP105 compatibility fixture. The raw register
difference and the earlier failures are retained.

Flash live readback, retained Flash, QOM diff and hashed telemetry members
passed on the new control milestone. Restricted STA obtained a guest DHCP
lease. Link and radio fault transitions were verified in the live model
state. The test did not verify full guest reconnect after each transition.
The prior legacy reviewer discovery fields matched across 36 catalog rows
after staging the pinned Tab5 assets. The normal catalog showed additive
control fields on existing esp32sim defaults.

The unchanged reviewer code rejected native Dial encoder and Cardputer SD
assertion identities. In the isolated reviewer candidate with the explicit
runtime guard, both QEMU and esp32sim observed 3 encoder detents and 12
delivered GPIO edges. Cardputer reported completed SPI response blocks and
passed the preserved SD assertion. Initial saved-snapshot jobs verified
Cardputer on both runtimes. Dial recorded encoder PASS and outer
SIM_PARTIAL with an extraneous raw key probe on both runtimes.

Tab5 qualified stock-image Flash snapshots matched on both runtimes. The
DSI route produced a QEMU QOM-snapshot error. The native QOM snapshot
returned live modeled state. Native panel boot and qualified speaker,
USB storage and DSI receive checks remain separate gates.

An isolated Core2 UART-REPL lease used the same stock base with the
service-generated bootstrap. The original Home/Settings test used the
unmodified stock image. Each assertion was measured in its own lease and
bound to its firmware and runtime identity. Physical devices were NOT RUN.

## Corrected reviewer saved-snapshot run

The Dial fixture supplied the same encoder options without treating the
semantic rotary action as a raw key name. The prior combined request had
added a second unrelated raw key probe. The Cardputer job retained the same
SD image and minimum completed-block threshold.

| Saved-snapshot job | Flag off | Flag on |
| --- | --- | --- |
| Dial encoder | QEMU, SIM_VERIFIED | esp32sim, SIM_VERIFIED |
| Cardputer SD read | QEMU, SIM_VERIFIED | esp32sim, SIM_VERIFIED |

All four jobs reported submission disabled. The Dial job observed three
delivered detents and 12 GPIO transitions. The isolated reviewer suite passed
369 tests. The default-off reviewer change is staged separately from the
Device Service source. This execution did not update resident services.
