# R2-D — all-device latest-UIFlow2 execution sweep (round 2, 2026-11-05)

- Scope: `.work/uiflow-latest-20261105/round2/device/` (owner: teammate `r2-device`, shared task `task-8`)
- Runbook: `.work/uiflow-latest-20261105/RUNBOOK2.md` § Scope D
- Lane: **virtual-device validation** — direct QEMU (canonical Nov-4 patch-built runtime, sha256 `0e16a9bc…`)
  and the tab5 esp-emu lane. Not physical hardware; no RF/optics/power/mechanics claims transfer.
- Firmware: 30 fetched latest UIFlow2 images, cache SHA-256 re-verified equal to
  `.work/uiflow-latest-20261105/firmware/manifest.json` for all 30 (0 mismatches).
- Tracked files were **not** edited; every adapter/fixture lives under `.work`.
- Machine-readable: `results.json` · tab5 lane: `tab5-attempts.json` ·
  derived partition layouts: `partition-layout.json` · failure cards: `candidates/`

## Result: 30/30 UIFlow2-capable devices executed

| status | count | devices |
| --- | --- | --- |
| **PASS** | **20** | stopwatch, sticks3, atoms3r, cores3, cardputer-adv, stamplc, stackchan, papermono, nesso-n1, tab5 (old-merged-image lane, see caveat), atoms3u, atom-echos3r, atoms3r-cam, atoms3r-m12, basic-v27, atomu, atom-echo, **atom-lite, atom-matrix, atom-matrix-v11** (derived console lane) |
| **FAIL** | **10** | atoms3, papercolor, dial, nanoc6, atoms3-lite, stickc, stickc-plus, stickc-plus-se (all `simulator`); core2, stickc-plus2 (**INFRA-LOAD**) |
| **NOT RUN** | **3** | m5stick, stickt2, cardputer-zero — no latest UIFlow2 build (reasons below) |

