# C6 软件复位 Flash/PMP 修复报告

## 背景

原 18 样本公开固件矩阵把 Nesso N1 Meshtastic 的
`LP_SW_HPSYS` 后 `chip id 12/预期 13` 归为 `runtime_model_gap`。本轮从
ROM/Flash 数据面继续定位，而不是假设 eFuse 或 chip-id 寄存器损坏。

## 根因

### 1. Flash 地址宽度

Nesso N1 使用 16 MiB ISSI Flash。C6 读路径需要四字节地址配置，但
`0x02` Page Program 和 `0x20` Sector Erase 仍使用三字节 address。
原模型把 `four_bytes_address_mode` 全局应用到所有命令：

```text
guest page-program address: 30 00 00
first data byte:            01
model four-byte parse:      address 0x000001, data starts one byte late
```

因此 core dump 对 `0x300000` 的写入落到了 `0x000001` 附近，并把 C6
secondary bootloader 头替换成另一个 chip id `0x0c` 的 image header。
下一次 ROM 只是如实报告 Flash 中读到的错误 chip id。

### 2. PMP reset

Flash 写地址修正后，ROM 能通过 chip-id 检查，但第二次 boot 在
`0x50002000` 发生 Store/AMO access fault。PMP 状态显示上一轮的
`0x50002000..0x5000203f` read-only range 仍存在；通用 RISC-V reset 只
unlock entry，没有清除 address/permission。C6 reset 需要恢复完整 reset
可见的 PMP 状态。

## 修复

- 保留 16 MiB 读路径的四字节地址模式；
- legacy PP/erase opcodes 固定使用三字节 address；
- 显式四字节 PP/erase opcodes 继续使用四字节 address；
- C6 reset 后清空 PMP table、`mseccfg` 和 TLB。

相关源码：

- `hw/block/m25p80.c`；
- `hw/riscv/esp32c6.c`；
- `target/riscv/esp_cpu.c`；
- `patches/qemu-esp32c6-uiflow2-adapters/0001-qemu-c6-m5stack-uiflow2-adapters.patch`；
- `patches/qemu-esp32c6-uiflow2-adapters/0006-espressif-riscv-reset-pmp.patch`。

## 执行与结果

### 修复前

```text
rst:0x3 (LP_SW_HPSYS),boot:0x8 (SPI_FAST_FLASH_BOOT)
Invalid chip id. Expected 13 read 12. Bootloader for wrong chip?
```

### 修复后

```text
page-program intent: 0x300000
page-program intent: 0x900000
LP_SW_HPSYS -> ROM boot
Invalid chip id: absent
Device Service status: PARTIAL
status_reason: fatal_after_application_frame
runtime_model_gaps: []
```

官方回归：

```text
Nesso N1 peripheral matrix: 5/5 PASS, no retry
NanoC6 board probe: PASS
Local platform tests: 317/317 PASS
Node tests: 2/2 PASS
GitHub Actions: platform-contracts PASS
GitHub Actions: network-namespace-policy PASS
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU rebuild；patch apply check；平台测试 |
| transport | `PASS` | 真实 SPI flash command/address trace |
| device_response | `PASS` | `LP_SW_HPSYS` 后 ROM 接受 bootloader 并进入 application |
| data_behavior | `PASS` | core dump 写目标保持 `0x300000/0x900000...`，offset 0 header 不变 |
| firmware_full_function | `PARTIAL` | 独立 Instruction access fault，重启循环 |
| visual_or_physical | `NOT RUN` | 未做真机/RF/电气测量 |
| delivery | `PASS` | 源码、patches、evidence、CI 和工作记录 |

## 边界

- 本记录关闭 `RUNTIME-01`，不关闭 Meshtastic 的完整功能；
- 该样本仍触发独立 Instruction access fault，当前无法仅凭证据归因为
  固件或新的模型缺陷；
- C6 Zigbee/802.15.4 `RUNTIME-02` 仍为 `OPEN`；
- 没有验证全部 Flash opcode、全部 reset cause 或真机行为。

## 风险与回滚

回滚源码提交 `58b7c14538f9407e4ffaecccd98825619ddd0bd6` 会恢复错误的全局
四字节写擦解析和旧 PMP reset 行为，不建议在 C6 16 MiB 路径回滚。
未修改或擦除物理设备。
