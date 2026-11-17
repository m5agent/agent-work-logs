# Native RISC-V crash symbolization on Nesso N1

The ESP-IDF v5.5.4 probe printed `RISCV_C6_CRASH_PROBE_BOOT` and `RISCV_C6_CRASH_PROBE_ARMED`, then called `abort()` from a named function. Both the reference and candidate Device Service used the same native C6 binary, merged Flash and application ELF. The reference admitted the ELF by identity and its Xtensa-only parser declined the RISC-V symbol table.

The new parser path accepts native ESP32-C6 `qemu` application executables in ELF32 little-endian RISC-V ILP32 soft-float format, with optional RVC. The validated probe's header has `EM_RISCV`, `ET_EXEC`, and flags `0x1`. The existing identity check requires a unique valid application descriptor, a matching panic-prefix from the same session, and the full SHA-256 of the application ELF. A distinct C6 ELF with the same machine type stayed ineligible. ABI and machine errors return an unavailable symbol result. [RISC-V ELF ABI](https://riscv-non-isa.github.io/riscv-elf-psabi-doc/)

| Guest address | Receipt field | Candidate symbol | Espressif control |
| --- | --- | --- | --- |
| `0x40804cb8` | Core 0 `MEPC` | `panic_abort+18` | `panic_abort` |
| `0x4200a5dd` | `panic.abort_call_site_pc` | `trigger_riscv_abort+39` | `trigger_riscv_abort` |

The API and same-session ZIP agreed on the firmware digest, ELF identity and symbols. The ZIP's verified serial digest covered the bounded console data used for parsing. After stop, the retained report still matched. The owned process, session Flash and lease were released. A separate same-path Core2 watchdog control on native Xtensa retained its `matched_xtensa_elf_function_ranges` report.

An isolated rerun on the queued integrated source `20f7e2bece0ace93574b9129576c9b8b14ac71b5` used the same native C6 executable, firmware and application ELF. Both symbols resolved again. The integrated ZIP SHA-256 is `0dbbba38d4d9fef937f0cc060774663ae6a43589290b2facfb96ed571c0a321d`. [Integrated validation](evidence/integrated-rerun-summary.json)

## Reproduction

Use `tests/firmware/crash_diagnostics/riscv_c6` and the pinned ESP-IDF v5.5.4 source. Build using an absolute build and SDKCONFIG path and merge with the generated Flash offsets.

```sh
idf.py -B "$BUILD_DIR" -DSDKCONFIG="$BUILD_DIR/sdkconfig" -DIDF_TARGET=esp32c6 build
cd "$BUILD_DIR"
python -m esptool --chip esp32c6 merge_bin --fill-flash-size 16MB -o merged.bin @flash_args
```

Start an isolated Device Service with the recorded C6-native QEMU and ROM. Upload the merged image and exact application ELF and register the image for `nesso-n1`. Open a native `qemu` session. After the two probe markers, read `GET /api/v1/sessions/{id}/crash` with the matching ELF digest, no ELF, and a mismatched same-architecture ELF. Compare the two reported PCs to `riscv32-esp-elf-addr2line -f -e m5_riscv_c6_crash.elf`. Obtain the evidence ZIP with `include=serial,logs,crash` and the matching ELF digest. Stop with `purge=0&retain_flash=0`, then read the retained report and check owned cleanup.

## Limits and rollback

The current report identifies function ranges for guest-reported addresses. RISC-V live register sampling, stack unwinding, other RISC-V boards, Tab5, browser WASM and physical hardware were `NOT RUN`. A request to the live PC endpoint returned `409 cpu_pc_not_supported` for this C6 guest. Source rollback returns the native crash API to the earlier symbol format coverage. Existing retained session data needs no migration.

This record retains bounded derived receipts and measured hashes. Raw ELF, firmware, ZIP, local paths and session identifiers are excluded.
