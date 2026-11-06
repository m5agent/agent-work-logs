# DOC1 - UIFlow2 docs API stability test (internal GitLab project 163 @ 509a67aa)

- **Docs commit**: `509a67aadb66b16f6c0e684f87fed178982c4686` (`upstream/develop_m5things`, version.txt v2.5.4, 2026-10-30); read read-only via `git show`; 401 `docs/source/**.rst` files parsed.
- **Firmware**: cores3 v2.5.5 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded` (latest cache); **runtime**: repaired canonical QEMU `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e` on Device Service `<agent-service> (token-less)`.
- **Interpreter lane**: system python3.13 + PYTHONPATH=.work/py:platform/tools:tests/uiflow2 (RUNBOOK3 corrected §Python); API-only stability sessions via venv python3.12. Load-induced failures: none (`INFRA-LOAD` not used).
- **Validation lane**: virtual-device validation; physical hardware `NOT RUN`. No tracked edits, no gh/glab writes.
- **Coverage**: 101 documented Unit pages (1303 documented methods), 185 documented hardware/display/system members, 1105 doc code blocks extracted / 1101 compiled / 60 executed; 3 Unit-model live sessions (rgb range/setter, joystick2 invert/swap, ENV III documented units) each 2 waves; `results.json` cases = 110.

## Headline results

| surface | result |
| --- | --- |
| Unit API declarations | 77/101 pages fully match; 22 pages with findings; 2 pages manual-review |
| Unit method categories | name-typos 5, camelCase-vs-snake_case 2, private-method-exposed 4, factory-class 12, name-mismatch 15, firmware-drift 0 |
| Unit class names | 14 documented class names not directly importable from `unit` |
| Hardware/display/system declarations | 185 documented members, 3 not found on the documented target, 32 return probes, 15 setter/getter stability probes |
| Doc directive misuse | 24 method directives with an owner that is not a class on the page |
| Doc code blocks | 1105 extracted; 1101 compile; 4 invalid Python; 60 executed: 47 PASS, 13 fragment-context (undefined local symbols, not doc API defects) |

## Confirmed findings (Target: gitlab 163)

### 1. Unit page class names that the firmware `unit` package does not export (bug/docs-quality)

| unit page | documented class | actual export (guest fuzzy-present) | doc:line |
| --- | --- | --- | --- |
| `docs/source/unit/angle.rst` | `Angle` | `AngleUnit` | 41 |
| `docs/source/unit/earth.rst` | `Earth` | `EarthUnit` | 34 |
| `docs/source/unit/light.rst` | `Light` | `LightUnit` | 34 |
| `docs/source/unit/limit.rst` | `LimitUnit` | `LIMITUnit` | 34 |
| `docs/source/unit/pir.rst` | `PIR` | `PIRUnit` | 34 |
| `docs/source/unit/rgb.rst` | `RGB` | `RGBUnit` | 42 |
| `docs/source/unit/weight.rst` | `WEIGHTUnit` | `WeightUnit` | 34 |

`RGB` duplicates the already-reported candidate (issue #15-#26 set); the other names (Angle, Earth, Light, LimitUnit, PIR, WEIGHTUnit) are first reported here. `unit/<page>.rst` examples import the documented names (`from unit import *` + `RGB(...)`, `Angle(...)`), which raise `NameError` on the firmware.

### 2. Unit method name mismatches / typos

**spelling typos (documented vs actual)**

| unit | documented method (line) | suggested fix | prior report |
| --- | --- | --- | --- |
| `adc` | `operating_mode` (line 96) | `set_operating_mode` | adcunit_documented_setter_names |
| `adc` | `data_rate` (line 105) | `set_data_rate` | adcunit_documented_setter_names |
| `buzzer` | `deint` (line 93) | `deinit` | buzzerunit_deint_typo |
| `byteswitch` | `get_byte_switch_state` (line 48) | `get_byte_switch_status` | - |
| `vibrator` | `deint` (line 93) | `deinit` | - |

**camelCase docs vs snake_case implementation**

| unit | documented method (line) | suggested fix | prior report |
| --- | --- | --- | --- |
| `dac2` | `setVoltage` (line 68) | `set_voltage` | - |
| `dac2` | `setVoltageBoth` (line 81) | `set_voltage_both` | - |

**private (underscore) implementation method documented as public**

| unit | documented method (line) | suggested fix | prior report |
| --- | --- | --- | --- |
| `co2` | `check_crc` (line 251) | `_check_crc` | - |
| `co2` | `crc8` (line 257) | `_crc8` | - |
| `co2l` | `check_crc` (line 250) | `_check_crc` | - |
| `co2l` | `crc8` (line 256) | `_crc8` | - |

**documented method not present in firmware (and not in the pinned source)**

| unit | documented method (line) | suggested fix | prior report |
| --- | --- | --- | --- |
| `adc` | `gain` (line 114) | `None` | adcunit_documented_setter_names |
| `dac2` | `setDACOutputVoltageRange` (line 57) | `None` | - |
| `dualbutton` | `DualButtonUnit` (line 75) | `None` | - |
| `dualbutton` | `isHolding` (line 87) | `None` | - |
| `dualbutton` | `setCallback` (line 95) | `None` | - |
| `dualbutton` | `tick` (line 106) | `None` | - |
| `dualbutton` | `SimpleDualButtonUnit` (line 120) | `None` | - |
| `extio` | `init` (line 143) | `None` | - |
| `extio` | `value` (line 150) | `None` | - |
| `extio` | `on` (line 160) | `None` | - |
| `extio` | `off` (line 165) | `None` | - |
| `finger` | `get_user_characteristics` (line 213) | `None` | fingerunit_get_user_characteristics_plural |
| `ir` | `rx_event` (line 57) | `None` | - |
| `op90` | `count_value` (line 70) | `None` | - |
| `tmos` | `is_connected` (line 430) | `None` | - |

### 3. Factory-class conventions documented as normal classes

12 documented methods live on factory-produced subclasses (`CardKBUnit` / `ACSSRUnit` `__new__` factories). The CardKB case duplicates the prior issue; ACSSR is newly reported. Docs should state the `mode`/`bus` factory contract and instance class.

### 4. Documented code blocks that are not valid Python

| snippet | doc location | compile error |
| --- | --- | --- |
| S239 | `docs/source/hat/servo8.rst` line 20 | expected an indented block after 'for' statement on line 9 (servo8.rst:20>, line 10) |
| S330 | `docs/source/m5ui/chart.rst` line 106 | unterminated string literal (detected at line 3) (chart.rst:106>, line 3) |
| S1095 | `docs/source/unit/op180.rst` line 11 | expected an indented block after function definition on line 9 (op180.rst:11>, line 10) |
| S1096 | `docs/source/unit/op90.rst` line 11 | expected an indented block after function definition on line 11 (op90.rst:11>, line 12) |

No executed code block produced an `AttributeError`/`ImportError`/signature `TypeError` on a resolvable documented symbol; the remaining failures are fragment-context (`NameError: can` and similar, because the block assumes setup from a previous snippet) and are recorded as context-missing, not doc API defects.

### 5. Hardware / display / system findings

| finding | detail | status |
| --- | --- | --- |
| EPD setEpdMode numeric mapping | docs `0..3`, runtime enum `EPD_QUALITY=1 .. EPD_FASTEST=4` | **duplicate** of prior reported issue (supplement evidence) |
| documented member not found | `docs/source/hardware/uart.rst`: `UART.IRQ_TXIDLE`(line 424) | see note |
| documented member not found | `docs/source/system/power.rst`: `PORT.HAT`(line 281), `PORT.ALL`(line 286) | see note |


Authoritative v4 guest run: **182/185 documented members resolve**; the three missing are `UART.IRQ_TXIDLE` (docs/source/hardware/uart.rst line 424), `PORT.HAT` (docs/source/system/power.rst line 281), `PORT.ALL` (docs/source/system/power.rst line 286). `UART.IRQ_TXIDLE` is absent from `machine.UART` (`IRQ_RXIDLE/IRQ_RX/IRQ_BREAK` present); `PORT.HAT`/`PORT.ALL` are absent from `M5.Power.PORT` (A/B1/B2/C1/C2/USB present). Documentation surfaces `IMU_TYPE`, `Callback_Type`, `PORT` are reachable as `M5.Imu.IMU_TYPE`, `BtnPWR.CB_TYPE`, `M5.Power.PORT` (a dedicated 2-round probe confirmed all five documented Callback_Type event names exist on the latest firmware).

Probe-iteration note (honesty/`infra`): the first hardware probe versions produced false negatives because `machine`/`time` were not imported in the probe preamble and class constants were resolved through the wrong alias; those iterations are retained in evidence (`hw-apis`, `hw-apis-v2`, `hw-apis-v3` FAILED due to a probe-code `NameError`) and the v4 run is the one used for verdicts.

### 6. Documented ranges / setter-getter stability (live sessions)

| check | documented | observed | verdict |
| --- | --- | --- | --- |
| `Display.setRotation`/`getRotation` pair 0..3 | rotation round-trip | r0/r1/r2/r3 round-trip identical, dims 320x240 / 240x320 alternate | PASS |
| `Display.setRotation(4)` (outside 0..3) | range 0-3 | accepted, `getRotation()`=4, dims stay 320x240, restoring 0 works | undocumented acceptance (minor) |
| `Speaker.setVolume`/`getVolume` | 0-255 | 64->64, 255->255, 0->0 | PASS |
| `Speaker.setVolume(300)` | accepts 0-255 | silently wraps to 44 (300 & 0xFF); docs silent on out-of-range | docs-quality note |
| `Speaker.setVolumePercentage/getVolumePercentage` | ratio 0.0-1.0, clamped | 25.0/50.0 clamp to 1.0 (docs-compliant) | PASS |
| `time.timezone()` no-arg | returns timezone string | returns None before any set; string after set | minor docs/runtime mismatch |
| `rgb.set_brightness(100)` + `fill_color(0xFF0000)` (model attached) | range 0-100 | QOM `led-rgb=[16711680,..]` (0xFF0000), `led-frames=2` | PASS closed loop |
| `rgb.set_brightness(0)` + out-of-range 150 | range 0-100 | brightness 0 -> QOM black; 150 accepted without error | range not enforced (minor) |
| `joystick2.set_axis_x_invert(True)` / `set_axis_swap(True)` | documented setter semantics | guest position sign flips / x-y swap, QOM inputs intact | PASS |
| `ENVUnit(type=3)` documented units | `read_temperature` °C, `read_humidity` %RH, `read_pressure` hPa | injected 25.0 °C / 50.0 %RH / 101325 Pa -> guest reads 25.00 / 50.00 / 1013.25; second wave 17.3 / 31.5 / 100000 Pa -> 17.30 / 31.50 / 1000.00 | PASS |

## Prior-issue dedupe


Prior candidates filed as internal GitLab project 163 issues #15-#26 (mapping in `results.json.prior_issue_dedupe`). Duplicates found in this run: `adcunit_documented_setter_names`, `buzzerunit_deint_typo`, `cardkbunit_factory_mode_undocumented`, `epd_setepdmode_numeric_mapping`, `fingerunit_get_user_characteristics_plural`. Older open issues #6-#14 titles are not present in the workspace; no new finding matches them by slug.

## NOT RUN

- **hat/module/chain/cap documented helper APIs on guest**: not loaded by the default CoreS3 firmware; unit-scope declarations are covered, other packages are DOC3/DOC4 scope
- **data-plane semantics of documented Unit APIs (return values/ranges)**: declaration existence is asserted here; data-plane closed loops are U1/DOC3 scope. Only rgb + joystick2 setter semantics were exercised live on 8903 for documented range/setter claims.
- **roller485 / rollercan full method surface**: pinned source resolution for these pages is incomplete (documented API spans a driver/register layer); marked MANUAL-REVIEW instead of confirmed mismatch

## Candidate issue drafts (Lead to file; Target gitlab 163)

- `doc_code_blocks_invalid.md` - 4 official UIFlow2 doc code blocks are not valid Python (docs CI gap) (docs-quality)
- `hardware_member_gaps.md` - Hardware/system docs: 3 documented enum members missing; minor range/return accuracy gaps (EPD duplicate) (docs-quality)
- `unit_class_names.md` - Unit docs document class names that the firmware `unit` package does not export (9 pages + RGB duplicate) (docs-quality)
- `unit_factory_private_directive.md` - Unit docs: factory-class contracts, private helpers exposed as public, and misused method directives (docs-quality)
- `unit_method_names.md` - Unit docs method names: typos, camelCase/snake_case mismatches and non-existent methods (firmware + pinned source cross-check) (bug)

## Evidence
```
.work/retest-20261106/docs-api/
  docs-index.json          # 401 docs files: path + sha256
  units.json               # 101 unit pages with documented classes/methods/constants/ranges
  hw-api-pages.json        # 85 hardware/system/base/chain pages API directives
  snippets.json            # 1105 official doc code blocks (id/path/line/sha256/risk flags)
  snippet-compile.json     # host compile results + 60 selected for guest execution
  unit-source-map.json     # docs class -> unit export -> pinned v2.5.4 source methods
  probe*-*.json            # generated probe metadata (in probes/)
  evidence/unit-breadth-v2 # guest: 101 unit pages / 1303 documented methods
  evidence/hw-apis-v4      # guest: 185 documented hardware/system members + stability probes
  evidence/snippets-1|2    # guest: 60 official doc code blocks executed
  evidence/stability-rgb|joystick2|env # Unit-model closed loops on 8903
  results.json             # machine-readable cases/findings
  candidates/*.md          # target gitlab 163 issue drafts (Lead to file)
  summary.md               # this file
```
