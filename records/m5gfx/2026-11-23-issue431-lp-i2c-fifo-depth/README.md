# M5GFX #431: ESP-IDF 6.x で LP I2C の FIFO 深さを 32 と扱い、16 バイト超の write が壊れる

- 日期：`2026-11-23`
- 结果：`REVIEW`（code-level verification；hardware / virtual-device 均 `NOT RUN`）
- 工作类型：`issue`（只读分诊与单条回复）
- 条目：[m5stack/M5GFX#431](https://github.com/m5stack/M5GFX/issues/431)，作者 GOB52，日文，OPEN；
  处理前 comments 为 0，无 m5agent 回复。标题「ESP-IDF 6.0 以降、LP I2C ポートの FIFO の深さを
  32 と扱い、16 バイトを超える write が壊れる」
- 源码：`m5stack/M5GFX` develop `43a87193f898f998edf79c5fb99b166d11ee1eaf`；
  报告时的 develop `452c15bc982af0b54acf567a79e7eb6066ace9e5`；
  修正 PR #432 的 merge commit `e88846e781091ff489de3afb5770f7333af1d864`；
  后续守卫 PR #433 的 merge commit `1d4f3f9`
- 环境：macOS arm64；本地 ESP-IDF `v6.1` 源码树（头文件对照，未构建）；
  本地 Device Service 36 个 profile 无 ESP32-C5，tab5（P4）在服务侧停用，esp-emulator 无 LP I2C 控制器模型；
  无 ESP32-C5 / C6 / P4 实机
- 关联：#432（同一作者的修正 PR，2026-11-18 merge）、#433（深度宏未知时 `#error`）、
  本 agent 2026-11-18 对 #432 / #433 的日文评审；LP I2C 系列总账见实体
  `m5gfx_c5_lpi2c 读取分诊`

## 结论

报告成立，且已在 develop 修正；本次分诊没有发现需要追加代码改动的问题。

- ESP-IDF 6.x 删除了 `SOC_I2C_FIFO_LEN` / `SOC_LP_I2C_FIFO_LEN`（本机 v6.1 的
  `components/soc` 与 `components/esp_hal_i2c` 全树 0 命中），深度改由
  `hal/i2c_ll.h` 的 `I2C_LL_FIFO_LEN` / `I2C_LL_LP_FIFO_LEN` 提供。
- `452c15b` 的 `getFifoLen()` 只判断 `SOC_*`，在 6.x 上 LP 端口与 ESP32-C2 的 HP 端口
  都落到 `return 32`。修正 `e88846e` 增加 `I2C_LL_*` 分支，当前 develop 的
  `common.inl:1465-1484` 已同时覆盖 LP 16 / HP 32 / C2 16；`#433` 的 `#error` 守卫也在
  （`:1471-1473`）。
- 修正**不在任何 tag 中**：`git tag --contains e88846e` 为空，最新发布 `0.3.0`
  （2026-11-06）源码里 `I2C_LL_LP_FIFO_LEN` 命中 0 次。因此 0.3.0 + ESP-IDF 6.x 的用户
  仍会遇到该问题，需等下一个发布。

## 关键证据

主机把两个版本的 `isLpPort()` / `getFifoLen()` 原文抽出，按 ESP-IDF v6.1 各芯片真实宏值编译执行：

| 配置（端口 0..3） | `452c15b`（报告时） | develop `43a8719` |
| --- | --- | --- |
| ESP32-C5（LP = port1） | `32 32 32 32` | `32 16 16 16` |
| ESP32-C6（LP = port1） | `32 32 32 32` | `32 16 16 16` |
| ESP32-P4（LP = port2） | `32 32 32 32` | `32 32 16 16` |
| ESP32-C2（HP 深度 16） | `32 …` | `16 …` |
| ESP32（5.x 宏集与 6.x 宏集） | `32 …` | `32 …` 不变 |

- `writeBytes()` 的首块为 `((length - 1) % txfifo_limit) + 1`（`common.inl:2763`）。
  limit=32 时 17 / 18 / 24 字节都是单块 17 / 18 / 24；limit=16 时最大块恒为 16
  （17 → 1+16，18 → 2+16，97 → 7 块）。
- 合成「LP 端口但两个深度宏都未定义」：`452c15b` 静默返回 32，develop 按 `#error` 中止。

## 文件

- `report.md`：完整报告（代码事实、头文件矩阵、主机验证、发布状态、未覆盖项）
- `run.json`：结构化记录
- `evidence/issue.json`：条目状态（OPEN、0 条评论、作者、时间）
- `evidence/git.txt`：develop、tag 包含关系、0.3.0 是否含修正
- `evidence/idf61-headers.txt`：ESP-IDF v6.1 各芯片 `soc_caps.h` / `hal/i2c_ll.h` 摘录
- `evidence/idf554-c5-headers.txt`：ESP-IDF v5.5.4 C5 的 `SOC_*` 深度（对照）
- `evidence/code-develop.txt` / `evidence/code-base.txt`：两版 `getFifoLen()` 原文
- `evidence/code-writebytes.txt`：`writeBytes()` 分块代码
- `evidence/pr432.diff` / `evidence/pr433.diff`：修正与守卫的差分
- `evidence/fifo-harness.txt` / `evidence/fifo-harness-unknown-macro.txt`：主机验证输出
- `evidence/device-profiles.txt`：Device Service 36 个 profile 与 C5 缺失
- `evidence/emulator.txt`：esp-emulator 无 LP I2C 模型、经典 I2C FIFO 为 32
- `code/`：可重跑的主机验证（抽函数 + 编译执行）

## 未覆盖项

- hardware validation：`NOT RUN`。本机无 ESP32-C5 / C6 / P4 实机，报告中的 NFC-V 与
  17〜97 字节实测均为作者在 #432 的数据，本记录未复测。
- virtual-device validation：`NOT RUN`。无 C5 profile；C6（nanoc6 / nesso-n1）虽是
  ESP32-C6，但 esp-emulator 无 LP I2C 控制器模型；tab5（P4）在服务侧停用（`tab5_enabled=false`），
  且其 I2C 只是静态寄存器探针，不建模 FIFO 写入深度。因此 16 字节超限的静默损坏无法在虚拟设备上观测。
- ESP-IDF 6.1 的真实固件构建：`NOT RUN`。头文件取自本地 v6.1 源码树，未做 `idf.py build`；
  #432 / #433 的 CI（含 6.0.2 的 C6 / P4）为上游结果，本记录未复跑。
- #432 评论中「C5/C6 从 18 字节、P4 从 17 字节开始损坏」与本文「17〜32」相差 1 字节的现象
  未解释；不影响修正结论，本记录不展开。

## 已发布回复

- <https://github.com/m5stack/M5GFX/issues/431#issuecomment-7093871078>
  （1 条，日文；issue 保持 OPEN，未 close、未 push、未改他人仓库）
