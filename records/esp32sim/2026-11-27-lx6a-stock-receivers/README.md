# LX6-A shared receivers and alternate stock startup

- Date 2026-11-27
- Result PARTIAL
- Work type classic ESP32 controller support and stock firmware validation
- Request LX6-A follow-up for LX6-B and LX6-C
- Source [esp32sim branch tip](https://github.com/m5agent/esp32sim/tree/082938f4333f0fcbb1f16dca0cf3146f3e226ba3)
- Environment native AArch64 macOS, ESP32 and ESP32-S3 virtual devices

RMT RX, the raw PDM waveform tap and the cyclic DAC reference passed controller and guest checks. The DAC code comes from LX6-C. M5Burner AtomU catalog v0.1 passed the launcher and device checks. The tested public GitHub Echo images still fail the same import.

[Report and candidate docs note](report.md) · [Run identities](run.json) · [Controller guest](evidence/controller-guest-summary.json) · [Stock inputs](evidence/stock-summary.json) · [Regressions](evidence/regression-summary.json)
