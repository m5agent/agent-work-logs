# LX6-A and S3-A virtual-device validation

The merge brought `8e82ee95` into `m5/batch-lx6a` and retained a single I2C MPU6886 model at address `0x68`. Both families use the same six-axis setter, guest-configured ranges and latched big-endian bursts. The device model keeps the data-ready, sleep and register reset behavior tested on Atom Matrix. Atom Matrix v1.1 still uses BMI270. The stock AtomS3 guest returned the same stationary vector and both signed injected vectors as the S3-A reference.

## Integration gate

| Check | Result |
| --- | --- |
| CoreS3 docs | PASS 15/15 |
| Cardputer-ADV docs | PASS 11/11 |
| AtomS3 profiles | 39 PASS and 5 inherited DOCS-DEFECT across nine profiles |
| Classic Atom profiles | 28 PASS, 3 DOCS-DEFECT and 2 inherited stock startup FAIL |
| Native and wasm32 Clippy | PASS with Rust warnings denied |
| Workspace Cargo | 1,978 PASS and 7 inherited P4 FAIL |

The five AtomS3 docs defects are the button sketch on Lite and the button and IMU sketches on both AtomS3 LCD revisions. The unchanged sketches lack HWCDC initialization. The S3 launcher and stock button probes passed, and the separate stock MPU6886 probe returned three vectors. The six P4 golden mismatches and the P4 Wi-Fi STA diagnostic mismatch are the same seven accepted failures as the pre-merge run. An intermediate automatic merge also left a duplicate Rust module declaration. The merge commit removes it and the first compile failure is retained in the local evidence.

| Classic case | Lite | Matrix | Matrix v1.1 | AtomU | Echo |
| --- | --- | --- | --- | --- | --- |
| Arduino button, RGB, NEC and log output | PASS | PASS | PASS | — | — |
| Arduino IMU | PASS, no-sensor control | PASS, MPU6886 | PASS, BMI270 | — | — |
| Stock startup | PASS | PASS | PASS | FAIL | FAIL |
| Stock UART0 REPL, button and RGB | PASS | PASS | PASS | PASS | PASS |
| 5×5 stock LED layout | — | PASS | PASS | — | — |
| Converted PDM | — | — | — | PASS | PASS |
| I2S1 speaker | — | — | — | — | PASS |
| EchoRest, PlayMusic, RecordPlay | — | — | — | — | DOCS-DEFECT |

The Echo Arduino build failures remain at `BaiduRest.cpp:175` (undeclared `WiFiClient`) and `LED_DisPlay.h:62` (undeclared `boolean`). AtomU has no dedicated Arduino docs case in the pinned inventory. The other classic results are recorded against the merged runtime. Its build used `CARGO_PROFILE_RELEASE_LTO=false cargo build --release -p esp32sim`. The workspace command used `cargo test --release --workspace --no-fail-fast -- --include-ignored --skip external_`. CoreS3 and ADV used the pinned firmware archive revision in the run record. AtomS3 used the repo's runner and checker, and classic Atom used `tools/run-lx6-atoms.sh`.

## Factory startup diagnosis

The AtomU and Echo guests entered `startup/headless.py` via boot option `1` and failed at its top-level `import M5Things`. The release source has the same unguarded import. Both guest reads of the factory partition matched every byte of the corresponding official input partition by SHA-256. Both 1,728-byte LittleFS `boot.py` reads matched the tagged source by SHA-256. The guest found the expected factory, NVS, PHY and VFS partitions. A scratch NVS key read back `37`, and a temporary Python module loaded from `/flash` returned `41`. The original sparse images and copies padded with erased bytes to 4 MiB produced the same import error and returned board IDs 130 and 142. The official Atom Lite v2.5.3 control imported `M5Things` on the same runtime and reported no module source file. These observations locate the failure in the v2.5.4 firmware's module availability. [UIFlow2 release](https://github.com/m5stack/uiflow-micropython/releases/tag/2.5.4) · [Boot dispatch](https://github.com/m5stack/uiflow-micropython/blob/e437118892520ba987c2d930a2428db1cab65ab1/m5stack/fs/user/boot.py#L34) · [Headless import](https://github.com/m5stack/uiflow-micropython/blob/e437118892520ba987c2d930a2428db1cab65ab1/m5stack/modules/startup/headless.py#L11)

The historical QEMU console tests started from the same official image hashes and replaced the LittleFS volume with an instrumented `boot.py` and `main.py`. Those probes set `_uiflow_run_main = True` and exercise REPL, board controls and audio without the factory launcher. The locally available generic QEMU ESP32 binary reached ROM boot with both unchanged payloads and panicked on cache access before the prompt. It provides no independent import result. Physical boot was NOT RUN. The batch keeps the exact stock contents and startup verdict. [AtomU QEMU evidence](https://github.com/m5agent/m5stack-esp-emulator/blob/74ee6cb006105fe8553eb83071e23ae3361a57f1/docs/evidence/2026-11-02-atomu-host/README.md) · [Echo QEMU evidence](https://github.com/m5agent/m5stack-esp-emulator/blob/74ee6cb006105fe8553eb83071e23ae3361a57f1/docs/evidence/2026-11-02-atom-echo-host/README.md)

Reproduce the stock observation with the board CLI profile and exact firmware SHA from the run record. Read the boot option with `esp32.NVS("uiflow").get_u8("boot_option")`. At the UART0 REPL, list modules with `help("modules")` and try `import M5Things`. The raw serial files are retained locally. The evidence summary retains hashes, exact partition readback and bounded probe results. To roll back the integration, use the first parent of the merge.
