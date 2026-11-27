# ESP Emulator browser board qualification

- Date 2026-11-27
- Result PARTIAL, browser virtual-device validation
- Work type code change
- Repository [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- Environment macOS, Chrome, exported project-relative static site
- Source and artifact hashes in [run.json](run.json)

Fifteen board cases passed the local workbench acceptance. Fourteen add new
esp32sim profiles. Cardputer K132 repeats the existing lane using the fixed
GPIO0 example. The browser observed one DedicatedWorker during each case and
zero after Stop before it closed the context.

- [Per-device report and reproduction](report.md)
- [Firmware, controller events, frames and teardown summary](evidence/local-browser-summary.json)
- [Prior Pages catalog release and baseline](https://github.com/m5agent/agent-work-logs/tree/ca41d8b12a603d8cec92e278e8031b1c31d0bd86/records/m5stack-esp-emulator/2026-11-27-esp32sim-catalog-rollout/followups/pages)

This record covers browser-WASM. Hardware and Device Service are outside the
execution in this record. The hosted issue and remaining boards are open.
