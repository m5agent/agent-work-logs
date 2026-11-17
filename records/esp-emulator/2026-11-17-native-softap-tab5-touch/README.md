# Native SoftAP association and Tab5 original firmware touch

- Date `2026-11-17`
- Result `PARTIAL` across the feature lanes below
- Work type `code_change`
- Source [M5Stack ESP Emulator](https://github.com/m5agent/m5stack-esp-emulator)
- Integrated source [fixed validation ledger](https://github.com/m5agent/m5stack-esp-emulator/blob/fd08569f06b4afa478eb46da3654c4468e35a5bb/docs/validation-ledger.md)
- Environment isolated native Device Service sessions using ESP32-S3 QEMU and macOS arm64 esp-emu

The same ESP32-S3 SoftAP probe reported station association on Cardputer and Cardputer ADV with the corrected QEMU runtime. The old runtime received authentication on ADV and produced neither authentication nor association responses. SoftAP DHCP and captive portal HTTP remained open. Separate STA controls reached DHCP and fixture HTTP.

An unmodified CarPlay v1.0.0 session on Tab5 acknowledged GT911 touch reports and opened the pairing-clear dialog from a single tap. The application received an inert blank-area tap and rejected input beyond the display boundary. Earlier startup failures leave DSI startup reliability `PARTIAL`. An independent staged firmware review of the same BIN remains `SIM_PARTIAL`.

- [Reproduction and scope](report.md)
- [Structured execution](run.json)
- [SoftAP and STA comparison](evidence/softap-summary.json)
- [Tab5 GT911 application and controller](evidence/tab5-touch-summary.json)
- [Separate Core2 offline core dump follow-up](../2026-11-17-native-crash-diagnostics/followups/2026-11-17-offline-coredump-task-cli/README.md)
