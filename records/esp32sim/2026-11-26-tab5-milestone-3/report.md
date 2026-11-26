# Tab5 milestone 3 virtual-device validation

The base was esp32sim `4770aa6f`. The [milestone 2 record](https://github.com/m5agent/agent-work-logs/blob/b50268351888f4ac0c1f061038188dee6092107a/records/esp32sim/2026-11-26-tab5-launcher/board-peripherals.md) documented 18 passing and seven failing cases. The goal was to complete the wake, network and USB Arduino paths while retaining the original failure evidence and existing Board regressions.

| Change | Source |
| --- | --- |
| P4 PMU stall, timed deep sleep, RX8130 board power, Tab5 USB identity and full-speed MSC | [8a866f6c](https://github.com/m5agent/esp32sim/commit/8a866f6cfe4adcf0c100f8c613b6992013ea79fd) |
| Route native `--wifi-sta` through the C6 under `--coproc` | [284b61da](https://github.com/m5agent/esp32sim/commit/284b61da59c88209b3b37fc2b77ca23debd883d2) |

## Wake paths

The five-second sketch calls M5Unified 0.3.0 `deepSleep(5000000, false)`. Arduino programs LP_TIMER comparator 0, selects the PMU RTC timer wake source and writes the sleep request. The model stops both HP cores, keeps the LP counter and wakes through the ROM with cause `0x5` at 8.767 virtual seconds. The guest redraws the original prompt. Other LP wake sources are outside this change. [M5Unified 0.3.0](https://github.com/m5stack/M5Unified/blob/0.3.0/src/utility/Power_Class.inl), [ESP-IDF v5.4.1 PMU registers](https://github.com/espressif/esp-idf/blob/v5.4.1/components/soc/esp32p4/register/soc/pmu_reg.h), [LP timer registers](https://github.com/espressif/esp-idf/blob/v5.4.1/components/soc/esp32p4/register/soc/lp_timer_reg.h).

The next-minute sketch calls `timerSleep(rtc_time_t)`. I2C showed RX8130 alarm 12:01 and AIE set, followed by a pulse on address 0x44 P4. The board routes that pin and the RTC IRQ through the standby supervisor, whose latch behavior is modeled from the visible signals. P4 stops at about 3.311 virtual seconds and boots from the ROM after the RTC IRQ at 60.976 seconds with cause `0x1`. The RTC keeps its calendar while the P4 supply is off. [Tab5 schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1132/Tab5_Schematics_PDF.pdf).

## Wi-Fi and SNTP

M5Stack Arduino 3.2.5 uses IDF `858a988d`, ESP-Hosted `2.0.13` and esp-wifi-remote `0.13.0` in the P4 package lock. The milestone 2 C6 image was identified by the application banner as `2.12.6` (IDF 5.5.4-dirty). The prior runner supplied bootloader, partition table, OTA data and application slices extracted at offsets 0x0000, 0x8000, 0xd000 and 0x10000 from the retained merged adapter. The exact slice comparison and digests are in the manifest. The original download URL was unavailable.

Station and scan had reached the mismatched slave's RPC layer but failed at the application. A diagnostic replay with P4 software stalls modeled reached a P4 `netif already added` assertion with the newer adapter. The matching ESP-Hosted 2.0.13 sample first stalled in C6 Bluetooth startup before enabling SDIO. Building the same sample with Bluetooth disabled and the documented C6 baseband calibration stub gave the original station and scan sketches working ESP-Hosted exchanges. The fixture was built with ESP-IDF v5.4.2, commit `f5c3654a1c2d2a01f7f67def7a0dc48e691f63c0`, and Arduino's RISC-V toolchain 14.2.0. The original station sketch associated via WPA2 and displayed a DHCP lease with NAT enabled. The scan listed the virtual AP and its WPA2 security.

The original SNTP sketch passed with deterministic DNS and NTP on the virtual LAN. The clock began at epoch 1764150000. One DNS response and one SNTP response traversed the C6, and the guest then read advancing RX8130 UTC seconds and showed them on the LCD. The host-NAT SNTP attempt had a DHCP lease and ARP replies but timed out waiting for external DNS. SoftAP uses a separate build containing the uncommented AP block. The native CLI routes the virtual station to the C6 and observed a lease from the guest's DHCP server. [C6 baseband calibration and hosted reference](https://github.com/m5agent/esp32sim/blob/284b61da59c88209b3b37fc2b77ca23debd883d2/examples/esp-hosted-p4/README.md).

## USB SDK and documentation

The original SDK guest first spun at `esp_cpu_stall` waiting for `HP_SYSTEM.CPU_CORESTALLED_ST`. The model now applies PMU software-stall keys to scheduling and status. The next failure was the Arduino USB HAL assertion that requires the 4.00a GSNPSID. The original Tab5 profile selects the measured 4.00a HS identity. Other P4 profiles retain their previously selected identity. Once the SDK initialized, it rejected 512-byte bulk endpoints above its 256-byte FIFO limit. A full-speed MSC fixture negotiates 64-byte endpoints and exercises the original SDK probe through enumeration, a 31-byte command wrapper, 512 bytes of sector 4 and a 13-byte successful status wrapper. The previous register probe checked only 4.30a and exited before enumeration on the Tab5 identity. The rebuilt probe accepts 4.00a and 4.30a and exercises the high-speed alternative. The negative run and rebuilt probe hashes are retained. [Arduino's pinned USB HAL](https://github.com/espressif/esp-idf/blob/858a988d/components/hal/usb_dwc_hal.c), [Arduino's pinned HCD](https://github.com/espressif/esp-idf/blob/858a988d/components/usb/hcd_dwc.c).

The original speaker example fails at English Tab5 `speaker.md` line 15, where `##include` has an extra hash. The checker emits `DOCS-DEFECT` once it verifies the compiler diagnostic. The corrected copy passes and produces the five ordered tones. The English Arduino Tab5 directory has no RS485 sketch. The UIFlow2 Tab5 programming guide covers IDE use and links shared examples. Existing stock launcher and REPL checks are retained.

## Final matrix

The checker emits 25 PASS, one DOCS-DEFECT and two NOT RUN entries. The corrected speaker and both USB MSC fixtures pass in the final results. [Per-case verdicts](evidence/verdicts-summary.ndjson).

## Regression scope

All 982 selected Rust release library and ROM integration tests passed across esp-periph, esp-soc, P4, S3 and C6. Native and WASM Clippy passed with Rust warnings denied. The P4 device-mode MSC goldens passed. Four P4 golden assertions already disagreed at the base: two hosted reports stringify the D0–D3 labels differently, and both SMP hello counts already exceed their golden values by 704 and 640 respectively. Replays match the candidate values. No golden files were regenerated. CoreS3 passed 15/15 and Cardputer-ADV passed 11/11 on their original firmware paths. Five benchmark workloads preserve instruction counts and console bytes. Timing varies on the shared host.

Revert the two source commits in reverse order to roll back. The report uses virtual-device validation only. No RF, electrical, physical hardware or browser guest result is claimed. [Case verdicts](evidence/verdicts-summary.ndjson).
