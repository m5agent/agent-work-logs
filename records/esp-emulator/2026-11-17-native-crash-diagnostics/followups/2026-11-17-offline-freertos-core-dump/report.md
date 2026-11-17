# Offline ESP-IDF FreeRTOS core dump control

Use the controlled Core2 dual-core watchdog output from the existing native
crash probe. The exact admitted application ELF matched the full hash
referenced by the same session. Extract the UART dump between the ESP-IDF
delimiters. Decode each Base64 line independently because intermediate records
are padded, and verify the decoded container length and CRC32. The fixture
uses the ESP32 `0x0102` envelope and retained ELF payload.

With outbound network denied, Espressif's `esp-coredump` 1.17.2 decoded the
exact capture with the trusted Xtensa GDB tooling. It reported five FreeRTOS
tasks, identified `fixture_fault` as the crashed task and resolved
`trigger_fault` at the top of its current stack.

The offline reproduction command is `esp-coredump --chip esp32 info_corefile
-t b64 -c <uart-body> -g <trusted-xtensa-gdb> <matching-application.elf>`.
Use only the full verified ELF. Keep the raw UART dump and debugger output
private. [ESP-IDF core dump format and reporting](https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32/api-guides/core_dump.html)

This is an offline decoder replay from a native virtual device. The live
Device Service task table, RISC-V decoding, physical hardware, and original
firmware without exact symbols were not verified. The summary omits memory
contents, task addresses and local paths.
