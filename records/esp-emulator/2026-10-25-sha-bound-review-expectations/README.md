# ESP Emulator SHA-bound 固件审查预期

- 日期：`2026-10-25`
- 结果：`PASS`（accepted virtual-device scope）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`e41bfd5b2e4dd0b582e1caa946d2245a67a37218`
- 结果版本：`351eb16d49f1ffbef562810668f3248e1cfc7f52`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40139992678>
- 环境：macOS Apple Silicon；Python 3；Device Service `/api/v1`；QEMU ESP32-S3 WiFi；GitHub Actions Ubuntu

## 结论

通用用户固件 matrix 新增 SHA-bound 审查预期，避免把“有屏设备但没有 UI”的
network-first/headless 固件永久按黑屏 UI 规则判为 PARTIAL。

支持三种模式：

- `ui-interactive`：保留默认的非空首帧和输入响应门禁；
- `headless-serial`：要求显式 guest 串口 marker、running 和无致命错误；
- `network-first`：要求 guest marker、Device Service network status 和
  请求的 pcap summary；不会只凭“session running”给 PASS。

审查预期不写入 FirmwareManifest，而是放在外部 v1 JSON，按
`device_id + firmware_id + sha256` 匹配。Manifest 继续只描述镜像事实；
expectation digest、NVS/SD fixture SHA 和 firmware SHA 共同进入结果键。
公开 BIN 的 SHA 变化后，旧 expectation 会 fail-closed，不允许继承结论。

明文 `wifi_password` 被拒绝，只允许 `wifi_password_env` 引用运行环境。

## 关键证据

- 平台测试：`387/387 PASS`；
- 文档契约：`20/20 PASS`；
- Node 固件上传/SHA 测试：`PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`；
- GitHub Actions `platform-contracts` 与 `network-namespace-policy`：
  `PASS`；
- 公开 OpenAI AtomS3R BIN：
  `b3597fcabbff57c98618caa8754af84745e9eac35b2868ab3c4cb0935b7c59b3`；
- session-isolated Open NVS fixture：
  `14f0acc47e1e1bef7e19d29c90febd0fe3707599fd8fc42eeb14dd27cfc26e5d`；
- expectation digest：
  `25c42d6ade2b946a6e1e597b2604dbcbf5627d20a2b8afa5e4a031519b952096`；
- Device Service session `25d4808c15c14585b0e2fad3adf4ec19`：
  `network-first_expectation_ok`、`wifi:connected`、`got ip:`、
  `api.openai.com` DNS、TCP/443、37-packet pcap，停止后保留历史；
- expectation schema SHA256：
  `9e83276d42d4013109d03eddcebf3643e04ade83b4ac5e07ec5fcc466feb24e4`；
- source evidence SHA256：
  `2da3a2fffd09674ff42a3d0e68cee3fcad1c20779f0bfeab6672bec917aeb64c`。

## 文件

- `report.md`：设计、执行、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏聚合证据。

源码证据：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/351eb16d49f1ffbef562810668f3248e1cfc7f52/platform/tools/user_firmware_expectations.schema.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/351eb16d49f1ffbef562810668f3248e1cfc7f52/tests/firmware/evidence-2026-10-25-network-first-review-expectation.json>

## 未覆盖项

- 真实 OpenAI key、账号、Realtime/WebRTC 和 voice/audio 业务；
- WPA3-SAE、group-key multicast 和物理 RF/WPA2；
- UI 或 provisioning frame；
- 物理硬件、功耗、声学和电气行为；
- 仍需要人工提供 expectation；binary 不能自动证明应用期望的网络行为。
