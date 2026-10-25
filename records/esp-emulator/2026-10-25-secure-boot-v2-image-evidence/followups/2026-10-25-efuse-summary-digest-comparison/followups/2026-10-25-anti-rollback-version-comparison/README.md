# ESP Emulator application/eFuse secure-version comparison

- 日期：`2026-10-25`
- 结果：`PASS`（static image-security validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`cb4267116d6cf9061f08484902be5a88864e7d99`
- 结果版本：`a358780eb572a9642bdf5f180572ef689529cf9c`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40166765668>
- 环境：macOS Apple Silicon；Python 3；Node 20；合成 8 MiB flash/eFuse summary；
  无物理硬件

## 结论

FirmwareManifest 现在在原有公钥/eFuse digest 对照之外，新增：

```text
security.anti_rollback
```

它会比较 application descriptor 的 `secure_version` 与包内 `espefuse`
summary 的 `SECURE_VERSION`，并区分：

- `image-secure-version-unavailable`；
- `efuse-summary-not-included`；
- `efuse-secure-version-unavailable`；
- `image-below-efuse-unverified-source`；
- `image-satisfies-efuse-unverified-source`。

镜像低于包内最低版本且 secure boot 有指示时产生
`secure_boot_image_secure_version_below_efuse` warning。若 secure boot
明确 disabled，仍保留数值关系，但不会生成误导性的运行时 warning。

`security.anti_rollback.status` 永远保持 `not-verified`。包内 summary 是
自报数据，本次没有读取 live eFuse，也没有执行 bootloader anti-rollback。

## 关键证据

- 平台测试：`455/455 PASS`；
- Secure Boot fixture：`26/26 PASS`；
- 文档契约：`34/34 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- below / satisfied / unavailable version comparison：`PASS`；
- secure boot disabled 不产生 warning：`PASS`；
- schema 拒绝 `status=verified` 和非法 comparison：`PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  Ruff `E9/F`、compileall、`git diff --check`：`PASS`；
- CI `platform-contracts` 与 `network-namespace-policy`：`PASS`。

## 文件

- `report.md`：字段语义、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `evidence/anti-rollback-26-checks.json`：fixture 和比较结果摘要。

## 未覆盖项

- 包内 eFuse summary 的真实性和设备身份；
- live eFuse read、key revocation 和 production key；
- bootloader/ROM anti-rollback 执行；
- Secure Boot v1、Flash Encryption runtime；
- QEMU 设备会话、物理硬件、RF、功耗和电气测量。
