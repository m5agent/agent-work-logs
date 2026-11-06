# R3-U1 — full Unit battery on repaired runtime (service 8901)

- generated_at: `2026-11-06T15:50:12.025421+08:00`
- 执行身份：virtual-device validation（QEMU + Device Service 8901），非物理硬件。
- runtime: `<repo>/.work/issue-repair-20261105/runtime-clean/source/build/qemu-system-xtensa` sha256 `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`（RUNBOOK3 issue-repair runtime-clean）
- interpreter: <local>/<path> (3.13.15) + PYTHONPATH=.work/py:platform/tools:tests/uiflow2:tests/units (Lead correction: not venv 3.12 with .work/py)

## 覆盖与结果

- cases: **144**；catalog Unit 覆盖: **142/160**
- PASS: **128**；PASS-AFTER-RERUN: **0**；PARTIAL: **7**；FAIL: **7**；BLOCKED: **2**；NOT RUN(case): **0**
- runtime provenance VERIFIED: **119/144**（#185：实际执行二进制 sha256 == 27df1b40de946c69…）

| batch | cases | PASS | AFTER-RERUN | PARTIAL | FAIL | BLOCKED | NOT RUN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| batch10 | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| batch11 | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| batch12a | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| batch12b | 7 | 0 | 0 | 7 | 0 | 0 | 0 |
| batch12c | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| batch2 | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| batch2b | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| batch3 | 12 | 6 | 0 | 0 | 6 | 0 | 0 |
| batch4 | 12 | 12 | 0 | 0 | 0 | 0 | 0 |
| batch5 | 12 | 12 | 0 | 0 | 0 | 0 | 0 |
| batch6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| batch6b | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| batch7 | 8 | 8 | 0 | 0 | 0 | 0 | 0 |
| batch8 | 12 | 10 | 0 | 0 | 0 | 2 | 0 |
| can_lorawan | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| cclass | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| control | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| gpio | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| i2c | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| io | 12 | 11 | 0 | 0 | 1 | 0 | 0 |
| sensor | 7 | 7 | 0 | 0 | 0 | 0 | 0 |
| service | 3 | 3 | 0 | 0 | 0 | 0 | 0 |

## FAIL 清单

- `batch3/laser-rx` device `atoms3r` — infra — round2: None — `candidates/batch3_laser-rx.md`
- `batch3/scales` device `sticks3` — infra — round2: None — `candidates/batch3_scales.md`
- `batch3/co2` device `sticks3` — infra — round2: None — `candidates/batch3_co2.md`
- `io/buzzer` device `cores3` — unclassified — round2: None — `candidates/io_buzzer.md`
- `batch3/tube-pressure` device `atoms3r` — infra — round2: None — `candidates/batch3_tube-pressure.md`
- `batch3/extio` device `sticks3` — infra — round2: None — `candidates/batch3_extio.md`
- `batch3/env-iv` device `atoms3r` — infra — round2: None — `candidates/batch3_env-iv.md`

## PARTIAL（功能观测有证据但 runtime provenance 未验证）

- `batch12b/bmm350` — {'status': 'NOT VERIFIED', 'error': 'no live runtime was observed'}
- `batch12b/ina226-1a` — {'status': 'NOT VERIFIED', 'error': 'no live runtime was observed'}
- `batch12b/roller485-lite` — {'status': 'NOT VERIFIED', 'error': 'no live runtime was observed'}
- `batch12b/rollercan-lite` — {'status': 'NOT VERIFIED', 'error': 'no live runtime was observed'}
- `batch12b/ina226-10a` — {'status': 'NOT VERIFIED', 'error': 'no live runtime was observed'}
- `batch12b/roller485` — {'status': 'NOT VERIFIED', 'error': 'no live runtime was observed'}
- `batch12b/rollercan` — {'status': 'NOT VERIFIED', 'error': 'no live runtime was observed'}

## 未覆盖 catalog Unit / NOT RUN 原因

- `2relay`：无 batch runner；仅 relay2_preview_probe（离线预览 probe）
- `scroll`：无 batch runner；仅 scroll_protocol_probe
- `flashlight`：无 batch runner；仅 run_flashlight_route_probe
- `servo8-hat`：无 batch runner
- `8servos`：无 batch runner（12c 覆盖 8servos2-*）
- `joystick2`：无 batch runner（control 覆盖 joystick-v11）
- `nfc`：无 batch runner
- `ssr`：无 batch runner / 时间盒外
- `4relay`：无 batch runner / 时间盒外
- `mini-bps-v11`：DEFER（既有 blocker，项目登记 DEFER）
- `mini-pdm`：DEFER（同上）
- `glass`：无 batch runner / 时间盒外
- `rf433r`：无 batch runner / 时间盒外
- `audioplayer`：无 batch runner / 时间盒外
- `fingerprint2`：无 batch runner / 时间盒外
- `cardkb2`：无 batch runner / 时间盒外
- `8servos2-i2c`：无 batch runner / 时间盒外
- `mq`：无 batch runner / 时间盒外

## 时间盒内 NOT RUN 的 case（9）

原因：host load>8（其他 scope 并发）导致每 case ~35–70 s；75 min 时间盒内按 fastest-first 排序后仍未执行。计划清单见 tools/queue-*.txt。

- `batch11`: `audioplayer`, `fingerprint2`, `glass`, `rf433r`
- `batch12a`: `8servos2-i2c`, `cardkb2`, `mq`
- `gpio`: `ssr`
- `i2c`: `4relay`

