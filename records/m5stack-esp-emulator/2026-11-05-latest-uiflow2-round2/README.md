# 最新 UIFlow2 第二轮：全设备/全 Unit/控制闭环补全（经 issue 驱动）

- 日期：`2026-11-05`（Asia/Shanghai）
- 结果：`PARTIAL`（覆盖面显著补齐，仍有设备/模型类阻塞；未达“全部 PASS”）
- 工作类型：`report`
- 问题来源：用户追问“是否测试全部设备的全部 UIFlow 固件、全部 Unit 代码、以及控制闭环（改模拟器状态→guest 读取）”，要求再次全量测试并把问题提 issue；并批评上一轮并行度不足（长尾）。
- 源码版本：[m5stack-esp-emulator @ 73ed554f](https://github.com/m5agent/m5stack-esp-emulator/tree/73ed554f)
- 环境：macOS arm64、7 个隔离 Device Service（canonical 43-machine runtime `0e16a9bc…`）、最新官方 UIFlow2 固件；无物理硬件
- 前置记录：round-1 全量扫描

## 结论

本轮按“最大并行 + 明确队列”重跑，共 6 个并行 scope（device 全量、Unit 剩余三组、控制闭环输入/输出两组），并用既有 issue 编号复用避免重复提报：

1. **全部设备**：30/30 台 UIFlow2 设备都执行了最新固件（20 PASS + 10 FAIL；10 个 FAIL 中 8 个归入既有/新增 simulator issue、2 个为负载诱发在静默重跑通过）。3 台无 UIFlow2 构建的设备（m5stick/stickt2/cardputer-zero）明确 NOT RUN；tab5 旧 merged-image lane PASS，最新 v2.5.4 二进制 lane NOT RUN（新 issue）。
2. **全部 Unit**：catalog **160/160** 都有本轮或上一轮执行证据（round-1 覆盖 104 + round-2 补齐 56：U1 17 PASS、U2 21 PASS + 2 known-blocker、U3 22 PASS + 2 DEFER blocked；其中 9 个无 batch runner 的 Unit 已写闭环 probe：7 PASS + 2 DEFER blocked）。
3. **控制闭环**：
   - 输入方向 112 个 runtime-implemented input Unit：**107 COVERED + 5 PARTIAL（字段级）**，0 missing；另做 **16 个 round-2 新会话注入→guest 读取**执行（含 ENV 两组不同温湿度/气压向量：25.5°C/60.5% → guest 25.5/60.5/1000.0；31.25°C/45.0% → 31.3/45.0/900.0）。
   - 输出方向 115 个 output Unit：**115/115 COVERED**（95 个审计自 round-1 可见会话 QOM 证据 + 20 个由 round-2 U1/U2 补齐 + 16 个 round-2 新会话 guest 写→host 观测重放，118 行全部 PASS）。
   - 无任何 zero/null/wrong-scaling mismatch 被确认；U2 的 `buzzer`（UNIT-HOST-17 frozen SoftTimer 回调签名缺口）与 `angle`（S3 ADC 校准 eFuse 缺口，新 issue #186）为文档化 known-blocker/simulator。
4. **新增 issue（本轮）**：GitHub #186（Angle Unit ADC 校准 eFuse）、#187（AtomS3 Lite v2.5.4 REPL 前卡住）、#188（Tab5 最新 v2.5.4 二进制无法在现有 esp-emu/GDB lane 启动）；并在 #183（Basic BtnB）追加 round-2 “未复现”更正评论。既有 issue #172–#185 不再重复提报。
5. **并行度改进（针对上一轮批评）**：把剩余 46 个 batch case 拆成 U1/U2/U3 三组、9 个无 runner Unit 独立一组、闭环输入/输出各一组；6 个 scope 同时跑，长尾只剩文档/记录整理由 Lead 承担。

## 覆盖总览

| scope | 覆盖 | 结果 |
| --- | --- | --- |
| 设备全量（round-2） | 30/30 UIFlow2 设备（+3 NOT RUN 无构建） | PASS 20 / FAIL 10（8 simulator 含既有 issue，2 INFRA-LOAD 静默重跑 PASS） |
| U1 剩余 Unit batch | batch11 7 + batch12a 7 + can_lorawan 3 | 17/17 PASS |
| U2 剩余 Unit batch | batch12b 7 + batch12c 4 + io 12 | 21/23 PASS + 2 known-blocker（buzzer/angle） |
| U3 control/sensor/无 runner Unit | control 5 + sensor 7 + 无 runner 9 + service 3 | 22 PASS + 2 BLOCKED（mini-bps-v11/mini-pdm DEFER） |
| 闭环输入 | 112 input Units | 107 COVERED + 5 PARTIAL；16 fresh round-2 sessions |
| 闭环输出 | 115 output Units | 115/115 COVERED；16 fresh round-2 sessions + 20 audited from U1/U2 |
| Unit catalog 总覆盖 | 160/160 | 都有执行证据（PASS/BLOCKED 明确） |

## 关键证据

- 聚合：coverage-summary.json（含闭环 fresh 执行计数、round-2 各 scope 状态、160/160 覆盖、未覆盖=[]）。
- 设备：device-round2-summary.md、`round2/device/results.json`（本地 ignored）；tab5 lane 证据 `tab5-attempts.json`。
- Unit：units-U1、U2、U3 summary；每 case 的固件版本+sha256、session_id、serial/QOM/frame、evidence ZIP 记录在各自 results.json。
- 闭环：输入 summary + coverage、输出 coverage；包含 per-unit 注入值/guest 读值/写入/观测与 executed_round2 标记。
- 原始串口/帧/QOM/evidence ZIP 保留在 ignored `.work/uiflow-latest-20261105/`（不提交）。

## 未覆盖项

- 物理硬件、RF、功耗、声学、光学、电气、机械：全部 `NOT RUN`；本轮仍为 virtual-device validation。
- 3 台无最新 UIFlow2 构建的设备：m5stick（EasyLoader factory）、stickt2（无 UIFlow2 build）、cardputer-zero（Linux ARM64 镜像）→ NOT RUN。
- tab5：旧 merged-image lane PASS 不等于最新 v2.5.4 二进制 PASS；后者 NOT RUN，已提 #188。
- 设备 FAIL 类：8 个 simulator（atoms3 面板、papercolor/dial/nanoc6/atoms3-lite 启动卡住、stickc/plus/plus-se 矩阵 fixture 契约）均引用既有或本轮新 issue，未修复。
- Unit：U2 的 buzzer/angle 两个 known-blocker/simulator；U3 的 mini-bps-v11/mini-pdm 为 catalog DEFER；31 个 runtime unsupported + 5 planned 的 Unit 无模型，不在闭环目标内（已按 catalog 状态排除）。
- 闭环 5 个 PARTIAL 为字段级（既有 probe 向量少于声明可写字段）：cardkb2 mode、8servos2-i2c 7 字段、step16 led/rgb/brightness、timerpwr 10 字段、mq ntc-mv；无错误读数，仅覆盖不足。
