# ESP Emulator Application/eFuse Secure-Version Comparison

## 背景

上一轮已经能把 Secure Boot v2 signature block 的公钥 SHA-256 与包内
eFuse `SECURE_BOOT_DIGEST` 做 match/mismatch 对照。该结果仍不能回答另一个
常见安全配置问题：

> application 的 `secure_version` 是否低于设备 eFuse 声明的最低版本？

如果低于，secure boot bootloader 通常会拒绝镜像。这个判断可以由
application descriptor 与包内 `espfuse` summary 的公开数值完成，但依然
不能把自报 summary 当成 live trust root。

## 实现

`firmware_manifest.py` 新增 `security.anti_rollback`：

```json
{
  "status": "not-verified",
  "comparison": "image-below-efuse-unverified-source",
  "source": "package-espefuse-json-unverified",
  "image_secure_version": 2,
  "efuse_secure_version": 3,
  "not_claimed": [
    "package-provided eFuse summary authenticity",
    "live eFuse read from the target device",
    "bootloader anti-rollback enforcement"
  ]
}
```

实现规则：

1. descriptor 无 `secure_version` 时记录 unavailable；
2. 无 eFuse summary 或 summary 无 `SECURE_VERSION` 时分别记录缺失；
3. image version 小于 eFuse version 时记录 below；
4. 否则记录 satisfied；
5. secure boot 有指示且 below 时才产生 warning；
6. schema 与 structure validator 禁止把 status 提升为 `verified`。

## 验证

```text
platform unittest       455/455 PASS
secure boot fixture      26/26 PASS
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
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40166765668>

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | `PASS` | manifest importer、schema、fixture 和平台测试 |
| image version parse | `PASS` | app descriptor builder + manifest |
| below/satisfied/unavailable comparison | `PASS` | fixture 与单元测试 |
| secure boot disabled boundary | `PASS` | 数值保留、warning 不产生 |
| live eFuse read | `NOT RUN` | 无目标设备读取 |
| bootloader anti-rollback | `NOT RUN` | 纯静态分析 |
| physical hardware | `NOT RUN` | 无物理设备或测量 |

## 验证边界

- `image-satisfies-efuse-unverified-source` 只描述两个包内数值的关系；
- 包内 summary 可以伪造，status 永远保持 `not-verified`；
- 未验证 key revocation、secure version 更新流程或设备实际 eFuse；
- 未让 ROM/bootloader 执行 secure boot 或 anti-rollback；
- 未覆盖 Secure Boot v1、Flash Encryption、生产 key 或真机。

## 风险与回滚

- 新字段不会放宽 Device Service 对 secure boot/Flash Encryption 镜像的拒绝；
- secure boot 明确 disabled 时不产生 below warning，避免误报运行时拒绝；
- 回滚实现为 revert `a358780`；
- 本文档归档不修改源码仓库运行时状态。
