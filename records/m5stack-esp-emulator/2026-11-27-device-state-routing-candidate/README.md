# Device Service board-state and routing candidate

- Date `2026-11-27`
- Result `PARTIAL`
- Work type `code_change`
- Scope M5Stack virtual-device validation on macOS arm64, using isolated leases and saved reviewer jobs
- Source and fixture identities are in [the report](report.md) and [the run record](run.json)

The candidate returned all registered component fields on 38 native leases across 19 boards. Eight restricted C6 Wi-Fi runs verified association, DHCP and Ethernet capture. The 56-case service oracle passed 56/56 on esp32sim and 46/56 on QEMU in each trial. Guest-side fixtures, diagnostic images, Tab5 stereo and frame review, and some regression lanes still block a wider default change.

## Evidence

- [Per-device routing and reviewer results](report.md)
- [Structured execution record](run.json)
- [Live state and cleanup](evidence/device-state-summary.json)
- [Legacy state fixture replay](evidence/state-fixture-summary.json)
- [C6 virtual network](evidence/c6-network-summary.json)
- [Tab5 stock four-way comparison and docs cases](evidence/tab5-summary.json)
- [Flag-ON reviewer jobs](evidence/reviewer-summary.json)
- [Native oracle trial 1](evidence/oracle-esp32sim-1-summary.json) and [trial 2](evidence/oracle-esp32sim-2-summary.json)
- [QEMU oracle trial 1](evidence/oracle-qemu-1-summary.json) and [trial 2](evidence/oracle-qemu-2-summary.json)
