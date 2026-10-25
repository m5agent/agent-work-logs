# Secure Boot V2 RSA-PSS Mathematical Verification

## 背景

上一轮已能解析 Secure Boot v2 signature sector、CRC 和 image digest，但
signature bytes 只是镜像中的数据。摘要一致不代表 RSA signature 数学有效。

ESP Secure Boot v2 RSA block 包含：

```text
n        384-byte little-endian RSA modulus
e        4-byte little-endian public exponent
sig      384-byte little-endian RSA-PSS signature
mHash    32-byte image SHA-256
```

新增验证使用 `n/e` 执行 RSA public operation，再按 RSA-PSS/SHA-256、MGF1、
32-byte salt 和 0xBC trailer 恢复 `mHash`。

## 实现

每个 RSA signature block 记录：

```text
signature_math       = valid | invalid | not-implemented
signature_math_valid = true | false | null
```

每个 image 记录：

```text
image_digest_match
signature_math_verified
```

状态优先级：

1. block CRC/magic/version 必须有效；
2. image digest 必须匹配；
3. RSA-PSS 数学验证必须通过；
4. 任一 mismatch 将整体状态设为 `invalid`；
5. ECDSA 数学验证保持 `not-implemented`。

Manifest 的 `signature_authenticity` 和 `trust_root` 仍固定为
`not-verified`。数学验证只说明 signature 与 block-embedded public key
匹配，不说明该 key 被设备信任。

## Test Vector

使用固定 3072-bit RSA 测试 key 对两个确定 image digest 生成 PSS 签名：

- bootloader 4 KiB content；
- application 4 KiB content。

仓库只保存公钥 modulus/exponent 和签名，不保存测试私钥。

负向运行把 application signature byte 翻转后重新计算 block CRC，使 CRC 和
image digest 仍有效，只破坏签名数学。结果必须为：

```text
image status       signature-math-mismatch
overall status     invalid
```

## 验证

```text
secure boot fixture checks       16/16 PASS
platform unittest                452/452 PASS
docs consistency                  34/34 PASS
Node SHA256/upload                  2/2 PASS
runtime coverage                   PASS
peripheral catalog                 PASS
QEMU profiles                      PASS
project snapshot                   PASS
Ruff E9/F                          PASS
compileall                         PASS
git diff --check                   PASS
GitHub Actions                     PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164683427>

## 验证边界

- RSA-PSS math valid 不等于 eFuse key digest trusted；
- ECDSA P-256/P-384数学验签未实现；
- 不执行 ROM/bootloader 安全启动；
- 不支持 Secure Boot v1；
- 不验证 Flash Encryption、生产 key、eFuse programming 或 anti-rollback；
- 不证明真机安全启动、RF、功耗或电气行为。

## 风险与回滚

- 纯 Python big-int public operation 运行有界到 384-byte modulus/signature；
- malformed modulus/signature 返回 invalid，不抛出；
- 如果 eFuse trust 被误写成已通过，会掩盖 key substitution；因此 manifest
  structure validator 固定拒绝非 `not-verified` trust root；
- 回滚为 revert `e37270e`，恢复上一轮的 CRC/digest-only 证据。
