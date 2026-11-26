# Tab5 launcher and graphics accelerators

The exact stock v2.5.4 image associated with issue #188 boots to a
uniformly white scanout on esp32sim `3e079c0b2fa4ad725bec9bcb4debdf9b34900ef1`.
Wi-Fi initializes. A graphics task polls channel 2 for DMA2D RESET_AVAIL
at offset 0x224. The previous register storage leaves this bit clear.
Connecting the shared DMA2D/PPA controller lets the task begin SRM.
The SRM implementation writes the rotated RGB565 output through its RX
descriptor, which the DSI scanout then reads.

Both stock images accept the GT911 press at native (83,755) at 7.00 s
and release at 7.45 s. The button callback plays an I²S0 click before
opening the ADC view. Before I²S0 integration this gesture left the
frame unchanged. After routing the port to AHB-GDMA, both frames show
the ADC pin selectors and OPEN controls. The click yielded 65,698 and
65,478 samples at 48 kHz, with 1,852 and 1,799 nonzero samples respectively.

| Commit | Change |
| --- | --- |
| `566989f0f237245d1f82acbe221f4d76ace1fe54` | P4 DMA2D and PPA MMIO, memory and interrupts |
| `cf6c3712b2ca1454eae9e3de4b244cb1fab79031` | RGB SRM, descriptor geometry and arbitration priority |
| `3cc79d768465a434d46eb155f17d9a96b6b068d2` | Packed colour conversion and YUV420 |
| `0d987ebd9e4b5bf5f3f5da1f70cb788b77c8fa40` | I²S0 port and playback DMA |

Register references are ESP-IDF [v5.4.1 DMA2D](https://github.com/espressif/esp-idf/blob/v5.4.1/components/soc/esp32p4/register/soc/dma2d_reg.h),
[v5.4.1 PPA](https://github.com/espressif/esp-idf/blob/v5.4.1/components/soc/esp32p4/register/soc/ppa_reg.h),
[v5.5.4 DMA2D HAL](https://github.com/espressif/esp-idf/blob/v5.5.4/components/hal/esp32p4/include/hal/dma2d_ll.h),
and [v5.5.4 PPA HAL](https://github.com/espressif/esp-idf/blob/v5.5.4/components/hal/esp32p4/include/hal/ppa_ll.h).
Packed YUV420 follows ESP32-P4 TRM v1.0 chapter 40.

Maker Fighter 1.4 reaches its menu on the intermediate RGB SRM build.
Its log records a 512 × 288 canvas and SRM to 720 × 1280. The frame
shows TAG and TROPHIES. That run has no USB peripheral connected.

The original Arduino speaker sketch failed to compile at `##include`.
Correcting only that line in a separate copy compiled under M5Stack
Arduino 3.2.5 and produced 209,558 samples of 48 kHz digital I²S0 PCM,
including 11,523 nonzero samples. Analog output and codec behavior
remain unverified.

The library checks, P4 and S3 suites, native and WASM Clippy, and both P4
device-mode USB MSC goldens passed. CoreS3 docs passed 15/15 and
Cardputer-ADV docs 11/11. The four hello workloads had identical
instruction counts and console bytes over three runs per revision.

Weighted arbitration timing and some DMA2D subsampling modes remain
outside the graphics coverage. Physical hardware, browser guest runs,
USB host acceptance, microphone and the remaining Tab5 board
peripherals were outside these checks. Revert the four commits in
reverse order to remove this delivery.
