# ESP Emulator Secure Boot v2 eFuse summary digest comparison

## 背景

已有 Secure Boot v2 fixture 能解析 signature sector、验证 block CRC、
镜像 digest、RSA-PSS 和 ECDSA P-192/P-256/P-384 数学签名，并记录每个
block 的公钥 SHA-256。但这些结果只说明“镜像内部的公钥能验证该镜像”，
不能说明公钥与目标设备 eFuse 中配置的 trust root 有什么关系。

本次目标是在不把自报数据升级成可信结论的前提下，提供一层可审计的摘要
对照证据。

## 实现

1. `_parse_efuse_security()` 只在 `KEY_PURPOSE_n` 为
   `SECURE_BOOT_DIGEST*` 时读取对应 `BLOCK_KEYn`；
2. `_efuse_sha256()` 去除常见分隔符和前导 `0x`，只接受 64 位十六进制
   SHA-256；
3. `_security_metadata()` 汇总 signed image 的
   `(image label, public_key_digest_sha256)` 与
   `efuse_summary.secure_boot_key_digests`；
4. 新增 `security.trust_root`：

```json
{
  "status": "not-verified",
  "comparison": "match-unverified-source",
  "source": "package-espefuse-json-unverified",
  "matching_pairs": [],
  "not_claimed": []
}
```

5. schema 与 structure validator 把 `status` 锁定为 `not-verified`，并校验
   comparison、source、matching pair digest 和 `not_claimed`；
6. `mismatch-unverified-source` 额外产生
   `secure_boot_v2_image_public_key_digest_mismatch` warning。

## 验证

```text
secure boot fixture       21/21 PASS
platform unittest       454/454 PASS
docs consistency         34/34 PASS
Node SHA256/upload        2/2 PASS
runtime coverage         PASS
peripheral catalog       PASS
QEMU profiles            PASS
project snapshot         PASS
Ruff E9/F                PASS
compileall               PASS
git diff --check         PASS
GitHub Actions           PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40166166903>

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | `PASS` | schema、manifest importer、fixture 和平台测试 |
| secure-image consistency | `PASS` | signature math、image digest 和 block CRC |
| eFuse summary comparison | `PASS` | match/mismatch/unavailable 分支 |
| live device response | `NOT RUN` | 没有从目标设备执行 `espefuse` |
| boot ROM execution | `NOT RUN` | 纯静态镜像分析 |
| physical hardware | `NOT RUN` | 无物理设备或测量 |

## 验证边界

- `match-unverified-source` 只表示两个包内摘要字符串相同；
- eFuse summary 是自报证据，`status` 永远保持 `not-verified`；
- 没有验证 eFuse 写入时点、目标设备身份、key revocation 或 secure version；
- 没有执行 QEMU guest，也没有让 boot ROM/bootloader 执行验签；
- 没有覆盖 Secure Boot v1、Flash Encryption、生产 key 或真机安全模式。

## 风险与回滚

- 该改动不会放宽 secure boot/Flash Encryption 的 Device Service 拒绝路径；
- 若后续误把 `trust_root.status` 提升为可信状态，schema 和单元测试会拒绝；
- 回滚实现为 revert `ee4ad8f`；回滚对应文档为 revert `cb42671`；
- 该功能只在静态 manifest 层增加证据，不回滚设备数据面或 QEMU 运行时。
