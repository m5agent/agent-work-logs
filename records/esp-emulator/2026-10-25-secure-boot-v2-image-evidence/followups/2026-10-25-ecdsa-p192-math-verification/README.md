# Secure Boot v2 ECDSA P-192 mathematical verification

- 日期：`2026-10-25`
- 结果：`PASS`（static image-security validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`6284afab191e336ceb3a31b824f82a04a292ae86`
- 结果版本：`79a23213167365b60653d23d14e78cd1bd41c46a`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40165174355>
- 环境：macOS Apple Silicon；Python 3；public-only ECDSA P-192 test vector；
  无物理硬件

## 结论

Secure Boot v2 ECDSA P-192/SHA-256 现在使用 block 内 public point、`r/s`
和 signed digest 进入与 P-256/P-384 相同的数学验签路径。

Secure Boot fixture 现在同时覆盖：

```text
RSA-PSS / RSA-3072
ECDSA P-192 / SHA-256
ECDSA P-256 / SHA-256
ECDSA P-384 / SHA-384
```

最终 fixture 为 `17/17 PASS`。

Manifest 仍固定：

```text
signature_authenticity = not-verified
trust_root             = not-verified
```

因为公钥来自镜像本身，尚未与实时 eFuse trusted digest 比较。

## 关键证据

- Secure Boot fixture：`PASS`；
- checks：`17/17 PASS`；
- ECDSA P-192 valid math：`PASS`；
- P-256/P-384 与 RSA-PSS regression：`PASS`；
- 平台测试：`453/453 PASS`；
- 文档契约：`34/34 PASS`；
- Node：`2/2 PASS`；
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40165174355>。

源码证据：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/79a23213167365b60653d23d14e78cd1bd41c46a/platform/tools/firmware_analysis.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/79a23213167365b60653d23d14e78cd1bd41c46a/platform/tests/fixtures/secure_boot_ecdsa_test_vectors.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/79a23213167365b60653d23d14e78cd1bd41c46a/tests/firmware/evidence-2026-10-25-secure-boot-image.json>

## 文件

- `report.md`：P-192 实现、验证和边界；
- `run.json`：机器可读记录；
- `evidence/secure-boot-ecdsa-p192-17-checks.json`：最终 evidence；
- `evidence/verification.summary.json`：脱敏摘要。

## 未覆盖项

- embedded public key digest 与实时 eFuse 的比较；
- ROM/bootloader 实际安全启动；
- Secure Boot v1；
- Flash Encryption key/runtime；
- 生产 key、真机 eFuse、secure version/anti-rollback；
- physical hardware/RF/power。
