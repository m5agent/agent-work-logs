# StickS3 wake and StopWatch audio power

The follow-up replayed the six contested cases from the documentation at `7219cc9286c39b463da84053deee40bc234625db`. They retain their original merged Arduino binaries built with `m5stack:esp32@3.2.5`. The native virtual-device runs used the board-specific wiring, ESP32-S3 mask ROM boot and corresponding sketch ELFs for symbol traces. Earlier results remain in the [batch report](../../report.md).

| Board | Case | Follow-up verdict | Source in extracted sketch |
| --- | --- | --- | --- |
| StickS3 | m5pm1-1 | DOCS-DEFECT | `m5pm1_1.ino:16` and `:37` |
| StickS3 | m5pm1-2 | DOCS-DEFECT | `m5pm1_2.ino:18` and `:52` |
| StickS3 | m5pm1-3 | DOCS-DEFECT | `m5pm1_3.ino:19` and `:72` |
| StickS3 | wakeup-2 | DOCS-DEFECT | `wakeup_2.ino:16` and `:36` |
| StickS3 | wakeup-1 | DOCS-DEFECT, previously FAIL | `wakeup_1.ino:18` |
| StopWatch | m5pm1_m5ioe1-6 | DOCS-DEFECT | `m5pm1_m5ioe1_6.ino:75–78` and `:107–113` |

## StickS3 I²C

