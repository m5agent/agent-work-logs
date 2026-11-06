# R3-DOC2 — UIFlow2 文档 ergonomics / 首次调用成功率审计

日期：2026-11-06。Scope：DOC2 docs-uiflow-ergonomics。Owner：epd-verifier（task-19）。
目标仓库：internal GitLab 163 `m5stack-uiflow-2.0-project-group/uiflow_micropython`，文档 commit **`509a67aadb66b16f6c0e684f87fed178982c4686`**（v2.5.4, 2026-10-30），只读 `git archive` 快照；未修改任何 tracked 文件，未写 gh/glab，未使用 8787/8830。

## 1. 结论摘要

- 共评分 **84 页**（45 unit 页跨传感器/IO/电机/通信/显示/音频 + 19 hardware 页 + m5ui/widgets/get-started/advanced/system 页），其中 23 页人工全文审阅，其余为静态指标启发式（summary 表内 `manual=Y/h` 标注）。
- 文档整体结构（签名区 / Constructors / Methods / UIFLOW2+MicroPython 示例 / 支持表）在多数 unit 页一致，传感器类 unit 页（如 env、sht30）质量最高；`system/power.rst` 是带类型签名+返回+范围+M5.begin 前置的最佳样例。
- 主要 ergonomics 问题：`hardware/display.rst` 参数默认值标注不可靠（140 处 "(default"，fillRect 省略 w/h 即 TypeError）、常用方法（drawString/textWidth/fontHeight/getEpdMode）无方法小节、示例对象名混用；`hardware/adc.rst` 缺 import 路径且 atten 未标可选；1 个新增不可编译代码块（m5espnow）；1 个悬空 literalinclude（unit/extio）；m5ui/index 示例缺 M5.begin 前置；unit/can 无方法文档。
- 首次调用实验（10 个常用 API，仅凭文档书写，Device Service 8909 真实固件执行）：**9/10 首轮成功**；ADC 首轮因文档未给 import 路径 NameError，第 2 轮（换 import）通过。另有 2 项“文档声明 vs 行为”不一致（display 参数默认值；ADC atten 可选性/导入路径）。
- 产出 **8 张 candidates**（Target gitlab 163），其中 3 张标注为既有 issue 的追加证据（#9/#17/#15），5 张无重复可新提。

## 2. 执行身份

