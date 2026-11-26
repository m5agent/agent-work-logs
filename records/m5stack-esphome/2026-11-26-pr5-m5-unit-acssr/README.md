# m5stack/esphome#5 Unit ACSSR / DCSSR 组件评审

- 日期：`2026-11-26`
- 结果：`REVIEW`
- 工作类型：`pr_review`
- 问题来源：<https://github.com/m5stack/esphome/pull/5>
- 源码版本：`m5stack/esphome @ d67c91f656fba5333b5f67d237200c244769342b`（PR head），base `m5-dev @ 6c84e04afe0985a73c705094f88b4f773ed4b6e9`
- 环境：macOS arm64；CPython 3.13 + 仓库 requirements（ESPHome 2026.11.0-dev）；ESP-IDF 5.5.6；本机 Device Service 的 `cores3` QEMU profile 与 `dcssr` Unit 模型（PORT.A，0x50）

## 结论

PR 的寄存器映射、组件构建、host 单测与虚拟 CoreS3 + DCSSR 数据面均未发现阻塞问题：
继电器写入、RGB 写入和固件版本读取在 QOM 上均可观测，5 s 的 update 轮询与
10 次重连窗口也能在串口上看到。重启恢复路径仍缺实机确认：QEMU DCSSR 模型不回读
0x10 LED 寄存器，导致 `update()` 在该模型上反复误判“Unit 重启”并重写状态；真实 Unit
固件会把写入字节保存在影子寄存器中，因此这被归为模型缺口而非组件缺陷。

证据等级：`host-level test` + `virtual-device validation`（仅 I2C 寄存器/事务面）+
`code-level verification`。AC 市电、触点闭合、带载、LED 光学和真实 3 s 上电窗口均
`NOT RUN`。

## 关键证据

- Host 单测：`script/cpp_unit_test.py m5_unit_acssr` → 11/11 PASS
- 组件构建：`script/test_build_components.py -c m5_unit_acssr -t esp32-idf` → 1 passed
- 配置校验：`python -m esphome config` → `Configuration is valid!`
- 虚拟设备：CoreS3 QEMU + `dcssr`（PORT.A，0x50），固件 `dc08a5b0…`；QOM 最终
  `relay-level=false`、`relay-transitions=2`、`led-rgb=0xFF8000`、`fw-version=1`、
  `i2c-address=80`、`transactions=233`；UART0 出现 `setup() finished successfully!`、
  `Firmware version: 1`、`Turning ON`/`Turning OFF`
- 无 Unit 会话：重连窗口结束后仅一条 `Unit not answering at 0x50…` 警告，之后
  `update()` 仍以 5 s 间隔继续探测 0x50
- 代码级：0x50 / 0x00 / 0x10 / 0xFE 与 `M5Unit-ACSSR@2996144` 一致；3 s 延迟与
  `initial_control()` 一致（`M5Unit-ACSSR-Internal-FW@45e6298`）

## 文件

- `report.md`：完整评审报告、命令与边界
- `run.json`：结构化记录
- `evidence/`：PR 元数据、协议核对、host 单测、组件构建、配置校验、两份串口日志、
  Unit QOM、probe YAML、模型缺口说明
- `patches/`：不适用（只读评审）
- `code/`：不适用（probe YAML 在 `evidence/08-cores3-dcssr-probe.yaml`）

## 未覆盖项

- 无 ACSSR/DCSSR 实机：继电器触点、AC/DC 带载、隔离、寿命、LED 光学与真实上电
  3 s 窗口均 `NOT RUN`；QEMU 模型只是寄存器/事务观测，不代表市电开关能力。
- QEMU DCSSR 不回读 0x10 LED，`update()` 的重启恢复判据在虚拟设备上无法公平验证；
  需要实机拔插 Unit 电源或按复位键后的串口日志确认。
- Unit 的 Button 与 Modbus/RS485 模式、0x20 改址均未覆盖。
- 继电器读回是 Unit 固件影子字节，不是触点反馈；不能据此断言 SSR 已闭合。
