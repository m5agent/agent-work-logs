# FirmwareManifest redacted static review and SBOM intake

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`4dea5236b21d2165e70d34fc0bae70fd8a75a540`
- 基线版本：`1ef7f0a081cfdc968a816741ca0ed52e18e6b967`
- 环境：Python 3；公开 M5Burner 固件缓存；无物理设备操作

## 结论

为 FirmwareManifest 增加可选的 `review` 契约，导入器始终生成该字段：

- URL 只保留 scheme、host/port、offset/length 和 URL/path SHA256；
- URL userinfo、query、fragment 和原始 path 不进入 manifest；
- API key/token/password/secret、JWT、AWS key 和 PEM 私钥头只记录类别与
  指纹，值全部 redacted；
- base64/hex 高熵编码块只记录 encoding、entropy、offset、length 和 SHA256；
- 支持 SPDX JSON 与 CycloneDX JSON SBOM 摘要；
- `REVIEW_REQUIRED` 与 capability/security validation 分层，不把 finding
  自动等同于恶意固件。

## 关键结果

- Platform tests：`221/221 PASS`
- Firmware structural analysis、partition/app descriptor：`PASS`
- 三个真实公开固件 manifest round-trip：`PASS`
- 三个样本 review：`REVIEW_REQUIRED`
- manifest 中原始凭据、URL query、编码块和宿主路径：`0`
- 旧版无 `review` 的 v1 manifest：继续可验证
- SPDX 2.3 / CycloneDX 1.6 元数据摘要：`PASS`
- 物理硬件和固件行为安全结论：`NOT RUN`

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- 启发式 finding 不证明恶意行为；
- SBOM 存在不证明组件版本或许可证声明真实；
- LittleFS/SPIFFS/FAT 深度资源解包、敏感文件权限和许可证策略仍待补；
- 证书链、生产 key、安全启动/Flash Encryption 运行态仍未验证。
