# NanoC6 and Nesso N1 native board replay

Batch C6-A added `m5stack-nanoc6` and `arduino-nesso-n1` to the
native ESP32-C6 CLI. The validation below used virtual devices and
unaltered product documentation and stock firmware. The machine-readable
record identifies the source, ROM, firmware and runtime for each run.
[Run manifest](run.json)
[Batch source](https://github.com/m5agent/esp32sim/tree/c2734200d15670eecd990386f89d0883528dd2f1)

## NanoC6

| Case | Result | Observed guest behavior |
| --- | --- | --- |
| button | PASS | GPIO9 press, hold and release produced the Arduino callbacks. Idle input produced none. |
| ir_nec | PASS | Eight decoded NEC frames, including distinct command bytes with valid complements. |
| led | PASS | Eight blue LED transitions on GPIO7. |
| program | PASS | GPIO19 enabled the RGB rail. Two captures decoded green and blue from GPIO20, with 81 and 82 RGB frames. |
| thread-1 | PASS | Guest formed a Thread Leader. |
| thread-2 | FAIL | The Leader attempted IPv6 UDP sends. No UDP application payload reached its peer. |
| thread-3 | FAIL | The receiver stayed Detached and never printed the UDP payload. |
| thread-4 | PASS | Active MLE discovery returned the peer PAN on channel 24. |
| thread-5 | PASS | The guest CLI returned the OpenThread version and disabled state. |
| thread-6 | PASS | The discovery/formation example printed Leader. |
| zigbee-1 | FAIL | Coordinator started. No temperature report arrived from the peer. |
| zigbee-2 | FAIL | The sketch stopped in its SHT30 probe before starting Zigbee. No ENVIII accessory was attached to the board model. |
| zigbee-3 | PASS | The scanner reported the permit-join coordinator on channel 15. |
| zigbee-4 | FAIL | Coordinator started. The peer never bound, so the Arduino switch issued no bound LED commands. |
| zigbee-5 | FAIL | End device started and searched for a network. Join and LED commands were absent. |
| Zigbee rejoin and post-reset traffic | NOT RUN | Initial join and binding were prerequisites. |
| BLE | NOT RUN | No matching ELF supplied for stock v2.5.3, and no qualifying ELF-backed ESP-IDF 5.5.x NimBLE transport fixture was available. |

Stock UIFlow2 v2.5.3 reached the USB-Serial-JTAG REPL. The guest evaluated
a calculation to 323 and read GPIO9 low during press and high after
release. REPL code received a host-originated UART0 line and UART0
transmitted a separate guest-originated marker. NanoC6 has no framebuffer.

The 36-second Cooja Thread run showed 22 legacy ACK frames and 100
frames with the MAC security bit set. The Zigbee coordinator/end-device
run showed 24 legacy ACK frames and no security-bit frames. The observed
flags and ACKs establish traffic through the modeled MAC. Initial
association remained incomplete. The pinned MAC source documents
unmodeled enhanced ACK, security processing and frame-pending behavior.
The isolated Thread guests produced zero receive events and zero ACKs.
These runs did not isolate which missing behavior blocks association.
[Arduino examples](https://docs.m5stack.com/en/arduino/m5nanoc6/program)

## Arduino Nesso N1

| Case | Result | Observed guest behavior |
| --- | --- | --- |
| button | PASS | Each key produced a distinct press and release via GPIO or expander mapping. No callbacks fired on the idle replay. |
| buzzer | PASS | I2S0/GDMA capture contained both the 4 kHz and 10 kHz tones at 48 kHz. |
| display | PASS | ST7789 rendered the centered text in landscape orientation. The framebuffer agreed with the documented layout. |
| imu | PASS | BMI270 rest was stable. Two motion samples produced distinct guest-rendered values and differed from rest. |
| ir_nec | PASS | Seven LCD-sketch NEC frames decoded at the board LED. |
| led | PASS | Blue LED toggled through expander output E1.P7. |
| lora-1 | PASS | Guest initialization and DIO1 TX completion succeeded. The UDP peer received all 14 sends. |
| lora-2 | PASS | Received the original greeting and numbered messages. The isolated receiver initialized and received no packets. |
| power-1 | DOCS-DEFECT | `power_1.ino:28` assigns a `bool` from `M5.Power.isCharging()` to `Power_Class::is_charging_t`. Arduino 3.2.5 rejected the conversion. |
| power-2 | PASS | Guest toggled the expander Grove output. The panel displayed ON at 7.5 simulated seconds and OFF at 8.0. |
| quickstart-bargraph | PASS | ST7789 rendered the scrolling RGB gradient shown in the quick start. |
| touch | PASS | Two FT6336 touch coordinates produced distinct frames. The no-input run produced no touch events. |

Stock UIFlow2 v2.5.3 rendered its launcher. The two keys selected USB mode.
After entering the USB REPL the guest evaluated a calculation to 323
and scanned the routed I2C bus. The scan included the two PI4IO
expanders, FT6336, BMI270, BQ27220 and AW32001. Battery inputs produced
3750 and 4020 mV on the BQ27220 voltage register. AW32001 status changed
from 0x00 with VIN absent to 0x14 with VIN and charging active.
[Arduino Nesso N1 examples](https://docs.m5stack.com/en/arduino/arduino_nesso_n1/program)
[Display example](https://docs.m5stack.com/en/arduino/arduino_nesso_n1/display)
[Quick start](https://docs.m5stack.com/en/arduino/arduino_nesso_n1/program)

## Implementation and reproduction

The Nesso board uses the S3-C PI4IOE5V6408 model from commit
`8984ba06`, the CoreS3 BMI270
model, the shared DCS panel model and FT5x06 touch registers. Its new
AW32001 and BQ27220 models attach to the normal hardware and soft I2C
routes. The new C6 I2S0 capture drains GDMA descriptors. C6 SPI2
retains its cursor across transactions sharing a partial GDMA descriptor.
The Cardputer-ADV SX1262 packet model serves Nesso LoRa with the SPI
version response added for RadioLib identification. This shared change
can also affect compatible CAP LoRa boards.
[Observed version response](https://github.com/jgromes/RadioLib/issues/683)

Before the C6 DMA fix, the original RadioLib sketches stalled in the
display SPI wait. With cursor retention they reached RadioLib and
returned `-2` at the version register probe. With the response at 0x0320, both original sketches initialized
through the same SPI controller. Fourteen packets crossed the UDP link.
The runs preserved the first failure and the passing replay separately.

Build the native simulator using Cargo. Use the pinned ESP32-C6 ROM
and the merged binaries built with Arduino board package
`m5stack:esp32@3.2.5`. The firmware documentation revision is
`7219cc9286c39b463da84053deee40bc234625db`. Each case is a ROM cold
boot. The runners exit each process at its emulated-time horizon or
stop the owned peer process. These commands take absolute local paths
through the shell variables.

```sh
export CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
cargo build --release -p esp32sim --bin esp32sim-c6 --bin esp32sim
commit=$(git rev-parse HEAD)
python3 tools/run-nanoc6-docs.py "$C6_BINARY" "$C6_ROM" "$NANO_FW" "$OUT/nano" --stock "$NANO_STOCK" --commit "$commit"
python3 tools/run-nesso-n1-docs.py "$C6_BINARY" "$C6_ROM" "$NESSO_FW" "$OUT/nesso" --stock "$NESSO_STOCK" --commit "$commit"
cooja() {
  python3 tools/run-nanoc6-peers.py "$C6_BINARY" "$C6_ROM" "$@" --commit "$commit"
}
peer() {
  first=$1 second=$2 label=$3
  shift 3
  cooja "$NANO_FW/$first/sketch.merged.bin" "$NANO_FW/$second/sketch.merged.bin" "$OUT/peers/$label" --seconds 36 "$@"
}
peer thread-2 thread-3 thread-peer
peer thread-2 thread-4 thread-scan
peer thread-2 thread-3 thread-isolated --isolated
peer zigbee-4 zigbee-5 zigbee-peer
peer zigbee-4 zigbee-3 zigbee-scan
peer zigbee-1 zigbee-2 zigbee-temp
python3 tools/run-nesso-n1-lora.py "$C6_BINARY" "$C6_ROM" "$NESSO_FW" "$OUT/peers/lora-peer" --commit "$commit"
python3 tools/run-nesso-n1-lora.py "$C6_BINARY" "$C6_ROM" "$NESSO_FW" "$OUT/peers/lora-isolated" --isolated --commit "$commit"
```

For the NanoC6 stock control, use `--script 0` with `4 press btnA 1400`
and `6.3 uart0 c6-uart-input` on separate lines. Send Ctrl-C at 1.2
simulated seconds. Use `--serial SECONDS 0 COMMAND` to print
`17*19` at 2.0 s, sample GPIO9 at 4.2 and 5.6 s, create
`machine.UART(0, baudrate=115200, tx=16, rx=17)` at 6.0 s, and
read it at 7.0 s. To capture guest data in the other direction,
repeat the stock run with `--console uart0` and have MicroPython
write the distinct UART marker at 3.0 s.

For Nesso stock, cold-boot to the launcher and then use
`--board arduino-nesso-n1` and the script below in a fresh guest.
Send Ctrl-C at 5.0 s. Read I2C0 on SDA GPIO10 and SCL GPIO8.
Print the calculation and scan at 5.5 s. At 6.5 and 8.5 s, read two
bytes at register 8 from device 0x55, and one byte at register 8 from
device 0x49. Save the USB outputs under the peer subdirectories
`nano-stock-repl` and `nesso-stock-repl`.

```text
2 key B down
2.3 key B up
3.5 key A down
3.8 key A up
6.0 battery 3750 -110 37 0
8.0 battery 4020 96 81 1
```

```sh
python3 tools/check-nanoc6.py "$OUT/nano" "$OUT/peers"
python3 tools/check-nesso-n1.py "$OUT/nesso" "$OUT/peers"
```

The evidence preserves the firmware, ROM, binary and input hashes.

## Regressions

CoreS3 and Cardputer-ADV replayed the pinned original images from the
firmware archive.
[Firmware archive](https://github.com/m5agent/m5stack-firmware-archive/tree/829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c)

The C6 crate passed 136 tests. The configured CI filter excludes two
external fixture tests requiring a Contiki-NG nullnet build or a
PlatformIO pin-transport image. The bare C6 ROM sentinel matched the
base and candidate at 800,000,000 instructions and cycles, zero
exceptions and 505 interrupts over five guest seconds. The host wall
times in the summary came from a concurrent workload.

On the final runtime, CoreS3 passed 15/15 and Cardputer-ADV passed
11/11. The native and WASM CI Clippy commands passed. The first
workspace run stopped because the checkout lacked the pinned P4
co-simulation images. After the repository CI fetch scripts restored
the assets, co-simulation passed 22/22. The completed workspace
suite reported 1976 passed, seven failed and 34 external tests
filtered by the repository CI test selection.

All seven assertions were reproduced with the base executable.
Four P4 Hosted goldens compare older SDIO pin formatting. The base
and candidate completed the same traffic and matched guest console
hashes and instruction counts for both Hosted versions and both
raw-throughput directions. Two P4 SMP Hello World goldens give
instruction counts 704 and 640 above the corresponding base and
candidate counts. The P4 Wi-Fi station option assertion expects
older error wording. The candidate was pushed as the C6-A
branch after the base comparison. The batch verdict remains PARTIAL.
[Regression evidence](evidence/regression-summary.json)

## Boundaries and rollback

Full matrix and physical hardware validation remain open for C6-A.
Packet-level LoRa and IEEE 802.15.4 evidence characterizes digital
behavior. RF, physical buzzer acoustics, charger electrical behavior
and BLE have no validation in this batch. Use the recorded base commit
to select the pre-port implementation or revert the batch commits
together to remove the two board profiles and their shared changes.
