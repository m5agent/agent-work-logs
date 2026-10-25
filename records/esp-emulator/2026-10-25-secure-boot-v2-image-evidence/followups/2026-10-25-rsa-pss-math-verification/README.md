# Secure Boot v2 RSA-PSS mathematical verification

- 日期：`2026-10-25`
- 结果：`PASS`（static image-security validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`cc84be137f407bea97d7ec257786dc0e7c0bd1d1`
- 结果版本：`e37270edc92d15e408cf9d5d1de9761f3379b787`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164683427>
- 环境：macOS Apple Silicon；Python 3；public-only RSA-3072 test vector；
  无物理硬件

## 结论

Secure Boot v2 RSA-PSS 现在不仅检查 sector/CRC/image digest，还会使用
signature block 内的 RSA modulus/exponent 对 signed image digest 做数学验签：

- RSA public operation；
- PSS/MGF1/SHA-256；
- 32-byte salt；
- 0xBC trailer；
- DB padding、separator 和 recovered hash。

一个 signature block 可以 CRC 和 image digest 都正确，但 RSA signature 数学
无效；该结果现在返回 `signature-math-mismatch`，整体 image evidence 为
`invalid`。

Manifest 仍保持：

```text
signature_authenticity = not-verified
trust_root             = not-verified
```

因为公钥来自同一份可替换镜像，且没有与实时 eFuse trusted digest 比较。
ECDSA P-256/P-384 仍只做格式/摘要解析，
`signature_math=not-implemented`。

## 关键证据

- Secure Boot v2 fixture：`PASS`；
- checks：`16/16 PASS`；
- RSA-PSS valid signature 数学验证：`PASS`；
- 坏 RSA signature + 正确 CRC/digest：`signature-math-mismatch`；
- ECDSA math 边界：`not-implemented`；
- 平台测试：`452/452 PASS`；
- 文档契约：`34/34 PASS`；
- Node：`2/2 PASS`；
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164683427>。

源码证据：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/e37270edc92d15e408cf9d5d1de9761f3379b787/platform/tools/firmware_analysis.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/e37270edc92d15e408cf9d5d1de9761f3379b787/platform/tests/fixtures/secure_boot_rsa3072_test_vector.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/e37270edc92d15e408cf9d5d1de9761f3379b787/tests/firmware/evidence-2026-10-25-secure-boot-image.json>

## 文件

- `report.md`：PSS 实现、test vector、验证与边界；
- `run.json`：机器可读记录；
- `evidence/secure-boot-rsa-pss-16-checks.json`：最终 evidence；
- `evidence/verification.summary.json`：脱敏摘要。

## 未覆盖项

- embedded public key digest 与实时 eFuse 的比较；
- ECDSA P-256/P-384 数学验签；
- ROM/bootloader 实际安全启动；
- Secure Boot v1；
- Flash Encryption key/runtime；
- 生产 key、真机 eFuse、secure version/anti-rollback；
- physical hardware/RF/power。
