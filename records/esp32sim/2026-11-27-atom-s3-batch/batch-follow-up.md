# AtomS3 family follow-up

2026-11-27 · virtual-device validation

The native batch covers seven shipped boards. AtomS3 and AtomS3R each have
an explicit GC9107 revision alongside the ST7735S default. The canonical
VoiceS3R, CAM and M12 variants use their shipped displayless layouts. Their
stock acceptance uses the interactive console and user input.

| Board | Arduino cases | Stock UIFlow2 |
| --- | --- | --- |
| AtomS3 Lite | PASS ir_nec and lite_led. DOCS-DEFECT button. | PASS v2.5.3, CDC ID 137 and G41 transition |
| AtomS3 | PASS display, quickstart-display and ir_nec. DOCS-DEFECT button and imu. | PASS v2.5.3, CDC ID 11, 128×128 home and G41 transition |
| AtomS3R | PASS button, display, imu, ir_nec and quickstart-bargraph. | PASS v2.5.3, CDC ID 18, 128×128 home and G41 transition |
| AtomS3U | PASS button, ir_nec, mic, program and rgb_led. | PASS v2.5.4, CDC ID 138 and G41 transition |
| Atom VoiceS3R | PASS button, ir, mic, program and speaker. | PASS v2.5.4, CDC and UART0 ID 145, G41 transition |
| AtomS3R-CAM | PASS quickstart-camera with 320×240 JPEGs. | PASS v2.5.4, CDC ID 144 and G41 transition |
| AtomS3R-M12 | PASS quickstart-camera with 1600×1200 JPEGs. | PASS shared v2.5.4 CAM image, CDC ID 144 and G41 transition |

Both AtomS3 LCD revisions rendered the Hello and library quickstart sketches
through their own IDs and GRAM dimensions. The AtomS3R bars had the same
left-to-right color progression and bottom alignment as the product guide.
Exact heights differ with animation phase.
[AtomS3R Arduino reference](https://docs.m5stack.com/en/arduino/m5atoms3r/program)

The AtomS3 button example is identical for Lite and LCD. Its
`static/en/arduino/m5atoms3/button.md:9` example declares serial prints but
omits HWCDC initialization. The unchanged firmware hit both guest print
call sites after G41 transitions. Stock CDC separately returned both G41
states. The `static/en/arduino/m5atoms3/imu.md:7` example has the same
initialization gap and supplies no other output. Stock AtomS3 yielded the
stationary vector and two different MPU6886 vectors via CDC.
[Button example](https://docs.m5stack.com/en/arduino/m5atoms3/button) ·
[IMU example](https://docs.m5stack.com/en/arduino/m5atoms3/imu)

AtomS3R read back LP5562 W-channel values 34 and 196 after two guest brightness
changes. The BMM150 is attached to BMI270 AUX. The final-board stock probe
returned different magnetometer vectors for the idle field and both
injected fields. [AtomS3R pin map](https://docs.m5stack.com/en/core/AtomS3R)

Each camera sent two decodable JPEGs per black, red and green input through
the Arduino DHCP and HTTP path. CAM converted the GC0308 RGB565 capture.
M12 transferred baseline JPEG input through the OV3660 JPEG path at the
guest-selected size. Each first guest JPEG matched its injected file byte
for byte. The shared stock image exposes the CAM board ID on
both profiles. The checker uses the schematic's G41 contact via the
stock machine Pin API, since the generic BtnA object stays inactive in the
CAM firmware. [CAM pin map](https://docs.m5stack.com/en/core/AtomS3R-CAM) ·
[M12 pin map](https://docs.m5stack.com/en/core/AtomS3R-M12)

The AtomS3 Lite virtual reset was requested after a successful CDC REPL
exchange. The guest logged a power-on reset and a new ROM boot. AtomS3U
also executed a firmware software reset. Earlier runs with long replay
windows hit wall timeouts after producing some functional observations.
Subsequent replays used bounded case-specific guest durations. Earlier
failed runs and their outcomes remain in the replay summary.

The new shared models cover MPU6886 polling, LP5562 direct RGBW control and
OV3660 SCCB and DVP output. AtomS3U uses the S3 I2S converter's PCM boundary.
The models cover the digital paths tested above. Physical optics, acoustics
and electrical behavior were NOT RUN. LP5562 engine programs, raw PDM bit
filtering, and physical validation are outside the tested model subset.


## Regression

CoreS3 15/15 and Cardputer-ADV 11/11 passed on the base and on the final native
runtime. The archive input revision is
`829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c`. The final Rust source is
`098a249ab674ba16e9a5f7880bfbdb52eb910b08` and the delivered branch adds only checker changes above it.
Native and wasm32 Clippy passed with warnings denied. The workspace suite
reported 1972 passed, 7 failed and 0 ignored.
The workspace build disabled release LTO and debug info to fit the shared
runner. Two earlier concurrent builds failed on stale crate interfaces
while changes were being made. The first completed build reached the P4
co-simulation fixtures and reported ten missing-input failures. The final
workspace replay used the checksum-pinned CI assets. The workspace gate
remains FAIL. The base binary reproduced all seven residual failures.
Four hosted/P4 report comparisons expect a GPIO range while both binaries
print a list. Two SMP goldens expect instruction counts different from
the identical counts measured on base and candidate. The P4 Wi-Fi option
test expects older diagnostic wording. The batch did not modify those goldens.

The ESP32-S3 Hello workload executed 4,570,780 guest instructions in 4 s on
each paired run. Pocket Tank executed 614,329,973 instructions in 2 s on
both versions. Build flags and concurrent load differed, so these are
instruction-count checks.

- [Final source](https://github.com/m5agent/esp32sim/tree/8d55e7b6a961a523c06d81af69b4371b9a796aa5)
- [Firmware archive](https://github.com/m5agent/m5stack-firmware-archive/tree/829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c)
- [Replay summaries](evidence/atom-s3-replays-summary.json)
- [Regression and instruction counts](evidence/atom-s3-regression-summary.json)
- [Supplemental guest evidence](evidence/atom-s3-extra-summary.json)
- [Base reproduction of seven P4 failures](evidence/p4-baseline-summary.json)