- 本 scope 聚合时 host load average: [6.0, 8.34, 7.84]（RUNBOOK3 要求 load>8 记录）。

## 额外 NOT RUN 的 runner（本 scope 声明）

- `run_web_cases.py`：包装 io/control/sensor/service 的 browser-UI bridge lane（重复覆盖，node bridge 额外依赖），时间盒内未跑。
- `run_host_io_cases.py` / `run_host_control_cases.py` / `run_host_sensor_cases.py`：均要求 `--prepared-dir`（prepare_host_*.py 产物），本 scope 未生成该准备流水线。
- `run_host_cases.py`：已跑 button/relay/env-iii/boot-control（atoms3r）。

## 已修 issue 验证对照（本 scope 相关）

- **#185 executed-runtime provenance**：119/144 cases `runtime_provenance.status=VERIFIED`，observed sha256 == `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`，证据见每 case results.json。
- **#186 Angle/Light ADC**：见 io/angle、io/light case 的 checks/QOM（下方修复验证节）。
- **UNIT-HOST-17 buzzer**：io/buzzer 未打 patch（unpatched verdict）；`--buzzer-callback-arity-patch` 仅 documented diagnostic（如时间允许另跑并标注）。
- closed-loop 断言：batch runner 内 injected→guest-read / guest-write→host-observed checks 原样保留（未改断言）。

---

# 终判补充（Lead 时间盒收尾指令后，2026-11-06 15:52）

## 计数修正（以 results.json 为准）
- cases: **144**（planned 153；9 case NOT RUN 见上）
- **PASS 128**（其中 runtime provenance VERIFIED 116；control 5 + sensor 7 功能 PASS 但 provenance 未接线，见 gap 卡片）
- **PARTIAL 7**：batch12b（checks 全 true，但 `runtime_provenance=NOT VERIFIED: no live runtime was observed`）
- **FAIL 7** = 6 × `infra`（batch3 harness argv bug，redo 未跑，**不代表 Unit 结论**）+ 1 × `known-blocker`（io/buzzer = UNIT-HOST-17 未打 patch 判决）
- **BLOCKED 2**：batch8 `mini-can`、`lorawan-us915`（tracked runner EXPECTED_BLOCKED，known-blocker）
- catalog Unit 覆盖：**142/160**；未覆盖 18 = 9 个 NOT RUN case 对应 unit（glass, rf433r, fingerprint2, 8servos2-i2c, ssr, audioplayer, mq, cardkb2, 4relay）+ 9 个无 batch runner unit（2relay, scroll, flashlight, servo8-hat, 8servos, joystick2, nfc, mini-bps-v11[ DEFER ], mini-pdm[ DEFER ]）

## #185 executed-runtime provenance（修复验证）
- `runtime_provenance.status=VERIFIED`：**119/144** 行；其中所有 VERIFIED 行 observed sha256 == `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`（= issue-repair runtime-clean），且逐行记录 observed_pid/session/worker 世代。
- 未验证 25 行 = 无功能结论的 infra/blocked/partial 行（19 行为 runner 未接线 provenance：batch12b/control/sensor，已出 gap candidate）。
- 结论：**#185 修复在已接线 runner 上 PASS**；覆盖率缺口是 runner 未接线（新 candidate），不是 provenance 逻辑回归。

## #186 Angle/Light ADC 校准（明确判决）
- `io/angle` = **PASS**，checks：`unchanged_idf_curve_fitting_exact_uv_and_monotonic_voltage`、`selected_white_adc_ideal_12bit_transfer`、`adc_receipt_matches_admitted_application`、`official_driver_ready`、`nonblank_application_frame`、`evidence_before_stop` 全部 true。
- `io/light` = **PASS**，checks：`selected_white_adc_ideal_12bit_transfer`、`independent_yellow_digital_input`、`adc_receipt_matches_admitted_application`、`official_driver_ready`、`nonblank_application_frame`、`evidence_before_stop` 全部 true。
- 细节：`fix-verification.json`；原始证据 `.work/retest-20261106/units/io-angle/`、`io-light/`。
- 结论：**#186 PASS（Angle 单调电压/ADC 12bit 传输 + Light ADC 校准 + digital input 独立性均验证）**。

## UNIT-HOST-17 Buzzer
- 未打 patch 判决：**FAIL**（`natural Buzzer timer zero not observed before TIMER_DONE/manual output`），分类 `known-blocker`；卡片 `candidates/known_unit-host-17_buzzer_soft-timer.md`。
- `--buzzer-callback-arity-patch` 仅 documented diagnostic，本轮时间盒内未跑（不升级未打 patch 判决）。

## 环境
- runtime: `.work/issue-repair-20261105/runtime-clean/source/build/qemu-system-xtensa` sha256 `27df1b40…`；service 8901（token-less，max_sessions=2）。
- interpreter: `<local>/<path>`（3.13.15）+ `PYTHONPATH=.work/py:platform/tools:tests/uiflow2:tests/units`（按 Lead 修正；venv 3.12 + .work/py 会 circular-import，已弃用；首次误用运行的 158 行 ledger 归档在 `tools/_failed-interpreter-run/`）。
- 并发：2 guests；host load 运行中 6–11.6（>8 时记录，未降并发因服务/scope 上限即 2）。
- derived runners（atoms3r/sticks3 漂移布局）由当前 tracked 源重新生成，仅改 matrix 路径/ROOT/probe 目录；断言与 tracked 一致。
- closed-loop：batch runner 内置 injected→guest-read / guest-write→host-observed 断言原样保留、未放宽（`fix-verification.json.checks.closed_loop_assertions`）。
