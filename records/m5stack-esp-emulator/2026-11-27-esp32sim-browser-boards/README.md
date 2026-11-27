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

[Prepared Pages release](https://github.com/m5agent/m5stack-esp-emulator/releases/tag/pages-20261127-dd6265db) is live.
Its manifest SHA-256 is `38cf12dcfdb8d9cdc3ecab92d7fa3cc568cf75a652a9048033031d738cadf1dd`.
All 2,209 indexed live assets matched. Chrome passed the 14 new
guest profiles and the existing Cardputer K132 against this deployment.

- [Live guest, firmware, controls, frames and teardown evidence](evidence/live-browser-summary.json)
- [HTTPS asset readback](evidence/live-asset-readback.json)
- [Local 72-case QEMU-WASM retry and supplementary gates](evidence/local-release-gates-summary.json)
- [Hosted UI-04 failure](evidence/hosted-qemu-summary.json)
- [Withheld device probes](evidence/excluded-candidate-summary.json)
