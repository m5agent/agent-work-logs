# Secure Boot v2 ECDSA P-256/P-384 mathematical verification

- 日期：`2026-10-25`
- 结果：`PASS`（static image-security validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`e37270edc92d15e408cf9d5d1de9761f3379b787`
- 结果版本：`6284afab191e336ceb3a31b824f82a04a292ae86`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164961843>
- 环境：macOS Apple Silicon；Python 3；public-only ECDSA test vectors；
  无物理硬件

## 结论

Secure Boot v2 的 ECDSA P-256/SHA-256 和 P-384/SHA-384 block 现在会使用
block 内的 public point、`r`、`s` 和 signed image digest 做数学验签：

- curve point on-curve 校验；
- `u1/u2` 计算；
- scalar multiplication 和 point addition；
- `r` recovery 校验。

一个 signature block 可以 CRC 和 image digest 都正确，但 ECDSA signature
数学无效；该结果现在返回 `signature-math-mismatch`，整体 evidence 为
`invalid`。

Manifest 仍保持：

```text
signature_authenticity = not-verified
trust_root             = not-verified
```

因为 public point 来自同一份可替换镜像，且没有与实时 eFuse trusted digest
比较。ECDSA P-192 仍只做格式/摘要解析，
`signature_math=not-implemented`。

## 关键证据

- Secure Boot fixture：`PASS`；
- checks：`16/16 PASS`；
- ECDSA P-256 valid math：`PASS`；
- ECDSA P-384 valid math：`PASS`；
- 坏 ECDSA signature + 正确 CRC/digest：`signature-math-mismatch`；
- RSA-PSS regression：`PASS`；
- 平台测试：`453/453 PASS`；
- 文档契约：`34/34 PASS`；
- Node：`2/2 PASS`；
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164961843>。

源码证据：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/6284afab191e336ceb3a31b824f82a04a292ae86/platform/tools/firmware_analysis.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/6284afab191e336ceb3a31b824f82a04a292ae86/platform/tests/fixtures/secure_boot_ecdsa_test_vectors.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/6284afab191e336ceb3a31b824f82a04a292ae86/tests/firmware/evidence-2026-10-25-secure-boot-image.json>

## 文件

- `report.md`：ECC 实现、test vector、验证和边界；
- `run.json`：机器可读记录；
- `evidence/secure-boot-ecdsa-16-checks.json`：最终 evidence；
- `evidence/verification.summary.json`：脱敏摘要。

## 未覆盖项

- ECDSA P-192 数学验签；
- embedded public key digest 与实时 eFuse 的比较；
- ROM/bootloader 实际安全启动；
- Secure Boot v1；
- Flash Encryption key/runtime；
- 生产 key、真机 eFuse、secure version/anti-rollback；
- physical hardware/RF/power。
