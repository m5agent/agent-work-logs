# esp32sim release qualification

The candidate integrates the native Device Service adapter with the published
esp32sim source pin and the public browser workbench. The prior fork baseline
is `5742b0bc617639c477e277fcae5970746327ec80`. The new pin is
`3e90d09bd31b5658d8dd2b6fc5d820da5f293489`. The independently downloadable
Tab5 C6 bundle is pinned by its archive and component hashes.
[Runtime release](https://github.com/m5agent/esp32sim/releases/tag/m5-device-service-20261127)

## Native Device Service

Upload the fixture with `POST /api/v1/artifacts`, compose it with
`POST /api/v1/firmware`, then start an isolated session with
`POST /api/v1/sessions`. Compare Tab5 with explicit `runtime=esp-emu` and
`runtime=esp32sim` using identical normalized Flash bytes. Poll the framebuffer,
inject the recorded coordinates or HID reports, and check the guest view.
Get the evidence ZIP before stop and preserve history with `purge=0`.

CoreS3 touch and the ADV keyboard changed the guest framebuffer. On Tab5
the same v2.5.4 Flash displayed the launcher on ST7123 and both runtimes opened
ADC after the same panel coordinates. The GT911 Maker Fighter session reached
the menu after real HID controller injection. The legacy comparison timed out
without a usable frame. Arduino Touch on GT911 changed its framebuffer, and
the Wi-Fi example observed a DHCP lease via ESP-Hosted. The latter ZIP includes
Ethernet PCAP. The default routing was replayed with the runtime field omitted
for the two admitted Tab5 firmware and panel pairs.

The source hashes, normalized Flash, P4 ROM, C6 images, controller inputs, frame
hashes and evidence ZIP hashes are in the native summary. Raw artifacts and
guest-specific serial/frame contents were omitted from the public record.

## Browser-WASM

The mixed source export was served by the isolated Device Service. The
repository's `test_public_esp32sim_guest.mjs` opened a cross-origin frame and
observed guest display and serial. CoreS3 Display, Touch and stock UIFlow2
passed. ADV Display, Keyboard and G0 Button passed. The exact ADV stock
firmware also displayed its offline launcher. Each run counted one
DedicatedWorker before Stop and zero after. The browser uses the S3 ROM.
Tab5 WASM is NOT RUN because the export and Worker do not yet admit P4/C6
runtime assets and board modes.

## Additional checks and limits

The direct CLI examples passed 15/15 for CoreS3, 11/11 for ADV and 25 cases
for Tab5. The Tab5 speaker sketch has an extra hash on its include line.
The corrected speaker fixture passed. Tab5 RS485 and the Tab5 UIFlow2 docs
page have no standalone examples. The workspace test suite counted 1,969
passes and seven failures. A baseline replay found the same six P4 golden
failures and one Wi-Fi CLI message mismatch. Native and WASM Clippy passed.
No golden was regenerated.

Full Tab5 cross-backend HTTP parity beyond the named cases is NOT RUN.
The frozen backend needs per-firmware configuration for its DSI path.
Other Tab5 sessions continue to select the previous runtime. Physical
hardware measurements and hosted delivery are outside this initial receipt.

## Hosted preview follow-up

The initial official workflow produced both pinned QEMU source artifacts.
The preview was cancelled once the raw GitHub route for its Arduino fixtures
was found to return Git LFS pointers. The fixture correction pins downloaded
media by SHA-256. [Initial workflow](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45925805446)
· [Fixture correction](https://github.com/m5agent/m5stack-esp-emulator/pull/280)

The next official preview passed all seven esp32sim guest cases, each with
one DedicatedWorker before Stop and zero after. Its separate CoreMatrix stock
runner failed the isolation assertion before any guest boot. The remaining
aggregate gate was NOT RUN in that workflow. The runner opened the mixed
site's default engine while waiting for QEMU's isolation condition.
[Second workflow](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45928863733)

After adding explicit QEMU selection to the runner, a local browser replay
used the identical pinned CI-built C61 WASM and original UIFlow2 v2.5.4 Flash.
It verified the stock missing-SSID framebuffer, USB raw REPL, nine input
edges and graceful Worker cleanup. Controller inputs and framebuffer hashes
are included in the summary. The browser target and session identifiers are
omitted. The corrected official preview was dispatched from the merged fix.
[Stock runner correction](https://github.com/m5agent/m5stack-esp-emulator/pull/281)
· [Corrected preview](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/45930498931)
· [Evidence summary](evidence/pages-preview-summary.json)
