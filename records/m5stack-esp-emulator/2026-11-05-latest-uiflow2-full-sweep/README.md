# 最新 UIFlow2 固件全设备 / 全外设多角度验证（issue 前置扫描）

- 日期：`2026-11-05`（Asia/Shanghai）
- 结果：`PARTIAL`（覆盖广但未全量：boot 19/29、UI 11/31、外设 60/68、Unit 104/160；所有 FAIL 已复现并分流）
- 工作类型：`report`
- 问题来源：用户要求“拉取最新 UIFlow 固件给每个设备装上；读取最新文档给每个设备/外设写多轮测试并先提 issue”
- 源码版本：[m5stack-esp-emulator @ 73ed554f](https://github.com/m5agent/m5stack-esp-emulator/tree/73ed554f)
- 环境：macOS arm64、隔离的 agent 自有 Device Service（多端口/独立状态）、QEMU Xtensa/C6 canonical runtime；未使用物理硬件

## 结论

1. **固件已拉取并逐字节校验**：30 台设备的当前官方 UIFlow2 固件（v2.5.5 × 4、v2.5.4 × 23、v2.5.4-4MB × 1、官方 pinned release × 2），全部 SHA256 与 sidecar 一致；缓存即为各 runner 的 base 路径。
2. **最新文档已读取**：内部 UIFlow2 仓库 `develop_m5things` @ `509a67aa`（version.txt v2.5.4，2026-10-30），只读 `git show`，未改动 UIFlow 工作树。
3. **本次提交 14 个 GitHub issue + 10 个内部 UIFlow 文档 issue**（另在 2 个既有内部 issue 追加最新证据），覆盖：模拟器模型缺口、tracked matrix/runner 工具缺陷、以及最新官方文档与实现不一致。所有 issue 均带固件/运行身份与两轮复现边界，便于其他 agent 逐个处理。
4. **已修复/规避的验证基础设施问题**（仅 `.work` 派生，不改 tracked 文件）：最新固件分区表漂移 → 派生 VFS 布局 adapter；matrix-pinned QEMU build 缺新 machine → canonical goals runtime（服务 G/F/E）；classic eFuse 参数与 fixture 形态不一致 → 派生 runner 绕过，但已作为工具缺陷提 issue。
5. **未达成全量**：见“未覆盖项”。物理硬件、RF、功耗、光学、电气、机械全部 `NOT RUN`；全部结论为 `virtual-device validation`。

## 覆盖总览

| scope | 覆盖 | 结果 | 说明 |
| --- | --- | --- | --- |
| 固件拉取 | 30/30 UIFlow2 设备 | PASS | 全部 SHA256 校验；无 UIFlow2 构建的 3 台另列 |
| Device Service 虚拟烧录+启动 | 29 台 × 2 轮 = 58 case | 38 PASS / 20 FAIL | 19 台设备两轮 PASS；10 台 classic 全部 known-blocker（qemu-esptool） |
| 设备 UI/输入矩阵 | 31 台（含 tab5 自有 lane） | 11 PASS / 15 FAIL / 4 BLOCKED / 3 NOT RUN | 15 个 FAIL 全部两轮复现；4 台 matrix 契约不一致 |
| 外设矩阵 | 68/68 case | 60 PASS / 8 FAIL | 8 个 FAIL 全部两轮复现；同类根因收敛为 2 模型缺口 + 2 期望更新 |
| Unit 电池 | 104/160 catalog Unit | 93 PASS + 9 PASS-after-rerun + 2 BLOCKED（0 FAIL） | round2 把 9 个 round1 FAIL 复跑为 PASS（根因是 agent 派生脚本路径回归，非模拟器/Unit 缺口）；46 case 未执行（时间盒），9 个无 batch runner |
| 文档驱动多角度 | 25 case / 135 checks | 19 PASS / 6 BLOCKED | 12 个确认 `uiflow-docs` mismatch，全部两轮复现并已提内部 issue |

## 已提交 issue

### GitHub（模拟器仓库，13 个）

- [#172](https://github.com/m5agent/m5stack-esp-emulator/issues/172) classic eFuse 版本 5/6 被 runner argparse 拒绝，9 台设备矩阵不可用
- [#173](https://github.com/m5agent/m5stack-esp-emulator/issues/173) 4 台 `mode=console` 缺 `make_image.py`，tracked 矩阵构建失败
- [#174](https://github.com/m5agent/m5stack-esp-emulator/issues/174) device matrix VFS 偏移与最新官方固件漂移（14 台静默写错 VFS、假 FAIL）
- [#175](https://github.com/m5agent/m5stack-esp-emulator/issues/175) PaperColor ED2208 partial-window 刷新（0x83）未建模，5 个外设 case 画面错位
- [#176](https://github.com/m5agent/m5stack-esp-emulator/issues/176) CoreS3 AXP2101 充电状态机 REG01 bits[2:0] 未建模，isCharging() 恒 true
- [#177](https://github.com/m5agent/m5stack-esp-emulator/issues/177) 外设矩阵两处旧期望需更新（PaperColor charging、StickS3 BMI270 轴向）
- [#178](https://github.com/m5agent/m5stack-esp-emulator/issues/178) classic ESP32 qemu-esptool 虚拟烧录路径失败（10 台设备 known-blocker）
- [#179](https://github.com/m5agent/m5stack-esp-emulator/issues/179) AtomS3 面板模型 invert/MADCTL 与最新 v2.5.4 初始化不符（帧 180°+反色）
- [#180](https://github.com/m5agent/m5stack-esp-emulator/issues/180) PaperColor v2.5.4 启动卡住未到 REPL（0x10200C rejected read 线索）
- [#181](https://github.com/m5agent/m5stack-esp-emulator/issues/181) Dial v2.5.4 启动卡住未到 REPL
- [#182](https://github.com/m5agent/m5stack-esp-emulator/issues/182) NanoC6 v2.5.4 卡在 `Startup with network type: WIFI`
- [#183](https://github.com/m5agent/m5stack-esp-emulator/issues/183) Basic v2.7 host key:b 未到 guest M5.BtnB（GPIO38）
- [#184](https://github.com/m5agent/m5stack-esp-emulator/issues/184) StickC 系列 4 个 matrix 条目的 frame 断言与自带 fixture 自相矛盾
- [#185](https://github.com/m5agent/m5stack-esp-emulator/issues/185) checked-in Unit batch runners 硬编码 pre-Unit QEMU runtime、evidence runtime SHA 可能不一致

### 内部 UIFlow2 GitLab（项目 163，10 个新 issue + 2 个既有更新）

- 新：`#17`…`#26`（见内部记录）：CANUnit 签名、RGB/RGBUnit 类名、ADCUnit setter 名、Finger 方法单复数、Buzzer `deint`、Relay 拼写与 `set_status` 参数、Joystick 默认地址、ToF 文案、Button `type`、CardKB factory mode —— 全部带 docs path:line + sha256 + guest 两轮证据。
- 更新：#16（EPD `setEpdMode` 0–3 vs 1–4 在最新 v2.5.4 文档仍存在）、#15（button.rst 支持表缺 StopWatch，最新固件实测 BtnA/B/C/PWR 可用）。

## 关键证据

- 构建或运行：最新固件清单与逐设备 SHA256（`evidence/coverage-summary.json`）；canonical runtime sha256 `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`；matrix-pinned runtime `6d9af027…`。
- 实机或服务执行：全部为 agent 自有 Device Service 可见 session / direct QEMU；boot 19 台两轮 cold PASS；tab5 仅其 emulator merged lane PASS（不转移到 M5Burner v2.5.4）。
- 日志、测量或协议：原始串口、frame、serial markers、QOM 与 evidence ZIP 保留在 ignored `.work/uiflow-latest-20261105/`（约 1.5 GB，不提交）；本记录只保存聚合摘要与 issue 索引。
- 关键失败已复现：boot 10/10、device-ui 15/15、peripheral 8/8 均为两轮复现；docs 12/12 两轮复现。

## 文件

- [report.md](report.md)：方法、逐 scope 结果、根因分类、issue 分流、未覆盖项与边界。
- [run.json](run.json)：机器可读记录（固件/运行时/覆盖/issue 索引/limits）。
- `evidence/coverage-summary.json`：固件版本分布、逐 scope 计数、限制。
- `evidence/issue-index.json`：本次所有 GitHub/GitLab issue 索引（内部 GitLab issue 仅编号，不含内网 URL）。
- 派生工具与完整原始证据：ignored `.work/uiflow-latest-20261105/`（`tools/`、各 scope `results.json`、`candidates/`）。

## 未覆盖项

- 物理硬件、RF、功耗、声学、光学、电气与机械行为：全部 `NOT RUN`；本记录不构成物理结论。
- 无最新 UIFlow2 构建的 3 台：`m5stick`（EasyLoader factory）、`stickt2`（UserDemo/thermal probe）、`cardputer-zero`（ARM64 Linux 镜像）——本轮没有“最新 UIFlow 固件”可装，保持既有 blocker。
- tab5：其 PASS 来自 `.work/uiflow2-tab5` emulator-merged lane，**不是** M5Burner v2.5.4 二进制；最新 P4 固件未在该 lane 执行。
- Unit：104/160 覆盖（93 PASS + 9 round2 PASS + 2 tracked EXPECTED_BLOCKED）；56 个未覆盖（46 个 batch case 超时盒、9 个无 batch runner、2 个 DEFER），需下一轮补 runner/时间。
- 全量 browser-WASM lane、网络/蓝牙 lane 未在本轮重跑；不继承旧结果。
- classic ESP32 的虚拟烧录（esptool 写入）在本环境不可用；host-image lane 可启动 guest，但不能替代 flashing 验收。
- 未提交任何仓库代码改动；所有模拟器/工具缺陷通过 issue 跟踪，不在此记录内修复。
