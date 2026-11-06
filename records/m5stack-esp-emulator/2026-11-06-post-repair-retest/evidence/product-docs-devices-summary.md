# DOC4 — 产品文档设备/HAT/Module 页面审计（nuxt-m5-docs @ c06d36fcf，2026-11-06）

- 仓库：internal GitLab 121 `shaoxiang/nuxt-m5-docs`，只读本地检出 `<local>/<path>` @ `c06d36fcf45e30c99d89c19dca991a41b975e216`（master，2026-11-06 14:14 +0800）。
- 范围：36 个产品页（24 个 device 页 `static/{en,zh_CN}/core/*.md` + 12 个 HAT/Module 页 `static/en/{hat,module}/*.md`，EN 与 ZH 对照）。
- 核对源：`devices/<group>/<id>/device.json`（模拟器验证过的 hardware 规格）、`devices/catalog.json`、`platform/units/catalog.json`（HAT/Module 芯片/接口/地址）、UIFlow2 文档（gitlab 163 @ 509a67aa，只读 git show）、nuxt-m5-docs 同站 Unit 页面。
- 结论：**34/36 页 PASS（规格与记录一致）**，**2 页 FINDING → 2 candidates**（HAT ENV-III QMP6988 地址 0x56→0x70，三语同错）。无 FAIL；可执行示例 NOT RUN（见下）。

## 覆盖表

| # | 页面 | 对照记录 | 状态 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | en/core/CoreS3.md | cores3 | PASS |  |
| 2 | en/core/Core2.md | core2 | PASS |  |
| 3 | en/core/Basic_v2.7.md | basic-v27 | PASS |  |
| 4 | en/core/StickC.md | stickc | PASS |  |
| 5 | en/core/StickC-Plus.md | stickc-plus | PASS |  |
| 6 | en/core/StickC-Plus2.md | stickc-plus2 | PASS |  |
| 7 | en/core/StickC-Plus_SE.md | stickc-plus-se | PASS |  |
| 8 | en/core/AtomS3.md | atoms3 | PASS |  |
| 9 | en/core/AtomS3-Lite.md | atoms3-lite | PASS |  |
| 10 | en/core/AtomS3U.md | atoms3u | PASS |  |
| 11 | en/core/AtomS3R.md | atoms3r | PASS |  |
| 12 | en/core/AtomS3R-CAM.md | atoms3r-cam | PASS |  |
| 13 | en/core/AtomS3R-M12.md | atoms3r-m12 | PASS |  |
| 14 | en/core/Cardputer.md | cardputer(no sim record) | PASS |  |
| 15 | en/core/Cardputer-Adv.md | cardputer-adv | PASS |  |
| 16 | en/core/PaperColor.md | papercolor | PASS |  |
| 17 | en/core/PaperMono.md | papermono | PASS |  |
| 18 | en/core/StopWatch.md | stopwatch | PASS |  |
| 19 | en/core/StickS3.md | sticks3 | PASS |  |
| 20 | en/core/NanoC6.md | nanoc6 | PASS |  |
| 21 | en/core/Dial.md | dial | PASS |  |
| 22 | en/core/StackChan_Core.md | stackchan | PASS |  |
| 23 | en/core/StamPLC.md | stamplc | PASS |  |
| 24 | en/core/Tab5.md | tab5 | PASS |  |
| 25 | en/hat/Hat_ADC.md | adc-v11 | PASS |  |
| 26 | en/hat/Hat_DAC.md | dac | PASS |  |
| 27 | en/hat/Hat_ENV-III.md | env-iii | FINDING | QMP6988 address 0x56 should be 0x70 (candidate hat-env-iii-qmp6988-address) |
| 28 | en/hat/Hat_Joystick.md | joystick | PASS |  |
| 29 | en/hat/Hat_NCIR.md | ncir2 | PASS |  |
| 30 | en/hat/Hat_PIR.md | pir | PASS |  |
| 31 | en/hat/Hat_ToF.md | tof4m | PASS |  |
| 32 | en/hat/Hat_Thermal.md | thermal2 | PASS |  |
| 33 | en/module/Module_4Relay.md | cardputer(no sim record) | PASS |  |
| 34 | en/module/Module13.2_Dual_Kmeter.md | kmeter-iso-v11 | PASS |  |
| 35 | en/module/Module_GoPlus.md | goplus2 | PASS |  |
| 36 | en/module/Module13.2_2Relay.md | 2relay | PASS |  |

## FINDING / candidate

- `candidates/atomS3-arduino-quickstart-link.md` — AtomS3 页 Softwares→Arduino quick-start 链接指向 Atom Echo 教程（en:136 / zh_CN:138），ja 缺该入口；正确路由 `/en/arduino/m5atoms3/program` 存在且同页 banner 已使用。Target gitlab 121。
- `candidates/hat-env-iii-qmp6988-address.md` — HAT ENV-III（en:15/41, zh_CN:15/41, ja:15/41）QMP6988 I2C 地址 `0x56` 应为 `0x70`；证据：QMP6988 驱动默认地址 0x70（gitlab 163 固件 `driver/qmp6988.py:11`）、同站 Unit ENV III 对比表 0x70、模拟器 unit env-iii 0x44/0x70。Target gitlab 121。

