# Qualify two isolated native Device Service paths

All results below are virtual-device validation. The reference binary, exact candidate binary and guest evidence hashes are recorded in the [SoftAP and STA comparison](evidence/softap-summary.json). The original Tab5 firmware and controller, runtime, frame, serial, and ZIP hashes are recorded in the [Tab5 touch report](evidence/tab5-touch-summary.json).

## ESP32-S3 SoftAP association

The old native QEMU run received the simulated station's authentication request and started the guest's HTTP listener. It produced neither an authentication response nor an association response, and the guest never reached `AP_FIXTURE_JOINED`. QEMU patch 0209 preserves the programmed receive interface and BSSID matches for the guest SoftAP. The comparison held the ESP-IDF v5.5.4 probe, Espressif QEMU base, build options, machine and device inventories, dependencies, and ESP32-S3 ROM constant. The native compilable source difference was `hw/misc/esp32s3_wifi.c`. The build source is identified by `ad8f512dc09f42047e698fd11b561bfc94f7a7ce`. The integrated patch has the same SHA-256 as the built revision. [QEMU patch 0209](https://github.com/m5agent/m5stack-esp-emulator/blob/fd08569f06b4afa478eb46da3654c4468e35a5bb/patches/qemu-m5stack-peripherals/0209-s3-softap-rx-interface-match.patch)

| Device and runtime | Authentication responses | Association responses | `AP_FIXTURE_JOINED` | DHCP lease | Portal HTTP sent |
| --- | ---: | ---: | --- | --- | --- |
| Cardputer ADV, reference | 0 | 0 | No | No | No |
| Cardputer ADV, candidate | 1 | 1 | Yes | No | No |
| Cardputer, candidate | 1 | 1 | Yes | No | No |

All three runs finalized their Ethernet capture, retained the pre-stop evidence ZIP and released their leases. Ethernet capture had zero packets. The management frame counts came from the native Wi-Fi trace, and the guest join marker came from the same session's UART. Starting the HTTP listener did not exercise the network path to it.

Separate ESP32-S3 station probes recorded DHCP DORA, bidirectional fixture HTTP and a verified body for Cardputer open and ADV WPA2. Reusing the exact ADV WPA2 firmware with mismatched fixture credentials gave `NO_LEASE`, zero DORA, zero fixture HTTP and no guest association. These station probes are controls for the candidate runtime.

To reproduce, use ESP-IDF `735507283d5b2f9fb363a1901172dbd9e847945d`, the [archived SoftAP fixture](code/softap/main/probe.c), and the emulator build recipe that applies patch 0209. Build with `idf.py -C code/softap -B build build` and merge the bootloader, partition table and `native_sta_fixture.bin` using `esptool merge_bin --fill-flash-size 8MB` and the generated `flash_args`. Keep the same merged 8 MiB firmware bytes for the reference and candidate runs. Import the image for `cardputer-adv` and `cardputer`, and create an isolated `qemu-wifi` session with `network.profile=generic-observe`, `http_fixture=false` and `capture_pcap=true`. Wait for `AP_FIXTURE_HTTP_READY`. Compare the Wi-Fi management subtype counts with UART `AP_FIXTURE_JOINED`, request the ZIP, then stop with `purge=0&retain_flash=0` and confirm finalized capture and lease release. The STA controls reuse the restricted one-NIC fixture configuration with the open, WPA2 and mismatch inputs.

SoftAP association `PASS` is confined to these two boards and probe. SoftAP DHCP and portal HTTP were `FAIL` for the probes that did not reach them. Client provisioning, other modes, browser WASM and physical behavior were `NOT RUN`.

## Tab5 CarPlay v1.0.0 GT911 single tap

The original upload and application bytes were preserved. No application ELF was supplied. The native esp-emu v1.1.0 runtime used `gt911-ili9881c`, a separately rebuilt GT911 ESP Part with identical bytes, GPIO23 INT, HP I²C controller 1 and address `0x14`. The application acknowledged reports by writing GT911 status register `0x814e`. The implementation execution source is `2bae48804564c61b2b6eb42f8f478267a009ce83`. [Integrated GT911 build instructions](https://github.com/m5agent/m5stack-esp-emulator/blob/fd08569f06b4afa478eb46da3654c4468e35a5bb/platform/esp-parts/tab5-gt911/README.md)

| Input on a stable 720 × 1280 DSI screen | HTTP or controller observation | Application observation |
| --- | --- | --- |
| Tap `(320,500)` in the blank area | 200, 13 reports and 13 acknowledgements | Frame bytes unchanged in the observation window |
| Tap `(640,160)` on the button | 200, 13 reports and 13 acknowledgements | `Clear phone pairing?`, `Cancel`, and `Clear pairing` appeared. The changed final frame differed by 56,199 pixels |
| Tap `(720,160)` beyond the screen | 400 `invalid_input` | Request declined |
| Separate ID-only GT911 control | 409 `input_requires_matching_elf` | Startup image matched the positive run; controller input remained unavailable |

Both taps finished with no contact. The positive and control runs retained their evidence ZIPs before stop and released session Flash and all leases. The destructive pairing action was left untouched. Earlier attempts included a test during startup screen refresh and a run that had no DSI frame within 32 seconds. Touch passed on stable frames. DSI startup reliability remains `PARTIAL`.

To reproduce from source, build the Tab5 part following `platform/esp-parts/tab5-gt911/README.md`. Configure an isolated native Device Service with the recorded esp-emu, `M5_TAB5_DSI_BOARD=gt911-ili9881c`, the GT911 part and allowlist entry for the recorded normalized Flash hash. Upload and import the original as `tab5`. Verify the session-reported touch part SHA and absence of application symbols. Read the same session's `frame.png` until the 720 × 1280 image showing `Connect your iPhone` is stable for at least 1.2 seconds. Send `touch` to the same session at the coordinates above and compare the resulting frame and `controller_reports`. Obtain the evidence ZIP before stopping. Repeat with the ID-only GT911 configuration as a negative control.

GT911 reset sequencing, swipes, multitouch, other panels or controllers, iPhone and USB data, browser WASM, and physical hardware were `NOT RUN`.

## Staged review readback

The independent dry-run of the same Tab5 BIN discovered a 720 × 1280 native frame and `esp-emu-gt911`. The generic reviewer used 1280 × 720 input sizing, accepted a tap without an observed frame change and received HTTP 409 `unsupported_input` for a drag. It returned `SIM_PARTIAL` and `E_INTERACTION_CLAIM_PARTIAL` after 60.245813 seconds. The preceding table records the direct native application path.

The integrated source platform suite ran 2309 tests, with 2299 passing and 10 skipped. Those counts describe the local source suite. On the same source commit, GitHub Actions jobs `platform-contracts` and `network-namespace-policy` passed. A positive guest runtime flow under a Linux namespace remains unverified. [GitHub Actions run](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44067130732)

## Evidence handling

The JSON files contain selected public identifiers, checksums, observations and counts from the original runs. Raw captures, host paths, network addresses, and session identifiers are excluded. The integrated commit identifies the candidate source for these changes. The session runs bind their tested runtime and guest bytes by SHA-256.
