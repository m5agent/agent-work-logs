# Device Service parity milestone

The catalog admission rule requires two stable paired runs per case and
compatibility with the endpoints used by the watcher and reviewer. The results
here cover individual capabilities and selected cases.

## Checks

| Area | Virtual-device observation |
| --- | --- |
| Live and final Flash | CoreS3 ran an actual MicroPython file write between snapshots. The HTTP diff reported changed bytes and retained stop returned a complete 16 MiB readback. |
| Modeled state | The API listed modeled paths, sampled guest cycles, stored snapshots and reported a positive cycle delta through the diff endpoint. ZIP member hashes matched for Flash, modeled state and telemetry. |
| Restricted STA | CoreS3 reached the guest association marker, obtained a modeled DHCP ACK and exported a PCAP. |
| SPI SD | Cardputer and Cardputer-ADV guest controllers delivered 6 and 41 complete response blocks in the sampled windows. Removal reported an empty controller with zero counters, and reinsertion changed attachment identity. |
| SD ejection at boot | PaperDIY started with its prepared card ejected. The legacy property path inserted, removed and reinserted the same media. The write-stamp endpoint rejected the ejected state and returned a fresh media identity after reinsertion. |
| StopWatch | The 466×466 panel and checked-in touch fixture passed twice per backend on the aperture milestone. The previous esp32sim size was 468×466. |
| PaperMono | An initial window ended before the fixture completed its synchronous startup drawing. After observing the initial UI, a one-second hold at (240,650) changed (440,30) from white to black twice on each backend. |
| PaperColor | Both observed the white phase and six colors. QEMU reached the palette in about 2.1 s. esp32sim reached it in 15.8–16.6 s, consistent with the [modeled ED2208 BUSY window](https://github.com/m5agent/esp32sim/blob/a6216b68abda3af76f6f491f940fbf0e4e8a42f7/docs/control-protocol.md#e-paper-readiness). |
| CoreS3 UIFlow2 fixture | An earlier composed image missed the startup marker in both backends. The exact checked-in fixture source ran through the service UART REPL on the manifest-imported v2.5.3 base. Both backends logged the touch and produced the green (2,2) pixel in both trials. |

The first SD stamp attempt inherited the legacy QEMU process ownership check.
The follow-up used the owned esp32sim process identity. Both observations are
retained in the HTTP summary. Serial, private paths, session identifiers and
raw ZIP members are omitted from the public summaries. Firmware, executable,
sample counts, frame conditions and ZIP hashes are preserved.

The AtomS3R-CAM and M12 fixtures require the existing camera auto-increment
property after the guest's base-capture marker. With that operation restored,
QEMU passed both trials for each device. The candidate esp32sim API rejected
the same operation in both trials for each device. Earlier runs without the
marker-driven operation remain in the matrix summary. These camera-dependent
paths are a concrete migration blocker.

## Reproduction

Provision the pinned native binaries and ROMs with the project's bootstrap
recipe and service control overlay. Start a dedicated Device Service with its
own state and control credential. The QEMU comparison used host-image Flash
initialization. Register exact firmware bytes through the artifact and firmware
endpoints. For each trial create a lease with an explicit runtime, bind the
firmware hash from the receipt and retain the evidence ZIP before stopping
with `purge=0`. Arduino panel predicates use the fixed [CoreS3 checker](https://github.com/m5agent/esp32sim/blob/4e257b6be8ee0ed706c2e509d8f31ef7472a424b/tools/check_cores3.py),
[S3-B checker](https://github.com/m5agent/esp32sim/blob/4e257b6be8ee0ed706c2e509d8f31ef7472a424b/tools/check-s3b-docs.py),
[classic checker](https://github.com/m5agent/esp32sim/blob/4e257b6be8ee0ed706c2e509d8f31ef7472a424b/tools/check-lx6-cores.py)
and [e-paper checker](https://github.com/m5agent/esp32sim/blob/4e257b6be8ee0ed706c2e509d8f31ef7472a424b/tools/check-paper-docs.py).
The visual trials report PARTIAL where the direct checker also requires
controller telemetry or exact guest-time checkpoints.

Flash validation steps use `/flash-snapshot`, `/flash/diff`,
`/qom-snapshot` and `/qom/diff`. Include `qom,flash,telemetry` in the
evidence selection. Send `retain_flash=1` with stop and read the final digest.
The SD counter fixture uses the archived SD examples and one prepared image.
Sample `/storage/sd/read-stats` across the read and removal. Verify the
empty negative control and the new media identity on reinsertion.

## Release boundary

PARTIAL for the whole catalog. The complete docs suites, stock home/input/REPL
checks, reviewer job semantics and cutover gates remain open. Existing QEMU
Unit and named reviewer network profiles still require their admitted runtime.
The milestone protocols are additive and remain gated by the pinned runtime.
