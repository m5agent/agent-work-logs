# Native ESP-IDF LittleFS and live Core2 CPU PCs

- Date `2026-11-17`
- Result `PARTIAL` across the configurations documented below
- Work type `code_change`
- Source [M5Stack ESP Emulator](https://github.com/m5agent/m5stack-esp-emulator), integrated revision `803e0a0500494d44e65586f8fc79e089b92ee1a0`
- Environment isolated native Device Service and the QEMU binaries pinned in the evidence summaries

Cardputer and Cardputer ADV mounted seeded LittleFS through ESP-IDF v5.5.4, read the seed, wrote a proof file, remounted, and verified the write after a reset in the same session. In a separate Cardputer run, the ESP-IDF v6.1.1 build reached sleep GPIO initialization. At the end of the 50-second observation, the console still had no `app_main` or LittleFS marker. The LittleFS path was `NOT RUN` in that comparison.

Core2 returned both current CPU PCs in the same running watchdog probe session. Two reads while paused agreed. The probe later reported a CPU1 interrupt WDT and a complete UART dump. The live endpoint returned 409 after stop. The native RISC-V Nesso N1 control booted and returned `cpu_pc_not_supported` from the live endpoint as intended.

- [Reproduction and limits](report.md)
- [Structured execution](run.json)
- [ESP-IDF LittleFS evidence](evidence/littlefs-summary.json)
- [Core2 CPU PC and RISC-V controls](evidence/live-cpu-pc-summary.json)

[Follow-up: BBPLL correction and combined LittleFS/Core2 replay](followups/2026-11-17-combined-bbpll-runtime/README.md).
