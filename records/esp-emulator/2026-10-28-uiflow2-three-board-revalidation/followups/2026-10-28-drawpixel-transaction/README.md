# Display.drawPixel framebuffer transaction 三设备复验

- 日期：`2026-10-28`
- 结果：`PASS`（限定 hash-pinned 候选固件、virtual-device validation）
- 工作类型：`code_change` + `virtual_device_validation`
- 源码版本：[`m5agent/m5stack-esp-emulator@37d304d1`](https://github.com/m5agent/m5stack-esp-emulator/commit/37d304d1)
- 环境：macOS arm64；matching UIFlow2 builds；QEMU `21b7e34c…`

## 结论

此前 StopWatch `drawPixel` 失败被归因于 CO5300 单像素/偶数窗口限制，该判断
已由同源 framebuffer 路径退役。实际根因是 Python binding 直接调用
`drawPixel()`，没有 `startWrite/endWrite`；StopWatch 的 framebuffer panel
只在 `endWrite()` 的 auto-display 路径 flush，因此 standalone 像素从未提交。

`0024` 增加嵌套安全的 `startWrite/endWrite`。StopWatch preimage 在“先显式
事务、后 standalone 像素”的程序中只显示事务像素；StopWatch、StickS3、Core2
候选均显示 standalone 奇/偶像素并保留相邻背景。

## 关键证据

- StopWatch preimage：`FAIL`
- StopWatch candidate：`FRAME_PASS`
- StickS3 candidate：`FRAME_PASS`
- Core2 candidate：`FRAME_PASS`
- 显式外层事务和内嵌 standalone 调用同时通过
- 完整平台回归 `1347` 项 `OK`、`1` 项 skip

## 文件

- `report.md`：根因、固件、像素和边界
- `run.json`：机器可读记录
- `evidence/results.json`：三台固件/frame/hash
- `evidence/regression-summary.txt`：回归与清理

## 未覆盖项

- incremental application relink，不是冷构建。
- 物理屏幕、功耗和长期 framebuffer DMA soak 为 `NOT RUN`。
