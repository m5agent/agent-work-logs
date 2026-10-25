# Secure Boot V2 Image Signature-Sector Evidence

## 背景

已有 FirmwareManifest 能分层记录 sdkconfig secure boot 配置、partition
encrypted flag、application secure version 和包内 eFuse summary。但这些层
都没有检查镜像是否实际带 Secure Boot v2 signature sector，也没有验证
signature block 与 image content 的摘要关系。

Secure Boot v2 在每个 bootloader/app image 的 4 KiB 对齐边界附加 signature
sector。每个 1216-byte block 包含 magic、version、image digest、公钥、
签名、CRC32 和 padding。完整签名验证还需要 boot ROM 使用 eFuse 中受信
公钥 digest；只做静态镜像解析不能替代该过程。

## 实现

### Signature sector 扫描

对 bootloader 和每个 present app partition：

1. 从 image segment 结束后的下一个 4 KiB 边界开始扫描；
2. 要求首字节为 `0xE7`；
3. 接受 RSA version `0x02` 或 ECDSA version `0x03`；
4. 读取最多 3 个连续 1216-byte block；
5. 重新计算前 1196-byte CRC32；
6. 从 signature sector 起点之前的镜像内容计算 SHA-256/SHA-384；
7. 与 block 内 digest 比较；
8. 记录 RSA/ECDSA scheme、curve、public-key digest、CRC 和 image match。

整体状态：

```text
signed-image-observed  valid block + matching image digest
invalid                signature-like sector with CRC/digest failure
not-found              no parseable v2 signature sector
```

单个 image 的 digest mismatch 优先把整体状态标为 `invalid`，不会被另一个
正常 bootloader block 掩盖。

### Manifest 分层

`security.secure_boot_image` 新增：

- 整体 status；
- bootloader/app 每 image 的 evidence；
- block count、scheme、image digest match；
- public key digest SHA-256；
- 固定 `signature_authenticity=not-verified`；
- 固定 `trust_root=not-verified`；
- 固定 `not_claimed` 边界。

Warnings：

```text
secure_boot_v2_image_signature_authenticity_unverified
secure_boot_v2_image_signature_not_observed
secure_boot_v2_image_signature_invalid
```

Manifest structure validation 会拒绝任何声称
`signature_authenticity != not-verified` 或
`trust_root != not-verified` 的结果。

## 验证

静态 fixture 使用 synthetic signature sectors：

```text
RSA-PSS/RSA-3072          PASS
ECDSA P-256/SHA-256       PASS
ECDSA P-384/SHA-384       PASS
bootloader image digest   PASS
application image digest  PASS
public key fingerprint    PASS
tampered image            invalid
unsigned image            not-found
manifest structure        PASS
```

全局验证：

```text
platform tests       451/451 PASS
docs contracts        34/34 PASS
Node tests              2/2 PASS
runtime coverage       PASS
peripheral catalog     PASS
QEMU profiles          PASS
project snapshot       PASS
Ruff E9/F              PASS
compileall             PASS
git diff --check       PASS
GitHub Actions         PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40164290554>

## 验证边界

- synthetic block 中的公钥和 signature bytes 为零；
- 没有做 RSA-PSS/ECDSA 数学验签；
- 没有把 block 内公钥 digest 与 eFuse 中 trusted digest 比较；
- 没有让 ROM/bootloader 执行 secure boot；
- 不支持 Secure Boot v1；
- 不验证 Flash Encryption key、生产 key、eFuse programming 或 secure
  version anti-rollback；
- 不证明真机安全启动、RF、功耗或电气行为。

## 风险与回滚

- 加密镜像可能无法按明文 layout 解析 signature sector，应保持
  `not-found`/unknown，而不是推断未签名；
- 结构有效的 block 仍可能是攻击者生成的自洽数据；这正是不提升为
  authenticity PASS 的原因；
- 回滚为 revert `cc84be1`，恢复旧 manifest 字段和扫描逻辑；
- 回滚后不得继续引用 `signed-image-observed` 或本轮 warnings。
