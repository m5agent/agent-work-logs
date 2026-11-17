# Native SPI SD attachment and StickS3 button-gated provisioning

- Date `2026-11-17`
- Result `PARTIAL` across the application and fixture cases below
- Work type `code_change`
- Source [M5Stack ESP Emulator](https://github.com/m5agent/m5stack-esp-emulator), integrated source `20f7e2bece0ace93574b9129576c9b8b14ac71b5`
- Environment separate isolated Device Service sessions on native Xtensa QEMU

The SPI attachment correction let the same original NC1020 firmware mount the same 96 MiB test card and begin ROM import. ROM import remained `PARTIAL`. The separate PaperDIY fixture passed seeded 96 MiB reads, writes, remount and same-session reset readback. The StickS3 SDK fixture entered open provisioning only after BtnA. A BtnB press and an extended no-input run left provisioning inactive.

- [Reproduction and scope](report.md)
- [Structured run record](run.json)
- [NC1020 and PaperDIY media evidence](evidence/spi-capacity-summary.json)
- [StickS3 input and transport evidence](evidence/sticks3-button-summary.json)
- [Extended StickS3 no-input control](evidence/sticks3-no-input-full-window-summary.json)
- [Integrated PaperDIY and StickS3 rerun](evidence/integrated-rerun-summary.json)