| 项 | 值 |
| --- | --- |
| 文档 commit | `509a67aadb66b16f6c0e684f87fed178982c4686`（内部 GitLab 163 `upstream/develop_m5things`） |
| 文档快照 | `evidence/docs/source`（779 文件，`git archive` 只读导出） |
| 设备/固件 | CoreS3，UIFlow2.0 CoreS3 **v2.5.5**，base sha256 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded` |
| native runtime | `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`（runbook 指定修复后 runtime） |
| guest 会话 | run1 `65cbf514c95b4ca6b7663661354c75d0`（composed fw `980cb24b…`）；run2 `7076e3e385754d12806817e1fa99a8db`（`69a4f532…`）；run3 `6f0d2c2a6f204f78a867a0ce3a89228d`（`05a5cc09…`），均 `purge=0`、normal-QMP stopped、cleanup complete |
| 服务 | Device Service `<agent-service>`，token `.work/retest-20261106/svc-8909.token`（可见 session） |
| 并发 | guest 串行 1 个（runbook 允许 ≤2；本轮未观察 load 异常） |

## 3. 首次调用成功率实验结果（仅凭文档书写）

方法：按文档页书写 10 个常用 API（页面 prose + 页面 literalinclude 渲染的示例），每个 API 独立 try/except 标记，一次 guest 程序记录首轮结果；失败项在后续 attempt 中只做“按文档修正”并记录次数与原因。所有 guest 证据在 `evidence/guest/{attempt1,attempt2,attempt3}.py` 与 `run{1,2,3}/serial.txt`；结构化结果见 `evidence/guest/first-call.json` 与 `results.json.first_call_experiment`。

| # | API（文档位置） | 首轮结果 | 需要的修正/尝试 | 失败分类 |
| --- | --- | --- | --- | --- |
| 1 | `M5.Lcd.fillRect(x,y,w,h,color)`（hardware/display.rst:730-748） | PASS | 1 | —（但文档声称的 w/h 默认值错误，见 candidate 01；`fillRect(20,20)` TypeError 'w' argument required） |
| 2 | `M5.Lcd.setRotation(r)`/`getRotation()`（display.rst:281-361） | PASS | 1 | —（rotation 维度表实测与文档一致：0/2→320×240，1/3→240×320） |
| 3 | `M5.Lcd.drawString(text,x,y)`（display.rst:21,55,220 引用） | PASS | 1 | 文档缺方法小节（candidate 02） |
| 4 | `hardware.Pin` + `.value()/.on()/.off()`（hardware/pin.rst:29-80） | PASS | 1 | —（value 返回值语义偏薄，minor） |
| 5 | `ADC(pin, *, atten)` + `read()`（hardware/adc.rst:35-66） | **FAIL NameError: ADC isn't defined** | 2（run1 失败→run3 改 import 通过；hardware/machine 两个命名空间均可用，`ADC(Pin(6))` 可省略 atten） | **文档缺信息**（API 区未给 import 路径；atten 未标可选）→ candidate 03 |
| 6 | `hardware.I2C(id, *, scl, sda, freq)` + `scan()`（hardware/i2c.rst:36-63） | PASS | 1 | —（返回 list 与文档一致） |
| 7 | `M5.BtnA.wasPressed()`（hardware/button.rst:138-145） | PASS | 1 | 支持表图例歧义（candidate 08，追加 #15） |
| 8 | `M5.Power.getBatteryLevel()`（system/power.rst:157-163） | PASS（返回 87，0-100 范围符合） | 1 | — |
| 9 | `M5.Widgets.Label(...)`（widgets/label.rst:30-43） | PASS | 1 | bg_c 默认值 prose 与签名不一致（minor，并入 candidate 02/08 附近的说明） |
| 10 | `m5ui.init()` + `m5ui.M5Label(...)`（m5ui/index.rst:9,135-143） | PASS（脚本先调 M5.begin()） | 1 | m5ui/index 示例缺 `import M5`/`M5.begin()` → candidate 07 |

额外 doc-claim 检查（非 10 API 计数）：裸 `Display.` 在固件可用（`from M5 import *` 导出，run2 A）；`M5.Lcd is M5.Display` 为 True（run2 G）；`display.rst` 的 `display.drawRect` 唯一小写示例未验证是否可运行（文档一致性候选 02 按文件证据记录）。

**未归因项（BLOCKED）**：run3 组合调用 `read()/read_u16()/read_uv()` 时抛 `OSError [Errno 95] EOPNOTSUPP: ESP_ERR_NOT_SUPPORTED`，时间盒内未隔离到具体方法，可能是 QEMU ADC 校准/eFuse 支持问题而非文档缺陷；**不作为 docs candidate**，需真机或隔离实验后再定。

## 4. 页面评分表（84 页；评分规则见 results.json.scoring）

评分：S1 签名、S2 参数/默认值/枚举、S3 返回值、S4 单位/范围/枚举、S5 初始化顺序/依赖、S6 示例可运行性、S7 错误/失败提示、S8 命名/一致性；每项 0–2，合计 /16 折百分比。`manual=Y` 为全文人工审阅（23 页），`h` 为静态指标启发式。

| docs page | lines | classes/methods | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | score | manual |
| --- | ---: | ---: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | ---: | :--: |
| `hardware/sht30.rst` | 58 | 0/2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 94% | Y |
| `unit/env.rst` | 97 | 1/3 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 94% | Y |
| `hardware/uart.rst` | 427 | 1/22 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 88% | Y |
| `system/power.rst` | 288 | 0/26 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 88% | Y |
| `hardware/i2c.rst` | 81 | 1/3 | 2 | 2 | 2 | 1 | 1 | 2 | 0 | 2 | 75% | Y |
| `hardware/touch.rst` | 196 | 1/5 | 2 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 75% | Y |
| `base/pwm.rst` | 55 | 0/1 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 69% | Y |
| `hardware/adc.rst` | 117 | 1/5 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 69% | Y |
| `hardware/pin.rst` | 110 | 1/7 | 2 | 2 | 1 | 1 | 1 | 2 | 0 | 2 | 69% | Y |
| `system/time.rst` | 341 | 1/13 | 2 | 0 | 1 | 2 | 2 | 0 | 2 | 2 | 69% | h |
| `unit/joystick2.rst` | 290 | 1/19 | 2 | 1 | 1 | 2 | 1 | 2 | 0 | 2 | 69% | h |
| `unit/mqtt.rst` | 282 | 1/16 | 2 | 1 | 1 | 1 | 2 | 2 | 0 | 2 | 69% | h |
| `unit/nbiot.rst` | 401 | 0/9 | 2 | 2 | 2 | 1 | 1 | 1 | 0 | 2 | 69% | Y |
| `advanced/image.rst` | 502 | 2/25 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 62% | Y |
| `hardware/button.rst` | 213 | 0/16 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 62% | Y |
| `hardware/imu.rst` | 121 | 0/4 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 62% | Y |
| `hardware/speaker.rst` | 355 | 0/19 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 62% | Y |
| `m5ui/button.rst` | 417 | 0/17 | 1 | 2 | 2 | 1 | 0 | 2 | 0 | 2 | 62% | h |
| `m5ui/msgbox.rst` | 463 | 0/22 | 1 | 2 | 2 | 1 | 0 | 2 | 0 | 2 | 62% | h |
| `m5ui/page.rst` | 208 | 0/7 | 1 | 2 | 2 | 1 | 0 | 2 | 0 | 2 | 62% | h |
| `unit/cardkb.rst` | 118 | 1/5 | 2 | 0 | 2 | 1 | 1 | 2 | 0 | 2 | 62% | h |
| `unit/dualbutton.rst` | 177 | 1/10 | 2 | 1 | 2 | 1 | 2 | 0 | 0 | 2 | 62% | h |
| `unit/buzzer.rst` | 99 | 1/5 | 2 | 1 | 0 | 2 | 2 | 0 | 0 | 2 | 56% | h |
| `unit/earth.rst` | 91 | 1/5 | 2 | 0 | 2 | 2 | 1 | 0 | 0 | 2 | 56% | h |
| `unit/lora_e220.rst` | 315 | 1/15 | 2 | 0 | 0 | 1 | 2 | 2 | 0 | 2 | 56% | h |
| `unit/neco.rst` | 143 | 1/9 | 2 | 2 | 0 | 2 | 1 | 0 | 0 | 2 | 56% | h |
| `unit/scales.rst` | 180 | 1/13 | 2 | 1 | 1 | 2 | 1 | 0 | 0 | 2 | 56% | h |
| `unit/synth.rst` | 323 | 1/23 | 2 | 2 | 0 | 2 | 1 | 0 | 0 | 2 | 56% | h |
| `unit/thermal.rst` | 160 | 1/4 | 2 | 1 | 2 | 1 | 1 | 0 | 0 | 2 | 56% | h |
| `unit/vibrator.rst` | 99 | 1/5 | 2 | 1 | 0 | 2 | 2 | 0 | 0 | 2 | 56% | h |
| `widgets/label.rst` | 102 | 1/6 | 2 | 2 | 0 | 1 | 1 | 2 | 0 | 1 | 56% | Y |
| `advanced/jpg.rst` | 69 | 1/2 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 2 | 50% | h |
| `hardware/display.rst` | 1212 | 2/43 | 2 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 50% | Y |
| `system/wlan.sta.rst` | 199 | 1/8 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 50% | Y |
| `unit/encoder.rst` | 127 | 1/8 | 2 | 1 | 0 | 2 | 1 | 0 | 0 | 2 | 50% | h |
| `unit/extio2.rst` | 191 | 1/14 | 2 | 2 | 0 | 1 | 1 | 0 | 0 | 2 | 50% | h |
| `unit/light.rst` | 73 | 1/3 | 2 | 0 | 2 | 1 | 1 | 0 | 0 | 2 | 50% | h |
| `unit/reflective_ir.rst` | 101 | 1/6 | 2 | 0 | 1 | 2 | 1 | 0 | 0 | 2 | 50% | h |
| `unit/relay4.rst` | 141 | 1/7 | 2 | 2 | 1 | 0 | 1 | 0 | 0 | 2 | 50% | h |
| `unit/rgb.rst` | 82 | 1/3 | 2 | 0 | 0 | 1 | 1 | 2 | 0 | 2 | 50% | h |
| `unit/tof.rst` | 165 | 1/11 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 50% | Y |
| `m5ui/chart.rst` | 573 | 0/28 | 1 | 2 | 2 | 0 | 0 | 0 | 0 | 2 | 44% | h |
| `unit/co2.rst` | 264 | 1/28 | 2 | 0 | 0 | 1 | 2 | 0 | 0 | 2 | 44% | h |
| `unit/dlight.rst` | 66 | 1/2 | 2 | 0 | 0 | 2 | 1 | 0 | 0 | 2 | 44% | h |
| `unit/extio.rst` | 168 | 2/11 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 44% | Y |
| `unit/joystick.rst` | 122 | 1/7 | 2 | 0 | 2 | 0 | 1 | 0 | 0 | 2 | 44% | h |
| `unit/key.rst` | 216 | 1/19 | 2 | 0 | 1 | 0 | 2 | 0 | 0 | 2 | 44% | h |
| `unit/timerpwr.rst` | 382 | 1/59 | 2 | 0 | 0 | 1 | 2 | 0 | 0 | 2 | 44% | h |
| `unit/tvoc.rst` | 176 | 1/19 | 2 | 0 | 0 | 1 | 2 | 0 | 0 | 2 | 44% | h |
| `widgets/circle.rst` | 81 | 1/4 | 2 | 2 | 0 | 1 | 0 | 0 | 0 | 2 | 44% | h |
| `hardware/rotary.rst` | 106 | 1/5 | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | 38% | h |
| `hardware/wdt.rst` | 53 | 1/1 | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | 38% | Y |
| `m5ui/label.rst` | 335 | 0/14 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 1 | 38% | Y |
| `system/wlan.ap.rst` | 170 | 1/6 | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | 38% | h |
| `unit/extencoder.rst` | 198 | 1/16 | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | 38% | h |
| `unit/fader.rst` | 110 | 0/8 | 1 | 0 | 1 | 0 | 2 | 0 | 0 | 2 | 38% | h |
| `widgets/image.rst` | 71 | 1/3 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 38% | h |
| `unit/button.rst` | 85 | 1/4 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 2 | 31% | h |
| `unit/envpro.rst` | 143 | 1/12 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 2 | 31% | h |
| `unit/ir.rst` | 63 | 1/2 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 2 | 31% | h |
| `unit/op90.rst` | 85 | 1/2 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 2 | 31% | h |
| `unit/relay.rst` | 82 | 1/4 | 2 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 31% | Y |
| `unit/weight.rst` | 105 | 1/6 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 2 | 31% | h |
| `advanced/dl.rst` | 314 | 1/17 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 25% | h |
| `unit/can.rst` | 147 | 2/0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 25% | Y |
| `system/audio.rst` | 55 | 1/0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/asr.rst` | 58 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/audioplayer.rst` | 59 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/bldc_driver.rst` | 57 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/cardkb2.rst` | 129 | 0/5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/encoder_motor_driver.rst` | 85 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/hbridge.rst` | 64 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/ina226.rst` | 65 | 0/2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/lcd.rst` | 70 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/oled.rst` | 63 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/rca.rst` | 63 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/relay2.rst` | 59 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/rf433r.rst` | 62 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/rf433t.rst` | 61 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/servo180.rst` | 51 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/servo360.rst` | 51 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/servos8.rst` | 95 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/servos8_v2.rst` | 90 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |
| `unit/step16.rst` | 59 | 0/1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 19% | h |

