# ESP Emulator security evidence conflict checks

- 日期：`2026-10-25`
- 结果：`PASS`（static-security contract）
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ 57d65bcb5009831be8346332938631644cc98872`
- 环境：macOS Python 平台测试；合成 sdkconfig/eFuse summary

## 结论

FirmwareManifest 现在对 sdkconfig 与包内 eFuse summary 的 security evidence
做双向一致性检查：

- config enabled / eFuse disabled；
- config disabled / eFuse enabled；
- secure-boot v1 / v2 模式不一致；
- secure boot enabled 但缺少 `SECURE_BOOT_DIGEST` key purpose；
- Flash Encryption enabled 但缺少 XTS AES key purpose。

全部产生结构化 warning。包内 eFuse summary 仍为 `efuse_summary_unverified`，
不会升级为可信硬件状态。

## 关键证据

- FirmwareManifest：`22/22 PASS`；
- 文档一致性：`19/19 PASS`；
- GitHub Actions run `40112470601`：`PASS`；
- static evidence：
  `tests/firmware/evidence-2026-10-25-security-evidence-conflicts.json`。

## 未覆盖项

- eFuse summary 真实性；
- 真机 secure boot / Flash Encryption 执行；
- 生产 key custody、revocation 和物理硬件。
