# Device Service parity in esp32sim

- Date `2026-11-27`
- Result `PARTIAL`
- Work type `code_change`
- Source [Device Service comparison fixtures](https://github.com/m5agent/agent-work-logs/blob/c85b8f0e84a51be65f1ab8273373bd472902fd74/records/m5stack-esp-emulator/2026-11-27-esp32sim-runtime-parity/per-device.md)
- Runtime [esp32sim @ 9eeb9a61e64cd3d3de6e4262fac13b8a3dc2f34d](https://github.com/m5agent/esp32sim/tree/9eeb9a61e64cd3d3de6e4262fac13b8a3dc2f34d)
- Environment native macOS arm64 virtual-device validation over the inherited Unix socket

The fork exports the visible StopWatch panel and provides the service with Flash readback, device-state and controller samples, runtime SD insertion and ejection, and network fault controls. PaperMono redraws after startup and the measured PaperColor refresh matches the product specification.

## Evidence

- [Report](report.md) covers the display measurements, protocol checks, compatibility and replay results.
- [Run](run.json) records the source versions and the verification commands.
- [Evidence summary](evidence/summary.json) contains runtime, ROM, firmware and frame SHA-256 values and guest observations.

## Remaining coverage

A PaperMono hold during startup still expires before the application reads touch. Tab5's hosted Wi-Fi controller has CLI network modes and needs a dedicated path for live fault control. Camera SCCB fixtures require the documented GPIO18 power sequence. The report records all regression coverage and known baseline failures. Physical hardware and service-default rollout are outside this record.