## 5. 静态审计结果

- **代码块可编译性**：docs 快照 `docs/source/**` 共 1113 个 Python 代码块，`compile()` 失败 **5** 个：`hat/servo8.rst:32`、`m5ui/chart.rst:111`、`unit/op180.rst:23`、`unit/op90.rst:25`（4 个已在 open #9 的清单内）以及 **`system/m5espnow.rst:40`（新增，不在 #9 清单）**。见 `evidence/compile-audit.json`、candidate 04。
- **literalinclude 目标存在性**：437 个 `literalinclude` 中仅 1 个悬空：`unit/extio.rst:13` → `examples/unit/extio/extio_core2_example.py` 不存在。见 candidate 05。
- **autoclass 覆盖**：146 个 `autoclass` 全部带 `:members:`，未发现“只列类不列成员”的生成错误。
- **casing 一致性**：静态扫描未发现文档方法名大小写与示例调用的大小写冲突（`casing_issues` 全为 0）；但 display 页存在 `display.`/`Display.`/`M5.Lcd.` 三种写法（candidate 02）。
- **支持表**：button/imu/speaker/mic/display 等页存在与固件对象存在性/StopWatch 行相关的问题（#15 已开；本轮 button CoreS3 行补充证据见 candidate 08）。

## 6. Candidates（Target gitlab 163，8 张）