M5Unified selects GPIO47/48 and the internal I²C1 controller. Each sketch starts Arduino `Wire` on the same pins. M5PM1 1.0.7 saves the supplied `TwoWire` instance, ends it, starts it on those GPIOs, and uses that object for register transfers. All four sketches initially read the PM1 identity successfully. [M5Unified pin map](https://github.com/m5stack/M5Unified/blob/96576a14247ddc935149145aa6b51943464120f1/src/M5Unified.inl#L104) · [M5Unified bus selection](https://github.com/m5stack/M5Unified/blob/96576a14247ddc935149145aa6b51943464120f1/src/M5Unified.inl#L1584) · [M5PM1 begin](https://github.com/m5stack/M5PM1/blob/be9a5456c007c333e7ac963f33bfde1ffa5d82ee/src/M5PM1.cpp#L275) · [M5PM1 transfers](https://github.com/m5stack/M5PM1/blob/be9a5456c007c333e7ac963f33bfde1ffa5d82ee/src/M5PM1_i2c_compat.h#L96)

After `M5.update()` polls PM1 key register `0x42`, the M5GFX path leaves the two GPIO output selectors assigned to I²C1. The register restore in M5GFX concerns its I²C peripheral state. The subsequent I²C0 operation uses the already configured controller, which can no longer drive the pads. In each guest the trace shows `set_pin(1, 47, 48)`, a subsequent I²C0 routing failure, and final GPIO47/48 selectors `0x5c/0x5b`. The ESP32-S3 GPIO matrix has one output select field per pad. It follows that the pinned example loses its I²C0 path on silicon as well. The previous batch's stock UIFlow2 control issued the four-second PM1 wake via I²C1, recorded one PM1 timer wake and observed a guest reset at 12.403 virtual seconds. [M5Unified update](https://github.com/m5stack/M5Unified/blob/96576a14247ddc935149145aa6b51943464120f1/src/M5Unified.inl#L3251) · [M5Unified PM1 key path](https://github.com/m5stack/M5Unified/blob/96576a14247ddc935149145aa6b51943464120f1/src/utility/Power_Class.inl#L4115) · [M5GFX pin select](https://github.com/m5stack/M5GFX/blob/28d47949bdc84f30881623476f555398e2194313/src/lgfx/v1/platforms/esp32/common.inl#L1646) · [M5GFX transaction](https://github.com/m5stack/M5GFX/blob/28d47949bdc84f30881623476f555398e2194313/src/lgfx/v1/platforms/esp32/common.inl#L2407) · [Espressif signal numbers](https://github.com/espressif/esp-idf/blob/v5.4.2/components/soc/esp32s3/include/soc/gpio_sig_map.h#L169) · [ESP32-S3 technical reference, section 6.5.2](https://documentation.espressif.com/esp32-s3_technical_reference_manual_en.pdf#page=477)

## StickS3 timer wake

The Button A press at 3.000 virtual seconds triggers `M5.Power.timerSleep(5)` at sketch line 18. The trace at 3.0100 seconds shows `esp_sleep_enable_timer_wakeup(5000000)`, followed by `M5PM1_Class::powerOff` and a write of `0xa1` to the PM1 system-control register `0x0c`. No PM1 timer programming or ESP deep-sleep entry follows. The virtual device stays off through 9.000 virtual seconds. This corrects the earlier incomplete characterization of the wake arm. The K150 schematic powers the ESP32-S3 from PM1-controlled `3V3_L2`. The source and schematic imply the on-chip wake timer loses power in this shutdown path. A previously recorded power-key control restarted the virtual board through PM1. [StickS3 wake example](https://docs.m5stack.com/en/arduino/m5sticks3/wakeup) · [M5Unified timerSleep](https://github.com/m5stack/M5Unified/blob/96576a14247ddc935149145aa6b51943464120f1/src/utility/Power_Class.inl#L2666) · [M5Unified StickS3 shutdown](https://github.com/m5stack/M5Unified/blob/96576a14247ddc935149145aa6b51943464120f1/src/utility/Power_Class.inl#L2164) · [K150 schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1207/K150_Stick_S3_PRJ_V0.6_20251111_2025_11_17_16_10_24.pdf)

## StopWatch rail and speaker

On C152 sheet 4, IOE1 PYG3 switches the ES8311 supply `AU_L3B`. Q5/Q6 isolate the codec I²C lines when the rail is down. The AW8737A amplifier draws from `VBUS_L0` and has its own PYG10 shutdown control. The model gates speaker PCM with the codec rail and amplifier enable, gates mic samples with the codec rail, and resets the shared codec register file when power falls. The board regression covers register reset, codec NACK, and independent gating of speaker gain. [C152 schematic, sheet 4](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1242/C152-SCH_Stopwatch_PRJ_Main_VA_20251201_2026_04_24_17_46_22.pdf)

The example plays the nominally silent tone via `Speaker.tone()` in its first phase. In its second phase it cuts the rail and then calls `Speaker.end()`, `Speaker.begin()` and `tone()`. The enable callback sets PYG3, initializes the ES8311 and enables PYG10. The trace and waveform capture show 10 kHz output after power returns in both phases. UART/USB selection, motor PWM and the audible 4 kHz and 6 kHz phases also passed. [StopWatch peripheral-control example](https://docs.m5stack.com/en/arduino/stopwatch/m5pm1_m5ioe1) · [M5Unified speaker enable callback](https://github.com/m5stack/M5Unified/blob/96576a14247ddc935149145aa6b51943464120f1/src/M5Unified.inl#L739)

The waveform contains 10 kHz intervals at 0.06–0.15 and 5.33–5.42 seconds on the emitted PCM timebase.

An independent stock UIFlow2 2.5.5 USB REPL control starts a 700 Hz tone for 2,000 ms and writes IOE1 register 5 after 500 ms. The control guest preserves `0x9d`. The cut guest writes `0x99`. Both read `0x02` from register 6, keeping the PYG10 bit set. The codec ACKs only with the rail on. Both guests have about 418,000 I²S0 output frames. At 8.0–9.1 seconds on the emitted PCM timebase, the rail-on capture contains 700 Hz at about 14,357 RMS and the rail-cut capture contains zeros. The [evidence summary](evidence/summary.json) retains the exact USB schedules, firmware and WAV hashes and selected windows.

## Replay

Build the source and invoke the runner with the staged Arduino ELFs alongside the merged images.

```sh
CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8 cargo build --release --bin esp32sim
export ESP32SIM_ROM_DIR="$ROM_DIR" S3B_FIRMWARE_DIR="$FIRMWARE_DIR"
S3B_CASES='m5pm1-1 m5pm1-2 m5pm1-3 wakeup-1 wakeup-2' \
  bash tools/run-s3b-docs.sh sticks3 target/release/esp32sim sticks3-power
S3B_CASES='m5pm1_m5ioe1-6 mic speaker stock' S3B_STOCK_IMAGE="$STOCK_IMAGE" \
  bash tools/run-s3b-docs.sh stopwatch target/release/esp32sim stopwatch-power
```

The wake cases were also isolated with the same runner flags and shorter virtual caps of 9.0 seconds for wakeup-1 and 5.2 seconds for wakeup-2.

The runner exits nonzero for the expected documentation defect entries and the filtered cases. Read the individual checker verdicts. To replay the independent audio control, write each stored USB schedule as lines, replacing the represented Ctrl-C character with ASCII ETX. Run the stock image with `--board m5stack-stopwatch --boot rom --console both --max-seconds 13.5 --no-dump --usb-host SCHEDULE --wav OUTPUT.wav`.

Reverting the board and codec model commit restores the previous StopWatch register retention and I²C behavior. The source and guest evidence here concerns the pinned binaries and libraries. Physical board validation, rail fall times and acoustic measurements were outside the run.

## Regression results

The board totals include earlier batch cases and the documented follow-up replays. The StopWatch microphone, speaker and stock UIFlow2 2.5.5 also passed on the follow-up runtime.

| Board | Arduino PASS | Arduino DOCS-DEFECT | Stock UIFlow2 |
| --- | ---: | ---: | --- |
| Cardputer | 10/10 | 0 | PASS |
| Dial | 10/10 | 0 | PASS |
| StickS3 | 10/15 | 5 | PASS |
| StopWatch | 17/18 | 1 | PASS |

CoreS3 passed 15/15 and Cardputer-ADV passed 11/11. Native and WASM Clippy passed. The release workspace suite with the ROM directory set reported 1,977 passing tests and the same six pre-existing P4 golden mismatches as the original batch. The first workspace attempt ended early after discovering the unset ROM directory. The S3, C3, C6 and Pocket Tank instruction sentinels matched the previous runtime and produced identical serial output.
