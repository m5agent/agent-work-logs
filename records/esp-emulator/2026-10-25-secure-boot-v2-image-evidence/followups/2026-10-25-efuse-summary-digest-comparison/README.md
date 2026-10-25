# ESP Emulator Secure Boot v2 eFuse summary digest comparison

- 日期：`2026-10-25`
- 结果：`PASS`（static image-security validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`79a23213167365b60653d23d14e78cd1bd41c46a`
- 实现提交：`ee4ad8f33ffa9083b41ddcbc8419189cd6fcbac1`
- 文档提交：`cb4267116d6cf9061f08484902be5a88864e7d99`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40166166903>
- 环境：macOS Apple Silicon；Python 3；Node 20；合成 Secure Boot v2 镜像；
  无物理硬件

## 结论

FirmwareManifest 现在能把 Secure Boot v2 signature block 中的公钥
SHA-256 与包内 `espefuse` summary 声明的 `SECURE_BOOT_DIGEST` 做结构化
对照：

- `efuse-summary-not-included`：有 signed image，但没有包内 summary；
- `efuse-key-digest-unavailable`：有 summary，但没有可读 digest；
- `match-unverified-source`：签名公钥摘要出现在包内 summary；
- `mismatch-unverified-source`：没有出现，并产生独立 warning；
- 未观察到 signed image 时为 `not-applicable`。

顶层 `security.trust_root.status` 仍固定为 `not-verified`。包内 summary
可以由调用者伪造，因此 digest match 不是 live eFuse trust、设备身份或 ROM
安全启动通过的证明。

## 关键证据

- Secure Boot fixture：`21/21 PASS`；
- RSA-PSS、ECDSA P-192/P-256/P-384 回归：`PASS`；
- 匹配、非匹配、digest 缺失三条 eFuse summary 路径：`PASS`；
- `status=verified` 和非法 comparison 被 manifest 校验拒绝：`PASS`；
- 平台测试：`454/454 PASS`；
- 文档契约：`34/34 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  Ruff `E9/F`、compileall、`git diff --check`：`PASS`；
- CI `platform-contracts` 与 `network-namespace-policy`：`PASS`。

## 文件

- `report.md`：字段语义、实现、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `evidence/secure-boot-efuse-comparison-21-checks.json`：fixture
  checks 与 trust comparison 的脱敏摘要。

## 未覆盖项

- 包内 eFuse summary 的来源、真实性和目标设备身份；
- live eFuse read、secure boot key revocation 和 production key；
- ROM/bootloader 实际执行 Secure Boot；
- Secure Boot v1 和 Flash Encryption runtime；
- QEMU 设备会话、物理硬件、RF、功耗和电气测量。

## Follow-up

- [Application/eFuse secure-version comparison](followups/2026-10-25-anti-rollback-version-comparison/)：
  application `secure_version` 与包内 `SECURE_VERSION` 的
  below/satisfied/unavailable 对照；fixture 扩展到 `26/26` checks。
  仍不执行 live eFuse read 或 bootloader anti-rollback。
