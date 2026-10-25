# Firmware security preflight understatement report

## 背景

固件审查需要同时支持 Secure Boot/Flash Encryption 静态证据与 QEMU
virtual-device 执行。当前 QEMU profile 不建模真实 key、boot ROM trust
chain 或 Flash Encryption，因此启用这些链的镜像必须在进入 session 前拒绝。

上一轮已修复 unknown required capability fail-closed 和 manifest identity。
继续审计发现 service preflight 只读取 manifest aggregate security 字段，
手写或篡改 manifest 可以通过把这些字段设为 `unknown` 来隐藏其它层的
enabled/observed 证据。

## 修复

### Security preflight

新增统一的 security runtime 判定：

- aggregate `secure_boot` 为 v1/v2/enabled-unspecified → reject；
- aggregate `flash_encryption` 为 enabled → reject；
- sdkconfig secure boot v1/v2/enabled-unspecified → reject；
- sdkconfig Flash Encryption enabled → reject；
- `secure_boot_image.status=signed-image-observed` → reject；
- `secure_boot_image.status=invalid` → reject；
- 包内 eFuse summary secure boot v1/v2/enabled-unspecified → reject；
- 包内 eFuse summary Flash Encryption enabled → reject。

包内 eFuse summary 仍不可信，但“不可信”不等于可以忽略其 requires-chain
声明。该判定只影响当前 runtime 兼容性，不升级 summary 为 hardware truth。

### 结构校验

即使调用方没有运行 JSON Schema validator，内部结构校验现在也要求：

- `security.secure_boot`、`flash_encryption`、`efuse` 存在；
- 聚合/config 字段属于受支持枚举；
- `validation.errors` 和 `validation.warnings` 为数组；
- schema 中 secure-boot / Flash Encryption config 明确允许 `disabled`。

## 证据

`security_preflight/run_test.py` 生成 synthetic Secure Boot v2 和普通
ESP32-S3 flash：

- baseline：`PASS`；
- aggregate v2：`REJECTED/secure_boot_not_modeled`；
- aggregate unknown + config v2：
  `REJECTED/secure_boot_config_not_modeled`；
- aggregate/config unknown + signed image：
  `REJECTED/secure_boot_image_not_modeled`；
- signed image 改为 invalid：`REJECTED/secure_boot_image_invalid`；
- aggregate unknown + Flash Encryption config enabled：
  `REJECTED/flash_encryption_config_not_modeled`；
- aggregate unknown + eFuse v2/enabled：同时拒绝 secure boot 与 Flash
  Encryption chain。

完整结果：
[`firmware-security-preflight-fail-closed.json`](https://github.com/m5agent/m5stack-esp-emulator/blob/eb7d80a27166be41f82782e7c104bc82226b6b30/tests/firmware/evidence-2026-10-26-firmware-security-preflight-fail-closed.json)

Secure Boot v2 原 fixture 使用当前 `firmware_manifest.py` 哈希重跑，结果为
[`secure-boot-image-security-preflight.json`](https://github.com/m5agent/m5stack-esp-emulator/blob/eb7d80a27166be41f82782e7c104bc82226b6b30/tests/firmware/evidence-2026-10-26-secure-boot-image-security-preflight.json)，
`26/26` checks PASS。authenticity、trust root 和 anti-rollback 仍固定
`not-verified`。

## 验证

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| static security preflight | `PASS` | `11/11` |
| Secure Boot image analysis | `PASS` | `26/26` |
| platform regression | `PASS` | `530/530` |
| Node source/upload units | `PASS` | `2/2` |
| firmware runtime | `NOT RUN` | 本轮是 manifest security contract |
| live eFuse/secure-boot execution | `NOT RUN` | 无真机或 ROM trace |
| physical hardware | `NOT RUN` | 无 RF/电气/功耗/光学验证 |

## 风险与边界

- 包内 eFuse summary 仍是 unverified self-assertion；
- 结构证据不能证明归档中的 Secure Boot 公钥可信；
- 当前 QEMU 不执行真实安全启动或 Flash Encryption；
- 完整 67-case matrix 没有重新执行；
- 没有真机安全配置或生产 key 流程。

## 回滚

回滚 product commit
`eb7d80a27166be41f82782e7c104bc82226b6b30` 可恢复旧行为，但会重新允许
aggregate security understatement 绕过 preflight。旧 evidence 不应删除或
改写。
