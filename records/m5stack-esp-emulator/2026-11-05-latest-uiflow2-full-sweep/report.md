# 最新 UIFlow2 固件全设备/全外设验证报告

## 背景

- 来源：用户要求（1）拉取最新 UIFlow 固件，给模拟器的每个设备装上；（2）读取最新 UIFlow 文档，给每个设备和每个外设写多轮、不同角度的测试；（3）发现的问题先提 issue（模拟器问题提本仓库；UIFlow 问题提 UIFlow 仓库）。
- 目标：在 `virtual-device validation` 层级给出最新官方固件的全设备覆盖现状，并把所有可复现问题分流成可执行的 issue，而不是在本轮直接修仓库。
- 团队：Lead + 5 个 teammate（boot/flash、device UI、peripheral matrix、Unit battery、docs-codegen），并行使用独立端口/状态的 Device Service 与 canonical QEMU runtime。

## 方法

1. **固件**：`platform/tools/fetch_firmware.py --all --force` 解析 M5Burner/GitHub 当前发布版本，写入 `platform/.cache/firmware/<device>/uiflow2.bin`（即各 runner 的 base 路径），逐设备校验 sha256。
2. **布局适配**：最新固件分区表与 tracked `tests/uiflow2/device_matrix.json` 的 VFS 偏移有 14 台漂移；用派生脚本按 base 分区表生成 `.work/.../device_matrix.latest.json` 与 provider adapter（不改 tracked 文件）。
3. **Runtime**：默认 matrix-pinned QEMU build（35 machines）缺少 2026-11-02 之后新增的 machine（m5basic/m5atomu/m5atomecho/m5atomvoices3r/m5atoms3rcam/m5atoms3rm12），改用仓库 canonical patch build（43 machines，sha `0e16a9bc…`）启动；Unit 需要 Unit model chain，另起 canonical runtime 服务。
4. **Scope 执行**：
   - boot/flash：每台可运行设备 2 轮 cold boot，经 Device Service 可见 session + evidence ZIP + `purge=0`。
   - device UI：tracked matrix（派生布局）+ `--flash-transport direct` 对照，两轮。
   - peripherals：68 个 checked-in case 全部执行，失败两轮 + v2.5.3 固件 differential。
   - Units：重跑既有 batch runners（canonical runtime + 派生 matrix），失败两轮。
   - docs：读取内网 UIFlow2 文档 commit `509a67aa`，生成 25 个 site 探针/135 checks，12 个 mismatch 两轮复现。
5. **Issue 分流**：模拟器模型/工具/matrix → GitHub（13 个新 issue）；文档与实现不一致 → 内部 UIFlow2 GitLab（10 个新 issue + 2 个更新）。

## 结果

### 固件

30 台设备 uiflow2 固件：v2.5.5（cores3/stackchan/sticks3/stopwatch）、v2.5.4（23 台）、v2.5.4-4MB（basic-v27）、pinned official release（atom-echo/atomu）。全部 SHA256 与 sidecar 一致；`tab5` v2.5.4 已下载但本轮 PASS lane 使用旧 emulator merged image，不作为 v2.5.4 执行证据。`m5stick`/`stickt2`/`cardputer-zero` 无最新 UIFlow2 构建。

### 逐 scope

| scope | 案件 | PASS | FAIL | BLOCKED/NOT RUN | 失败分类 |
| --- | ---: | ---: | ---: | ---: | --- |
| boot/flash（29 设备 ×2 轮） | 58 | 38 | 20 | — | 10 台 classic qemu-esptool known-blocker |
| device UI（31 设备） | 33 | 11 | 15 | 4 BLOCKED + 3 NOT RUN | 9 simulator（2 QEMU 模型/输入/启动、4 matrix 契约、tab5 lane 说明），5 infra（flash/machine 环境） |
| peripheral matrix | 68 | 60 | 8 | — | 5 ED2208 partial-window、1 AXP2101 电荷状态、2 stale expectation |
| Unit battery | 104（覆盖 104/160） | 93 + 9 round2-PASS | 0 | 2 BLOCKED + 46 NOT RUN | 2 个 tracked EXPECTED_BLOCKED（mini-can/lorawan-us915）；round1 9 个 FAIL 为 agent 派生脚本路径回归（infra），round2 全 PASS |
| docs-driven | 25 | 19 | 0 | 6 BLOCKED(infra) | 12 个 `uiflow-docs` mismatch 已确认 |

### GitHub issues（本仓库，13 个）

工具/matrix 缺陷（5）：#172 eFuse 5/6 argparse、#173 4 台 console fixture 缺 make_image、#174 VFS 布局漂移导致假 FAIL、#184 StickC 系列 frame 断言与 fixture 自相矛盾、#185 Unit batch runner 硬编码 pre-Unit runtime/证据 SHA 不一致。

QEMU 模型/输入缺口（5）：#175 PaperColor ED2208 partial-window、#176 CoreS3 AXP2101 充电状态机、#179 AtomS3 面板方向/反色、#180 PaperColor v2.5.4 启动卡住、#181 Dial v2.5.4 启动卡住。

环境/固件启动与矩阵期望（4）：#178 classic qemu-esptool 烧录阻断、#182 NanoC6 网络启动卡住、#183 Basic v2.7 BtnB 输入、#177 PaperColor/StickS3 官方行为变化的旧期望更新。

### 内部 UIFlow2 issues（10 新 + 2 更新）

文档/实现不一致（全部两轮 guest 复现、带 docs path:line + sha256）：CANUnit 签名、RGB vs RGBUnit、ADCUnit setter 名、Finger 方法单复数、Buzzer `deint`、Relay 拼写/参数、Joystick 默认地址、ToF 文案、Button `type`、CardKB factory mode。

更新：#16（EPD 数值 0–3 在最新 v2.5.4 文档仍错）、#15（button.rst 支持表缺 StopWatch，实测 BtnA/B/C/PWR 存在）。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| 固件获取与哈希 | PASS | 30/30 sha256 match；版本分布见 coverage-summary |
| transport（guest UART / Device Service） | PASS（19 台） / known-blocker（10 台 classic） | 串口 marker + session + evidence ZIP |
| device_response | PARTIAL | 19/29 boot；11/31 UI；60/68 外设；12/12 docs mismatch 复现 |
| data_behavior | PARTIAL | 42/51 Unit；8 外设 FAIL 根因收敛；Unit round2 未完成 |
| visual_or_physical | NOT RUN | 无物理硬件；所有结论仅 virtual-device |

## 验证边界

- 全部结果为 `virtual-device validation`；物理 RF/功耗/声学/光学/电气/机械未测，不能从本记录外推真机行为。
- 3 台无最新 UIFlow2 构建的设备与 tab5 的 lane 边界已在 README/issue 中明确；不得把 tab5 emulator-merged PASS 说成 M5Burner v2.5.4 PASS。
- classic 设备的“host-image 可启动”不等于“虚拟烧录通过”；esptool 写入失败已单独提 #178。
- 失败分类中 `infra`（环境/工具使用）与 `simulator`/`uiflow-*` 分开记录；未把环境阻塞算作固件失败。
- 未修改 tracked 文件；所有派生 adapter/证据在 ignored `.work/`，本记录仅保存聚合摘要与 issue 索引。

## 风险与回滚

- 无 tracked 代码改动，无需回滚；隔离服务与 guest 已按 owner 停止（最终清理时记录）。用户 8787/8830 未使用。
- issue 已提交后，若后续发现证据边界问题，应在对应 issue 追加更正而不是改写历史结论；本记录保留 `PARTIAL` 状态与未覆盖清单。
