# M5GFX #440: wait for the panel reload after the Core2 / Tough LCD reset

- 日期：`2026-11-23`
- 结果：`REVIEW`（virtual-device validation 仅证明 Core2 路径不回归；hardware `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5GFX#440](https://github.com/m5stack/M5GFX/pull/440)，作者 ainyan03，英文，OPEN；
  评审前 comments / reviews 均为 0，无 m5agent 回复
- 源码：PR head `81642aef6a6571330689d581005b94286955de3b`
  （base `43a87193f898f998edf79c5fb99b166d11ee1eaf` = develop tip；9 files，+114 / -8）
- 对应 issue：[#438](https://github.com/m5stack/M5GFX/issues/438)（svengrun，Core2 + ILI9342E
  隔次复位黑屏；m5agent 已在 issue 下做过 code-level 归因）
- 环境：macOS arm64 + ESP-IDF v6.1 + 本机 Device Service 的 `core2`
  （`qemu-esp32lx6` / `m5core2` / ILI9342C-E 320x240 / simulated / screenshot）

## 结论

没有发现需要阻止合并的问题。实现与 #438 的根因和作者自己的硬件测量一致：

- `reset_panel_reload` 只加在 Core2 与 Tough 的 `i2c_reset(1, 10)` 上；
  `description_valid()` 同时限制它只能用于完整 `i2c_regs` 复位，不能和
  `reset_hold_when_skipped` 组合。
- 复位前用 RDDPM（0Ah）读一次 Sleep In：`(b & 0x18) == 0x08`（Normal Mode On，
  Sleep Out 为 0）。只有“第一次复位前就读到 Sleep In”才跳过等待；一旦尝试过该复位，
  之后的读数不再采信（正在 reload 的 panel 也会读成 Sleep In）。
- 复位释放后把 deadline 设为 `millis() + 122`，真正等待放在 panel init 之前
  （`M5GFX.cpp:925` / `:1039` → `_init_adopted_panel`），因此检测和 NVS 已花掉的时间
  计入 122 ms，不会叠加。冷启动 / 本来就在 Sleep In 的启动保持原时长。

本机虚拟设备验证覆盖的是 **不回归**：PR 固件在 Core2 profile 上正常识别 `board=2`、
初始化成功、渲染出预期画面，320x240 截图与 base 构建逐字节相同（同一 sha256），
`display.init()` 耗时 328333 µs（base 328330 µs）。emulator 的 ILI9342 sink 不实现
RDDPM 读和 120 ms reload，且复位后的按键探测在模型上必定跑满 120 ms，正好吃掉 122 ms
deadline，所以 **无法** 在这个模型上复现“隔次黑屏已被修复”，也无法观察到新增等待。

## 关键证据

- `evidence/pr440.diff`：完整 PR diff（9 files）。
- `evidence/code-facts.txt`：行号级代码路径、状态机、调用点与测试覆盖。
- `evidence/host-tests.txt`：本机 `test/board_detect/run.sh`，34 个 C++ 测试程序全部通过
  （含新增 `core_panel_sleep_in`）。
- `evidence/ci-status.txt`：上游 40 项检查全 pass（Arduino 2.0.17–4.0.0、ESP-IDF 5.1.6/5.4.3/6.0.2、
  catalog / host 等）。
- `evidence/build-info.txt`：两次固件构建、合并、上传、会话与结果；含 BIN / stored firmware sha256。
- `evidence/serial-pr.txt` / `serial-base.txt`：两条启动串口关键行。
- `evidence/frame-pr440.png` / `frame-base.png`：320x240 截图，sha256 相同
  `22fe80fc…ab3356`。
- `evidence/harness-main.diff`：仅为测量而改的 example `main.cpp`（不改库源码）。
- `evidence/environment.txt`：Device Service profile、emulator panel 模型缺口（patch 行号）、
  本机无 node/npm 的工具链缺口。

## 文件

- `report.md`：完整报告（现象、实现核对、验证、未覆盖项与风险）
- `run.json`：结构化记录
- `evidence/`：上列原始证据

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 Core2 / Tough 实物；#438 的复现与 PR 的四板
  测量表都是作者侧证据（PR 正文）。
- 虚拟设备无法验证修复本身：模型没有 ILI9342 寄存器 reload 窗口、没有 reset→Sleep In 转换、
  没有 RDDPM 命令读，SPI 读恒为 `0x7f`；复位后按键探测固定跑满 120 ms，122 ms 等待不会触发。
- `extras/board_spec` 的 `npm test` / `npm run check`：本机无 node/npm，未跑；由上游 CI 覆盖。
- 无 EN/RST 复位重复、无 Sleep In 起始、无触摸/SD/背光回归；每次构建只跑了 1 次上电启动。
