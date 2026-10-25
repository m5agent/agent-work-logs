# ESP Emulator Core2 QIO, WDT-mask and cross-core boundary report

## 背景

- 来源：
  [m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator)
- 需求：完整整理代码和文档，并说明当前已完成工作、正在调查的问题和后续
  TODO；用户指出多份页面仍停留在旧的 I2C/单一 timer 阶段。
- 目标：吸收 `0035`、QIO bulk-read 比较和 cross-core/DPORT 停滞证据，
  把“模型修正、诊断快路、产品门禁”明确分开。

## 结论

TIMG 旧模型在 `INT_ENA.WDT=0` 时仍抬高 WDT level IRQ，与硬件 masked
status 语义不符。`0035` 只在 enable bit 置位时抬高 level，保留 raw status
和 stage timer，不改变复位阶段。两个 Device Service control 在修复后仍以
`TG0WDT_SYS_RESET`/reset PC `0` 失败，因此它不能关闭 `RUNTIME-03`。

legacy 启动期的大量 QIO 事务使逐字节 `ssi_transfer` 成为显著宿主成本。
临时 `blk_pread` 路径从同一 m25p80 BlockBackend 读取，并与随后的 SSI
字节流逐项对比；512 个 64-byte 样本全部一致。该快路只在单独临时 control
中推进到 MicroPython banner/REPL，随后仍复位；它绕过 controller
command/dummy/data phase，不满足产品数据面要求。

关闭 WDT reset 后，UI banner 保持不变，CPU0 位于
`spi_flash_op_block_func` 等待 `0x3ffc7ec8`，CPU1 位于 DPORT safe-read /
flash-cache handoff；cross-core IRQ0/IRQ1 持续翻转。该结果只说明症状改变，
不证明“关闭 WDT 就能运行”，也不足以指定单一根因。

## 改动范围

- 新增
  `patches/qemu-m5stack-peripherals/0035-esp32-timg-wdt-int-ena.patch`；
- 新增 `tests/firmware/evidence-2026-10-26-core2-qio-crosscore-diagnostic.json`；
- 更新 README、项目状态、Backlog、工作流、交接、QEMU 矩阵、代码地图、
  历史 Core2 调查、公开固件矩阵、验证台账、patch 说明和生成快照；
- Core2 文档契约新增 TIMG mask、QIO diagnostic-only、cross-core 和 patch
  apply-order 检查；
- 未修改 Device Service 模块边界；`SVC-03` 继续作为独立重构任务。

## 执行

```bash
git archive HEAD hw/timer/esp32_timg.c | tar -x -C "$tmp_dir"
git -C "$tmp_dir" apply --check \
  esp-emulator/patches/qemu-m5stack-peripherals/0035-esp32-timg-wdt-int-ena.patch
git -C "$tmp_dir" apply \
  esp-emulator/patches/qemu-m5stack-peripherals/0035-esp32-timg-wdt-int-ena.patch
git -C "$tmp_dir" apply --reverse --check \
  esp-emulator/patches/qemu-m5stack-peripherals/0035-esp32-timg-wdt-int-ena.patch

PYTHONPATH=platform/tests:platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_docs_*_contract.py'

PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'

python3 platform/tools/project_snapshot.py --check
python3 platform/tools/runtime_coverage.py --check
python3 platform/tools/peripheral_catalog.py --check
python3 platform/tools/qemu_profiles.py --check
ruff check --select E9,F platform/tools platform/tests
```

QEMU patch base：
`da100c909249926b9f4458f18e4f2d216d08f51a`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | patch clean-base forward/reverse check、compileall、Ruff `E9/F` |
| transport | `PARTIAL` | `0035` control 仍进入 TG0 reset；QIO 快路可到 REPL，但绕过 SSI phase |
| device_response | `PARTIAL` | cross-core IRQ 持续翻转，但 handshake 未完成、无非空应用帧 |
| data_behavior | `PARTIAL` | 512 个 QIO 样本与 SSI 字节一致；不是产品 controller 路径 |
| documentation contract | `PASS` | docs `41/41`、platform `501/501`、snapshot/coverage/catalog/profile |
| delivery | `PASS` | product commit `5a004b2`；CI `40221727154` 两 job PASS |
| legacy UIFlow | `FAIL` | `TG0WDT_SYS_RESET`、reset PC `0`、black frame |
| visual_or_physical | `NOT RUN` | 物理 SPI/cache/PSRAM/timer/WDT、RF、电气与真机均未执行 |

## 验证边界

- `0035` 只修正 TIMG level IRQ mask，不证明 legacy watchdog reset 根因；
- QIO 对比来自 retained dirty QEMU 诊断树，evidence 明确为
  `DIAGNOSTIC_ONLY`，不绑定产品 runtime；
- `M5SW_DISABLE_WDT`、temporary bulk read 和单次 REPL marker 都不能成为
  固件 PASS；
- 完整 UIFlow2 外设矩阵、Core2 长稳/并发和物理硬件没有在本轮重跑；
- 同 SoC 或其他 Core2 固件不能继承此处局部结论。

## 风险与回滚

没有烧录、擦除或持久设备状态变更。`0035` 是单行语义修正；若发现 ESP32
hardware 文档或跨固件回归与预期不符，可 revert product commit `5a004b2`。
更小回滚点是移除 `0035` 并重建 QEMU，但这会恢复已确认错误的 masked WDT
level IRQ 行为。retained dirty QEMU 工作树未进入产品仓库，必须继续保留；
不能执行 reset/clean。
