# M5GFX #436: LP I2C 的 ACK 终端 read 后 endTransaction 等待 25 ms

- 日期：`2026-11-19`
- 结果：`REVIEW`（代码级验证；hardware / virtual-device / build 均 `NOT RUN`）
- 工作类型：`issue`
- 条目：[m5stack/M5GFX#436](https://github.com/m5stack/M5GFX/issues/436)
  「LP_I2C ポートで ACK 終端の read の後に endTransaction() が 25 ms 待ち切る
  (ToughC5 のタッチで M5.update() が毎回 37〜80 ms 止まる)」，作者 GOB52，日文，OPEN；
  2026-11-19 处理前 comments 为 0，无 m5agent 回复
- 源码：`m5stack/M5GFX` `develop` @ `44324f34748812ce557e0dea39fb173cf9a73952`
  （与报告中的 `44324f3` 一致）
- 环境：macOS arm64 只读源码检查；本机无 Arduino / ESP-IDF 工具链；
  Device Service 36 个 profile 中没有 ESP32-C5；硬件测试中心 5 个节点（4 个在线）中
  也没有 ESP32-C5

## 结论

报告的原因分析在代码上成立。#423（`cc60eaa`）之后，LP 端口的 read 终端改由控制器
`STOP` + `END` 关闭；如果最后一个字节是 ACK 终端，从机仍驱动 SDA，控制器无法形成
STOP，`TRANS_COMPLETE` 不会到来，`i2c_wait()` 一直等到 `i2c_stall_limit_us`（25 ms），
随后以 `connection_lost` 失败并调用 `i2c_stop()` 恢复。`Touch_CHSC6540` 正好以 ACK 终端
读取点数，且丢弃 `endTransaction()` 的返回值，所以错误不可见、耗时进入 `M5.update()`。

不建议回退 #423。修复方向优先选报告中的案 B：在 LP 的 `endTransaction()` 里，若本次
read 的最后一个字节是 ACK 终端，先在 STOP 前补 1 字节 `READ` + NACK，让从机释放 SDA，
再发控制器 STOP。案 A（只改 CHSC6540 为一次读完并 NACK 终端）只能修一块触摸 IC；
`FT5x06` / `CST816S` 仍有同型 ACK 终端，`GT911` 在 0 点（未触摸）时也会留下 ACK 终端。

## 关键证据

- 源码路径：`src/lgfx/v1/platforms/common.hpp:275` 的 `last_nack = false` 默认值；
  `src/lgfx/v1/touch/Touch_CHSC6540.inl:73` 的 ACK 终端点数读取、`:84` 的返回值丢弃；
  `src/lgfx/v1/platforms/esp32/common.inl:2072` 的 LP `force_stop_read = false`、
  `:2099` 的 25 ms 等待、`:2110` 的 `i2c_stop()` 恢复。
- `git show cc60eaa`：确认 #423 只把「read 终端」从 GPIO `i2c_stop()` 改为控制器
  STOP，25 ms 等待本身是既有路径。
- 触摸驱动分布：`FT5x06:118,127`、`CST816S:208,213` 为 ACK 终端；`GT911:150` 的
  点数读取为 ACK 终端，坐标读取 `:158` 才是 NACK 终端。
- 运行条件：Device Service 36 个 profile 无 ESP32-C5；硬件测试中心 5 个节点无
  ESP32-C5；本机无 Arduino / ESP-IDF 工具链，无法构建最小 sketch 或合并固件。

## 文件

- `report.md`：完整报告（代码路径、回归来源、案 A/B 评估、边界）
- `run.json`：结构化记录
- `evidence/issue-status.txt`：条目状态、版本、评论数
- `evidence/code-facts.txt`：固定 commit 的源码摘录与行号
- `evidence/environment.txt`：设备 profile / 硬件节点 / 工具链盘点（已脱敏）
- `evidence/duplicate-check.txt`：重复条目与修复 PR 检索

## 未覆盖项

- hardware validation：`NOT RUN`。没有 ESP32-C5（ToughC5）实机。
- virtual-device validation：`NOT RUN`。Device Service 没有 C5 profile；现有 QEMU
  profile 不含 C5，无法启动报告中的板型。
- build：`NOT RUN`。本机没有 Arduino / ESP-IDF 工具链，未编译最小 sketch。
- 案 B 的实现、编译与实机确认：`NOT RUN`。报告只给出代码位置与实现方向。
- C6 / P4 的 LP 端口是否出现同一等待：`NOT RUN`。代码路径共用，但没有对应板型的
  触摸配置可供确认。
- 报告中的 ToughC5 实测数据（37〜80 ms、36.5 ms 内訳、NACK 对照）均为作者实机数据，
  本记录没有复测。

## 已发布回复

- 待发布后补充固定链接。
