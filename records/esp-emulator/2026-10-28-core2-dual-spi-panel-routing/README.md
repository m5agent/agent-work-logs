# ESP Emulator Core2 legacy dual-SPI panel routing

- 日期：`2026-10-28`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：Core2 legacy UIFlow 黑帧与 `RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator @ 5abfeac88029f549ff496a6397b6dc2baffa3e69`
- 环境：Core2 `UIFlow_Core2 v1.15.4`，QEMU `m5core2`，Device Service
  `runtime=qemu-wifi` / `core2-openmac`

## 结论

公开 legacy UIFlow 的 `display.TFT` 使用 classic ESP32 HSPI/SPI2，而
UIFlow2 使用 VSPI/SPI3。旧 `m5core2` 板级模型只把 panel sink 接到
SPI3，因此 legacy LCD DMA 写到了没有面板的控制器。`0068` 将同一个面板
对象同时接到 SPI2/SPI3 后，同一 `m5stack`/`lcd` 绘制路径从全黑变为
`1422` 个非黑像素。

该修复关闭面板控制器路由子问题；原厂 startup UI、完整应用帧和
normal-WDT 仍未通过，所以 `RUNTIME-03` 继续保持 `OPEN`。

## 关键证据

- 负控：SPI3-only 下 panel DMA `0` 次，非面板控制器 DMA `412` 次。
- 修复后：`runtime=qemu-wifi`、WDT-off 120 秒诊断，frame
  `320x240`、`1422` nonblack pixels、`2` colors。
- Serial：`652` bytes，包含原 boot、probe draw 完成 marker。
- Frame SHA256：`55249d07…`。
- QEMU：`6ff2aca0…`。
- 平台测试：`1363` 项通过，`1` skip。
- CI：[`40701604803`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40701604803)
  两个 job 均通过。

## 文件

- `report.md`：根因、控制、修复与边界。
- `run.json`：机器可读记录。
- `patches/0068-core2-dual-spi-panel-routing.patch`：QEMU 板级修复。
- `evidence/summary.json`：脱敏后的验证摘要。

## 未覆盖项

- 原厂 startup UI 仍没有完成画面；
- normal-WDT 仍触发 TG0 reset；
- probe 修改了 `/flash/boot.py` 并停留在绘制循环；
- 物理面板、SPI 信号完整性、亮度、触控和时序均为 `NOT RUN`。