| 卡片 | 标题 | 严重度 | Existing 去重 |
| --- | --- | --- | --- |
| `candidates/c01_display_param_defaults.md` | display.rst 图元参数统一标 "(default -1/0)"，fillRect 缺 w/h 即 TypeError | docs-quality | 新（非 #9/#7） |
| `candidates/c02_display_method_inventory.md` | display.rst 引用 drawString/textWidth/fontHeight 无方法小节；getEpdMode 缺失；示例对象名混用 | docs-quality | 相关 #16（EPD 数值），本条不同；非 #9 |
| `candidates/c03_adc_import_atten.md` | adc.rst 未说明 import 路径，atten 未标可选 | docs-quality | 新 |
| `candidates/c04_m5espnow_syntax.md` | m5espnow.rst:40 `while True::` 不可编译（#9 清单外新增） | docs-quality | **#9 追加证据** |
| `candidates/c05_extio_dangling_literalinclude.md` | unit/extio.rst literalinclude 目标不存在（全仓唯一） | docs-quality | 新 |
| `candidates/c06_can_missing_methods.md` | unit/can.rst 双签名矛盾且无方法文档 | docs-quality | **#17 追加证据** |
| `candidates/c07_m5ui_index_example_preamble.md` | m5ui/index 示例缺 import M5/M5.begin，正文“只需要 m5ui.init()” | docs-quality | 相关 #11，非重复 |
| `candidates/c08_button_table_legend.md` | button 支持表缺图例；CoreS3 行只标 BtnPWR 但 Btn* 对象均存在 | minor | **#15 追加证据** |

