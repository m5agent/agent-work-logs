# M5GFX #438 Core2 AXP192 + ILI9342E 复位后初始化落在 120 ms 重载窗口内

- 日期：`2026-11-22`
- 结果：`REVIEW`（code-level verification；硬件与虚拟设备均 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：<https://github.com/m5stack/M5GFX/issues/438>
- 源码版本：`m5stack/M5GFX @ 28d47949bdc84f30881623476f555398e2194313`（v0.3.0）
- 环境：macOS arm64 只读源码审阅；本机 Device Service（36 个 profile，含 `core2`）；
  硬件测试中心 5 个节点（4 个在线，均为 `matrix` / `profile=unknown`，无 Core2）；
  本机无 Arduino/ESP-IDF 工具链，容器运行时当前无法新建容器

## 结论

作者的结论在 0.3.0 代码里成立：Core2/Tough 检测路径对 ILI9342 做一次 LCD 复位后，
`identify_panel_variant(..., 120, ...)` 只是"最多等 120 ms"，面板一旦回读键值就立即返回；
随后初始化列表紧接着发出，落在 ILI9342E 复位后最长 120 ms 的 NV 重载窗口内。
`Panel_ILI9342E` 初始化列表里现有的 `CMD_INIT_DELAY 120` 挂在 `SLPOUT` **之后**，
而且 `DISPON` 还在 `SLPOUT` 之前，所以它对窗口没有任何保护作用；
`PR #300` 描述里"which also keeps the init sequence out of the reload window"对 E 不成立。

## 关键证据

- **代码路径**：`src/board_detect/m5/esp32_d0wdq6.inl:60` 的 `i2c_reset(1, 10)`（1 ms 拉低、
  释放后 10 ms）、`:508` 的复位后探测、`src/board_detect/m5/board_registry.inl:170-183`
  的 1 ms 轮询提前返回、`src/M5GFX.cpp:997-1002` 明确不再二次复位、
  `src/lgfx/v1/panel/Panel_ILI9342.hpp:86-101` 的 E 初始化顺序。
- **硬件**：`NOT RUN`，无 Core2 / ILI9342E 或同路径 AXP192 板可用。
- **虚拟设备**：`NOT RUN`。`core2` profile 存在（`m5core2`、显示 sink `ILI9342C / ILI9342E`），
  但模拟器 ILI9342 sink（`hw/m5stopwatch/m5_spi_panel.c`）只把 Sleep In/Out 当作
  `0x10`/`0x11` 置位的布尔量，没有复位后 NV 重载时间窗、也没有复位回 Sleep In 的转移，
  交替黑屏在该模型里不可表达；同时本机没有可用的 M5GFX 构建链（详见 report 第 6 节）。

## 文件

- `report.md`：完整报告（代码链、修复位置、边界）
- `run.json`：结构化记录
- `evidence/code-snippets.md`：固定 commit 的代码片段与行号
- `evidence/device-profiles.json`：Device Service 中 Core2 profile 字段与硬件节点概况
- `patches/`：不适用（只读分诊，未提交补丁）
- `code/`：不适用

## 未覆盖项

- 物理 Core2（AXP192）+ ILI9342E 的复位时序：`NOT RUN`。
- Core2 v1.1（AXP2101）与 Tough：作者未测，本次也未评估。
- 与 0.2.34 的逐行差异：只核对了 0.3.0（作者已声明 0.3.0 同形）。
- 修复补丁：未实现、未编译、未验证。