## 已修/可变动的既有 issue 对照（供 Lead 更新）

- master `c06d36fcf` Correct IMU Axes：IMU 3-axis orientation diagrams/description corrected; CoreS3/AtomS3R pages touched — check whether these lines overlap #14 review scope before closing anything
- master `4bd3f32e2` fixed some bugs：bug-fix commit immediately before IMU axes; pages list not fully enumerated by scope
- master `e78de2a3f` clarify relay, DAC2, charger specifications (refs #5)：#5-related HAT/Module spec clarifications landed at master
- master `b00fe1f01` fix Hat SPK2 specifications and comparison (refs #4)：#4-related HAT SPK2 spec fix landed at master
- master `4882025ad` correct ADC ranges and product comparison specifications：#3-related HAT ADC range/comparison fix landed at master
- master `5bd709014` 修正 Basic IMU 标注及 SX1262 规格与射频开关例程：Basic v2.7 IMU labelling + Stamp LoRa-1262 spec/example fixes landed
- 说明：本审计基线（c06d36fcf）已晚于这些修复提交；审计中未再发现 #3/#4/#5 对应问题（HAT ADC 量程、Hat SPK2、relay/DAC2/charger 规格）。#14 覆盖的 CoreS3 页只记录到既有 ambiguity（净重 vs 套装重量），归入 #14，不新增 candidate。

## 跨仓库记录差异（非 121 文档问题，供模拟器维护方参考）

- NanoC6 SKU：docs=`static/en/core/NanoC6.md:3 `SKU:C125` (zh same; model PDF URLs C125-*)`；simulator=`devices/esp32-c6/nanoc6/device.json:4 `"sku": "C122"`; catalog.source.json:905 C122` → docs self-consistent and model-file URLs use C125 -> simulator record likely wrong; NOT a 121 candidate; report to simulator maintainers
- Dial product size：docs=`static/en/core/Dial.md:73 / zh_CN/core/Dial.md:73 `51.0 x 51.0 x 32.3mm` (EN+ZH agree)`；simulator=`devices/esp32-s3/dial/device.json hardware.dimensions_mm [45,45,32.3]` → EN/ZH agree and package size (71.9x71.9x57.4) is consistent with 51mm body -> simulator record likely wrong; NOT a 121 candidate
- AtomS3R-CAM product size：docs=`static/en/core/AtomS3R-CAM.md:22 (description) & :72 `24.0 x 24.0 x 13.5 mm`; zh same`；simulator=`devices/esp32-s3/atoms3r-cam/device.json dimensions_mm [24.0,24.0,14.0]` → docs internally consistent (EN+ZH+description); 0.5mm differs from simulator record -> unresolved cross-source, no 121 candidate without an authoritative measurement
- CoreS3 weight：docs=`static/en/core/CoreS3.md:89-90 Product Size labels whole set vs main unit, Product Weight 72.7g unlabeled`；simulator=`devices/esp32-s3/cores3/device.json weight_g 37.8 (main unit)` → CoreS3 page already under open #14 review; weight unit/scenario ambiguity belongs there -> Existing: #14 (no new candidate)

## NOT RUN

- 可执行只读示例（Device Service 8907）：时间盒内优先做静态规格交叉核对；唯一可执行的显示分辨率声明已由 2026-11-05/06 设备矩阵证据覆盖（cores3 320×240、stickc 80×160、atoms3 128×128 等），无新增文档结论依赖 guest 执行。**NOT RUN 原因：time-box / 优先级，classification=infra**。
- gitlab 121 open issues #1–#14 实时 API 读取：本机无内网 GitLab 读凭据（glab 仅 gitlab.com 且 401；API /projects/121 未授权返回 404）。查重基于 Lead 提供的映射（#14 CoreS3、#10 LLM630、#8 UIFlow1、#9 tutorial breakage）+ 本地历史审计记录 `.work/observatory-work-logs-20261106/records/nuxt-m5-docs/2026-11-02-documentation-audit/issues/`。**classification=infra**。

## 方法

- 程序化提取每页 `## Specifications` 表（EN/ZH），与 `device.json` 的 SoC/Flash/PSRAM/显示分辨率/屏幕对角线/尺寸/重量/SKU 对比；HAT/Module 页与 `platform/units/catalog.json` 的芯片/接口/地址对比；EN/ZH 同表数值对比。
- 自动信号（37 条）全部人工复核后仅保留 1 条真实不一致；其余为整机/套装尺寸重量口径差异、SKU 变体（如 Tab5 C145 vs C145/K145、Core2 K010 vs K010-V11）、显示驱动变体（ST7735S/ST7735SV）等，不构成文档错误。
- 脚本：`tools/spec_audit.py`（输出 `spec-audit.json`）；派生/证据均在 `.work/retest-20261106/product-devices/`。
- 规则：未修改 tracked 文件；未做 gh/glab 写；未触碰 8787/8830。
