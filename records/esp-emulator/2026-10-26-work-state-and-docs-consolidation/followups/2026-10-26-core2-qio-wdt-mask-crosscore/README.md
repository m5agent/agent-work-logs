# ESP Emulator Core2 QIO, WDT-mask and cross-core boundary

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户要求完整整理代码和文档，把后续 Core2 QIO、TIMG WDT
  trace、timer 与 cross-core 诊断合并到当前工作/待办，并清理仍停留在旧
  I2C 或单一 timer 结论的页面
- 源码版本：
  [m5stack-esp-emulator @ 5a004b2](https://github.com/m5agent/m5stack-esp-emulator/commit/5a004b24053bf791203083be4dfa426f971525a8)
- Base commit：`c3193b92cc46b41a7dc8574089fc2b95df37caa4`
- 环境：macOS arm64；Python 3.13；QEMU `9.2.2` virtual Core2；
  physical hardware `NOT RUN`

## 结论

新增产品补丁 `0035-esp32-timg-wdt-int-ena.patch`，修正 TIMG WDT level
IRQ 的 mask 语义：只有 `INT_RAW & INT_ENA` 才驱动 level line，raw status
和 stage timer 保持可见/运行。trace 已直接观测到
`INT_ENA=0x00000000`、`INT_RAW=0x00000004`、masked status `0`；但两个
Device Service control 在修复后仍进入 `TG0WDT_SYS_RESET`，所以 `0035`
是独立模型修正，不是 `RUNTIME-03` 根因修复。

legacy Flash 扫描还暴露逐字节 SSI 转发成本。临时 `blk_pread` 快路径在
512 个 64-byte 采样 cache line 上与后续 SSI 字节流全部一致，并把一个临时
control 推进到 MicroPython banner 和 `>>>`；但它绕过 SSI/m25p80
command/dummy/data 状态机，不能作为产品实现。关闭 watchdog reset 后，
CPU0 停在 flash operation block 等待路径，CPU1 停在 DPORT safe-read /
flash-cache handoff，cross-core IRQ0/IRQ1 持续翻转。下一步必须在真实
控制器数据面内实现高效 QIO，并证明 cross-core/DPORT 交接顺序。

README、当前状态、Backlog、工作流、交接、代码地图、公开固件矩阵、
QEMU 后端矩阵、运行时缺口登记、验证台账和生成快照已统一到同一口径。
代码审计仍将 `device_service.py` 的状态机、storage、runtime、evidence 和
HTTP 混合边界列为 `SVC-03`；本轮没有为了“整齐”移动该文件，因为现有
Core2 evidence 绑定它的 tool hash。

## 关键证据

- 产品 patch clean-base forward/reverse apply check：PASS；
- QIO 字节对照：`512` 个事务、每事务 `64` bytes、`0` mismatch；
- `0035` control：两个独立 Device Service session 仍分别出现 `6`/`10`
  次 `TG0WDT_SYS_RESET`；
- WDT-disabled cross-core control：`97,150` 条 cross-core trace transition，
  握手完成条件未观察到；
- 平台测试：`501/501 PASS`；
- 文档领域契约：`41/41 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、Ruff `E9/F`、JSON 和 `git diff --check`：PASS；
- 产品 CI
  [`40221727154`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40221727154)
  的两个 job 均 PASS；
- firmware、legacy 非空应用帧、正常 WDT 下的产品 QIO 路径、物理 timer/
cache、RF、电气和真机仍为 `FAIL`/`NOT RUN`。

## 文件

- `report.md`：问题、改动、验证、边界与回滚；
- `run.json`：机器可读结果；
- `evidence/core2-qio-wdt-crosscore-summary.json`：脱敏 evidence 摘要、
  原始日志哈希与平台验证；
- `patches/0001-esp32-timg-wdt-int-ena.patch`：QEMU TIMG mask 业务补丁。

## 未覆盖项

- temporary `blk_pread` 与 `M5SW_DISABLE_WDT` 都不是产品修复；
- legacy UIFlow 仍没有在正常 WDT、真实 SSI/m25p80 数据面下产生非空应用帧；
- cross-core handshake 未完成的根因仍是 `OPEN`；
- 本轮没有重跑完整 UIFlow2 外设矩阵或 Core2 长稳/并发；
- 物理 SPI Flash、cache、PSRAM、timer、watchdog、RF、电气和真机均
  `NOT RUN`。