Execution lanes (two parallel batches; max 2 concurrent QEMU; classic batch serial-only host-image):
- **b1 / S3+C6 normal lane** — `.work/uiflow-latest-20261105/round2/device/lanes/b1-esp-emu/` (18 devices; esp-emu flash + QEMU)
- **b2 / classic LX6 host-image lane** — `.work/uiflow-latest-20261105/round2/device/lanes/b2-classic-direct/` (11 devices; `--flash-transport direct`; the known esptool blocker #178 is bypassed, **not re-filed**, and only recorded as the lane)
- **derived console lane** — 4 matrix-contract-inconsistent devices; helper `tools/run_device_matrix_round2.py` over
  `device_matrix.round2.json`; `tools/make_image_<device>.py` masters + `fixtures/<device>/` (boot.py/main.py/make_image.py)
- **tab5 lane** — checked-in `run_tab5_ui_test.py`; script `tools/run_tab5_round2.sh old|latest`

Runtime/firmware identities: per-case SHA-256 in `results.json`; runtimes:
canonical xtensa `0e16a9bc…`, tab5 esp-emu `a4c3468a…`.

## Coverage table

| device | mode | firmware | lane | status | classification |
| --- | --- | --- | --- | --- | --- |
| stopwatch | ui | v2.5.5 | b1-esp-emu | PASS | |
| sticks3 | ui | v2.5.5 | b1-esp-emu | PASS | |
| atoms3 | ui | v2.5.4 | b1-esp-emu | FAIL | `simulator` (GC9107 INVON/MADCTL frame 180°-rotated + inverted; exact R1 frame sha reproduced) |
| atoms3r | ui | v2.5.4 | b1-esp-emu | PASS | |
| cores3 | ui | v2.5.5 | b1-esp-emu | PASS | |
| cardputer-adv | ui | v2.5.4 | b1-esp-emu | PASS | |
| stamplc | ui | v2.5.4 | b1-esp-emu | PASS | |
| stackchan | ui | v2.5.5 | b1-esp-emu | PASS | |
| papercolor | ui | v2.5.4 | b1-esp-emu | FAIL | `simulator` (boot hang before REPL) |
| papermono | ui | v2.5.4 | b1-esp-emu | PASS | |
| core2 | ui | v2.5.4 | b2-classic-direct | FAIL→**INFRA-LOAD** | host saturation; quiet serial retry PASS |
| stickc-plus2 | ui | v2.5.4 | b2-classic-direct | FAIL→**INFRA-LOAD** | host saturation; quiet serial retry PASS incl. key input |
| nesso-n1 | ui | v2.5.4 | b1-esp-emu | PASS | |
| nanoc6 | console | v2.5.4 | b1-esp-emu | FAIL | `simulator` (stops at `Startup with network type: WIFI`) |
| tab5 | tab5-gdb-ui | v2.5.4 (ref) | tab5-old-merged | PASS (old image lane) | latest M5Burner binary lane **NOT RUN** (not bootable on this emulator lane) |
| atoms3-lite | console (derived) | v2.5.4 | b1-esp-emu | FAIL | `simulator` (boot hang before REPL; first execution of this device) |
| atoms3u | console | v2.5.4 | b1-esp-emu | PASS | |
| atom-echos3r | console | v2.5.4 | b1-esp-emu | PASS | |
| atoms3r-cam | console | v2.5.4 | b1-esp-emu | PASS | |
| atoms3r-m12 | console | v2.5.4 | b1-esp-emu | PASS | |
| basic-v27 | console | v2.5.4-4MB | b2-classic-direct | PASS | (R1 BtnB canonical residual not reproduced) |
| dial | ui | v2.5.4 | b1-esp-emu | FAIL | `simulator` (boot hang before REPL) |
| stickc | ui | v2.5.4 | b2-classic-direct | FAIL | `simulator` (checked-in case unsatisfiable: 1 colour < min 2) |
| stickc-plus | ui | v2.5.4 | b2-classic-direct | FAIL | `simulator` (1 colour < min 2; unreachable post-frame colour) |
| stickc-plus-se | ui | v2.5.4 | b2-classic-direct | FAIL | `simulator` (1 colour < min 2) |
| atom-lite | console (derived) | v2.5.4 | b2-classic-direct | **PASS** | first execution of this device |
| atom-matrix | console (derived) | v2.5.4 | b2-classic-direct | **PASS** | first execution of this device |
| atom-matrix-v11 | console (derived) | v2.5.4 | b2-classic-direct | **PASS** | first execution of this device |
| atomu | console | pinned artifact | b2-classic-direct | PASS | QOM led-rgb/led-frames validated |
| atom-echo | console | pinned artifact | b2-classic-direct | PASS | PCM/QOM validated |
| m5stick | — | none | — | NOT RUN | no latest UIFlow2 image (EasyLoader factory only) |
| stickt2 | — | none | — | NOT RUN | no latest UIFlow2 build; kernel probe lane out of scope |
| cardputer-zero | — | none | — | NOT RUN | Linux ARM64 target, not UIFlow2/ESP |

## Derived console lane for the 4 matrix-contract-inconsistent devices

Tracked matrix marks `atoms3-lite, atom-lite, atom-matrix, atom-matrix-v11` as `mode=console`, but their
`tests/uiflow2/*_ui_test/` dirs contain only `boot.py`/`main.py` (no `make_image.py`) — round 1 recorded this as
BLOCKED. Round 2 builds derived console fixtures with the **actual latest-firmware partition layout** parsed from
`platform/tools/firmware_analysis.py` (`partition-layout.json`, all partition tables valid):

| device | vfs offset/size (latest PT) | flash | built image sha256 | result |
| --- | --- | --- | --- | --- |
| atoms3-lite | `0x651000`/`0x1ae000` (tracked `0x641000` drifted) | 8 MiB | `738e414a…` | FAIL (pre-REPL boot hang) |
| atom-lite | `0x375000`/`0x89000` (tracked `0x371000` drifted) | 4 MiB | (in results.json) | PASS |
| atom-matrix | `0x375000`/`0x89000` | 4 MiB | (in results.json) | PASS |
| atom-matrix-v11 | `0x375000`/`0x89000` | 4 MiB | (in results.json) | PASS |

Derived probes reuse the checked-in `*_ui_test` main.py/boot.py; only the image builder and matrix entry are derived
(`tools/make_image_*.py`, `fixtures/*/make_image.py`, `device_matrix.round2.json`). The tracked matrix contract
inconsistency itself is unchanged (tracked files untouched) — this lane is the workaround/reproduction path.

## tab5 lane (explicit caveats)

- **PASS — old emulator merged-image lane**: `.work/uiflow-latest-20261105/round2/device/lanes/tab5-old-merged/`
  (`PASS machine=tab5-esp-emu-gdb size=1280x720 touch=640,520 changed=7524`; markers
  `TAB5_I2C_PORT`, `TAB5_UI_DRAWN`, `TAB5_DRAW_AFTER_TOUCH`). This executes the
  `.work/uiflow2-tab5/tab5-emulator-merged.bin` image/ELF (built from the emulator ELF), **not** the M5Burner
  v2.5.4 binary; the company firmware SHA is recorded for reference only and no conclusion transfers.
- **NOT RUN — latest M5Burner v2.5.4 binary lane**: attempted with the real latest partition table
  (16 MiB pad, VFS injected at `0xaa0000`/`0x4c0000`, serial-only probe):
  `E esp_image: invalid segment length 0xffffffff`, `Factory app partition is not bootable`,
  `No bootable app partitions`; emulator times out without `TAB5_UI_DRAWN`. The lane requires an image produced
  from the same emulator ELF, so the official image is not bootable here. Evidence:
  `lanes/tab5-latest-v254-probe/p4.log`, `tab5-attempts.json`.

## Failures and classification

Candidates (reproduction cards) in `candidates/`, one per failing device:

| device | finding | classification | two-round status |
| --- | --- | --- | --- |
| atoms3 | GC9107 `INVON 0x21` + `MADCTL 0xDC` vs QEMU model `invert=false/apply-madctl=true` → 180°-rotated + inverted frame; after-frame packed sha identical to round 1 (`6e83db4d…`) | `simulator` | R1 FAIL → R2 FAIL reproduced |
| papercolor | hangs before REPL (ROM banner + i2c error only) | `simulator` | R1 FAIL → R2 FAIL reproduced |
| dial | hangs before REPL (same signature) | `simulator` | R1 FAIL → R2 FAIL reproduced |
| nanoc6 | stops at `Startup with network type: WIFI` | `simulator` | R1 FAIL → R2 FAIL reproduced |
| atoms3-lite | pre-REPL boot hang (same class as papercolor/dial); first execution via derived console image | `simulator` | R1 BLOCKED → R2 FAIL |
| stickc / stickc-plus / stickc-plus-se | checked-in case unsatisfiable with its own probe (`1` colour < default min `2`; stickc-plus post-frame colour unreachable) | `simulator` (tracked matrix/test contract) | R1 direct-lane defect → R2 reproduced on host-image lane |
| core2 | **INFRA-LOAD**: under host saturation the fixed `--post-input-wait 3.0` captured the after-frame mid-redraw (`000000` @(2,2)); reproduced on canonical **and** matrix-pinned runtimes; quiet-host serial retry of the identical argv **PASS** | `infra` | R1 same-lane PASS; R2 FAIL under load → serial PASS |
| stickc-plus2 | **INFRA-LOAD**: 6 s `--wait` expired before guest boot under load (`before frame blank`); quiet-host serial retry **PASS** incl. `STICKCPLUS2_BTN_A 1` and post-frame colour | `infra` | R1 input residual; R2 FAIL under load → serial PASS |

Host-load disclosure: the primary batches ran while other round-2 scopes saturated the 10-core host
(load avg **10.4–12.9**, ~30 concurrent guest processes); the quiet serial retries ran at load avg **3.1–3.8** with
1 concurrent guest. `results.json` preserves both observations; the FAILs are recorded as `INFRA-LOAD`, not product
failures. A later PASS does not erase the earlier FAIL observation.

## NOT RUN (explicit)

- **m5stick** — no latest UIFlow2 firmware in the fetched manifest (EasyLoader factory firmware only); tracked matrix
  mode=firmware base absent from latest cache.
- **stickt2** — no latest UIFlow2 build (official StickT2 UserDemo only); tracked matrix mode=kernel bare-metal probe
  lane is out of scope for the UIFlow2 device matrix.
- **cardputer-zero** — Linux ARM64 target, not ESP32/UIFlow2 (tracked matrix mode=excluded).
- **tab5 latest M5Burner v2.5.4 binary** — see tab5 lane above (lane precondition not met; old-image lane PASS kept
  separate).

## Rules compliance

- No tracked file edits; no gh/glab writes; no ports 8787/8830; evidence only under `.work/.../round2/device/`.
- Classic LX6 ran on the `--flash-transport direct` host-image lane; the esptool blocker (issue #178) is recorded,
  not re-filed.
- Max 2 concurrent QEMU in the two parallel batches; post-load serial retries at 1 concurrent guest.

## Reproduce

```sh
cd <repo>
# normal lane (example)
PYTHONPATH=platform/tools:tests/uiflow2 <local>/<path> \
  .work/uiflow-latest-20261105/round2/device/tools/run_device_matrix_round2.py \
  --device atoms3r --out-dir /tmp/r2d-atoms3r
# classic LX6 host-image lane (example)
PYTHONPATH=platform/tools:tests/uiflow2 <local>/<path> \
  .work/uiflow-latest-20261105/round2/device/tools/run_device_matrix_round2.py \
  --device core2 --flash-transport direct --out-dir /tmp/r2d-core2
# derived console device (example)
PYTHONPATH=platform/tools:tests/uiflow2 <local>/<path> \
  .work/uiflow-latest-20261105/round2/device/tools/run_device_matrix_round2.py \
  --device atom-matrix --flash-transport direct --out-dir /tmp/r2d-atom-matrix
# tab5 lanes
.work/uiflow-latest-20261105/round2/device/tools/run_tab5_round2.sh old
.work/uiflow-latest-20261105/round2/device/tools/run_tab5_round2.sh latest
# aggregate
PYTHONPATH=platform/tools:tests/uiflow2 <local>/<path> \
  .work/uiflow-latest-20261105/round2/device/tools/build_round2_results.py
```
