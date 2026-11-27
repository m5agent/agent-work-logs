# Catalog Board Device Service qualification

## Runtime and scope

The Device Service candidate uses esp32sim
`4e257b6be8ee0ed706c2e509d8f31ef7472a424b` with a pinned private-control patch.
It exposes 35 board models and retains the established default selection.
Cardputer K132 adds an explicit esp32sim browser engine while its QEMU-WASM
default remains available. CardputerZero is outside the ESP32 lane.

## Native virtual-device validation

The stock run uploaded each matching original merged firmware, created its
board record, and allocated a separate `/api/v1/sessions` lease for each
available runtime. The QEMU lane used the stable host-image Flash preparer.
Readiness here means Device Service entered running. Fresh panel/LED PNGs,
serial channel output, typed input responses and the evidence ZIP were
collected before DELETE with `purge=0`. The summaries use firmware, executable,
ROM, frame and evidence hashes. Original session identifiers, host paths
and raw guest logs are excluded.

35 esp32sim stock leases reached running and stopped. The two classic
M5Stick and StickT2 QEMU matrix modes have no Device Service session admission.
Tab5's first legacy comparison attempt lacked the separate legacy assets.
Atoms with no panel can return frame_unavailable. The captured launcher
ImportError for AtomU/Atom Echo points to the stock M5Things issue. Build
or service readiness alone does not qualify a default change. Stock home
pixels, per-case peripherals, REPL and deterministic repeats remain separate
checks. The provided UIFlow2 fixture images were composed from checked-in
rules and shares of the same stock artifacts in each service lane.
Docs coverage is still PARTIAL.

## Browser virtual-device validation

The exact source-built WASM and S3 ROM received CoreS3 and ADV regression
images, plus the original Cardputer K132 keyboard example and stock UIFlow2.
The export was tested in an iframe on a different origin without cross-origin
isolation. Keyboard matrix/GPIO0 or touch inputs reached the guest where
the case required them, and the panel changed. Each passing case ended
with zero Dedicated Worker targets.

Other new browser board profiles are NOT RUN for admission. They need the
workbench's own firmware/ROM, board input/observable output and cleanup
checks. Physical validation is NOT RUN.

## Independent radio evidence

The following fork record verifies synchronized LoRa/SX1262 and CC1101 payloads
under loaded and unloaded conditions. The adapter uses one guest per lease.
[Radio evidence](https://github.com/m5agent/agent-work-logs/tree/c2f333ff576220a0a22c8460297f772c00037be4/records/esp32sim/2026-11-27-radio-peer-synchronization)

## Reproduction and delivery boundary

Use Python 3.12+, the pinned ESP32/S3/C6/P4 ROM ELFs and the matching Tab5
C6 bundle. Build with `CARGO_PROFILE_RELEASE_LTO=false python3 scripts/bootstrap-esp32sim-runtime.py --with-classic --with-tab5 --rom-dir "$ROM_DIR"`.
Run `platform/tools/serve.py` on an isolated bind and separate state directory.
Upload the source artifact as octet-stream, register it with
`kind=merged`, then request both runtimes with the same firmware ID.
Basic v2.7 uses `runtime_variant=flash-4mb` for the matching 4 MiB stock bytes.
Read `serial`, `frame.png?max_age_ms=0`, `input`, then `evidence` before stop.
For the WASM lane, build with `platform/tools/bootstrap_browser_runtime.py`,
export with `platform/tools/build_public_site.py`, and use
`platform/tests/test_public_esp32sim_guest.mjs` with the same source hashes.

This qualification record precedes merge and rollout. Service cutover and
hosted Pages verification are separate delivery steps.
