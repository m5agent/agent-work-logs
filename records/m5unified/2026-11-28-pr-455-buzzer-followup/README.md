# M5Unified #455 评审：Buzzer `isEnabled()` 注释与 `build_test` 等待上限

- 日期：`2026-11-28`
- 结果：`PARTIAL`（`virtual-device validation` + `code-level verification`；
  CoreMatrix PWM 运行时为 `NOT RUN`）
- 工作类型：`pr_review`
- 问题来源：[m5stack/M5Unified#455](https://github.com/m5stack/M5Unified/pull/455)，
  作者 `ainyan03`，英文，OPEN；评审前无评论
- 源码版本：`m5stack/M5Unified` head `b05f46ecaa8913ed4f067e5f5e435189b928d568`，
  base `48799c2a56a6252bb51adf94782658563c25393b`（develop，已合并 #454）
- 环境：macOS arm64；ESP-IDF 6.1（`esp32c61` 构建、`esp32s3` 探针）；`arduino-cli 1.6.0`
  与 `esp32:esp32@3.3.13`；本机 Device Service 的 `cardputer-adv` profile
  （ESP32-S3 虚拟设备）

## 结论

#454 的两条非阻塞建议都已落实，本 PR 没有阻塞问题：`isEnabled()` 注释与 C61 分支的
实际选择顺序一致，`test_buzzer()` 的无界等待已加上限。

一个非阻塞点：在 ESP-IDF 构建（`CONFIG_FREERTOS_HZ=100`）下，`M5.delay(1)` 实际是
`vTaskDelay(1 / 10) = vTaskDelay(0)`，所以等待并不是约 200 ms，而是 200 次
`M5.update()`；虚拟设备实测 200 次循环在 0 ms 内结束、50 ms 的有限音仍在播放，
随后被 `tone(1000)` 覆盖。若希望在正常路径上观察有限音自然结束，可改用
`M5.delay(10)`（一个 tick）并相应减少次数，或直接用 `vTaskDelay(1)`。

## 关键证据

- 构建：IDF 6.1 `esp32c61` 下 `examples/Test/build_test` 构建通过
  （app `0x58290` 字节）；CI 37/37 通过，含 `esp32c61 (IDF 6.1)`、Arduino
  `3.0.7`/`3.2.1`/`3.3.13`/`4.0.0` 矩阵与 SourceCheck。
- 虚拟设备：`cardputer-adv`（`board=24`，`buzzer=1`），用同一段循环的 IDF 探针
  采集到 `loop_i=200 dt_ms=0 playing=1`、`delay20_ms=0`，说明上限生效且不会挂死，
  同时证明 IDF 下的等待没有真实墙钟时长。
- 代码：`M5Unified.inl:1704-1710` 对 `board_M5CoreMatrix` 无条件创建 M5IOE1 并
  `_attachIOE1()`；`Buzzer_Class.inl:34-40` 的 `isEnabled()` 先看 `_ioe1`；
  `Buzzer_Class.inl:57-62, 88` 的 `tone()` 在 `use_pwm` 时提前返回，不经过 Speaker。
  这正是注释所述行为。
- 失败场景：`Buzzer_Class.inl:218-238` 在两次停止写都失败时 `_cutPowerLocked()`
  仍可能留下 `_ioe1_playing=true` 且清空 `_deadline_us`，旧的无界 `while` 会永久自旋；
  200 次上限可以退出。

## 文件

- `report.md`：完整评审报告与源码行号
- `run.json`：结构化记录
- `evidence/pr455.diff`：被评审的 diff
- `evidence/c61-build.txt`：IDF 6.1 esp32c61 构建摘要
- `evidence/idf-probe-serial.txt`：IDF 探针在 cardputer-adv 上的串口全文
- `evidence/build-test-probe-serial.txt`：加了串口打印的 build_test 在 cardputer-adv 上的串口全文
- `evidence/ci.txt`：PR 检查结果

## 未覆盖项

- CoreMatrix 的 IOE1 PWM 运行时时序（本机 Device Service 没有 C61/CoreMatrix profile）；
- 真实硬件的蜂鸣器声音、响度与电气行为；
- 作者 fork 上的实机结果未复现。
