# ESP Emulator P0 网络、固件与 Core2 收口

- 日期：`2026-10-23`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：M5Stack ESP Emulator P0 工程推进
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`11bdf8fc3ed0588b4fb2ad7783d6b894489588fb`
- 基线版本：`67c0aa481e80b993b5445cf0bebf81d48ad65081`
- 环境：macOS Apple Silicon 平台测试；Linux arm64 容器内 QEMU/network namespace

## 结论

本轮闭合了三个 P0 工作流的大部分实现基础：网络 namespace/pcap/负向认证/
断线重连，Core2 确定性启动、unified WiFi、公网 DNS/HTTP 和 HCI-offload
BLE，以及版本化 FirmwareManifest、WebBurner/M5Burner/ESP-IDF 导入和
capability mismatch。

最终状态仍为 `PARTIAL`：Core2 原生 ESP32 BT controller 尚未被外部 peer 观察到
advertising/connection/GATT，正式 worker/CI 网络生命周期和物理硬件验证仍未完成。

## 关键证据

- 平台测试：`210/210` PASS；
- UIFlow2 全矩阵：`67/67` 用例、`274/274` 检查 PASS；
- Core2：确定性 TCG/icount 下 10 次独立首轮运行 10/10 PASS，未使用重试；
- Linux arm64：同一 QEMU 源码重建后在 private network namespace 内完成
  guest DHCP、受控 HTTP、DNS deny、pcap 和 ready marker；
- 网络负向：incorrect-credential 用例和 StickS3 link fault/reconnect 用例 PASS；
- 固件：三个公开样本完成 manifest round-trip，capability mismatch 返回
  HTTP 409 且未创建 session；
- runtime coverage、peripheral catalog、QEMU profiles、OpenAPI/schema parse 和
  `git diff --check` PASS；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：实现、根因、执行、验证和边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：脱敏后的聚合证据摘要

## 未覆盖项

- Core2 原生 BT controller 的外部 advertising、connection 和 GATT；
- 物理 Core2 cache/PSRAM 时序、RF、coexistence、soak 和真机路径；
- Linux network lane 的正式 CI/worker、allowlist、TLS 测试 CA 和双设备 lab fabric；
- FirmwareManifest 的深层静态审查、生产安全 key 流程和跨厂商回归；
- 任何物理硬件 PASS。
