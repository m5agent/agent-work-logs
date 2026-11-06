# 修复后复测：模拟器全链路 + UIFlow2 文档 + 产品文档（issue 驱动）

- 日期：`2026-11-06`（Asia/Shanghai）
- 结果：`PARTIAL`（修复验收基本达成，但 #178 classic 烧录仍不稳定、#188 tab5 未解；文档/产品文档新增 19 个问题 issue）
- 工作类型：`report`
- 来源：用户要求“除了 tab5 其他都修好了，现在再次全面测试：UIFlow2 文档、模拟器测试，有问题提 issue；新增产品文档测试；UIFlow2 文档不只要测接口稳定性，还要看文档是否合理、是否迫使反复试错（uiflow-coder skill 本质就是这些文档）”
- 源码版本：[m5stack-esp-emulator @ dd2eb35d](https://github.com/m5agent/m5stack-esp-emulator/tree/dd2eb35d)
- 环境：macOS arm64；修复后 native runtime `27df1b40…` + C6 `25497c52…`；7 个隔离 Device Service；最新官方 UIFlow2 固件（30 台，重新 fetch 校验）；UIFlow2 文档 `509a67aa`；产品文档 `c06d36fc`

## 结论

1. **模拟器修复验收**：#172/#173/#174/#175/#176/#177/#179/#180/#181/#182/#183/#184/#187 全部 **VERIFIED**（fresh run，绑定固件/runtime/session）；**#178 未真正修好**——classic LX6 stock-stub 冷烧录仍间歇失败（39 次尝试 23 次失败：13× checksum 0107、10× serial stream stopped，所有设备最终可重试通过），已重新打开 #178 并附证据；**#188 tab5 仍 OPEN**（未追修，记录状态）。
2. **全设备执行**：30/30 UIFlow2 设备均有修复后执行证据；Device Service 冷启动 29/30（19 PASS + 10 PASS-flaky），tab5 NOT RUN；tracked device matrix 33 设备 primary 20 PASS/12 FAIL/1 EXCLUDED，重试+host-image 诊断后 30 PASS、2 NOT RUN（缺 pinned artifact）、1 EXCLUDED（cardputer-zero 为 Linux 后端）。
3. **全外设矩阵**：68/68 case 执行，主观察 66 PASS / 2 FAIL；core2-axp192 retry 恢复（INFRA-LOAD），stackchan-peripherals 3/3 固定 3s settle 超时但 `--wait 10` 帧与修复阶段 PASS 帧逐字节一致 → fixture 时序问题（新 issue #192），不是模型回归。
4. **全 Unit**：144/153 case 执行，128 PASS（116 provenance VERIFIED）、7 PARTIAL（batch12b provenance 未接线）、7 FAIL（6 为 agent harness argv 错误/infra + 1 known-blocker buzzer）、2 BLOCKED（tracked EXPECTED_BLOCKED）；catalog 覆盖 142/160；#186 Angle/Light ADC **VERIFIED**；#185 覆盖不全 → 新 issue #193。
5. **UIFlow2 文档**：API 稳定性 + 文档合理性双线审计。101 Unit 页/1303 文档方法、185 hardware/display/system 成员、1105 代码块（1101 可编译、60 执行）对账；新增 9 个 UIFlow2 文档 issue（#27–#35），并对既有 #9/#15/#17 追加证据。关键改进项：图元参数 "(default -1)" 误导（fillRect 2 参数直接 TypeError）、display 缺 drawString/textWidth/fontHeight/getEpdMode 文档、ADC 缺 import 路径、9 页类名不可导入、若干方法名拼写/case/不存在、3 个 hardware 枚举成员文档存在但固件缺失、1 个悬空 literalinclude、m5ui 示例缺 M5.begin、CAN 页无方法文档等。
6. **产品文档（新 scope）**：产品文档 Unit 页 32 units/64 页 + 设备/HAT/Module 36 页审计；新增 5 个产品文档 issue（121 #15–#19）和 2 个模拟器数据 issue（GitHub #190 设备档案元数据、#191 Unit catalog 数据）；另确认 master 已修复 #3/#4/#5 等历史文档问题。
7. **并行编排**：8 个 scope（boot / device matrix / peripheral / unit / docs-api / docs-ergonomics / product-units / product-devices）同时执行；长尾仅 Unit（144 case）在 75 分钟时间盒后主动收口，其余 scopes 全部完成；负载 8–14 时统一 1–2 并发并记录 load。

## 修复验收矩阵

| issue | 状态 | 证据 |
| --- | --- | --- |
| #172 eFuse 5/6 admission | VERIFIED | device matrix 5/6 classic 设备 PASS |
| #173 console fixtures | VERIFIED | 4 台 fixture 无需 make_image.py 即可组合/执行 |
| #174 VFS 布局 | VERIFIED | `layout_drift=true` 组合 + 按实际偏移 PASS |
| #175 ED2208 partial window | VERIFIED | 7 个 PaperColor 外设 case PASS，EPD 帧正确 |
| #176 AXP2101 charger | VERIFIED | cores3-power-transitions `87 4000 1 → 64 3600 0 → 93 4200 1 + DONE PASS` |
| #177 SHA-bound expectations | VERIFIED | StickS3 轴向 / PaperColor charging 仅按精确固件 sha 选择 |
| #178 classic ESP32 flash | **NOT ROBUST → reopened** | 39 次冷烧录 23 失败；matrix primary 10/11 classic 失败，重试/镜像 lane 可过 |
| #179 AtomS3 panel variant | VERIFIED | atoms3/atoms3r/cam/m12 PASS |
| #180 PaperColor UART0 | VERIFIED | 2/2 cold boot PASS + UART0 markers |
| #181 Dial UART0 | VERIFIED | 2/2 cold boot PASS + UART0 markers |
| #182 NanoC6 startup | VERIFIED | 2/2 cold boot PASS + UART0 markers |
| #183 Basic BtnB fence | VERIFIED | host-image lane `BASIC27_BUTTON_STATE 0 1 0` + FRAME_READY |
| #184 StickC frame fixtures | VERIFIED | 4 台 frame oracle 与 fixture/输入一致 |
| #185 runtime provenance | PARTIAL | 119/144 行 VERIFIED；batch12b/control/sensor 19 case 未接线 → #193 |
| #186 ADC calibration | VERIFIED | io/angle（exact-µV curve fitting）+ io/light PASS |
| #187 AtomS3 Lite console | VERIFIED | 2/2 cold boot + matrix primary PASS（UART0） |
| #188 Tab5 latest image | OPEN（未变） | 旧 merged-image lane PASS；最新官方镜像仍卡 DSI PHY |

## 本轮新增/更新 issue

### GitHub（模拟器仓库）

- [#190](https://github.com/m5agent/m5stack-esp-emulator/issues/190) 设备档案元数据与官方产品页不一致（NanoC6 SKU C122/C125、Dial 45/51mm、AtomS3R-CAM 14.0/13.5mm）
- [#191](https://github.com/m5agent/m5stack-esp-emulator/issues/191) Unit catalog 数据缺陷：Joystick2 SKU 误填 U169；TimerPWR/Step16/DoF6/CardKB2 research gaps 与 ADC v1.1 gap 过期
- [#192](https://github.com/m5agent/m5stack-esp-emulator/issues/192) stackchan-peripherals 固定 3s before-frame settle 在并行负载下不稳定（core2-axp192 同类瞬时失败）
- [#193](https://github.com/m5agent/m5stack-esp-emulator/issues/193) #185 follow-up：batch12b/control/sensor 仍不记录执行 runtime provenance（19 个 Unit case 不可绑定）
- [#178](https://github.com/m5agent/m5stack-esp-emulator/issues/178) 重新打开：classic ESP32 qemu-esptool 冷烧录在修复后 runtime 上仍间歇失败

### 内部 UIFlow2 GitLab（项目 163，9 个新 issue + 3 条既有 issue 证据）

- #27 display 图元参数 "(default -1/0)" 误导（fillRect 2 参数 TypeError）
- #28 display 缺 drawString/textWidth/fontHeight/getEpdMode 方法文档 + 对象名混用
- #29 ADC 文档缺 import 路径、atten 未标可选
- #30 unit/extio.rst literalinclude 悬空（437 个中唯一）
- #31 m5ui/index.rst 示例缺 M5.begin 前置
- #32 9 页 Unit 类名不可导入（Angle/Earth/Light/LimitUnit/PIR/WEIGHTUnit 等）
- #33 Unit 方法名拼写/case/不存在（byteswitch/vibrator/dac2/ir/op90/tmos/co2/co2l 等）
- #34 factory class 契约、私有 CRC 当公开、method directive 误用
- #35 hardware/system 文档 3 个成员缺失（UART.IRQ_TXIDLE、PORT.HAT、PORT.ALL）
- 追加证据：#9（4 个官方代码块不可编译 + 新增 m5espnow:40 双冒号）、#15（button 支持表图例）、#17（CAN 页无方法文档）

### 内部产品文档 GitLab（项目 121，5 个新 issue）

- #15 Hat ENV-III QMP6988 I2C 地址 0x56 应为 0x70（三语）
- #16 AtomS3 页 Arduino 快速上手链接误指 Atom Echo（en/zh_CN）+ ja 缺入口
- #17 ENV/ENV-II/ENV-III 规格表与同页对比表数值矛盾（三语）
- #18 INA226-1A/10A Model Size 资源误用 Unit CAN U085；INA226-1A 缺 UiFlow2 链接
- #19 CardKB2 三语 UiFlow2 段仍 "coming soon..."，官方文档已存在

## 边界

- 全部为 `virtual-device validation`；物理 RF/光学/电气/机械 `NOT RUN`。
- `INFRA-LOAD` 类（stackchan settle、core2-axp192、classic flash 部分失败）保留双观测（失败+重试/诊断 PASS），不记为产品回归；#192 要求 fixture 硬化而非放宽断言。
- UIFlow2 文档 commit `509a67aa` 与产品文档 `c06d36fc` 为基线；上一轮提的 UIFlow2 文档 issue #6–#26 仍 open，本轮新增 #27–#35。
- 未改任何 tracked 仓库文件；未提交 raw 固件/帧/日志；原始证据在 ignored `.work/retest-20261106/`。
- Unit 覆盖为 142/160：未覆盖 9 个无 batch runner Unit（2relay/scroll/flashlight/servo8-hat/8servos/joystick2/nfc + DEFER mini-bps-v11/mini-pdm）与 9 个超时盒 case；上一轮有独立 probe 的 Unit 本轮未全部重跑，已标 NOT RUN。
