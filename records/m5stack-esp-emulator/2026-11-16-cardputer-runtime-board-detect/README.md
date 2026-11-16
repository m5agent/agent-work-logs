# Cardputer 运行时板型探测回退与两日审核归因

- 日期：`2026-11-16`
- 结果：`PARTIAL`
- 工作类型：`service_debug`
- 问题来源：模拟器固件审核批次（近两日 `SIM_PARTIAL` 任务）与 issue
  [#230](https://github.com/m5agent/m5stack-esp-emulator/issues/230)
- 源码版本：`m5agent/m5stack-esp-emulator @ 55e5763e`；运行证据来自 esp-emu `0.50.0`
- 环境：macOS arm64；Device Service 原生 QEMU（ESP32-S3 / ESP32-P4）；审查服务只读归因；
  未使用真机

## 结论

对近两日（2026-11-14 00:00 至 2026-11-16 09:20 +08:00）42 条固件审核任务逐条读取
`review-report.json`、串口、帧、`observation.json`、`session.json`、交互与网络证据后：

- 27 条 `SIM_PARTIAL` 中，**6 条可归因到已确认或本次新开的模拟器缺陷**：
  - 4 条 Cardputer / Cardputer-ADV 运行时板型探测回退为 `board_M5StampS3`（136），
    本次新开 [#230](https://github.com/m5agent/m5stack-esp-emulator/issues/230)；
  - 1 条 M5Apps 卡在 ROM EXTMEM occupy（既有
    [#229](https://github.com/m5agent/m5stack-esp-emulator/issues/229)）；
  - 1 条 CarPlay-Tab5 板型探测缺 ST7123/GT911（既有
    [#227](https://github.com/m5agent/m5stack-esp-emulator/issues/227)）。
- 1 条 M5TabOS 在 Tab5 上 `E_SIM_MODEL_GAP`（串口 `Core dump` 后 `SW_CPU_RESET` 循环）；
  Tab5 外设覆盖本来就不完整，无法把卡点收敛到单个模型，登记为未定位的模型缺口，未新开 issue。
- 13 条属于**审查服务 / 取证链路 / 设备映射 / 镜像静态判定**，不是模拟器缺陷；
  其中 4 条是 `DEVICE_MAP` 缺 `ATOM_S3`、`PAPER_S3`、`PAPER_DIY`（模拟器已有对应
  `atoms3`、`papers3`、`paperdiy` 档案），5 条是 Tab5 取帧要求匹配 ELF 而审查链路只有
  BIN，2 条是网络验证路径未启用，1 条是 StickC-Plus2 合并镜像静态判定误放行
  （既有 [#228](https://github.com/m5agent/m5stack-esp-emulator/issues/228)），
  1 条是 app-only 启动上下文缺失。
- 4 条依赖 DUT 之外的外设：ZILLASTICK 需要 CC1101 RF Pack，vinylM5Dial 需要
  Unit AudioPlayer；虚拟设备未装对应夹具，应用停在初始化/等待，不认定为模拟器模型缺陷。
- 3 条是输入/声明解析或应用自身交互面：AD Arcade 的 “tap” 被当作触摸声明，
  alpha-buddy 与 OnePork 的 A/B 只响应其中一键，不足以归因模拟器。
- 其余 12 条为 `SIM_VERIFIED`，3 条为静态 `FAIL`（OnePork、Tab5 ADB × 2）。

因此“近两日大多数是模拟器 bug”不成立；多数是取证口径和审查服务配置问题，真正可复现的
模拟器模型缺陷集中在 Cardputer 运行时板型探测与既有 #229/#227。

本记录只覆盖 virtual-device 归因与 Cardputer 模型缺口，不包含真机结论。

## 关键证据

- 4 个 Cardputer 固件（Tiny Journal、MacroCard、Cardputer ADV Frequency、CapLab）
  串口均打印
  `[error] Keyboard: Unsupported board type: 136`，60 s 观察窗口内帧始终为 174 B 全黑
  （240×135）。
- M5GFX 板型枚举：`board_M5Cardputer=14`、`board_M5CardputerADV=24`、
  `board_M5StampS3=136`；Cardputer 探测器使用 GPIO 位翻转的 ST7789 RDDID 探测
  （命令 `0x04`，期望 `0x81`），而 esp-emu 的 Cardputer 面板只在 GP-SPI 寄存器读路径
  返回该 ID。
- 近两日 26 条 `SIM_PARTIAL` 的逐条归因见
  [evidence/attribution-summary.json](evidence/attribution-summary.json)。
- 4 个 Cardputer 任务的串口与帧摘要见
  [evidence/cardputer-serial-frames.json](evidence/cardputer-serial-frames.json)。

## 文件

- `report.md`：完整归因报告（分组、逐条依据、未开单理由）
- `run.json`：结构化记录
- `evidence/attribution-summary.json`：26 条 `SIM_PARTIAL` 的脱敏归因表
- `evidence/cardputer-serial-frames.json`：4 个 Cardputer 任务的串口/帧证据摘要

## 未覆盖项

- 4 个 Cardputer BIN 在真实 Cardputer / Cardputer-ADV 上的复跑：`NOT RUN`。
- Cardputer 面板、键盘、SD、音频、USB、BLE、RF cap 的完整功能：`NOT RUN`。
- Tab5 的 4 个非 CarPlay 固件在真机或带 ELF 的取帧路径上的首帧：`NOT RUN`；
  审查链路的 409 已定位为 `screenshot_requires_matching_elf`，不是本轮模拟器归因对象。
- ZILLASTICK 的 CC1101 RF Pack、vinylM5Dial 的 Unit AudioPlayer 数据面：`NOT RUN`。
- 审查服务的 `DEVICE_MAP`、Tab5 ELF 取帧与触摸声明已在
  [2026-11-16 修复记录](../../firmware-review-service/2026-11-16-device-map-tab5-elf-touch-fix/)
  中修复并验证；网络路径、app-only 上下文与 StickC-Plus2 静态判定仍未改。
