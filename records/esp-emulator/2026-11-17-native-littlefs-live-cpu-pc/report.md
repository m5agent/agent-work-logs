# Native data partition and crash observation validation

All guest results in this record are virtual-device validation. The integrated source is `803e0a0500494d44e65586f8fc79e089b92ee1a0`. The exact executions used the source and runtime SHA-256 values recorded separately in each summary.

## ESP-IDF LittleFS on Cardputer and Cardputer ADV

The firmware mounts the LittleFS data partition at `0x110000` with size `0x100000` and subtype `0x83`. `esp_vfs_littlefs_register` uses formatting disabled. The probe reads and lists the seeded `FIXTURE.TXT`, writes `PROOF.TXT`, unmounts and remounts the volume, then reads the proof. The device service fixture is applied to the per-session Flash image. This run qualifies ESP-IDF guest behavior on that storage path.

| Guest and input | Mount and initial contents | Write and remount | Later reset |
| --- | --- | --- | --- |
| Cardputer, ESP-IDF v5.5.4, seed supplied | `seeded=1 listed=1 prior=0` | `wrote=1 restored=1 listed=1` | `prior=1` |
| Cardputer ADV, ESP-IDF v5.5.4, seed supplied | `seeded=1 listed=1 prior=0` | `wrote=1 restored=1 listed=1` | `prior=1` |
| Cardputer, ESP-IDF v5.5.4, empty baseline | `seeded=0 listed=0 prior=0` | `wrote=1 restored=1 listed=1` | Outside this control |
| Cardputer, ESP-IDF v6.1.1, same seed | `FAIL` at guest startup before `app_main` | `NOT RUN` | `NOT RUN` |

All three v5.5.4 cases retained the pre-stop ZIP and kept the live Flash outside the target partition byte-identical to the baseline. The uploaded artifacts also stayed unchanged. The v6.1.1 comparison used the same runtime and LittleFS seed with a different build's merged Flash. Its last observed stage was ESP-IDF sleep GPIO initialization. The console contained 2,648 bytes and none of the application or LittleFS markers after 50 seconds. That observation establishes a startup failure for this run. The cause of the startup stall and v6.1.1 LittleFS behavior remain undetermined. All four sessions released Flash and leases. [Exact LittleFS cases](evidence/littlefs-summary.json)

From `tests/firmware/littlefs_partition` use ESP-IDF v5.5.4 (`735507283d5b2f9fb363a1901172dbd9e847945d`), LittleFS component `1.21.1` and `littlefs-python 0.15.0`. Build the probe and prepare the 8 MiB bootable empty baseline plus the 1 MiB seed.

```sh
idf.py -B build build
python3 prepare_images.py --build build --out "$TEST_OUTPUT"
```

1. Start a dedicated native Device Service. Upload the baseline and seed and register the 8 MiB baseline as merged firmware for the target model.
2. Create a native session with `storage.filesystem.image_artifact_id` set to the uploaded seed digest, `partition_label` set to `storage`, and `format` set to `littlefs`.
3. Read the initial UART markers, including `LITTLEFS_PROBE_DONE`. Reset the same seeded session and require `prior=1` in new UART data. Run the empty-baseline control in a fresh session with no seed supplied.
4. Compare the preboot Flash receipt with the baseline replaced only at `[0x110000, 0x210000)`. Request `include=manifest,serial,storage,flash` before stop. Compare the live Flash for unchanged bytes outside the target partition and rehash the uploaded artifacts. Stop with `purge=0&retain_flash=0` and check lease release.
5. Compare the separate Cardputer v6.1.1 build at SDK commit `051e4c4eb20346e043cdd47bc388fde75ff8af63` with the same fixture and native runtime. Distinguish last startup markers from guest filesystem evidence.

## Live Xtensa CPU PCs from one Core2 session

The `GET /api/v1/sessions/{id}/crash/cpu-pc` endpoint uses the existing local QMP connection to read each CPU's current PC. The response carries the firmware digest and before/after QEMU states. It returns CPU indices and PCs without general register or monitor output. The operation requires the existing `serial.read` runtime ACL when configured. It leaves the run state alone, uses a fixed register query, and rejects a detected state change. Running vCPU reads are sequential. A transient reset can occur between the state checks.

The ESP-IDF v5.5.4 Core2 watchdog probe emitted `CRASH_PROBE_BOOT`. Both PCs were read while running. The testing harness paused the guest explicitly and issued two reads, both bracketed by `paused`, with identical CPU0/1 values. It resumed the guest separately and the API observed running again. The guest then emitted a CPU1 interrupt watchdog panic and UART dump. After panic, current PCs were `0x400d1b33` and `0x400814e6`, while the guest's panic-time tagged PCs were `0x4000bfea` and `0x400d7d1b`. The same-session archive passed integrity checks. A post-stop sample returned HTTP 409 `session_not_running`. [Exact CPU samples](evidence/live-cpu-pc-summary.json)

Reproduce from `tests/firmware/crash_diagnostics`. Build the watchdog variant with the pinned ESP-IDF v5.5.4 and `-DCRASH_PROBE_WATCHDOG=ON`, merging bootloader, partition table and app as listed in the build's `flash_args` into a 16 MiB image. Keep the exact matching ELF. Register it for Core2 in an owned native QEMU session. Wait for `CRASH_PROBE_BOOT`, sample the live endpoint, and separately check the expected QEMU states and panic receipt. The test harness uses the same session-local QMP connection to pause and resume under its exclusive control. The HTTP route needs no host GDB connection or writable monitor command. Wait for the CPU1 WDT and UART dump end, then archive `include=serial,logs,crash` with the matching ELF and save the live PC response alongside that ZIP. Stop without purging the session and verify the 409 response, no remaining process, and lease release.

The separate Nesso N1 ESP32-C6 MWDT fixture returned the expected UART readiness marker and HTTP 409 `cpu_pc_not_supported`. With the exact normalized firmware descriptor and matching RISC-V ELF, Espressif `riscv32-esp-elf-addr2line` resolved the known symbol-table address `0x42000020` to `setup()` and a source line. That address came from the ELF symbol table. This demonstrates offline toolchain compatibility. RISC-V live PC sampling and panic attribution, physical hardware and browser WASM were `NOT RUN`.

## Retention and rollback

The evidence comprises bounded derived summaries with input, runtime, capture and ZIP digests. It excludes raw archives, host paths and unique session identifiers. A source rollback removes the live API and its contract. The LittleFS follow-up adds fixture sources and evidence for the existing filesystem API. Neither change migrates service data.

## Later same-artifact replay

The initial v6.1.1 startup failure above is retained. Live PC diagnosis and subsequent same-artifact runs are documented separately. [BBPLL correction and combined runtime replay](followups/2026-11-17-combined-bbpll-runtime/README.md)
