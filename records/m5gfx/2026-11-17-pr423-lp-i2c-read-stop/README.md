# ESP32-C5 LP_I2C: read 终端的 STOP 改用控制器命令（M5GFX PR #423 评审）

- 日期：`2026-11-17`
- 结果：`REVIEW`（仅代码层评审；硬件 / 虚拟设备 / 构建均 `NOT RUN`）
- 工作类型：`pull_request`
- 条目：[m5stack/M5GFX#423](https://github.com/m5stack/M5GFX/pull/423)
  「i2c: LP ポートでは read の後もコントローラの STOP で閉じる」，作者 GOB52，日文
- 源码：base `develop` `b48dce04c80d3e3c9874b7ba946c43d672129c28`、PR head
  `cc60eaa02af50a559e7f856392a2b740f446fa0b`（1 文件 +6/-2，
  `src/lgfx/v1/platforms/esp32/common.inl`）
- 环境：macOS。本机无 ESP32-C5；本机 Device Service 的 profile 只到 ESP32-C6 / P4；
  QEMU 的 C6 机器未实现 LP I2C 控制器

## 结论

补丁的根因说明与 `develop` `b48dce0` 的代码一致。`i2c_wait()` 对“以 read 结束的事务”无条件
走强制 STOP 路径（`:1988`）；该路径的 `i2c_stop()` 只用普通 GPIO 位操作（`:1847-1882`），
LP 端口焊盘由 LP IO 域接管（`:2278-2300`，且 `beginTransaction()` 对 LP 跳过 `set_pin()`，
`:2555-2562`），因此 STOP 到不了总线；随后 `lp_i2c_ll_reset_register()`（`:1583-1587`）
没有返回值，调用仍报成功。

补丁把 LP 端口的 read 终端改为走控制器的 STOP 命令（`STOP` + `END`），HP 端口、write 终端、
错误时的强制 STOP 全部保持原样；`LGFX_LP_I2C_NUM == 0`（IDF < 5.4 或没有 LP I2C 的芯片）时
`isLpPort()` 恒为 false，条件表达式与旧代码等价，不存在既有目标退行。

评审未发现阻塞问题。唯一待确认项是 C6 / P4 等其他 LP I2C 芯片未实测（作者已在正文声明）。
若该路径在这些芯片上不成立，失败形态会从“静默缺 STOP”变成“每次 read 等 25 ms 后返回
`connection_lost`”，退行更明显；因此建议至少取得一个 C6 或 P4 的 read→read 数据点。

补丁可在 `b48dce0` 上干净应用（`git apply --check` 通过）。#421 中要求的「控制器 STOP
单独」隔离，作者已用正文第一张表（Space B read 直后的 Space A read：`develop` 0/100 → 本补丁 100/100）给出。

## 行为矩阵（本 PR 后）

| 端口 | 以 write 结束 | 以 read 结束 | 出错时 |
| --- | --- | --- | --- |
| HP（`isLpPort` false） | 控制器 STOP | 强制 STOP（GPIO），不变 | 强制 STOP（GPIO） |
| LP（`isLpPort` true） | 控制器 STOP | **控制器 STOP（本 PR 改动）** | 强制 STOP（GPIO，仍到不了焊盘） |

## 关键证据

- 代码定位（`b48dce0`）：`i2c_stop()` `:1847-1882`；LP 复位 `:1583-1587`；read 强制 STOP
  分支 `:1988`；控制器 STOP 分支 `:2000-2037`（25 ms 上限 `:2011`、失败回落 `:2016-2023`）；
  `isLpPort()` `:1447-1456`；LP 打开总线 `:2278-2300`；LP 跳过 `set_pin()` `:2555-2562`；
  bus busy 恢复 `:2545-2549`；read 超时 `:2754`；`endTransaction()` `:2620`。
  摘录见 `evidence/source-lines.txt`。
- 补丁适配：`evidence/apply-check.txt`（对 `b48dce0` 干净应用）。
- 硬件清单（脱敏）：`evidence/hardware-inventory.md`（无 ESP32-C5）。
- 虚拟设备边界：`evidence/virtual-device-check.md`（C6 的 LP 域 RTC I2C 是 all-ones 桩，
  LP I2C 控制器未建模；无 C5 profile、无 ST25R3916）。
- 已发布回复：`evidence/reply.md`。

## 文件

- `report.md`：完整评审、影响面、风险与时间线
- `run.json`：结构化状态
- `evidence/`：PR 元数据与 diff、应用检查、源码摘录、硬件清单、虚拟设备边界、回复原文

## 未覆盖项

- hardware validation：`NOT RUN`（本机与内部硬件测试中心都没有 ESP32-C5）
- virtual-device validation：`NOT RUN`（见上，LP I2C 控制器与 ST25R3916 均无模型）
- build：`NOT RUN`（本机无 ESP-IDF / Arduino-ESP32 工具链）
- C6 / P4 实机、SDA/SCL 波形、LP_I2C 寄存器 dump：`NOT RUN`
