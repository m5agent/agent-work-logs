# R3-D2 — tracked full device matrix on the repaired native runtime (2026-11-06)

- Scope: `.work/retest-20261106/device-matrix/` (owner: teammate `r2-device`, shared task `task-15`)
- Runbook: `.work/retest-20261106/RUNBOOK3.md` § D2; issue-repair background: `docs/evidence/2026-11-05-latest-firmware-issues/`
- Lane: **virtual-device validation** — direct QEMU on the repaired "native final integration" runtime; not physical hardware.
- Tracked runner: `tests/uiflow2/run_device_matrix.py` (33 matrix devices, no derived runner, tracked matrix as-is).
- Interpreter: system `python3` 3.13 with `PYTHONPATH=.work/py:platform/tools:tests/uiflow2` per Lead correction;
  the `.work/issue-review-venv/bin/python3.12` attempt is preserved under `../device-matrix-venv312-invalid/` and is **not**
  counted as device evidence (`.work/py/littlefs` is py3.13-built → circular-import error under 3.12).
- Machine-readable: `results.json` (33 device cases + retry/diagnostic runs + repair-verification matrix).
- Candidate: `candidates/classic-flash-stub-instability.md`.

## Execution identities

| item | value |
| --- | --- |
| repaired runtime (S3/LX6) | `.work/issue-repair-20261105/runtime-clean/source/build/qemu-system-xtensa` sha256 `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e` |
| C6 runtime | `.work/M5StopWatch-QEMU/build/qemu-c6/build/qemu-system-riscv32` sha256 `25497c521ebd5838a56b066551dd5c33d6dd00df853ed4a256fcca79944de7db` |
| ROM dirs | `.work/M5StopWatch-QEMU/build/qemu/pc-bios` / `…/qemu-c6/pc-bios` |
| tab5 emulator | `.work/esp-emu-versions/0.50.0/…/esp-emu` sha256 `a4c3468a4abf3f2e55ca0912fa7cdfbe5e101ecb6ab74a9ec35182d70ba6a771` |
| firmware | 30/30 cache images re-hashed == `.work/uiflow-latest-20261105/firmware/manifest.json` (v2.5.5 x4 / v2.5.4 x23 / v2.5.4-4MB x1 / pinned x2, `version=null`) |
| firmware label note | the 2026-11-06 re-fetch log prints a different upstream version label for the same sha256 bytes (e.g. `atoms3 v2.5.3` vs manifest `v2.5.4`); both are recorded per case as `firmware_version` / `firmware_version_fetch_log_label`. This is an upstream metadata inconsistency observation, not filed as a candidate by D2. |
| esptool | 5.6.0, `loader=stock-esptool-stub` (classic LX6 flash lane) |
| concurrency | runner is sequential (1 QEMU); other round-3 scopes ran concurrently; load avg 8.6–14.1 during primary run, 6.5–8.8 during retries, ~5.1 during direct diagnostics |

## Result — 33 matrix devices

Primary run: **PASS 20 / FAIL 12 / EXCLUDED 1**. Every FAIL was re-run once with the identical command;
double-FAILs additionally got the tracked host-image (`--flash-transport direct`) diagnostic lane. All 10
classic-LX6-lane failures are flash-transport failures (`qemu-esptool stock-stub` upload), not assertion or
firmware failures — see the candidate card.

