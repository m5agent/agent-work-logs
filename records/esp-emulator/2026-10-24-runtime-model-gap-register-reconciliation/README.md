# ESP Emulator 运行时模型缺口登记与代码文档重整

- 日期：`2026-10-24`
- 结果：`PASS`（代码、契约、生成档案和文档一致性）
- 工作类型：`code_change`
- 问题来源：用户反馈多处文档仍停留在旧结论，要求完整梳理当前工作与待办
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码基线：`e339a6299000656aabbd687b587b949432b642a6`
- 结果提交：`d6694295e1ebee48f1056c2894171c48da6cac99`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40075831017>
- 环境：macOS Apple Silicon；Python 3；Node.js 22；GitHub Actions Ubuntu

## 结论

完成一次从源 catalog、QEMU profile、生成后的设备档案、代码地图、当前状态、
Backlog、工作流和专题页到文档契约测试的统一整理。

本次没有把“已分类”写成“已修复”。C6 Zigbee/802.15.4 未建模和 C6
`LP_SW_HPSYS` 软件复位后的 chip-id 错误仍为 `OPEN`，现分别由
`RUNTIME-02` 和 `RUNTIME-01` 跟踪；关闭它们必须补真实 QEMU
controller/reset 语义和新的运行 evidence，不能用宿主假值绕过 guest。

## 关键证据

- 平台契约测试：`317/317 PASS`，无跳过；
- Node SHA256/upload client：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- catalog/profile JSON parse 与 `git diff --check`：`PASS`；
- GitHub Actions run `40075831017`：`platform-contracts` 与
  `network-namespace-policy` 均成功；
- 本次源码改动：`32` files、`396` insertions、`67` deletions；
- 本轮未重跑完整 QEMU 外设矩阵，也未操作物理硬件：`NOT RUN`。

## 已修正的旧结论

- Core2 unified 专题仍写“十轮重连”，而当前证据是 3 个独立 lease 各 20 轮；
- Core2 OpenETH 夹具仍写 WiFi 为 `PARTIAL`，与后续 stock OpenMAC WiFi
  scan/association/DHCP/HTTP 和公网 DNS/HTTP PASS 冲突；
- StickS3 外设 README 仍写 IMU 数值为零，而当前 `Imu` API 与 QEMU 注入均已
  PASS；
- Core2 catalog/profile 仍缺 120 秒、active-BLE 和二十轮重连描述；
- C6 设备 catalog/profile 没有体现跨厂商矩阵中两个仍开放的模型缺口。

## 文件

- `report.md`：改动范围、证据、验证层级和剩余边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：测试、CI 和文件变更摘要。

## 未覆盖项

- `RUNTIME-01` C6 软件复位 chip-id 根因和修复：`NOT RUN`；
- `RUNTIME-02` C6 Zigbee/802.15.4 控制器可行性或实现：`NOT RUN`；
- 完整 67-case QEMU 矩阵：`NOT RUN`，本次没有修改 QEMU 控制器或设备数据面；
- 物理硬件、RF、功耗、声学和电气验证：`NOT RUN`。
