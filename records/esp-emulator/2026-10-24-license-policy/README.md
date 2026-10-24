# ESP Emulator FirmwareManifest 声明级许可策略

- 日期：`2026-10-24`
- 结果：`PASS`（静态 Manifest 策略）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`21d26c93055a65b9952a3d5611838bcbb3f2dc10`
- 基线版本：`acd5329c4fecb23d7ac2cb1e5dd6dcf370c673f5`
- 环境：macOS Apple Silicon；Python 3；合成 firmware/filesystem fixtures

## 结论

FirmwareManifest 现在包含可审计的 `license_policy`：

- 汇总 provenance、文件系统 SPDX 和 SPDX/CycloneDX SBOM 声明；
- 支持显式 allowlist/denylist；
- allowlist 全匹配为 `PASS`；
- denylist 或不在 allowlist 内为 `REJECTED`，Manifest validation 同步拒绝；
- 未配置 allowlist、无声明或 `NONE`/`NOASSERTION`/`unknown` 保持
  `REVIEW_REQUIRED`；
- 输出每条声明的来源，不把声明检查写成法律意见或完整源码扫描。

## 关键证据

- 平台测试：`272/272 PASS`；
- Python compileall、JSON schema parse 和 selected Ruff rules：PASS；
- GitHub Actions `40047172520`：两个 job 均成功；
- evidence：
  `tests/firmware/evidence-2026-10-24-license-policy.json`；
- 运行时文件权限、完整源码级许可扫描、法律审批和真机：`NOT RUN`。

## 文件

- `report.md`：策略、状态机、验证和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：检查摘要

## 未覆盖项

- 不判断版权归属；
- 不扫描未声明的源码级依赖；
- 不把 `PASS` 写成许可证合规或法律意见；
- 文件系统仍为 `permissions=not-recorded`；
- 不涉及真机 secure boot、key 或 eFuse 状态。
