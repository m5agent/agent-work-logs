# ESP Emulator security evidence conflict report

## 背景

Manifest 已经区分镜像、sdkconfig 和 eFuse summary，但只处理
`config=on / eFuse=off`。反方向的 evidence 冲突、secure-boot 模式不一致和
key-purpose 缺失可能静默通过。

## 实现

- sdkconfig 明确 `=n` 时记录 `disabled`，不把“未声明”混成“关闭”。
- config disabled 但 eFuse enabled 时增加反方向 warning。
- secure boot config v1/v2 与 eFuse v1/v2 不同则 warning。
- secure boot enabled 但没有 `SECURE_BOOT_DIGEST*` purpose 则 warning。
- Flash Encryption enabled 但没有 XTS AES purpose 则 warning。
- 所有 eFuse summary 继续标记 `efuse_summary_unverified`。

## 验证

使用合成 ESP32-S3 flash、sdkconfig 和 espefuse JSON：

```text
config=on  / eFuse=off -> existing mismatch warnings
config=off / eFuse=on  -> reverse mismatch + missing key purposes
config=v1  / eFuse=v2  -> secure_boot_mode_mismatch
```

结果：FirmwareManifest `22/22`、文档契约 `19/19`、GitHub Actions
`40112470601` PASS。

## 边界

这不是 eFuse 真实性、真机密钥、secure boot 执行或法律/合规证明。

## 回滚

回退源码提交
`57d65bcb5009831be8346332938631644cc98872`。
