# Device Service consumer compatibility

The GitHub reply watcher reads the top-level device catalog and uses
`creatable`, `peripheral_status` and `display`. Its review prompt directs
the reply agent through firmware intake, lease creation, serial and screen
evidence. The deployed firmware reviewer reads the same catalog, selects
explicit runtime values and applies job-specific assertions on the leased
guest. The reviewer worker can enable the legacy catalog view so its
top-level capability checks follow the runtime it selects.

| Operation and parameters | esp32sim (workbench default where selected) | Reviewer worker with explicit QEMU or network runtime |
| --- | --- | --- |
| `GET /devices`, device and capabilities reads | Runtime and per-backend readiness are reported. M5Stick and StickT2 are available when their native assets are ready. | Legacy creatable and feature discovery, plus per-runtime readiness. The old reviewer previously had no M5Stick or StickT2 QEMU lease. |
| `POST /artifacts`, `POST /firmware`, firmware analysis | Standard uploads, normalization and target admission. | Standard artifact routes, app-only boot-context checks and normalized SHA. |
| `POST /sessions` with stored firmware, TTL, ready options | Supports plain, controller-validated esp32sim leases. Existing Tab5 conditional firmware/panel selection applies. | Reviewer supplies `runtime=qemu`, `qemu-wifi`, or another advertised network lane. QEMU-only `units`, NVS, filesystem, SD and network fields use their established admission checks. |
| `GET /sessions/{id}`, `POST /wait`, `GET /events` | Supports the common lease contract. Readiness can include guest markers and framebuffer conditions. | Same paths on the selected runtime. |
| `POST /input`, touch, keyboard, encoder, hold timing | Typed input depends on device wiring. Device-specific QEMU-only input paths require QEMU. | Supported input, drag, encoder and explicit review assertion paths depend on the board profile. |
| `GET /frame.png?max_age_ms=0` | Supported for modeled displays. Geometry comes from the board frame, including raw Tab5 panel orientation. | Supported on admitted display paths. Tab5 capture status uses its pinned DSI firmware and panel. |
| `GET /serial?offset=&limit=`, optional channel and `logs` reads | Supports bounded cursor reads. USB serial is exposed when captured. | Same cursor contract. |
| `GET /network`, review STA, provisioning, packet capture | Trusted-host NAT can use esp32sim STA. Reviewer QEMU-specific profiles require their respective network runtimes. | Review STA, isolated AP portals and PCAP remain the explicit runtime profiles advertised by the same worker. |
| `GET /device-state`, `GET /qom/list`, `POST /qom-snapshot`, `GET /qom/diff` | StackChan offers typed servo state. Generic QOM requires QEMU. | QOM snapshots and diff use the QMP runtime. State probes remain device-dependent. |
| `POST /flash-snapshot`, `GET /flash/diff`, `GET /flash?format=sha256` | Live Flash is volatile and its QEMU snapshot contract is unavailable. | Supports the review snapshot path where admitted. |
| `GET /crash` with optional ELF | Collects retained guest serial/logs. Native QEMU-specific dump and core-frame decoders retain their own admission. | Crash receipt is bound to the session, firmware and matching ELF when provided. |
| `GET /storage/sd`, `read-stats`, `write-stamp`, media export | Preboot media and retained export on modeled slots. QEMU controller counters and hot-plug are unavailable. | Continues SD write-stamp and read-stats for admitted controllers. Empty, unsupported and unready cases use typed errors. |
| `GET /audio.pcm` cursor, metrics and bounded evidence windows | Modeled session i2s PCM capture. The reviewer's native QEMU and Unit audio contracts select explicit QEMU. | Uses native i2s, permitted Tab5 audio and QEMU Unit playback where advertised. |
| `GET /evidence?include=…`, `DELETE ?purge=0` | Standard retained evidence and stop. Power-off includes its terminal board frame. Pair evidence includes both leases. | Preserves session ZIP and stopped history. Member evidence from the new pair API is additive. |

The reviewer discovery comparison covered 36 catalog rows. The candidate
preserved existing creatability, feature flags, machine and network profiles
in legacy view. Unsupported M5Stick and StickT2 report QEMU readiness false
in this view. The watcher flow used the ordinary catalog and omitted
`runtime` for both native-only boards.

## Device routing

The default column of [the per-device comparison](per-device.md) applies to
workbench and watcher leases. For every QEMU-default row, the reviewer selects
explicit QEMU or a device-advertised network lane. CoreS3 and Cardputer-ADV
have full legacy discovery on the dedicated reviewer worker and can use
explicit QEMU for its QOM, Flash and storage fields. Tab5 keeps its old
reviewer's explicit QEMU/esp-emu, DSI, SDMMC and audio rules. M5Stick and
StickT2 have no reviewer QEMU admission. CardputerZero has the external
Linux path.

The [36-row catalog/capability matrix](evidence/device-api-compatibility.json)
records the advertised default, frame/input/QOM/storage flags, reviewer
QEMU readiness, review STA and every advertised network profile per board.
[Executed review cases](rollout.md#reviewer-fixture-outcomes) record the
functional checks and partial outcomes separately from capability reads.
