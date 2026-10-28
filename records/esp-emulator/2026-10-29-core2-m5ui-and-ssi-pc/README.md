# ESP Emulator Core2 M5UI panel DMA 修复与 legacy SSI PC 绑定

- 日期：`2026-10-29`
- 结果：`PASS`（M5UI candidate frame 子问题）/ `PARTIAL`（legacy `RUNTIME-03`）
- 工作类型：`code_change`
- 问题来源：StopWatch、StickS3、Core2 UIFlow2 三设备复测后的剩余问题
- 源码版本：[m5stack-esp-emulator@38760a0f](https://github.com/m5agent/m5stack-esp-emulator/commit/38760a0f968136119fe435b99d031bff611d1406)
- 环境：macOS arm64；QEMU virtual device；UIFlow2 `v2.5.3`；Core2 legacy `UIFlow_Core2 v1.15.4`

## 结论

Core2 M5UI candidate 的全屏刷新条带根因是 classic ESP32 SPI panel 对同一笔
flush 的 DMA descriptor 数据和 CPU data-register 数据发生了二次消费。`0074`
在 DMA 已消费 panel 数据后跳过当前 command 的重复 CPU-register replay，并增加
opt-in RAMWR byte accounting。

同一 hash-pinned candidate 的 RAMWR mismatch 从 `49/54` 降到 `0/54`；
M5Canvas triangle、M5Image scale、M5Spinbox integer/decimal 共 `4/4`
state PASS，triangle/image 两个 frame oracle 从 `FAIL/FAIL` 变为
`FRAME_PASS/FRAME_PASS`。最终虚拟帧 SHA256 为
`5a074d2987258112f79cecc800578df7325e6f35c32ceace859b828c8f942403`。

Core2 legacy 侧，`0073` 将 SSI command 绑定到 issuer CPU/PC：`0x05` 的
`49,961/49,972` 次来自 ROM read-command 区间 `0x4006222c`，`0xBB/64`
的 `49,452/49,783` 次来自应用 segment 5 的 `0x40093b57`。这缩小了
`RUNTIME-03` 的调查范围，但没有解释 normal-WDT 下 startup/APIKEY 前的
完整预算，因此 `RUNTIME-03` 继续 `OPEN`。

## 关键证据

- 修复前 frame：`evidence/frame-pre-fix.png`
- 修复后 frame：`evidence/frame-post-fix.png`
- M5UI/RAMWR/三设备 smoke 摘要：`evidence/m5ui-dma-summary.json`
- SSI issuer PC 与 normal-WDT 摘要：`evidence/ssi-command-pc-summary.json`
- 三设备 system/shared smoke：`evidence/three-board-smoke.json`
- patch：`patches/0001-esp32-ssi-command-pc.patch`、
  `patches/0002-esp32-spi-panel-dma-dedup.patch`
- CI：[40766337332](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40766337332)

## 文件

- `report.md`：根因、修改、验证和边界
- `run.json`：机器可读记录
- `evidence/`：修复前后帧、machine summaries 和三设备 smoke
- `patches/`：QEMU 增量 patch
- `code/`：不适用；测试代码已随源码提交

## 未覆盖项

- legacy Core2 normal-WDT startup、setup/REPL 和非空原厂应用帧仍 `OPEN`；
- 物理 ILI9342 panel、DMA/SPI 实时性、电气、RF 和真机视觉均为 `NOT RUN`；
- stock internal-controller BLE GATT、外部/加密 ESP-NOW 不在本次修改范围；
- 本次证据是 `virtual-device validation`，不是 physical hardware validation。
