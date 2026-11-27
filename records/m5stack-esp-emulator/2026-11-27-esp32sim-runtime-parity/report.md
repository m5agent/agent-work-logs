# Native runtime validation

The two StickC Arduino shutdown examples filled the panel green, waited in
guest time and called AXP192 PowerOff. The original service reported a zero
process exit as failed in two trials per board. The new control overlay
carries a board power-off event and the terminal RGB565 frame on the private
stream. The service stored the black terminal frame, serial and evidence
before releasing both repeats for each model. A plain zero exit still
requires the normal exit classification.

Paired LoRa and CC1101 sessions use the fork's guest-time TCP transport.
The service selected the board/accessory and allocated two leases. The ADV
tests loaded the original example sources into UIFlow2 with a receiver UART
marker for delivered bytes. The typed keyboard sent `w`, `a`, `s`, `m`
and Enter to the two LoRa transmitter examples. CC1101 delivered the
expected sequence-zero payload from its automatic sender. PaperMono and
Nesso used their original Arduino sender and receiver builds and delivered
ordered payloads. NanoC6 Thread delivered `Hello,M5Stack`; Zigbee used
typed source button pulses and the receiver controller's black and blue LED
transitions. Both trials passed the delivery markers in each mode.
Wall-window packet counts can differ. A retained ZIP contains both member
archives; Cooja includes a bounded radio/LED timing trace.

## Reproduction

Build the pinned native service overlay with the matching ROM assets.

```sh
CARGO_PROFILE_RELEASE_LTO=false python3 scripts/bootstrap-esp32sim-runtime.py \
  --with-classic --with-tab5 --rom-dir "$ROM_DIR"
```

Start a dedicated worker with a disposable state directory. Use the existing
Device Service API to upload the original firmware artifact and register a
merged image. For the default comparison request both runtimes on each
board-matched image, twice. Use the frame checks and typed input sequence
from `tests/uiflow2/device_matrix.json` for composed base fixtures. For the
sampled Arduino displays use the corresponding fork checks for pixel
counts, geometry, palette and changes across frame captures. Save fresh
frames, cursor serial and evidence before delete with `purge=0`. For radio
checks register both board-matched images and create one `/radio-pairs`
resource. Read separate serial and input endpoints and download pair
evidence before deleting the pair.

## Fork findings and scope

- PaperMono. In the base UIFlow2 fixture a typed touch hold at (240,650) for
  1 second was accepted but the frame stayed unchanged and (440,30) stayed
  white. On the same image, QEMU changed the frame and rendered that pixel
  black in both trials. Inspect whether the pinned PaperMono FT5x06
  touch report and redraw path reaches the UIFlow2 guest after press and
  release.
- StopWatch. The same touch oracle matched the pixel in both runtimes.
  The native Stopwatch frame is 468×466 in the fork and the fixture
  expects 466×466. Confirm the two-column panel window and the origin of
  the extra columns before advertising geometry parity.
- AtomU and Atom Echo. The stock GitHub v2.5.4 M5Things launcher defect is
  separate from the comparison. Existing images with replaced LittleFS
  were used only for the identified composed regression fixtures.
- The CLI accepts an SD image before launch. The pinned native service
  interface has no insert/remove control method, so the capability
  error remains.
- The complete Arduino, stock interactive and checked-in peripheral
  fixture oracle matrix remains PARTIAL. Host QEMU preparation using
  esptool hit readiness/timeout failures in the first matrix attempt.
  Measured comparisons used the existing host-image preparer. Several
  display outcomes represent a time-window sample and may still require
  longer or guest-timed inspection. No physical hardware measurements
  are claimed.

The source contract suite passed 2,587 tests with 11 skips after selecting
Node 20 and Python 3.12. Scope, profile, catalog and snapshot checks were
run. The rollout closeout is a separate record of exact merge and service
identities.
