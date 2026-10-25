# Secure Boot V2 ECDSA P-256/P-384 Verification

## 背景

上一轮已实现 RSA-PSS 数学验证，但 ECDSA P-256/P-384 仍只检查 block 格式、
CRC 和 image digest。ECDSA signature bytes 本身没有参与验证。

ESP Secure Boot v2 ECDSA block 包含：

```text
curve_id
public X/Y point
r/s signature
image SHA-256 or SHA-384
```

## 实现

新增纯 Python ECDSA verifier：

1. 校验 public point 坐标范围和 curve equation；
2. 校验 `0 < r,s < n`；
3. 计算 `s^-1 mod n`；
4. 计算 `u1 = z*s^-1`、`u2 = r*s^-1`；
5. 执行 double-and-add scalar multiplication；
6. 计算 `u1*G + u2*Q`；
7. 比较 result X 与 `r mod n`。

支持：

```text
NIST P-256 / SHA-256
NIST P-384 / SHA-384
```

P-192 保持 `not-implemented`，不从其他曲线继承 PASS。

## Test Vector

仓库保存 public-only 固定 test vectors：

- P-256 X/Y point 与两个 signed image 的 r/s；
- P-384 X/Y point 与两个 signed image 的 r/s。

没有保存测试私钥。负向运行把 P-256 application signature byte 翻转后重新
计算 block CRC，使 CRC 和 image digest 仍有效，只破坏 ECDSA 数学。结果必须为：

```text
image status       signature-math-mismatch
overall status     invalid
```

## 验证

```text
secure boot fixture checks       16/16 PASS
platform unittest                453/453 PASS
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
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164961843>

## 验证边界

- ECDSA P-256/P-384 math valid 不等于 eFuse key digest trusted；
- P-192 数学验签未实现；
- 不执行 ROM/bootloader 安全启动；
- 不支持 Secure Boot v1；
- 不验证 Flash Encryption、生产 key、eFuse programming 或 anti-rollback；
- 不证明真机安全启动、RF、功耗或电气行为。

## 风险与回滚

- ECC 运算只使用公开曲线参数和有界 scalar；
- malformed point/signature 返回 invalid，不抛出；
- 该实现不会改变 `signature_authenticity=not-verified` 或
  `trust_root=not-verified`；
- 回滚为 revert `6284afa`，恢复 ECDSA `not-implemented` 边界。
