# Reproduce retained Core2 crash task reports

The previous watchdog experiment established that Espressif's decoder could read this capture manually. Device Service retained UART bytes and crash observations. It had no repeatable offline command that checked the evidence inputs before extracting tasks, and presence of UART delimiters alone did not verify the dump payload.

The new offline CLI at `platform/tools/decode_esp32_coredump.py` binds the evidence ZIP manifest and crash receipt to their archived UART bytes. It finds a single dump after the recorded panic and before any subsequent boot. It checks the ESP-IDF ELF CRC32 `0x0102` container and its embedded application ELF hash prefix. The supplied full application ELF SHA-256 must also match the supplied merged image's app descriptor, the receipt and the panic digest. The version-checked vendor decoder and GDB run inside a macOS sandbox with network access denied, writes limited to a private temporary directory, GDB auto-loading disabled, and wall-time/output limits. The JSON report contains named tasks, current and base priority, used and free stack bytes, and the crashed task, along with the case input digests.

## Reproduction

Use the `tests/firmware/crash_diagnostics` fixture at `9436f1475dd03490c304cd90f5780bf5e6484b4e`. Build the watchdog and abort variants with ESP-IDF at `735507283d5b2f9fb363a1901172dbd9e847945d`. The original guest runs used native Core2 QEMU image SHA-256 `cbc0ea74c5763a9d989562b7061516fb3489fdc4056ddce4e016d555c1b86bb2`. Retain each exact 16 MiB merged firmware image and its app ELF. Export a session ZIP including serial and crash diagnostics with that matching ELF. The checked-in fixture summary records guest triggers, original bundle hashes and session cleanup. [Exact source fixture](https://github.com/m5agent/m5stack-esp-emulator/blob/fd08569f06b4afa478eb46da3654c4468e35a5bb/tests/firmware/crash_diagnostics/summary.json)

```sh
python3 platform/tools/decode_esp32_coredump.py \
  --evidence evidence.zip --firmware merged.bin --elf m5_crash_diagnostics.elf \
  --decoder /path/to/esp-coredump --gdb /path/to/xtensa-esp32-elf-gdb
```

This offline replay reused the captured guest sessions. The integrated CLI, regression tests, fixture instructions and bounded task evidence are byte-for-byte identical to the tested source candidate. The output ZIP, firmware and ELF digests equal the original fixture summary for both cases.

| Guest trigger | Dump bytes | CRC32 | Tasks decoded | Crashed task | Priority current/base | Stack used/free bytes |
| --- | ---: | --- | ---: | --- | --- | --- |
| CPU1 interrupt watchdog | 7,536 | `3c97c0a7` | 5 | `fixture_fault` | 2/2 | 1696/2396 |
| CPU1 abort | 10,388 | `c6b23dd2` | 6 | `fixture_fault` | 2/2 | 1696/2396 |

Using the abort ELF for the watchdog archive returns an ELF note digest mismatch. Modifying UART data with the original manifest returns a manifest mismatch. Updating the manifest and receipt to reflect the modified UART bytes still returns a CRC32 mismatch. These checks used an unusable decoder command and returned no report. An isolated sandbox probe verified denial of a connection to a fresh loopback listener and a write outside the private working directory.

## Scope

This record covers ASCII task names admitted by the bounded parser, native Core2 QEMU, and the ESP32 Xtensa ELF CRC32 UART format `0x0102`. RISC-V, other format versions, live inspection and automated HTTP decoding were outside the execution. Neither replay used physical hardware. Reverting the isolated source commit removes the offline CLI and its tests. It has no service configuration or persisted session migration.

The JSON evidence is a bounded derived report. It excludes raw serial, GDB output, source paths, internal task control-block addresses, and session identifiers.