| # | status | count | devices |
| --- | --- | --- | --- |
| 1 | **PASS on primary run** | 20 | stopwatch, sticks3, atoms3, atoms3r, cores3, cardputer-adv, stamplc, stackchan, papercolor, papermono, stickc-plus2, nesso-n1, nanoc6, tab5, atoms3-lite, atoms3u, atom-echos3r, atoms3r-cam, atoms3r-m12, dial |
| 2 | **PASS after retry** (primary FAIL = infra, classic flash lane) | 6 | core2, stickc, stickc-plus, atom-matrix, atom-matrix-v11, atom-echo |
| 3 | **FAIL default flash lane / PASS host-image diagnostic** (infra, regression evidence #178) | 4 | basic-v27, stickc-plus-se, atom-lite, atomu |
| 4 | **NOT RUN** (missing pinned artifacts; no run executed) | 2 | m5stick, stickt2 |
| 5 | EXCLUDED | 1 | cardputer-zero (Linux ARM64 target, out of ESP32/UIFlow2 scope) |

Functional summary: **30/30 ESP32 UIFlow2 matrix devices have evidence of the unchanged assertions passing**
(20 primary + 6 retry + 4 host-image diagnostic); the only residual defect is the #178 flash-lane instability.

## Device table (all 33 matrix devices)

| device | mode | firmware (manifest / fetch label) | primary | retry | direct diag | verdict | repair issues | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stopwatch | ui | v2.5.5 / v2.5.3 | PASS | — | — | PASS | #174 | `.work/retest-20261106/device-matrix/stopwatch` |
| sticks3 | ui | v2.5.5 / v2.5.3 | PASS | — | — | PASS | #174 | `.work/retest-20261106/device-matrix/sticks3` |
| atoms3 | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174, #179 | `.work/retest-20261106/device-matrix/atoms3` |
| atoms3r | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174, #179 | `.work/retest-20261106/device-matrix/atoms3r` |
| cores3 | ui | v2.5.5 / v2.5.3 | PASS | — | — | PASS | #174 | `.work/retest-20261106/device-matrix/cores3` |
| cardputer-adv | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174 | `.work/retest-20261106/device-matrix/cardputer-adv` |
| stamplc | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174 | `.work/retest-20261106/device-matrix/stamplc` |
| stackchan | ui | v2.5.5 / v2.5.3 | PASS | — | — | PASS | #174 | `.work/retest-20261106/device-matrix/stackchan` |
| papercolor | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174, #175, #180 | `.work/retest-20261106/device-matrix/papercolor` |
| papermono | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174 | `.work/retest-20261106/device-matrix/papermono` |
| core2 | ui | v2.5.4 / v2.5.3 | FAIL | PASS | — | PASS (retry; primary FAIL = infra) | #174, #178 | `.work/retest-20261106/device-matrix/core2; .work/retest-20261106/device-matrix/retries/core2/core2` |
| stickc-plus2 | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #172, #174, #178, #184 | `.work/retest-20261106/device-matrix/stickc-plus2` |
| nesso-n1 | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174, #182 | `.work/retest-20261106/device-matrix/nesso-n1` |
| nanoc6 | console | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174, #182 | `.work/retest-20261106/device-matrix/nanoc6` |
| tab5 | tab5-gdb-ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #188 | `.work/retest-20261106/device-matrix/tab5` |
| cardputer-zero | excluded | n/a / n/a | EXCLUDED | — | — | EXCLUDED | — | `` |
| atoms3-lite | console | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #173, #174, #187 | `.work/retest-20261106/device-matrix/atoms3-lite` |
| atoms3u | console | v2.5.4 / v2.5.4 | PASS | — | — | PASS | #173, #174 | `.work/retest-20261106/device-matrix/atoms3u` |
| atom-echos3r | console | v2.5.4 / v2.5.4 | PASS | — | — | PASS | #173, #174 | `.work/retest-20261106/device-matrix/atom-echos3r` |
| atoms3r-cam | console | v2.5.4 / v2.5.4 | PASS | — | — | PASS | #173, #174, #179 | `.work/retest-20261106/device-matrix/atoms3r-cam` |
| atoms3r-m12 | console | v2.5.4 / v2.5.4 | PASS | — | — | PASS | #173, #174, #179 | `.work/retest-20261106/device-matrix/atoms3r-m12` |
| basic-v27 | console | v2.5.4-4MB / v2.5.4 | FAIL | FAIL | PASS | FAIL default lane / PASS host-image diag | #173, #174, #178, #183 | `.work/retest-20261106/device-matrix/basic-v27; .work/retest-20261106/device-matrix/retries/basic-v27/basic-v27; .work/retest-20261106/device-matrix/direct-lane/basic-v27/basic-v27` |
| dial | ui | v2.5.4 / v2.5.3 | PASS | — | — | PASS | #174, #181 | `.work/retest-20261106/device-matrix/dial` |
| m5stick | firmware | n/a / n/a | FAIL | FAIL | — | NOT RUN | — | `.work/retest-20261106/device-matrix/m5stick; .work/retest-20261106/device-matrix/retries/m5stick/m5stick` |
| stickt2 | kernel | n/a / n/a | FAIL | FAIL | — | NOT RUN | — | `.work/retest-20261106/device-matrix/stickt2; .work/retest-20261106/device-matrix/retries/stickt2/stickt2` |
| stickc | ui | v2.5.4 / v2.5.3 | FAIL | PASS | — | PASS (retry; primary FAIL = infra) | #172, #174, #178, #184 | `.work/retest-20261106/device-matrix/stickc; .work/retest-20261106/device-matrix/retries/stickc/stickc` |
| stickc-plus | ui | v2.5.4 / v2.5.2 | FAIL | PASS | — | PASS (retry; primary FAIL = infra) | #172, #174, #178, #184 | `.work/retest-20261106/device-matrix/stickc-plus; .work/retest-20261106/device-matrix/retries/stickc-plus/stickc-plus` |
| stickc-plus-se | ui | v2.5.4 / v2.5.3 | FAIL | FAIL | PASS | FAIL default lane / PASS host-image diag | #172, #174, #178, #184 | `.work/retest-20261106/device-matrix/stickc-plus-se; .work/retest-20261106/device-matrix/retries/stickc-plus-se/stickc-plus-se; .work/retest-20261106/device-matrix/direct-lane/stickc-plus-se/stickc-plus-se` |
| atom-lite | console | v2.5.4 / v2.5.3 | FAIL | FAIL | PASS | FAIL default lane / PASS host-image diag | #172, #173, #174, #178 | `.work/retest-20261106/device-matrix/atom-lite; .work/retest-20261106/device-matrix/retries/atom-lite/atom-lite; .work/retest-20261106/device-matrix/direct-lane/atom-lite/atom-lite` |
| atom-matrix | console | v2.5.4 / v2.5.3 | FAIL | PASS | — | PASS (retry; primary FAIL = infra) | #172, #173, #174, #178 | `.work/retest-20261106/device-matrix/atom-matrix; .work/retest-20261106/device-matrix/retries/atom-matrix/atom-matrix` |
| atom-matrix-v11 | console | v2.5.4 / v2.5.3 | FAIL | PASS | — | PASS (retry; primary FAIL = infra) | #172, #173, #174, #178 | `.work/retest-20261106/device-matrix/atom-matrix-v11; .work/retest-20261106/device-matrix/retries/atom-matrix-v11/atom-matrix-v11` |
| atomu | console | n/a / v2.5.4 | FAIL | FAIL | PASS | FAIL default lane / PASS host-image diag | #172, #173, #174, #178 | `.work/retest-20261106/device-matrix/atomu; .work/retest-20261106/device-matrix/retries/atomu/atomu; .work/retest-20261106/device-matrix/direct-lane/atomu/atomu` |
| atom-echo | console | n/a / v2.5.4 | FAIL | PASS | — | PASS (retry; primary FAIL = infra) | #172, #173, #174, #178 | `.work/retest-20261106/device-matrix/atom-echo; .work/retest-20261106/device-matrix/retries/atom-echo/atom-echo` |

## Repair verification (#172–#188)

Every closed issue #172–#187 that the D2 device matrix can exercise is covered below; #176/#177/#185/#186 belong to
the peripheral/Unit/runtime scopes and are NOT COVERED here (recorded, not claimed).

| issue | scope | D2 verdict | devices with executable evidence | blockers / notes |
| --- | --- | --- | --- | --- |
| #172 | classic ESP32 eFuse package 5/6 admission | **VERIFIED** | stickc-plus2, stickc, stickc-plus, stickc-plus-se, atom-lite, atom-matrix, atom-matrix-v11, atomu, atom-echo | stickc-plus2 (pkg 6) and classic pkg-5 devices pass with the bounded eFuse encoding; blocked devices are flash-lane only |
| #173 | four missing console image builders (generic source composer) | **VERIFIED** | atoms3-lite, atoms3u, atom-echos3r, atoms3r-cam, atoms3r-m12, basic-v27, atom-lite, atom-matrix, atom-matrix-v11, atomu, atom-echo | console fixtures compose without per-device make_image.py; passes on primary/retry/host-image diagnostic lanes |
| #174 | actual VFS layout derived from base partition table + stock preservation | **VERIFIED** | stopwatch, sticks3, atoms3, atoms3r, cores3, cardputer-adv, stamplc, stackchan, papercolor, papermono, core2, stickc-plus2, nesso-n1, nanoc6, atoms3-lite, atoms3u, atom-echos3r, atoms3r-cam, atoms3r-m12, basic-v27, dial, stickc, stickc-plus, stickc-plus-se, atom-lite, atom-matrix, atom-matrix-v11, atomu, atom-echo | every drifted device's composition.json records layout_drift=true and the guest PASSes using the actual partition-table offset |
| #175 | ED2208 partial window/AUTO refresh (extra coverage) | **VERIFIED** | papercolor |  |
| #176 | AXP2101 charging status semantics (peripheral scope) | NOT COVERED BY D2 | — |  |
| #177 | SHA-bound official driver behaviour expectations | NOT COVERED BY D2 | — |  |
| #178 | classic ESP32 esptool stock-stub transport | **REGRESSION EVIDENCE** (lane instability) | core2, stickc-plus2, basic-v27, stickc, stickc-plus, stickc-plus-se, atom-lite, atom-matrix, atom-matrix-v11, atomu, atom-echo | primary 10 FAIL / 1 PASS; retry 6 PASS / 4 FAIL; host-image diagnostic 4/4 PASS -> QEMU esptool stock-stub upload checksum/protocol errors are load/timing flaky |
| #179 | AtomS3 ST7735S panel variant | **VERIFIED** | atoms3, atoms3r, atoms3r-cam, atoms3r-m12 |  |
| #180 | PaperColor UART0 observation + EPD output (extra coverage) | **VERIFIED** | papercolor |  |
| #181 | Dial Python console observation | **VERIFIED** | dial |  |
| #182 | NanoC6 latest startup fixture | **VERIFIED** | nesso-n1, nanoc6 |  |
| #183 | Basic v2.7 BtnB guest redraw fence | **VERIFIED** | basic-v27 | basic-v27 default lane blocked by #178 flash flake; its case PASSes on the host-image diagnostic lane incl. BASIC27_BUTTON_STATE 0 1 0 and FRAME_READY fences |
| #184 | StickC family frame/fixture contract | **VERIFIED** | stickc-plus2, stickc, stickc-plus, stickc-plus-se | stickc/stickc-plus PASS after retry; stickc-plus-se PASSes on the host-image diagnostic lane |
| #185 | executed runtime provenance | NOT COVERED BY D2 | — |  |
| #186 | CoreS3 ADC calibration admission (peripheral scope) | NOT COVERED BY D2 | — |  |
| #187 | AtomS3 Lite Python console observation (UART0) | **VERIFIED** | atoms3-lite | atoms3-lite PASS on the primary run incl. BOARD 137 + RGB markers via real UART0 observation |
| #188 | Tab5 latest official image packing / ELF (open) | STATUS ONLY (open) | tab5 | no conclusion transfer: matrix uses the old emulator merged image, not the latest M5Burner binary |

- **#172** eFuse pkg 5/6: verified — stickc-plus2 (pkg 6) PASS primary; stickc/stickc-plus/atom-matrix/
  atom-matrix-v11/atom-echo PASS retry; stickc-plus-se/atom-lite/atomu PASS host-image diagnostic (pkg-5
  eFuse encoding exercised by `--efuse-pkg-version 5` + real `nvram.esp32.efuse` drive).
- **#173** four missing console builders: verified — the generic source composer built every console fixture with
  no per-device `make_image.py` (atoms3-lite, atoms3u, atom-echos3r, atoms3r-cam, atoms3r-m12, nanoc6, basic-v27,
  atom-lite, atom-matrix, atom-matrix-v11, atomu, atom-echo all reached their assertions; flash-lane-only blocks
  were resolved on retry/diagnostic lanes).
- **#174** actual VFS layout: verified — `composition.json` for every drifted device records `layout_drift=true`
  and the guest PASSes using the actual partition-table offset (no manual offsets in the tracked matrix).
- **#179** AtomS3 ST7735S variant: verified — atoms3 (primary), atoms3r, atoms3r-cam, atoms3r-m12 PASS.
- **#183** Basic v2.7 BtnB fence: verified on the host-image diagnostic lane — `BASIC27_BUTTON_STATE 0 1 0` and the
  three `BASIC27_FRAME_READY` fences are present; the default lane is blocked by the #178 flash flake.
- **#184** StickC frame/fixture contract: verified — stickc/stickc-plus PASS on retry, stickc-plus-se PASS on the
  host-image diagnostic lane; stickc-plus2 (4th family oracle) PASS primary.
- **#187** AtomS3 Lite console: verified — atoms3-lite PASS primary incl. `ATOMS3_LITE_BOARD 137`, RGB marker, real
  UART0 observation.
- **#178** classic esptool transport: **regression evidence / residual instability** — 10/11 classic devices failed the
  stock-stub upload on the primary run, 6 passed a retry, 4 passed the host-image lane; candidate card filed.
- **#188** tab5: status only — matrix tab5 control lane (old emulator merged-image image) PASS (see below); latest
  official image lane remains PARTIAL/open per the repair campaign record, no conclusion transfer.

## FAIL list and classification

| device | primary failure | classification | two-run status |
| --- | --- | --- | --- |
| core2 | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Serial data stream stopped: Possible serial noise or corruption | infra | primary FAIL; retry PASS; direct — |
| basic-v27 | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Serial data stream stopped: Possible serial noise or corruption | infra | primary FAIL; retry FAIL; direct PASS |
| m5stick | missing firmware image <repo>/platform/.cache/firmware/m5stick/factory-test-4m.bin; run the pinned extraction t | known-blocker | primary FAIL; retry FAIL; direct — |
| stickt2 | missing probe ELF <repo>/platform/.cache/firmware/stickt2/probe/stickt2-probe.elf; build it with tests/uiflow2/ | known-blocker | primary FAIL; retry FAIL; direct — |
| stickc | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry PASS; direct — |
| stickc-plus | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry PASS; direct — |
| stickc-plus-se | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry FAIL; direct PASS |
| atom-lite | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry FAIL; direct PASS |
| atom-matrix | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry PASS; direct — |
| atom-matrix-v11 | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry PASS; direct — |
| atomu | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry FAIL; direct PASS |
| atom-echo | QEMU esptool 5.6.0 write failed (2, loader=stock-stub): ERROR: A fatal error occurred: Failed to write to target RAM (result was 0107: Checksum error) | infra | primary FAIL; retry PASS; direct — |

All 10 classic-LX6 FAILs are `infra`: `QEMU esptool 5.6.0 write failed (…, loader=stock-stub)` during stub/RAM
upload (checksum 0107 / protocol 0105 / stream stopped). No firmware or assertion regression was found: the same
cases pass on retry and/or the host-image lane with unchanged markers/frames. m5stick/stickt2 FAIL rows are the
runner reporting missing pinned artifacts (=> NOT RUN, not product failures).

## NOT RUN (explicit)

- **m5stick** (matrix mode `firmware`): `platform/.cache/firmware/m5stick/factory-test-4m.bin` is absent in this
  environment (re-fetch keeps only `uiflow2.bin` cache paths); re-run reproduced `missing firmware image`. No
  UIFlow2 application result is claimed.
- **stickt2** (matrix mode `kernel`): `platform/.cache/firmware/stickt2/probe/stickt2-probe.elf` is absent; the
  bare-metal FLIR probe lane cannot run. Re-run reproduced `missing probe ELF`.
- **cardputer-zero**: EXCLUDED by the tracked matrix — Linux ARM64 target, not an ESP32/UIFlow2 device.

## tab5 (status only)

- Tracked lane `tab5-gdb-ui` (`.work/uiflow2-tab5/tab5-emulator-merged.bin` + ELF; esp-emu native + GDB) **PASS**:
  1280x720, rotation 1, touch logical 640,520 → raw 199,640, `changed_channels=7900`, markers
  `TAB5_I2C_PORT`, `TAB5_UI_DRAWN`, `TAB5_DRAW_AFTER_TOUCH`; after-frame png sha256
  `7a6302a1ad6e8db4731e205e334c353d2e51d59712da7e64f3984a775dfc733e`, flash `esp-emu-esptool` verified.
- This is the **old emulator merged-image control lane, not the latest M5Burner v2.5.4 image**. **#188 remains open**
  (latest official app waits on the P4 DSI PHY); no PASS conclusion transfers to the company image.

## Reproduction

```sh
cd <repo>/
M5_QEMU_XTENSA=$PWD/.work/issue-repair-20261105/runtime-clean/source/build/qemu-system-xtensa \
M5_QEMU_XTENSA_ROM_DIR=$PWD/.work/M5StopWatch-QEMU/build/qemu/pc-bios \
M5_QEMU_RISCV32=$PWD/.work/M5StopWatch-QEMU/build/qemu-c6/build/qemu-system-riscv32 \
M5_QEMU_RISCV32_ROM_DIR=$PWD/.work/M5StopWatch-QEMU/build/qemu-c6/pc-bios \
PYTHONPATH=.work/py:platform/tools:tests/uiflow2 python3 \
  tests/uiflow2/run_device_matrix.py --out-dir .work/retest-20261106/device-matrix
# FAIL retry (identical argv, one device):
#   ... run_device_matrix.py --device <device> --out-dir .work/retest-20261106/device-matrix/retries/<device>
# host-image diagnostic for the classic flash flake:
#   ... run_device_matrix.py --device <device> --flash-transport direct --out-dir <dir>
```

Aggregation: `python3 .work/retest-20261106/device-matrix/tools/build_results.py`.

## Rules / boundaries

- No tracked file edits; no gh/glab writes; all evidence/derived files under `.work/retest-20261106/device-matrix/`.
- Failure-first policy: every FAIL was re-run once with the same command; both runs are retained; the later PASS does
  not erase the earlier FAIL (verdicts and counts show both).
- Interpretation caveat: the venv3.12 attempt in `device-matrix-venv312-invalid/` is an environment error (littlefs
  shadowing), not a device result; the corrected system-python3 run is the evidence of record.
