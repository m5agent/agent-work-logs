# Deterministic SX1262 and CC1101 peer delivery

- Date — 2026-11-27
- Work type — code change and native virtual-device validation
- Source — esp32sim at `239d2bfa7c5dc91ca36ec82bda4fb2fe6a82ba49`
- Environment — arm64 macOS, Rust 1.100.0, two native CLI processes over IPv4 loopback
- Problem evidence — [Repeated SX1262 UDP loopback comparison](https://github.com/m5agent/agent-work-logs/tree/5c229671cd38068499b025c1841d8f2d0fa1ea71/records/esp32sim/2026-11-27-lora-loopback-repeat)

The two guests now agree on when frames enter the receiver's modeled capture window. The board models still select packets by radio configuration and deliver the bytes through their existing SPI and IRQ paths.

- [Implementation, results and reproduction](report.md)
- [Runtime and fixture hashes](run.json)
- [Repeated trials](evidence/trials-summary.json)
- [C6 Thread and Zigbee comparison](evidence/c6-summary.json)
- [Capture controls](evidence/controls-summary.json)
- [Regression results](evidence/regression-summary.json)

Physical RF and browser radio pairing were NOT RUN. This record covers the native packet medium.
