# ESP Emulator required/optional capability consistency

- 日期：`2026-10-25`
- 结果：`PASS`（static-manifest contract）
- 工作类型：`code_change`
- 问题来源：FirmwareManifest capability mismatch
- 源码版本：`m5agent/m5stack-esp-emulator @ 6e2e7693f8b5edf787d49ecb709bdc00acaaa7f0`
- 基线版本：`92263b596eea3a895339436b38e99935d09118e7`
- 环境：macOS Python 平台测试；静态合成 ESP32-S3 flash

## 结论

Capability 声明的 required/optional 语义已补齐：

- 同一 capability 同时出现在 required 和 optional 时，importer 拒绝；
- 已生成 manifest 出现该重叠时，structure validation 拒绝；
- required capability 不被目标 profile 支持时，manifest 为 `REJECTED`；
- optional capability 不被目标 profile 支持时，只产生
  `unsupported_optional_capability` warning，manifest 仍为 `PASS`；
- unknown required/optional capability 分别产生结构化 warning。

这解决的是 Manifest 声明一致性，不证明固件代码实际调用或运行 optional
能力。

## 关键证据

- FirmwareManifest：`22/22 PASS`；
- 文档一致性：`19/19 PASS`；
- 完整平台套件：`350/350 PASS`；
- static evidence：
  `tests/firmware/evidence-2026-10-25-capability-required-optional-consistency.json`；
- GitHub Actions run `40112248145`：`PASS`；
- required/optional `camera` on StickS3 的正向/负向对照均保留。

## 文件

- `report.md`：契约、示例和边界。
- `run.json`：机器可读记录。
- `evidence/verification-summary.json`：脱敏摘要。
- `patches/`、`code/`：不适用；实现位于公开源码仓库。

## 未覆盖项

- 声明与所有 firmware code paths 的一一映射；
- optional 分支的实际运行行为；
- 外设真机能力探测；
- 物理硬件。
