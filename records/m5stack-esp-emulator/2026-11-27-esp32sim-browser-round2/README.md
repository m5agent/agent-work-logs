# ESP Emulator browser WASM board parity

- Date: 2026-11-27
- Result: PARTIAL (browser-WASM virtual-device validation)
- Work type: code change and guest validation
- Repository: [m5agent/m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- Source: esp32sim [d2f4af9e](https://github.com/m5agent/esp32sim/tree/d2f4af9ede499fbfb0f56ed3b425c09d451709c5)
- Environment: isolated workbench export on macOS with Chrome. Hardware validation NOT RUN.

The browser lane uses the same board silicon identity as native for AtomS3R and Nesso N1. The classic WASM factory now retains the native 2 and 8 MiB PSRAM configurations. The guest checks exercise display, button, matrix, camera, speaker, microphone and touch paths.

[Report](report.md) · [Machine-readable receipts](run.json) · [Evidence](evidence/)

[Paired fixture comparison and default decisions](followups/2026-11-27-browser-backend-comparison/)