既有 open #6–#26 共 21 条已逐条读取（`evidence/open-issues-163.json`），本轮未重复提报：#16（EPD 0–3 vs 1–4）在 commit 509a67aa **仍未修复**（display.rst:381-401 仍为 0–3），本轮把 getEpdMode 缺失并入 c02 而非另开；#17–#26 的文档问题仍 open，c06 只补“无方法文档”证据。未创建 issue、未写 issue 评论（按 runbook Lead 统一提报）。

## 7. NOT RUN / 边界

- 未与真机/物理硬件对比：所有 guest 结果为 QEMU `virtual-device validation`，`hardware_validation: NOT RUN`。
- 首调用实验只覆盖 CoreS3 的 10 个内建 API + 少量 doc-claim；unit 页（40+）只做文档静态/人工审阅，**未**逐个接 Unit 到 guest 运行（8909 未挂 Unit；Unit 行为属 DOC1/U1 scope）。
- `ADC.read_u16/read_uv` 的 EOPNOTSUPP 未隔离归因（BLOCKED），不写入文档断言。
- 未测产品文档（nuxt-m5-docs，属 DOC3/DOC4）、未验证 #172–#187 修复（属 D1/D2/P1/U1 scope）。
- 未跑完整 docs 构建（sphinx）；代码块审计为 `compile()` 静态检查，literalinclude 为存在性检查。
- 文档快照来自 `git archive`（不含 submodule/图片），图片资源存在性未审。
- 时间盒 ~70 分钟；本轮 guest 串行 3 次（每次 ~1.5–2 分钟），未触发 load 保护。

## 8. 产物

- `results.json`：84 页评分 + first-call 实验记录 + 静态审计 + candidates 索引。
- `summary.md`：本文件。
- `candidates/*.md`：8 张卡片。
- `evidence/static-analysis.json`、`evidence/compile-audit.json`、`evidence/guest/first-call.json`、`evidence/guest/run{1,2,3}/`、`evidence/open-issues-163.json`、`evidence/docs/source/`。
- 脚本：`scripts/analyze_docs.py`、`scripts/build_results.py`、`evidence/guest/attempt{1,2,3}.py`。
