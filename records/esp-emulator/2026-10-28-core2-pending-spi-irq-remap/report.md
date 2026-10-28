# Core2 pending SPI IRQ remap 报告

## 背景

`RUNTIME-03` 的既有证据把 legacy Core2 的 late wait 收敛到 LVGL
`lv_refr_vdb_flush`：display flush callback 已启动，但
`lv_disp_flush_ready` 未执行。进一步使用独立 SPI 固件后发现，问题可以在
不依赖 vendor UIFlow 地址的情况下复现。

目标是把 guest SPI completion 与 QEMU interrupt-matrix 行为对齐，并保留
明确的失败 control。该修复不预设 legacy UIFlow 必定启动成功。

## 根因

guest 先将 SPI3 source 映射到 CPU interrupt 5，随后写回 QEMU
“unconnected”值，抬高 `SPI_SLAVE.TRANS_DONE` 与 `TRANS_INTEN`，最后再
写回映射 5。

旧 interrupt matrix 只在输入 level 变化时转发。source 已经为高后再修改
mapping 不会触发重新计算，因此 CPU interrupt line 没有抬高，SPI ISR 和
queued transaction completion 永远等待。

## 改动

- 保留全部 69 个 interrupt matrix 输入 level；
- 在输入 level 或 mapping 变化时，按 CPU external interrupt 重新计算
  output；
- 多个输入映射到同一 CPU interrupt 时按 OR 汇总；
- 保存 `SPI_SLAVE.TRANS_DONE/TRANS_INTEN`，SPI IRQ 为二者逻辑 AND；
- 增加真实 ESP-IDF guest 探针、patch C contract、pre-fix control 和
  Core2 UIFlow2 定向回归。

## 执行

构建环境：

```text
ESP-IDF 5.5.4
QEMU fixed binary 22bf9dba026ccb8a2d5f483de5917eb56433610d97709abe29122c49358d3d67
QEMU pre-fix binary 03ae86b5ce2d2029bf68a1b0e9c89153447217a02938a556ea292066b222afaf
```

核心命令：

```bash
idf.py -C tests/firmware/core2_spi_irq_remap \
  -B .work/core2-spi-irq-remap-build build

python3 tests/firmware/core2_spi_irq_remap/run_test.py \
  --image .work/core2-spi-irq-remap-16m.bin \
  --elf .work/core2-spi-irq-remap-build/core2_spi_irq_remap.elf \
  --attempts 3 \
  --out-dir /tmp/core2-spi-irq-remap

PYTHONPATH=.work/py python3 tests/uiflow2/run_peripheral_matrix.py \
  --device core2 \
  --out-dir /tmp/core2-uiflow2-matrix
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | ESP-IDF image 与 core2 UIFlow2 设备组所需 runtime 均成功构建 |
| transport | `PASS` | 真实 guest SPI3 queue、IRQ、post callback 和 result path 完成 |
| device_response | `PASS` | `TRANS_DONE && TRANS_INTEN` 驱动 SPI line，mapping 重算后 ISR 可达 |
| data_behavior | `PASS` | fixed guest `3/3 PASS`；Core2 UIFlow2 `6/6 PASS`，无 retry |
| visual_or_physical | `NOT RUN` | 未做物理 SPI timing、电气或真机验证 |
| legacy UIFlow | `FAIL` | 最新 legacy runtime 在 display completion 前 reset/停止，仍无应用帧 |

## 证据

- fixed evidence：
  `tests/firmware/core2_spi_irq_remap/evidence-2026-10-28-core2-spi-irq-remap.json`
- pre-fix control：
  `tests/firmware/core2_spi_irq_remap/evidence-2026-10-28-core2-spi-irq-remap-control.json`
- Core2 UIFlow2 group：
  `PASS 6`；每条 attempt 1，retry false
- platform：
  `Ran 1354 tests ... OK (skipped=1)`
- docs contracts：
  `Ran 48 tests ... OK`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot 和
  `git diff --check` 均 PASS

## 验证边界

独立 SPI probe PASS 只说明 pending SPI source remap 和 guest completion
已修复。legacy UIFlow 仍需要解释 display-driver 到达条件和 reset 前启动
phase；不能用本记录关闭 `RUNTIME-03` 或宣称非空应用帧。

## 风险与回滚

本次没有烧录、擦除、写标签或其他不可逆硬件操作。回滚方式是撤回 patch
`0064`；这会恢复旧的 pending mapping 丢失行为，并让独立 SPI probe 再次
callback timeout。
