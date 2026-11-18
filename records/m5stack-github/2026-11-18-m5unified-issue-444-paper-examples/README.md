# m5stack/M5Unified #444 — M5Paper examples still route to M5EPD

- 日期：`2026-11-18`
- 结果：`PARTIAL`（`code-level verification`；构建与实机 `NOT RUN`）
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/M5Unified/issues/444
- 源码版本：`m5stack/M5Unified @ 96576a14247ddc935149145aa6b51943464120f1`（0.3.0）；`m5stack/M5GFX @ 28d47949bdc84f30881623476f555398e2194313`
- 环境：macOS arm64；无 M5Paper 实机；本机虚拟设备目录无 M5Paper profile；无 Arduino-ESP32 工具链

## 结论

作者指出的文档链路问题成立：`docs.m5stack.com/en/core/Paper` 的 Arduino 资源列表仍然列出
已归档的 M5EPD 库和三个 M5EPD 示例仓库。但 M5Unified 本身已经支持 M5Paper：板型出现在
支持列表，按键、总线、电源按板型处理，显示/触摸由 M5GFX 的 `Panel_IT8951` + `Touch_GT911`
提供，540x960 `grayscale_8bit`，EPD 刷新模式通过 `setEpdMode()` 暴露。

因此这是「缺 Paper 专用示例 + 文档链接未迁移」，不是驱动缺失。仓库当前 18 个 sketch 全部是
跨板示例，`examples/Basic/HowToUse` 只是把 `board_M5Paper` 映射成名字 "Paper"；ArduinoBuild
CI 矩阵也只编译 `m5stack_core` / `m5stack_cores3` 两个 M5Stack 板，新增 Paper 示例不会被 CI 覆盖。

## 关键证据

- 支持范围：`evidence/m5unified-paper-support.txt`（README.md:60、`src/M5Unified.inl:153/1839/2988`）。
- 面板与触摸：`evidence/m5gfx-paper-panel.txt`（`construct_paper()` 用 `Panel_IT8951` + `Touch_GT911`；
  `M5GFX.cpp:1105-1113` 设 540x960 `grayscale_8bit`；`Panel_IT8951.inl:116` `_auto_display = true`；
  `Panel.hpp:88` `endWrite()` 触发 `display()`；`LGFXBase.hpp:1440` `setEpdMode()`）。
- 示例覆盖：`evidence/examples-tree.txt`，58 条 `examples/` 路径、18 个 `.ino`，无 Paper 专用示例。
- 文档：`evidence/docs-paper-page.txt` 为 2026-11-18 抓取的线上页面，产品页仍渲染
  "Paper v1.1 Arduino M5EPD Driver Library" 及 M5EPD_Todo / M5EPD_Calculator / M5EPD_TTFExample；
  Paper Arduino 快速上手页已经安装 M5Unified/M5GFX，并把 M5EPD 示例标为 "no longer maintained"。
- 废弃状态：`evidence/m5epd-repo.json`（`archived: true`）与 `evidence/m5epd-readme-head.txt`
  （README 首行 "🚫 Deprecated — Use M5GFX & M5Unified"）。
- 运行时不可用原因：`evidence/local-virtual-paper-profiles.txt`（本机 4 个 e-paper profile 全是
  ESP32-S3 + 其它面板）与 `evidence/esp-emulator-esp32-models.txt`（esp32-lx6 无 Paper 机型）。
- 构建尝试：`evidence/build-attempt.txt`，`arduino-cli core install esp32:esp32@3.3.12` 在解压
  `esp-x32` 时磁盘空间不足失败，未得到任何编译结论。

## 文件

- `report.md`：完整报告（方法、证据、回复正文、未覆盖项）
- `run.json`：结构化记录
- `evidence/`：issue JSON、源码摘录、线上文档摘录、虚拟设备口径、构建尝试记录
- `code/PaperHello/`：最小 Paper sketch 与构建命令（本轮未编译）

## 未覆盖项

- 未编译：本机没有 Arduino-ESP32 工具链，安装因磁盘空间不足中断（`NOT RUN`）。
- 未烧录、未在 M5Paper（ESP32-D0WDQ6-V3 + IT8951）实机观察画面、触摸、EPD 刷新时序（`NOT RUN`）。
- 无虚拟设备验证：本机设备目录没有 M5Paper profile，e-paper profile 均为 ESP32-S3 + 其它面板，
  不能代表 IT8951 路径；esp-emulator 的 esp32-lx6 也没有 Paper 机型。
- 未验证 Paper 专用示例是否会被维护者接受、以及是否应同时把 `m5stack:esp32:m5stack_paper` 加入 CI 矩阵。
