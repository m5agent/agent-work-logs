# M5Stack Tab5 bring-up inventory

Baseline: esp32sim `76e8b35710d1879e073f73c4a03bd11b216fb95f`.
Board contracts: M5GFX and M5Unified 0.3.0, M5Stack Arduino 3.2.5
(`idf-release_v5.4-858a988d-v1`), and the original Tab5 preset (16 MiB
flash, 32 MiB PSRAM). M5GFX selects Tab5X on P4 revision 3 or later. That
selection is independent of the glass fitted to the board.

| Path | Firmware contract | Baseline gap |
| --- | --- | --- |
| Board detection | M5GFX `board_detect/m5/esp32p4.inl` bit-bangs SDA 31 and SCL 32 to ID register 1 of both PI4IOE5V6408 devices (0x43, 0x44), sets rails and reset, then selects GT911 (0x14) or Sitronix (0x55, firmware 3 for ST7123, 1 for ST7121) | P4 I2C1 has hardware traffic, but no Tab5 devices or GPIO open-drain bridge |
| DSI DBI | Two lanes, ILI9881C page select FF 98 81 01 and page-1 registers 00/01/02 through GEN_PLD_DATA RX FIFO (issue 188 fallback). Standard DCS sleep and display control. ST7123 and ST7121 use their own initialization tables | DSI host and bridge are register RAM |
| DSI DPI | 720 × 1280 native scanout, GPIO 22 LEDC. IDF v5.4.1 and v5.5.4 `esp_lcd_panel_dpi.c` configure the bridge and DW-GDMA linked lists on PSRAM. M5GFX writes the framebuffer directly in its drawing methods and requests DMA2D for the IDF copy path | DW-GDMA, DMA2D and PPA are register RAM. Existing SPI2 display path is independent |
| Touch | GT911 status/coordinates/acknowledgement, or ST7123 16-bit-addressed capability and contact packets, INT GPIO 23 | GT911 is S3-local, no Sitronix endpoints |
| Audio | ES8388 playback and ES7210 microphone through I2S and I2C configuration | P4 has I2S1 transmit through AHB-GDMA. Need Tab5 I2S port/routing, RX and codec data-plane checks |
| IMU | BMI270 over internal I2C | Shared model exists, needs board attachment and motion verification |
| RTC | RX8130 time registers and alarm/timer output | Need RX8130 device and wake/power integration |
| Battery | INA226 16-bit I2C registers, IP2326 charger state through PI4IOE, push button/power logic | Need board state and input injection. The IP2326 has no independent I2C endpoint |
| microSD | SDMMC slot 0; Arduino documentation example actually uses SPI on GPIO 42/43/44/39 | Native SDMMC/IDMAC present. SPI mode needs the physical socket route and a shared card |
| USB | HS OTG and host enumeration for Maker Fighter (issue 226) | P4 uses DWC2 buffer DMA, device mode already has MSC goldens. Guest host channels and HID/class probes need separate verification |
| Wi-Fi | ESP32-C6, ESP-Hosted SDIO with CLK 12, CMD 13, D0–3 11/10/9/8 and reset 15 | P4 already has SDIO/C6 support. Tab5 reset/antenna/profile and matched ESP-Hosted firmware need verification |
| Other paths | SC2356 on CSI and SIT3088 on UART1/direction GPIO 34 | CSI absent. RS485 wiring and transport remain to be exercised |

## Documentation cases

English Arduino pages under `static/en/arduino/m5tab5` contain touch button,
multi-touch, IMU, microphone, speaker, power/battery, power output control,
local RTC, SNTP RTC, second-level timed wake, specified-time RTC wake,
microSD read/write, Wi-Fi station/AP, Wi-Fi scan and antenna selection.
The programming guide covers toolchain, download mode and upload.

English UIFlow2 `static/en/uiflow2/Tab5/program.md` covers flashing,
access-code wireless connection, USB connection and program run/download.
It links Screen widgets, IMU, Speaker and SDCard and lists the startup
firmware modules EZDATA, ADC, GPIO, UART, Wi-Fi, I2C, APP.LIST, Sleep, Output,
Sound and Screen. Those are distinct validation routes. The page links
shared API examples and does not embed standalone Tab5 sketches.

Acceptance starts with firmware-originated DSI pixels and actual I2C contact
reports that cause the documentation program to redraw. Check the ILI9881C
fallback independently because current M5GFX can select the original panel
solely from a GT911 ACK. Draw-accelerator, audio, storage, network and USB
claims need their own inputs and observations on the same firmware.
