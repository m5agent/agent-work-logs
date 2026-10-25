# Secure Boot V2 ECDSA P-192 Verification

## 背景

P-256/P-384 已通过 block-embedded public point 与 `r/s` 完成 ECDSA
数学验证，但 P-192 仍为 `not-implemented`。本轮补齐最后一个受支持曲线。

## 实现

新增 NIST P-192 曲线参数：

```text
p, a=-3, b, Gx, Gy, n
```

P-192 block 使用：

```text
24-byte X little-endian
24-byte Y little-endian
24-byte r little-endian
24-byte s little-endian
SHA-256 image digest
```

验签复用统一 ECDSA verifier：

1. point on-curve；
2. `0 < r,s < n`；
3. `s^-1 mod n`；
4. `u1G + u2Q`；
5. recovered X == r。

## 验证

固定 public-only P-192 测试点与两个 image 的 `r/s`：

```text
bootloader image digest  PASS
application image digest PASS
RSA-PSS regression       PASS
ECDSA P-256/P-384 regress PASS
```

全局验证：

```text
secure boot checks       17/17 PASS
platform unittest        453/453 PASS
docs consistency          34/34 PASS
Node SHA256/upload          2/2 PASS
runtime coverage           PASS
peripheral catalog         PASS
QEMU profiles              PASS
project snapshot           PASS
Ruff E9/F                  PASS
compileall                 PASS
git diff --check           PASS
GitHub Actions             PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40165174355>

## 验证边界

- P-192 math valid 不等于 eFuse key digest trusted；
- 不执行 ROM/bootloader 安全启动；
- 不支持 Secure Boot v1；
- 不验证 Flash Encryption、生产 key、eFuse programming 或 anti-rollback；
- 不证明真机安全启动、RF、功耗或电气行为。

## 风险与回滚

- 曲线参数固定为 NIST P-192；
- malformed point/signature 返回 invalid；
- 不改变 `signature_authenticity=not-verified` 和
  `trust_root=not-verified`；
- 回滚为 revert `79a2321`。
