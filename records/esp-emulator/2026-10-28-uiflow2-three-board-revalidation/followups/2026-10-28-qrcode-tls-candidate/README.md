# QRCode.setText 与 TLS epoch 三设备候选固件复验

- 日期：`2026-10-28`
- 结果：`PASS`（限定三台 hash-pinned 候选固件、virtual-device validation）
- 工作类型：`code_change` + `virtual_device_validation`
- 源码版本：[`m5agent/m5stack-esp-emulator@007b93d5`](https://github.com/m5agent/m5stack-esp-emulator/commit/007b93d5)
- 环境：macOS arm64；UIFlow2 v2.5.3 matching source builds；QEMU runtime `21b7e34c…`

## 结论

StopWatch、StickS3、Core2 分别用匹配 cached build 增量重链接
`0014-widgets-qrcode-text` 和 `0010-mbedtls-epoch`。QR preimage 三台均
`ORACLE_MISMATCH`（仍解码旧文本），候选三台均 `FRAME_PASS`（解码新文本）。
TLS preimage 三台均为 `2 ERROR + 3 STATE_PASS`（证书被判过期），候选三台均为
`5/5 PASS`，完成 TLSv1.2 双向认证 HTTP 交换和精确客户端证书校验。

应用分区外字节、原始源码和 cached library 均保持不变。该结果是 incremental
relink，不是冷构建，也不是原厂冻结固件或物理硬件 PASS。

## 关键证据

- QR：三台 preimage→candidate 均为 `ORACLE_MISMATCH → FRAME_PASS`。
- TLS：三台 preimage `2 ERROR + 3 STATE_PASS` → candidate `5 PASS`。
- 每次 TLS 运行有两次 `/tls-authenticated` GET，服务端验证 guest 客户端证书。
- StickS3 TLS 使用 native UART REPL 的 `unified` build，并显式选择 native bootstrap。
- 完整平台回归 `1346` 项 `OK`、`1` 项 skip；四个生成器检查 PASS。

## 文件

- `report.md`：构建、执行、边界和复现
- `run.json`：机器可读记录
- `evidence/results.json`：固件、app、证书、peer 和结果
- `evidence/regression-summary.txt`：回归与清理摘要

## 未覆盖项

- 增量 relink，不是独立冷构建。
- 公网 PKI、证书持久化、Secure Element 和物理硬件均为 `NOT RUN`。
- 原厂 CDN 冻结固件仍未修复；结论只适用于记录的候选镜像。
