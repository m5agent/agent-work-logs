# ESP Emulator Host Allowlist Fixture 与文档对账

- 日期：`2026-10-23`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户要求完整整理 ESP Emulator 代码、文档、当前工作和待办
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`dd705e8b8dfdb3bab927e9f4d1a7561a684466bc`
- 基线版本：`4dea5236b21d2165e70d34fc0bae70fd8a75a540`
- 环境：macOS Apple Silicon；Python 3；现有启用了 M5Stack 板级模型的 QEMU

## 结论

完成一次代码、测试、状态、Backlog 和专项测试文档的交叉对账：

- Device Service 契约升级到 `1.8.0`，新增受控 HTTP gateway 的 Host
  allowlist 参数和 profile 能力检查；
- 新增 TLS/Host allowlist fixture、测试 CA、允许/拒绝日志和 pcap 断言；
- 修正 Core2 native-VHCI、StickS3 UI、Core2 OpenMAC 重试策略等已经过期的
  README；
- 平台测试 `223/223` PASS，catalog/coverage/profile 校验 PASS；
- TLS fixture 实际执行结果为 `FAIL`：guest 完成 WiFi/DHCP 后停在
  `ssl.SSLContext` 创建，QEMU 同时报告 ESP32-S3 AES/GDMA read error。

因此本轮代码/文档一致性是 `PASS`，Host allowlist 基础设施是 `PARTIAL`，
TLS 数据面是 `FAIL`。没有把 Host 层过滤描述成任意公网 destination
allowlist，也没有把 TLS fixture 描述为通过。

## 关键证据

- 平台测试：`223/223` PASS；
- runtime coverage、peripheral catalog、QEMU profiles：PASS；
- 文档索引、相对链接、动态测试计数、API 版本和旧陈述检查：PASS；
- TLS fixture：WiFi/DHCP 和 pcap 通过，`SSLContext` 创建失败；
- 记录到的 blocker：
  `ssl_context_creation_stalls_after_esp32s3_aes_gdma_read_error`；
- 最近完整 UIFlow2 矩阵仍为 `67/67`、`274/274`，本轮未重跑；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：问题、改动、执行、验证和边界
- `run.json`：机器可读结果
- `evidence/verification.summary.json`：脱敏后的聚合证据摘要

## 未覆盖项

- S3 AES/GDMA 数据面未修复，TLS Host allowlist fixture 尚未 PASS；
- Linux network namespace 下的 TLS fixture 未重跑；
- 可控 resolver、通用 destination allowlist、DHCP renewal 和双设备 fabric
  仍未完成；
- 本轮未重跑 67-case 全矩阵，因为未修改 QEMU 板级控制器；最近矩阵结果继续
  作为基线；
- 物理硬件、RF、功耗、声学、光学和机械行为均未验证。
