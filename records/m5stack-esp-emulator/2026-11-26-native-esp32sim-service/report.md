# Native Device Service integration and validation

CoreS3 and Cardputer-ADV now select esp32sim when the session request omits the runtime. The original QEMU profiles remain explicit selectors. Other device defaults follow the existing catalogs. The service launches one ROM-booted child per lease. It uses an inherited Unix stream with the simulator's frame and audio wire formats. The same worker owns serial capture, input dispatch, scheduler-bound RGB565 samples, TTL cleanup, and evidence retention.

The host provisions a Cargo-locked simulator build from the published service-control pin. The service checks the binary and ROM digest, the board handshake, and firmware geometry before accepting a result. The configured board memory is 16 MiB Flash and 8 MiB PSRAM for CoreS3, and 8 MiB Flash with zero PSRAM for Cardputer-ADV. QEMU metadata and the migrated native backend are declared separately. Static browser overlay admission checks the export manifest, member length/hash, runtime/profile coverage and declared engine assets.

## Reproduction

1. Use Device Service commit `b95ca421d327120dd43f2b48e856d71e903508ef` on the migration base. The local source branch is stored for integrator handoff.
2. Run `python3 scripts/bootstrap-esp32sim-runtime.py --rom-dir <rom-directory>` with an operator-provided ESP32-S3 mask ROM. The native build pins [e374bdff519450cb3202b02cd5f40868a6961a38](https://github.com/m5agent/esp32sim/commit/e374bdff519450cb3202b02cd5f40868a6961a38).
3. Start Device Service on an isolated port and state directory. Upload the exact merged docs images, then POST the uploaded artifact to the firmware registration route and create a session. The [summary](evidence/api-summary.json) pins the individual firmware, runtime, frame and ZIP identities, along with each HTTP input.
4. Read frame PNG with `max_age_ms=0`, capture serial and any audio metrics, and fetch the evidence ZIP before stopping with `purge=0`. PCM uses the native captured sample rate. Verify ZIP members against the manifest's SHA-256 and length. Terminal sessions must release the worker lease with history retained.
5. Repeat the explicit `runtime=qemu` CoreS3 control and run StopWatch UIFlow2 with the pinned freeze rollout and host-image Flash provisioning.

## Final verification

The Python 3.12 platform suite ran 2,580 tests across four shards with 11 skips,
zero failures and zero errors. Coverage, peripheral catalog, profiles and project
snapshot validators passed. Rust web tests passed 12 cases and native Clippy
passed for the two modified crates.

The UIFlow2 v2.5.3 touch probe injected panel coordinates (137, 101) through
HTTP after its guest-ready marker. With guest rotation 1, UIFlow2 reported
both logical and raw coordinates (137, 101). The earlier rotation-0 run
reported logical coordinates (138, 137). Both runs completed the guest
program and retained their ZIPs before releasing the lease.

## Observed results

| Path | Result | Observation |
| --- | --- | --- |
| CoreS3 docs examples | PASS | Touch, power key, injected IMU, battery and ALS changed guest output. The SD example reported write success and two files detected. The camera example rendered the three supplied PPM bands. |
| Cardputer-ADV docs examples | PASS | GPIO0 produced press and release serial markers. Keyboard input left typed text in the guest frame. IMU changed the guest frame. The SD guest read its fixture and reported 1 MiB read and written. |
| Speaker PCM | PASS | Both devices returned 48 kHz mono PCM, with nonzero samples and a dominant tone near 10 kHz on CoreS3 and 7 kHz on Cardputer-ADV. |
| Microphone WAV | PASS | Separate same-firmware tone and silence sessions on both boards produced distinct guest waveform frames. The first short CoreS3 control had a blank framebuffer and is retained in local evidence. |
| CoreS3 UIFlow2 | PASS | Stock v2.5.3 home, touch receipt and panel evidence. Composed UART0 bootstrap executed Python source and a complete file package in the same guest. The binary main.mpy loader proof remained unsupported. |
| CoreS3 Wi-Fi | PASS | Explicit trusted-host guest associated and reached the dedicated host HTTP fixture through NAT. The first attempt against the virtual gateway timed out. A namespace policy request returned 409. |
| Frozen QEMU | PASS and PARTIAL | CoreS3 explicit QEMU completed touch and frame change. StopWatch composed UART Run completed and painted the panel. Stock StopWatch remained blank in two separate attempts. |
| Cleanup | PASS | ZIP CRC and manifest member digests verified. Terminal leases released their workers. A 30-second TTL test stopped the ADV session and retained history. |
| Browser overlay | PASS | The actual mixed export streamed WASM bytes whose SHA-256 matched the manifest. Static admission tests covered mixed including legacy, esp32sim-only, QEMU-only, tamper and absent advertised C61 assets. |

Physical hardware, RF, acoustic and electrical behavior were NOT RUN. Namespace egress and QOM are disabled for esp32sim. The live guest Flash is volatile. Browser WASM guest execution is the separate browser workstream. The raw HTTP responses, images, network capture and ZIPs stay in private evidence storage. The public summary omits runtime-local paths, network addresses, access data, launch and session identifiers, and guest device identifiers.
