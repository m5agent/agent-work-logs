# ESP Emulator Secure Boot v2 image signature-sector evidence

- 日期：`2026-10-25`
- 结果：`PASS`（static image-security validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`9e88699199b8b473d1fb74b581931a398f4b68ca`
- 结果版本：`cc84be137f407bea97d7ec257786dc0e7c0bd1d1`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164290554>
- 环境：macOS Apple Silicon；Python 3；静态镜像 fixture；无物理硬件

## 结论

FirmwareManifest 现在能静态识别 bootloader 和 application partition 中的
Secure Boot v2 signature sector：

- RSA-PSS/RSA-3072；
- ECDSA P-192/P-256/SHA-256；
- ECDSA P-384/SHA-384；
- 最多 3 个连续 signature block；
- block magic/version、CRC32、image SHA-256/SHA-384；
- block 内公钥区域的 SHA-256 指纹。

合成签名 sector 在 bootloader 和 app 两处均得到
`signed-image-observed`；篡改 app 内容后整体结果变为 `invalid`；没有
signature sector 时得到 `not-found`。

Manifest 始终记录：

```text
signature_authenticity = not-verified
trust_root             = not-verified
```

因此该结果不会把“签名块与镜像摘要自洽”写成“公钥可信、ROM 已验签或真机
安全启动成功”。

## 关键证据

- Secure Boot v2 fixture：`PASS`；
- 每轮 checks：`13/13 PASS`；
- signed bootloader/app digest match：`PASS`；
- tampered image digest rejection：`PASS`；
- unsigned image `not-found` + warning：`PASS`；
- RSA-PSS、ECDSA P-256、ECDSA P-384：`PASS`；
- 平台测试：`451/451 PASS`；
- 文档契约：`34/34 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  Ruff `E9/F`、compileall、`git diff --check`：`PASS`；
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164290554>。

源码证据：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/cc84be137f407bea97d7ec257786dc0e7c0bd1d1/platform/tools/firmware_analysis.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/cc84be137f407bea97d7ec257786dc0e7c0bd1d1/platform/tools/firmware_manifest.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/cc84be137f407bea97d7ec257786dc0e7c0bd1d1/tests/firmware/evidence-2026-10-25-secure-boot-image.json>

## 文件

- `report.md`：格式依据、实现、验证和风险；
- `run.json`：机器可读记录；
- `evidence/secure-boot-image.json`：静态 fixture evidence；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- RSA-PSS/ECDSA 数学签名验证；
- embedded public key digest 与实时 eFuse 的比较；
- ROM/bootloader 实际安全启动；
- Secure Boot v1；
- Flash Encryption key/runtime；
- 生产 key、secure version/anti-rollback 真机状态；
- physical hardware/RF/power；
- live eFuse authenticity。

## Follow-up

- [RSA-PSS mathematical verification](followups/2026-10-25-rsa-pss-math-verification/)：
  使用 signature block 内 RSA modulus/exponent 验证 PSS/MGF1/SHA-256；
  `16/16` checks。ECDSA 数学验证、eFuse trust root 和 ROM 执行仍未覆盖。
- [ECDSA P-256/P-384 mathematical verification](followups/2026-10-25-ecdsa-p256-p384-math-verification/)：
  使用 block 内 public point/r/s 验证 ECDSA P-256/SHA-256 与
  P-384/SHA-384；`16/16` checks。
- [ECDSA P-192 mathematical verification](followups/2026-10-25-ecdsa-p192-math-verification/)：
  补齐 P-192/SHA-256；最终 fixture `17/17` checks。eFuse trust root 和
  ROM 执行仍未覆盖。
